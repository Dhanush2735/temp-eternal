#!/usr/bin/env python3
"""
Step 47 part 3 (E8, E22): pack the anachronisms and the two settings.

    python3 build_anachronisms.py            build, then write
    python3 build_anachronisms.py --check    check only, write nothing
"""

import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data",
                   "eternalengine", "eternal", "economy", "anachronisms.json.gz")

sys.path.insert(0, HERE)
try:
    import anachronism_table as A
finally:
    sys.path.pop(0)


def build():
    problems = list(A.problems())
    rows = [{
        "id": r["id"],
        "kind": r["kind"],
        "action": r["action"],
        "year": r["year"],
        "asWhat": r["myth"],
        "note": r["note"],
        "source": r["source"],
    } for r in A.ROWS]
    doc = {
        "format": "eternal-anachronisms-1",
        "id": "anachronisms",
        "source": ("Alchemy from Principe's The Secrets of Alchemy; pharmacy from Totelin; the "
                   "diamond from Pliny and the standard history; the Pharos; the myth cycles named "
                   "in each row; vanilla for the items themselves. The dates that are real are the "
                   "only dates claimed, and most of these rows have no date because the thing has "
                   "no history."),
        "note": ("Step 47 part 3 (E8 and E22): vanilla things that do not belong, and what a year "
                 "may use. **THE DISTINCTION THE PACK IS BUILT ON: Minecraft contains three kinds "
                 "of impossible thing and they need three answers.** `real` - a real thing existed "
                 "and the game's version is better: allowed from its year. `myth` - people believed "
                 "in it, so it existed as a belief and not as a function: allowed and RENAMED, "
                 "because the object is real and the power is not. `never` - nothing like it has "
                 "ever existed at any date: locked in a strict world, allowed for a time traveller. "
                 "Treating all of it as fantasy to remove would delete the game; treating all of it "
                 "as allowed would make the year meaningless."),
        "finding": ("**The middle kind is the one worth having, and it is what turns the register "
                    "from a blacklist into a translation.** Alchemy is real history: it runs from "
                    "Hellenistic Egypt through the Islamic world to Newton, who wrote more on "
                    "alchemy than on physics, and it gave us distillation and the mineral acids. So "
                    "a brewing stand in 1300 is not an anachronism, it is an alchemist's bench, and "
                    "the register renames it rather than deleting it. The same is true of the "
                    "enchanting table, which is a shrine, and the diamond, which is a gem that was "
                    "traded from India to Rome and that nobody ever made a sword of. **Six of the "
                    "19 rows are renamed and 10 are locked**, which is the right proportion: the "
                    "game's magic is mostly belief and only sometimes nothing at all."),
        "settings": [{"id": k, "note": v} for k, v in A.SETTINGS.items()],
        "rows": rows,
        "counts": {
            "rows": len(rows),
            "real": sum(1 for r in rows if r["kind"] == "real"),
            "myth": sum(1 for r in rows if r["kind"] == "myth"),
            "never": sum(1 for r in rows if r["kind"] == "never"),
            "allowed": sum(1 for r in rows if r["action"] == "allow"),
            "renamed": sum(1 for r in rows if r["action"] == "rename"),
            "locked": sum(1 for r in rows if r["action"] == "lock"),
        },
    }
    return doc, problems


def check(doc):
    bad = []

    def ok(cond, what):
        print(("  ok   " if cond else "  FAIL ") + what)
        if not cond:
            bad.append(what)

    c = doc["counts"]
    ok(doc["format"] == "eternal-anachronisms-1", "the format is the one this builder writes")
    ok(c["rows"] >= 18, "%d rows" % c["rows"])
    ok(c["real"] >= 2 and c["myth"] >= 3 and c["never"] >= 5,
       "all three kinds are represented: %d real, %d myth, %d never"
       % (c["real"], c["myth"], c["never"]))
    ok(c["renamed"] >= 5, "%d rows are renamed rather than deleted" % c["renamed"])
    ok(c["locked"] >= 8, "%d are locked" % c["locked"])

    # THE INVARIANTS, checked in the pack rather than only in the table.
    for r in doc["rows"]:
        if r["kind"] == "never":
            ok(r["year"] is None, r["id"] + " never existed and claims no year")
            ok(r["action"] == "lock", r["id"] + " never existed and is locked")
        else:
            ok(r["year"] is not None, r["id"] + " is " + r["kind"] + " and has a year")
        if r["action"] == "rename":
            ok(bool(r["asWhat"]), r["id"] + " is renamed to something and names it")

    # The one the game got right by accident.
    gold = next(r for r in doc["rows"] if r["id"] == "minecraft:golden_sword")
    ok(gold["action"] == "allow", "the golden sword is allowed, being useless in reality too")
    ok("worse than iron" in gold["note"], "and the row says why")

    # The diamond is a gem before it is a tool, and the note must say so.
    dia = next(r for r in doc["rows"] if r["id"] == "minecraft:diamond")
    ok(dia["year"] == -300, "the diamond is allowed from 300 BC, as a traded gem")
    ok("nobody made a tool" in dia["note"].replace("nobody made a tool of one",
                                                   "nobody made a tool"),
       "and the row refuses the diamond pickaxe")

    # Alchemy, which is the finding.
    brew = next(r for r in doc["rows"] if r["id"] == "minecraft:brewing_stand")
    ok(brew["asWhat"] == "an alchemist's bench", "the brewing stand is an alchemist's bench")
    ok("Newton" in brew["note"], "and the row names Newton, who wrote more on alchemy than physics")

    ok(len(doc["settings"]) == 2, "two settings, strict and traveller")
    ok(any(s["id"] == "traveller" for s in doc["settings"]),
       "E8's time traveller is one of them")
    ok("seen" in next(s for s in doc["settings"] if s["id"] == "traveller")["note"],
       "and a time traveller is SEEN doing it, which is the point of the setting")
    return bad


def main(argv):
    doc, problems = build()
    for p in problems:
        print("  PROBLEM " + p)
    c = doc["counts"]
    print("anachronisms: %d rows (%d real, %d myth, %d never); %d allowed, %d renamed, %d locked"
          % (c["rows"], c["real"], c["myth"], c["never"], c["allowed"], c["renamed"], c["locked"]))
    bad = check(doc)
    if problems or bad or "--check" in argv:
        return 1 if (problems or bad) else 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with gzip.GzipFile(OUT, "wb", mtime=0) as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    print("  wrote %s (%d bytes)" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
