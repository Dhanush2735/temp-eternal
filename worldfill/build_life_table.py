#!/usr/bin/env python3
"""Step 38 (D2, D17, and the life-span half of C20): build history/life_table.json.gz.

    python3 build_life_table.py
    python3 build_life_table.py --selftest    rebuild in memory and check it (exit 1 on a problem)

Two tables, built from the hand-written rows in life_table.py: how long people lived by place and
year, and when they married and how many children they had. The register in the mod (people/LifeTable)
reads the pack and turns the anchors into a survivor curve; nothing here is computed except the
checks, because the arithmetic belongs with the register that uses it.

What this script does check:

* every place and year the mod can ask about gets an answer, or the build fails;
* no two rows of the same kind overlap in a way that makes the answer depend on file order;
* the anchors are plausible: a fifteen-year-old is always better off than a newborn, and the curve
  never claims anyone lives past 125.
"""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from life_table import ESTIMATED, MARRIAGE, MIXED, MORTALITY, RECORDED  # noqa: E402

MOD = os.path.normpath(os.path.join(HERE, "..", "eternal"))
OUT = os.path.join(MOD, "src", "main", "resources", "data", "eternalengine", "eternal",
                   "history", "life_table.json.gz")

SOURCE = ("English Wikipedia (dump 2026-10-16): 'Life expectancy', 'Demography of the Roman "
          "Empire', 'Western European marriage pattern', 'Total fertility rate', 'Black Death', "
          "'Marriageable age' and 'History of the family'; the English-city figures from Woods, "
          "Mortality, migration and epidemiological change in English cities, 1600-1870 "
          "(PMC7611108); the Qing figures from Voigtlander and Voth, American Economic Review "
          "103:6 (2013); the England 1650-1849 reconstitution from Cummins, EHES 259. Values "
          "marked estimated are the table's own, not any source's.")


# --------------------------------------------------------------------------- helpers
def box_area(boxes):
    """The whole world scores as infinitely large, so any named box beats it."""
    if not boxes:
        return float("inf")
    return sum((b[1] - b[0]) * (b[3] - b[2]) for b in boxes)


def holds(row, lat, lon, year):
    if year < row.frm or (row.to is not None and year > row.to):
        return False
    if not row.boxes:
        return True
    return any(b[0] <= lat <= b[1] and b[2] <= lon <= b[3] for b in row.boxes)


def pick(rows, lat, lon, year, urban=False):
    """The most specific row that holds: an urban row for an urban question first, then the
    smallest box, then the later start."""
    best = None
    for r in rows:
        if not holds(r, lat, lon, year):
            continue
        key = (0 if getattr(r, "urban", False) == urban else 1, box_area(r.boxes), r.frm)
        if best is None or key < (0 if getattr(best, "urban", False) == urban else 1,
                                  box_area(best.boxes), best.frm):
            best = r
    return best


def build():
    """Sort by (from, id) so the pack is stable, then serialise."""
    mort = sorted(MORTALITY, key=lambda r: (r.frm, r.id))
    marr = sorted(MARRIAGE, key=lambda r: (r.frm, r.id))
    doc = {
        "format": 1,
        "id": "life_table",
        "source": SOURCE,
        "mortality": [{
            "id": r.id, "name": r.name,
            "boxes": [[b[0], b[1], b[2], b[3]] for b in r.boxes],
            "from": r.frm, "to": r.to,
            "anchors": [[a, e] for a, e in r.anchors],
            "infant": r.infant, "urban": r.urban, "mark": r.mark, "note": r.note,
            "source": r.src,
        } for r in mort],
        "marriage": [{
            "id": r.id, "name": r.name,
            "boxes": [[b[0], b[1], b[2], b[3]] for b in r.boxes],
            "from": r.frm, "to": r.to,
            "wife": r.wife, "husband": r.husband, "celibate": r.celibate, "births": r.births,
            "mark": r.mark, "note": r.note, "source": r.src,
        } for r in marr],
    }
    return doc


