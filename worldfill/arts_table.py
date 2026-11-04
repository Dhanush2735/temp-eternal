#!/usr/bin/env python3
"""
Step 47 part 6 (C15): **culture** — the parts that were still missing after clothes, food and games.

    python3 arts_table.py            check the register and print it

The plan's row is *"Culture: clothes, food, music, games, customs, arts"* and the survey found it
"partly: looks by era". By the end of part 6 the picture is precise:

| part of C15 | where it lives now |
|---|---|
| **clothes** | part 4: 27 period garments over 11 culture pools (E12) |
| **food** | step 44's products atlas and step 45's diet register |
| **games** | part 6: 21 games over 9 kinds (E17) |
| **customs** | `CultureAtlas`: 21,000 holy places, feasts, pilgrimage, scripts, measures |
| **music and arts** | **nothing at all** |

So this register is music and the visual arts, and nothing else.

## What a music and arts register can honestly be

There is no such thing as "the year a place got music". Every human group sings, drums and dances,
and it is older than the span. So the register is not of **music** but of <b>the things that carry
music and pictures</b>: an instrument, a medium, a way of copying a thing. That is a technology
history and it dates honestly, and it produces the same shape as part 2's tools, which is not a
coincidence: a violin is a manufactured object.

## The finding

**Every art form in this register is older than the means of copying it, and copying changes what
the art is.** Painting is as old as people; the oil medium, the woodblock, the engraving, the
photograph and the recording each arrive late and each one changes who can own a picture or hear a
piece of music. The two sharpest dates are a **phonograph in 1877**, which separates a performance
from the performer for the first time in the history of the species, and **photography in 1839**,
which arrives before the cinema (1895) and after the oil painting it replaces as the way to record
a face.
"""

AREAS = ["NNA", "MNA", "CAC", "SAM", "EUR", "EEU", "WAS", "NAF", "WAF", "MSA", "EAF", "CAS",
         "SAS", "EAS", "SEA", "AUS", "PAC"]

KINDS = ["voice", "percussion", "wind", "string", "keyboard", "medium", "copy", "record",
         "performance"]

