"""Step 38 (D3): families and homes — what a household is made of, by place and year.

Why this file exists
--------------------
The mod remembers sixty-four people per square so that the same face answers you twice, and that
is the whole of a family: no household, no spouse, no children, no parents, no home. Walk into a
house and there is nobody inside who is anybody to anybody.

This is the table of what fills one.

The thing almost everybody gets wrong
-------------------------------------
**The extended family is not the traditional family.** Laslett's null hypothesis, from the
Cambridge Group's reconstruction of a hundred English communities, is that the household was
"always and invariably nuclear unless the contrary can be proven". Mean household size in England
and Wales sat at 4.75 or a little below from the sixteenth century to 1911 — through the whole of
the Industrial Revolution — and only 10 per cent of pre-industrial households were extended, which
is the same percentage as England in 1966. The Industrial Revolution did not smash the extended
family; there was no extended family to smash.

What *did* vary is where the exceptions sat: **stem** households (one married child stays, with
the parents) in Japan, and in parts of France, Germany, Austria and Scandinavia; **joint**
households (married brothers with their wives and children under one roof in a shared
property-holding unit) in India. Those three words — nuclear, stem, joint — are the spine of this
table.

Rules for a row
---------------
1. No source, no row.
2. `nuclear + stem + joint + solo` must be 100. The builder checks.
3. `size` is the mean over **households**, not the size the average person lives in. The two are
   different numbers and the gap is wide: the mean household worldwide is about 4.0 people, but
   the average *person* lives in a household of about 4.9, because big households hold more
   people. The mod wants the first — it is filling houses, not sampling people.
4. Boxes may overlap; empty means the whole world. The most specific box wins, and an urban row
   beats a country row when the question is asked about a town.
"""

from beliefs_table import (AFRICA, AMERICAS, CHINA, EAST_ASIA, EUROPE, MIDEAST, OLD_WORLD,
                           SOUTH_ASIA, WORLD)
from life_table import BRITAIN, FRANCE, JAPAN, NW_EUROPE

RECORDED = "recorded"
MIXED = "mixed"
ESTIMATED = "estimated"
MARKS = (RECORDED, MIXED, ESTIMATED)

# stem-family Europe, on the Le Play line: France, the Low Countries, Germany, Austria,
# Switzerland, Bohemia, and the north of Italy and Spain
STEM_EUROPE = [(43.0, 55.0, -2.0, 19.0)]
KOREA = [(34.0, 38.5, 126.0, 130.0)]
N_AMERICA = [(25.0, 60.0, -125.0, -66.0)]
LATIN_AMERICA = [(-35.0, 24.0, -82.0, -34.0)]
MENA = [(12.0, 40.0, -15.0, 63.0)]
OCEANIA = [(-47.0, -1.0, 110.0, 179.0)]
SE_ASIA = [(-10.0, 21.0, 95.0, 141.0)]

LASLETT = ("Laslett, P. (ed.) Household and Family in Past Time (1972); Laslett, Size and "
           "structure of the household in England over three centuries, Population Studies 23:2 "
           "(1969)")
CENSUS = "Household and family structure in England and Wales, 1851-1911 (Cambridge)"
UN_HH = "United Nations DESA, Database on Household Size and Composition 2026 (ST/ESA/SER.A/433)"
HAJNAL2 = "Western European marriage pattern"


class H:
    """One household regime: how many people under one roof, and who they are to each other."""

    __slots__ = ("id", "name", "boxes", "frm", "to", "size", "nuclear", "stem", "joint", "solo",
                 "leave", "servants", "widow", "urban", "mark", "note", "src", "pub")

    def __init__(self, id, name, boxes, frm, to, size, nuclear, stem, joint, solo, leave,
                 servants, widow, mark, note, src, urban=False, pub=True):
        assert src, "every row needs a source: " + id
        assert to is None or frm <= to, "ends before it starts: " + id
        assert mark in MARKS, "unknown mark %r in %s" % (mark, id)
        assert 1.0 <= size <= 15.0, "implausible household size in " + id
        assert nuclear + stem + joint + solo == 100, \
            "structure shares must be 100, got %d in %s" % (nuclear + stem + joint + solo, id)
        assert 10 <= leave <= 40, "implausible leaving age in " + id
        assert 0 <= servants <= 100 and 0 <= widow <= 100, "shares out of range in " + id
        for bx in boxes:
            assert len(bx) == 4 and -90 <= bx[0] <= bx[1] <= 90 and -180 <= bx[2] <= bx[3] <= 180, \
                "bad box in " + id
        self.id = id
        self.name = name
        self.boxes = boxes
        self.frm = frm
        self.to = to
        self.size = size
        self.nuclear = nuclear
        self.stem = stem
        self.joint = joint
        self.solo = solo
        self.leave = leave
        self.servants = servants
        self.widow = widow
        self.urban = urban
        self.mark = mark
        self.note = note
        self.src = src
        # pub: is `size` a figure a source published for this place and year, or is it this
        # table's own number? Only the first kind can be used to test the generator — testing the
        # second kind is asking the generator whether it agrees with itself. Rows whose size is
        # the table's own carry pub=False and say so in their note.
        self.pub = pub


