#!/usr/bin/env python3
"""Step 38 (D4): build history/jobs.json.gz from the hand-written rows.

    python3 build_jobs.py
    python3 build_jobs.py --selftest     rebuild in memory and check it (exit 1 on a problem)

What it checks:

* every place and year the mod can ask about gets an occupational structure, or the build fails;
* the twelve shares add to 100 in every row (the row class refuses otherwise);
* **the three English rows reproduce the published sector split**, which is the only place in
  this table where a measured three-way split exists to be checked against:

      1688   55.6 / 18.5 / 25.9   primary / secondary / tertiary   (Crafts, CAMPOP)
      1802-3 41.7 / 24.7 / 33.6
      1841   22.2 / 40.5 / 37.3

* the industrial town has almost no farmers, and modern Europe has almost no farmers either but
  for the opposite reason.

The lookup rule is imported from build_life_table, not written again: three copies of "the most
specific box wins" would be three chances to disagree with the Java register.
"""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from build_life_table import SPOTS, pick_rows               # noqa: E402
from jobs_table import JOBS, WORKS                          # noqa: E402

MOD = os.path.normpath(os.path.join(HERE, "..", "eternal"))
OUT = os.path.join(MOD, "src", "main", "resources", "data", "eternalengine", "eternal",
                   "history", "jobs.json.gz")

SOURCE = ("Cambridge Group for the History of Population and Social Structure, The occupational "
          "structure of England and Wales c.1750-1911 (Crafts; Lindert and Williamson); Gregory "
          "King's social table for England and Wales 1688, as revised; Robert Allen, Class "
          "structure and inequality during the industrial revolution; the 1831 census of England "
          "and Wales; ILO modelled estimates of employment in agriculture via the World Bank; "
          "FAO, FAOSTAT Analytical Brief 92, Employment indicators 2000-2022; English Wikipedia, "
          "'List of countries by employment in agriculture', 'Domesday Book', 'Census in India' "
          "and 'History of agriculture'. Rows marked estimated, and every row with pub=false, "
          "carry this table's own shares, not any source's.")

# name, lat, lon, year, urban, expected row id
CASES = [
    ("London 1688", 51.51, -0.13, 1688, False, "england_1688"),
    ("London 1800", 51.51, -0.13, 1800, False, "england_1800"),
    ("London 1841", 51.51, -0.13, 1841, False, "england_1841"),
    ("London 1880, a town", 51.51, -0.13, 1880, True, "industrial_town"),
    ("Oxfordshire 1688", 51.75, -1.25, 1688, False, "england_1688"),
    ("Bavaria 1700", 48.14, 11.58, 1700, False, "early_modern_europe"),
    ("Rome 1700", 41.90, 12.50, 1700, False, "early_modern_europe"),
    ("Hyderabad 1850", 17.39, 78.49, 1850, False, "british_india"),
    ("Hyderabad 1948", 17.39, 78.49, 1948, False, "british_india"),
    ("Delhi 2020", 28.61, 77.21, 2020, False, "modern_india"),
    ("Kyoto 1700", 35.01, 135.77, 1700, False, "early_modern_world"),
    ("Beijing 1700", 39.90, 116.41, 1700, False, "early_modern_world"),
    ("Beijing 2020", 39.90, 116.41, 2020, False, "modern_east_asia"),
    ("Tokyo 2020", 35.68, 139.69, 2020, False, "modern_east_asia"),
    ("Cusco 1500", -13.53, -71.97, 1500, False, "late_medieval"),
    ("Cahokia 1100", 38.65, -90.06, 1100, False, "medieval_world"),
    ("Timbuktu 1400", 16.77, -3.01, 1400, False, "late_medieval"),
    ("London 2020", 51.51, -0.13, 2020, False, "modern_europe"),
    ("New York 2020", 40.71, -74.01, 2020, False, "modern_europe"),
    ("Lagos 2020", 6.52, 3.38, 2020, False, "modern_africa"),
    ("Cairo 2020", 30.04, 31.24, 2020, False, "modern_mena"),
    ("Cusco 2020", -13.53, -71.97, 2020, False, "modern_latin"),
    ("Yakutsk 2020", 62.03, 129.73, 2020, False, "modern_world"),
    ("Angkor 1300", 13.41, 103.87, 1300, False, "medieval_world"),
]

