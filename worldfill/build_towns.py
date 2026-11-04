#!/usr/bin/env python3
"""Step 29 (systems C2, C3, C4, C5, C6): the towns of the world through time.

What a villager can now say about the town they live in, in any year:
  * its name in that year (C4): Bombay until 1995, then Mumbai; Edo until 1868; Leopoldville until 1966; Leningrad
    from 1924 to 1991; Byzantium, then Constantinople, then Istanbul;
  * how many people live there (C6): census figures with their year, between two figures a straight line, never
    beyond the first figure and at most 15 years after the last;
  * when it was founded, and whether it is growing or shrinking (C5);
  * which province or district it lies in (C3): the Bombay Presidency until 1947, Bombay State until 1960, then
    Maharashtra;
  * who runs it (C2): the town's own head (a mayor, a governor ...) and the head of its province, with their years.

    python3 build_towns.py --wiki         read Wikipedia's "List of city name changes" (the lines that carry a year)
                                          into build/towns/wiki_renames.json and the article titles to look up
    python3 fetch_towns_wd.py towns wiki  fetch the town lists and the titles' Wikidata numbers (build/towns/raw/)
    python3 build_towns.py --select       choose the towns (build/towns/towns.txt)
    python3 fetch_towns_wd.py details     fetch their names, figures, dates, provinces and offices
    python3 build_towns.py --divisions    list the provinces and districts named (build/towns/divisions.txt)
    python3 fetch_towns_wd.py divisions   fetch their names, dates, kinds and offices
    python3 fetch_towns_wd.py parents     fetch the province each district lies in today
    python3 build_towns.py --parents      list those provinces not yet fetched (build/towns/divisions2.txt)
    python3 fetch_towns_wd.py divisions2  fetch their names, dates, kinds and offices
    python3 build_towns.py --offices      list the offices (build/towns/offices.txt)
    python3 fetch_towns_wd.py holders     fetch who held them, with their years
    python3 build_towns.py --build        write history/towns.json.gz into the mod
    python3 build_towns.py --check        read it back and check it (exit 1 on a problem)

Which towns: every human settlement with a coordinate and a population figure of 20,000 or more; every settlement
with a dated official name (a renamed town) and 8 or more Wikipedia articles; the 4,112 cities of step 26; and the
towns of Wikipedia's list of city name changes.

Names (C4). Three layers, the last one wins: the dated lines of Wikipedia's list of city name changes (a coarse list:
it leaves out spelling changes, so it only fills the years Wikidata leaves open), then Wikidata's official names with
dates (P1448, P2561), then a short table of famous renamings written by hand from the towns' own Wikipedia articles
(HAND_NAMES below, for the cases Wikidata gives only in a non-Latin script or not at all: Edo, Constantinople,
Calcutta, Rangoon ...; turn 12: Wikipedia first). From Wikidata, one name per stretch of years: English first, then other languages
written in Latin letters; a past name that is the same as that language's name today is today's English name (the
German "Sankt Petersburg" of 1703-1914 is Saint Petersburg). A change in the first half of a year counts from that
year, a change in the second half from the next. Names are only used for the stretch of years they are dated for;
before the first dated stretch the history data keeps the name it has.

File layout (history/towns.json.gz, JSON):
  towns: [[qid, name, lat*1000, lon*1000, flags, founded, foundedPrecision, names, pops, divs, head], ...]
      flags: 1 ghost town (abandoned), 2 ended (founded..ended is its life), 4 a capital of a country today
      founded: year or null; precision 9 year, 8 decade, 7 century, 6 millennium
      names: [[from, to, name], ...]  (to exclusive; null open)
      pops: [year, people, year, people, ...] (at most 12 figures, oldest first)
      divs: [[from, to, division], ...]  (division = index into "divisions"; null = unknown)
      head: office index or -1 (the town's own head: mayor, governor ...)
  ended: {qid: year} for towns that were abandoned or ended (flag 2)
  divisions: [[qid, name, office, parent, parentFrom], ...]   office = index into "offices" or -1; parent = the
      province (first-level division) a district lies in today, index or -1, from that year
  offices: [[qid, title, [[from, to, holder], ...]], ...]   the title ("Mayor of Paris"); holders with a known start
      year, oldest first (to: the last year, inclusive; null unknown)
"""
import collections
import gzip
import json
import math
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modpack as M                       # noqa: E402
from build_cards import qid_of, literal, point, rows_in   # noqa: E402

BASE = os.path.join(HERE, "build", "towns")
RAW = os.path.join(BASE, "raw")
OUT_NAME = "towns.json.gz"
OUT = os.path.join(M.HISTORY, OUT_NAME)
REPORT = os.path.join(HERE, "logs", "step29_towns_report.json")
WIKI_JSON = os.path.join(BASE, "lcnc.json")
WIKI_URL = ("https://en.wikipedia.org/w/api.php?action=parse&page=List_of_city_name_changes&prop=wikitext"
            "&format=json&formatversion=2")
CITIES26 = os.path.join(HERE, "sources", "step26_cities.json.gz")
NOW = 2026

