import io
#!/usr/bin/env python3
"""Step 6.2: who ruled, what people spoke and believed, for every state the mod knows.

Writes history/polity_facts.json.gz, read by the mod's LeaderRegister (not a gazetteer pack,
so it is not listed in index.json). One entry per Cliopatria state (Wikidata id), the same ids
RulerRegister answers with, so "which state rules this spot in this year" leads straight here.

Sources, all already in the workspace (no new downloads):
  * the state's own Wikipedia infobox (cached by probe_polity_infoboxes.py from the 2026-10-01
    dump): common/official languages, religion, capital, leaderN + year_leaderN (head of state),
    deputyN + year_deputyN (head of government, e.g. grand vizier, prime minister);
  * accession lines on the Wikipedia year pages that are already events in the mod
    ("Peter I becomes King of Portugal", "Dan I succeeds his father Radu as Prince of
    Wallachia"): each line is tied to the state ruling the spot it was placed at, and a reign
    lasts until the next accession to the same title (at most 50 years; a recorded death of
    that person ends it sooner).

Rules:
  * A reign is only claimed inside its years. Between two known reigns the mod says nothing
    about a name rather than guess one.
  * Per state, accession chains of lesser titles (a duke inside a kingdom) are dropped when the
    same state has a chain of a higher title, so the King of France is not replaced by the Duke
    of Burgundy just because Burgundy lay inside France.
  * Languages and religions are the state's, as its infobox lists them (up to 4 each); they
    describe the state, not every village in it.

    python3 build_polity_facts.py --dry    # statistics only
    python3 build_polity_facts.py          # write the resource
"""
import collections, gzip, json, math, os, re, sqlite3, sys, unicodedata

sys.path.insert(0, "/home/user/worldfill")
import modpack as M  # noqa: E402
from wikitext_clean import infobox_params, clean_items, years_of, clean_person  # noqa: E402

WORLD = f"{M.HISTORY}/world_rulers.json.gz"
BOXES = os.path.expanduser("~/.cache/wpdump/polity_infoboxes.jsonl.gz")
DB = os.path.expanduser("~/.cache/wpdump/wp.sqlite")
DEATHS = os.path.expanduser("~/.cache/wpdump/people_lines.json.gz")   # written by build_people.py
OUT_FILE = "polity_facts.json.gz"
REPORT = "/home/user/worldfill/polity_facts_report.json"
MAX_REIGN = 30          # a reign with no recorded end is not claimed for longer
DEATH_LOOKAHEAD = 80    # a recorded death up to this many years after accession ends the reign
PRESENT = 2026            # the dump's year: a reign still open is not claimed past it
PEOPLE = f"{M.HISTORY}/famous_people.json.gz"
ERA_LIMITED = re.compile(r"\[\[[^\]]+\]\]\s*(?:<small>)?\s*\(\s*(?:c\.\s*)?\d{3,4}\s*[–-]\s*\d{2,4}\s*\)")
JUNK_ITEM = re.compile(r"(?i)\b(schedule|constitution|article|recogni[sz]ed|statutory|minority|regional languages|"
                       r"national languages|official languages|see also)\b")

# ------------------------------------------------------------------ titles
GENDER = {"queen": "king", "empress": "emperor", "princess": "prince", "duchess": "duke",
          "countess": "count", "tsarina": "tsar", "tsaritsa": "tsar", "czar": "tsar", "czarina": "tsar",
          "sultana": "sultan", "rajah": "raja", "maharajah": "maharaja", "shōgun": "shogun",
          "grand duchess": "grand duke", "grand princess": "grand prince", "margravine": "margrave",
          "landgravine": "landgrave", "electress": "elector", "high queen": "high king",
          "regnant queen": "king", "basilissa": "basileus"}
RANK = [
    (0, r"emperor|pharaoh|caliph|khagan|shahanshah|tsar|basileus|sapa inca|huey tlatoani|great khan|mansa|negus|chhatrapati"),
    (1, r"high king|king|sultan|shah|khan|maharaja|raja|nizam|pope|doge|president|tlatoani|ajaw|oba|kabaka|mwami|monarch|shogun|sovereign|ruler|head of state|chief of state|regent of the kingdom"),
    (2, r"grand duke|grand prince|grand master|prime minister|chancellor|premier|chief minister|first minister|grand vizier|peshwa|nawab|emir|amir|stadtholder|lord protector"),
    (3, r"prince|duke|elector|despot|voivode|margrave|landgrave|bey|dey|pasha|ban"),
    (4, r"count|earl|lord|governor|viceroy|regent|archon|consul|tyrant|chief"),
]
GOV = re.compile(r"(?i)\b(prime minister|chancellor|premier|chief minister|first minister|grand vizier|"
                 r"vizier|peshwa|head of government|chief executive)\b")
