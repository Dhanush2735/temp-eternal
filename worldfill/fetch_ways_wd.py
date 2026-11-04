#!/usr/bin/env python3
# ============================================================
# Step 34 (B14, B15, B18, B24-mines, B26): the works of the past
# — railways and stations, bridges and canals, ports and light-
# houses, factories and power stations, mills and shipyards,
# caravanserais and pilgrim ways — fetched from Wikidata, each
# with a point, and with a year where Wikidata has one.
#
#   python3 fetch_ways_wd.py --check    verify every class QID against its label
#   python3 fetch_ways_wd.py --fetch    the rows -> build/ways/raw/class_Q*.json
#   python3 fetch_ways_wd.py --labels   English names for the QIDs fetched
#   python3 fetch_ways_wd.py --report   what came back, and what the test places gain
#
# How it works, and why it looks like this:
#
#  * Every class QID was read back from Wikidata before it was used. Step 34's
#    first draft guessed 60 of them and ~30 were something else entirely
#    (Q11446 is a ship, not a railway; Q192242 is frustration, not a
#    caravanserai). --check repeats that read-back whenever the list changes.
#  * Rows are fetched, not counted: a COUNT over `P31/P279*` times out on the
#    public endpoint, streaming the rows with a notability filter does not.
#  * One pass per class, dated and undated together. The undated rows are
#    kept on purpose: they are the ones that get their year from the
#    technology atlas (a station cannot predate the railway in its country),
#    and they are marked as estimated when the pack is built. Wikidata has
#    136,674 railway stations with a point but only 79,333 with a year.
#  * Notability floor 3 (decision 5 of part 1): stations, bridges and mines
#    are written about far less than monuments, and at 5 the sawmill and
#    gasworks classes fall to single figures.
#  * The date properties: inception (P571), date of official opening (P1619),
#    start time (P580) — opening first, because a railway line or a canal is
#    opened, not "incepted". End: dissolution (P576), end time (P582).
#  * B24 (what lies under the ground) is NOT here. Wikidata's gold mine class
#    has 2 items; B24 comes from USGS MRDS in part 4.
# ============================================================
import json
import os
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "build", "ways", "raw")
UA = "EternalEngineDataBuild/1.0 (history data; Eternal Engine Minecraft mod)"

