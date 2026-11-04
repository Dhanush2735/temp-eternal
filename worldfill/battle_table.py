#!/usr/bin/env python3
"""Step 40 (D10 armies in action), part 3: the numbers behind how a battle comes out.

`war/BattleSimulator.java` decides a battle with one dice roll and then sets the losses at
**8% for the winner and 18% for the loser, unconditionally** — for Cannae and for a skirmish in
Flanders alike. That is the whole reason a battle in this mod tells you nothing.

This table is the replacement. It holds four things:

* **BANDS** — how many of each side are lost, by the arms of the era. Peter Krentz gathered every
  surviving casualty figure from Classical Greek sources and got about **5% for the winner and 14%
  for the loser**, honestly a range of **3–10% against 10–20%**. That is the anchor, and it is
  recorded;
* **BREAKS** — *how the loser goes*, which is what the 8/18 pair throws away. Most of the killing
  in pre-modern battle happened **after one side broke**, and the difference between a line that
  withdrew in order at dusk and one that ran in the open with cavalry behind it is the difference
  between 15% and half the army;
* **MATCHUP** — which kind of formation has the better of which, in points of probability.
  Estimated, and says so;
* **GROUND** — what it costs a formation to fight on ground it does not want.

The counter-intuitive finding, and the one worth stating in the register because a player will
assume the opposite: **casualty rates in land combat have been falling since the seventeenth
century.** Weapons got enormously more lethal and losses went down, because armies dispersed
faster than lethality rose. Dupuy's figures put the daily loss rate at about 21–23 per thousand in
the Napoleonic and Civil War eras — the Civil War being the exception that proved the rule, since
it threw massed formations against strong positions, "a violation of dispersion" — then 12 in the
First World War and 9 in the Second. So the rifle band below is *lower* than the musket band, and
that is deliberate.
"""

PURPOSES = ("shock", "hold", "missile", "envelope", "screen")
MARKS = ("recorded", "mixed", "estimated")


class Band:
    """How many of each side are lost, for the arms of the era."""

    def __init__(self, id, name, arms, wlo, whi, llo, lhi, note, src, mark):
        assert wlo <= whi and llo <= lhi, "%s: band upside down" % id
        assert 0.0 < wlo and whi < lhi, "%s: the winner must lose less than the loser" % id
        for a in arms:
            assert a in ("chariot", "spear", "pike", "javelin", "bow", "horsebow", "sword",
                         "elephant", "arquebus", "musket", "rifle", "cannon"), \
                "%s: unknown arm %s" % (id, a)
        assert src, "%s: no source" % id
        assert mark in MARKS, "%s: unknown mark %s" % (id, mark)
        self.id, self.name, self.arms = id, name, list(arms)
        self.wlo, self.whi, self.llo, self.lhi = wlo, whi, llo, lhi
        self.note, self.src, self.mark = note, src, mark


def _mk_break(id, name, mult, when, note, src, mark):
    """How the losing army goes, and what that costs it.

    The multiplier is applied to the loser's own band and to nothing else, because the winner is
    not being killed during the pursuit -- it is doing the killing.

    A multiplier **below 1 is allowed and means something**: the band is what a beaten army
    loses, and most of that is the pursuit, so an army that retreated in order, with its
    officers alive and its rear rank facing about, pays less than the band. Step 40 part 6 found
    the floor at 1.0 and every beaten army in the register was paying the full routed rate
    whatever how it went -- nothing ever retired in good order, and no loser was ever below
    Krentz's 12 per cent breaking point.
    """
    assert 0.3 <= mult <= 5.0, "%s: bad multiplier %s" % (id, mult)
    assert src and when and note, "%s: a way of losing has to say what it is" % id
    assert mark in MARKS, "%s: unknown mark %s" % (id, mark)
    return Break(id, name, mult, when, note, src, mark)


class Break:
    """One way of losing. Built by `_mk_break`, which checks it."""

    def __init__(self, id, name, mult, when, note, src, mark):
        self.id, self.name, self.mult = id, name, mult
        self.when, self.note, self.src, self.mark = when, note, src, mark