TITLE_RX = (r"(?:High\s+King|High\s+Queen|Grand\s+Duke|Grand\s+Duchess|Grand\s+Prince|Grand\s+Princess|"
            r"Grand\s+Master|Grand\s+Vizier|Prime\s+Minister|Chief\s+Minister|First\s+Minister|President|"
            r"Chancellor|Premier|King|Queen|Emperor|Empress|Pharaoh|Sultana|Sultan|Shahanshah|Shah|Caliph|"
            r"Tsarina|Tsaritsa|Tsar|Czarina|Czar|Khagan|Great\s+Khan|Khan|Shōgun|Shogun|Maharajah|Maharaja|"
            r"Rajah|Raja|Nizam|Negus|Emir|Amir|Bey|Dey|Pasha|Doge|Pope|Prince-Bishop|Princess|Prince|Duchess|"
            r"Duke|Countess|Count|Earl|Margrave|Landgrave|Elector|Despot|Voivode|Regent|Basileus|Ajaw|"
            r"Tlatoani|Sapa\s+Inca|Mansa|Oba|Kabaka|Mwami|Chhatrapati|Peshwa|Nawab|Stadtholder|"
            r"Lord\s+Protector|Monarch|Ruler)")
VERB_RX = (r"(?:becomes|became|is\s+crowned(?:\s+as)?|is\s+proclaimed(?:\s+as)?|is\s+declared(?:\s+as)?|"
           r"is\s+elected(?:\s+as)?|is\s+installed\s+as|is\s+enthroned\s+as|is\s+recognized\s+as|"
           r"ascends\s+(?:to\s+)?the\s+(?:\w+\s+)?throne\s+as|accedes\s+(?:to\s+the\s+throne\s+)?as|"
           r"succeeds\s+[^.;]{1,90}?\s+as|takes\s+office\s+as|is\s+inaugurated\s+as|is\s+appointed(?:\s+as)?|"
           r"proclaims\s+(?:himself|herself)|declares\s+(?:himself|herself))")
POLITY_WORD = r"[A-ZÀ-Þ][\w'’\-]*"
LINE = re.compile(
    r"^(?P<name>[A-ZÀ-ÞĀ-Ž][^,;:()\"]{0,60}?)(?:,\s[^,;]{1,90},)?\s+(?P<verb>" + VERB_RX + r")\s+"
    r"(?:the\s+|a\s+)?(?:new\s+|first\s+|last\s+|sole\s+|next\s+|joint\s+|\d+(?:st|nd|rd|th)\s+)?"
    r"(?P<title>(?i:" + TITLE_RX + r"))(?:\s+regnant)?"
    r"(?:\s+(?:of|over)\s+(?:the\s+)?(?P<polity>" + POLITY_WORD +
    r"(?:\s+(?:of|the|and|de|del|la|le|du|di|von|al|des)\s+" + POLITY_WORD + r"|\s+" + POLITY_WORD + r")*))?")
BAD_NAME = re.compile(r"(?i)^(he|she|they|his|her|its|their|the|a|an|this|that|after|following|when|"
                      r"during|upon|on|in|at|by|with|as|it|there|several|many|nobles|rebels|parliament|"
                      r"citizens|army|troops)\b")
NOT_RULER = re.compile(r"(?i)\b(consort|heir|crown prince|co-regent|antipope|pretender|governor of|"
                       r"bishop of|archbishop|abbot|abbess|mayor|tribune|praetor|senator)\b")


ADJ2NOUN = {"polish": "poland", "lithuanian": "lithuania", "russian": "russia", "english": "england",
            "french": "france", "spanish": "spain", "portuguese": "portugal", "swedish": "sweden",
            "danish": "denmark", "norwegian": "norway", "hungarian": "hungary", "german": "germany",
            "austrian": "austria", "british": "britain", "scottish": "scotland", "persian": "persia",
            "chinese": "china", "japanese": "japan", "korean": "korea", "mexican": "mexico",
            "brazilian": "brazil", "italian": "italy", "greek": "greece", "egyptian": "egypt",
            "ethiopian": "ethiopia", "moroccan": "morocco", "dutch": "netherlands", "belgian": "belgium",
            "serbian": "serbia", "bulgarian": "bulgaria", "romanian": "romania", "bohemian": "bohemia",
            "prussian": "prussia", "bavarian": "bavaria", "saxon": "saxony", "sicilian": "sicily",
            "neapolitan": "naples", "venetian": "venice", "genoese": "genoa", "florentine": "florence",
            "milanese": "milan", "castilian": "castile", "aragonese": "aragon", "navarrese": "navarre",
            "georgian": "georgia", "armenian": "armenia", "byzantine": "byzantium", "roman": "rome",
            "ottoman": "ottomans", "mongol": "mongolia", "tibetan": "tibet", "afghan": "afghanistan",
            "iranian": "iran", "turkish": "turkey", "indian": "india", "siamese": "siam", "burmese": "burma",
            "vietnamese": "vietnam", "thai": "thailand", "american": "america", "canadian": "canada"}
SYNONYMS = [{"persia", "iran", "safavid", "qajar", "afsharid", "zand"}, {"china", "qing", "ming"},
            {"turkey", "ottomans", "ottoman"}, {"india", "mughal", "hindustan"}, {"korea", "joseon"},
            {"japan", "tokugawa"}, {"rome", "papal"}, {"byzantium", "byzantine", "constantinople"},
            {"britain", "england"}, {"burma", "myanmar"}, {"siam", "thailand"}, {"russia", "muscovy"}]


def expand(words):
    """State words plus their country-name equivalents: {"polish"} -> {"polish", "poland"}."""
    out = set(words)
    for w in list(words):
        if w in ADJ2NOUN:
            out.add(ADJ2NOUN[w])
    for group in SYNONYMS:
        if out & group:
            out |= group
    return out


