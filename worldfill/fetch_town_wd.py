#!/usr/bin/env python3
# ============================================================
# Step 33 (B25 water, E14 materials, B9 styles): the fetch.
#
#   python3 fetch_town_wd.py --check         verify the water class QIDs
#   python3 fetch_town_wd.py --fetch         water and sanitation rows -> build/water/raw/
#   python3 fetch_town_wd.py --props         material (P186) and style (P149) for the buildings
#   python3 fetch_town_wd.py --labels        English labels for every QID we hold
#   python3 fetch_town_wd.py --report        the statistics and the test-place coverage
#
# Three things are fetched, and each is fetched because part 1's survey said it
# was there:
#
#  * WATER CLASSES (B25): wells, stepwells, cisterns, aqueducts, fountains,
#    bath houses, reservoirs, water towers. Every QID was read back from
#    Wikidata first (survey_water_wd.py --labels): 16 of the 25 candidates the
#    survey tried matched, and nine did not at all -- Q9070 is an airport in
#    Uruguay, not a sewer.
#  * MATERIAL AND STYLE (E14, B9): P186 (material used) and P149 (architectural
#    style) for the buildings step 32 fetched. Sparse but real: 8.5% carry a
#    material, 30% a style, and the styles are the regional, dated vocabulary
#    B9 needs (Gothic, Dravidian, Indo-Islamic, Safavid, Qajar, Brick Gothic).
#  * LABELS, into the one store step 32 built.
#
# The notability floor for water is 3 Wikipedias, not step 32's 5: water works
# are far less written about than monuments, and at 5 the stepwell class gives
# 2 rows and the qanat class none. The floor is written into the pack's source.
# ============================================================
import json
import os
import re
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
WRAW = os.path.join(HERE, "build", "water", "raw")
BRAW = os.path.join(HERE, "build", "buildings", "raw")
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

# --check compares a QID's English label with the Wikidata label it is expected
# to carry. For seven of the classes the name the mod shows is deliberately not
# that label -- "thermae" is displayed as Roman baths, "onsen" as hot spring
# bath, "sentō" as bath house, "water treatment" as water works -- because a
# player reads "Roman baths" and not "thermae". The Wikidata label is what gets
# verified; the display name is what goes in the pack.
WIKI_LABELS = {
    "Q43483": "water well",
    "Q221275": "sewage treatment",
    "Q655311": "onsen",
    "Q1046648": "sentō",
    "Q1058719": "water treatment",
    "Q6581615": "thermae",
    "Q93429857": "ancient Roman cistern",
}

MIN_SITELINKS = 3

# A real QID, and only a real QID: QLever and WDQS both hand back the odd
# hash where an entity should be, and a label cannot be asked for those.
QID = re.compile(r"^Q[0-9]+$")

# The water and sanitation classes. Labels verified by --check.
# Classes known to give no rows at this floor are kept, with a note: the zero
# is the finding (qanats are never items with three Wikipedias; nobody has
# written an article about an individual sewer).
CLASSES = {
    # ---- supply -----------------------------------------------------------
    "Q1473950": "stepwell",         # 6 rows at floor 3
    "Q43483": "well",               # water well
    "Q1371047": "holy well",
    "Q838858": "cistern",
    "Q93429857": "Roman cistern",
    "Q459297": "qanat",             # 0 rows: kept so the zero stays visible
    "Q474": "aqueduct",
    "Q131681": "reservoir",
    "Q2551525": "water reservoir",
    "Q483453": "fountain",
    "Q274153": "water tower",
    "Q354411": "standpipe",
    "Q2245442": "water pump",
    "Q837176": "shadoof",
    "Q756952": "noria",
    # ---- bathing and washing ----------------------------------------------
    "Q6581615": "Roman baths",
    "Q28077": "hammam",
    "Q1046648": "bath house",       # sento
    "Q655311": "hot spring bath",   # onsen
    "Q785952": "bathhouse",
    "Q2531616": "public bath",
    # ---- sanitation --------------------------------------------------------
    "Q5615741": "latrine",
    "Q204435": "cesspit",
    "Q221275": "sewage works",
    "Q1058719": "water works",
    "Q3951623": "drain",
}