GHOST = {74047, 350895, 21751582, 2974842}  # ghost town, abandoned village, deserted medieval village, lost city
# (checked by label on 2026-10-15)
LATIN_LANGS = ["en", "en-gb", "en-us", "en-ca", "mul", "de", "fr", "es", "it", "pt", "nl", "pl", "sv", "nb", "nn",
               "da", "ro", "cs", "sk", "hu", "fi", "tr", "id", "ms", "vi", "tl", "sq", "hr", "sl", "lt", "lv", "et",
               "ca", "eu", "gl", "la", "az", "uz", "tk"]
LANG_RANK = {lang: i for i, lang in enumerate(LATIN_LANGS)}

# Famous renamings Wikidata gives only in a non-Latin script or not at all, written from each town's own English
# Wikipedia article (2026-10-15). (from, to, name): to exclusive, None = open. Only years the article states.
HAND_NAMES = {
    # Every QID here was checked against its English label on 2026-10-15 (wrong guesses were replaced).
    "Q406": [(None, 330, "Byzantium"), (330, 1930, "Constantinople")],            # Istanbul: renamed 1930 (postal law)
    "Q1490": [(1457, 1868, "Edo")],                                               # Tokyo: Edo until 1868
    "Q1348": [(1690, 2001, "Calcutta")],                                          # Kolkata: renamed 2001
    "Q37995": [(1755, 1989, "Rangoon")],                                          # Yangon: renamed 1989
    "Q1854": [(1698, 1976, "Saigon")],                                            # Ho Chi Minh City: renamed 1976
    "Q956": [(1153, 1215, "Zhongdu"), (1267, 1368, "Khanbaliq"), (1368, 1403, "Beiping"), (1928, 1949, "Beiping")],
    "Q5826": [(None, 1369, "Chang'an")],                                          # Xi'an: Chang'an before the Ming
    "Q1355": [(None, 2014, "Bangalore")],                                         # Bengaluru: renamed 2014
    "Q1538": [(None, 1978, "Poona")],                                             # Pune
    "Q66568": [(None, 1948, "Cawnpore")],                                         # Kanpur
    "Q79980": [(None, 1956, "Benares")],                                          # Varanasi
    "Q11909": [(None, 1974, "Baroda")],                                           # Vadodara
    "Q167715": [(None, 1991, "Trivandrum")],                                      # Thiruvananthapuram
    "Q162442": [(1575, 2018, "Allahabad")],                                       # Prayagraj
    "Q1800": [(None, 1996, "Cochin")],                                            # Kochi
    "Q3889": [(1876, 1976, "Lourenço Marques")],                                  # Maputo
    "Q3659": [(1900, 1973, "Fort-Lamy")],                                         # N'Djamena
    "Q146723": [(1883, 1966, "Stanleyville")],                                    # Kisangani
    "Q187593": [(1910, 1966, "Élisabethville")],                                  # Lubumbashi
    "Q3854": [(None, 1962, "Usumbura")],                                          # Bujumbura
    "Q3919": [(None, 1969, "Gaberones")],                                         # Gaborone
    "Q3818": [(None, 1973, "Santa Isabel")],                                      # Malabo
    "Q891": [(1932, 1990, "Gorky")],                                              # Nizhny Novgorod
    "Q894": [(1935, 1991, "Kuybyshev")],                                          # Samara
    "Q887": [(1924, 1991, "Sverdlovsk")],                                         # Yekaterinburg
    "Q2288": [(1931, 1990, "Kalinin")],                                           # Tver
    "Q35493": [(1855, 1921, "Verny"), (1921, 1993, "Alma-Ata")],                  # Almaty
    "Q1520": [(1832, 1961, "Akmolinsk"), (1961, 1992, "Tselinograd"), (1992, 1998, "Akmola"),
              (2019, 2022, "Nur-Sultan")],                                        # Astana
    "Q43070": [(1869, 1924, "Yuzovka"), (1924, 1961, "Stalino")],                 # Donetsk
    "Q200166": [(None, 1916, "Berlin")],                                          # Kitchener, Ontario
    "Q9361": [(1926, 1991, "Frunze")],                                            # Bishkek
    "Q9365": [(1929, 1961, "Stalinabad")],                                        # Dushanbe
    "Q994": [(None, 1936, "Tiflis")],                                             # Tbilisi
    "Q1799": [(1741, 1945, "Breslau")],                                           # Wrocław
    "Q393": [(1720, 1945, "Stettin")],                                            # Szczecin
    "Q1780": [(None, 1919, "Pressburg")],                                         # Bratislava
    "Q36036": [(1772, 1918, "Lemberg"), (1918, 1939, "Lwów")],                    # Lviv
    "Q2795": [(1953, 1990, "Karl-Marx-Stadt")],                                   # Chemnitz
    "Q35997": [(None, 1930, "Smyrna")],                                           # İzmir (postal law 1930)
    "Q3640": [(None, 1930, "Angora")],                                            # Ankara (postal law 1930)
    "Q1930": [(1826, 1855, "Bytown")],                                            # Ottawa
    "Q172": [(1793, 1834, "York")],                                               # Toronto
    "Q62": [(1835, 1847, "Yerba Buena")],                                         # San Francisco
    "Q60": [(1625, 1664, "New Amsterdam")],                                       # New York City
    "Q1489": [(1325, 1521, "Tenochtitlan")],                                      # Mexico City
    "Q8684": [(1394, 1910, "Hanseong"), (1910, 1945, "Keijō")],                   # Seoul
    "Q43387": [(125, 1930, "Adrianople")],                                         # Edirne (postal law 1930)
}
# Founding years where the town's Wikipedia article differs from Wikidata (None: the article gives no founding year,
# the town is far older than the date Wikidata gives).
HAND_FOUNDED = {
    "Q1361": (1591, 9),   # Hyderabad: founded in 1591 by Muhammad Quli Qutb Shah (Wikidata: 1592)
    "Q1156": None,        # Mumbai: Wikidata's 1507 is not a founding; the islands were settled long before
}
# Other names people used at the same time ("also called"), from the towns' Wikipedia articles.
HAND_ALSO = {
    "Q1361": [(1600, 1700, "Bhagnagar")],   # Hyderabad: European travellers of the 17th century wrote Bhagnagar
}


