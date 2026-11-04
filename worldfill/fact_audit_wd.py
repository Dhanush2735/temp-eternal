#!/usr/bin/env python3
"""Fact audit, part 1: the Wikidata look-ups (through the QLever endpoint), cached for fact_audit.py.

Nothing in the mod is changed. Writes worldfill/fact_audit_wikidata.json.gz with:
  persons:  name -> [[qid, birth, birthPrecision, death, deathPrecision], ...]   (humans, by English label or alias)
  states:   name -> [[qid, inception, precision, dissolved, precision], ...]     (non-humans with P571/P576)
  qids:     qid  -> [label, inception, precision, dissolved, precision]
  capitals: [[countryQid, countryLabel, capitalLabel, lat, lon], ...]           (today's sovereign states)
Years are historical years (no year 0: Wikidata's astronomical -62 becomes -63, 63 BC).
Precision is Wikidata's: 9 year, 8 decade, 7 century, 6 millennium; 10/11 month/day.

Usage: python3 fact_audit_wd.py [persons|states|qids|capitals|all]
"""
import collections
import gzip
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HIST = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/history"
ETER = "/home/user/eternal/src/main/resources/data/eternalengine/eternal"
CACHE = "/home/user/worldfill/fact_audit_wikidata.json.gz"
ENDPOINT = "https://qlever.dev/api/wikidata"
UA = "EternalEngine-worldfill-fact-audit/1.0 (history data check; one query at a time)"

