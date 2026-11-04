#!/usr/bin/env python3
"""Finish survey §2: every Wikidata event class, dated + geocoded, by census era (3000 BC-AD 2026).

One query per class returns each item's earliest date (P580 start time or P585 point in time)
and whether it has coordinates (own P625, or the P625 of its P276 location). Counting is done
client-side so no COUNT/UNION query can time out. Also checks the class QIDs' English labels,
because the original survey used several wrong QIDs."""
import json, subprocess, time, urllib.parse, collections, sys, re, gzip
UA = "EternalEngineSurvey/2.0 (historical data survey; research use)"
ERAS = [(-3000, -1001, "3000-1001 BC"), (-1000, -1, "1000-1 BC"), (1, 999, "AD 1-999"),
        (1000, 1499, "1000-1499"), (1500, 1799, "1500-1799"), (1800, 2026, "1800-2026")]

def sparql(q, tries=5):
    url = "https://query.wikidata.org/sparql"
    for i in range(tries):
        r = subprocess.run(["curl", "-s", "-G", "--max-time", "300", "-A", UA, "-H", "Accept: application/sparql-results+json",
                            "--data-urlencode", "query=" + q, url], capture_output=True, text=True)  # GET: WDQS 429s POST from this client
        try:
            return json.loads(r.stdout)["results"]["bindings"]
        except Exception:
            print("   retry", i, r.stdout[:150].replace("\n", " "), file=sys.stderr); time.sleep(10 * (i + 1))
    raise RuntimeError("query failed")

def era(y):
    for lo, hi, n in ERAS:
        if lo <= y <= hi: return n
    return None

def wd_year(v):
    # xsd:dateTime from WDQS; BC years are astronomical (0 = 1 BC), convert to historical
    s = v.strip()
    neg = s.startswith("-")
    y = int(s.lstrip("-").split("-")[0])
    return -(y + 1) if neg else (y if y != 0 else -1)

res = {}
HIST = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/history"
have = {}
for fn in json.load(open(f"{HIST}/index.json"))["packs"]:
    for e in json.load(open(f"{HIST}/{fn}", encoding="utf-8")).get("events", []):
        if re.fullmatch(r"q\d+", str(e.get("id", ""))):
            have[e["id"].upper()] = e.get("kind")
print("QIDs already in the mod's packs:", len(have), dict(collections.Counter(have.values())), flush=True)
items_out = {}
# 1. labels of every class QID the survey used
qids = ["Q198", "Q124734", "Q178561", "Q188055", "Q131569", "Q131361", "Q4426883", "Q17000908", "Q3241045", "Q44512", "Q8065", "Q7944", "Q8068", "Q168247", "Q168983"]
rows = sparql("SELECT ?c ?l WHERE { VALUES ?c { %s } ?c rdfs:label ?l FILTER(LANG(?l)='en') }" % " ".join("wd:" + q for q in qids))
labels = {b["c"]["value"].rsplit("/", 1)[-1]: b["l"]["value"] for b in rows}
res["class_labels"] = labels
print("labels:", labels, flush=True)

# 2. per class: items with earliest date and coordinate availability
CLASSES = [
    ("battle", "?x wdt:P31 wd:Q178561 ."),
    ("siege", "?x wdt:P31 wd:Q188055 ."),
    ("war", "?x wdt:P31 wd:Q198 ."),
    ("survey's 'war' class Q124734", "?x wdt:P31 wd:Q124734 ."),
    ("treaty (by label, as survey)", "?x wdt:P31/rdfs:label \"treaty\"@en ."),
    ("epidemic (by label)", "?x wdt:P31/rdfs:label \"epidemic\"@en ."),
    ("pandemic (by label)", "?x wdt:P31/rdfs:label \"pandemic\"@en ."),
    ("disease outbreak Q3241045", "?x wdt:P31 wd:Q3241045 ."),
    ("earthquake Q7944", "?x wdt:P31 wd:Q7944 ."),
    ("flood Q8068", "?x wdt:P31 wd:Q8068 ."),
    ("famine Q168247", "?x wdt:P31 wd:Q168247 ."),
]
for name, pat in CLASSES:
    q = ("SELECT ?x (MIN(?d) AS ?date) (SAMPLE(?c1) AS ?own) (SAMPLE(?c2) AS ?via) WHERE { %s "
         "OPTIONAL { ?x wdt:P580|wdt:P585 ?d } OPTIONAL { ?x wdt:P625 ?c1 } "
         "OPTIONAL { ?x wdt:P276 ?p . ?p wdt:P625 ?c2 } } GROUP BY ?x" % pat)
    t0 = time.time(); b = sparql(q)
    c = collections.Counter(); by = collections.defaultdict(collections.Counter)
    rows_out = []
    for r in b:
        c["items"] += 1
        has_date = "date" in r and r["date"]["value"][:1] in "-0123456789"
        own, via = "own" in r, "via" in r
        if own: c["with_own_P625"] += 1
        if own or via: c["with_coord_or_P276_coord"] += 1
        if not has_date: continue
        c["dated"] += 1
        try: y = wd_year(r["date"]["value"])
        except Exception: continue
        e = era(y)
        if e is None: c["dated_outside_range"] += 1; continue
        c["dated_in_range"] += 1
        if own: c["dated_in_range_own_P625"] += 1; by["own_P625"][e] += 1
        if own or via:
            c["dated_in_range_geocoded"] += 1; by["geocoded"][e] += 1
            q = r["x"]["value"].rsplit("/", 1)[-1]
            rows_out.append([q, y, int(own)])
            if q in have:
                c["dated_in_range_geocoded_already_in_mod"] += 1
            else:
                c["dated_in_range_geocoded_NEW"] += 1; by["new"][e] += 1
                if own: c["NEW_with_own_P625"] += 1
    res[name] = {"counts": dict(c), "geocoded_by_era": {k: dict(v) for k, v in by.items()}}
    items_out[name] = rows_out
    print(f"{name:30} {dict(c)}  ({time.time()-t0:.0f}s)", flush=True)
    time.sleep(2)
res["mod_qids"] = {"total": len(have), "by_kind": dict(collections.Counter(have.values()))}
json.dump(res, open("wikidata_eras.json", "w"), indent=1)
json.dump(items_out, gzip.open("wikidata_items.json.gz", "wt"))
print("saved wikidata_eras.json")
