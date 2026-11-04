#!/usr/bin/env python3
"""Step 23a: where does the money table still answer with a placeholder?

Reads the money table the mod ships (money_table.json) and the world ruler register (world_rulers.json.gz) and asks
the table, the way MoneyTable.at does, for the money of every land cell of the register (every STEP-th cell) in a
list of years. Answers are sorted into:

  named        a real money: coins, notes or weighed metal with their own names
  barter       no money: people swap goods (an honest answer where nobody used money)
  placeholder  the old fallbacks "silver and copper coins" and "local money", which name no money

It prints the shares by year and by part of the world, and the biggest groups of placeholder answers by ruler and
century (what still needs a row). With --json it writes worldfill/money_coverage_report.json.

The register stops in 2024; later years ask it about 2024, as MoneyTable does from step 23a.
Cells holding a Deccan place are left to deccan_rulers.json in the game; here they simply have no ruler, so the
table's boxes answer there (the Deccan is covered by the Hyderabad and South India rows anyway).
"""
import collections
import gzip
import json
import math
import struct
import sys

MONEY = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/economy/money_table.json"
RULERS = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/history/world_rulers.json.gz"
REPORT = "/home/user/worldfill/money_coverage_report.json"
HYDE = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/population/hyde_density.bin.gz"
LAST_RULER_YEAR = 2024
YEARS = [-3000, -1500, -600, -300, 0, 300, 600, 900, 1100, 1300, 1450, 1550, 1650, 1750, 1800, 1850, 1880, 1910,
         1930, 1950, 1970, 1990, 2010, 2026]
PARTS = [  # (name, latMin, lonMin, latMax, lonMax); the first that holds a point wins
    ("Europe", 35, -25, 72, 45),
    ("North Africa and West Asia", 12, -18, 45, 63),
    ("Africa south of the Sahara", -36, -20, 18, 52),
    ("South Asia", 5, 60, 37, 98),
    ("East Asia", 18, 98, 54, 146),
    ("South-East Asia", -11, 92, 28.5, 141),
    ("Central and North Asia", 35, 45, 82, 180),
    ("North America", 14, -170, 84, -50),
    ("Latin America", -56, -120, 33, -30),
    ("Oceania", -50, 110, 0, 180),
]


def part_of(lat, lon):
    for name, a, b, c, d in PARTS:
        if a <= lat <= c and b <= lon <= d:
            return name
    return "elsewhere"


class Register:
    def __init__(self, path):
        d = json.load(gzip.open(path, "rt", encoding="utf-8"))
        self.polities = [p[0] for p in d["polities"]]
        self.timelines = d["timelines"]
        places = d["places"]
        self.cells = [(places[i] / 100.0, places[i + 1] / 100.0, places[i + 2]) for i in range(0, len(places), 3)]

    def ruler(self, cell, year):
        year = min(year, LAST_RULER_YEAR)
        t = self.timelines[cell[2]]
        for i in range(0, len(t), 3):
            if t[i + 1] <= year <= t[i + 2]:
                return self.polities[t[i]]
        return None


class People:
    """HYDE 3.2.1 people per 0.5-degree cell (the mod's hyde_density.bin.gz), nearest time slice."""

    def __init__(self, path):
        b = gzip.open(path, "rb").read()
        assert b[:4] == b"HYD1", b[:4]
        o = 4
        self.mdeg, slices = struct.unpack(">ii", b[o:o + 8])
        o += 8
        self.years = list(struct.unpack(">" + "i" * slices, b[o:o + 4 * slices]))
        o += 4 * slices
        (cells,) = struct.unpack(">i", b[o:o + 4])
        o += 4
        self.codes = {}
        for _ in range(cells):
            (idx,) = struct.unpack(">i", b[o:o + 4])
            o += 4
            self.codes[idx] = b[o:o + slices]
            o += slices

    def people(self, lat, lon, year):
        row = int(math.floor((lat + 90.0) / 0.5))
        col = int(math.floor((lon + 180.0) / 0.5))
        code = self.codes.get(row * 720 + col)
        if code is None:
            return 0.0
        s = min(range(len(self.years)), key=lambda i: abs(self.years[i] - year))
        c = code[s]
        if c == 0:
            return 0.0
        density = 10.0 ** ((c - 1) / 40.0 - 2.3)
        area = (0.5 * 110.57) * (0.5 * 111.32 * math.cos(math.radians(lat)))
        return density * area


