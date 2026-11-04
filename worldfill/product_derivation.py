"""
Step 44 part 3 (E5 part C): grow the product list from 132 toward 400 **by derivation**.

The plan (PRODUCT_ATLAS_PLAN.md section 10, part C) asks for about 400 product kinds. Part B got
to 132 by hand, each with a year for each of the 17 areas. To reach 400 the same way would mean
writing another 268 x 17 = 4,556 years by hand, which is not a thing this project can honestly
do -- the survey for this step said so before any code was written.

So the **years are computed and the classification is written by hand**. What is written here is
what each product *is*, which family it belongs to, what it is made from, and which technology
makes it possible -- none of which is a date. Every date comes out of a register that already
ships:

  * **the technology atlas** (130 technologies, each with an arrival year for 258 countries) says
    *when*. A product made possible by a technology appears in an area in the earliest year that
    technology reaches any country of that area.
  * **the mineral register** (143,302 USGS sites, 57 minerals) says *where*. A metal can only be
    *made* where the ore is; everywhere else it has to be *brought*. This is the "nature" check
    in section 5 of the plan, and it is measured, not guessed.
  * **a parent product** says *not before*. A processed thing cannot exist before the raw thing
    it is made from, so a child's year is the later of its parent's year and its own technology's
    arrival.

Three source kinds, all declared on the row:

    ("tech",    tech_id)               made[A]  = tech arrival in A
    ("mineral", MINERAL, tech_id)      made[A]  = tech arrival in A, where the ore is
                                       brought[A] = tech arrival in A, where it is not
    ("parent",  parent_id, tech_id)    made[A]  = later of parent's year in A and tech arrival

The country-to-area map comes from `country_areas.py`, which places each of the 258 countries by
the area holding most of its land, using the same box rule the game itself uses
(`ProductAtlas.boxArea`). Two functions below do the arithmetic; the tables are the hand work.
"""

import gzip
import json
import os

import country_areas

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
HIST = os.path.join(ROOT, "eternal", "src", "main", "resources", "data",
                    "eternalengine", "eternal", "history")
TECH_ATLAS = os.path.join(HIST, "technology_atlas.json.gz")
MINERALS = os.path.join(HIST, "minerals.json.gz")

NEVER = None   # an area the product never reaches is simply left out of the maps

TOOL = "metals and tools"          # read as "materials and tools": clay and manure are materials
WRITE = "writing and knowledge"
FOOD2 = "other food and drink"
STAPLE = "staple food"
ANIMAL = "animals and animal goods"
CLOTH = "cloth and clothes"
BUILD = "building"
FUEL = "fuel and light"
WEAPON = "weapons and armour"
MOVE = "transport"
MONEY = "money"
CARE = "medicine and care"
FUN = "luxury, faith and fun"
PAPER = "papers and permits"