def norm_title(t):
    t = re.sub(r"\s+", " ", t.strip().lower())
    for k in sorted(GENDER, key=len, reverse=True):
        t = re.sub(r"\b" + re.escape(k) + r"\b", GENDER[k], t)
    return t


def rank_of(title):
    t = norm_title(title)
    for r, rx in RANK:
        if re.search(r"\b(?:" + rx + r")\b", t):
            return r
    return 5


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def key_words(s):
    stop = {"of", "the", "and", "kingdom", "empire", "dynasty", "state", "republic", "sultanate",
            "caliphate", "principality", "duchy", "grand", "great", "first", "second", "third", "later",
            "early", "late", "old", "new", "middle", "lower", "upper", "northern", "southern", "eastern",
            "western", "khanate", "emirate", "county", "march", "shogunate", "period", "united"}
    return {w for w in re.findall(r"[a-z]+", strip_accents(s.lower())) if w not in stop and len(w) > 2}


def display_title(raw):
    items = clean_items(raw or "", 2, split_and=False)
    if not items:
        return ""
    t = re.sub(r"(?i)^(notable|list of|famous|important|main|selected)\s+", "", items[0]).strip()
    t = re.sub(r"(?i)\b(monarch|emperor|king|ruler|sultan|pharaoh|president|shah|khan|caliph|leader|"
               r"governor|prince|duke|chancellor|minister|tsar|doge|raja|maharaja|queen)s\b", r"\1", t)
    return t[:40]


