"""Step 38 (D2, D17 and the life-span half of C20): how long people lived, and when they married.

Why this file exists
--------------------
Nobody in this mod has ever been born. `VirtualVillager.updateYear` loses one point of health per
twenty years and marks a person dead at zero; there is no birth year, no age, no marriage, no
children and no cause. `PeopleMemory` remembers sixty-four people per square so that the same face
answers you twice, and that is the whole of a person.

Two tables here, because the sources reach different distances:

    MORTALITY   how long people lived, by place and year
    MARRIAGE    when they married, and how many children they had

The two are separate on purpose. Life expectancy at birth is published for a fair spread of eras
and places. The age at first marriage is not: it is published in detail for Europe (the Hajnal
literature) and thinly everywhere else. Welding them into one table would force an answer about
marriage in 500 BC Peru that no source supports.

The distinction the whole table turns on
----------------------------------------
**Life expectancy at birth is not the adult lifespan.** In a population whose e0 is 26, a
fifteen-year-old can expect another thirty-odd years. Every figure below therefore carries at
least two anchors — life expectancy at birth *and* life expectancy at some adult age — because a
register that rolls deaths from e0 alone produces a world with no grandparents in it, which is
wrong: the sources say the most common age of adult death in England between 1600 and 1800 was
about seventy.

Rules for a row
---------------
1. No source, no row. Every row names the article or paper its numbers came from.
2. Anchors are pairs (age, years of life remaining at that age). The first is always (0, e0).
   Where a figure is published, it is used as published. Where the sources stop, the tail is
   *shaped*, and the row says so and is marked `mixed` or `estimated`.
3. `mark` is recorded (every anchor published), mixed (some anchors published, some shaped) or
   estimated (nothing published for this place and era).
4. Boxes may overlap. Empty boxes means the whole world. The most specific box that contains the
   place wins, so a village inside both EUROPE and WORLD gets the European row.
"""

from beliefs_table import (AFRICA, AMERICAS, CHINA, EAST_ASIA, EUROPE, MIDEAST, OLD_WORLD,
                           SOUTH_ASIA, WORLD)

RECORDED = "recorded"
MIXED = "mixed"
ESTIMATED = "estimated"
MARKS = (RECORDED, MIXED, ESTIMATED)

# the Mediterranean and the lands Rome ruled, as one box
ROME = [(28.0, 48.0, -10.0, 45.0)]
# Britain, the Low Countries, France, Germany, Scandinavia: west of the Hajnal line
NW_EUROPE = [(43.0, 62.0, -8.0, 18.0)]
BRITAIN = [(50.0, 59.0, -6.0, 2.0)]
FRANCE = [(43.0, 51.0, -2.0, 8.0)]
JAPAN = [(31.0, 45.0, 130.0, 145.0)]
OCEANIA = [(-47.0, -1.0, 110.0, 179.0)]

# the source names, written once
LE = "Life expectancy"
ROME_DEM = "Demography of the Roman Empire"
WEMP = "Western European marriage pattern"
TFR = "Total fertility rate"


class R:
    """One mortality regime: how long people lived in these boxes, in these years."""

    __slots__ = ("id", "name", "boxes", "frm", "to", "anchors", "infant", "mark", "note", "src",
                 "urban")

    def __init__(self, id, name, boxes, frm, to, anchors, infant, mark, note, src, urban=False):
        assert src, "every row needs a source: " + id
        assert -100000 <= frm <= 2100, "year out of range: " + id
        assert to is None or frm <= to, "ends before it starts: " + id
        assert mark in MARKS, "unknown mark %r in %s" % (mark, id)
        assert len(anchors) >= 2, "a regime needs at least two anchors: " + id
        ages = [a for a, _ in anchors]
        assert ages == sorted(ages), "anchors out of age order: " + id
        assert ages[0] == 0, "the first anchor must be at birth: " + id
        for a, e in anchors:
            assert 0 <= a < 130 and 0 < e < 130, "implausible anchor (%s, %s) in %s" % (a, e, id)
        assert 0 <= infant <= 600, "infant mortality out of range: " + id
        assert anchors[-1][0] >= 10, "a regime needs an adult anchor, not just children: " + id
        for bx in boxes:
            assert len(bx) == 4 and -90 <= bx[0] <= bx[1] <= 90 and -180 <= bx[2] <= bx[3] <= 180, \
                "bad box in " + id
        self.id = id
        self.name = name
        self.boxes = boxes
        self.frm = frm
        self.to = to
        self.anchors = anchors
        self.infant = infant
        self.mark = mark
        self.note = note
        self.src = src
        # True for a row that describes a town or city rather than the land around it, so that
        # "Liverpool" and "Lancashire" can be different answers to the same year
        self.urban = urban