# --------------------------------------------------------------------------- 1. from a technology
# Each entry: tech id -> [(product id, name, family, note)]
# Technologies that are infrastructure (paved roads, aqueducts, the internet) are deliberately
# absent: they are works, not products, and step 44 part D has a register of works already.
TECH_PRODUCTS = {
    # communication
    "photography": [("photographs", "Photographs", WRITE, "")],
    "gramophone": [("gramophones", "Gramophones", FUN, "")],
    "colour_tv": [("colour_tv", "Colour television sets", WRITE, "")],
    "post": [("postage_stamps", "Postage stamps", PAPER, "the Penny Black of 1840")],
    # computing
    "computer": [("computers", "Computers", WRITE, "")],
    "personal_computer": [("home_computers", "Home computers", WRITE, "")],
    "mobile_phone": [("mobile_phones", "Mobile phones", WRITE, "")],
    "smartphone": [("smartphones", "Smartphones", WRITE, "")],
    "satnav": [("satnav", "Satellite navigation", WRITE, "")],
    "bank_card": [("bank_cards", "Bank cards", MONEY, "")],
    # crafts
    "pottery": [("pottery", "Pottery", TOOL, "earthenware vessels; the family is read as materials")],
    "porcelain": [("porcelain", "Porcelain", FUN, "a fine ware and a trade good, not a peasant pot")],
    "matches": [("matches", "Matches", FUEL, "")],
    "pencil": [("pencils", "Pencils", WRITE, "")],
    "fountain_pen": [("fountain_pens", "Fountain pens", WRITE, "")],
    "ballpoint_pen": [("ballpoint_pens", "Ballpoint pens", WRITE, "")],
    "fireworks": [("fireworks", "Fireworks", FUN, "")],
    # energy
    "steam_engine": [("steam_engines", "Steam engines", TOOL, "")],
    "solar_panels": [("solar_panels", "Solar panels", FUEL, "")],
    "wind_turbines": [("wind_turbines", "Wind turbines", FUEL, "")],
    # farming
    "canning": [("tinned_food", "Tinned food", FOOD2, "")],
    "fertiliser": [("fertiliser", "Artificial fertiliser", TOOL, "")],
    "tractor": [("tractors", "Tractors", TOOL, "")],
    "combine": [("combine_harvesters", "Combine harvesters", TOOL, "")],
    "watermill": [("watermills", "Water mills", TOOL, "")],
    "windmill": [("windmills", "Windmills", TOOL, "")],
    # the home
    "refrigerator": [("refrigerators", "Refrigerators", TOOL, "")],
    "washing_machine": [("washing_machines", "Washing machines", TOOL, "")],
    "vacuum_cleaner": [("vacuum_cleaners", "Vacuum cleaners", TOOL, "")],
    "microwave": [("microwave_ovens", "Microwave ovens", TOOL, "")],
    "air_conditioning": [("air_conditioners", "Air conditioners", TOOL, "")],
    "electric_fan": [("electric_fans", "Electric fans", TOOL, "")],
    "safety_razor": [("safety_razors", "Safety razors", CARE, "")],
    "typewriter": [("typewriters", "Typewriters", WRITE, "")],
    "cd_player": [("compact_discs", "Compact discs", FUN, "")],
    "video_recorder": [("video_recorders", "Video recorders", FUN, "")],
    "digital_camera": [("digital_cameras", "Digital cameras", WRITE, "")],
    # land
    "coaches": [("carriages", "Horse carriages", MOVE, "")],
    "tram": [("trams", "Electric trams", MOVE, "")],
    "bus": [("buses", "Motor buses", MOVE, "")],
    "lorry": [("lorries", "Lorries", MOVE, "")],
    "motorcycle": [("motorcycles", "Motorcycles", MOVE, "")],
    "electric_car": [("electric_cars", "Electric cars", MOVE, "")],
    "high_speed_rail": [("high_speed_trains", "High-speed trains", MOVE, "")],
    # water
    "steamship": [("steamships", "Steamships", MOVE, "")],
    "motor_ship": [("motor_ships", "Motor ships", MOVE, "")],
    "compass": [("compasses", "Compasses", WRITE, "")],
    # metals
    "cast_iron": [("cast_iron", "Cast iron", TOOL, "")],
    "aluminium": [("aluminium", "Aluminium", TOOL, "")],
    # textiles
    "spinning_wheel": [("spinning_wheels", "Spinning wheels", CLOTH, "")],
    "sewing_machine": [("sewing_machines", "Sewing machines", CLOTH, "")],
    # war
    "matchlock": [("matchlocks", "Matchlock guns", WEAPON, "")],
    "flintlock": [("flintlocks", "Flintlock muskets", WEAPON, "")],
    "rifle": [("rifles", "Breech-loading rifles", WEAPON, "")],
    "machine_gun": [("machine_guns", "Machine guns", WEAPON, "")],
    "cannon": [("cannons", "Cannons", WEAPON, "")],
    "tank": [("tanks", "Tanks", WEAPON, "")],
    "crossbow": [("crossbows", "Crossbows", WEAPON, "")],
    "chariot": [("war_chariots", "War chariots", WEAPON, "")],
    "chain_mail": [("mail_armour", "Mail armour", WEAPON, "")],
    "plate_armour": [("plate_armour", "Plate armour", WEAPON, "")],
    "siege_engines": [("siege_engines", "Siege engines", WEAPON, "")],
    "stirrup": [("stirrups", "Stirrups", MOVE, "")],
    # medicine
    "anaesthesia": [("anaesthetics", "Anaesthetics", CARE, "")],
    "antiseptic": [("antiseptics", "Antiseptics", CARE, "")],
    "child_vaccines": [("child_vaccines", "Vaccines for children", CARE, "")],
    "xray": [("xray_machines", "X-ray machines", CARE, "")],
    "ct_scanner": [("hospital_scanners", "Hospital scanners", CARE, "")],
    # writing
    "pocket_watch": [("pocket_watches", "Pocket watches", WRITE, "")],
    "telescope": [("telescopes", "Telescopes", WRITE, "")],
    "eyeglasses": [("spectacles", "Spectacles", CARE, "")],
    "woodblock": [("woodblock_prints", "Woodblock prints", WRITE, "")],
}


# -------------------------------------------------------------------------- 2. from the ground
# Each row: (product id, name, family, mineral, technology that first lets people use it)
# A mineral is MADE where the ore is and BROUGHT where it is not, both from the year the working
# technology arrives -- because a smith who knows lead will import lead if he has no lead ore,
# which is precisely how tin reached Mesopotamia and copper reached Egypt.
#
# A technology of **None** means nothing gates it. Granite, flint and peat are older than any
# technology in the atlas, so where the ground holds them they were always there; the atlas has
# no "stone working" row, and inventing one to satisfy the table would be the wrong fix.
MINERAL_PRODUCTS = [
    ("clay", "Clay", TOOL, "CLAY", "pottery"),
    ("ochre", "Ochre and earth pigments", TOOL, "OCHRE", "pottery"),
    ("flint_chert", "Flint and chert", TOOL, "FLINT", None),
    ("granite", "Granite", BUILD, "GRANITE", None),
    ("marble", "Marble", BUILD, "MARBLE", None),
    ("sandstone", "Sandstone", BUILD, "SANDSTONE", None),
    ("slate", "Slate", BUILD, "SLATE", None),
    ("gypsum", "Gypsum and plaster", BUILD, "GYPSUM", "pottery"),
    ("mica", "Mica", TOOL, "MICA", "glass"),
    ("graphite", "Graphite", TOOL, "GRAPHITE", "pencil"),
    ("lead", "Lead", TOOL, "LEAD", "bronze"),
    ("silver", "Silver", MONEY, "SILVER", "bronze"),
    ("zinc", "Zinc", TOOL, "ZINC", "cast_iron"),
    ("mercury", "Mercury", CARE, "MERCURY", "aluminium"),
    ("antimony", "Antimony", CARE, "ANTIMONY", "bronze"),
    ("arsenic", "Arsenic", CARE, "ARSENIC", "bronze"),
    ("potash", "Potash", TOOL, "POTASH", "glass"),
    ("bauxite", "Bauxite", TOOL, "BAUXITE", "aluminium"),
    ("chromium", "Chromium", TOOL, "CHROMIUM", "electric_steel"),
    ("manganese", "Manganese", TOOL, "MANGANESE", "bessemer"),
    ("nickel", "Nickel", TOOL, "NICKEL", "electric_steel"),
    ("tungsten", "Tungsten", TOOL, "TUNGSTEN", "electric_steel"),
    ("molybdenum", "Molybdenum", TOOL, "MOLYBDENUM", "electric_steel"),
    ("vanadium", "Vanadium", TOOL, "VANADIUM", "bessemer"),
    ("titanium", "Titanium", TOOL, "TITANIUM", "oxygen_steel"),
    ("cobalt", "Cobalt", TOOL, "COBALT", "electric_steel"),
    ("platinum", "Platinum", FUN, "PLATINUM", "aluminium"),
    ("uranium", "Uranium", FUEL, "URANIUM", "nuclear_power"),
    ("lithium", "Lithium", TOOL, "LITHIUM", "computer"),
    ("phosphate", "Phosphate rock", TOOL, "PHOSPHATE", "fertiliser"),
    ("asbestos", "Asbestos", BUILD, "ASBESTOS", "cement"),
    ("talc", "Talc", CARE, "TALC", "pottery"),
    ("barite", "Barite", TOOL, "BARITE", "bessemer"),
    ("fluorite", "Fluorite", TOOL, "FLUORITE", "bessemer"),
    ("pumice", "Pumice", TOOL, "PUMICE", "pottery"),
]


