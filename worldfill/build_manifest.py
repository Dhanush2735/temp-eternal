#!/usr/bin/env python3
"""Step 26 (systems A3, A7, K4): the data manifest and the credits.

Every data file of the mod gets one line in data/eternalengine/eternal/manifest.json: its size, its SHA-256, how many
rows it holds, what it is for, where it comes from, under which licence, whether its answers are recorded or
estimated (the A5 mark), which script builds it, and the pack it belongs to ("core": everything ships inside the mod,
decision 5 of the systems plan). The game checks the manifest on /ee check all (com.eternalengine.data.DataManifest):
every shipped file present, the same size and hash, a licence for each.

The credits file (eternal/src/main/resources/DATA_CREDITS.md, inside the mod's jar, never shown in play) is written
from the same table, so a new source cannot be added without its credit.

    python3 build_manifest.py           write manifest.json and DATA_CREDITS.md
    python3 build_manifest.py --check   compare them with the files (exit 1 when out of date)

Run it last, after any script that changes data (fix_history_data.py, build_tiles.py, ...).
"""
import gzip
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.normpath(os.path.join(HERE, "..", "eternal"))
DATA = os.path.join(MOD, "src", "main", "resources", "data", "eternalengine", "eternal")
MANIFEST = os.path.join(DATA, "manifest.json")
CREDITS = os.path.join(MOD, "src", "main", "resources", "DATA_CREDITS.md")
GRADLE = os.path.join(MOD, "build.gradle")

# --------------------------------------------------------------------------- sources and their licences
SOURCES = {
    "cliopatria": ("Cliopatria v0.2.1, Seshat Global History Databank (state borders 3400 BC to 2024)",
                   "CC BY 4.0", "credit Seshat / Cliopatria"),
    "wikipedia": ("English Wikipedia (dump 2026-10-01; decade and century pages, 2023 revisions)",
                  "CC BY-SA 4.0", "credit Wikipedia contributors; a file built from Wikipedia text stays CC BY-SA 4.0"),
    "wikidata": ("Wikidata (query.wikidata.org and the QLever endpoint of the University of Freiburg)",
                 "CC0 1.0", "nothing required"),
    "laouenan": ("Laouenan, M. et al. A cross-verified database of notable people, 3500BC-2018AD. Scientific Data 9, "
                 "290 (2022); Sciences Po doi:10.21410/7E4/RDAG3O", "CC BY-SA 4.0",
                 "credit the authors; the file stays CC BY-SA 4.0"),
    "pleiades": ("Pleiades, a community-built gazetteer and graph of ancient places (pleiades.stoa.org)", "CC BY 3.0",
                 "credit Pleiades"),
    "chgis": ("CHGIS, Version 6. Fairbank Center for Chinese Studies (Harvard) and Center for Historical Geographical "
              "Studies (Fudan), 2016; doi:10.7910/DVN/Q9VOF5", "CC0 1.0", "nothing required; citation appreciated"),
    "reba": ("Reba, M., Reitsma, F. & Seto, K. C. Spatializing 6,000 years of global urbanization from 3700 BC to "
             "AD 2000. Scientific Data 3, 160034 (2016)", "CC BY 4.0", "credit the authors"),
    "hyde": ("HYDE 3.2.1 (Klein Goldewijk, K. et al. Anthropogenic land use estimates for the Holocene - HYDE 3.2. "
             "Earth System Science Data 9, 927-953 (2017)); DANS doi:10.17026/DANS-25G-GEZ3",
             "CC0 1.0 (DANS record; the release readme says CC BY 3.0)", "credit HYDE"),
    "imperial_gazetteer": ("Imperial Gazetteer of India, Hyderabad State (1909)", "public domain", "nothing required"),
    "keynes": ("Keynes, J. M. Indian Currency and Finance (Macmillan, 1913)", "public domain",
               "nothing required; out of copyright"),
    "india_banking": ("Banking Enquiry Committee and the histories of the Presidency Banks of Bengal, Bombay and "
                      "Madras (1806-1935)", "public domain", "nothing required"),
    "siddham": ("Siddham Epigraphic Archive (siddham.network)", "free with attribution", "credit Siddham"),
    "noaa": ("NOAA NCEI Global Significant Earthquake, Tsunami and Volcano databases (doi:10.7289/V5TD9V7K, "
             "10.7289/V5PN93H7, 10.7289/V5JW8BSH)", "public domain (US government work)", "cite NOAA NCEI"),
    "ibtracs": ("NOAA NCEI International Best Track Archive for Climate Stewardship (IBTrACS) v04r01 (Knapp, K. R. et al. "
                "Bulletin of the American Meteorological Society 91, 363-376 (2010); Gahtan, J. et al. NOAA NCEI "
                "doi:10.25921/82ty-9e16)", "public domain (US government work)", "cite IBTrACS (Knapp et al. 2010)"),
    "owid": ("Our World in Data, Literacy rate (cross-country-literacy-rates): UNESCO (1953, 1957), Buringh and van "
             "Zanden (2009), van Zanden et al. (2014), UNESCO Institute for Statistics", "CC BY 4.0",
             "credit Our World in Data and the sources it names"),
    "allenunger": ("Allen, R. C. and Unger, R. W., The Allen-Unger Global Commodity Prices Database (2019); "
                   "DANS doi:10.17026/dans-zsu-xavf (deposited by the International Institute of Social History)",
                   "CC BY-NC 4.0", "credit Allen and Unger; the licence is non-commercial"),
    "maddison": ("Maddison Project Database, version 2023 (Bolt, J. and van Zanden, J. L., Groningen Growth and "
                 "Development Centre)", "CC BY 4.0", "credit Bolt and van Zanden (2024)"),
    "natural_earth": ("Natural Earth, Admin 0 - Countries, 1:10m (naturalearthdata.com)", "public domain",
                      "nothing required; credit Natural Earth appreciated"),
    "chat": ("CHAT, the Cross-country Historical Adoption of Technology dataset (Comin, D. and Hobijn, B., NBER working "
             "paper 15319, 2009; data.nber.org; datahub.io core/historical-adoption-of-technology)",
             "public domain (ODC-PDDL)", "cite Comin and Hobijn (2009)"),
    "gvp": ("Smithsonian Global Volcanism Program, Volcanoes of the World v5", "free use with citation",
            "cite the Smithsonian GVP"),
    "plague": ("Plague outbreaks 1339-1900: Biraben (1975), digitised by Buentgen et al. 2012 and Atanasiu et al. "
               "2008, merged by Schmid et al. 2015 (PNAS 112:3020), Zenodo record 14973", "EPL-1.0",
               "credit Schmid et al. 2015 and the original compilers"),
    "ucdp": ("UCDP Georeferenced Event Dataset (GED) Global version 25.1, Uppsala Conflict Data Program (Sundberg & "
             "Melander 2013; Davies, Pettersson & Oeberg 2025)", "CC BY 4.0", "credit UCDP and cite the two papers"),
    "glottolog": ("Glottolog 5.3 (Hammarstroem, Forkel, Haspelmath & Bank)", "CC BY 4.0", "credit Glottolog"),
    "sil": ("SIL International, ISO 639-3 code tables (living status, ISO 639-1 codes)",
            "free to use under SIL's terms of use", "credit SIL"),
    "cow": ("Correlates of War World Religion Data v1.1 (Maoz, Z. & Henderson, E. A. The World Religion Dataset, "
            "1945-2010. International Interactions 39, 265-291 (2013))", "free to use with citation",
            "cite Maoz & Henderson 2013"),
    "itinere": ("Itiner-e (de Soto, P. et al. A high-resolution dataset of roads of the Roman Empire. Scientific Data "
                "12, 1731 (2025); Zenodo doi:10.5281/zenodo.17122148)", "CC BY 4.0", "credit Itiner-e"),
    "archaeoglobe": ("ArchaeoGLOBE Project, Science 365, 897-902 (2019); Harvard Dataverse doi:10.7910/DVN/CNCANQ "
                     "and doi:10.7910/DVN/CQWUBI", "CC0 1.0", "nothing required (credit appreciated)"),
    "khoury2016": ("Khoury, C. K. et al., 'Origins of food crops connect countries worldwide', "
                   "Proceedings of the Royal Society B 283: 20160792 (2016), supplementary tables S1 "
                   "and S2; Dryad doi:10.5061/dryad.s08t2, Zenodo record 5006466",
                   "CC0 1.0", "credit the paper and the dataset"),
    "osm": ("OpenStreetMap (place names and points of cities, towns, villages and hamlets, via Overpass)",
            "ODbL 1.0", "credit \"(c) OpenStreetMap contributors\"; the files built from it stay under the ODbL"),
    "census": ("Census of India and the district gazetteers (each row names its own census or gazetteer)",
               "public record (government statistics)", "credit the census named in each row"),
    "meeus": ("Meeus, J. Astronomical Algorithms, 2nd ed. (Willmann-Bell, 1998), chapters 25 and 49: the series for "
              "the sun's apparent longitude and the times of the new moon, implemented in the mod to compute the "
              "Chinese calendar", "nothing of the book ships: the algorithms are implemented, no tables are copied",
              "cite Meeus where the numbers are quoted"),
    "britannica": ("Britannica (britannica.com: 'Germ theory', 'History of Public Health: A Timeline')",
                  "free use with attribution", "credit Britannica"),
    "fao": ("Food and Agriculture Organization of the United Nations (fao.org): working-capacity figures for camels and other draught animals", "FAO content is copyright FAO unless stated; the figures here are quoted summary values with credit to FAO", "commercial"),
    "who": ("World Health Organization (who.int: the history of smallpox vaccination; the Global Commission for "
            "the Certification of Smallpox Eradication, final report 1980)",
            "free use with attribution", "credit WHO"),
    "own": ("Eternal Engine's own work: rules, estimates, cards and tables written for the mod", "MIT (the mod's licence)",
            "nothing beyond the mod's licence"),
}
NON_COMMERCIAL = re.compile(r"(?i)\bNC\b|non-?commercial")