LETTERS = str.maketrans({"ł": "l", "Ł": "L", "ø": "o", "Ø": "O", "æ": "ae", "Æ": "AE", "ß": "ss", "đ": "d", "Đ": "D",
                         "ı": "i", "œ": "oe", "Œ": "OE", "þ": "th", "Þ": "Th", "ð": "d", "Ð": "D"})


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.translate(LETTERS)) if unicodedata.category(c) != "Mn")


def norm(s):
    return re.sub(r"[^a-z0-9]", "", strip_accents(s or "").lower())


def latin(s):
    """True when every letter of s is a Latin letter (accents allowed)."""
    for ch in s:
        if ch.isalpha():
            try:
                if "LATIN" not in unicodedata.name(ch):
                    return False
            except ValueError:
                return False
    return True


# ---------------------------------------------------------------------------------------------------- Wikipedia list

def wiki():
    """Parses the dated lines of Wikipedia's list of city name changes."""
    os.makedirs(BASE, exist_ok=True)
    if not os.path.exists(WIKI_JSON):
        import requests
        r = requests.get(WIKI_URL, headers={"User-Agent": "EternalEngineDataBuild/1.0 (history data)"}, timeout=60)
        r.raise_for_status()
        with open(WIKI_JSON, "w", encoding="utf-8") as f:
            f.write(r.text)
    text = json.load(open(WIKI_JSON, encoding="utf-8"))["parse"]["wikitext"]
    text = re.sub(r"<ref[^>]*/>", "", text)
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.S)
    text = re.sub(r"\{\{[^{}]*\}\}", "", text)
    out = []
    year_re = re.compile(r"\((?:c\.\s*|circa\s*)?(\d{3,4})(?:\s*(?:AD|CE))?\)")
    for line in text.split("\n"):
        if not line.startswith("*") or "→" not in line or not year_re.search(line):
            continue
        segs = [s.strip(" *") for s in line.split("→")]
        chain = []
        title = None
        for s in segs:
            m = year_re.search(s)
            year = int(m.group(1)) if m else None
            s2 = year_re.sub("", s)
            link = re.search(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", s2)
            if link:
                name = (link.group(2) or link.group(1)).strip()
                title = link.group(1).strip()
            else:
                name = re.sub(r"\[\[|\]\]|''+", "", s2).strip()
                title = None
            name = re.sub(r"\s+", " ", name).strip(" ,.;")
            if not name or len(name) > 60:
                chain = []
                break
            chain.append([name, year])
        if len(chain) < 2 or title is None:
            continue
        if year_re.search(segs[0]) and len(segs) == 2 and chain[0][1] and not chain[1][1]:
            continue  # "Old (1900) → New": the year belongs to the old name's start; not a renaming date
        out.append({"title": title, "chain": chain, "line": line.strip()[:200]})
    with open(os.path.join(BASE, "wiki_renames.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=0)
    titles = sorted({e["title"] for e in out})
    with open(os.path.join(BASE, "wiki_titles.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(titles) + "\n")
    print(f"wiki: {len(out)} dated lines, {len(titles)} towns")


def wiki_periods(chain):
    """[[name, startYear|None], ...] -> [(from, to, name)] for the stretches whose start (or first) and end are known."""
    out = []
    for i, (name, start) in enumerate(chain):
        end = chain[i + 1][1] if i + 1 < len(chain) else None
        if i + 1 < len(chain) and end is None:
            continue
        if i > 0 and start is None:
            continue
        out.append((start, end, name))
    return out


# ---------------------------------------------------------------------------------------------------- choosing towns

def select():
    towns = {}
    for r in rows_in(RAW, "towns_big"):
        q = qid_of(r[0])
        pt = point(r[3]) if len(r) > 3 else None
        if q and pt:
            towns[q] = pt
    big = len(towns)
    for r in rows_in(RAW, "towns_renamed"):
        q = qid_of(r[0])
        pt = point(r[2]) if len(r) > 2 else None
        if q and pt:
            towns.setdefault(q, pt)
    renamed = len(towns) - big
    for c in json.load(gzip.open(CITIES26, "rt"))["cities"]:
        towns.setdefault(int(c["q"][1:]), (c["lat"], c["lon"]))
    for r in rows_in(RAW, "w_titles", required=False) or []:
        q = qid_of(r[1])
        pt = point(r[2]) if len(r) > 2 else None
        if q and pt:
            towns.setdefault(q, pt)
    for q in list(HAND_NAMES) + list(HAND_ALSO):
        if int(q[1:]) not in towns:
            print(f"  hand town {q} is not in the lists (no point?)")
    with open(os.path.join(BASE, "towns.txt"), "w") as f:
        for q in sorted(towns):
            f.write(f"Q{q}\n")
    print(f"select: {len(towns):,} towns ({big:,} with 20,000 people or more, {renamed:,} more renamed ones)")


def divisions():
    ds = set()
    for r in rows_in(RAW, "t_admin"):
        d = qid_of(r[1])
        if d and "Deprecated" not in (r[4] if len(r) > 4 else ""):
            ds.add(d)
    with open(os.path.join(BASE, "divisions.txt"), "w") as f:
        for q in sorted(ds):
            f.write(f"Q{q}\n")
    print(f"divisions: {len(ds):,}")


def parents():
    have = set(int(q[1:]) for q in open(os.path.join(BASE, "divisions.txt")).read().split())
    more = set()
    for r in rows_in(RAW, "v_parent"):
        p = qid_of(r[1])
        if p and p not in have:
            more.add(p)
    with open(os.path.join(BASE, "divisions2.txt"), "w") as f:
        for q in sorted(more):
            f.write(f"Q{q}\n")
    print(f"parents: {len(more):,} provinces not yet fetched")


def offices():
    offs = set()
    for prefix in ("t_office", "v_office", "v2_office"):
        for r in rows_in(RAW, prefix):
            o = qid_of(r[2])
            if o:
                offs.add(o)
    with open(os.path.join(BASE, "offices.txt"), "w") as f:
        for q in sorted(offs):
            f.write(f"Q{q}\n")
    print(f"offices: {len(offs):,}")


# ---------------------------------------------------------------------------------------------------- building

CYR_RU = {"а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo", "ж": "zh", "з": "z", "и": "i",
          "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
          "у": "u", "ф": "f", "х": "kh", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "shch", "ъ": "", "ы": "y", "ь": "",
          "э": "e", "ю": "yu", "я": "ya"}
CYR_UK = dict(CYR_RU, **{"г": "h", "ґ": "g", "е": "e", "є": "ye", "и": "y", "і": "i", "ї": "yi", "й": "y",
                         "щ": "shch", "ь": "", "'": "", "’": ""})


def translit(name, lang):
    """Russian or Ukrainian Cyrillic to Latin letters (a plain BGN-like table); None for anything else."""
    table = CYR_RU if lang == "ru" else CYR_UK if lang == "uk" else None
    if table is None:
        return None
    out = []
    for ch in name:
        low = ch.lower()
        if low in table:
            t = table[low]
            out.append(t.capitalize() if ch != low and t else t)
        elif ch.isalpha() and not latin(ch):
            return None
        else:
            out.append(ch)
    s2 = "".join(out).strip()
    return s2 or None


def boundary(cell):
    """A date cell -> the first year of what starts (or the first year after what ends) on that date: a change in
    the first half of a year counts from that year, in the second half from the next. None for unknown values."""
    if not cell or cell.startswith("<"):
        return None
    m = re.match(r'^"?(-?)(\d+)-(\d\d)-(\d\d)', cell)
    if not m:
        return None
    y = int(m.group(2)) * (-1 if m.group(1) else 1)
    if y <= 0:
        y -= 1
    return y + 1 if int(m.group(3)) > 6 else y


def year_cell(cell):
    """A date cell -> its year in the mod's count (no year 0); None for unknown values."""
    if not cell or cell.startswith("<"):
        return None
    m = re.match(r'^"?(-?)(\d+)-(\d\d)-(\d\d)', cell)
    if not m:
        try:
            y = int(float(cell.strip('"')))
        except ValueError:
            return None
    else:
        y = int(m.group(2)) * (-1 if m.group(1) else 1)
    return y - 1 if y <= 0 else y


INF = 10 ** 6


def lo(a):
    return -INF if a is None else a


def hi(b):
    return INF if b is None else b


def back(a):
    return None if a is None or abs(a) >= INF else a


def overlay(base, top):
    """Periods (from, to, name) of `top` replace what `base` says for the same years."""
    segs = [(lo(a), hi(b), n) for a, b, n in base]
    for ta, tb, _ in top:
        ta, tb = lo(ta), hi(tb)
        new = []
        for sa, sb, sn in segs:
            if tb <= sa or ta >= sb:
                new.append((sa, sb, sn))
                continue
            if sa < ta:
                new.append((sa, ta, sn))
            if tb < sb:
                new.append((tb, sb, sn))
        segs = new
    segs += [(lo(a), hi(b), n) for a, b, n in top]
    return sorted(segs)


def tidy_periods(segs, label):
    """Drops today's name and empty stretches, joins neighbours with the same name."""
    out = []
    for a, b, n in sorted(segs):
        if n is None or b <= a or norm(n) == norm(label) or b >= INF:
            continue          # an open stretch is today's name, and today's name is the town's own label
        if out and out[-1][2] == n and out[-1][1] == a:
            out[-1] = (out[-1][0], b, n)
        else:
            out.append((a, b, n))
    return [[back(a), back(b), n] for a, b, n in out]


ADMIN_WORDS = re.compile(r"(?i)\b(district|rayon|raion|urban settlement|rural settlement|municipality|municipalit[ée]|"
                         r"municipal|selsoviet|selsovet|volost|hromada|poselenie|county|prefecture|province|region|"
                         r"oblast|governorate|okrug|uyezd|gmina|commune de|landkreis|parish|township|borough council)\b")


def wd_periods(stmts, label):
    """Wikidata's dated names (lang, prop, name, from, to) -> [(from, to, name)] in English or Latin letters.
    Russian and Ukrainian names are spelled in Latin letters only for towns Wikidata names in no Latin language at
    all (otherwise "Stolp" would also come back as "Shtolp"); names of offices or districts are left out."""
    has_latin = any(latin(name) and lang in LANG_RANK for lang, prop, name, f, t in stmts)
    cands = []
    for lang, prop, name, f, t in stmts:
        if f is not None and t is not None and t <= f:
            continue
        if ADMIN_WORDS.search(name):
            continue
        shown = name if latin(name) else (None if has_latin else translit(name, lang))
        if not shown or len(shown) > 50:
            continue
        rank = LANG_RANK.get(lang, 100 + (0 if lang == "ru" else 1 if lang == "uk" else 50))
        if rank >= 150:
            continue
        cands.append((rank, 0 if prop == "o" else 1, lang, shown, f, t))
    if not cands:
        return []
    current = {}
    for rank, pr, lang, shown, f, t in sorted(cands, key=lambda c: (c[4] is None, c[4] or 0)):
        if t is None and f is not None:
            current[lang] = shown
    bounds = sorted({c[4] for c in cands if c[4] is not None} | {c[5] for c in cands if c[5] is not None})
    edges = [None] + bounds + [None]
    out = []
    for i in range(len(edges) - 1):
        a, b = edges[i], edges[i + 1]
        if i == 0 and not bounds:
            continue
        best = None
        for c in cands:
            rank, pr, lang, shown, f, t = c
            if f is not None and (a is None or f > a):
                continue
            if t is not None and (b is None or t < b):
                continue
            if best is None or (rank, pr) < (best[0], best[1]):
                best = c
        if best is None:
            continue
        name = best[3]
        if norm(name) == norm(current.get(best[2], "")) or norm(name) == norm(label):
            name = None
        out.append((lo(a), hi(b), name))
    return out


def thin(points, keep=12):
    """[(year, people)] oldest first -> at most `keep`, the first and last kept, the rest spread over the years."""
    if len(points) <= keep:
        return points
    first, last = points[0][0], points[-1][0]
    chosen = {0, len(points) - 1}
    for k in range(1, keep - 1):
        target = first + (last - first) * k / (keep - 1)
        best = min((i for i in range(len(points)) if i not in chosen), key=lambda i: abs(points[i][0] - target))
        chosen.add(best)
    return [points[i] for i in sorted(chosen)]


def rank_of(tops):
    if 10864048 in tops:
        return 1
    if tops & {6256, 3624078} and not tops & {3024240}:
        return 9          # a country today: the ruler line says that already
    if tops & {133156, 1336152}:
        return 2          # a colony or a princely state
    if 3024240 in tops:
        # A state of the past: kept when it was also an administrative unit (Hyderabad State, the Soviet republics,
        # the Electorate of Saxony); a sovereign one is the ruler line's business. The game also leaves out a province
        # with the ruler's own name.
        return 3 if 19953632 in tops else 9
    if 19953632 in tops:
        return 3          # a former province or district
    if 486972 in tops:
        return 8          # a town (a town inside a town): left out
    return 4


def build():
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    towns_q = [int(q[1:]) for q in open(os.path.join(BASE, "towns.txt")).read().split()]
    report = collections.Counter()

    def labels(prefix):
        lab = {}
        for r in rows_in(RAW, prefix):
            q = qid_of(r[0])
            text = literal(r[1])
            if not text:
                continue
            if r[2].strip('"') == "en" or q not in lab:
                lab[q] = text
        return lab

    tlab = labels("t_label")
    points = {}
    for r in rows_in(RAW, "towns_big"):
        q, pt = qid_of(r[0]), point(r[3])
        if q and pt:
            points[q] = pt
    for r in rows_in(RAW, "towns_renamed"):
        q, pt = qid_of(r[0]), point(r[2])
        if q and pt:
            points.setdefault(q, pt)
    for c in json.load(gzip.open(CITIES26, "rt"))["cities"]:
        points.setdefault(int(c["q"][1:]), (round(c["lat"], 3), round(c["lon"], 3)))
    wiki_q = {}
    for r in rows_in(RAW, "w_titles", required=False) or []:
        q, pt = qid_of(r[1]), point(r[2]) if len(r) > 2 else None
        if q:
            wiki_q[literal(r[0])] = q
            if pt:
                points.setdefault(q, pt)

    # names
    stmts = collections.defaultdict(list)
    for r in rows_in(RAW, "t_names"):
        q = qid_of(r[0])
        name = literal(r[2])
        lang = r[3].strip('"')
        f, t = boundary(r[4]), boundary(r[6])
        if q and name and (f is not None or t is not None):
            stmts[q].append((lang, r[1].strip('"'), name, f, t))
    wiki_periods_by_q = collections.defaultdict(list)
    for e in json.load(open(os.path.join(BASE, "wiki_renames.json"), encoding="utf-8")):
        q = wiki_q.get(e["title"])
        if q:
            wiki_periods_by_q[q] += wiki_periods(e["chain"])
            report["wiki lines matched"] += 1
        else:
            report["wiki lines without a town"] += 1

    # population figures
    figs = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows_in(RAW, "t_pop"):
        if "Deprecated" in r[3]:
            continue
        q, y = qid_of(r[0]), year_cell(r[2])
        try:
            v = float(r[1])
        except ValueError:
            continue
        if q and y is not None and 0 < v < 1e8 and y <= NOW:
            figs[q][y].append((("Preferred" in r[3]), v))

    # founding, end, kinds
    founded = {}
    for r in rows_in(RAW, "t_life"):
        q, which = qid_of(r[0]), r[1].strip('"')
        y = year_cell(r[2])
        try:
            prec = int(r[3])
        except ValueError:
            continue
        if not q or y is None or which != "from" or prec < 7 or y > NOW:
            continue
        key = (0 if prec >= 9 else 1 if prec == 8 else 2, y)
        if q not in founded or key < founded[q][0]:
            founded[q] = (key, y, min(prec, 9))
    ended = {}
    for r in rows_in(RAW, "t_life"):
        q, which = qid_of(r[0]), r[1].strip('"')
        y = year_cell(r[2])
        if q and which == "to" and y is not None:
            ended.setdefault(q, y)
    ghost = set()
    for r in rows_in(RAW, "t_kind"):
        if qid_of(r[1]) in GHOST:
            ghost.add(qid_of(r[0]))

    # divisions
    vlab = labels("v_label")
    vlab.update({k: v for k, v in labels("v2_label").items() if k not in vlab})
    span = re.compile(r"\s*\((?:\d{3,4}\s*[–-]\s*\d{0,4}|\d{3,4})\)$")
    vlab = {k: span.sub("", v) for k, v in vlab.items() if latin(v)}   # "Andhra Pradesh (1956–2014)" -> "Andhra Pradesh"
    vtop = collections.defaultdict(set)
    for prefix in ("v_top", "v2_top"):
        for r in rows_in(RAW, prefix):
            vtop[qid_of(r[0])].add(qid_of(r[1]))
    vfrom, vto = {}, {}
    for prefix in ("v_dates", "v2_dates"):
        for r in rows_in(RAW, prefix):
            q, which = qid_of(r[0]), r[1].strip('"')
            y = year_cell(r[2])
            if y is None:
                continue
            if which == "from":
                vfrom[q] = min(vfrom.get(q, y), y)
            else:
                vto[q] = max(vto.get(q, y), y)
    parent = collections.defaultdict(list)
    for r in rows_in(RAW, "v_parent"):
        parent[qid_of(r[0])].append(qid_of(r[1]))
    office_of = {}
    for prefix in ("t_office", "v_office", "v2_office"):
        for r in rows_in(RAW, prefix):
            q, which, off = qid_of(r[0]), r[1].strip('"'), qid_of(r[2])
            if not off:
                continue
            if which == "gov" or q not in office_of:
                if which == "gov" and q in office_of and office_of[q][0] == "gov":
                    office_of[q] = ("gov", min(office_of[q][1], off))   # one office per place, the same each time
                else:
                    office_of[q] = (which, off)
    # An office named as the head's office of three or more places is a general one ("mayor", "governor",
    # "chairperson"), not this place's own: its holders are people from everywhere, so it is left out.
    office_users = collections.defaultdict(set)
    for prefix in ("t_office", "v_office", "v2_office"):
        for r in rows_in(RAW, prefix):
            office_users[qid_of(r[2])].add(qid_of(r[0]))
    general = {o for o, users in office_users.items() if len(users) >= 3}
    report["general offices left out"] = len(general)
    office_of = {q: v for q, v in office_of.items() if v[1] not in general}
    adm = collections.defaultdict(list)
    for r in rows_in(RAW, "t_admin"):
        if "Deprecated" in r[4]:
            continue
        q, d = qid_of(r[0]), qid_of(r[1])
        if q and d and d in vlab:
            adm[q].append((d, boundary(r[2]), boundary(r[3])))

    # holders
    holders = collections.defaultdict(list)
    for r in rows_in(RAW, "h_holders"):
        off, h, name = qid_of(r[0]), qid_of(r[1]), literal(r[2])
        f, t = year_cell(r[3]), year_cell(r[5])
        if not off or not name or f is None or f > NOW or (t is not None and t < f) or not latin(name):
            continue
        holders[off].append((f, t, name, h))
    for off in list(holders):
        if len(holders[off]) > 400:
            del holders[off]          # a general office again (thousands of holders)
            continue
        seen, keep = set(), []
        for f, t, name, h in sorted(holders[off], key=lambda x: (x[0], INF if x[1] is None else x[1], x[2], x[3])):
            if (h, f) in seen:
                continue
            seen.add((h, f))
            keep.append((f, t, name))
        holders[off] = keep
    # office names: the head's title from the town or province (e.g. "mayor of Paris") is not fetched separately;
    # the title is made from the place: see title_for() in TownFacts.java (mayor / governor / head).

    div_index, divs_out = {}, []
    off_index, offs_out = {}, []

    olab = labels("o_label")

    def office_idx(off):
        if off not in holders or not holders[off] or not latin(olab.get(off, "x")):
            return -1
        if off not in off_index:
            off_index[off] = len(offs_out)
            offs_out.append([f"Q{off}", olab.get(off, ""), [[f, t, n] for f, t, n in holders[off]]])
        return off_index[off]

    def div_idx(d):
        if d not in div_index:
            div_index[d] = len(divs_out)
            off = office_of.get(d, (None, None))[1]
            par, par_from = -1, None
            if rank_of(vtop.get(d, set())) != 1:
                for p in parent.get(d, []):
                    if p in vlab and rank_of(vtop.get(p, set())) == 1:
                        par = p
                        par_from = vfrom.get(p, 1990)
                        break
            divs_out.append([f"Q{d}", vlab[d], office_idx(off) if off else -1, par, par_from])
        return div_index[d]

    towns_out = []
    for q in towns_q:
        label = tlab.get(q)
        pt = points.get(q)
        if not label or not pt or not latin(label):
            report["left out: no name in Latin letters or no point"] += 1
            continue
        if ADMIN_WORDS.search(label):
            report["left out: a district, not a town"] += 1
            continue
        fy = founded.get(q)
        if f"Q{q}" in HAND_FOUNDED:
            hf = HAND_FOUNDED[f"Q{q}"]
            fy = None if hf is None else ((0, hf[0]), hf[0], hf[1])
        first_fig = min(figs[q]) if figs.get(q) else None
        hand = HAND_NAMES.get(f"Q{q}")
        if fy and ((first_fig is not None and first_fig < fy[1])
                   or (hand and any(a is None or a < fy[1] for a, b, n in hand))):
            fy = None             # the founding Wikidata gives is a refounding (Istanbul 1453, Tokyo 1868): left out
            report["founding years left out (the town is older)"] += 1
        segs = wd_periods(stmts.get(q, []), label)
        if wiki_periods_by_q.get(q):
            # The list is coarse (it leaves out spelling changes such as Christiania -> Kristiania in 1877), so it
            # fills the years Wikidata leaves open; the towns' own articles (HAND_NAMES) come last and win.
            segs = overlay(wiki_periods_by_q[q], [(back(a), back(b), n) for a, b, n in segs])
            report["towns named from the Wikipedia list"] += 1
        if hand:
            segs = overlay([], hand)    # the towns' own articles: the whole story of the names, nothing else
            report["towns named from the hand table"] += 1
        elif fy:
            segs = overlay(segs, [(None, fy[1], None)])   # no name before the town was founded
        names = tidy_periods(segs, label)
        if names:
            report["towns with names by era"] += 1
        also = [[a, b, n] for a, b, n in HAND_ALSO.get(f"Q{q}", [])]
        pts = []
        for y in sorted(figs.get(q, {})):
            vals = figs[q][y]
            pref = [v for p_, v in vals if p_]
            use = sorted(pref or [v for _, v in vals])
            pts.append((y, int(round(use[len(use) // 2]))))
        pts = thin(pts)
        flat = [x for yv in pts for x in yv]
        if pts:
            report["towns with population figures"] += 1
            report["population figures kept"] += len(pts)
        flags = (1 if q in ghost else 0) | (2 if q in ghost and q in ended else 0)
        # provinces: one per stretch of years, the best kind first
        st = []
        for d, f, t in adm.get(q, []):
            rk = rank_of(vtop.get(d, set()))
            if rk >= 8:
                continue
            if f is None and t is None:
                f = vfrom.get(d, 1990)
                t = vto.get(d)
                dated = False
            else:
                if f is None:
                    f = vfrom.get(d)
                if t is None:
                    t = vto.get(d)
                dated = True
            if f is not None and t is not None and t <= f:
                continue
            st.append((rk, 0 if dated else 1, d, f, t))
        dv = []
        if st:
            bounds = sorted({x[3] for x in st if x[3] is not None} | {x[4] for x in st if x[4] is not None})
            edges = [None] + bounds + [None]
            for i in range(len(edges) - 1):
                a, b = edges[i], edges[i + 1]
                best = None
                for x in st:
                    rk, und, d, f, t = x
                    if f is not None and (a is None or f > a):
                        continue
                    if t is not None and (b is None or t < b):
                        continue
                    if best is None or (rk, und) < (best[0], best[1]):
                        best = x
                if best is None:
                    continue
                if dv and dv[-1][2] == best[2] and dv[-1][1] == a:
                    dv[-1][1] = b
                else:
                    dv.append([a, b, best[2]])
        divs_town = [[a, b, div_idx(d)] for a, b, d in dv]
        if divs_town:
            report["towns with provinces"] += 1
        head = -1
        if q in office_of:
            head = office_idx(office_of[q][1])
            if head >= 0:
                report["towns with heads"] += 1
        row = [f"Q{q}", label, int(round(pt[0] * 1000)), int(round(pt[1] * 1000)), flags,
               fy[1] if fy else None, fy[2] if fy else None, names, flat, divs_town, head]
        if also:
            row.append(also)
        towns_out.append(row)
    # parents point at division numbers too (added after the towns so every parent has a row)
    for row in divs_out:
        p = row[3]
        row[3] = div_idx(p) if isinstance(p, int) and p > 0 else -1
    data = {
        "format": 1,
        "id": "towns",
        "source": ("Wikidata (CC0) through the QLever endpoint (qlever.dev), 2026-10-15: human settlements with a "
                   "population of 20,000 or more or a dated official name; names with dates (P1448, P2561), population "
                   "figures with their year (P1082, P585), founding (P571), the provinces and districts they lay in "
                   "(P131) and the holders of their heads' offices (P1313, P1906, P39). English Wikipedia's 'List of "
                   "city name changes' (CC BY-SA 4.0) for the dated renamings it lists, and a short table of famous "
                   "renamings written from the towns' Wikipedia articles (build_towns.py HAND_NAMES)."),
        "rule": ("A name holds for the years it is dated for (a change in the first half of a year counts from that "
                 "year); population figures: a straight line between two figures, never before the first, at most 15 "
                 "years after the last; a province: the best-dated statement of the best kind for that year; a head: "
                 "the holder whose term started last before or in that year."),
        "towns": towns_out,
        "divisions": divs_out,
        "offices": offs_out,
    }
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    tmp = OUT + ".tmp"
    with open(tmp, "wb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", compresslevel=9, mtime=0) as g:
            g.write(raw)
    json.loads(gzip.open(tmp).read())
    os.replace(tmp, OUT)
    report["towns"] = len(towns_out)
    report["divisions"] = len(divs_out)
    report["offices"] = len(offs_out)
    report["holders"] = sum(len(o[2]) for o in offs_out)
    report["json bytes"] = len(raw)
    report["gzip bytes"] = os.path.getsize(OUT)
    with open(REPORT, "w") as f:
        json.dump(dict(sorted(report.items())), f, indent=1)
    for k, v in sorted(report.items()):
        print(f"  {k}: {v:,}")


def check():
    data = json.load(gzip.open(OUT, "rt", encoding="utf-8"))
    bad = []
    towns, divs, offs = data["towns"], data["divisions"], data["offices"]
    seen = set()
    for t in towns:
        q, name, lat, lon, flags, fy, fp, names, pops, dv, head = t[:11]
        if q in seen:
            bad.append(f"{q}: twice")
        seen.add(q)
        if not name or not (-90000 <= lat <= 90000 and -180000 <= lon <= 180000):
            bad.append(f"{q}: name or point")
        prev = None
        for a, b, n in names:
            if a is not None and b is not None and b <= a:
                bad.append(f"{q}: empty name stretch {a}-{b}")
            if prev is not None and a is not None and prev is not None and a < prev:
                bad.append(f"{q}: name stretches overlap")
            prev = b if b is not None else INF
            if not n or norm(n) == norm(name):
                bad.append(f"{q}: name stretch with today's name")
        if len(pops) % 2 or len(pops) > 24:
            bad.append(f"{q}: population list")
        ys = pops[0::2]
        if ys != sorted(ys) or len(set(ys)) != len(ys):
            bad.append(f"{q}: population years not in order")
        for a, b, d in dv:
            if not (0 <= d < len(divs)):
                bad.append(f"{q}: province number")
        if head >= len(offs):
            bad.append(f"{q}: head number")
    for d in divs:
        if d[2] >= len(offs) or d[3] >= len(divs):
            bad.append(f"{d[0]}: office or parent number")
    for o in offs:
        ys = [h[0] for h in o[2]]
        if ys != sorted(ys):
            bad.append(f"{o[0]}: holders not in order")
    # spot checks: renamed towns in the right years
    by_q = {t[0]: t for t in towns}

    def name_at(q, y):
        t = by_q.get(q)
        if not t:
            return None
        for a, b, n in t[7]:
            if (a is None or a <= y) and (b is None or y < b):
                return n
        return t[1]

    expect = [("Q1156", 1990, "Bombay"), ("Q1156", 2000, "Mumbai"), ("Q1490", 1700, "Edo"), ("Q1490", 1900, "Tokyo"),
              ("Q3838", 1950, "Léopoldville"), ("Q3838", 1970, "Kinshasa"), ("Q656", 1950, "Leningrad"),
              ("Q656", 1920, "Petrograd"), ("Q656", 1800, "Saint Petersburg"), ("Q406", 1500, "Constantinople"),
              ("Q406", -500, "Byzantium"), ("Q406", 1950, "Istanbul"), ("Q914", 1940, "Stalingrad"),
              ("Q1352", 1950, "Madras"), ("Q1348", 1950, "Calcutta"), ("Q585", 1900, "Kristiania"),
              ("Q3921", 1970, "Salisbury")]
    for q, y, want in expect:
        got = name_at(q, y)
        if got != want:
            bad.append(f"{q} in {y}: {got!r}, expected {want!r}")
    print(f"check: {len(towns):,} towns, {len(divs):,} provinces, {len(offs):,} offices, "
          f"{sum(len(o[2]) for o in offs):,} holders; {len(bad)} problems")
    for b in bad[:30]:
        print("  " + b)
    return 1 if bad else 0


def main(argv):
    mode = argv[1] if len(argv) > 1 else ""
    if mode == "--wiki":
        wiki()
    elif mode == "--select":
        select()
    elif mode == "--divisions":
        divisions()
    elif mode == "--parents":
        parents()
    elif mode == "--offices":
        offices()
    elif mode == "--build":
        build()
    elif mode == "--check":
        return check()
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