# **What is deliberately missing from this list: fruit and vegetables.** The plan names a source
# for them -- Khoury et al. 2016, 151 food crops and the 23 regions they originated in -- but
# that register has never been built, so there is nothing to derive a mango's arrival in Europe
# from. A fruit given a universal parent and no technology comes out "always, everywhere", which
# puts mangoes and aubergines in prehistoric Norway. They stay out until the register exists,
# and the same is true of ship types (a junk is Chinese and a galley is Mediterranean, and no
# register here knows that) and of institutions like dispensaries, which are not products at all.

# ------------------------------------------------------------------------- 3. from a parent
# A child cannot exist before the thing it is made from, and not before the technology that
# makes it. Each row: (id, name, family, parent id, technology or None, staple, needs)
CHILD_PRODUCTS = [
    # ---- staple food: things made of grain, and the grains the atlas named only in bunches
    ("oats", "Oats", STAPLE, "wheat", None, "food", ["farm"]),
    ("rye", "Rye", STAPLE, "wheat", None, "food", ["farm"]),
    ("sorghum", "Sorghum", STAPLE, "millet", None, "food", ["farm"]),
    ("buckwheat", "Buckwheat", STAPLE, "millet", None, "food", ["farm"]),
    ("plantain", "Plantains and bananas", STAPLE, "roots", None, "food", ["farm"]),
    ("breadfruit", "Breadfruit", STAPLE, "roots", None, "food", ["farm"]),
    ("sago", "Sago palm starch", STAPLE, "roots", None, "food", []),
    ("acorns", "Acorns and nuts", STAPLE, "wild_food", None, "food", []),
    ("flour", "Flour and meal", STAPLE, "wheat", "watermill", None, ["farm"]),
    ("semolina", "Semolina and broken wheat", STAPLE, "wheat", None, None, ["farm"]),
    ("rice_flour", "Rice flour", STAPLE, "rice", None, None, ["farm"]),
    ("pasta", "Dried pasta and noodles", STAPLE, "flour", None, None, ["town"]),
    ("porridge", "Porridge and gruel", STAPLE, "millet", None, "food", []),
    ("oilseeds", "Oilseeds (sesame, mustard, linseed)", STAPLE, "wheat", None, None, ["farm"]),
    ("groundnut", "Groundnuts", STAPLE, "oilseeds", None, None, ["farm"]),
    ("coconut", "Coconuts", FOOD2, "roots", None, None, []),
    ("grapes", "Grapes", FOOD2, "wine", None, None, ["farm"]),
    ("melons", "Melons and gourds", FOOD2, "roots", None, None, ["farm"]),
    ("greens", "Leafy greens and herbs", FOOD2, "wild_food", None, None, ["farm"]),
    ("onions", "Onions and garlic", FOOD2, "wild_food", None, None, ["farm"]),
    ("cucumbers", "Cucumbers and gourds", FOOD2, "roots", None, None, ["farm"]),
    ("carrots", "Carrots and roots", FOOD2, "roots", None, None, ["farm"]),
    # ---- other food and drink
    ("candy", "Boiled sweets", FOOD2, "sugar", None, None, ["town"]),
    ("vinegar", "Vinegar", FOOD2, "wine", None, None, []),
    ("pickles", "Pickles", FOOD2, "salt", None, None, []),
    ("dried_fish", "Dried and salted fish", FOOD2, "fish", None, None, []),
    ("salt_meat", "Salt meat", FOOD2, "meat", None, None, []),
    ("cheese", "Cheese", FOOD2, "dairy", None, None, ["herd"]),
    ("ghee", "Clarified butter (ghee)", FOOD2, "dairy", None, None, ["herd"]),
    ("yoghurt", "Yoghurt and curds", FOOD2, "dairy", None, None, ["herd"]),
    ("spirits", "Distilled spirits", FOOD2, "beer", None, None, ["town"]),
    ("arrack", "Arrack and palm spirits", FOOD2, "toddy", None, None, []),
    ("chocolate", "Chocolate", FOOD2, "cacao", None, None, ["town"]),
    ("coffee_houses", "Coffee, ground and roasted", FOOD2, "coffee", None, None, ["town"]),
    ("opium", "Opium", CARE, "wild_food", None, None, ["farm"]),
    ("pepper", "Black pepper", FOOD2, "spices", None, None, ["farm"]),
    ("cardamom", "Cardamom", FOOD2, "spices", None, None, ["farm"]),
    ("cinnamon", "Cinnamon and cassia", FOOD2, "spices", None, None, []),
    ("cloves", "Cloves", FOOD2, "spices", None, None, []),
    ("nutmeg", "Nutmeg and mace", FOOD2, "spices", None, None, []),
    ("turmeric", "Turmeric", FOOD2, "spices", None, None, ["farm"]),
    ("ginger", "Ginger", FOOD2, "spices", None, None, ["farm"]),
    ("cumin", "Cumin and coriander", FOOD2, "spices", None, None, ["farm"]),
    ("saffron", "Saffron", FOOD2, "spices", None, None, ["farm"]),
    ("fenugreek", "Fenugreek", FOOD2, "spices", None, None, ["farm"]),
    ("asafoetida", "Asafoetida", FOOD2, "spices", None, None, []),
    ("vanilla", "Vanilla", FOOD2, "cacao", None, None, ["farm"]),
    # ---- animals
    ("pigs", "Pigs", ANIMAL, "cattle", None, None, ["herd"]),
    ("poultry", "Poultry", ANIMAL, "eggs", None, None, ["settled"]),
    ("buffalo", "Water buffalo", ANIMAL, "cattle", None, None, ["herd"]),
    ("donkeys", "Donkeys and mules", ANIMAL, "horses", None, None, ["herd"]),
    ("reindeer", "Reindeer", ANIMAL, "sheep_goats", None, None, ["herd"]),
    ("dogs", "Dogs", ANIMAL, "wild_food", None, None, []),
    ("cats", "Cats", ANIMAL, "wild_food", None, None, ["settled"]),
    ("beeswax", "Beeswax", ANIMAL, "honey", None, None, []),
    ("bone", "Bone, horn and antler", TOOL, "cattle", None, None, []),
    ("feathers", "Feathers and down", CLOTH, "poultry", None, None, []),
    ("bristles", "Bristles and hair", TOOL, "pigs", None, None, []),
    ("gut", "Gut and sinew", TOOL, "cattle", None, None, []),
    ("glue", "Glue and size", TOOL, "gut", None, None, ["town"]),
    ("manure", "Manure", TOOL, "cattle", None, None, ["farm"]),
    ("dung_fuel", "Dung fuel", FUEL, "dung_cakes", None, "fuel", []),
    ("peat", "Peat", FUEL, "firewood", None, "fuel", []),
    # ---- cloth
    ("jute", "Jute", CLOTH, "hemp", None, None, ["farm"]),
    ("coir", "Coir", CLOTH, "coconut", None, None, []),
    ("ramie", "Ramie and nettle cloth", CLOTH, "hemp", None, None, ["farm"]),
    ("sisal", "Sisal and agave fibre", CLOTH, "hemp", None, None, ["farm"]),
    ("kapok", "Kapok", CLOTH, "cotton", None, None, []),
    ("felt", "Felt", CLOTH, "wool", None, None, ["herd"]),
    ("thread", "Thread and yarn", CLOTH, "cotton", "spinning_wheel", None, []),
    ("rope", "Rope and cordage", CLOTH, "hemp", None, None, []),
    ("sacking", "Sacking and canvas", CLOTH, "jute", None, None, []),
    ("carpets", "Carpets and rugs", CLOTH, "wool", None, None, ["town"]),
    ("blankets", "Blankets", CLOTH, "wool", None, None, []),
    ("tents", "Tents", CLOTH, "felt", None, None, ["herd"]),
    ("sails", "Sails", MOVE, "linen", None, None, ["town"]),
    ("footwear", "Footwear", CLOTH, "leather", None, None, ["town"]),
    ("hats", "Hats and caps", CLOTH, "felt", None, None, ["town"]),
    ("needles", "Needles", TOOL, "iron", None, None, ["town"]),
    ("buttons", "Buttons and fastenings", CLOTH, "bone", None, None, ["town"]),
    ("indigo_dye", "Indigo", CLOTH, "dyes", None, None, ["farm"]),
    ("madder_dye", "Madder", CLOTH, "dyes", None, None, ["farm"]),
    ("alum", "Alum (a mordant)", CLOTH, "dyes", None, None, []),
    ("kermes", "Kermes and cochineal", CLOTH, "dyes", None, None, []),
    ("lac", "Lac", CLOTH, "dyes", None, None, []),
    # ---- building
    ("thatch", "Thatch", BUILD, "timber", None, None, []),
    ("wattle", "Wattle and daub", BUILD, "mud_brick", None, None, ["settled"]),
    ("dressed_stone", "Dressed stone", BUILD, "stone", None, None, ["town"]),
    ("roof_tiles", "Roof tiles", BUILD, "pottery", None, None, ["town"]),
    ("terracotta", "Terracotta", BUILD, "pottery", None, None, ["town"]),
    ("plaster", "Plaster and whitewash", BUILD, "lime_mortar", None, None, ["town"]),
    ("mosaic", "Mosaic and inlay", BUILD, "dressed_stone", None, None, ["town"]),
    ("window_glass", "Window glass", BUILD, "glass", None, None, ["town"]),
    ("mirrors", "Mirrors", FUN, "glass", None, None, ["town"]),
    ("locks", "Locks and keys", TOOL, "iron", None, None, ["town"]),
    ("nails", "Nails and fastenings", TOOL, "iron", None, None, ["town"]),
    ("hinges", "Hinges and fittings", TOOL, "iron", None, None, ["town"]),
    ("wells", "Wells and cisterns", BUILD, "dressed_stone", None, None, ["settled"]),
    ("drains", "Drains and sewers", BUILD, "pottery", None, None, ["town"]),
    ("ovens", "Ovens and kilns", BUILD, "pottery", None, None, ["settled"]),
    ("bitumen", "Bitumen and asphalt", BUILD, "petrol", None, None, []),
    # ---- fuel and light
    ("tallow", "Tallow", FUEL, "cattle", None, None, ["herd"]),
    ("tallow_candles", "Tallow candles", FUEL, "tallow", None, "light", []),
    ("rushlights", "Rush lights", FUEL, "cooking_oil", None, "light", []),
    ("lanterns", "Lanterns", FUEL, "oil_lamp", None, None, ["town"]),
    ("flint_steel", "Flint and steel", FUEL, "iron", None, None, []),
    ("coke", "Coke", FUEL, "coal", "ironworks", None, ["town"]),
    ("briquettes", "Briquettes", FUEL, "charcoal", None, None, ["town"]),
    ("batteries", "Batteries", FUEL, "electricity", None, None, ["town"]),
    ("light_bulbs", "Electric light bulbs", FUEL, "electricity", None, "light", ["town"]),
    ("biogas", "Biogas", FUEL, "manure", None, None, ["town"]),
    ("street_light", "Electric street light", FUEL, "electricity", None, None, ["town"]),
    # ---- metals and tools
    ("brass", "Brass", TOOL, "copper", None, None, ["town"]),
    ("pewter", "Pewter", TOOL, "tin", None, None, ["town"]),
    ("bell_metal", "Bell metal", TOOL, "bronze", None, None, ["town"]),
    ("wrought_iron", "Wrought iron", TOOL, "iron", None, None, ["town"]),
    ("pig_iron", "Pig iron", TOOL, "cast_iron", None, None, ["town"]),
    ("wootz", "Crucible steel (wootz)", TOOL, "steel", None, None, ["town"]),
    ("gilding", "Gilding", FUN, "gold", None, None, ["town"]),
    ("solder", "Solder", TOOL, "tin", None, None, ["town"]),
    ("wire", "Wire", TOOL, "iron", None, None, ["town"]),
    ("chain", "Chain", TOOL, "iron", None, None, ["town"]),
    ("knives", "Knives and blades", TOOL, "iron_tools", None, None, ["town"]),
    ("sickles", "Sickles and scythes", TOOL, "iron_tools", None, None, ["farm"]),
    ("hoes", "Hoes and spades", TOOL, "iron_tools", None, None, ["farm"]),
    ("axes", "Axes and adzes", TOOL, "iron_tools", None, None, []),
    ("hammers", "Hammers and mallets", TOOL, "iron_tools", None, None, ["town"]),
    ("saws", "Saws", TOOL, "iron_tools", None, None, ["town"]),
    ("chisels", "Chisels and planes", TOOL, "iron_tools", None, None, ["town"]),
    ("files", "Files and rasps", TOOL, "iron_tools", None, None, ["town"]),
    ("anvils", "Anvils", TOOL, "iron", None, None, ["town"]),
    ("bellows", "Bellows", TOOL, "leather", None, None, ["town"]),
    ("querns", "Querns and millstones", TOOL, "stone_tools", None, None, ["farm"]),
    ("mortars", "Mortars and pestles", TOOL, "stone_tools", None, None, []),
    ("whetstones", "Whetstones", TOOL, "stone_tools", None, None, []),
    ("scissors", "Scissors and shears", TOOL, "iron_tools", None, None, ["town"]),
    ("tongs", "Tongs and pincers", TOOL, "iron", None, None, ["town"]),
    ("balances", "Balances and weights", TOOL, "bronze", None, None, ["town"]),
    ("clocks", "Mechanical clocks", WRITE, "brass", "clock_tower", None, ["town"]),
    ("sundials", "Sundials", WRITE, "bronze", None, None, ["town"]),
    ("hourglasses", "Hourglasses and water clocks", WRITE, "glass", None, None, ["town"]),
    ("astrolabes", "Astrolabes", WRITE, "brass", None, None, ["town"]),
    # Step 47 E7: the microscope was derived from `glass` with no technology of its own, so it
    # inherited glass's date and became 2500 BC in West Asia. It is an optical instrument and
    # belongs to the same lens workshops as the telescope; the finer 1590 date is in
    # worldfill/tool_table.py, which overrides this row rather than trusting it.
    ("microscopes", "Microscopes", WRITE, "glass", "telescope", None, ["town"]),
    ("barometers", "Barometers and thermometers", WRITE, "glass", None, None, ["town"]),
    ("abacus", "Counting boards and the abacus", WRITE, "coins", None, None, ["town"]),
    ("baskets", "Baskets", TOOL, "hemp", None, None, []),
    ("pots_metal", "Metal cooking pots", TOOL, "copper", None, None, ["town"]),
    # ---- weapons
    ("spears", "Spears and javelins", WEAPON, "bows", None, None, []),
    ("clubs", "Clubs and maces", WEAPON, "timber", None, None, []),
    ("daggers", "Daggers and knives", WEAPON, "copper", None, None, ["town"]),
    ("swords", "Swords", WEAPON, "bronze_weapons", None, None, ["town"]),
    ("shields", "Shields", WEAPON, "leather", None, None, []),
    ("helmets", "Helmets", WEAPON, "bronze_weapons", None, None, ["town"]),
    ("slings", "Slings", WEAPON, "hemp", None, None, []),
    ("pikes", "Pikes and halberds", WEAPON, "iron_weapons", None, None, ["town"]),
    ("lances", "Lances", WEAPON, "iron_weapons", None, None, ["herd"]),
    ("horseshoes", "Horseshoes", MOVE, "iron", None, None, ["town"]),
    ("harpoons", "Harpoons and fish-hooks", TOOL, "bone", None, None, []),
    ("nets", "Nets and traps", TOOL, "hemp", None, None, []),
    ("greek_fire", "Greek fire and incendiaries", WEAPON, "sulphur", None, None, ["town"]),
    ("rockets", "War rockets", WEAPON, "gunpowder", None, None, ["town"]),
    ("bayonets", "Bayonets", WEAPON, "firearms", None, None, ["town"]),
    ("cartridges", "Cartridges", WEAPON, "firearms", None, None, ["town"]),
    ("artillery", "Artillery shells", WEAPON, "cannons", None, None, ["town"]),
    # ---- transport
    ("sledges", "Sledges", MOVE, "timber", None, None, []),
    ("skis", "Skis and snowshoes", MOVE, "timber", None, None, []),
    ("litters", "Litters and palanquins", MOVE, "timber", None, None, ["town"]),
    ("wheelbarrows", "Wheelbarrows", MOVE, "carts", None, None, ["town"]),
    ("wagons", "Wagons", MOVE, "carts", None, None, ["farm"]),
    ("carriages_city", "Hackney carriages", MOVE, "carriages", None, None, ["town"]),
    ("rickshaws", "Rickshaws", MOVE, "carts", None, None, ["town"]),
    ("rafts", "Rafts and reed boats", MOVE, "boats", None, None, []),
    ("canoes", "Dugout canoes", MOVE, "boats", None, None, []),
    ("oars", "Oars and paddles", MOVE, "timber", None, None, []),
    ("anchors", "Anchors", MOVE, "iron", None, None, ["town"]),
    ("rigging", "Rigging and masts", MOVE, "rope", None, None, ["town"]),
    ("bridles", "Bridles and bits", MOVE, "leather", None, None, ["herd"]),
    ("yokes", "Yokes", MOVE, "timber", None, None, ["farm"]),
    ("lighthouses", "Lighthouses", MOVE, "dressed_stone", None, None, ["town"]),
    ("bridges", "Bridges", MOVE, "dressed_stone", None, None, ["town"]),
    ("caravanserais", "Caravanserais and inns", MOVE, "mud_brick", None, None, ["town"]),
    ("balloons", "Balloons and airships", MOVE, "aeroplane", None, None, ["town"]),
    ("helicopters", "Helicopters", MOVE, "aeroplane", None, None, ["town"]),
    # ---- writing and knowledge
    ("seals", "Seals and signets", WRITE, "pottery", None, None, ["town"]),
    ("quipu", "Quipu and tally cords", WRITE, "hemp", None, None, ["settled"]),
    ("tally_sticks", "Tally sticks", WRITE, "timber", None, None, ["town"]),
    ("envelopes", "Envelopes", WRITE, "paper", None, None, ["town"]),
    ("quills", "Quills and brushes", WRITE, "feathers", None, None, ["town"]),
    ("scrolls", "Scrolls", WRITE, "parchment", None, None, ["town"]),
    ("codices", "Bound codices", WRITE, "parchment", None, None, ["town"]),
    ("ledgers", "Ledgers and account books", WRITE, "paper", None, None, ["town"]),
    ("almanacs", "Almanacs and calendars", WRITE, "paper", None, None, ["town"]),
    ("dictionaries", "Dictionaries and encyclopaedias", WRITE, "books", None, None, ["town"]),
    ("pamphlets", "Pamphlets and broadsides", WRITE, "newspaper", None, None, ["town"]),
    ("charts", "Sea charts and atlases", WRITE, "maps", None, None, ["town"]),
    ("globes", "Globes", WRITE, "maps", None, None, ["town"]),
    ("lithography", "Lithographs", WRITE, "books", "printing_press", None, ["town"]),
    ("carbon_paper", "Carbon paper", WRITE, "typewriters", None, None, ["town"]),
    ("slide_rules", "Slide rules", WRITE, "brass", None, None, ["town"]),
    ("calculators", "Mechanical calculators", WRITE, "brass", None, None, ["town"]),
    ("film", "Photographic film", WRITE, "photographs", None, None, ["town"]),
    ("records", "Gramophone records", FUN, "gramophones", None, None, ["town"]),
    ("libraries", "Libraries and archives", WRITE, "books", None, None, ["town"]),
    ("schools", "Schools", WRITE, "books", None, None, ["town"]),
    ("observatories", "Observatories", WRITE, "telescopes", None, None, ["town"]),
    ("chalk", "Chalk and blackboards", WRITE, "gypsum", None, None, ["town"]),
    # ---- money
    ("cowries", "Cowrie shells", MONEY, "pearls", None, None, []),
    ("hack_silver", "Weighed silver (hacksilver)", MONEY, "silver", None, None, []),
    ("ingots", "Ingots", MONEY, "bronze", None, None, ["town"]),
    ("milled_coins", "Milled machine-struck coins", MONEY, "coins", "steam_engine", None, ["town"]),
    ("banknotes", "Bank notes", MONEY, "paper_money", None, None, ["town"]),
    ("cheques", "Cheques", MONEY, "banknotes", None, None, ["town"]),
    ("bills_exchange", "Bills of exchange", MONEY, "paper_money", None, None, ["town"]),
    ("hundis", "Hundis", MONEY, "bills_exchange", None, None, ["town"]),
    ("money_orders", "Money orders", MONEY, "postage_stamps", None, None, ["town"]),
    ("bonds", "Government bonds", MONEY, "paper_money", None, None, ["town"]),
    ("shares", "Shares in a company", MONEY, "bonds", None, None, ["town"]),
    ("insurance", "Insurance policies", MONEY, "paper_money", None, None, ["town"]),
    ("pawnbroking", "Pawn tickets", MONEY, "coins", None, None, ["town"]),
    ("touchstones", "Touchstones and assay", MONEY, "gold", None, None, ["town"]),
    ("safes", "Strongboxes and safes", MONEY, "iron", None, None, ["town"]),
    ("mints", "Mints", MONEY, "coins", None, None, ["town"]),
    # ---- medicine and care
    ("mineral_drugs", "Mineral drugs", CARE, "arsenic", None, None, ["town"]),
    ("syringes", "Syringes", CARE, "glass", None, None, ["town"]),
    ("bandages", "Bandages and lint", CARE, "linen", None, None, []),
    ("splints", "Splints", CARE, "timber", None, None, []),
    ("sutures", "Sutures and forceps", CARE, "iron_tools", None, None, ["town"]),
    ("scalpels", "Surgical instruments", CARE, "steel", None, None, ["town"]),
    ("dentures", "False teeth", CARE, "bone", None, None, ["town"]),
    ("prosthetics", "Prosthetic limbs", CARE, "leather", None, None, ["town"]),
    ("hearing_horns", "Hearing horns", CARE, "bone", None, None, ["town"]),
    ("crutches", "Crutches", CARE, "timber", None, None, []),
    ("tooth_powder", "Tooth powder", CARE, "salt", None, None, ["town"]),
    ("kohl", "Kohl and eye paint", CARE, "antimony", None, None, ["town"]),
    ("henna", "Henna", CARE, "ochre", None, None, []),
    ("contraceptives", "Contraceptives", CARE, "linen", None, None, ["town"]),
    ("hospitals", "Hospitals", CARE, "dressed_stone", None, None, ["town"]),
    ("blood_transfusion", "Blood transfusion", CARE, "syringes", None, None, ["town"]),
    ("insulin", "Insulin", CARE, "syringes", None, None, ["town"]),
    ("sulphonamides", "Sulpha drugs", CARE, "penicillin", None, None, ["town"]),
    # ---- luxury, faith and fun
    ("jewellery", "Jewellery", FUN, "gold", None, None, ["town"]),
    ("beads", "Beads", FUN, "stone_tools", None, None, []),
    ("bangles", "Bangles and anklets", FUN, "glass", None, None, ["town"]),
    ("amulets", "Amulets and talismans", FUN, "bone", None, None, []),
    ("idols", "Images for worship", FUN, "dressed_stone", None, None, ["settled"]),
    ("icons", "Painted icons", FUN, "woodblock_prints", None, None, ["town"]),
    ("censers", "Censers and lamps for worship", FUN, "brass", None, None, ["town"]),
    ("bells", "Bells", FUN, "bell_metal", None, None, ["town"]),
    ("drums", "Drums", FUN, "leather", None, None, []),
    ("flutes", "Flutes and pipes", FUN, "bone", None, None, []),
    ("stringed", "Lutes and fiddles", FUN, "gut", None, None, ["town"]),
    ("harps", "Harps and lyres", FUN, "gut", None, None, ["town"]),
    ("trumpets", "Trumpets and horns", FUN, "brass", None, None, ["town"]),
    ("cosmetics", "Cosmetics", FUN, "kohl", None, None, ["town"]),
    ("combs", "Combs", FUN, "bone", None, None, []),
    ("wigs", "Wigs and hairpieces", FUN, "feathers", None, None, ["town"]),
    ("dice", "Dice", FUN, "bone", None, None, []),
    ("backgammon", "Backgammon and dice games", FUN, "dice", None, None, ["town"]),
    ("kites", "Kites", FUN, "paper", None, None, ["town"]),
    ("dolls", "Dolls and toys", FUN, "clay", None, None, []),
    ("puppets", "Puppets and masks", FUN, "leather", None, None, ["town"]),
    ("gardens", "Gardens and parks", FUN, "wheat", "irrigation", None, ["town"]),
    ("bathhouses", "Baths and bathhouses", FUN, "dressed_stone", None, None, ["town"]),
    ("theatre", "Plays and theatre", FUN, "puppets", None, None, ["town"]),
    ("music_boxes", "Music boxes", FUN, "bells", None, None, ["town"]),
    ("lanterns_festive", "Festival lanterns", FUN, "paper", None, None, ["town"]),
    ("perfume_oils", "Perfumed oils", FUN, "cooking_oil", None, None, ["town"]),
    ("sandalwood", "Sandalwood", FUN, "incense", None, None, []),
    ("arecanut", "Areca nut", FUN, "betel", None, None, ["farm"]),
    # ---- papers and permits
    ("receipts", "Receipts", PAPER, "paper", None, None, ["town"]),
    ("invoices", "Invoices and bills of lading", PAPER, "paper", None, None, ["town"]),
    ("contracts", "Contracts", PAPER, "paper", None, None, ["town"]),
    ("wills", "Wills", PAPER, "paper", None, None, ["town"]),
    ("certificates", "Birth and death certificates", PAPER, "ledgers", None, None, ["town"]),
    ("licences_trade", "Trade licences", PAPER, "land_deeds", None, None, ["town"]),
    ("visas", "Visas", PAPER, "passport", None, None, ["town"]),
    ("identity_cards", "Identity cards", PAPER, "certificates", None, None, ["town"]),
    ("driving_licences", "Driving licences", PAPER, "car", None, None, ["town"]),
    ("tax_receipts", "Tax receipts", PAPER, "land_deeds", None, None, ["town"]),
    ("court_orders", "Court orders and summons", PAPER, "land_deeds", None, None, ["town"]),
    ("patents", "Patents", PAPER, "books", "printing_press", None, ["town"]),
    ("title_deeds", "Title deeds", PAPER, "land_deeds", None, None, ["town"]),
    ("survey_maps", "Cadastral survey maps", PAPER, "maps", None, None, ["town"]),
    ("health_certificates", "Health certificates", PAPER, "certificates", None, None, ["town"]),
    ("census_returns", "Census returns", PAPER, "ledgers", None, None, ["town"]),
    ("insurance_papers", "Marine insurance papers", PAPER, "insurance", None, None, ["town"]),
    ("share_certificates", "Share certificates", PAPER, "shares", None, None, ["town"]),
    ("telegrams", "Telegrams", PAPER, "telegraph", None, None, ["town"]),
    ("postal_orders", "Postal orders", PAPER, "money_orders", None, None, ["town"]),
]