# --------------------------------------------------------------------------- what each file is
# (pattern, sources, role, mark, builder). The first pattern that matches the path wins.
FILES = [
    (r"history/world_rulers\.json\.gz", ["cliopatria", "wikidata", "own"],
     "who ruled each half-degree square of the world, 3400 BC to 2026", "mixed", "build_rulers.py, fix_history_data.py"),
    (r"history/deccan_rulers\.json\.gz", ["cliopatria", "own"], "who ruled each place of the Deccan, in detail", "mixed",
     "build_deccan_rulers.py, fix_history_data.py"),
    (r"history/polity_facts\.json\.gz", ["wikipedia", "cliopatria", "wikidata", "cow", "own"],
     "each state's heads of state and government, languages, faiths and capital", "mixed",
     "build_polity_facts.py, fill_rulers.py, fix_history_data.py"),
    (r"history/famous_people\.json\.gz", ["wikipedia", "laouenan", "wikidata", "cliopatria"],
     "famous people of every land (the master; the game reads famous_people.tiles)", "recorded",
     "build_people.py, build_notable_people.py, fill_famous_gaps.py, fix_history_data.py"),
    (r"history/famous_people\.tiles", ["wikipedia", "laouenan", "wikidata", "cliopatria"],
     "famous people of every land, in tiles by land and century", "recorded", "build_tiles.py"),
    # Step 41 (D11, C11). Both are QLever exports of Wikidata and nothing else, so both are
    # "recorded": a row is what the source says, even when the source is thin.
    (r"history/kinship\.json\.gz", ["wikidata"],
     "step 41 (C11): who was whose parent, who married whom, what house they were of, and the "
     "families that held one office across generations - derived, not asserted",
     "recorded", "fetch_step41.py, read_cards.py, build_kinship.py"),
    (r"history/presence\.json\.gz", ["wikidata", "wikipedia", "laouenan", "cliopatria"],
     "step 41 (D11): where a famous person was, in which years, and why - born, died, studied, "
     "worked, served, joined, founded, lived (the master; the game reads presence.tiles)",
     "recorded", "fetch_step41.py, read_cards.py, build_presence.py"),
    (r"history/presence\.tiles", ["wikidata", "wikipedia", "laouenan", "cliopatria"],
     "step 41 (D11): where a famous person was, in tiles by the box of the place and by the person",
     "recorded", "build_tiles.py"),
    (r"history/events_world\.json|history/events_wikidata_more\.json\.gz", ["wikidata"],
     "dated events with a place: battles, sieges, disasters", "recorded", "build_events.py, fix_history_data.py"),
    (r"history/events_wikipedia\.json\.gz", ["wikipedia", "wikidata"],
     "events of the Wikipedia year, decade and century pages", "recorded", "build_wikipedia_events.py, fix_history_data.py"),
    (r"history/events_wikipedia_regional\.json\.gz|history/events_wikipedia_decades\.json\.gz",
     ["wikipedia", "cliopatria", "hyde"], "events of a whole state or region, placed at its people's centre",
     "mixed", "build_regional.py, build_decades.py, fix_history_data.py"),
    (r"history/events_wars\.json\.gz", ["wikipedia", "cliopatria"], "wars, over the lands of their sides", "mixed",
     "build_wars.py, fix_history_data.py"),
    (r"history/events_hazards\.json\.gz", ["wikipedia", "noaa", "gvp", "plague"],
     "epidemics, famines, earthquakes, eruptions, tsunamis and floods", "recorded", "build_hazards.py, fix_history_data.py"),
    (r"history/disaster_supplement\.json\.gz", ["wikipedia", "own"],
     "the great disasters the scraped hazards pack misses, written by hand", "mixed",
     "build_disasters.py"),
    (r"history/events_ucdp\.json\.gz", ["ucdp"], "organised violence 1989 to 2024", "recorded", "build_ucdp.py"),
    (r"history/deccan_events\.json\.gz", ["imperial_gazetteer", "siddham"], "events of the Deccan", "recorded",
     "hand-written from the sources, fix_history_data.py"),
    (r"history/places_pleiades\.json\.gz", ["pleiades"], "ancient places", "mixed", "build_pleiades.py"),
    (r"history/places_chgis\.json\.gz", ["chgis"], "Chinese county seats through history", "recorded", "build_chgis.py"),
    (r"history/places_reba\.json\.gz", ["reba"], "cities 3700 BC to AD 2000", "recorded", "build_reba.py"),
    (r"history/present_.*\.json\.gz", ["osm", "own"], "today's named places; their founding years are estimated",
     "estimated", "Overpass export; years by SettlementYearEstimator"),
    (r"history/local_languages\.json\.gz", ["glottolog", "sil"], "the language of the people of each place",
     "recorded", "build_languages.py, fix_history_data.py"),
    (r"history/trade_routes\.json\.gz", ["itinere", "wikipedia"], "roads and trade routes and their towns", "mixed",
     "build_trade_routes.py"),
    (r"history/ways_of_life\.json\.gz", ["archaeoglobe"], "how people lived: foraging, farming, herding, cities",
     "estimated", "build_ways_of_life.py"),
    (r"history/(afro_islamic|americas|borders|china|egypt|events|indus|mediterranean|mesopotamia|south_asia)\.json",
     ["wikipedia", "own"], "hand-made region pack of well-known sites and events", "mixed", "hand-written"),
    (r"history/(index\.json|README\.md|ATTRIBUTION\.md)", ["own"], "list of the history packs, and their notes",
     "recorded", "hand-written"),
    (r"population/hyde_density\.bin\.gz", ["hyde"], "how many people lived on each square, 10000 BC to 2026",
     "estimated", "build_hyde.py"),
    (r"population/population_south_asia\.json", ["census"], "census figures of South Asian towns", "recorded",
     "hand-written from the censuses"),
    (r"economy/money_table\.json", ["wikipedia", "own"], "the money of every place and year, and its pieces",
     "mixed", "build_money_table.py, money_world.py, fix_history_data.py"),
    (r"economy/products_world\.json", ["wikipedia", "own"],
     "the product atlas: 529 products in 14 families, each with the year it is first made and "
     "first brought in each of the 17 areas of the ways-of-life survey. 132 rows are part B, "
     "hand-written estimates from the history of each product; 397 are part C (step 44), whose "
     "years are derived from the technology atlas (130 technologies x 258 countries), a parent "
     "product, and the natural range of a material - no part C year was written by hand",
     "mixed", "build_product_atlas.py, build_products_c.py, product_derivation.py, country_areas.py"),
    (r"war/armory\.json\.gz", ["wikipedia", "own"],
     "the armoury: 24 kinds of weapon and armour, each dated where it exists and recorded where "
     "it never did. 11 are hand-dated per area (spear, club, dagger, bow, javelin, sling, pike, "
     "lance, shield, elephant, horsebow) because the product atlas derives those from MATERIALS "
     "rather than weapons - spears from bows, daggers from copper, shields from leather - which "
     "put the spear in Australia in 1800 and the dagger in North America in 1700. 13 read their "
     "dates from the technology atlas (258 countries, spread-modelled) or the product atlas. "
     "Every kind answers to one of D10's twelve arms, so step 40's 16 dated formations and 4 "
     "casualty bands join without a translation layer. 39 absences in 9 areas are recorded as "
     "facts: no bow in Australia (step 44 left a note asking this step to decide), no metal "
     "sword anywhere in the Americas before 1492, no war chariot in Africa south of the tsetse "
     "belt, no war elephant outside Asia. 17 kinds name the technology that ended them, so the "
     "rifle retires the bow, the sword, the lance and the shield at a different time in every "
     "country",
     "mixed", "build_armory.py, armory_table.py"),
    (r"war/arms\.json\.gz", ["wikipedia", "own"],
     "how a weapon reaches a man's hand: 18 rows over 17 areas from 10000 BC to AD 2000, each "
     "saying which of the five ways are open - issued by the state, brought from home, bought, "
     "taken off a beaten enemy, or given - plus a sixth flag for whether he may CARRY it, which "
     "is not a way of getting one but is the law that matters most of the time. KEEPING AND "
     "CARRYING ARE DIFFERENT LAWS IN EVERY AGE: the Statute of Northampton 1328 never touched a "
     "man's right to own a sword, it forbade him to walk into a market wearing one, so that row "
     "has buy open and carry shut while the 1181 Assize of Arms - a DUTY, not a restriction - has "
     "buy open and gift shut, because a freeman must own arms and may not sell or pledge them. "
     "12 of the 18 rows name a polity, and a row naming the state that rules a square outranks "
     "one that names none, because an area is not a country: East Asia holds both Japan and "
     "China, and in 1700 a Japanese peasant could not own a sword while a Qing subject could buy "
     "one. Hand-written and ILLUSTRATIVE, not comprehensive - there is no table of army supply to "
     "be read - so a place-year with no row of its own falls through to the default, which is the "
     "honest answer for most of the map and most of time: you bring your own. The weapon LAWS "
     "themselves are not in this pack; they are kind 5 of history/law.json.gz, keyed by polity "
     "rather than by area, and the two are meant to be read together",
     "mixed", "build_arms.py, arms_ways_table.py, weapon_law_table.py, build_law.py"),
    (r"war/units\.json\.gz", ["wikipedia", "own"],
     "units and ranks: 15 systems over 17 areas from 10000 BC to AD 2000, each a ladder of "
     "rungs from the smallest unit to the largest with who commanded each. **The finding that "
     "organises it: an army is counted in whatever base the society counts in** - ten on the "
     "steppe, in the Andes and in Ming China (arban 10 / zuun 100 / mingghan 1000 / tumen 10000, "
     "where a mingghan was also a thousand households, so the regiment and the tax roll were the "
     "same list); twenty among the Aztecs, because Nahuatl counts in twenties and the xiquipilli "
     "of 8000 is also the word for the pouch that held 8000 cacao beans; three in the Indian "
     "epics, whose smallest unit the patti is not ten soldiers but a combined-arms team of 1 "
     "elephant, 1 chariot, 3 horse and 5 foot, tripled eight times to reach an akshauhini of "
     "218,700; two in Sparta (36-72-144-576); and no base at all in Rome, which counted in eights "
     "because a century of EIGHTY kept the name of a levy of a hundred. **The Zulu amabutho count "
     "by birth year and not by number at all** - a man belongs to the regiment of his age set, is "
     "quartered in its ikhanda, wears its shield colours and may not marry until the king releases "
     "his whole age set at once. Also the Mughal mansabdari, which ranks MEN rather than units: a "
     "mansab is two numbers, zat (personal rank and pay) and sawar (the cavalry he must "
     "maintain), decimal in inheritance from Mongol and Timurid practice. 10 of the 15 name a "
     "polity, and one that does outranks one that does not wherever that state rules, because an "
     "area is not a country. Every polity fragment is checked at build time against the 1,581 "
     "names in the ruler register, so a row that can never fire is caught before it ships. "
     "Hand-written and ILLUSTRATIVE - there is no table of military units to be read - so a "
     "place-year with no system of its own falls through to the default, the war party of kin, "
     "which is the honest answer for most of the map and most of time",
     "mixed", "build_units.py, unit_table.py"),
    (r"war/weapon_items\.json\.gz", ["own"],
     "what goes in a soldier's hand, and THE MOD SHIPS NO WEAPONS: 9 optional weapon mods named "
     "by modid with their licence and dependencies, 20 item rows, 2 ammunition rows, 163 name "
     "tokens for guessing a kind from an unknown item, and local names for 15 areas. Three "
     "rules: an item TAG beats an item id (Spartan Weaponry renamed its registry between 1.16.5 "
     "and 1.19.2 and broke datapacks that hard-coded ids); an unknown item is GUESSED from its "
     "name and the guess is logged; and a missing weapon is never an error, because with no "
     "mod installed every kind falls back to the vanilla item the armoury already names on all "
     "24 kinds (read, NOT duplicated here). Only 6 rows are recorded - Musket Mod's five, read "
     "from its own source - the rest are estimated and say so. No Indian weapons exist for "
     "Java 1.20.1 (only a Bedrock add-on, unusable) and no matchlock mod exists at all, so a "
     "talwar in 1650 Agra is a modded sabre CARRYING the name talwar: the local-name table is "
     "the honest fix for a gap no mod fills. Dependencies are a chain, not a list: Musket Mod "
     "without Cloth Config is unusable and falls back rather than handing back an item that "
     "does not exist.",
     "mixed", "build_weapon_items.py, weapon_items_table.py"),
    (r"economy/animals\.json\.gz", ["own", "fao", "britannica"],
     "the working animals - what carried the world's goods and drew its ploughs: 12 entries "
     "(11 beasts and the human porter), each with what it does (pack, ride, pull, plough), what "
     "it carries in kilograms, how far in a day, the year it reaches each of 17 areas, and where "
     "it never reached and why. BUILT TO FIX ONE BUG: `trade/LogisticsManager` spawned TWO TO "
     "FOUR DONKEYS for every caravan in every era on every continent - three donkeys at Cusco in "
     "1500, when the Andes had llamas for four thousand years, and three donkeys in Australia in "
     "1700, eighty-eight years before donkeys arrived. A 500 kg caravan at Cusco in 1500 is "
     "**12 llamas**; at Timbuktu in 1300 it is **3 camels**. The years are READ from the products "
     "atlas, not rewritten. Two corrections to that atlas are recorded, not hidden: **reindeer "
     "were dated -2000 in West Africa**, a step-44 part-C artefact, and are removed from six "
     "areas; and **donkeys and horses shared a date everywhere**, which cannot be right because "
     "the donkey is African and the horse is a steppe animal, so in Africa the donkey is moved "
     "earlier. The tsetse belt cannot be drawn at 17 areas, so three areas are marked MIXED and "
     "say so: the Sahel has camels and the forest has none. Loads and distances from the FAO "
     "working-capacity tables, Britannica, the Logistics Cluster pack-animal table, Murra's "
     "ethnohistoric llama caravans (1965), the pre-colonial Kano trade study and Rockel's "
     "Carriers of Culture (2006); the tsetse effect is Alsan 2014.",
     "mixed", "build_animals.py, animal_table.py"),
    (r"economy/vehicles\.json\.gz", ["own", "wikipedia"],
     "every way there has been of getting somewhere: 32 vehicles over six mediums - foot, "
     "beast, wheel, rail, water, air - covering the plan's whole E10 list (porters, palanquins, "
     "carts, chariots, horses, camels, elephants, bicycles, rickshaws, trams, buses, cars, "
     "lorries; rafts, dhows, galleys, junks, sailing ships, steamships; trains; balloons, "
     "airships, planes), each with what it carries, how far in a day, the year it reaches each "
     "of 17 areas, and WHERE IT NEVER REACHED. THE DATES ARE READ, NOT REWRITTEN: three "
     "registers in the mod already owned them - the products atlas (per area), the technology "
     "atlas (spread curves for 258 countries) and the armoury (the war chariot, with its "
     "never-map). WHAT IS NEW IS THE `needs` COLUMN: the other registers say when a thing "
     "exists, none of them says WHAT IT RUNS ON - a train is not 'the railway exists' but 'the "
     "railway exists HERE', a canal boat needs a canal here, a cart needs a beast that has "
     "arrived here (a step-46 part-2 question). That join is the whole of E11. A SYSTEMATIC "
     "ARTEFACT IS RECORDED, NOT PATCHED AROUND: the products atlas dates `rickshaws` and "
     "`wheelbarrows` at EUR -3000 - the exact date of `carts` - and `oars` at -10000 in all 17 "
     "areas; those are template copies from step 44 part C, where a child inherited its "
     "parent's row unchanged. TEN VEHICLES carry explicit sourced dates instead and every one "
     "is listed in the pack: rickshaw (Japan, c. 1868), wheelbarrow (Han China c. AD 100, "
     "Europe c. 1200), galley, dhow (the Indian Ocean's monsoon trades), junk (China, not "
     "Europe), sledge (snow and dogs, not Australia), balloon (Paris 1783, not 1919), "
     "helicopter (1936, not before the aeroplane) and the sailing ship (the sail of c. -3200, "
     "not a boat of -10000). The chariot is dated by the technology atlas and still carries the "
     "armoury's never-map - no chariots in the Americas, none in the tsetse belt - because "
     "arrival and beast are two different questions.",
     "mixed", "build_vehicles.py, vehicle_table.py"),
    (r"economy/traffic\.json\.gz", ["own", "wikipedia"],
     "E11, traffic: how much moves along a road, river, canal, railway or sea here, and BY WHICH "
     "MEDIUM. 15 goods, 5 routes, 4 gates that cap throughput, 12 working speeds, and 5 "
     "DOCUMENTED traffic counts. THE DECISIVE FACT IS THAT FREIGHT IS PRICED BY THE KILOGRAM AND "
     "THE KILOMETRE, and so is the good: Diocletian's Edict on Maximum Prices (AD 301) prices "
     "both in the same currency on the same day, which is why its ratios are usable where later "
     "reconstructions are not - 1 sea : 5 downriver : 10 upriver : 52 ROAD per kg-km. So a cargo "
     "goes exactly as far as its own value pays for, and the BREAKING DISTANCES are DERIVED, not "
     "invented: wheat (10 denarii/kg, the Edict's own price) reaches 286 km by road before "
     "freight doubles its price, 2,941 km downriver, 14,925 km by sea - WHICH IS WHY ROME WAS "
     "FED BY SEA AND NOT BY ROAD, and why every great pre-industrial city sits on water. Silk, at "
     "36,697 denarii a kilogram, has effectively no leash at all, which is why the Silk Road "
     "carried silk and not wheat. Rail and canal cannot come from the Edict, which predates "
     "railways, so they are given as fractions of the road rate from Bogart's British ton-mile "
     "series (rail road/12, canal road/6). A CROSS-CHECK WORTH KEEPING: a free river in England "
     "in 1700 cost road/10.00 and the Edict's downriver rate is road/10.29 - two documents "
     "1,400 years apart, to within 3 per cent. THE MODEL IS CHECKED AGAINST THREE DOCUMENTED "
     "JOURNEYS, not asserted: Bolton Massachusetts' 14,000 tons a year in forty wagons comes back "
     "as 40 at the measured 0.8 LOAD FACTOR (wagons ran five-sixths full); the 1333 Exchequer "
     "carriage Westminster-York, 330 km in nine days, comes back at 37 km a day inside "
     "Spufford's 30-40; and the turnpike wagon limits (6 tons summer, 4 winter) and the "
     "packhorse's hundredweight are the capacities. Fourth of four registers: WaysGrid knows "
     "whether a road is HERE, Vehicles knows WHICH vehicle and what it NEEDS, WorkingAnimals "
     "knows whether the beast has ARRIVED, and this knows HOW MUCH and BY WHICH MEDIUM.",
     "mixed", "build_traffic.py, traffic_table.py"),
    (r"economy/credit\.json\.gz", ["wikipedia", "keynes", "india_banking", "own"],
     "what it costs to borrow: 29 rows from -3500 BC to 1950, each with the rate, who lends, "
     "whether charging interest is lawful there, and what was done instead where it was not. "
     "12 recorded (a document states the rate), 9 measured (read off many records, like the "
     "1,563 cash waqfs of Bursa at 10.8-11.5 per cent), 8 estimated. Hand-written: no register "
     "anywhere carries rates. Not a European table - Mesopotamia, Egypt, Athens, Rome, "
     "Byzantium, Tang and Song China, the Ottomans, Mughal India, colonial India, Italy, "
     "England, Holland, the United States, West Africa and the Andes are all present. 5 rows "
     "carry no rate on purpose and say so: the Inca had no money at all, and pre-colonial West "
     "Africa ran on cowries, pawnship and rotating savings clubs rather than a price for credit",
     "mixed", "build_credit.py, credit_table.py"),
    (r"economy/substitutes\.json\.gz", ["own"],
     "what people use when the thing they would use is not there: 38 products and the 89 "
     "goods that stand in for them, each marked good, serves or last resort, plus how hard a "
     "shock to the land, the hands, the roofs or the road reaches each of the twelve kinds of "
     "work. Written by hand for this mod - no register anywhere carries substitutions - and "
     "every product id is checked against the product atlas so no answer names something that "
     "does not exist. The disruption half of part E needs no pack: it reads the 37,201 "
     "disasters, the 84 climate periods and the 14 trade routes that already ship",
     "mixed", "product_substitutes.py, build_substitutes.py"),
    (r"food/seats\.json\.gz", ["own", "khoury2016"],
     "what part of a meal each of 80 foods is - the grain, the pulse, the greens, the fruit, "
     "the meat or fish, the fat it is cooked in, what sharpens it, the sweet, the seasoning, "
     "the drink, the stimulant - so a place with wheat, lentils, ghee and chillies has a meal "
     "to describe and a place with wheat alone does not. Written by hand: no register records "
     "that a lentil and a mango play different parts at a table. Every id is checked against "
     "the product atlas, and every food in the atlas is checked to hold a seat. Which food "
     "fills which seat is not written down anywhere - it is read from the atlas at the time, "
     "so the maize that reaches Italy in 1500 takes the grain's seat on its own",
     "mixed", "diet_roles.py, build_diet.py"),
    (r"economy/(goods|products)\.json", ["wikipedia", "own"],
     "what is made, sold and bought where and when", "mixed", "build_goods_table.py, build_product_atlas.py"),
    (r"cards/events\.tiles", ["wikidata", "wikipedia", "ibtracs"],
     "event cards and the cause-and-effect graph: what, when, where, who took part, why, what came of it",
     "recorded", "fetch_events_wd.py, build_event_cards.py"),
    (r"history/events_storms\.json\.gz", ["ibtracs", "wikidata"],
     "tropical cyclones where they came ashore or passed close to land, 1842 on", "recorded", "build_nature.py"),
    (r"history/events_nature\.json\.gz", ["wikidata"],
     "floods, wildfires, landslides, avalanches, tornadoes, heat waves, droughts, famines and epidemics", "recorded",
     "fetch_events_wd.py, build_nature.py"),
    (r"history/occupations\.json\.gz", ["cliopatria", "own"],
     "squares held by an occupying power in the Second World War (the record before step 26's fix)", "recorded",
     "build_occupations.py"),
    (r"history/countries\.grid\.gz", ["natural_earth", "wikidata"],
     "which country of today a point lies in (0.1-degree grid), and each country's biggest town", "recorded",
     "build_country_grid.py"),
    (r"history/culture\.json\.gz", ["owid", "maddison", "wikipedia", "own"],
     "who can read (by country and year), scripts, weights and measures, the metric year, wealth, hard times, "
     "festivals and pilgrimages", "mixed", "build_culture.py, culture_table.py"),
    (r"history/holy_places\.json\.gz", ["wikidata", "wikipedia"],
     "holy places (mosques, temples, churches ...) with their faith and the years they stood", "recorded",
     "build_culture.py"),
    # Step 42. Four packs, and the marks are the whole point: C18's dated abolitions are recorded,
    # because a source states the year; D7, F3 and F8 are estimated throughout, because nothing
    # states how much of a society was brahmin, that the peace of a given century was kept by a
    # paid watch, or that a frontier demanded a gift. The register prints the mark with the answer.
    (r"history/law\.json\.gz", ["wikipedia", "cliopatria", "wikidata", "own"],
     "step 42 (C18): dated changes in the law, by the state that made them - abolitions of slavery and "
     "serfdom, the vote, capital punishment - 620 rows over 237 polities; keyed by the ruler register's "
     "own polity QIDs so a row can never name a state the mod cannot find. The dated abolitions are "
     "read from three Wikipedia tables and are recorded; 250 rows are this pack's reading of a "
     "tradition for a region and era and are marked estimated. **KIND 7, THE LAW OF THE ROAD, WAS "
     "ADDED BY STEP 46 PART 5 (E10 B)** and is not one of C18's six kinds: 22 hand-written rows "
     "over 10 jurisdictions and 9 shapes - closed, toll, forced, gauge, side, speed, hours, "
     "labour, ban - because **a road is not a right of way and never was**. The cursus publicus, "
     "which a man without a warrant might not ride; Caesar's ban on carts in Rome by daylight, "
     "which is why Juvenal could not sleep; the Qin axle standard, the only ancient gauge law with "
     "a ruler's name on it; Cologne's staple right, which forbade you to PASS THROUGH without "
     "selling, and which the French Revolution abolished in 1790; the Rhine tolls at every castle, "
     "ended by the Congress of Vienna in 1815; England's six days' statute labour, which is why the "
     "roads were bad; the first turnpike gate of 1663 and the 8,000 that followed; keep-left in "
     "1835, which Britain has never repealed; the red flag of 1865, whose purpose was to make the "
     "motor car useless; the Inca royal road and the Tokugawa sekisho checkpoints. **A law of the "
     "road is a law about a class of vehicle or a class of person**, like step 45's weapon laws, "
     "and each row names its source. The claim that Roman ruts are the ancestor of standard gauge "
     "is a MYTH and this pack does not repeat it.",
     "mixed", "build_law.py, road_law_table.py"),
    (r"economy/herds\.json\.gz", ["own", "wikipedia"],
     "step 46 part 7 (D14, the second half): HERDS, and the roads they made. Part 2 built the "
     "register of working animals and said plainly what it had left out, that sheep, goats, pigs "
     "and poultry were not yet read as herds; this is that register, 28 rows over 15 animals and "
     "13 areas. It answers what is kept in a herd, where, from when and how many to a herd, "
     "because the herd size is what makes a road necessary, and what a herd yields that one beast "
     "does not: wool, milk, manure, hides, eggs, blood, dung for fuel. THE FINDING REORDERS THE "
     "SUBJECT: **the herd is the missing reason for the road.** Part 5 found that a road is almost "
     "never a right of way and never found why the road is there at all. A Roman road is 4 to 6 m "
     "wide, which is two carts; a Spanish canada real is 75 m wide, and it is 75 m wide because "
     "sheep spread out while they graze and a flock must walk and eat at the same time. **A road "
     "you can eat is a different object from a road you can drive on.** The largest road-building "
     "institution in early modern Europe was a shepherds' guild. 10 droves are carried with their "
     "width, length, animals a year and law shape, from the canadas of 1273 to the Chisholm Trail "
     "of 1867, which existed for 17 years and was closed by barbed wire and a Kansas quarantine "
     "law. Four claims are refused in the pack: the giant medieval flock, wool at the start, the "
     "chicken at 8000 BC, and the herd as a thing you can count. The chicken is carried on the "
     "2022 PNAS date, 1650 to 1250 BC at Ban Non Wat in Thailand and NOT the Indian subcontinent, "
     "reaching Mediterranean Europe about 800 BC. The bison is carried as the one herd in the "
     "register that ENDED: 30 to 60 million in 1800, and 1,091 counted by Hornaday in 1889, and it "
     "is still gone in AD 3000. 124 checks.",
     "mixed", "build_herds.py, herd_table.py"),
    (r"history/healers\.json\.gz", ["own", "wikipedia"],
     "step 47 part 6 (E15): MEDICINE AND HEALERS BY ERA - the half the plan did not know was "
     "missing. **The medicine half is already done**: step 38's health register carries 14 remedies "
     "with a year, a place, a multiplier and a note saying what each actually did, and "
     "MedicineSystem.tierAt asks it by coordinates, so the old fault of the whole planet becoming "
     "modern on one day in 1945 is fixed and the plan's row saying 'old code' is wrong. **The "
     "healers were not done at all.** A healer is not a remedy: a remedy is a thing that works and "
     "spreads as technology spreads, and a healer is a person you can get to, so their data is a "
     "different shape - who is available, how far a patient travels, what they will touch, and "
     "whether the neighbours approve. 16 trades over 17 areas and 12 kinds of complaint. **Two "
     "things a one-axis register cannot say.** (1) **Surgery is four thousand years older than "
     "anaesthesia**: trepanation is Neolithic, cataract couching is described by Sushruta, a Roman "
     "army surgeon could ligate an artery, and the part where the patient does not feel it starts in "
     "1846, so a game that gates the knife on anaesthesia has the order of events exactly backwards. "
     "(2) **The midwife is the oldest trained practitioner and the least respected one.** Childbirth "
     "happens everywhere in every year, so she is the only universal healer, which is why the "
     "coverage check demands somebody for a birth in every area in 3000 BC; and in Europe from about "
     "1450 to 1750 she is the one prosecuted, which is a change in STANDING and not an arrival, so "
     "this register carries two axes and her row uses both. 82 checks.",
     "mixed", "build_healers.py, healers_table.py"),
    (r"names/games\.json\.gz", ["own", "wikipedia"],
     "step 47 part 6 (E17): GAMES AND SPORTS. The plan names chess, polo, cricket, kites, theatre "
     "and cinema and the survey said 'not yet', which was right about the code and wrong about the "
     "data: the products atlas already carries chess, dice, backgammon, kites, playing_cards, "
     "puppets, dolls, drums, flutes, theatre and fireworks with a year for all 17 areas. What nothing "
     "carried is the GAME as a thing people play. 21 games over 9 kinds. **The finding: a game is "
     "the cheapest thing a culture exports and the last thing it gives up.** Board games travel with "
     "merchants and cross every border within a few centuries (backgammon from Mesopotamia, chess "
     "from India, cards from China), while the sports travel with empires and then with schools - "
     "and the codified ones are astonishingly late: football is a folk game in every European "
     "village and a RULE in 1863, basketball is 1891, the modern Olympics are 1896 and the ancient "
     "ones end about 393, so the two things with the same name are two thousand years apart. Before "
     "the nineteenth century a crowd does not watch a sport, it watches a SPECTACLE, and the "
     "Mesoamerican ball game is the extreme case: a religious obligation with a ballcourt in the "
     "middle of the city and, at the end of some of them, a death. **The register also refuses to "
     "guess**: a crop has an arrival in every area because the atlas computed one, and nobody can "
     "say when polo reached Java, so a game has an origin and only the spread years the record "
     "gives - everywhere else the answer is `unknown`, which is not `never`. 39 checks.",
     "mixed", "build_games.py, games_table.py"),
    (r"history/climate_projection\.json\.gz", ["own"],
     "step 47d: CLIMATE TO AD 3000, AS ARITHMETIC UNDER A STATED ASSUMPTION. Allowed where a price is "
     "refused, because it is physics and not prophecy: carbon leaves the air at rates measured from "
     "the isotope record, temperature follows the logarithm of carbon with a thermal lag, and sea "
     "level follows temperature with a slower lag still. It does not forecast, because it does not "
     "say what people will do - it says IF emissions follow this path THEN this is what the physics "
     "does, and the assumption is a field on every scenario. Three paths: emissions stop in 2027, end "
     "by 2060, or stay flat to 2050 and end by 2120. **Every value is a BAND, not a point**, which is "
     "the lesson the backtest In step 47c taught: the same kind of projection printed as a single "
     "number is wrong by about twenty points, so each value carries low, mid and high from running "
     "the same physics at the two parameters nobody knows, climate sensitivity (2.0 to 4.5 C per "
     "doubling) and the ice response rate. **The finding: about a fifth of every tonne of carbon is "
     "still in the air in AD 3000** - the carbon box that never empties holds 18.6 per cent forever - "
     "so even the zero scenario does not put the world back, and **sea level is the one number in "
     "this project that only ever goes up**. By 3000 the gap between acting and waiting has widened "
     "rather than closed, because the ice term keeps integrating after the temperature has stopped "
     "falling. 36 checks.",
     "projected", "build_climate_projection.py"),
    (r"history/obsolescence\.json\.gz", ["own"],
     "step 47c: THE OBSOLESCENCE ATLAS, the half the projection atlas does not measure. That pack "
     "computes what ARRIVES; this one computes what LEAVES, and it is computable for the same reason: "
     "TechnologyAtlas has always carried the `replaces` graph and `share()` already multiplies a "
     "dying technology by the share of what replaced it. A technology is GONE at one per cent of its "
     "own ceiling and COMMON at half of it. **The finding is also the limit: the last technology this "
     "register can say goodbye to is the steamship, and it leaves Australia in 2051.** Only 11 of the "
     "130 technologies carry a successor at all, so only 102 area-and-technology pairs have an end "
     "that can be computed, 98 before the seam and 4 after; the other 1,956 pairs have no successor "
     "in the data, so nothing computes their end and they persist to 3000. That is the carry rule "
     "working and it is also the honest shape of the register: **it can say goodbye to eleven "
     "things.** The general point it earns is that an obsolete technology is not a dead one - the "
     "matchlock is superseded in the 1720s and flintlocks are in use in the 1930s, gas light and the "
     "kerosene lamp are both superseded by electricity in the 1930s and both are still sold - so a "
     "world in a single year is not of one era but of several standing next to each other. 29 checks.",
     "projected", "build_obsolescence.py"),
    (r"history/projection\.json\.gz", ["own"],
     "step 47b: THE PROJECTION ATLAS, and the answer to 'can the data for 3000 BC to AD 2026 be "
     "built for 2027 to 3000'. **Not all of it, and the reason is not effort.** `projection_plan.py` "
     "classifies every one of the 120 shipped packs into computed (5), carried (64), refused (32), "
     "past only (14) and template (5), and fails if any pack is left without a stated answer for "
     "2400 - so no part of the engine goes silent at the seam. The refused 32 are people, rulers, "
     "events, wars, disasters, prices and populations, which Projector will not invent. What IS "
     "computable is built here: **no technology in the atlas arrives after 2025**, so between 2027 "
     "and 3000 the only honest change is the SPREAD of what already exists, and the engine's "
     "diffusion curve never clamped at the seam. This pack reads that curve forward. **Its finding "
     "is that the future in it runs out in 2300**: 42 area-and-technology pairs are short of common "
     "in 2026, all 42 clear by 2300, and after that the curve is flat for seven hundred years. So "
     "the honest answer to 'what is the world like in 2400' is 'the world of 2026, fully spread', "
     "and everything a story adds beyond that is an invention this engine refuses to make. It names "
     "nobody, dates nothing, prices nothing and counts no population. 92 checks.",
     "projected", "build_projection_atlas.py, projection_plan.py"),
    (r"names/arts\.json\.gz", ["own", "wikipedia"],
     "step 47 part 6 (C15): CULTURE, the last part of it - music and the arts. The plan's row is "
     "'clothes, food, music, games, customs, arts' and by the end of this part five of the six live "
     "somewhere: clothes in part 4's 27 period garments, food in the products atlas and the diet "
     "register, games in the games register, customs in CultureAtlas's 21,000 holy places with "
     "feasts, scripts and measures. **Music and the arts had nothing at all.** There is no such "
     "thing as the year a place got music - every human group sings, and the oldest instrument known "
     "is a bone flute about 40,000 years old, thirty-seven thousand years before the span begins - "
     "so the register is not of music but of THE THINGS THAT CARRY MUSIC AND PICTURES: an "
     "instrument, a medium, a way of copying. That is a technology history and it dates honestly, "
     "and it has the same shape as the tools register because a violin is a manufactured object. 14 "
     "rows over 9 kinds, 12 of them universal from the first year. **The finding: every art form "
     "here is older than the means of copying it, and copying changes what the art is.** The two "
     "sharpest dates are the phonograph in 1877, which separates a performance from the performer "
     "for the first time in the history of the species, and photography in 1839, which arrives after "
     "the oil painting it replaces as the way to record a face and before the cinema it makes "
     "possible in 1895. 70 checks.",
     "mixed", "build_arts.py, arts_table.py"),
    (r"names/wildlife\.json\.gz", ["own", "wikipedia"],
     "step 47 part 5 (B5): WILD ANIMALS BY ERA. The plan asks for 'lions and cheetahs in India, "
     "aurochs in Europe, no horses in the Americas before 1493', and the survey found that the only "
     "wild animal anywhere in this project was the bison, which was there because it was hunted in "
     "herds and not because it was in a place. 14 species over all 17 areas. **The point of the "
     "pack is that a wild animal's data is not its birth date but the year its range ENDED**, and "
     "almost every row is one of three stories. The animal is GONE FROM HERE and alive there: the "
     "lion is a predator of the Greek hills in the Iliad and fights in Roman arenas, and it is out "
     "of Greece by about 100 BC, out of the Balkans by 500 and out of India outside Gujarat in "
     "1884. The animal is GONE EVERYWHERE and the year is known because somebody was counting: the "
     "aurochs at Jaktorow in 1627, the passenger pigeon in Cincinnati in 1914, the thylacine in "
     "Hobart in 1936, the dodo about 1681 by nobody's count at all. Or the animal was NEVER THERE "
     "and the absence is the fact, which is the plan's own horse: it died out in the Americas at "
     "the end of the Pleistocene and the continent had none for ten thousand years, so **a horse "
     "in the Americas in 1200 is not a small anachronism but the largest biological fact about the "
     "continent**. The register keeps that as an absence WITH A REASON, because the three stories "
     "need different things from a game: an extirpated animal can be reintroduced, an extinct one "
     "cannot, and an animal that never lived there is not a conservation problem. 43 checks.",
     "mixed", "build_wildlife.py, wildlife_table.py"),
    (r"economy/spread\.json\.gz", ["own", "wikipedia"],
     "step 47 part 5 (B6, E18): CROPS AND ANIMALS AS ITEMS, AS THEY SPREAD. **No date is written "
     "for this pack.** Step 44's atlas already puts maize in Europe in 1520 and in Mesoamerica in "
     "7000 BC, and chillies in Goa in 1540, so the plan's example ('no maize, potatoes or chillies "
     "in India before the 1500s') was already true. What was missing is the OTHER half of a "
     "spread, which is where the thing came from: a year alone cannot tell a potato in Bengal in "
     "1700 from a potato that was always there. So this is a JOIN of the atlas (when) with the "
     "crop-origins register (where, Khoury et al. 2016, 150 crops against 23 regions, no dates at "
     "all), and the year a crop left home falls out of it as the earliest year it is made outside "
     "its origin, which is exactly what E18 asks for. 26 rows, 18 crops and 8 animals. **The "
     "finding: the Columbian exchange is measurable and it took about a lifetime** - the chilli is "
     "in Goa by 1540 and has displaced long pepper in Indian cooking within fifty years, so a New "
     "World fruit made South Asian food into what the world now calls South Asian food in less "
     "than one life, which is a story about ships and not about food. **The limit is real and the "
     "data declares it**: the atlas has 133 hand-written rows and 406 derived ones, and a derived "
     "row takes its parent's dates, which is right for flour and wrong for sorghum (parent millet, "
     "so derived sorghum 'originates' in China) and for groundnut (which inherits West Asia from "
     "oilseeds). An origin is therefore claimed only for a hand-written row, and every other row "
     "says `inherited` and names its parent. Three rows (cotton, pulses, wool) are more than one "
     "species domesticated in different hemispheres and declare `poly`, because the exchange rule "
     "is not a rule for them: cotton alone is four species, two Old World and two American. "
     "47 checks.",
     "mixed", "build_spread.py, spread_table.py"),
    (r"names/wardrobe\.json\.gz", ["own", "wikipedia"],
     "step 47 part 4 (E12): THE PERIOD WARDROBE, and the bug it fixes is the sharpest in this step. "
     "SkinPoolDatabase holds 40 garments and **every one arrives in 1873 or later**: jeans 1873, "
     "button_down 1900, crew_tee 1913. So its own code does the only thing it can, returning an "
     "EMPTY outfit for any year before the pool's modern turning point, and **every person in the "
     "world before 1945 is dressed in nothing**. The plan called E12 'partly: looks by era' and it "
     "was not: it was looks by the MODERN era, and six thousand years of the world were bare. The "
     "culture pools carry a `lower` (dhoti, sari, tunic, robe, wrap) and a handful of cultural "
     "items, so the missing half is precise and a little comic: **the top half of the body**. A "
     "weaver in the Deccan in 1400 wore a dhoti and no shirt. This pack adds 27 garments that exist "
     "before the machine age, all 27 before 1873, over all 11 culture pools and 17 areas. **The "
     "finding: the wardrobe is a technology and its dates are the history of tailoring.** Almost "
     "everything before 1300 is a RECTANGLE - the tunic, the chiton, the hanfu, the huipil, the "
     "poncho, the wrapper - and none of them needs a curved seam. The doublet of the 1340s is the "
     "first European garment CUT to a body, and everything fitted that Europe has worn since "
     "follows from that one change in a tailor's technique, in the same decade as the Black Death. "
     "It also refuses the tempting error: the sherwani is a 19th-century coat and is dated 1850, so "
     "a Mughal nobleman of 1600 wears the kaftan and the angarkha. The check caught its own gap "
     "twice: the African pool had no upper garment at all, and Europe had no coat between 600 BC and "
     "1873 until the cloak was added. 73 checks.",
     "mixed", "build_wardrobe.py, wardrobe_table.py"),
    (r"economy/anachronisms\.json\.gz", ["own", "wikipedia"],
     "step 47 part 3 (E8, E22): vanilla things that do not belong, and what a year may use. E22 was "
     "decided in turns 73 to 81 for swords and NEVER BUILT; this is it. **The pack distinguishes "
     "three kinds of impossible thing, because they need three answers.** `real` - a real thing "
     "existed and the game's version is just better: allowed from its year, and a golden sword is "
     "worse than iron in vanilla and in history, which is one of the few places the game is "
     "accidentally right. `myth` - people believed in it, so it existed as a belief and not as a "
     "function: ALLOWED AND RENAMED, because the object is real and the power is not. `never` - "
     "nothing like it has existed at any date: locked in a strict world and allowed only for a time "
     "traveller, who is then SEEN carrying it. Treating all of it as fantasy to delete would remove "
     "the game; treating all of it as allowed would make the year meaningless. **The middle kind is "
     "the one worth having and it is what turns a blacklist into a translation**: alchemy is real "
     "history, running from Hellenistic Egypt through the Islamic world to Newton, who wrote more on "
     "alchemy than on physics and gave us distillation and the mineral acids, so a brewing stand in "
     "1300 is an ALCHEMIST'S BENCH and the enchanting table is a SHRINE. Six of the 19 rows are "
     "renamed and 10 locked. The diamond is the sharpest: a real gem, traded from India to the "
     "Mediterranean by 300 BC, which nobody made a tool of for two thousand years because it is "
     "brittle, so the gem is allowed and the pickaxe is not. An unknown item is always allowed and "
     "the verdict says it was never judged, which is step 45's and step 46's rule again. It never "
     "decides whether a potion WORKS: that is step 38's health register. 55 checks.",
     "mixed", "build_anachronisms.py, anachronism_table.py"),
    (r"economy/tools\.json\.gz", ["own", "wikipedia"],
     "step 47 part 2 (E7): TOOLS AND INVENTIONS AS ITEMS - the thing in a person's hands, what it "
     "does, what it REPLACED, and what in Minecraft stands for it, where step 44's products atlas "
     "asks only what a place makes and sells. 27 tools over 8 families of work and all 17 areas, 21 "
     "of them reading their dates from the products atlas by id and 6 written here with a source. "
     "THE RULE THE PACK EXISTS TO ENFORCE: **a tool's date is not its material's date.** Step 44 "
     "derives a product from its parent, and for tools the parent is a material, so a microscope "
     "whose parent is glass became as old as glass: 2500 BC in West Asia. Step 46 found the same "
     "fault in reindeer and donkeys, which makes three instances and a class of error, so no row "
     "here is derived from a material. **The microscope bug is fixed at its source**: the atlas now "
     "derives it from the telescope technology and dates it AD 1608, and this row carries the finer "
     "1590 with the Janssen attribution and the warning that the attribution comes from a "
     "recollection given sixty-five years after the fact. **Two of the seven things the plan names "
     "had no row anywhere and are this pack's main additions**: the atlas has woodblock_prints, "
     "which is the print and not the press, and no loom of any kind. The treadle loom is the "
     "sharper of them because it is not only a machine: it is expensive, so it moved weaving out "
     "of the household and into guilds, and the guilds excluded women. A tool can reorganise who "
     "is allowed to work. The warp-weighted loom is 5000 BC and so OLDER THAN THE WORLD, which "
     "begins at 3000 BC, and is marked before_world rather than clamped. Every tool resolves to a "
     "vanilla item or says why it cannot, which is A13's rule from step 46 applied where it was "
     "always needed: an inventory. Four have none, including the watermill and the windmill. 82 "
     "checks.",
     "mixed", "build_tools.py, tool_table.py"),
    (r"economy/vehicle_mods\.json\.gz", ["own", "wikipedia"],
     "step 46 part 6 (A13, the vehicle half): WHICH mod supplies which vehicle, and what stands "
     "in when none is installed. A13's own line is \"optional links; everything also works "
     "without them\", which imposes three duties and this pack keeps all of them. **Never hand "
     "back nothing**: all 32 of part 3's vehicles resolve to a mod, to a vanilla stand-in, or to a "
     "written statement of why there is neither, and 11 take the third answer. **Never pretend a "
     "stand-in is the real thing**: a boat is not a ship and a minecart is not a cart, and each "
     "answer carries that flag. **Never invent an id**: 5 providers are marked read (AstikorCarts "
     "Redux, MIT, whose supply_cart, animal_cart, plow and wheel come from the mod's own "
     "DeferredRegisters; Small Ships; Minecraft itself), or content (Immersive Vehicles and Create, "
     "whose ids come from JSON content packs, so those providers name NO id at all and claim only "
     "vehicle KINDS; a content-marked provider that names an id fails the build). Two of those "
     "mods ship a config list that is exactly a question this step already answers - AstikorCarts' "
     "pull_animals and Small Ships' dockyardBuildableShips - so this step REPORTS what those lists "
     "should hold for a place and year through the mod's public surface rather than editing its "
     "config. **Small Ships has no crafting recipes at all** - ships are built at a Dockyard - so "
     "there is no result slot to empty and the gate must refuse the Dockyard itself, the same "
     "shape as step 45's gun bench; and it refuses it for two different reasons that it "
     "distinguishes: Paris in 1400 for want of water, Marseille in 3000 BC for want of years. The "
     "four working animals with no entity anywhere - ox, elephant, reindeer, water buffalo - are "
     "named as such rather than glossed over. 139 checks.",
     "mixed", "build_vehicle_mods.py, vehicle_mod_table.py"),
    (r"history/social_order\.json\.gz", ["own"],
     "step 42 (D7): the order of a society by place and year - 12 orders, 58 strata, and who may "
     "address whom uninvited. Written by hand and estimated throughout: no source states what share "
     "of a society was brahmin or shudra in a given century, and the plan's \"old code (class system)\" "
     "never existed",
     "estimated", "build_social.py, social_order_table.py"),
    (r"history/justice\.json\.gz", ["own"],
     "step 42 (F3): who keeps the peace, who judges, and what can be done to a man - 16 kinds of "
     "guard, 14 of court, 8 of punishment. Written by hand and estimated throughout. Whether a polity "
     "still puts men to death is NOT from here: it is the C18 law pack's own dated abolitions",
     "estimated", "build_justice.py, justice_table.py"),
    (r"history/border\.json\.gz", ["own"],
     "step 42 (F8): what a crossing demands of you - 12 kinds, a gate and a gift to a passport desk - "
     "by country and year, and by whether you arrive by land or by sea. Written by hand and estimated "
     "throughout, except the five dates read out of the articles themselves (Ragusa 1377, the passport "
     "1914 and 1920, the Zollverein 1834, sakoku 1633-1853, Canton 1757-1842). WHERE THE BORDER RUNS "
     "IS NOT IN THIS FILE: it is derived at runtime from the step-31 ruler register",
     "estimated", "build_border.py, borders_table.py"),
    (r"history/technology_atlas\.json\.gz", ["wikipedia", "chat", "own"],
     "which technology reached which country when (130 technologies), how common it was; estimates marked",
     "mixed", "build_technology_atlas.py, technology_table.py"),
    (r"history/water_works\.json\.gz",
     ["wikidata", "pleiades", "chgis", "reba", "own"],
     "water supply, bathing and sanitation by year (B25): wells, stepwells, cisterns, qanats, aqueducts, "
     "fountains, reservoirs, water towers, bath houses and hammams with a map point and the year they were made; "
     "where Wikidata has no year at all, the year is the gazetteer's occupation window for the site and is marked "
     "estimated. Fetched at 3 Wikipedias rather than 5, because water works are far less written about than "
     "monuments. Sanitation is nearly absent: Wikidata has articles about sewers, not about individual ones. "
     "Step 35 part 4 added the field (B17, and B2's rule that no reservoir stands before its dam): 21 more "
     "classes -- dams, canals, irrigation canals, weirs, polders, levees, watermills, oases, acequias, terraces, "
     "ditches -- bringing it to 3,884 works in eleven groups. The irrigation tank class gives nothing at all, "
     "however many tanks there are in South India, and neither do chinampas or anicuts; that zero is recorded "
     "too. The gazetteer may date a work only when the name matches the site it stands on, not merely because it "
     "is near one -- a canal two kilometres from an abandoned site is usually not of it, and Dujiangyan, built "
     "in 256 BCE, was being given a Sui county seat's window of 568 CE",
     "mixed", "fetch_town_wd.py, fetch_farm_water_wd.py, date_undated.py --water, build_water_works.py"),
    (r"history/climate_periods\.json\.gz", ["wikipedia", "own"],
     "the climate of every era (B4): 84 periods, written by hand because the mod's whole climate used to be two "
     "events typed into ClimateEngine -- the Little Ice Age and the Year Without a Summer -- and nothing at all "
     "for the four thousand three hundred years before them. The warm and cold ages (Roman, Sui-Tang, Medieval, "
     "Little Ice Age), the solar minima (Homeric, Oort, Wolf, Sporer, Maunder, Dalton), twelve volcanic winters "
     "with their Northern Hemisphere anomalies (536 and 540, Samalas 1257, the 1452 mystery eruptions, "
     "Huaynaputina 1600, Parker 1641, Laki 1783, Tambora 1815, Krakatoa 1883, Pinatubo 1991), the megadroughts "
     "(the four Maya pulses of 760-910, Tiwanaku, the Ancestral Puebloan Great Drought of 1276-1299, the "
     "Sahel, the Dust Bowl), the failed monsoons and the famines (the Global Famine of 1876-78 with its fifty "
     "million dead, Bengal 1770, the Deccan 1630, the last Ming years, the Irish famine), and the heat and "
     "drought of our own day. Temperatures are degrees Celsius against the twentieth-century mean; rainfall and "
     "harvest are percentages. The thing that shaped the table: a 2019 synthesis of more than ninety proxy "
     "records found the Roman Warm Period, the Medieval Warm Period and the Little Ice Age to be regional "
     "phenomena rather than globally coherent episodes, so every row carries a centre and a radius and only the "
     "volcanic winters are marked as everywhere. The Little Ice Age is therefore four rows with different "
     "dates -- the North Atlantic, Asia, North America and the Andes -- and a civ in Cusco in 1650 feels the "
     "Andean one and not Europe's. 49 of the 84 are recorded, 34 estimated; 29 of the mod's 31 test places have "
     "a period standing in their year, and the two that do not (Ur and Mohenjo-daro in 2500 BC) are real gaps "
     "rather than bugs. The Meghalayan stage row carries no anomaly on purpose, because the twentieth century "
     "these numbers are measured against is itself in the Meghalayan, and counting it too would take the same "
     "thing off twice",
     "mixed", "climate_periods_table.py, build_climate_periods.py"),
    (r"history/water_changes\.json\.gz", ["wikipedia", "own"],
     "the water that moved, by year (B2): 158 changes written by hand because no data set has them -- rivers that "
     "changed course, coasts and deltas that grew or were eaten back, seas and lakes that dried or were made, "
     "marshes drained, straits opened and shut, from the Yellow River's six recorded avulsions and the drowning of "
     "Doggerland to the closing of the Zuiderzee and the drying of the Aral. Each row gives the place, the year, "
     "how wide a thing it was, and whether that year is recorded or estimated; 98 are recorded, 60 estimated. "
     "The years of the Yellow River, the Zuiderzee works, the Aral Sea, the Caspian, Ghaggar-Hakra, the Kosi and "
     "the Rann of Kutch were checked against English Wikipedia and Britannica",
     "mixed", "water_changes_table.py, build_water_changes.py"),
    (r"history/building_culture\.json\.gz", ["wikipedia", "own"],
     "what a town is made of, by place and year (B9 houses, B11 insides, B13 streets and their surfacing, "
     "B20 lighting, E14 markets, E16 materials, B25 water): 109 building cultures, each naming the house, its "
     "walls, roof and floor, how the town is laid out, what the lanes are surfaced with, where the water comes "
     "from, what it is lit by after dark, what is inside a home, where people trade, and how many storeys. "
     "Written by hand from English Wikipedia's articles, every row naming the one it came from; the years a "
     "technology reached a place are NOT here and are asked of the technology atlas instead",
     "mixed", "building_culture_table.py, build_building_culture.py"),
    (r"history/buildings_famous\.json\.gz",
     ["wikidata", "pleiades", "chgis", "reba", "own"],
     "famous buildings, walls and ruins with a map point, the year they were built and the year they ended: "
     "temples, churches, mosques, castles, forts, palaces, bridges, towers, tombs, monasteries, stupas, "
     "citadels, city gates, theatres, monuments and archaeological sites; where Wikidata has no year at all, "
     "the year is the gazetteer's occupation window for the site and is marked estimated (B8, B16, B19)",
     "mixed", "fetch_buildings_wd.py, date_undated.py, build_famous_buildings.py"),
    (r"history/towns\.json\.gz", ["wikidata", "wikipedia", "own"],
     "towns through time: names by era, people by year, founding, provinces by era, who runs them", "recorded",
     "fetch_towns_wd.py, build_towns.py"),
    (r"history/state_relations\.json\.gz", ["cliopatria", "wikidata"],
     "ties between states by year: alliances, allegiance, vassals, shared rulers, realms, military alliances",
     "recorded", "build_relations.py"),
    (r"history/disputed_lands\.json", ["wikipedia", "own"],
     "land one state holds and another claims, in the mod's own words", "recorded", "hand-written"),
    (r"cards/cards\.tiles", ["wikidata", "wikipedia"],
     "knowledge cards for every place: famous people and groups (who, what, when, where, links), in tiles by land and "
     "century", "recorded", "fetch_cards_wd.py, build_cards.py"),
    (r"history/calendars\.json\.gz", ["wikipedia", "meeus", "own"],
     "which calendar each place actually used, by year: Hijri, Vikram Samvat, Saka, Fasli, Chinese, Julian before "
     "1582, regnal years of the ruling polity", "mixed",
     "build_calendars.py, hand-written from the Wikipedia article each row names"),
    (r"history/beliefs\.json\.gz", ["wikipedia", "own"],
     "what people believed, by place and year: the shape of the world, the body, matter, rule and the unseen, each "
     "row saying who held it and what we would say instead", "mixed",
     "build_beliefs.py, hand-written from the Wikipedia article each row names"),
    (r"knowledge/.*", ["wikipedia", "own"], "talk cards of a place and time", "recorded", "hand-written"),
    (r"vips/.*", ["wikipedia", "own"], "well-known people the engine can meet", "recorded",
     "hand-written, fix_history_data.py"),
    (r"scenarios/.*", ["wikipedia", "own"], "what-if scenarios", "estimated", "hand-written"),
    (r"history/life_table\.json\.gz", ["wikipedia", "own"],
     "how long people lived and when they married, by place and year (D2, D17): 30 mortality regimes "
     "and 14 marriage regimes, each a life table with survival from birth to ninety, and the age a "
     "man and a woman first married. Hand-written from the Wikipedia article each row names; the "
     "pre-modern regimes are marked estimated, because nobody counted",
     "mixed", "life_table.py, build_life_table.py"),
    (r"history/households\.json\.gz", ["wikipedia", "own"],
     "what a household is made of, by place and year (D3): 25 regimes giving the mean number of "
     "people under one roof, the shares of nuclear, stem, joint and one-person houses, the age a "
     "child leaves, how often the head is a widow, and how often a house kept a servant. "
     "Hand-written from the Wikipedia article each row names",
     "mixed", "households_table.py, build_households.py"),
    (r"history/jobs\.json\.gz", ["wikipedia", "own"],
     "what work there was, by place and year (D4): 23 occupations with the share of the people who "
     "did each, whether it is town work or country work, and the technology it needs. Bound to step "
     "30a's technology atlas, so a job does not exist before the thing it is made of",
     "mixed", "jobs_table.py, build_jobs.py"),
    (r"history/day_round\.json\.gz", ["wikipedia", "own"],
     "the shape of the day and of the year, by place and year (D5): whether the day is set by the "
     "task or by the clock, how many hours it runs, whether there is a day on which nobody works, "
     "how often the market comes round (the Roman nundinae every eighth day, the Javanese pasaran "
     "every fifth), how many times the day stops for prayer and in which faith, and how many "
     "seasons the year has. Hand-written from the Wikipedia article each row names",
     "mixed", "day_round_table.py, build_day_round.py"),
    (r"history/migrations\.json\.gz", ["wikipedia", "own"],
     "the roads people took when they had to go (C7): 38 movements, each with where they left, where "
     "they arrived, in what years, how many, whether anybody made them go, and what kind of going it "
     "was -- from the Partition of India in 1947 to the refugees of the Syrian civil war. Each route "
     "is handed to step 37's news-travel register, so a migration is a number of days and not a line "
     "on a map. Hand-written from the Wikipedia article each row names",
     "mixed", "migrations_table.py, build_migrations.py"),
    (r"history/health\.json\.gz", ["wikipedia", "britannica", "who", "owid", "own"],
     "what can kill you here and what anybody here can do about it (C20): 14 remedies -- the medicine "
     "of the four humours, quarantine, variolation, vaccination, clean water, epidemiology, the germ "
     "theory, anaesthesia, antiseptic surgery, penicillin, children's vaccines, oral rehydration -- "
     "each with the year and place it was learned in, and 18 named diseases with how they move, where "
     "they were first seen and how many of the people who caught them died. Six of the remedies ask "
     "step 30a's technology atlas when they reached a place, and the rest run the atlas's spread "
     "function from their origin, so medicine arrives somewhere rather than everywhere at once",
     "mixed", "health_table.py, build_health.py"),
    (r"history/scenes\.json\.gz", ["wikipedia", "britannica", "own"],
     "what is going on here, and who is in it (D9): the twenty event scenes -- a crowning, a court "
     "day, a procession, an election, a protest, a trial, an hour of prayer, a festival, a market "
     "day, a caravan or ship arriving, building works, a plague, a famine, a flight, refugees, a "
     "fire, a battle, a siege, a wedding and a funeral. Each one says what kind of ground it "
     "stands on, what sets it off, what the people in it are doing, and a cast given in the twelve "
     "work sectors of step 38's jobs register, so the scene is cast from the people this place and "
     "year actually has rather than drawn from thin air. The customs that had to be right were "
     "fetched rather than cited: the route of a Roman triumph, the assize courts and the end of "
     "trial by ordeal in 1215, the weekly market against the annual fair on its saint's day, the "
     "banns read on three Sundays, and the wake the night before a funeral. Five rows are "
     "recorded, four mixed and eleven estimated, and the estimated ones say so in the printed "
     "sentence",
     "mixed", "scenes_table.py, build_scenes.py"),
    (r"history/formations\.json\.gz", ["wikipedia", "own"],
     "how armies stood (D10): 16 named formations, each with the place and years it was used, the "
     "ground it wants, how deep and how wide it stands, and what it is carrying -- the chariot "
     "swarm, the hoplite phalanx, the Macedonian phalanx, the Roman line of cohorts, the "
     "elephant screen, the shield wall, the steppe horse archers, the ashigaru pike block, the "
     "Swiss pike square, the Spanish tercio, the Swedish brigade, the line and the column, the "
     "Civil War skirmish line, open order, the horns of the buffalo, and the fire team. A "
     "formation is asked for by latitude, longitude and year, and answers with the one the record "
     "says that place and year used. No row for the Americas before 1491, none for Oceania, and "
     "none for sub-Saharan Africa outside the Zulu kingdom -- not because those peoples did not "
     "form up, but because no article was read for them",
     "mixed", "formations_table.py, build_formations.py"),
    (r"history/battles\.json\.gz", ["wikipedia", "own"],
     "how a battle came out (D10): four casualty bands by weapon -- shock, bow, musket, rifle -- "
     "each giving the winner's share and the loser's, and four ways of losing -- gave ground in "
     "order, broke and ran, was ridden down, was encircled -- each multiplying the loser's band. "
     "The shock band is Krentz's survey of every surviving casualty figure from Classical Greek "
     "sources: the winner 3-10%, the loser 10-20%, and the gap between those two numbers is not "
     "marksmanship but the pursuit. The rifle band is lower than the musket band because casualty "
     "rates have been falling since the seventeenth century as armies dispersed faster than "
     "weapons got more lethal. Twenty matchups and nine kinds of ground decide the odds",
     "mixed", "battle_table.py, build_battles.py"),
    (r"history/sieges\.json\.gz", ["wikipedia", "britannica", "own"],
     "what a siege cost (D10): 11 kinds of wall from a ditch and a palisade to a city held "
     "street by street, 10 methods a besieger had from blockade to heavy guns, five ways a siege "
     "stops -- terms, starvation, relief, abandonment, storm -- and the two clocks that decide "
     "which: the wall clock, how long to make a practicable breach, and the food clock, how much "
     "bread the town has. Siege length is checked against the dates the record kept: "
     "Constantinople 1453 at 53 days against 53, Rochester 1215 at 50 against about 50, "
     "Kenilworth 1266 where no breach was ever made and hunger decided it. The distribution of "
     "the five endings is estimated, and it says so",
     "mixed", "siege_table.py, build_sieges.py"),
    (r"history/morale\.json\.gz", ["wikipedia", "britannica", "own"],
     "why men stand and what makes them stop (D10): 32 factors, each with the reason attached "
     "rather than a bare number, in two kinds -- what keeps a man in the army and what keeps him "
     "fighting -- and 23 tests that switch them on: the primary group, pay in arrears, plunder "
     "denied, the nation after the lev\u00e9e en masse, decimation in republican Rome, blocking "
     "detachments in the age of total war. Nine ways of raising an army, 11 measured desertion "
     "rates (Prussia 1713 at 3.2% a year, Saxony 1717 at 7.0%, the Army of Northern Virginia in "
     "1864 at 8.0%), and four ways of breaking. dispersion costs morale rather than granting it, "
     "after du Picq: the skirmish line needs more cohesion than the phalanx did, not less",
     "mixed", "morale_table.py, build_morale.py"),
    (r"history/sides\.json\.gz", ["wikipedia", "own"],
     "who was fighting, and as what (D10): 14 kinds of party -- a sovereign state, a dynastic "
     "house, a city commune, a religious body, a slave-soldier state, a rebellion, a separatist "
     "movement, a tribal confederacy, a warlord band, a steppe khanate, a hired company, a "
     "chartered company, a coalition, and civilians -- each saying whether it can be bound by a "
     "treaty, whether it can start a war, and how its men were raised. Brecke's rule that a party "
     "need not be a state is what puts a warlord band in the table at all, and the consequence "
     "is kept: a side containing a warlord band cannot be offered terms, which is the difference "
     "between a town opening its gates and a town being sacked. The catalog itself was not "
     "loaded; the taxonomy is read from its description of its own fields",
     "mixed", "sides_table.py, build_sides.py"),
    # Step 43 (J2). Both of these used to fall through to the catch-all below and were listed as
    # "engine settings and starting tables" counted in faiths, which described neither of them.
    (r"history/soundscape\.json\.gz", ["wikipedia", "own"],
     "what a place sounds like, by layer (J2): 27 sounds -- ground, crowd, voice and machine -- "
     "each with the faith or the technology that puts it there, the time of day it belongs to, and "
     "whether it is a recorded fact or a reading. The voices of faith (the call to prayer, the "
     "bell, the chant, the sermon) hang off the religion of the polity ruling the place, dated by "
     "that polity's own span in the ruler register, which is how 960 states get a faith at all when "
     "only twelve have hand-written dated ones. The machines hang off the technology atlas, so a "
     "place hears trains when the railway reached its country and not when a list happens to "
     "mention a station there. Written by hand, and every row says where it was read from",
     "estimated", "soundscape_table.py, build_soundscape.py"),
    # Step 43 (J3).
    (r"history/scripts\.json\.gz", ["wikipedia", "own"],
     "what the signs at a place are written in (J3): 40 scripts over 17 areas, each with the years "
     "it ran and what was written in it, and 11 kinds of sign standing at a place -- the edict cut "
     "in the rock, the boundary stone, the temple inscription, the grave, the milestone, the "
     "graffiti, the shop sign, the posted notice, the street name, the road sign and the official "
     "notice in two scripts -- each gated on the share of people who could read it and on the "
     "technologies that must have arrived first. Written by hand because the script of an "
     "inscription is not in any data set, and because the obvious chain (place -> language -> "
     "script) answers \"Aymara in the Latin alphabet\" at Cuzco in 1400, a century before any "
     "alphabet reached Peru. The gaps are listed in the file itself",
     "estimated", "script_table.py, build_scripts.py"),
    # Step 44 (E4, prices and wages through time): measured prices, not invented ones. The
    # absolute figures are "derived" because grain measured by the litre is converted to
    # kilograms at a bulk density, and because a series whose ordinary level is wildly out of
    # line with the same good elsewhere is marked suspect rather than trusted.
    (r"history/prices\.json\.gz", ["allenunger", "own"],
     "step 44 (E4): measured prices in grams of silver per unit - 773 series over 193 markets and "
     "89 goods, the years 965 to 1914 - each with an index against the price of its own time, plus "
     "1,225 shortage years read out of the grain prices themselves", "derived",
     "build_prices.py, price_markets.py, price_table.py"),
    (r".*", ["own"], "engine settings and starting tables", "estimated", "hand-written"),
]

