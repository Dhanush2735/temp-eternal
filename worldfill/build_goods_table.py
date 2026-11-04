#!/usr/bin/env python3
"""Step 19b: write the goods table (what merchants buy, which items count as it, and where and when it is bought).

Writes eternal/src/main/resources/data/eternalengine/eternal/economy/goods.json.

Rules of the file (GoodsTable.java reads it):
  * One entry per good of the trade engine (CommodityPricingEngine): "id" is the engine's name (WHEAT ...). The
    price comes from the engine (its base price, times its supply and demand), never from this file.
  * "name" is the good in a list ("wheat", "logs"); "one" and "many" name a single item and several ("sheaf of
    wheat", "sheaves of wheat").
  * "items": Minecraft item ids, or item tags written with a "#" ("#minecraft:wool"). A good without items cannot be
    sold yet (wine, silk and spices wait for their own items in the product atlas).
  * "unitItems": how many items make one priced unit of the engine (4 sheaves of wheat are one unit of WHEAT). One
    engine unit is worth a twentieth of an ordinary labourer's day (MarketService.DAYS_PER_PRICE_UNIT).
  * "want": how many a merchant takes in one Minecraft day at full price; the next as many at half price; then he
    has enough of it for the day.
  * "not": where and when nobody buys it: {"before": year} everywhere, or with "box": [latMin, lonMin, latMax, lonMax]
    only there. Years are BCE negative; "before" is exclusive (iron "before": -1200 is bought from 1200 BCE on).
  * Notes are for developers only; the game never shows them, and the player never sees where a number came from.
"""
import json
import os

from build_money_table import AMERICAS, AUSTRALIA, CHINA, JAPAN

OUT = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/economy/goods.json"

KOREA = [33, 124, 43.5, 131]
SOUTHERN_AFRICA = [-35, 10, -15, 41]

# Engine base prices (CommodityPricingEngine.registerDefaults), only to print the table below and to check that
# every good is one the engine knows.
ENGINE = {"WHEAT": 2.0, "BREAD": 3.0, "TIMBER": 4.0, "STONE": 2.5, "COAL": 5.0, "IRON_INGOT": 10.0,
          "COPPER_INGOT": 7.0, "WOOL": 6.0, "WINE": 14.0, "SILK": 28.0, "SPICES": 35.0, "GOLD_INGOT": 55.0,
          "EMERALD": 65.0}
DAYS_PER_PRICE_UNIT = 0.05


def before(year, box=None, note=None):
    r = {"before": year}
    if box:
        r["box"] = box
    if note:
        r["note"] = note
    return r


NO_GRAIN = [before(1520, AMERICAS, "Wheat came to the Americas with the Spanish (Mexico in the 1520s)."),
            before(1788, AUSTRALIA, "Wheat and bread came to Australia with the First Fleet (1788).")]
NOT_IN_AUSTRALIA = [before(1788, AUSTRALIA, "No metal, wool or gems in trade before 1788.")]

