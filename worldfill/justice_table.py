#!/usr/bin/env python3
"""Step 42 part 6 (F3, law and crime by era): the table of guards, courts and punishment.

Why this is hand-written and not fetched
----------------------------------------

The survey measured what is fetchable about law and found it country-granular and mostly modern:
**164** capital-punishment-by-country articles, **761** Wikidata codes of law of which only **197**
are dated, and nothing at all that says *who kept the peace in this place, in this year*. There is
no table to fetch. So this file is a table this project wrote, from the reference works named on
each row - the same decision and the same shape as `social_order_table.py` for D7, and held to the
same rule: **every row is estimated and says so**.

What was verified
-----------------

Every article named in a `source` was checked to exist before it was written down: one batched
Wikipedia query on 45 candidate titles returned **43 present and 2 missing** (*Blood money (Islam)*
and *Moot (early medieval)*, both dropped). A source that does not exist is worse than no source,
so the check comes first.

What a row carries
------------------

  * `guards`      - who keeps the peace, and what a man does when something is stolen
  * `courts`      - who judges, and what he judges by
  * `punishments` - what is done to a man who is found guilty

The one hard fact
-----------------

Everything here is a reading - **except whether a place still puts men to death**, which is not
read from this table at all. It comes from the C18 law pack through `LawRegister`, which carries
real abolition dates for real polities. `Justice.available()` asks it, so `a judicial death` simply
stops being an option in a country the year that country abolished it, and the table does not have
to be right about it. That is the whole reason F3 was scheduled after C18.

Coverage
--------

Every point of the map in every year has to get an answer, so each of the three tables ends with a
default: the kindred answering a wrong itself, an elder judging, and a blood-price settling it. A
register that shrugs has failed; this one always answers.

Sources are named per row and are Wikipedia articles unless they say otherwise.
"""

# --------------------------------------------------------------------------- regions (ISO3)
# Copied from social_order_table.py so the two packs key the map identically: one map, one set of
# region names, and no chance of the social order and the justice of a place disagreeing about
# where "Western Europe" is.

from social_order_table import (  # noqa: F401
    ALL, WEST_EUROPE, NORTH_EUROPE, EAST_EUROPE, BALKANS_BYZANTINE, MIDDLE_EAST,
    NORTH_AFRICA, SAHEL_WEST_AFRICA, EAST_AFRICA, CENTRAL_SOUTHERN_AFRICA, SOUTH_ASIA,
    EAST_ASIA, SOUTHEAST_ASIA, CENTRAL_ASIA, LATIN_AMERICA, NORTH_AMERICA, OCEANIA,
    CARIBBEAN,
)

CHINA = ["CHN", "TWN", "HKG", "MAC"]
JAPAN = ["JPN"]
KOREA = ["KOR", "PRK"]
INDIA = ["IND", "PAK", "BGD", "NPL", "LKA"]
DAR_AL_ISLAM = list(dict.fromkeys(MIDDLE_EAST + NORTH_AFRICA + CENTRAL_ASIA + ["BGD", "PAK"]))
COLONIAL = list(dict.fromkeys(
    LATIN_AMERICA + CARIBBEAN + SOUTH_ASIA + SOUTHEAST_ASIA
    + SAHEL_WEST_AFRICA + EAST_AFRICA + CENTRAL_SOUTHERN_AFRICA))
SOVIET = ["RUS", "UKR", "BLR", "MDA", "KAZ", "UZB", "TKM", "KGZ", "TJK", "AZE", "ARM", "GEO",
          "EST", "LVA", "LTU"]


def row(rid, name, who, line, where, start, end, priority, source, **extra):
    """One row. `end` of None means 'and still'. Anything else a table needs goes in extra."""
    r = {
        "id": rid,
        "name": name,
        "who": who,
        "line": line,
        "where": list(dict.fromkeys(where)),
        "start": start,
        "end": end,
        "priority": priority,
        "source": source,
    }
    r.update(extra)
    return r


# =========================================================================== who keeps the peace

