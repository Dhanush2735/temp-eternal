#!/usr/bin/env python3
"""Step 40 (D10 armies in action): build history/formations.json.gz from the hand-written table.

    python3 build_formations.py
    python3 build_formations.py --selftest     rebuild in memory and check it (exit 1 on a problem)

What it checks:

* every row stands in one of the five shapes `war/FormationType` can actually draw, because a
  formation the mod cannot render is not a formation;
* every row is dated and placed, and no row runs for ever -- a way of standing that stopped being
  used has to say when it stopped;
* every row names the article its figures came from;
* the table spans the world and not one corner of it: both hemispheres, and a spread of longitude
  wide enough that it is not a European table with a Japanese footnote;
* the table spans the millennia, so that there is an answer for a Bronze Age chariot army and for
  one in 1870;
* and it prints the gaps it knows about, because a register that hides its holes is a register
  that will be trusted where it should not be.
"""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from formations_table import FORMATIONS, GAPS, GROUND, SHAPES, MARKS   # noqa: E402

MOD = os.path.normpath(os.path.join(HERE, "..", "eternal"))
OUT = os.path.join(MOD, "src", "main", "resources", "data", "eternalengine", "eternal",
                   "history", "formations.json.gz")

SOURCE = ("English Wikipedia: 'Macedonian phalanx', 'Sarissa', 'Phalanx', 'Hoplite', 'Ancient "
          "Greek warfare', 'Roman infantry tactics', 'Chariot', 'Battle of Kadesh', 'Chariotry "
          "in ancient Egypt', 'Shield wall', 'Anglo-Saxon warfare', 'War elephant', 'Military "
          "history of India', 'Ancient warfare', 'Nageyari', 'Ashigaru', 'Tercio', 'Pike and "
          "shot', 'Line infantry', 'Battle of Breitenfeld (1631)', 'Napoleonic tactics', "
          "'Infantry in the American Civil War', 'Franco-Prussian War', 'Impi', 'Shaka'; the TOTA "
          "project on Mongol warfare; and Peter Krentz, 'Casualties in Hoplite Battles' (GRBS), "
          "for the casualty bands the next part uses. Rows marked estimated carry a figure that "
          "is this table's reading, not any source's.")


def build():
    return {
        "format": 1,
        "id": "formations",
        "source": SOURCE,
        "gaps": GAPS,
        "formations": [{
            "id": f.id, "name": f.name, "shape": f.shape, "ranks": f.ranks,
            "start": f.start, "end": f.end,
            "box": [f.box[0], f.box[1], f.box[2], f.box[3]],
            "arm": f.arm, "troop": f.troop, "purpose": f.purpose,
            "ground": GROUND[f.id],
            "needs": f.needs, "doing": f.doing, "note": f.note,
            "source": f.src, "mark": f.mark,
        } for f in FORMATIONS],
    }


def selftest(doc):
    problems = []
    rows = doc["formations"]

    ids = [r["id"] for r in rows]
    if len(set(ids)) != len(ids):
        problems.append("duplicate formation ids")

    for r in rows:
        if r["shape"] not in SHAPES:
            problems.append("%s: shape %s is not one the mod can draw" % (r["id"], r["shape"]))
        if not r["source"]:
            problems.append("%s: no source" % r["id"])
        if r["mark"] not in MARKS:
            problems.append("%s: unknown mark %s" % (r["id"], r["mark"]))
        if r["end"] - r["start"] > 3600:
            problems.append("%s runs for %d years: that is not a formation, it is a habit"
                            % (r["id"], r["end"] - r["start"]))
        if not r["doing"] or not r["needs"]:
            problems.append("%s: says neither what it does nor what it needs" % r["id"])
        if r["ranks"] and r["shape"] == "SKIRMISH" and r["ranks"] > 1:
            problems.append("%s: a skirmish order %d ranks deep is not a skirmish order"
                            % (r["id"], r["ranks"]))

    # ---------------------------------------------------------------- it spans the world
    las = [v for r in rows for v in (r["box"][0], r["box"][1])]
    los = [v for r in rows for v in (r["box"][2], r["box"][3])]
    if min(las) > 0.0:
        problems.append("nothing in the southern hemisphere: this is a northern table")
    if max(las) < 50.0:
        problems.append("nothing above 50N: this is a Mediterranean table")
    if max(los) - min(los) < 150.0:
        problems.append("longitude spans only %d degrees: this is one theatre"
                        % int(max(los) - min(los)))

    # ---------------------------------------------------------------- it spans the millennia
    empty = []
    for millennium in range(-1500, 2001, 500):
        if not any(r["start"] <= millennium <= r["end"] for r in rows):
            empty.append(millennium)
    if empty:
        problems.append("no formation in force in %s: the register has no answer there"
                        % ", ".join(str(y) for y in empty))

    # ---------------------------------------------------------------- it uses the shapes
    used = set(r["shape"] for r in rows)
    if len(used) < 4:
        problems.append("only %d of the five shapes are ever used" % len(used))

    est = sum(1 for r in rows if r["mark"] == "estimated")
    mix = sum(1 for r in rows if r["mark"] == "mixed")
    print("  formations %2d: %2d recorded, %d mixed, %2d estimated"
          % (len(rows), len(rows) - est - mix, mix, est))
    print("  by shape:   %s" % ", ".join("%s %d" % (s, sum(1 for r in rows
                                                           if r["shape"] == s)) for s in SHAPES))
    print("  by purpose: %s" % ", ".join("%s %d" % (p, sum(1 for r in rows
                                                           if r["purpose"] == p))
                                         for p in ("shock", "hold", "missile", "envelope",
                                                   "screen")))
    print("  ground covered: lat %.0f..%.0f, lon %.0f..%.0f"
          % (min(las), max(las), min(los), max(los)))
    print("  years: %d..%d" % (min(r["start"] for r in rows), max(r["end"] for r in rows)))
    print("  by ground:  %s" % ", ".join("%s %d" % (g, sum(1 for r in rows
                                                           if r["ground"] == g))
                                         for g in ("level", "open", "broken", "any")))
    print("  known gaps: %s" % GAPS)

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
    print("  %d formations, %d bytes raw, %d gzipped"
          % (len(doc["formations"]), len(raw), os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
