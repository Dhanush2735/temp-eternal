#!/usr/bin/env python3
"""Product atlas, part B: the world product list and the "is it here?" years.

Writes eternal/src/main/resources/data/eternalengine/eternal/economy/products_world.json and
worldfill/PRODUCT_ATLAS_TABLE.md (the same years as a table, for checking by eye).

How it works (see PRODUCT_ATLAS_PLAN.md, sections 1-5):
- The world is split into the 17 large areas of the ArchaeoGLOBE survey that the mod already uses for ways of life
  (146 regions in 17 areas): NNA northern North America, MNA middle North America, CAC Central America and the
  Caribbean, SAM South America, EUR Europe, EEU eastern Europe and Russia, WAS western Asia, NAF northern Africa, WAF
  western Africa, MSA middle and southern Africa, EAF eastern Africa, CAS central Asia, SAS southern Asia, EAS eastern
  Asia, SEA south-east Asia, AUS Australia, New Zealand and Melanesia, PAC Micronesia and Polynesia.
- Each product has, per area, the year it is first MADE there (know-how has arrived and nature allows it), the year
  it is first BROUGHT there by trade (when it is not made), and the year it is GONE (replaced by its successor; old
  stock may remain). No year: never.
- "needs" are what the people of a region must do for it to be made there: farm, herd, live in towns, or be
  "settled" (farm, herd or have towns: anything but only hunting and gathering). The game reads that from the
  ways-of-life survey (to 1899); later every place meets every need.
- "inputs" are the journey: every group needs one of its products made or brought in the same place.
- "staple" marks the four needs every place must have: food, cloth, fuel, light.

Years come from the history of each product (Wikipedia articles first, by the user's rule); they are first years in a
whole area, so a big area takes its earliest corner. Rows marked estimate=True are estimates (most are). A product
may be made in one corner of an area and only brought to the rest; the area keeps the earlier year.
"""
import json
import os

AREAS = ["NNA", "MNA", "CAC", "SAM", "EUR", "EEU", "WAS", "NAF", "WAF", "MSA", "EAF", "CAS", "SAS", "EAS", "SEA",
         "AUS", "PAC"]
WORLD = {
    "Northern North America and Greenland": "NNA", "Middle North America": "MNA",
    "Central America and Caribbean": "CAC", "South America": "SAM", "Europe": "EUR", "Eastern Europe": "EEU",
    "Western Asia": "WAS", "Northern Africa": "NAF", "Western Africa": "WAF", "Middle and Southern Africa": "MSA",
    "Eastern Africa": "EAF", "Central Asia": "CAS", "Southern Asia": "SAS", "Eastern Asia": "EAS",
    "Southeastern Asia": "SEA", "Australia, New Zealand, Melanesia": "AUS", "Micronesia and Polynesia": "PAC",
}
AREA_NAMES = {v: k for k, v in WORLD.items()}
GROUPS = {
    "ALL": AREAS,
    "OLD": ["EUR", "EEU", "WAS", "NAF", "CAS", "SAS", "EAS", "SEA"],
    "AFR": ["WAF", "MSA", "EAF"],
    "AMR": ["NNA", "MNA", "CAC", "SAM"],
    "OCE": ["AUS", "PAC"],
}
FAMILIES = ["staple food", "other food and drink", "animals and animal goods", "cloth and clothes", "building",
            "fuel and light", "metals and tools", "weapons and armour", "transport", "writing and knowledge", "money",
            "medicine and care", "luxury, faith and fun", "papers and permits"]
PRODUCTS = []


def expand(d):
    """Group keys first, then single areas (a single area overrides its group)."""
    out = {}
    if not d:
        return out
    for k, v in d.items():
        if k in GROUPS:
            for a in GROUPS[k]:
                out[a] = v
    for k, v in d.items():
        if k not in GROUPS:
            assert k in AREAS, k
            out[k] = v
    return out


# Step 19g: one and many, for the products with an item, as a buyer counts them.
WORDS = {
    "potato": ("potato", "potatoes"), "sugar": ("heap of sugar", "heaps of sugar"),
    "honey": ("bottle of honey", "bottles of honey"), "cacao": ("cacao bean", "cacao beans"), "eggs": ("egg", "eggs"),
    "leather": ("piece of leather", "pieces of leather"), "dyes": ("pot of blue dye", "pots of blue dye"),
    "mud_brick": ("mud brick", "mud bricks"), "fired_brick": ("fired brick", "fired bricks"),
    "glass": ("glass bottle", "glass bottles"), "firelight": ("torch", "torches"), "oil_lamp": ("oil lamp", "oil lamps"),
    "candles": ("candle", "candles"), "kerosene_lamp": ("kerosene lamp", "kerosene lamps"),
    "stone_tools": ("piece of flint", "pieces of flint"), "iron_tools": ("iron axe", "iron axes"),
    "saddle": ("saddle", "saddles"), "palm_leaf": ("palm leaf", "palm leaves"), "paper": ("sheet of paper", "sheets of paper"),
    "ink": ("pot of ink", "pots of ink"), "books": ("book", "books"),
}


def P(pid, name, family, made=None, brought=None, gone=None, staple=None, needs=(), inputs=(), item=None, count=1,
      days=0.0, sellers=("merchant",), estimate=True, note="", short=None, rename=False):
    assert family in FAMILIES, family
    assert pid not in [p["id"] for p in PRODUCTS], pid
    m, b, g = expand(made), expand(brought), expand(gone)
    for a in list(b):
        if a in m and b[a] >= m[a]:
            del b[a]  # made first: brought adds nothing
    p = {"id": pid, "name": name, "family": family, "made": m, "brought": b, "gone": g}
    if staple:
        p["staple"] = staple
    if needs:
        p["needs"] = list(needs)
    if inputs:
        p["inputs"] = [list(x) for x in inputs]
    if item:
        p["item"] = item
        p["count"] = count
        p["days"] = days
        p["sellers"] = list(sellers)
        p["short"] = short or name
        # Step 19g: how a buyer counts it ("1 sheet of paper", "16 sheets of paper").
        assert pid in WORDS, "no words for " + pid
        p["one"], p["many"] = WORDS[pid]
        if rename:
            p["rename"] = True  # the item given is called by this name (a lantern is an oil lamp)
    if estimate:
        p["estimate"] = True
    if note:
        p["note"] = note
    PRODUCTS.append(p)


ANY = -10000  # "always" in the game's span (it starts in 3000 BCE)

# ---------------------------------------------------------------------------------------------- 1. staple food
P("wild_food", "Wild food (hunting, fishing, gathering)", "staple food", made={"ALL": ANY}, staple="food",
  estimate=False)
P("wheat", "Wheat and barley", "staple food", staple="food", needs=["farm"],
  made={"WAS": -9000, "EUR": -6500, "EEU": -5500, "NAF": -5500, "CAS": -5000, "SAS": -7000, "EAS": -2500,
        "EAF": -3000, "CAC": 1520, "SAM": 1540, "MNA": 1600, "NNA": 1800, "MSA": 1700, "AUS": 1790},
  brought={"SEA": 1600, "WAF": 1900, "PAC": 1850}, note="Mehrgarh about 7000 BCE; the Americas only after 1492")
P("rice", "Rice", "staple food", staple="food", needs=["farm"],
  made={"EAS": -7000, "SAS": -5000, "SEA": -3000, "WAF": -1500, "WAS": 500, "NAF": 700, "EAF": 700, "CAS": 800,
        "EUR": 1450, "CAC": 1600, "MNA": 1690, "SAM": 1700, "AUS": 1920},
  brought={"EUR": 1000, "EEU": 1700}, note="African rice in the Niger delta about 1500 BCE")
P("millet", "Millets and sorghum (jowar)", "staple food", staple="food", needs=["farm"],
  made={"EAS": -8000, "WAF": -2500, "EAF": -3000, "NAF": -3000, "SAS": -2500, "EUR": -1500, "EEU": -3000,
        "CAS": -3000, "WAS": -1000, "MSA": 300})
P("maize", "Maize", "staple food", staple="food", needs=["farm"],
  made={"CAC": -7000, "SAM": -3000, "MNA": -1000, "NNA": 1000, "EUR": 1520, "NAF": 1550, "WAF": 1550, "WAS": 1550,
        "EAS": 1550, "SEA": 1550, "MSA": 1600, "EAF": 1600, "SAS": 1600, "EEU": 1700, "CAS": 1700, "AUS": 1800},
  note="the Columbian exchange: the Old World only after 1492")