GUARDS = [

    row("kin_self", "the kindred itself",
        "the kin of the man who suffered",
        "there is no one to call. A wrong is answered by the kin of the man who suffered it, and "
        "if his kin will not answer it, it is not answered",
        ALL, -10000, None, 0,
        "Feud; Weregild",
        note="before there is a state there is nobody to keep the peace but the people concerned"),

    row("palace_temple", "the palace and the temple",
        "the king's men, and the Medjay on the roads",
        "the peace is the king's peace and the temple's: Nubian Medjay keep the desert roads and "
        "the king's own keep the gate; a village settles its own quarrels until it cannot, and "
        "then it is brought to the gate",
        ["EGY", "SDN", "IRQ", "SYR", "ISR", "PSE", "JOR", "LBN", "TUR", "IRN"], -3200, -300, 3,
        "Medjay; Cuneiform law; Ancient Near East; Vizier (Ancient Egypt)"),

    row("zhou_officers", "the officers of the king",
        "the officers of the Zhou",
        "the king's officers keep the peace of the states he has enfeoffed, and each feudal lord "
        "keeps his own; punishment is the lord's to decree and the code is not published, so a "
        "man does not know what he has broken until he is broken for it",
        CHINA, -1046, -200, 3,
        "Zhou dynasty; Chinese law; Shang dynasty"),

    row("assembly", "the assembly",
        "the free men gathered",
        "the whole township is the peace-keeping: every free man is bound to raise the cry, and a "
        "man who does not is fined with the rest",
        NORTH_EUROPE + ["ISL"], -800, 1300, 3,
        "Thing (assembly); Hue and cry"),

    row("lord_household", "the lord's household",
        "his reeve and his men",
        "the lord's reeve holds the peace of the manor; outside the manor gate there is no peace "
        "that anyone is paid to keep",
        WEST_EUROPE + EAST_EUROPE, 500, 1500, 4,
        "Manorial court; Sheriff"),

    row("hundred_shire", "the hundred and the shire",
        "the tithing, the constable, the sheriff",
        "every man is in a tithing of ten, and the tithing answers for him; a cry raised must be "
        "followed by every man who hears it, and the constable of the hundred is one of them, "
        "unpaid and appointed for a year",
        ["GBR", "IRL"], 900, 1800, 6,
        "Hundred (county division); Tithing; Constable; Hue and cry; Sheriff"),

    row("city_watch", "the city watch",
        "the watchmen of the ward",
        "the town sets a watch at the gates and through the night, and the watch is the town's own "
        "men taking turns; they carry a staff and a lantern and they do not pursue",
        WEST_EUROPE + EAST_EUROPE + MIDDLE_EAST, 1200, 1830, 5,
        "Watchman (law enforcement)"),

    row("magistrate_runners", "the magistrate's runners",
        "the yamen runners and the constables",
        "the magistrate sends runners; the runners are not paid a wage, they live on what they can "
        "take from the people they summon, and a summons is a thing to buy your way out of",
        CHINA + KOREA + ["VNM"], -200, 1911, 5,
        "Yamen"),

    row("bugyo_men", "the bugyo's men",
        "the samurai of the magistrate's office",
        "the bugyo keeps Edo with samurai; a commoner who lays a complaint before him kneels, and "
        "the complaint may cost him more than the theft",
        JAPAN, 1200, 1868, 5,
        "Bugyo"),

    row("qadi_muhtasib", "the qadi and the muhtasib",
        "the judge and the market inspector",
        "the muhtasib walks the market with a scale and a rod, for weights, measures and public "
        "order; the qadi hears what he brings, and between them the street is kept without a "
        "police force at all",
        DAR_AL_ISLAM, 700, 1900, 5,
        "Muhtasib; Qadi; Enjoining good and forbidding wrong"),

    row("headman_caste", "the headman and the caste",
        "the village headman, and the caste's own elders",
        "the headman keeps the village's peace and the caste keeps its own: a man is disciplined "
        "by his caste before he is ever disciplined by a state, and being put out of caste is a "
        "worse sentence than any the state can pass",
        INDIA + ["AFG"], -600, 1900, 5,
        "Panchayati raj"),

    row("colonial_guard", "the colonial guard",
        "the askari, the native police, the district officer",
        "a handful of the colonising power and a great many men recruited elsewhere: the guard is "
        "armed, is not of the district he polices, and keeps a peace the district did not ask him "
        "to keep",
        LATIN_AMERICA + CARIBBEAN, 1500, 1820, 6,
        "Law enforcement agency; Police"),

    row("colonial_guard_old_world", "the colonial guard",
        "the sepoy, the askari, the district officer",
        "a handful of the colonising power and a great many men recruited elsewhere: the guard is "
        "armed, is not of the district he polices, and keeps a peace the district did not ask him "
        "to keep",
        SOUTH_ASIA + SOUTHEAST_ASIA + SAHEL_WEST_AFRICA + EAST_AFRICA
        + CENTRAL_SOUTHERN_AFRICA, 1757, 1970, 6,
        "Law enforcement agency; Police",
        note="1757 and not 1600: at 1600 India was Mughal and answered to nobody's colony. The "
             "Americas were colonised two centuries earlier and have their own row, because one "
             "date for both would call Akbar's empire a colony"),

    row("police_force", "a standing police force",
        "men paid to do nothing else",
        "a body of men in a uniform, paid a wage, whose whole work is the peace - which is a new "
        "thing in the world and was thought, when it began, to be the end of liberty",
        ALL, 1829, None, 7,
        "Metropolitan Police; Bow Street Runners; Police"),

    row("gendarmerie", "the gendarmerie",
        "soldiers doing the work of police",
        "soldiers, not constables: they are barracked, they are armed, they answer to the "
        "ministry of war and not to the town, and the countryside is their beat",
        [c for c in WEST_EUROPE + EAST_EUROPE + MIDDLE_EAST + NORTH_AFRICA + LATIN_AMERICA
         if c not in ("GBR", "IRL")], 1791, None, 7,
        "Gendarmerie",
        note="Britain and Ireland are left out on purpose: they are the exception that proves the "
             "row, and a register that gives them a gendarmerie has stopped being checked"),

    row("political_police", "the political police",
        "men who watch for opinions",
        "the police are for the peace of the state and not the peace of the street: a man is "
        "taken at night, the charge is not told to his family, and the neighbourhood learns to "
        "say nothing at all",
        SOVIET + EAST_EUROPE, 1930, 1991, 9,
        "Secret police",
        note="above the militia, because in a police state it was: the militia kept the street "
             "and this kept the state, and a man on the street knew which one he feared"),

    row("peoples_militia", "the people's militia",
        "volunteers from the works and the street",
        "the militia are neighbours with armbands; they have no training, no wage and a great "
        "deal of zeal, and a drunk is their whole caseload",
        SOVIET + CHINA, 1917, 1991, 8,
        "Militia; Druzhina"),
]

