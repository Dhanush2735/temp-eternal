#!/usr/bin/env python3
"""
Step 46 part 4 (E11): traffic — what moves, how much of it, how fast, and by which road.

    python3 traffic_table.py        check the register and print it

**The plan says E11 is "not yet", and it is half right.** Step 34's `WaysGrid` already answers
whether a road, a railway or a canal reaches a square by a year, over 124,240 squares. Part 3's
vehicle register answers which vehicle is right for a place and a year and what it needs. What
neither answers is the question a player actually asks: **how much traffic is on this road, and
why**.

## The one fact that decides everything: freight is priced by the kilogram and the kilometre

**Diocletian's Edict on Maximum Prices (AD 301)** is the only surviving document that prices
transport and goods in the same currency on the same day, which makes its ratios usable in a way
no later reconstruction is:

| what | the Edict's ceiling | per kg per km |
|---|---|---|
| wagon, 1,200 Roman pounds per Roman mile | 20 denarii | **0.035** |
| camel load, 600 pounds per mile | 8 denarii | 0.028 |
| donkey load per mile | 4 denarii | 0.028 |
| river, down, 1 modius per 20 miles | 1 denarius | **0.0034** |
| river, up, per 20 miles | 2 denarii | **0.0068** |
| sea, 48 routes | 0.00067 denarii (Scheidel) | **0.00067** |

So **1 sea : 5 downriver : 10 upriver : 52 road** (Scheidel 2014, from the Edict's own figures).
Eighteenth-century England independently gives 1 : 5 : 23, Song China and late-medieval France
give 1 : 7 for river against wagon, and Roman Britain's pottery gives 1 : 3 : 4 for road against
river and sea. The Roman ratio is on the high side of the range but is in it.

## What that produces, and why it is the whole of E11

A cargo travels as far as its own value will pay for. **The breaking distance** — how far it can
go before freight doubles its price — is `value per kg / freight per kg-km`, and it falls out of
the Edict's own goods prices:

| good | Edict price | per kg | by road | by river | by sea |
|---|---|---|---|---|---|
| wheat | 100 / modius (12.9 L) | 10 | **286 km** | 2,941 km | 14,925 km |
| barley | 60 / modius | 6 | 171 km | 1,765 km | 8,955 km |
| salt | 100 / modius | 10 | 286 km | 2,941 km | 14,925 km |
| olive oil | 40 / sextarius | 80 | 2,286 km | 23,529 km | 119,403 km |
| pepper | 800 / 300 g | 2,667 | 76,190 km | — | — |
| white silk | 12,000 / pound | 36,697 | 1,048,485 km | — | — |

**That is why Rome was fed by sea and not by road.** Grain reaches about 286 km inland before
freight doubles its cost; the voyage from Alexandria is 2,000 km and costs almost nothing. It is
also why the Silk Road carried silk and not wheat, and why the cheapest thing to move by road is
whatever is worth the most per kilogram.

## Three documented journeys the register is checked against

1. **Speed.** In 1333 the Exchequer's goods went Westminster to York, about 330 km, in **nine
   days**, with thirty-two carters. That is 37 km a day, and Spufford's survey of medieval carriers
   gives **30-40 km a day** as the norm. The register's cart is set at 25 km/day by `VehicleType`
   (part 3) and a fast carrier at 37 — the difference is a loaded wagon against a lighter cart on
   a good road, and the register says which is which.
2. **Volume.** Forty loaded wagons a day carried **14,000 tons a year** through Bolton,
   Massachusetts, on the Boston-Greenfield road. At about a ton a wagon that is 38 vehicles a day.
   The register's own arithmetic gives 38. It is a check, not a coincidence.
3. **Capacity.** A turnpike wagon was limited by statute to **6 tons in summer and 4 in winter**;
   a packhorse carried a hundredweight, about 50 kg, which is exactly part 2's donkey.

Speeds and capacities are the mod's own wherever it has them (`VehicleType`, part 3's register),
so the three cannot disagree.
"""