PREFIXES = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX wikibase: <http://wikiba.se/ontology#>
"""

ENDPOINTS = [
    ("wdqs", "https://query.wikidata.org/sparql", 240),
    ("qlever", "https://qlever.dev/api/wikidata", 600),
]

MIN_SITELINKS = 3

# qid -> (name, system, what kind of thing it is in the mod's own words)
# Every one of these was read back from Wikidata; see logs/step34_part1_notes.md.
CLASSES = {
    # -- B14 railways ------------------------------------------------------
    "Q728937":  ("railway line",       "B14", "rail"),
    "Q55488":   ("railway station",    "B14", "station"),
    "Q928830":  ("metro station",      "B14", "station"),
    "Q2175765": ("tram stop",          "B14", "station"),
    "Q1311958": ("railway tunnel",     "B14", "rail"),
    "Q420962":  ("heritage railway",   "B14", "rail"),
    # -- B15 waterways -----------------------------------------------------
    "Q12280":   ("bridge",             "B15", "bridge"),
    "Q39715":   ("lighthouse",         "B15", "port"),
    "Q12284":   ("canal",              "B15", "canal"),
    "Q44782":   ("port",               "B15", "port"),
    "Q283202":  ("harbor",           "B15", "port"),
    "Q12323":   ("dam",                "B15", "dam"),
    "Q105731":  ("lock",              "B15", "canal"),
    "Q1066997": ("weir",               "B15", "canal"),
    "Q828909":  ("wharf",              "B15", "port"),
    "Q811177":  ("dry dock",           "B15", "port"),
    "Q1478783": ("ferry port",         "B15", "port"),
    "Q1359152": ("sea wall",           "B15", "port"),
    # -- B18 industry and utilities ---------------------------------------
    "Q83405":   ("factory",            "B18", "works"),
    "Q159719":  ("power station",      "B18", "power"),
    "Q15911738": ("hydroelectric power station", "B18", "power"),
    "Q6558431": ("coal-fired power station",     "B18", "power"),
    "Q12353044": ("oil refinery",      "B18", "works"),
    "Q505213":  ("sawmill",            "B18", "mill"),
    "Q2069494": ("steel mill",         "B18", "works"),
    "Q46398483": ("textile factory",   "B18", "works"),
    "Q256132":  ("telephone exchange", "B18", "power"),
    "Q1495738": ("gasworks",           "B18", "works"),
    "Q185187":  ("watermill",          "B18", "mill"),
    "Q38720":   ("windmill",           "B18", "mill"),
    "Q190928":  ("shipyard",           "B18", "works"),
    "Q174814":  ("electrical substation", "B18", "power"),
    "Q1248784": ("airport",            "B18", "air"),
    "Q820477":  ("mine",               "B18", "mine"),
    # -- B26 rest houses and road marks -----------------------------------
    "Q186347":  ("caravanserai",       "B26", "rest"),
    "Q337912":  ("pilgrims' way",      "B26", "way"),
    "Q28532565": ("post station",      "B26", "rest"),
    "Q966002":  ("coaching inn",       "B26", "rest"),
    "Q194029":  ("Roman road",         "B26", "way"),
    "Q11410923": ("ancient road",      "B26", "way"),
}

ROWS = """SELECT ?x ?coord ?incept ?open ?start ?end ?stop ?country ?k WHERE {{
  ?x wdt:P31/wdt:P279* wd:{q} ;
     wdt:P625 ?coord ;
     wikibase:sitelinks ?k .
  OPTIONAL {{ ?x wdt:P571  ?incept }}
  OPTIONAL {{ ?x wdt:P1619 ?open   }}
  OPTIONAL {{ ?x wdt:P580  ?start  }}
  OPTIONAL {{ ?x wdt:P576  ?end    }}
  OPTIONAL {{ ?x wdt:P582  ?stop   }}
  OPTIONAL {{ ?x wdt:P17   ?country }}
  FILTER(?k >= {floor})
}}"""


def ask(query, retries=4):
    """One query, tried on each endpoint in turn. Rows as a list of dicts."""
    body = PREFIXES + query
    for attempt in range(retries):
        for name, url, timeout in ENDPOINTS:
            try:
                t = time.time()
                r = requests.get(url, params={"query": body}, timeout=timeout,
                                 headers={"Accept": "application/sparql-results+json",
                                          "User-Agent": UA})
                if r.status_code in (429, 500, 502, 503, 504):
                    raise RuntimeError(f"{name}: HTTP {r.status_code}")
                r.raise_for_status()
                # strict=False: WDQS sometimes emits a raw newline inside a
                # string literal; the strict parser rejects the whole response.
                return (json.loads(r.text, strict=False)["results"]["bindings"],
                        name, time.time() - t)
            except Exception as e:  # noqa: BLE001 - retried on the next endpoint
                print(f"      {e} ({time.time() - t:.0f}s)", flush=True)
                time.sleep(3)
        wait = 10 * (attempt + 1)
        print(f"      all endpoints failed; again in {wait} s", flush=True)
        time.sleep(wait)
    return [], "failed", 0.0


def check():
    qids = sorted(CLASSES, key=lambda q: int(q[1:]))
    values = " ".join("wd:" + q for q in qids)
    rows, ep, dt = ask(
        f'SELECT ?x ?xLabel WHERE {{ VALUES ?x {{ {values} }} '
        f'?x rdfs:label ?xLabel . FILTER(LANG(?xLabel) = "en") }}')
    labels = {r["x"]["value"].rsplit("/", 1)[-1]: r["xLabel"]["value"] for r in rows}
    print(f"class QIDs, checked against Wikidata ({ep}, {dt:.1f}s)")
    bad = 0
    for q in qids:
        real = labels.get(q, "<none>")
        want = CLASSES[q][0]
        ok = real.lower() == want.lower()
        bad += 0 if ok else 1
        print(f"  {q:12s} {real[:34]:34s} {'ok' if ok else 'MISMATCH (assumed %r)' % want}")
    print(f"  {len(qids) - bad} of {len(qids)} match")
    return labels


def year(v):
    """Wikidata date -> int year, or None. Handles -0500-01-01T00:00:00Z."""
    if not v:
        return None
    s = v.lstrip("+")
    neg = s.startswith("-")
    s = s.lstrip("-")
    if not s[:4].isdigit():
        return None
    y = int(s[:4])
    return -y if neg else y


def point(v):
    """Point(lon lat) -> (lat, lon)."""
    try:
        lon, lat = v[v.index("(") + 1:v.index(")")].split()
        return float(lat), float(lon)
    except Exception:  # noqa: BLE001
        return None


def fetch():
    os.makedirs(RAW, exist_ok=True)
    for q, (name, system, kind) in sorted(CLASSES.items(), key=lambda kv: int(kv[0][1:])):
        path = os.path.join(RAW, f"class_{q}.json")
        if os.path.exists(path) and os.path.getsize(path) > 50:
            n = len(json.load(open(path, encoding="utf-8")))
            print(f"  {name:32s} {n:>7,} rows (cached)", flush=True)
            continue
        rows, ep, dt = ask(ROWS.format(q=q, floor=MIN_SITELINKS))
        out, seen = [], set()
        for r in rows:
            qid = r["x"]["value"].rsplit("/", 1)[-1]
            if qid in seen:          # a class or a country repeated the row
                continue
            ll = point(r["coord"]["value"])
            if not ll:
                continue
            seen.add(qid)
            g = lambda k: r[k]["value"] if k in r else None  # noqa: E731
            start, how = None, None
            for k, tag in (("open", "opened"), ("incept", "inception"), ("start", "start")):
                y = year(g(k))
                if y is not None:
                    start, how = y, tag
                    break
            end = year(g("end"))
            if end is None:
                end = year(g("stop"))
            out.append({"q": qid, "lat": round(ll[0], 4), "lon": round(ll[1], 4),
                        "start": start, "how": how, "end": end,
                        "cc": (g("country") or "").rsplit("/", 1)[-1],
                        "links": int(r["k"]["value"]), "cls": q, "kind": kind,
                        "sys": system})
        json.dump(out, open(path, "w", encoding="utf-8"))
        dated = sum(1 for r in out if r["start"] is not None)
        print(f"  {name:32s} {len(out):>7,} rows, {dated:>7,} with a year"
              f"  ({ep}, {dt:.0f}s)", flush=True)
        time.sleep(1.0)


def labels_for():
    """English names for every QID fetched, from the wbgetentities API."""
    qids = set()
    for q in CLASSES:
        path = os.path.join(RAW, f"class_{q}.json")
        if os.path.exists(path):
            for r in json.load(open(path, encoding="utf-8")):
                qids.add(r["q"])
    qids = sorted(qids)
    path = os.path.join(RAW, "labels.json")
    have = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    todo = [q for q in qids if q not in have]
    print(f"{len(qids):,} QIDs, {len(have):,} named already, {len(todo):,} to fetch")
    URL = "https://www.wikidata.org/w/api.php"
    for i in range(0, len(todo), 45):
        chunk = todo[i:i + 45]
        for attempt in range(4):
            try:
                r = requests.get(URL, params={"action": "wbgetentities", "ids": "|".join(chunk),
                                              "props": "labels", "languages": "en",
                                              "format": "json"},
                                 timeout=60, headers={"User-Agent": UA})
                if r.status_code != 200 or not r.text.lstrip().startswith("{"):
                    raise RuntimeError(f"HTTP {r.status_code}")
                for q, e in r.json().get("entities", {}).items():
                    lb = e.get("labels", {}).get("en", {}).get("value")
                    if lb:
                        have[q] = lb
                break
            except Exception as e:  # noqa: BLE001
                print(f"      {e}; again in {5 * (attempt + 1)} s", flush=True)
                time.sleep(5 * (attempt + 1))
        if (i // 45) % 200 == 0:
            json.dump(have, open(path, "w", encoding="utf-8"))
            print(f"  {len(have):,} names  ({i + len(chunk):,}/{len(todo):,})", flush=True)
        time.sleep(0.02)
    json.dump(have, open(path, "w", encoding="utf-8"))
    print(f"{len(have):,} names saved to {path}")


# rdfs:label, not SERVICE wikibase:label: the label service answers some of
# these classes and silently returns nothing for others (tram stop, steel mill,
# hydroelectric — every one of them came back empty with HTTP 200), and QLever
# rejects the label service outright.
LABELS = """SELECT ?x ?xLabel WHERE {{
  ?x wdt:P31/wdt:P279* wd:{q} ;
     wdt:P625 ?coord ;
     wikibase:sitelinks ?k .
  FILTER(?k >= {floor})
  ?x rdfs:label ?xLabel . FILTER(LANG(?xLabel) = "en")
}}"""


def labels_sparql():
    """English names straight out of SPARQL.

    The wbgetentities API is the usual way (labels_for) but it is one HTTP
    call per 45 QIDs — 2,700 calls for this step, which the public API
    stretches over hours. The label service answers a whole class in one
    query. It is slower per row, so it is tried per class and the API
    finishes anything it misses.
    """
    path = os.path.join(RAW, "labels.json")
    have = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    for q, (name, system, kind) in sorted(CLASSES.items(), key=lambda kv: int(kv[0][1:])):
        src = os.path.join(RAW, f"class_{q}.json")
        if not os.path.exists(src):
            continue
        rows = json.load(open(src, encoding="utf-8"))
        missing = [r for r in rows if r["q"] not in have]
        if not missing:
            print(f"  {name:32s} named already", flush=True)
            continue
        got, ep, dt = ask(LABELS.format(q=q, floor=MIN_SITELINKS))
        n = 0
        for r in got:
            qid = r["x"]["value"].rsplit("/", 1)[-1]
            lb = r.get("xLabel", {}).get("value", "")
            if lb and not lb.startswith("Q") and qid not in have:
                have[qid] = lb
                n += 1
        json.dump(have, open(path, "w", encoding="utf-8"))
        print(f"  {name:32s} {n:>7,} names ({len(have):,} held)  ({ep}, {dt:.0f}s)", flush=True)
        time.sleep(1.0)
    print(f"{len(have):,} names saved")


def labels_any():
    """Names for the rows Wikidata has no English label for.

    About 2,700 of the 122,000 rows (tram stops in Vitoria-Gasteiz, stations
    in Kyiv) carry a Spanish, Russian, Basque or Dutch label and no English
    one. The query route cannot see them, so the API fetches them in whatever
    language they have; the pack marks them as untranslated.
    """
    path = os.path.join(RAW, "labels.json")
    have = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    other = json.load(open(os.path.join(RAW, "labels_other.json"))) \
        if os.path.exists(os.path.join(RAW, "labels_other.json")) else {}
    todo = set()
    for f in os.listdir(RAW):
        if f.startswith("class_"):
            for r in json.load(open(os.path.join(RAW, f), encoding="utf-8")):
                if r["q"] not in have and r["q"] not in other:
                    todo.add(r["q"])
    todo = sorted(todo)
    print(f"{len(todo):,} QIDs with no English name")
    URL = "https://www.wikidata.org/w/api.php"
    for i in range(0, len(todo), 45):
        chunk = todo[i:i + 45]
        for attempt in range(5):
            try:
                r = requests.get(URL, params={"action": "wbgetentities", "ids": "|".join(chunk),
                                              "props": "labels", "format": "json"},
                                 timeout=60, headers={"User-Agent": UA})
                if r.status_code != 200 or not r.text.lstrip().startswith("{"):
                    raise RuntimeError(f"HTTP {r.status_code}")
                for q, e in r.json().get("entities", {}).items():
                    labs = e.get("labels", {})
                    if "en" in labs:
                        have[q] = labs["en"]["value"]
                    elif labs:
                        lang = sorted(labs)[0]
                        other[q] = {"n": labs[lang]["value"], "l": lang}
                break
            except Exception as e:  # noqa: BLE001
                print(f"      {e}; again in {10 * (attempt + 1)} s", flush=True)
                time.sleep(10 * (attempt + 1))
        if (i // 45) % 20 == 0:
            json.dump(have, open(path, "w", encoding="utf-8"))
            json.dump(other, open(os.path.join(RAW, "labels_other.json"), "w", encoding="utf-8"))
            print(f"  {i + len(chunk):,}/{len(todo):,}  ({len(other):,} untranslated)", flush=True)
        time.sleep(1.0)
    json.dump(have, open(path, "w", encoding="utf-8"))
    json.dump(other, open(os.path.join(RAW, "labels_other.json"), "w", encoding="utf-8"))
    print(f"{len(have):,} English names, {len(other):,} untranslated names")


def report():
    from collections import Counter
    tot, dated, by_sys, by_cls, years = 0, 0, Counter(), Counter(), Counter()
    for q, (name, system, kind) in CLASSES.items():
        path = os.path.join(RAW, f"class_{q}.json")
        if not os.path.exists(path):
            continue
        rows = json.load(open(path, encoding="utf-8"))
        d = sum(1 for r in rows if r["start"] is not None)
        tot += len(rows)
        dated += d
        by_sys[system] += len(rows)
        by_cls[name] = (len(rows), d)
        for r in rows:
            if r["start"] is not None:
                years[min(2025, max(-3000, r["start"])) // 100 * 100] += 1
    print(f"{tot:,} rows, {dated:,} with a year ({100 * dated / max(1, tot):.0f}%)")
    for s, n in sorted(by_sys.items()):
        print(f"  {s}: {n:,}")
    print("\n  by class:")
    for name, (n, d) in sorted(by_cls.items(), key=lambda kv: -kv[1][0]):
        print(f"    {name:32s} {n:>7,} rows {d:>7,} dated")
    print("\n  start years by century:")
    for c, n in sorted(years.items()):
        print(f"    {c:>6d}s {n:>7,}")


def places(km=25.0):
    """What each test place would actually get, in its own year.

    The measure that matters for this step: not how many rows Wikidata has,
    but how many stand in a given place in a given year. Sydney in 1850 must
    answer 0 railways — Australia's first was 1854.
    """
    sys.path.insert(0, HERE)
    from fetch_town_wd import TEST_PLACES
    rows_by_sys = {}
    for f in sorted(os.listdir(RAW)):
        if not f.startswith("class_"):
            continue
        for r in json.load(open(os.path.join(RAW, f), encoding="utf-8")):
            if r["start"] is None:
                continue                      # estimated rows are not counted here
            rows_by_sys.setdefault(r["sys"], []).append(r)
    d = 111.32
    for name, lat, lon, year in TEST_PLACES:
        hits = {}
        for system, rows in rows_by_sys.items():
            n = 0
            for r in rows:
                if r["start"] > year:
                    continue
                if r["end"] is not None and r["end"] < year:
                    continue
                if abs(r["lat"] - lat) * d <= km and abs(r["lon"] - lon) * d * \
                        max(0.02, __import__("math").cos(__import__("math").radians(lat))) <= km:
                    n += 1
            hits[system] = n
        line = "  ".join(f"{s} {hits[s]}" for s in sorted(hits))
        print(f"  {name:12s} {year:>6d}  {line}", flush=True)


def main(argv):
    mode = argv[1] if len(argv) > 1 else "--report"
    {"--check": check, "--fetch": fetch, "--labels": labels_for,
     "--report": report, "--labels-sparql": labels_sparql,
     "--labels-any": labels_any, "--places": places}[mode]()


if __name__ == "__main__":
    main(sys.argv)