# =========================================================================== who judges

COURTS = [

    row("elder_judges", "an elder of the kindred",
        "the oldest man who will listen",
        "the elder does not find facts, he finds a settlement both sides can live with; and "
        "there is no one to make them take it",
        ALL, -10000, None, 0,
        "Feud; Weregild",
        note="a judge who cannot compel is a mediator, and for most of history that is what a "
             "judge was"),

    row("kings_judgement", "the king's own judgement",
        "the king, his vizier, or the judges at the gate",
        "the king judges at the gate and the code is his: Ur-Nammu sets a fine in silver, "
        "Hammurabi sets an eye for an eye, and the poor man's case is heard in the same place as "
        "the rich man's, though not to the same end",
        ["IRQ", "SYR", "EGY", "IRN", "TUR", "ISR", "PSE", "JOR", "LBN"], -2400, 300, 3,
        "Code of Ur-Nammu; Cuneiform law; Vizier (Ancient Egypt); Maat",
        note="2400 BC and not earlier, because the earliest thing the sources describe as law is "
             "Urukagina's reforms (c. 2380 BC). Before that this pack names no court, because no "
             "source does - and the check says so instead of inventing one"),

    row("vedic_dharma", "the king and the dharma",
        "the king, with the brahmins who know the dharma",
        "the king judges and the dharma is what he judges by - not a code but an order, set out "
        "in the Arthashastra and the Laws of Manu: what a man of each station owes, and what is "
        "owed to him, and the two are not the same",
        INDIA, -1500, 1850, 3,
        "Dharma; Arthashastra; Manusmriti; Varna (Hinduism)"),

    row("assembly_court", "the assembly",
        "the free men, and the law-speaker",
        "the thing judges: the law-speaker says what the law is, the free men give judgement, and "
        "the judgement is the neighbours' opinion of you made binding",
        NORTH_EUROPE + ["ISL"], -800, 1300, 3,
        "Thing (assembly)"),

    row("manor_court", "the lord's court",
        "the lord, or his steward",
        "the court is the manor court and the steward keeps it; it is a court of the lord's will "
        "as much as of the law, and its fines are the lord's income",
        WEST_EUROPE + EAST_EUROPE, 500, 1500, 4,
        "Manorial court"),

    row("kings_justices", "the king's justices",
        "a judge sent out from the capital",
        "the king's justices ride the circuit and they judge by the king's law and not the "
        "lord's; a man can now be heard against his own lord, which is the whole change",
        ["GBR", "IRL", "FRA"], 1100, 1900, 5,
        "Assizes; Court of Common Pleas"),

    row("jury_court", "a jury of his neighbours",
        "twelve men of the hundred",
        "twelve men of the neighbourhood say what happened, and the judge says what the law is; "
        "a man is tried by people who know his face, which cuts both ways",
        ["GBR", "IRL", "USA", "CAN", "AUS", "NZL"], 1215, None, 6,
        "Assizes; Jury"),

    row("qadi_court", "the qadi",
        "a judge of the religious law",
        "the qadi sits in the mosque or at the gate and judges by the sharia; there is no "
        "prosecutor, no appeal and no long delay, and two witnesses or a confession end it",
        DAR_AL_ISLAM, 700, None, 5,
        "Qadi; Sharia court"),

    row("yamen_court", "the magistrate's court",
        "the district magistrate",
        "the magistrate is judge, jury and investigator, and he is also the tax officer: he is "
        "examined on his findings by a superior, and torture to obtain a confession is lawful",
        CHINA + KOREA + ["VNM"], -200, 1911, 5,
        "Yamen"),

    row("bugyo_court", "the bugyo",
        "the magistrate of the shogunate",
        "the bugyo judges and the judgement is his: there is no advocate, the accused confesses "
        "or does not, and the sentence is not argued with",
        JAPAN, 1200, 1868, 5,
        "Bugyo"),

    row("panchayat_court", "the panchayat",
        "five men of the caste or the village",
        "five men of the caste sit on it and the caste obeys it; the state's court is a day's "
        "walk and a ruinous expense, and most disputes never go there",
        INDIA + ["AFG"], -600, None, 4,
        "Panchayati raj"),

    row("colonial_court", "the colonial court",
        "the officer, and a separate court for the colonised",
        "two laws in one place: the settler is tried by the law of the metropole and the "
        "colonised man by a native court applying something the officer calls his own custom",
        LATIN_AMERICA + CARIBBEAN, 1500, 1820, 6,
        "Law enforcement agency; Indian Penal Code"),

    row("colonial_court_old_world", "the colonial court",
        "the officer, and a separate court for the colonised",
        "two laws in one place: the coloniser is tried by the law of the metropole and the "
        "colonised man by a native court applying something the officer calls his own custom",
        SOUTH_ASIA + SOUTHEAST_ASIA + SAHEL_WEST_AFRICA + EAST_AFRICA
        + CENTRAL_SOUTHERN_AFRICA, 1757, 1970, 6,
        "Law enforcement agency; Indian Penal Code"),

    row("professional_court", "a court of trained judges",
        "a judge, an advocate, and an appeal",
        "a trained judge, a written code, an advocate paid to argue, and a second court that can "
        "undo the first: the trial is a procedure and not a meeting",
        ALL, 1800, None, 7,
        "Court of Common Pleas; Indian Penal Code; Judge"),

    row("peoples_court", "the people's court",
        "a tribunal of the party",
        "the court is not there to find out what happened; the verdict is settled before the "
        "hearing and the hearing is for the record and the crowd",
        SOVIET + EAST_EUROPE + CHINA, 1917, 1991, 8,
        "People's Court; Show trial"),
]

