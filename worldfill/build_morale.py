#!/usr/bin/env python3
"""Step 40 (D10 armies in action): build history/morale.json.gz from the hand-written table.

    python3 build_morale.py
    python3 build_morale.py --selftest     rebuild in memory and check it (exit 1 on a problem)

What it checks:

* every row is dated, placed and sourced, and every `when` is one `war/Morale.java` can actually
  test -- a factor keyed on a condition the mod cannot see is not a factor;
* the four kinds are all in use, because a table of morale that is all one kind of motivation has
  collapsed the sustaining/combat distinction the sources insist on;
* **winning outweighs losing-as-mirrored**, and the `winning` row and the `losing` row are not
  simply equal and opposite. The Naval Institute's study is unambiguous about the asymmetry;
* dispersion *costs* morale rather than granting it. This is du Picq's most counter-intuitive
  claim and the one most likely to be got backwards later;
* depth *gains* morale. Same passage, other half;
* every `raised` row names a desertion band and a cohesion, and no `raised` row runs for ever
  without saying how it was paid -- an army paid in nothing is not an army;
* the measured desertion figures are in the band the record actually reports, and every one of
  them carries either a rate, a total or a count;
* at least one way of breaking is keyed on a loss percentage, because an army that has lost a
  fifth of itself is a different body from one that has lost a twentieth;
* and it prints the gaps it knows about, because a register that hides its holes is a register
  that will be trusted where it should not be.
"""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from morale_table import (BREAKING, CASUALTIES, COMBAT, CONDITION, DESERTION, FACTORS,  # noqa: E402
                          FORMING, GAPS, KINDS, MARKS, RAISED, SUSTAINING, WHENS)

MOD = os.path.normpath(os.path.join(HERE, "..", "eternal"))
OUT = os.path.join(MOD, "src", "main", "resources", "data", "eternalengine", "eternal",
                   "history", "morale.json.gz")

SOURCE = ("Ardant du Picq, 'Battle Studies' (posthumous, trans. Greely & Cotton; Project "
          "Gutenberg), for the terror of battle, the collapse from the rear, the cost of "
          "dispersion and the Cannae passage; Marshal Foch's summary of it. Edward Shils and "
          "Morris Janowitz, 'Cohesion and Disintegration in the Wehrmacht in World War II' "
          "(Public Opinion Quarterly, 1948), and Samuel Stouffer et al., 'The American Soldier' "
          "(1949), for the primary group and for what soldiers themselves said kept them going; "
          "S.L.A. Marshall (1947), Leonard Wong, 'Why They Fight' (2003), Charles Moskos, and "
          "Anthony King, for the qualifications. Ilya Berkovich, 'Motivation in War: The "
          "Example of the Old Regime', for the three stages of a soldier's war. Branislav "
          "Slantchev, 'Warfare on Land', for conscripts and for hired troops. 'Mutiny -- A "
          "Study', US Naval Institute Proceedings (1932), for the passage on winning. Lyall and "
          "Zhukov on fratricidal coercion; 'Why Armies Break' on mass desertion. Michael J. "
          "Taylor on Hellenistic legitimacy; UNRV on mutiny among the legions; Syler on mutiny "
          "versus desertion. For the measured desertion rates: Duffy's 'The Military Experience "
          "in the Age of Reason' via Kabinettskriege, Corvisier via the same, the National Park "
          "Service at Fort Scott, Encyclopedia Virginia, and White Rose Research Online. Every "
          "weight in this pack is this table's reading, not any source's, and is marked "
          "estimated or mixed accordingly.")


def build():
    return {
        "format": 1,
        "id": "morale",
        "source": SOURCE,
        "gaps": GAPS,
        "kinds": list(KINDS),
        "whens": list(WHENS),
        "factors": [f.as_dict() for f in FACTORS],
        "raised": [r.as_dict() for r in RAISED],
        "desertion": [d.as_dict() for d in DESERTION],
        "breaking": [b.as_dict() for b in BREAKING],
        "casualties": CASUALTIES,
    }