# the key that holds a file's rows, when it is not simply the longest list
ROW_KEYS = {"history/world_rulers.json.gz": ("places", 3, "squares"),
            "history/towns.json.gz": ("towns", 1, "towns"),
            "history/state_relations.json.gz": ("relations", 1, "ties"),
            "history/technology_atlas.json.gz": ("techs", 1, "technologies"),
            "history/holy_places.json.gz": ("places", 1, "holy places"),
            "history/buildings_famous.json.gz": ("buildings", 1, "buildings"),
            "history/water_works.json.gz": ("works", 1, "works"),
            "history/deccan_rulers.json.gz": ("places", 1, "places"),
            "history/formations.json.gz": ("formations", 1, "formations"),
            "history/battles.json.gz": ("breaks", 4, "ways of losing"),
            "history/sieges.json.gz": ("walls", 1, "kinds of wall"),
            "history/morale.json.gz": ("factors", 1, "factors"),
            "history/sides.json.gz": ("parties", 1, "kinds of party"),
            # Step 43: without these the manifest counted the longest list, which is "faiths" for
            # the soundscape and happens to be right for the scripts while still missing its signs.
            "history/soundscape.json.gz": ("sounds", 1, "sounds"),
            "history/scripts.json.gz": ("scripts", 1, "scripts"),
            # Step 44: the longest list here is "series" (773 price histories), but the number
            # worth quoting is the markets.
            "history/prices.json.gz": ("places", 1, "markets"),
            # Step 44 part C: the longest list here is "products", which is also the right count.
            "economy/products_world.json": ("products", 1, "products"),
            # Step 44 part E: the longest list is "substitutes", and the number worth quoting
            # is the products covered rather than the links between them.
            "economy/substitutes.json.gz": ("substitutes", 1, "products"),
            # Step 44 part 6 (E6): the foods are the things that hold seats; the seats
            # themselves are only eleven.
            "food/seats.json.gz": ("foods", 1, "foods")}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def content_sha256(path):
    """The hash of what a pack MEANS, not of the bytes it happens to be stored in.

    Added 2026-10-22 after the marking turn found the manifest could never re-verify the
    shipped data: gzip writes the build time into the file header, so a no-op rebuild of an
    unchanged pack changes the file's sha256 (seen: calendars.json.gz fcfd9ab3... -> bd2cc4c6...
    with identical content, twice). The manifest therefore reported 9 "changed" packs after
    a day of test runs in which no fact had changed at all - and could never have reported a
    real change either, because every rebuild moves the hash.
    A .json.gz is parsed and re-serialised with sorted keys, so key order cannot mask or fake a
    change; anything else is hashed as raw bytes.
    """
    if path.endswith(".gz") or path.endswith(".json"):
        try:
            op = gzip.open if path.endswith(".gz") else open
            with op(path, "rt", encoding="utf-8") as f:
                obj = json.load(f)
            canon = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            return hashlib.sha256(canon.encode("utf-8")).hexdigest()
        except Exception:
            pass
    return sha256(path)


