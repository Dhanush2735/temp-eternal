#!/usr/bin/env python3
"""Step 37 (C29): turn `beliefs_table.py` into `beliefs.json.gz`.

Hand-written and sourced, on the discipline of step 36's disaster supplement: no source, no row.

Usage:  python3 build_beliefs.py [--out PATH] [--selftest]
"""
import argparse
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from beliefs_table import (BELIEFS, EDUCATED, EVERYONE, SCHOLARS)  # noqa: E402

DEFAULT_OUT = os.path.join(
    HERE, "..", "eternal", "src", "main", "resources",
    "data", "eternalengine", "eternal", "history", "beliefs.json.gz")

TITLE = ("What people knew or believed, by era and place: hand-written, every row sourced to "
         "Wikipedia, 3000 BCE to the present")


def build(rows):
    out = [r.as_dict() for r in rows]
    out.sort(key=lambda r: (r["from"], r["id"]))
    return {
        "title": TITLE,
        "count": len(out),
        "note": ("Hand-written. Every row is sourced to the Wikipedia article named in its "
                 "'source' field. A row's 'now' is what a player from today would say, and is "
                 "sometimes the same as the belief: the table is about what was believed, and "
                 "sometimes what was believed was right. 'who' is EDUCATED (the learned "
                 "consensus), EVERYONE (the fields as much as the schools) or SCHOLARS (a "
                 "minority against the consensus of their own time). Empty 'boxes' means the "
                 "whole world."),
        "beliefs": out,
    }


def holds(r, lat, lon, year):
    if r.frm > year or (r.to is not None and r.to < year):
        return False
    if not r.boxes:
        return True
    return any(b[0] <= lat <= b[1] and b[2] <= lon <= b[3] for b in r.boxes)


def selftest(rows):
    problems = []
    ids = {}
    for r in rows:
        if r.id in ids:
            problems.append("duplicate id: " + r.id)
        ids[r.id] = r

    def at(lat, lon, year):
        return [r for r in rows if holds(r, lat, lon, year)]

    # the cases a player is most likely to walk into
    cases = [
        ("Hyderabad", 17.39, 78.49, 1348, "miasma"),
        ("Hyderabad", 17.39, 78.49, 1348, "three_doshas"),
        ("a plague village in Europe", 48.86, 2.35, 1348, "miasma"),
        ("Paris 1348", 48.86, 2.35, 1348, "four_humours"),
        ("Paris 1348", 48.86, 2.35, 1348, "geocentrism"),
        ("Baghdad 900", 33.3, 44.4, 900, "four_humours"),
        ("Baghdad 900", 33.3, 44.4, 900, "alchemy"),
        ("Cairo 1900", 30.0, 31.2, 1900, "jinn"),
        ("Cairo 1900", 30.0, 31.2, 1900, "germ_theory"),
        ("Chang'an 800", 34.3, 108.9, 800, "mandate_of_heaven"),
        ("London 1650", 51.5, -0.13, 1650, "young_earth"),
        ("London 1700", 51.5, -0.13, 1700, "witchcraft_europe"),
        ("London 1900", 51.5, -0.13, 1900, "aether"),
        ("London 1970", 51.5, -0.13, 1970, "plate_tectonics"),
        ("London 1970", 51.5, -0.13, 1970, "ulcer_stress"),
        ("Delhi 500", 28.6, 77.2, 500, "rotating_earth_india"),
        ("Cusco 1400", -13.5, -72.0, 1400, "miasma"),
        ("Tenochtitlan 1400", 19.4, -99.1, 1400, "astrology"),
        ("Timbuktu 1400", 16.8, -3.0, 1400, "bloodletting"),
        ("Chang'an 800", 34.3, 108.9, 800, "wuxing"),
    ]
    for label, lat, lon, year, want in cases:
        got = [r.id for r in at(lat, lon, year)]
        if want not in got:
            problems.append("%s %d: wanted %s, got %s" % (label, year, want, got or "nothing"))

    # the two exclusions: a Chinese emperor's village is not Indian, and 1970 is not 1600
    if any(r.id == "five_elements_india" for r in at(34.3, 108.9, 800)):
        problems.append("five_elements_india should not reach China")
    if any(r.id == "phlogiston" for r in at(51.5, -0.13, 1900)):
        problems.append("phlogiston should be over by 1900")
    if any(r.id == "witchcraft_europe" for r in at(51.5, -0.13, 1900)):
        problems.append("the witch trials should be over by 1900")

    # every inhabited continent must have something to say in every era the mod covers
    spots = [(48.86, 2.35), (33.3, 44.4), (28.6, 77.2), (34.3, 108.9), (16.8, -3.0),
             (-13.5, -72.0), (30.0, 31.2), (35.0, 135.8)]
    for lat, lon in spots:
        for year in (-500, 1, 500, 1000, 1500, 1700, 1900, 2000):
            if not at(lat, lon, year):
                problems.append("nothing believed at all at (%.1f, %.1f) in %d" % (lat, lon, year))

    print("selftest: %d beliefs, %d cases" % (len(rows), len(cases)))
    for p in problems:
        print("  PROBLEM: " + p)
    return not problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    ok = selftest(BELIEFS)
    doc = build(BELIEFS)
    out = os.path.abspath(a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    blob = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    # mtime=0: the same data must give the same bytes. gzip.open() stamps the current time into the
    # header, so a rebuild of unchanged data changed the file's SHA-256 and /ee check all reported
    # "history/beliefs.json.gz: different content" after every run of probe_calendars.sh.
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(out, "wb"), compresslevel=9, mtime=0) as fh:
        fh.write(blob)

    who = {}
    for r in doc["beliefs"]:
        who[r["who"]] = who.get(r["who"], 0) + 1
    print("wrote %s" % out)
    print("  %d beliefs, %d bytes raw, %d gzipped" % (doc["count"], len(blob),
                                                      os.path.getsize(out)))
    print("  held by: " + ", ".join("%s %d" % kv for kv in sorted(who.items())))
    print("  still held somewhere today: %d"
          % sum(1 for r in doc["beliefs"] if r["to"] is None))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