GOODS = [
    {"id": "WHEAT", "name": "wheat", "one": "sheaf of wheat", "many": "sheaves of wheat",
     "items": ["minecraft:wheat"], "unitItems": 4, "want": 64, "not": NO_GRAIN},
    {"id": "BREAD", "name": "bread", "one": "loaf of bread", "many": "loaves of bread",
     "items": ["minecraft:bread"], "unitItems": 1.5, "want": 32, "not": NO_GRAIN,
     "note": "A loaf (3 sheaves) is worth a third more than its wheat: the baker's work and fuel."},
    {"id": "TIMBER", "name": "logs", "one": "log", "many": "logs",
     "items": ["#minecraft:logs_that_burn"], "unitItems": 4, "want": 64, "not": []},
    {"id": "STONE", "name": "stone", "one": "block of stone", "many": "blocks of stone",
     "items": ["minecraft:stone", "minecraft:cobblestone"], "unitItems": 16, "want": 128, "not": []},
    {"id": "COAL", "name": "coal", "one": "lump of coal", "many": "lumps of coal",
     "items": ["minecraft:coal", "minecraft:charcoal"], "unitItems": 4, "want": 32, "not": NOT_IN_AUSTRALIA,
     "note": "Charcoal counts as coal: it was the fuel of smiths everywhere long before coal was mined."},
    {"id": "IRON_INGOT", "name": "iron", "one": "bar of iron", "many": "bars of iron",
     "items": ["minecraft:iron_ingot"], "unitItems": 1, "want": 16,
     "not": [before(-1200, None, "The Iron Age: the Near East and South Asia about 1200 BCE."),
             before(-700, CHINA, "Iron in China from about 700-600 BCE."),
             before(-400, KOREA, "Iron in Korea from about 400 BCE."),
             before(-300, JAPAN, "Iron in Japan from about 300 BCE (Yayoi)."),
             before(300, SOUTHERN_AFRICA, "Iron reached southern Africa about 300 CE."),
             before(1500, AMERICAS, "No iron working in the Americas before the Spanish."),
             before(1788, AUSTRALIA)]},
    {"id": "COPPER_INGOT", "name": "copper", "one": "bar of copper", "many": "bars of copper",
     "items": ["minecraft:copper_ingot"], "unitItems": 1, "want": 16, "not": NOT_IN_AUSTRALIA},
    {"id": "WOOL", "name": "wool", "one": "bundle of wool", "many": "bundles of wool",
     "items": ["#minecraft:wool"], "unitItems": 2, "want": 32, "not": NOT_IN_AUSTRALIA},
    {"id": "GOLD_INGOT", "name": "gold", "one": "bar of gold", "many": "bars of gold",
     "items": ["minecraft:gold_ingot"], "unitItems": 1, "want": 4, "not": NOT_IN_AUSTRALIA},
    {"id": "EMERALD", "name": "emeralds", "one": "emerald", "many": "emeralds",
     "items": ["minecraft:emerald"], "unitItems": 1, "want": 4, "not": NOT_IN_AUSTRALIA},
    {"id": "WINE", "name": "wine", "one": "jar of wine", "many": "jars of wine", "items": [], "unitItems": 1,
     "want": 8, "not": [], "note": "No item yet: comes with the product atlas."},
    {"id": "SILK", "name": "silk", "one": "bolt of silk", "many": "bolts of silk", "items": [], "unitItems": 1,
     "want": 8, "not": [], "note": "No item yet: comes with the product atlas."},
    {"id": "SPICES", "name": "spices", "one": "bag of spices", "many": "bags of spices", "items": [],
     "unitItems": 1, "want": 8, "not": [], "note": "No item yet: comes with the product atlas."},
]


def main():
    ids = set()
    for g in GOODS:
        assert g["id"] in ENGINE, g["id"]
        assert g["id"] not in ids, g["id"]
        ids.add(g["id"])
        assert g["unitItems"] > 0 and g["want"] > 0, g["id"]
        for it in g["items"]:
            assert ":" in it, (g["id"], it)
        for r in g["not"]:
            assert isinstance(r["before"], int), (g["id"], r)
            if "box" in r:
                b = r["box"]
                assert len(b) == 4 and b[0] < b[2] and b[1] < b[3], (g["id"], b)
    data = {
        "format": 1,
        "about": "Step 19b: what merchants buy. See worldfill/build_goods_table.py for the rules. Prices come from"
                 " the trade engine; notes are for developers only.",
        "goods": GOODS,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    with_items = sum(1 for g in GOODS if g["items"])
    print(f"wrote {OUT}: {len(GOODS)} goods ({with_items} with items), {os.path.getsize(OUT):,} bytes")
    print("worth of one item, in days of an ordinary labourer's pay (before the merchant's share):")
    for g in GOODS:
        days = ENGINE[g["id"]] * DAYS_PER_PRICE_UNIT / g["unitItems"]
        print(f"  {g['id']:<13} {days:.4f}  ({g['want']} a day at full price)")


if __name__ == "__main__":
    main()
