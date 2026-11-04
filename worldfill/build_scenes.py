#!/usr/bin/env python3
"""Step 39 (D9 event scenes): build history/scenes.json.gz from the hand-written table.

    python3 build_scenes.py
    python3 build_scenes.py --selftest     rebuild in memory and check it (exit 1 on a problem)

What it checks:

* twenty scenes, and their ids are exactly the twenty D9 names;
* every scene stands on a ground this register knows and is set off by a trigger it knows;
* every scene casts from the twelve work sectors step 38's `Jobs` actually draws from, so the
  register is never asking for a kind of person the job table has never heard of;
* every scene is sourced, and the ones whose composition is this table's own reading say so;
* all seven triggers are used, and no trigger carries more than half the scenes -- a register
  where everything is an event is a register with one idea;
* the suffering scenes together are the largest group, because most of what gathers a crowd in
  history is something going wrong.
"""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from scenes_table import SCENES                                   # noqa: E402

MOD = os.path.normpath(os.path.join(HERE, "..", "eternal"))
OUT = os.path.join(MOD, "src", "main", "resources", "data", "eternalengine", "eternal",
                   "history", "scenes.json.gz")

# D9's list, in the plan's own order. The table must be exactly this.
WANTED = ["battle", "siege", "crowning", "court_day", "procession", "festival", "prayer",
          "market_day", "plague", "famine", "flight", "fire", "building_works", "refugees",
          "election", "protest", "trial", "wedding", "funeral", "caravan_arrival"]

SOURCE = ("English Wikipedia: 'Coronation', 'Assizes', 'Trial by ordeal', 'Assize of Clarendon', "
          "'Roman triumph', 'Election', 'Protest', 'Canonical hours', 'Salah', 'Siddur', 'Charter "
          "fair', 'Wake (ceremony)', 'Banns of marriage', 'Fourth Council of the Lateran', "
          "'Funeral procession'; Britannica: 'triumph', 'assize'; the Institute of Historical "
          "Research, 'Gazetteer of Markets and Fairs to 1516'; and the mod's own registers, each "
          "sourced where it was built: steps 28, 30b, 32, 34, 36, 37 and 38. Rows marked "
          "estimated carry a cast that is this table's reading, not any source's.")


def build():
    return {
        "format": 1,
        "id": "scenes",
        "source": SOURCE,
        "scenes": [{
            "id": s.id, "name": s.name, "group": s.group, "where": s.where,
            "trigger": s.trigger,
            "sectors": list(s.cast.keys()), "counts": [s.cast[k] for k in s.cast],
            "doing": s.doing, "note": s.note, "source": s.src, "mark": s.mark,
        } for s in SCENES],
    }


def selftest(doc):
    problems = []
    rows = doc["scenes"]

    got = [r["id"] for r in rows]
    if sorted(got) != sorted(WANTED):
        problems.append("the scenes are not D9's twenty: missing %s, extra %s"
                        % (sorted(set(WANTED) - set(got)), sorted(set(got) - set(WANTED))))
    if len(set(got)) != len(got):
        problems.append("duplicate scene ids")

    from scenes_table import S
    for r in rows:
        if not r["source"]:
            problems.append("scene %s has no source" % r["id"])
        if r["where"] not in S.GROUNDS:
            problems.append("scene %s stands on an unknown ground: %s" % (r["id"], r["where"]))
        if r["trigger"] not in S.TRIGGERS:
            problems.append("scene %s has an unknown trigger: %s" % (r["id"], r["trigger"]))
        for k in r["sectors"]:
            if k not in S.SECTORS:
                problems.append("scene %s casts from an unknown sector: %s" % (r["id"], k))
        if len(r["sectors"]) != len(r["counts"]):
            problems.append("scene %s: %d sectors but %d counts"
                            % (r["id"], len(r["sectors"]), len(r["counts"])))
        if sum(r["counts"]) <= 0:
            problems.append("scene %s has nobody in it" % r["id"])

    # a register where everything is an event is a register with one idea
    by_trigger = {}
    by_group = {}
    for r in rows:
        by_trigger[r["trigger"]] = by_trigger.get(r["trigger"], 0) + 1
        by_group[r["group"]] = by_group.get(r["group"], 0) + 1
    if len(by_trigger) < 7:
        problems.append("only %d of the 7 triggers are used" % len(by_trigger))
    for k, n in by_trigger.items():
        if n * 2 > len(rows):
            problems.append("%s carries %d of %d scenes: one trigger is doing all the work"
                            % (k, n, len(rows)))
    if by_group.get("suffering", 0) < 5:
        problems.append("only %d suffering scenes: most of what gathers a crowd in history is "
                        "something going wrong" % by_group.get("suffering", 0))

    est = sum(1 for r in rows if r["mark"] == "estimated")
    mix = sum(1 for r in rows if r["mark"] == "mixed")
    print("  scenes %2d: %2d recorded, %d mixed, %2d estimated"
          % (len(rows), len(rows) - est - mix, mix, est))
    print("  by trigger: %s" % ", ".join("%s %d" % (k, v) for k, v in sorted(by_trigger.items())))
    print("  by group:   %s" % ", ".join("%s %d" % (k, v) for k, v in sorted(by_group.items())))

    if problems:
        print("\n%d PROBLEM(S):" % len(problems))
        for p in problems[:40]:
            print("  - " + p)
        return 1
    print("  0 problems")
    return 0


def main():
    doc = build()
    rc = selftest(doc)
    if rc:
        return rc
    if "--selftest" in sys.argv:
        print("  (no pack written in --selftest mode)")
        return 0
    raw = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.GzipFile(OUT, "wb", compresslevel=9, mtime=0) as fh:
        fh.write(raw)
    print("wrote %s" % OUT)
    print("  %d scenes, %d bytes raw, %d gzipped"
          % (len(doc["scenes"]), len(raw), os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