# The world-wide test set (SYSTEMS_PLAN.md part 9), as step 32 uses it.
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
            t = time.time()
            try:
                r = requests.get(url, params={"query": body}, timeout=timeout,
                                 headers={"Accept": "application/sparql-results+json",
                                          "User-Agent": UA})
                if r.status_code in (429, 500, 502, 503, 504):
                    raise RuntimeError(f"{name}: HTTP {r.status_code}")
                r.raise_for_status()
                # strict=False: WDQS sometimes returns a raw newline inside a string literal.
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
    out = {}
    for i in range(0, len(qids), 150):   # at 600 QIDs the body comes back empty and silent
        values = " ".join("wd:" + q for q in qids[i:i + 150])
        rows, ep, dt = ask(f'SELECT ?x ?xLabel WHERE {{ VALUES ?x {{ {values} }} '
                           f'?x rdfs:label ?xLabel . FILTER(LANG(?xLabel) = "en") }}')
        for r in rows:
            out[r["x"]["value"].rsplit("/", 1)[-1]] = r["xLabel"]["value"]
        print(f"  {len(qids[i:i + 150])} QIDs from {ep} in {dt:.1f}s", flush=True)
    print("water classes, checked against Wikidata")
    bad = 0
    for q, shown in sorted(CLASSES.items(), key=lambda kv: int(kv[0][1:])):
        want = WIKI_LABELS.get(q, shown)
        real = out.get(q, "<none>")
        ok = real.lower() == want.lower()
        bad += 0 if ok else 1
        note = f"shown as {shown!r}" if shown != want else ""
        print(f"  {q:12s} {real:26s} {'ok' if ok else 'MISMATCH (expected %r)' % want}  {note}")
    print(f"  {len(CLASSES) - bad} of {len(CLASSES)} match")
    return out


def year(v):
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

UNDATED = """SELECT ?x ?coord ?k WHERE {
  ?x wdt:P31/wdt:P279* wd:%s ;
     wdt:P625 ?coord .
  FILTER NOT EXISTS { ?x wdt:P571 ?any }
  FILTER NOT EXISTS { ?x wdt:P1619 ?any2 }
  OPTIONAL { ?x wikibase:sitelinks ?k }
  FILTER(?k >= %d)
}"""


def fetch_water(undated=False):
    """Water and sanitation works with a point, and (for --fetch) a date."""
    os.makedirs(WRAW, exist_ok=True)
    for q, name in sorted(CLASSES.items(), key=lambda kv: int(kv[0][1:])):
        query = (UNDATED if undated else ROWS) % (q, MIN_SITELINKS)
        rows, ep, dt = ask(query)
        out = []
        for r in rows:
            pt = point(r.get("coord", {}).get("value"))
            if pt is None:
                continue
            start = year(r.get("d", {}).get("value")) or year(r.get("open", {}).get("value"))
            if not undated and start is None:
                continue
            out.append({
                "qid": r["x"]["value"].rsplit("/", 1)[-1],
                "lat": pt[0], "lon": pt[1],
                "start": start,
                "end": year(r.get("end", {}).get("value")),
                "sitelinks": int(r.get("k", {}).get("value", 0)),
                "dated_by": None if undated else ("inception" if r.get("d") else "opening"),
                "class": name,
            })
        tag = "undated_" if undated else "class_"
        json.dump(out, open(os.path.join(WRAW, f"{tag}{q}.json"), "w", encoding="utf-8"))
        print(f"  {name:16s} {len(out):6d} rows in {dt:.0f}s [{ep}]", flush=True)