P("potato", "Potatoes", "staple food", staple="food", needs=["farm"], item="minecraft:potato", count=16, days=0.08, short="Potatoes",
  made={"SAM": -6000, "EUR": 1570, "SAS": 1615, "EAS": 1650, "CAC": 1600, "MNA": 1700, "NNA": 1750, "EEU": 1750,
        "SEA": 1700, "AUS": 1790, "WAS": 1800, "NAF": 1800, "AFR": 1800, "PAC": 1800, "CAS": 1850},
  note="the Andes; Spain about 1570; India with the Portuguese, early 1600s (common much later)")
P("cassava", "Cassava (manioc)", "staple food", staple="food", needs=["farm"],
  made={"SAM": -5000, "CAC": -2000, "WAF": 1600, "MSA": 1600, "EAF": 1750, "SEA": 1800, "SAS": 1850})
P("roots", "Taro, yams and breadfruit", "staple food", staple="food", needs=["farm"],
  made={"AUS": -7000, "SEA": -5000, "WAF": -3000, "MSA": -1000, "PAC": -1000, "EAF": 500, "CAC": 1600},
  note="taro at Kuk in New Guinea about 7000 BCE; the Lapita people in the Pacific")
P("pulses", "Lentils, chickpeas and beans (dal)", "staple food", staple="food", needs=["farm"],
  made={"WAS": -8000, "EUR": -6000, "NAF": -5000, "SAS": -3000, "CAS": -3000, "EEU": -4000, "EAS": -1000,
        "CAC": -5000, "SAM": -6000, "MNA": -1000, "NNA": 1000, "EAF": -1000, "WAF": -1000, "MSA": 500, "SEA": 500})
P("fish", "Fish", "staple food", made={"ALL": ANY}, staple="food", estimate=False)
P("meat", "Meat", "staple food", made={"ALL": ANY}, staple="food", estimate=False)
P("bread", "Bread from bakeries", "staple food", staple="food", needs=["town"], inputs=[["wheat", "millet", "maize"]],
  made={"WAS": -3000, "NAF": -2500, "EUR": -500, "EEU": 900, "CAS": 800, "SAS": 1300, "SEA": 1600, "EAS": 1860,
        "CAC": 1530, "SAM": 1550, "MNA": 1620, "NNA": 1700, "MSA": 1700, "AUS": 1800, "EAF": 1900, "WAF": 1900,
        "PAC": 1900},
  note="villages bake flatbread at home; bakeries are in towns (the good BREAD)")

# ------------------------------------------------------------------------------------- 2. other food and drink
P("sugar", "Crystal sugar", "other food and drink", needs=["farm"], item="minecraft:sugar", count=8, days=0.12, short="Sugar",
  made={"SAS": 350, "WAS": 600, "EAS": 650, "NAF": 700, "SEA": 1100, "EAF": 1000, "CAC": 1520, "SAM": 1540,
        "MNA": 1795, "EUR": 1810, "EEU": 1840, "MSA": 1850, "AUS": 1860, "PAC": 1840},
  brought={"EUR": 1100, "EEU": 1300, "CAS": 900, "WAF": 1500, "MSA": 1700, "NNA": 1700},
  inputs=[["sugarcane"]],
  note="India under the Guptas; a luxury in Europe until the 1700s; beet sugar in Europe from about 1810")
P("sugarcane", "Sugar cane", "other food and drink", needs=["farm"],
  made={"AUS": -6000, "SEA": -3000, "PAC": -1500, "SAS": -1000, "EAS": -500, "WAS": -500,
        "NAF": 700, "EUR": 900, "EAF": 1000, "CAS": 1000, "MNA": 1520, "CAC": 1501, "SAM": 1518,
        "WAF": 1500, "MSA": 1500},
  brought={"EUR": 900, "EEU": 1300, "NNA": 1700, "AUS": 1788},
  note="domesticated in New Guinea; to India and China by 500 BCE; the Arabs carried it round the "
        "Mediterranean; Columbus took it to Hispaniola in 1493")
P("jaggery", "Jaggery (gur)", "other food and drink", needs=["farm"],
  inputs=[["sugarcane"]],
  made={"SAS": -500, "SEA": 500, "EAS": 300, "EAF": 1500})
P("honey", "Honey", "other food and drink", item="minecraft:honey_bottle", count=1, days=0.06, short="Honey",
  made={"ALL": ANY}, estimate=False)
P("salt", "Salt", "other food and drink",
  made={"OLD": -5000, "AFR": -1000, "AMR": -1000, "OCE": 1800}, brought={"WAF": -500, "AUS": 1790})
P("beer", "Beer and grain wine", "other food and drink", needs=["farm"],
  inputs=[["wheat", "millet", "rice", "maize", "cassava"]],
  made={"WAS": -3500, "NAF": -3500, "EUR": -3000, "EEU": -2000, "CAS": -1500, "EAS": -5000, "SAS": -1500,
        "SEA": -500, "WAF": -1000, "EAF": -1000, "MSA": 500, "SAM": -1000, "CAC": -1000, "MNA": 1600, "NNA": 1700,
        "AUS": 1795}, note="Sumer; rice wine in China; sorghum beer in Africa; chicha in the Andes")
P("wine", "Wine", "other food and drink", needs=["farm"],
  made={"WAS": -6000, "EUR": -2000, "NAF": -3000, "CAS": -500, "EAS": 640, "EEU": -500, "CAC": 1530, "SAM": 1550,
        "MNA": 1770, "MSA": 1659, "AUS": 1820},
  brought={"SAS": -300, "EAS": -100, "SEA": 1500, "AFR": 1500, "NNA": 1700})
P("toddy", "Toddy (palm wine)", "other food and drink",
  made={"SAS": -1000, "SEA": -1000, "WAF": -1000, "EAF": -1000, "MSA": -500, "PAC": 0})
P("tea", "Tea", "other food and drink", needs=["farm"],
  made={"EAS": 300, "SAS": 1840, "SEA": 1830, "EAF": 1925, "EEU": 1900, "WAS": 1890, "SAM": 1930},
  brought={"CAS": 900, "WAS": 1600, "EUR": 1610, "EEU": 1640, "NAF": 1700, "MNA": 1700, "NNA": 1700, "CAC": 1700,
           "SAM": 1750, "AUS": 1790, "SAS": 1700, "AFR": 1800, "PAC": 1800, "SEA": 1600},
  note="China; Europe from 1610; Assam from about 1840 (a daily drink in India only in the 1900s); Georgia 1890s")
P("coffee", "Coffee", "other food and drink", needs=["farm"],
  made={"EAF": 1400, "WAS": 1450, "SAS": 1670, "SEA": 1700, "CAC": 1730, "SAM": 1730, "NAF": 1900, "WAF": 1900,
        "MSA": 1900, "PAC": 1820},
  brought={"NAF": 1500, "EUR": 1615, "EEU": 1700, "MNA": 1670, "NNA": 1700, "CAS": 1700, "SAS": 1600, "EAS": 1850,
           "AUS": 1800, "WAF": 1800, "MSA": 1800},
  note="Yemen in the 1400s; Baba Budan's seeds in Mysore about 1670")
P("cacao", "Cacao and chocolate", "other food and drink", needs=["farm"], item="minecraft:cocoa_beans", count=8, days=0.1, short="Cacao beans",
  made={"CAC": -1500, "SAM": -1500, "SEA": 1700, "WAF": 1880, "MSA": 1880},
  brought={"EUR": 1590, "EEU": 1750, "WAS": 1750, "MNA": 1700, "NNA": 1750, "SAS": 1850, "EAS": 1850, "NAF": 1750,
           "AUS": 1850}, note="the Olmec; Spain in the 1590s; Ghana from 1879")
P("chillies", "Chillies", "other food and drink", needs=["farm"],
  made={"CAC": -6000, "SAM": -6000, "MNA": 1600, "EUR": 1530, "SAS": 1540, "SEA": 1540, "EAS": 1600, "WAS": 1550,
        "NAF": 1550, "WAF": 1550, "EAF": 1600, "MSA": 1600, "CAS": 1700, "EEU": 1600, "AUS": 1800},
  note="with the Portuguese to Goa in the 1500s")
P("spices", "Spices (pepper, cinnamon, cloves)", "other food and drink", needs=["farm"],
  made={"SAS": -2000, "SEA": -1000, "EAF": 1800},
  brought={"NAF": -1200, "WAS": -1000, "EUR": -300, "EEU": 900, "EAS": 200, "CAS": 500, "EAF": 100, "WAF": 1500,
           "MSA": 1600, "CAC": 1550, "SAM": 1550, "MNA": 1650, "NNA": 1700, "AUS": 1790, "PAC": 1850},
  note="pepper from Kerala; cloves and nutmeg from the Moluccas (the good SPICES)")
