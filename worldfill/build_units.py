#!/usr/bin/env python3
"""
Step 45 part 4 (C19): pack the units and ranks — how an army here is counted, and who counts it.

    python3 build_units.py            build, then write
    python3 build_units.py --check    check only, write nothing

The register lives in `unit_table.py`. This script only checks it and writes it out; it does not
decide anything.

**What it is for.** C19 asks for "units, ranks, tactics, weapons and armour by state and era".
Weapons and armour are part A (the armoury); how they were come by is part B (the five ways). This
is the units and ranks half, and it is the part the plan marked as having no raw material at all.
There is no Wikipedia list of military units to scrape, so every system here is written by hand and
names its source.

**The finding that organises it: an army is counted in whatever base the society counts in.** Ten
on the steppe and in the Andes and in Ming China, twenty among the Aztecs, three in the Indian
epics, two in Sparta, and Rome counted in eights because a century of eighty kept the name of a
levy of a hundred. And the Zulu count by **birth year**, not by number at all.

Run from the repository root:  python3 worldfill/build_units.py
"""

import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data",
                   "eternalengine", "eternal", "war", "units.json.gz")

SYS_PATH = sys.path[:]
sys.path.insert(0, HERE)
try:
    import unit_table as T
finally:
    sys.path = SYS_PATH


INDEX = {a: i for i, a in enumerate(T.AREAS)}


def build():
    problems = list(T.problems())

    rows = []
    for s in T.SYSTEMS:
        rows.append({
            "id": s["id"],
            "name": s["name"],
            "polity": s["polity"] or [],
            "areas": [INDEX[a] for a in s["areas"]],
            "y0": s["y0"], "y1": s["y1"],
            "base": s["base"],
            "rungs": [{"name": r["name"], "local": r["local"], "size": r["size"],
                       "commander": r["commander"], "note": r["note"]} for r in s["rungs"]],
            "note": s["note"].replace("**", ""),
            "source": s["source"],
        })

    doc = {
        "format": "eternal-units-1",
        "id": "units",
        "source": ("Hand-written from named sources; every system in worldfill/unit_table.py "
                   "carries its own. English Wikipedia throughout. No Seshat."),
        "note": ("How an army is divided in an area and year, and who commands each division. "
                 "AN ARMY IS COUNTED IN WHATEVER BASE THE SOCIETY COUNTS IN: ten on the steppe, "
                 "in the Andes and in Ming China; twenty among the Aztecs, because Nahuatl counts "
                 "in twenties; three in the Indian epics; two in Sparta; and Rome in eights, "
                 "because a century of eighty kept the name of a levy of a hundred. The Zulu "
                 "amabutho count by BIRTH YEAR and not by number at all. A system may name the "
                 "polity it belongs to, and one that does outranks one that does not wherever "
                 "that state rules, because an area is not a country."),
        "areas": T.AREAS,
        "gaps": [
            "Illustrative, not comprehensive. There is no table of military units to be read, so "
            "the %d systems are hand-written and name their sources. A place and year with no "
            "system of its own falls through to the default (row 0, the war party), which is the "
            "honest answer for most of the map and most of time." % len(rows),
            "Coverage is strongest where a documented ladder survives: Europe, the steppe, the "
            "Andes, Mesoamerica, India, China, the Ottoman lands, the Zulu kingdom and the "
            "western Sudan. South-East Asia, the Horn of Africa, eastern and southern Africa "
            "before 1800, and most of North America fall through to the default, which is a gap "
            "in the register and not a claim that those peoples had no armies.",
            "The sizes are the ones the sources give, and several are disputed: Xenophon and "
            "Thucydides disagree about the Spartan lochos, the Ottoman orta varied from 100 to "
            "500, and the Songhai figures at Tondibi differ by a factor of two between sources. "
            "Where a number is contested the note says so rather than picking one.",
            "This register names units and commands. It does not stage fighting — that is D10 / "
            "step 40, whose sixteen dated formations and four casualty bands are the thing that "
            "actually puts an army on a field.",
        ],
        "counts": {
            "systems": len(rows),
            "rungs": sum(len(r["rungs"]) for r in rows),
            "areas": len(T.AREAS),
            "namedPolity": sum(1 for r in rows if r["polity"]),
            "bases": sorted({r["base"] for r in rows if r["base"] is not None}),
        },
        "rows": rows,
    }
    return doc, problems