# --------------------------------------------------------------------------- the checks
SPOTS = [
    ("Hyderabad", 17.39, 78.49), ("Delhi", 28.61, 77.21), ("London", 51.51, -0.13),
    ("Paris", 48.86, 2.35), ("Rome", 41.90, 12.50), ("Athens", 37.98, 23.73),
    ("Cairo", 30.04, 31.24), ("Baghdad", 33.31, 44.36), ("Chang'an", 34.27, 108.90),
    ("Kyoto", 35.01, 135.77), ("Timbuktu", 16.77, -3.01), ("Cusco", -13.53, -71.97),
    ("Tenochtitlan", 19.43, -99.13), ("Cahokia", 38.65, -90.06), ("Sydney", -33.87, 151.21),
    ("Cape Town", -33.92, 18.42),
]

CASES = [
    # the cases a player is most likely to walk into, and the answers the sources support
    ("Hyderabad", 17.39, 78.49, 1500, "mortality", "late_medieval"),
    ("Hyderabad", 17.39, 78.49, 1348, "mortality", "medieval_world"),
    ("Hyderabad", 17.39, 78.49, 1948, "mortality", "nineteen_hundred"),
    ("Hyderabad", 17.39, 78.49, 1948, "marriage", "world_1900"),
    ("London", 51.51, -0.13, 1348, "mortality", "black_death"),
    ("London", 51.51, -0.13, 1340, "mortality", "medieval_europe"),
    ("London", 51.51, -0.13, 1840, "mortality", "nineteenth_england"),
    ("London", 51.51, -0.13, 1750, "mortality", "eighteenth_england"),
    ("London", 51.51, -0.13, 1700, "marriage", "hajnal_england_1650"),
    ("Paris", 48.86, 2.35, 1750, "mortality", "eighteenth_france"),
    ("Paris", 48.86, 2.35, 1700, "marriage", "hajnal_west"),
    ("Rome", 41.90, 12.50, 100, "mortality", "classical_rome"),
    ("Athens", 37.98, 23.73, -400, "mortality", "classical_greece"),
    ("Baghdad", 33.31, 44.36, 900, "mortality", "medieval_islam"),
    ("Cairo", 30.04, 31.24, 1900, "mortality", "nineteen_hundred"),
    ("Chang'an", 34.27, 108.90, 750, "mortality", "east_asia_old"),
    ("Chang'an", 34.27, 108.90, 1800, "marriage", "qing_china"),
    ("Delhi", 28.61, 77.21, 1850, "mortality", "nineteenth_india"),
    ("Cusco", -13.53, -71.97, 1400, "mortality", "late_medieval"),
    ("Cahokia", 38.65, -90.06, 1100, "marriage", "medieval_world"),
    ("Sydney", -33.87, 151.21, 1800, "mortality", "nineteenth_world"),
]


