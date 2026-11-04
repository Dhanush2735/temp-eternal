#!/usr/bin/env python3
"""
Step 47 part 5 (B6 and E18): **crops and animals as items, as they spread.**

    python3 spread_table.py           check and print the register
    python3 build_spread.py           pack it (see that script)

The plan's line for B6 is *"crops by era (no maize, potatoes or chillies in India before the
1500s)"*, and for E18 *"animals and crops as items, as they spread"*.

**Neither of those needs new dates.** Step 44's products atlas already carries 539 products with a
year for each of the 17 areas, and it already knows the Columbian exchange: `maize` reaches Europe
in 1520 and Mesoamerica in 7000 BC, `chillies` reach Goa in 1540 and Mesoamerica in 6000 BC. What
the atlas does **not** have is the other half of a spread, which is *where the thing came from*. A
year on its own cannot say whether a potato in Bengal in 1700 is a crop that arrived or a crop that
was always there.

So this register is a **join**, and it is the third time in this step that the data existed and the
join did not:

  * the **products atlas** (`economy/products_world.json`) says *when* a thing is made in an area.
  * step 44's **crop origins** register (Khoury et al. 2016, 150 crops against 23 regions of
    diversity) says *where its wild relatives and oldest varieties are*. It has no dates at all,
    which is Khoury's own point: 69% of what the world eats is foreign to where it is eaten.

Put the two together and a spread becomes measurable: the year a thing left home is the earliest
year it is made **outside** its origin areas, and the lag is the difference. That number is the
whole of what E18 is asking for, and nobody has to write a date by hand to get it.

## The limit this register has to declare

The atlas has **133 hand-written rows and 406 derived ones**, and a derived row takes its dates
from its parent. For `flour` that is exactly right: flour cannot precede wheat. For `sorghum` it is
wrong, because sorghum's parent is `millet` and millet's home in this atlas is East Asia, so a
derived sorghum "originates" in China. The same fault puts `groundnut` (a South American crop) in
West Asia, inherited from `oilseeds`.

So **this register only claims an origin for the 133 hand-written rows**, and every derived row it
carries says `inherited` and names its parent. A derived row is still useful for *when it is
available* (which is what a game needs) and is not used for *where it came from* (which is what a
claim needs).
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
ATLAS = os.path.join(ROOT, "eternal", "src", "main", "resources", "data",
                     "eternalengine", "eternal", "economy", "products_world.json")

AREAS = ["NNA", "MNA", "CAC", "SAM", "EUR", "EEU", "WAS", "NAF", "WAF", "MSA", "EAF", "CAS",
         "SAS", "EAS", "SEA", "AUS", "PAC"]

NEW_WORLD = ["NNA", "MNA", "CAC", "SAM"]
OLD_WORLD = ["EUR", "EEU", "WAS", "NAF", "WAF", "MSA", "EAF", "CAS", "SAS", "EAS", "SEA"]

# ---------------------------------------------------------------------------------------------
# What this register carries. A crop or an animal has to be worth naming by hand, which means
# either the plan names it or its spread is a fact of world history.
#
# `home` is what the atlas SHOULD say the origin is, written down independently of the atlas so
# that the check can fail. It comes from the origin register and from the standard account.
# `derived` rows have no `home`: their origin is their parent's and is not a claim.
# `poly` marks a row that is more than one species domesticated independently in more than one
# hemisphere. Cotton is four species, two Old World and two American; "pulses" is every legume
# domesticated anywhere; "wool" is sheep and alpaca. Those rows legitimately have years on both
# sides of 1492 and the exchange check must not fire on them, so they declare it and the check
# demands the declaration.
ROWS = [
    # ---- THE AMERICAN CROPS: the Columbian exchange, measured --------------------------------
    dict(id="maize", kind="crop", home=["CAC"], note=(
        "**The exchange's biggest single item and the one that changed most diets.** It is in "
        "Mesoamerica by 7000 BC, in the American south-west by 2000 BC and the east by AD 1000, "
        "and in the Old World only after 1492. It reached Europe in 1520 and West Africa within a "
        "generation, where it out-yielded every local grain and fed the slave trade's cargo.")),
    dict(id="potato", kind="crop", home=["SAM"], note=(
        "**The Andes, and the crop that let Europe's population grow.** In Europe from about 1570 "
        "and in India from about 1615, and the potato's arrival is why the north European "
        "population doubled in a century and why Ireland's failure of it killed a million.")),
    dict(id="chillies", kind="crop", home=["CAC", "SAM"], note=(
        "**The plan's own example, and it passes.** Goa by 1540, and within fifty years the chilli "
        "had displaced long pepper in Indian cooking: a New World fruit that made South Asian food "
        "what the world now calls South Asian food, in less than one lifetime.")),
    dict(id="cassava", kind="crop", home=["SAM"], note=(
        "**The crop that made the tropical world survivable.** It is a South American tuber, it "
        "grows where wheat will not, and it is in West Africa by 1600 and in India by 1850: the "
        "slowest of the American crops to arrive, because it had to be processed before it could "
        "be eaten.")),
    dict(id="tobacco", kind="crop", home=["SAM"], note=(
        "**The first global commodity and the fastest spread of any plant in history.** In Europe by "
        "1560, in India by 1605 at Akbar's court, and in China within sixty years of Columbus. "
        "Nothing else in this register moves with that speed, and the reason is that it is a "
        "pleasure and not a food: it does not have to out-yield anything to be adopted.")),
    dict(id="sweet_potato", kind="derived_crop", parent="root_crops", home=None, derived=True,
         note=(
        "**The one American crop that crossed the Pacific on its own.** It is in Polynesia "
        "centuries before Columbus, carried by Polynesian voyagers to and from South America, and "
        "it is the strongest evidence that the Pacific was crossed before Europe crossed the "
        "Atlantic.")),
    dict(id="tomatoes", kind="derived_crop", parent="roots", home=None, derived=True, note=(
        "**A fruit the Columbian exchange had to argue about.** The tomato is Andean and was "
        "domesticated in Mexico; Italy calls it a food only in the 1690s, and the sauce that "
        "defines Italian cooking is a nineteenth-century thing.")),
    dict(id="chocolate", kind="derived_crop", parent="cocoa", home=None, derived=True, note=(
        "**A drink before it was a bar.** Mesoamerican by 1500 BC, in Europe by 1590, and the solid "
        "bar is 1847: the technology that makes a bar is a nineteenth-century one, and this row is "
        "a reminder that a crop's date and a food's date are different dates.")),
    dict(id="vanilla", kind="derived_crop", parent="spices", home=None, derived=True, note=(
        "**A Mesoamerican orchid that needs a bee that lives only there.** The Mexican vanilla bee "
        "is the only pollinator, which is why vanilla was a Mexican monopoly until 1841, when a "
        "twelve-year-old enslaved boy on Réunion worked out how to hand-pollinate it.")),
    # ---- THE OLD WORLD CROPS THAT CROSSED THE OTHER WAY --------------------------------------
    dict(id="wheat", kind="crop", home=["WAS"], note=(
        "**The Fertile Crescent, and the name in the atlas is 'wheat and barley'**: step 44 folded "
        "barley into it rather than invent a second 17-area map, which is why there is no barley "
        "product to look for. Wheat reaches the Americas with the Spanish after 1492 and Australia "
        "with the First Fleet.")),
    dict(id="rice", kind="crop", home=["EAS"], note=(
        "**The Yangtze, and a crop that crossed the ocean twice.** It is in West Africa before "
        "Europe arrives there, in South Asia from the Indus, and in the Americas with the "
        "sixteenth-century Spanish and the seventeenth-century slave trade, since the rice the "
        "Carolina planters grew is a West African rice.")),
    dict(id="millet", kind="crop", home=["EAS"], note=(
        "**Two different crops with one English name.** Foxtail millet is Chinese and pearl millet "
        "is Sahelian, and this row is the Chinese one (it is the parent of sorghum and buckwheat "
        "here). The African millets are the reason the Sahel was farmed at all.")),
    dict(id="pulses", kind="crop", home=["WAS"], poly=True, note=(
        "**The other half of the founder package**: lentils, peas and chickpeas domesticated "
        "alongside wheat in the same fields. The nitrogen-fixing rotation that keeps a field alive "
        "is as old as farming and is in this atlas as one row.")),
    dict(id="sugarcane", kind="crop", home=["AUS"], note=(
        "**New Guinea, six thousand years before the sugar anyone ate.** It is domesticated in New "
        "Guinea, refined in India (the word sugar is Sanskrit), planted in the Mediterranean by the "
        "Arabs, and turned into a slave economy in the Caribbean after 1492. The area code `AUS` "
        "here covers New Guinea, which is why the home looks odd.")),
    dict(id="cotton", kind="crop", home=["SAS"], poly=True, note=(
        "**Four separate domestications of four different species.** The Old World cotton is "
        "South Asian (Mehrgarh, 5000 BC); the American cottons are a different species "
        "domesticated separately in Peru and Mesoamerica; and China has no cotton until the 1200s, "
        "which is why Chinese clothing is hemp and silk for three thousand years.")),
    dict(id="pepper", kind="crop", home=["SAS"], note=(
        "**The reason Europeans sailed.** Black pepper grows only in south-west India, and the "
        "trade that carried it is why Rome had a spice market, why Venice was rich, and why "
        "Vasco da Gama went to Calicut. It is in this register because the chilli replaced it, and "
        "the two rows together are the whole of the Columbian exchange in one dish.")),
    dict(id="coffee", kind="crop", home=["EAF"], note=(
        "**Ethiopian, and a drink only from the 1400s.** The plant is Ethiopian, the drink is "
        "Yemeni (Sufi night prayer), the coffee house is Ottoman, and the plantation is Dutch "
        "(Java) and then Brazilian. Every step in that list is a different century.")),
    dict(id="tea", kind="crop", home=["EAS"], note=(
        "**Chinese, and a monopoly for a thousand years.** The plant is Chinese; the British "
        "planting of it in Assam in the 1830s is an act of industrial espionage (Robert Fortune "
        "smuggled the plants) and it is why the world's tea is Indian and not Chinese.")),
    # ---- THE ANIMALS ------------------------------------------------------------------------
    dict(id="horses", kind="animal", home=["EEU", "CAS"], note=(
        "**The steppe, and the plan's own example read the other way.** The horse is domesticated "
        "on the Pontic-Caspian steppe and it dies out of the Americas at the end of the "
        "Pleistocene, so a horse in the Americas before 1493 is not an anachronism of dress but "
        "the largest biological fact about the continent. It comes back with the Spanish from "
        "1520.")),
    dict(id="cattle", kind="animal", home=["WAS"], note=(
        "**Two domestications and two humps.** The taurine cattle of the Fertile Crescent and the "
        "zebu of the Indus are separate domestications of separate aurochs populations, and a "
        "South Asian cow is not the same animal as a European one. The Americas have none before "
        "the Spanish, and the Texas longhorn is a Spanish herd gone feral.")),
    dict(id="sheep_goats", kind="animal", home=["WAS"], note=(
        "**The first animals kept for wool and milk rather than meat.** Sheep are domesticated in "
        "the Fertile Crescent about 9000 BC and they are the reason a farmer can wear cloth and "
        "eat grain without hunting; the wool sheep (a mutation, not a separate species) is much "
        "later.")),
    dict(id="llamas", kind="animal", home=["SAM"], note=(
        "**The only large domestic animal of the Americas, and it cannot pull a plough.** A llama "
        "carries about 30 kg and will not be harnessed, which is one honest reason Andean farming "
        "looks nothing like Mesopotamian farming: no wheel, no plough, no milk.")),
    dict(id="camels", kind="animal", home=["CAS"], note=(
        "**Central Asia, and the caravan is a technology.** The dromedary is Arabian and the "
        "Bactrian is Central Asian; the caravan as an institution is what makes the Silk Road "
        "work, and it is dated here by the animal because the atlas has no row for a caravan.")),
    dict(id="elephants", kind="animal", home=["SAS"], note=(
        "**The war elephant, and its range is already in B5.** This row carries the working animal; "
        "the wildlife register carries the wild one. The two disagree on purpose: the Syrian "
        "elephant is extinct by 100 BC while the war elephant keeps being imported.")),
    dict(id="silk", kind="animal", home=["EAS"], note=(
        "**A textile that is an animal product and a state secret.** Silkworms leave China in "
        "hollow walking sticks in 552 under Justinian, and Byzantium, Sicily and later Lucca build "
        "an industry on stolen eggs. The atlas's `brought` map for silk is one of the loneliest "
        "in the file and it is correct.")),
    dict(id="wool", kind="animal", home=["WAS", "SAM"], poly=True, note=(
        "**Two wools, because the Americas have their own.** Sheep's wool from West Asia and "
        "alpaca from the Andes are not the same fibre, are not the same animal, and the second one "
        "is finer. Folding them into one row is a compromise and the note says so.")),
]

# The plan's three examples, as an independent written expectation so that the check can fail.
PLAN_EXAMPLES = [
    ("maize", "SAS", 1500), ("potato", "SAS", 1500), ("chillies", "SAS", 1500),
]

# A crop whose home is in the Americas must not be in the Old World before 1492, and a crop whose
# home is in the Old World must not be in the Americas before 1492. This is the structural check
# that catches a copied date, and it is the same fault step 46 found in reindeer and donkeys.
EXCHANGE_YEAR = 1492


def atlas():
    with open(ATLAS, encoding="utf-8") as f:
        return {p["id"]: p for p in json.load(f)["products"]}


def made(p):
    return {a: y for a, y in p.get("made", {}).items() if y is not None}


def origin_of(p):
    """The area an atlas row's earliest year is in, and whether that year is a hand-written one."""
    m = made(p)
    if not m:
        return [], None
    lo = min(m.values())
    return sorted(a for a, y in m.items() if y == lo), lo


