#!/usr/bin/env python3
# ============================================================================
# Step 33, part 4 (B9, B11, B13, B20, E14, E16): build
# history/building_culture.json.gz from building_culture_table.py.
#
#   python3 build_building_culture.py            build the pack and report
#   python3 build_building_culture.py --places   what the 31 test places get
#
# The hand-written table says where (country codes, groups, @subregions, or
# ALL) and when (a year window). This turns it into one slice list per country,
# so the game's question -- what is a house here, in this year? -- is answered
# by a lookup and not by a search.
#
# Which slice wins where several reach the same point and year, in order:
#   1. a row carrying a box does not apply at all outside it (Cusco is in the
#      Inca country, not in a maloca, though both boxes would take it), and one
#      whose box holds the point beats one without a box (South India is not
#      North India, the Arctic is not the eastern woodlands);
#   2. a higher rank: a local row beats a national one, a national one beats a
#      continental era, and the modern world comes after both;
#   3. the later start year -- the most recent claim is the most specific;
#   4. the row covering fewer countries;
#   5. the row written later in the table.
# Anything uncovered falls to the world default, and the report says how much
# that is: a big default share means a hole in the table, not a finished job.
#
# Nothing the technology atlas already knows is stored here. Fired brick,
# cement, steel, glass, paved roads, tarmac, candles, gas light, paraffin lamps,
# electric light and running water have a year for each of 258 countries and a
# share by the size of the town; the register asks the atlas and upgrades these
# words itself. What is stored is only what no atlas can know.
# ============================================================================
import collections
import gzip
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import building_culture_table as CT          # noqa: E402
import build_country_grid as CG              # noqa: E402
import build_technology_atlas as BTA         # noqa: E402

LOGS = os.path.join(HERE, "logs")
HISTORY = os.path.join(HERE, "..", "eternal", "src", "main", "resources",
                       "data", "eternalengine", "eternal", "history")
OUT = os.path.join(HISTORY, "building_culture.json.gz")

# The world-wide test set (SYSTEMS_PLAN.md part 9), as every other step uses it.
sys.path.insert(0, HERE)
from fetch_town_wd import TEST_PLACES  # noqa: E402

NEVER_NEG = -10000
NEVER_POS = 10000


def tenths(x):
    return int(round(float(x) * 10))


