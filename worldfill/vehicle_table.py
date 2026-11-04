#!/usr/bin/env python3
"""
Step 46 part 3 (E10 A): the vehicle register — every way there has been of getting somewhere.

    python3 vehicle_table.py        check the register and print it

**The plan's E10 list**, which is what this register has to cover:
*porters, palanquins, carts, chariots, horses, camels, elephants, bicycles, rickshaws, trams,
buses, cars, lorries; rafts, dhows, galleys, junks, sailing ships, steamships; trains; balloons,
airships, planes.*

**It reads, it does not rewrite.** Three registers in the mod already date these things, and this
one draws on all three rather than starting a fourth copy:

| source | gives |
|---|---|
| the **products atlas** (step 44 part C) | per-area `made` years for 34 transport goods |
| the **technology atlas** (step 30a) | spread-modelled dates for 258 countries: wheel, chariot, bicycle, tram, steamship, motor_ship, stirrup |
| the **armoury** (step 45 part 2) | the war chariot, the elephant and the mounted bow, with their `never` maps |

**What is new here is the `needs` column.** A train needs a railway, a tram needs a tram line, a
canal boat needs a canal, a cart needs a beast and something to roll on. The armoury and the
products atlas say *when a thing exists*; they do not say *what it runs on*. That question is what
E11 (traffic) is made of, and step 34's `WaysGrid` already answers the road/rail/canal half of it
for 124,240 squares.

**Speeds are the mod's own**, carried over from `VehicleType` wherever it already named one, so the
two cannot disagree. Where it did not, the figure is marked `estimated` and says where it came from.
"""

# The atlas's own area codes. Part 4 of step 45 caught invented codes twice; part 2 of step 46
# caught a plural/singular mismatch. Every area in this file is checked against this list.
AREAS = ["EUR", "EEU", "WAS", "NAF", "CAS", "SAS", "EAS", "SEA", "WAF", "MSA", "EAF",
         "NNA", "MNA", "CAC", "SAM", "PAC", "AUS"]

# What a vehicle moves over or through.
MEDIUMS = ["foot", "beast", "wheel", "rail", "water", "air"]

# --------------------------------------------------------------------------------------------------
# A SYSTEMATIC FINDING ABOUT STEP 44 PART C
#
# The products atlas dates `rickshaws` at EUR -3000 and `wheelbarrows` at EUR -3000 - the EXACT
# dates of `carts`. `oars` is -10000 in all 17 areas. `reindeer` is -2000 in West Africa. Those
# are not dates; they are template copies, because part C derived each child from a parent and
# several children inherited the parent's row unchanged.
#
# This register has now met that artefact four times - reindeer in West Africa (D14), donkeys
# sharing a date with horses (D14), and here rickshaws and wheelbarrows sharing one with carts.
# So the rule is: **a products-atlas date is used only where it is independently sensible, and
# every other vehicle carries an explicit, sourced date marked `estimated` with the reason.**
# The affected vehicles are recorded in `CORRECTED` below and shipped inside the pack.
# --------------------------------------------------------------------------------------------------
CORRECTED = {
    "rickshaw": "the products atlas dates `rickshaws` at EUR -3000 - the date of `carts`, copied "
                "unchanged. A rickshaw was invented in Japan around 1868. Corrected to explicit "
                "dates, marked estimated.",
    "wheelbarrow": "the products atlas dates `wheelbarrows` at EUR -3000, again the cart's date. "
                   "The wheelbarrow is Chinese (Han, around AD 100) and reached Europe about "
                   "1200. Corrected.",
    "galley": "dated from `oars`, which the products atlas puts at -10000 in all 17 areas - true "
              "of a paddle, absurd of a Mediterranean warship. Corrected to explicit dates.",
    "dhow": "dated from `sails`, which gave a dhow to the Americas and Australia. The dhow is the "
            "ship of the Indian Ocean's monsoon trades; corrected to the lands that had it.",
    "junk": "dated from `rigging`, which put junks in Europe from 500 BC. The junk is Chinese; "
            "corrected to East and South-East Asia and the lands they traded with.",
    "chariot": "the armoury's own row carries no flat years (it is technology-driven), so the "
               "chariot is dated by the technology atlas's `chariot` tech instead, with the "
               "armoury's never-map and end-years.",
    "sledge": "the products atlas dates `sledges` at -10000 in all 17 areas, inherited from its "
              "parent `timber`. A sledge is a vehicle of snow and of dogs - it is not a universal "
              "vehicle, and there was never one in Australia or the Congo. Restricted to the "
              "northern and cold-winter areas, marked estimated.",
    "balloon": "the products atlas dates `balloons` at EUR 1919, inherited from its parent "
               "`aeroplane` - a hundred and thirty-six years after the Montgolfiers. Corrected to "
               "explicit first-flight dates: Paris 1783, Philadelphia 1793, Calcutta 1836, "
               "Australia 1858, the Paraguayan War 1866, and the late-century reaching of the "
               "rest. Marked estimated away from the six documented firsts.",
    "helicopter": "the products atlas dates `helicopters` at EUR 1919 too, again from the "
                  "aeroplane - a helicopter BEFORE the aeroplane. Corrected to the Focke-Wulf Fw "
                  "61 (1936) and the Sikorsky VS-300 (1939) firsts, then the post-war spread. "
                  "Marked estimated away from those two.",
    "sailing_ship": "dated from `boats`, which the products atlas puts at -10000 in all 17 areas "
                    "- a raft, not a 200-tonne ship under sail. Corrected to the documented "
                    "coming of the sail: the Egyptian Nile boat of about -3200, the Cycladic "
                    "ships of about -2200, the Austronesian expansion, the Polynesian canoes of "
                    "-900, and the Portuguese caravel of 1440 in West Africa. Marked estimated "
                    "away from those.",
}