def excluded():
    """Data paths build.gradle leaves out of the jar (masters the game reads in another form)."""
    out = set()
    if os.path.exists(GRADLE):
        for m in re.finditer(r"exclude\s+'data/eternalengine/eternal/([^']+)'", open(GRADLE, encoding="utf-8").read()):
            out.add(m.group(1))
    return out


def rows_of(rel, path):
    try:
        if rel.endswith(".tiles"):
            with open(path, "rb") as f:
                head = f.read(4096)
            i = 8
            for _ in range(2):
                n = int.from_bytes(head[i:i + 2], "big")
                i += 2 + n
            return int.from_bytes(head[i:i + 4], "big", signed=True), "rows"
        if not (rel.endswith(".json") or rel.endswith(".json.gz")):
            return None, None
        op = gzip.open if rel.endswith(".gz") else open
        with op(path, "rt", encoding="utf-8") as f:
            doc = json.load(f)
        if rel in ROW_KEYS:
            key, per, what = ROW_KEYS[rel]
            return len(doc[key]) // per, what
        if isinstance(doc, list):
            return len(doc), "items"
        best, name = None, None
        for k, v in doc.items():
            if isinstance(v, list) and (best is None or len(v) > best):
                best, name = len(v), k
        return best, name
    except Exception:
        return None, None


