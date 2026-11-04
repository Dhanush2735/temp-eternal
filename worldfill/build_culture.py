#!/usr/bin/env python3
"""Step 30b (systems C13, C14, C17, C26, C27): who can read, how people measure, how well off they are, their scripts,
holy places, festivals and pilgrimages - for every place and year.

    python3 build_culture.py --fetch   download the figures (into build/culture/, not kept): Our World in Data's
                                       literacy rates, the Maddison Project's GDP per person, Wikipedia's
                                       "Metrication" article, and Wikidata's places of worship (QLever)
    python3 build_culture.py --build   write history/culture.json.gz and history/holy_places.json.gz into the mod
    python3 build_culture.py --check   read them back and check them (exit 1 on a problem)

Sources:
  * literacy: Our World in Data, "Literacy rate" (cross-country-literacy-rates; UNESCO 1953 and 1957, Buringh and van
    Zanden 2009, van Zanden et al. 2014, the UNESCO Institute for Statistics; CC BY 4.0), 235 countries, 1475-2024.
    A country without figures takes the mean of its UN subregion for the years they have; the game adds the years
    before the first figure (from the technology atlas: nobody reads where there is no writing; a few priests and
    scribes before printing; rising from the printing press to the first figure).
  * wealth: the Maddison Project Database 2023 (Bolt and van Zanden; CC BY 4.0): GDP per person in 2011 dollars, 169
    countries from year 1 to 2022; a country without figures takes its region's.
  * the metric system: the year each country began it (English Wikipedia, "Metrication", the table of all countries).
  * measures, scripts, festivals, pilgrimages, hard times: culture_table.py, by hand from Wikipedia's articles.
  * holy places: Wikidata (CC0), every place of worship with a point and 5 or more Wikipedia articles: its name, kind
    (mosque, Hindu temple, cathedral ...), faith, and the years it stood.

File layout (history/culture.json.gz, JSON): countries (the grid's codes), literacy {code: [year, percent, ...]},
literacyMark {code: "R" own figures | "S" the subregion's}, wealth {code: [year, dollars, ...]}, metric {code: year},
units [...], noSystem, notMetric, stillSaid, scripts {key: [[from, to, script], ...]}, latin [...], faiths [...],
crises [...].
history/holy_places.json.gz: places [[name, lat*1000, lon*1000, kind, faith, from, to, articles], ...] (from/to null:
unknown; the game names a place without a founding year only from 1950).
"""
import collections
import gzip
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modpack as M                 # noqa: E402
import culture_table as CT          # noqa: E402
import technology_table as TT       # noqa: E402
import build_country_grid as CG     # noqa: E402

BASE = os.path.join(HERE, "build", "culture")
RAW = os.path.join(BASE, "raw")
OUT = os.path.join(M.HISTORY, "culture.json.gz")
OUT_HOLY = os.path.join(M.HISTORY, "holy_places.json.gz")
REPORT = os.path.join(HERE, "logs", "step30b_culture_report.json")
LIT_CSV = os.path.join(BASE, "literacy.csv")
LIT_URL = ("https://ourworldindata.org/grapher/cross-country-literacy-rates.csv?v=1&csvType=full"
           "&useColumnShortNames=false")
MPD = os.path.join(BASE, "mpd2023_web.xlsx")
MPD_URL = "https://huggingface.co/datasets/yuiseki/maddison-project/resolve/main/raw/2023/mpd2023_web.xlsx"
METRIC_JSON = os.path.join(BASE, "metrication.json")
METRIC_URL = ("https://en.wikipedia.org/w/api.php?action=parse&page=Metrication&prop=wikitext&format=json"
              "&formatversion=2")
NOW = 2026
OWID_CODES = {"SSD": "SDS", "PSE": "PSX", "ESH": "SAH", "OWID_KOS": "KOS", "XKX": "KOS"}

