#!/usr/bin/env python3
"""Step 37 (A2): turn `calendars_table.py` into `calendars.json.gz`.

The arithmetic lives in `Calendars.java`; this is the one fact arithmetic cannot supply, which is
**which calendar the people in a place were using**. It is a hand table, on the pattern of step
35's `water_changes_table.py` and step 36's `disaster_supplement.py`.

Usage:  python3 build_calendars.py [--out PATH] [--selftest]
"""
import argparse
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from calendars_table import REGIONS  # noqa: E402

DEFAULT_OUT = os.path.join(
    HERE, "..", "eternal", "src", "main", "resources",
    "data", "eternalengine", "eternal", "history", "calendars.json.gz")

TITLE = ("Which calendar a place wrote its dates in, and when: hand-written, sourced to "
         "Wikipedia, covering 3000 BCE to the present")


def build(regions):
    rows = [r.as_dict() for r in regions]
    rows.sort(key=lambda r: (r["from"], r["name"]))
    return {
        "title": TITLE,
        "count": len(rows),
        "note": ("Hand-written. Every row is sourced to the Wikipedia article named in its "
                 "'source' field. Boxes may overlap: the first matching row gives the primary "
                 "calendar and every matching row contributes to the list, because a place can "
                 "use several at once — Hyderabad in 1948 is dated Fasli 1357, 1367 AH and "
                 "2005 VS on the same morning."),
        "regions": rows,
    }


def selftest(regions):
    problems = []
    names = {}
    for r in regions:
        if r.name in names:
            problems.append("duplicate name: " + r.name)
        names[r.name] = r
        if r.to is not None and r.to < r.frm:
            problems.append("ends before it starts: " + r.name)

    def lookup(lat, lon, year):
        out = []
        for r in regions:
            if r.lat0 <= lat <= r.lat1 and r.lon0 <= lon <= r.lon1 \
                    and r.frm <= year and (r.to is None or year <= r.to):
                for c in r.calendars:
                    if c not in out:
                        out.append(c)
        return out

    # the cases that matter, and the ones a player is most likely to hit
    cases = [
        ("Rome", 41.9, 12.5, 1500, "julian"),
        ("Rome", 41.9, 12.5, 1700, "gregorian"),
        ("London", 51.5, -0.1, 1700, "julian"),
        ("London", 51.5, -0.1, 1800, "gregorian"),
        ("Moscow", 55.75, 37.6, 1900, "julian"),
        ("Moscow", 55.75, 37.6, 1930, "gregorian"),
        ("Cairo", 30.0, 31.2, 1300, "hijri"),
        ("Cairo", 30.0, 31.2, 1950, "gregorian"),
        ("Baghdad", 33.3, 44.4, 900, "hijri"),
        ("Delhi", 28.6, 77.2, 1700, "vikram"),
        ("Delhi", 28.6, 77.2, 1900, "gregorian"),
        ("Hyderabad (Deccan)", 17.39, 78.49, 1948, "fasli"),
        ("Hyderabad (Deccan)", 17.39, 78.49, 1948, "hijri"),
        ("Beijing", 39.9, 116.4, 1700, "chinese"),
        ("Beijing", 39.9, 116.4, 1950, "gregorian"),
        ("Kyoto", 35.0, 135.8, 1700, "chinese"),
        ("Cusco", -13.5, -72.0, 1400, "gregorian"),   # not modelled; the note says so
        ("Timbuktu", 16.8, -3.0, 1500, "hijri"),   # a Muslim scholarly city; dated by the Hijri year
        ("Benin", 6.3, 5.6, 1500, "gregorian"),     # not modelled; the note says so
    ]
    for label, lat, lon, year, want in cases:
        got = lookup(lat, lon, year)
        if want not in got:
            problems.append("%s %d: wanted %s, got %s" % (label, year, want, got or "nothing"))

    # every inhabited continent must be covered by something
    spots = [(48.8, 2.3), (-13.5, -72.0), (6.5, 3.4), (35.0, 135.8), (28.6, 77.2),
             (30.0, 31.2), (-33.9, 151.2), (55.75, 37.6), (19.4, -99.1), (16.8, -3.0)]
    for lat, lon in spots:
        if not lookup(lat, lon, 1500):
            problems.append("no calendar at all for (%.1f, %.1f) in 1500" % (lat, lon))

    print("selftest: %d regions, %d test cases" % (len(regions), len(cases)))
    for p in problems:
        print("  PROBLEM: " + p)
    return not problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return 0 if selftest(REGIONS) else 1

    ok = selftest(REGIONS)
    doc = build(REGIONS)
    out = os.path.abspath(a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    blob = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    # mtime=0: the same data must give the same bytes. gzip.open() stamps the current time into the
    # header, so a rebuild of unchanged data changed the file's SHA-256 and /ee check all reported
    # "history/beliefs.json.gz: different content" after every run of probe_calendars.sh.
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(out, "wb"), compresslevel=9, mtime=0) as fh:
        fh.write(blob)

    counts = {}
    for r in doc["regions"]:
        for c in r["calendars"]:
            counts[c] = counts.get(c, 0) + 1
    print("wrote %s" % out)
    print("  %d regions, %d bytes raw, %d gzipped" % (doc["count"], len(blob),
                                                      os.path.getsize(out)))
    print("  calendars: " + ", ".join("%s %d" % kv for kv in sorted(counts.items())))
    print("  rows admitting they are not modelled: %d"
          % sum(1 for r in doc["regions"] if "Not modelled" in r.get("note", "")))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
