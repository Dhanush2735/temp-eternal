#!/usr/bin/env python3
"""Step 36 (B27): turn `disaster_supplement.py` into `disaster_supplement.json.gz`.

This is the small half of B27's data. The bulk is `events_hazards.json.gz`, 26,997 scraped
hazards; this is the 63 or so great disasters that scrape missed, written by hand and sourced
one row at a time. `Disasters` reads both and marks the hand ones so a caller can tell them
apart.

Usage:  python3 build_disasters.py [--out PATH] [--selftest]
"""
import argparse
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from disaster_supplement import EVENTS  # noqa: E402

DEFAULT_OUT = os.path.join(
    HERE, "..", "eternal", "src", "main", "resources",
    "data", "eternalengine", "eternal", "history", "disaster_supplement.json.gz")

def title(n):
    return ("The great disasters: %d events, 1600 BCE to AD 2023, written by hand and sourced to "
            "Wikipedia, because the scraped hazards pack misses them" % n)


def build(events):
    rows = []
    for i, e in enumerate(events):
        d = e.as_dict()
        d["id"] = "hand_%02d" % i
        rows.append(d)
    rows.sort(key=lambda r: (r["start"], r["name"]))
    return {
        "title": title(len(rows)),
        "count": len(rows),
        "note": ("Hand-written. Every row is sourced to the Wikipedia article named in its "
                 "'source' field. These are the great disasters absent from "
                 "events_hazards.json.gz, or present in it with a year or radius that is wrong."),
        "events": rows,
    }


def selftest(events):
    """The table is hand-written, so it is the part most likely to be quietly wrong."""
    problems = []
    seen = {}
    for e in events:
        if e.name in seen:
            problems.append("duplicate name: " + e.name)
        seen[e.name] = e
        if e.end is not None and e.end < e.year:
            problems.append("ends before it starts: " + e.name)
        if e.kind == "earthquake" and e.mag is not None and not (4.0 <= e.mag <= 9.6):
            problems.append("implausible magnitude: %s (%.1f)" % (e.name, e.mag))
        if e.kind == "volcano" and e.mag is not None and not (0 <= e.mag <= 8):
            problems.append("implausible VEI: %s (%.1f)" % (e.name, e.mag))
        if e.dead is not None and (e.dead < 0 or e.dead > 60_000_000):
            problems.append("implausible dead: %s (%d)" % (e.name, e.dead))
        if e.radius <= 0:
            problems.append("needs a radius: " + e.name)
        if e.radius > 16000:
            problems.append("radius beyond the far side of the Earth: " + e.name)
        if e.sev is not None and not (0.0 <= e.sev <= 1.0):
            problems.append("severity out of range: " + e.name)

    # coverage: the point of the table is that it is not one place or one era
    lats = [e.lat for e in events]
    lons = [e.lon for e in events]
    years = [e.year for e in events]
    hemis = {("north" if a >= 0 else "south") for a in lats}
    if len(hemis) < 2:
        problems.append("every event is in one hemisphere")
    continents = set()
    for e in events:
        lon, lat = e.lon, e.lat
        if -125 <= lon <= -35:
            continents.add("Americas")
        elif -25 <= lon <= 45 and 35 <= lat <= 72:
            continents.add("Europe")
        elif -20 <= lon <= 52 and lat < 37:
            continents.add("Africa")
        elif lon > 45 and lat < -10:
            continents.add("Oceania")
        elif lon > 45:
            continents.add("Asia")
        else:
            continents.add("Atlantic")
    for c in ("Americas", "Europe", "Africa", "Asia", "Oceania"):
        if c not in continents:
            problems.append("no events in " + c)
    millennia = {(y // 1000) for y in years}
    for m in (-2, -1, 0, 1, 2):
        if m not in millennia:
            problems.append("no events in the millennium beginning %d" % (m * 1000))

    print("selftest: %d events, %d continents, %d millennia, %d hemispheres"
          % (len(events), len(continents), len(millennia), len(hemis)))
    for p in problems:
        print("  PROBLEM: " + p)
    return not problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return 0 if selftest(EVENTS) else 1

    ok = selftest(EVENTS)
    doc = build(EVENTS)
    out = os.path.abspath(a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    blob = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(out, "wb"), compresslevel=9, mtime=0) as fh:
        fh.write(blob)

    kinds = {}
    for r in doc["events"]:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    print("wrote %s" % out)
    print("  %d events, %d bytes raw, %d gzipped" % (doc["count"], len(blob),
                                                     os.path.getsize(out)))
    print("  kinds: " + ", ".join("%s %d" % kv for kv in sorted(kinds.items())))
    print("  continental or wider (radius > 2000 km): %d" % sum(1 for r in doc["events"] if r["radiusKm"] > 2000))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
