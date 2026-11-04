"""Step 38 (D5): the day round — work, rest, market, prayer, season, by place and year.

Why this file exists
--------------------
`VillagerBehaviorSystem` is twenty-two lines and none of them is about behaviour. Nothing in this
mod knows when anyone gets up, whether today is market day, whether there is a day on which one
does not work, or how many times a day one stops to pray. A villager in Mecca in 900 and a
villager in Manchester in 1850 keep the same hours, because nobody has told the mod otherwise.

This is the table of what the day is made of.

The two things that are not universal
-------------------------------------
**The clock.** E. P. Thompson's distinction is the whole of it: a pre-industrial worker is
*task-oriented*, not *time-oriented*. You work until the task is done or the light goes; you do
not work "from nine to five", and the harvest day is longer than the day in February. The clock
comes with the factory, and with it the strange modern idea that a day's work is a number of
hours rather than a piece of work. The eight-hour day and the two-day weekend are not the default
state of the human race; they are about a hundred years old.

**The market.** A market is not open every day. In most of the world for most of history it meets
on a cycle, and the cycle is not always seven days long:

* **Java** — the **pasaran**, a five-day market week (Legi, Pahing, Pon, Wage, Kliwon), from
  *pasar*, "market". Villagers gathered every five days. The five-day and seven-day cycles
  together make the thirty-five-day *wetonan*.
* **Bali** — the **Pawukon**, ten concurrent weeks of one to ten days in a 210-day cycle; the
  three-day **Triwara** sets market days, which vary from village to village but fall **every
  three days**.
* **Rome** — the **nundinae**, the market day of the eight-day week (counted inclusively, so
  every eighth day by our reckoning; every ninth by the Romans' own).
* **Mesoamerica** — the **tianguis**, from Nahuatl *tiyanquiztli*, held on a fixed day of the
  week; the greatest of them, Tlatelolco, was set up and taken down every day.

Rules for a row
---------------
1. No source, no row.
2. `rest` is a weekday number, 0 for Sunday through 6 for Saturday, or -1 for "no day off at
   all", which is the honest answer for most of human history.
3. `market` is the cycle in days: 0 no market, 1 every day, 7 weekly, 5 the Javanese pasaran,
   8 the Roman nundinae, and so on.
4. How the year is divided is **not** in these rows: it lives in `SEASONS`, looked up on its
   own, so that naming the six seasons of India cannot silently decide what day the market is
   held there. Where no season row holds, the register falls back on latitude: two seasons in
   the tropics, four outside them.
5. Prayer times are **not** in these rows: they belong to a faith, not to a place, and they live
   in the `PRAYERS` list, keyed by faith. A caller asks for the faith's prayers and the place's
   day, and puts them together.
"""

from beliefs_table import (AFRICA, EAST_ASIA, EUROPE, MIDEAST, OLD_WORLD, SOUTH_ASIA, WORLD)
from households_table import MENA, N_AMERICA, SE_ASIA
from life_table import BRITAIN, ROME

RECORDED = "recorded"
MIXED = "mixed"
ESTIMATED = "estimated"
MARKS = (RECORDED, MIXED, ESTIMATED)

EGYPT = [(22.0, 31.5, 24.0, 35.0)]
# not the ROME box, which reaches longitude 45 and would put the nundinae in Athens
ITALY = [(36.0, 47.0, 6.0, 19.0)]
NORTH_AFRICA = [(20.0, 34.0, -18.0, 35.0)]
JAVA = [(-8.6, -5.5, 105.0, 115.0)]
BALI = [(-9.0, -7.8, 114.4, 115.8)]
MESOAMERICA = [(14.0, 24.0, -106.0, -83.0)]
ISRAEL = [(29.5, 33.5, 34.2, 35.9)]

THOMPSON = ("E. P. Thompson, Time, Work-Discipline, and Industrial Capitalism, Past and Present "
            "38 (1967)")
JAVANESE = "English Wikipedia, 'Javanese calendar'"
PAWUKON = "English Wikipedia, 'Pawukon calendar'"
TIANGUIS = "English Wikipedia, 'Tianguis'"
NUNDINAE = "English Wikipedia, 'Nundinae'"
PRAYER = "English Wikipedia, 'Fixed prayer times' and 'Canonical hours'"
SEASONS = "English Wikipedia, 'Season' and 'Ritu (season)'"