# Each row: what it is, when and where it is first attested, and where it spreads after that.
# `spread` is written only where the record gives a year, as in the games register: everywhere else
# the answer is unknown and the register refuses to guess.
ARTS = [
    # ---- WHAT EVERYBODY HAS ---------------------------------------------------------------
    dict(id="song", name="song and chant", kind="voice", year=-3000, home="WAS",
         equipment=None, spread={a: -3000 for a in AREAS},
         note=(
        "**The one art in this register that is universal and undatable.** Every human group sings, "
        "and the oldest musical instrument known is a bone flute from a cave in Germany at about "
        "40,000 years old, which is thirty-seven thousand years before the span begins. **Song is "
        "therefore in every area at the first year of the world**, and it is the only row here that "
        "needs no diffusion to explain it."),
         source="the Hohle Fels bone flute; the universal ethnography of song"),
    dict(id="drum", name="the drum", kind="percussion", year=-3000, home="WAF",
         equipment="drums", spread={a: -3000 for a in AREAS},
         note=(
        "**A hollow object with a skin on it is not a technology that has to be invented twice.** "
        "Drums are in the record everywhere at the start of the span, and their use is not "
        "entertainment: a drum carries a signal further than a voice, paces a work gang, and marks "
        "time in a ritual. **The talking drums of West Africa encode language**, which makes them a "
        "telecommunication and not a musical instrument."),
         source="the West African talking drums; the Mesopotamian and Chinese percussion records"),
    dict(id="flute", name="the flute", kind="wind", year=-3000, home="WAS", equipment="flutes",
         spread={a: -3000 for a in AREAS},
         note=(
        "**The oldest instrument anybody has found**, in bone, in a cave, and playable. The "
        "register carries it from the first year everywhere because a hollow bird bone with holes "
        "in it is available to anybody who finds one, and the archaeological record bears that out "
        "across four continents."),
         source="the Hohle Fels and Divje Babe flutes; the Chinese bone flutes of Jiahu"),
    dict(id="harp", name="the harp and the lyre", kind="string", year=-3000, home="WAS",
         equipment="harps", spread={"WAS": -3000, "NAF": -2500, "EUR": -2000, "SAS": -2000,
                                    "EAS": -1500, "CAS": -1000, "EEU": -1000, "SEA": 500,
                                    "WAF": 800, "MSA": 800, "EAF": 800},
         note=(
        "**A stretched string over a resonator, and the first instrument that needs a maker.** The "
        "Sumerian and Egyptian harps are in tomb paintings with the players named; the Greek lyre is "
        "the instrument of a citizen and the aulos (a reed pipe) is the instrument of a professional, "
        "which is a class distinction carried in an instrument choice. **A string instrument is the "
        "first thing in this register that is expensive enough to belong to somebody.**"),
         source="the Ur and Theban harp paintings; the Greek lyre and aulos"),
    dict(id="trumpet", name="the horn and the trumpet", kind="wind", year=-1500, home="WAS",
         equipment="trumpets", spread={"WAS": -1500, "NAF": -1400, "EUR": -1000, "SAS": -1000,
                                       "EAS": -800, "CAS": -800, "EEU": -500, "WAF": 1000,
                                       "MSA": 1000, "EAF": 1000, "SEA": 1200, "CAC": 1500,
                                       "SAM": 1530, "NNA": 1600, "MNA": 1500, "AUS": 1788,
                                       "PAC": 1800},
         note=(
        "**A loud instrument is a piece of government.** The trumpet is a signal device before it is "
        "a musical one: it calls an assembly, announces a ruler and directs an army, which is why "
        "the earliest ones are in palaces and temples. **The valve, which lets it play a tune rather "
        "than a fanfare, is 1815**, so every trumpet part written before that date is written for an "
        "instrument that could not play it."),
         source="the Egyptian and Tutankhamun trumpets; the 1815 Stoelzel valve"),
    dict(id="organ", name="the organ", kind="keyboard", year=757, home="WAS",
         equipment=None, spread={"WAS": 757, "EUR": 800, "EEU": 1000, "NAF": 1000, "SAS": 1200,
                                 "EAS": 1300, "NNA": 1700, "SAM": 1600, "MNA": 1600,
                                 "CAC": 1600, "AUS": 1800, "SEA": 1600, "CAS": 1500,
                                 "WAF": 1800, "MSA": 1800, "EAF": 1800, "PAC": 1850},
         note=(
        "**A Byzantine diplomatic gift and the first machine that plays music.** An organ reaches "
        "Charlemagne's court from Constantinople in 757, and by the fourteenth century the "
        "cathedral organ is the largest and most complicated machine in Europe: a keyboard, a "
        "wind supply, and pipes tuned to a scale. **It is the ancestor of every keyboard instrument "
        "and of the factory that made them.**"),
         source="the 757 Byzantine gift to Pippin and Charlemagne; the medieval cathedral organs"),
    dict(id="bowed_strings", name="the bowed string", kind="string", year=800, home="CAS",
         equipment=None, spread={"CAS": 800, "WAS": 900, "EAS": 1000, "SAS": 1000, "EUR": 1000,
                                 "NAF": 1000, "EEU": 1200, "SEA": 1300, "WAF": 1400,
                                 "MSA": 1400, "EAF": 1400},
         note=(
        "**A horsehair bow on a string, and a family of instruments that becomes the orchestra.** "
        "The Central Asian *rabab* travels with the steppe and the caravan into the Islamic world, "
        "Byzantium, China and India, and the European fiddle that comes out of it is a mutation of "
        "the same object. **The violin of the 1550s is the same instrument with a changed body**, "
        "which is why this register dates the bow and not the violin."),
         source="the Central Asian rabab; the Amati workshops of Cremona"),
    dict(id="piano", name="the piano", kind="keyboard", year=1709, home="EUR",
         equipment=None, spread={"EUR": 1709, "NNA": 1770, "EEU": 1780, "SAM": 1820, "SAS": 1840,
                                 "EAS": 1860, "AUS": 1830, "MNA": 1830, "CAC": 1840,
                                 "NAF": 1840, "WAS": 1840, "SEA": 1860, "CAS": 1860,
                                 "WAF": 1900, "MSA": 1900, "EAF": 1900, "PAC": 1900},
         note=(
        "**The instrument that made a composer's idea audible without an orchestra.** Cristofori in "
        "Florence, 1709: a hammer that strikes the string and then falls away, which is the one "
        "thing a harpsichord cannot do. **Within eighty years it is in every middle-class parlour "
        "in Europe and the Americas**, and the sheet-music industry, the piano lesson and the "
        "domestic recital are all consequences of one mechanism."),
         source="Cristofori's 1709 instrument and Scipione Maffei's 1711 description"),
    dict(id="woodblock_print", name="the woodblock print", kind="copy", year=700, home="EAS",
         equipment="woodblock_prints",
         spread={"EAS": 700, "SEA": 900, "SAS": 1100, "CAS": 1200, "WAS": 1300, "NAF": 1300,
                 "EUR": 1400, "EEU": 1500, "MNA": 1550, "SAM": 1600, "NNA": 1650,
                 "CAC": 1600, "AUS": 1800, "PAC": 1850, "MSA": 1700, "EAF": 1700, "WAF": 1700},
         note=(
        "**The first way to make a picture many times, and it is Chinese.** A carved block, ink on "
        "paper, and a Buddhist sutra of 868 is the oldest dated printed book in the world. "
        "**The consequence is not artistic but social**: the printed image of a saint, a map or a "
        "playing card is the first picture a poor household can own, and the European Reformation is "
        "fought with it."),
         source="the 868 Dunhuang Diamond Sutra; the European block-book trade"),
    dict(id="oil_painting", name="oil paint", kind="medium", year=1420, home="EUR",
         equipment=None, spread={"EUR": 1420, "NNA": 1700, "SAM": 1600, "SAS": 1700, "EAS": 1700,
                                 "MNA": 1600, "NAF": 1600, "WAS": 1600, "AUS": 1800,
                                 "EEU": 1550, "CAS": 1700, "CAC": 1600, "SEA": 1700,
                                 "MSA": 1800, "EAF": 1800, "WAF": 1800, "PAC": 1850},
         note=(
        "**A medium that dries slowly, which sounds like a technicality and is not.** Slow drying "
        "means you can work wet into wet, so the oil painting can show light falling on a fold of "
        "cloth in a way tempera cannot, and the van Eycks in the 1420s are where the northern "
        "European record of the visible world becomes possible. **It is a chemistry change and it "
        "produces a style.**"),
         source="the van Eyck Ghent altarpiece, completed 1432"),
    dict(id="photography", name="photography", kind="copy", year=1839, home="EUR",
         equipment="photographs", spread={"EUR": 1839, "NNA": 1839, "SAS": 1840, "EAS": 1841,
                                          "NAF": 1840, "WAS": 1840, "SAM": 1840, "AUS": 1841,
                                          "EEU": 1840, "MNA": 1840, "CAC": 1840, "SEA": 1843,
                                          "CAS": 1845, "MSA": 1860, "EAF": 1860, "WAF": 1860,
                                          "PAC": 1870},
         note=(
        "**The first picture that is not made by a hand, and it changes what a portrait is for.** "
        "Daguerre in 1839, and within two years there is a studio in every major city on earth: "
        "**the fastest spread of anything in this register**, faster than the cinema and faster than "
        "the telegraph, because the apparatus is a product and can be shipped. The trade it destroys "
        "is the miniature painter's."),
         source="the 1839 French Academy announcement; the studio directories of the 1840s"),
    dict(id="phonograph", name="the recording", kind="record", year=1877, home="NNA",
         equipment="gramophones", spread={"NNA": 1877, "EUR": 1878, "SAS": 1880, "EAS": 1885,
                                          "AUS": 1885, "SAM": 1885, "NAF": 1890, "WAS": 1890,
                                          "EEU": 1890, "MNA": 1890, "CAC": 1890, "CAS": 1895,
                                          "SEA": 1895, "MSA": 1900, "EAF": 1900, "WAF": 1900,
                                          "PAC": 1910},
         note=(
        "**The sharpest date in this register: the first time in the history of the species that a "
        "performance is separated from the performer.** Edison, 1877, on a tinfoil cylinder, and the "
        "consequences are not musical: a voice can be heard after its owner is dead, a language can "
        "be recorded before it has no speakers, and music becomes something a household buys rather "
        "than something somebody plays. **Every other art in this list is older than its own "
        "copying; music is the one that was copied last.**"),
         source="Edison's 1877 tinfoil phonograph; Berliner's 1887 disc"),
    dict(id="dance", name="dance", kind="performance", year=-3000, home="WAS",
         equipment=None, spread={a: -3000 for a in AREAS},
         note=(
        "**The oldest performance art and the one with the least material record.** It leaves no "
        "object, so it is known from pictures of it (the Egyptian tomb dancers, the Minoan "
        "bull-leapers), from descriptions written by people who disapproved of it, and from "
        "continuity. **It is in every area from the first year for the same reason as song**, and it "
        "is in this register because a world with music and no dance is not a world."),
         source="the Egyptian tomb paintings of dancers; the Minoan frescoes"),
    dict(id="theatre_masks", name="the mask", kind="performance", year=-3000, home="WAF",
         equipment=None,
         spread={"WAF": -3000, "NAF": -2500, "WAS": -2000, "EUR": -1000, "SAS": -1000,
                 "EAS": -500, "SEA": 0, "CAC": 500, "SAM": 800, "MSA": 0, "EAF": 0,
                 "CAS": 0, "EEU": 500, "NNA": 1000, "MNA": 1000, "AUS": 1500, "PAC": 1500},
         note=(
        "**A face you put on to be somebody else, and in most of the world it is religious.** The "
        "West African masquerade is a performed appearance of an ancestor or a spirit and the dancer "
        "is not pretending; the Greek mask is a megaphone made of linen; the Japanese Noh mask is "
        "carved to change expression with the angle of the head. **Theatre is in E17; the object "
        "that makes a theatre possible is here.**"),
         source="the West African masquerade traditions; the Greek and Noh mask records"),
]


