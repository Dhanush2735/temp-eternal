#!/usr/bin/env python3
"""
Step 45 part 3 (E9 B): pack the five ways a weapon gets into a man's hand.

    python3 build_arms.py            build, then write
    python3 build_arms.py --check    check only, write nothing

The register lives in `arms_ways_table.py`. This script only checks it and writes it out; it does
not decide anything.

**What is in the pack and what is not.** The weapon LAWS are not here — they are kind 5 of
`history/law.json.gz`, built by `build_law.py` from `weapon_law_table.py`, and the two are meant to
be read together. This pack answers *how an army gets its weapons*; the law pack answers *what the
law there says about who may have one*. They are keyed differently on purpose — this one by area
and year, that one by the polity that rules the square — because the first is a fact about warfare
and the second is a fact about a state.

Run from the repository root:  python3 worldfill/build_arms.py
"""

import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data",
                   "eternalengine", "eternal", "war", "arms.json.gz")

SYS_PATH = sys.path[:]
sys.path.insert(0, HERE)
try:
    import arms_ways_table as T
finally:
    sys.path = SYS_PATH


INDEX = {a: i for i, a in enumerate(T.AREAS)}
SHAPE_INDEX = {s: i for i, s in enumerate(T.SHAPES)}


def build():
    problems = list(T.problems())

    rows = []
    for r in T.ROWS:
        rows.append({
            "id": r["id"],
            "areas": [INDEX[a] for a in r["areas"]],
            "y0": r["y0"], "y1": r["y1"],
            "shape": SHAPE_INDEX[r["shape"]],
            "flags": [int(r["flags"][f]) for f in T.FLAGS],
            "polity": r["polity"] or [],
            "for": r["forWhom"],
            "text": r["text"],
            "note": r["note"].replace("**", ""),
            "source": r["source"],
        })

    doc = {
        "format": "eternal-arms-1",
        "id": "arms",
        "source": ("Hand-written from named sources; each row in worldfill/arms_ways_table.py "
                   "carries its own. Weapon LAWS are not in this pack - they are kind 5 of "
                   "history/law.json.gz, built by build_law.py from weapon_law_table.py, and are "
                   "keyed by polity rather than by area."),
        "note": ("How a weapon reaches a hand in an area and year. Five ways - issued, bring, buy, "
                 "take, gift - plus a sixth flag, carry, which is not a way of getting one but is "
                 "the law that matters most of the time: KEEPING AND CARRYING ARE DIFFERENT LAWS "
                 "IN EVERY AGE. The Statute of Northampton 1328 never touched a man's right to own "
                 "a sword; it forbade him to walk into a market wearing one. Illustrative, not "
                 "comprehensive: a place-year with no row falls through to row 0, the default."),
        "areas": T.AREAS,
        "ways": T.WAYS,
        "flags": T.FLAGS,
        "flagMeaning": [T.FLAG_MEANING[f] for f in T.FLAGS],
        "shapes": T.SHAPES,
        "gaps": [
            "Illustrative, not comprehensive. There is no table of how armies were supplied to be "
            "read, so the %d rows are hand-written and name their sources. A place and year with "
            "no row at all falls through to the default (row 0), which is the honest answer for "
            "most of the map and most of time: you bring your own." % len(rows),
            "The rows are area- and year-granular, so they cannot say what one town or one "
            "regiment did. The weapon LAWS in history/law.json.gz are polity-granular and the two "
            "granularities do not line up exactly.",
            "The flags describe what the law allowed for the class named in 'for'. They do not "
            "describe what happened: row 'hyderabad' is the one place they are written "
            "deliberately to disagree, because a blockade is exactly the distance between the two.",
            "'carry' is about going about armed in peacetime. An army on campaign carries "
            "everywhere, and no row here is about that.",
        ],
        "counts": {
            "rows": len(rows),
            "areas": len(T.AREAS),
            "ways": len(T.WAYS),
            "rowsWithAllFiveOpen": sum(1 for r in rows if all(r["flags"][:5])),
            "rowsWithOnlyIssued": sum(1 for r in rows
                                      if r["flags"][0] and not any(r["flags"][1:])),
        },
        "rows": rows,
    }
    return doc, problems