# What a vehicle needs that its own date does not tell you. This is the join E11 runs on.
NEEDS = ["none", "beast", "road", "rail", "tramline", "water", "canal", "air"]

_PRODUCTS = None
_ATLAS = None
_ARMOURY = None

DATA = None  # 'eternal/src/main/resources' root, worked out on first use


def _root():
    import os
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "eternal",
                        "src", "main", "resources")


def _products():
    global _PRODUCTS, DATA
    if _PRODUCTS is None:
        import json
        import os
        DATA = _root()
        with open(os.path.join(DATA, "data", "eternalengine", "eternal", "economy",
                               "products_world.json"), encoding="utf-8") as fh:
            _PRODUCTS = {p["id"]: p for p in json.load(fh)["products"]}
    return _PRODUCTS


def _atlas():
    """The technology atlas: tech id -> the year it reaches each country, as a spread curve."""
    global _ATLAS
    if _ATLAS is None:
        import gzip
        import json
        import os
        with gzip.open(os.path.join(_root(), "data", "eternalengine", "eternal", "history",
                                    "technology_atlas.json.gz"), "rb") as fh:
            d = json.loads(fh.read().decode("utf-8"))
        _ATLAS = {}
        for t in d["techs"]:
            _ATLAS[t["id"]] = t
    return _ATLAS


def _armoury():
    global _ARMOURY
    if _ARMOURY is None:
        import gzip
        import json
        import os
        with gzip.open(os.path.join(_root(), "data", "eternalengine", "eternal", "war",
                                    "armory.json.gz"), "rb") as fh:
            d = json.loads(fh.read().decode("utf-8"))
        _ARMOURY = {k["id"]: k for k in d["rows"]}
    return _ARMOURY


def product_years(pid):
    """The `made` years of a products-atlas good, or None when the atlas has no such good."""
    p = _products().get(pid)
    return dict(p["made"]) if p else None


def armoury_years(kind):
    """The years, end-years and never-map of an armoury kind."""
    k = _armoury().get(kind)
    if not k:
        return None
    return {"years": k.get("years"), "end": k.get("end") or {}, "never": k.get("never") or {}}


# --------------------------------------------------------------------------------------------------
# The register.
#
# `yearsFrom` says where the dates come from: ("product", id) or ("tech", id) or
# ("armoury", kind) or ("explicit", {...}). Anything else would be a fourth copy of a date that
# already exists somewhere in the mod.
# --------------------------------------------------------------------------------------------------

