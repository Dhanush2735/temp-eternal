"""Step 37 (C29): what people knew or believed, by era and place.

Why this file exists
--------------------
The mod knows what happened and who ruled. It has never had the faintest idea what anybody
*thought*. That is the difference between a chronicle and a place: walk into a village in 1348
and the first thing you meet is not a date, it is what the villagers believe about the sickness
in the next valley — bad air, God's anger, an imbalance of the humours.

This is the table of those. It is hand-written, on the discipline of step 36's disaster
supplement and step 37's calendar table:

    No source, no row.

Every row carries the Wikipedia article it came from. If a belief cannot be sourced it does not
go in, however vivid.

Rules for a row
---------------
1. `now` is what a player from today would say. Sometimes it is the same as `belief` — the table
   is about what was believed, and sometimes what was believed was right, and the interesting
   thing is *when* it became the common view.
2. `who` is not decoration. C29 asks what **educated** people believed, and that was often not
   what the street believed and sometimes not what a handful of scholars believed either.
   EDUCATED  the learned consensus of the place: the physicians, the clerks, the priests, the
             astronomers
   EVERYONE  held as much in the fields as in the schools
   SCHOLARS  a minority of the learned, against the consensus of their own time
3. Boxes may overlap; every matching row contributes. Empty boxes means the whole world.
4. `to` of None means it is still held somewhere.
5. Do not write a row to make a point about how silly the past was. Several of these were
   reasonable given what could be observed at the time — that is the whole reason they were
   believed — and a row that sneers is a row that lies.
"""

EDUCATED = "educated"
EVERYONE = "everyone"
SCHOLARS = "scholars"

# --- named boxes, so a row reads -------------------------------------------------------------
OLD_WORLD = [(20.0, 60.0, -12.0, 45.0), (12.0, 45.0, 25.0, 63.0)]   # the Mediterranean, the Levant, Persia
EUROPE = [(36.0, 71.0, -11.0, 40.0)]
MIDEAST = [(12.0, 42.0, 25.0, 63.0)]
SOUTH_ASIA = [(5.0, 37.0, 60.0, 93.0)]
EAST_ASIA = [(20.0, 53.0, 100.0, 146.0)]
CHINA = [(20.0, 53.0, 100.0, 125.0)]
AFRICA = [(-35.0, 16.0, -18.0, 52.0)]
AMERICAS = [(-56.0, 72.0, -170.0, -34.0)]
WORLD = []


class B:
    __slots__ = ("id", "belief", "now", "frm", "to", "who", "boxes", "note", "src")

    def __init__(self, id, belief, now, frm, to, who, boxes, note, src):
        assert src, "every row needs a source article: " + id
        assert -3000 <= frm <= 2100, "year out of range: " + id
        assert to is None or frm <= to, "ends before it starts: " + id
        assert who in (EDUCATED, EVERYONE, SCHOLARS), "unknown who %r in %s" % (who, id)
        for bx in boxes:
            lat0, lat1, lon0, lon1 = bx
            assert -90 <= lat0 < lat1 <= 90, "bad latitude box in " + id
            assert -180 <= lon0 < lon1 <= 180, "bad longitude box in " + id
        self.id, self.frm, self.to, self.who = id, frm, to, who
        self.belief, self.now, self.boxes, self.note, self.src = belief, now, boxes, note, src

    def as_dict(self):
        d = {"id": self.id, "belief": self.belief, "now": self.now, "who": self.who,
             "from": self.frm, "to": self.to, "source": self.src}
        if self.boxes:
            d["boxes"] = [[b[0], b[1], b[2], b[3]] for b in self.boxes]
        if self.note:
            d["note"] = self.note
        return d


# --- the table -----------------------------------------------------------------------------