def props():
    """Material (P186) and architectural style (P149) for the buildings step 32 fetched."""
    qids = set()
    for fn in os.listdir(BRAW):
        if fn.startswith("class_") or fn.startswith("undated_"):
            for r in json.load(open(os.path.join(BRAW, fn), encoding="utf-8")):
                if r.get("qid"):
                    qids.add(r["qid"])
    qids = sorted(qids, key=lambda q: int(q[1:]))
    print(f"  {len(qids):,} building QIDs", flush=True)
    props_path = os.path.join(BRAW, "props.json")
    out = json.load(open(props_path, encoding="utf-8")) if os.path.exists(props_path) else {}
    todo = [q for q in qids if q not in out]
    print(f"  {len(todo):,} still to ask", flush=True)
    t0 = time.time()
    for i in range(0, len(todo), 150):
        chunk = todo[i:i + 150]
        values = " ".join("wd:" + q for q in chunk)
        rows, ep, dt = ask(f'SELECT ?x ?mat ?sty WHERE {{ VALUES ?x {{ {values} }} '
                           f'OPTIONAL {{ ?x wdt:P186 ?mat }} OPTIONAL {{ ?x wdt:P149 ?sty }} }}')
        for q in chunk:
            out.setdefault(q, {"material": [], "style": []})
        for r in rows:
            q = r["x"]["value"].rsplit("/", 1)[-1]
            e = out.setdefault(q, {"material": [], "style": []})
            if "mat" in r:
                m = r["mat"]["value"].rsplit("/", 1)[-1]
                # One item in 42,721 comes back with a hash instead of a QID
                # (Q645062's material is 8a10c697b61c...). It names nothing, so
                # it is dropped rather than written into the pack.
                if QID.match(m) and m not in e["material"]:
                    e["material"].append(m)
            if "sty" in r:
                sty = r["sty"]["value"].rsplit("/", 1)[-1]
                if QID.match(sty) and sty not in e["style"]:
                    e["style"].append(sty)
        if (i // 150) % 20 == 0:
            json.dump(out, open(props_path, "w", encoding="utf-8"))
            print(f"    {i + len(chunk):,}/{len(todo):,} ({time.time() - t0:.0f}s)", flush=True)
    json.dump(out, open(props_path, "w", encoding="utf-8"))
    with_mat = sum(1 for v in out.values() if v["material"])
    with_sty = sum(1 for v in out.values() if v["style"])
    print(f"  props: {len(out):,} items, {with_mat:,} with a material, {with_sty:,} with a style"
          f"  ({time.time() - t0:.0f}s)", flush=True)


def labels():
    """English labels for every QID we hold: buildings, water works, materials and styles."""
    qids = set()
    for d, pats in ((BRAW, ("class_", "undated_")), (WRAW, ("class_", "undated_"))):
        if not os.path.exists(d):
            continue
        for fn in os.listdir(d):
            if fn.startswith(pats) and fn.endswith(".json"):
                for r in json.load(open(os.path.join(d, fn), encoding="utf-8")):
                    if r.get("qid"):
                        qids.add(r["qid"])
    pp = os.path.join(BRAW, "props.json")
    if os.path.exists(pp):
        for v in json.load(open(pp, encoding="utf-8")).values():
            qids.update(v.get("material", []))
            qids.update(v.get("style", []))
    qids = sorted((q for q in qids if QID.match(q)), key=lambda q: int(q[1:]))
    path = os.path.join(BRAW, "labels.json")
    out = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    todo = [q for q in qids if q not in out]
    print(f"  {len(qids):,} QIDs, {len(todo):,} without a label", flush=True)
    for i in range(0, len(todo), 400):
        chunk = todo[i:i + 400]
        values = " ".join("wd:" + q for q in chunk)
        rows, ep, dt = ask(f'SELECT ?x ?xLabel WHERE {{ VALUES ?x {{ {values} }} '
                           f'?x rdfs:label ?xLabel . FILTER(LANG(?xLabel) = "en") }}')
        for r in rows:
            out[r["x"]["value"].rsplit("/", 1)[-1]] = r["xLabel"]["value"]
        print(f"    {i + len(chunk):,}/{len(todo):,} ({dt:.0f}s)", flush=True)
        if (i // 400) % 10 == 0:
            json.dump(out, open(path, "w", encoding="utf-8"))
        time.sleep(1)
    json.dump(out, open(path, "w", encoding="utf-8"))
    print(f"  labels: {len(out):,}", flush=True)


def report():
    """What the water fetch gave, and what it covers."""
    labels_path = os.path.join(BRAW, "labels.json")
    lab = json.load(open(labels_path, encoding="utf-8")) if os.path.exists(labels_path) else {}
    total = {}
    rows_all = []
    for fn in sorted(os.listdir(WRAW)) if os.path.exists(WRAW) else []:
        if not fn.startswith("class_") or not fn.endswith(".json"):
            continue
        for r in json.load(open(os.path.join(WRAW, fn), encoding="utf-8")):
            rows_all.append(r)
            total[r["class"]] = total.get(r["class"], 0) + 1
    print(f"\nwater and sanitation works: {len(rows_all):,} rows (floor: {MIN_SITELINKS} Wikipedias)")
    for k, n in sorted(total.items(), key=lambda kv: -kv[1]):
        print(f"  {k:16s} {n:6d}")
    print("\nthe test places, 25 km, in their own year")
    for name, lat, lon, yr in TEST_PLACES:
        near = []
        for r in rows_all:
            if r["start"] is None or r["start"] > yr:
                continue
            if r["end"] is not None and r["end"] < yr:
                continue
            d = ((r["lat"] - lat) ** 2 + (r["lon"] - lon) ** 2) ** 0.5 * 111.0
            if d <= 25.0:
                near.append((r["sitelinks"], lab.get(r["qid"], r["qid"]), r["class"], r["start"]))
        near.sort(reverse=True)
        shown = ", ".join(f"{n} ({c}, from {s})" for _, n, c, s in near[:4])
        print(f"  {name:16s} {yr:>6d}  {len(near):3d}  {shown}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--check" in args:
        check()
    if "--fetch" in args:
        fetch_water(False)
    if "--fetch-undated" in args:
        fetch_water(True)
    if "--props" in args:
        props()
    if "--labels" in args:
        labels()
    if "--report" in args:
        report()
    if not any(a in args for a in ("--check", "--fetch", "--fetch-undated", "--props",
                                   "--labels", "--report")):
        print(__doc__)