HOUSEHOLDS = [

    H("foraging_band", "before the first villages", WORLD, -100000, -8000,
      4.4, 70, 8, 18, 4, 18, 0, 8, ESTIMATED,
      "Nothing is published. A mobile band of twenty-five or thirty is not a household but a "
      "camp of five or six hearth groups; the numbers here describe the hearth group and are "
      "marked estimated. Note that the household is still mostly nuclear: the nuclear family is "
      "not a modern invention and it is not a European one either. The mean size in this row is this table's own, not any source's: what is published is the shape of the household, not how many people stood in it.",
      "History of the family", pub=False),

    H("early_farming", "the first farmers", WORLD, -8000, -3000,
      4.7, 60, 12, 24, 4, 18, 0, 8, ESTIMATED,
      "Settled life and heritable property make the joint household worth having for the first "
      "time: a house, a field and a herd are easier to hold between brothers than to divide. "
      "Marked estimated. The mean size in this row is this table's own, not any source's: what is published is the shape of the household, not how many people stood in it.",
      "History of the family", pub=False),

    H("bronze_old_world", "the Bronze and Iron Ages", OLD_WORLD, -3000, -801,
      4.7, 58, 14, 24, 4, 18, 12, 8, ESTIMATED,
      "No census survives, but the households of the Near Eastern and Mediterranean cities are "
      "known from their law codes and their inheritance disputes, and they are not small: a "
      "householder's house held his wife, his children, his widowed mother, his brother's widow "
      "and the slaves and dependants of the household. Servants at 12 per cent is the table's "
      "own figure and is marked estimated. The mean size in this row is this table's own, not any source's: what is published is the shape of the household, not how many people stood in it.",
      "History of the family", pub=False),

    H("bronze_world", "the Bronze and Iron Ages, everywhere else", WORLD, -3000, -801,
      4.7, 60, 12, 24, 4, 18, 6, 8, ESTIMATED,
      "The coverage check found this hole: the Bronze Age row covers the Old World only, so "
      "India under the early Vedic settlements, Shang China, the Americas and Africa had nothing "
      "for fifteen hundred years. Filled at the Old World shares and marked estimated. The mean size in this row is this table's own, not any source's: what is published is the shape of the household, not how many people stood in it.",
      "History of the family", pub=False),

    H("classical_world", "the classical world", WORLD, -800, 399,
      4.4, 58, 14, 23, 5, 18, 15, 9, ESTIMATED,
      "The Roman *familia* counted slaves and freedmen as members and the *domus* was a "
      "property-holding unit before it was a family. No household census survives for any of "
      "these centuries, so the whole row is marked estimated and the shares are held close to "
      "the Bronze Age ones. The mean size in this row is this table's own, not any source's: what is published is the shape of the household, not how many people stood in it.",
      "Family in ancient Rome", pub=False),

    H("medieval_world", "the Middle Ages", WORLD, 400, 1349,
      4.8, 60, 14, 21, 5, 18, 12, 9, ESTIMATED,
      "No household listing survives from anywhere in the world between the fall of Rome and "
      "the first English listings of the late sixteenth century. Marked estimated, and held at "
      "the classical shares. The mean size in this row is this table's own, not any source's: what is published is the shape of the household, not how many people stood in it.",
      "History of the family", pub=False),

    H("late_medieval", "the late Middle Ages", WORLD, 1350, 1549,
      4.9, 62, 16, 17, 5, 19, 14, 10, ESTIMATED,
      "Another hole the coverage check found: the first household listings anywhere in the world "
      "are the English ones of the late sixteenth century, so the two centuries between the "
      "Black Death and 1550 have no measured household anywhere. Filled a little below the "
      "medieval figure and marked estimated — after the plague there was more land per head and "
      "servants cost more, and the household is thought to have got smaller, not bigger. The mean size in this row is this table's own, not any source's: what is published is the shape of the household, not how many people stood in it.",
      "History of the family", pub=False),

    # ---------------------------------------------------------------- the measured rows
    H("early_modern_england", "England before 1750", BRITAIN, 1550, 1749,
      4.44, 66, 18, 9, 7, 21, 28, 12, RECORDED,
      "Published: the average size of household in England before 1750 was **4.44 persons**. "
      "This is the number that settled the argument. Laslett expected to find the three-"
      "generation household of the sociologists' imagination and found instead a mean under "
      "five and a structure that was already nuclear.",
      LASLETT),

    H("preindustrial_england", "England, 1750 to 1911", BRITAIN, 1750, 1911,
      4.81, 66, 18, 9, 7, 21, 22, 12, RECORDED,
      "Published: mean household size rose to **4.81** in the seventy years after 1750, and "
      "stayed at 4.75 or a little below for the whole period from the sixteenth century until "
      "1911, falling only after that — by about a third between 1911 and 1931. It was "
      "'surprisingly resistant to demographic fluctuation on the one hand and to the structural "
      "influences of industrialization on the other'.",
      LASLETT),

    H("victorian_england", "England and Wales, 1851 to 1911", BRITAIN, 1851, 1911,
      4.75, 71, 16, 6, 7, 21, 32, 12, RECORDED,
      "Published: throughout 1851-1911 the nuclear household — a single conjugal family unit "
      "with no additional members — was by far the most common, accounting for **70 to 73 per "
      "cent of all households** and housing 63 to 69 per cent of the population. A majority of "
      "people nonetheless lived in households of six or more, because the big households were "
      "few and crowded.",
      CENSUS),

    H("preindustrial_europe", "Europe before 1911", EUROPE, 1550, 1911,
      4.75, 64, 22, 7, 7, 22, 18, 12, MIXED,
      "Published for England and Wales: 4.75 or a little below, constant from the sixteenth "
      "century to 1911. Laslett's null hypothesis holds the same for north-western Europe as a "
      "whole — 'always and invariably nuclear unless the contrary can be proven' — and the "
      "Hajnal marriage pattern is the same story told from the other end: late marriage and a "
      "neolocal household on marriage make a nuclear household, and the two cannot be separated. "
      "Carried to the rest of Europe and marked mixed.",
      LASLETT + "; " + HAJNAL2),

    H("stem_europe", "the stem-family lands of Europe", STEM_EUROPE, 1550, 1911,
      4.4, 50, 38, 7, 5, 25, 16, 11, RECORDED,
      "Published: Le Play's *famille souche* — one married child stays in the parental house "
      "and inherits it, the rest go — was the arrangement of a broad band of Europe from the "
      "Pyrenees through France and the German lands to Bohemia and Scandinavia. Richard Wall "
      "later showed that Laslett's method could not detect it, because a stem family looks "
      "nuclear at the moment a census is taken and only becomes three-generational later. That "
      "is why this row exists beside the English one rather than inside it. The mean size in this row is this table's own, not any source's: what is published is the shape of the household, not how many people stood in it.",
      LASLETT + "; Household and family during urbanization and industrialization (2013)", pub=False),

    H("joint_india", "India, the joint family", SOUTH_ASIA, -300, 1999,
      5.4, 44, 12, 39, 5, 20, 8, 11, RECORDED,
      "Published: the Indian joint family is the extension of the nuclear family horizontally as "
      "well as vertically — all the brothers with their wives and children share one household, "
      "and it is strictly a **property-sharing unit**, not merely a co-residing one. The "
      "instructive complication, from the Indian sociologists, is that a household counted as "
      "nuclear by a census enumerator can still *function* as joint in every way that matters. "
      "The shares here are the residents, not the functioning. The mean size in this row is this table's own, not any source's: what is published is the shape of the household, not how many people stood in it.",
      "Joint family; History of the family", pub=False),

    H("east_asian_stem", "China, Japan and Korea", EAST_ASIA + JAPAN + KOREA, -200, 1949,
      4.6, 52, 36, 8, 4, 22, 10, 9, RECORDED,
      "Published: 'in the case of Japan, the existence of stem families was already known for a "
      "long time.' The Chinese ideal was the joint household of the classics — five generations "
      "under one roof — and the reality was closer to the stem: the ideal was what the gentry "
      "wrote about, and the stem was what the land could hold. Both give a household of about "
      "five. The mean size in this row is this table's own, not any source's: what is published is the shape of the household, not how many people stood in it.",
      LASLETT + "; History of the family", pub=False),

    H("early_modern_world", "the early modern world outside Europe", WORLD, 1550, 1899,
      5.1, 50, 14, 30, 6, 20, 12, 10, ESTIMATED,
      "A third hole: between 1550 and 1900 the only measured households on Earth are European, "
      "Chinese, Japanese, Korean and Indian, and this row is what is left — the Ottoman lands, "
      "South-East Asia, Africa, the Americas and Oceania. Five or so to a house, a third of them "
      "joint, and marked estimated. The mean size in this row is this table's own, not any source's: what is published is the shape of the household, not how many people stood in it.",
      "History of the family", pub=False),

    H("world_1950", "the world in the mid-twentieth century", WORLD, 1900, 1979,
      5.0, 52, 12, 30, 6, 20, 10, 9, MIXED,
      "Published: the world average was roughly **five people per household in the mid-twentieth "
      "century**, down to about 3.5 now. The shares are shaped from the modern regional rows "
      "and marked mixed.",
      UN_HH + "; worldpopulationclock, Global Average Household Size"),

    H("modern_world", "the world since 2000", WORLD, 2000, None,
      4.0, 52, 10, 28, 10, 22, 6, 10, RECORDED,
      "Published: the mean average household size across 153 countries or areas is **4.0 persons "
      "per household** and the median is 3.8. Eighty per cent of the world's countries sit "
      "between 2.3 and 5, and those countries hold 83 per cent of the world's population. The "
      "average *person*, note, lives in a household of about 4.9, because the big households "
      "hold more people — the mod wants the household figure, because it is filling houses.",
      UN_HH + "; Liu et al., A global perspective on household size and composition, 1970-2020"),

    H("modern_europe", "Europe and North America", EUROPE + N_AMERICA, 2000, None,
      2.4, 38, 4, 6, 52, 24, 2, 12, RECORDED,
      "Published: the median average household size across Europe and Northern America is "
      "**2.4**, and for half the countries of the region it falls between 2.3 and 2.7. "
      "One-person households are the largest single kind: 45 per cent in Finland, 43 in Germany, "
      "39 in Czechia, 38 in France and 38 in Japan. Germany 2.04, France 2.15, the United "
      "Kingdom 2.27, Russia 2.58, the United States 2.49.",
      UN_HH),

    H("modern_africa", "sub-Saharan Africa", AFRICA, 2000, None,
      4.8, 36, 8, 50, 6, 22, 8, 12, RECORDED,
      "Published: among the 42 countries of sub-Saharan Africa with a recent estimate the "
      "median average household size is **4.8**, and for half of them it lies between 4.1 and "
      "5.3. In eleven countries worldwide, households of six or more are more than half of all "
      "households, and most of them are here. Senegal 8.45, Gambia 8.70, Nigeria 4.66, Ethiopia "
      "4.73, DR Congo 5.17.",
      UN_HH),

    H("modern_india", "South Asia since 2000", SOUTH_ASIA, 2000, None,
      4.4, 44, 12, 38, 6, 22, 8, 11, RECORDED,
      "Published: India 4.38 to 4.57, Bangladesh 4.26, Pakistan 6.80 — Pakistan's is the largest "
      "household of any big country, and the joint-family share is held high here for that "
      "reason.",
      UN_HH),

    H("modern_mena", "the Middle East and North Africa", MENA, 2000, None,
      4.6, 44, 10, 40, 6, 22, 8, 11, MIXED,
      "Published: Egypt 4.13, Iran 3.43, Turkey 4.07, Yemen 6.55, Afghanistan 8.26. The average "
      "*person* in the region lives in a household of 6.2, which is the second-largest in the "
      "world after sub-Saharan Africa. The household figure here is the mean of the countries "
      "named and is marked mixed.",
      UN_HH + "; Pew Research, Household patterns by region"),

    H("modern_east_asia", "China, Japan and Korea since 2000",
      EAST_ASIA + JAPAN + KOREA, 1950, None,
      2.6, 52, 20, 6, 22, 24, 3, 12, RECORDED,
      "Published: China **2.70**, Japan 2.33, South Korea 2.34. China's is the most striking "
      "number in the whole table: the civilisation whose classical ideal was five generations "
      "under one roof now has a smaller mean household than Germany had in 1900.",
      UN_HH),

    H("modern_latin", "Latin America and the Caribbean", LATIN_AMERICA, 2000, None,
      3.4, 48, 10, 34, 8, 22, 8, 12, RECORDED,
      "Published: Brazil 3.31, Mexico 3.75, an average of about 3.5 for the region.",
      UN_HH),

    H("modern_se_asia", "South-East Asia and the Pacific", SE_ASIA + OCEANIA, 2000, None,
      3.6, 46, 12, 34, 8, 22, 8, 11, MIXED,
      "Published: Indonesia 3.86, the Philippines 4.23, Vietnam 3.44, Thailand 2.84, South "
      "Africa 3.36. Marked mixed: the region is a dozen different arrangements averaged into "
      "one row.",
      UN_HH),

    H("industrial_town", "the industrial town", EUROPE + N_AMERICA, 1800, 1899,
      4.1, 66, 16, 8, 10, 20, 14, 14, MIXED,
      "The industrial city packed people in and took lodgers in: a mill town household took in "
      "lodgers and apprentices because the rent demanded it, and a lodging house is not a family "
      "at all. The size is held a little above the countryside and the solo share higher. Marked "
      "mixed. The mean size in this row is this table's own, not any source's: what is published is the shape of the household, not how many people stood in it.",
      UN_HH + "; " + LASLETT, True, pub=False),
]
