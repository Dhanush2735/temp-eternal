#!/usr/bin/env python3
# ============================================================
# Step 34 part 5 (B14, B15, B18, B26): the works of the past.
#
#   python3 build_ways_works.py           build history/ways_works.json.gz
#   python3 build_ways_works.py --check   read it back and check it
#   python3 build_ways_works.py --places  what stands in each test place, in its own year
#
# The 122,080 rows fetched in part 2, turned into a pack the mod can ship.
# Part 1's first decision rules this file: **a row goes in with a year or it
# does not go in at all.** 82,304 rows carry a year in Wikidata; of the 39,776
# that do not, the ones whose kind has an arrival year in the technology atlas
# get that year and are marked as estimated — a railway station cannot predate
# the railway in its own country — and the rest are dropped, because a bridge
# with no date is the very thing that would put a motorway in Rome in AD 100.
#
# The pack is a list of works, each with a point, a kind, a first year, an end
# year where Wikidata has one, a name where Wikidata has an English one, and a
# mark saying whether the year is recorded or estimated.
# ============================================================
import gzip
import json
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modpack as M  # noqa: E402

RAW = os.path.join(HERE, "build", "ways", "raw")
ATLAS = os.path.join(M.HISTORY, "technology_atlas.json.gz")
OUT = os.path.join(M.HISTORY, "ways_works.json.gz")

# class qid -> (kind, the technology whose arrival in the country is the floor
# for an undated row; None means an undated row is dropped)
CLASSES = {
    "Q728937": ("line", "railway"), "Q55488": ("station", "railway"),
    "Q928830": ("station", "railway"), "Q2175765": ("station", "tram"),
    "Q1311958": ("line", "railway"), "Q420962": ("line", "railway"),
    "Q12280": ("bridge", None), "Q39715": ("lighthouse", None),
    "Q12284": ("canal", None), "Q44782": ("port", None), "Q283202": ("port", None),
    "Q12323": ("dam", None), "Q105731": ("canal", None), "Q1066997": ("canal", None),
    "Q828909": ("port", None), "Q811177": ("port", None),
    "Q1478783": ("port", None), "Q1359152": ("port", None),
    "Q83405": ("works", "steam_engine"), "Q159719": ("power", "electricity"),
    "Q15911738": ("power", "electricity"), "Q6558431": ("power", "electricity"),
    "Q12353044": ("works", "steam_engine"), "Q505213": ("mill", "steam_engine"),
    "Q2069494": ("works", "steam_engine"), "Q46398483": ("works", "steam_engine"),
    "Q256132": ("power", "telephone"), "Q1495738": ("works", "steam_engine"),
    "Q185187": ("mill", "watermill"), "Q38720": ("mill", "windmill"),
    "Q190928": ("works", "steam_engine"), "Q174814": ("power", "electricity"),
    "Q1248784": ("air", "air_travel"), "Q820477": ("mine", None),
    "Q186347": ("rest", None), "Q337912": ("way", None),
    "Q28532565": ("rest", "post"), "Q966002": ("rest", None),
    "Q194029": ("way", None), "Q11410923": ("way", None),
}

# The class files carry Wikidata country QIDs and the atlas indexes countries
# by ISO 3166-1 alpha-3, so P298 (alpha-3) is what is asked for — P297 would
# give two-letter codes that match nothing in the atlas.
ISO_CACHE = os.path.join(RAW, "iso.json")


def iso_codes(qids):
    """QID -> ISO 3166-1 alpha-3, from Wikidata's P298."""
    have = json.load(open(ISO_CACHE)) if os.path.exists(ISO_CACHE) else {}
    todo = sorted(q for q in qids if q and q not in have)
    for i in range(0, len(todo), 150):          # 150 at a time: the SPARQL limit
        chunk = todo[i:i + 150]
        values = " ".join("wd:" + q for q in chunk)
        import fetch_ways_wd as F
        rows, ep, dt = F.ask(
            f'SELECT ?x ?iso WHERE {{ VALUES ?x {{ {values} }} ?x wdt:P298 ?iso . }}')
        for r in rows:
            have[r["x"]["value"].rsplit("/", 1)[-1]] = r["iso"]["value"].upper()
    json.dump(have, open(ISO_CACHE, "w"))
    return have


def load_atlas():
    d = json.loads(gzip.open(ATLAS, "rt").read())
    countries = d["countries"]
    techs = {t["id"]: t for t in d["techs"]}
    return countries, techs


