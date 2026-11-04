#!/usr/bin/env python3
# ============================================================
# Step 32 (B8, B16, B19): famous buildings, walls, forts and
# ruins by year — fetch from Wikidata.
#
#   python3 fetch_buildings_wd.py --check     verify the class QIDs
#   python3 fetch_buildings_wd.py --fetch     download the rows -> build/buildings/raw/
#   python3 fetch_buildings_wd.py --labels    English labels for the QIDs fetched
#   python3 fetch_buildings_wd.py --report    the statistics and the test-place coverage
#
# How it works, and why it looks like this:
#
#  * Every class QID is checked against its English label first (step 25's
#    lesson: never trust a guessed QID). The first draft of this file had 10
#    of 19 wrong, including "city gate" -> JavaScript and "temple" -> Ian Paice.
#  * Rows are fetched, not counted. A COUNT over `P31/P279*` takes minutes on
#    the public endpoint and times out; streaming the rows with a notability
#    filter takes seconds (2,088 castles in 3.5 s).
#  * The broad class Q41176 "building" times out even filtered, so it is not
#    fetched. B8's own list is all specific types (temples, forts, palaces,
#    mosques, churches, bridges, monuments), so the 18 specific classes carry
#    the step; the gap is recorded as a known limit.
#  * Dates: inception (P571) is the build year; where there is none, the date
#    of official opening (P1619) is used and the row is marked as dated by
#    opening. That fallback matters: 993 of 3,765 notable bridges (26%) have
#    no inception at all.
#  * End dates: dissolution/demolition (P576). This is what B19 (ruins) needs.
# ============================================================
import json
import os
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "build", "buildings", "raw")
LOGS = os.path.join(HERE, "logs")
UA = "EternalEngineDataBuild/1.0 (history data; Eternal Engine Minecraft mod)"

PREFIXES = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

ENDPOINTS = [
    ("wdqs", "https://query.wikidata.org/sparql", 240),
    ("qlever", "https://qlever.dev/api/wikidata", 600),
]

# The classes B8 (famous buildings), B16 (walls, gates, forts) and B19 (ruins)
# need. Every label verified against Wikidata by --check.
CLASSES = {
    "Q23413": "castle",
    "Q1785071": "fort",
    "Q57821": "fortification",
    "Q88291": "citadel",
    "Q82117": "city gate",
    "Q41229037": "city wall",
    "Q16970": "church building",
    "Q32815": "mosque",
    "Q44539": "temple",
    "Q44613": "monastery",
    "Q180987": "stupa",
    "Q381885": "tomb",
    "Q16560": "palace",
    "Q12280": "bridge",
    "Q12518": "tower",
    "Q4989906": "monument",
    "Q24354": "theatre building",
    "Q839954": "archaeological site",
    # ---- part 5 (B16, B19) -------------------------------------------------
    # "city wall" Q41229037 from part 1 returns 0 rows: it is a single wall
    # section in Schongau, not the class. The class is Q16748868 "city walls".
    # These seven labels were read back from Wikidata before being added.
    "Q16748868": "city walls",
    "Q57346": "defensive wall",
    "Q1416685": "rampart",
    "Q54831": "amphitheatre",
    "Q7362268": "Roman amphitheatre",
    "Q109607": "ruins",
    "Q17715832": "castle ruin",
}

# Notability floor: fewer than 5 Wikipedias is not "famous" for R1's purposes.
MIN_SITELINKS = 5

