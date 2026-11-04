"""
Step 44 part 2 (E4, prices and wages through time): the Allen-Unger commodities, as the mod
names them.

The database has **160 commodity names with no vocabulary of its own** -- "Wheat", "Rye",
"Cocao", "Buchwheat", "Pork Mess" -- and each is measured in whatever unit the archive happened
to use: wheat appears by the kilogram *and* by the litre, cloth by the metre, the square metre
and the kilogram. A price in litres of wheat cannot be compared with a price in kilograms of it.

So each commodity gets one **canonical measure**, the one the data uses most, and observations
in any other measure are set aside and counted. That is the only way a series means one thing
from one end of it to the other.

`family` is the product atlas's own fourteen families (`economy/products_world.json`), so a
price can be joined to a product.

**One commodity is deliberately left out: `Slave`, 179 observations, measured in "Individual
Adult Male".** It is in the source and it is not going into this mod. A price for a human being
has no business appearing as a market price, and the game has no honest use for it. The
exclusion is recorded in the pack's own `gaps`.
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "/tmp/fc/forex-centuries-main/data/sources/allenunger"

# Families, from economy/products_world.json
STAPLE = "staple food"
FOOD = "other food and drink"
ANIMAL = "animals and animal goods"
CLOTH = "cloth and clothes"
BUILD = "building"
FUEL = "fuel and light"
METAL = "metals and tools"
WEAPON = "weapons and armour"
TRANSPORT = "transport"
WRITE = "writing and knowledge"
MONEY = "money"
MEDICINE = "medicine and care"
LUXURY = "luxury, faith and fun"
PAPERS = "papers and permits"

# (allen-unger name, mod id, display name, family, canonical measure)
GOODS = [
    # ---- staple food
    ("Wheat", "wheat", "wheat", STAPLE, "Kilogram"),
    ("Rye", "rye", "rye", STAPLE, "Kilogram"),
    ("Barley", "barley", "barley", STAPLE, "Kilogram"),
    ("Oats", "oats", "oats", STAPLE, "Kilogram"),
    ("Rice", "rice", "rice", STAPLE, "Kilogram"),
    ("Maize", "maize", "maize", STAPLE, "Kilogram"),
    ("Millet", "millet", "millet", STAPLE, "Kilogram"),
    ("Sorghum", "millet", "sorghum", STAPLE, "Litre"),
    ("Potato", "potato", "potatoes", STAPLE, "Kilogram"),
    ("Spelt", "spelt", "spelt", STAPLE, "Litre"),
    ("Buchwheat", "buckwheat", "buckwheat", STAPLE, "Litre"),
    ("Bread", "bread", "bread", STAPLE, "Kilogram"),
    ("Flour", "flour", "flour", STAPLE, "Kilogram"),
    ("Oatmeal", "oatmeal", "oatmeal", STAPLE, "Kilogram"),
    ("Meal", "meal", "meal", STAPLE, "Litre"),
    ("Grains", "grain", "grain", STAPLE, "Kilogram"),
    ("Peas", "pulses", "peas", STAPLE, "Litre"),
    ("Beans", "pulses", "beans", STAPLE, "Kilogram"),
    ("Garbanzo", "pulses", "chickpeas", STAPLE, "Kilogram"),
    ("Chickpeas", "pulses", "chickpeas", STAPLE, "Kilogram"),
    ("Soybean", "soy", "soy beans", STAPLE, "Litre"),
    ("Soy", "soy", "soy", STAPLE, "Litre"),
    ("Oilcake", "oilcake", "oilcake", STAPLE, "Kilogram"),
    # ---- other food and drink
    ("Sugar", "sugar", "sugar", FOOD, "Kilogram"),
    ("Treacle", "sugar", "treacle", FOOD, "Kilogram"),
    ("Molasses", "sugar", "molasses", FOOD, "Litre"),
    ("Maple Syrup", "sugar", "maple syrup", FOOD, "Litre"),
    ("Honey", "honey", "honey", FOOD, "Kilogram"),
    ("Salt", "salt", "salt", FOOD, "Kilogram"),
    ("Wine", "wine", "wine", FOOD, "Litre"),
    ("Malmsey", "wine", "malmsey", FOOD, "Litre"),
    ("Beer", "beer", "beer", FOOD, "Litre"),
    ("Sake", "beer", "sake", FOOD, "Litre"),
    ("Cider", "cider", "cider", FOOD, "Litre"),
    ("Brandy", "spirits", "brandy", FOOD, "Litre"),
    ("Whiskey", "spirits", "whiskey", FOOD, "Litre"),
    ("Rum", "spirits", "rum", FOOD, "Litre"),
    ("Gin", "spirits", "gin", FOOD, "Litre"),
    ("Spirits", "spirits", "spirits", FOOD, "Litre"),
    ("Tea", "tea", "tea", FOOD, "Kilogram"),
    ("Coffee", "coffee", "coffee", FOOD, "Kilogram"),
    ("Chicory", "coffee", "chicory (a coffee substitute)", FOOD, "Kilogram"),
    ("Chocolate", "cacao", "chocolate", FOOD, "Kilogram"),
    ("Cocao", "cacao", "cacao", FOOD, "Litre"),
    ("Yerba", "tea", "yerba mate", FOOD, "Kilogram"),
    ("Oil", "cooking_oil", "cooking oil", FOOD, "Litre"),
    ("Vinegar", "vinegar", "vinegar", FOOD, "Litre"),
    ("Mustard", "mustard", "mustard", FOOD, "Litre"),
    ("Soya Sauce", "soy_sauce", "soy sauce", FOOD, "Litre"),
    ("Miso", "miso", "miso", FOOD, "Kilogram"),
    ("Pepper", "spices", "pepper", FOOD, "Kilogram"),
    ("Ginger", "spices", "ginger", FOOD, "Kilogram"),
    ("Saffron", "spices", "saffron", FOOD, "Kilogram"),
    ("Cinnamon", "spices", "cinnamon", FOOD, "Kilogram"),
    ("Cloves", "spices", "cloves", FOOD, "Kilogram"),
    ("Nutmeg", "spices", "nutmeg", FOOD, "Kilogram"),
    ("Allspice", "spices", "allspice", FOOD, "Kilogram"),
    ("Caraway", "spices", "caraway", FOOD, "Litre"),
    ("Currants", "fruit", "currants", FOOD, "Kilogram"),
    ("Raisins", "fruit", "raisins", FOOD, "Kilogram"),
    ("Apples", "fruit", "apples", FOOD, "Kilogram"),
    ("Plum", "fruit", "plums", FOOD, "Kilogram"),
    ("Oranges", "fruit", "oranges", FOOD, "Unit"),
    ("Pie Fruits", "fruit", "pie fruit", FOOD, "Unit"),
    ("Turnips", "vegetables", "turnips", FOOD, "Kilogram"),
    ("Cabbage", "vegetables", "cabbages", FOOD, "Unit"),
    # ---- animals and animal goods
    ("Beef", "meat", "beef", ANIMAL, "Kilogram"),
    ("Veal", "meat", "veal", ANIMAL, "Kilogram"),
    ("Mutton", "meat", "mutton", ANIMAL, "Kilogram"),
    ("Pork", "meat", "pork", ANIMAL, "Kilogram"),
    ("Pork Mess", "meat", "salt pork", ANIMAL, "Litre"),
    ("Bacon", "meat", "bacon", ANIMAL, "Kilogram"),
    ("Ham", "meat", "ham", ANIMAL, "Kilogram"),
    ("Speck", "meat", "speck", ANIMAL, "Kilogram"),
    ("Sausage", "meat", "sausage", ANIMAL, "Kilogram"),
    ("Meat", "meat", "meat", ANIMAL, "Kilogram"),
    ("Lamb", "meat", "lamb", ANIMAL, "Litre"),
    ("Ox", "cattle", "an ox", ANIMAL, "Unit"),
    ("Goat", "goats", "a goat", ANIMAL, "Unit"),
    ("Turkey", "poultry", "turkey", ANIMAL, "Kilogram"),
    ("Chicken", "poultry", "chickens", ANIMAL, "Unit"),
    ("Poultry", "poultry", "poultry", ANIMAL, "Unit"),
    ("Eggs", "eggs", "eggs", ANIMAL, "Unit"),
    ("Milk", "dairy", "milk", ANIMAL, "Litre"),
    ("Cream", "dairy", "cream", ANIMAL, "Litre"),
    ("Butter", "dairy", "butter", ANIMAL, "Kilogram"),
    ("Cheese", "dairy", "cheese", ANIMAL, "Kilogram"),
    ("Lard", "dairy", "lard", ANIMAL, "Kilogram"),
    ("Suet", "dairy", "suet", ANIMAL, "Kilogram"),
    ("Tallow", "dairy", "tallow", ANIMAL, "Kilogram"),
    ("Wool", "wool", "wool", ANIMAL, "Kilogram"),
    ("Silk", "silk", "silk", ANIMAL, "Kilogram"),
    ("Herring", "fish", "herring", ANIMAL, "Kilogram"),
    ("Cod", "fish", "cod", ANIMAL, "Kilogram"),
    ("Stockfish", "fish", "stockfish", ANIMAL, "Kilogram"),
    ("Salmon", "fish", "salmon", ANIMAL, "Kilogram"),
    ("Carp", "fish", "carp", ANIMAL, "Kilogram"),
    ("Pike", "fish", "pike", ANIMAL, "Kilogram"),
    ("Fish", "fish", "fish", ANIMAL, "Kilogram"),
    ("Wax", "wax", "wax", ANIMAL, "Kilogram"),
    # ---- cloth and clothes
    ("Cloth", "cloth", "cloth", CLOTH, "Metre"),
    ("Linen", "linen", "linen", CLOTH, "Metre"),
    ("Canvas", "canvas", "canvas", CLOTH, "Metre"),
    ("Sheeting", "cloth", "sheeting", CLOTH, "Metre"),
    ("Print", "cloth", "printed cloth", CLOTH, "Metre"),
    ("Clothing", "clothes", "a garment", CLOTH, "Unit"),
    ("Shoes", "shoes", "shoes", CLOTH, "Pair"),
    ("Boots", "shoes", "boots", CLOTH, "Pair"),
    ("Stockings", "stockings", "stockings", CLOTH, "Pair"),
    ("Socks", "stockings", "socks", CLOTH, "Pair"),
    ("Underpants", "clothes", "underpants", CLOTH, "Unit"),
    ("Flax", "flax", "flax", CLOTH, "Kilogram"),
    ("Cotton", "cotton", "cotton", CLOTH, "Kilogram"),
    ("Bark", "bark", "bark for tanning", CLOTH, "Kilogram"),
    # ---- building
    ("Bricks", "fired_brick", "bricks", BUILD, "Unit"),
    ("Tiles", "tiles", "tiles", BUILD, "Unit"),
    ("Lime", "lime", "lime", BUILD, "Litre"),
    ("Mortar", "lime", "mortar", BUILD, "Litre"),
    ("Boards", "timber", "boards", BUILD, "Metre"),
    ("Wood", "timber", "timber", BUILD, "Cubic Metre"),
    ("Glass", "glass", "glass", BUILD, "Unit"),
    ("Glassware", "glass", "glassware", BUILD, "Unit"),
    ("Nails", "nails", "nails", BUILD, "Kilogram"),
    # ---- fuel and light
    ("Coal", "coal", "coal", FUEL, "Kilogram"),
    ("Charcoal", "charcoal", "charcoal", FUEL, "Kilogram"),
    ("Firewood", "firewood", "firewood", FUEL, "Kilogram"),
    ("Peat", "peat", "peat", FUEL, "Cart"),
    ("Candles", "candles", "candles", FUEL, "Kilogram"),
    ("Kerosene", "kerosene", "kerosene", FUEL, "Litre"),
    ("Coalgas", "coal_gas", "coal gas", FUEL, "Litre"),
    ("Ashes", "ashes", "ashes", FUEL, "Litre"),
    ("Straw", "straw", "straw", FUEL, "Kilogram"),
    ("Hay", "hay", "hay", FUEL, "Kilogram"),
    # ---- metals and tools
    ("Iron", "iron", "iron", METAL, "Kilogram"),
    ("Copper", "copper", "copper", METAL, "Kilogram"),
    ("Lead", "lead", "lead", METAL, "Kilogram"),
    ("Pewter", "pewter", "pewter", METAL, "Kilogram"),
    ("Quicksilver", "mercury", "mercury", METAL, "Kilogram"),
    ("Shovel", "tools", "a shovel", METAL, "Unit"),
    ("Axe", "tools", "an axe", METAL, "Unit"),
    ("Saw", "tools", "a saw", METAL, "Unit"),
    ("Scythe", "tools", "a scythe", METAL, "Unit"),
    ("Horse shoes", "tools", "horse shoes", METAL, "Unit"),
    # ---- weapons
    ("Shot", "shot", "shot", WEAPON, "Kilogram"),
    # ---- transport
    ("Transportation", "transport", "carrying a load", TRANSPORT, "Kilometre"),
    ("Cordage", "cordage", "rope", TRANSPORT, "Kilogram"),
    ("Tar", "tar", "tar", TRANSPORT, "Litre"),
    ("Turpentine", "tar", "turpentine", TRANSPORT, "Litre"),
    # ---- writing and knowledge
    ("Paper", "paper", "paper", WRITE, "Sheet"),
    ("Parchment", "parchment", "parchment", WRITE, "Unit"),
    ("Books", "books", "books", WRITE, "Unit"),
    # ---- money
    ("Gold", "gold", "gold", MONEY, "Gram"),
    # ---- medicine: nothing in the source is a medicine, and the family is left empty on purpose
    # ---- luxury, faith and fun
    ("Tobacco", "tobacco", "tobacco", LUXURY, "Kilogram"),
    ("Hops", "hops", "hops", LUXURY, "Kilogram"),
    ("Soap", "soap", "soap", LUXURY, "Kilogram"),
    ("Trenchers", "trenchers", "trenchers", LUXURY, "Unit"),
]

# --------------------------------------------------------------------------- litres to kilograms
# Grain is reported two ways: Europe measured it by the litre and British India by the kilogram.
# Picking one and discarding the other silently deletes a whole subcontinent -- the first build
# kept 94% of the wheat by choosing litres and lost every Indian market, because Allahabad,
# Calcutta, Dacca and all fourteen Bengal districts weigh their grain.
#
# So grain is converted to kilograms at a bulk density, and the conversion is recorded. These are
# ordinary bulk densities (kilograms per litre), and they are estimates: a measured bushel of
# wheat weighs a little more or a little less than 0.77 kg/l according to the year, the moisture
# and the measure it was sold by. Every price so converted is marked, and the count is in the
# pack.
BULK_DENSITY = {
    "wheat": 0.77,
    "rye": 0.72,
    "barley": 0.61,
    "oats": 0.41,
    "rice": 0.75,
    "millet": 0.72,
    "maize": 0.72,
    "spelt": 0.50,
    "buckwheat": 0.65,
    "pulses": 0.77,
}

# In the data but deliberately not in the pack. See the module note about SLAVE.
EXCLUDE = {
    "Slave": "a price for a human being; 179 observations, left out on purpose",
    "Rent": "annual rent, not a commodity price",
    "Tax": "a tax, not a commodity price",
    "Insurance": "one observation, not a commodity price",
}


def by_name():
    """{allen-unger name: (id, display, family, measure)}."""
    out = {}
    for src, gid, disp, fam, meas in GOODS:
        out.setdefault(src, (gid, disp, fam, meas))
    return out


def goods_index():
    """{mod id: (display, family, measure)} -- first spelling wins."""
    out = {}
    for src, gid, disp, fam, meas in GOODS:
        out.setdefault(gid, (disp, fam, meas))
    return out


if __name__ == "__main__":
    problems = []
    seen_src = [g[0] for g in GOODS]
    dupes = sorted({s for s in seen_src if seen_src.count(s) > 1})
    if dupes:
        problems.append("mapped twice (later ignored): " + ", ".join(dupes))
    for src, gid, disp, fam, meas in GOODS:
        if fam not in (STAPLE, FOOD, ANIMAL, CLOTH, BUILD, FUEL, METAL, WEAPON, TRANSPORT,
                       WRITE, MONEY, MEDICINE, LUXURY, PAPERS):
            problems.append(f"{src}: family '{fam}' is not one of the atlas's fourteen")
    if not os.path.isdir(DATA):
        print(f"the data is not unpacked at {DATA}")
    else:
        import csv
        import collections
        have = collections.Counter()
        for f in os.listdir(DATA):
            if f.endswith(".tab"):
                have[f[:-4].rsplit("_", 1)[1]] += 1
        mapped = by_name()
        unmapped = sorted(c for c in have if c not in mapped and c not in EXCLUDE)
        if unmapped:
            problems.append(f"{len(unmapped)} commodities in the data are not mapped: "
                            + ", ".join(unmapped))
        print(f"commodities: {len(mapped)} mapped, {len(have)} in the data, "
              f"{len(EXCLUDE)} excluded, {len(unmapped)} unmapped")
    print(f"goods: {len(goods_index())} distinct, {len(GOODS)} spellings")
    for p in problems:
        print("  PROBLEM " + p)
    print(f"price_table: {len(problems)} problem(s)")