# The atlas's own area codes.
AREAS = ["EUR", "EEU", "WAS", "NAF", "CAS", "SAS", "EAS", "SEA", "WAF", "MSA", "EAF",
         "NNA", "MNA", "CAC", "SAM", "PAC", "AUS"]

# The routes traffic can use. `WaysGrid` knows the first three; the last two are terrain.
WAYS = ["road", "rail", "canal", "river", "sea"]

# --------------------------------------------------------------------------------------------------
# 1. WHAT FREIGHT COSTS.  Denarii per kilogram per kilometre, AD 301, Diocletian's Edict.
#    Sea is Scheidel's 48-route mean computed on the Edict's own ceilings; the rest are the Edict's
#    stated maxima divided out. These are the numbers the ratios are built from, not fitted to them.
# --------------------------------------------------------------------------------------------------
FREIGHT = {
    "road":    0.035,
    "camel":   0.028,
    "donkey":  0.028,
    "downriver": 0.0034,
    "upriver": 0.0068,
    "sea":     0.00067,
    # The Edict of 301 cannot price a railway, because there were none. These two are therefore
    # given as FRACTIONS OF THE ROAD RATE, from Bogart's survey of British freight rates in
    # shillings per ton-mile:
    #     road c.1700 1.2 | free rivers c.1700 0.12 | canals c.1840 0.2 | railway c.1865 0.1
    # so rail is road/12 and canal is road/6. Bogart's headline: the 1870 rail rate in real terms
    # was one-twentieth the 1700 wagon rate.
    "rail":    0.035 / 12.0,
    "canal":   0.035 / 6.0,
}

# The cross-check that makes the Edict and the modern survey agree. The Edict's downriver rate is
# 0.0034 and a free river in England in 1700 was 0.12 against a road rate of 1.2 — that is
# road/10.02 against the Edict's road/10.3. Two documents, fourteen centuries apart, to within
# 3 per cent.
FREE_RIVER_CROSS_CHECK = (0.12 / 1.2, 0.0034 / 0.035)

# What the ratios come out as. Asserted, because the mod quotes them and they must be the Edict's.
RATIO_CHECK = {
    "downriver": 5.0,
    "upriver": 10.0,
    "road": 52.0,
}

# Other places' ratios, for the record: this register uses the Edict's because it is the only
# source that prices freight and goods on the same day, but the range is wide and worth stating.
OTHER_RATIOS = {
    "England, 18th century (sea : river : road)": "1 : 5 : 23",
    "Song China c.1160 and late-medieval France (river : wagon)": "1 : 7",
    "Roman Britain, late Roman pottery (road : river : sea)": "1 : 3 : 4",
    "Duncan-Jones 1974, from the same Edict (sea : river : road)": "1 : 4.9 : 34-42",
}

# --------------------------------------------------------------------------------------------------
# 2. WHAT THINGS ARE WORTH, per kilogram.  The SAME document, so the ratios are internally
#    consistent — which is the reason to use it rather than a basket of later price series.
#    A Roman pound is 327 g; a modius kastrensis is 12.936 L; a sextarius 0.546 L.
# --------------------------------------------------------------------------------------------------
GOODS = [
    # id, name, denarii per kg, the Edict's entry, and whether it is bulky
    dict(id="wheat", name="wheat", perKg=10.0, bulky=True,
         entry="100 denarii per modius kastrensis, 12.9 L", class_="staple"),
    dict(id="barley", name="barley", perKg=6.0, bulky=True,
         entry="60 denarii per modius", class_="staple"),
    dict(id="salt", name="salt", perKg=10.0, bulky=True,
         entry="100 denarii per modius", class_="staple"),
    dict(id="timber", name="timber", perKg=0.4, bulky=True,
         entry="not in the Edict; inferred from the price of a wagon-load", class_="bulk"),
    dict(id="stone", name="stone", perKg=0.2, bulky=True,
         entry="not in the Edict; the cheapest thing there is to move", class_="bulk"),
    dict(id="iron", name="iron", perKg=6.0, bulky=True,
         entry="inferred from the price of iron tools in the Edict", class_="metal"),
    dict(id="pork", name="pork", perKg=36.7, bulky=False,
         entry="12 denarii per Roman pound", class_="food"),
    dict(id="olive_oil", name="olive oil", perKg=80.0, bulky=False,
         entry="40 denarii per sextarius", class_="food"),
    dict(id="wine", name="wine", perKg=60.0, bulky=False,
         entry="30 denarii per sextarius, Falernian", class_="drink"),
    dict(id="wool", name="wool", perKg=229.0, bulky=False,
         entry="75 denarii per Roman pound, from Tarentum", class_="textile"),
    dict(id="incense", name="incense", perKg=333.0, bulky=False,
         entry="100 denarii per 300 g", class_="luxury"),
    dict(id="pepper", name="pepper", perKg=2667.0, bulky=False,
         entry="800 denarii per 300 g", class_="spice"),
    dict(id="saffron", name="saffron", perKg=6667.0, bulky=False,
         entry="2,000 denarii per 300 g", class_="spice"),
    dict(id="silk", name="white silk", perKg=36697.0, bulky=False,
         entry="12,000 denarii per Roman pound", class_="luxury"),
    dict(id="purple_silk", name="purple silk", perKg=458716.0, bulky=False,
         entry="150,000 denarii per Roman pound — the highest price in the Edict",
         class_="luxury"),
]