class D:
    """One day round: how the day is spent, and what the year is divided into."""

    __slots__ = ("id", "name", "boxes", "frm", "to", "work", "hours", "rest", "restname",
                 "market", "marketname", "urban", "mark", "note", "src")

    def __init__(self, id, name, boxes, frm, to, work, hours, rest, restname, market, marketname,
                 mark, note, src, urban=False):
        assert src, "every row needs a source: " + id
        assert to is None or frm <= to, "ends before it starts: " + id
        assert mark in MARKS, "unknown mark %r in %s" % (mark, id)
        assert work in ("task", "daylight", "clock", "shift"), "unknown work pattern in " + id
        assert 1 <= hours <= 20, "implausible working hours in " + id
        assert -1 <= rest <= 6, "rest day must be -1 or 0..6 in " + id
        assert 0 <= market <= 30, "implausible market cycle in " + id
        assert (market == 0) == (marketname == ""), \
            "a market needs a name and a name needs a market, in " + id
        assert (rest == -1) == (restname == ""), \
            "a rest day needs a name and a name needs a rest day, in " + id
        for bx in boxes:
            assert len(bx) == 4 and -90 <= bx[0] <= bx[1] <= 90 and -180 <= bx[2] <= bx[3] <= 180, \
                "bad box in " + id
        self.id = id
        self.name = name
        self.boxes = boxes
        self.frm = frm
        self.to = to
        self.work = work
        self.hours = hours
        self.rest = rest
        self.restname = restname
        self.market = market
        self.marketname = marketname
        self.urban = urban
        self.mark = mark
        self.note = note
        self.src = src


class S:
    """How a culture divides the year. Looked up on its own, so that naming the seasons of India
    cannot silently override what day of the week the market is held there."""

    __slots__ = ("id", "name", "boxes", "frm", "to", "count", "names", "mark", "note", "src")

    def __init__(self, id, name, boxes, frm, to, count, names, mark, note, src):
        assert src, "every row needs a source: " + id
        assert to is None or frm <= to, "ends before it starts: " + id
        assert mark in MARKS, "unknown mark %r in %s" % (mark, id)
        assert count == len(names), "%s: %d seasons but %d names" % (id, count, len(names))
        assert 2 <= count <= 24, "implausible number of seasons in " + id
        self.id = id
        self.name = name
        self.boxes = boxes
        self.frm = frm
        self.to = to
        self.count = count
        self.names = names
        self.mark = mark
        self.note = note
        self.src = src


SEASONS = [
    S("egypt_three_seasons", "the Nile", EGYPT, -3000, 1902, 3,
      ["the inundation", "the growing", "the harvest"], RECORDED,
      "Published: the Egyptian year is **three seasons** — *Akhet* the inundation, *Peret* the "
      "growing and *Shemu* the harvest — because the Nile, not the sun, decides what the year is "
      "made of. When the river rises the fields are under water and there is no field work to "
      "do, and that is when the pyramids were built. This row ends in **1902**, when the first "
      "Aswan Dam closed and the flood stopped coming; modern Egypt has four seasons like "
      "anywhere else, and the register says so.",
      "English Wikipedia, 'Season' and 'Egyptian calendar'"),

    S("india_six_seasons", "India", SOUTH_ASIA, -1500, 1947, 6,
      ["spring", "the hot season", "the rains", "autumn", "winter", "the cool season"], RECORDED,
      "Published: the Hindu year is **six seasons**, the *ritu* — Vasanta, Grishma, Varsha, "
      "Sharad, Hemanta and Shishira — each of two months. The four-season year of Europe is not "
      "the only way to cut it and it is not the commonest one.",
      SEASONS),

    S("china_terms", "China", EAST_ASIA, -1000, 1911, 4,
      ["spring", "summer", "autumn", "winter"], RECORDED,
      "Published: the Chinese farmer's year is divided by the **twenty-four solar terms**, each "
      "of about fifteen days, whose names are instructions rather than descriptions — 'the "
      "insects wake', 'the grain rain', 'the wheat is in ear', 'the white dew'. This row holds "
      "the four coarse seasons and the note carries the twenty-four.",
      "English Wikipedia, 'Solar term' and 'Chinese calendar'")
]

