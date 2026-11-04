#!/usr/bin/env python3
"""Step 35, part 4 (B2): pack the written table of the water that moved.

`water_changes_table.py` holds the table itself, written by hand from the historical record. This
script checks it and writes it into the mod as `history/water_changes.json.gz`, so that the
register can answer "was this water here in this year?" for a river that moved, a sea that went,
a marsh that was drained.

    python3 build_water_changes.py              build the pack
    python3 build_water_changes.py --check      check the table and the pack
    python3 build_water_changes.py --places     what the water was doing at the test places

File layout (history/water_changes.json.gz, gzip):
  {"format": "eternalengine/water_changes@1", "about": ..., "source": ...,
   "kinds": {kind: what it is}, "changes_vocabulary": {code: what it means},
   "count": N,
   "changes": [[name, kind, lat*1000, lon*1000, radiusKm, year, endYear or null,
                change, note, "recorded" or "estimated"], ...]}

Radius in kilometres is how wide a thing the change was: a river's avulsion counts in hundreds,
a harbour silting up in tens. The register uses it to decide whether a change is close enough to
the place being asked about to be the answer.
"""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modpack as M                                   # noqa: E402
from water_changes_table import CHANGES               # noqa: E402

OUT = os.path.join(M.HISTORY, "water_changes.json.gz")
FORMAT = "eternalengine/water_changes@1"

KINDS = {
    "river": "a river, its bed or its mouth",
    "coast": "a shore, where the land meets the sea",
    "delta": "the land a river has built into the sea",
    "lake": "a lake, standing water in a basin",
    "sea": "a sea, or a part of one",
    "marsh": "a marsh, a swamp, a fen, a wetland",
    "strait": "a strait or a crossing",
    "canal": "a canal cut by people",
    "works": "a dam, a dike or a barrage",
}

VOCABULARY = {
    "course": "the river took a new bed",
    "dried": "the water went away entirely",
    "shrank": "the water drew back, but did not go",
    "flooded": "land became water",
    "drained": "people let the water out",
    "dammed": "a river was stopped and a lake made behind it",
    "advanced": "the land grew out into the water",
    "retreated": "the water came back over the land",
    "reclaimed": "the water was made into land by people",
    "diverted": "the river's water was taken somewhere else",
    "silted": "a channel or a harbour filled up",
    "closed": "a strait, a bay or an arm of the sea was cut off",
    "breached": "a dam, a dike or a bank gave way",
    "rose": "the level went up",
    "subsided": "the land sank under the water",
    "opened": "a new channel or canal was cut, and water put through it",
}

CERTAINTY = ("recorded", "estimated")
YEAR_MIN, YEAR_MAX = -11000, 2030


def validate():
    """Every row of the table, checked. Returns a list of problems."""
    bad = []
    seen = set()
    for i, row in enumerate(CHANGES):
        if len(row) != 10:
            bad.append("row %d: %d fields, not 10" % (i, len(row)))
            continue
        name, kind, lat, lon, radius, year, end, change, note, cert = row
        where = "row %d (%s)" % (i, name)
        if kind not in KINDS:
            bad.append("%s: kind %r is not one of %s" % (where, kind, sorted(KINDS)))
        if change not in VOCABULARY:
            bad.append("%s: change %r is not one of %s" % (where, change, sorted(VOCABULARY)))
        if not (-90.0 <= lat <= 90.0):
            bad.append("%s: latitude %s out of range" % (where, lat))
        if not (-180.0 <= lon <= 180.0):
            bad.append("%s: longitude %s out of range" % (where, lon))
        if not (radius > 0):
            bad.append("%s: radius %s must be more than nothing" % (where, radius))
        if not (YEAR_MIN <= year <= YEAR_MAX):
            bad.append("%s: year %s outside %d..%d" % (where, year, YEAR_MIN, YEAR_MAX))
        if end is not None and end <= year:
            bad.append("%s: end year %s is not after %s" % (where, end, year))
        if cert not in CERTAINTY:
            bad.append("%s: certainty %r must be one of %s" % (where, cert, list(CERTAINTY)))
        if not note.strip():
            bad.append("%s: no note" % where)
        key = (name, year)
        if key in seen:
            bad.append("%s: the same change twice" % where)
        seen.add(key)
    return bad


def rows():
    out = []
    for name, kind, lat, lon, radius, year, end, change, note, cert in CHANGES:
        out.append([name, kind, round(lat * 1000), round(lon * 1000), radius, year, end,
                    change, note, cert])
    return out