P("dairy", "Milk, butter and ghee", "other food and drink", needs=["herd"],
  inputs=[["cattle", "sheep_goats", "camels", "horses", "llamas"]],
  made={"WAS": -7000, "EUR": -6000, "SAS": -4000, "NAF": -5000, "EAF": -3000, "CAS": -4000, "EEU": -4000,
        "EAS": -1000, "MSA": 500, "WAF": -1000, "CAC": 1530, "SAM": 1540, "MNA": 1620, "NNA": 1700, "AUS": 1790,
        "PAC": 1800, "SEA": 1600})
P("eggs", "Chickens and eggs", "other food and drink", needs=["settled"], item="minecraft:egg", count=16, days=0.05, short="Eggs",
  made={"SEA": -6000, "EAS": -5000, "SAS": -2500, "WAS": -1500, "NAF": -1500, "EUR": -800, "EEU": -500,
        "CAS": -500, "EAF": 500, "WAF": 500, "MSA": 900, "PAC": -1000, "AUS": 1788, "CAC": 1520, "SAM": 1520,
        "MNA": 1600, "NNA": 1700})
P("olive_oil", "Olive oil", "other food and drink", needs=["farm"],
  made={"WAS": -6000, "EUR": -3000, "NAF": -1000, "SAM": 1560, "CAC": 1530, "MNA": 1770, "AUS": 1800},
  brought={"EEU": -500, "CAS": 0, "SAS": 0})
P("cooking_oil", "Sesame, mustard and coconut oil", "other food and drink", needs=["farm"],
  made={"SAS": -2500, "WAS": -2000, "NAF": -1500, "EAS": -500, "SEA": -500, "EAF": 0, "WAF": -500, "CAS": -500,
        "EEU": 1000, "EUR": 1000, "PAC": 0, "AUS": 1800, "AMR": 1600, "MSA": 1000})

# --------------------------------------------------------------------------------- 3. animals and animal goods
P("cattle", "Cattle", "animals and animal goods", needs=["herd"],
  made={"WAS": -8500, "SAS": -6500, "NAF": -6000, "EUR": -6000, "EEU": -5000, "CAS": -4000, "EAS": -3000,
        "SEA": -2000, "EAF": -3000, "WAF": -2000, "MSA": 0, "CAC": 1520, "SAM": 1530, "MNA": 1600, "NNA": 1700,
        "AUS": 1788, "PAC": 1800}, note="zebu in South Asia; the Americas only after 1492")
P("sheep_goats", "Sheep and goats", "animals and animal goods", needs=["herd"],
  made={"WAS": -9000, "SAS": -7000, "NAF": -6000, "EUR": -6000, "EEU": -5000, "CAS": -5000, "EAS": -3000,
        "SEA": -1000, "EAF": -3000, "WAF": -2000, "MSA": 0, "CAC": 1520, "SAM": 1540, "MNA": 1600, "NNA": 1700,
        "AUS": 1788, "PAC": 1800})
P("llamas", "Llamas and alpacas", "animals and animal goods", needs=["herd"], made={"SAM": -4000})
P("horses", "Horses", "animals and animal goods", needs=["herd"],
  made={"EEU": -3500, "CAS": -3500, "WAS": -2000, "EUR": -2000, "NAF": -1600, "SAS": -1500, "EAS": -1200,
        "SEA": -500, "WAF": 1000, "EAF": 1500, "MSA": 1650, "CAC": 1520, "SAM": 1530, "MNA": 1650, "NNA": 1730,
        "AUS": 1788, "PAC": 1820}, note="the steppe; chariots by 1800 BCE; back to the Americas with the Spanish")
P("camels", "Camels", "animals and animal goods", needs=["herd"],
  made={"CAS": -2500, "WAS": -1000, "SAS": -1000, "EAS": -1000, "EAF": -1000, "NAF": 300, "WAF": 500, "AUS": 1840})
P("elephants", "Working elephants", "animals and animal goods", needs=["town"], made={"SAS": -2000, "SEA": -1500})
P("wool", "Wool", "animals and animal goods", needs=["herd"], inputs=[["sheep_goats", "llamas"]],
  made={"WAS": -4000, "EUR": -3000, "EEU": -3000, "CAS": -3000, "SAS": -2000, "NAF": -2000, "EAS": -1000,
        "EAF": -1000, "SAM": -4000, "CAC": 1540, "MNA": 1600, "NNA": 1700, "MSA": 1700, "AUS": 1797, "PAC": 1850},
  note="the good WOOL; alpaca wool in the Andes")
P("hides_furs", "Hides and furs", "animals and animal goods", made={"ALL": ANY}, staple="cloth", estimate=False)
P("leather", "Leather", "animals and animal goods", item="minecraft:leather", count=4, days=0.3, short="Leather",
  inputs=[["cattle", "sheep_goats", "horses", "camels", "llamas", "hides_furs"]],
  made={"OLD": -5000, "AFR": -3000, "AMR": -3000, "AUS": 1800, "PAC": 1850})
P("silk", "Silk", "animals and animal goods", needs=["farm"],
  made={"EAS": -3000, "SAS": 300, "CAS": 440, "WAS": 552, "SEA": 500, "NAF": 900, "EUR": 1100},
  brought={"EUR": -50, "WAS": -100, "NAF": 0, "EEU": 900, "EAF": 500, "WAF": 1300, "AMR": 1600, "AUS": 1800},
  note="China; the Byzantines got silkworms in 552; Sicily and Italy from about 1100 (the good SILK)")
P("pearls", "Pearls", "animals and animal goods",
  made={"WAS": -2000, "SAS": -500, "EAS": 0, "SEA": 0, "PAC": 1800, "CAC": 1520},
  brought={"EUR": -300, "NAF": -500, "EEU": 900, "CAS": 500})
P("ivory", "Ivory", "animals and animal goods", made={"SAS": -2000, "EAF": -2000, "WAF": -1000, "MSA": -1000,
                                                       "SEA": -1000, "NAF": -3000},
  brought={"WAS": -2000, "EUR": -500, "EAS": 0, "EEU": 900})

# ---------------------------------------------------------------------------------------- 4. cloth and clothes
P("cotton", "Cotton (fibre and hand-woven cloth)", "cloth and clothes", staple="cloth", needs=["farm"],
  made={"SAS": -5000, "NAF": -300, "WAS": -700, "CAS": 600, "EAS": 1250, "SEA": 300, "EAF": 1000, "WAF": 900,
        "MSA": 1100, "CAC": -3000, "SAM": -4000, "MNA": 500, "AUS": 1860},
  brought={"EUR": 900, "EEU": 1300, "NNA": 1700, "PAC": 1850},
  note="Mehrgarh; Peru and Mesoamerica on their own; China only from the 1200s; Europe brought it")
P("linen", "Linen", "cloth and clothes", staple="cloth", needs=["farm"],
  made={"WAS": -8000, "NAF": -5000, "EUR": -4000, "EEU": -3000, "SAS": -2000, "CAS": -1000, "EAS": 1000,
        "MNA": 1650, "NNA": 1700, "CAC": 1550, "SAM": 1600, "AUS": 1800})
P("hemp", "Hemp and other bast fibres", "cloth and clothes", needs=["farm"],
  made={"EAS": -4000, "SAS": -1000, "WAS": -1000, "EUR": -500, "EEU": -500, "CAS": -1000, "SEA": 0,
        "MNA": 1650, "SAM": 1550, "CAC": 1550})
P("wool_cloth", "Woollen cloth", "cloth and clothes", staple="cloth", inputs=[["wool"]],
  made={"WAS": -4000, "EUR": -3000, "EEU": -3000, "CAS": -3000, "SAS": -2000, "NAF": -2000, "EAS": -1000,
        "EAF": -1000, "SAM": -4000, "CAC": 1540, "MNA": 1600, "NNA": 1700, "MSA": 1700, "AUS": 1800},
  note="the gongadi blanket is one (part A)")
P("bark_cloth", "Bark cloth (tapa)", "cloth and clothes", staple="cloth",
  made={"SEA": -3000, "PAC": -1000, "MSA": 1000, "EAF": 1000, "CAC": -500, "AUS": -1000, "SAM": 0})
P("dyes", "Indigo and other dyes", "cloth and clothes", needs=["farm"], item="minecraft:blue_dye", count=4, days=0.25, short="Blue dye",
  made={"SAS": -3000, "NAF": -2400, "WAS": -2000, "EUR": -1000, "EEU": -500, "EAS": -1000, "CAS": -500,
        "SEA": 0, "CAC": -500, "SAM": -500, "WAF": 900, "EAF": 1000, "MNA": 1740, "MSA": 1800},
  brought={"NNA": 1700, "AUS": 1800, "PAC": 1850},
  note="indigo from India (Harappa); woad in Europe; cochineal in the Americas")