# How many times a day one stops, and when. This belongs to a faith, not to a place, and it is
# looked up by faith rather than by co-ordinates. `keep` is the number a lay person actually
# keeps, which is not always the number the faith sets out: the canonical hours are eight, but a
# parish church kept Matins and Evensong and a ploughman went to neither on a Tuesday.
PRAYERS = [
    ("islam", 5, 5, ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"],
     ["before dawn", "after the sun passes its height", "in the mid-afternoon", "at sunset",
      "at night"],
     "The five set prayers of Islam. The day is marked by them rather than by the clock: the "
     "first is said in the dark before dawn and the last after the night has closed.", PRAYER),

    ("christianity", 8, 2,
     ["Matins", "Lauds", "Prime", "Terce", "Sext", "None", "Vespers", "Compline"],
     ["in the night", "at dawn", "at the first hour", "at the third hour", "at noon",
      "at the ninth hour", "at sunset", "before sleep"],
     "The eight canonical hours, fixed for Western monasticism by the Rule of St Benedict to "
     "fulfil the 'seven times a day' of Psalm 119. Lauds was very rarely separated from Matins, "
     "so the eight were in practice seven; since the reform of 1971 Prime is gone and the "
     "offices number five. In a parish church, though, it was Matins and Evensong — two.",
     PRAYER),

    ("judaism", 3, 3, ["Shacharit", "Mincha", "Ma'ariv"],
     ["at dawn", "in the afternoon", "at nightfall"],
     "Three daily services, rooted in the twice-daily offering of the Temple, with the evening "
     "service added by rabbinic tradition. A fourth, Musaf, is said on the Sabbath and the "
     "festivals; a fifth, Ne'ilah, once a year on Yom Kippur.", PRAYER),

    ("hinduism", 3, 3, ["the morning sandhya", "the noon sandhya", "the evening sandhya"],
     ["at dawn", "at noon", "at dusk"],
     "The sandhyavandanam is performed at the three junctions of the day, where the light turns.",
     PRAYER),

    ("sikhism", 3, 3, ["the morning banis", "Rehras", "Kirtan Sohila"],
     ["at dawn", "at sunset", "before sleep"],
     "Nitnem is five compositions in three sittings: Japji Sahib, Jaap Sahib and Tav Prasad "
     "Savaiye after waking and bathing, Rehras in the evening, Kirtan Sohila before bed.",
     PRAYER),

    ("buddhism", 2, 2, ["the morning chanting", "the evening chanting"],
     ["at dawn", "at dusk"],
     "Buddhism has no set hours of prayer in the Abrahamic sense; the monasteries keep morning "
     "and evening chanting, and the lay day is not divided by it.", PRAYER),

    ("none", 0, 0, [], [], "No set hours. Whatever the seasons and the work demand.", ""),
]

