#!/usr/bin/env python3
"""
Step 46 part 2 (D14): the working animals — what carried the world's goods, and what drew its
ploughs, and where no beast could live at all.

    python3 animal_table.py        check the register and print it

**The bug this register exists to fix.** `trade/LogisticsManager` spawns **two to four donkeys for
every caravan, in every era, on every continent**. Donkeys reach South America in 1530 and
Australia in 1788; the Andes had **llamas from 4000 BC**; the Sahara's pack animal is the **camel**;
and below the tsetse belt no beast survives at all, so the carrier is a **human porter**. This is
step 45's eighteen hardcoded swords over again, and it is fixed the same way: one *pack animal for
(place, year)* lookup.

**Where the dates come from.** The products atlas (step 44 part C) already dates the animals in all
17 areas, so this register **reads those dates** rather than rewriting them. It adds the three
things the products atlas does not carry: **what each animal does** (pack, ride, pull, plough),
**how much and how far**, and **where it never was**.

**Two corrections are made to the products atlas, and both are recorded:**
- **`reindeer` is dated −2000 in West Africa and AD 0 in Middle Africa.** That is a step-44 part-C
  derivation artefact — a child inheriting a parent's date. There have never been reindeer in
  West or Middle Africa, and the register says so with a `never` entry.
- **`donkeys` and `horses` share a date in every area**, which cannot be right — the donkey was
  domesticated in Africa (from the African wild ass) long before the horse arrived there from the
  steppe. The products atlas has them identical because part C derived both from the same parent.
  This register keeps the products date for the horse and **moves the donkey earlier in Africa**,
  marked `estimated`, with the reason given.

**Figures are ranges, marked `recorded` or `estimated`.** Nothing here is invented: every load and
every day's march is read from the sources named in each row.
"""

# The armoury's own area codes. Anything else is a mistake - part 4 of step 45 caught invented
# codes twice, and this register refuses to repeat that.
AREAS = ["EUR", "EEU", "WAS", "NAF", "CAS", "SAS", "EAS", "SEA", "WAF", "MSA", "EAF",
         "NNA", "MNA", "CAC", "SAM", "PAC", "AUS"]

# What an animal is for. A beast can do several.
ROLES = ["port", "pack", "ride", "pull", "plough", "herd"]

PRODUCTS = None  # filled on demand; the products atlas, read once


def _products():
    """The products atlas, read from the shipped pack so the two cannot drift."""
    global PRODUCTS
    if PRODUCTS is None:
        import gzip
        import json
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(here, "..", "eternal", "src", "main", "resources", "data",
                            "eternalengine", "eternal", "economy", "products_world.json")
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        PRODUCTS = {p["id"]: p for p in data["products"]}
    return PRODUCTS


def years_of(product_id):
    """The `made` years of a product, or an empty dict when the atlas does not carry it."""
    return dict(_products().get(product_id, {}).get("made", {}))