BANDS = [
    Band("shock", "spear and pike",
         ("chariot", "spear", "pike", "javelin", "sword", "elephant"),
         3.0, 10.0, 10.0, 20.0,
         "Krentz's survey of every surviving casualty figure from Classical Greek sources: the "
         "winner about 5%, the loser about 14%, honestly a range of 3-10 against 10-20. The gap "
         "between the two numbers is not marksmanship; it is that most of the killing is done "
         "after one side breaks and runs.",
         "Casualties in Hoplite Battles, Peter Krentz (GRBS), via the secondary discussion",
         "recorded"),

    Band("bow", "the bow",
         ("bow", "horsebow"),
         2.0, 6.0, 8.0, 18.0,
         "An army that fights by shooting and will not close keeps its own losses down and takes "
         "its profit when the other side comes apart. The steppe armies were almost always "
         "outnumbered and won by refusing to stand where they could be counted. This band is this "
         "table's reading: no survey of steppe casualty figures was found.",
         "Mongolian Warfare (the TOTA project), for the refusal to close",
         "estimated"),

    Band("musket", "the musket in close order",
         ("arquebus", "musket", "cannon"),
         8.0, 15.0, 18.0, 30.0,
         "Musket-era close order is the bloodiest band in this table, and Dupuy's figures are the "
         "reason: daily loss rates of about 21-23 per thousand in the Napoleonic period and the "
         "American Civil War, the Civil War being the case that proves the rule because it threw "
         "massed formations against strong defensive positions -- 'a violation of dispersion'. "
         "The band itself is this table's reading of those rates as a single-battle figure.",
         "Changes in Lethality and Casualty Rates (Air University, on Dupuy)",
         "estimated"),

    Band("rifle", "the rifle, dispersed",
         ("rifle",),
         4.0, 12.0, 12.0, 25.0,
         "Lower than the musket band, and deliberately so. Weapons became far more lethal and "
         "losses fell, because armies dispersed faster than lethality rose: Dupuy's daily loss "
         "rates run 12 in the First World War and 9 in the Second, against 21-23 in the "
         "Napoleonic and Civil War eras. Any register that assumes modern battle is bloodier than "
         "Napoleonic battle has this exactly backwards.",
         "Changes in Lethality and Casualty Rates (Air University, on Dupuy); "
         "Attrition In Future Land Combat (The Dupuy Institute)",
         "estimated"),
]

BREAKS = [
    _mk_break("withdrawn", "gave ground in order", 0.55,
              "the line goes back but keeps its order, its officers and its rear",
              "The cheapest way to lose, and the only one in this table that costs less than the "
              "band says. **The band is what a beaten army loses, and most of that is the "
              "pursuit** -- so an army that retreated in order, with its officers alive and its "
              "rearrank facing about, does not pay it. At 0.55 it loses a little more than the "
              "winner does and nothing like the routed rate, which is why the same army can lose "
              "three battles and still be an army. **Step 40 part 6 found this row at 1.0**: "
              "every beaten army in the register was then losing the full routed rate whatever "
              "how it went, so nothing ever retired in good order and no loser was ever below "
              "Krentz's 12 per cent breaking point.",
              "Casualties in Hoplite Battles, Peter Krentz (GRBS)", "mixed"),

    _mk_break("broken", "broke and ran", 1.5,
              "the line comes apart and the men go, but it is late, or dark, or there is cover",
              "The common case, and the one Krentz's 10-20% describes. Breaking is the event that "
              "decides the casualty list; everything before it is comparatively cheap.",
              "Casualties in Hoplite Battles, Peter Krentz (GRBS)", "mixed"),

    _mk_break("pursued", "broken in the open with horse behind it", 2.2,
              "it breaks in daylight on open ground and the winner has the cavalry to run it down",
              "Most of the killing in pre-modern battle happened here, after the fighting had "
              "stopped and one side was merely being destroyed. Thirty per cent was very common; "
              "Krentz notes the Greeks did not usually pursue far, which is part of why their "
              "figures stay as low as they do.",
              "Casualties in Hoplite Battles, Peter Krentz (GRBS)", "estimated"),

    _mk_break("surrounded", "encircled, with nowhere to go", 3.2,
              "both flanks are turned and there is no line to fall back to",
              "The rarest and the worst: where the losing army was surrounded at the end the rate "
              "could approach the whole of it. A commander who lets this happen to a conscript "
              "army does not have an army afterwards, whatever the survivors are called.",
              "Casualties in Hoplite Battles, Peter Krentz (GRBS)", "estimated"),
]

# Which kind of formation has the better of which, in points of probability. Estimated: three of
# these pairings are attested in the sources read for part 2 -- the Roman line beat the phalanx,
# the Swedish brigade beat the tercio at Breitenfeld, and the tercio was built to answer the
# Swiss square -- and the rest is this table's reading of what those three have in common.
MATCHUP = {
    ("envelope", "hold"): 0.08,     # going round a steady line is how steady lines die
    ("envelope", "shock"): 0.05,
    ("hold", "shock"): 0.06,        # pikes stop horses
    ("shock", "missile"): 0.08,     # closing is the answer to shooting, if you can close
    ("shock", "screen"): 0.06,
    ("missile", "shock"): -0.08,
    ("missile", "hold"): -0.04,
    ("screen", "hold"): 0.03,
    ("screen", "shock"): -0.06,
    ("hold", "missile"): 0.04,
    ("shock", "hold"): -0.06,
    ("hold", "envelope"): -0.08,
    ("shock", "envelope"): -0.05,
    ("missile", "envelope"): -0.03,
    ("envelope", "missile"): 0.03,
    ("screen", "missile"): 0.02,
    ("missile", "screen"): -0.02,
    ("envelope", "screen"): 0.04,
    ("screen", "envelope"): -0.04,
    ("hold", "screen"): -0.03,
}