def selftest(doc):
    problems = []
    rows = doc["factors"]

    ids = [r["id"] for r in rows]
    if len(set(ids)) != len(ids):
        problems.append("duplicate factor ids")

    by_id = dict((r["id"], r) for r in rows)
    for r in rows:
        if r["kind"] not in KINDS:
            problems.append("%s: kind %s is not one the mod knows" % (r["id"], r["kind"]))
        if r["when"] not in WHENS:
            problems.append("%s: when %s is not one the mod can test" % (r["id"], r["when"]))
        if not r["src"]:
            problems.append("%s: no source" % r["id"])
        if r["mark"] not in MARKS:
            problems.append("%s: unknown mark %s" % (r["id"], r["mark"]))
        if not r["doing"] or not r["needs"]:
            problems.append("%s: says neither what it does nor what it needs" % r["id"])
        if not r["note"]:
            problems.append("%s: a factor with no reason given is not an answer" % r["id"])
        if r["weight"] == 0:
            problems.append("%s: weighs nothing, so it is not in the register" % r["id"])

    # --------------------------------------------------------- all four factor kinds are in use
    # 'breaking' is not a factor kind: it lives in its own list, because how an army stops is not
    # a weight on a scale, it is a different question.
    FACTOR_KINDS = ("sustaining", "combat", "forming", "condition")
    used = set(r["kind"] for r in rows)
    for k in FACTOR_KINDS:
        if k not in used:
            problems.append("no row of kind '%s': the register has collapsed a distinction" % k)
    for k in KINDS:
        if k not in FACTOR_KINDS and k not in doc:
            problems.append("kind '%s' has no list of its own in the pack" % k)

    # --------------------------------------------------------- the du Picq claims, checked
    if "winning" in by_id and "losing" in by_id:
        w, l = by_id["winning"]["weight"], by_id["losing"]["weight"]
        if w <= 0 or l >= 0:
            problems.append("winning (%+d) does not help or losing (%+d) does not hurt"
                            % (w, l))
        if abs(l) <= abs(w):
            problems.append("losing (%+d) is not worse than winning (%+d) is good, and the "
                            "record says it is: 'Lee's men fought hungry through much of the "
                            "Civil War, cheerfully and without complaint; it was only when Grant "
                            "and Sherman began to close in that they deserted'" % (l, w))
    else:
        problems.append("no 'winning' or no 'losing' row: the register cannot speak to the "
                        "largest single factor in the literature")

    if "dispersion_cost" in by_id:
        if by_id["dispersion_cost"]["weight"] >= 0:
            problems.append("dispersion does not cost morale, and du Picq's whole argument is "
                            "that it does: 'the more men think themselves isolated, the more "
                            "need they have of high morale'")
    else:
        problems.append("no dispersion row: the register cannot charge the loose formations")

    if "depth_holds" in by_id:
        if by_id["depth_holds"]["weight"] <= 0:
            problems.append("depth does not help morale, and du Picq's whole argument is that "
                            "it does: the Romans 'kept soldiers in the rear removed from the "
                            "fear and panic of the front line'")
    else:
        problems.append("no depth row: the register cannot credit the formations that have it")

    # --------------------------------------------------------- sustaining vs combat, both real
    if not SUSTAINING:
        problems.append("nothing sustains an army in this register")
    if not COMBAT:
        problems.append("nothing makes an army stand in this register")
    if not FORMING:
        problems.append("no row reads the formation table, so part 2 and part 5 do not touch")
    if not CONDITION:
        problems.append("nothing has ever been done to an army in this register")

    # --------------------------------------------------------- how armies were raised
    rids = [r["id"] for r in doc["raised"]]
    if len(set(rids)) != len(rids):
        problems.append("duplicate raised ids")
    for r in doc["raised"]:
        if not r["src"]:
            problems.append("%s: no source" % r["id"])
        if r["mark"] not in MARKS:
            problems.append("%s: unknown mark %s" % (r["id"], r["mark"]))
        if not r["paidIn"]:
            problems.append("%s: does not say what the men are paid in" % r["id"])
        if not (0 <= r["cohesion"] <= 100):
            problems.append("%s: cohesion %s is off the scale" % (r["id"], r["cohesion"]))
        if not (0.0 <= r["desertion"] <= 40.0):
            problems.append("%s: desertion %s is not a rate anybody ever measured"
                            % (r["id"], r["desertion"]))
        if r["end"] - r["start"] > 4200 and "default" not in r["note"].lower():
            problems.append("%s runs for %d years without saying in its note that it is the "
                            "default: that is not a way of raising an army, it is the human "
                            "condition" % (r["id"], r["end"] - r["start"]))
        if not r["note"]:
            problems.append("%s: no reason given for its figures" % r["id"])

    # the two extremes of the table must actually differ, or the column is decoration
    coh = [r["cohesion"] for r in doc["raised"]]
    des = [r["desertion"] for r in doc["raised"]]
    if max(coh) - min(coh) < 20:
        problems.append("cohesion spread is only %d: the register is not distinguishing between "
                        "a citizen militia and a warlord band" % (max(coh) - min(coh)))
    if max(des) / max(0.1, min(des)) < 2.0:
        problems.append("desertion spread is too narrow to mean anything")

    # --------------------------------------------------------- the measured rates
    dids = [d["id"] for d in doc["desertion"]]
    if len(set(dids)) != len(dids):
        problems.append("duplicate desertion ids")
    if len(doc["desertion"]) < 8:
        problems.append("only %d measured desertion rates: this is a guess with footnotes"
                        % len(doc["desertion"]))
    for d in doc["desertion"]:
        if d["perYear"] is None and d["totalPct"] is None and d["count"] is None:
            problems.append("%s: carries no rate, no total and no count" % d["id"])
        if not d["src"]:
            problems.append("%s: no source" % d["id"])
        if d["mark"] == "estimated":
            problems.append("%s is a measured rate and may not be marked estimated" % d["id"])
        if d["perYear"] is not None and not (0.0 <= d["perYear"] <= 60.0):
            problems.append("%s: %s a year is not a desertion rate" % (d["id"], d["perYear"]))
        if not d["note"]:
            problems.append("%s: a number with no note is not a number" % d["id"])
    # the record's own range must be in the table somewhere
    per = [d["perYear"] for d in doc["desertion"] if d["perYear"] is not None]
    if per and (min(per) > 5.0 or max(per) < 12.0):
        problems.append("the measured annual rates run %s..%s and the record's own range runs "
                        "3.2 (Prussia) to 14.8 (US regulars)" % (min(per), max(per)))

    # --------------------------------------------------------- breaking
    bids = [b["id"] for b in doc["breaking"]]
    if len(set(bids)) != len(bids):
        problems.append("duplicate breaking ids")
    if not any(b["lossPct"] > 0.0 for b in doc["breaking"]):
        problems.append("nothing breaks on casualties in this register, and Krentz's 12 per "
                        "cent is the one measured breaking point there is")
    for b in doc["breaking"]:
        if not b["src"]:
            problems.append("%s: no source" % b["id"])
        if not b["note"]:
            problems.append("%s: no note" % b["id"])
        if not (0.0 <= b["lossPct"] <= 100.0):
            problems.append("%s: lossPct %s is not a share of an army" % (b["id"], b["lossPct"]))

    # --------------------------------------------------------- the pursuit is the whole point
    cas = doc["casualties"]
    if cas["loserPct"] <= cas["winnerPct"]:
        problems.append("the losers of a battle lose no more than the winners do, so this "
                        "register is modelling the fighting and not the battle")
    if cas["routAt"] <= cas["winnerPct"]:
        problems.append("an army routs before it has lost more than the winners lose, which "
                        "means every battle in the register is a rout")
    if cas["routAt"] > cas["loserPct"]:
        problems.append("an army is destroyed before the register will admit it has routed")
    break_at = [b for b in doc["breaking"] if b["id"] == "pursuit"]
    if break_at and abs(break_at[0]["lossPct"] - cas["loserPct"]) > 0.01:
        problems.append("the pursuit row says %.1f and the casualty block says %.1f: they are "
                        "the same figure and must agree"
                        % (break_at[0]["lossPct"], cas["loserPct"]))

    # --------------------------------------------------------- it spans the millennia
    empty = []
    for y in range(-1500, 2001, 500):
        if not any(r["start"] <= y <= r["end"] for r in rows):
            empty.append(y)
    if empty:
        problems.append("no morale factor in force in %s: the register has no answer there"
                        % ", ".join(str(y) for y in empty))

    est = sum(1 for r in rows if r["mark"] == "estimated")
    mix = sum(1 for r in rows if r["mark"] == "mixed")
    print("  factors  %2d: %2d recorded, %d mixed, %2d estimated"
          % (len(rows), len(rows) - est - mix, mix, est))
    print("  by kind:      %s" % ", ".join("%s %d" % (k, sum(1 for r in rows
                                                             if r["kind"] == k)) for k in KINDS))
    print("  by when:      %s" % ", ".join("%s %d" % (w, sum(1 for r in rows
                                                             if r["when"] == w)) for w in WHENS))
    print("  raised     %2d  cohesion %d..%d, desertion %.1f..%.1f a year"
          % (len(doc["raised"]), min(coh), max(coh), min(des), max(des)))
    print("  desertion  %2d: %s"
          % (len(doc["desertion"]), ", ".join(d["id"] for d in doc["desertion"])))
    print("  breaking   %2d: %s"
          % (len(doc["breaking"]), ", ".join("%s@%.0f%%" % (b["id"], b["lossPct"])
                                             for b in doc["breaking"])))
    print("  years: %d..%d" % (min(r["start"] for r in rows), max(r["end"] for r in rows)))
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
    print("  %d factors, %d raised, %d rates, %d ways of breaking; %d bytes raw, %d gzipped"
          % (len(doc["factors"]), len(doc["raised"]), len(doc["desertion"]),
             len(doc["breaking"]), len(raw), os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