P("mill_cloth", "Mill cloth", "cloth and clothes", staple="cloth", needs=["town"], inputs=[["cotton", "wool"],
                                                                                          ["machines"]],
  made={"EUR": 1780, "MNA": 1790, "EEU": 1820, "NAF": 1818, "SAS": 1854, "CAC": 1835, "WAS": 1850, "EAS": 1890,
        "SAM": 1850, "AUS": 1870, "MSA": 1920, "SEA": 1920, "EAF": 1930, "WAF": 1950, "CAS": 1930, "NNA": 1860},
  brought={"ALL": 1820}, note="Arkwright's mills in the 1770s; Bombay's first mill in 1854")
P("nylon", "Nylon and other made fibres", "cloth and clothes", needs=["town"], inputs=[["petrol"]],
  made={"MNA": 1939, "EUR": 1940, "EAS": 1950, "EEU": 1950, "SAS": 1962, "SAM": 1960, "CAC": 1960, "AUS": 1955,
        "WAS": 1970, "SEA": 1970, "NAF": 1970},
  brought={"ALL": 1950})

P("plastics", "Plastics (polythene, PVC)", "metals and tools", needs=["town"], inputs=[["petrol"]],
  made={"MNA": 1940, "EUR": 1940, "EEU": 1955, "EAS": 1950, "AUS": 1950, "SAM": 1955, "CAC": 1960, "SAS": 1957,
        "WAS": 1965, "NAF": 1965, "SEA": 1965, "MSA": 1960},
  brought={"ALL": 1950, "SAS": 1950}, note="Bakelite came first (1907), as a rare thing; everyday plastics after 1940")

# ------------------------------------------------------------------------------------------------- 5. building
P("mud_brick", "Mud bricks", "building", item="minecraft:mud_bricks", count=16, days=0.15, short="Mud bricks", needs=["farm"],
  made={"WAS": -8000, "SAS": -7000, "NAF": -5000, "CAS": -4000, "EAS": -3000, "WAF": -1000, "EAF": -2000,
        "CAC": -1500, "SAM": -2500, "MNA": 700, "EUR": -6000, "EEU": -5000, "MSA": 1000, "SEA": 0})
P("fired_brick", "Fired bricks", "building", item="minecraft:brick", count=16, days=0.3, short="Fired bricks", needs=["town"],
  inputs=[["firewood", "charcoal", "coal", "dung_cakes"]],
  made={"WAS": -3500, "SAS": -2600, "EAS": -500, "NAF": -1000, "EUR": -200, "EEU": 1000, "CAS": 300, "SEA": 300,
        "CAC": 600, "SAM": 1550, "MNA": 1620, "NNA": 1700, "AUS": 1800, "EAF": 1300, "MSA": 1700, "WAF": 1900},
  note="the Indus cities; Comalcalco in the Maya lands")
P("stone", "Cut stone", "building", needs=["town"],
  made={"OLD": -3000, "AFR": 1000, "CAC": -1200, "SAM": -1000, "MNA": 900, "NNA": 1700, "AUS": 1800,
        "PAC": 1100}, note="the good STONE")
P("timber", "Timber", "building", made={"ALL": ANY}, estimate=False, note="the good TIMBER")
P("lime_mortar", "Lime mortar and plaster", "building", needs=["town"],
  made={"WAS": -4000, "NAF": -2600, "SAS": -2000, "EUR": -300, "EAS": 0, "EEU": 900, "CAS": 0, "SEA": 500,
        "CAC": -300, "SAM": 1550, "MNA": 1620, "EAF": 1000, "WAF": 1900, "MSA": 1700, "AUS": 1800})
P("roman_concrete", "Roman concrete", "building", needs=["town"],
  made={"EUR": -200, "WAS": -100, "NAF": -50}, gone={"EUR": 500, "WAS": 600, "NAF": 500})
P("cement", "Portland cement", "building", needs=["town"], inputs=[["coal", "charcoal"]],
  made={"EUR": 1824, "EEU": 1856, "MNA": 1871, "EAS": 1880, "AUS": 1880, "SAM": 1890, "CAC": 1900, "NAF": 1900,
        "WAS": 1910, "SAS": 1914, "SEA": 1920, "MSA": 1920, "EAF": 1930, "WAF": 1950, "CAS": 1930, "NNA": 1890},
  brought={"ALL": 1860}, note="England 1824; India from 1914")
P("glass", "Glass", "building", item="minecraft:glass_bottle", count=4, days=0.25, short="Glass bottles", needs=["town"],
  inputs=[["firewood", "charcoal", "coal"]],
  made={"WAS": -2500, "NAF": -1500, "EUR": -100, "EEU": 1000, "SAS": -1000, "EAS": -500, "CAS": 500, "SEA": 0,
        "WAF": 1000, "MNA": 1610, "CAC": 1540, "SAM": 1600, "AUS": 1820, "NNA": 1750},
  brought={"ALL": 1700, "AUS": 1788, "PAC": 1770}, note="Mesopotamian beads; Roman blown glass; glass beads at Ile-Ife")

# -------------------------------------------------------------------------------------------- 6. fuel and light
P("firewood", "Firewood", "fuel and light", made={"ALL": ANY}, staple="fuel", estimate=False)
P("charcoal", "Charcoal", "fuel and light", staple="fuel",
  made={"OLD": -4000, "AFR": -1000, "AMR": -500, "OCE": 1800})
P("dung_cakes", "Dung cakes", "fuel and light", staple="fuel", needs=["herd"], inputs=[["cattle", "camels",
                                                                                         "sheep_goats"]],
  made={"SAS": -3000, "WAS": -3000, "CAS": -3000, "EAF": -1000, "NAF": -3000, "EAS": -1000})
P("firelight", "Firelight and torches", "fuel and light", item="minecraft:torch", count=16, days=0.04, short="Torches",
  made={"ALL": ANY}, staple="light", estimate=False)
P("oil_lamp", "Oil lamps", "fuel and light", item="minecraft:lantern", count=1, days=0.25, staple="light", short="Oil lamp",
  rename=True,
  inputs=[["olive_oil", "cooking_oil", "dairy", "fish"]],
  made={"WAS": -4500, "NAF": -3500, "EUR": -1500, "EEU": -500, "SAS": -2500, "EAS": -1000, "CAS": -1000,
        "SEA": 0, "WAF": 1000, "EAF": 0, "MSA": 1700, "NNA": -2000, "MNA": 1600, "SAM": 1550, "CAC": 1530,
        "AUS": 1800, "PAC": 1850},
  gone={"EUR": 1900, "MNA": 1890, "EEU": 1920, "AUS": 1910},
  note="clay lamps; seal-oil lamps of the Inuit; the diya stays in South Asia")
P("candles", "Candles", "fuel and light", needs=["settled"], item="minecraft:candle", count=4, days=0.1, short="Candles", staple="light",
  inputs=[["cattle", "sheep_goats", "honey"]],
  made={"EUR": -300, "EAS": -200, "WAS": 0, "NAF": 0, "SAS": 200, "EEU": 900, "CAS": 800, "SEA": 1000,
        "AMR": 1600, "AFR": 1700, "AUS": 1800, "PAC": 1850})
P("coal", "Coal", "fuel and light", needs=["settled"], staple="fuel",
  made={"EAS": 1000, "EUR": 1250, "MNA": 1750, "AUS": 1800, "SAS": 1820, "EEU": 1800, "SAM": 1850, "WAS": 1850,
        "SEA": 1850, "MSA": 1860, "NAF": 1900, "CAC": 1900, "EAF": 1950, "NNA": 1720, "CAS": 1900},
  brought={"ALL": 1860, "CAC": 1835, "NAF": 1850}, note="China in the Song; England from the 1200s, common in the 1700s (the good COAL)")
P("kerosene", "Kerosene", "fuel and light", needs=["town"], staple="fuel",
  made={"EUR": 1854, "MNA": 1859, "EEU": 1873, "SEA": 1890, "WAS": 1913, "SAM": 1920, "CAC": 1910, "NNA": 1870},
  brought={"ALL": 1875, "SAS": 1870, "AUS": 1870},
  note="Poland 1853 and Pennsylvania 1859; India bought most of it from abroad")