# What it costs a formation to fight on ground it does not want. Estimated, and small on purpose:
# ground decides battles by a few points of probability, not by arithmetic.
GROUND_COST = {
    ("level", "broken"): -0.10,     # a phalanx in rough country is not a phalanx
    ("level", "open"): -0.02,
    ("open", "broken"): -0.06,      # horse and guns want room
    ("open", "level"): 0.0,
    ("broken", "open"): -0.03,
    ("broken", "level"): -0.01,
    ("any", "broken"): 0.0,
    ("any", "open"): 0.0,
    ("any", "level"): 0.0,
}
GROUND_BONUS = 0.02                 # fighting on the ground you want
GROUNDS = ("level", "open", "broken", "any")

# How far the dice can swing it. A battle is not determined by arithmetic, and a register that
# says it is will produce the same winner every time.
# ---------------------------------------------------------------- how a beaten army goes
#
# Krentz's survey establishes the two ends -- a withdrawal in good order costs the loser 10-20%,
# a rout with cavalry behind it costs 30% and more -- and it establishes that most battles sit
# near the low end, since the average is about 14%. It says nothing about how often each happens.
# These numbers are this table's reading, and they are here rather than in the Java so that
# anyone who disagrees can change them in one place.
ROUT_MORALE = 50        # below this, a beaten line cannot reform, whatever its officers say
ROUT_SUPPLY = 35        # nor can a hungry one
ROUT_RATIO = 1.5        # nor can one outnumbered by this much: it has no line to hold
INTACT_MORALE = 55      # at or above this, and fed, a beaten line gets away more often than not
INTACT_SUPPLY = 45
ESCAPE_CHANCE = 0.75    # ...but "more often than not" is not "always": two defeats that look
                        # identical on paper end differently, and that is its own dice roll
SURROUNDED_ODDS = 0.15  # a verdict this clear, with both flanks turned, is an encirclement
PURSUED_ODDS = 0.08     # and this clear, with something faster behind it, is a pursuit
NARROW_ODDS = 0.10      # a verdict this narrow is a withdrawal, whatever the armies were
CEILING = 0.85          # nothing on record loses more than this and is still called an army

ROLL_LOW = 0.05
ROLL_HIGH = 0.95

# Below this share of its own number, an army is not an army any more.
SHATTERED = 0.45


def check():
    problems = []
    ids = [b.id for b in BANDS]
    if len(set(ids)) != len(ids):
        problems.append("duplicate band ids")
    for b in BANDS:
        # Krentz's bands touch -- 3-10% against 10-20% -- so abutting is allowed; overlapping
        # is not. A register in which the winner can lose more than the loser is broken.
        if b.whi > b.llo:
            problems.append("%s: the winner can lose more than the loser: %s%% over %s%%"
                            % (b.id, b.whi, b.llo))
        if b.lhi > 95.0:
            problems.append("%s: a band cannot reach %s%%" % (b.id, b.lhi))
    arms = sorted(set(b.id for b in BANDS))
    if len(arms) != len(BANDS):
        problems.append("band ids are not unique")
    seen = {}
    for b in BANDS:
        for a in b.arms:
            if a in seen:
                problems.append("arm %s is in two bands: %s and %s" % (a, seen[a], b.id))
            seen[a] = b.id
    for (x, y), v in MATCHUP.items():
        assert x in PURPOSES and y in PURPOSES, "unknown purpose in matchup %s/%s" % (x, y)
        if (y, x) in MATCHUP and abs(MATCHUP[(y, x)] + v) > 0.011:
            problems.append("matchup %s/%s is %+.2f but the reverse is %+.2f: they must cancel"
                            % (x, y, v, MATCHUP[(y, x)]))
    for (w, g) in GROUND_COST:
        assert w in GROUNDS and g in GROUNDS, "unknown ground in %s" % ((w, g),)
    bks = [k.id for k in BREAKS]
    if len(set(bks)) != len(bks):
        problems.append("duplicate break ids")
    if len(BREAKS) < 3:
        problems.append("a register that only knows one way to lose is the old one")
    return problems