BELIEFS = [

    # ------------------------------------------------------------------ the shape of the world
    B("spherical_earth",
      "the world is a sphere",
      "which is so",
      -300, None, EDUCATED, OLD_WORLD + SOUTH_ASIA + EAST_ASIA,
      "The story that educated people in the Middle Ages thought the earth was flat is a "
      "nineteenth-century invention; from the third century BCE onwards every learned tradition "
      "of the Old World knew the earth was round, and Eratosthenes had measured it.",
      "Myth of the flat Earth"),

    B("geocentrism",
      "the earth stands still and the sun goes round it",
      "the earth goes round the sun",
      -300, 1686, EDUCATED, WORLD,
      "Aristarchus proposed a moving earth in the third century BCE and was not believed; "
      "Ptolemy's model held for eighteen hundred years, and it predicted the planets well "
      "enough to be used by navigators.",
      "Geocentric model"),

    B("rotating_earth_india",
      "the earth turns on its axis and the stars stand still",
      "which is so",
      499, 1200, SCHOLARS, SOUTH_ASIA,
      "Aryabhata, in 499. The astronomers who followed him argued against it and the "
      "consensus of India went back to a still earth.",
      "Aryabhata"),

    B("heliocentrism",
      "the earth goes round the sun",
      "which is so",
      1687, None, EDUCATED, WORLD,
      "Copernicus put it forward in 1543 and was argued with for a century; Newton's "
      "Principia of 1687 is where it stops being a proposal and becomes the consensus.",
      "Heliocentrism"),

    B("young_earth",
      "the world was made a few thousand years ago",
      "the earth is about 4.5 thousand million years old",
      1650, 1850, EDUCATED, OLD_WORLD + EUROPE,
      "Ussher's chronology of 1650 put the creation at 4004 BCE. It was a serious piece of "
      "scholarship, worked out from the scriptures by a man who had read everything; the "
      "geologists of the 1780s onward simply found the rocks would not fit it.",
      "Ussher chronology"),

    B("deep_time",
      "the earth is immensely old, and the rocks are its record",
      "which is so",
      1788, None, EDUCATED, EUROPE + OLD_WORLD + SOUTH_ASIA + EAST_ASIA,
      "Hutton's Theory of the Earth in 1788, then Lyell: 'no vestige of a beginning, no "
      "prospect of an end'.",
      "Age of the Earth"),

    B("fixed_continents",
      "the continents have always stood where they stand",
      "they move, an inch or two in a year",
      -3000, 1959, EDUCATED, OLD_WORLD + EUROPE,
      "Wegener proposed drift in 1912 with the fossil and rock evidence in front of him and "
      "was refused for fifty years because he could not say what pushed them. The box is the "
      "Old World and Europe on purpose: elsewhere the question was not framed in these terms "
      "at all, and this register would rather say nothing than put a European argument in a "
      "mouth that never made it.",
      "Continental drift"),

    B("plate_tectonics",
      "the continents move, carried on the floor of the sea",
      "which is so",
      1960, None, EDUCATED, WORLD,
      "Seafloor spreading settled the argument Wegener could not.",
      "Plate tectonics"),

    # ------------------------------------------------------------------ the body and its illness
    B("four_humours",
      "illness is an imbalance of the four humours",
      "illness has causes: a germ, a poison, a failure of the body",
      -400, 1858, EDUCATED, OLD_WORLD + EUROPE + MIDEAST,
      "Blood, phlegm, yellow bile, black bile. Greek, carried into Islam and into Europe, and "
      "it was a system: it told you what to do, and the treatment followed from the "
      "diagnosis. It lasted two thousand years because it was the best account anyone had.",
      "Humorism"),

    B("three_doshas",
      "illness is an imbalance of the three doshas",
      "illness has causes: a germ, a poison, a failure of the body",
      -600, None, EDUCATED, SOUTH_ASIA,
      "Vata, pitta, kapha. Still the frame of Ayurveda today, alongside every modern "
      "hospital in the same street.",
      "Dosha"),

    B("miasma",
      "bad air brings the fever",
      "the fever is carried by a mosquito, or in the water",
      -400, 1880, EVERYONE, WORLD,
      "Malaria means 'bad air', and the observation behind it was sound: people who slept "
      "near the marsh did sicken. What the theory got wrong was the agent.",
      "Miasma theory"),

    B("germ_theory",
      "illness is carried by living things too small to see",
      "which is so",
      1880, None, EDUCATED, WORLD,
      "Pasteur and Koch in the 1880s. Snow had shown it for cholera in 1854 by mapping a "
      "pump handle in Soho, and was not believed for thirty years.",
      "Germ theory of disease"),

    B("bloodletting",
      "letting blood cures what ails you",
      "it does not, and it kills",
      -400, 1900, EDUCATED, WORLD,
      "The most durable single practice in the history of medicine, and it followed from "
      "the humours: if the illness is a surfeit, the cure is to take some away.",
      "Bloodletting"),

    B("jinn",
      "illness and madness can come from the jinn",
      "illness has causes: a germ, a poison, a failure of the body",
      600, None, EVERYONE, MIDEAST + AFRICA + SOUTH_ASIA,
      "Held across the Islamic world and by Muslims in South Asia, and still, in the "
      "ordinary sense of the word, today.",
      "Jinn"),

    B("spontaneous_generation",
      "maggots come of themselves out of rotting meat",
      "they come from eggs",
      -300, 1859, EDUCATED, WORLD,
      "Redi had half-disproved it in 1668 with a piece of gauze; Pasteur's flasks in 1859 "
      "finished it.",
      "Spontaneous generation"),

    B("ulcer_stress",
      "ulcers come from worry and from the acid of the stomach",
      "they come from a bacterium, and a course of antibiotics cures them",
      1910, 1982, EDUCATED, WORLD,
      "Barry Marshall drank the bacterium in 1984 to prove it, and got the ulcer he predicted "
      "and a Nobel prize in 2005. This is the one row in this table about a belief that was "
      "held by people who are still alive.",
      "Helicobacter pylori"),

    # ------------------------------------------------------------------ what things are made of
    B("four_elements",
      "everything is made of earth, water, air and fire",
      "of a hundred-odd elements, and they are made of atoms",
      -500, 1789, EDUCATED, OLD_WORLD + EUROPE,
      "Aristotle's, and it was not a guess about chemistry so much as a way of reading the "
      "world: every thing seeks its place, which is why fire goes up and a stone falls.",
      "Classical element"),

    B("five_elements_india",
      "everything is made of the five great elements",
      "of a hundred-odd elements, and they are made of atoms",
      -600, 1850, EDUCATED, SOUTH_ASIA,
      "Prithvi, apas, tejas, vayu, akasha: earth, water, fire, air, ether — the same "
      "thinking arrived at independently, with space added.",
      "Mahābhūta"),

    B("wuxing",
      "everything moves through the five phases: wood, fire, earth, metal, water",
      "of a hundred-odd elements, and they are made of atoms",
      -300, 1900, EDUCATED, EAST_ASIA,
      "Wu xing is not a list of stuff so much as a list of behaviour: wood grows, fire rises, "
      "earth receives, metal cuts, water sinks. It ordered the seasons, the dynasties, the "
      "organs of the body and the pitch of a bell.",
      "Wuxing (Chinese philosophy)"),

    B("phlogiston",
      "things burn because they give off phlogiston",
      "things burn because they join with oxygen",
      1667, 1780, EDUCATED, EUROPE,
      "Stahl's, and it explained a great deal: why a candle goes out under a glass, why "
      "charcoal leaves so little ash. Lavoisier weighed the ash and it stopped explaining.",
      "Phlogiston theory"),

    B("caloric",
      "heat is a fluid that flows from the hot thing to the cold",
      "heat is the movement of the particles",
      1780, 1850, EDUCATED, EUROPE + OLD_WORLD,
      "It survived phlogiston by sixty years and gave thermodynamics some of its mathematics.",
      "Caloric theory"),

    B("aether",
      "light travels through the aether, which fills all space",
      "light needs nothing to travel through",
      1700, 1905, EDUCATED, EUROPE + OLD_WORLD,
      "Everybody knew light was a wave, and no wave was known to travel without a medium. "
      "Michelson and Morley looked for it in 1887 and did not find it; Einstein in 1905 "
      "said there was nothing to find.",
      "Luminiferous aether"),

    B("alchemy",
      "base metal can be turned into gold",
      "it cannot, not by any means anyone then had",
      -300, 1700, EDUCATED, OLD_WORLD + EUROPE + SOUTH_ASIA + EAST_ASIA,
      "Held in Alexandria, in Baghdad, in Song China and in Europe, and in India as rasayana; "
      "and out of it came the retort, the alembic, the acids, and chemistry. The Americas are "
      "left out: there is no transmutation of metals on record there before contact.",
      "Alchemy"),

    B("great_chain",
      "all living things are ordered in a chain, from the worm up to the angel",
      "living things are related by descent, and there is no up",
      1300, 1859, EDUCATED, EUROPE + OLD_WORLD,
      "A chain cannot have a missing link, so every kind must exist somewhere and always "
      "have — which is what made the fossils so hard.",
      "Great chain of being"),

    B("descent",
      "living things are related to one another by descent",
      "which is so",
      1859, None, EDUCATED, WORLD,
      "On the Origin of Species. Ninety per cent of working biologists accepted it within "
      "twenty years.",
      "On the Origin of Species"),

    # ------------------------------------------------------------------ rule
    B("mandate_of_heaven",
      "the emperor rules while heaven grants him the mandate; famine and earthquake are "
      "heaven's warning that he is losing it",
      "governments fall for reasons that can be studied",
      -1000, 1911, EDUCATED, CHINA,
      "The oldest continuous political theory in the world, and the one thing a Chinese "
      "rebel needed in order to be a rebel and not a criminal.",
      "Mandate of Heaven"),

    B("divine_right",
      "the king rules by God's own appointment and answers to God alone",
      "governments answer to the people, or pretend to",
      800, 1789, EDUCATED, EUROPE,
      "Argued for in the same century that produced Newton, by men who were not fools.",
      "Divine right of kings"),

    B("chakravartin",
      "the true king is the turner of the wheel, who rules by dharma and not by force",
      "governments answer to the people, or pretend to",
      -300, 1858, EDUCATED, SOUTH_ASIA,
      "The ideal of the universal ruler: Ashoka on his pillars, and every raja's "
      "inscription claiming the same of himself.",
      "Chakravartin"),

    # ------------------------------------------------------------------ the unseen
    B("astrology",
      "the stars shape a life",
      "they do not",
      -3000, 1700, EDUCATED, WORLD,
      "A branch of learned medicine for two thousand years: a physician who could not cast "
      "a horoscope was not a physician. It died in Europe in the seventeenth century and "
      "has been in good health ever since everywhere else.",
      "Astrology"),

    B("witchcraft_europe",
      "witches ride by night, spoil the harvest and sicken the cattle",
      "there is no such thing; the neighbours were neighbours",
      1400, 1750, EVERYONE, EUROPE,
      "Perhaps fifty thousand people were executed. The peak was not the 'dark' Middle "
      "Ages but the century of Shakespeare and Newton.",
      "Witch trials in the early modern period"),
]
