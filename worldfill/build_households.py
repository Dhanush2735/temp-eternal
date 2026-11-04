#!/usr/bin/env python3
"""Step 38 (D3): build history/households.json.gz from the hand-written rows.

    python3 build_households.py
    python3 build_households.py --selftest    rebuild in memory and check it (exit 1 on a problem)

What it checks:

* every place and year the mod can ask about gets a household, or the build fails;
* the four structure shares add to 100 in every row (the row class refuses otherwise);
* a mean size that contradicts its own structure — fewer than two people in a row that is almost
  all nuclear families, or nine people in one that is a third solitaries — is a mistake.

The lookup rule is imported from build_life_table, not written again: two copies of "the most
specific box wins" is two chances to disagree with the Java register.
"""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from build_life_table import SPOTS, pick_rows                      # noqa: E402
from households_table import ESTIMATED, HOUSEHOLDS, MIXED          # noqa: E402

MOD = os.path.normpath(os.path.join(HERE, "..", "eternal"))
OUT = os.path.join(MOD, "src", "main", "resources", "data", "eternalengine", "eternal",
                   "history", "households.json.gz")

SOURCE = ("Laslett, P. (ed.) Household and Family in Past Time (1972) and Laslett, Size and "
          "structure of the household in England over three centuries, Population Studies 23:2 "
          "(1969); Household and family structure in England and Wales, 1851-1911 (Cambridge); "
          "Household and family during urbanization and industrialization, 2013; United Nations "
          "DESA, Database on Household Size and Composition 2026 (ST/ESA/SER.A/433); Liu et al., "
          "A global perspective on household size and composition 1970-2020; Pew Research, "
          "Household patterns by region; English Wikipedia, 'Joint family' and 'History of the "
          "family'. Rows marked estimated are the table's own, not any source's.")

CASES = [
    # the cases a player is most likely to walk into
    ("London 1600", 51.51, -0.13, 1600, False, "early_modern_england"),
    ("London 1800", 51.51, -0.13, 1800, False, "preindustrial_england"),
    ("London 1880", 51.51, -0.13, 1880, False, "victorian_england"),
    ("London 1880, a town", 51.51, -0.13, 1880, True, "industrial_town"),
    ("Oxfordshire 1600", 51.75, -1.25, 1600, False, "early_modern_england"),
    ("Bavaria 1700", 48.14, 11.58, 1700, False, "stem_europe"),
    ("Paris 1700", 48.86, 2.35, 1700, False, "stem_europe"),
    ("Hyderabad 1700", 17.39, 78.49, 1700, False, "joint_india"),
    ("Hyderabad 1948", 17.39, 78.49, 1948, False, "joint_india"),
    ("Delhi 2020", 28.61, 77.21, 2020, False, "modern_india"),
    ("Chang'an 800", 34.27, 108.90, 800, False, "east_asian_stem"),
    ("Kyoto 1700", 35.01, 135.77, 1700, False, "east_asian_stem"),
    ("Kyoto 2020", 35.01, 135.77, 2020, False, "modern_east_asia"),
    ("Beijing 2020", 39.90, 116.41, 2020, False, "modern_east_asia"),
    ("Timbuktu 1400", 16.77, -3.01, 1400, False, "late_medieval"),
    ("Cusco 1500", -13.53, -71.97, 1500, False, "late_medieval"),
    ("Cahokia 1100", 38.65, -90.06, 1100, False, "medieval_world"),
    ("Cahokia 1300", 38.65, -90.06, 1300, False, "medieval_world"),
    ("London 2020", 51.51, -0.13, 2020, False, "modern_europe"),
    ("New York 2020", 40.71, -74.01, 2020, False, "modern_europe"),
    ("Lagos 2020", 6.52, 3.38, 2020, False, "modern_africa"),
    ("Cairo 2020", 30.04, 31.24, 2020, False, "modern_mena"),
    ("Cusco 2020", -13.53, -71.97, 2020, False, "modern_latin"),
    # the number that settled the argument, asked for directly
    ("England before 1750", 51.51, -0.13, 1650, False, "early_modern_england"),
]


def build():
    rows = sorted(HOUSEHOLDS, key=lambda r: (r.frm, r.id))
    return {
        "format": 1,
        "id": "households",
        "source": SOURCE,
        "households": [{
            "id": r.id, "name": r.name,
            "boxes": [[b[0], b[1], b[2], b[3]] for b in r.boxes],
            "from": r.frm, "to": r.to,
            "size": r.size, "nuclear": r.nuclear, "stem": r.stem, "joint": r.joint,
            "solo": r.solo, "leave": r.leave, "servants": r.servants, "widow": r.widow,
            "urban": r.urban, "mark": r.mark, "note": r.note, "source": r.src, "pub": r.pub,
        } for r in rows],
    }


def selftest(doc):
    problems = []
    rows = doc["households"]
    seen = set()
    for r in rows:
        if r["id"] in seen:
            problems.append("duplicate id: " + r["id"])
        seen.add(r["id"])

    # 1. every place and every year gets a household
    for name, lat, lon in SPOTS:
        for year in list(range(-10000, 2027, 25)) + [-5000, -3000, -800, -400, 1, 500, 1000,
                                                     1348, 1500, 1700, 1800, 1900, 1950, 2000,
                                                     2026]:
            if pick_rows(rows, lat, lon, year) is None:
                problems.append("no household row for %s in %d" % (name, year))

    # 2. the written cases
    for name, lat, lon, year, urban, want in CASES:
        got = pick_rows(rows, lat, lon, year, urban)
        got_id = got["id"] if got else None
        if got_id != want:
            problems.append("%s: wanted %s, got %s" % (name, want, got_id))

    # 3. a size its own structure cannot produce
    for r in rows:
        if r["nuclear"] + r["stem"] >= 80 and r["size"] < 2.0:
            problems.append("%s: almost all nuclear but a mean of %.1f people" % (r["id"],
                                                                                  r["size"]))
        if r["solo"] >= 40 and r["size"] > 4.0:
            problems.append("%s: %d%% solitaries but a mean of %.1f people"
                            % (r["id"], r["solo"], r["size"]))
        if r["joint"] >= 35 and r["size"] < 3.5:
            problems.append("%s: %d%% joint households but a mean of only %.1f people"
                            % (r["id"], r["joint"], r["size"]))
        if r["nuclear"] + r["stem"] + r["joint"] + r["solo"] != 100:
            problems.append("%s: structure shares do not add to 100" % r["id"])

    est = sum(1 for r in rows if r["mark"] == ESTIMATED)
    mix = sum(1 for r in rows if r["mark"] == MIXED)
    print("  households %2d rows: %2d recorded, %2d mixed, %2d estimated"
          % (len(rows), len(rows) - est - mix, mix, est))

    if problems:
        print("\n%d PROBLEM(S):" % len(problems))
        for p in problems[:40]:
            print("  - " + p)
        return 1
    print("  %d cases, 0 problems" % len(CASES))
    return 0


def main():
    doc = build()
    if "--selftest" in sys.argv:
        print("selftest: %d household rows, %d cases" % (len(doc["households"]), len(CASES)))
        rc = selftest(doc)
        if rc:
            return rc
        print("  (no pack written in --selftest mode)")
        return 0

    rc = selftest(doc)
    if rc:
        return rc
    raw = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.GzipFile(OUT, "wb", compresslevel=9, mtime=0) as fh:
        fh.write(raw)
    print("wrote %s" % OUT)
    print("  %d household rows, %d bytes raw, %d gzipped"
          % (len(doc["households"]), len(raw), os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
