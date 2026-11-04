#!/usr/bin/env python3
"""Step 40 (D10 armies in action), part 4: build history/sieges.json.gz.

    python3 build_sieges.py
    python3 build_sieges.py --selftest

The numbers a siege is run with, kept as data so that they can be read, argued with and replaced
without touching the Java. What it checks:

* the five endings add up to one siege, and the commonest of them is the one nobody guesses -- a
  table in which most sieges end in a sack is a table that has forgotten what the rules of war
  were for;
* terms, relief and abandonment never sack the town, and storm and starvation always do. If that
  stops being true the register has stopped saying anything;
* every wall and every method is sourced, and none of them spans history;
* every century from 1500 BC to today has both a wall standing and a way of attacking one, because
  a year in which the register has no answer is a year in which it will quietly guess;
* the world is covered, not one favourite corner;
* **the timetable changes.** Something must be available to a besieger of 1453 that was not
  available to one of 1400, and something again by 1670. A register in which siege warfare never
  changes is a register that has not read the sources.
"""

import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import siege_table as T                                             # noqa: E402

MOD = os.path.normpath(os.path.join(HERE, "..", "eternal"))
OUT = os.path.join(MOD, "src", "main", "resources", "data", "eternalengine", "eternal",
                   "history", "sieges.json.gz")

SOURCE = ("Wikipedia 'Siege' and 'Siegecraft' for the Peloponnesian count of 100 sieges and 58 "
          "surrenders, for Alesia's circumvallation and contravallation, and for blockade being "
          "the commonest practice; 'Siege warfare in ancient Rome' for Syracuse and Numantia; "
          "English Heritage 'Medieval siege warfare' for Kenilworth's 172 days with two days of "
          "food left, Rochester's pigs and Dover's held breach; The Castle Rolls 'How Was a "
          "Castle Taken?' for 'usually by hunger, not by assault', for Odiham's thirteen men, for "
          "Dryslwyn's wall falling on the attackers, and for 'what a mine did in weeks and hunger "
          "did in months, a battery now did in days'; Britannica and EBSCO for escalade failing "
          "above ten metres, for belfroys and for mining; Wikipedia 'Siege of Constantinople "
          "(1453)' for the fifty-three days, the sixty-nine guns, Orban's Basilic and its three "
          "hours to reload; Rebus, the Modern War Institute and Wikipedia 'Italian Wars' for "
          "Charles VIII's forty siege guns in 1494 and the trace italienne that answered them; "
          "the New World Encyclopedia on Vauban's saps and parallels and the request to surrender "
          "after every step; Blaise de Monluc at Siena in 1555 for the 4,400 useless mouths; "
          "Wikipedia 'Effects of the siege of Leningrad' for the thirty-five days of grain and "
          "the 125-gram ration; Britannica for Sarajevo's 1,425 days and its airlift. Wall "
          "strength, the distribution of the five endings and the besiegers' own clock are this "
          "register's reading and are marked estimated.")

GAPS = ("The distribution of the five endings is estimated: one number is measured, the "
        "Peloponnesian War's 58 surrenders out of 100 sieges, and it does not separate terms from "
        "starvation. Wall strength -- stormMult and breachDays -- is estimated throughout: no "
        "source was read that ranks wall types against one another, and the ordering here is "
        "argued from what each wall was built to answer. The besiegers' own clock is a single "
        "number, not a model of disease, weather and supply. Water is a floor of three days and "
        "not a supply, because the register does not yet know whether a town has a cistern or a "
        "well. There is no row for Oceania, none for the Americas before 1491 and none for "
        "sub-Saharan Africa outside the general fallback -- not because those peoples did not "
        "fortify, but because no article was read for them.")


def build():
    return {
        "format": 1,
        "id": "sieges",
        "source": SOURCE,
        "gaps": GAPS,
        "walls": [{"id": w.id, "name": w.name, "start": w.start, "end": w.end,
                   "box": list(w.box), "scale": w.scale, "mine": w.mine, "storm": w.storm,
                   "resist": w.resist, "scope": w.scope, "note": w.note, "source": w.src,
                   "mark": w.mark}
                  for w in T.WALLS],
        "methods": [{"id": m.id, "name": m.name, "start": m.start, "end": m.end,
                     "days": m.days, "assault": m.assault, "risk": m.risk, "needs": m.needs,
                     "note": m.note, "source": m.src, "mark": m.mark} for m in T.METHODS],
        "endings": [{"id": e.id, "name": e.name, "share": e.share, "sack": e.sack,
                     "when": e.when, "note": e.note, "source": e.src, "mark": e.mark}
                    for e in T.ENDINGS],
        "food": {
            "grainKgPerHeadPerDay": T.GRAIN_KG_PER_HEAD_PER_DAY,
            "cutAtDays": T.CUT_AT_DAYS,
            "rationCut": T.RATION_CUT,
            "uselessLastYear": T.USELESS_LAST_YEAR,
            "noSurrenderMorale": T.NO_SURRENDER_MORALE,
            "famineDeathsPerDay": T.FAMINE_DEATHS_PER_DAY,
            "uselessShare": T.USELESS_SHARE,
            "uselessGain": T.USELESS_GAIN,
            "waterDays": T.WATER_DAYS,
        },
        "besiegerBaseDays": T.BESIEGER_BASE_DAYS,
        "besiegerSupplyCurve": T.BESIEGER_SUPPLY_CURVE,
        "stormBase": T.STORM_BASE,
        "stormPerMan": T.STORM_PER_MAN,
        "stormNoBreach": T.STORM_NO_BREACH,
        "stormCost": T.STORM_COST,
        "bargainingMorale": T.BARGAINING_MORALE,
    }