HP_LIST = """SELECT ?x ?k (SAMPLE(?c) AS ?coord) WHERE {
  ?x wdt:P31/wdt:P279* wd:Q1370598 .
  ?x wdt:P625 ?c .
  ?x wikibase:sitelinks ?k .
  FILTER(xsd:integer(STR(?k)) >= 5)
} GROUP BY ?x ?k"""
HP_NAMES = """SELECT ?x ?l WHERE {
  VALUES ?x { %s }
  ?x rdfs:label ?l . FILTER(LANG(?l) = "en")
}"""
HP_FAITH = """SELECT ?x ?r ?rl WHERE {
  VALUES ?x { %s }
  ?x wdt:P140 ?r . ?r rdfs:label ?rl . FILTER(LANG(?rl) = "en")
}"""
HP_KIND = """SELECT ?x ?c ?cl WHERE {
  VALUES ?x { %s }
  ?x wdt:P31 ?c . ?c rdfs:label ?cl . FILTER(LANG(?cl) = "en")
}"""
HP_YEARS = """SELECT ?x ?which ?d WHERE {
  VALUES ?x { %s }
  { ?x wdt:P571 ?d . BIND("from" AS ?which) } UNION { ?x wdt:P576 ?d . BIND("to" AS ?which) }
}"""


def fc():
    import fetch_cards_wd
    fetch_cards_wd.RAW = RAW
    return fetch_cards_wd


def fetch():
    import requests
    os.makedirs(RAW, exist_ok=True)
    for path, url, headers in ((LIT_CSV, LIT_URL, {"User-Agent": "Our World In Data data fetch/1.0"}),
                               (MPD, MPD_URL, {}),
                               (METRIC_JSON, METRIC_URL, {"User-Agent": "EternalEngineDataBuild/1.0 (history data)"})):
        if not os.path.exists(path):
            r = requests.get(url, headers=headers, timeout=600)
            r.raise_for_status()
            open(path, "wb").write(r.content)
            print(f"  {os.path.basename(path)}: {len(r.content):,} bytes")
    f = fc()
    f.run(HP_LIST, "hp_list")
    from build_cards import qid_of
    qids = sorted({qid_of(r[0]) for r in rows("hp_list")} - {0})
    qs = [f"Q{q}" for q in qids]
    f.batches("hp_names", HP_NAMES, qs, 6000)
    f.batches("hp_faith", HP_FAITH, qs, 6000)
    f.batches("hp_kind", HP_KIND, qs, 6000)
    f.batches("hp_years", HP_YEARS, qs, 6000)


def rows(prefix):
    from build_cards import rows_in
    return rows_in(RAW, prefix)


def year_of(cell):
    if not cell or cell.startswith("<"):
        return None
    m = re.match(r'^"?(-?)(\d+)-', cell)
    if not m:
        return None
    y = int(m.group(2)) * (-1 if m.group(1) else 1)
    return y - 1 if y <= 0 else y


def faith_key(text):
    """The faith family of a name ("Catholic Church" -> christian_west); None when nothing matches."""
    t = (text or "").lower()
    for f in CT.FAITHS:
        for m in f["match"]:
            if m in t:
                return f["key"]
    return None


KIND_FAITH = [("mosque", "muslim"), ("masjid", "muslim"), ("church", "christian_west"), ("cathedral", "christian_west"),
              ("basilica", "christian_west"), ("chapel", "christian_west"), ("abbey", "christian_west"),
              ("monastery", None), ("priory", "christian_west"), ("minster", "christian_west"),
              ("hindu temple", "hindu"), ("mandir", "hindu"), ("synagogue", "jewish"), ("buddhist temple", "buddhist"),
              ("stupa", "buddhist"), ("pagoda", "buddhist"), ("wat", "buddhist"), ("vihara", "buddhist"),
              ("gurdwara", "sikh"), ("shinto shrine", "shinto"), ("jinja", "shinto"), ("jain temple", "jain"),
              ("fire temple", "zoroastrian"), ("taoist temple", "chinese_folk"), ("confucian", "chinese_folk")]