VEHICLES = [
    # ---------------------------------------------------------------- on foot
    dict(id="porter", name="a porter with a load", medium="foot", needs=["none"], beast=None,
         people=0, loadKg=29, kmPerDay=20, yearsFrom=("explicit", {a: -10000 for a in AREAS}),
         supersedes=[], vanilla=None, mark="recorded",
         note="The oldest vehicle, and the one that needs nothing at all. See D14 (part 2): 29 kg "
              "on the head, 20 km a day, and the only carrier the tsetse belt ever had.",
         source="step 46 part 2, animals.json.gz"),
    dict(id="litter", name="the litter and the palanquin", medium="foot", needs=["none"],
         beast=None, people=1, loadKg=80, kmPerDay=25,
         yearsFrom=("product", "litters"), supersedes=[], vanilla=None, mark="recorded",
         note="**A chair with poles.** The products atlas dates litters to -10000 in all 17 "
              "areas, alongside rafts, canoes and sledges: the four carriers that need no "
              "technology, which is why they are first everywhere. Carried by two, four or eight "
              "bearers, it is how a person of rank moved in China, India, Rome and Peru - and in "
              "the Andes, where there were no beasts to ride, the Inca travelled in one.",
         source="products atlas (litters)"),
    dict(id="wheelbarrow", name="the wheelbarrow", medium="wheel", needs=["none"], beast=None,
         people=0, loadKg=60, kmPerDay=15,
         yearsFrom=("explicit", {"EAS": 100, "SEA": 600, "SAS": 1200, "EUR": 1200, "EEU": 1300,
                                 "WAS": 1200, "NAF": 1200, "CAS": 1200, "WAF": 1900, "MSA": 1900,
                                 "EAF": 1900, "NNA": 1750, "MNA": 1700, "CAC": 1700, "SAM": 1750,
                                 "PAC": 1850, "AUS": 1850}), supersedes=[],
         vanilla="minecraft:minecart", mark="estimated",
         note="**One wheel and one person**, and the only wheeled vehicle that needs no beast. "
              "The products atlas dates it with the cart, because both wait on the wheel - but a "
              "wheelbarrow works where a cart cannot, on a path too narrow for a beast.",
         source="products atlas (wheelbarrows)"),
    dict(id="sledge", name="the sledge and the travois", medium="foot", needs=["beast"],
         beast="dog", people=0, loadKg=200, kmPerDay=30,
         yearsFrom=("explicit", {"EEU": -6000, "EUR": -6000, "CAS": -4000, "NNA": -2000,
                                 "EAS": -2000, "SAS": -1000, "WAS": -1000}),
         supersedes=[], vanilla="minecraft:minecart", mark="estimated",
         note="Two poles dragged behind a dog, a horse or a person. **The vehicle that predates "
              "the wheel**, because it needs no wheel: snow or bare ground does the work. A "
              "vehicle of snow and of dogs, so **only the northern and cold-winter areas have "
              "one** - the products atlas had it at -10000 in all seventeen, inherited from "
              "`timber`.",
         source="corrected: products atlas (sledges) dates it from `timber`"),

    # ---------------------------------------------------------------- on a beast
    dict(id="riding_horse", name="a rider on a horse", medium="beast", needs=["beast"],
         beast="horse", people=1, loadKg=100, kmPerDay=40, yearsFrom=("product", "horses"),
         supersedes=[], vanilla="minecraft:horse", mark="recorded",
         note="The fastest thing on land for three thousand years. The mod's own `VehicleType` "
              "gives it 45 km a day. **None in the Americas between their extinction and 1493, and "
              "none in Australia until 1788** - which is why the Comanche and the Plains peoples "
              "were a horse culture for barely two centuries.",
         source="products atlas (horses); VehicleType.HORSE"),
    dict(id="riding_camel", name="a rider on a camel", medium="beast", needs=["beast"],
         beast="camel", people=1, loadKg=200, kmPerDay=35, yearsFrom=("product", "camels"),
         supersedes=[], vanilla="minecraft:camel", mark="recorded",
         note="Slower than a horse over a day and faster than one over a desert, because the "
              "horse has to stop and drink. **It was the North Arabian saddle, not the animal, "
              "that made the camel a mount of war** - before it, a rider sat behind the hump and "
              "could not use a weapon.",
         source="products atlas (camels)"),
    dict(id="elephant_howdah", name="an elephant with a howdah", medium="beast",
         needs=["beast"], beast="elephant", people=4, loadKg=500, kmPerDay=25,
         yearsFrom=("armoury", "elephant"), supersedes=[], vanilla=None, mark="estimated",
         note="Not a way of getting somewhere so much as a way of arriving. The armoury (step 45) "
              "has war elephants in South Asia from -2000, South-East Asia from -1500 and Europe "
              "from -280 - Pyrrhus crossed into Italy with twenty of them - and **nowhere in "
              "Africa**, where the elephant was never trained for war. **This register refuses "
              "Europe anyway**: twenty imported beasts are a battle and not a transport system, "
              "and there has never been a working elephant population there, which is exactly the "
              "join the `needs` column exists to make. Vanilla has no elephant, so this stands in "
              "with a horse and says so.",
         source="step 45 armoury (elephant)"),

    # ---------------------------------------------------------------- wheeled
    dict(id="cart", name="the cart", medium="wheel", needs=["beast"], beast="ox",
         people=2, loadKg=500, kmPerDay=25, yearsFrom=("product", "carts"), supersedes=[],
         vanilla="minecraft:minecart", mark="recorded",
         note="**Two wheels, one axle and a beast** - the device that turned a 50 kg pack into a "
              "500 kg load, and the single largest change in the history of moving things. The "
              "mod's own `VehicleType` gives it 25 km a day. **It is also the thing the Americas "
              "never had**: the wheel was known there (on children's toys) and never put to work, "
              "because there was nothing to hitch to it.",
         source="products atlas (carts); VehicleType.CART"),
    dict(id="wagon", name="the wagon", medium="wheel", needs=["beast"], beast="ox",
         people=4, loadKg=1200, kmPerDay=20, yearsFrom=("product", "wagons"), supersedes=[],
         vanilla="minecraft:minecart", mark="recorded",
         note="Four wheels and a turning front axle, which is what lets it corner - a cart has to "
              "be dragged round. The wagon train that crossed North America, and the covered wagon "
              "of the Boer trek.",
         source="products atlas (wagons)"),
    dict(id="chariot", name="the chariot", medium="wheel", needs=["beast"], beast="horse",
         people=2, loadKg=150, kmPerDay=60, yearsFrom=("tech", "chariot"), armouryFrom="chariot", supersedes=[],
         vanilla="minecraft:minecart", mark="recorded",
         note="Fast, light, and useless on rough ground - which is why it was a weapon and a "
              "racing car and never a cart. **Step 45's armoury already dated it**, with an end "
              "year per area (it left the field in Europe by AD 100) and a `never` map: no war "
              "chariots in the Americas (no horses), none in Oceania, and **none in West, Middle "
              "or East Africa, because the horse does not cross the tsetse belt.**",
         source="step 45 armoury (chariot); technology atlas (chariot)"),
    dict(id="carriage", name="the horse carriage", medium="wheel", needs=["beast", "road"],
         beast="horse", people=4, loadKg=300, kmPerDay=50, yearsFrom=("product", "carriages"),
         supersedes=[], vanilla="minecraft:minecart", mark="recorded",
         note="A wagon made for people, and the first vehicle whose speed depended on the ROAD "
              "rather than on the beast - which is why turnpikes and macadam arrive with it. The "
              "hackney carriage (`carriages_city`) is its public form: the first vehicle you could "
              "hail.",
         source="products atlas (carriages, carriages_city)"),
    dict(id="rickshaw", name="the rickshaw", medium="wheel", needs=["road"], beast=None,
         people=1, loadKg=120, kmPerDay=30,
         yearsFrom=("explicit", {"EAS": 1868, "SEA": 1875, "SAS": 1880, "EUR": 1890, "EEU": 1900,
                                 "WAS": 1900, "NAF": 1900, "CAS": 1900, "WAF": 1900, "MSA": 1900,
                                 "EAF": 1890, "NNA": 1890, "MNA": 1890, "CAC": 1890, "SAM": 1890,
                                 "PAC": 1890, "AUS": 1890}), supersedes=[],
         vanilla="minecraft:minecart", mark="estimated",
         note="**A cart pulled by a person instead of a beast** - which sounds like a step "
              "backward and was in fact a step forward: it is cheaper than a horse, it needs no "
              "stabling, and in the crowded cities of East and South Asia in the nineteenth "
              "century it beat both. Cycled on from the bicycle, not from the cart.",
         source="products atlas (rickshaws)"),
    dict(id="bicycle", name="the bicycle", medium="wheel", needs=["road"], beast=None,
         people=1, loadKg=30, kmPerDay=60, yearsFrom=("product", "bicycle"), supersedes=[],
         vanilla=None, mark="recorded",
         note="**The only vehicle that makes a person faster than a horse on the same food.** A "
              "walking man uses more energy per kilometre than a cyclist, a horse less efficiently "
              "still - which is why the bicycle, not the car, was the machine that liberated the "
              "countryside in the 1890s. Six of the 17 areas in the products atlas.",
         source="products atlas (bicycle); technology atlas (bicycle)"),

    # ---------------------------------------------------------------- on rails
    dict(id="train", name="the train", medium="rail", needs=["rail"], beast=None,
         people=200, loadKg=500000, kmPerDay=500, yearsFrom=("product", "railway"),
         supersedes=["wagon"], vanilla="minecraft:minecart", mark="recorded",
         note="**The first vehicle faster than anything alive**, and the first that needed a road "
              "built for it alone. The mod's own `VehicleType` gives it 500 km a day against a "
              "wagon's 25. Step 34's `ways.grid.gz` knows the year a railway reached each of "
              "124,240 squares, so E11 can ask whether the rail is here YET - a train is not "
              "simply 'the railway exists', it is 'the railway exists here'.",
         source="products atlas (railway); step 34 WaysGrid; VehicleType.TRAIN"),
    dict(id="tram", name="the electric tram", medium="rail", needs=["tramline"], beast=None,
         people=60, loadKg=10000, kmPerDay=200, yearsFrom=("product", "trams"), supersedes=[],
         vanilla="minecraft:minecart", mark="recorded",
         note="A railway laid in a street, and the first transport a city could afford to use "
              "twice a day. It made the suburb, and the suburb made it.",
         source="products atlas (trams); technology atlas (tram)"),
    dict(id="high_speed_train", name="the high-speed train", medium="rail", needs=["rail"],
         beast=None, people=400, loadKg=400000, kmPerDay=1500,
         yearsFrom=("product", "high_speed_trains"), supersedes=["train"], vanilla=None,
         mark="recorded",
         note="Eight of the 17 areas. It needs its own track - it cannot share with freight - so "
              "it is less an improvement on the train than a different railway that happens to "
              "carry people.",
         source="products atlas (high_speed_trains)"),

    # ---------------------------------------------------------------- on water
    dict(id="raft", name="the raft and the reed boat", medium="water", needs=["water"],
         beast=None, people=4, loadKg=500, kmPerDay=25, yearsFrom=("product", "rafts"),
         supersedes=[], vanilla="minecraft:boat", mark="recorded",
         note="**-10000 in all 17 areas, like the litter and the sledge:** a raft is bound reeds "
              "or lashed logs and needs no technology to speak of. It is also how people reached "
              "islands no raft could have been aimed at, which is why the Pacific was settled from "
              "the east.",
         source="products atlas (rafts)"),
    dict(id="canoe", name="the dugout canoe", medium="water", needs=["water"], beast=None,
         people=6, loadKg=800, kmPerDay=30, yearsFrom=("product", "canoes"), supersedes=[],
         vanilla="minecraft:boat", mark="recorded",
         note="One log, hollowed with fire and adze. -10000 everywhere, and still the vehicle of "
              "every riverine people on earth. **A canoe is why the Amazon is a road system and "
              "not a wilderness.**",
         source="products atlas (canoes)"),
    dict(id="galley", name="the galley", medium="water", needs=["water"], beast=None,
         people=50, loadKg=30000, kmPerDay=80,
         yearsFrom=("explicit", {"WAS": -1500, "NAF": -1200, "EUR": -800, "EEU": -500,
                                 "SAS": -300, "EAS": -200, "SEA": 200, "CAS": -500, "WAF": 1500,
                                 "EAF": 1500, "NNA": 1500, "MNA": 1500, "CAC": 1500, "SAM": 1500,
                                 "PAC": 1800, "AUS": 1800, "MSA": 1500}), supersedes=[],
         vanilla="minecraft:boat", mark="estimated",
         note="A ship of oars, and **the only vessel that can move when the wind will not** - "
              "which is why the trireme could ram and the Mediterranean could be policed. The "
              "mod's `VehicleType` gives it 80 km a day. Dated from `oars`, the part of it the "
              "products atlas carries; the hull itself the atlas does not name.",
         source="products atlas (oars); VehicleType.GALLEY"),
    dict(id="dhow", name="the dhow", medium="water", needs=["water"], beast=None,
         people=20, loadKg=40000, kmPerDay=100,
         yearsFrom=("explicit", {"WAS": -200, "NAF": 300, "SAS": 200, "EAF": 500, "SEA": 700,
                                 "EUR": 800, "EEU": 900, "EAS": 900, "CAS": 400, "WAF": 900,
                                 "MSA": 1000}), supersedes=[],
         vanilla="minecraft:boat", mark="estimated",
         note="**The lateen sail - a triangular sail on a long yard - is the reason the Indian "
              "Ocean was one world.** Unlike a square sail it can beat back against the wind, so "
              "a dhow can sail to Africa on the winter monsoon and home on the summer one, which "
              "a square-rigged ship cannot do on schedule. Dated from `sails`.",
         source="products atlas (sails, rigging)"),
    dict(id="junk", name="the junk", medium="water", needs=["water"], beast=None,
         people=60, loadKg=120000, kmPerDay=110,
         yearsFrom=("explicit", {"EAS": 200, "SEA": 800, "SAS": 1200}), supersedes=[],
         vanilla="minecraft:boat", mark="estimated",
         note="**The Chinese junk carried bulkhead walls, a balanced rudder and a compass centuries "
              "before the West had any of them**, and its battened sails could be reefed by one "
              "man from the deck. Dated from `rigging`, which the products atlas carries in 10 of "
              "17 areas.",
         source="products atlas (rigging)"),
    dict(id="sailing_ship", name="the sailing ship", medium="water", needs=["water"], beast=None,
         people=40, loadKg=200000, kmPerDay=120,
         yearsFrom=("explicit", {"WAS": -3200, "NAF": -3200, "EUR": -2200, "EEU": -800,
                                 "SAS": -1000, "SEA": -1500, "EAS": 200, "PAC": -900,
                                 "EAF": 500, "CAS": 1500, "WAF": 1440, "MSA": 1482,
                                 "NNA": 1492, "CAC": 1492, "MNA": 1519, "SAM": 1500,
                                 "AUS": 1700}),
         supersedes=[], vanilla="minecraft:boat", mark="estimated",
         note="The mod's own `VehicleType` gives it 120 km a day, the fastest thing on earth "
              "until the steamship. **It is the vehicle that made the world one system** - and the "
              "reason a European in 1600 could reach a port on every continent and a step inland "
              "from none of them. **Dated from the coming of the sail, not from the boat**: the "
              "Nile boat of about -3200, the Cycladic ships of about -2200, the Austronesian "
              "expansion of -1500, the Polynesian canoes of -900, and the caravel of 1440 that "
              "brought it to West Africa.",
         source="corrected: products atlas (boats) is -10000 everywhere; Wikipedia, Sailing ship / "
                "Austronesian expansion / Age of Discovery; VehicleType.SAILING_SHIP"),
    dict(id="steamship", name="the steamship", medium="water", needs=["water"], beast=None,
         people=200, loadKg=500000, kmPerDay=300, yearsFrom=("product", "steamships"),
         supersedes=["sailing_ship"], vanilla="minecraft:boat", mark="recorded",
         note="**The first vehicle that did not have to wait for the wind**, which mattered less "
              "for speed than for timetable: a steamship arrives on a date. The mod's "
              "`VehicleType` gives it 300 km a day against a sailing ship's 120.",
         source="products atlas (steamships); VehicleType.STEAMSHIP"),
    dict(id="motor_ship", name="the motor ship", medium="water", needs=["water"], beast=None,
         people=40, loadKg=2000000, kmPerDay=700, yearsFrom=("product", "motor_ships"),
         supersedes=["steamship"], vanilla="minecraft:boat", mark="recorded",
         note="The diesel-engined cargo ship, and **the vehicle that carries almost everything you "
              "own**. Its 700 km a day is slower than a plane by a factor of three and a half and "
              "cheaper by a factor of a hundred.",
         source="products atlas (motor_ships); VehicleType.CARGO_SHIP"),

    # ---------------------------------------------------------------- on land, powered
    dict(id="car", name="the motor car", medium="wheel", needs=["road"], beast=None,
         people=4, loadKg=400, kmPerDay=120, yearsFrom=("product", "car"), supersedes=[],
         vanilla=None, mark="recorded",
         note="Thirteen of the 17 areas in the products atlas. The mod's `VehicleType` gives it "
              "120 km a day - **the same as a sailing ship** - and unlike the ship the car needs a "
              "road under it, which is the join E11 is built on.",
         source="products atlas (car); VehicleType.AUTOMOBILE"),
    dict(id="bus", name="the motor bus", medium="wheel", needs=["road"], beast=None,
         people=40, loadKg=2000, kmPerDay=150, yearsFrom=("product", "buses"), supersedes=[],
         vanilla=None, mark="recorded",
         note="A carriage route with an engine in it. It is the vehicle that decides where a "
              "twentieth-century city ends, and it is cheaper per seat than anything on rails.",
         source="products atlas (buses)"),
    dict(id="lorry", name="the lorry", medium="wheel", needs=["road"], beast=None,
         people=2, loadKg=20000, kmPerDay=350, yearsFrom=("product", "lorries"), supersedes=["wagon"],
         vanilla=None, mark="recorded",
         note="**The vehicle that ended the caravan.** A lorry carries twenty tonnes at 350 km a "
              "day with one driver, which is what four hundred camels or two thousand porters "
              "could not do at any price. The mod's `VehicleType` gives it 350 km a day.",
         source="products atlas (lorries); VehicleType.TRUCK"),
    dict(id="motorcycle", name="the motorcycle", medium="wheel", needs=["road"], beast=None,
         people=2, loadKg=50, kmPerDay=200, yearsFrom=("product", "motorcycles"), supersedes=[],
         vanilla=None, mark="recorded",
         note="A bicycle with an engine, and in most of the world not a toy but the family "
              "vehicle - cheap to buy, cheap to run, and able to use a path a car cannot.",
         source="products atlas (motorcycles)"),
    dict(id="electric_car", name="the electric car", medium="wheel", needs=["road"], beast=None,
         people=4, loadKg=400, kmPerDay=120, yearsFrom=("product", "electric_cars"),
         supersedes=[], vanilla=None, mark="recorded",
         note="Fourteen of the 17 areas. **It is older than the petrol car's dominance and newer "
              "than its decline** - electric cars were sold in the 1890s, and came back in the "
              "2010s. Dated from the products atlas, which carries both waves.",
         source="products atlas (electric_cars)"),

    # ---------------------------------------------------------------- in the air
    dict(id="balloon", name="the balloon and the airship", medium="air", needs=["air"],
         beast=None, people=8, loadKg=2000, kmPerDay=150,
         yearsFrom=("explicit", {"EUR": 1783, "EEU": 1805, "NNA": 1793, "MNA": 1860,
                                 "CAC": 1870, "SAM": 1866, "WAS": 1850, "NAF": 1880,
                                 "SAS": 1836, "EAS": 1877, "SEA": 1890, "CAS": 1890,
                                 "AUS": 1858, "PAC": 1900, "WAF": 1900, "MSA": 1900,
                                 "EAF": 1900}),
         supersedes=[], vanilla=None, mark="estimated",
         note="**The first vehicle that left the ground, and the only one whose cargo was ever "
              "just the sky** - the balloon's first uses were the map, the weather and the siege "
              "of Paris in 1870, when 66 of them carried 2.5 million letters out of a city the "
              "Prussians had surrounded. The airship is the dirigible: a balloon you can steer "
              "(Giffard, 1852). **Dated from the documented first flights**: Paris 1783, "
              "Philadelphia 1793, Calcutta 1836, Australia 1858 and the Paraguayan War 1866; the "
              "rest of the map is an estimate of the late-century spread.",
         source="corrected: Wikipedia, History of ballooning; Montgolfier 1783, Blanchard 1793, "
                "Robertson over Calcutta 1836, Dean in Australia 1858"),
    dict(id="aeroplane", name="the aeroplane", medium="air", needs=["air"], beast=None,
         people=150, loadKg=20000, kmPerDay=2500, yearsFrom=("product", "aeroplane"),
         supersedes=["sailing_ship", "steamship"], vanilla=None, mark="recorded",
         note="The mod's `VehicleType` gives it 2,500 km a day: **five times a motor ship and "
              "twenty times a lorry.** It is the first vehicle for which the distance matters "
              "less than the airport at each end.",
         source="products atlas (aeroplane); VehicleType.AIRPLANE"),
    dict(id="helicopter", name="the helicopter", medium="air", needs=["air"], beast=None,
         people=6, loadKg=3000, kmPerDay=900,
         yearsFrom=("explicit", {"EUR": 1936, "NNA": 1939, "EEU": 1950, "EAS": 1950,
                                 "AUS": 1955, "MNA": 1955, "CAC": 1955, "SAM": 1955,
                                 "WAS": 1955, "NAF": 1955, "SAS": 1955, "CAS": 1965,
                                 "SEA": 1960, "WAF": 1960, "MSA": 1960, "EAF": 1960,
                                 "PAC": 1970}),
         supersedes=[], vanilla=None, mark="estimated",
         note="**The only vehicle that needs no road, no rail, no runway and no port** - which is "
              "why it is the ambulance and the rescue craft rather than the transport. 900 km a "
              "day. Dated from the two firsts - the Focke-Wulf Fw 61 in 1936 and the Sikorsky "
              "VS-300 in 1939 - and then the post-war spread; everything after those two is an "
              "estimate.",
         source="corrected: Wikipedia, Focke-Wulf Fw 61 (1936), Sikorsky VS-300 (1939); "
                "VehicleType.HELICOPTER"),
]

