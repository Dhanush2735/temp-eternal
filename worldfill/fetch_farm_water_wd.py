#!/usr/bin/env python3
"""Step 35, part 4 (B17 farm and water works): fetch the field's water works from Wikidata.

Step 33's water pack brought wells, cisterns, stepwells and bath houses — everything inside a
town. B17 asks for what is outside it: the tanks and lakes of Telangana, the terraces, the canals,
and B2 needs the year of every dam, so that no reservoir appears before the dam that made it. This
is the fetch for those classes, at the same notability floor step 33 chose for water (3 Wikipedias),
against the same query, into the same raw directory, so build_water_works.py picks them up.

    python3 fetch_farm_water_wd.py                 the dated rows  -> build/water/raw/class_Q*.json
    python3 fetch_farm_water_wd.py --fetch-undated the rows with no year, for the gazetteer to date
    python3 fetch_farm_water_wd.py --check         read every QID's label back first

Classes that give nothing are kept, so the zero stays visible: Wikidata has no item for an
individual irrigation tank, no matter that there are a hundred thousand of them in South India,
and that is the finding as much as any row is.
"""
import json
import os
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "build", "water", "raw")

UA = "EternalEngineDataBuild/1.0 (history data; Eternal Engine Minecraft mod)"
PREFIXES = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""
ENDPOINTS = [
    ("wdqs", "https://query.wikidata.org/sparql", 240),
    ("qlever", "https://qlever.dev/api/wikidata", 600),
]
MIN_SITELINKS = 3          # step 33's floor for water works

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

# Field and water engineering. Every QID was read back from Wikidata first
# (survey_farm_water_wd.py --labels): 21 of 21 match their label.
CLASSES = {
    "Q12323": "dam",
    "Q12284": "canal",
    "Q2935978": "irrigation canal",
    "Q1066997": "weir",
    "Q106259": "polder",
    "Q105190": "levee",
    "Q185187": "watermill",
    "Q43742": "oasis",
    "Q1385463": "acequia",
    "Q2048319": "ditch",
    "Q838625": "terrace",
    "Q1052083": "check dam",
    "Q3515208": "irrigation tank",
    "Q750176": "chinampa",
    "Q177734": "artesian well",
    "Q4315": "subak",
    "Q842623": "paddy field",
    "Q96372097": "anicut",
    "Q25495": "Aflaj Irrigation System of Oman",
    "Q2695327": "polder windmill",
    "Q146728": "water wheel",
}

# Labels Wikidata gives these classes, where it differs from how the pack should name them.
WIKI_LABELS = {"Q4315": "Subak", "Q96372097": "Anicut",
               "Q25495": "Aflaj Irrigation System of Oman"}


def ask(query, retries=4):
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
                return json.loads(r.text, strict=False)["results"]["bindings"], name, time.time() - t
            except Exception as e:  # noqa: BLE001
                print(f"      {e} ({time.time() - t:.0f}s)", flush=True)
                time.sleep(3)
        wait = 10 * (attempt + 1)
        print(f"      all endpoints failed; again in {wait} s", flush=True)
        time.sleep(wait)
    return [], "failed", 0.0


def point(v):
    """'Point(12.5 41.9)' -> (41.9, 12.5)."""
    if not v:
        return None
    try:
        a, b = v[v.find("(") + 1:v.find(")")].split()
        return (float(b), float(a))
    except Exception:  # noqa: BLE001
        return None


def year(v):
    if not v:
        return None
    s = v.lstrip("+")
    neg = s.startswith("-")
    s = s.lstrip("-")
    y = int(s.split("-")[0]) if s[:4].isdigit() else None
    if y is None:
        return None
    return -y if neg else y


def check():
    qids = sorted(CLASSES, key=lambda q: int(q[1:]))
    values = " ".join("wd:" + q for q in qids)
    rows, ep, dt = ask(f'SELECT ?x ?xLabel WHERE {{ VALUES ?x {{ {values} }} '
                       f'?x rdfs:label ?xLabel . FILTER(LANG(?xLabel) = "en") }}')
    out = {r["x"]["value"].rsplit("/", 1)[-1]: r["xLabel"]["value"] for r in rows}
    print(f"  {len(qids)} QIDs from {ep} in {dt:.1f}s\nfarm and field water classes, checked")
    bad = 0
    for q in qids:
        want = WIKI_LABELS.get(q, CLASSES[q])
        real = out.get(q, "<none>")
        ok = real.lower() == want.lower()
        bad += 0 if ok else 1
        print(f"  {q:12s} {real:34s} {'ok' if ok else 'MISMATCH (expected %r)' % want}")
    print(f"  {len(CLASSES) - bad} of {len(CLASSES)} match")


def labels():
    """English labels for every water QID we hold, merged into the one store the pack reads.

    Step 33's own --labels collects from the buildings directory only, so the classes added here
    would arrive at build_water_works.py unnamed and be dropped. This asks for all of them.
    """
    path = os.path.join(HERE, "build", "buildings", "raw", "labels.json")
    out = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}
    qids = set()
    for fn in os.listdir(RAW):
        if fn.startswith("class_") or fn.startswith("undated_"):
            for r in json.load(open(os.path.join(RAW, fn), encoding="utf-8")):
                if r.get("qid"):
                    qids.add(r["qid"])
    todo = sorted((q for q in qids if q not in out), key=lambda q: int(q[1:]))
    print(f"  {len(qids):,} water QIDs on hand, {len(todo):,} without a label", flush=True)
    for i in range(0, len(todo), 150):
        chunk = todo[i:i + 150]
        values = " ".join("wd:" + q for q in chunk)
        rows, ep, dt = ask(f'SELECT ?x ?xLabel WHERE {{ VALUES ?x {{ {values} }} '
                           f'?x rdfs:label ?xLabel . FILTER(LANG(?xLabel) = "en") }}')
        for r in rows:
            out[r["x"]["value"].rsplit("/", 1)[-1]] = r["xLabel"]["value"]
        print(f"    {len(chunk):5d} asked in {dt:.0f}s [{ep}]", flush=True)
    json.dump(out, open(path, "w", encoding="utf-8"))
    print(f"  {len(out):,} labels now in the store")


def fetch(undated=False):
    os.makedirs(RAW, exist_ok=True)
    total = 0
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
        json.dump(out, open(os.path.join(RAW, f"{tag}{q}.json"), "w", encoding="utf-8"))
        total += len(out)
        print(f"  {name:32s} {len(out):6d} rows in {dt:.0f}s [{ep}]", flush=True)
    print(f"\n  {total:,} rows in all (floor: {MIN_SITELINKS} Wikipedias)")


if __name__ == "__main__":
    a = sys.argv[1:] or ["--help"]
    if "--check" in a:
        check()
    if "--fetch" in a:
        fetch(False)
    if "--fetch-undated" in a:
        fetch(True)
    if "--labels" in a:
        labels()
    if not any(x in a for x in ("--check", "--fetch", "--fetch-undated", "--labels")):
        print(__doc__)