# ------------------------------------------------------------------ where a line belongs
class Register:
    """RulerRegister.rulerAt, in Python: the state at the nearest register cell within 60 km."""
    CELL, MAX_KM, KM_LAT, NEIGHBOUR_KM = 0.5, 60.0, 110.57, 20.0

    def __init__(self):
        w = json.load(gzip.open(WORLD, "rt"))
        self.pols = [(p[0], p[1] if len(p) > 1 else None) for p in w["polities"]]
        self.tls = [[(f[k], f[k + 1], f[k + 2]) for k in range(0, len(f) - 2, 3)] for f in w["timelines"]]
        pl = w["places"]
        self.lat = [pl[3 * i] / 100.0 for i in range(len(pl) // 3)]
        self.lon = [pl[3 * i + 1] / 100.0 for i in range(len(pl) // 3)]
        self.tl = [pl[3 * i + 2] for i in range(len(pl) // 3)]
        self.grid = collections.defaultdict(list)
        for i in range(len(self.lat)):
            self.grid[self.key(self.lat[i], self.lon[i])].append(i)
        self.span_years = collections.defaultdict(lambda: [10 ** 6, -10 ** 6])
        for t in self.tls:
            for p, s, e in t:
                q = self.pols[p][1]
                if q:
                    a = self.span_years[q]
                    a[0], a[1] = min(a[0], s), max(a[1], e)

    def key(self, la, lo):
        return (math.floor((la + 90.0) / self.CELL), math.floor((lo + 180.0) / self.CELL))

    def dist(self, la1, lo1, la2, lo2):
        mid = math.radians((la1 + la2) / 2.0)
        dy = (la1 - la2) * self.KM_LAT
        dx = (lo1 - lo2) * self.KM_LAT * math.cos(mid)
        return math.hypot(dx, dy)

    def at(self, la, lo, year):
        best, bkm = -1, 1e18
        for ring in range(3):
            for dy in range(-ring, ring + 1):
                for dx in range(-ring, ring + 1):
                    if ring and abs(dy) != ring and abs(dx) != ring:
                        continue
                    for i in self.grid.get(self.key(la + dy * self.CELL, lo + dx * self.CELL), ()):
                        d = self.dist(la, lo, self.lat[i], self.lon[i])
                        if d < bkm:
                            best, bkm = i, d
            if best >= 0 and bkm <= ring * self.CELL * self.KM_LAT:
                break
        if best < 0 or bkm > self.MAX_KM:
            return None
        for p, s, e in self.tls[self.tl[best]]:
            if s <= year <= e:
                return self.pols[p]
        # as RulerRegister.rulerAt: an unruled nearest place yields to the nearest ruled one at most
        # NEIGHBOUR_KM farther (a point between grid cells, like Rome)
        limit = min(self.MAX_KM, bkm + self.NEIGHBOUR_KM)
        alt, akm = None, 1e18
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                for i in self.grid.get(self.key(la + dy * self.CELL, lo + dx * self.CELL), ()):
                    if i == best:
                        continue
                    d = self.dist(la, lo, self.lat[i], self.lon[i])
                    if d <= limit and d < akm:
                        for p, s, e in self.tls[self.tl[i]]:
                            if s <= year <= e:
                                alt, akm = self.pols[p], d
                                break
        return alt


# ------------------------------------------------------------------ sources
def infobox_facts(reg):
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    title_of = {}
    for name, q in reg.pols:
        if q and q not in title_of:
            r = con.execute("SELECT t.title FROM props p JOIN titles t ON t.page_id = p.page_id "
                            "WHERE p.qid = ? LIMIT 1", (q,)).fetchone()
            if r:
                title_of[q] = r[0]
    box = {}
    for line in gzip.open(BOXES, "rt", encoding="utf-8"):
        d = json.loads(line)
        box[d["title"]] = d["infobox"]
    facts = {}
    for q, t in title_of.items():
        p = infobox_params(box.get(t, ""))
        f = {"article": t, "lang": [], "rel": [], "cap": "", "head": [], "gov": []}
        if p:
            for k in ("official_languages", "common_languages", "languages", "language",
                      "national_languages", "regional_languages", "spoken_languages"):
                for x in clean_items(ERA_LIMITED.sub("", p.get(k, "")), 6):
                    if JUNK_ITEM.search(x):
                        continue
                    x = re.sub(r"(?i)\s+language$", "", x)
                    if x not in f["lang"]:
                        f["lang"].append(x)
            for k in ("religion", "state_religion", "official_religion", "religions"):
                # "[[Din-i Ilahi]] (1582–1605)": a faith of a few years is not the state's faith.
                for x in clean_items(ERA_LIMITED.sub("", p.get(k, "")), 6):
                    if JUNK_ITEM.search(x):
                        continue
                    if x not in f["rel"]:
                        f["rel"].append(x)
            f["lang"], f["rel"] = f["lang"][:4], f["rel"][:4]
            cap = clean_items(p.get("capital", ""), 1, split_and=False)
            f["cap"] = cap[0] if cap else ""
            for role, who, when, title_key in (("head", "leader", "year_leader", "title_leader"),
                                               ("gov", "deputy", "year_deputy", "title_deputy")):
                title = display_title(p.get(title_key, "")) or ("Ruler" if role == "head" else "")
                if role == "gov" and not title:
                    continue
                rows = []
                for i in range(1, 60):
                    if f"{who}{i}" not in p:
                        continue
                    nm = clean_person(p[f"{who}{i}"])
                    yrs = years_of(p.get(f"{when}{i}", ""))
                    if not nm or not yrs:
                        continue
                    rows.append([nm, title, yrs[0], yrs[1]])
                rows.sort(key=lambda r: r[2])
                for j, r in enumerate(rows):
                    if r[3] is None:     # one year only: up to the next ruler, at most 25 years
                        nxt = rows[j + 1][2] if j + 1 < len(rows) else r[2] + 25
                        r[3] = max(r[2], min(nxt, r[2] + 25))
                f[role] = rows
        facts[q] = f
    return facts, title_of


def accession_lines():
    out, seen = [], set()
    for e in M.existing_events():
        conf = str(e.get("confidence", ""))
        if not conf.startswith("wikipedia") and e["_pack"] not in ("events_world.json", "events.json"):
            continue
        text = e.get("name", "")
        text = re.sub(r"^[A-Z][a-z]+ \d{1,2}(?:\s*[–-]\s*\d{1,2})?\s*[–-]\s*", "", text)   # "March 14 – "
        text = re.sub(r"^(?:In|By|Around|About|After|Following)\s[^,]{1,60},\s+", "", text)
        text = re.sub(r"^(?:c\.\s*|approximate date\s*[–-]\s*)", "", text)
        m = LINE.match(text)
        if not m:
            continue
        name = re.sub(r"\s+", " ", m.group("name")).strip()
        name = re.sub(r"^(?:(?:the\s+)?(?:\d+|[A-Za-z]+)-year-old|young|the young|infant|teenage)\s+", "", name, flags=re.I)
        title = re.sub(r"\s+", " ", m.group("title")).strip()
        polity = (m.group("polity") or "").strip()
        if BAD_NAME.match(name) or NOT_RULER.search(text[:m.end()]) or len(name.split()) > 6:
            continue
        if re.search(r"\b(?:becomes|is|succeeds|crowned)\b", name):
            continue
        k = (name.lower(), e["_start"])
        if k in seen:
            continue
        seen.add(k)
        out.append({"name": name, "title": title + (f" of {polity}" if polity else ""),
                    "tkey": norm_title(title) + "|" + strip_accents(polity.lower()),
                    "year": e["_start"], "lat": e["lat"], "lon": e["lon"], "line": text[:140]})
    return out


NAME_STOP = {"the", "of", "great", "saint", "st", "king", "queen", "emperor", "empress", "sultan", "pope",
             "prince", "duke", "tsar", "shah", "khan", "caliph", "pharaoh"}


def name_tokens(name):
    return frozenset(w for w in re.findall(r"[a-z0-9]+", strip_accents(name.lower())) if w not in NAME_STOP)


class Deaths:
    """Recorded deaths from the year pages, matched by name loosely: "Wladyslaw IV Waza" finds
    "Władysław IV Vasa" (same first words), "Augustus the Strong" finds "Augustus II the Strong"
    (one name's words inside the other's, at least two words)."""

    def __init__(self):
        self.by_first = collections.defaultdict(list)
        self.n = 0
        if not os.path.exists(DEATHS):
            return
        for p in json.load(gzip.open(DEATHS, "rt")):
            if p.get("death") is None:
                continue
            for nm in {p["name"], re.sub(r"\s*\([^()]*\)$", "", p.get("article") or "")}:
                t = name_tokens(nm)
                if t:
                    self.by_first[min(t)].append((t, p["death"]))
            self.n += 1

    def __len__(self):
        return self.n

    ORDINAL = re.compile(r"^(?=[ivxl]+$)m{0,3}(cm|cd|d?c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})$")

    def same_core(self, name, t2):
        """First name plus a regnal number on both sides: "wladyslaw iv" in either spelling."""
        words = [w for w in re.findall(r"[a-z0-9]+", strip_accents(name.lower())) if w not in NAME_STOP]
        if len(words) < 2 or not self.ORDINAL.match(words[1]):
            return False
        return words[0] in t2 and words[1] in t2

    def first_death(self, name, lo, hi):
        t = name_tokens(name)
        if not t:
            return None
        best = None
        words = sorted(t)
        for w in words:
            for t2, d in self.by_first.get(w, ()):
                if not (lo <= d <= hi):
                    continue
                small, big = (t, t2) if len(t) <= len(t2) else (t2, t)
                if small == big or (len(small) >= 2 and small <= big) or self.same_core(name, t2):
                    best = d if best is None else min(best, d)
        return best


def deaths_by_name():
    return Deaths()


class StateNames:
    """Find a state by the words of its name, among the states that existed in a year."""

    def __init__(self, reg, title_of):
        self.reg = reg
        self.words = {}
        self.by_word = collections.defaultdict(set)
        for n, q in reg.pols:
            if not q:
                continue
            raw = key_words(n) | key_words(title_of.get(q, ""))
            w = expand(raw)
            self.words[q] = self.words.get(q, set()) | w
            self.raw = getattr(self, "raw", {})
            self.raw[q] = self.raw.get(q, set()) | raw
            for x in w:
                self.by_word[x].add(q)
        self.name = {q: n for n, q in reg.pols if q}

    def find(self, words, year):
        # The rarest word of the name must match ("Taifa of Arjona" needs "arjona", not "taifa").
        known = [w for w in words if w in self.by_word]
        if len(known) < len(words):
            return None
        rare = min(known, key=lambda w: len(self.by_word[w]))
        cands = collections.Counter()
        for x in words:
            for q in self.by_word.get(x, ()):
                s, e = self.reg.span_years[q]
                if s <= year <= e:
                    cands[q] += 1
        cands = collections.Counter({q: c for q, c in cands.items()
                                     if q in self.by_word[rare] and c == len(words)})
        if not cands:
            return None
        top = max(cands.values())
        best = [q for q, c in cands.items() if c == top]
        own = [q for q in best if set(words) <= self.raw.get(q, set())]
        pool = own or best
        if own:     # named outright: the most specific ("Taifa of Arjona", "Duchy of Milan")
            pool.sort(key=lambda q: (self.reg.span_years[q][1] - self.reg.span_years[q][0], q))
        else:       # only through a synonym ("China" -> Qing, Southern Ming): the longest-lived
            pool.sort(key=lambda q: (-(self.reg.span_years[q][1] - self.reg.span_years[q][0]), q))
        return pool[0]


ELECTED = re.compile(r"(?i)\b(president|prime minister|chancellor|premier|chief minister|first minister|"
                     r"head of government|grand vizier|vizier)\b")
ELECTED_TERM = 8          # an elected leader's term with no recorded successor


def state_for(polity_text, q_land, names, year, title_has_of):
    """The state a title points at: the land's own state when every word of (one part of) the
    title's state fits it, else a state found by name; None when nothing fits."""
    parts = [p for p in re.split(r"\s+and\s+", polity_text or "") if p.strip()] or [""]
    for part in parts:
        words = expand(key_words(part))
        if not words:
            return q_land
        if q_land and expand(key_words(part)) & names.words.get(q_land, set()) and \
                key_words(part) <= names.words.get(q_land, set()) | expand(key_words(part)) and \
                all(expand({w}) & names.words.get(q_land, set()) for w in key_words(part)):
            return q_land
    for part in parts:
        q2 = names.find(key_words(part), year)
        if q2:
            return q2
    return None if title_has_of else q_land


def chains(lines, reg, deaths, names):
    """Accession lines -> reigns per state: (qid, role, [name, title, start, end]).

    The state is the one ruling the spot the line was placed at, unless the line names a state
    ("King of Bosnia") whose words do not fit that state: then the state is looked up by name
    among the states of that year, and a line that fits no state is left out.
    """
    by = collections.defaultdict(list)
    unplaced = 0
    for ln in lines:
        polity_text = ln["tkey"].split("|", 1)[1]
        if re.search(r"(?i)-?elect\b", ln["line"][:ln["line"].find(ln["name"]) + len(ln["name"]) + 60]) or \
                (ELECTED.search(ln["title"]) and not polity_text):
            unplaced += 1          # "President-elect of the National Union of Mineworkers"
            continue
        pol = reg.at(ln["lat"], ln["lon"], ln["year"])
        q = state_for(polity_text, pol[1] if pol else None, names, ln["year"], bool(polity_text))
        if not q:
            unplaced += 1
            continue
        ln["qid"], ln["state"] = q, names.name.get(q)
        title_word = norm_title(ln["tkey"].split("|", 1)[0])
        # Top titles chain per state ("King of Portugal" = "King of Portugal and the Algarves");
        # lesser ones keep their land, so two duchies inside one kingdom stay two chains.
        key = title_word if rank_of(title_word) <= 2 else ln["tkey"]
        by[(q, key)].append(ln)
    out = collections.defaultdict(list)          # qid -> [(rank, matches, role, reign)]
    for (q, tkey), ls in by.items():
        ls.sort(key=lambda x: x["year"])
        title_words = key_words(tkey.split("|", 1)[1]) if "|" in tkey else set()
        for i, ln in enumerate(ls):
            nxt = ls[i + 1]["year"] if i + 1 < len(ls) else None
            cap = ELECTED_TERM if ELECTED.search(ln["title"]) else MAX_REIGN
            died = deaths.first_death(ln["name"], ln["year"], ln["year"] + (cap if cap == ELECTED_TERM else DEATH_LOOKAHEAD))
            ends = [x for x in (nxt, died) if x is not None]
            end = min(ends) if ends else ln["year"] + cap
            if (died is None or cap == ELECTED_TERM) and (nxt is None or nxt - ln["year"] > cap):
                end = min(end, ln["year"] + cap)
            role = "gov" if GOV.search(ln["title"]) else "head"
            out[q].append((rank_of(ln["title"]), title_words, role, [ln["name"], ln["title"], ln["year"], max(end, ln["year"])]))
    return out, unplaced


RULER_DESC = re.compile(
    r"^(?:the\s+)?(?:(?P<adj>[A-Z][\w'’\-]+(?:\s+[A-Z][\w'’\-]+)?)\s+)?(?P<title>(?i:" + TITLE_RX + r"))"
    r"(?:\s+(?:of|over)\s+(?:the\s+)?(?P<polity>" + POLITY_WORD +
    r"(?:\s+(?:of|the|and|de|del|la|le|du|di|von|al|des)\s+" + POLITY_WORD + r"|\s+" + POLITY_WORD + r")*))?\s*$")
DEMONYM_WORDS = {"American", "British", "French", "German", "Italian", "Spanish", "Portuguese", "Russian",
                 "Chinese", "Japanese", "Korean", "Indian", "Persian", "Ottoman", "Mughal", "Byzantine", "Roman",
                 "Holy", "Polish", "Swedish", "Danish", "Norwegian", "Hungarian", "Austrian", "Mexican",
                 "Brazilian", "Egyptian", "Turkish", "Iranian", "Greek", "Dutch", "Belgian", "Serbian",
                 "Bulgarian", "Romanian", "Prussian", "Bavarian", "Saxon", "Scottish", "English", "Irish",
                 "Welsh", "Ethiopian", "Moroccan", "Afghan", "Mongol", "Tibetan", "Siamese", "Burmese",
                 "Vietnamese", "Thai", "Abbasid", "Umayyad", "Fatimid", "Safavid", "Seljuk", "Timurid",
                 "Frankish", "Carolingian", "Merovingian", "Aztec", "Inca", "Mayan", "Maya", "Khmer",
                 "Georgian", "Armenian", "Venetian", "Genoese", "Neapolitan", "Sicilian", "Castilian",
                 "Aragonese", "Bohemian", "Lithuanian", "Ukrainian", "Finnish", "Canadian", "Australian",
                 "Argentine", "Chilean", "Peruvian", "Colombian", "Venezuelan", "Cuban", "Israeli",
                 "Pakistani", "Bangladeshi", "Indonesian", "Filipino", "Malaysian", "Nigerian", "Kenyan",
                 "Ghanaian", "South", "Sri", "New", "Yuan", "Tang", "Song", "Ming", "Qing", "Han", "Sui",
                 "Jin", "Liao", "Goryeo", "Joseon", "Silla", "Gupta", "Chola", "Maratha", "Sasanian", "Parthian",
                 "Achaemenid", "Assyrian", "Babylonian", "Hittite", "Egyptian", "Kushan", "Muslim", "Mamluk"}
RELATIVE = re.compile(r"(?i)^(?:\S+\s+){0,2}?(son|grandson|brother|half-brother|nephew|heir|father|uncle|"
                      r"cousin|descendant|husband|tutor|regent|general|vizier|minister|governor|claimant|"
                      r"pretender|rival|usurper)\b")
FEMALE = re.compile(r"(?i)\b(queen|empress|princess|duchess|countess|sultana|tsarina|tsaritsa|czarina|"
                    r"margravine|landgravine|electress|consort|wife|widow|mother|daughter)\b")


TOP_TITLE = (r"Holy\s+Roman\s+Emperor|Emperor|Empress|King|Sultan|Shahanshah|Shah|Caliph|Khagan|Great\s+Khan|Khan|"
             r"Pharaoh|Tsar|Czar|Maharaja|Maharajah|Raja|Rajah|Nizam|Negus|Doge|Pope|President|Prime\s+Minister|"
             r"Chancellor|Grand\s+Duke|Grand\s+Prince|Shogun|Shōgun|Mansa|Sapa\s+Inca|Tlatoani|Basileus")
POL = POLITY_WORD + r"(?:\s+(?:of|the|and|de|del|la|le|du|di|von|al|des)\s+" + POLITY_WORD + r"|\s+" + POLITY_WORD + r")*"
TITLE_OF = re.compile(r"\b(?P<title>(?i:" + TOP_TITLE + r"))\s+(?:of|over)\s+(?:the\s+)?(?P<polity>" + POL + r")")
ADJ_TITLE = re.compile(r"(?P<adj>\b[A-Z][\w'’\-]+(?:\s+[A-Z][\w'’\-]+)?)\s+(?P<title>(?i:" + TOP_TITLE + r"))\b(?!\s+(?:of|over)\b)")
ERA_EMPEROR = re.compile(r"^(?:Emperor\s+)?(?P<era>[A-Z][\w'’\-]+)(?:\s+Emperor)?(?:\s+of\s+(?P<polity>" + POL + r"))?$")
NAME_OF = re.compile(r"\bof\s+(?:the\s+)?(?P<polity>" + POL + r")\s*$")


def ruler_title(name, desc):
    """(display title, polity words) when a death line says the person was a top ruler, else None.

    The title must be the person's own: in the name ("Maximilian I, Holy Roman Emperor") or among
    the first words of the description ("Mughal emperor"), not someone they served ("vizier of
    the Mughal emperor Akbar").
    """
    name, desc = strip_accents(name), strip_accents(desc or "")
    if re.search(r"\bEmperor\b", name) and desc.startswith("of "):
        pol = desc[3:].strip()
        return f"Emperor of {pol}", pol             # "Kangxi Emperor, of Qing China"
    text = name + (", " + desc if desc else "")
    words_at = [m.start() for m in re.finditer(r"\S+", desc)]
    limit = len(name) + 2 + (words_at[3] if len(words_at) > 3 else len(desc))
    head = name.split(",", 1)[0]
    for rx in (TITLE_OF, ADJ_TITLE):
        for m in rx.finditer(text):
            if m.start("title") > limit:
                continue
            # "John Pope", "Stephen King": a surname, not a title. Inside the name itself only
            # "Title of X" counts, or a title after a comma ("Maximilian I, Holy Roman Emperor").
            if rx is ADJ_TITLE and m.start() < len(head) and not re.search(r"\bEmperor$", head):
                continue
            title = re.sub(r"\s+", " ", m.group("title"))
            if rank_of(title) > 2:
                continue
            if "polity" in rx.groupindex and m.group("polity"):
                return f"{title} of {m.group('polity')}", m.group("polity")
            adj = m.group("adj")
            if adj.lower() in ("the", "a", "an", "former", "last", "first", "deposed", "titular", "nominal"):
                continue
            n = NAME_OF.search(name)
            return f"{adj} {title}", (n.group("polity") if n else adj)
    if re.search(r"\bEmperor\b", name) and desc.startswith("of "):
        pol = desc[3:].strip()
        return f"Emperor of {pol}", pol
    if re.match(r"^Pope\s+[A-Z]", name):
        return "Pope", "Papal"
    # "Emperor Taizong of Tang" - but not "Sultan Muhammad Akbar" (a prince's name, not a title)
    m = re.match(r"^(?P<title>Emperor)\s+[A-Z][\w'’\-]+(?:\s+[\w'’\-]+)*?"
                 r"\s+of\s+(?P<polity>" + POL + r")$", name)
    if m:
        return (f"{m.group('title')} of {m.group('polity')}" if m.group("polity") else m.group("title")), (m.group("polity") or "")
    return None


def death_chains(names, reg):
    """Rulers whose death line names a top title ("Sigismund III Vasa, King of Poland",
    "Maximilian I, Holy Roman Emperor", "Kangxi Emperor, of Qing China", "Mughal emperor"):
    a reign runs from the previous holder's recorded death to the holder's own.

    The state is the one ruling the person's land in the year before death (a ruler's reign ends
    at death), checked against the state words in the title or the name ("Daozong of Liao"); a
    line that fits no state is left out. Female titles are left out (on the year pages "Queen of
    France" is far more often a consort; regnant queens come in through the accession lines).
    The first holder in a chain, or one after a gap of more than 75 years, is claimed only for the
    year of death: nothing is guessed. Year-page lines are sometimes loose (a prince called
    "Mughal emperor"); lines naming a relation ("son of ...") are dropped, the rest is trusted.
    """
    if not os.path.exists(PEOPLE):
        return {}, collections.Counter()
    placed = {(r[0], r[3]): (r[5], r[6]) for r in json.load(gzip.open(PEOPLE, "rt", encoding="utf-8"))["people"]}
    rows = json.load(gzip.open(DEATHS, "rt", encoding="utf-8")) if os.path.exists(DEATHS) else []
    st = collections.Counter()
    by = collections.defaultdict(list)
    for r in rows:
        name, desc, birth, death = r["name"], r.get("desc") or "", r["birth"], r["death"]
        la, lo = placed.get((name, death), (None, None))
        if death is None or FEMALE.search(desc) or FEMALE.search(name):
            continue
        if RELATIVE.search(desc) or re.search(r"(?i)\bEmpire\s+emperor\b", desc):
            continue            # "son of Mughal emperor Humayun"; "Mughal Empire emperor" (princes)
        t = ruler_title(name, desc)
        if not t:
            continue
        title, polity = t
        adjective_only = not re.search(r"\bof\b", title)
        if adjective_only and polity and ELECTED.search(title) and polity.split()[0] not in DEMONYM_WORDS:
            st["death_rulers_unplaced"] += 1      # "American University president"
            continue
        pol = reg.at(la, lo, death - 1) if la is not None else None
        q_land = pol[1] if pol else None
        if adjective_only and polity and not key_words(polity) & set(names.by_word) and \
                polity.split()[0] not in DEMONYM_WORDS:
            if not re.search(r"(?i)\bemperor\b", title) or not q_land:
                st["death_rulers_unplaced"] += 1
                continue
            q = q_land          # "Kangxi Emperor": an era name, the land's own state
        else:
            q = state_for(polity, q_land, names, death - 1, not adjective_only)
        if not q:
            st["death_rulers_unplaced"] += 1
            continue
        st["death_rulers"] += 1
        title_word = norm_title(re.sub(r"\s+of\s+.*$", "", title).split()[-1])
        by[(q, title_word)].append((death, birth, name, title))
    out = collections.defaultdict(list)
    for (q, key), ls in by.items():
        ls.sort(key=lambda x: (x[0], x[2]))
        words = key_words(key.split("|", 1)[1]) if "|" in key else set()
        prev = None
        for death, birth, name, title in ls:
            if ELECTED.search(title):
                continue        # an elected leader's term does not end at death
            # From the previous holder's death; with no previous holder (or a gap of more than 75
            # years) nothing is guessed: only the death year itself is claimed.
            start = prev if prev is not None and 0 < death - prev <= 75 else death
            if birth is not None:
                start = max(start, min(birth + 15, death))
            start = min(start, death)
            role = "gov" if GOV.search(title) else "head"
            out[q].append((rank_of(title), words, role, [name, title[:40], start, death]))
            prev = death
    return out, st


def main(dry=False):
    reg = Register()
    facts, title_of = infobox_facts(reg)
    lines = accession_lines()
    deaths = deaths_by_name()
    ch, unplaced = chains(lines, reg, deaths, StateNames(reg, title_of))
    dch, dst = death_chains(StateNames(reg, title_of), reg)
    for q, rows in dch.items():
        ch[q].extend(rows)
    names = {q: n for n, q in reg.pols if q}
    st = collections.Counter()
    for q, rows in ch.items():
        f = facts.setdefault(q, {"article": "", "lang": [], "rel": [], "cap": "", "head": [], "gov": []})
        state_words = key_words(names.get(q, "")) | key_words(f.get("article", ""))
        for role in ("head", "gov"):
            rr = [r for r in rows if r[2] == role]
            if not rr:
                continue
            best = min(r[0] for r in rr)
            keep = [r for r in rr if r[0] <= 2 or r[0] == best or (r[1] and r[1] & state_words)]
            st[f"chain_{role}_dropped_lesser"] += len(rr) - len(keep)
            have = {x[0].lower() for x in f[role]}
            for r in keep:
                reign = list(r[3])
                reign[3] = min(reign[3], PRESENT)
                if reign[2] > PRESENT or reign[0].lower() in have:
                    continue
                have.add(reign[0].lower())
                f[role].append(reign)
                st[f"chain_{role}_reigns"] += 1
            f[role].sort(key=lambda x: (x[2], x[3]))
    polities = []
    for q in sorted(facts, key=lambda x: int(x[1:]) if x[1:].isdigit() else 0):
        f = facts[q]
        if not (f["lang"] or f["rel"] or f["cap"] or f["head"] or f["gov"]):
            continue
        row = {"q": q, "n": names.get(q, f["article"])}
        if f["article"] and f["article"] != row["n"]:
            row["a"] = f["article"]
        for k in ("lang", "rel", "cap", "head", "gov"):
            if f[k]:
                row[k] = f[k]
        polities.append(row)
        st["polities"] += 1
        for k in ("lang", "rel", "cap", "head", "gov"):
            st[f"with_{k}"] += bool(f[k])
        st["head_reigns"] += len(f["head"])
        st["gov_reigns"] += len(f["gov"])
    rep = {"states_in_register": len({q for _n, q in reg.pols if q}),
           "states_with_article": len(title_of),
           "accession_lines_parsed": len(lines), "accession_lines_unplaced": unplaced,
           "deaths_known_for_names": len(deaths), **dict(dst), **dict(st)}
    # how often a spot's state has a named ruler that year: the register's own cells, by year
    years = [-2500, -1500, -500, 1, 500, 1000, 1300, 1500, 1700, 1850, 1900, 1950, 2000, 2020]
    head = {r["q"]: r.get("head", []) for r in polities}
    cover = {}
    for y in years:
        n = k = 0
        for i in range(0, len(reg.lat), 7):
            pol = None
            for p, s, e in reg.tls[reg.tl[i]]:
                if s <= y <= e:
                    pol = reg.pols[p]
                    break
            if not pol:
                continue
            n += 1
            if any(r[2] <= y <= r[3] for r in head.get(pol[1], ())):
                k += 1
        cover[str(y)] = f"{100.0 * k / n:.0f}% of {n} ruled cells" if n else "-"
    rep["named_ruler_share_of_ruled_cells"] = cover
    rep["examples"] = [f"{ln['year']}: {ln['name']} | {ln['title']} -> {ln.get('state')}" for ln in lines[::max(1, len(lines) // 15)]][:15]
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    if dry:
        return polities
    doc = {"format": 1,
           "source": ("worldfill/build_polity_facts.py: Wikipedia state infoboxes and year-page accession "
                      "lines (enwiki dump 2026-10-01, CC BY-SA 4.0), keyed by the Cliopatria Wikidata ids"),
           "note": "head/gov rows are [name, title, firstYear, lastYear] (inclusive); lang, rel, cap describe the state",
           "polities": polities}
    path = f"{M.HISTORY}/{OUT_FILE}"
    with open(path + ".tmp", "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as fh:
        json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
    json.load(gzip.open(path + ".tmp", "rt", encoding="utf-8"))
    os.replace(path + ".tmp", path)
    rep["bytes"] = os.path.getsize(path)
    json.dump(rep, open(REPORT, "w"), ensure_ascii=False, indent=1)
    print(f"wrote {path} ({rep['bytes'] / 1e6:.2f} MB)")
    return polities


if __name__ == "__main__":
    main(dry="--dry" in sys.argv)
