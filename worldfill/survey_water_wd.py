#!/usr/bin/env python3
# ============================================================
# Step 33 (B25 water, B9 houses): survey Wikidata for the
# classes of water supply, sanitation and traditional houses.
#
#   python3 survey_water_wd.py --labels    check the candidate QIDs
#   python3 survey_water_wd.py --count     how many dated, located, notable rows each gives
#
# Part 1 of step 33: before any class is used, its English label is read back
# from Wikidata (step 25's lesson: never trust a guessed QID). Then, and only
# then, the rows are counted with the same notability floor step 32 used
# (5 Wikipedias) and the same dates (inception P571, else opening P1619).
# ============================================================
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

MIN_SITELINKS = 5

# Candidates, by system. B25: water supply and sanitation. B9: the traditional
# house types of a region (a house is the fabric of an old town; instances are
# rarely notable, so this list is a survey, not a promise).
CANDIDATES = [
    # ---- B25: water supply -------------------------------------------------
    ("Q1473950", "stepwell", "B25"),
    ("Q474", "aqueduct", "B25"),
    ("Q838858", "cistern", "B25"),
    ("Q93429857", "ancient Roman cistern", "B25"),
    ("Q459297", "qanat", "B25"),
    ("Q43483", "water well", "B25"),
    ("Q131681", "reservoir", "B25"),
    ("Q2551525", "water reservoir", "B25"),
    ("Q483453", "fountain", "B25"),
    ("Q274153", "water tower", "B25"),
    # ---- B25: bathing and washing -----------------------------------------
    ("Q6581615", "thermae", "B25"),
    ("Q28077", "hammam", "B25"),
    ("Q1046648", "sentō", "B25"),
    ("Q655311", "onsen", "B25"),
    # ---- B25: sanitation ---------------------------------------------------
    ("Q9070", "sewer", "B25"),
    ("Q1320083", "sewerage", "B25"),
    ("Q181531", "latrine", "B25"),
    ("Q128865", "sanitation", "B25"),
    # ---- B9: traditional houses -------------------------------------------
    ("Q7882520", "haveli", "B9"),
    ("Q1062462", "siheyuan", "B9"),
    ("Q1142368", "hanok", "B9"),
    ("Q667471", "longhouse", "B9"),
    ("Q187796", "yurt", "B9"),
    ("Q187832", "igloo", "B9"),
    ("Q3947", "house", "B9"),
]


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
            except Exception as e:  # noqa: BLE001 - the next endpoint is tried
                print(f"      {e} ({time.time() - t:.0f}s)", flush=True)
                time.sleep(3)
        wait = 10 * (attempt + 1)
        print(f"      all endpoints failed; again in {wait} s", flush=True)
        time.sleep(wait)
    return [], "failed", 0.0


def labels():
    """Read every candidate QID's English label back and compare it."""
    qids = sorted({q for q, _, _ in CANDIDATES}, key=lambda q: int(q[1:]))
    # <=150 QIDs per VALUES chunk: at 600 the body comes back empty and silent.
    out = {}
    for i in range(0, len(qids), 150):
        chunk = qids[i:i + 150]
        values = " ".join("wd:" + q for q in chunk)
        rows, ep, dt = ask(f'SELECT ?x ?xLabel ?xDesc WHERE {{ VALUES ?x {{ {values} }} '
                           f'?x rdfs:label ?xLabel . FILTER(LANG(?xLabel) = "en") '
                           f'OPTIONAL {{ ?x schema:description ?xDesc . FILTER(LANG(?xDesc) = "en") }} }}')
        for r in rows:
            out[r["x"]["value"].rsplit("/", 1)[-1]] = (r["xLabel"]["value"], r.get("xDesc", {}).get("value", ""))
        print(f"  {len(chunk)} QIDs from {ep} in {dt:.1f}s", flush=True)
    print("\ncandidate QIDs, checked against Wikidata")
    bad = 0
    for q, want, system in CANDIDATES:
        real, desc = out.get(q, ("<no English label>", ""))
        ok = real.lower() == want.lower()
        bad += 0 if ok else 1
        print(f"  {system:4s} {q:12s} {real:28s} {'ok' if ok else 'MISMATCH (assumed %r)' % want}"
              f"   {desc[:60]}")
    print(f"  {len(CANDIDATES) - bad} of {len(CANDIDATES)} match")
    return out


COUNT = """SELECT ?x ?coord ?d ?open ?end ?k WHERE {
  ?x wdt:P31/wdt:P279* wd:%s ;
     wdt:P625 ?coord .
  OPTIONAL { ?x wdt:P571  ?d    }
  OPTIONAL { ?x wdt:P1619 ?open }
  OPTIONAL { ?x wdt:P576  ?end  }
  OPTIONAL { ?x wikibase:sitelinks ?k }
  FILTER(?k >= %d)
  FILTER(BOUND(?d) || BOUND(?open))
}"""


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


def count():
    print("\nrows with a point, a date and 5 or more Wikipedias")
    for q, want, system in CANDIDATES:
        rows, ep, dt = ask(COUNT % (q, MIN_SITELINKS))
        dated = 0
        samples = []
        for r in rows:
            d = year(r.get("d", {}).get("value")) or year(r.get("open", {}).get("value"))
            if d is None or point(r.get("coord", {}).get("value")) is None:
                continue
            dated += 1
            if len(samples) < 3:
                samples.append(f"{r['x']['value'].rsplit('/', 1)[-1]} {d}")
        print(f"  {system:4s} {q:12s} {want:24s} {len(rows):6d} rows, {dated:6d} dated and located"
              f"   [{ep} {dt:.1f}s]  e.g. {', '.join(samples)}", flush=True)


if __name__ == "__main__":
    if "--labels" in sys.argv:
        labels()
    if "--count" in sys.argv:
        count()
    if not any(a in sys.argv for a in ("--labels", "--count")):
        print(__doc__)