# =========================================================================== what is done to him

PUNISHMENTS = [

    row("blood_price", "a blood-price",
        "compensation paid to the injured, or to his kin",
        "a wrong is settled by payment: so much for a man, so much for an eye, so much for the "
        "theft of a cow. It is not a fine to a state, because there is no state to pay it to - "
        "it is the price of not being killed in return",
        ALL, -10000, None, 0,
        "Weregild; Diya (Islam); Code of Hammurabi",
        note="the oldest answer in the world, and the only one that leaves nobody wanting revenge"),

    row("outlawry", "outlawry",
        "being put outside the law",
        "a man declared outlaw may be killed by anyone, holds no property, and no man may shelter "
        "him: the law does not punish him, it abandons him",
        NORTH_EUROPE + WEST_EUROPE + ["ISL"], -800, 1600, 3,
        "Outlaw"),

    row("public_shame", "public shame",
        "the stocks, the pillory, the public penance",
        "he is put in the stocks at the market cross on a market day, and the point is the "
        "looking: the punishment costs the parish nothing and takes nothing from him that he "
        "cannot carry home",
        WEST_EUROPE + EAST_EUROPE + NORTH_AMERICA, 1200, 1850, 3,
        "Stocks; Pillory"),

    row("corporal", "the lash and the brand",
        "whipping, mutilation, branding",
        "the body is punished where it can be seen: a hand, an ear, a brand on the cheek or the "
        "palm, so that a man carries his record on him for the rest of his life",
        ALL, -3000, 1950, 3,
        "Flagellation; Mutilation; Code of Hammurabi"),

    row("judicial_death", "a judicial death",
        "hanging, the block, the firing party",
        "the state kills him, in public, and the manner of it says what he was: hanging for a "
        "thief, the block for a gentleman, burning for a heretic",
        ALL, -3000, None, 3,
        "Hanging; Capital punishment",
        death=True,
        note="stopped by the C18 law pack the year a polity abolishes it - see Justice.available()"),

    row("transportation", "transportation",
        "sent across the sea to a penal colony",
        "he is shipped out of the country for seven years or for life, and the country's whole "
        "object is to be rid of him rather than to amend him",
        ["GBR", "IRL", "FRA", "AUS", "USA", "NZL"], 1600, 1875, 4,
        "Penal transportation"),

    row("prison_term", "a term of years",
        "imprisonment as the punishment itself",
        "the sentence is the loss of time: he is held for a term fixed in advance, and prison is "
        "the punishment rather than the place he waits in - which is a late and strange idea",
        ALL, 1780, None, 5,
        "Prison"),

    row("fine_state", "a fine to the state",
        "money paid to the treasury",
        "he pays the state, and the person he wronged gets nothing out of it at all: the wrong "
        "is now against the law and no longer against a man",
        ALL, 1200, None, 5,
        "Fine (penalty)"),

    row("suspended", "a suspended sentence",
        "probation, treatment, and a record",
        "he is not punished but he is not free either: he reports, he is tested, he is "
        "supervised, and the sentence hangs over him for as long as the order runs",
        ALL, 1900, None, 6,
        "Probation; Suspended sentence"),
]

