#!/usr/bin/env python3
"""
Step 47 part 2 (E7): **tools and inventions as items** — what a person can pick up in a year.

    python3 tool_table.py        check the register and print it

The plan's line for E7 is *"ploughs, looms, printing, clocks, the compass, guns, radio, telephone"*,
and the survey found that **the dates for most of these already exist and the items do not**. Step
44's products atlas is a register of *products*: what a place makes and sells. This is a register of
*tools*: the thing in a person's hands, what it does, what it replaced, and what in Minecraft stands
for it.

## The rule this register follows, and why it is a rule

**A tool's date is not its material's date.** The survey found the atlas has this wrong in a way that
matters: `microscopes` is dated **2500 BC in West Asia**, because step 44 derived the microscope from
its parent `glass` and a compound microscope then became as old as glass. That is the same fault
found in step 46 in `reindeer` (2000 BC in West Africa) and `donkeys` (a date shared with horses
everywhere). **Three instances make it a class of error, not an accident**, so this register does not
derive a tool from a material at all: every row is either read from the atlas **by id** (a tool the
atlas dates correctly) or **written by hand with a source**.

## The three things a tool row carries that a product row cannot

1. **What it replaced.** The horse collar replaced the ox yoke for pulling; the heavy plough replaced
   the ard; the printing press replaced the scriptorium. A tool with no predecessor is a tool this
   register has misunderstood.
2. **The vanilla item that stands for it.** Every one of these has to resolve to something in
   Minecraft, or to say why it cannot, which is A13's rule from step 46 applied where it was always
   needed: an inventory.
3. **Where it never went, and why.** The treadle loom was known in China by the 2nd century BC and
   reached Europe in the 11th; the heavy plough needs soil and oxen that the Mediterranean does not
   have. A tool is not a universal.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
PRODUCTS = os.path.join(ROOT, "eternal", "src", "main", "resources", "data", "eternalengine",
                        "eternal", "economy", "products_world.json")

AREAS = ["EUR", "EEU", "WAS", "NAF", "CAS", "SAS", "EAS", "SEA", "WAF", "MSA", "EAF",
         "NNA", "MNA", "CAC", "SAM", "PAC", "AUS"]

# The work a tool does. One tool does one main thing; a few do two.
FAMILIES = ["farm", "make", "measure", "move", "write", "fight", "heal", "weigh", "light", "spin",
            "build"]

_ATLAS = None


def atlas():
    """The products atlas, read from the shipped pack so the two cannot drift."""
    global _ATLAS
    if _ATLAS is None:
        with open(PRODUCTS, encoding="utf-8") as fh:
            data = json.load(fh)
        _ATLAS = {p["id"]: p for p in data["products"]}
    return _ATLAS


# ---------------------------------------------------------------------------------------------
# The tools. `from_atlas` reads the dates from the products atlas by id.
# `made` writes them, and is only used where the atlas has no row, or has the wrong one.
# ---------------------------------------------------------------------------------------------

TOOLS = [
    # ---- THE HAND TOOLS, WHICH NEVER REALLY CHANGE ----------------------------------------
    dict(id="hand_axe", name="the hand axe", family="make", from_atlas="axes",
         replaces=None, vanilla="minecraft:stone_axe",
         note="The oldest tool in the register and the only one whose shape does not change for a "
              "million years. The atlas dates axes from 850 BC in Europe, which is the **iron** "
              "axe: a flaked hand axe is older than our span and a ground stone axe is Mesolithic. "
              "This register keeps the atlas's date because within 3000 BC to AD 3000 the axe is "
              "the iron axe, and says so here rather than pretending the row means the first axe "
              "ever made.",
         source="the products atlas, axes"),
    dict(id="sickle", name="the sickle", family="farm", from_atlas="sickles",
         replaces="the hand, and the basket",
         vanilla="minecraft:shears",
         note="Reaping is the one harvest job a machine still does badly: a combine harvester "
              "replaced the sickle only in the 20th century, and the sickle is a flint blade with "
              "a handle. The curve is the invention and it has never been improved on.",
         source="the products atlas, sickles"),
    dict(id="plough_ard", name="the ard, the scratch plough", family="farm", from_atlas="plough",
         replaces=None, vanilla="minecraft:wooden_hoe",
         note="A pointed stick drawn through the soil: it scratches a furrow and does not turn it. "
              "The atlas's `plough` dates the ard, and its dates are right for the ard: West Asia "
              "4000 BC, Europe 3000 BC, and the Americas only in 1540 with the Europeans.",
         source="the products atlas, plough"),
    dict(id="plough_heavy", name="the heavy plough with a mouldboard", family="farm", made={
             "EUR": 900, "EEU": 900, "WAS": 900, "CAS": 1000, "EAS": -200, "SAS": 1900,
             "NNA": 1650, "SAM": 1550, "AUS": 1800, "MNA": 1600, "NAF": 950, "WAF": 1950,
             "MSA": 1900, "EAF": 1950, "SEA": 1900, "CAC": 1550, "PAC": 1850},
         replaces="the ard", vanilla="minecraft:iron_hoe",
         note="**The mouldboard is a European answer to European soil.** It turns the turf over "
              "instead of scratching through it, which is what heavy wet northern clay needs and "
              "what a thin Mediterranean soil does not. China had a cast-iron mouldboard plough by "
              "the Han, several centuries earlier, and it is a different machine in a different "
              "soil. The row is dated **AD 900 in Europe** and the reason it never reached the "
              "Mediterranean before the modern period is the soil, not the technology.",
         source="Britannica, history of the plough; Han tomb reliefs for the Chinese mouldboard"),
    dict(id="wheelbarrow", name="the wheelbarrow", family="move", from_atlas="wheelbarrows",
         replaces="the carrying pole and two men",
         vanilla="minecraft:minecart",
         note="**A one-wheeled barrow is a Chinese invention of the first century BC** and it "
              "reaches Europe only in the 12th century. The 江州 legend names Zhuge Liang, which is "
              "probably wrong, but the date is not. One wheel is better than two for a plank path "
              "and worse on a road, which is why the European version that followed had two.",
         source="the products atlas, wheelbarrows; Needham, Science and Civilisation in China"),
    dict(id="quern", name="the quern", family="farm", from_atlas="querns",
         replaces="the grinding stone and the tooth",
         vanilla="minecraft:grindstone",
         note="Two stones and a hole. The quern is in the atlas dated 10000 BC in every area, "
              "which is outside our span and is the honest answer: it is older than the world "
              "this mod runs.",
         source="the products atlas, querns"),
    # ---- SPINNING AND WEAVING: THE MISSING TOOL ---------------------------------------------
    dict(id="spinning_wheel", name="the spinning wheel", family="spin", from_atlas="spinning_wheels",
         replaces="the spindle and the distaff",
         vanilla="minecraft:spinning_wheel_placeholder",
         note="The spindle is 20,000 years old; the **wheel** that turns it is Indian, about AD "
              "500, and it reaches Europe in the 13th century and China in the 11th. It triples "
              "what one person can spin, which is a change in the price of cloth and therefore of "
              "everything. **There is no vanilla item for a spinning wheel** and this row says so "
              "rather than borrowing the spinning-wheel shape the atlas already draws on the "
              "cloth: what stands in for it in play is the wool, not the wheel.",
         source="the products atlas, spinning_wheels"),
    dict(id="loom_warp_weighted", name="the warp-weighted loom", family="spin", made={
             "EUR": -5000, "WAS": -6000, "EEU": -5000, "NAF": -4000, "CAS": -4000, "SAS": -3000,
             "EAS": -3000, "SEA": -2000, "NNA": -1000, "MNA": -1500, "SAM": -1000, "CAC": -1000,
             "WAF": -1000, "MSA": -1000, "EAF": -1000, "AUS": 1788, "PAC": 1800},
         replaces="the ground loom and the backstrap loom",
         vanilla="minecraft:loom", before_world=True,
         note="**The atlas has no loom at all and this is the register's main addition.** A vertical "
              "frame with the warp hanging from a bar and clay weights tied to the bottom: loom "
              "weights are found from the early Neolithic in Serbia, Hungary, Switzerland and at "
              "Çatalhöyük about 7000 BC, and Barber argues for the 6th or 7th millennium in central "
              "Europe. It weaves from the top down and can be rolled, so the cloth is not limited "
              "by the height of the frame. **It is older than the world this mod runs**: 3000 BC "
              "is the first year the mod answers for and the warp-weighted loom was already four "
              "thousand years old in 3000 BC, so every area is dated at its true year and marked "
              "`before_world`. A player in 3000 BC finds it already there, which is the truth.",
         source="Wikipedia, warp-weighted loom; Barber, Prehistoric Textiles; Smith College Museum "
                "of Ancient Inventions"),
    dict(id="loom_treadle", name="the horizontal treadle loom", family="spin", made={
             "EAS": -200, "EUR": 1050, "EEU": 1100, "WAS": 1000, "NAF": 1000, "CAS": 1100,
             "SAS": 1100, "SEA": 1200, "NNA": 1650, "MNA": 1520, "SAM": 1550, "CAC": 1520,
             "WAF": 1900, "MSA": 1800, "EAF": 1900, "AUS": 1790, "PAC": 1850},
         replaces="the warp-weighted loom",
         vanilla="minecraft:loom",
         note="**The treadle frees both hands.** One foot lifts the warp and the other throws the "
              "shuttle, so a weaver can make cloth three times as fast in the same day. China has "
              "it by the 2nd century BC; the earliest European examples are at Gdańsk and Novgorod "
              "in the 11th century, and the earliest picture of one in Europe is an English "
              "manuscript of the mid-13th. **The transition also took weaving out of women's hands "
              "and into guilds**: the horizontal loom was expensive, so it went into workshops, and "
              "the workshops excluded women.",
         source="Wikipedia, loom and treadle loom; EXARC, model of a horizontal treadle loom; "
                "Hoffmann on the 11th-century shift"),
    # ---- PRINTING: ALSO MISSING FROM THE ATLAS ---------------------------------------------
    dict(id="printing_block", name="woodblock printing", family="write", from_atlas="woodblock_prints",
         replaces="the scribe",
         vanilla="minecraft:paper",
         note="One block, one page, carved in reverse and thrown away after the run. The atlas "
              "dates it East Asia 700, North Africa 950, Southeast Asia 1250, Europe 1400, and the "
              "workplace it names is **a printing house**, which is right.",
         source="the products atlas, woodblock_prints"),
    dict(id="printing_movable", name="movable type", family="write", made={
             "EAS": 1040, "EUR": 1450, "WAS": 1490, "EEU": 1490, "NAF": 1500, "CAS": 1500,
             "SAS": 1550, "SEA": 1600, "NNA": 1640, "MNA": 1539, "SAM": 1550, "CAC": 1540,
             "WAF": 1800, "MSA": 1820, "EAF": 1900, "AUS": 1795, "PAC": 1830},
         replaces="woodblock printing, and the copyist",
         vanilla="minecraft:lectern",
         note="**China had movable type 410 years before Gutenberg, and it did not change the "
              "world there.** Bi Sheng made ceramic type about 1040, described by Shen Kuo; Korea "
              "printed a metal-type book in 1377. Gutenberg's contribution is not the idea but the "
              "**hand mould**: a way to cast a thousand identical pieces of type in a day from a "
              "lead-tin-antimony alloy, plus oil ink and a screw press borrowed from wine. What "
              "made it explode in Europe was the script, not the machine: an alphabet needs 26 "
              "shapes and Chinese needs thousands, so the whole of Bi Sheng's invention was the "
              "setting of the type and none of it was the casting. **The press is not in the atlas "
              "at all**; `woodblock_prints` is the product and not the machine.",
         source="Wikipedia, movable type; Britannica, history of printing; the 1377 Jikji"),
    # ---- TIME, DIRECTION AND MEASURE ---------------------------------------------------------
    dict(id="sundial", name="the sundial", family="measure", made={
             "WAS": -1500, "EUR": -600, "EEU": -600, "NAF": -1500, "CAS": -500, "SAS": -500,
             "EAS": -1000, "SEA": -500, "NNA": 1600, "MNA": 1520, "SAM": 1550, "CAC": 1520,
             "WAF": 1900, "MSA": 1800, "EAF": 1900, "AUS": 1790, "PAC": 1850},
         replaces=None, vanilla="minecraft:daylight_detector",
         note="The gnomon is a stick and the shadow is the answer. Egyptian and Babylonian sundials "
              "are known by 1500 BC and the Greek portable dial by 300 BC. A sundial tells the "
              "**hour of the day**; the mechanical clock tells the **same hour everywhere**, and "
              "that is the invention that changed life, not the clock.",
         source="Wikipedia, sundial; Vitruvius book IX"),
    dict(id="clock_mechanical", name="the mechanical clock", family="measure",
         from_atlas="clocks",
         replaces="the water clock, the candle and the bell",
         vanilla="minecraft:clock",
         note="The atlas dates clocks East Asia 1092, Europe 1283, South Asia 1520, West Asia 1550 "
              "and North America 1700, and the first two are exactly right: Su Song's astronomical "
              "clock at Kaifeng is 1092 and the tower clocks of Italy and England are the 1280s. "
              "**A clock is not a machine that tells the time; it is a machine that lets a town "
              "agree on the time**, which is why they went up on towers and not on wrists.",
         source="the products atlas, clocks; Su Song's Xin Yixiang Fayao"),
    dict(id="compass", name="the magnetic compass", family="measure", from_atlas="compasses",
         replaces="the pole star and the lead",
         vanilla="minecraft:compass",
         note="The atlas dates it East Asia 1088, Europe 1190, West Asia 1232, South Asia 1350 and "
              "North America 1497, which is the spread of the **mariner's** compass. The Chinese "
              "had the lodestone spoon two centuries before that, on land, for divination. A "
              "compass is only useful at sea, where there is no other north.",
         source="the products atlas, compasses; Needham on the wet compass"),
    dict(id="astrolabe", name="the astrolabe", family="measure", from_atlas="astrolabes",
         replaces="the altitude of the pole star by hand",
         vanilla="minecraft:spyglass",
         note="**A computer made of brass**: set the date and read the time, or set the time and "
              "read the star. It is the instrument that made latitude findable, and it was the "
              "most sophisticated object in the world for a thousand years.",
         source="the products atlas, astrolabes"),
    dict(id="telescope", name="the telescope", family="measure", from_atlas="telescopes",
         replaces="the naked eye",
         vanilla="minecraft:spyglass",
         note="The atlas dates it Europe 1608, East Asia 1613, South Asia 1616, West Asia 1620 and "
              "North America 1680: the telescope spreads across the world faster than anything "
              "before printing, in eight years to Japan.",
         source="the products atlas, telescopes"),
    dict(id="microscope", name="the compound microscope", family="measure", made={
             "EUR": 1590, "EAS": 1650, "SAS": 1700, "WAS": 1650, "EEU": 1650, "NAF": 1700,
             "CAS": 1750, "SEA": 1750, "NNA": 1750, "MNA": 1700, "SAM": 1750, "CAC": 1750,
             "WAF": 1900, "MSA": 1900, "EAF": 1950, "AUS": 1800, "PAC": 1850},
         replaces="the naked eye, and the loupe",
         vanilla="minecraft:spyglass",
         note="**A correction, and the third instance of the same atlas bug.** The atlas dates "
              "`microscopes` to 2500 BC in West Asia, 1000 BC in South Asia and 500 BC in East "
              "Asia, because step 44 derived it from its parent `glass` and a microscope then "
              "became as old as glass. Step 46 found the same fault in `reindeer` and `donkeys`. "
              "The compound microscope is **about 1590**, attributed to Hans and Zacharias Janssen "
              "of Middelburg on the strength of a recollection given to the diplomat Willem Boreel "
              "in **1655**, sixty-five years later, by the inventor's son. The attribution is "
              "doubted and the date is not much better; 1590 is the conventional figure and this "
              "row marks it `estimated` for that reason.",
         source="Wikipedia, Zacharias Janssen and timeline of microscope technology; Britannica, "
                "microscope history"),
    # ---- POWER -------------------------------------------------------------------------------
    dict(id="watermill", name="the watermill", family="make", from_atlas="watermills",
         replaces="the hand quern and the slave",
         vanilla="minecraft:water_wheel_placeholder",
         note="**The first machine that did work without muscles**, and it is Roman: the atlas "
              "dates West Asia 71 BC, Europe 250 BC, China AD 31 and South Asia 783. The "
              "undershot wheel is a wheel in a stream; the overshot wheel, which is twice as "
              "efficient, needs an aqueduct and appears in the Roman world in the 4th century. "
              "**Nothing in vanilla is a mill wheel**: the nearest thing is a waterlogged staircase "
              "and it does no work, so there is no vanilla item for this and the row admits it.",
         source="the products atlas, watermills"),
    dict(id="windmill", name="the windmill", family="make", from_atlas="windmills",
         replaces="the watermill, where there is no water",
         vanilla="minecraft:windmill_placeholder",
         note="A windmill is what you build where the water will not run: Persia and Sistan for "
              "grinding, and the **post mill** of northern Europe for drainage. The atlas dates "
              "South Asia and West Asia 900, Europe 1180, East Asia 1219. **Nothing in vanilla is "
              "a windmill**, for the same reason as the watermill.",
         source="the products atlas, windmills"),
    dict(id="steam_engine", name="the steam engine", family="make", from_atlas="steam_engines",
         replaces="the waterwheel, the windmill and the horse",
         vanilla="minecraft:piston",
         note="**The engine that made the watermill obsolete by not needing a river.** The atlas "
              "dates Europe 1712, North America 1757, West Asia 1809, East Asia 1819 and South "
              "Asia 1820. 1712 is Newcomen's mine pump, which is a machine that burns coal to "
              "lift water; Watt's separate condenser in 1769 made it worth putting anywhere else.",
         source="the products atlas, steam_engines"),
    dict(id="tractor", name="the tractor", family="farm", from_atlas="tractors",
         replaces="the horse and the ox, at last",
         vanilla="minecraft:horse" ,
         note="**The only tool in this register that removed an animal from the world.** The "
              "atlas dates North America 1899, Europe 1902, West Asia 1924, South Asia 1946 and "
              "East Asia 1952, and the horse population of every industrial country falls from "
              "that year. Step 46 dates the working animals; this is the row that ends them.",
         source="the products atlas, tractors"),
    # ---- THE THINGS THAT CARRY INFORMATION ---------------------------------------------------
    dict(id="abacus", name="the abacus", family="weigh", from_atlas="abacus",
         replaces="counting on the fingers and the ground",
         vanilla="minecraft:abacus_placeholder",
         note="The atlas dates it 550 BC in Europe, 600 BC in East Asia, 500 BC in South Asia and "
              "West Asia, and 1800 in North America, where it arrives with Chinese labourers and "
              "is still faster than a 1960s adding machine. **There is no vanilla abacus**, and "
              "the honest stand-in is a chest of counted items, not a block.",
         source="the products atlas, abacus"),
    dict(id="paper", name="paper", family="write", from_atlas="paper",
         replaces="parchment, papyrus and bamboo",
         vanilla="minecraft:paper",
         note="The atlas dates it China 105, West Asia 794, East Asia 105, Europe 1150, South Asia "
              "1200. **The date is Cai Lun's report to the Han court in 105**, and paper reaches "
              "Samarkand in 751 with the prisoners of the Battle of Talas, which is how a Chinese "
              "craft becomes an Islamic one.",
         source="the products atlas, paper"),
    dict(id="telegraph", name="the electric telegraph", family="write", from_atlas="telegraph",
         replaces="the semaphore and the post rider",
         vanilla="minecraft:redstone",
         note="**The first thing that ever travelled faster than a horse.** The atlas dates it "
              "Europe 1837, North America 1844, South Asia 1851 and East Asia 1871. Before it, "
              "news travelled at the speed of the road, which is step 37's news register: after "
              "it, the news register had to be rewritten and was.",
         source="the products atlas, telegraph"),
    dict(id="telephone", name="the telephone", family="write", from_atlas="telephone",
         replaces="the telegraph, for everything that is not a code",
         vanilla="minecraft:bell",
         note="The telegraph needed a clerk at each end. The telephone did not, which is why it "
              "went into houses and the telegraph never did. The atlas dates Europe 1876, North "
              "America 1877, South Asia 1882, East Asia 1890.",
         source="the products atlas, telephone"),
    dict(id="radio", name="radio", family="write", from_atlas="radio",
         replaces="the telegraph wire",
         vanilla="minecraft:jukebox",
         note="**The first broadcast: one voice to everybody at once, with no wire and no "
              "address.** The atlas dates it Europe 1895, North America 1900, South Asia 1922, "
              "East Asia 1925. Marconi's patent is 1896 and the first transatlantic signal is "
              "1901.",
         source="the products atlas, radio"),
    # ---- THE THINGS THAT KILL, WHICH STEP 45 ALREADY OWNS ------------------------------------
    dict(id="gunpowder", name="gunpowder", family="fight", from_atlas="gunpowder",
         replaces="the spring, the counterweight and the muscle",
         vanilla="minecraft:gunpowder",
         note="**A tool row here even though step 45 owns the weapons**, because gunpowder is also "
              "the first explosive used for mining and for fireworks, and the atlas dates it China "
              "900, West Asia 1280, Europe 1350, South Asia 1400. Step 45's armoury dates the "
              "**guns**; this is the substance.",
         source="the products atlas, gunpowder"),
]


def problems():
    bad = []
    seen = set()
    A = atlas()
    for t in TOOLS:
        if t["id"] in seen:
            bad.append("duplicate tool id " + t["id"])
        seen.add(t["id"])
        if t["family"] not in FAMILIES:
            bad.append(t["id"] + " is in the family " + t["family"] + ", which does not exist")
        if "from_atlas" in t:
            if t["from_atlas"] not in A:
                bad.append(t["id"] + " reads the atlas row " + t["from_atlas"] + ", which is absent")
            if "made" in t:
                bad.append(t["id"] + " both reads the atlas and writes dates")
        elif "made" not in t:
            bad.append(t["id"] + " has no dates at all")
        if "made" in t:
            for area, year in t["made"].items():
                if area not in AREAS:
                    bad.append(t["id"] + " dates the area " + area + ", which is not real")
                if year > 3000:
                    bad.append(t["id"] + " has " + str(year) + " in " + area
                               + ", which is past the end of the world")
                if year < -3000 and not t.get("before_world"):
                    bad.append(t["id"] + " is dated " + str(year) + " in " + area
                               + ", which is before the world begins, and does not set "
                                 "before_world: the quern is the case to copy")
        if not t["note"] or len(t["note"]) < 60:
            bad.append(t["id"] + " does not say anything useful")
        if not t["source"]:
            bad.append(t["id"] + " cites nothing")

    # EVERY TOOL MUST RESOLVE TO A VANILLA ITEM OR SAY IT CANNOT - A13's rule, applied to an
    # inventory. A placeholder means "nothing in vanilla stands for this" and must be listed as
    # such rather than left to look like an id.
    for t in TOOLS:
        v = t.get("vanilla", "")
        if not v:
            bad.append(t["id"] + " names no vanilla item")
        elif v.endswith("_placeholder"):
            low = t["note"].lower()
            if "no vanilla" not in low and "nothing in vanilla" not in low:
                bad.append(t["id"] + " has no vanilla item and does not say so")

    # THE CLASS OF ERROR THIS REGISTER EXISTS TO PREVENT. A microscope cannot be older than a
    # telescope by three thousand years, and a tool cannot predate the material it is made of.
    mic = next((t for t in TOOLS if t["id"] == "microscope"), None)
    if mic and mic["made"]["WAS"] < 1500:
        bad.append("the microscope is dated before 1500: the glass-inheritance bug is back")
    tl = next((t for t in TOOLS if t["id"] == "loom_treadle"), None)
    if tl and tl["made"]["EAS"] > tl["made"]["EUR"]:
        bad.append("the treadle loom reaches Europe before China, which is backwards")
    pr = next((t for t in TOOLS if t["id"] == "printing_movable"), None)
    if pr and pr["made"]["EAS"] > pr["made"]["EUR"]:
        bad.append("movable type reaches Europe before China, which is backwards")

    # A tool with no predecessor must be one of the handful that genuinely had none.
    no_pred = [t["id"] for t in TOOLS if not t["replaces"]]
    if len(no_pred) > 6:
        bad.append(str(len(no_pred)) + " tools claim no predecessor: " + ", ".join(no_pred))
    return bad


def main():
    bad = problems()
    A = atlas()
    print("tools: %d rows over %d families and %d areas"
          % (len(TOOLS), len({t["family"] for t in TOOLS}),
             len({a for t in TOOLS for a in (t["made"] if "made" in t
                                             else A[t["from_atlas"]]["made"])})))
    read = sum(1 for t in TOOLS if "from_atlas" in t)
    print("  %d read their dates from the products atlas, %d written here with a source"
          % (read, len(TOOLS) - read))
    print("  %d have no vanilla item and say so: %s"
          % (sum(1 for t in TOOLS if t.get("vanilla", "").endswith("_placeholder")),
             ", ".join(t["id"] for t in TOOLS if t.get("vanilla", "").endswith("_placeholder"))))
    print()
    for t in TOOLS:
        years = t["made"] if "made" in t else A[t["from_atlas"]]["made"]
        eur = years.get("EUR")
        eas = years.get("EAS")
        print("  %-20s %-8s EUR=%-6s EAS=%-6s %s"
              % (t["id"], t["family"], eur, eas,
                 "atlas" if "from_atlas" in t else "written"))
    for p in bad:
        print("  PROBLEM " + p)
    print("tool_table: %d problem(s)" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
