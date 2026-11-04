#!/usr/bin/env python3
"""Step 42 part 7 (F8, borders and permits): what a crossing is, and what it demands of you.

Why this is hand-written
------------------------

The survey measured what is fetchable and there is no table of border posts: no source says *what
the frontier of this place demanded of a traveller, in this year*. So, as with D7 and F3, this is a
table this project wrote from the reference works named on each row, and **every row is estimated
and says so**.

What was verified
-----------------

Every article named in a `source` was checked to exist first: one batched Wikipedia query on 28
candidate titles returned **26 present and 2 missing** (*Caravan (traders)*, *Internal tariff* -
both dropped). Then the dated claims F8 turns on were pulled out of the articles themselves, so
the years on those rows are read and not guessed:

  * **Quarantine** - "the trentino, or thirty-day isolation period, first imposed in **1377** in
    the Republic of Ragusa, Dalmatia (modern Dubrovnik)"; the *quarantena* that followed is where
    the word comes from.
  * **Passport** - "the modern passport was universally adopted and standardised in **1920**", and
    the British Nationality and Status of Aliens Act was passed in **1914** - the First World War
    the plan names. The League of Nations held the Paris Conference on Passports & Customs
    Formalities in 1920.
  * **Zollverein** - "formally started on 1 January **1834**"; by 1866 it covered most of the
    German states. A row in which the answer is *no border at all*.
  * **Sakoku** - the edicts run **1633 to 1639**, and the policy ended after **1853** (Perry).
  * **Canton System** - **1757-1842**, all Western trade through one door.
  * **Octroi** - a Mazarin ordinance of **1647**, Paris re-established **1798**, the law of **1809**.
  * **Turnpike trust** - a bill in **1621/22**, and the end came with the Local Government Act
    **1888**.

What a row carries
------------------

  * `what`    - what the crossing actually is: a gate, a ford, a customs house, a lazaretto
  * `demand`  - what it demands of you: a gift, a toll, duty, papers, forty days, or your turning
                back
  * `flags`   - `papers` (it wants to see who you are), `quarantine` (it holds you),
                `closed` (it will not let you through at all),
                `sea` (it stands at a port and only meets you if you come by water), and
                `internal` (it is a toll inside one state, not a line between two)

The last two are why the table works at all. A lazaretto is not a frontier: it is a walled yard by
the water where a ship's company sits out the plague, and a traveller crossing a land border never
meets one. A turnpike is the opposite: it is the toll you pay for the road inside a country, and a
ship putting in at Liverpool never meets one either. Without the distinction the priority ordering
has to choose between them and gets both wrong - the lazaretto won everywhere from 1377 to 1860,
so an Englishman riding north in 1800 was told he was being quarantined.

The border itself is not in this table
--------------------------------------

**Where the line runs is not data.** It is derived at runtime from `RulerRegister`: two points in
different hands mean a border between them, and bisection finds where. That is the "neighbouring
state" the survey said F8 needed, and it is why this part needed no state graph building - the
ruler register already is one.

Coverage
--------

Every point of the map in every year has to get an answer, so the table ends with a default: open
ground, where there is nothing to cross and nobody to ask. A register that shrugs has failed.

Sources are named per row and are Wikipedia articles unless they say otherwise.
"""

# --------------------------------------------------------------------------- regions (ISO3)
# Copied, as in justice_table.py, so the packs cannot disagree about where a region is.

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
MEDiterranean = list(dict.fromkeys(
    ["ITA", "GRC", "TUR", "HRV", "ESP", "FRA", "EGY", "TUN", "DZA", "MAR", "CYP", "MLT", "ISR",
     "PSE", "LBN", "SYR", "ALB", "MNE", "BIH", "SVN", "PRT", "ROU", "BGR", "UKR", "RUS"]))
MEDITERRANEAN = MEDiterranean
BRITISH_ISLES = ["GBR", "IRL"]
GERMAN_STATES = ["DEU", "AUT", "CZE", "POL", "LUX", "BEL", "NLD", "CHE"]
SILK_ROAD = list(dict.fromkeys(
    CENTRAL_ASIA + ["IRN", "AFG", "CHN", "MNG", "IRQ", "SYR", "TUR", "PAK", "IND"]))
