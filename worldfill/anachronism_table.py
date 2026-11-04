#!/usr/bin/env python3
"""
Step 47 part 3 (E8, E22): **vanilla things that do not belong, and what a year may use.**

    python3 anachronism_table.py        check the register and print it

E22's line in the plan is *"enchanting, potions, diamond and netherite gear, ender pearls: locked
or renamed by era, as a setting"*, decided in turns 73 to 81 for swords and **never built**. E8 is
the other half: *"what can be made or used in a year — a time traveller setting for exceptions"*.

## The distinction the register is built on

Minecraft contains three kinds of impossible thing, and they need three different answers. Treating
them all as "fantasy, remove it" would delete the game; treating them all as "allowed" would make
the year meaningless.

| kind | what it means | what the mod does |
|---|---|---|
| `real` | a real thing existed, the game's version is just better | **allowed**, from its year |
| `myth` | people believed in it. It existed as a belief, not as a function | **allowed and renamed**: the object is real, the power is not |
| `never` | nothing like it has ever existed, at any date | **locked** in a strict world, allowed for a time traveller |

That middle row is the one worth having. **Alchemy is real history**; a potion that cures wounds in
four seconds is not. So a brewing stand in 1300 is not an anachronism, it is **an alchemist's
bench**, and the register renames it rather than deleting it. The same is true of a diamond: gems
were traded from India to Rome, and a diamond sword is a **ceremonial** sword, not a better one.

## The dates that are real

Most of these have no date because they never existed. A few genuinely do:

- **Enchanting as a belief** is everywhere and always: amulets, curses, spoken charms. The words are
  recorded; the effects are not.
- **Alchemy** runs from Hellenistic Egypt to Newton, who wrote more on alchemy than on physics.
- **Gold as a soft decorative metal** is real, and a golden sword that is worse than iron is one of
  the few places vanilla accidentally agrees with history.
- **Diamonds** reach the Mediterranean from India by the 4th century BC, and are the hardest thing
  anyone had seen for two thousand years, and nobody made a sword of one.
"""

AREAS = ["EUR", "EEU", "WAS", "NAF", "CAS", "SAS", "EAS", "SEA", "WAF", "MSA", "EAF",
         "NNA", "MNA", "CAC", "SAM", "PAC", "AUS"]

KINDS = ["real", "myth", "never"]

# What the mod can do about a thing. `rename` keeps the item and changes the words.
ACTIONS = ["allow", "rename", "lock"]

# The two settings the world can be played in. E8's "time traveller" is the second.
SETTINGS = {
    "strict": "the world obeys its year: a thing from the future is locked for everybody",
    "traveller": "the player is an exception and may carry and use their own time's things, and is "
                 "seen doing it",
}