# The world-wide test set (SYSTEMS_PLAN.md part 9).
TEST_PLACES = [
    ("Ur", 30.9625, 46.1031, -2500), ("Giza", 29.9792, 31.1342, -2500),
    ("Mohenjo-daro", 27.3242, 68.1356, -2500), ("Anyang", 36.1000, 114.3500, -1200),
    ("Athens", 37.9715, 23.7257, -430), ("Pataliputra", 25.5940, 85.1370, -300),
    ("Rome", 41.8925, 12.4853, 100), ("Teotihuacan", 19.6925, -98.8438, 500),
    ("Chang'an", 34.2611, 108.9422, 750), ("Baghdad", 33.3152, 44.3661, 900),
    ("Greenland Norse", 61.1550, -45.5170, 1000), ("Cahokia", 38.6603, -90.0618, 1100),
    ("Angkor", 13.4125, 103.8670, 1150), ("Great Zimbabwe", -20.2675, 30.9339, 1300),
    ("Timbuktu", 16.7735, -3.0074, 1350), ("Tenochtitlan", 19.4326, -99.1332, 1500),
    ("Cusco", -13.5163, -71.9785, 1500), ("the Amazon", -3.4653, -62.2159, 1500),
    ("Vijayanagara", 15.3350, 76.4600, 1520), ("Delhi", 28.6562, 77.2410, 1650),
    ("Edo", 35.6852, 139.7528, 1700), ("London", 51.5074, -0.1278, 1700),
    ("Paris", 48.8566, 2.3522, 1789), ("Sydney", -33.8688, 151.2093, 1850),
    ("New York", 40.7128, -74.0060, 1920), ("Hyderabad", 17.3616, 78.4747, 1948),
    ("Lagos", 6.4541, 3.3947, 1960), ("Moscow", 55.7520, 37.6175, 1980),
    ("Sao Paulo", -23.5505, -46.6333, 2020), ("Yakutsk", 62.0355, 129.6755, 1900),
    ("the Sahara", 23.4162, 25.6628, 1000),
]


def ask(query, retries=4):
    """One query, tried on each endpoint in turn. Returns rows as a list of dicts."""
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
                # strict=False: WDQS sometimes returns a raw newline inside a
                # string literal, which the strict parser rejects outright and
                # the whole response is lost. Seen on the temple class.
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
        ok = real.lower() == CLASSES[q].lower()
        bad += 0 if ok else 1
        print(f"  {q:12s} {real:24s} {'ok' if ok else 'MISMATCH (assumed %r)' % CLASSES[q]}")
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


ROWS = """SELECT ?x ?coord ?d ?open ?end ?k WHERE {
  ?x wdt:P31/wdt:P279* wd:%s ;
     wdt:P625 ?coord .
  OPTIONAL { ?x wdt:P571  ?d    }
  OPTIONAL { ?x wdt:P1619 ?open }
  OPTIONAL { ?x wdt:P576  ?end  }
  OPTIONAL { ?x wikibase:sitelinks ?k }
  FILTER(?k >= %d)
  FILTER(BOUND(?d) || BOUND(?open))
}"""


def fetch():
    os.makedirs(RAW, exist_ok=True)
    for q, name in sorted(CLASSES.items(), key=lambda kv: int(kv[0][1:])):
        path = os.path.join(RAW, f"class_{q}.json")
        if os.path.exists(path) and os.path.getsize(path) > 50:
            n = len(json.load(open(path, encoding="utf-8")))
            print(f"  {name:22s} {n:>7,} rows (cached)", flush=True)
            continue
        rows, ep, dt = ask(ROWS % (q, MIN_SITELINKS))
        out = []
        for r in rows:
            ll = point(r["coord"]["value"])
            if not ll:
                continue
            d = year(r.get("d", {}).get("value"))
            op = year(r.get("open", {}).get("value"))
            end = year(r.get("end", {}).get("value"))
            start = d if d is not None else op
            if start is None:
                continue
            out.append({
                "qid": r["x"]["value"].rsplit("/", 1)[-1],
                "lat": ll[0], "lon": ll[1],
                "start": start, "end": end,
                "sitelinks": int(r["k"]["value"]),
                "dated_by": "inception" if d is not None else "opening",
                "class": name,
            })
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f)
        print(f"  {name:22s} {len(out):>7,} rows in {dt:.0f}s [{ep}]", flush=True)
        time.sleep(1)