# ---------------------------------------------------------------------------- where, by nature
# A handful of products are not universal, and no register in the mod can say where they are --
# the mineral register is 75% United States (see the note in build_products_c.py) and the crop
# register the plan names was never built. Rather than let them fall out "always, everywhere" --
# which put peat in Tahiti and Andean amaranth in Rome -- their range is written as plain
# physical geography. These are statements about where a bog, a wild cat or a ski run is, and
# not about dates; the row says so.
AREA_LIMITS = {
    # peat bogs need cold, waterlogged ground
    "peat": ["EUR", "EEU", "NNA", "CAS", "SEA", "AUS"],
    # snow
    "skis": ["EUR", "EEU", "NNA", "CAS", "EAS"],
    # the opium poppy is Old World; it reached the Americas with Columbus and later
    "opium": ["EUR", "EEU", "WAS", "NAF", "CAS", "SAS", "EAS", "SEA", "EAF"],
    # the domestic cat came from the Old World: no cats in pre-Columbian America or old Tahiti
    "cats": ["EUR", "EEU", "WAS", "NAF", "WAF", "MSA", "EAF", "CAS", "SAS", "EAS", "SEA"],
    # buckwheat came out of Central Asia and spread across Eurasia, reaching Europe late
    "buckwheat": ["CAS", "EAS", "EEU", "EUR", "SAS"],
}