ROMAN_LIMES = list(dict.fromkeys(
    WEST_EUROPE + EAST_EUROPE + BALKANS_BYZANTINE + NORTH_AFRICA + MIDDLE_EAST))


def row(rid, name, what, demand, line, where, start, end, priority, source, **extra):
    r = {
        "id": rid,
        "name": name,
        "what": what,
        "demand": demand,
        "line": line,
        "where": list(dict.fromkeys(where)),
        "start": start,
        "end": end,
        "priority": priority,
        "source": source,
        "papers": False,
        "quarantine": False,
        "closed": False,
        "sea": False,
        "internal": False,
    }
    r.update(extra)
    return r


CROSSINGS = [

    row("tribute_gate", "a gate and a gift",
        "the gate of a town, or the fire of a chief",
        "a gift, and leave asked for",
        "you stop at the gate and you ask. Leave is a matter of who you are and what you bring, "
        "and a man who does not stop and ask has declared himself an enemy",
        ALL, -3000, 1500, 4,
        "Safe conduct; Firman; Silk Road"),

    row("river_toll", "a toll at the crossing",
        "a ford, a ferry, or a bridge with a man on it",
        "a toll, paid in coin or in kind",
        "the river is the border and the bridge is the toll: a man in a hut takes so much for a "
        "cart, so much for a beast, so much for a man on foot, and the bridge is why he is there",
        ALL, -1000, 1900, 3,
        "Toll (fee); Turnpike trust"),

    row("imperial_frontier", "the frontier",
        "the limes: a road, a palisade, and a garrison behind it",
        "the leave of the state, which is not given at the gate",
        "there is no gate to stop at. There is a line the empire drew, a road along the back of "
        "it, and a fort every day's march: you are let through because someone in authority has "
        "already decided you may be, and not because you asked at the time",
        ROMAN_LIMES, -30, 500, 4,
        "Limes; Border control"),

    row("caravan_gate", "the caravanserai and the gate",
        "a walled yard on the road, and the toll at the city gate beyond",
        "a toll on the goods, and a night in the yard",
        "the road is safe because the ruler takes a share of what goes along it: you pay at the "
        "gate for what you carry, you sleep where the beasts sleep, and the toll is the price of "
        "the road not being full of thieves",
        SILK_ROAD + NORTH_AFRICA, 200, 1800, 4,
        "Silk Road; Toll (fee); Caravan"),

    row("octroi", "the octroi",
        "the town gate, and a barrier across it",
        "a toll on everything you carry in to sell",
        "the border is not the edge of the country, it is the wall of the town: the octroi takes "
        "a duty on food and fuel and cloth coming in, a clerk writes it in a book, and the poor "
        "of the town pay it in the price of bread",
        WEST_EUROPE + ["TUR"], 1200, 1900, 5,
        "Octroi",
        internal=True,
        note="1647 Mazarin takes the proceeds for the treasury, 1798 Paris is allowed to "
             "re-establish its octroi, 1809 the law lays down the basis - and it is abolished in "
             "the course of the 19th century"),

    row("turnpike", "the turnpike",
        "a gate across a road that somebody has been made responsible for",
        "a toll for the road itself",
        "the road was a parish duty and nobody maintained it, so a trust was given the road and "
        "leave to charge: a gate, a keeper, a scale of tolls by the sort of traffic, and a road "
        "that is passable for the first time in living memory",
        BRITISH_ISLES + ["USA"], 1706, 1895, 8,
        "Turnpike trust",
        internal=True,
        note="1621/22 the first bill; the railways killed them and the Local Government Act 1888 "
             "gave the roads back to the counties"),

    row("customs_house", "the customs house",
        "a house at the port or the road, with a scale and a book",
        "duty on the goods, and a declaration",
        "the border is now a thing the state owns and not a thing a lord collects: your goods are "
        "weighed, they are valued, a percentage is taken, and the paper you are given is the "
        "proof you paid it",
        ALL, 1500, None, 6,
        "Custom house; Tariff",
        note="the border belongs to the state now and not to a lord: duty is a percentage of "
             "value, written in a book, and it is paid on goods rather than on blood"),

    row("closed_shore", "a closed shore",
        "one door, and the rest of the coast shut",
        "you may not land at all, save through the one door",
        "the country is closed by edict. A handful of licensed ships come to one port, they trade "
        "through a monopoly of merchants the state has chosen, and everybody else who touches the "
        "shore is a criminal whether he came to trade or to ask for water",
        JAPAN + CHINA + KOREA, 1633, 1853, 7,
        "Sakoku; Canton System",
        sea=True,
        note="the sakoku edicts run 1633 to 1639 and the shore opens after Perry in 1853; the "
             "Canton System runs 1757 to 1842 and forces all Western trade through one door",
        closed=True),

    row("lazaretto", "the lazaretto",
        "a walled place by the water, and forty days in it",
        "you are held, for as long as the plague takes to show",
        "your papers do not matter and your goods are fumigated. You are put in a walled yard by "
        "the harbour with your crew and your cargo and you wait out the forty days, and if "
        "somebody sicken on the eleventh day then the count begins again",
        MEDITERRANEAN, 1377, 1860, 7,
        "Quarantine; Lazaretto",
        sea=True,
        note="first imposed in 1377 in the Republic of Ragusa as a thirty-day trentino; the "
             "forty-day quarantena is where the word comes from. It is a Mediterranean "
             "institution: the lazaretti of Venice, Ragusa, Genoa, Marseille and Malta. A ship "
             "putting in at Liverpool or Hamburg was never held forty days for the plague, so "
             "this row does not reach northern Europe",
        quarantine=True),

    row("zollverein", "no border at all",
        "a customs union: the tolls inside it have been abolished",
        "nothing - and that is the point of it",
        "there is no gate. The states inside the union have given up their tolls against each "
        "other and take duty together at the edge of the whole, and the thing a traveller notices "
        "is the absence of the thing he has spent his life paying",
        GERMAN_STATES, 1834, 1919, 30,
        "Zollverein",
        note="formally started 1 January 1834, foundations from 1818, most of the German states "
             "in by 1866 - the one row in this table whose answer is that you are not stopped"),

    row("passport_control", "passport control",
        "a desk, a photograph, and a stamp",
        "papers: a passport, and often a visa besides",
        "the state now wants to know who you are and not only what you carry. There is a "
        "booklet with your photograph in it, the photograph has been compulsory for years, and "
        "the officer is not interested in your goods until he is satisfied about you",
        ALL, 1914, None, 9,
        "Passport; Travel visa; Border control",
        note="the British Nationality and Status of Aliens Act 1914 defines citizenship and "
             "creates the booklet form; the League of Nations standardises it in 1920 - the First "
             "World War the plan names",
        papers=True),

    row("checkpoint", "the checkpoint",
        "a barrier, a uniform, and a queue",
        "papers, and a search if they choose",
        "a barrier across the road and a man with a weapon beside it: you stop, you show the "
        "booklet, and whether you are waved through depends on a thing decided elsewhere about "
        "the country on the other side",
        ALL, 1945, None, 20,
        "Checkpoint; Border control",
        papers=True),
]

# --------------------------------------------------------------------------- the default
# Not also a row: as a row it matched everywhere and the fallback could never fire - the same
# defect F3 had this step, and the reason it is checked for there.

DEFAULT_CROSSING = {
    "id": "open_ground",
    "name": "open ground",
    "what": "no line, and nobody keeping it",
    "demand": "nothing",
    "line": "there is no border here and no one to ask you for anything. You walk, and the only "
            "thing that stops you is the ground",
    "where": [], "start": None, "end": None, "priority": -1,
    "source": "Freedom of movement",
    "note": "the answer for most of the map in most of history: a frontier needs a state on both "
            "sides of it, and most of the map in most years has not had one",
    "papers": False, "quarantine": False, "closed": False,
    "sea": False, "internal": False,
}