def in_force(rows, year):
    return [r for r in rows if r["start"] <= year <= r["end"]]


def selftest(doc):
    problems = list(T.check())

    if len(doc["walls"]) < 8:
        problems.append("only %d kinds of wall" % len(doc["walls"]))
    if len(doc["methods"]) < 7:
        problems.append("only %d ways of attacking a wall" % len(doc["methods"]))
    for w in doc["walls"]:
        if w["end"] - w["start"] > 6000:
            problems.append("%s stands for %d years: that is not a fortification, that is "
                            "geography" % (w["id"], w["end"] - w["start"]))
    for row in doc["walls"] + doc["methods"] + doc["endings"]:
        if row["mark"] not in T.MARKS:
            problems.append("%s has no honest mark: %s" % (row["id"], row["mark"]))
        if not row.get("source"):
            problems.append("%s has no source" % row["id"])

    # the timetable has to change
    before = {m["id"] for m in in_force(doc["methods"], 1400)}
    in1453 = {m["id"] for m in in_force(doc["methods"], 1453)}
    by1670 = {m["id"] for m in in_force(doc["methods"], 1670)}
    if not in1453 - before:
        problems.append("a besieger of 1453 has nothing a besieger of 1400 lacked")
    if not by1670 - in1453:
        problems.append("a besieger of 1670 has nothing a besieger of 1453 lacked")

    # the register's own claim
    ends = sorted(doc["endings"], key=lambda e: -e["share"])
    if ends[0]["id"] != "terms":
        problems.append("the commonest ending here is %s, and the whole point of the register is "
                        "that a siege usually ended in an agreement" % ends[0]["id"])
    quiet = sum(e["share"] for e in doc["endings"] if not e["sack"])
    if quiet < 0.5:
        problems.append("only %.0f%% of sieges end without the town being sacked" % (quiet * 100))

    print("  walls   %2d: %s" % (len(doc["walls"]), ", ".join(w["id"] for w in doc["walls"])))
    print("  methods %2d: %s" % (len(doc["methods"]),
                                 ", ".join("%s(%s)" % (m["id"],
                                                       "%dd" % m["days"] if m["days"]
                                                       else "assault" if m["assault"]
                                                       else "no breach")
                                           for m in doc["methods"])))
    print("  endings %2d: %s" % (len(doc["endings"]),
                                 ", ".join("%s %.0f%%%s" % (e["id"], e["share"] * 100,
                                                            "*" if e["sack"] else "")
                                           for e in doc["endings"])))
    print("           (* the town is sacked: a place taken by force could be ransacked, one that")
    print("              surrendered could not -- %.0f%% of sieges end without that)"
          % (quiet * 100))
    print("  food    %.1f kg a head a day; ration cut to %.0f%%; %.2f%% of the town dying a day "
          "in famine"
          % (doc["food"]["grainKgPerHeadPerDay"], doc["food"]["rationCut"] * 100,
             doc["food"]["famineDeathsPerDay"] * 100))
    print("          putting out %.0f%% of the mouths stretches the bread by %.2fx"
          % (doc["food"]["uselessShare"] * 100, doc["food"]["uselessGain"]))
    print("          and only before %d: after that age a state evacuates its people rather than "
          "driving them out" % doc["food"]["uselessLastYear"])
    def days_for(supply):
        return int(doc["besiegerBaseDays"]
                   * (1.0 + doc["besiegerSupplyCurve"] * (supply / 100.0) ** 2))
    print("  clocks  the besiegers can sit %d days on no supply, %d at half, %d at full"
          % (days_for(0), days_for(50), days_for(100)))
    if days_for(0) > 200:
        problems.append("an army with no supply will sit for %d days" % days_for(0))
    if days_for(90) < 800:
        problems.append("a fully supplied army gives up at %d days, but the Germans sat outside "
                        "Leningrad for 872" % days_for(90))
    if days_for(100) < 365:
        problems.append("even a fully supplied army gives up at %d days, and Machiavelli's city "
                        "with a year of provisions could outlast any siege" % days_for(100))

    # every wall must either be breachable or say it is not: a resist of 0 is a wall no one
    # bothered to build
    for w in doc["walls"]:
        if w["resist"] <= 0:
            problems.append("%s resists nothing" % w["id"])
    # and at least one age must have a method that cannot breach, or the register is claiming
    # that every siege anywhere was a matter of knocking a hole
    if not any(m["days"] == 0 for m in doc["methods"]):
        problems.append("every method can open a breach: blockade and escalade cannot")
    # the wall the register cannot approach must exist, or the Kenilworth case has no answer
    if not any(m["needs"] == "approach" for m in doc["methods"]):
        problems.append("no method has to be brought up to the wall, so water defends nothing")
    # and somewhere in history there must be a year in which nothing at all can open a breach,
    # or the register is claiming that every siege anywhere was a matter of knocking a hole
    gap = [y for y in range(-1500, 2027, 25)
           if not any(m["days"] > 0 and m["start"] <= y <= m["end"] and m["needs"] == ""
                      for m in doc["methods"])]
    if not gap:
        problems.append("in every year some method works regardless of the ground, so the ground "
                        "never decides anything")
    rec = sum(1 for x in doc["walls"] + doc["methods"] + doc["endings"]
              if x["mark"] == "recorded")
    tot = len(doc["walls"]) + len(doc["methods"]) + len(doc["endings"])
    print("  %d of %d rows recorded, and the rest say so" % (rec, tot))

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
    print("  %d walls, %d methods, %d endings, %d bytes raw, %d gzipped"
          % (len(doc["walls"]), len(doc["methods"]), len(doc["endings"]), len(raw),
             os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