ROWS = [
    # ---- THE THREE THAT ARE REAL, AND ONLY MISDATED -------------------------------------
    dict(id="minecraft:golden_sword", kind="real", action="allow", year=-3000,
         myth=None, note=(
             "Gold is real, soft, and useless as a blade, and vanilla agrees: a golden sword is "
             "worse than iron. **This is the one anachronism the game got right by accident.** A "
             "golden sword is a display object in every century, and the register allows it from the "
             "first year."),
         source="vanilla material properties; gold in the archaeological record"),
    dict(id="minecraft:diamond", kind="real", action="rename", year=-300,
         myth="a stone of great hardness, worn and never used",
         note=(
             "Diamonds are real, and they reach the Mediterranean from India by about the 4th "
             "century BC: they are the hardest substance anyone had and **nobody made a tool of "
             "one** for two thousand years, because a diamond is brittle and a lapidary grinds it "
             "with its own dust. The register renames the item and allows the gem from 300 BC, and "
             "**the armour and the tool are not allowed**: a diamond pickaxe is a 20th-century "
             "invention wearing an ancient stone."),
         source="Wikipedia, diamond history; Pliny on adamas"),
    dict(id="minecraft:golden_apple", kind="myth", action="rename", year=-3000,
         myth="a fruit of eternal youth, in a golden dish",
         note=(
             "**Every culture has this object.** The apples of the Hesperides, the golden apples of "
             "Idunn, the peaches of immortality at Xi Wangmu's court. The register renames it to the "
             "local myth and **does not let it heal**: what a myth promises is not a mechanic, and a "
             "player who eats one in 1200 should not get regeneration out of a story."),
         source="Greek, Norse and Chinese myth cycles"),
    # ---- THE ONES THAT ARE REAL AS PRACTICE AND NOT AS POWER ---------------------------
    dict(id="minecraft:brewing_stand", kind="myth", action="rename", year=-2000,
         myth="an alchemist's bench",
         note=(
             "**Alchemy is real history and it is not magic.** It runs from Hellenistic Egypt through "
             "the Islamic world to Isaac Newton, who wrote more on alchemy than on physics, and it "
             "gave us distillation, the mineral acids and half of the laboratory. So a brewing stand "
             "in 1300 is not an anachronism: it is an alchemist's bench, and the register allows it "
             "from about 2000 BC and renames it. **What it may produce is a different question**, and "
             "one this register does not answer: a potion that closes a wound in four seconds is not "
             "in the historical record at any date."),
         source="Principe, The Secrets of Alchemy"),
    dict(id="minecraft:enchanting_table", kind="myth", action="rename", year=-3000,
         myth="a shrine, and a man who says the words",
         note=(
             "**The belief is universal and the effect is not.** Amulets, curses, blessings and "
             "spoken charms are in every literate culture from the beginning, and the words are "
             "recorded; no charm has ever been shown to work. The register keeps the table as a "
             "**shrine** and allows it everywhere from the first year, which is truer than locking "
             "it: people in 1000 BC did have shrines, and they did believe things happened at them."),
         source="Frazer's record of charms; Assyrian and Egyptian amulet collections"),
    dict(id="minecraft:potion", kind="myth", action="rename", year=-2000,
         myth="a draught, a tincture, a physick",
         note=(
             "A potion as an object is a Roman and medieval reality: the theriac, the mithridatium, "
             "the tonic. A potion as a **four-second cure** is not. Renamed and allowed as medicine "
             "from about 2000 BC; whether it works is step 38's health register, which is the only "
             "part of this project that should ever answer that."),
         source="Totelin on Greek and Roman pharmacy"),
    dict(id="minecraft:bookshelf", kind="real", action="allow", year=-3000,
         myth=None,
         note=(
             "A shelf of books, allowed from the first year, and **wrong before there are books**: "
             "step 47's own tool register dates paper to AD 105 in China and 1150 in Europe. The "
             "register allows the block and notes that the honest early form is a shelf of tablets, "
             "which is what a library was."),
         source="the products atlas: paper, clay_tablets, parchment"),
    # ---- THE ONES THAT ARE SIMPLY IMPOSSIBLE ------------------------------------------
    dict(id="minecraft:ender_pearl", kind="never", action="lock", year=None,
         myth="a throwing stone that returns, or a soul in a jar",
         note=(
             "**Nothing in the record throws a man across a room.** The nearest real object is the "
             "boomerang, which returns to the thrower and carries nobody, and the bola, which "
             "entangles. A pearl is a real and precious thing and an ender pearl is not: the "
             "register locks it in a strict world and allows it only for a time traveller, who is "
             "then seen doing it."),
         source="vanilla mechanics against the ethnographic record of throwing weapons"),
    dict(id="minecraft:netherite_ingot", kind="never", action="lock", year=None, myth=None,
         note=(
             "An alloy that does not exist, from a dimension that does not exist, and **the most "
             "anachronistic thing in the game**: it is better than diamond, which is itself fantasy "
             "as armour. Nothing about the Bronze Age collapse is improved by it."),
         source="vanilla"),
    dict(id="minecraft:elytra", kind="never", action="lock", year=None,
         myth="the wings of Daedalus, and the flying carpet",
         note=(
             "Flight is the oldest wish in the record and the last to arrive: the balloon is 1783 "
             "and step 46 dates it. **A pair of wings that let a person fly is never in the "
             "record**, only in the myths about what happens to people who try."),
         source="vanilla; the Icarus cycle"),
    dict(id="minecraft:totem_of_undying", kind="never", action="lock", year=None,
         myth="an object that brings a man back",
         note=(
             "Every army has carried something it believed would keep a man alive, and **none of "
             "them ever did**. The register locks it. A time traveller may carry one and will be "
             "seen carrying it, which is the honest result."),
         source="vanilla; amulet and standard history"),
    dict(id="minecraft:beacon", kind="never", action="lock", year=None,
         myth="a tower that reaches the sky",
         note=(
             "A beacon that grants powers is impossible. A **lighthouse** is not, and it is old: the "
             "Pharos of Alexandria, the Roman pharos at Dover. The register locks the beacon and "
             "notes that the historical object is a tower with a fire on it, which is what a player "
             "should build instead."),
         source="vanilla; the Pharos"),
    dict(id="minecraft:end_portal_frame", kind="never", action="lock", year=None, myth=None,
         note="A door to a place that does not exist. Locked in a strict world; the ender pearl and "
              "the eye of ender are locked with it, so the dimension is unreachable by ordinary play.",
         source="vanilla"),
    dict(id="minecraft:nether_portal", kind="never", action="lock", year=None, myth=None,
         note="As above, and this one matters more because the Nether is where the game's best "
              "resources are: a locked portal is a locked economy, not a locked decoration.",
         source="vanilla"),
    dict(id="minecraft:respawn_anchor", kind="never", action="lock", year=None, myth=None,
         note="A block that moves where a person comes back from the dead. Locked.",
         source="vanilla"),
    dict(id="minecraft:dragon_egg", kind="never", action="lock", year=None,
         myth="a dragon's egg, which is a thing in the record as a story",
         note="Dragons are in every mythology and their eggs are in none of them as objects. Locked "
              "in a strict world.",
         source="vanilla"),
    dict(id="minecraft:shulker_box", kind="never", action="lock", year=None, myth=None,
         note="A box that holds more than a box. Locked: the carrying capacity of a person is a "
              "real constraint and step 46's porter exists because of it.",
         source="vanilla"),
    # ---- THE ONES THAT ARE ORDINARY MAGIC IN THE GAME AND ORDINARY HISTORY IN LIFE ------
    dict(id="minecraft:redstone", kind="real", action="rename", year=-3000,
         myth="a signal in a stone, and a wire under the floor",
         note=(
             "Redstone is an invented mineral, but **the thing it stands for is real**: a stone that "
             "carries a signal. Lodestone was used for the compass from step 47's tool register, and "
             "a wire carrying a current is 19th-century. Renamed and allowed; what a player builds "
             "with it in 1200 is a mechanism, which is fair, because the Antikythera mechanism is "
             "2000 years old."),
         source="the products atlas: compasses; the Antikythera mechanism"),
    dict(id="minecraft:anvil", kind="real", action="allow", year=-1000, myth=None,
         note="An anvil is a real object from the Bronze Age, and the one in the game is a Roman "
              "pattern. Allowed from 1000 BC; the products atlas dates anvils itself.",
         source="the products atlas, anvils"),
]