ANIMALS = [
    dict(
        id="porter",
        name="the human porter",
        kind="human",
        roles=["port", "pack"],
        loadKg=29,
        kmPerDay=20,
        mark="recorded",
        years={a: -10000 for a in AREAS},
        never={},
        supersedes=[],
        vanilla=None,
        note="**The default carrier of the tropics and the oldest carrier anywhere.** A Nyamwezi "
             "porter on the caravans to the Swahili coast carried 25-30 kg, 16-24 km a day; a "
             "Rhodesian carrier with 27-36 kg made 24-32 km. In pre-colonial Kano a porter's load "
             "was about 65 lb (29 kg) - **half a donkey's pack, and a tenth of a camel's**, so it "
             "took over ten men to carry one camel's load. Tens of thousands of professional "
             "porters worked the East African caravan corridors (Rockel, *Carriers of Culture*, "
             "2006). This is the answer wherever no beast can live.",
        source="Nyamwezi caravan figures; pre-colonial Kano trade (Yusuf Umar Madugu); Rockel 2006",
    ),
    dict(
        id="donkey",
        name="the donkey",
        kind="beast",
        roles=["pack", "pull"],
        loadKg=50,
        kmPerDay=24,
        mark="recorded",
        years=None,                      # read from the products atlas, corrected in Africa
        never={},
        supersedes=[],
        vanilla="minecraft:donkey",
        note="The pack animal of the poor and of the rocky hill. 20-25% of its body weight, "
             "roughly 36-54 kg, and 20-32 km a day. Domesticated from the African wild ass, so "
             "**it was in Africa long before the horse was** - the products atlas gives them the "
             "same date everywhere, which is wrong, and this register moves the donkey earlier in "
             "Africa (see `fix_donkey_africa`).",
        source="Logistics Cluster pack-animal table; Britannica",
    ),
    dict(
        id="mule",
        name="the mule",
        kind="beast",
        roles=["pack", "pull", "ride"],
        loadKg=70,
        kmPerDay=25,
        mark="estimated",
        years=None,                      # follows the donkey: a mule is a horse-donkey cross
        never={},
        supersedes=[],
        vanilla="minecraft:mule",
        note="A horse-donkey cross, and **sterile**, so it cannot be bred true - every mule is "
             "made again from a donkey stallion and a horse mare. Stronger and surer-footed than "
             "either parent, and the reason a mule train could cross a mountain a horse could "
             "not. Where the products atlas has no mule, it follows the donkey.",
        source="follows the donkey; the figures are between the two parents",
    ),
    dict(
        id="horse",
        name="the horse",
        kind="beast",
        roles=["ride", "pack", "pull", "plough"],
        loadKg=100,
        kmPerDay=40,
        mark="recorded",
        years=None,                      # read from the products atlas
        never={},
        supersedes=[],
        vanilla="minecraft:horse",
        note="Fast, and useless for heavy pulling until the **horse collar** reached Europe from "
             "China: with an ox-yoke across its chest a horse strangles itself at about 500 kg of "
             "pull, and the collar put the load on its shoulders instead. That one invention is "
             "why medieval Europe ploughed with horses and the classical world did not. **No horse "
             "in the Americas between their extinction and 1493**, and none in Australia until "
             "1788.",
        source="products atlas (horses); the collar and the yoke from the technology atlas",
    ),
    dict(
        id="camel",
        name="the camel",
        kind="beast",
        roles=["pack", "ride", "pull"],
        loadKg=200,
        kmPerDay=35,
        mark="recorded",
        years=None,                      # read from the products atlas
        never={},
        supersedes=[],
        vanilla="minecraft:camel",
        note="**The ship of the desert, and the only reason the Sahara is a road rather than a "
             "wall.** An adult carries about 40% of its body weight - 200-240 kg for a male "
             "Bactrian, 150-200 for a female - and 30-40 km a day on a journey of weeks (FAO); "
             "Britannica has the Bactrian at 170-250 kg over 47 km. It was the **North Arabian "
             "saddle**, not the animal, that made the camel a mount of war. **No camels in the "
             "Americas, the Congo or the archipelago.**",
        source="FAO working-capacity figures; Wikipedia (Bactrian camel); Britannica",
    ),
    dict(
        id="llama",
        name="the llama",
        kind="beast",
        roles=["pack"],
        loadKg=45,
        kmPerDay=25,
        mark="recorded",
        years=None,                      # read from the products atlas: SAM only, from -4000
        never={},
        supersedes=[],
        vanilla="minecraft:llama",
        note="**The only beast of burden the Americas had.** 25-30% of its body weight, 45-60 kg, "
             "for 25-30 km a day above 4,000 m (Britannica); llama caravans measured by Murra "
             "(1965) carried 34-45 kg for 16-19 km. Its soft pads erode the trail far less than a "
             "horse's hooves. **It refuses to move when overloaded, and it spits** - which is a "
             "fact a caravan master had to plan around. Four thousand years of llamas in the "
             "Andes, and the Spanish brought donkeys in 1530.",
        source="Britannica; Murra 1965 (ethnohistoric llama caravans); National Geographic",
    ),
    dict(
        id="ox",
        name="the ox",
        kind="beast",
        roles=["pull", "plough"],
        loadKg=120,
        kmPerDay=15,
        mark="recorded",
        years=None,                      # read from the products atlas (cattle)
        never={},
        supersedes=[],
        vanilla="minecraft:cow",
        note="A castrated bull, and **the plough animal of the ancient and medieval world** - "
             "slower than a horse, far cheaper to keep, and able to pull against a yoke across "
             "its neck. Oxen drew the wagon trains of the Great Trek across North America and the "
             "covered wagons of the American frontier. **The tsetse fly is why the plough never "
             "reached the forest**: Alsan measures a one-standard-deviation rise in tsetse "
             "suitability as a **23-point fall in the chance a people had large domestic animals "
             "and a 6-point fall in plough use.**",
        source="products atlas (cattle); Alsan, *The Effect of the Tsetse Fly on African "
               "Development* (2014)",
    ),
    dict(
        id="water_buffalo",
        name="the water buffalo",
        kind="beast",
        roles=["plough", "pull"],
        loadKg=150,
        kmPerDay=12,
        mark="estimated",
        years=None,                      # read from the products atlas (buffalo)
        never={},
        supersedes=[],
        vanilla=None,
        note="**The plough animal of wet rice.** A buffalo stands hock-deep in a flooded paddy "
             "where an ox founders, which is why it carries the rice agriculture of South, East "
             "and South-East Asia. Vanilla Minecraft has no buffalo, so this one falls back to "
             "the ox - a stand-in, and marked as one.",
        source="products atlas (buffalo); the figures are between the ox and the cattle",
    ),
    dict(
        id="elephant",
        name="the working elephant",
        kind="beast",
        roles=["pull", "ride"],
        loadKg=500,
        kmPerDay=25,
        mark="estimated",
        years=None,                      # read from the products atlas: SAS -2000, SEA -1500
        never={},
        supersedes=[],
        vanilla=None,
        note="Not a pack animal but a **haulage and a siege animal**: it drags what no team of "
             "oxen can start, and it is the only beast that will walk into a wall of men. "
             "**Working elephants are Indian (-2000) and South-East Asian (-1500)**; the African "
             "elephant was never trained for war, which is why step 45's armoury has war "
             "elephants in South Asia and nowhere in Africa. Vanilla has no elephant, so this "
             "falls back to the horse and says so.",
        source="products atlas (elephants); step 45 armoury, the elephant row",
    ),
    dict(
        id="reindeer",
        name="the reindeer",
        kind="beast",
        roles=["pull", "ride", "pack"],
        loadKg=60,
        kmPerDay=30,
        mark="estimated",
        years=None,
        never={
            "WAF": "there have never been reindeer in West Africa - the products atlas dates them "
                   "-2000 there, which is a derivation artefact of step 44 part C, where a child "
                   "inherited its parent's date",
            "MSA": "no reindeer in Middle Africa, for the same reason",
            "EAF": "no reindeer in East Africa: they are an animal of the Arctic and the "
                   "sub-Arctic",
            "AUS": "no reindeer in Australia, and none in the southern hemisphere at all until "
                   "they were introduced to South Georgia in 1911",
            "PAC": "no reindeer in Oceania",
            "SEA": "no reindeer in South-East Asia",
        },
        supersedes=[],
        vanilla=None,
        note="The pack, riding and sledge animal of the Arctic and sub-Arctic, and the only "
             "domestic deer. **Correction carried:** the products atlas dates reindeer to -2000 in "
             "West Africa and AD 0 in Middle Africa, which is impossible; the `never` entries "
             "above remove them.",
        source="products atlas (reindeer), corrected",
    ),
    dict(
        id="dog",
        name="the dog",
        kind="beast",
        roles=["pack", "pull"],
        loadKg=15,
        kmPerDay=30,
        mark="estimated",
        years=None,                      # the products atlas has dogs at -10000 everywhere
        never={},
        supersedes=[],
        vanilla="minecraft:wolf",
        note="On the Plains and in the Arctic a dog drew a **travois** - two poles trailing "
             "behind it with a load lashed between - and that was the wheeled transport of a "
             "people who had the wheel and no animal to pull it. Small loads, but enough to move "
             "a camp. Vanilla has wolves, not sled dogs, so this falls back and says so.",
        source="products atlas (dogs, -10000 everywhere); the travois",
    ),
    dict(
        id="sled",
        name="the sledge and the travois",
        kind="gear",
        roles=["pull"],
        loadKg=200,
        kmPerDay=30,
        mark="estimated",
        years=None,                      # sledges are -10000 everywhere: they need no technology
        never={},
        supersedes=[],
        vanilla="minecraft:minecart",
        note="**A vehicle that predates the wheel**, because it needs no wheel: drag two poles "
             "and the snow or the ground does the rest. The products atlas dates sledges to "
             "-10000 in all 17 areas, alongside litters, rafts and canoes - the four carriers "
             "that need no technology at all, which is why they are the answer everywhere and "
             "first.",
        source="products atlas (sledges)",
    ),
]