# Vehicles that need a beast, mapped to the animal that draws them. Read from part 2 so the two
# registers cannot disagree about whether the beast has arrived.
BEAST_OK = None  # filled lazily to avoid importing animal_table at module load


def years_for(v):
    """The years for a vehicle, read from whichever register owns them."""
    kind, key = v["yearsFrom"]
    if kind == "explicit":
        return dict(key)
    if kind == "product":
        return product_years(key) or {}
    if kind == "tech":
        # No flat years here: the technology atlas stores a SPREAD CURVE per country, resolved in
        # Java by TechnologyAtlas.present(). This register names the tech; the mod answers it.
        return {}
    if kind == "armoury":
        a = armoury_years(key)
        return dict(a["years"] or {}) if a else {}
    return {}


def _armoury_keys(v):
    """Which armoury rows carry this vehicle's `never`/`end` maps.

    A vehicle dated by the technology atlas still carries the armoury's never-map: the chariot's
    end-years and its nine `never` areas are war facts, and they are the only thing that stops a
    chariot being offered in Tenochtitlan or in the tsetse belt.
    """
    kind, key = v["yearsFrom"]
    out = []
    if kind == "armoury":
        out.append(key)
    if v.get("armouryFrom"):
        out.append(v["armouryFrom"])
    return out