class M:
    """One marriage regime: when people married, and how many children they had."""

    __slots__ = ("id", "name", "boxes", "frm", "to", "wife", "husband", "celibate", "births",
                 "mark", "note", "src")

    def __init__(self, id, name, boxes, frm, to, wife, husband, celibate, births, mark, note, src):
        assert src, "every row needs a source: " + id
        assert to is None or frm <= to, "ends before it starts: " + id
        assert mark in MARKS, "unknown mark %r in %s" % (mark, id)
        assert 9 <= wife <= 45 and 9 <= husband <= 60, "implausible marriage age in " + id
        assert wife <= husband, "wives marry older than husbands in " + id
        assert 0 <= celibate <= 100, "celibacy out of range: " + id
        assert 0.0 <= births <= 14.0, "implausible fertility in " + id
        for bx in boxes:
            assert len(bx) == 4 and -90 <= bx[0] <= bx[1] <= 90 and -180 <= bx[2] <= bx[3] <= 180, \
                "bad box in " + id
        self.id = id
        self.name = name
        self.boxes = boxes
        self.frm = frm
        self.to = to
        self.wife = wife
        self.husband = husband
        self.celibate = celibate
        self.births = births
        self.mark = mark
        self.note = note
        self.src = src


# ----------------------------------------------------------------- mortality
#
# Two figures are published for most of these: life expectancy at birth, and life expectancy at
# some adult age. Both go in. Where a source gives a range, the middle is used and the range is
# written into the note.

