"""Step 38 (D4): jobs and workplaces — what people do for a living, by place and year.

Why this file exists
--------------------
Before this the mod picked a villager's job with a six-way switch — farmer, artisan, merchant,
soldier, scholar, citizen — at random, identically in the Nile valley in 3000 BC and in
Manchester in 1850. The same switch for every place and every year. A Palaeolithic forager and a
Victorian railwayman were one `case 1` apart.

This is the table of what people actually did.

The number that matters
-----------------------
**How many people it takes to feed everybody.** Everything else follows from it. In a
pre-industrial economy it is most of them — the share of the workforce in farming is the single
figure that separates 1688 from 2022, and it falls from about **56 per cent of the English
labour force in 1688** (Crafts; the Cambridge Group's revision of King's social table) to **1.0
per cent in the United Kingdom today** and **1.6 per cent in the United States** (ILO modelled
estimates). In Burundi it is still **85 per cent**.

The English series is measured and it is the spine of this table:

    1688  1759  1802-3  1841      primary / secondary / tertiary, per cent
    55.6  48.0  41.7    22.2      primary (farming, herding, foraging)
    18.5  23.8  24.7    40.5      secondary (craft, mining)
    25.9  28.2  33.6    37.3      tertiary (trade, service, transport, and the rest)

Note what the series does *not* say. The folk figure of "eighty per cent of people were peasants"
is too high even for 1688 England: as the Cambridge Group put it, "no-one would now suggest that
a figure as high as 80 per cent is remotely plausible". England was already proto-industrial, and
by 1841 the secondary sector was the largest of the three.

Rules for a row
---------------
1. No source, no row.
2. The twelve shares must add to 100. The row class refuses otherwise.
3. Boxes may overlap; empty means the whole world. The most specific box wins, and an urban row
   beats a country row when the question is asked about a town.
4. `pub` is about the shares, not the row: True where the shares come from a published
   occupational table, False where they are this table's own. Only the first kind can be used to
   test anything.
"""

from beliefs_table import AFRICA, EAST_ASIA, EUROPE, OLD_WORLD, SOUTH_ASIA, WORLD
from households_table import LATIN_AMERICA, MENA, N_AMERICA, OCEANIA, SE_ASIA
from life_table import BRITAIN, JAPAN

RECORDED = "recorded"
MIXED = "mixed"
ESTIMATED = "estimated"
MARKS = (RECORDED, MIXED, ESTIMATED)

# The twelve kinds of work. Ordered: getting food first, then making, moving, ruling, praying.
WORKS = ("farming", "herding", "foraging", "craft", "miner", "trade", "service", "transport",
         "soldier", "clergy", "official", "scholar")

# What each one is called, in the words a person would use.
PLAIN = {
    "farming": "farmer", "herding": "herder", "foraging": "hunter",
    "craft": "craftsman", "miner": "miner", "trade": "merchant",
    "service": "servant", "transport": "carter", "soldier": "soldier",
    "clergy": "priest", "official": "clerk", "scholar": "scholar",
}

# Which of the three classical sectors each belongs to, so the English series can be checked.
SECTOR = {
    "farming": 1, "herding": 1, "foraging": 1,
    "craft": 2, "miner": 2,
    "trade": 3, "service": 3, "transport": 3, "soldier": 3, "clergy": 3, "official": 3,
    "scholar": 3,
}

CAMPOP = ("Cambridge Group for the History of Population and Social Structure, The occupational "
          "structure of England and Wales c.1750-1911; Crafts; Allen, Class structure and "
          "inequality during the industrial revolution")
KING = "Gregory King's social table for England and Wales, 1688 (as revised)"
ILO = ("ILO modelled estimates / World Bank, Employment in agriculture (% of total employment); "
       "FAO, Analytical Brief 92: Employment indicators 2000-2022")
FAO = ("FAO, FAOSTAT Analytical Brief 92, Employment indicators 2000-2022: world 26.2%, "
       "Africa 47.8%, Asia 28.8%, Americas 9.0%, Oceania 6.6%, Europe 5.2%")