def marks_note(rel, path):
    """The A5 mark in numbers, where the file carries it."""
    try:
        if rel == "history/world_rulers.json.gz":
            d = json.load(gzip.open(path, "rt", encoding="utf-8"))
            return (f"recorded until {d.get('recordedUntil')}, later years carry the last states forward; "
                    f"{len(d.get('estimated', []))} stretches of coastal squares taken from their neighbours")
        if rel == "history/deccan_rulers.json.gz":
            d = json.load(gzip.open(path, "rt", encoding="utf-8"))
            return f"recorded until {d.get('recordedUntil')}, later years carry the last states forward"
        if rel == "history/polity_facts.json.gz":
            d = json.load(gzip.open(path, "rt", encoding="utf-8"))
            facts = d if isinstance(d, list) else d.get("polities", d.get("facts", []))
            n = sum(1 for p in facts for k in ("head", "gov") for r in p.get(k, []) if len(r) > 4 and r[4] == 1)
            return f"{n} reigns whose end the list does not give (start + 25 years) are marked estimated"
        if rel.startswith("history/present_"):
            return "the places are recorded (OpenStreetMap); the years they were founded are estimated"
        if rel.endswith(".json") or rel.endswith(".json.gz"):
            op = gzip.open if rel.endswith(".gz") else open
            d = json.load(op(path, "rt", encoding="utf-8"))
            if isinstance(d, dict):
                for key in ("events", "sites"):
                    items = d.get(key)
                    if isinstance(items, list) and items and isinstance(items[0], dict):
                        est = sum(1 for e in items if str(e.get("confidence", "")).lower() == "estimated")
                        if est:
                            return f"{est} of {len(items)} {key} have estimated years"
    except Exception as e:
        return f"(not read: {e})"
    return ""


