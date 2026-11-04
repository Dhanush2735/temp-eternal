#!/usr/bin/env python3
# ============================================================
# Step 33, part 3 (B25): build water_works.json.gz.
#
#   python3 build_water_works.py            build the pack and report
#   python3 build_water_works.py --check    the rows a reader would ask for
#
# Water supply, bathing and sanitation by year: wells, stepwells, cisterns,
# aqueducts, fountains, reservoirs, water towers, bath houses and the few
# sanitation works Wikidata has. Fetched by fetch_town_wd.py at a notability
# floor of 3 Wikipedias -- step 32's floor of 5 leaves the stepwell class with
# 2 rows and the qanat class with none, because water works are far less
# written about than monuments.
#
# The shape is step 32's, deliberately: one row per work, a point, the year it
# was made, the year it ended, how famous it is, and a kind taken from the
# *narrowest* Wikidata class it belongs to (fewest members worldwide), because
# the broad ones misdescribe -- a hammam is also a bathhouse is also a building.
# A work Wikidata cannot date takes the mod's own gazetteer's window for the
# site it stands on, and is marked gazetteer.
#
# Written to the mod's own history folder, in the columnar shape the other
# registers use (lat and lon as thousandths of a degree).
# ============================================================
import gzip
import io
import json
import os
import sys
from collections import Counter
from math import radians, sin, cos, asin, sqrt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fetch_town_wd import TEST_PLACES  # noqa: E402

RAW = os.path.join(HERE, "build", "water", "raw")
LOGS = os.path.join(HERE, "logs")
HISTORY = os.path.join(HERE, "..", "eternal", "src", "main", "resources",
                       "data", "eternalengine", "eternal", "history")
OUT = os.path.join(HISTORY, "water_works.json.gz")

# What a work is for. Step 33 had three groups -- supply, bathing, sanitation --
# because that was what it fetched; part 4 of step 35 adds the field, and with it
# the works that carry water, hold it back, or put it to work. Aqueducts move to
# conveyance, where they belong: they carry water to a town, they are not the town's
# own supply. The register reads this through the pack's "groups" dictionary.
GROUPS = {
    # drawing water up out of the ground
    "well": "supply", "holy well": "supply", "artesian well": "supply",
    "water pump": "supply", "standpipe": "supply", "shadoof": "supply", "noria": "supply",
    # holding it
    "cistern": "storage", "Roman cistern": "storage", "reservoir": "storage",
    "water reservoir": "storage", "water tower": "storage", "dam": "storage",
    "check dam": "storage", "anicut": "storage",
    # carrying it
    "aqueduct": "conveyance", "qanat": "conveyance", "canal": "conveyance",
    "irrigation canal": "conveyance", "acequia": "conveyance", "ditch": "conveyance",
    # turning it aside
    "weir": "diversion",
    # putting it on the land
    "terrace": "field", "paddy field": "field", "chinampa": "field", "subak": "field",
    "irrigation tank": "field",
    # putting it to work
    "watermill": "power", "water wheel": "power", "polder windmill": "power",
    # keeping it off the land
    "polder": "defence", "levee": "defence",
    # where it comes out of the ground by itself
    "oasis": "source",
    # the rest, as step 33 had them
    "water works": "supply",
    "Roman baths": "bathing", "hammam": "bathing", "bath house": "bathing",
    "hot spring bath": "bathing", "bathhouse": "bathing", "public bath": "bathing",
    "fountain": "fountain",
    "latrine": "sanitation", "cesspit": "sanitation", "sewage works": "sanitation",
    "drain": "sanitation",
}

GROUP_ORDER = ["supply", "storage", "conveyance", "diversion", "field", "power",
               "defence", "source", "bathing", "fountain", "sanitation"]

# The world begins in 3000 BCE. A work the gazetteer dates earlier than that was
# already standing when the world did, so its year is the world's first, not a
# year the world cannot reach.
WORLD_START = -3000


def km(lat1, lon1, lat2, lon2):
    p1, p2 = radians(lat1), radians(lat2)
    dp, dl = radians(lat2 - lat1), radians(lon2 - lon1)
    h = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return 2 * 6371 * asin(min(1, sqrt(h)))