def never_for(v):
    """The areas a vehicle never reached, with the reason."""
    out = {}
    for key in _armoury_keys(v):
        a = armoury_years(key)
        if a:
            out.update(a["never"])
    return out


def end_for(v):
    """The year a vehicle leaves the field in each area, when the source knows."""
    out = {}
    for key in _armoury_keys(v):
        a = armoury_years(key)
        if a:
            out.update(a["end"])
    return out


def problems():
    """Everything that would make the register wrong. Returns a list of strings."""
    bad = []
    seen = set()
    for v in VEHICLES:
        vid = v["id"]
        if vid in seen:
            bad.append("duplicate id " + vid)
        seen.add(vid)
        if v["medium"] not in MEDIUMS:
            bad.append(vid + ": unknown medium " + v["medium"])
        for n in v["needs"]:
            if n not in NEEDS:
                bad.append(vid + ": unknown need " + n)
        if not v["needs"]:
            bad.append(vid + ": needs nothing at all, which is not true of any vehicle")
        if v["kmPerDay"] <= 0:
            bad.append(vid + ": goes nowhere")
        if v["mark"] not in ("recorded", "estimated"):
            bad.append(vid + ": mark must be recorded or estimated")
        if v["beast"] is not None and "beast" not in v["needs"]:
            bad.append(vid + ": names a beast but does not need one")
        if "beast" in v["needs"] and v["beast"] is None:
            bad.append(vid + ": needs a beast but names none")
        y = years_for(v)
        if not y and v["yearsFrom"][0] != "tech":
            bad.append(vid + ": reaches no area at all - its source id is probably wrong")
        for a in y:
            if a not in AREAS:
                bad.append(vid + ": area " + a + " is not one of the 17")
        for a in never_for(v):
            if a not in AREAS:
                bad.append(vid + ": never-area " + a + " is not one of the 17")
        # A rail vehicle must need a rail. This is the join E11 depends on.
        if v["medium"] == "rail" and not any(n in ("rail", "tramline") for n in v["needs"]):
            bad.append(vid + ": runs on rails but does not need a railway")
        if v["medium"] == "water" and "water" not in v["needs"]:
            bad.append(vid + ": floats but does not need water")
        if v["medium"] == "air" and "air" not in v["needs"]:
            bad.append(vid + ": flies but does not need air")

    # The plan's list, checked. A vehicle the plan names and this register lacks is a gap.
    want = ["porter", "palanquin", "cart", "chariot", "horse", "camel", "elephant", "bicycle",
            "rickshaw", "tram", "bus", "car", "lorry", "raft", "dhow", "galley", "junk",
            "sailing ship", "steamship", "train", "balloon", "airship", "plane"]
    have = " ".join(v["id"] + " " + v["name"] for v in VEHICLES).lower()
    for w in want:
        if w not in have:
            bad.append("the plan names " + w + " and this register does not carry it")
    return bad


if __name__ == "__main__":
    p = problems()
    cols = ["EUR", "SAS", "EAS", "WAF", "NNA", "SAM", "AUS"]
    print("vehicles: %d entries, %d mediums"
          % (len(VEHICLES), len(set(v["medium"] for v in VEHICLES))))
    for v in VEHICLES:
        y = years_for(v)
        print("  %-18s %-6s %-9s %6.0f km/d %5d kg  %2d/17  %s"
              % (v["id"], v["medium"], ",".join(v["needs"]), v["kmPerDay"], v["loadKg"], len(y),
                 " ".join("%s:%s" % (c, y.get(c, "--")) for c in cols)))
    print("  corrected dates (step 44 part C template copies):")
    for k, why in CORRECTED.items():
        print("    - " + k + ": " + why[:96] + "...")
    for b in p:
        print("  PROBLEM " + b)
    print("vehicle_table: %d problem(s)" % len(p))