DAYS = [

    D("foraging_band", "before the first villages", WORLD, -100000, -8000,
      "task", 5, -1, "", 0, "", ESTIMATED,
      "The shortest working day in the whole table. A band's foragers are often done by the "
      "middle of the morning, and the anthropologists who timed them found four or five hours of "
      "work a day feeding people better than the first farmers were fed. There is no market, "
      "because there is nothing to sell, and no day of rest, because there is no week.",
      "English Wikipedia, 'Hunter-gatherer' and 'Original affluent society'", ),

    D("early_farming", "the first farmers", WORLD, -8000, -3000,
      "task", 8, -1, "", 0, "", ESTIMATED,
      "Farming is the moment the working day lengthens and does not shorten again for ten "
      "thousand years. The work is still task-bound — you sow when the ground is ready and reap "
      "when the grain is — but there is more of it, and it comes every day of the year.",
      "English Wikipedia, 'Neolithic Revolution' and 'History of agriculture'"),

    D("bronze_old_world", "the Bronze and Iron Ages", OLD_WORLD, -3000, -801,
      "task", 9, -1, "", 7, "market day", ESTIMATED,
      "The first market days, in the first cities. Nothing is measured about them for any of "
      "these centuries, so the shares here are the table's own and the row is marked estimated.",
      "English Wikipedia, 'Bronze Age' and 'Market (place)'"),

    D("bronze_world", "the Bronze and Iron Ages, everywhere else", WORLD, -3000, -801,
      "task", 9, -1, "", 0, "", ESTIMATED,
      "Outside the city belts there is nothing you would call a market: goods move by gift and "
      "by kinship, not by sale on a fixed day.",
      "English Wikipedia, 'Gift economy' and 'Bronze Age'"),

    D("roman_italy", "Italy under Rome", ITALY, -800, 399,
      "task", 9, -1, "", 8, "the nundinae", RECORDED,
      "Published: the **nundinae** was the market day of the Roman eight-day week — every ninth "
      "day by the Romans' inclusive reckoning, every eighth by ours — and country people came "
      "into the town on it for the business of buying, selling and hearing the news. It is the "
      "one market cycle in this table that is not a multiple of nothing.",
      NUNDINAE),

    D("classical_world", "the classical world", WORLD, -800, 399,
      "task", 9, -1, "", 7, "market day", ESTIMATED,
      "A weekly market outside Italy, and no day on which nobody works: the gods had their "
      "festivals but the week had no sabbath. Marked estimated.",
      "English Wikipedia, 'Market (place)' and 'Economy of the Roman Empire'"),

    D("medieval_world", "the Middle Ages", WORLD, 400, 1349,
      "daylight", 9, 0, "Sunday", 7, "market day", RECORDED,
      "Published: Sunday is the Lord's Day and work stops on it, and the weekly market is fixed "
      "by charter to a day of the week — which is why so many English towns are called "
      "Market Drayton and Chipping Camden. The day itself is bound by the light: the ploughman's "
      "day runs from first light to last, longer in June than in December.",
      "English Wikipedia, 'Sabbath in Christianity', 'Market town' and 'Medieval agriculture'"),

    D("late_medieval", "the late Middle Ages", WORLD, 1350, 1549,
      "daylight", 9, 0, "Sunday", 7, "market day", MIXED,
      "The same round a little looser: after the Black Death a labourer could name his price, "
      "and the number of holidays — the Saints' days, the feast of the dedication, the wakes — "
      "grew, so that a fifteenth-century English worker might keep fifty or sixty days a year "
      "that were not working days at all.",
      "English Wikipedia, 'Medieval agriculture' and 'Holy day of obligation'"),

    D("early_modern_england", "England before the factories", BRITAIN, 1550, 1799,
      "task", 10, 0, "Sunday", 7, "market day", RECORDED,
      "Published, and it is the row that E. P. Thompson's essay is about: the working year here "
      "is **task-oriented, not time-oriented**. A man works until the job is finished, and the "
      "day shortens and lengthens with the light and the season. Saint Monday — the custom of "
      "not working on Monday either — held through the eighteenth century, and the preachers and "
      "the employers spent two hundred years trying to break it.",
      THOMPSON + "; English Wikipedia, 'Saint Monday'"),

    D("early_modern_europe", "Europe before 1900", EUROPE, 1550, 1899,
      "daylight", 10, 0, "Sunday", 7, "market day", MIXED,
      "Carried from the measured English case to the rest of Europe and marked mixed. Thompson's "
      "distinction is a western European one, and the further east you go the more the round is "
      "set by the Orthodox calendar of feasts and fasts rather than by the week.",
      THOMPSON, ),

    D("early_modern_world", "the early modern world outside Europe", WORLD, 1550, 1899,
      "daylight", 9, -1, "", 7, "market day", ESTIMATED,
      "The coverage check found this hole: between 1550 and 1900 the only day rounds this table "
      "can source are European, Islamic, Javanese, Balinese and Mesoamerican, and that leaves "
      "most of Asia, Africa and the Americas with nothing. Note what this row does *not* claim: "
      "outside the Abrahamic lands there is no day of the week on which nobody works, and "
      "pretending otherwise would be a European assumption smuggled in as a fact. Marked "
      "estimated.",
      "English Wikipedia, 'Sabbath' and 'Market (place)'"),

    D("islamic_world", "the Middle East and North Africa", MIDEAST + NORTH_AFRICA, 632, 1899,
      "daylight", 9, 5, "Friday", 7, "market day", RECORDED,
      "Published: Friday is the day of the congregational prayer, the jumu'ah, and it is the "
      "week's gathering rather than a sabbath of rest — the Quran does not forbid work on it. "
      "The day is marked out by the five prayers instead, and the suq is busiest after the "
      "noon prayer.",
      PRAYER + "; English Wikipedia, 'Jumu'ah' and 'Souq'"),

    D("java_pasaran", "Java", JAVA, 1, 1899,
      "daylight", 9, -1, "", 5, "the pasaran", RECORDED,
      "Published: the Javanese week is **five days long** — Legi, Pahing, Pon, Wage, Kliwon — and "
      "the word *pasaran* comes from *pasar*, 'market', because the market was held on one of "
      "the five. 'Pasar Kliwon' and 'Pasar Legi' are still the names of markets now open every "
      "day. With the seven-day week the five-day cycle makes the thirty-five-day *wetonan*, by "
      "which marriages are dated and characters read.",
      JAVANESE),

    D("bali_triwara", "Bali", BALI, 1, 1899,
      "daylight", 9, -1, "", 3, "the three-day market", RECORDED,
      "Published: the Balinese **Pawukon** runs ten concurrent weeks of one to ten days in a "
      "210-day cycle, and the **Triwara**, the three-day week, sets the market days — which vary "
      "from village to village but fall every three days. When the five-day and seven-day "
      "cycles meet, every thirty-five days, that day is a festival.",
      PAWUKON),

    D("mesoamerica_tianguis", "Mexico and Central America", MESOAMERICA, -1500, 1899,
      "daylight", 9, -1, "", 7, "the tianguis", RECORDED,
      "Published: the **tianguis**, from Nahuatl *tiyanquiztli*, is the market held on a fixed "
      "day of the week, and the tradition runs unbroken from the pre-Hispanic period to the "
      "present. The greatest of them all, Tlatelolco, was set up and taken down **every day**.",
      TIANGUIS),

    D("industrial_town", "the factory town", EUROPE + N_AMERICA, 1800, 1899,
      "clock", 12, 0, "Sunday", 7, "market day", RECORDED,
      "Published, and this is the row where the clock wins: **time now is money**, the factory "
      "bell and not the light sets the day, and twelve to sixteen hours is the length of it. The "
      "week's rhythm moves with it — Saint Monday dies in the first generation of factories, and "
      "the Saturday half-holiday is won a generation later.",
      THOMPSON + "; English Wikipedia, 'Factory Acts' and 'Eight-hour day'", True),

    D("world_1900", "the world in the twentieth century", WORLD, 1900, 1945,
      "clock", 10, 0, "Sunday", 7, "market day", RECORDED,
      "Published: the ten-hour day and the Sunday rest, spreading with the railway and the "
      "factory beyond Europe. The eight-hour day is the demand of the whole labour movement, and "
      "in much of the world it is not yet won.",
      "English Wikipedia, 'Eight-hour day' and 'Labor movement'"),

    D("modern_world", "the world since 1946", WORLD, 1946, None,
      "clock", 8, 0, "Sunday", 7, "market day", RECORDED,
      "Published: the eight-hour day and the two-day weekend, which are about a hundred years "
      "old and are the least ancient thing in this table. Note what they replaced: for the whole "
      "of human history before 1900, a working day of eight hours and a two-day break every "
      "week would have been unrecognisable.",
      "English Wikipedia, 'Eight-hour day', 'Weekend' and 'Workweek'"),

    D("modern_mena", "the Middle East and North Africa since 1900", MENA, 1900, None,
      "clock", 8, 5, "Friday", 7, "market day", MIXED,
      "Published: Friday is the day of gathering, and the working week bends around it — "
      "Sunday to Thursday in much of the Gulf and the Levant, Monday to Friday in Turkey and "
      "elsewhere. Marked mixed, because the region no longer agrees with itself.",
      "English Wikipedia, 'Workweek' and 'Jumu'ah'"),

    D("modern_israel", "Israel since 1948", ISRAEL, 1948, None,
      "clock", 8, 6, "the Sabbath", 7, "market day", RECORDED,
      "Published: the Sabbath runs from before sunset on Friday to nightfall on Saturday, and "
      "the week's work stops for it. The working week in Israel is Sunday to Thursday, or "
      "Monday to Saturday for some, and it is the one place in the modern world where the rest "
      "day is Saturday by law rather than by custom.",
      "English Wikipedia, 'Shabbat' and 'Workweek'")
]
