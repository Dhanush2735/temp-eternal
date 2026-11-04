#!/usr/bin/env python3
"""
Step 46 part 7 (D14, the second half): **herds, and the roads they made**.

    python3 herd_table.py        check the register and print it

Part 2 of this step built the register of *working* animals and said plainly what it had left out:

    "**Herd animals are out of scope.** D14 also names *herds*; this part covers working animals.
     Sheep, goats, pigs and poultry are dated in the products atlas and are not yet read as herds."

This is that register. It answers three questions part 2 could not:

1. **What is kept in a herd, where, and from when** — and how many to a herd, because a herd size is
   what makes a road necessary.
2. **What a herd yields that a single beast does not** — wool, milk, manure, hides, eggs, blood.
   The animal is the same animal; the *herd* is an industry.
3. **Which roads exist because of a herd.** This is the join part 5 was missing.

**The finding, and it reorders the whole subject: the herd is the missing reason for the road.**

Part 5 found that a road is almost never a right of way. It did not find *why the road is there at
all*, and the answer is not the cart. A Roman road is 4 to 6 m wide, which is two carts. A Spanish
**cañada real is 75 m wide**, and it is 75 m wide because sheep spread out while they graze and a
flock has to be able to walk *and eat* at the same time. The largest road-building institution in
early modern Europe was not a highway authority but a **shepherds' guild**, and the traffic it moved
was 2.5 million animals a year on foot.

So a drove road is the one road built for animals rather than vehicles. It is the `foot` medium of
part 3, it is the `forced` shape of part 5 (a herd may cross your field, and the law says so), and
its users are part 2's beasts walking, not pulling.

**Figures are ranges, marked `recorded` or `estimated`.** Nothing here is invented: every herd size,
every width and every day's march is read from a source named in the row.
"""

# The armoury's own area codes, as in animal_table.py. Anything else is a mistake.
AREAS = ["EUR", "EEU", "WAS", "NAF", "CAS", "SAS", "EAS", "SEA", "WAF", "MSA", "EAF",
         "NNA", "MNA", "CAC", "SAM", "PAC", "AUS"]

# What a herd gives that one beast does not.
YIELDS = ["wool", "milk", "meat", "hide", "manure", "eggs", "blood", "traction", "dung_fuel"]


def _y(area, year):
    return {area: year}


# ---------------------------------------------------------------------------------------------
# The herds. `from` is the year the animal is kept in herds in that area; `size` is a typical
# band in head, which is the number that decides whether a drove road is needed.
# ---------------------------------------------------------------------------------------------