def build():
    A = atlas()
    out = []
    for r in ROWS:
        pid = r["id"]
        if pid not in A:
            continue
        p = A[pid]
        m = made(p)
        if r.get("derived"):
            parent = r.get("parent")
            pg = A.get(parent) if parent else None
            porig, pyear = origin_of(pg) if pg else ([], None)
            origin = {"areas": porig, "year": pyear, "source": "inherited", "parent": parent}
        else:
            areas, year = origin_of(p)
            origin = {"areas": areas, "year": year, "source": "hand",
                      "claimed": r.get("home") or areas}
        # the first year outside the origin areas: the year it left home
        away = {a: y for a, y in m.items() if a not in origin["areas"]}
        first_away = min(away.values()) if away else None
        out.append({
            "id": pid,
            "kind": "crop" if r["kind"].endswith("crop") else r["kind"],
            "name": p.get("name") or pid,
            "item": p.get("item"),
            "mark": "projected" if p.get("projected") else ("estimated" if p.get("estimate")
                                                            else "recorded"),
            "origin": origin,
            "made": m,
            "gone": {a: y for a, y in p.get("gone", {}).items() if y is not None},
            "poly": bool(r.get("poly")),
            "firstAway": first_away,
            "lag": (first_away - origin["year"]) if (first_away is not None
                                                    and origin["year"] is not None) else None,
            "note": r["note"],
        })
    return out