P("kerosene_lamp", "Kerosene lamps", "fuel and light", item="minecraft:lantern", count=1, days=0.3, staple="light",
  short="Kerosene lamp", rename=True,
  inputs=[["kerosene"]],
  made={"EUR": 1855, "MNA": 1860, "EEU": 1875, "SAS": 1880, "EAS": 1880, "WAS": 1880, "NAF": 1880, "SAM": 1880,
        "CAC": 1880, "AUS": 1870, "SEA": 1890, "NNA": 1870, "CAS": 1890},
  brought={"ALL": 1880}, gone={"EUR": 1950, "MNA": 1940, "AUS": 1950, "NNA": 1950})
P("gas_light", "Gas light", "fuel and light", staple="light", needs=["town"], inputs=[["coal"]],
  made={"EUR": 1812, "MNA": 1816, "EEU": 1840, "AUS": 1841, "SAS": 1860, "EAS": 1865, "SAM": 1850, "CAC": 1850,
        "WAS": 1860, "NAF": 1860, "NNA": 1840, "MSA": 1870, "SEA": 1870},
  gone={"EUR": 1950, "MNA": 1940, "EEU": 1950, "AUS": 1950, "NNA": 1950})
P("electricity", "Electric light", "fuel and light", staple="light", needs=["town"],
  made={"EUR": 1882, "MNA": 1882, "EAS": 1885, "SAM": 1885, "MSA": 1882, "AUS": 1888, "EEU": 1890, "CAC": 1890,
        "NAF": 1895, "SEA": 1895, "SAS": 1900, "WAS": 1900, "PAC": 1900, "NNA": 1900, "EAF": 1910, "WAF": 1920,
        "CAS": 1920}, note="London and New York 1882; Kimberley 1882; Calcutta 1899")
P("petrol", "Petrol and diesel", "fuel and light", made={"MNA": 1890, "EEU": 1900, "EUR": 1886, "WAS": 1915,
                                                        "SEA": 1900, "SAM": 1920, "CAC": 1910, "NNA": 1920},
  brought={"ALL": 1910, "NNA": 1900}, note="benzine for the first cars; India bought it from abroad")

# ---------------------------------------------------------------------------------------- 7. metals and tools
P("stone_tools", "Stone tools", "metals and tools", item="minecraft:flint", count=8, days=0.02, short="Flint for tools",
  made={"ALL": ANY},
  gone={"WAS": -1000, "EUR": -800, "SAS": -800, "NAF": -800, "EAS": -500, "CAS": -500, "EEU": -500, "SEA": 500,
        "WAF": 0, "EAF": 500, "MSA": 800, "CAC": 1600, "SAM": 1600, "MNA": 1700, "NNA": 1850, "AUS": 1850,
        "PAC": 1850}, note="gone where metal tools took over")
P("copper", "Copper", "metals and tools", needs=["settled"],
  made={"WAS": -5000, "EUR": -4500, "SAS": -4000, "NAF": -4000, "EAS": -2500, "CAS": -3000, "EEU": -4000,
        "SEA": -1500, "WAF": -1000, "MSA": 400, "EAF": 500, "MNA": -4000, "SAM": -1500, "CAC": 650, "NNA": 1700,
        "AUS": 1844, "PAC": 1850}, note="the good COPPER_INGOT; the Old Copper culture by the Great Lakes")
P("tin", "Tin", "metals and tools", needs=["settled"],
  made={"EUR": -2500, "CAS": -2000, "EAS": -2000, "SEA": -1500, "SAM": 500, "WAF": 0, "CAC": 1200, "WAS": -3300,
        "AUS": 1872}, brought={"SAS": -2600, "NAF": -2000, "EEU": -2000, "MSA": 1700, "EAF": 1000, "MNA": 1700})
P("bronze", "Bronze", "metals and tools", needs=["settled"], inputs=[["copper"], ["tin"]],
  made={"WAS": -3300, "EUR": -2500, "SAS": -2600, "NAF": -2000, "EAS": -2000, "CAS": -2000, "EEU": -2000,
        "SEA": -1000, "SAM": 600, "CAC": 1200, "WAF": 900, "MNA": 1700},
  note="the Igbo-Ukwu bronzes of the 900s; Andean bronze")
P("iron", "Iron", "metals and tools", needs=["settled"], inputs=[["charcoal", "coal"]],
  made={"WAS": -1200, "NAF": -700, "EUR": -900, "SAS": -1200, "EAS": -700, "CAS": -1000, "EEU": -800,
        "SEA": -500, "WAF": -600, "EAF": -500, "MSA": 300, "CAC": 1530, "SAM": 1540, "MNA": 1620, "AUS": 1848},
  brought={"NNA": 1700, "AUS": 1788, "PAC": 1800}, note="the good IRON_INGOT (same years as the goods table)")
P("steel", "Steel (wootz and after)", "metals and tools", needs=["settled"], inputs=[["iron"], ["charcoal", "coal"]],
  made={"SAS": -300, "EAS": -200, "EAF": 0, "CAS": 700, "WAS": 900, "EUR": 1100, "EEU": 1500, "MNA": 1720,
        "SAM": 1900, "AUS": 1915}, brought={"ALL": 1870}, note="wootz from South India")
P("gold", "Gold", "metals and tools", needs=["settled"],
  made={"WAS": -4000, "EEU": -4500, "NAF": -3000, "EUR": -3000, "SAS": -2000, "CAS": -2000, "EAS": -1500,
        "SEA": -500, "WAF": 400, "MSA": 1100, "EAF": 1000, "SAM": -1500, "CAC": 500, "MNA": 1799, "NNA": 1896,
        "AUS": 1851}, note="the good GOLD_INGOT")
P("gems", "Gems (diamonds, emeralds, rubies)", "luxury, faith and fun", needs=["settled"],
  made={"SAS": -300, "NAF": -1500, "SAM": 500, "SEA": 600, "WAS": -3000, "MSA": 1870, "EAS": -500},
  brought={"EUR": -300, "EEU": 900, "CAS": 0, "EAF": 500, "WAF": 1000, "MNA": 1700, "CAC": 1550, "AUS": 1850},
  note="India was the only source of diamonds until 1725 (Golconda); the good EMERALD")
P("plough", "Ploughs", "metals and tools", needs=["farm"],
  made={"WAS": -4000, "NAF": -3000, "SAS": -2500, "EUR": -3000, "EEU": -3000, "EAS": -500, "CAS": -2000,
        "SEA": -500, "EAF": -500, "MSA": 1700, "WAF": 1900, "CAC": 1530, "SAM": 1540, "MNA": 1620, "NNA": 1750,
        "AUS": 1790, "PAC": 1850})
P("iron_tools", "Iron tools (axes, sickles, hoes)", "metals and tools", needs=["settled"], item="minecraft:iron_axe", count=1,
  days=0.8, short="Iron axe", inputs=[["iron"], ["charcoal", "coal"]],
  made={"WAS": -1100, "NAF": -650, "EUR": -850, "SAS": -1100, "EAS": -650, "CAS": -950, "EEU": -750, "SEA": -450,
        "WAF": -550, "EAF": -450, "MSA": 350, "CAC": 1530, "SAM": 1540, "MNA": 1620, "AUS": 1850},
  brought={"NNA": 1700, "AUS": 1788, "PAC": 1800})
P("machines", "Machines and steam engines", "metals and tools", needs=["town"], inputs=[["iron"], ["coal", "charcoal"]],
  made={"EUR": 1712, "MNA": 1790, "EEU": 1800, "SAS": 1850, "EAS": 1860, "AUS": 1860, "SAM": 1880, "CAC": 1880,
        "WAS": 1880, "NAF": 1880, "NNA": 1860},
  brought={"ALL": 1860, "NAF": 1815, "SAS": 1830, "CAC": 1835, "WAS": 1840, "SAM": 1840},
  note="Newcomen's engine 1712; common from the 1780s; Muhammad Ali's mills in Egypt from 1818")

# ------------------------------------------------------------------------------------- 8. weapons and armour
P("bows", "Bows and arrows", "weapons and armour",
  made={"OLD": ANY, "AFR": ANY, "AMR": ANY, "PAC": 1800, "AUS": 1800},
  note="Australia had no bows; the weapons step decides who may have them")
P("bronze_weapons", "Bronze weapons", "weapons and armour", needs=["settled"], inputs=[["bronze"]],
  made={"WAS": -3000, "EUR": -2300, "SAS": -2500, "NAF": -1900, "EAS": -1900, "CAS": -1900, "EEU": -1900,
        "SEA": -900}, gone={"WAS": -800, "EUR": -600, "SAS": -600, "NAF": -500, "EAS": -200, "CAS": -500,
                             "EEU": -500, "SEA": 500})