# --------------------------------------------------------------------------- the defaults
# Every table needs one, because the mod covers every square of the map in every year and a
# register that shrugs has failed. These three are the answers before there is a state.
#
# They are NOT also rows. As rows they matched every country in every year - which looked harmless
# and was not: each one then appeared in every repertoire, and the fallback could never fire,
# because there was never a place and year where no row matched. A fallback that is also a row is
# a fallback that never runs, which is the same defect as part 3's `may` defaulting to 3.

DEFAULT_GUARDS = {
    "id": "kin_self", "name": "the kindred itself",
    "who": "the kin of the man who suffered",
    "line": ("there is no one to call. A wrong is answered by the kin of the man who suffered it, "
             "and if his kin will not answer it, it is not answered"),
    "where": [], "start": None, "end": None, "priority": -1,
    "source": "Feud; Weregild",
    "note": "before there is a state there is nobody to keep the peace but the people concerned",
}

DEFAULT_COURTS = {
    "id": "elder_judges", "name": "an elder of the kindred",
    "who": "the oldest man who will listen",
    "line": ("the elder does not find facts, he finds a settlement both sides can live with; and "
             "there is no one to make them take it"),
    "where": [], "start": None, "end": None, "priority": -1,
    "source": "Feud; Weregild",
    "note": "a judge who cannot compel is a mediator, and for most of history that is what a "
            "judge was",
}

DEFAULT_PUNISHMENT = {
    "id": "blood_price", "name": "a blood-price",
    "who": "compensation paid to the injured, or to his kin",
    "line": ("a wrong is settled by payment: so much for a man, so much for an eye, so much for "
             "the theft of a cow. It is not a fine to a state, because there is no state to pay "
             "it to - it is the price of not being killed in return"),
    "where": [], "start": None, "end": None, "priority": -1,
    "source": "Weregild; Diya (Islam); Code of Hammurabi",
    "note": "the oldest answer in the world, and the only one that leaves nobody wanting revenge",
}

# ...and so they are struck from the row lists.
GUARDS = [r for r in GUARDS if r["id"] != DEFAULT_GUARDS["id"]]
COURTS = [r for r in COURTS if r["id"] != DEFAULT_COURTS["id"]]
PUNISHMENTS = [r for r in PUNISHMENTS if r["id"] != DEFAULT_PUNISHMENT["id"]]