def check(rows):
    bad = []
    A = atlas()
    by = {r["id"]: r for r in rows}
    for r in ROWS:
        if r["id"] not in A:
            bad.append(r["id"] + " is named here and is not in the atlas")

    # 1. THE PLAN'S OWN EXAMPLES.
    for pid, area, until in PLAN_EXAMPLES:
        r = by.get(pid)
        if not r:
            bad.append("the plan names " + pid + " and this register does not carry it")
            continue
        y = r["made"].get(area)
        if y is not None and y < until:
            bad.append("%s is in %s in %d, before %d: the plan's example fails"
                       % (pid, area, y, until))

    # 2. THE COLUMBIAN EXCHANGE, AS A STRUCTURAL RULE AND NOT A LIST OF EXCEPTIONS.
    for r in rows:
        if r["origin"]["source"] != "hand":
            continue
        if r.get("poly"):
            continue            # more than one species; the exchange rule is not a rule here
        home_areas = r["origin"]["areas"]
        american_home = any(a in NEW_WORLD for a in home_areas)
        for area, year in r["made"].items():
            if american_home and area in OLD_WORLD and year < EXCHANGE_YEAR:
                bad.append("%s has an American home and is made in %s in %d"
                           % (r["id"], area, year))
            if not american_home and area in NEW_WORLD and year < EXCHANGE_YEAR:
                bad.append("%s has an Old World home and is made in %s in %d"
                           % (r["id"], area, year))

    # 3. THE ORIGIN HAS TO AGREE WITH THE INDEPENDENTLY WRITTEN HOME.
    for r in ROWS:
        if r.get("derived"):
            continue
        row = by.get(r["id"])
        if not row:
            continue
        want = set(r["home"])
        got = set(row["origin"]["areas"])
        if not want & got:
            bad.append("%s: the atlas puts the origin in %s and the register says %s"
                       % (r["id"], sorted(got), sorted(want)))

    # 3b. A POLY ROW HAS TO BE POLY. The exemption is only for a row that really is made on
    #     both sides of the Atlantic before 1492, and a row using it to dodge a bad date goes red.
    for r in ROWS:
        if not r.get("poly"):
            continue
        row = by.get(r["id"])
        if not row:
            continue
        old_side = [a for a, y in row["made"].items() if a in OLD_WORLD and y < EXCHANGE_YEAR]
        new_side = [a for a, y in row["made"].items() if a in NEW_WORLD and y < EXCHANGE_YEAR]
        if not (old_side and new_side):
            bad.append(r["id"] + " claims to be polyphyletic and is only made on one side of "
                       "the Atlantic before 1492")

    # 4. A DERIVED ROW MUST NOT CLAIM AN ORIGIN.
    for r in ROWS:
        if r.get("derived") and r.get("home"):
            bad.append(r["id"] + " is derived and still declares a home")

    # 5. THE EXCHANGE HAS TO BE VISIBLE AS SPEED. American crops must be in the Old World inside
    #    a century and a half of 1492, or the register is carrying a crop that did not travel.
    lags = []
    for r in rows:
        if r["origin"]["source"] != "hand" or not any(a in NEW_WORLD for a in r["origin"]["areas"]):
            continue
        old = [y for a, y in r["made"].items() if a in OLD_WORLD]
        if old:
            lags.append(min(old) - EXCHANGE_YEAR)
    if len(lags) < 4:
        bad.append("only %d American crops reach the Old World: the exchange is not in the data"
                   % len(lags))
    if lags and max(lags) > 150:
        bad.append("an American crop is %d years late leaving the Americas, which is not an "
                   "exchange" % max(lags))

    # 6. EVERY ROW MUST SAY SOMETHING, AND SAY WHERE IT CAME FROM.
    for r in rows:
        if len(r["note"]) < 60:
            bad.append(r["id"] + " does not say anything useful")
        if not r["made"]:
            bad.append(r["id"] + " is made nowhere, so it is not a spread")
    return bad


def main():
    rows = build()
    bad = check(rows)
    print("spread: %d rows (%d crops, %d animals); %d with a hand-written origin"
          % (len(rows), len([r for r in rows if r["kind"] == "crop"]),
             len([r for r in rows if r["kind"] == "animal"]),
             len([r for r in rows if r["origin"]["source"] == "hand"])))
    print()
    print("  %-13s %-6s %-11s %-7s %-7s %s" % ("row", "origin", "area", "left", "lag", "made in"))
    for r in sorted(rows, key=lambda x: (x["lag"] if x["lag"] is not None else 10 ** 9)):
        o = r["origin"]
        print("  %-13s %-6s %-11s %-7s %-7s %d areas"
              % (r["id"], o["source"], ",".join(o["areas"])[:11],
                 o["year"] if o["year"] is not None else "-",
                 r["lag"] if r["lag"] is not None else "-", len(r["made"])))
    for p in bad:
        print("  PROBLEM " + p)
    print("spread_table: %d problem(s)" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