class Table:
    def __init__(self, path):
        d = json.load(open(path, encoding="utf-8"))
        self.monies = {m["id"]: m for m in d["currencies"]}
        rows = list(enumerate(d["rows"]))
        rows.sort(key=lambda ir: (-ir[1].get("priority", 0), ir[0]))
        self.rows = [r for _, r in rows]

    def at(self, lat, lon, year, ruler_of):
        memo = {}

        def ruler(y):
            if y not in memo:
                memo[y] = ruler_of(y)
            return memo[y]

        for r in self.rows:
            if year < r["from"] or year > r["to"]:
                continue
            for w in r["where"]:
                b = w.get("box")
                if b is not None and not (b[0] <= lat <= b[2] and b[1] <= lon <= b[3]):
                    continue
                if "ruler" in w and ruler(year) not in w["ruler"]:
                    continue
                if "rulerIn" in w and ruler(w["rulerIn"]) not in w["names"]:
                    continue
                if w.get("world") or b is not None or "ruler" in w or "rulerIn" in w:
                    return r
        return None


def classify(table, row):
    if row is None:
        return "barter"
    kind = table.monies[row["money"]]["kind"]
    if kind == "barter":
        return "barter"
    if kind == "local":
        return "placeholder"
    return "named"


def main():
    step = 4
    write = "--json" in sys.argv
    for a in sys.argv[1:]:
        if a.startswith("--step="):
            step = int(a.split("=")[1])
    reg = Register(RULERS)
    table = Table(MONEY)
    folk = People(HYDE)
    by_year_people = collections.OrderedDict()
    cells = reg.cells[::step]
    by_year = collections.OrderedDict()
    by_part = collections.defaultdict(collections.Counter)
    groups = collections.Counter()
    monies_seen = collections.Counter()
    for year in YEARS:
        c = collections.Counter()
        cp = collections.Counter()
        for cell in cells:
            lat, lon = cell[0], cell[1]
            row = table.at(lat, lon, year, lambda y, cell=cell: reg.ruler(cell, y))
            k = classify(table, row)
            c[k] += 1
            cp[k] += folk.people(lat, lon, year)
            by_part[part_of(lat, lon)][k] += 1
            if row is not None:
                monies_seen[row["money"]] += 1
            if k == "placeholder":
                century = (year // 100) * 100
                groups[(reg.ruler(cell, year) or "(nobody)", century, part_of(lat, lon))] += 1
        by_year[year] = c
        by_year_people[year] = cp
    total = sum(sum(c.values()) for c in by_year.values())
    named = sum(c["named"] for c in by_year.values())
    barter = sum(c["barter"] for c in by_year.values())
    ph = sum(c["placeholder"] for c in by_year.values())
    print(f"{len(cells)} land cells x {len(YEARS)} years = {total} answers: named {named} ({100 * named / total:.1f}%),"
          f" barter {barter} ({100 * barter / total:.1f}%), placeholder {ph} ({100 * ph / total:.1f}%)")
    tp = sum(sum(c.values()) for c in by_year_people.values())
    pn = sum(c["named"] for c in by_year_people.values())
    pp = sum(c["placeholder"] for c in by_year_people.values())
    print(f"by people (HYDE, all years together): named {100 * pn / tp:.1f}%, barter"
          f" {100 * (tp - pn - pp) / tp:.1f}%, placeholder {100 * pp / tp:.1f}%")
    print("by year: cells named / barter / placeholder | share of people named / barter / placeholder:")
    for y, c in by_year.items():
        q = by_year_people[y]
        t = sum(q.values()) or 1.0
        print(f"  {y:>6}: {c['named']:>6} {c['barter']:>6} {c['placeholder']:>6} | {100 * q['named'] / t:5.1f}%"
              f" {100 * q['barter'] / t:5.1f}% {100 * q['placeholder'] / t:5.1f}%")
    print("by part of the world (named / barter / placeholder):")
    for p, c in sorted(by_part.items()):
        t = sum(c.values())
        print(f"  {p:<28} {c['named']:>6} {c['barter']:>6} {c['placeholder']:>6}  ({100 * c['placeholder'] / t:.1f}% placeholder)")
    print("biggest placeholder groups (ruler, century, part):")
    for (r, cen, p), n in groups.most_common(60):
        print(f"  {n:>5}  {cen:>6}  {p:<28} {r}")
    if write:
        rep = {
            "cells": len(cells), "years": YEARS, "answers": total, "named": named, "barter": barter,
            "placeholder": ph,
            "byYear": {str(y): dict(c) for y, c in by_year.items()},
            "peopleShareByYear": {str(y): {k: round(v / (sum(q.values()) or 1.0), 4) for k, v in q.items()}
                                  for y, q in by_year_people.items()},
            "peopleShareAllYears": {"named": round(pn / tp, 4), "placeholder": round(pp / tp, 4),
                                    "barter": round((tp - pn - pp) / tp, 4)},
            "byPart": {p: dict(c) for p, c in by_part.items()},
            "placeholderGroups": [[r, cen, p, n] for (r, cen, p), n in groups.most_common(200)],
            "moniesSeen": dict(monies_seen.most_common()),
        }
        with open(REPORT, "w", encoding="utf-8") as f:
            json.dump(rep, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("wrote", REPORT)


if __name__ == "__main__":
    main()