P("iron_weapons", "Iron weapons", "weapons and armour", needs=["settled"], inputs=[["iron"]],
  made={"WAS": -1100, "NAF": -650, "EUR": -850, "SAS": -1100, "EAS": -650, "CAS": -950, "EEU": -750, "SEA": -450,
        "WAF": -550, "EAF": -450, "MSA": 350, "CAC": 1530, "SAM": 1540, "MNA": 1620},
  brought={"NNA": 1700, "AUS": 1788, "PAC": 1800})
P("saltpetre", "Saltpetre", "weapons and armour", needs=["settled"],
  made={"EAS": 800, "SAS": 1000, "WAS": 1250, "EUR": 1350, "EEU": 1500, "NAF": 1300, "SAM": 1830, "MNA": 1770},
  brought={"EUR": 1600, "CAS": 1450, "SEA": 1500}, note="Bihar was the main source from 1600 to 1850")
P("sulphur", "Sulphur", "weapons and armour",
  made={"EUR": -500, "EAS": -500, "WAS": 0, "SEA": 1500, "CAC": 1550, "MNA": 1900, "SAM": 1600},
  brought={"ALL": 1700, "SAS": 1300, "NAF": 1000, "EEU": 1000, "CAS": 1300})
P("gunpowder", "Gunpowder", "weapons and armour", needs=["town"], inputs=[["saltpetre"], ["sulphur"], ["charcoal"]],
  made={"EAS": 900, "WAS": 1280, "EUR": 1350, "EEU": 1500, "NAF": 1300, "SAS": 1400, "CAS": 1450, "SEA": 1500,
        "MNA": 1775, "SAM": 1830},
  brought={"ALL": 1700, "CAC": 1520, "SAM": 1530, "MNA": 1600, "NNA": 1650, "AUS": 1788, "PAC": 1790},
  note="China in the 800s; the weapons step adds licences")
P("firearms", "Firearms", "weapons and armour", needs=["settled"], inputs=[["gunpowder"], ["iron", "bronze"]],
  made={"EAS": 1280, "EUR": 1350, "WAS": 1400, "EEU": 1500, "NAF": 1450, "SAS": 1500, "CAS": 1500, "SEA": 1520,
        "MNA": 1775, "SAM": 1830},
  brought={"ALL": 1700, "CAC": 1520, "SAM": 1530, "MNA": 1600, "NNA": 1650, "AUS": 1788, "WAF": 1600,
           "EAF": 1550, "MSA": 1700, "PAC": 1790}, note="see WEAPONS_RESEARCH.md")
P("armour", "Metal armour", "weapons and armour", needs=["settled"], inputs=[["bronze", "iron"]],
  made={"WAS": -2000, "EUR": -1000, "SAS": -1500, "NAF": -1500, "EAS": -1000, "CAS": -1000, "EEU": -1000,
        "SEA": 0, "WAF": 1100}, gone={"EUR": 1700, "WAS": 1750, "SAS": 1800, "EAS": 1870, "EEU": 1700,
                                     "NAF": 1800, "CAS": 1850, "SEA": 1800, "WAF": 1900},
  note="it fades after guns")

# ------------------------------------------------------------------------------------------------ 9. transport
P("carts", "Carts and the wheel", "transport", needs=["farm"],
  made={"WAS": -3500, "EUR": -3000, "EEU": -3500, "SAS": -2600, "NAF": -1700, "EAS": -1200, "CAS": -3000,
        "SEA": 0, "EAF": 1500, "MSA": 1700, "CAC": 1530, "SAM": 1540, "MNA": 1620, "NNA": 1750, "AUS": 1788,
        "PAC": 1850, "WAF": 1900}, note="no wheels for carrying in the Americas before 1492")
P("boats", "Boats and ships", "transport", made={"ALL": ANY}, estimate=False)
P("saddle", "Saddles", "transport", item="minecraft:saddle", count=1, days=2.0, short="Saddle", inputs=[["leather"], ["horses",
                                                                                                    "camels"]],
  made={"EEU": -1000, "CAS": -1000, "WAS": -700, "EUR": -500, "NAF": -500, "SAS": -500, "EAS": -300, "SEA": 0,
        "WAF": 1100, "EAF": 1600, "MSA": 1700, "CAC": 1530, "SAM": 1540, "MNA": 1660, "NNA": 1740, "AUS": 1800})
P("railway", "Railways", "transport", needs=["town"], inputs=[["coal", "kerosene", "petrol"], ["iron", "steel"]],
  made={"EUR": 1825, "MNA": 1830, "NNA": 1836, "EEU": 1837, "CAC": 1837, "SAM": 1851, "SAS": 1853, "AUS": 1854,
        "NAF": 1856, "WAS": 1856, "MSA": 1860, "SEA": 1867, "EAS": 1876, "CAS": 1880, "WAF": 1885, "EAF": 1896,
        "PAC": 1900}, note="Britain 1825; India 1853")
P("bicycle", "Bicycles", "transport", made={"EUR": 1868, "MNA": 1878, "EAS": 1900, "SAS": 1952, "EEU": 1900,
                                            "AUS": 1890},
  brought={"ALL": 1895})
P("car", "Motor cars", "transport", needs=["town"], inputs=[["petrol"]],
  made={"EUR": 1886, "MNA": 1896, "EEU": 1910, "AUS": 1920, "SAM": 1920, "EAS": 1930, "SAS": 1948, "CAC": 1925,
        "NNA": 1904, "WAS": 1960, "NAF": 1960, "MSA": 1930, "SEA": 1960},
  brought={"ALL": 1905}, note="India's first car in 1898; Hindustan Motors from 1948")
P("aeroplane", "Air travel", "transport", needs=["town"], inputs=[["petrol"]],
  made={"EUR": 1919, "MNA": 1925, "EEU": 1923, "SAS": 1932, "EAS": 1930, "AUS": 1921, "SAM": 1927, "CAC": 1930,
        "NNA": 1927, "WAS": 1935, "NAF": 1935, "MSA": 1935, "SEA": 1935, "EAF": 1935, "WAF": 1940, "CAS": 1935,
        "PAC": 1945}, note="Tata Airlines 1932")

# ---------------------------------------------------------------------------------- 10. writing and knowledge
P("clay_tablets", "Clay tablets", "writing and knowledge", needs=["town"], made={"WAS": -3200}, gone={"WAS": 100},
  estimate=False, note="cuneiform, about 3200 BCE to about 75 CE")
P("papyrus", "Papyrus", "writing and knowledge", needs=["town"], made={"NAF": -3000}, brought={"EUR": -600, "WAS": -600},
  gone={"NAF": 1100, "EUR": 1100, "WAS": 1000})
P("palm_leaf", "Palm-leaf books", "writing and knowledge", needs=["town"], item="minecraft:paper", count=8, days=0.2, short="Palm leaves",
  rename=True,
  made={"SAS": -300, "SEA": 500}, gone={"SAS": 1900, "SEA": 1900}, note="South India; paper took over")
P("birch_bark", "Birch-bark writing", "writing and knowledge", made={"SAS": 0, "EEU": 1000, "NNA": 1000},
  gone={"SAS": 1600, "EEU": 1500})
P("parchment", "Parchment", "writing and knowledge", needs=["town"], inputs=[["sheep_goats", "cattle"]],
  made={"WAS": -200, "EUR": 0, "NAF": 0, "EEU": 900, "EAF": 400}, gone={"EUR": 1550, "WAS": 1200, "NAF": 1200,
                                                                      "EEU": 1600})
P("paper", "Paper", "writing and knowledge", item="minecraft:paper", count=16, days=0.3, short="Paper", needs=["town"],
  inputs=[["cotton", "linen", "hemp", "bark_cloth", "silk"]],
  made={"EAS": 105, "CAS": 751, "WAS": 794, "NAF": 900, "EUR": 1150, "SAS": 1200, "EEU": 1500, "SEA": 1300,
        "CAC": 1580, "MNA": 1690, "SAM": 1600, "AUS": 1820, "MSA": 1900, "NNA": 1800},
  brought={"ALL": 1700, "WAF": 1300, "EAF": 1300, "MSA": 1700, "AUS": 1788, "PAC": 1800, "SAM": 1540,
           "MNA": 1610, "CAC": 1521},
  note="China about 105; Samarkand 751; Baghdad 794; Spain 1150; the Delhi sultans; in Mexico brought by the"
       " Spanish from 1521 and made at Culhuacan from about 1580 (bark paper before that is its own row)")
