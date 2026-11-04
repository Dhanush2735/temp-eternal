#!/usr/bin/env python3
"""Step 40 (D10 armies in action): build history/sides.json.gz from the hand-written table.

    python3 build_sides.py
    python3 build_sides.py --selftest     rebuild in memory and check it (exit 1 on a problem)

What it checks:

* every row is dated, placed and sourced;
* **every `raised` id points at a real row in the morale pack.** A party whose troops are raised
  in a way the register has never heard of is a party the register cannot simulate, and this is
  the only check in the step that crosses from one pack into the other;
* `willTreat` actually varies. If every kind of party could be bound by a treaty the field would
  be decoration, and the siege register in part 4 depends on it being real;
* the parties Brecke's rule admits are here: a rising, a people, a company, a coalition, and a
  band with no state behind it at all. A table of sides that is a table of states has missed the
  point of the source;
* `civilians` cannot initiate. That is what the word means, and Brecke counts them separately;
* the table spans the millennia and the world, so that there is an answer for a Bronze Age
  campaign and for one in 1870, and for somewhere other than Europe;
* and it prints the gaps it knows about -- including, first among them, that the catalog itself
  was never loaded.
"""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from sides_table import GAPS, KIND, MARKS, PARTIES            # noqa: E402
from morale_table import RAISED                               # noqa: E402

MOD = os.path.normpath(os.path.join(HERE, "..", "eternal"))
OUT = os.path.join(MOD, "src", "main", "resources", "data", "eternalengine", "eternal",
                   "history", "sides.json.gz")

SOURCE = ("Peter Brecke, 'Conflict Catalog' (Georgia Institute of Technology), and his "
          "'Violent Conflicts 1400 A.D. to the Present in Different Regions of the World', "
          "'Notes regarding the Conflict Catalog' and 'Toward a Taxonomy of Violent Conflicts' "
          "-- for the rule that a party need not be a state, for the separation of military and "
          "civilian fatalities, and for the fields the catalog keeps. Branislav Slantchev, "
          "'Warfare on Land', for hired troops; Michael J. Taylor on Hellenistic legitimacy; "
          "and the cited articles on the Mamluk sultanate, the Janissaries, the Teutonic Order, "
          "the Catalan and Great Companies, the Dutch and English East India Companies, medieval "
          "communes, and dynastic succession. **No row of Brecke's catalog was read into this "
          "pack** -- it is a binary spreadsheet -- and the kinds of party here are the ones the "
          "catalog's own description of its fields admits, not the conflicts it contains.")


def build():
    return {
        "format": 1,
        "id": "sides",
        "source": SOURCE,
        "gaps": GAPS,
        "kinds": list(KIND),
        "parties": [p.as_dict() for p in PARTIES],
    }