def check(doc):
    """Everything the Java will assume about the pack, asserted here before it ships."""
    bad = []

    def ok(cond, what):
        print(("  ok   " if cond else "  FAIL ") + what)
        if not cond:
            bad.append(what)

    ok(doc["format"] == "eternal-arms-1", "the format is the one this builder writes")
    for key in ("areas", "ways", "flags", "rows", "gaps", "counts", "flagMeaning", "shapes"):
        ok(key in doc, "the pack carries %s" % key)

    rows = doc["rows"]
    ok(len(rows) >= 10, "%d rows" % len(rows))
    ok(len(doc["flags"]) == len(doc["ways"]) + 1,
       "%d flags: the five ways plus carry" % len(doc["flags"]))
    ok(len(doc["flagMeaning"]) == len(doc["flags"]), "every flag is explained")

    ok(all(len(r["flags"]) == len(doc["flags"]) for r in rows), "every row carries every flag")
    ok(all(f in (0, 1) for r in rows for f in r["flags"]), "every flag is 0 or 1")
    ok(all(r["y1"] >= r["y0"] for r in rows), "no row ends before it starts")
    ok(all(0 <= a < len(doc["areas"]) for r in rows for a in r["areas"]),
       "every row names areas that exist")
    ok(all(0 <= r["shape"] < len(doc["shapes"]) for r in rows), "every row names a shape that exists")
    ok(all(r["text"].strip() and r["note"].strip() and r["source"].strip() for r in rows),
       "every row has text, a note and a source")
    ok(any(r["polity"] for r in rows) and any(not r["polity"] for r in rows),
       "some rows name a polity and some do not (%d of %d)"
       % (sum(1 for r in rows if r["polity"]), len(rows)))
    # Japan and China are the same area with opposite laws in 1700; only a polity can tell them
    # apart, so the two rows that collide there must both carry one.
    byid = {r["id"]: r for r in rows}
    for rid in ("katanagari", "qinglate"):
        if rid in byid:
            ok(bool(byid[rid]["polity"]), "row '%s' names its polity (EAS holds two laws at once)" % rid)

    # The default must exist and must span everything, or a lookup can fall off the end of the pack.
    d = [r for r in rows if r["id"] == "own"]
    ok(len(d) == 1, "there is exactly one default row")
    if d:
        ok(d[0]["y0"] <= -3000 and d[0]["y1"] >= 1900, "the default spans the whole mod")
        ok(len(d[0]["areas"]) == len(doc["areas"]), "the default covers every area")

    # Every area-year must be covered, which is the part A coverage rule applied to this pack.
    empty = 0
    for ai in range(len(doc["areas"])):
        for yr in range(-3000, 2001, 100):
            if not any(ai in r["areas"] and r["y0"] <= yr <= r["y1"] for r in rows):
                empty += 1
    ok(empty == 0, "no area-year is uncovered (%d area-years swept)" % (len(doc["areas"]) * 51))

    # The distinction the pack exists to make.
    by = {r["id"]: r for r in rows}
    if "northampton" in by and "assize" in by:
        n, a = by["northampton"], by["assize"]
        ok(n["flags"][doc["flags"].index("carry")] == 0
           and n["flags"][doc["flags"].index("buy")] == 1,
           "under Northampton you may BUY a weapon but not CARRY it")
        ok(a["flags"][doc["flags"].index("buy")] == 1
           and a["flags"][doc["flags"].index("gift")] == 0,
           "under the 1181 Assize you may BUY one but not GIVE one away")

    return bad


def main(argv):
    doc, problems = build()
    for p in problems:
        print("  PROBLEM " + p)

    c = doc["counts"]
    print("arms: %d rows, %d areas, %d ways (+carry), %d with all five open, %d issued-only"
          % (c["rows"], c["areas"], c["ways"], c["rowsWithAllFiveOpen"], c["rowsWithOnlyIssued"]))

    bad = check(doc)
    if problems or bad or "--check" in argv:
        return 1 if (problems or bad) else 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    # mtime=0 so the same register always produces the same bytes: what ships is reproducible
    with gzip.GzipFile(OUT, "wb", mtime=0) as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    print("  wrote %s (%d bytes)" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
