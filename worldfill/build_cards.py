#!/usr/bin/env python3
"""Step 27 (systems C10, C12, C22): the knowledge cards for every place: famous people and organisations.

    python3 fetch_cards_wd.py pool orgs     fetch the two pools from Wikidata (into build/cards/raw/, not kept)
    python3 build_cards.py --select         choose who gets a card (build/cards/chosen_*.txt)
    python3 fetch_cards_wd.py details       fetch names, dates, places, offices, memberships and works for them
    python3 build_cards.py --positions      list the offices found (build/cards/positions.txt)
    python3 fetch_cards_wd.py holders       count each office's holders and fetch its name
    python3 build_cards.py --build          write cards/cards.tiles into the mod
    python3 build_cards.py --check          read cards/cards.tiles back and check it (exit 1 on a problem)

Who gets a card (people): everyone with 12 or more Wikipedia articles, at most 300 for one 5-degree box of the map
and one century; and in every box and century at least the 30 best known people there are (so a quiet land still
has its own names). Organisations: companies, schools and universities, newspapers, parties, armies, guilds and
societies, religious orders, the best known of each kind per box and century.

The card file is the record (there is no separate master): the Wikidata exports are large and can be fetched again.
Facts kept per card: the name, the short description, the years (birth and death, or founded and closed, with
"around" when Wikidata gives only the decade), the home or seat on the map and its name, the death place, up to three
offices with their years, up to two works with their year, and links to other cards (studied at, party, served in,
worked for, member of, founded / founded by).

Cross-check: the people also found in history/famous_people.json.gz (the Wikipedia year pages) by name and one year
are compared; where the other year differs, the Wikipedia year is used (turn 12: Wikipedia is the primary source); a
difference of more than a year is counted in the report.

File layout: the step-26 tile format (build_tiles.write_tiles), dataset "cards".
  groups "b/<y>/<x>": 5-degree boxes by the home or seat; buckets by the century of the year a card becomes known
  (people: birth + 20, or the first dated office or work if earlier but not before age 5, or death - 40;
  organisations: the founding year).
  group "v": one tile, the office names: int n, then n strings.
  group "i": one tile, the index: int n, then n QIDs (ascending, as varint gaps), then n tile numbers (varints; tile
  numbers count every tile of the file in the order of the groups and their tiles).
  group "f": the people known far and wide (50 or more articles) in short rows: int qid, int lat, int lon, short fame,
  short known, int from, int to, str name; buckets by the century they became known.
  group "n": one tile, names for "who rules here?": int n, then n (int name hash, int qid) sorted by hash (FNV-1a of
  the name in lower case without accents, letters and digits only; also the name before " of " and the first two
  words of a longer name); the holders of a head's office (king, emperor, president, prime minister, governor ...).
  A card row: int qid; byte kind (0 person, 1 company, 2 school, 3 paper, 4 party, 5 army, 6 society, 7 order);
  short fame (Wikipedia articles); str name; str line; short lineFrom (the first year the line may be said, -32768 =
  always: a line naming an office, a rank or an honour waits for it); str early (the part of the line that may be
  said before then, "" = none or the same);
  int from; int to (-2147483648 unknown); short known (the year people start to talk about it); byte flags (1 from is "around", 2 to is "around", 4 female, 8 male);
  int lat; int lon (thousandths of a degree); str home;
  people only: int deathLat; int deathLon (unknown -2147483648); str deathPlace; byte offices, each (int office,
  short from, short to; -32768 unknown); byte works, each (str title, short year);
  every card: byte links, each (byte role, int qid, short from, short to). Roles: 1 studied at, 2 party, 3 worked for,
  4 served in, 5 member of, 6 founded, 7 founded by.
"""
import collections
import gzip
import io
import hashlib
import json
import math
import os
import re
import struct
import sys
import unicodedata
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_tiles  # noqa: E402

RAW = os.path.join(HERE, "build", "cards", "raw")
WORK = os.path.join(HERE, "build", "cards")
DATA = os.path.normpath(os.path.join(HERE, "..", "eternal", "src", "main", "resources", "data", "eternalengine",
                                     "eternal"))
OUT = os.path.join(DATA, "cards", "cards.tiles")
MASTER_PEOPLE = os.path.join(DATA, "history", "famous_people.json.gz")
REPORT = os.path.join(HERE, "logs", "step27_cards_report.json")
UNKNOWN = -2147483648
SHORT_UNKNOWN = -32768
BOX = 5
PT = re.compile(r"POINT\(([-0-9.eE]+) ([-0-9.eE]+)\)")

# Who gets a card.
PEOPLE_FAME = 12        # every person with this many Wikipedia articles ...
PEOPLE_CAP = 300        # ... but at most this many per box and century
PEOPLE_FLOOR = 30       # and at least the best known this many per box and century
EARLIEST_BIRTH = -3500
ORG_KINDS = ["company", "school", "paper", "party", "army", "society", "order"]
ORG_PRIORITY = ["paper", "party", "army", "order", "society", "school", "company"]  # an organisation of two kinds
ORG_CAP = {"company": 20, "school": 20, "paper": 8, "party": 8, "army": 8, "society": 8, "order": 8}
ORG_FAME = {"company": 6, "school": 3, "paper": 2, "party": 2, "army": 2, "society": 2, "order": 2}
ORG_FLOOR = {"company": 3, "school": 3, "paper": 2, "party": 2, "army": 2, "society": 2, "order": 2}
KIND_CODE = {"person": 0, "company": 1, "school": 2, "paper": 3, "party": 4, "army": 5, "society": 6, "order": 7}

# What a card keeps.
MAX_OFFICES = 3
MAX_WORKS = 3
WORKS_FAME = 20
MAX_LINKS = 4
MAX_LINE = 140
FAMOUS_FAR_FAME = 50    # people known far and wide: group "f" (PlaceCards.FAMOUS_FAR_FAME)
MAX_TITLE = 60
ROLE = {"educated": 1, "party": 2, "employer": 3, "branch": 4, "member": 5, "founded": 6, "founder": 7}
ROLE_ORDER = ["founded", "party", "educated", "branch", "member", "employer"]
MALE, FEMALE = "Q6581097", "Q6581072"