# ---- part 2: the undated ones ----------------------------------------------
#
# Part 1 fetched only structures Wikidata can date (P571 inception or P1619
# opening). That filter is what left the ancient world empty: 9,839 of 11,656
# notable archaeological sites carry no date at all, and Mohenjo-daro, Great
# Zimbabwe, Hampi and Teotihuacan are among them.
#
# This is the same query with the date filter removed, keeping back only the
# rows Wikidata cannot date. Part 2 then dates them from the mod's own
# gazetteer, where they fall inside a curated site.
# Ordered and paged. Both are forced by the endpoint: an unpaged answer for a
# big class (temple, archaeological site) passes 60 s and the stream is cut
# mid-JSON, so the response is lost however it is parsed. 4,000 rows comes back
# in ~8 s and 1.7 MB. ORDER BY ?x keeps the pages disjoint.
ROWS_UNDATED = """SELECT ?x ?coord ?end ?k WHERE {
  ?x wdt:P31/wdt:P279* wd:%s ;
     wdt:P625 ?coord .
  OPTIONAL { ?x wdt:P571  ?inception }
  OPTIONAL { ?x wdt:P1619 ?opening  }
  OPTIONAL { ?x wdt:P576  ?end      }
  OPTIONAL { ?x wikibase:sitelinks ?k }
  FILTER(?k >= %d)
  FILTER(!BOUND(?inception) && !BOUND(?opening))
} ORDER BY ?x LIMIT 4000 OFFSET %d
"""

UNDATED_PAGE = 4000


def fetch_undated():
    """Fetch notable structures Wikidata gives no start date for."""
    os.makedirs(RAW, exist_ok=True)
    total = 0
    for q, name in sorted(CLASSES.items(), key=lambda kv: int(kv[0][1:])):
        path = os.path.join(RAW, f"undated_{q}.json")
        if os.path.exists(path) and os.path.getsize(path) > 50:
            n = len(json.load(open(path, encoding="utf-8")))
            print(f"  {name:22s} {n:>7,} rows (cached)", flush=True)
            total += n
            continue
        out = []
        t0 = time.time()
        pages = 0
        offset = 0
        while True:
            rows, ep, dt = ask(ROWS_UNDATED % (q, MIN_SITELINKS, offset))
            pages += 1
            if not rows:
                break
            for r in rows:
                ll = point(r["coord"]["value"])
                if not ll:
                    continue
                out.append({
                    "qid": r["x"]["value"].rsplit("/", 1)[-1],
                    "lat": ll[0], "lon": ll[1],
                    "end": year(r.get("end", {}).get("value")),
                    "sitelinks": int(r["k"]["value"]),
                    "class": name,
                })
            if len(rows) < UNDATED_PAGE:
                break
            offset += UNDATED_PAGE
            time.sleep(1)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f)
        total += len(out)
        print(f"  {name:22s} {len(out):>7,} rows in {time.time() - t0:.0f}s "
              f"({pages} page(s), {ep})", flush=True)
        time.sleep(1)
    print(f"  undated total (with duplicates across classes): {total:,}")


def labels_for():
    """English labels for every QID fetched, in chunks."""
    qids = set()
    for q in CLASSES:
        for pat in (f"class_{q}.json", f"undated_{q}.json"):
            p = os.path.join(RAW, pat)
            if os.path.exists(p):
                for r in json.load(open(p, encoding="utf-8")):
                    qids.add(r["qid"])
    qids = sorted(qids, key=lambda s: int(s[1:]))
    print(f"  {len(qids):,} QIDs need labels", flush=True)
    out = {}
    path = os.path.join(RAW, "labels.json")
    if os.path.exists(path):
        out = json.load(open(path, encoding="utf-8"))
    todo = [q for q in qids if q not in out]
    for i in range(0, len(todo), 400):
        chunk = todo[i:i + 400]
        values = " ".join("wd:" + q for q in chunk)
        rows, ep, dt = ask(
            f'SELECT ?x ?xLabel WHERE {{ VALUES ?x {{ {values} }} '
            f'?x rdfs:label ?xLabel . FILTER(LANG(?xLabel) = "en") }}')
        for r in rows:
            out[r["x"]["value"].rsplit("/", 1)[-1]] = r["xLabel"]["value"]
        print(f"    {i + len(chunk):,}/{len(todo):,} ({dt:.0f}s)", flush=True)
        if i % 2000 == 0:
            json.dump(out, open(path, "w", encoding="utf-8"))
        time.sleep(1)
    json.dump(out, open(path, "w", encoding="utf-8"))
    print(f"  labels: {len(out):,}", flush=True)