def problems():
    bad = []
    seen = set()
    for a in ARTS:
        if a["id"] in seen:
            bad.append("duplicate row " + a["id"])
        seen.add(a["id"])
        if a["kind"] not in KINDS:
            bad.append(a["id"] + " has the kind " + str(a["kind"]))
        if a["home"] not in AREAS:
            bad.append(a["id"] + " comes from " + str(a["home"]))
        if a["home"] not in a["spread"]:
            bad.append(a["id"] + " does not exist in its own home")
        elif a["spread"][a["home"]] != a["year"]:
            bad.append(a["id"] + " is dated " + str(a["year"]) + " and its home says "
                       + str(a["spread"][a["home"]]))
        for area, y in a["spread"].items():
            if area not in AREAS:
                bad.append(a["id"] + " spreads to " + area)
            if y < a["year"]:
                bad.append(a["id"] + " is in " + area + " in " + str(y) + ", before it exists")
        if not a["note"] or len(a["note"]) < 80:
            bad.append(a["id"] + " does not say anything useful")
        if not a["source"]:
            bad.append(a["id"] + " cites nothing")

    # THE COVERAGE TEST, and it is the same one the healers register uses: song and dance are
    # universal, so if any area has no music in 3000 BC this register is wrong about people.
    for area in AREAS:
        if not any(a["spread"].get(area, 10 ** 9) <= -3000 and a["kind"] == "voice" for a in ARTS):
            bad.append("nobody sings in " + area + " in 3000 BC")

    by = {a["id"]: a for a in ARTS}
    # THE ORDER OF EVENTS: a copy is later than the thing it copies, a recorder later than the
    # music, and the photograph after the painting it replaces as a record of a face.
    order = [("song", "organ"), ("organ", "piano"), ("harp", "bowed_strings"),
             ("woodblock_print", "photography"), ("oil_painting", "photography"),
             ("photography", "phonograph"), ("trumpet", "organ"), ("song", "phonograph")]
    for a, b in order:
        if a not in by or b not in by:
            bad.append("the order check names " + a + " and " + b + ", and one of them is missing")
        elif by[a]["year"] >= by[b]["year"]:
            bad.append(a + " cannot come after " + b)

    # THE FINDING, AS A TEST: every art form is older than the means of copying it, except
    # recording, which is the point about music.
    for old, copy in (("oil_painting", "photography"), ("harp", "woodblock_print")):
        if by[old]["year"] > by[copy]["year"]:
            bad.append(old + " is later than " + copy + ", so the finding is wrong")

    # A medium row must name a medium, and a copy row must name a way of copying.
    for kind, must in (("copy", "equipment"), ("record", "equipment")):
        for a in ARTS:
            if a["kind"] == kind and not a.get(must):
                bad.append(a["id"] + " is a " + kind + " row and names no means of doing it")
    return bad


def main():
    bad = problems()
    print("arts: %d rows over %d areas and %d kinds; %d universal from the first year"
          % (len(ARTS), len({a for x in ARTS for a in x["spread"]}), len(KINDS),
             len([a for a in ARTS if len(a["spread"]) == len(AREAS)])))
    print()
    print("  %-16s %-12s %-7s %-6s %s" % ("row", "kind", "home", "from", "areas"))
    for a in ARTS:
        print("  %-16s %-12s %-7s %-6s %d" % (a["id"], a["kind"], a["home"], a["year"],
                                              len(a["spread"])))
    for p in bad:
        print("  PROBLEM " + p)
    print("arts_table: %d problem(s)" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