def main():
    labels_path = os.path.join(HERE, "build", "buildings", "raw", "labels.json")
    labels = json.load(open(labels_path, encoding="utf-8")) if os.path.exists(labels_path) else {}
    print(f"  {len(labels):,} labels on hand")

    class_size = Counter()
    works = {}
    for f in sorted(os.listdir(RAW)):
        if not (f.startswith("class_") or f.startswith("undated_")) or not f.endswith(".json"):
            continue
        for r in json.load(open(os.path.join(RAW, f), encoding="utf-8")):
            q = r["qid"]
            class_size[r["class"]] += 1
            if q in works:
                if r["class"] not in works[q]["classes"]:
                    works[q]["classes"].append(r["class"])
            else:
                works[q] = {"qid": q, "lat": r["lat"], "lon": r["lon"],
                            "start": r["start"], "end": r["end"],
                            "sitelinks": r["sitelinks"],
                            "dated_by": r["dated_by"], "classes": [r["class"]]}
    print(f"  {len(works):,} works fetched from Wikidata "
          f"({sum(1 for w in works.values() if w['start'] is not None):,} of them dated)")

    # ---- what the gazetteer dates -----------------------------------------
    gz_path = os.path.join(RAW, "gazetteer_dated.json")
    gz = json.load(open(gz_path, encoding="utf-8")) if os.path.exists(gz_path) else []
    if gz:
        print(f"  {len(gz):,} works dated from the gazetteer (estimated)")

    def kind_of(classes):
        """The narrowest class it belongs to: fewest members worldwide."""
        cands = [c for c in classes if c in GROUPS]
        if not cands:
            return "water works"
        return min(cands, key=lambda c: (class_size.get(c, 1 << 30), c))

    rows = []
    no_label = 0
    for w in works.values():
        if w["start"] is None:
            continue                       # dated by the gazetteer, below
        name = labels.get(w["qid"])
        if not name:
            no_label += 1
            continue
        rows.append([w["qid"], name, round(w["lat"] * 1000), round(w["lon"] * 1000),
                     kind_of(w["classes"]), w["start"], w["end"], w["sitelinks"],
                     "inception" if w["dated_by"] == "inception" else "opening"])

    for r in gz:
        if r["qid"] in works and works[r["qid"]]["start"] is not None:
            continue                       # a recorded date always wins
        name = r.get("label")
        if not name:
            no_label += 1
            continue
        rows.append([r["qid"], name, round(r["lat"] * 1000), round(r["lon"] * 1000),
                     kind_of(r["classes"]), r["start"], r["end"], r.get("sitelinks", 0),
                     "gazetteer"])

    # ---- repair ends that are not after their start ------------------------
    repaired = 0
    for r in rows:
        if r[6] is not None and r[6] <= r[5]:
            r[6] = None
            repaired += 1
    if repaired:
        print(f"\n  {repaired} end dates dropped: not after the start year, so the "
              f"work could never have stood")

    # ---- a year before the world begins is clamped to its first year --------
    clamped = 0
    for r in rows:
        if r[5] < WORLD_START:
            r[5] = WORLD_START
            clamped += 1
    if clamped:
        print(f"  {clamped} start years before {WORLD_START} clamped to it: the work was "
              f"already standing when the world began")

    rows.sort(key=lambda r: -r[7])         # best known first

    # The qid is dropped here, not earlier: the report below counts by kind and
    # the settlement filter of step 32 does the same, and both are easier to
    # read while the id is still in the row. What ships is what the note says.
    works = [r[1:] for r in rows]

    pack = {
        "format": 1,
        "id": "water_works",
        "source": ("Wikidata (CC0), fetched 2026-10-16: wells, stepwells, cisterns, qanats, "
                   "aqueducts, fountains, reservoirs, water towers, bath houses, hammams and "
                   "the few sanitation works that are written about; then, in step 35 part 4, "
                   "the dams, canals, irrigation canals, weirs, polders, levees, watermills, "
                   "oases, acequias, terraces and ditches of the field (B17, and B2's rule "
                   "that no reservoir stands before the dam that made it). Each has a map "
                   "point, 3 or more Wikipedias and a build year (inception, else date of "
                   "official opening). The floor is 3 and not step 32's 5 because water works "
                   "are far less written about than monuments: at 5 the stepwell class gives "
                   "2 rows and the qanat class none. Where Wikidata has no date at all, the "
                   "year is the mod's own gazetteer's occupation window for the site the work "
                   "stands on, and is marked estimated -- but only for a work that is itself "
                   "the place, so the field's works take no window at all."),
        "note": ("One row: [name, lat*1000, lon*1000, kind, from, to, sitelinks, source]. "
                 "source is inception, opening or gazetteer (estimated). to is null where "
                 "the end is unknown. Kinds are taken from the narrowest Wikidata class, so "
                 "a hammam is a hammam and not a bathhouse, and a mere canal is a canal "
                 "while one Wikidata calls an irrigation canal says so. groups maps every "
                 "kind to what the work is for. Sanitation is nearly absent: Wikidata has "
                 "articles about sewers, not about individual ones. A work no source could "
                 "date is not here at all -- step 35 part 4 tried the gazetteer on the "
                 "field's works and took it back, because a canal two kilometres from an "
                 "abandoned site is usually not of it (Dujiangyan, built in 256 BCE, was "
                 "being given a Sui county seat's window of 568 CE)."),
        "groups": GROUPS,
        "count": len(works),
        "works": works,
    }
    with open(OUT, "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as fh:
        json.dump(pack, fh, ensure_ascii=False, separators=(",", ":"))

    size = os.path.getsize(OUT)
    print(f"\n  {len(rows):,} works -> {OUT.split('/')[-1]} ({size / 1000:.0f} kB)")
    if no_label:
        print(f"  {no_label} dropped: no English label")

    kinds = Counter(r[4] for r in rows)
    kinds_count = dict(kinds)
    srcs = Counter(r[8] for r in rows)
    print("\n  kind")
    for k, v in kinds.most_common():
        print(f"    {k:16s} {v:>6,}   {GROUPS.get(k, '?')}")
    print("  where the year came from")
    for k, v in srcs.most_common():
        print(f"    {k:16s} {v:>6,}")
    print("\n  what the works are for")
    for g in GROUP_ORDER:
        n = sum(1 for r in rows if GROUPS.get(r[4]) == g)
        gkinds = sorted(k for k, v in GROUPS.items() if v == g)
        have = [k for k in gkinds if kinds_count.get(k)]
        print(f"    {g:11s} {n:>6,}   " + ", ".join(f"{k} {kinds_count[k]:,}" for k in have))
    print(f"\n  with an end date {sum(1 for r in rows if r[6] is not None):,}")
    print(f"  before 1900      {sum(1 for r in rows if r[5] < 1900):,}")
    print(f"  before AD 1      {sum(1 for r in rows if r[5] < 1):,}")

    rep = {"count": len(rows), "bytes": size, "by_kind": dict(kinds),
           "by_source": dict(srcs),
           "by_group": {g: sum(1 for r in rows if GROUPS.get(r[4]) == g) for g in GROUP_ORDER},
           "clamped_to_world_start": clamped,
           "with_end": sum(1 for r in rows if r[6] is not None),
           "before_1900": sum(1 for r in rows if r[5] < 1900),
           "before_1": sum(1 for r in rows if r[5] < 1)}
    with open(os.path.join(LOGS, "step35_water_report.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1)

    ok = 0
    for name, lat, lon, yr in TEST_PLACES:
        n = sum(1 for r in rows
                if km(lat, lon, r[2] / 1000.0, r[3] / 1000.0) <= 25
                and r[5] <= yr and (r[6] is None or yr < r[6]))
        if n:
            ok += 1
    print(f"  test places answered by the pack: {ok} of {len(TEST_PLACES)}")
    rep["test_places"] = ok
    with open(os.path.join(LOGS, "step35_water_report.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1)
    print("\n  written: logs/step35_water_report.json")


if __name__ == "__main__":
    main()