def report():
    os.makedirs(LOGS, exist_ok=True)
    rows = {}
    per_class = {}
    for q, name in CLASSES.items():
        p = os.path.join(RAW, f"class_{q}.json")
        if not os.path.exists(p):
            continue
        rs = json.load(open(p, encoding="utf-8"))
        per_class[name] = len(rs)
        for r in rs:
            k = r["qid"]
            if k in rows:
                rows[k]["classes"].append(name)
            else:
                rows[k] = dict(r, classes=[name])
    all_rows = list(rows.values())

    def century(y):
        return (y // 100) * 100 if y is not None else None

    stats = {
        "total": len(all_rows),
        "unique_qids": len(all_rows),
        "per_class_raw": per_class,
        "with_end_date": sum(1 for r in all_rows if r["end"] is not None),
        "dated_by_opening": sum(1 for r in all_rows if r["dated_by"] == "opening"),
        "before_1900": sum(1 for r in all_rows if r["start"] < 1900),
        "before_1500": sum(1 for r in all_rows if r["start"] < 1500),
        "before_1": sum(1 for r in all_rows if r["start"] < 1),
        "in_multiple_classes": sum(1 for r in all_rows if len(r["classes"]) > 1),
        "sitelinks_bands": {
            "5-9": sum(1 for r in all_rows if 5 <= r["sitelinks"] < 10),
            "10-49": sum(1 for r in all_rows if 10 <= r["sitelinks"] < 50),
            "50+": sum(1 for r in all_rows if r["sitelinks"] >= 50),
        },
    }

    # Coverage of the world-wide test set: is there a famous dated building
    # within 25 km of each test place, standing in that place's year?
    def km(a, b, c, d):
        from math import radians, sin, cos, asin, sqrt
        p1, p2 = radians(a), radians(c)
        dp, dl = radians(c - a), radians(d - b)
        h = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
        return 2 * 6371 * asin(min(1, sqrt(h)))

    cov = []
    for name, lat, lon, yr in TEST_PLACES:
        near = [r for r in all_rows if km(lat, lon, r["lat"], r["lon"]) <= 25]
        standing = [r for r in near if r["start"] <= yr and (r["end"] is None or yr < r["end"])]
        cov.append({"place": name, "year": yr, "within_25km": len(near),
                    "standing_in_year": len(standing),
                    "earliest": min((r["start"] for r in near), default=None)})
    stats["test_place_coverage"] = cov
    stats["places_with_something_standing"] = sum(1 for c in cov if c["standing_in_year"] > 0)

    with open(os.path.join(LOGS, "step32_fetch_report.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=1)

    print()
    print(f"  unique structures      {stats['total']:,}")
    print(f"  with an end date       {stats['with_end_date']:,}   (B19 ruins)")
    print(f"  dated by opening only  {stats['dated_by_opening']:,}")
    print(f"  starting before 1900   {stats['before_1900']:,}")
    print(f"  starting before 1500   {stats['before_1500']:,}")
    print(f"  starting before AD 1   {stats['before_1']:,}")
    print(f"  in more than one class {stats['in_multiple_classes']:,}")
    print(f"  sitelinks 5-9 / 10-49 / 50+   "
          f"{stats['sitelinks_bands']['5-9']:,} / "
          f"{stats['sitelinks_bands']['10-49']:,} / "
          f"{stats['sitelinks_bands']['50+']:,}")
    print()
    print(f"  test places with a famous building standing in the year: "
          f"{stats['places_with_something_standing']} of {len(cov)}")
    for c in cov:
        mark = "ok " if c["standing_in_year"] else "NONE"
        print(f"    {mark} {c['place']:18s} {c['year']:>6}  "
              f"within 25 km: {c['within_25km']:>4}   standing: {c['standing_in_year']:>4}")
    print()
    print("  written: logs/step32_fetch_report.json")


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ""
    if cmd == "--check":
        check()
    elif cmd == "--fetch":
        fetch()
    elif cmd == "--fetch-undated":
        fetch_undated()
    elif cmd == "--labels":
        labels_for()
    elif cmd == "--report":
        report()
    elif cmd == "--all":
        check()
        fetch()
        labels_for()
        report()
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