def problems():
    bad = []
    seen = set()
    for r in ROWS:
        if r["id"] in seen:
            bad.append("duplicate row " + r["id"])
        seen.add(r["id"])
        if r["kind"] not in KINDS:
            bad.append(r["id"] + " has the kind " + str(r["kind"]))
        if r["action"] not in ACTIONS:
            bad.append(r["id"] + " has the action " + str(r["action"]))
        # THE INVARIANT. A thing that never existed cannot have a year, and a thing that is real
        # must have one, because "allowed from whenever" is not an answer.
        if r["kind"] == "never" and r["year"] is not None:
            bad.append(r["id"] + " never existed and yet has the year " + str(r["year"]))
        if r["kind"] in ("real", "myth") and r["year"] is None:
            bad.append(r["id"] + " is " + r["kind"] + " and has no year")
        if r["kind"] == "never" and r["action"] != "lock":
            bad.append(r["id"] + " never existed and is not locked")
        if r["action"] == "rename" and not r["myth"]:
            bad.append(r["id"] + " is renamed and does not say what to rename it to")
        # A locked row may name the myth it resembles, and should: the elytra and Icarus belong
        # together. What it must not do is carry a rename, because a rename means the object stays.
        if r["action"] == "lock" and r["kind"] != "never":
            bad.append(r["id"] + " is locked and yet is " + r["kind"] + ": only a thing that never "
                       "existed may be locked")
        if not r["note"] or len(r["note"]) < 60:
            bad.append(r["id"] + " does not say anything useful")
        if not r["source"]:
            bad.append(r["id"] + " cites nothing")
        if r["year"] is not None and not (-3000 <= r["year"] <= 3000):
            bad.append(r["id"] + " has the year " + str(r["year"]) + ", which is outside the world")

    # The three kinds must all be represented, or the table is not doing its job.
    for k in KINDS:
        if not any(r["kind"] == k for r in ROWS):
            bad.append("no row of the kind " + k + ": the table has stopped distinguishing")
    # And a renamed thing must keep its item: that is the whole point of renaming.
    ren = [r["id"] for r in ROWS if r["action"] == "rename"]
    if len(ren) < 5:
        bad.append("only " + str(len(ren)) + " rows are renamed: the register is deleting history "
                   "rather than translating it")
    return bad


def main():
    bad = problems()
    print("anachronisms: %d rows over %d kinds; %d allowed, %d renamed, %d locked"
          % (len(ROWS), len({r["kind"] for r in ROWS}),
             sum(1 for r in ROWS if r["action"] == "allow"),
             sum(1 for r in ROWS if r["action"] == "rename"),
             sum(1 for r in ROWS if r["action"] == "lock")))
    print("settings: " + "; ".join(k + " (" + v[:60] + ")" for k, v in SETTINGS.items()))
    print()
    for r in ROWS:
        print("  %-30s %-6s %-7s year=%-6s %s"
              % (r["id"].replace("minecraft:", ""), r["kind"], r["action"],
                 r["year"] if r["year"] is not None else "-", r["myth"] or ""))
    for p in bad:
        print("  PROBLEM " + p)
    print("anachronism_table: %d problem(s)" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