def build():
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    import pandas as pd
    report = collections.Counter()
    countries, _rows = CG.read()
    codes = [c[0] for c in countries]
    idx = {c: i for i, c in enumerate(codes)}
    sub_of = {c[0]: c[2] for c in countries}
    feats = json.load(open(CG.NE, encoding="utf-8"))["features"] if os.path.exists(CG.NE) else []
    ne_names = {}
    for keys in (("NAME", "NAME_LONG", "ADMIN", "NAME_EN", "FORMAL_EN", "NAME_SORT"), ("SOVEREIGNT",)):
        for f in feats:            # a country's own names first, its sovereign's name only after
            p = f["properties"]
            for k in keys:
                if p.get(k):
                    ne_names.setdefault(p[k].lower(), p["ADM0_A3"])
    for c in countries:
        ne_names.setdefault(c[1].lower(), c[0])

    # ---------------------------------------------------------------------------------------------- literacy
    lit = collections.defaultdict(dict)
    df = pd.read_csv(LIT_CSV)
    for name, code, year, val in df[["Entity", "Code", "Year", "Literacy rate"]].itertuples(index=False):
        if not isinstance(code, str):
            continue
        code = OWID_CODES.get(code, code)
        if code in idx and val == val:
            lit[code][int(year)] = round(float(val), 1)
    lit_mark = {c: "R" for c in lit}
    by_sub = collections.defaultdict(list)
    for c in codes:
        by_sub[sub_of[c]].append(c)
    for c in codes:
        if c in lit:
            continue
        pts = collections.defaultdict(list)
        for o in by_sub[sub_of[c]]:
            if o in lit and lit_mark.get(o) == "R":
                for y, v in lit[o].items():
                    pts[y].append(v)
        if pts:
            lit[c] = {y: round(sum(v) / len(v), 1) for y, v in pts.items() if len(v) >= 1}
            lit_mark[c] = "S"
    report["literacy: countries with own figures"] = sum(1 for m in lit_mark.values() if m == "R")
    report["literacy: countries from their subregion"] = sum(1 for m in lit_mark.values() if m == "S")
    literacy = {c: [x for y in sorted(v) for x in (y, v[y])] for c, v in sorted(lit.items())}

    # ------------------------------------------------------------------------------------------------- wealth
    mp = pd.read_excel(MPD, sheet_name="Full data")
    wealth = collections.defaultdict(dict)
    region_of = {}
    for code, region, year, g in mp[["countrycode", "region", "year", "gdppc"]].itertuples(index=False):
        region_of[code] = region
        if g == g and code in idx:
            wealth[code][int(year)] = int(round(float(g)))
    report["wealth: countries with own figures"] = len(wealth)
    # regions: the Maddison regional series (from 1820)
    rd = pd.read_excel(MPD, sheet_name="Regional data", header=None)
    names = [str(x) for x in rd.iloc[1, 1:9]]
    regional = collections.defaultdict(dict)
    for r in range(2, len(rd)):
        y = rd.iloc[r, 0]
        if y != y:
            continue
        for k, nm in enumerate(names):
            v = rd.iloc[r, 1 + k]
            if v == v:
                regional[nm][int(y)] = int(round(float(v)))
    sub_region = {}
    for c in codes:          # the Maddison region of a country without figures: its neighbours'
        if c in region_of:
            sub_region[c] = region_of[c]
    sub_votes = collections.defaultdict(collections.Counter)
    for c, rg in sub_region.items():
        sub_votes[sub_of.get(c, "")][rg] += 1
    filled = 0
    for c in codes:
        if c in wealth and len(wealth[c]) >= 3:
            continue
        rg = sub_region.get(c) or (sub_votes[sub_of[c]].most_common(1)[0][0] if sub_votes[sub_of[c]] else None)
        if rg and rg in regional:
            own = wealth.get(c, {})
            wealth[c] = dict(regional[rg]) | own
            filled += 1
    report["wealth: countries from their region"] = filled
    wealth_out = {}
    for c, v in sorted(wealth.items()):
        keep = []
        for y in sorted(v):
            if y <= 1820 or (y < 1950 and y % 10 == 0) or y % 5 == 0 or y == max(v):
                keep.append((y, v[y]))
        wealth_out[c] = [x for y, g in keep for x in (y, g)]

    # --------------------------------------------------------------------------------------- the metric system
    text = json.load(open(METRIC_JSON, encoding="utf-8"))["parse"]["wikitext"]
    text = re.sub(r"<ref[^>]*/>", "", text)
    text = re.sub(r"<ref[^>]*>.*?</ref>", "", text, flags=re.S)
    i = text.find('{| class="wikitable sortable plainrowheaders"')
    j = text.find("\n|}", i)
    table = text[i:j]
    metric = {}
    year = None
    unknown = []
    aliases = {"united states": "USA", "us": "USA", "soviet union": "RUS", "russia": "RUS", "korea": "KOR",
               "south korea": "KOR", "north korea": "PRK", "burma": "MMR", "myanmar": "MMR", "taiwan": "TWN",
               "ivory coast": "CIV", "côte d'ivoire": "CIV", "czechoslovakia": "CZE", "yugoslavia": "SRB",
               "east timor": "TLS", "gambia": "GMB", "the gambia": "GMB", "bahamas": "BHS", "the bahamas": "BHS",
               "democratic republic of the congo": "COD", "republic of the congo": "COG", "congo": "COG",
               "cape verde": "CPV", "eswatini": "SWZ", "swaziland": "SWZ", "north macedonia": "MKD",
               "macedonia": "MKD", "palestine": "PSX", "vatican city": "VAT", "hong kong": "HKG", "macau": "MAC",
               "united kingdom": "GBR", "uk": "GBR", "ireland": "IRL", "liberia": "LBR"}
    for line in table.split("\n"):
        m = re.match(r'^\|\s*(?:rowspan="?\d+"?\s*\|\s*)?(\d{4})', line)
        if m:
            year = int(m.group(1))
            continue
        m = re.match(r'^!\s*scope="row"\s*\|\s*(.+)$', line)
        if m and year:
            name = m.group(1)
            name = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]+)\]\]", r"\1", name)
            name = re.sub(r"\{\{[^}]*\}\}", "", name)
            name = re.sub(r"<[^>]+>", "", name).strip().strip("'").strip()
            name = re.sub(r"\s*\(.*?\)\s*", " ", name).strip()      # "Austria (including Austrian Poland)"
            name = re.sub(r"\d{4}$", "", name).strip()                 # "Greece1959"
            key = name.lower()
            code = aliases.get(key) or ne_names.get(key)
            if code and code in idx:
                metric.setdefault(code, year)
            else:
                unknown.append(name)
    report["metric: countries with a year"] = len(metric)
    report["metric: names not matched"] = len(unknown)
    # Where the table is silent (it lists 74 countries): a few years from the countries' own Wikipedia articles,
    # then the colonial power's time, then 1970 (marked as estimated in metricMark).
    metric_mark = {c: "R" for c in metric}
    for c, y in CT.METRIC_MORE.items():
        if c not in metric:
            metric[c] = y
            metric_mark[c] = "R"
    # the parts of former unions follow the union's year where they have none of their own
    for child, parent in (("SVK", "CZE"), ("UKR", "RUS"), ("BLR", "RUS"), ("KAZ", "RUS"), ("UZB", "RUS"),
                          ("TKM", "RUS"), ("TJK", "RUS"), ("KGZ", "RUS"), ("MDA", "RUS"), ("GEO", "RUS"),
                          ("ARM", "RUS"), ("AZE", "RUS"), ("LTU", "RUS"), ("LVA", "RUS"), ("EST", "RUS"),
                          ("HRV", "SRB"), ("SVN", "SRB"), ("BIH", "SRB"), ("MNE", "SRB"), ("MKD", "SRB"),
                          ("KOS", "SRB"), ("BGD", "PAK"), ("ERI", "ETH"), ("SDS", "SDN"), ("TLS", "IDN")):
        if child not in metric and parent in metric:
            metric[child] = metric[parent]
            metric_mark[child] = "E"
    for group, y in CT.METRIC_COLONIAL:
        for c in group:
            if c in idx and c not in metric:
                metric[c] = y
                metric_mark[c] = "E"
    for c in codes:
        if c not in metric:
            metric[c] = CT.METRIC_DEFAULT
            metric_mark[c] = "E"

    # --------------------------------------------------------------------------------------------- the tables
    from build_technology_atlas import resolve_groups
    subregion_of = {c[0]: c[2] for c in countries}
    expand = resolve_groups(countries, subregion_of)
    units = []
    for u in CT.UNITS:
        where = sorted({c for w in u["where"] for c in expand(w)})
        units.append({k: v for k, v in u.items() if k != "where"} | {"where": where})
    crises = []
    for c in CT.CRISES:
        crises.append({k: v for k, v in c.items() if k != "where"} | {"where": sorted(c["where"])})

    # ------------------------------------------------------------------------------------------- holy places
    from build_cards import qid_of, literal, point
    pts = {}
    arts = {}
    for r in rows("hp_list"):
        q = qid_of(r[0])
        p = point(r[2]) if len(r) > 2 else None
        if q and p:
            pts[q] = p
            try:
                arts[q] = int(float(r[1]))
            except ValueError:
                arts[q] = 0
    name = {qid_of(r[0]): literal(r[1]) for r in rows("hp_names")}
    faith = {}
    for r in rows("hp_faith"):
        q = qid_of(r[0])
        k = faith_key(literal(r[2]))
        if k and q not in faith:
            faith[q] = k
    kind = {}
    for r in rows("hp_kind"):
        q = qid_of(r[0])
        lab = literal(r[2])
        if not lab:
            continue
        low = lab.lower()
        if any(g == low or g in low for g in CT.HOLY_GENERIC_KINDS) and "church building" not in low:
            continue          # "structure of worship", "cathedral library": say nothing rather than that
        score = 2 if any(w in low for w, _ in KIND_FAITH) else 1 if any(w in low for w in CT.HOLY_WORDS) else 0
        if q not in kind or score > kind[q][0] or (score == kind[q][0] and len(lab) < len(kind[q][1])):
            kind[q] = (score, lab)
    years_from, years_to = {}, {}
    for r in rows("hp_years"):
        q = qid_of(r[0])
        y = year_of(r[2])
        if y is None or y > NOW:
            continue
        if r[1].strip('"') == "from":
            years_from[q] = min(years_from.get(q, y), y)
        else:
            years_to[q] = max(years_to.get(q, y), y)
    holy = []
    for q, (la, lo) in sorted(pts.items()):
        nm = name.get(q)
        if not nm or not re.search(r"[A-Za-z]", nm):
            report["holy places left out: no English name"] += 1
            continue
        k = kind.get(q, (0, ""))[1]
        fk = faith.get(q)
        if not fk and not any(w in k.lower() for w in CT.HOLY_WORDS):
            report["left out: not a holy place (a town, a valley, a palace ...)"] += 1
            continue
        if fk is None:
            low = k.lower()
            for w, f in KIND_FAITH:
                if w in low and f:
                    fk = f
                    break
        shown = (k.replace("church building", "church").replace("minor basilica", "basilica")
                 .replace("Catholic cathedral", "cathedral") if k else "")
        y_from, y_to = years_from.get(q), years_to.get(q)
        if nm in CT.HOLY_YEARS and y_from is None:
            y_from, y_to = CT.HOLY_YEARS[nm][0], CT.HOLY_YEARS[nm][1] if y_to is None else y_to
            report["holy places dated from the hand table"] += 1
        if y_from is None and not fk:
            # no faith and no year: mostly the ruins of old temples (Heliopolis), not a holy place people use today
            report["left out: neither a faith nor a founding year"] += 1
            continue
        holy.append([nm, int(round(la * 1000)), int(round(lo * 1000)), shown, fk or "", y_from, y_to, arts.get(q, 0)])
        report["holy places"] += 1
        if years_from.get(q) is not None:
            report["holy places with a founding year"] += 1
        if fk:
            report["holy places with a faith"] += 1

    data = {
        "format": 1, "id": "culture",
        "source": ("Our World in Data, Literacy rate (UNESCO; Buringh and van Zanden 2009; van Zanden et al. 2014; "
                   "CC BY 4.0); the Maddison Project Database 2023 (Bolt and van Zanden; CC BY 4.0); English "
                   "Wikipedia ('Metrication' and the articles named in worldfill/culture_table.py)."),
        "countries": codes, "literacy": literacy, "literacyMark": lit_mark, "wealth": wealth_out, "metric": metric,
        "metricMark": metric_mark,
        "units": units, "noSystem": CT.NO_SYSTEM, "notMetric": sorted(CT.NOT_METRIC), "stillSaid": CT.STILL_SAID_YEARS,
        "scripts": {k: [list(p) for p in v] for k, v in CT.SCRIPTS.items()}, "latin": CT.LATIN,
        "faiths": [{k: (v if k not in ("festivals", "pilgrimages") else [list(x) for x in v]) for k, v in f.items()}
                   for f in CT.FAITHS],
        "crises": crises,
        "literacyBase": [{"where": sorted(w), "start": a, "end": b, "share": v} for w, a, b, v in CT.LITERACY_BASE],
        "literacyBaseDefault": CT.LITERACY_BASE_DEFAULT,
        "holyDefaultFrom": CT.HOLY_DEFAULT_FROM,
    }
    write(OUT, data)
    write(OUT_HOLY, {"format": 1, "id": "holy_places",
                     "source": "Wikidata (CC0) through QLever, 2026-10-15: places of worship with 5 or more articles",
                     "places": holy})
    report["culture gzip bytes"] = os.path.getsize(OUT)
    report["holy places gzip bytes"] = os.path.getsize(OUT_HOLY)
    with open(REPORT, "w") as f:
        json.dump(dict(sorted(report.items())) | {"metric names not matched": unknown[:60]}, f, indent=1,
                  ensure_ascii=False)
    for k, v in sorted(report.items()):
        print(f"  {k}: {v:,}")
    if unknown:
        print("  metric names not matched:", ", ".join(unknown[:40]))