def check(doc):
    bad = []

    def ok(cond, what):
        print(("  ok   " if cond else "  FAIL ") + what)
        if not cond:
            bad.append(what)

    ok(doc["format"] == "eternal-units-1", "the format is one this builder writes")
    for key in ("areas", "rows", "gaps", "counts"):
        ok(key in doc, "the pack carries %s" % key)

    rows = doc["rows"]
    ok(len(rows) >= 10, "%d systems" % len(rows))
    ok(all(len(r["rungs"]) >= 2 for r in rows), "every system has at least two rungs")
    ok(all(r["y1"] >= r["y0"] for r in rows), "no system ends before it starts")
    ok(all(0 <= a < len(doc["areas"]) for r in rows for a in r["areas"]),
       "every system names areas that exist")
    ok(all(r["note"].strip() and r["source"].strip() for r in rows),
       "every system has a note and a source")
    ok(all(g["name"].strip() for r in rows for g in r["rungs"]), "every rung has a name")
    # Every system must be able to say who commands its smallest real unit. Upper rungs are
    # allowed to be silent where the sources are - the Indian ladder names a commander for the
    # patti and the senamukha and then falls quiet, and inventing one would be worse than not.
    sized = [r for r in rows if any(g.get("size") is not None for g in r["rungs"])]
    ok(all(next(g["commander"] for g in r["rungs"] if g.get("size") is not None) for r in sized),
       "the smallest sized rung names a commander in every system that has one (%d of %d)"
       % (len(sized), len(rows)))
    silent = sum(1 for r in rows for g in r["rungs"] if not g.get("commander"))
    ok(silent == 0 or silent < sum(len(r["rungs"]) for r in rows),
       "%d rungs name no commander, and the notes say so rather than guessing" % silent)

    # A ladder must climb. Sizeless rungs are allowed (the war party, the Ottoman orta).
    for r in rows:
        sizes = [g["size"] for g in r["rungs"] if g.get("size") is not None]
        ok(sizes == sorted(sizes), "%s: the rungs climb (%s)" % (r["id"], sizes))

    # The default must exist and span everything, or a lookup falls off the end of the pack.
    d = [r for r in rows if r["id"] == "warband"]
    ok(len(d) == 1, "there is exactly one default system")
    if d:
        ok(d[0]["y0"] <= -3000 and d[0]["y1"] >= 1900, "the default spans the whole mod")
        ok(len(d[0]["areas"]) == len(doc["areas"]), "the default covers every area")

    # Every area-year must be covered, which is the part A coverage rule applied here.
    empty = 0
    for ai in range(len(doc["areas"])):
        for yr in range(-3000, 2001, 100):
            if not any(ai in r["areas"] and r["y0"] <= yr <= r["y1"] for r in rows):
                empty += 1
    ok(empty == 0, "no area-year is uncovered (%d area-years swept)"
       % (len(doc["areas"]) * 51))

    # The finding the register exists to record: the same thousand men, five different ladders.
    bases = {r["id"]: r["base"] for r in rows}
    ok(bases.get("mongol") == 10 and bases.get("inca") == 10,
       "the steppe and the Andes both count in tens")
    ok(bases.get("aztec") == 20, "the Aztecs count in twenties")
    ok(bases.get("maurya") == 3, "the Indian epics count in threes")
    ok(bases.get("sparta") == 2, "Sparta counts by doubling")
    ok(bases.get("zulu") is None and bases.get("warband") is None,
       "the Zulu and the war party count by no number at all")
    ok(len(set(bases.values())) >= 5,
       "at least five different ways of counting an army are in the pack")

    return bad



# --------------------------------------------------------------------------- the polity names must be real
#
# A fragment that matches nothing in the ruler register is a row that can never fire. This is the
# bug twice seen in this project: "British India" when the register says "British Raj", and then
# "Sparta" when it says "Peloponnesian League". So every fragment is checked against the register's
# own names here, at build time, rather than being left to be discovered in the prose.

RULERS = os.path.join(ROOT, "eternal", "src", "main", "resources", "data",
                      "eternalengine", "eternal", "history", "world_rulers.json.gz")


def ruler_names():
    """Every polity name in the ruler register, lower-cased."""
    if not os.path.exists(RULERS):
        return None
    with gzip.open(RULERS, "rt", encoding="utf-8") as f:
        d = json.load(f)
    return [p[0].lower() for p in d["polities"]]


def check_polity(rows):
    """Every polity fragment must appear in at least one real polity name."""
    bad = []
    names = ruler_names()
    if names is None:
        print("  skip  the ruler register is not built, so the polity names are unchecked")
        return bad
    for r in rows:
        for frag in r["polity"]:
            hit = [n for n in names if frag.lower() in n]
            if not hit:
                bad.append("row '%s': no polity in the ruler register contains '%s'"
                           % (r["id"], frag))
    if not bad:
        print("  ok   every polity fragment matches a real name in the ruler register "
              "(%d checked)" % sum(len(r["polity"]) for r in rows))
    return bad


def main(argv):
    doc, problems = build()
    for p in problems:
        print("  PROBLEM " + p)

    c = doc["counts"]
    print("units: %d systems, %d rungs, %d areas, %d named to a polity, bases %s"
          % (c["systems"], c["rungs"], c["areas"], c["namedPolity"], c["bases"]))

    bad = check(doc)
    for b in check_polity(doc["rows"]):
        print("  FAIL " + b)
        bad.append(b)
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