UNUSED_RULES = []


def build():
    gone = excluded()
    files = []
    for root, _dirs, names in os.walk(DATA):
        for n in names:
            path = os.path.join(root, n)
            rel = os.path.relpath(path, DATA).replace(os.sep, "/")
            if rel == "manifest.json":
                continue
            files.append((rel, path))
    files.sort()
    out = []
    used = set()
    for rel, path in files:
        rule = next(r for r in FILES if re.fullmatch(r[0], rel))
        _pat, srcs, role, mark, builder = rule
        rows, what = rows_of(rel, path)
        used.update(srcs)
        out.append({
            "path": rel, "bytes": os.path.getsize(path), "sha256": sha256(path),
            "contentSha256": content_sha256(path), "shipped": rel not in gone,
            "rows": rows, "rowsAre": what, "role": role, "sources": srcs,
            "licences": sorted({SOURCES[s][1] for s in srcs}), "mark": mark, "markNote": marks_note(rel, path),
            "builder": builder, "pack": "core"})
    shipped = [f for f in out if f["shipped"]]

    # A rule that matched nothing is a rule that will never be applied, which is the same failure as
    # the syntax gate's fixed list of ten files: it looks like coverage and is not. Report them.
    declared = {r[0] for r in FILES}
    matched = {r[0] for r in FILES
               if any(re.fullmatch(r[0], f["path"]) for f in out)}
    UNUSED_RULES[:] = sorted(declared - matched)
    doc = {
        "format": 1,
        "about": "Step 26 (A3, A7, K4): every data file of the mod with its size, SHA-256, rows, role, sources, "
                 "licences, recorded/estimated mark, builder and pack. Built by worldfill/build_manifest.py; checked "
                 "by /ee check all (com.eternalengine.data.DataManifest). Files with shipped=false are masters kept "
                 "for the build scripts and left out of the jar.",
        "packs": {"core": "everything, inside the mod (decision 5: data inside the mod, split into region packs only "
                          "if it grows too big; no download server)"},
        "totals": {"files": len(out), "shipped": len(shipped), "shippedBytes": sum(f["bytes"] for f in shipped),
                   "mastersOnly": len(out) - len(shipped)},
        "sources": {k: {"name": v[0], "licence": v[1], "duty": v[2]} for k, v in SOURCES.items() if k in used},
        "files": out,
    }
    return doc