# ------------------------------------------------------------------------------------------------ reading the exports

def qid_of(cell):
    """'<http://www.wikidata.org/entity/Q42>' -> 42 (0 for anything else)."""
    i = cell.rfind("/Q")
    if i < 0 or not cell.endswith(">"):
        return 0
    try:
        return int(cell[i + 2:-1])
    except ValueError:
        return 0


def year_of(cell):
    """A year as Wikidata's RDF writes it (year 0 = 1 BCE) -> the mod's years (-1 = 1 BCE, no year 0)."""
    if not cell:
        return None
    try:
        y = int(float(cell))
    except ValueError:
        return None
    return y - 1 if y <= 0 else y


def point(cell):
    m = PT.search(cell or "")
    if not m:
        return None
    lon, lat = float(m.group(1)), float(m.group(2))
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return round(lat, 3), round(lon, 3)


def literal(cell):
    """'"Galileo Galilei"@en' -> 'Galileo Galilei' (TSV escapes undone)."""
    if not cell:
        return ""
    s = cell
    if s.startswith('"'):
        j = s.rfind('"')
        s = s[1:j] if j > 0 else s[1:]
    return s.replace("\\t", " ").replace("\\n", " ").replace('\\"', '"').replace("\\\\", "\\").strip()


def rows(prefix):
    """Every row of build/cards/raw/<prefix>*.tsv.gz, header left out, as lists of cells."""
    return rows_in(RAW, prefix)


def rows_in(raw, prefix, required=True):
    """Every row of <raw>/<prefix>*.tsv.gz (step 28: the event exports use their own folder)."""
    names = sorted(n for n in os.listdir(raw) if n.startswith(prefix) and n.endswith(".tsv.gz")) if os.path.isdir(raw) \
        else []
    if not names:
        if not required:
            return
        raise SystemExit(f"no export {prefix}* in {raw}: run the fetch script first")
    for n in names:
        with gzip.open(os.path.join(raw, n), "rt", encoding="utf-8") as f:
            next(f, None)
            for line in f:
                yield line.rstrip("\n").split("\t")


def box_of(lat, lon):
    return math.floor((lat + 90.0) / BOX), math.floor((lon + 180.0) / BOX)


# ------------------------------------------------------------------------------------------------ choosing

def read_people_pool():
    people = {}
    for c in rows("pool_"):
        q = qid_of(c[0])
        p = point(c[4]) if len(c) > 4 else None
        if not q or p is None:
            continue
        k, by, dy = int(c[1]), year_of(c[2]), year_of(c[3])
        r = people.get(q)
        if r is None:
            people[q] = [k, by, dy, p[0], p[1]]
        else:
            if by is not None and (r[1] is None or by < r[1]):
                r[1] = by
            if dy is not None and (r[2] is None or dy > r[2]):
                r[2] = dy
    return people


def known_from(birth, death):
    """When people start to talk about somebody: at 30 (earlier with a dated office or work, see build())."""
    return birth + 30 if birth is not None else death - 40


def particular(office):
    """"President of the United States" before "professor": an office of some place or body."""
    return " of " in office or any(w[:1].isupper() for w in office.split()[1:])


