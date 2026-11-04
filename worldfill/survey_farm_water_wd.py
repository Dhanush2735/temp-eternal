#!/usr/bin/env python3
"""Step 35, part 4 (B17 farm and water works): survey Wikidata for the classes of farm water works.

B17 asks for tanks, stepwells, terraces and canals; step 33's water pack brought the stepwells and
the cisterns but nothing of the field. This is the survey before the fetch: every candidate QID has
its English label read back from Wikidata first (step 25's lesson — never trust a guessed QID), and
then its rows are counted at two notability floors, because farm works are even less written about
than water works and step 33's floor of 3 may leave the tank class empty.

    python3 survey_farm_water_wd.py --labels    read the candidate QIDs back
    python3 survey_farm_water_wd.py --count     how many located rows each gives at floors 3 and 2
"""
import json
import sys
import time

import requests

UA = "EternalEngineDataBuild/1.0 (history data; Eternal Engine Minecraft mod)"

PREFIXES = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

ENDPOINTS = [
    ("wdqs", "https://query.wikidata.org/sparql", 240),
    ("qlever", "https://qlever.dev/api/wikidata", 600),
]

# Farm and field water works, and the fields themselves. Every QID was found by searching
# Wikidata's own labels, then checked again here.
CANDIDATES = [
    ("Q1052083", "check dam"),
    ("Q3515208", "irrigation tank"),
    ("Q2935978", "irrigation canal"),
    ("Q12284", "canal"),
    ("Q838625", "terrace"),
    ("Q1066997", "weir"),
    ("Q106259", "polder"),
    ("Q105190", "levee"),
    ("Q146728", "water wheel"),
    ("Q1385463", "acequia"),
    ("Q750176", "chinampa"),
    ("Q43742", "oasis"),
    ("Q177734", "artesian well"),
    ("Q4315", "subak"),
    ("Q842623", "paddy field"),
    ("Q185187", "watermill"),
    ("Q25495", "Aflaj Irrigation System of Oman"),
    ("Q96372097", "anicut"),
    ("Q12323", "dam"),
    ("Q2048319", "ditch"),
    ("Q2695327", "polder windmill"),
]

COUNT = """SELECT (COUNT(*) AS ?n) WHERE {
  ?x wdt:P31/wdt:P279* wd:%s ;
     wdt:P625 ?coord .
  OPTIONAL { ?x wikibase:sitelinks ?k }
  FILTER(?k >= %d)
}"""

COUNT_DATED = """SELECT (COUNT(*) AS ?n) WHERE {
  ?x wdt:P31/wdt:P279* wd:%s ;
     wdt:P625 ?coord .
  OPTIONAL { ?x wdt:P571  ?d    }
  OPTIONAL { ?x wdt:P1619 ?open }
  OPTIONAL { ?x wikibase:sitelinks ?k }
  FILTER(?k >= %d)
  FILTER(BOUND(?d) || BOUND(?open))
}"""


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


def labels():
    qids = sorted({q for q, _ in CANDIDATES}, key=lambda q: int(q[1:]))
    values = " ".join("wd:" + q for q in qids)
    rows, ep, dt = ask(f'SELECT ?x ?xLabel ?xDesc WHERE {{ VALUES ?x {{ {values} }} '
                       f'?x rdfs:label ?xLabel . FILTER(LANG(?xLabel) = "en") '
                       f'OPTIONAL {{ ?x schema:description ?xDesc . FILTER(LANG(?xDesc) = "en") }} }}')
    out = {}
    for r in rows:
        out[r["x"]["value"].rsplit("/", 1)[-1]] = (r["xLabel"]["value"],
                                                   r.get("xDesc", {}).get("value", ""))
    print(f"  {len(qids)} QIDs from {ep} in {dt:.1f}s\n")
    bad = 0
    for q, want in CANDIDATES:
        real, desc = out.get(q, ("<no English label>", ""))
        ok = real.lower() == want.lower()
        bad += 0 if ok else 1
        print(f"  {q:12s} {real:34s} {'ok' if ok else 'MISMATCH (expected %r)' % want}   {desc[:56]}")
    print(f"  {len(CANDIDATES) - bad} of {len(CANDIDATES)} match")


def count():
    print("%-34s %10s %10s %10s %10s" % ("class", "floor 3", "3 dated", "floor 2", "2 dated"))
    for q, want in CANDIDATES:
        cells = []
        for floor in (3, 2):
            for qy in (COUNT, COUNT_DATED):
                rows, ep, dt = ask(qy % (q, floor))
                n = int(rows[0]["n"]["value"]) if rows else -1
                cells.append(n)
        print("%-34s %10d %10d %10d %10d" % (want, cells[0], cells[1], cells[2], cells[3]), flush=True)


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else "--labels"
    if a == "--count":
        count()
    else:
        labels()