def credits(doc):
    lines = ["# Data credits", "",
             "Eternal Engine's code is under the MIT licence. Its data files keep the licences of their sources, listed",
             "here. The game never shows sources in play; this file travels inside the mod (written by",
             "worldfill/build_manifest.py from data/eternalengine/eternal/manifest.json, step 26).", "",
             "Files built from CC BY-SA 4.0 sources (Wikipedia, the notable-people database) stay under CC BY-SA 4.0;",
             "files built from OpenStreetMap stay under the ODbL 1.0. Facts themselves are free; the game's sentences",
             "are written in the mod's own words.", "",
             "## Sources", "", "| Source | Licence | What it asks |", "|---|---|---|"]
    for k, s in sorted(doc["sources"].items(), key=lambda kv: kv[1]["name"].lower()):
        lines.append(f"| {s['name']} | {s['licence']} | {s['duty']} |")
    lines += ["", "## Files", "", "| File | What it is | Sources | Recorded or estimated |", "|---|---|---|---|"]
    for f in doc["files"]:
        if not f["shipped"]:
            continue
        names = ", ".join(sorted(doc["sources"][s]["name"].split(" (")[0].split(",")[0] for s in f["sources"]))
        note = f["mark"] + (f": {f['markNote']}" if f["markNote"] else "")
        lines.append(f"| `{f['path']}` | {f['role']} | {names} | {note} |")
    lines += ["", f"{doc['totals']['shipped']} files, {doc['totals']['shippedBytes']:,} bytes.", ""]
    return "\n".join(lines)