def selftest(doc):
    problems = []
    rows = doc["parties"]

    ids = [r["id"] for r in rows]
    if len(set(ids)) != len(ids):
        problems.append("duplicate party ids")

    known_raised = set(r.id for r in RAISED)
    for r in rows:
        if r["kind"] not in KIND:
            problems.append("%s: kind %s is not one the mod knows" % (r["id"], r["kind"]))
        if not r["src"]:
            problems.append("%s: no source" % r["id"])
        if r["mark"] not in MARKS:
            problems.append("%s: unknown mark %s" % (r["id"], r["mark"]))
        if not r["doing"] or not r["needs"]:
            problems.append("%s: says neither what it is nor what it needs" % r["id"])
        if not r["note"]:
            problems.append("%s: a party with no reason given is not an answer" % r["id"])
        if r["raised"] not in known_raised:
            problems.append("%s: raised '%s' is not a row in the morale pack -- the register "
                            "would not know how these men were raised"
                            % (r["id"], r["raised"]))
        if r["end"] - r["start"] > 4200 and "default" not in r["note"].lower():
            problems.append("%s runs for %d years without saying in its note that it is the "
                            "default" % (r["id"], r["end"] - r["start"]))

    # --------------------------------------------------- willTreat is a real distinction
    can = [r["id"] for r in rows if r["willTreat"]]
    cannot = [r["id"] for r in rows if not r["willTreat"]]
    if not cannot:
        problems.append("every kind of party can be bound by a treaty, so the field says nothing "
                        "and part 4's conditional surrender is meaningless")
    if not can:
        problems.append("no kind of party can be bound by a treaty, so no siege ever ends in "
                        "terms and no war ever ends in a peace")

    # --------------------------------------------------- Brecke's rule is honoured
    for want in ("warlord_band", "rebellion", "tribal_confederacy", "mercenary_company",
                 "coalition", "civilians"):
        if want not in ids:
            problems.append("no '%s' row: Brecke's own rule is that a party need not be a state, "
                            "and this table is missing one of the kinds he names" % want)

    civ = dict((r["id"], r) for r in rows).get("civilians")
    if civ is not None and civ["canInitiate"]:
        problems.append("civilians can initiate a war in this register, which is what the word "
                        "means it cannot do")

    if not any(r["kind"] == "company" for r in rows):
        problems.append("no company: the register cannot express a war fought for a dividend")
    if not any(r["kind"] == "faith" for r in rows):
        problems.append("no religious party: the register cannot express a war of religion")

    # --------------------------------------------------- it spans the world and the millennia
    las = [v for r in rows for v in (r["box"][0], r["box"][1])]
    los = [v for r in rows for v in (r["box"][2], r["box"][3])]
    if max(los) - min(los) < 150.0:
        problems.append("longitude spans only %d degrees: this is one theatre, and Brecke's "
                        "catalog is not" % int(max(los) - min(los)))

    empty = []
    for y in range(-1500, 2001, 500):
        if not any(r["start"] <= y <= r["end"] for r in rows):
            empty.append(y)
    if empty:
        problems.append("no kind of party in force in %s: the register has no answer there"
                        % ", ".join(str(y) for y in empty))

    # --------------------------------------------------- the map only gets to guess some of them
    general = [r["id"] for r in rows if r["scope"] == "general"]
    local = [r["id"] for r in rows if r["scope"] == "local"]
    if len(general) < 4:
        problems.append("only %d kinds of party can be guessed from a map and a year: the "
                        "register has no default anywhere" % len(general))
    if len(local) < 5:
        problems.append("only %d kinds of party are local, so the register is claiming a "
                        "latitude and a year can tell you that a town is a commune" % len(local))
    if not any(r["scope"] == "general" and r["willTreat"] for r in rows):
        problems.append("no general party can be bound by a treaty, so nothing the map can "
                        "guess is ever worth negotiating with")
    if "city_commune" in ids and rows[ids.index("city_commune")]["scope"] != "local":
        problems.append("a city that governs itself is not something a map can tell you, and "
                        "this register is claiming it is")

    # --------------------------------------------------- all the kinds are in use
    used = set(r["kind"] for r in rows)
    for k in KIND:
        if k not in used:
            problems.append("kind '%s' is never used: drop it or fill it" % k)

    est = sum(1 for r in rows if r["mark"] == "estimated")
    mix = sum(1 for r in rows if r["mark"] == "mixed")
    print("  parties %2d: %2d recorded, %d mixed, %2d estimated"
          % (len(rows), len(rows) - est - mix, mix, est))
    print("  by kind:     %s" % ", ".join("%s %d" % (k, sum(1 for r in rows
                                                            if r["kind"] == k)) for k in KIND))
    print("  can treat:   %s" % ", ".join(can))
    print("  cannot:      %s" % ", ".join(cannot))
    print("  ground: lat %.0f..%.0f, lon %.0f..%.0f" % (min(las), max(las), min(los), max(los)))
    print("  years: %d..%d" % (min(r["start"] for r in rows), max(r["end"] for r in rows)))
    print("  general:     %s" % ", ".join(general))
    print("  local:       %s" % ", ".join(local))
    print("  known gaps: %d" % len(GAPS))

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
    print("  %d kinds of party; %d bytes raw, %d gzipped"
          % (len(doc["parties"]), len(raw), os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