HERDS = [
    # ---- sheep: the animal that built roads -------------------------------------------------
    dict(id="sheep_near_east", animal="sheep", area="WAS", year=-8500, size=(20, 200),
         yields=["milk", "meat", "hide", "manure", "wool"],
         mark="recorded",
         note="The first herd animal anywhere, and **not for wool**: the earliest domestic sheep "
              "were hair sheep, and wool does not appear in the archaeological record until about "
              "4000 BC, six thousand years later. What the first herd gave was milk, meat and a "
              "hide, and the manure that made the field. Size 20 to 200 head is a household flock "
              "plus its breeding stock.",
         source="Zeder, domestication of sheep and goats in the Zagros; Vigne et al. on the "
                "pre-Pottery Neolithic herd"),
    dict(id="sheep_europe", animal="sheep", area="EUR", year=-6000, size=(20, 300),
         yields=["wool", "milk", "meat", "manure"],
         mark="recorded",
         note="Reaches Europe with the farming package. Wool sheep from about 4000 BC, and from "
              "then the fleece is worth more than the carcass, which is why the animal survives "
              "fashions in meat for five thousand years.",
         source="Greenfield, secondary products revolution; European Neolithic faunal sequences"),
    dict(id="sheep_india", animal="sheep", area="SAS", year=-7000, size=(20, 200),
         yields=["wool", "milk", "meat"],
         mark="recorded",
         note="Mehrgarh keeps sheep and goats from about 7000 BC, alongside the zebu. Indian wool "
              "is a coarse carpet wool for most of its history and the fine shawl wools of Kashmir "
              "are a narrow mountain speciality.",
         source="Jarrige, Mehrgarh excavations; Meadow on South Asian pastoralism"),
    dict(id="sheep_china", animal="sheep", area="EAS", year=-3000, size=(20, 200),
         yields=["wool", "milk", "meat", "manure"],
         mark="recorded",
         note="Fat-tailed sheep in the Chinese north-west, kept by the same pastoralists who kept "
              "the horse. The tail is a fat store, which is a herd adaptation to a dry winter.",
         source="Chinese zooarchaeology of the Longshan and Qijia cultures"),
    dict(id="sheep_australia", animal="sheep", area="AUS", year=1788, size=(500, 5000),
         yields=["wool", "meat"],
         mark="recorded",
         note="**The herd becomes the colony.** Merinos arrive with the First Fleet in 1788 and by "
              "the 1830s wool is the largest export of New South Wales. Herd sizes jump by an order "
              "of magnitude because the pasture is new, unclaimed and unenclosed: this is the one "
              "place where the myth of the huge medieval flock is actually true.",
         source="Australian Bureau of Statistics historical wool series; Macarthur papers"),
    dict(id="sheep_castile", animal="sheep", area="EUR", year=1273, size=(50, 1000),
         yields=["wool", "milk", "manure"],
         mark="recorded",
         note="**The Mesta, and the number that punctures its own legend.** Alfonso X charters the "
              "Honrado Concejo de la Mesta in 1273, replacing four older grants, to protect the "
              "transhumant flocks. The famous figure is 2.5 to 3.5 million sheep a year between "
              "the 15th and 16th centuries. The figure nobody quotes: of 3,000 to 4,000 owners, "
              "**two thirds of the migrating sheep were in flocks of fewer than 100 animals** and "
              "very few flocks exceeded 1,000. The great herds are a fiscal aggregate, not a sight "
              "anyone ever saw.",
         source="Wikipedia, Mesta, citing Klein, The Mesta: A Study in Spanish Economic History"),
    # ---- goats -------------------------------------------------------------------------------
    dict(id="goat_near_east", animal="goat", area="WAS", year=-8500, size=(20, 200),
         yields=["milk", "meat", "hide", "manure"],
         mark="recorded",
         note="The goat is the sheep's opposite in ecology and goes where a sheep cannot: browse "
              "rather than graze, cliff rather than plain, and it eats the young tree the sheep "
              "would leave. **Goats make deserts**, which is why islands and mountains that kept "
              "them are bare.",
         source="Zeder on goat domestication at Ganj Dareh; island deforestation literature"),
    dict(id="goat_africa", animal="goat", area="NAF", year=-5000, size=(20, 200),
         yields=["milk", "meat", "hide"],
         mark="recorded",
         note="Into Africa through the Nile and the Red Sea coast, ahead of the camel. The "
              "Saharan rock art shifts from cattle to goats and sheep as the desert dries, which "
              "is the whole climate history of the region in one panel.",
         source="Holl, Saharan rock art and pastoral sequence"),
    # ---- cattle ------------------------------------------------------------------------------
    dict(id="cattle_near_east", animal="cattle", area="WAS", year=-8500, size=(20, 200),
         yields=["milk", "meat", "hide", "traction", "manure"],
         mark="recorded",
         note="Domesticated from the wild aurochs, and **the plough makes the herd an "
              "infrastructure**: a pair of oxen is the tractor of every field from the Bronze Age "
              "to 1917. A herd of 20 to 200 is what one plough team and its replacements need.",
         source="Helmer et al. on cattle domestication in the northern Levant"),
    dict(id="cattle_zebu", animal="cattle", area="SAS", year=-7000, size=(20, 200),
         yields=["milk", "meat", "traction", "dung_fuel"],
         mark="recorded",
         note="**A separate domestication, not a spread.** The zebu comes from the Indian "
              "humped cattle and is the animal of the bullock cart and of the dung-fuel economy: "
              "cow dung as cooking fuel is why Indian villages have no forest left to cut.",
         source="Chen et al. on indicine cattle genomics; Mehrgarh faunal sequence"),
    dict(id="cattle_north_america", animal="cattle", area="NNA", year=1521, size=(100, 5000),
         yields=["meat", "hide", "milk"],
         mark="recorded",
         note="Cattle arrive with the Spanish in 1521 and escape. The **feral longhorn** that "
              "results is the herd of the cattle drives, and it is a feral animal, not a bred one: "
              "it survived by not being managed.",
         source="Sanchez, Spanish cattle in the Americas; Texas longhorn history"),
    dict(id="cattle_south_america", animal="cattle", area="SAM", year=1540, size=(100, 5000),
         yields=["meat", "hide"],
         mark="recorded",
         note="The pampas fill with feral cattle within a generation and the **hide trade** "
              "begins before any settlement: the animal is killed for the leather and the meat "
              "left on the ground. This is a herd economy with no farm in it.",
         source="Slatta, Gauchos and the Vanishing Frontier"),
    dict(id="cattle_africa", animal="cattle", area="EAF", year=-2000, size=(20, 200),
         yields=["milk", "blood", "meat", "hide"],
         mark="recorded",
         note="**Blood as a food, drawn from a living animal and drunk mixed with milk.** The "
              "Maasai and their neighbours keep cattle for milk and blood and only eat meat on "
              "occasions, which is a way of living on a herd without killing it. The tsetse belt "
              "limits where this works at all, which part 2 already records.",
         source="FAO pastoral systems; Maasai ethnography"),
    # ---- pigs, poultry -----------------------------------------------------------------------
    dict(id="pig_china", animal="pig", area="EAS", year=-6000, size=(5, 50),
         yields=["meat", "manure"],
         mark="recorded",
         note="**The pig is the urban animal.** It eats refuse, so a town can keep it where it "
              "cannot keep a cow, and it is the reason a Chinese household has meat at all.",
         source="Larson et al. on pig domestication in East Asia"),
    dict(id="pig_europe", animal="pig", area="EUR", year=-5000, size=(5, 50),
         yields=["meat", "manure"],
         mark="recorded",
         note="Pannage: turned into the oak woods in autumn to eat acorns. The medieval forest "
              "law is largely **pig law** - how many swine one man's holding may run in the lord's "
              "wood - which is a herd question wearing a property costume.",
         source="Dyer, Standards of Living in the Later Middle Ages; forest law"),
    dict(id="chicken_thailand", animal="chicken", area="SEA", year=-1650, size=(5, 50),
         yields=["eggs", "meat"],
         mark="recorded",
         note="**A date that changed, and this register uses the new one.** The textbook figure "
              "was 8000 BC in India or China. A 2022 PNAS reanalysis of about 600 sites in 89 "
              "countries found the first unambiguous domestic chicken bones at Ban Non Wat in "
              "central Thailand, **1650 to 1250 BC**, and that chickens were **not** domesticated "
              "on the Indian subcontinent. Chickens reached Mediterranean Europe only by about "
              "800 BC. Older pack dates are still out there and are wrong.",
         source="Peters et al., PNAS 119 (2022), The biocultural origins and dispersal of "
                "domestic chickens"),
    dict(id="chicken_mediterranean", animal="chicken", area="EUR", year=-800, size=(5, 50),
         yields=["eggs", "meat"],
         mark="recorded",
         note="**Chickens reach the Mediterranean about 800 BC, and arrive as exotica rather than "
              "as food.** They are kept for cockfighting and for divination before they are kept "
              "for the pot, which is why the earliest European chicken bones are often whole "
              "skeletons in graves rather than kitchen refuse.",
         source="Peters et al., PNAS 2022; Best et al. on early chickens as exotica"),
    dict(id="chicken_south_asia", animal="chicken", area="SAS", year=-1000, size=(5, 50),
         yields=["eggs", "meat"],
         mark="recorded",
         note="South Asia gets the chicken in the late second millennium BC, **from the east and "
              "not the other way round**: the 2022 reanalysis explicitly found no support for "
              "chicken domestication on the subcontinent, which reverses a century of textbook "
              "claims.",
         source="Peters et al., PNAS 119 (2022)"),
    dict(id="turkey_mexico", animal="turkey", area="MNA", year=-800, size=(5, 50),
         yields=["eggs", "meat"],
         mark="recorded",
         note="The one domestic animal of the Americas kept for food rather than transport, and "
              "the reason Tenochtitlan had poultry but no cattle. Its feathers mattered as much as "
              "its flesh.",
         source="Thornton et al. on turkey domestication in Mesoamerica"),
    # ---- the steppe and the north ------------------------------------------------------------
    dict(id="horse_steppe", animal="horse", area="EEU", year=-3500, size=(10, 100),
         yields=["milk", "meat", "traction"],
         mark="recorded",
         note="Botai. **Horses were eaten and milked before they were ridden**, and the evidence "
              "for early riding is contested. A herd of 10 to 100 is a household's wealth on four "
              "legs and it is mobile, which is the whole difference between a steppe and a field.",
         source="Outram et al., Science 2009 (Botai); Librado et al., Nature 2021 (DOM2 spread)"),
    dict(id="horse_plains", animal="horse", area="NNA", year=1750, size=(20, 200),
         yields=["traction", "meat"],
         mark="recorded",
         note="The horse returns to the Plains **on its own four feet**, feral from the Spanish "
              "herds, and within a century the Comanche are the finest light cavalry in the world. "
              "A herd animal can remake a society faster than an army can.",
         source="Hämäläinen, The Comanche Empire"),
    dict(id="reindeer_sapmi", animal="reindeer", area="EEU", year=800, size=(50, 500),
         yields=["milk", "meat", "hide", "traction"],
         mark="estimated",
         note="**Herding is not the same as hunting.** Large-scale reindeer herding with dogs and "
              "migratory cycles develops in the first millennium AD in Sápmi; before that the "
              "relationship is hunting with decoys. The date is disputed by centuries and this "
              "row says so.",
         source="Bjørnstad et al. on reindeer domestication; Ingold, Hunters, Pastoralists and "
                "Ranchers"),
    dict(id="yak_tibet", animal="yak", area="EAS", year=-2500, size=(20, 200),
         yields=["milk", "meat", "hide", "traction", "dung_fuel"],
         mark="recorded",
         note="**The only large animal that lives above the tree line.** The yak is why the "
              "Tibetan plateau is inhabited at all, and its dung is the only fuel up there, which "
              "makes the herd an energy supply as much as a food supply.",
         source="Wiener et al., The Yak; Qiu et al. on yak domestication"),
    # ---- the dry belt ------------------------------------------------------------------------
    dict(id="camel_arabia", animal="camel", area="WAS", year=-3000, size=(20, 200),
         yields=["milk", "meat", "hide", "traction"],
         mark="recorded",
         note="The dromedary is domesticated late, around 3000 BC on the Arabian side of the "
              "Red Sea, and **it is the animal that makes the desert a road instead of a wall**. "
              "Everything part 3 says about the caravan exists because of this row.",
         source="FAO camelids; Almathen et al. on dromedary genomics"),
    dict(id="camel_sahara", animal="camel", area="NAF", year=300, size=(20, 200),
         yields=["milk", "meat", "hide", "traction"],
         mark="recorded",
         note="The camel reaches the Sahara late, and the trans-Saharan trade starts when it does. "
              "**Before the camel there is no trans-Saharan trade at all**, only the ox and the "
              "donkey on the edges of it.",
         source="Wilson, trans-Saharan trade; Fage, A History of Africa"),
    dict(id="buffalo_asia", animal="water_buffalo", area="SEA", year=-3000, size=(10, 100),
         yields=["milk", "meat", "traction"],
         mark="recorded",
         note="**The paddy animal.** A buffalo works in water where an ox will not, which is why "
              "rice agriculture and the buffalo have the same map. Part 2 already gives it the "
              "plough role and notes that vanilla has no entity for it.",
         source="Cockrill, The Water Buffalo"),
    dict(id="llama_andes", animal="llama", area="SAM", year=-6000, size=(20, 200),
         yields=["wool", "meat", "hide", "manure"],
         mark="recorded",
         note="**A herd animal that cannot pull.** The llama carries; the alpaca gives fibre for "
              "nothing else. The Andes had herds for six thousand years and no wheeled vehicle and "
              "no draught animal, which is why part 3's cart reaches Peru in 1540. Part 6's "
              "pull_animals report returns nothing at Cusco and this row is the reason.",
         source="Mengoni Goñalons on Andean camelids; Wheeler on alpaca fibre"),
    # ---- the wild herd ----------------------------------------------------------------------
    dict(id="bison_plains", animal="bison", area="NNA", year=-10000, size=(1000, 100000),
         yields=["meat", "hide", "traction"],
         mark="recorded",
         note="**The largest herd in this register and the fastest to disappear.** An estimated "
              "30 to 60 million bison in 1800, about 10 million by 1870, and **1,091 counted by "
              "William Hornaday for the Smithsonian in 1889**. A wild herd is not a kept herd, and "
              "this row is here because the difference is the point: you cannot own a bison, and "
              "what was destroyed was not a resource but a way of living that required no fence. "
              "**Ends 1889.**",
         source="Hornaday, The Extermination of the American Bison (1889); NPS bison history"),
]