def selftest(doc):
    problems = []
    seen = set()
    for kind in ("mortality", "marriage"):
        for row in doc[kind]:
            rid = kind + "/" + row["id"]
            if rid in seen:
                problems.append("duplicate id: " + rid)
            seen.add(rid)

    # 1. every place and every year gets an answer
    for name, lat, lon in SPOTS:
        for year in range(-10000, 2027, 25):
            for kind in ("mortality", "marriage"):
                rows = doc[kind]
                got = pick_rows(rows, lat, lon, year)
                if got is None:
                    problems.append("no %s row for %s in %d" % (kind, name, year))
        for year in (-5000, -3000, -800, -400, 1, 500, 1000, 1348, 1500, 1700, 1800, 1900,
                     1950, 2000, 2026):
            for kind in ("mortality", "marriage"):
                if pick_rows(doc[kind], lat, lon, year) is None:
                    problems.append("no %s row for %s in %d" % (kind, name, year))

    # 2. the written cases
    for name, lat, lon, year, kind, want in CASES:
        got = pick_rows(doc[kind], lat, lon, year)
        got_id = got["id"] if got else None
        if got_id != want:
            problems.append("%s %d: wanted %s, got %s" % (name, year, want, got_id))

    # 3. the anchors themselves
    for row in doc["mortality"]:
        a = row["anchors"]
        # There is deliberately no check that e(0) < e(15). In a high-mortality population it is
        # true — surviving the dangerous years is worth more than the years already lived, so
        # remaining years climb through childhood. In a modern one it is false: with 20 deaths
        # per thousand in the first year a newborn already expects a long life, and e(15) is
        # below e(0). The check above (expected age at death never falls with age) covers both.
        for age, e in a:
            if age + e > 125:
                problems.append("%s: anchor age %d + %s years is past 125" % (row["id"], age, e))
        # surviving longer must never mean expecting to die younger
        totals = [age + e for age, e in a]
        if any(totals[i + 1] < totals[i] - 1e-9 for i in range(len(totals) - 1)):
            problems.append("%s: expected age at death falls with age (%s)" % (row["id"], totals))
        # and after the childhood peak the remaining years must fall away
        peak = max(range(len(a)), key=lambda i: a[i][1])
        tail = [e for _, e in a[peak:]]
        if any(tail[i + 1] > tail[i] + 1e-9 for i in range(len(tail) - 1)):
            problems.append("%s: remaining years rise again after the peak (%s)" % (row["id"], a))

    for row in doc["marriage"]:
        if row["wife"] > row["husband"]:
            problems.append("%s: wives marry older than husbands" % row["id"])
        if row["celibate"] >= 100:
            problems.append("%s: nobody marries" % row["id"])

    # 4. how much of the table is measured and how much is shaped
    for kind in ("mortality", "marriage"):
        n = len(doc[kind])
        est = sum(1 for r in doc[kind] if r["mark"] == ESTIMATED)
        mix = sum(1 for r in doc[kind] if r["mark"] == MIXED)
        print("  %-9s %2d rows: %2d recorded, %2d mixed, %2d estimated"
              % (kind, n, n - est - mix, mix, est))

    if problems:
        print("\n%d PROBLEM(S):" % len(problems))
        for p in problems[:40]:
            print("  - " + p)
        return 1
    print("  %d cases, 0 problems" % len(CASES))
    return 0


def pick_rows(rows, lat, lon, year, urban=False):
    """The same rule the Java register uses: an urban row for an urban question first, then the
    smallest box, then the later start."""
    def area(bs):
        # the whole world scores as infinitely large, so any named box beats it
        return float("inf") if not bs else sum((b[1] - b[0]) * (b[3] - b[2]) for b in bs)

    def key(r):
        # later start first: when two rows claim the same box, the more precise one wins
        return (0 if r.get("urban", False) == urban else 1, area(r["boxes"]), -r["from"])

    best = None
    for r in rows:
        if year < r["from"] or (r["to"] is not None and year > r["to"]):
            continue
        if r["boxes"] and not any(b[0] <= lat <= b[1] and b[2] <= lon <= b[3] for b in r["boxes"]):
            continue
        if best is None or key(r) < key(best):
            best = r
    return best


# --------------------------------------------------------------------------- the curve
#
# An independent implementation of the arithmetic the Java register does, so the two can be
# checked against each other. mu(x) = (1 + e'(x)) / e(x) follows from the definition of a life
# table: with T(x) the years left to the cohort and S(x) the share alive, e = T/S and S = -T',
# so d(ln T)/dx = -1/e and -d(ln S)/dx = 1/e + e'/e.

import math  # noqa: E402


def expectancy(anchors, age):
    if age <= anchors[0][0]:
        return anchors[0][1]
    for i in range(1, len(anchors)):
        if age <= anchors[i][0]:
            span = anchors[i][0] - anchors[i - 1][0]
            f = 0.0 if span <= 0 else (age - anchors[i - 1][0]) / span
            return anchors[i - 1][1] + f * (anchors[i][1] - anchors[i - 1][1])
    n = len(anchors) - 1
    span = anchors[n][0] - anchors[n - 1][0]
    slope = -1.0 if span <= 0 else (anchors[n][1] - anchors[n - 1][1]) / span
    if slope >= 0:
        slope = -1.0
    return max(0.0, anchors[n][1] + slope * (age - anchors[n][0]))