def build():
    labels = json.load(open(os.path.join(RAW, "labels.json"), encoding="utf-8"))
    other = {}
    p = os.path.join(RAW, "labels_other.json")
    if os.path.exists(p):
        other = json.load(open(p, encoding="utf-8"))

    rows = []
    for cls, (kind, tech) in CLASSES.items():
        path = os.path.join(RAW, f"class_{cls}.json")
        if not os.path.exists(path):
            continue
        for r in json.load(open(path, encoding="utf-8")):
            r["kind"], r["tech"] = kind, tech
            rows.append(r)
    print(f"{len(rows):,} rows fetched in part 2")

    countries, techs = load_atlas()
    iso = iso_codes({r.get("cc") for r in rows})
    cpos = {c: i for i, c in enumerate(countries)}

    kinds = sorted({k for k, _ in CLASSES.values()})
    kpos = {k: i for i, k in enumerate(kinds)}
    works, dated, est, dropped = [], 0, 0, 0
    for r in rows:
        start = r.get("start")
        flag = 0
        if start is None:
            tech = r["tech"]
            if not tech:
                dropped += 1
                continue
            code = iso.get(r.get("cc"))
            i = cpos.get(code) if code else None
            if i is None:
                dropped += 1
                continue
            arr = techs[tech]["arrive"]
            start = arr[i] if i < len(arr) else None
            if start is None:
                dropped += 1
                continue
            flag = 1
            est += 1
        else:
            dated += 1
        name = labels.get(r["q"])
        if name is None and r["q"] in other:
            name = other[r["q"]]["n"]
        end = r.get("end")
        if end is not None and end < start:
            # 7 rows in 110,447 say they were pulled down before they were
            # opened. The end year is the untrustworthy one, so it is dropped.
            end = None
        works.append([r["lat"], r["lon"], kpos[r["kind"]], start, end,
                      name or None, r.get("links", 0), flag])

    pack = {
        "format": "eternalengine/ways_works@1",
        "about": "the works of the past: railways and stations, bridges and canals, ports and "
                 "lighthouses, dams, factories and power stations, mills and shipyards, airports, "
                 "mines, caravanserais and pilgrim ways, each with the year it opened",
        "source": [
            {"name": "Wikidata (40 classes of structure and infrastructure with a map point, "
                     "3 or more Wikipedias, and an inception, opening or start year)",
             "url": "https://query.wikidata.org/", "licence": "CC0 1.0", "rows": dated},
            {"name": "the mod's own technology atlas, for the rows Wikidata gives no year: "
                     "the year the technology reached their country",
             "url": None, "licence": "MIT", "rows": est},
        ],
        "note": "flag 0: the year is recorded in Wikidata. flag 1: the year is estimated from "
                "the technology atlas — a railway station cannot predate the railway in its "
                "country. Rows with no year and no technology to estimate from are not in "
                "this pack.",
        "kinds": kinds,
        "works": works,
    }
    raw = json.dumps(pack, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(raw)
    print(f"ways_works.json.gz: {len(works):,} works ({dated:,} recorded, {est:,} estimated, "
          f"{dropped:,} rows dropped for having no year at all), "
          f"{len(kinds)} kinds, {len(raw):,} bytes raw, "
          f"{os.path.getsize(OUT):,} bytes gzipped")


def check():
    d = json.loads(gzip.open(OUT, "rt").read())
    assert d["format"].startswith("eternalengine/ways_works@")
    w = d["works"]
    bad = [x for x in w if not (-90 <= x[0] <= 90 and -180 <= x[1] <= 180)]
    end_before_start = [x for x in w if x[4] is not None and x[4] < x[3]]
    print(f"ways_works.json.gz: {len(w):,} works, {len(d['kinds'])} kinds, "
          f"{sum(1 for x in w if x[7] == 0):,} recorded, "
          f"{sum(1 for x in w if x[7] == 1):,} estimated, "
          f"{sum(1 for x in w if x[4]):,} with an end year, "
          f"{sum(1 for x in w if x[5]):,} named")
    print(f"  {len(bad)} with a bad point, {len(end_before_start)} ending before they start")
    c = Counter(d["kinds"][x[2]] for x in w)
    print("  by kind:", ", ".join(f"{k} {v:,}" for k, v in c.most_common()))
    c2 = Counter()
    for x in w:
        c2[min(2020, max(-2500, x[3])) // 100 * 100] += 1
    print("  first years by century:", ", ".join(f"{k}s {v:,}" for k, v in sorted(c2.items())))
    return 1 if bad or end_before_start else 0


def places():
    from math import cos, radians
    from fetch_town_wd import TEST_PLACES
    d = json.loads(gzip.open(OUT, "rt").read())
    w = d["works"]
    for name, lat, lon, year in TEST_PLACES:
        hits = Counter()
        for x in w:
            if x[3] > year or (x[4] is not None and x[4] < year):
                continue
            if abs(x[0] - lat) <= 0.25 and abs(x[1] - lon) <= 0.25 / max(0.2, cos(radians(lat))):
                hits[d["kinds"][x[2]]] += 1
        got = ", ".join(f"{k} {v}" for k, v in hits.most_common(6))
        print(f"  {name:12s} {year:>6d}  {got if got else 'nothing'}")


def main(argv):
    mode = argv[1] if len(argv) > 1 else ""
    if mode == "--check":
        sys.exit(check())
    elif mode == "--places":
        places()
    else:
        build()


if __name__ == "__main__":
    main(sys.argv)