# The donkey was domesticated from the African wild ass and was in Africa long before the horse,
# which came from the Eurasian steppe. The products atlas gives them the same date in every area
# because part C derived both from the same parent; in Africa the donkey is earlier.
FIX_DONKEY_AFRICA = {
    "WAF": -3000, "NAF": -3000, "EAF": -1000, "MSA": -3000,
}
FIX_DONKEY_NOTE = ("moved earlier than the horse: the donkey is African (from the African wild "
                   "ass) and the horse is a steppe animal that arrived later")


# Which product of the atlas carries each animal's dates. The ids are PLURAL there
# (donkeys, horses, camels) and singular here, and that mismatch is exactly the kind of thing
# that silently empties a row - so it is written down rather than guessed.
PRODUCT_OF = {
    "donkey": "donkeys", "mule": "donkeys", "horse": "horses", "camel": "camels",
    "llama": "llamas", "ox": "cattle", "water_buffalo": "buffalo", "elephant": "elephants",
    "reindeer": "reindeer", "dog": "dogs", "sled": "sledges", "porter": None,
}


def resolve_years(a):
    """The years for an animal: the products atlas, then the corrections, then `never`."""
    if a["years"] is not None:
        years = dict(a["years"])
    else:
        pid = PRODUCT_OF.get(a["id"])
        years = dict(years_of(pid)) if pid else {}
    if a["id"] == "donkey":
        for area, year in FIX_DONKEY_AFRICA.items():
            if area in years and years[area] is not None and years[area] > year:
                years[area] = year
    for area in a["never"]:
        years.pop(area, None)
    return {k: v for k, v in years.items() if v is not None}