MORTALITY = [

    R("prehistoric", "before the Bronze Age", WORLD, -100000, -3001,
      [(0, 26.0), (15, 31.0), (50, 15.0), (70, 8.0)], 300, ESTIMATED,
      "No published figure exists for the Palaeolithic or the Neolithic, and this table would "
      "rather say so than invent one. The Bronze Age value is carried back, and the row is marked "
      "estimated: everything before 3000 BC is a guess wearing a Bronze Age hat.",
      LE),

    R("bronze_old_world", "the Bronze and Iron Ages", OLD_WORLD, -3000, -801,
      [(0, 26.0), (15, 32.0), (50, 15.0), (70, 8.0)], 300, MIXED,
      "Published: 26 at birth, with life expectancy at fifteen of 28 to 36 years. The tail past "
      "fifteen is shaped, not published — the article gives nothing beyond it.",
      LE),

    R("bronze_world", "the Bronze and Iron Ages, everywhere else", WORLD, -3000, -801,
      [(0, 26.0), (15, 30.0), (50, 14.0), (70, 7.0)], 300, ESTIMATED,
      "The 26 of the Old World carried to the rest of the world as a baseline, because there is "
      "no figure for anywhere else and no answer at all is worse than an honest guess.",
      LE),

    R("classical_greece", "Classical Greece", [(34.0, 41.0, 19.0, 29.0)], -800, -101,
      [(0, 26.5), (15, 36.0), (40, 20.0), (50, 16.0), (60, 11.0), (70, 6.5)], 250, RECORDED,
      "Every anchor here is published: 25 to 28 at birth, and the remaining years falling to 33-39 "
      "at fifteen, about 20 at forty, 14-18 at fifty, 10-12 at sixty and 6-7 at seventy. This is "
      "the one ancient population for which the whole curve is on record.",
      LE),

    R("classical_rome", "Rome and the Mediterranean", ROME + OLD_WORLD, -100, 399,
      [(0, 27.5), (1, 37.5), (5, 42.5), (50, 15.0), (70, 8.0)], 300, MIXED,
      "Published: 22 to 33 at birth; of the two thirds to three quarters who survived the first "
      "year, 34 to 41 years remained, and of the 55 to 65 per cent who reached five, 40 to 45. "
      "Those three anchors are consistent with each other and with an infant mortality near a "
      "third. The tail past five is shaped: the article goes no further.",
      ROME_DEM),

    R("classical_world", "the classical centuries, everywhere else", WORLD, -800, 399,
      [(0, 27.0), (15, 34.0), (50, 15.0), (70, 8.0)], 280, ESTIMATED,
      "A baseline for the lands outside the Greek and Roman record: India under the Mauryas, Han "
      "China, the Americas, Africa. No life table is published for any of them. The shape is "
      "borrowed from the Mediterranean and the level is held a little lower.",
      LE),

    R("medieval_world", "the Middle Ages, outside Europe and the Caliphate", WORLD, 400, 1399,
      [(0, 30.0), (15, 33.0), (50, 15.0), (70, 8.0)], 260, ESTIMATED,
      "The coverage check found this hole: the only medieval life tables on record are for the "
      "English peerage and the Islamic world, so India under the Cholas, Song China, the "
      "Maya, Mali and the Anasazi had **no answer at all** between the fall of Rome and 1400. "
      "This row fills it at the world baseline and is marked estimated. More specific rows — "
      "China and Japan, the Caliphate, Europe — still win inside their own boxes.",
      LE),

    R("medieval_islam", "the Caliphate and the Islamic world", MIDEAST + OLD_WORLD, 700, 1400,
      [(0, 35.0), (15, 38.0), (50, 17.0), (70, 9.0)], 220, MIXED,
      "Published: 35 or more at birth, which is the highest figure of the medieval world. The "
      "article also gives 59 to 84.3 years for Islamic scholars in the Middle East and 69 to 75 "
      "in Islamic Spain — and that is a biased sample if ever there was one: literate, urban, "
      "well-fed men whose lifetimes were recorded precisely because they were worth recording. "
      "The scholar figure is not used here; it is written down so nobody reaches for it.",
      LE),

    R("medieval_europe", "medieval Europe", EUROPE, 500, 1346,
      [(0, 31.5), (10, 32.2), (25, 23.3), (50, 14.0), (70, 7.0)], 300, MIXED,
      "Published, for the English peerage: 30 to 33 at birth, about a third of infants dead in "
      "their first year, 32.2 years remaining at ten and 23.3 at twenty-five. The tail past "
      "twenty-five is shaped. Note the population: these are landholding families, the only "
      "medieval European group with a life table on record, and they almost certainly lived "
      "longer than the people who worked their land.",
      LE),

    R("black_death", "the plague years", EUROPE + MIDEAST, 1347, 1400,
      [(0, 20.0), (15, 25.0), (50, 12.0), (70, 6.0)], 400, ESTIMATED,
      "No life table is published for the Black Death years, only the death tolls. A normal "
      "medieval e0 of 31 falling to about 20 for two generations is this table's own arithmetic, "
      "marked estimated: it is what the mortality rates imply and nobody measured it.",
      "Black Death"),

    R("late_medieval", "the late Middle Ages", WORLD, 1400, 1549,
      [(0, 32.0), (15, 34.0), (50, 15.0), (70, 8.0)], 260, MIXED,
      "Published for early modern Britain: 33 to 40 at birth, with a woman's remaining years at "
      "fifteen rising from about 33 in the fifteenth and sixteenth centuries to about 42 in the "
      "eighteenth. The 32 used here is the lower end, held down a little for the rest of the "
      "world, where nothing is published.",
      LE),

    R("early_modern_europe", "early modern Europe", EUROPE, 1550, 1699,
      [(0, 36.0), (15, 37.0), (50, 17.0), (70, 9.0)], 240, MIXED,
      "Published: 33 to 40 at birth for Britain across the sixteenth to eighteenth centuries, and "
      "a woman's remaining years at fifteen of about 33. The Netherlands, the best-documented "
      "case, held an age at first marriage of 27 for women and 30 for men from the late 1400s "
      "until the Second World War.",
      LE + "; " + WEMP),

    R("early_modern_world", "the two centuries before 1700, outside Europe", WORLD, 1550, 1699,
      [(0, 31.0), (15, 34.0), (50, 16.0), (70, 8.0)], 260, ESTIMATED,
      "Another hole the coverage check found: between 1550 and 1700 the only published figures "
      "are European, so Mughal India, Ming and Qing China, Japan, the Ottoman lands outside the "
      "Caliphate box, Africa and the Americas had nothing. Filled at the world baseline and "
      "marked estimated.",
      LE),

    R("eighteenth_england", "eighteenth-century England", BRITAIN, 1700, 1799,
      [(0, 37.0), (15, 40.0), (50, 18.0), (70, 9.0)], 220, RECORDED,
      "Published: for most of the century 35 to 40, dipping as low as 25 in the 1720s, averaging "
      "37 in the second half and passing 40 — approaching 50 — for the elite. Eighteenth-century "
      "male life expectancy at birth was 34.",
      LE),

    R("eighteenth_france", "eighteenth-century France", FRANCE, 1700, 1799,
      [(0, 28.0), (15, 33.0), (50, 16.0), (70, 8.0)], 250, RECORDED,
      "Published, for males: 24.8 years in the 1740s, 27.9 in the 1750s and 33.9 in the 1800s. "
      "The rise inside one lifetime is the whole of the demographic transition in miniature.",
      LE),

    R("eighteenth_world", "the eighteenth century, everywhere else", WORLD, 1700, 1799,
      [(0, 30.0), (15, 34.0), (50, 16.0), (70, 8.0)], 250, ESTIMATED,
      "Nothing is published outside Europe, France and England. Thirty at birth is the middle of "
      "what is known, carried to the rest of the world and marked estimated.",
      LE),

    R("nineteenth_world", "the world in 1800", WORLD, 1800, 1899,
      [(0, 29.0), (15, 35.0), (50, 16.0), (70, 8.0)], 250, MIXED,
      "Published: about 29 at the beginning of the nineteenth century, and **no country in the "
      "world** had a life expectancy at birth longer than 40 years. England, Belgium and the "
      "Netherlands came closest, each reaching 40 by the 1840s, by which time Norway, Sweden and "
      "Denmark had passed them. India is estimated at about 25 and Europe at about 33.",
      LE),

    R("nineteenth_india", "India in the nineteenth century", SOUTH_ASIA, 1800, 1899,
      [(0, 25.0), (15, 32.0), (50, 15.0), (70, 8.0)], 280, RECORDED,
      "Published: India's life expectancy at the beginning of the nineteenth century is estimated "
      "at about 25 years, against a European average of about 33.",
      LE),

    R("nineteenth_england", "early nineteenth-century England", BRITAIN, 1800, 1849,
      [(0, 40.0), (1, 46.0), (20, 40.0), (50, 20.0), (70, 10.0)], 160, RECORDED,
      "Every anchor published: 40 at birth; 45 to 47 years remaining for the 84 per cent who "
      "survived their first year; 40 years still remaining at twenty, 20 at fifty and 10 at "
      "seventy. The most complete historical life table in this pack, and the one that shows how "
      "badly a single e0 figure misleads: a parish of people 'living to forty' on average held "
      "plenty of seventy-year-olds.",
      LE),

    R("industrial_city", "the industrial city", EUROPE + AMERICAS, 1800, 1899,
      [(0, 30.0), (15, 32.0), (50, 14.0), (70, 7.0)], 220, RECORDED,
      "Published, for English cities of 100,000 or more: Liverpool 28.3 in 1838-44 and 37.5 in "
      "1891-1900; Manchester 29.8 then 38.3; London 36.7 then 43.7; England and Wales as a whole "
      "40.4 then 46.1. The city was a death trap and the record says so: a Liverpool child born "
      "in 1840 could expect twelve fewer years than one born in the countryside. This row is "
      "marked urban, because the penalty belongs to the town and not to the county — without "
      "that it could never be reached, England being a smaller box than Europe.",
      "Mortality, migration and epidemiological change in English cities, 1600-1870 (PMC7611108)",
      True),

    R("east_asia_old", "China and Japan before 1900", EAST_ASIA, -200, 1899,
      [(0, 30.0), (15, 34.0), (50, 16.0), (70, 8.0)], 250, ESTIMATED,
      "No historical life table is published here for China or Japan. The level is held at the "
      "world baseline and marked estimated; the marriage table below has real figures for Qing "
      "China, which is more than the mortality record can say.",
      LE),

    R("nineteen_hundred", "the world in 1900", WORLD, 1900, 1949,
      [(0, 33.0), (15, 42.0), (50, 20.0), (70, 10.0)], 180, MIXED,
      "Published: a world average of 31 in 1900. England and Wales reached 44 for males and 48 "
      "for females by 1900, with median ages at death of 52 and 57 — the gap between the mean "
      "and the median is the child mortality, and it is most of the story.",
      LE),

    R("modern_1950", "the world in 1950", WORLD, 1950, 1979,
      [(0, 46.0), (15, 52.0), (50, 24.0), (70, 11.0)], 130, MIXED,
      "United Nations World Population Prospects through the article: about 46 at birth in 1950 "
      "and about 63 by 1980. The tail is shaped from the modern curve.",
      LE + " (UN World Population Prospects)"),

    R("modern_1980", "the world in 1980", WORLD, 1980, 1999,
      [(0, 63.0), (15, 57.0), (50, 28.0), (70, 13.0)], 70, MIXED,
      "About 63 at birth in 1980 and about 67 by 2000, United Nations estimates.",
      LE + " (UN World Population Prospects)"),

    R("modern_2000", "the world since 2000", WORLD, 2000, 2021,
      [(0, 70.0), (15, 60.0), (50, 31.0), (70, 15.0)], 40, MIXED,
      "About 67 at birth in 2000 and about 72 in 2019, United Nations estimates. Sub-Saharan "
      "Africa is the great exception and has its own row.",
      LE + " (UN World Population Prospects)"),

    R("modern_aids_africa", "southern Africa in the AIDS years", [(-35.0, -5.0, 11.0, 41.0)],
      1990, 2010,
      [(0, 45.0), (15, 45.0), (50, 20.0), (70, 9.0)], 90, RECORDED,
      "Published, United Nations 2002 projections for 2010-2015 with and without HIV: Botswana "
      "70.7 instead of 31.6, South Africa 69.9 instead of 41.5, Zimbabwe 70.5 instead of 31.8. "
      "The whole of the twentieth century's gain, undone by one disease in one region in one "
      "generation.",
      LE),

    R("modern_japan", "Japan today", JAPAN, 1980, None,
      [(0, 82.0), (15, 68.0), (50, 35.0), (70, 18.0)], 20, RECORDED,
      "Published: 84.5 in 2023, 4.2 years above the OECD average; in the 1960s Japan's life "
      "expectancy was among the lowest of the G7, on account of cerebrovascular disease. The "
      "fastest improvement ever recorded, inside one lifetime.",
      LE),

    R("modern_now", "the world since 2022", WORLD, 2022, None,
      [(0, 73.0), (15, 62.0), (50, 32.0), (70, 16.0)], 30, MIXED,
      "About 72 at birth in 2019 and a shade over 73 by the 2020s, United Nations estimates. The "
      "tail is shaped from the modern curve. Without this row the pack simply stops in 2021 — "
      "which the coverage check caught.",
      LE + " (UN World Population Prospects)"),

    R("industrial_town", "the mill towns of the Industrial Revolution",
      [(53.2, 54.2, -2.5, -0.5)], 1750, 1899,
      [(0, 32.0), (15, 34.0), (50, 15.0), (70, 7.0)], 200, MIXED,
      "The same published city series, for the towns the Industrial Revolution built rather than "
      "the ports it grew: Manchester 29.8 in 1838-44 and 38.3 by 1891-1900, Birmingham 35.5 then "
      "41.9, Leeds 35.1 then 41.7, Sheffield 36.1 then 41.6, Bradford 35.3 then 39.5. Slower "
      "than the countryside and faster than Liverpool, which was the worst town in England.",
      "Mortality, migration and epidemiological change in English cities, 1600-1870 (PMC7611108)",
      True),

    R("modern_rich", "the rich world since 2000", EUROPE + JAPAN + AMERICAS + OCEANIA, 2000, None,
      [(0, 79.0), (15, 65.0), (50, 33.0), (70, 17.0)], 20, RECORDED,
      "Published: the United States reached a record 79.0 in 2024 (76.5 men, 81.4 women) after "
      "falling for two years; Spaniards from Madrid can expect 85, Bulgarians from Severozapaden "
      "just past 73. Within the rich world the spread is still a dozen years.",
      LE),
]