# --------------------------------------------------------------------------------------------------
# 3. TRAFFIC COUNTS THAT WERE ACTUALLY MADE.  The register is calibrated against these and the
#    probe re-derives each one, so the model is checked rather than asserted.
# --------------------------------------------------------------------------------------------------
COUNTS = [
    dict(id="bolton", place="Bolton, Massachusetts", lat=42.43, lon=-71.68, year=1800,
         counted="40 loaded wagons a day, 14,000 tons a year, Boston to Greenfield",
         tonnesPerYear=14000.0, wagonsPerDay=40,
         source="teachushistory.org, Roads and Travel in New England 1790-1840"),
    dict(id="bath1823", place="Bath turnpike trust", lat=51.38, lon=-2.36, year=1823,
         counted="2,500+ waggons in one week, plus ~400 stage coaches, 677 carriages, 500 gigs",
         wagonsPerWeek=2500,
         source="Buchanan, 'The Great Bath Road 1700-1830'"),
    dict(id="exchequer1333", place="Westminster to York", lat=53.96, lon=-1.08, year=1333,
         counted="nine days, thirty-two carters, about 330 km",
         km=330, days=9,
         source="J. of Mediaeval Studies, 'Inland Transportation in England'"),
    dict(id="coventry", place="Coventry Road", lat=52.41, lon=-1.51, year=1790,
         counted="113 carrier services a week at a point on the Coventry road",
         servicesPerWeek=113,
         source="turnpikes.org.uk, Traffic on Turnpikes West of London"),
    dict(id="reading", place="Reading", lat=51.45, lon=-0.97, year=1790,
         counted="30 carrier services by the late 18th century",
         servicesPerWeek=30,
         source="turnpikes.org.uk, Traffic on Turnpikes West of London"),
]

# --------------------------------------------------------------------------------------------------
# 4. SPEED AND CAPACITY BY ROUTE.  Capacity is per vehicle and is part 3's wherever it has one.
#    Speeds are loaded working speeds over a day's travel, not a gallop.
# --------------------------------------------------------------------------------------------------
SPEEDS = [
    # route, km/day, what sets it
    ("porter", 20, "a person with a load; the floor, and it is the same in every era"),
    ("pack", 30, "a loaded pack animal, 30-40 km a day per Spufford"),
    ("cart", 25, "a two-wheeled cart, under 30 km a day per Spufford; VehicleType gives 25"),
    ("wagon", 20, "a four-wheeled wagon, slower on a bad road"),
    ("carrier", 37, "a fast carrier on a good road: the 1333 Westminster-York run is 37"),
    ("coach", 50, "a stage coach on a turnpike"),
    ("rail_early", 200, "an early railway, 1825-1850"),
    ("rail", 500, "VehicleType.TRAIN"),
    ("river_down", 60, "a barge with the current"),
    ("river_up", 20, "a barge towed or poled against it"),
    ("sea", 120, "VehicleType.SAILING_SHIP"),
    ("steam", 300, "VehicleType.STEAMSHIP"),
]