class J:
    """One occupational structure: what share of working people do what."""

    __slots__ = ("id", "name", "boxes", "frm", "to", "shares", "urban", "mark", "note", "src",
                 "pub")

    def __init__(self, id, name, boxes, frm, to, shares, mark, note, src, urban=False, pub=True):
        assert src, "every row needs a source: " + id
        assert to is None or frm <= to, "ends before it starts: " + id
        assert mark in MARKS, "unknown mark %r in %s" % (mark, id)
        total = sum(shares.values())
        assert total == 100, \
            "shares must add to 100 in %s, got %d" % (id, total)
        unknown = [k for k in shares if k not in WORKS]
        assert not unknown, "unknown kind of work %r in %s" % (unknown, id)
        assert all(v >= 0 for v in shares.values()), "negative share in " + id
        for bx in boxes:
            assert len(bx) == 4 and -90 <= bx[0] <= bx[1] <= 90 and -180 <= bx[2] <= bx[3] <= 180, \
                "bad box in " + id
        self.id = id
        self.name = name
        self.boxes = boxes
        self.frm = frm
        self.to = to
        self.shares = shares
        self.urban = urban
        self.mark = mark
        self.note = note
        self.src = src
        # pub: do the shares come from a published occupational table, or are they this table's
        # own? Where they are the table's own, no check can be built on them.
        self.pub = pub

    def sector(self, n):
        return sum(v for k, v in self.shares.items() if SECTOR.get(k) == n)


def w(farming=0, herding=0, foraging=0, craft=0, miner=0, trade=0, service=0, transport=0,
      soldier=0, clergy=0, official=0, scholar=0):
    """Twelve shares in a fixed order, so a row reads like a sentence."""
    d = {"farming": farming, "herding": herding, "foraging": foraging, "craft": craft,
         "miner": miner, "trade": trade, "service": service, "transport": transport,
         "soldier": soldier, "clergy": clergy, "official": official, "scholar": scholar}
    return {k: v for k, v in d.items() if v}