def write(path, data):
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with open(path + ".tmp", "wb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", compresslevel=9, mtime=0) as g:
            g.write(raw)
    json.loads(gzip.open(path + ".tmp").read())
    os.replace(path + ".tmp", path)


def check():
    d = json.load(gzip.open(OUT, "rt", encoding="utf-8"))
    h = json.load(gzip.open(OUT_HOLY, "rt", encoding="utf-8"))
    bad = []

    def series_at(s, y):
        pts = list(zip(s[0::2], s[1::2]))
        if y <= pts[0][0]:
            return pts[0][1]
        for (y0, v0), (y1, v1) in zip(pts, pts[1:]):
            if y0 <= y <= y1:
                return v0 + (v1 - v0) * (y - y0) / max(1, y1 - y0)
        return pts[-1][1]

    for code, y, lo, hi in (("IND", 1901, 5, 8), ("IND", 2011, 60, 80), ("GBR", 1650, 40, 60), ("FRA", 1475, 1, 15)):
        s = d["literacy"].get(code)
        v = series_at(s, y) if s else None
        if v is None or not lo <= v <= hi:
            bad.append(f"literacy {code} {y}: {v}")
    for code, y, lo, hi in (("IND", 1900, 600, 1400), ("USA", 2000, 30000, 60000), ("GBR", 1700, 2000, 5000)):
        s = d["wealth"].get(code)
        v = series_at(s, y) if s else None
        if v is None or not lo <= v <= hi:
            bad.append(f"wealth {code} {y}: {v}")
    for code, want in (("FRA", 1795), ("IND", 1956), ("JPN", 1924)):
        got = d["metric"].get(code)
        if got is None or abs(got - want) > 10:
            bad.append(f"metric {code}: {got}, expected about {want}")
    if len(h["places"]) < 10000:
        bad.append(f"only {len(h['places'])} holy places")
    names = {p[0] for p in h["places"]}
    for want in ("Mecca Masjid", "Golden Temple", "Notre-Dame de Paris", "Hagia Sophia"):
        if not any(want.lower() in n.lower() for n in names):
            bad.append(f"no holy place {want}")
    for c in d["countries"]:
        if c not in d["literacy"] and c not in ("ATA", "HMD", "ATF", "SGS", "CLP", "BJN", "SER", "ATC", "CSI", "PGA",
                                                "SCR", "IOA", "IOT", "UMI", "BRT", "SPI", "KAS", "USG", "CNM", "ESB",
                                                "WSB", "KAB", "BRI"):
            bad.append(f"no literacy for {c}")
    print(f"check: literacy for {len(d['literacy'])} countries, wealth for {len(d['wealth'])}, metric years for "
          f"{len(d['metric'])}, {len(d['units'])} unit systems, {len(d['scripts'])} scripts, {len(d['faiths'])} faiths, "
          f"{len(h['places']):,} holy places; {len(bad)} problems")
    for b in bad[:30]:
        print("  " + b)
    return 1 if bad else 0


def main(argv):
    mode = argv[1] if len(argv) > 1 else ""
    if mode == "--fetch":
        fetch()
    elif mode == "--build":
        build()
        return check()
    elif mode == "--check":
        return check()
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