# ------------------------------------------------------------------------------ the arithmetic
_cache = {}


def tech_arrivals():
    """{tech id: {area: earliest arrival year}}, from the technology atlas."""
    if "tech" in _cache:
        return _cache["tech"]
    areas, codes, _names = country_areas.country_areas()
    d = json.loads(gzip.open(TECH_ATLAS).read())
    out = {}
    for t in d["techs"]:
        per = {}
        for i, y in enumerate(t.get("arrive") or []):
            if y is None or i >= len(codes):
                continue
            a = areas.get(codes[i])
            if a is None:
                continue
            if a not in per or y < per[a]:
                per[a] = y
        out[t["id"]] = per
    _cache["tech"] = out
    return out


def mineral_areas():
    """{mineral: set of areas whose land holds it}."""
    if "min" in _cache:
        return _cache["min"]
    d = json.loads(gzip.open(MINERALS).read())
    names = d["minerals"]
    out = {m: set() for m in names}
    for s in d["sites"]:
        lat, lon = s[0], s[1]
        if lat is None or lon is None:
            continue
        a = country_areas.box_area(lat, lon)
        for mi in s[2]:
            if 0 <= mi < len(names):
                out[names[mi]].add(a)
    _cache["min"] = out
    return out


if __name__ == "__main__":
    ta = tech_arrivals()
    ma = mineral_areas()
    problems = []
    ids = []
    for tid, rows in TECH_PRODUCTS.items():
        if tid not in ta:
            problems.append(f"tech '{tid}' is not in the technology atlas")
        for pid, name, fam, _note in rows:
            ids.append(pid)
    for pid, name, fam, mineral, tech in MINERAL_PRODUCTS:
        ids.append(pid)
        if mineral not in ma:
            problems.append(f"'{pid}': mineral '{mineral}' is not in the register")
        if tech is not None and tech not in ta:
            problems.append(f"'{pid}': tech '{tech}' is not in the technology atlas")
    for row in CHILD_PRODUCTS:
        ids.append(row[0])
        if row[4] is not None and row[4] not in ta:
            problems.append(f"'{row[0]}': tech '{row[4]}' is not in the technology atlas")
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        problems.append(f"ids used twice: {', '.join(dupes)}")
    fams = {row[2] for rows in TECH_PRODUCTS.values() for row in rows}
    fams |= {row[2] for row in MINERAL_PRODUCTS}
    fams |= {row[2] for row in CHILD_PRODUCTS}
    bad = sorted(f for f in fams if f not in (TOOL, WRITE, FOOD2, STAPLE, ANIMAL, CLOTH, BUILD,
                                              FUEL, WEAPON, MOVE, MONEY, CARE, FUN, PAPER))
    if bad:
        problems.append(f"families that are not one of the fourteen: {bad}")
    print("tech products:    %d from %d technologies" %
          (sum(len(v) for v in TECH_PRODUCTS.values()), len(TECH_PRODUCTS)))
    print("mineral products: %d" % len(MINERAL_PRODUCTS))
    print("child products:   %d" % len(CHILD_PRODUCTS))
    print("new products:     %d" % len(ids))
    for p in problems:
        print("  PROBLEM " + p)
    print("product_derivation: %d problem(s)" % len(problems))