JOBS = [

    J("foraging_band", "before the first villages", WORLD, -100000, -8000,
      w(farming=2, herding=2, foraging=80, craft=4, trade=1, service=4, soldier=3, clergy=2,
        scholar=1, transport=1), ESTIMATED,
      "Nothing is published, because there is no census of a band. Four people in five are "
      "getting food by hunting, gathering and fishing, and almost everything else is part-time: "
      "the same woman who gathers makes the baskets. The 2 per cent of farming is the very end "
      "of the period, at the first gardens.",
      "English Wikipedia, 'Hunter-gatherer' and 'History of agriculture'", pub=False),

    J("early_farming", "the first farmers", WORLD, -8000, -3000,
      w(farming=55, herding=14, foraging=15, craft=7, trade=2, service=3, soldier=2, clergy=1,
        transport=1), ESTIMATED,
      "Farming does not replace hunting at a stroke: for two thousand years the two sit side by "
      "side, and this row keeps the foragers at fifteen per cent. The full-time specialist — "
      "the potter, the flint-knapper, the smith — appears here for the first time, because a "
      "village with a surplus can feed somebody who does not farm.",
      "English Wikipedia, 'Neolithic Revolution' and 'History of agriculture'", pub=False),

    J("bronze_old_world", "the Bronze and Iron Ages", OLD_WORLD, -3000, -801,
      w(farming=50, herding=15, foraging=8, craft=10, trade=4, service=4, soldier=4, clergy=2,
        official=2, scholar=1), ESTIMATED,
      "The first cities, and with them the first people who do nothing but one thing: the "
      "temple's scribes, the palace's weavers, the standing soldiers, the merchants who carry "
      "tin from somewhere a thousand miles away. Clerk at two per cent is not a rounding error, "
      "it is the invention of writing.",
      "English Wikipedia, 'Bronze Age' and 'Ancient Egypt'", pub=False),

    J("bronze_world", "the Bronze and Iron Ages, everywhere else", WORLD, -3000, -801,
      w(farming=55, herding=14, foraging=12, craft=7, trade=2, service=3, soldier=3, clergy=2,
        official=1, transport=1), ESTIMATED,
      "The same row a little earlier and a little thinner: outside the Old World's city belts "
      "there are fewer full-time specialists and more people who hunt as well as farm.",
      "English Wikipedia, 'Bronze Age' and 'History of agriculture'", pub=False),

    J("classical_world", "the classical world", WORLD, -800, 399,
      w(farming=52, herding=12, foraging=6, craft=10, trade=5, service=6, soldier=5, clergy=2,
        official=1, scholar=1), ESTIMATED,
      "Alexander of Aphrodisias lists the occupations of a Roman city and there are dozens of "
      "them — fullers, goldsmiths, physicians, teachers of letters, shipowners, muleteers — but "
      "the base is still the land: roughly half of everyone, and in the countryside nearer "
      "nine-tenths. Five per cent under arms is a standing army, which is itself the novelty.",
      "English Wikipedia, 'Ancient Rome' and 'Economy of the Roman Empire'", pub=False),

    J("medieval_world", "the Middle Ages", WORLD, 400, 1349,
      w(farming=58, herding=12, foraging=4, craft=8, trade=3, service=6, soldier=3, clergy=2,
        official=1, scholar=1, transport=1, miner=1), ESTIMATED,
      "The Domesday record of 1086 counts ploughmen, bordars, cottars, serfs, villeins, "
      "smiths, carpenters, fishermen, salt-makers, potters, weavers, priests — and the ploughmen "
      "and those below them are the overwhelming majority. No census gives a percentage for any "
      "country in these centuries, so the whole row is marked estimated.",
      "English Wikipedia, 'Domesday Book' and 'Medieval demography'", pub=False),

    J("late_medieval", "the late Middle Ages", WORLD, 1350, 1549,
      w(farming=60, herding=10, foraging=3, craft=9, trade=4, service=6, soldier=2, clergy=2,
        official=1, scholar=1, transport=1, miner=1), ESTIMATED,
      "After the Black Death there is more land per head and labour is dear; the wage of a "
      "ploughman rises and the share of the workforce in farming stays high while the numbers "
      "fall. Nothing is measured anywhere in the world before the English listings of the "
      "sixteenth century, so this row is the table's own.",
      "English Wikipedia, 'Black Death' and 'Medieval demography'", pub=False),

    # ---------------------------------------------------------------- the measured rows
    J("england_1688", "England under King William", BRITAIN, 1600, 1749,
      w(farming=50, herding=3, foraging=3, craft=12, miner=5, trade=8, service=10, transport=4,
        soldier=2, clergy=1, official=1, scholar=1), RECORDED,
      "Published, and the most important row in this table: the Cambridge Group's revision of "
      "Gregory King's 1688 social table gives a labour force that is **55.6 per cent primary, "
      "18.5 secondary and 25.9 tertiary**. This row reproduces it as 56 / 17 / 27. Note what it "
      "is *not*: it is not eighty per cent peasants. 'No-one would now suggest that a figure as "
      "high as 80 per cent is remotely plausible' — England in 1688 was already "
      "proto-industrial, with five per cent of the workforce down the mines and twelve per cent "
      "in the crafts.",
      CAMPOP + "; " + KING),

    J("england_1800", "England at the turn of the nineteenth century", BRITAIN, 1750, 1814,
      w(farming=38, herding=2, foraging=2, craft=18, miner=7, trade=10, service=12, transport=5,
        soldier=3, clergy=1, official=1, scholar=1), RECORDED,
      "Published: **41.7 per cent primary, 24.7 secondary, 33.6 tertiary** in 1802-3. This row "
      "is 42 / 25 / 33. In a single lifetime the primary sector loses a seventh of itself and "
      "the secondary gains a third. The 1831 census — the first to ask everybody's occupation — "
      "found that only sixty per cent of the men called 'labourer' were agricultural labourers, "
      "which is the moment the word stops meaning 'farm hand'.",
      CAMPOP + "; 1831 census of England and Wales"),

    J("england_1841", "industrial England", BRITAIN, 1815, 1899,
      w(farming=20, herding=1, foraging=1, craft=28, miner=12, trade=11, service=13, transport=7,
        soldier=3, clergy=1, official=2, scholar=1), RECORDED,
      "Published: **22.2 per cent primary, 40.5 secondary, 37.3 tertiary** in 1841. This row is "
      "22 / 40 / 38. This is the first moment in the recorded history of the world at which "
      "making things employs more people than growing food. Allen's tables put agriculture's "
      "share of the English labour force at 20 per cent in both 1846 and 1867, against 15 per "
      "cent of national income.",
      CAMPOP + "; Allen, Class structure and inequality during the industrial revolution"),

    J("early_modern_europe", "Europe before 1900", EUROPE, 1550, 1899,
      w(farming=55, herding=4, foraging=2, craft=14, miner=3, trade=7, service=8, transport=3,
        soldier=2, clergy=1, official=1), MIXED,
      "Carried from the measured English figures to the rest of Europe and marked mixed: the "
      "Hajnal marriage pattern, the nuclear household and the late age of marriage are one and "
      "the same economic arrangement, and England is the best-measured case of it rather than "
      "an outlier from it. Held a little more agricultural than England, because most of Europe "
      "was.",
      CAMPOP, pub=False),

    J("early_modern_world", "the early modern world outside Europe", WORLD, 1550, 1899,
      w(farming=62, herding=10, foraging=3, craft=9, miner=1, trade=4, service=5, transport=2,
        soldier=2, clergy=1, official=1), ESTIMATED,
      "Between 1550 and 1900 the only occupational tables on Earth are European, and this row is "
      "what is left: the Ottoman lands, South-East Asia, Africa, the Americas and Oceania, held "
      "more agricultural than Europe and with fewer people in the crafts. Marked estimated.",
      "English Wikipedia, 'History of agriculture' and 'Occupation (human)'", pub=False),

    J("british_india", "India under the Raj", SOUTH_ASIA, 1850, 1979,
      w(farming=68, herding=4, foraging=2, craft=9, trade=5, service=6, transport=2, soldier=1,
        clergy=1, official=1, scholar=1), MIXED,
      "The decennial Indian census from 1881 classified every occupation, and the finding that "
      "shocked the administrators was de-industrialisation: the hand-weavers, who had supplied "
      "a large part of the world's cotton cloth, were driven back onto the land by machine-spun "
      "yarn, and the share in agriculture rose through the nineteenth century. Two thirds to "
      "seven tenths is the range the censuses give. Marked mixed.",
      "English Wikipedia, 'Census in India' and 'Deindustrialisation of India'", pub=False),

    J("world_1950", "the world in the twentieth century", WORLD, 1900, 1999,
      w(farming=55, herding=4, foraging=1, craft=12, miner=2, trade=7, service=8, transport=4,
        soldier=3, clergy=1, official=2, scholar=1), MIXED,
      "Across the twentieth century the world goes from most people farming to about a quarter, "
      "and the "
      "change is not uniform: Europe and North America are nearly done by 1950, Africa and much "
      "of Asia are barely begun. Shaped from the modern regional rows and the English series, "
      "and marked mixed.",
      ILO + "; " + CAMPOP, pub=False),

    # ---------------------------------------------------------------- the present
    J("modern_world", "the world since 2000", WORLD, 2000, None,
      w(farming=26, herding=1, craft=20, miner=1, trade=14, service=14, transport=7, soldier=2,
        clergy=1, official=8, scholar=6), RECORDED,
      "Published: in 2022 the share of employment in agriculture worldwide was **26.2 per cent** "
      "— Africa 47.8, Asia 28.8, the Americas 9.0, Oceania 6.6, Europe 5.2. This row is the "
      "world figure, and it is the last generation in which the majority of the world's workers "
      "were not farmers.",
      FAO),

    J("modern_africa", "sub-Saharan Africa since 2000", AFRICA, 2000, None,
      w(farming=48, herding=4, foraging=1, craft=11, miner=1, trade=12, service=10, transport=4,
        soldier=2, clergy=1, official=4, scholar=2), RECORDED,
      "Published: **47.8 per cent** of employment in Africa was agricultural in 2022, more than "
      "any other region. Burundi 85.1, Burkina Faso 74.2, Niger 70.9, Madagascar 70.1, Chad "
      "69.2, Ethiopia 62.8 — the highest national figures left in the world.",
      FAO + "; English Wikipedia, 'List of countries by employment in agriculture'"),

    J("modern_europe", "Europe and North America since 2000", EUROPE + N_AMERICA, 2000, None,
      w(farming=3, herding=1, craft=17, trade=13, service=17, transport=6, soldier=2, clergy=1,
        official=16, scholar=24), RECORDED,
      "Published: **Europe 5.2 per cent, the Americas 9.0**; the United Kingdom **1.0**, Germany "
      "1.2, Canada 1.3, the United States 1.6, Sweden 1.8. The jobs that replaced the farm are "
      "not mainly factories: they are the clerk at sixteen per cent and the teacher, the nurse "
      "and the engineer at twenty-four. That is what a post-industrial economy is made of.",
      FAO + "; English Wikipedia, 'List of countries by employment in agriculture'"),

    J("modern_india", "South Asia since 2000", SOUTH_ASIA, 2000, None,
      w(farming=42, herding=3, craft=16, miner=1, trade=12, service=11, transport=5, soldier=1,
        clergy=1, official=5, scholar=3), RECORDED,
      "Published: **India 43.5 per cent** (36.6 of men, 61.5 of women), Nepal 61.2, Pakistan "
      "36.1, Bangladesh 35.3. The female figure being two thirds is not a rounding detail: in "
      "much of South Asia the men have left the fields and the women have not.",
      ILO + "; English Wikipedia, 'List of countries by employment in agriculture'"),

    J("modern_east_asia", "China, Japan and Korea since 1980", EAST_ASIA + JAPAN, 1980, None,
      w(farming=20, herding=1, craft=26, miner=1, trade=13, service=14, transport=6, soldier=2,
        clergy=1, official=9, scholar=7), RECORDED,
      "Published: China's agricultural employment fell from **50.0 per cent in 1991 to 22.2 per "
      "cent in 2024** — the fastest structural change in the history of the world, done in one "
      "generation, and the reason the world figure is where it is. Japan and South Korea are "
      "below 5 per cent.",
      ILO + "; statbase.org, Employment by sector"),

    J("modern_mena", "the Middle East and North Africa since 2000", MENA, 2000, None,
      w(farming=20, herding=3, craft=20, miner=1, trade=15, service=14, transport=6, soldier=3,
        clergy=2, official=10, scholar=6), MIXED,
      "Published: Morocco 29.6, Yemen 28.6, Iran about 16, Turkey about 15, Israel 0.8. The "
      "spread within the region is enormous, from a Yemeni highland farm to a Gulf city where "
      "almost nobody is a citizen of the place they work in. Marked mixed.",
      ILO + "; English Wikipedia, 'List of countries by employment in agriculture'", pub=False),

    J("modern_latin", "Latin America and the Caribbean since 2000", LATIN_AMERICA, 2000, None,
      w(farming=14, herding=2, craft=18, miner=2, trade=16, service=17, transport=6, soldier=2,
        clergy=1, official=12, scholar=10), MIXED,
      "Published: **the Americas 9.0 per cent** as a whole, but that average is dragged down by "
      "the United States; Brazil is about 9 and Mexico about 13, while Ecuador is 30.0 and "
      "Haiti 45.5. Marked mixed.",
      FAO + "; English Wikipedia, 'List of countries by employment in agriculture'", pub=False),

    J("modern_se_asia", "South-East Asia and the Pacific since 2000", SE_ASIA + OCEANIA, 2000,
      None,
      w(farming=27, herding=2, foraging=1, craft=18, miner=1, trade=14, service=14, transport=6,
        soldier=2, clergy=1, official=8, scholar=6), MIXED,
      "Published: **Asia 28.8 per cent, Oceania 6.6**; Vietnam 33.0, Thailand 30.1, Indonesia "
      "28.8, the Philippines about 23. The Pacific islands are far lower and the mainland far "
      "higher, and one row cannot say both honestly. Marked mixed.",
      FAO + "; English Wikipedia, 'List of countries by employment in agriculture'", pub=False),

    J("industrial_town", "the industrial town", EUROPE + N_AMERICA, 1800, 1899,
      w(farming=5, craft=34, miner=6, trade=14, service=20, transport=8, soldier=3, clergy=1,
        official=5, scholar=4), MIXED,
      "A mill town is not a village with a factory in it. Five per cent farm, a third make, a "
      "fifth serve, and eight per cent move things — the carters, the boatmen, the railwaymen, "
      "without whom a town of a hundred thousand cannot eat. Shaped from the 1841 English "
      "structure with the farming taken out and the crafts and transport put up. Marked mixed.",
      CAMPOP, True, pub=False),
]