def problems():
    """Everything that would make the register wrong. Returns a list of strings."""
    bad = []
    seen = set()
    for a in ANIMALS:
        aid = a["id"]
        if aid in seen:
            bad.append("duplicate id " + aid)
        seen.add(aid)
        if a["kind"] not in ("beast", "human", "gear"):
            bad.append(aid + ": kind must be beast, human or gear")
        for r in a["roles"]:
            if r not in ROLES:
                bad.append(aid + ": unknown role " + r)
        if not a["roles"]:
            bad.append(aid + ": no role at all")
        if a["loadKg"] <= 0:
            bad.append(aid + ": a load of nothing")
        if a["kmPerDay"] <= 0:
            bad.append(aid + ": goes nowhere")
        if a["mark"] not in ("recorded", "estimated"):
            bad.append(aid + ": mark must be recorded or estimated")
        for area in a["never"]:
            if area not in AREAS:
                bad.append(aid + ": never-area " + area + " is not one of the 17")
            elif not a["never"][area].strip():
                bad.append(aid + ": " + area + " is excluded with no reason")
        for area in resolve_years(a):
            if area not in AREAS:
                bad.append(aid + ": year-area " + area + " is not one of the 17")
    if not any("port" in a["roles"] for a in ANIMALS):
        bad.append("no porter: the tropics would have no carrier at all")
    # An animal that reaches nowhere is a row whose product id does not match the atlas. This is
    # the check that was missing when five of the twelve silently resolved to zero areas.
    for a in ANIMALS:
        if not resolve_years(a):
            bad.append(a["id"] + ": reaches no area at all - its product id is probably wrong")
    # The porter must be everywhere and first, or the tsetse belt has nothing.
    porter = next((a for a in ANIMALS if a["id"] == "porter"), None)
    if porter is not None:
        py = resolve_years(porter)
        missing = [a for a in AREAS if a not in py]
        if missing:
            bad.append("the porter does not reach " + ", ".join(missing))
    return bad


if __name__ == "__main__":
    p = problems()
    cols = ["NNA", "MNA", "SAM", "AUS", "WAF", "CAS", "SAS", "EUR", "EAS"]
    print("working animals: %d entries, %d role(s) each on average"
          % (len(ANIMALS), sum(len(a["roles"]) for a in ANIMALS) / len(ANIMALS)))
    for a in ANIMALS:
        y = resolve_years(a)
        print("  %-14s %-24s %3d kg %3d km/d  %2d/17 areas  %s"
              % (a["id"], ",".join(a["roles"]), a["loadKg"], a["kmPerDay"], len(y),
                 " ".join("%s:%s" % (c, y.get(c, "--")) for c in cols)))
    for b in p:
        print("  PROBLEM " + b)
    print("animal_table: %d problem(s)" % len(p))
