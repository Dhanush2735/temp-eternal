import io
#!/usr/bin/env python3
"""Step 8.4: famous people only where a land has none (history/famous_people.json.gz).

A gap is a state and a 25-year period: the state rules populated land on the map, but no famous
person of that state is alive then. The people come from Wikidata (CC0; secondary source; the step-7
source, the Sciences Po database, now sits behind an anti-bot wall and the Wikidata Query Service
allows one query a minute): one export from the QLever Wikidata endpoint (qlever.dev) of every human
born before 1960 with an English Wikipedia article, a birth year and a birthplace with coordinates
(~843,000). For each gap, up to 3 people alive then and born where the map puts that state in their
active years are added, the best-known first (most Wikipedia language editions). Rows are like the
other exact-birthplace rows: [name, description, birth, death, state, lat, lon, 25].

Usage: python3 fill_famous_gaps.py
Writes worldfill/famous_gaps_report.json.
"""
import collections, gzip, json, math, os, re, sys, time, urllib.parse, urllib.request

import numpy as np

sys.path.insert(0, "/home/user/worldfill")
sys.path.insert(0, "/home/user/harvest")
import modpack as M  # noqa: E402
import build_regional as BR  # noqa: E402
import build_polity_facts as PF  # noqa: E402
from build_notable_people import active_year, key  # noqa: E402

PEOPLE = f"{M.HISTORY}/famous_people.json.gz"
REPORT = "/home/user/worldfill/famous_gaps_report.json"
UA = "EternalEngineWorldFill/1.0 (historical data build; research use)"
BIN = 25
PER_GAP = 3
Q = """SELECT ?p ?pLabel ?pDescription ?b ?d ?loc ?sl WHERE {
  SERVICE wikibase:around { ?place wdt:P625 ?loc . bd:serviceParam wikibase:center "Point(%LON% %LAT%)"^^geo:wktLiteral .
                            bd:serviceParam wikibase:radius "%KM%" . }
  ?p wdt:P19 ?place ; wdt:P31 wd:Q5 ; wdt:P569 ?b ; wikibase:sitelinks ?sl .
  FILTER(YEAR(?b) >= %B0% && YEAR(?b) <= %B1%)
  ?art schema:about ?p ; schema:isPartOf <https://en.wikipedia.org/> .
  OPTIONAL { ?p wdt:P570 ?d . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
} ORDER BY DESC(?sl) LIMIT 12"""


def year_of(v):
    m = re.match(r"^(-?)(\d{1,4})-", v or "")
    if not m:
        return None
    y = int(m.group(2))
    return -y if m.group(1) else y


def sparql(q):
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": q, "format": "json"})
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
            with urllib.request.urlopen(req, timeout=75) as r:
                return json.load(r)["results"]["bindings"]
        except Exception as e:      # timeouts and 429s: wait and retry
            time.sleep(10 * (attempt + 1))
            err = e
    print("query failed:", err, flush=True)
    return []


SRC = os.path.expanduser("~/.cache/srcdata/qlever_people.tsv.gz")


def load_people():
    seen, out = set(), []
    with gzip.open(SRC, "rt", encoding="utf-8") as f:
        next(f)
        for line in f:
            c = line.rstrip("\n").split("\t")
            if len(c) < 7 or c[0] in seen:
                continue
            m = re.match(r"POINT\(([-\d.]+) ([-\d.]+)\)", c[3])
            if not m or not c[1].lstrip("-").isdigit():
                continue
            seen.add(c[0])
            name = re.sub(r'^"|"@en$', "", c[5])
            desc = re.sub(r'^"|"@en$', "", c[6]) if c[6] else ""
            desc = re.sub(r"\s*\([^()]*\d{3,4}[^()]*\)\s*$", "", desc)[:80]
            out.append((name, desc, int(c[1]), int(c[2]) if c[2].lstrip("-").isdigit() else None,
                        float(m.group(2)), float(m.group(1)), int(c[4]) if c[4].isdigit() else 0))
    return out