def choose_people(pool):
    cells = collections.defaultdict(list)
    for q, (k, by, dy, lat, lon) in pool.items():
        if by is None and dy is None:
            continue
        if by is not None and (by > 2010 or by < EARLIEST_BIRTH):
            continue
        if by is not None and dy is not None and not (0 <= dy - by <= 120):
            continue  # an impossible life: one of the years is wrong; the dates are fetched again with precision
        cells[(box_of(lat, lon), known_from(by, dy) // 100)].append((-k, q))
    chosen = set()
    for key in sorted(cells):
        lst = sorted(cells[key])
        famous = [q for nk, q in lst if -nk >= PEOPLE_FAME][:PEOPLE_CAP]
        if len(famous) < PEOPLE_FLOOR:
            famous = [q for nk, q in lst[:PEOPLE_FLOOR]]
        chosen.update(famous)
    return chosen, len(cells)


def read_org_pool():
    orgs = {}
    for kind in ORG_KINDS:
        for c in rows(f"orgs_{kind}"):
            q = qid_of(c[0])
            if not q:
                continue
            k, iy = int(c[2]), year_of(c[3])
            prec = int(c[4]) if c[4] else 0
            dy = year_of(c[5]) if len(c) > 5 else None
            p1, p2, p3 = (point(c[i]) if len(c) > i else None for i in (6, 7, 8))
            p = p1 or p2 or p3
            r = orgs.get(q)
            if r is None:
                orgs[q] = {"k": k, "kind": kind, "iy": iy, "prec": prec, "dy": dy, "p": p}
                continue
            if ORG_PRIORITY.index(kind) < ORG_PRIORITY.index(r["kind"]):
                r["kind"] = kind
            if prec > r["prec"] or (prec == r["prec"] and iy is not None and (r["iy"] is None or iy < r["iy"])):
                r["iy"], r["prec"] = iy, prec
            if r["p"] is None and p:
                r["p"] = p
            if dy is not None and (r["dy"] is None or dy < r["dy"]):
                r["dy"] = dy
    return orgs


def choose_orgs(pool):
    cells = collections.defaultdict(lambda: collections.defaultdict(list))
    for q, r in pool.items():
        if r["p"] is None or r["iy"] is None or r["prec"] < 8 or r["iy"] > 2026 or r["iy"] < -3500:
            continue
        if r["dy"] is not None and r["dy"] < r["iy"]:
            continue
        cells[(box_of(*r["p"]), r["iy"] // 100)][r["kind"]].append((-r["k"], q))
    chosen = set()
    for key in sorted(cells):
        for kind, lst in sorted(cells[key].items()):
            lst.sort()
            take = [q for nk, q in lst if -nk >= ORG_FAME[kind]][:ORG_CAP[kind]]
            if len(take) < ORG_FLOOR[kind]:
                take = [q for nk, q in lst[:ORG_FLOOR[kind]]]
            chosen.update(take)
    return chosen


def select():
    os.makedirs(WORK, exist_ok=True)
    pool = read_people_pool()
    people, cells = choose_people(pool)
    orgpool = read_org_pool()
    orgs = choose_orgs(orgpool)
    with open(os.path.join(WORK, "chosen_people.txt"), "w") as f:
        f.writelines(f"Q{q}\n" for q in sorted(people))
    with open(os.path.join(WORK, "chosen_orgs.txt"), "w") as f:
        f.writelines(f"Q{q}\n" for q in sorted(orgs))
    keep = {str(q): pool[q] for q in people}
    keep_o = {str(q): orgpool[q] for q in orgs}
    with open(os.path.join(WORK, "chosen_pool.json.gz"), "wb") as _gzraw, \
            gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, \
            io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as f:
        json.dump({"people": keep, "orgs": keep_o, "peoplePool": len(pool), "orgPool": len(orgpool),
                   "cells": cells}, f)
    kinds = collections.Counter(orgpool[q]["kind"] for q in orgs)
    print(f"people: {len(pool):,} in the pool, {len(people):,} chosen ({cells} boxes and centuries)")
    print(f"organisations: {len(orgpool):,} in the pool, {len(orgs):,} chosen: " +
          ", ".join(f"{k} {kinds[k]:,}" for k in ORG_KINDS))


def positions():
    seen = collections.Counter()
    for c in rows("offices_"):
        pos = qid_of(c[1])
        if pos:
            seen[pos] += 1
    with open(os.path.join(WORK, "positions.txt"), "w") as f:
        f.writelines(f"Q{q}\n" for q in sorted(seen))
    linked = set()
    chosen_o = {int(x[1:]) for x in open(os.path.join(WORK, "chosen_orgs.txt")).read().split()}
    for c in rows("links_"):
        o = qid_of(c[2])
        if o and o not in chosen_o:
            linked.add(o)
    works = set()
    for c in rows("works_"):
        w = qid_of(c[1])
        if w:
            works.add(w)
    with open(os.path.join(WORK, "works.txt"), "w") as f:
        f.writelines(f"Q{q}\n" for q in sorted(works))
    print(f"{len(seen):,} offices held by the chosen people; {len(linked):,} linked organisations without a card;"
          f" {len(works):,} works")


def place_list():
    """Every place named on a card (birthplaces, death places, seats), for fetch_cards_wd.py places."""
    out = set()
    for c in rows("places_"):
        for i in (2, 4):
            if len(c) > i and qid_of(c[i]):
                out.add(qid_of(c[i]))
    for c in rows("orgseat_"):
        for i in (1, 2):
            if len(c) > i and qid_of(c[i]):
                out.add(qid_of(c[i]))
    with open(os.path.join(WORK, "places.txt"), "w") as f:
        f.writelines(f"Q{q}\n" for q in sorted(out))
    print(f"{len(out):,} places named on cards")


def class_list():
    out = set()
    for c in rows("placekind_"):
        if len(c) > 2 and qid_of(c[2]):
            out.add(qid_of(c[2]))
    with open(os.path.join(WORK, "classes.txt"), "w") as f:
        f.writelines(f"Q{q}\n" for q in sorted(out))
    print(f"{len(out):,} kinds of places")


# ------------------------------------------------------------------------------------------------ building

YEAR_IN_TEXT = re.compile(r"(?<![\d.,])(\d{3,4})(?![\d,])")
PAREN_DIGITS = re.compile(r"\s*[\(\[][^\)\]]*\d[^\)\]]*[\)\]]")
TRAIL_BORN = re.compile(r",?\s*\b(born|died|b\.|d\.|fl\.|floruit|active)\s+(in\s+|c\.\s*|circa\s+|around\s+)?\d.*$",
                        re.IGNORECASE)
LEADING = re.compile(r"^(former|ex-|late)\s+", re.IGNORECASE)
_ERA = r"(\s*(BCE|BC|CE|AD|B\.C\.|A\.D\.))?"
YEAR_SPANS = [
    re.compile(r"\s+(from|between)\s+(c\.\s*|circa\s+|about\s+)?\d{1,4}" + _ERA +
               r"\s+(to|and|until|till|-|\u2013)\s+(c\.\s*|circa\s+|about\s+)?\d{1,4}" + _ERA, re.IGNORECASE),
    re.compile(r",?\s+(c\.\s*)?\d{3,4}" + _ERA + r"\s*[\u2013-]\s*(c\.\s*)?\d{2,4}" + _ERA +
               r"(\s+and\s+(again\s+)?(in\s+)?\d{3,4})?", re.IGNORECASE),
    re.compile(r"\s+(since|from|until|till|in)\s+(c\.\s*)?\d{3,4}" + _ERA + r"\b", re.IGNORECASE),
]


SOURCE_WORDS = re.compile(r"wiki", re.IGNORECASE)


def clean_line(text):
    """A Wikidata description made fit to be said at any date: no "(1564-1642)", no "born 1950", no "former".
    No source names either (turn 56): "co-founder of Wikipedia" says "an online encyclopedia"."""
    s = " ".join((text or "").split())
    s = re.sub(r"\bWikipedia\b", "an online encyclopedia", s)
    if SOURCE_WORDS.search(s):
        return ""
    s = PAREN_DIGITS.sub("", s)
    s = TRAIL_BORN.sub("", s)
    for span in YEAR_SPANS:  # "queen of the United Kingdom from 1837 to 1901": the years come from the office
        s = span.sub("", s)
    s = LEADING.sub("", s)
    s = s.strip(" ,;:-\u2013\u2014")
    if len(s) > MAX_LINE:
        cut = s.rfind(",", 0, MAX_LINE)
        if cut < 30:
            cut = s.rfind(" ", 0, MAX_LINE)
        s = s[:cut].rstrip(" ,;:")
        words = s.split(" ")
        while len(words) > 3 and words[-1].lower() in STOP_TAIL:
            words.pop()
        s = " ".join(words).rstrip(" ,;:")
    if s and s[0].isupper() and len(s) > 1 and s.split(" ")[0].lower() in COMMON_FIRST:
        s = s[0].lower() + s[1:]
    return s


# Words Wikidata sometimes capitalises at the start of a description; they are lowered so that "is a painter" reads well.
COMMON_FIRST = {"painter", "writer", "poet", "politician", "actor", "actress", "singer", "composer", "king", "queen",
                "emperor", "empress", "philosopher", "scientist", "physician", "author", "artist", "architect",
                "university", "company", "newspaper", "political", "public", "private", "school", "college"}


# Words that tie a description to a time of life: an office, a rank, a deed, a later honour (step 27). A line with one
# of them is said only from the year it became true: the start of a matching office, the year written in it, the
# death (for "saint" and the like), or, with nothing better, from age 45.
TITLE_WORDS = re.compile(
    r"\b(president|vice[- ]president|king|queen|emperor|empress|prime minister|premier|chancellor|governor|pope|sultan|"
    r"sultana|shah|caliph|khagan|khan|pharaoh|tsar|czar|tsarina|monarch|ruler|regent|dictator|minister|senator|mayor|"
    r"general|admiral|marshal|commander|founder|co-founder|cofounder|winner|laureate|champion|medalist|medallist|"
    r"olympic|nobel|first|leader of|head of|chairman|chairwoman|chair of|ceo|director of|member of|deputy|ambassador|"
    r"bishop|archbishop|cardinal|patriarch|abbot|abbess|consul|tribune|doge|vizier|wazir|nawab|nizam|maharaja|raja|"
    r"rajah|emir|amir|chief justice|justice of|secretary of|secretary-general|general secretary|secretary general|"
    r"speaker of|viceroy|shogun|grand master|mufti|imam|lord mayor|inventor of|discoverer of|author of|creator of|"
    r"\d+(st|nd|rd|th)(?![- ]century)(?![- ]millennium))\b", re.IGNORECASE)
# Any of these in a line matches any of them in an office ("queen of Egypt" and the office "pharaoh").
RULER_WORDS = {"king", "queen", "emperor", "empress", "pharaoh", "monarch", "sultan", "sultana", "shah", "tsar", "czar",
               "tsarina", "caliph", "khan", "khagan", "ruler", "regent", "maharaja", "raja", "rajah", "emir", "amir",
               "nawab", "nizam", "shogun", "doge", "sovereign", "prince", "princess", "duke", "duchess", "count",
               "elector", "basileus", "negus"}
NOT_A_LIFE = re.compile(r"\b(mummy|mummies|skeleton|skull|fossil|remains|bog body)\b", re.IGNORECASE)
AFTER_DEATH = re.compile(r"\b(saint|blessed|venerable|martyr)\b", re.IGNORECASE)


def line_parts(line):
    return [x.strip() for x in re.split(r",\s*|;\s*", line) if x.strip()]


def safe_from(line, offices, birth, death, office_names):
    """(the first year the whole line may be said, or None for always; the part that may always be said)."""
    if not line:
        return None, ""
    early = []
    worst = None
    for part in line_parts(line):
        when = None
        ly = line_year(part)
        if ly:
            when = ly
        words = {m.group(0).lower() for m in TITLE_WORDS.finditer(part)}
        if words:
            starts = []
            rulers = any(w in RULER_WORDS for w in words)
            for pos, fy, ty in offices:
                label = office_names.get(pos, "").lower()
                if fy is None:
                    continue
                label_words = set(re.findall(r"[a-z]+", label))
                if any(w in label for w in words if not w[0].isdigit()) or (rulers and label_words & RULER_WORDS):
                    starts.append(fy)
            if starts:
                w = min(starts)
            elif death is not None:
                w = death
            elif birth is not None:
                w = birth + 45
            else:
                w = 32767
            when = max(when, w) if when is not None else w
        if AFTER_DEATH.search(part):
            w = death if death is not None else 32767
            when = max(when, w) if when is not None else w
        if when is None:
            early.append(part)
        else:
            worst = when if worst is None else max(worst, when)
    early_text = ", ".join(early)
    if worst is None:
        return None, ""
    return worst, ("" if early_text == line else early_text)


STOP_TAIL = {"in", "of", "the", "a", "an", "and", "at", "by", "for", "with", "from", "to", "on", "or", "who", "which",
             "that", "as"}


# Offices of the heads of states and governments, whose holders "who rules here?" names (group "n").
HEAD_WORDS = re.compile(
    r"\b(king|queen|emperor|empress|pharaoh|monarch|sultan|sultana|shah|tsar|czar|tsarina|caliph|khan|khagan|ruler|"
    r"regent|maharaja|raja|rajah|emir|amir|nawab|nizam|shogun|doge|sovereign|prince|princess|duke|duchess|count|"
    r"elector|grand duke|archduke|president|prime minister|premier|chancellor|governor|general secretary|"
    r"first secretary|chairman|pope|patriarch|dictator|consul|viceroy|head of state|head of government|"
    r"supreme leader|leader|taoiseach|stadtholder|tenno|basileus|negus|sapa inca|tlatoani|mansa|oba|kabaka)\b",
    re.IGNORECASE)


def name_variants(name):
    """The plain name, the name before " of " ("Louis XVI of France" -> "Louis XVI") and its first two words when it has
    three or more ("Cosimo II de' Medici" -> "Cosimo II"): the registers name rulers in these ways."""
    plain = norm_name(name)
    out = [plain]
    raw = name.split(" of ")[0].strip()
    if " of " in name and raw:
        out.append(norm_name(raw))
    words = plain.split(" ")
    if len(words) >= 3:
        out.append(" ".join(words[:2]))
    seen, keep = set(), []
    for v in out:
        if v and v not in seen:
            seen.add(v)
            keep.append(v)
    return keep


def name_hash(name, plain=False):
    """FNV-1a (32 bits, signed) of the name made plain (CardStore.nameHash does the same in Java)."""
    h = 0x811C9DC5
    for b in (name if plain else norm_name(name)).encode("utf-8"):
        h ^= b
        h = (h * 0x01000193) & 0xFFFFFFFF
    return h - (1 << 32) if h >= (1 << 31) else h


def line_year(text):
    best = 0
    for m in YEAR_IN_TEXT.finditer(text or ""):
        y = int(m.group(1))
        if 1000 <= y <= 2100 and y > best:
            best = y
    return best


def norm_name(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def pick_dates(values):
    """Wikidata may give several dates: the most precise first, then the earliest. Returns (year, around, spread)."""
    if not values:
        return None, False, 0
    best_prec = max(p for y, p in values)
    good = sorted(y for y, p in values if p == best_prec)
    year = good[0]
    years = {y for y, p in values if p >= 9}
    spread = (max(years) - min(years)) if years else 0
    around = best_prec < 9 or spread > 1
    return year, around, spread


def s16(text):
    return build_tiles.s16(text)


def short(v):
    if v is None:
        return SHORT_UNKNOWN
    return max(-32767, min(32767, int(v)))


def varint(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def load_master_people():
    """name -> [(birth, death), ...] from the famous people master (the Wikipedia year pages)."""
    with gzip.open(MASTER_PEOPLE, "rt", encoding="utf-8") as f:
        doc = json.load(f)
    out = collections.defaultdict(list)
    for r in doc["people"]:
        out[norm_name(r[0])].append((r[2], r[3]))
    return out


def build():
    with gzip.open(os.path.join(WORK, "chosen_pool.json.gz"), "rt", encoding="utf-8") as f:
        pool = json.load(f)
    people = {int(q): r for q, r in pool["people"].items()}
    orgs = {int(q): r for q, r in pool["orgs"].items()}
    report = collections.Counter()

    # Names and descriptions.
    names, lines = {}, {}
    for prefix in ("names_p_", "names_o_", "names_pos_"):
        for c in rows(prefix):
            q = qid_of(c[0])
            if q and q not in names:
                names[q] = literal(c[1])
                lines[q] = literal(c[2]) if len(c) > 2 else ""

    # Dates with their precision.
    births, deaths = collections.defaultdict(list), collections.defaultdict(list)
    for prefix, target in (("dates_b_", births), ("dates_d_", deaths)):
        for c in rows(prefix):
            q, y = qid_of(c[0]), year_of(c[1])
            if q and y is not None and c[2]:
                target[q].append((y, int(c[2])))

    # Gender.
    gender = {}
    for c in rows("places_"):
        q = qid_of(c[0])
        g = c[1].rsplit("/", 1)[-1].rstrip(">") if q and c[1] else ""
        if g and q not in gender:
            gender[q] = g

    # Offices: the most particular ones (fewest holders) first.
    holders = {}
    for c in rows("holders_"):
        q = qid_of(c[0])
        if q:
            holders[q] = int(c[1])
    offices = collections.defaultdict(dict)
    for c in rows("offices_"):
        q, pos = qid_of(c[0]), qid_of(c[1])
        if not q or not pos or not names.get(pos) or re.fullmatch(r"Q\d+", names[pos]):
            continue
        fy, ty = year_of(c[2]), year_of(c[3]) if len(c) > 3 else None
        old = offices[q].get(pos)
        if old is None or (fy is not None and (old[0] is None or fy < old[0])):
            offices[q][pos] = (fy, ty if ty is not None else (old[1] if old else None))
        elif ty is not None and (old[1] is None or ty > old[1]):
            offices[q][pos] = (old[0], ty)

    # Memberships (only to organisations that have a card).
    links = collections.defaultdict(dict)
    for c in rows("links_"):
        q, o = qid_of(c[0]), qid_of(c[2])
        role = literal(c[1])
        if not q or o not in orgs or role not in ROLE:
            continue
        fy, ty = year_of(c[3]) if len(c) > 3 else None, year_of(c[4]) if len(c) > 4 else None
        links[q].setdefault((role, o), (fy, ty))

    # Works with a year.
    works = collections.defaultdict(dict)
    for c in rows("works_"):
        q, w = qid_of(c[0]), qid_of(c[1])
        title = literal(c[2])
        y = year_of(c[3]) if len(c) > 3 and c[3] else (year_of(c[4]) if len(c) > 4 else None)
        if not q or not w or not title or y is None or len(title) > MAX_TITLE or re.fullmatch(r"Q\d+", title):
            continue
        if SOURCE_WORDS.search(title):
            continue  # no source names (turn 56)
        old = works[q].get(w)
        if old is None or y < old[1]:
            works[q][w] = (title, y, w)

    # Founders.
    founders = collections.defaultdict(set)
    for c in rows("orgplace_"):
        o = qid_of(c[0])
        f = qid_of(c[3]) if o and len(c) > 3 else 0
        if f:
            founders[o].add(f)

    master = load_master_people()

    # Place names: a town keeps its own name; a building, a hospital or a river is named by what it lies in.
    town_classes = {qid_of(c[0]) for c in rows("townclass_")}
    place_label, place_town, place_up = {}, {}, {}
    for c in rows("placekind_"):
        x = qid_of(c[0])
        if not x:
            continue
        if len(c) > 1 and c[1] and x not in place_label:
            place_label[x] = literal(c[1])
        if len(c) > 2 and qid_of(c[2]) in town_classes:
            place_town[x] = True
        if len(c) > 4 and c[4] and x not in place_up:
            place_up[x] = literal(c[4])

    def nice(label):
        letters = [ch for ch in label if ch.isalpha()]
        if len(letters) >= 4 and all(ch.isupper() for ch in letters):
            return label.title()  # "CHHATRAPATI SHIVAJI MAHARAJ" was typed in capitals
        return label

    def place_name(x, fallback=""):
        if not x:
            return nice(fallback)
        label = place_label.get(x, fallback)
        if place_town.get(x):
            return nice(label)
        if place_up.get(x):
            return nice(place_up[x])
        return "" if x in place_label or x in place_town else nice(label)  # a road or a building, nothing around it

    home_name, death_place = {}, {}
    for c in rows("places_"):
        q = qid_of(c[0])
        if not q:
            continue
        bp = qid_of(c[2]) if len(c) > 2 else 0
        if bp and (q not in home_name or (place_town.get(bp) and not home_name[q][1])):
            home_name[q] = (place_name(bp, literal(c[3]) if len(c) > 3 else ""), bool(place_town.get(bp)))
        if len(c) > 6 and c[6]:
            p = point(c[6])
            dp = qid_of(c[4])
            if p and q not in death_place:
                death_place[q] = (p[0], p[1], place_name(dp, literal(c[5])))
    home_name = {q: v[0] for q, v in home_name.items()}
    seat_name = {}
    for c in rows("orgseat_"):
        o = qid_of(c[0])
        if not o or o in seat_name:
            continue
        hq = qid_of(c[1]) if len(c) > 1 else 0
        ad = qid_of(c[2]) if len(c) > 2 else 0
        name = place_name(hq) if hq else place_name(ad) if ad else ""
        if name:
            seat_name[o] = name
    fame_of = {}
    for prefix in ("fame_pos_", "fame_work_"):
        for c in rows(prefix):
            x = qid_of(c[0])
            if x:
                fame_of[x] = int(c[1])

    # The person cards.
    cards = {}
    named = set()  # people a name can find (group "n"): everyone with an office (rulers) and the very famous
    for q in sorted(people):
        k, by0, dy0, lat, lon = people[q]
        name = names.get(q, "")
        if not name or re.fullmatch(r"Q\d+", name):
            report["people without an English name"] += 1
            continue
        by, b_around, b_spread = pick_dates(births.get(q))
        dy, d_around, d_spread = pick_dates(deaths.get(q))
        if by is None and births.get(q) is None:
            by = by0
        if dy is None and deaths.get(q) is None:
            dy = dy0
        # Cross-check with the Wikipedia year pages: same name and one year the same.
        cand = master.get(norm_name(name), [])
        match = None
        for mb, md in cand:
            if (by is not None and mb == by) or (dy is not None and md == dy):
                match = (mb, md)
                break
        if match is not None:
            report["cross-checked with the year pages"] += 1
            mb, md = match
            if by is not None and mb is not None and mb != by:
                if abs(mb - by) > 1:
                    report["birth year taken from the year pages"] += 1
                by, b_around = mb, False
            if dy is not None and md is not None and md != dy:
                if abs(md - dy) > 1:
                    report["death year taken from the year pages"] += 1
                dy, d_around = md, False
            if by is None and mb is not None:
                by = mb
            if dy is None and md is not None:
                dy = md
        if by is None and dy is None:
            report["people without a usable year"] += 1
            continue
        if by is not None and dy is not None and not (0 <= dy - by <= 120):
            report["people with an impossible life left out"] += 1
            continue
        if by is not None and by > 2010:
            continue
        if NOT_A_LIFE.search(lines.get(q, "")):
            report["remains and mummies left out"] += 1  # Ötzi is "a well-preserved natural mummy"
            continue
        if b_around or d_around:
            report["people with a year given as around"] += 1
        g = gender.get(q, "")
        flags = (1 if b_around else 0) | (2 if d_around else 0) | (4 if g == FEMALE else 0) | (8 if g == MALE else 0)
        line = clean_line(lines.get(q, ""))
        all_offs = [(pos, fy, ty) for pos, (fy, ty) in offices.get(q, {}).items()
                    if "-elect" not in names[pos].lower() and " elect" not in names[pos].lower()]
        offs = sorted(all_offs, key=lambda o: (0 if particular(names[o[0]]) else 1, -fame_of.get(o[0], 0),
                                               o[1] if o[1] is not None else 99999, o[0]))[:MAX_OFFICES]
        all_works = sorted(works.get(q, {}).values(), key=lambda t: (t[1], t[0]))
        if dy is not None:
            all_works = [w for w in all_works if w[1] <= dy + 30]
        if by is not None:
            all_works = [w for w in all_works if w[1] >= by]
        wks = []
        if k >= WORKS_FAME:
            wks = [(t, y) for t, y, w in sorted(all_works, key=lambda t: (-fame_of.get(t[2], 0), t[1], t[0]))]
            wks = wks[:MAX_WORKS]
        first_deed = min([fy for pos, fy, ty in all_offs if fy is not None] + [y for t, y, w in all_works],
                         default=None)
        kf = known_from(by, dy)
        if first_deed is not None and by is not None and by + 5 <= first_deed < kf:
            kf = first_deed
        dp = death_place.get(q)
        lf, early = safe_from(line, all_offs, by, dy, names)
        if lf is not None:
            report["people whose line waits for its year"] += 1
        if any(HEAD_WORDS.search(names.get(pos, "")) for pos, fy, ty in all_offs):
            named.add(q)
        cards[q] = {"kind": 0, "fame": k, "name": name, "line": line, "lineFrom": lf, "early": early,
                    "from": by, "to": dy, "flags": flags,
                    "lat": lat, "lon": lon, "home": home_name.get(q, ""), "death": dp, "offices": offs,
                    "works": wks, "links": [], "known": kf}

    # The organisation cards. A "company" that is really a town (a municipal corporation counts as a business in
    # Wikidata: Walla Walla, Schweinfurt, Kyoto) is left out.
    towns_as_orgs = {qid_of(c[0]) for c in rows("orgtown_")}
    for o in sorted(orgs):
        r = orgs[o]
        name = names.get(o, "")
        if not name or re.fullmatch(r"Q\d+", name):
            report["organisations without an English name"] += 1
            continue
        if o in towns_as_orgs and r["kind"] in ("company", "party", "society", "order"):
            report["towns and lands left out of the organisations"] += 1
            continue
        if SOURCE_WORDS.search(name):
            continue  # no source names (turn 56)
        lat, lon = r["p"]
        flags = 1 if r["prec"] < 9 else 0
        line = clean_line(lines.get(o, ""))
        ly = line_year(line)
        cards[o] = {"kind": KIND_CODE[r["kind"]], "fame": r["k"], "name": name, "line": line,
                    "lineFrom": ly if ly else None, "early": "",
                    "from": r["iy"], "to": r["dy"], "flags": flags, "lat": lat, "lon": lon,
                    "home": seat_name.get(o, ""), "links": [], "known": r["iy"]}

    # Links both ways between the cards that exist.
    for q in sorted(links):
        if q not in cards:
            continue
        for (role, o), (fy, ty) in sorted(links[q].items(), key=lambda kv: (ROLE_ORDER.index(kv[0][0]), kv[0][1])):
            if o in cards:
                cards[q]["links"].append((ROLE[role], o, fy, ty))
    for o in sorted(founders):
        if o not in cards:
            continue
        for f in sorted(founders[o]):
            if f in cards and cards[f]["kind"] == 0:
                cards[o]["links"].append((ROLE["founder"], f, None, None))
                cards[f]["links"].insert(0, (ROLE["founded"], o, cards[o]["from"], None))
                report["founders linked"] += 1
    for q, cd in cards.items():
        seen, kept = set(), []
        for ln in cd["links"]:
            if ln[1] not in seen:
                seen.add(ln[1])
                kept.append(ln)
        cd["links"] = kept[:MAX_LINKS]

    # The office names used.
    vocab = sorted({pos for cd in cards.values() if cd["kind"] == 0 for pos, fy, ty in cd["offices"]})
    vindex = {pos: i for i, pos in enumerate(vocab)}

    # Rows, by box and century.
    groups = {}
    order = sorted(cards, key=lambda q: (-cards[q]["fame"], q))
    for q in order:
        cd = cards[q]
        raw = bytearray()
        raw += struct.pack(">ibh", q, cd["kind"], min(32767, cd["fame"]))
        raw += s16(cd["name"]) + s16(cd["line"]) + struct.pack(">h", short(cd["lineFrom"])) + s16(cd["early"])
        raw += struct.pack(">ii", UNKNOWN if cd["from"] is None else cd["from"], UNKNOWN if cd["to"] is None else cd["to"])
        raw += struct.pack(">h", short(cd["known"]))
        raw += struct.pack(">b", cd["flags"])
        ilat, ilon = round(cd["lat"] * 1000), round(cd["lon"] * 1000)
        raw += struct.pack(">ii", ilat, ilon) + s16(cd["home"])
        if cd["kind"] == 0:
            dp = cd["death"]
            if dp:
                raw += struct.pack(">ii", round(dp[0] * 1000), round(dp[1] * 1000)) + s16(dp[2])
            else:
                raw += struct.pack(">ii", UNKNOWN, UNKNOWN) + s16("")
            raw += struct.pack(">b", len(cd["offices"]))
            for pos, fy, ty in cd["offices"]:
                raw += struct.pack(">ihh", vindex[pos], short(fy), short(ty))
            raw += struct.pack(">b", len(cd["works"]))
            for title, y in cd["works"]:
                raw += s16(title) + struct.pack(">h", short(y))
        raw += struct.pack(">b", len(cd["links"]))
        for role, o, fy, ty in cd["links"]:
            raw += struct.pack(">bihh", role, o, short(fy), short(ty))
        by, bx = box_of(cd["lat"], cd["lon"])
        groups.setdefault(f"b/{by}/{bx}", {}).setdefault(cd["known"] // 100, []).append((q, bytes(raw)))

    # Group "f": the people known far and wide, in short rows (int qid, int lat, int lon, short fame, short known,
    # int from, int to, str name), by the century they became known; a quiet land hears of them (PlaceCards).
    far = {}
    for q in order:
        cd = cards[q]
        if cd["kind"] == 0 and cd["fame"] >= FAMOUS_FAR_FAME:
            far.setdefault(cd["known"] // 100, []).append(struct.pack(
                ">iiihhii", q, round(cd["lat"] * 1000), round(cd["lon"] * 1000), min(32767, cd["fame"]),
                short(cd["known"]), UNKNOWN if cd["from"] is None else cd["from"], UNKNOWN if cd["to"] is None else cd["to"])
                + s16(cd["name"]))
    # Group "n": names, for "who rules here?" to find the ruler's card: int n, then n (int hash, int qid) by hash.
    pairs = sorted({(name_hash(v, plain=True), q) for q in named if q in cards for v in name_variants(cards[q]["name"])})
    name_raw = struct.pack(">i", len(pairs)) + b"".join(struct.pack(">ii", h, q) for h, q in pairs)

    # Tile numbers for the index: build_tiles.write_tiles packs whole buckets into tiles of MIN_ROWS rows or more,
    # in the order of the sorted groups; the same packing is done here to know each card's tile.
    vocab_raw = struct.pack(">i", len(vocab)) + b"".join(s16(names[pos]) for pos in vocab)
    tile_of = {}
    plain = {}
    tile_no = 0
    plain["f"] = far
    all_groups = sorted(list(groups) + ["f", "i", "n", "v"])
    for g in all_groups:
        if g in ("i", "n", "v"):
            tile_no += 1
            continue
        if g == "f":
            buckets = {b: [(0, raw) for raw in rs] for b, rs in far.items()}
        else:
            buckets = groups[g]
        keys = sorted(buckets)
        cur, members = 0, []
        for i, bucket in enumerate(keys):
            members += [q for q, raw in buckets[bucket]]
            cur += len(buckets[bucket])
            if cur >= build_tiles.MIN_ROWS or i == len(keys) - 1:
                if g != "f":
                    for q in members:
                        tile_of[q] = tile_no
                tile_no += 1
                cur, members = 0, []
        if g != "f":
            plain[g] = {b: [raw for q, raw in groups[g][b]] for b in keys}
    qs = sorted(tile_of)
    idx = bytearray(struct.pack(">i", len(qs)))
    prev = 0
    for q in qs:
        idx += varint(q - prev)
        prev = q
    for q in qs:
        idx += varint(tile_of[q])
    plain["i"] = {0: [bytes(idx)]}
    plain["v"] = {0: [vocab_raw]}
    plain["n"] = {0: [name_raw]}
    report["people known far and wide"] = sum(len(v) for v in far.values())
    report["people a name can find"] = len(pairs)

    kinds = collections.Counter(cd["kind"] for cd in cards.values())
    meta = {"people": kinds[0], "organisations": sum(v for k, v in kinds.items() if k > 0), "offices": len(vocab),
            "box": BOX, "minRows": build_tiles.MIN_ROWS, "fame": PEOPLE_FAME, "cap": PEOPLE_CAP,
            "floor": PEOPLE_FLOOR, "source": "Wikidata (CC0), cross-checked with the Wikipedia year pages",
            "kinds": ",".join(f"{k}:{kinds[k]}" for k in sorted(kinds))}
    for k in sorted(kinds):
        meta[f"kind{k}"] = kinds[k]
    digest = hashlib.sha256()
    for q in qs:
        digest.update(struct.pack(">i", q))
    data = build_tiles.write_tiles("cards", digest.hexdigest(), len(cards), meta, plain)
    # The tile count must agree with the numbering above.
    store_tiles = len(iter_tiles(data)[0])
    assert store_tiles == tile_no, (store_tiles, tile_no)

    report["people cards"] = kinds[0]
    report["organisation cards"] = meta["organisations"]
    report["offices named"] = len(vocab)
    report["people with offices"] = sum(1 for cd in cards.values() if cd["kind"] == 0 and cd["offices"])
    report["people with works"] = sum(1 for cd in cards.values() if cd["kind"] == 0 and cd["works"])
    report["cards with links"] = sum(1 for cd in cards.values() if cd["links"])
    report["people with a death place"] = sum(1 for cd in cards.values() if cd["kind"] == 0 and cd["death"])
    report["cards without a description"] = sum(1 for cd in cards.values() if not cd["line"])
    return data, dict(sorted(report.items())), meta


def iter_tiles(data):
    """(tiles, blob offset): every tile of a tile file as (group, first, last, offset, length, rawLength, rows)."""
    pos = 8

    def rd_str():
        nonlocal pos
        n = struct.unpack_from(">H", data, pos)[0]
        pos += 2
        s = data[pos:pos + n].decode("utf-8")
        pos += n
        return s

    rd_str()
    rd_str()
    pos += 4
    metas = struct.unpack_from(">i", data, pos)[0]
    pos += 4
    for _ in range(metas):
        rd_str()
        rd_str()
    groups = struct.unpack_from(">i", data, pos)[0]
    pos += 4
    tiles = []
    for _ in range(groups):
        g = rd_str()
        n = struct.unpack_from(">i", data, pos)[0]
        pos += 4
        for _ in range(n):
            tiles.append((g,) + struct.unpack_from(">iiiiii", data, pos))
            pos += 24
    blob_len = struct.unpack_from(">i", data, pos)[0]
    assert pos + 4 + blob_len == len(data), "the blob length does not match the file"
    return tiles, pos + 4


def check():
    if not os.path.exists(OUT):
        print("cards.tiles: missing")
        return 1
    data = open(OUT, "rb").read()
    tiles, blob_at = iter_tiles(data)
    by_group = collections.defaultdict(list)
    for i, t in enumerate(tiles):
        by_group[t[0]].append((i, t))
    problems = 0
    idx_tile = by_group["i"][0][1]
    raw = zlib.decompress(data[blob_at + idx_tile[3]: blob_at + idx_tile[3] + idx_tile[4]])
    n = struct.unpack_from(">i", raw, 0)[0]
    pos, qs, prev = 4, [], 0
    for _ in range(n):
        v, shift = 0, 0
        while True:
            b = raw[pos]
            pos += 1
            v |= (b & 0x7F) << shift
            shift += 7
            if not b & 0x80:
                break
        prev += v
        qs.append(prev)
    tile_nos = []
    for _ in range(n):
        v, shift = 0, 0
        while True:
            b = raw[pos]
            pos += 1
            v |= (b & 0x7F) << shift
            shift += 7
            if not b & 0x80:
                break
        tile_nos.append(v)
    found = collections.defaultdict(set)
    rows_seen = 0
    for i, t in enumerate(tiles):
        if not t[0].startswith("b/"):
            continue
        body = zlib.decompress(data[blob_at + t[3]: blob_at + t[3] + t[4]])
        if len(body) != t[5]:
            problems += 1
        p = 0
        cnt = 0
        while p < len(body):
            q, kind = struct.unpack_from(">ib", body, p)
            p = skip_row(body, p)
            found[i].add(q)
            cnt += 1
        if cnt != t[6]:
            print(f"tile {i}: {cnt} rows, the index says {t[6]}")
            problems += 1
        rows_seen += cnt
    missing = sum(1 for q, tn in zip(qs, tile_nos) if q not in found.get(tn, ()))
    if missing:
        print(f"{missing} cards are not in the tile the index names")
        problems += 1
    print(f"cards.tiles: {len(data):,} bytes, {len(tiles)} tiles, {rows_seen:,} cards, index {n:,}"
          f" -> {'OK' if not problems and rows_seen == n else 'PROBLEMS'}")
    return 0 if not problems and rows_seen == n else 1


def skip_row(b, p):
    def sk_str(p):
        return p + 2 + struct.unpack_from(">H", b, p)[0]
    q, kind, fame = struct.unpack_from(">ibh", b, p)
    p += 7
    p = sk_str(p)
    p = sk_str(p)
    p += 2
    p = sk_str(p)
    p += 8 + 2 + 1 + 8
    p = sk_str(p)
    if kind == 0:
        p += 8
        p = sk_str(p)
        n = b[p]
        p += 1 + n * 8
        n = b[p]
        p += 1
        for _ in range(n):
            p = sk_str(p) + 2
    n = b[p]
    p += 1 + n * 9
    return p


def main(argv):
    if "--select" in argv:
        select()
        return 0
    if "--positions" in argv:
        positions()
        return 0
    if "--places" in argv:
        place_list()
        return 0
    if "--classes" in argv:
        class_list()
        return 0
    if "--check" in argv:
        return check()
    if "--build" in argv:
        data, report, meta = build()
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "wb") as f:
            f.write(data)
        os.makedirs(os.path.dirname(REPORT), exist_ok=True)
        with open(REPORT, "w") as f:
            json.dump({"file": "cards/cards.tiles", "bytes": len(data), "meta": meta, "report": report}, f, indent=1)
        print(f"cards.tiles: {len(data):,} bytes")
        for k, v in report.items():
            print(f"  {k}: {v:,}")
        return check()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