# ----------------------------------------------------------------- marriage and children
#
# The Hajnal line: a line from Trieste to Saint Petersburg. West of it, women married in their
# middle twenties and a tenth or more never married at all. East of it, and outside Europe,
# marriage came years earlier and was nearly universal. That is the single biggest fact about
# European demography before 1900 and the mod has to get it right, because a village of women who
# marry at 25 and bear five children is a completely different village from one where they marry
# at 17 and bear seven.

MARRIAGE = [

    M("hunter_gatherer", "before the first towns", WORLD, -100000, -8000,
      16.5, 19.5, 5, 6.0, ESTIMATED,
      "Nothing is published. Mobile foragers wean late and space births about four years apart, "
      "which gives a completed family near six and a first birth in the late teens — but this row "
      "is an argument, not a measurement, and is marked estimated.",
      "Total fertility rate"),

    M("early_farming", "the first farmers", WORLD, -8000, -3000,
      16.0, 19.0, 5, 6.5, ESTIMATED,
      "Settled farming shortened birth spacing and raised fertility: the Neolithic demographic "
      "transition ran the other way from the modern one. Marked estimated.",
      "Neolithic Revolution"),

    M("classical", "the classical world", WORLD, -3000, 499,
      16.0, 26.0, 6, 5.5, ESTIMATED,
      "Girls married in their mid teens and men in their mid twenties across the Mediterranean "
      "and the Near East; the age gap is the mark of the pattern. Marked estimated — the detailed "
      "parish records that make the European figures possible do not exist for these centuries.",
      WEMP),

    M("medieval_world", "the Middle Ages", WORLD, 500, 1399,
      17.0, 24.0, 8, 6.0, ESTIMATED,
      "Before the Hajnal pattern established itself, European marriage was not yet late: the "
      "transition raised the female age at first marriage from about 20 to more than 25 inside a "
      "century, and it affected only the lands west of the line. Outside Europe, marriage in the "
      "teens remained the norm. Marked estimated.",
      WEMP),

    M("hajnal_west", "western Europe, the Hajnal pattern", NW_EUROPE, 1400, 1899,
      25.5, 28.0, 14, 5.0, RECORDED,
      "Published and well documented: west of a line from Trieste to Saint Petersburg the average "
      "age at first marriage was 24 or more for women and 26 or more for men, with 10 to 20 per "
      "cent never marrying and a neolocal household on marriage. England in the late sixteenth "
      "century: 25 for women, 27 for men. The Netherlands: 27 and 30 from the late 1400s until "
      "the Second World War, rising at times to 30 and 32. Three-quarters of western European "
      "women were still unmarried at twenty-five, where east of the line three-quarters were "
      "married by it.",
      WEMP),

    M("hajnal_england_1650", "England, 1650 to 1849", BRITAIN, 1650, 1849,
      24.6, 27.2, 14, 5.5, RECORDED,
      "Published from family reconstitution: mean ages at first marriage of 27.9 for men and 24.0 "
      "for women in 1650-1699, 29.1 and 24.6 in 1700-1749, 28.0 and 24.8 in 1750-1799, 27.3 and "
      "25.0 in 1800-1849; 10 to 18 per cent of women never married. An Englishwoman marrying at "
      "the average 26 in the late seventeenth century and surviving her childbearing years bore "
      "5.03 children; one marrying at 23.5 in the early nineteenth bore 6.02 — a three-year fall "
      "in the marriage age raised fertility by about a fifth.",
      WEMP + "; Cummins, How did the European Marriage Pattern persist? (EHES 259)"),

    M("hajnal_east", "eastern Europe and the Mediterranean", EUROPE + MIDEAST + OLD_WORLD, 1400,
      1899,
      19.0, 23.0, 5, 6.5, RECORDED,
      "Published: east of the Hajnal line the mean age at marriage was earlier for both sexes, "
      "the gap between husband and wife was wider and marriage was more nearly universal — as "
      "late as 1900, early marriage for women was still the rule in eastern Europe. The "
      "nineteenth-century Egyptian case gives the contrast plainly: western European women "
      "married at 25 or 26 and so gave up a third of their childbearing years.",
      WEMP + "; Kumon, The Middle-Eastern marriage pattern? (Economic History Review 2023)"),

    M("ming_china", "Ming China and Tokugawa Japan", EAST_ASIA, 1400, 1699,
      17.5, 21.0, 15, 6.0, ESTIMATED,
      "A hole the coverage check found: East Asia has no marriage row between the end of the "
      "medieval baseline and the Qing figures of 1700. The Qing numbers are carried back two and "
      "a half centuries and marked estimated, because an unsourced invention would be worse and "
      "no answer at all is worse than both.",
      WEMP),

    M("qing_china", "China in the Qing", CHINA, 1700, 1899,
      19.0, 21.5, 22, 6.0, RECORDED,
      "Published: the average age at marriage for men was 21 to 22, and because of the taking of "
      "multiple wives many men could not marry at all — about 22 per cent never did, against 45 "
      "per cent in England, Norway and Sweden around 1800. Celibacy in China was forced and "
      "poverty-shaped; in north-western Europe it was chosen and service-shaped. Same number, "
      "opposite cause.",
      "Voigtlander and Voth, How the West Invented Fertility Restriction (AER 2013, 103:6)"),

    M("india_old", "India before 1900", SOUTH_ASIA, -300, 1899,
      16.0, 21.0, 4, 6.0, ESTIMATED,
      "Child marriage was the norm and the sources are caste-bound and disputed. Sixteen is "
      "held rather than the thirteen or fourteen some of the sources name, because the register "
      "refuses to generate a bride of twelve and a mean that sits below its own floor is a mean "
      "that lies. Marked estimated and deliberately vague: this is a place where a precise "
      "invented number would be worse than a rough one.",
      "Marriageable age"),

    M("early_modern_world", "the wider world, 1400 to 1799", WORLD, 1400, 1799,
      19.0, 23.0, 6, 6.2, ESTIMATED,
      "A hole the coverage check found: between 1400 and 1800 the marriage literature reaches "
      "Europe, the Mediterranean, China and India and nowhere else — Africa, the Americas, "
      "Oceania, Japan and Korea had no row at all. Filled at the pattern that held across most "
      "of the world before the modern fall: marriage in the late teens for women, the early "
      "twenties for men, near-universal, six children. Marked estimated. Every named row — "
      "western Europe, the Mediterranean, Ming China, Qing China, India — still wins inside its "
      "own box.",
      WEMP + "; " + TFR),

    M("world_1800", "the world in 1800", WORLD, 1800, 1899,
      21.0, 25.0, 8, 6.2, RECORDED,
      "Published: total fertility in Western Europe before 1800 ran from 4.5 in Scandinavia to "
      "6.2 in Belgium, and the United States stood at 7.0 in 1800. France before 1790: a mean "
      "age at first marriage of 25.3, 6.5 births per married woman, 10 per cent never married "
      "and a total fertility rate of 5.8.",
      TFR + "; Our World in Data, The global decline of the fertility rate"),

    M("world_1900", "the world in 1900 to 1950", WORLD, 1900, 1964,
      22.0, 25.0, 9, 5.0, RECORDED,
      "Marital fertility in Europe fell from about 7.0 children per woman in 1800-1849 to about "
      "6.0 by 1870-1919, and infant mortality with it — from 25-30 per 1,000 in 1800 to 15-20 by "
      "1900 — which is what ended the need for a crowd of children to look after a parent's old "
      "age.",
      "History of the family"),

    M("world_modern", "the world since 1965", WORLD, 1965, None,
      24.0, 27.0, 10, 2.4, RECORDED,
      "The European Union's total fertility rate stood at 1.46 in 2022, well below replacement, "
      "with the mean age at first marriage past 30 for women in Sweden and Italy. The world "
      "figure is held a little higher because it is not all Europe.",
      WEMP + "; " + TFR),
]