P("bark_paper", "Bark paper (amate)", "writing and knowledge", needs=["town"], made={"CAC": 75}, gone={"CAC": 1600},
  note="the oldest known piece 75 CE (Huitzilapa, Jalisco); Maya huun from the 5th century; Maya and Aztec books;"
       " mostly banned after the Spanish conquest and replaced by European paper")
P("bamboo_slips", "Bamboo and wooden slips", "writing and knowledge", needs=["town"], made={"EAS": -1250},
  gone={"EAS": 400},
  note="precursors from the late Shang (about 1250 BCE); the earliest surviving slips 5th century BCE; the standard"
       " writing material of the Han; largely given up for paper by the 4th century CE")
P("wax_tablets", "Wax tablets", "writing and knowledge", needs=["town"],
  made={"WAS": -1300, "EUR": -750, "NAF": -300}, gone={"WAS": 1000, "NAF": 1000, "EUR": 1600},
  note="a writing board in the Uluburun wreck (14th century BCE); Greeks from the mid-8th century BCE; Roman and"
       " medieval notes and accounts (Enns hospital records from 1500); paper notebooks took over in the 1500s, though"
       " a few markets kept them longer; Egypt with Greek schools (estimate)")
P("ink", "Ink", "writing and knowledge", needs=["town"], item="minecraft:ink_sac", count=4, days=0.1, short="Ink",
  made={"NAF": -2500, "WAS": -2500, "EAS": -1000, "SAS": -400, "EUR": -500, "EEU": 900, "CAS": 0, "SEA": 500,
        "CAC": -500, "SAM": 1550, "MNA": 1640, "NNA": 1700, "AUS": 1800, "EAF": 400, "WAF": 1500, "MSA": 1700,
        "PAC": 1800})
P("books", "Printed books", "writing and knowledge", item="minecraft:book", count=1, days=1.0, short="Printed book", needs=["town"],
  inputs=[["paper", "parchment"], ["ink"]],
  made={"EAS": 900, "EUR": 1455, "CAC": 1539, "SAS": 1556, "EEU": 1564, "SAM": 1584, "SEA": 1593, "MNA": 1640,
        "WAS": 1727, "AUS": 1802, "NAF": 1820, "MSA": 1800, "CAS": 1880, "EAF": 1890, "WAF": 1900, "PAC": 1830,
        "NNA": 1750},
  brought={"ALL": 1800, "WAS": 1500, "SAS": 1600, "NAF": 1550, "AUS": 1788}, note="Goa 1556; Istanbul 1727")
P("newspaper", "Newspapers", "writing and knowledge", needs=["town"], inputs=[["paper"], ["ink"]],
  made={"EUR": 1605, "MNA": 1690, "EEU": 1703, "CAC": 1722, "SAS": 1780, "MSA": 1800, "AUS": 1803, "SAM": 1808,
        "SEA": 1820, "NAF": 1828, "WAS": 1831, "CAS": 1870, "EAS": 1870, "NNA": 1750, "WAF": 1850, "EAF": 1870,
        "PAC": 1840},
  note="the newspaper of steps 19c-19d (paper sellers follow NewsEras city by city)")
P("maps", "Maps", "writing and knowledge", needs=["town"],
  inputs=[["paper", "parchment", "papyrus", "palm_leaf", "silk"], ["ink"]],
  made={"WAS": -600, "NAF": -1100, "EUR": -500, "EAS": -200, "SAS": 1000, "EEU": 1100, "CAS": 900, "SEA": 1500,
        "CAC": 1540, "SAM": 1600, "MNA": 1650, "AUS": 1800, "NNA": 1750, "MSA": 1800, "EAF": 1800, "WAF": 1800,
        "PAC": 1850}, note="the map of step 19e")
P("telegraph", "Telegraph", "writing and knowledge", needs=["town"],
  made={"EUR": 1840, "MNA": 1844, "CAC": 1851, "SAS": 1854, "AUS": 1854, "NAF": 1854, "WAS": 1855, "EEU": 1853,
        "SAM": 1857, "EAS": 1871, "SEA": 1870, "MSA": 1860, "NNA": 1850, "CAS": 1880, "EAF": 1890, "WAF": 1890,
        "PAC": 1900})
P("telephone", "Telephone", "writing and knowledge", needs=["town"],
  made={"MNA": 1877, "EUR": 1879, "SAS": 1882, "EAS": 1882, "AUS": 1880, "EEU": 1882, "SAM": 1880, "CAC": 1882,
        "NNA": 1880, "WAS": 1890, "NAF": 1890, "MSA": 1890, "SEA": 1890, "EAF": 1900, "WAF": 1900, "CAS": 1900,
        "PAC": 1900}, note="India 1882")
P("radio", "Radio", "writing and knowledge", needs=["town"],
  made={"MNA": 1920, "EUR": 1922, "EEU": 1924, "AUS": 1923, "EAS": 1925, "SAM": 1925, "SAS": 1955, "NNA": 1922},
  brought={"ALL": 1930, "SAS": 1927, "CAC": 1923}, note="the Radio Club of Bombay 1923; sets were brought from abroad")
P("television", "Television", "writing and knowledge", needs=["town"],
  made={"EUR": 1936, "MNA": 1941, "EEU": 1950, "EAS": 1953, "SAM": 1950, "CAC": 1950, "AUS": 1956, "SAS": 1959,
        "NNA": 1952, "WAS": 1960, "NAF": 1960, "MSA": 1976, "SEA": 1962, "EAF": 1965, "WAF": 1960, "CAS": 1960,
        "PAC": 1970}, note="India 1959")
P("internet", "The internet", "writing and knowledge", needs=["town"],
  made={"MNA": 1991, "EUR": 1993, "EAS": 1994, "SAS": 1995, "AUS": 1993, "EEU": 1995, "NNA": 1991, "ALL": 1997})

# -------------------------------------------------------------------------------------------------- 11. money
P("barter", "Barter", "money", made={"ALL": ANY}, estimate=False, note="the money table (step 19a)")
P("coins", "Coins", "money", needs=["town"],
  made={"WAS": -600, "EUR": -550, "SAS": -500, "EAS": -600, "NAF": -400, "CAS": -400, "EEU": -500, "SEA": 400,
        "EAF": 270, "CAC": 1536, "SAM": 1568, "MNA": 1652, "NNA": 1800, "AUS": 1788, "MSA": 1700, "WAF": 1900,
        "PAC": 1850}, brought={"WAF": 1700}, note="Lydia; punch-marked coins in India; Aksum's coins")
P("paper_money", "Paper money", "money", needs=["town"],
  made={"EAS": 1024, "EUR": 1661, "MNA": 1690, "EEU": 1769, "SAS": 1770, "WAS": 1840, "NAF": 1898, "SAM": 1820,
        "CAC": 1822, "AUS": 1817, "NNA": 1817, "SEA": 1850, "MSA": 1850, "EAF": 1900, "WAF": 1900, "CAS": 1920,
        "PAC": 1900}, note="China 1024; Sweden 1661; the Bank of Hindostan 1770; Hyderabad 1918")

# ------------------------------------------------------------------------------------------ 12. medicine and care
P("herbs", "Herbal medicine", "medicine and care", made={"ALL": ANY}, estimate=False,
  note="Ayurveda and Unani in India")
P("quinine", "Quinine", "medicine and care", needs=["town"],
  made={"SAM": 1630, "SAS": 1865, "SEA": 1854},
  brought={"EUR": 1640, "ALL": 1820, "WAS": 1700, "MNA": 1700},
  note="Jesuit's bark from Peru; cinchona in the Nilgiris from the 1860s")
P("vaccine", "Smallpox vaccine", "medicine and care", needs=["town"],
  made={"EUR": 1796, "MNA": 1800, "SAS": 1802, "CAC": 1804, "SAM": 1805, "SEA": 1805, "EAS": 1805, "EEU": 1801,
        "WAS": 1840, "NAF": 1830, "AUS": 1804, "NNA": 1800, "MSA": 1803, "EAF": 1900, "WAF": 1900, "CAS": 1880,
        "PAC": 1850}, note="Jenner 1796; Bombay 1802")
P("penicillin", "Penicillin", "medicine and care", needs=["town"],
  made={"MNA": 1942, "EUR": 1943, "AUS": 1944, "EEU": 1946, "EAS": 1950, "SAS": 1954, "SAM": 1950},
  brought={"ALL": 1946, "SAS": 1945})
P("soap", "Soap", "medicine and care", needs=["settled"],
  inputs=[["olive_oil", "cooking_oil", "cattle", "sheep_goats"], ["potash"]],
  made={"WAS": -2800, "NAF": -1500, "EUR": 0, "EEU": 900, "CAS": 900, "SAS": 1800, "EAS": 1900, "MNA": 1620,
        "SAM": 1550, "CAC": 1530, "AUS": 1800, "MSA": 1700, "EAF": 1900, "WAF": 1900, "SEA": 1900, "NNA": 1750},
  brought={"ALL": 1880})