def main():
    t0 = time.time()
    hyde, reg = BR.Hyde(), PF.Register()
    doc = json.load(gzip.open(PEOPLE, "rt", encoding="utf-8"))
    rows = doc["people"]
    alive = collections.defaultdict(set)              # state -> bins with someone alive
    have = set()

    def bins_of(b, d):
        a0 = b + 20 if b is not None else d - 40
        a1 = d if d is not None else b + 70
        return range(a0 // BIN * BIN, a1 + 1, BIN)
    for r in rows:
        if r[2] is not None:
            have.add((key(r[0]), r[2]))
        if r[4] and (r[2] is not None or r[3] is not None):
            for b in bins_of(r[2], r[3]):
                alive[r[4]].add(b)
    cells = np.nonzero(hyde.cell >= 0)[0]
    lat = -90 + 0.25 + (cells // 720) * 0.5
    lon = -180 + 0.25 + (cells % 720) * 0.5
    gaps = {}                     # (state, bin) -> people share
    for y in range(-1000, 2001, BIN):
        ppl = hyde.people(lat, lon, y + BIN // 2)
        tot = float(ppl.sum())
        acc = collections.Counter()
        names = {}
        for i in np.nonzero(ppl > 0)[0]:
            pol = reg.at(float(lat[i]), float(lon[i]), y + BIN // 2)
            if pol and pol[1] and y not in alive.get(pol[1], ()):
                acc[pol[1]] += float(ppl[i])
                names[pol[1]] = pol[0]
        for q, w in acc.items():
            gaps[(q, y)] = (w / tot, names[q])
    st = collections.Counter(gaps_found=len(gaps))
    print(f"{len(gaps)} gaps, {round(time.time() - t0)} s", flush=True)
    cands = collections.defaultdict(list)            # (state, bin) -> [(sitelinks, person)]
    people = load_people()
    st["wikidata_people"] = len(people)
    for name, desc, b, d, la, lo, sl in people:
        if (key(name), b) in have or re.match(r"^Q\d+$", name) or b < -1100:
            continue
        pol = reg.at(la, lo, active_year(b, d))
        if not pol or not pol[1]:
            continue
        for bb in bins_of(b, d):
            if (pol[1], bb) in gaps:
                cands[(pol[1], bb)].append((sl, name, desc, b, d, la, lo))
    print(f"candidates for {len(cands)} gaps, {round(time.time() - t0)} s", flush=True)
    added, picked = [], collections.Counter()
    for (q, bb), (share, sname) in sorted(gaps.items(), key=lambda x: -x[1][0]):
        if bb in alive.get(q, ()):
            st["already_filled"] += 1
            continue
        got = 0
        for sl, name, desc, b, d, la, lo in sorted(cands.get((q, bb), []), key=lambda c: -c[0]):
            if (key(name), b) in have:
                continue
            added.append([name, desc, b, d, q, round(la, 3), round(lo, 3), 25])
            have.add((key(name), b))
            for x in bins_of(b, d):
                alive[q].add(x)
            got += 1
            picked[sname] += 1
            if got >= PER_GAP:
                break
        st["gaps_filled" if got else "gaps_no_person_found"] += 1
    rows += added
    rows.sort(key=lambda r: (r[3] if r[3] is not None else (r[2] or 0) + 60, r[0]))
    if "fill_famous_gaps" not in doc["source"]:
        doc["source"] += ("; plus people from Wikidata (CC0, via the QLever endpoint) for lands with no famous person in a "
                          "period, each with an English Wikipedia article and a birthplace in that land, worldfill/fill_famous_gaps.py")
    with open(PEOPLE + ".tmp", "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as fh:
        json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
    json.load(gzip.open(PEOPLE + ".tmp", "rt", encoding="utf-8"))
    os.replace(PEOPLE + ".tmp", PEOPLE)
    era = collections.Counter(r[2] // 100 * 100 for r in added)
    rep = {**dict(st), "people_added": len(added), "total_people": len(rows), "seconds": round(time.time() - t0),
           "bytes": os.path.getsize(PEOPLE), "added_by_century": {str(k): v for k, v in sorted(era.items())},
           "top_states": picked.most_common(30),
           "examples": [f"{r[0]} | {r[1]} | {r[2]}-{r[3]}" for r in added[:: max(1, len(added) // 15)]][:15]}
    json.dump(rep, open(REPORT, "w"), ensure_ascii=False, indent=1)
    print(json.dumps(rep, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
