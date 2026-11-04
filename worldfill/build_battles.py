#!/usr/bin/env python3
"""Step 40 (D10 armies in action), part 3: build history/battles.json.gz.

    python3 build_battles.py
    python3 build_battles.py --selftest

The numbers a battle is decided with, kept as data so that they can be read, argued with and
replaced without touching the Java. What it checks:

* the bands are honest -- no band in which the winner can lose more than the loser, and every arm
  of the era belongs to exactly one band;
* the ways of losing are ordered and distinct, and the worst of them is not the same as the best;
* the matchup table cancels: whatever advantage `envelope` has over `hold`, `hold` has the mirror
  of it over `envelope`, or the register is quietly favouring one kind of army;
* the ground costs are all small. Ground decides battles by a few points of probability, and a
  table in which it decides them by arithmetic is a table that has been tuned to a result.
"""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import battle_table as T                                            # noqa: E402

MOD = os.path.normpath(os.path.join(HERE, "..", "eternal"))
OUT = os.path.join(MOD, "src", "main", "resources", "data", "eternalengine", "eternal",
                   "history", "battles.json.gz")

SOURCE = ("Peter Krentz, 'Casualties in Hoplite Battles' (GRBS), for the 3-10% and 10-20% bands; "
          "'Changes in Lethality and Casualty Rates' (Air University, on Dupuy) and 'Attrition In "
          "Future Land Combat' (The Dupuy Institute) for the finding that casualty rates have "
          "been falling since the seventeenth century as armies dispersed; and the formation "
          "sources in formations.json.gz for the three matchups that are attested rather than "
          "inferred. Everything else in this pack -- the bow band, the musket and rifle bands, "
          "the pursuit multipliers, the matchup matrix and the ground costs -- is this table's "
          "reading and is marked estimated.")


def build():
    return {
        "format": 1,
        "id": "battles",
        "source": SOURCE,
        "bands": [{"id": b.id, "name": b.name, "arms": b.arms,
                   "winner": [b.wlo, b.whi], "loser": [b.llo, b.lhi],
                   "note": b.note, "source": b.src, "mark": b.mark} for b in T.BANDS],
        "breaks": [{"id": k.id, "name": k.name, "mult": k.mult, "when": k.when,
                    "note": k.note, "source": k.src, "mark": k.mark} for k in T.BREAKS],
        "matchup": [{"a": a, "b": b, "adv": v} for (a, b), v in sorted(T.MATCHUP.items())],
        "ground": [{"wants": w, "on": g, "cost": v}
                   for (w, g), v in sorted(T.GROUND_COST.items())],
        "groundBonus": T.GROUND_BONUS,
        "roll": [T.ROLL_LOW, T.ROLL_HIGH],
        "shattered": T.SHATTERED,
        "breakRules": {
            "routMorale": T.ROUT_MORALE,
            "routSupply": T.ROUT_SUPPLY,
            "routRatio": T.ROUT_RATIO,
            "intactMorale": T.INTACT_MORALE,
            "intactSupply": T.INTACT_SUPPLY,
            "escapeChance": T.ESCAPE_CHANCE,
            "surroundedOdds": T.SURROUNDED_ODDS,
            "pursuedOdds": T.PURSUED_ODDS,
            "narrowOdds": T.NARROW_ODDS,
            "ceiling": T.CEILING,
        },
    }


def selftest(doc):
    problems = list(T.check())

    if len(doc["bands"]) < 3:
        problems.append("only %d bands: the register needs one for the spear, the bow and the gun"
                        % len(doc["bands"]))
    if len(doc["breaks"]) < 3:
        problems.append("only %d ways to lose" % len(doc["breaks"]))
    mults = [k["mult"] for k in doc["breaks"]]
    if sorted(mults) != mults:
        problems.append("the ways of losing are not in order")
    if max(mults) / min(mults) < 2.0:
        problems.append("the worst way to lose is only %.1fx the best: the pursuit is not worth "
                        "modelling" % (max(mults) / min(mults)))
    for g in doc["ground"]:
        if abs(g["cost"]) > 0.15:
            problems.append("%s on %s costs %.2f: ground is deciding this by arithmetic"
                            % (g["wants"], g["on"], g["cost"]))
    lo, hi = doc["roll"]
    if not 0.0 < lo < hi < 1.0:
        problems.append("the dice is broken: %s..%s" % (lo, hi))
    if not 0.0 < doc["shattered"] < 1.0:
        problems.append("a shattered army cannot be %s of itself" % doc["shattered"])
    r = doc["breakRules"]
    if r["routMorale"] >= r["intactMorale"]:
        problems.append("an army at %d morale cannot both hold its line and fail to" %
                        r["intactMorale"])
    if r["routSupply"] >= r["intactSupply"]:
        problems.append("an army at %d supply cannot both be fed and be starving" %
                        r["intactSupply"])
    if not 0.0 < r["escapeChance"] < 1.0:
        problems.append("a beaten line escapes %s of the time" % r["escapeChance"])
    if not 0.0 < r["pursuedOdds"] < r["surroundedOdds"] < 1.0:
        problems.append("an encirclement must be a clearer verdict than a pursuit: %s against %s"
                        % (r["surroundedOdds"], r["pursuedOdds"]))
    if not 0.0 < r["ceiling"] < 1.0:
        problems.append("nothing loses %s of itself and is still an army" % r["ceiling"])

    est = sum(1 for x in doc["bands"] + doc["breaks"] if x["mark"] == "estimated")
    tot = len(doc["bands"]) + len(doc["breaks"])
    print("  bands   %d: %s" % (len(doc["bands"]),
                                ", ".join("%s %.0f-%.0f/%.0f-%.0f" % (b["id"], b["winner"][0],
                                          b["winner"][1], b["loser"][0], b["loser"][1])
                                          for b in doc["bands"])))
    print("  breaks  %d: %s" % (len(doc["breaks"]),
                                ", ".join("%s x%.1f" % (k["id"], k["mult"])
                                          for k in doc["breaks"])))
    print("  matchup %d pairs, ground %d costs (largest %.2f)"
          % (len(doc["matchup"]), len(doc["ground"]),
             max(abs(g["cost"]) for g in doc["ground"])))
    print("  rules   rout below %d morale / %d supply / %.1fx outnumbered; intact %d / %d; "
          "\n         escapes %.0f%% of the time; ceiling %.0f%%"
          % (r["routMorale"], r["routSupply"], r["routRatio"], r["intactMorale"],
             r["intactSupply"], r["escapeChance"] * 100.0, r["ceiling"] * 100.0))
    print("  %d of %d rows estimated, and they say so" % (est, tot))

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
    print("  %d bands, %d breaks, %d bytes raw, %d gzipped"
          % (len(doc["bands"]), len(doc["breaks"]), len(raw), os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