# --------------------------------------------------------------------------------- 13. luxury, faith and fun
P("tobacco", "Tobacco", "luxury, faith and fun", needs=["farm"],
  made={"SAM": -3000, "CAC": -1000, "MNA": -1000, "NNA": 500, "EUR": 1560, "WAS": 1600, "NAF": 1600, "SAS": 1605,
        "EAS": 1620, "SEA": 1575, "EEU": 1697, "WAF": 1600, "EAF": 1650, "MSA": 1650, "CAS": 1650, "AUS": 1800,
        "PAC": 1800}, note="India about 1605, at Akbar's court")
P("betel", "Betel leaf and areca (paan)", "luxury, faith and fun", needs=["farm"],
  made={"SEA": -2500, "SAS": -500, "EAS": 200, "PAC": -1000, "EAF": 1000})
P("incense", "Incense", "luxury, faith and fun",
  made={"WAS": -2000, "EAF": -2000, "SAS": -1000, "EAS": 200, "SEA": 500, "CAC": -1000},
  brought={"NAF": -2500, "EUR": -700, "EEU": 900, "CAS": 0, "ALL": 1800})
P("perfume", "Attar and perfume", "luxury, faith and fun", needs=["town"],
  made={"NAF": -2000, "WAS": -1200, "SAS": 1000, "EUR": 1300, "EAS": 500, "EEU": 1700, "CAS": 1000},
  brought={"ALL": 1850})
P("chess", "Chess", "luxury, faith and fun", needs=["town"],
  made={"SAS": 600, "WAS": 650, "NAF": 700, "CAS": 700, "EAS": 800, "EUR": 1000, "EEU": 1000, "SEA": 1000,
        "EAF": 1100, "CAC": 1550, "SAM": 1550, "MNA": 1650, "NNA": 1750, "AUS": 1800}, note="India about 600")
P("playing_cards", "Playing cards (ganjifa)", "luxury, faith and fun", needs=["town"],
  made={"EAS": 900, "WAS": 1300, "NAF": 1350, "EUR": 1370, "SAS": 1520, "EEU": 1500, "CAS": 1500, "SEA": 1600,
        "AMR": 1600, "AUS": 1800}, note="the Mughals' ganjifa in the 1520s")

# ------------------------------------------------------------------------------------- 14. papers and permits
P("land_deeds", "Land deeds", "papers and permits", needs=["town"],
  made={"WAS": -3000, "NAF": -2500, "EUR": -500, "SAS": -300, "EAS": -500, "EEU": 900, "CAS": 0, "SEA": 900,
        "AMR": 1530, "AUS": 1790, "AFR": 1850, "PAC": 1850})
P("railway_ticket", "Railway tickets", "papers and permits", needs=["town"], inputs=[["railway"]],
  made={"EUR": 1830, "MNA": 1830, "NNA": 1836, "EEU": 1837, "CAC": 1837, "SAM": 1851, "SAS": 1853, "AUS": 1854,
        "NAF": 1856, "WAS": 1856, "MSA": 1860, "SEA": 1867, "EAS": 1876, "CAS": 1880, "WAF": 1885, "EAF": 1896,
        "PAC": 1900})
P("weapon_licence", "Weapon licences", "papers and permits", needs=["town"],
  made={"SAS": 1878, "EUR": 1920, "MNA": 1934, "EAS": 1900, "AUS": 1920, "EEU": 1924, "ALL": 1950},
  note="the Indian Arms Act of 1878")
P("passport", "Passports", "papers and permits", needs=["town"], made={"ALL": 1920}, note="the League of Nations standard of 1920")
P("ration_card", "Ration cards", "papers and permits", needs=["town"],
  made={"EUR": 1940, "EEU": 1941, "SAS": 1943, "EAS": 1955, "AUS": 1942, "MNA": 1942},
  gone={"EUR": 1954, "MNA": 1946, "AUS": 1950})


# --------------------------------------------------------------------------------------------------- checks
def first(p, area):
    ys = [y for y in (p["made"].get(area), p["brought"].get(area)) if y is not None]
    return min(ys) if ys else None


def check():
    """Every input of a product is made or brought in an area by the year the product is made there."""
    by = {p["id"]: p for p in PRODUCTS}
    problems = []
    for p in PRODUCTS:
        for grp in p.get("inputs", []):
            for i in grp:
                assert i in by, (p["id"], i)
        for area, y in p["made"].items():
            for grp in p.get("inputs", []):
                avail = [first(by[i], area) for i in grp if by[i]["gone"].get(area, 99999) > y]
                avail = [a for a in avail if a is not None]
                if not avail or min(avail) > y:
                    problems.append(f"{p['id']} made in {area} in {y}, but none of {grp} is there by then "
                                    f"({min(avail) if avail else 'never'})")
        for area, g in p["gone"].items():
            f = first(p, area)
            if f is not None and g <= f:
                problems.append(f"{p['id']} gone in {area} in {g}, before it came ({f})")
    for staple in ("food", "cloth", "fuel", "light"):
        for area in AREAS:
            if not any(p.get("staple") == staple and first(p, area) is not None and first(p, area) <= -3000
                       and not p.get("needs") for p in PRODUCTS):
                problems.append(f"no {staple} without needs in {area} from 3000 BCE")
    return problems


def main():
    problems = check()
    for pr in problems:
        print("PROBLEM", pr)
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, "eternal/src/main/resources/data/eternalengine/eternal/economy/products_world.json")
    # Step 44 part C: this file grows to 529 products, 397 of them derived by
    # build_products_c.py. Running this script alone would quietly put it back to 132, so it
    # refuses to overwrite a pack that already holds derived rows and says where to go instead.
    if os.path.exists(out):
        try:
            with open(out, encoding="utf-8") as f:
                have = json.load(f)
            if any(p.get("derived") for p in have.get("products", [])):
                print("REFUSING to overwrite " + out)
                print("  it holds %d products, %d of them derived by part C."
                      % (len(have.get("products", [])),
                         sum(1 for p in have.get("products", []) if p.get("derived"))))
                print("  run build_products_c.py instead: it imports this file and adds to it.")
                return 1
        except Exception as e:
            print("cannot read the existing pack, so refusing to overwrite it: " + str(e))
            return 1
    data = {
        "format": 1,
        "about": "Product atlas part B (worldfill/build_product_atlas.py): the world product list and, per area of the"
                 " ways-of-life survey, the year each product is first made there, first brought there, and gone."
                 " Most years are estimates (estimate=true) for a whole area, from the history of each product.",
        "areas": [{"id": a, "name": AREA_NAMES[a]} for a in AREAS],
        "families": FAMILIES,
        "products": PRODUCTS,
    }
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    # The table for checking by eye.
    lines = ["# Product atlas, part B: the years (generated by build_product_atlas.py)", "",
             "Each cell: the year a product is first **made** in the area; *b* = first brought there by trade;"
             " *g* = gone (replaced). Empty: never. BCE years are negative. Areas: " +
             "; ".join(f"{a} {AREA_NAMES[a]}" for a in AREAS) + ".", "",
             "Most years are estimates for a whole area (its earliest corner). Please tell me any that look wrong.", ""]
    for fam in FAMILIES:
        rows = [p for p in PRODUCTS if p["family"] == fam]
        if not rows:
            continue
        lines += [f"## {fam[0].upper() + fam[1:]}", "", "| Product | " + " | ".join(AREAS) + " |",
                  "|---|" + "---|" * len(AREAS)]
        for p in rows:
            cells = []
            for a in AREAS:
                c = []
                if a in p["made"]:
                    c.append("always" if p["made"][a] == ANY else str(p["made"][a]))
                if a in p["brought"]:
                    c.append(f"b {'always' if p['brought'][a] == ANY else p['brought'][a]}")
                if a in p["gone"]:
                    c.append(f"g {p['gone'][a]}")
                cells.append(" ".join(c))
            mark = " (est.)" if p.get("estimate") else ""
            lines.append(f"| {p['name']}{mark} | " + " | ".join(cells) + " |")
        lines.append("")
    with open(os.path.join(root, "worldfill/PRODUCT_ATLAS_TABLE.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    items = sum(1 for p in PRODUCTS if p.get("item"))
    print(f"{len(PRODUCTS)} products ({items} with items), {len(problems)} problems -> {out}")


if __name__ == "__main__":
    main()