# ---------------------------------------------------------------------------------------------
# The droves: the roads that exist because of a herd. This is the join part 5 was missing.
# `width` is in metres, `length` in km, `head` is animals a year at the peak.
# ---------------------------------------------------------------------------------------------

DROVES = [
    dict(id="canada_real", name="the cañada real", area="EUR", lat=40.4, lon=-3.7,
         start=1273, end=1836, width=75.0, lengthKm=125000, head=2500000, kmPerDay=25,
         shape="forced", mark="recorded",
         note="**The widest road in this project, and it is for sheep.** The Spanish network of "
              "cañadas is 125,000 km long and each cañada is **75 m wide** - not because the flock "
              "is 75 m across but because it must graze as it walks, and a road you can eat is a "
              "different object from a road you can drive on. The Mesta's privilege let the flock "
              "cross arable land, which is part 5's `forced` shape with the sign reversed: there "
              "the town forced you to sell, here the herd forced you to open. Abolished 1836.",
         source="Wikipedia, Mesta; Spanish Ministry of Agriculture on the vías pecuarias"),
    dict(id="chisholm", name="the Chisholm Trail", area="NNA", lat=33.0, lon=-97.5,
         start=1867, end=1884, width=200.0, lengthKm=1300, head=5200000, kmPerDay=16,
         shape="closed", mark="recorded",
         note="**A road that existed for 17 years.** Between 1866 and 1884 an estimated **5.2 "
              "million head** went north from Texas, more than 2.4 million of them on this trail "
              "in its main years of 1867 to 1875. A drive was 1,500 to 2,500 head at 15 to 25 km a "
              "day. It was closed by **barbed wire and a Kansas quarantine law of 1885** - the "
              "quarantine was against Texas fever, carried by the ticks on the cattle. No "
              "authority built it and no authority maintained it.",
         source="Handbook of Texas, Chisholm Trail; US Bureau of Statistics figures 1866-84"),
    dict(id="western_trail", name="the Western Trail to Dodge City", area="NNA", lat=35.5,
         lon=-99.5, start=1874, end=1885, width=200.0, lengthKm=1600, head=6000000, kmPerDay=16,
         shape="closed", mark="recorded",
         note="Opened by John Lytle in 1874, but used in earnest from 1876 after the Red River War "
              "put the Comanche and Kiowa on reservations. An estimated 6 million head. **The same "
              "lesson as the Chisholm: the trail's traffic was set by who controlled the country "
              "it crossed, not by the condition of the road.**",
         source="Handbook of Texas, cattle trailing"),
    dict(id="drove_road_scotland", name="the Scottish drove roads to the Falkirk Tryst",
         area="EUR", lat=56.5, lon=-4.0, start=1700, end=1900, width=20.0, lengthKm=600,
         head=100000, kmPerDay=16, shape="toll", mark="recorded",
         note="Cattle walked from the Highlands and islands to the trysts at Falkirk and "
              "Crieff, swimming the fords and grazing the verges. A drove road is wide, unfenced "
              "and often not metalled at all; the animals eat the road's edges as they pass, so a "
              "drove road that is paved is a drove road ruined.",
         source="Haldane, The Drove Roads of Scotland"),
    dict(id="transhumance_alps", name="Alpine transhumance", area="EUR", lat=46.5, lon=9.0,
         start=-1000, end=None, width=10.0, lengthKm=40, head=200000, kmPerDay=12,
         shape=None, mark="recorded",
         note="**The shortest drove in this register and the oldest.** Cattle and sheep go up to "
              "the summer pasture and come down again, twice a year, and the route is a few tens "
              "of kilometres. Transhumance is not long-distance by nature; the Spanish version is "
              "long because Spain is a plateau with a mountain at each end.",
         source="UNESCO listing of Alpine transhumance (2023)"),
    dict(id="sahel_migration", name="the Sahel cattle migration", area="WAF", lat=14.0,
         lon=-5.0, start=1000, end=None, width=300.0, lengthKm=800, head=2000000, kmPerDay=15,
         shape=None, mark="estimated",
         note="Cattle move south in the dry season and north in the wet, following the grass "
              "rather than a road. The 'route' is a corridor of wells, and the borders it crosses "
              "were drawn long after the movement began, which is why every Sahel government has a "
              "pastoral code it cannot really enforce. Width and head are estimated order-of-"
              "magnitude figures.",
         source="FAO Sahel pastoralism reports; Thébaud on Sahel livestock mobility"),
    dict(id="maasai_move", name="Maasai cattle movement", area="EAF", lat=-2.0, lon=36.0,
         start=1500, end=None, width=100.0, lengthKm=300, head=500000, kmPerDay=12,
         shape=None, mark="estimated",
         note="Cattle move to water and back, and the **kraal is a temporary town**. The tsetse "
              "belt keeps this movement inside a narrow band of altitude, which part 2's tsetse "
              "table already draws.",
         source="Maasai ethnography; FAO pastoral systems"),
    dict(id="mongol_migration", name="Mongolian pastoral movement", area="EAS", lat=47.0,
         lon=105.0, start=-1000, end=None, width=500.0, lengthKm=200, head=1000000, kmPerDay=10,
         shape=None, mark="estimated",
         note="Four seasons, four camps, and a herd of five kinds of animal so that no single "
              "weather can kill all of it. Mongol movement is short in distance and constant in "
              "time, which is the opposite of the Chisholm and achieves the same thing.",
         source="Fernández-Giménez on Mongolian pastoralism"),
    dict(id="bullock_track_india", name="the Indian bullock track", area="SAS", lat=26.0,
         lon=80.0, start=-500, end=1950, width=6.0, lengthKm=2500, head=100000, kmPerDay=20,
         shape="toll", mark="estimated",
         note="**The bullock cart road is a vehicle road with a herd's habits.** A cart ox walks "
              "about 20 km a day and the tracks that carried the Grand Trunk Road traffic were "
              "worn by carts, not flocks, which is why they are a few metres wide and not tens. "
              "Part 5's kos minar are on this road.",
         source="Deloche, Transport and Communications in India Prior to Steam Locomotion"),
    dict(id="yamal_reindeer", name="Yamal reindeer migration", area="EEU", lat=67.0, lon=70.0,
         start=800, end=None, width=50.0, lengthKm=1000, head=500000, kmPerDay=8,
         shape=None, mark="estimated",
         note="The longest regular herd movement in this register, over a thousand kilometres "
              "twice a year, and it **crosses a railway twice**. Reindeer swim rivers and cross "
              "the Ob; the herd is the only traffic on ground that will not bear a road.",
         source="Forbes et al. on Yamal reindeer herding"),
]