# the measured three-way split, from the Cambridge Group's revision of the English social tables.
# Nothing else in this table has a published sector split to be checked against.
SECTOR_CASES = [
    ("england_1688", 55.6, 18.5, 25.9),
    ("england_1800", 41.7, 24.7, 33.6),
    ("england_1841", 22.2, 40.5, 37.3),
]


def build():
    rows = sorted(JOBS, key=lambda r: (r.frm, r.id))
    return {
        "format": 1,
        "id": "jobs",
        "source": SOURCE,
        "works": list(WORKS),
        "jobs": [{
            "id": r.id, "name": r.name,
            "boxes": [[b[0], b[1], b[2], b[3]] for b in r.boxes],
            "from": r.frm, "to": r.to, "urban": r.urban,
            "shares": {k: r.shares.get(k, 0) for k in WORKS},
            "mark": r.mark, "note": r.note, "source": r.src, "pub": r.pub,
        } for r in rows],
    }


def selftest(doc):
    problems = []
    rows = doc["jobs"]
    seen = set()
    for r in rows:
        if r["id"] in seen:
            problems.append("duplicate id: " + r["id"])
        seen.add(r["id"])
        if sum(r["shares"].values()) != 100:
            problems.append("%s: shares add to %d" % (r["id"], sum(r["shares"].values())))

    # 1. every place and every year gets work
    for name, lat, lon in SPOTS:
        for year in list(range(-10000, 2027, 25)) + [-5000, -3000, -800, -400, 1, 500, 1000, 1348,
                                                     1500, 1600, 1700, 1800, 1841, 1900, 1950,
                                                     1980, 2000, 2026]:
            if pick_rows(rows, lat, lon, year) is None:
                problems.append("no jobs row for %s in %d" % (name, year))

    # 2. the written cases
    for name, lat, lon, year, urban, want in CASES:
        got = pick_rows(rows, lat, lon, year, urban)
        got_id = got["id"] if got else None
        if got_id != want:
            problems.append("%s: wanted %s, got %s" % (name, want, got_id))

    # 3. the three measured English rows reproduce the published sector split
    by_id = {r["id"]: r for r in rows}
    for rid, p1, p2, p3 in SECTOR_CASES:
        r = by_id[rid]
        got = [sector(r, n) for n in (1, 2, 3)]
        for n, (g, w) in enumerate(zip(got, (p1, p2, p3)), start=1):
            if abs(g - w) > 2.0:
                problems.append("%s sector %d: got %.1f, published %.1f" % (rid, n, g, w))

    # 4. the two rows that are defined by having almost no farmers
    for rid in ("industrial_town", "modern_europe"):
        if by_id[rid]["shares"]["farming"] > 10:
            problems.append("%s should have almost no farmers, has %d%%"
                            % (rid, by_id[rid]["shares"]["farming"]))
    # and the one defined by having almost nobody else
    if by_id["modern_africa"]["shares"]["farming"] < 40:
        problems.append("modern Africa should be mostly farming")

    est = sum(1 for r in rows if r["mark"] == "estimated")
    mix = sum(1 for r in rows if r["mark"] == "mixed")
    pub = sum(1 for r in rows if r["pub"])
    print("  jobs %2d rows: %2d recorded, %2d mixed, %2d estimated; %2d with published shares"
          % (len(rows), len(rows) - est - mix, mix, est, pub))

    if problems:
        print("\n%d PROBLEM(S):" % len(problems))
        for p in problems[:40]:
            print("  - " + p)
        return 1
    print("  %d cases, 0 problems" % (len(CASES) + len(SECTOR_CASES)))
    return 0


def sector(row, n):
    which = {
        1: ("farming", "herding", "foraging"),
        2: ("craft", "miner"),
        3: ("trade", "service", "transport", "soldier", "clergy", "official", "scholar"),
    }[n]
    return sum(row["shares"][k] for k in which)


def main():
    doc = build()
    if "--selftest" in sys.argv:
        print("selftest: %d jobs rows, %d cases" % (len(doc["jobs"]), len(CASES)))
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
    print("  %d jobs rows, %d bytes raw, %d gzipped"
          % (len(doc["jobs"]), len(raw), os.path.getsize(OUT)))
    for rid in ("england_1688", "england_1800", "england_1841"):
        r = next(x for x in doc["jobs"] if x["id"] == rid)
        print("    %-14s primary %2d  secondary %2d  tertiary %2d"
              % (rid, sector(r, 1), sector(r, 2), sector(r, 3)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