def main(argv):
    doc = build()
    text = json.dumps(doc, ensure_ascii=False, indent=1) + "\n"
    cred = credits(doc)
    bad = [f["path"] for f in doc["files"] if not f["licences"]]
    if UNUSED_RULES:
        for r in UNUSED_RULES:
            print(f"  RULE MATCHES NO FILE: {r}")
        bad.extend("unused rule " + r for r in UNUSED_RULES)
    nc = [f["path"] for f in doc["files"] if any(NON_COMMERCIAL.search(l) for l in f["licences"])]
    if "--check" in argv:
        same_m = os.path.exists(MANIFEST) and open(MANIFEST, encoding="utf-8").read() == text
        same_c = os.path.exists(CREDITS) and open(CREDITS, encoding="utf-8").read() == cred
        print(f"manifest.json: {'up to date' if same_m else 'OUT OF DATE'}; DATA_CREDITS.md: "
              f"{'up to date' if same_c else 'OUT OF DATE'}")
        return 0 if same_m and same_c and not bad else 1
    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write(text)
    with open(CREDITS, "w", encoding="utf-8") as f:
        f.write(cred)
    t = doc["totals"]
    print(f"manifest.json: {t['files']} files ({t['shipped']} shipped, {t['shippedBytes']:,} bytes; "
          f"{t['mastersOnly']} masters kept out of the jar); {len(doc['sources'])} sources")
    print(f"files without a licence: {len(bad)} {bad[:5]}; non-commercial licences: {len(nc)} {nc[:5]}")
    print(f"DATA_CREDITS.md: {len(cred.splitlines())} lines")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