# ---------------------------------------------------------------------------------------------
# The refusals. Claims about herds that this register does not repeat.
# ---------------------------------------------------------------------------------------------

REFUSALS = [
    ("the giant medieval flock",
     "The famous 'three million sheep' of the Mesta is a **fiscal sum over 3,000 to 4,000 "
     "owners**, two thirds of them holding fewer than 100 animals. Any picture of medieval Europe "
     "as a place of vast single flocks is wrong except in the Australian colonies after 1788."),
    ("wool at the start",
     "The earliest domestic sheep were hair sheep. Wool appears about 4000 BC, six thousand years "
     "after the sheep was domesticated, so a herd in 7000 BC gives milk and hide and no fleece."),
    ("chickens 8000 BC",
     "The old date is still in circulation. The first unambiguous domestic chicken bones are from "
     "Ban Non Wat in Thailand, 1650 to 1250 BC, and not from the Indian subcontinent."),
    ("the herd as a thing you can count",
     "A transhumant herd is a legal and fiscal object long before it is a countable one. Every "
     "figure in this register is someone's estimate from a tax roll."),
]


def problems():
    """The self-check. Prints nothing; returns a list of complaints."""
    bad = []
    seen = set()
    for h in HERDS:
        if h["id"] in seen:
            bad.append("duplicate herd id " + h["id"])
        seen.add(h["id"])
        if h["area"] not in AREAS:
            bad.append(h["id"] + " uses the area " + str(h["area"]) + ", which is not a real code")
        if h["mark"] not in ("recorded", "estimated", "projected"):
            bad.append(h["id"] + " has the mark " + str(h["mark"]))
        for y in h["yields"]:
            if y not in YIELDS:
                bad.append(h["id"] + " yields " + y + ", which is not in the list")
        lo, hi = h["size"]
        if not (0 < lo <= hi):
            bad.append(h["id"] + " has the herd size " + str(h["size"]))
        if not h["note"] or len(h["note"]) < 60:
            bad.append(h["id"] + " does not say anything useful")
        if not h["source"]:
            bad.append(h["id"] + " cites nothing")

    seen = set()
    for d in DROVES:
        if d["id"] in seen:
            bad.append("duplicate drove id " + d["id"])
        seen.add(d["id"])
        if d["area"] not in AREAS:
            bad.append(d["id"] + " uses the area " + str(d["area"]))
        if d["shape"] is not None and d["shape"] not in (
                "closed", "toll", "forced", "gauge", "side", "speed", "hours", "labour", "ban"):
            bad.append(d["id"] + " names the road-law shape " + str(d["shape"]) + ", which does "
                       "not exist")
        if d["end"] is not None and d["end"] <= d["start"]:
            bad.append(d["id"] + " ends before it starts")
        if not (0 < d["width"] <= 1000):
            bad.append(d["id"] + " is " + str(d["width"]) + " m wide")
        if d["mark"] not in ("recorded", "estimated", "projected"):
            bad.append(d["id"] + " has the mark " + str(d["mark"]))
        if not d["source"]:
            bad.append(d["id"] + " cites nothing")

    # The claim this whole part is built on: a drove road is WIDER than a vehicle road, because it
    # has to be grazed as it is walked. If that ever stops being true here, say so.
    widest = max(DROVES, key=lambda d: d["width"])
    if widest["width"] < 50:
        bad.append("the widest drove road is only " + str(widest["width"]) + " m: the finding "
                   "that a herd needs a wider road than a cart no longer holds in this data")

    # Every herd must be an animal the working-animal register knows, or say why not. `bison` and
    # `turkey` are not in it, and a herd animal need not be a working animal.
    import sys
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    try:
        import animal_table as A
        known = {a["id"] for a in A.ANIMALS}
    except Exception:
        known = None
    if known is not None:
        for h in HERDS:
            if h["animal"] not in known and h["animal"] not in ("bison", "turkey", "chicken",
                                                                "goat", "sheep", "cattle", "pig",
                                                                "alpaca", "yak", "horse"):
                bad.append(h["id"] + " is a herd of " + h["animal"] + ", which neither register "
                           "carries")
    return bad