def build():
    bad = validate()
    if bad:
        for b in bad:
            print("  " + b)
        print("\n  %d problems in the table; nothing written" % len(bad))
        return 1
    r = rows()
    pack = {
        "format": FORMAT,
        "about": ("What the water did, by year: rivers that changed course, coasts and deltas "
                  "that grew or were eaten back, seas and lakes that dried or were made, marshes "
                  "drained, straits opened and shut. Written by hand, because there is no data "
                  "set for it: nobody publishes the shape of the Zuiderzee in 1500. Every row "
                  "carries the year, the place, how wide a thing it was, and whether the year is "
                  "recorded or estimated. The last rows are the changes that were already done "
                  "before the world begins in 3000 BCE; they are there so that the register can "
                  "say what the world started with, not as things a player will see happen."),
        "source": ("Written from the historical record for the Eternal Engine mod, 2026: "
                   "Wikipedia and Britannica for the Yellow River's courses, the Zuiderzee and "
                   "the Dutch works, the Aral Sea, the Caspian, Ghaggar-Hakra, the Kosi and the "
                   "Rann of Kutch; the rest from the standard histories of each place. Every "
                   "year marked recorded has a date in the record; every year marked estimated "
                   "is a range or an inference, and is meant to be read as one."),
        "kinds": KINDS,
        "changes_vocabulary": VOCABULARY,
        "count": len(r),
        "changes": r,
    }
    raw = json.dumps(pack, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.GzipFile(OUT, "wb", compresslevel=9, mtime=0) as f:
        f.write(raw)
    print("  %d changes, %d bytes raw, %d gzipped" % (len(r), len(raw), os.path.getsize(OUT)))
    print("  written: %s" % OUT)
    return 0


def report():
    from collections import Counter
    by_kind = Counter(c[1] for c in CHANGES)
    by_change = Counter(c[7] for c in CHANGES)
    by_cert = Counter(c[9] for c in CHANGES)
    print("  %d changes" % len(CHANGES))
    print("  what moved")
    for k, v in by_kind.most_common():
        print("    %-8s %4d   %s" % (k, v, KINDS[k]))
    print("  what happened")
    for k, v in by_change.most_common():
        print("    %-11s %4d   %s" % (k, v, VOCABULARY[k]))
    print("  how sure")
    for k, v in by_cert.most_common():
        print("    %-10s %4d" % (k, v))
    in_world = [c for c in CHANGES if c[5] >= -3000]
    print("  inside the world's span (3000 BCE onwards): %d of %d" % (len(in_world), len(CHANGES)))
    print("  before it begins: %d" % (len(CHANGES) - len(in_world)))
    for era in ((-3000, -1000), (-1000, 1), (1, 1000), (1000, 1500), (1500, 1800),
                (1800, 1900), (1900, 2000), (2000, 2030)):
        n = sum(1 for c in in_world if era[0] <= c[5] < era[1])
        print("    %6d..%-6d %4d" % (era[0], era[1], n))
    return 0


def places():
    from fetch_town_wd import TEST_PLACES
    from math import radians, sin, cos, asin, sqrt

    def km(lat1, lon1, lat2, lon2):
        p1, p2 = radians(lat1), radians(lat2)
        dp, dl = radians(lat2 - lat1), radians(lon2 - lon1)
        h = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
        return 2 * 6371 * asin(min(1, sqrt(h)))

    ok = 0
    for name, lat, lon, yr in TEST_PLACES:
        hits = []
        for c in CHANGES:
            d = km(lat, lon, c[2], c[3])
            if d > c[4]:
                continue
            if c[5] > yr:
                continue
            if c[6] is not None and c[6] < yr:
                continue          # it was undone before the year asked about
            hits.append((c[5], d, c))
        hits.sort(key=lambda t: -t[0])
        if hits:
            ok += 1
            _, d, c = hits[0]
            print("%-16s %6d  %5.0f km  %s: %s (%s, %s)" %
                  (name, yr, d, c[1], c[0], VOCABULARY[c[7]], c[9]))
        else:
            print("%-16s %6d  nothing recorded" % (name, yr))
    print("\n  %d of %d test places have a water change standing in their year" %
          (ok, len(TEST_PLACES)))
    return 0


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else ""
    if a == "--places":
        sys.exit(places())
    if a == "--check":
        bad = validate()
        for b in bad:
            print("  " + b)
        print("  %d problems" % len(bad))
        sys.exit(report() if not bad else 1)
    sys.exit(build())