def main():
    countries, grid_rows = CG.read()
    codes = [c[0] for c in countries]
    sub_of = {c[0]: c[2] for c in countries}
    expand = BTA.resolve_groups(countries, sub_of)
    print(f"  {len(codes)} countries, "
          f"{len(set(sub_of.values()))} subregions")

    bad_places = []
    rows = []
    row_id = {}
    slices = collections.defaultdict(list)       # code -> [[start, end, row, box, rank, n]]
    for c in CT.CULTURES:
        places = []
        for w in c["where"]:
            if w == "ALL":
                places += codes
            else:
                try:
                    places += expand(w)
                except SystemExit:
                    bad_places.append((c["id"], w))
        places = sorted(set(places))
        if not places:
            print(f"  WARNING: {c['id']} covers no country")
            continue
        box = []
        if c.get("box"):
            s, n, w, e = c["box"]
            box = [tenths(s), tenths(n), tenths(w), tenths(e)]
        rec = {
            "id": c["id"],
            "house": c["house"], "wall": c["wall"], "roof": c["roof"], "floor": c["floor"],
            "plan": c["plan"], "surface": c["surface"], "water": c["water"], "light": c["light"],
            "inside": c["inside"], "market": c["market"], "storeys": c["storeys"],
            "source": c["source"],
        }
        idx = row_id.get(c["id"])
        if idx is None:
            idx = len(rows)
            rows.append(rec)
            row_id[c["id"]] = idx
        start = c["start"] if c["start"] is not None else NEVER_NEG
        end = c["end"] if c["end"] is not None else NEVER_POS
        rank = CT.RANKS.get(c["id"], CT.DEFAULT_RANK)
        for code in places:
            slices[code].append([start, end, idx, box, rank, len(places)])

    d = CT.DEFAULT
    default_rec = {
        "id": d["id"], "house": d["house"], "wall": d["wall"], "roof": d["roof"],
        "floor": d["floor"], "plan": d["plan"], "surface": d["surface"], "water": d["water"],
        "light": d["light"], "inside": d["inside"], "market": d["market"],
        "storeys": d["storeys"], "source": d["source"],
    }
    default_idx = len(rows)
    rows.append(default_rec)

    # A country with no slice of its own takes the default; the report counts
    # how often that happens for a point in a real year.
    covered = {c for c in slices}
    bare = [c for c in codes if c not in covered]
    if bare:
        print(f"  {len(bare)} countries have no row at all: {', '.join(bare[:20])}")

    if bad_places:
        print("\n  unknown places in building_culture_table.py (Natural Earth's codes):")
        for i, w in bad_places:
            print(f"    {i:28s} {w}")
        raise SystemExit(1)

    sources = sorted({r["source"] for r in rows})
    print(f"  {len(rows)} rows, {len(slices)} countries with at least one, "
          f"{len(sources)} articles cited")

    pack = {
        "format": 1,
        "id": "building_culture",
        "source": ("English Wikipedia's articles, written down by hand for the mod (step 33, part 4): "
                   "what a house is, what it is made of, how a town is laid out, what its lanes are "
                   "surfaced with, where its water comes from, what it is lit by after dark, what is "
                   "inside a home, and where people trade. Every row names the article it was written "
                   "from. The years a technology reached a country -- fired brick, cement, steel, "
                   "glass, paved roads, tarmac, candles, gas light, paraffin lamps, electric light, "
                   "running water -- are NOT here: they come from the technology atlas (step 30a), "
                   "which knows them for 258 countries and by the size of the town."),
        "note": ("countries: {code: [[from, to, row, box, rank, countriesCovered], ...]}. "
                 "from is inclusive, to exclusive; -10000 and 10000 stand for no bound. "
                 "box is [south, north, west, east] in tenths of a degree, [] when the row covers "
                 "the whole country; a row with a box does not apply outside it. rank settles which "
                 "row wins: a row whose box holds the point beats one without a box, then a higher "
                 "rank (3 a region inside a country, 2 a nation or a culture, 1 a continental era, "
                 "0 the modern world and the two rows of prehistory), then the later start year, "
                 "then the row covering fewer countries. rows hold the words; default is the row "
                 "used where nothing reaches."),
        "rows": rows,
        "countries": {c: slices[c] for c in sorted(slices)},
        "default": default_idx,
        "sources": sources,
    }
    with open(OUT, "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as fh:
        json.dump(pack, fh, ensure_ascii=False, separators=(",", ":"))
    size = os.path.getsize(OUT)
    print(f"\n  {len(rows)} rows -> {OUT.split('/')[-1]} ({size / 1000:.0f} kB)")

    # ---- how much of the world is actually covered -------------------------
    def pick(code, lat, lon, year):
        best, best_key = None, None
        for s in slices.get(code, ()):
            if not (s[0] <= year < s[1]):
                continue
            if s[3]:                       # a boxed row speaks only inside its box
                so, no, we, ea = s[3]
                if not ((so <= tenths(lat) <= no) and (we <= tenths(lon) <= ea)):
                    continue
            key = (1 if s[3] else 0, s[4], s[0], -s[5])
            if best_key is None or key > best_key:
                best, best_key = s, key
        return best

    total = hit = 0
    used = collections.Counter()
    uncovered = collections.Counter()
    # Two eras are counted apart: the deep past, where one row (a village of
    # mud and poles) is the honest answer nearly everywhere, and the last three
    # thousand years, where a country should have a row of its own.
    eras = {"-8000..-1000": (range(-8000, -999, 100), [0, 0]),
            "-1000..2026": (range(-1000, 2027, 100), [0, 0])}
    for c in countries:
        code, name, sub = c[0], c[1], c[2]
        # c[5], c[6] are the country's biggest town (the grid's own centre);
        # c[3], c[4] are the weighted middle of all its land.
        mlat, mlon = (c[5], c[6]) if c[5] or c[6] else (c[3], c[4])
        for label, (years, tally) in eras.items():
            for year in years:
                total += 1
                tally[0] += 1
                s = pick(code, mlat, mlon, year)
                if s is None:
                    uncovered[sub] += 1
                else:
                    hit += 1
                    tally[1] += 1
                    used[rows[s[2]]["id"]] += 1
    for label, (_years, (n, h)) in eras.items():
        print(f"  {label:14s} {h:>6,}/{n:<6,} of country-years answered "
              f"({100.0 * h / n:.1f}%)")
    print(f"\n  country-years answered (258 countries x -3000..2026 by 100): "
          f"{hit:,} of {total:,} ({100.0 * hit / total:.1f}%)")
    if uncovered:
        print(f"  {sum(uncovered.values()):,} fall to the default, worst subregions first:")
        for k, v in uncovered.most_common(10):
            print(f"    {k:26s} {v:>6,}")
    print("\n  the rows that carry the world, most used first")
    for k, v in used.most_common(20):
        print(f"    {k:30s} {v:>7,}")
    never = [k for k in row_id if k not in used]
    if never:
        print(f"\n  rows never reached by a country's own centre: {', '.join(sorted(never))}")

    rep = {"rows": len(rows), "bytes": size, "countries_with_rows": len(slices),
           "country_years": total, "covered": hit,
           "default_share_pct": round(100.0 * (total - hit) / total, 2),
           "by_row": dict(used), "sources": sources}
    with open(os.path.join(LOGS, "step33_culture_report.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1)
    print("\n  written: logs/step33_culture_report.json")

    if "--places" in sys.argv:
        print("\n  the 31 test places, in their own year")
        for name, lat, lon, year in TEST_PLACES:
            code = CG.country_at(countries, grid_rows, lat, lon)
            s = pick(code, lat, lon, year) if code else None
            r = rows[s[2]] if s else rows[default_idx]
            tag = r["id"] if s else "DEFAULT"
            print(f"    {name:18s} {year:>6d}  {str(code):4s} {tag:28s} "
                  f"{r['house'][:52]}")
            print(f"    {'':18s} {'':>6s}      wall {r['wall']}; roof {r['roof']}; "
                  f"streets {r['surface']}, {r['plan']}")
            print(f"    {'':18s} {'':>6s}      water {r['water']}")
            print(f"    {'':18s} {'':>6s}      after dark {r['light']}")


if __name__ == "__main__":
    main()