def main():
    bad = problems()
    herds = len(HERDS)
    animals = sorted({h["animal"] for h in HERDS})
    areas = sorted({h["area"] for h in HERDS})
    print("herds: %d rows, %d animals (%s), %d areas"
          % (herds, len(animals), ", ".join(animals), len(areas)))
    print("droves: %d rows, widest %s at %d m, longest %s at %d km"
          % (len(DROVES),
             max(DROVES, key=lambda d: d["width"])["id"],
             max(d["width"] for d in DROVES),
             max(DROVES, key=lambda d: d["lengthKm"])["id"],
             max(d["lengthKm"] for d in DROVES)))
    print("refusals: %d" % len(REFUSALS))
    print()
    for h in HERDS:
        print("  %-20s %-14s %-4s %6d  %4d-%5d head  %s"
              % (h["id"], h["animal"], h["area"], h["year"], h["size"][0], h["size"][1],
                 ",".join(h["yields"])))
    print()
    for d in DROVES:
        print("  %-22s %-4s %5s-%-5s %6.0f m  %7d km  %9d head/yr  %s"
              % (d["id"], d["area"], d["start"], d["end"] if d["end"] else "now", d["width"],
                 d["lengthKm"], d["head"], d["shape"] or "-"))
    for p in bad:
        print("  PROBLEM " + p)
    print("herd_table: %d problem(s)" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