def hazard(a0, e0, a1, e1):
    if a1 <= a0:
        return 0.0
    if e0 <= 0 or e1 <= 0:
        return float("inf")
    log = math.log(e1 / e0)
    integral = (a1 - a0) / e0 if abs(e1 - e0) < 1e-9 else (a1 - a0) / (e1 - e0) * log
    return integral + log


def survival(anchors, upto=130):
    out = [1.0]
    cumulative = 0.0
    for age in range(1, upto + 1):
        cumulative += hazard(age - 1, expectancy(anchors, age - 1), age,
                              expectancy(anchors, age))
        out.append(math.exp(-cumulative))
        if expectancy(anchors, age) <= 0.0:
            break
    return out


def curve_table(row):
    a = row["anchors"]
    s = survival(a)
    def at(age):
        return s[age] if age < len(s) else 0.0
    return {
        "e0": a[0][1],
        "e15": expectancy(a, 15),
        "age15": 15 + expectancy(a, 15),
        "s15": at(15),
        "s50": at(50),
        "s70": at(70),
        "max": len(s) - 1,
    }


CURVE_SPOTS = [
    ("classical_greece", 37.98, 23.73, -400),
    ("classical_rome", 41.90, 12.50, 100),
    ("medieval_europe", 51.51, -0.13, 1300),
    ("black_death", 51.51, -0.13, 1350),
    ("nineteenth_england", 51.51, -0.13, 1830),
    ("nineteenth_india", 28.61, 77.21, 1850),
    ("industrial_city", 53.40, -2.98, 1840, True),      # Liverpool, asked for as a town
    ("industrial_town", 53.80, -1.55, 1840, True),      # Leeds, asked for as a town
    ("nineteenth_england", 51.75, -1.25, 1840, False),  # Oxfordshire, asked for as countryside
    ("modern_2000", 17.39, 78.49, 2010),
    ("modern_aids_africa", -24.65, 25.91, 2000),
    ("modern_japan", 35.68, 139.69, 2020),
]


def print_curves(doc):
    print()
    print("  %-22s %5s %5s %6s %6s %6s %6s %5s" % ("regime", "e0", "e15", "dies@15", "S(15)",
                                                    "S(50)", "S(70)", "max"))
    for spot in CURVE_SPOTS:
        want, lat, lon, year = spot[0], spot[1], spot[2], spot[3]
        urban = spot[4] if len(spot) > 4 else False
        row = pick_rows(doc["mortality"], lat, lon, year, urban)
        assert row is not None and row["id"] == want, \
            "curve spot %s got %s" % (want, row["id"] if row else None)
        c = curve_table(row)
        print("  %-22s %5.1f %5.1f %6.1f %6.3f %6.3f %6.3f %5d"
              % (row["id"], c["e0"], c["e15"], c["age15"], c["s15"], c["s50"], c["s70"], c["max"]))
    print()
    print("  e0 = years of life at birth; e15 = years remaining at fifteen;")
    print("  dies@15 = the age a fifteen-year-old can expect to reach; S(x) = share reaching x.")


def main():
    doc = build()
    if "--selftest" in sys.argv:
        print("selftest: %d mortality rows, %d marriage rows, %d cases"
              % (len(doc["mortality"]), len(doc["marriage"]), len(CASES)))
        rc = selftest(doc)
        if rc:
            return rc
        print_curves(doc)
        print("  (no pack written in --selftest mode)")
        return 0

    rc = selftest(doc)
    if rc:
        return rc
    raw = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.GzipFile(OUT, "wb", compresslevel=9, mtime=0) as fh:
        fh.write(raw)
    print("wrote %s" % OUT)
    print("  %d mortality rows, %d marriage rows" % (len(doc["mortality"]), len(doc["marriage"])))
    print("  %d bytes raw, %d gzipped" % (len(raw), os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