PREFIXES = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX psv: <http://www.wikidata.org/prop/statement/value/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
"""


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def qlever(query, tries=4):
    data = urllib.parse.urlencode({"query": PREFIXES + query, "action": "tsv_export"}).encode()
    for k in range(tries):
        try:
            req = urllib.request.Request(ENDPOINT, data=data, headers={"User-Agent": UA,
                                                                       "Accept": "text/tab-separated-values"})
            with urllib.request.urlopen(req, timeout=300) as r:
                text = r.read().decode("utf-8")
            lines = text.split("\n")
            rows = [ln.split("\t") for ln in lines[1:] if ln.strip()]
            time.sleep(1.5)                     # polite: one query at a time, with a pause
            return rows
        except Exception as e:                  # noqa: BLE001
            print(f"  query failed ({e}); retry {k + 1}", flush=True)
            time.sleep(10 * (k + 1))
    raise SystemExit("QLever does not answer; try again later")


def lit(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"@en'


def unlit(s):
    m = re.match(r'^"(.*)"(@\w+)?$', s)
    return m.group(1).replace('\\"', '"').replace("\\\\", "\\") if m else s


def qid(s):
    m = re.search(r"/(Q\d+)>", s)
    return m.group(1) if m else None


def wd_year(s):
    m = re.match(r'^"?(-?\d+)-', s or "")
    if not m:
        return None
    y = int(m.group(1))
    return y - 1 if y <= 0 else y


def num(s):
    m = re.match(r'^"?(\d+)', s or "")
    return int(m.group(1)) if m else None


# ------------------------------------------------------------------ names to look up

TITLE_PREFIX = re.compile(r"^(?:Sultan|King|Queen|Emperor|Empress|Prince|Princess|Shah|Maharaja|Maharana|Raja|Rajah|"
                          r"Sir|Saint|St\.|Pope|Tsar|Czar|Khan|Emir|Amir|Nawab|Duke|Count|Grand Duke|Pharaoh|"
                          r"Chief|Lord|Lady|Mir|Sheikh|Shaikh|Sayyid|Imam|Caliph|Negus|Ras|General|President)\s+")


def name_variants(name):
    """The name as written, and a few cleaner forms a Wikidata label might have."""
    out = []

    def add(x):
        x = re.sub(r"\s+", " ", x).strip(" ,;:-")
        if 2 < len(x) <= 120 and x not in out:
            out.append(x)

    add(name)
    a = re.sub(r'\s*["“”][^"“”]*["“”]', "", name)          # Louis XIV "the Great" -> Louis XIV
    add(a)
    b = re.sub(r"\s*\([^)]*\)", "", a)                     # strip (…)
    add(b)
    if "," in b:
        head, tail = b.split(",", 1)
        add(head)
        add(tail)
    c = TITLE_PREFIX.sub("", b)
    add(c)
    return out


def persons_wanted():
    pf = jload(f"{HIST}/polity_facts.json.gz")["polities"]
    names = set()
    for p in pf:
        for kind in ("head", "gov"):
            for r in p.get(kind, []):
                names.update(name_variants(r[0]))
    for v in jload(f"{ETER}/vips/foundation_vips.json"):
        names.update(name_variants(v["name"]))
    return sorted(names)


def map_names_and_qids():
    w = jload(f"{HIST}/world_rulers.json.gz")
    names, qids = set(), set()
    for p in w["polities"]:
        names.add(p[0])
        if len(p) > 1 and p[1]:
            qids.add(p[1])
    d = jload(f"{HIST}/deccan_rulers.json")
    for t in d["timelines"]:
        for s in t:
            names.add(s["name"])
            if s.get("wikidata"):
                qids.add(s["wikidata"])
    for p in jload(f"{HIST}/polity_facts.json.gz")["polities"]:
        qids.add(p["q"])
    names = {n for n in names if not n.startswith("(")}
    return sorted(names), sorted(qids)


# ------------------------------------------------------------------ the four look-ups

def fetch_persons(cache):
    want = persons_wanted()
    have = cache.setdefault("persons", {})
    todo = [n for n in want if n not in have]
    print(f"persons: {len(want)} names, {len(todo)} to fetch", flush=True)
    B = 800
    for i in range(0, len(todo), B):
        batch = todo[i:i + B]
        q = ("SELECT ?name ?p ?b ?bp ?d ?dp WHERE {\n VALUES ?name { " + " ".join(lit(n) for n in batch) + " }\n"
             " { ?p rdfs:label ?name } UNION { ?p skos:altLabel ?name }\n"
             " ?p wdt:P31 wd:Q5 .\n"
             " OPTIONAL { ?p p:P569/psv:P569 ?bn . ?bn wikibase:timeValue ?b ; wikibase:timePrecision ?bp }\n"
             " OPTIONAL { ?p p:P570/psv:P570 ?dn . ?dn wikibase:timeValue ?d ; wikibase:timePrecision ?dp }\n}")
        t0 = time.time()
        rows = qlever(q)
        got = collections.defaultdict(set)
        for r in rows:
            r = r + [""] * (6 - len(r))
            got[unlit(r[0])].add((qid(r[1]), wd_year(r[2]), num(r[3]), wd_year(r[4]), num(r[5])))
        for n in batch:
            have[n] = sorted(got.get(n, ()), key=lambda x: (x[0] or "", str(x)))
        print(f"  {i + len(batch)}/{len(todo)}: {len(rows)} rows in {time.time() - t0:.0f}s", flush=True)
        if (i // B) % 5 == 4:
            save(cache)


def fetch_states(cache):
    names, _ = map_names_and_qids()
    have = cache.setdefault("states", {})
    todo = [n for n in names if n not in have]
    print(f"states: {len(names)} names, {len(todo)} to fetch", flush=True)
    B = 400
    for i in range(0, len(todo), B):
        batch = todo[i:i + B]
        q = ("SELECT ?name ?s ?i ?ip ?e ?ep WHERE {\n VALUES ?name { " + " ".join(lit(n) for n in batch) + " }\n"
             " { ?s rdfs:label ?name } UNION { ?s skos:altLabel ?name }\n"
             " { ?s p:P571/psv:P571 ?in . ?in wikibase:timeValue ?i ; wikibase:timePrecision ?ip }\n"
             " UNION { ?s p:P576/psv:P576 ?en . ?en wikibase:timeValue ?e ; wikibase:timePrecision ?ep }\n"
             " FILTER NOT EXISTS { ?s wdt:P31 wd:Q5 }\n}")
        rows = qlever(q)
        got = collections.defaultdict(lambda: collections.defaultdict(lambda: [None, None, None, None]))
        for r in rows:
            r = r + [""] * (6 - len(r))
            g = got[unlit(r[0])][qid(r[1])]
            i_, ip, e_, ep = wd_year(r[2]), num(r[3]), wd_year(r[4]), num(r[5])
            if i_ is not None and (g[0] is None or (ip or 0) > (g[1] or 0)):
                g[0], g[1] = i_, ip
            if e_ is not None and (g[2] is None or (ep or 0) > (g[3] or 0)):
                g[2], g[3] = e_, ep
        for n in batch:
            have[n] = [[q_] + v for q_, v in sorted(got.get(n, {}).items())]
        print(f"  {i + len(batch)}/{len(todo)}: {len(rows)} rows", flush=True)


def fetch_qids(cache):
    _, qids = map_names_and_qids()
    have = cache.setdefault("qids", {})
    todo = [q for q in qids if q not in have]
    print(f"qids: {len(qids)}, {len(todo)} to fetch", flush=True)
    B = 500
    for i in range(0, len(todo), B):
        batch = todo[i:i + B]
        q = ("SELECT ?s ?label ?i ?ip ?e ?ep WHERE {\n VALUES ?s { " + " ".join("wd:" + x for x in batch) + " }\n"
             " OPTIONAL { ?s rdfs:label ?label . FILTER (LANG(?label) = \"en\") }\n"
             " OPTIONAL { ?s p:P571/psv:P571 ?in . ?in wikibase:timeValue ?i ; wikibase:timePrecision ?ip }\n"
             " OPTIONAL { ?s p:P576/psv:P576 ?en . ?en wikibase:timeValue ?e ; wikibase:timePrecision ?ep }\n}")
        rows = qlever(q)
        for r in rows:
            r = r + [""] * (6 - len(r))
            k = qid(r[0])
            g = have.setdefault(k, [None, None, None, None, None])
            if r[1] and not g[0]:
                g[0] = unlit(r[1])
            i_, ip, e_, ep = wd_year(r[2]), num(r[3]), wd_year(r[4]), num(r[5])
            if i_ is not None and (g[1] is None or (ip or 0) > (g[2] or 0)):
                g[1], g[2] = i_, ip
            if e_ is not None and (g[3] is None or (ep or 0) > (g[4] or 0)):
                g[3], g[4] = e_, ep
        for x in batch:
            have.setdefault(x, [None, None, None, None, None])
        print(f"  {i + len(batch)}/{len(todo)}: {len(rows)} rows", flush=True)


def fetch_capitals(cache):
    q = """SELECT ?c ?cl ?capl ?coord WHERE {
 ?c wdt:P31 wd:Q3624078 .
 FILTER NOT EXISTS { ?c wdt:P576 ?gone }
 ?c wdt:P36 ?cap .
 ?cap wdt:P625 ?coord .
 OPTIONAL { ?c rdfs:label ?cl . FILTER (LANG(?cl) = "en") }
 OPTIONAL { ?cap rdfs:label ?capl . FILTER (LANG(?capl) = "en") }
}"""
    out = []
    for r in qlever(q):
        r = r + [""] * (4 - len(r))
        m = re.search(r"(?i)point\(([-\d.e]+) ([-\d.e]+)\)", r[3])
        if m:
            out.append([qid(r[0]), unlit(r[1]), unlit(r[2]), float(m.group(2)), float(m.group(1))])
    cache["capitals"] = out
    print(f"capitals: {len(out)}", flush=True)


STATE_TOPS = ["Q1048835", "Q7275", "Q3024240", "Q1250464", "Q11514315", "Q164950", "Q6256", "Q28171280",
              "Q15642541", "Q1371849"]


def fetch_statelike(cache, qids):
    """Which of these items are states, polities, dynasties or historical periods (not bands or ships)."""
    have = cache.setdefault("statelike", {})
    todo = sorted(q for q in qids if q and q not in have)
    print(f"statelike: {len(todo)} to fetch", flush=True)
    B = 500
    tops = " ".join("wd:" + t for t in STATE_TOPS)
    for i in range(0, len(todo), B):
        batch = todo[i:i + B]
        q = ("SELECT DISTINCT ?s WHERE {\n VALUES ?s { " + " ".join("wd:" + x for x in batch) + " }\n"
             " VALUES ?top { " + tops + " }\n ?s wdt:P31/wdt:P279* ?top .\n}")
        yes = {qid(r[0]) for r in qlever(q)}
        for x in batch:
            have[x] = x in yes
        print(f"  {i + len(batch)}/{len(todo)}: {len(yes)} state-like", flush=True)


def fetch_roles(cache, qids):
    """Occupations, and whether Wikidata records a position held (P39) or a noble title (P97)."""
    have = cache.setdefault("roles", {})
    todo = sorted(q for q in qids if q and q not in have)
    print(f"roles: {len(todo)} to fetch", flush=True)
    B = 400
    for i in range(0, len(todo), B):
        batch = todo[i:i + B]
        vals = " ".join("wd:" + x for x in batch)
        q1 = ("SELECT ?s ?ol WHERE {\n VALUES ?s { " + vals + " }\n ?s wdt:P106 ?o .\n"
              " ?o rdfs:label ?ol . FILTER (LANG(?ol) = \"en\")\n}")
        q2 = ("SELECT DISTINCT ?s WHERE {\n VALUES ?s { " + vals + " }\n { ?s wdt:P39 ?x } UNION { ?s wdt:P97 ?y }\n}")
        occ = collections.defaultdict(set)
        for r in qlever(q1):
            if len(r) >= 2:
                occ[qid(r[0])].add(unlit(r[1]))
        held = {qid(r[0]) for r in qlever(q2)}
        for x in batch:
            have[x] = [sorted(occ.get(x, ())), x in held]
        print(f"  {i + len(batch)}/{len(todo)}", flush=True)


def load_cache():
    return jload(CACHE) if os.path.exists(CACHE) else {}


def save(cache):
    tmp = CACHE + ".tmp"
    with open(tmp, "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as f:
        json.dump(cache, f, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, CACHE)


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    cache = load_cache()
    cache["source"] = ("Wikidata through the QLever endpoint (qlever.dev/api/wikidata), fetched "
                       + time.strftime("%Y-%m-%d") + "; CC0. worldfill/fact_audit_wd.py")
    for name, fn in (("qids", fetch_qids), ("states", fetch_states), ("capitals", fetch_capitals),
                     ("persons", fetch_persons)):
        if what in (name, "all"):
            fn(cache)
            save(cache)
    print("saved", CACHE, os.path.getsize(CACHE), "bytes")


if __name__ == "__main__":
    main()