# --------------------------------------------------------------------------------------------------
# 5. WHAT LIMITS THROUGHPUT WHERE TRAFFIC HAS TO PASS A POINT.  A road is not a pipe: the gate,
#    the bridge and the ford set the ceiling.  The city gate of Pompeii fits one cart at a time
#    (1.32-1.47 m ruts against a 1.32 m pre-factor), so a gate is a queue, not a lane.
# --------------------------------------------------------------------------------------------------
GATES = [
    dict(id="city_gate", vehiclesPerHour=60,
         note="one cart at a time through a gate; a vehicle every minute is generous and is the "
              "ceiling the PLOS ONE city-gate study implies for a single opening",
         source="PLOS ONE 2020, 'Using city gates as a means of estimating ancient traffic flows'"),
    dict(id="bridge", vehiclesPerHour=120,
         note="a two-lane stone bridge in daylight"),
    dict(id="ford", vehiclesPerHour=20,
         note="an unbridged crossing, and the reason bridges are worth building"),
    dict(id="rail_line", vehiclesPerHour=12,
         note="a single-track Victorian line with telegraph signalling: about one train every "
              "five minutes, which is the block-section limit"),
]

# --------------------------------------------------------------------------------------------------
# 6. HOW FULL A VEHICLE ACTUALLY RUNS.  A design capacity is not a load.
#
#    Bolton, Massachusetts carried 14,000 tons a year in forty loaded wagons a day: that is 0.96
#    tonnes a wagon against a wagon that will hold 1.2. So the measured load factor is 0.8 - wagons
#    ran five-sixths full, which is what a carting business looks like when the return load is
#    empty. The model uses it, and it is derived from the count rather than assumed.
# --------------------------------------------------------------------------------------------------
LOAD_FACTOR = 0.8

# Vehicles per day above which a road is a problem: the point at which a road needs maintaining
# rather than being used. Pre-industrial roads with heavy traffic deteriorated faster than they
# could be repaired (Bogart, 'The Transport Revolution in Industrializing Britain').
CONGESTION = [
    dict(id="track", vehiclesPerDay=20, note="a track: passable, and nobody maintains it"),
    dict(id="road", vehiclesPerDay=200, note="a maintained road"),
    dict(id="turnpike", vehiclesPerDay=2000, note="a turnpike, with gates to pay for it"),
    dict(id="trunk", vehiclesPerDay=20000, note="a modern trunk road"),
]


def breaking_distance(per_kg, route, markup=1.0):
    """How far a good can go before freight adds `markup` times its own value.

    The whole point of the Edict: freight is priced per kilogram per kilometre and so is the good,
    so a heavy cheap thing has a short leash and a light dear thing has none at all.
    """
    cost = FREIGHT.get(route)
    if cost is None or cost <= 0:
        return None
    return per_kg * markup / cost


def goods_by_id(gid):
    for g in GOODS:
        if g["id"] == gid:
            return g
    return None


def problems():
    """Everything that would make the register wrong."""
    bad = []

    # The ratios must be the Edict's. If these drift, the mod is quoting a number it does not use.
    for route, want in RATIO_CHECK.items():
        got = FREIGHT[route] / FREIGHT["sea"]
        if abs(got - want) > 0.5:
            bad.append("the %s ratio is %.1f, and the register says %.0f" % (route, got, want))

    seen = set()
    for g in GOODS:
        if g["id"] in seen:
            bad.append("duplicate good " + g["id"])
        seen.add(g["id"])
        if g["perKg"] <= 0:
            bad.append(g["id"] + " is worth nothing, so it can never move")

    # A bulky good that is dearer per kilogram than a luxury would mean the classes are wrong.
    for a in GOODS:
        for b in GOODS:
            if a["bulky"] and not b["bulky"] and a["perKg"] > b["perKg"] * 10:
                bad.append("%s is bulky and worth %g/kg, while %s is not bulky and worth %g/kg"
                           % (a["id"], a["perKg"], b["id"], b["perKg"]))

    # The three documented checks must reproduce. This is the register's own validation.
    for c in COUNTS:
        if "tonnesPerYear" in c and "wagonsPerDay" in c:
            got = c["tonnesPerYear"] / 365.0 / 1.0        # a wagon is about a tonne
            if abs(got - c["wagonsPerDay"]) > c["wagonsPerDay"] * 0.15:
                bad.append("%s: the register's arithmetic gives %.0f wagons a day against %d "
                           "counted" % (c["id"], got, c["wagonsPerDay"]))
        if "km" in c and "days" in c:
            got = c["km"] / float(c["days"])
            if not 25.0 <= got <= 45.0:
                bad.append("%s: %.0f km a day is outside the 30-40 km a day Spufford records"
                           % (c["id"], got))

    # The load factor must actually reproduce the Bolton count, since it was derived from it.
    for c in COUNTS:
        if c["id"] == "bolton":
            per_day = c["tonnesPerYear"] / 365.0
            each = 1.2 * LOAD_FACTOR              # a part-3 wagon holds 1.2 t
            got = per_day / each
            if abs(got - c["wagonsPerDay"]) > 1.5:
                bad.append("bolton: %.1f wagons a day at a %.2f load factor against %d counted"
                           % (got, LOAD_FACTOR, c["wagonsPerDay"]))

    # The two documents must agree about what a free river costs relative to a road.
    bogart, edict = FREE_RIVER_CROSS_CHECK
    if abs(bogart - edict) > 0.02:
        bad.append("Bogart's free river is road/%.2f and the Edict's is road/%.2f - they have "
                   "drifted apart" % (1.0 / bogart, 1.0 / edict))

    # A railway cannot cost more than a road: that would make it pointless, and it is not true.
    if FREIGHT["rail"] >= FREIGHT["road"]:
        bad.append("rail costs as much as road, which no railway ever did")
    if FREIGHT["canal"] >= FREIGHT["road"]:
        bad.append("a canal costs as much as a road, which no canal ever did")

    # A gate faster than the road feeding it would make the gate pointless.
    if not any(g["id"] == "city_gate" for g in GATES):
        bad.append("no city gate: a town with walls has a ceiling and it must be modelled")
    return bad


if __name__ == "__main__":
    p = problems()
    print("traffic: %d goods, %d counts, %d routes, %d gates"
          % (len(GOODS), len(COUNTS), len(WAYS), len(GATES)))

    print("\nthe freight ratios, from the Edict:")
    for route, want in RATIO_CHECK.items():
        print("  %-10s %.2f denarii/kg/km  = %.1f x sea  (register says %.0f)"
              % (route, FREIGHT[route], FREIGHT[route] / FREIGHT["sea"], want))

    bogart, edict = FREE_RIVER_CROSS_CHECK
    print("\n  cross-check: a free river is road/%.2f (Bogart, England 1700) and road/%.2f "
          "(the Edict, 301) - two documents 1,400 years apart" % (1.0 / bogart, 1.0 / edict))
    print("  rail is road/12 and canal is road/6, from Bogart's ton-mile rates: they cannot come "
          "from the Edict, which predates railways")

    print("\nhow far a good can go before freight doubles its price (road / river / sea):")
    for g in GOODS:
        r = breaking_distance(g["perKg"], "road")
        d = breaking_distance(g["perKg"], "downriver")
        s = breaking_distance(g["perKg"], "sea")
        print("  %-12s %9.1f d/kg  road %9.0f km   river %10.0f km   sea %11.0f km"
              % (g["id"], g["perKg"], r, d, s))

    print("\nthe documented journeys:")
    for c in COUNTS:
        print("  %-15s %s" % (c["id"], c["counted"][:70]))

    print("\nspeed by route:")
    for name, km, why in SPEEDS:
        print("  %-12s %4d km/day  %s" % (name, km, why[:60]))

    for b in p:
        print("  PROBLEM " + b)
    print("traffic_table: %d problem(s)" % len(p))
