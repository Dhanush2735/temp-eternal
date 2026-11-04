# Every system the 7 requirements need: research and plan (turn 92, 2026-10-14)

Your request: "do research and plan for each and every direct or indirect possible system. according to my
requirements?"

This file lists every system I found that your 7 requirements (`REQUIREMENTS.md`) need, directly or indirectly. For
each system it says:
- what it is for;
- what exists now;
- where its facts come from and how it is built in Minecraft;
- how big it is;
- in which step it is done.

Part 2 is the research (sources, numbers, licences), part 3 is the systems, and part 5 is the order of work
(steps 21–61). This file replaces the order table in `REQUIREMENTS.md`.

## 1. How to read the tables

- **Needed for:** R1–R7 are your requirements. **D** means the requirement asks for it directly; **I** means it is
  needed so that a direct one works or looks right.
- **Now:**
  - **Done:** built and tested here.
  - **Partly:** some of it works.
  - **Old code:** it exists from the original upload, but it has not been reviewed or fed with real data yet
    (world-systems groups 3–12 in `WORLD_SYSTEMS.md`).
  - **Terra++:** your Terra++ build (`terra3/`) has it, according to its notes; I have not checked it in a game.
  - **Not yet:** nothing works yet.
- **Size:** S small (about one turn), M medium (2–3 turns), L large (4–8 turns), XL very large (done in parts over
  many turns).
- **One key for everything:** every system answers the same question: what is true here, at this date, in this
  timeline and in this universe? That key is system A1.

## 2. What the research found

### 2.1 Data sources

| Source | What it gives | Span | Licence | Used for |
|---|---|---|---|---|
| Wikidata (counted today through the QLever mirror) | 720,735 buildings and structures with a map point and a build date (282,921 built before 1900; 46,498 also have an end date); 10,808 railway lines with an opening date; 69,071 events with a map point and a date; 2,376,851 people born before 1950 with a birth date and a mapped birthplace; 184,779 cause-and-effect statements ("has cause", "has effect", "immediate cause of", "has immediate cause") | all | CC0 | B8, B14, C8, C9, C10 |
| Wikipedia | the primary source (turn 12) for everything told in words | all | the text is CC BY-SA: facts are free to use, but copied sentences need credit and share-alike. So game text stays in our own words, and credits go in a file outside play | all of C |
| OpenHistoricalMap | dated map features: buildings, roads, borders | all | CC0, except features tagged otherwise | B7, B12, C3 (Terra++ already uses it) |
| Historical Urban Population (Reba, Reitsma and Seto, 2016) | each city's name, map point, year, population and a reliability rank | 3700 BC – AD 2000 | free download with a login (NASA SEDAC) | B9, C5 |
| HYDE 3.3 | population, cropland, pasture and built-up area on 5-minute grids | 10,000 BC – 2023 | free with credit | B3, C6 (the people part is already used) |
| Itiner-e (2025) | 299,171 km of Roman roads around AD 150; 2.7% of the routes are known exactly, 89.8% roughly and 7.4% are guesses | AD 150 | open | B12 |
| Old World Trade Routes (OWTRAD, Ciolek) | trade routes of Asia, Africa and Europe, for example the Venetian galleys of 1400–1530 and the Viking routes of 950–1050 | various | copyright: needs the author's permission | B12, C17 |
| NOAA hazard databases | significant earthquakes from 2150 BC, 600+ volcanic eruptions from 4360 BC, 2,400+ tsunamis from 2100 BC, with deaths and damage | 4360 BC – now | US government, free | C21 |
| Conflict Catalog (Brecke) | 3,708 violent conflicts with sides, deaths and dates; weaker outside Europe before 1800 | 1400 – 2000 | free download | C8, D10 |
| Seshat Global History Databank | per state and period: social complexity, warfare, weapons, farming, religion | deep past – about 1900 | CC BY-NC-SA (no commercial use) | C19, G3 |
| Primitive technology (Comin, Easterly and Gong) | which technologies each land had, in five fields: farming, transport, communication, military, industry | 1000 BC, AD 0, 1500 | free | C16, E7, E10 |
| CHAT (Comin and Hobijn) | 104 technologies (railways, cars, electricity, telephones, radio and more) in 161 countries | 1800 – 2008 | public domain | C16, E10, B18 |
| Maddison Project 2023 | GDP per person and population for 169 countries | AD 1 – 2022 | CC BY 4.0 | C17, E4 |
| GRanD and the Global Dam Tracker | 6,862 dams with their build year; 35,000+ dams with completion years | to 2018 | free with credit | B2 |
| Glottolog 5.3 | the world's languages with map points | today | CC BY 4.0 | C14 |
| Numista and coin catalogues | coins and notes with dates, issuers and values | all | the facts are free; the photos belong to their owners, so coin pictures are drawn new | E1 |
| Castlemap | 9,079 castles, forts, palaces and ruins (built from Wikidata) | all | CC0 | B8, B16 |
| Already in the mod | the gazetteer, the rulers (Cliopatria), 122,422 dated events, HYDE people, the money table, the product atlas, Allen–Unger prices, crop origins (Khoury) | | | |

Links: Reba et al. `doi:10.1038/sdata.2016.34`; Itiner-e `doi:10.1038/s41597-025-06140-z` and itiner-e.org; NOAA
hazards at ncei.noaa.gov; Conflict Catalog at brecke.inta.gatech.edu; Seshat at seshatdatabank.info; CHAT at
nber.org/data/chat; primitive technology at dcomin.host.dartmouth.edu; Maddison at rug.nl/ggdc; GRanD at
globaldamwatch.org; Glottolog at glottolog.org; OHM at openhistoricalmap.org; OWTRAD at ciolek.com/owtrad.html.

### 2.2 Minecraft and Forge

- **Gravity** can be changed per entity: Forge 1.20.1 has the `forge:entity_gravity` attribute (base 0.08). I checked
  that it is there in the sandbox's Forge 47.2.0 jar. → H5.
- **A dimension's rules** come from its dimension type, which can set:
  - a fixed time (the sun stands still), skylight and ambient light;
  - "ultrawarm" (water boils away);
  - whether beds work or explode;
  - the coordinate scale.
  → H5. Terra++ already registers its universe dimensions in advance.
- **Vehicle mods for Forge 1.20.1:**
  - AstikorCarts Redux (horse carts and ploughs);
  - Small Ships (ships with cannons);
  - Immersive Vehicles (cars and planes);
  - Create has trains (to check).

  Vanilla has horses, donkeys, camels, boats and minecarts. → E10.
- **Performance on Forge 1.20.1:** measure with Spark. A common safe set is ModernFix, FerriteCore and Entity Culling,
  plus Embeddium (client) and Canary (server). → I9.
- **Paradox kinds:** the consistency ("grandfather") paradox and the causal loop ("bootstrap") paradox, and the idea
  that the past resists change (the Novikov self-consistency principle). → H1, G9.
- **What the mod already has, from the original upload (not reviewed or fed with real data yet):**
  - engines for technology, religion, climate (Little Ice Age), farming and famine, and disease and disasters;
  - trade with caravans, ships and bandits;
  - migration and social classes;
  - heraldry and historical sound.
- **What Terra++ (`terra3/`) already has:**
  - buildings and roads by year;
  - timeline branches that change buildings in place;
  - universes with other physics;
  - the paradox rupture.

  Its own notes list the link to the mod as "not yet done".

### 2.3 How close the world is to the real Earth (turn 93, measured with the world's own projection code)

`probes/bte/run.sh` runs Terra++'s real BTE projection (copied from `terra3/`) for 12 cities, and the height rule from
`TerraDensityFunctions.scaleElevation`:

| Place | 1 km on Earth is | True north, from Minecraft north |
|---|---|---|
| Hyderabad | 1,036 blocks | 29° to the left |
| Delhi | 1,019 blocks | 26° to the left |
| Mumbai | 1,063 blocks | 26° to the left |
| London | 1,086 blocks | 20° to the right |
| New York | 1,054 blocks | 17° to the left |
| Tokyo | 1,087 blocks | 95° to the left |
| Beijing | 1,294 blocks | 51° to the left |
| Sydney | 1,001 blocks | 37° to the left |
| Cairo | 1,005 blocks | 5° to the right |

Shapes are kept: north–south and east–west scale are the same at every place.

Heights:
- 1:1 up to 1,000 m above the sea and 2,000 m below it;
- above that, squashed: 2,000 m becomes 1,254 blocks, 4,500 m becomes 1,573 and Everest (8,849 m) becomes 1,969;
- dry land below sea level is shown at one tenth.

King Kothi's real block is about X 10,070,410, Z −2,026,016; Terra++'s public API gives X 1,215,455, Z 5,963,920.

## 3. All systems (166)

### A. Foundations (needed by every requirement)

| ID | System | Needed for | Now | Facts and method | Size | Step |
|---|---|---|---|---|---|---|
| A1 | The key: every answer depends on place, date, timeline and universe | all, I | **Done (step 26):** `core/WorldKey` (place, date, timeline, universe) and `core/WorldQuery`, the one door every game system asks; events follow the key's own timeline; other universes (dimensions) have no recorded history yet | facts a timeline changes (who rules, money) go into `WorldQuery` when systems G make them (step 47 on) | M | 26 |
| A2 | Calendar and clock | R2, I | Done: one calendar follows the Minecraft days, and only `/ee date` goes back | add local calendars for talk and papers: Hijri, Vikram Samvat, Saka, Fasli, Chinese, Julian before 1582, regnal years | S | 37 |
| A3 | Data pipeline: fetch, build, check, install | all, I | **Done (step 26):** `build_manifest.py` lists every data file (size, SHA-256, rows, role, sources, licences, mark, builder, pack) after every data script; `/ee check all` proves the game has exactly that data | one more script per new source | M | 26 |
| A4 | Data storage that streams by region and era | all, I | **Partly (step 26):** tiles by land and century (`build_tiles.py`, `data/TileStore`, `data/TileCache`, budget 48 MB); the famous people use them (40 MB → 8 MB, the same answers) | places and events (70 MB) in step 28, the border map (26 MB) in step 34; the knowledge cards (step 27) are tiles too (8.5 MB) | L | 26 |
| A5 | A "recorded" or "estimated" mark on every fact | R2, I | **Done (step 26):** the border map (recorded until 2024; 7,358 estimated stretches), reigns (217 guessed ends), places, population and ways of life; shown by `/ee villager who` and the checks, never to players | every new data set carries it | S | 26 |
| A6 | Fact checks | R2, I | Partly: spot checks, the fact audit | a spot check of 200 answers after every data step | M | every data step |
| A7 | Licences and credits | all, I | **Done (step 26):** `DATA_CREDITS.md` inside the mod, written from the manifest (22 sources; the OpenStreetMap credit was missing); no file forbids commercial use; checked by `/ee check all` | — | S | 26 |
| A8 | An on/off setting for each system | all, I | Partly | every new system gets one | S | every step |
| A9 | Tests: `/ee check all`, probes, the fake player, the long test walk | all, I | Partly | each step adds its own checks | M | every step |
| A10 | Saves per timeline and universe (world state, people, purses, notes) | R5, R6, I | **Done in step 52:** world state as deltas (step 51's `BranchSave`) plus `player/PocketSave` for people, purses and notes per (universe, branch) - a purse refused below zero, a note written once, `diff` checked against a full save | save only the differences | M | 52 |
| A11 | Time for several players: different years, timelines and universes at once | R5, R6, D | **Done in step 52:** `clock/Clocks` per decision 3 - one date and timeline per world, different years at once as different universes, a shared date moves everyone in it, and a private year in a shared world is always refused | decision 3 | L | 52 |
| A12 | The Terra++ link: heights, places, timeline branches, universes, the paradox counter | R1, R5, R6, D | Partly: heights and places. **Step 21:** map position → block uses the world's own projection (Terra++'s density functions) first; the public API only if its answer survives a round trip (435 places within 1 m; Charminar and King Kothi on the measured blocks). Still to do: every dimension is read with the prime projection, so a mirror universe would be read wrong | connect to Terra++'s own hooks; the projection of each universe | M | 51 |
| A13 | Working with other mods (weapons, vehicles, maps, Create) | R4, I | **Partly (turn 189): the weapons half is done.** `war/weapon_items.json.gz` - 9 optional weapon mods named by modid with licence and dependencies, 20 item rows, 2 ammunition rows, 163 name tokens, local names for 15 areas. `war/WeaponItems.java` - the resolver: an item TAG beats an item id (Spartan Weaponry renamed its registry between 1.16.5 and 1.19.2 and broke datapacks that hard-coded ids); an unknown item is GUESSED from its name and logged; and a missing weapon is never an error, because with no mod installed every kind falls back to the vanilla item the armoury already names on all 24 kinds (read, NOT duplicated). `war/WarGear.java` - the year gate: a musket is refused in 1200 Paris, an unlisted mod's toradar is refused in 1400 Agra, the gun benches stay shut until the rifle's year (AD 1866 in Europe), and nothing is ever taken out of a player's inventory. **The 18 hardcoded weapon items are gone** from RegimentCohort, RoyalCourtManager, CaravanEntityGroup, BanditAmbushEngine, MerchantShipConvoy and ChronoNexusCampaignEngine. **The mod ships no weapons of its own.** The vehicles half is also done (turn 196): `economy/vehicle_mods.json.gz` - 5 providers marked `read` (AstikorCarts Redux MIT, Small Ships, Minecraft), `content` (Immersive Vehicles and Create, which name NO id at all because their ids live in JSON content packs) or `vanilla`; all 32 vehicles resolve to a mod, a vanilla stand-in or a written reason there is neither, and 11 take the third answer. `vehicle/VehicleMods.java` reports what AstikorCarts' `pull_animals` and Small Ships' `dockyardBuildableShips` SHOULD hold for a place and year through the mods' own public surface rather than editing their config, and `VehicleModGate.java` refuses the Small Ships Dockyard, which has no crafting recipes at all, the same shape as the gun bench | **Done (turn 196)**: optional links; everything also works without them | M | 45, 46 |
| A14 | Time budgets: each system gets a share of each tick | R7, I | Partly: the spawner's 50 ms | measured in every test | M | every step |
| A15 | **Turn 95:** a review of the 69 old world systems (groups 3–12 in `WORLD_SYSTEMS.md`): each is kept and fed real data, or switched off (random incidents, random bandits, the AI brain, the web console, the fantasy parts of the old campaign) | all, I | Not yet (groups 1–2 reviewed) | `WORLD_SYSTEMS.md` | L | each phase reviews its own group |
| A16 | **Turn 95:** permissions: who may move time, change history or use admin commands when several people play | R5, R6, I | **Done in step 52:** `player/Permissions` - three kinds of act (only you / moves the shared world / rewrites what is recorded), a vote of the people the act moves with more than half needed, operator override on the record; the commands still gate on `hasPermission(2)` until wired | — | S | 52 |
| A17 | **Turn 95:** a backup before big changes (time jumps, timeline splits, ruptures) | R5, R6, I | **Done in step 51:** `timeline/BeforeChange` takes the copy by the code doing the damage, keeps it OPEN until the change is answered, refuses a second of the same kind, never rotates an open copy, and treats the 30-minute timed copy as no substitute | — | S | 51 |

### B. The Earth through time (R1)

| ID | System | Needed for | Now | Facts and method | Size | Step |
|---|---|---|---|---|---|---|
| B1 | The land 1:1 | R1, D | Terra++ | — | — | — |
| B2 | Water by era: coasts, deltas, river courses, shrinking seas; reservoirs only after their dam is built | R1, D | Not yet: today's water | dam build years (GRanD, the Global Dam Tracker); Wikipedia for big river and coast changes | L | 35 |
| B3 | Fields, pastures and forests by era | R1, D | Not yet: today's land | HYDE 3.3 cropland and pasture maps; what grows where (crop origins) | M | 35 |
| B4 | Climate and weather by era and season: monsoon, cold periods, droughts | R1, I | Old code (the Little Ice Age system) | climate reconstructions (to research); Minecraft weather and snow by region and season | M | 35 |
| B5 | Wild animals by era (lions and cheetahs in India, aurochs in Europe, no horses in the Americas before 1493) | R1, I | **Done (turn 197)** | Wikipedia and Wikidata (ranges, extinction dates) | M | 47 |
| B6 | Crops by era (no maize, potatoes or chillies in India before the 1500s) | R1, I | **Done (turn 197)** | crop origins (Khoury), Wikipedia | M | 47 |
| B7 | Mapped buildings by year | R1, D | **Checked (step 31):** works only where the map itself is dated. 0.9% of mapped OSM structures (181 of 19,272 at all 31 test places) carry a start_date; the rest fall to a region population floor, so today's map is drawn in antiquity, and 2 of 31 test places show nothing at all. Angkor 1150 is right because its temples are dated. Needs the mod's population gate (A12) and the dated buildings of step 32 | the mod's population gate (A12); step 32 | M | 31 |
| B8 | Famous buildings by year (temples, forts, palaces, mosques, churches, bridges, monuments), with build and end dates | R1, D | **Done (step 32)**: 23,534 famous buildings by year, dated where Wikidata is silent from the mod's own gazetteer and marked estimated; a Terra++ hook hands them out in Terra++'s own structure shape | Wikidata: 720,735 dated structures (282,921 before 1900; 46,498 with end dates); Castlemap | XL | 32 |
| B9 | Old towns where the maps are empty: houses, streets, markets, temples and walls, at the place's size and density | R1, D | **Done in step 33:** 109 building cultures by place and year name the house, its walls, roof and floor, the layout, the market and the storeys; what the maps give is still only 0.9% dated | city populations 3700 BC – AD 2000 (Reba); HYDE built-up area; the gazetteer; era styles per culture | XL | 33 |
| B10 | Building life: building works, standing, damaged, ruin, gone, repaired | R1, I | Old code (temporal rebuilding, idle) | events (war, earthquake, fire) change buildings | L | 36 |
| B11 | Inside buildings by era: homes, shops, temples, palaces | R1, I | **Done in step 33:** every building culture names what is inside a home (hearth, mats, pots, the shrine, the bedding) | furniture sets by era | L | 33 |
| B12 | Roads of the past: Roman roads, the Silk Roads, the Grand Trunk Road, royal roads, pilgrim routes | R1, D | **Step 34: 124,240 squares know the first year a dated road reached them** (Itiner-e -514..700, OHM, Wikidata); the gate is written, the map does not call it yet | Itiner-e (Roman roads); OWTRAD (with permission); OHM; Wikipedia | L | 34 |
| B13 | Road surfaces and street things by era: dirt, stone, brick, macadam, asphalt; oil, gas and electric lamps | R1, I | **Done in step 33:** every building culture names what the lanes are surfaced with; when the road itself should be laid is step 34 | rules by era and place | M | 33 |
| B14 | Railways by year: lines and stations | R1, D | **Step 34: 77,184 stations and 2,374 lines dated, and a first-railway year for 124,240 squares** — no railway before 1825 anywhere, Sydney 1850 has none | 10,808 dated railway lines (Wikidata); OpenStreetMap dates | M | 34 |
| B15 | Waterways: canals, ports, lighthouses, bridges by date | R1, D | **Step 34: 384 canals, 737 ports, 2,286 lighthouses, 3,831 bridges dated, plus a first-canal year per square** | Wikidata, OHM | M | 34 |
| B16 | City walls, gates and forts by era, and walls pulled down later | R1, D | **Done (step 32)**: 1,092 walls, gates, citadels and forts by year (castles left out on purpose: a castle is a fortified house) | Wikidata, Castlemap | M | 32 |
| B17 | Farm and water works: tanks and lakes (Telangana), stepwells, terraces, canals | R1, I | Not yet | Wikidata, OHM | M | 35 |
| B18 | Industry and utilities by era: mines, mills, factories, power and telegraph lines, airports | R1, I | **Step 34: 6,602 power stations, 2,031 works, 445 mills, 12,165 airports, 1,949 dams and 329 mines dated** | CHAT (when each arrived), Wikidata dates | M | 34 |
| B19 | Ruins: places in ruin in later years (Mohenjo-daro; Hampi after 1565) | R1, D | **Done (step 32)**: 2,569 buildings with a real end year, and 555 flagged as ruins where Wikidata never recorded the year they fell | end dates and ruin styles | M | 32 |
| B20 | Night light by era: dark old nights, lamps, electric light | R1, I | **Done in step 33:** every building culture names what it is lit by after dark, and the technology atlas moves it with the year (oil, gas, paraffin, electric) | light blocks by era | S | 33 |
| B21 | Player buildings across time jumps and timelines | R1, R5, I | Not yet (a Terra++ note) | keep or restore player edits per timeline | L | 36 |
| B22 | **Turn 95:** sky and time of day: local time by longitude (today one Minecraft sun serves the whole world), day length and sun height by latitude and season, the sun's direction (true north is turned, part 2.3), moon phases, real stars | R1, D | Not yet (a 20-minute day, one sun path everywhere) | astronomy formulas; the sky drawn per player | L | 35 |
| B23 | **Turn 95:** eclipses and comets on their real dates (recorded, and feared, in history) | R1, R2, I | Not yet | NASA eclipse lists, comet dates (to research) | S | 35 |
| B24 | **Turn 95:** what lies under the ground: real coal, iron, copper, gold, diamonds (Golconda), salt, oil, for mining, goods and industry | R1, R4, D | **Step 34: 143,302 deposit sites, 57 minerals, from USGS MRDS, hand-written famous deposits and Wikidata's oil fields** | MRDS (public domain), Wikipedia, Wikidata | M | 34 |
| B25 | **Turn 95:** water supply and sanitation by era: wells, stepwells, tanks, aqueducts, sewers, piped water | R1, I | **Done in step 33:** 1,634 built water works with years (Wikidata), and every building culture names where a house's water comes from; sanitation beyond the 2 rows Wikidata has is not there | Wikipedia, OHM | M | 33 |
| B26 | **Turn 95:** rest houses and road marks: caravanserais, sarais, dak bungalows, milestones (kos minars) | R1, I | **Step 34: 121 caravanserais dated — thin, no dataset covers them** | Wikidata, OHM | S | 34 |
| B27 | **Turn 95:** disasters that change the land: eruptions, floods that move rivers, earthquakes | R1, I | Not yet | NOAA, Wikipedia | M | 36 |

### C. History data (R2)

| ID | System | Needed for | Now | Facts and method | Size | Step |
|---|---|---|---|---|---|---|
| C1 | States, borders, rulers | R2, D | Done. **Step 25:** the known errors fixed (prime ministers named as rulers, occupations named as the occupier, names used long after their state, the Nizam's Hyderabad State, coastal squares, 2025–2026). **Step 26:** rebels and the occupations of the Second World War are not the state (S8), Ireland, Moldova, St Croix; 89 border cities follow their own country (S9: Kinshasa, Tijuana, Basel, Geneva, Nice...) | the gaps before 1800 (known problem 34) | M | 25 |
| C2 | Local rulers and officials: governors, nawabs, zamindars, mayors | R2, D | Partly (**step 29:** "Who runs this town?": the town's head and its province's head with their years, 3,724 offices, 30,206 holders; 1,578 towns have their own head; zamindars not yet) | Wikidata "position held" with dates | L | 29 |
| C3 | Divisions by era: provinces, subahs, districts | R2, I | Partly (**step 29:** "Which province is this?" by era for 27,585 towns, 15,849 provinces; by town, not yet as areas between towns) | Wikidata "located in" with dates; OHM borders | M | 29 |
| C4 | Place names by era and language (Bhagyanagar; Bombay becoming Mumbai in 1995) | R2, D | **Done in step 29** (3,892 towns with names by era from Wikidata, Wikipedia's list of city name changes and a hand table from the towns' articles; every history site that is a town takes its name of the year; "It was called Bombay until 1995") | Wikidata names with dates; Pleiades | M | 29 |
| C5 | Towns' lives: founding, growth, decline, abandonment | R2, D | Partly (**step 29:** founding, growing and shrinking for the town list; abandonment only through the history sites' years) | city populations (Reba); Wikidata founding and end dates | M | 29 |
| C6 | How many people, and who | R2, D | Done (estimates; **step 29:** census figures by year for 24,983 towns) | HYDE; city figures (Reba) | S | 29 |
| C7 | Migrations and refugees (the 1947 Partition and others) | R2, D | Old code (migration system) | Wikipedia | M | 38 |
| C8 | Events: wars, battles, sieges, treaties, revolts, crownings, deaths, foundings, disasters, epidemics, famines | R2, D | **Done (step 28):** 129,163 dated events in the history data; 32,542 event cards (`cards/events.tiles`: what, when, where, who took part, deaths, links), 23,062 of them the history data's own events, the years cross-checked with the history data | Wikidata (69,071 events with a map point); the Conflict Catalog (3,708 conflicts); NOAA; Wikipedia lists | L | 28 |
| C9 | Cause and effect between events (the butterfly graph) | R5, I | **Done (step 28):** the graph in the event cards, stored both ways: 2,346 causes, 2,276 effects, 17,404 part-of, 689 came before, 686 came after (all 3,151 cause-and-effect statements Wikidata has between dated things); walked by step 49 | Wikidata's 184,779 cause-and-effect statements, plus "part of" and "follows" | L | 28 |
| C10 | Famous people: births, deaths, homes, offices, deeds | R2, R3, D | **Done (step 27):** 148,510 people cards (birth and death with their places, the home town, up to three offices and three works with their years, studied at, party, served in, worked for, member of, founded), chosen from 1,959,134 people with a mapped birthplace, cross-checked with the Wikipedia year pages (`build_cards.py`) | Wikidata: 2,376,851 people born before 1950 with mapped birthplaces | XL | 27 |
| C11 | Families and dynasties | R2, R3, D | **Done (step 41):** 95,585 parent edges, 32,394 marriages, 91,168 named relatives, 3,312 houses and 534 dynasties over one pack; a person's page names his parents, spouse, children, house and dynasty | Wikidata father, mother, spouse, child | M | 41 |
| C12 | Organisations: companies, guilds, armies, parties, universities, newspapers | R2, I | **Done (step 27):** 26,855 group cards: schools and universities 10,586, companies 7,607, parties 2,528, newspapers 2,189, armies 2,173, guilds and societies 1,513, religious orders 259 (founded, closed, seat, founders) | Wikidata | M | 27 |
| C13 | Faiths by place and era; holy places, festivals, pilgrimages | R2, D | Partly: faith lines in talk; old religion engine. **Step 30b:** 19,828 holy places with their years, the festivals and pilgrimages of 30 faith families, Christian and Islamic feast days by the calendar | Wikipedia; Wikidata | M | 30 |
| C14 | Languages and scripts by place and era; names | R2, D | Partly: names by language. **Step 30b:** the script of 97 languages by years (Turkish Latin from 1928 ...); languages before 1500 are still the state's | Glottolog; Wikipedia | M | 30 |
| C15 | Culture: clothes, food, music, games, customs, arts | R2, R3, D | **Done (turn 197)** | Wikipedia | L | 47 |
| C16 | Technology by place and era: the **technology atlas** (when each technology reached each region, how common it was, its versions, losses) — `TECHNOLOGY_PLAN.md` | R2, R4, D | Partly (**step 30a:** the atlas: 130 technologies, the year each reached each of 258 countries (3,499 recorded from Wikipedia, 226 from CHAT, the rest estimated and marked), the spread inside a country, how common (CHAT for 10 household things), losses, versions; "What new things are there here?"; vehicles by place; the country grid). **Step 21:** the 7 technologies have their first known years and never come earlier (moving the date back takes them away); vehicles have first years too (a train from 1825, a car from 1886). Not yet linked: the old 7-technology engine, medicine steps by era, buildings, weapons, tools | Wikipedia first; CHAT (1800–2008); primitive technology (1000 BC, AD 0, 1500); Wikidata (thin); spread rule for the gaps | L | 30a |
| C17 | Economy: prices, wages, wealth, taxes, banks, crises, trade routes | R2, R4, D | Partly: money, goods, prices. **Step 30b:** wealth by land and year (Maddison) and 26 hard times (hyperinflations, depressions); prices, wages, taxes and banks in step 44 | Maddison; Allen–Unger; OWTRAD | L | 30 |
| C18 | Law and rights by era: law codes, punishments, weapon laws, slavery and its end, votes, caste and class rules | R2, R3, D | Not yet | Wikipedia | M | 42 |
| C19 | Armies: units, ranks, tactics, weapons and armour by state and era | R2, R3, D | **Done (turn 189):** `war/units.json.gz` - 15 ladder systems, 69 rungs, 17 areas, 10 named to a polity verified against the mod's own 1,581-name ruler register. The organising finding is that **an army is counted in whatever base the society counts in**: ten (Mongol, Inca, Ming), twenty (Aztec), three (the Indian epics), two (Sparta), eight (Rome, whose century of eighty kept the name of a levy of a hundred) - and **no number at all for the Zulu**, whose amabutho count by birth year. Two systems rank MEN not units (Mughal mansabdari, Aztec captives). **Seshat was not used** (closed by standing instruction); Wikipedia was, which the plan named anyway | Wikipedia | L | 45 |
| C20 | Health: diseases, epidemics, medicine, life span | R2, D | Old code (disease engines) | Wikipedia lists of epidemics | M | 38 |
| C21 | Natural events: earthquakes, volcanoes, tsunamis, floods, cyclones, droughts | R2, D | **Done (step 28):** storms (5,884 landfalls since 1842, IBTrACS), floods, wildfires, tornadoes, epidemics, landslides, heat waves, avalanches, famines and droughts (1,844, Wikidata), with step 12's earthquakes, eruptions, tsunamis and plagues (26,997); the old disaster engine (block effects) waits for event scenes (step 39) | the NOAA databases | M | 28 |
| C22 | Knowledge cards for every place (who, what, when, where, links) | R2, R3, D | **Partly (step 27):** every place: the people talked about and the groups known, each with a card worded for the date (who, what they did, where from with the compass, links to further cards), the ruler linked to the ruler's card, the history book finds them; step 28: event cards with causes and effects, the news linked to them, "What happened here before?" for every place; still to come: local rulers and divisions (step 29) | the card pipeline | XL | 27 |
| C23 | News by era: criers, inscriptions, newsletters, papers, radio, television | R2, D | Partly: crier, newsletter, paper | rules by era | M | 37 |
| C24 | The speed of news: news travels as fast as its era allows | R2, R3, I | Not yet | runners, riders, ships, the telegraph from the 1850s, radio | M | 37 |
| C25 | The data fix (1 answer in 10 was wrong) | R2, D | **Done in turn 102:** `fix_history_data.py`, 8,680 changes, each listed and reversible; the fact check's "wrong" findings 1,543 → 44, wrong lines heard by 12–18% of people (1850–1900) → under 0.5% | a spot check after every data step | M | 25 |
| C26 | **Turn 95:** weights, measures and distances by place and era (seer, maund, tola, gaz, kos, cubit, mile), for prices and talk | R2, R4, I | **Done in step 30b** (35 systems by land and era, the metric year of every country, "How do people here measure things?"; prices in these units come with step 44) | Wikipedia | S | 30b |
| C27 | **Turn 95:** reading and schooling by place, era, class and gender: who can read the paper or the book | R2, R3, I | Partly (**step 30b:** who reads by land, year, town size and sex; schools and who may buy the paper or the book not yet) | literacy data (to research), Wikipedia | S | 30b |
| C28 | **Turn 95:** relations between states by date: alliances, vassals, tribute, trade partners | R2, R5, D | Partly (**step 29:** "Which states is it tied to?": 538 ties from Cliopatria's relations and realms and 16 military alliances; tribute and trade partners not yet; the old treaty engine not reviewed) | alliance data (to research), Wikipedia | M | 29 |
| C29 | **Turn 95:** ideas and beliefs by era: what educated people knew or believed (the shape of the Earth, medicine, the stars), for talk | R2, R3, I | Partly (knowledge levels) | Wikipedia | M | 37 |

### D. People who live and act out history (R3)

| ID | System | Needed for | Now | Facts and method | Size | Step |
|---|---|---|---|---|---|---|
| D1 | Spawning and numbers | R3, D | Done | — | — | — |
| D2 | Who they are: names, looks by era, region, class and job, age | R3, D | Partly | skins, name lists | M | 38 |
| D3 | Families and homes | R3, D | Not yet | households from the population model | L | 38 |
| D4 | Jobs and workplaces by era | R3, D | Partly: roles | job lists by era and place | L | 38 |
| D5 | Daily life by era and culture: work, prayer times, market days, festivals, seasons | R3, D | Partly: simple day rounds | calendars (A2), faiths (C13) | M | 38 |
| D6 | Needs and mind: food, safety, faith, money, mood | R3, I | Not yet (villager plan step 3) | — | L | 38 |
| D7 | Social order: class, caste, guilds, who may speak to whom | R3, D | Old code (class system) | C18 | M | 42 |
| D8 | Talk (done), and rumours passed from person to person | R3, D | Partly | C24 | M | 37 |
| D9 | Event scenes: battle, siege, crowning, court day, procession, festival, prayer, market day, plague, famine, flight from flood or earthquake, fire, building works, refugees, election, protest, trial, wedding, funeral, a caravan or ship arriving | R3, D | **Done (step 39):** `people/Scenes.java` over `history/scenes.json.gz` - twenty scenes, each with the ground it stands on, what sets it off and a cast in step 38's twelve work sectors, so a scene is cast from the people this place and year has and is not on at all where fewer than half the parts can be filled. **Fighting is not staged here** - that is D10 | C8 + D2 + E9 + E12 | XL | 39 |
| D10 | Armies in action: formations, sieges, weapons of the era, morale, sides | R3, D | **Done (step 40):** five registers over five packs - `Formations` (16 dated formations), `Battles` (4 casualty bands by weapon, 4 ways of losing), `Sieges` (11 walls, 10 methods, 5 endings, two clocks), `Morale` (32 factors, 9 ways of raising, 11 measured desertion rates, 4 ways of breaking) and `Sides` (14 kinds of party, 6 of which cannot be bound by a treaty). The old flat **8% winner / 18% loser** is gone: the loser's share is now a consequence of *how the loser went*, and the gap between the two sides is the pursuit (Krentz: winners 3-10%, losers 10-20%, and the gap is not marksmanship). A siege is a race between the wall clock and the food clock, checked against the dates the record kept (Constantinople 1453 in 53 days against a recorded 53). **Weapons themselves are D22 / step 45** - this step reads what an army was carrying, it does not write it | C19, E9 | XL | 40 |
| D11 | Famous people where and when they were: homes, courts, journeys | R3, D | **Done (step 41):** 352,250 stays over 58,375 places, each with the years and the reason; 64% of people are somewhere other than their birthplace; T. H. White is in Cambridge in 1928 | C10, C22 | L | 41 |
| D12 | Rulers decide (in changed history: wars, taxes, heirs) | R5, D | Old code (succession, court) | G3 | L | 49 |
| D13 | Reactions: to the player, to the law, to strange clothes and things from the future | R3, D | Old code (reputation) | — | M | 42 |
| D14 | Animals in daily life: oxen, horses, camels, elephants, herds | R3, R4, I | **Done (turn 196)** | B5, E10 | M | 46 |
| D15 | The background crowd (cheap figures) | R3, R7, I | Done. **Step 21:** a figure you talk to becomes a townsperson and stays; places with no ground are remembered for 5 minutes and one cycle gives up after 256 refused places (the slow cycle) | — | S | — |
| D16 | A working economy: makers, buyers, sellers, workers | R3, R4, D | Partly: sellers and buyers | E5 | L | 44 |
| D17 | **Turn 95:** the life cycle: births, ageing, marriages and deaths as the years pass; the same families through generations (today a remembered person never ages) | R3, D | Not yet (planned in the villager plan) | the population model | L | 38 |
| D18 | **Turn 95:** friendship and greetings: people remember you, greet you by name and keep an opinion of each player (villager plan step 8) | R3, I | Not yet | — | M | 42 |
| D19 | **Turn 95:** Minecraft's own creatures in a history world: night monsters, pillager patrols and raids (the world has raids switched on), wandering traders. Switched off, or replaced by real dangers (bandits, wolves, tigers, storms, disease) | R1, R3, D | Partly. **Step 21:** off by default, with three settings (`[minecraftMobs]`: monsters, raids and patrols, wandering traders); spawn eggs, spawners and `/summon` still work; the Nether and the End are not touched. Real dangers of the era come later | the spawn events (done); bandits, wolves, tigers | S | 40, 47 |

### E. Things of the world (R4)

| ID | System | Needed for | Now | Facts and method | Size | Step |
|---|---|---|---|---|---|---|
| E1 | Money as items for every place and era: coins, notes, shells, weighed metal | R4, D | **Done (step 23b):** money is pieces in the inventory, in 16 looks (gold, silver, copper, holed cash, nickel, paper, cowries, cacao beans, cut silver, weighed copper, manillas, nzimbu shells, salt bars, cloth, beaver pelts, bullet coins); pieces for all 398 monies with coins, by year; paying with exact change; merchants and the money-changer pay in pieces; the start money and old purses become pieces; barter keeps a written tab (swapping goods: done in step 24) | the money table; currency articles; coin facts; our own pictures | L | 23b |
| E2 | Real money where the data has only placeholder money | R4, R2, D | **Done (step 23a):** 401 kinds of money, 1,006 rows, 124 fixed rates, a day's pay per place for shared monies; placeholders for 0.0% of people (were 41.5%), 0.1% of land (lakes and empty islands, like the sea); 121 test places | Wikipedia currency articles; Wikidata's 1,729 currencies as a cross-check | M | 23a |
| E3 | Minecraft's trade screen: buy, sell, change money, swap goods, old money | R4, D | **Done (step 24):** Minecraft's villager trade screen with real slots (two to pay, one to take, the inventory); clicking a trade fills the slots from the bag; any mix of money taken here pays, change back; selling a lot at a time; changing any amount; bigger and smaller pieces; swapping goods where people have no money (the tab pays, too much is owed back); old and foreign money refused with the reason; cowries as small change beside manillas; out of the purse when two slots cannot hold the pieces | needs E1 | M | 24 |
| E4 | Prices and wages through time; shortages | R4, D | Partly | Maddison, Allen–Unger, events | M | 44 |
| E5 | Goods: about 400 kinds, the chains from raw to made, disruptions | R4, D | Partly: 129 kinds | product atlas parts C, D, E | L | 44 |
| E6 | Food and drink by era and region | R4, D | Partly | crops (B6), Wikipedia | M | 44 |
| E7 | Tools and inventions as items: ploughs, looms, printing, clocks, the compass, guns, radio, telephone | R4, D | **Done (turn 197)** | C16 | M | 47 |
| E8 | What can be made or used in a year (a time traveller setting for exceptions) | R4, R6, I | **Done (turn 197)** | C16; things from the future feed paradoxes (H1) | M | 47 |
| E9 | Weapons and armour: all five ways to get them, era rules, laws | R4, R5, D | **Done (turn 189):** `war/armory.json.gz` - 24 kinds, each with the year it reaches each of 17 areas, when it leaves, where it NEVER existed and why (no bow in Australia, no metal sword in the Americas before 1492, no war chariots below the tsetse belt), what retires it, and a vanilla item that stands for it. `war/arms.json.gz` - the five ways an army comes by weapons (issued, bring, buy, take, gift) plus **carry**, which is a sixth because keeping and carrying are different laws in every age. `history/law.json.gz` kind 5 - 13 weapon laws keyed by the POLITY that rules the square, not by area, because a weapon law is a fact about a government | `WEAPONS_RESEARCH.md`; weapon mods | L | 45 |
| E10 | Vehicles of every era: porters, palanquins, carts, chariots, horses, camels, elephants, bicycles, rickshaws, trams, buses, cars, lorries; rafts, dhows, galleys, junks, sailing ships, steamships; trains; balloons, airships, planes | R4, D | **Done (turn 196)**: the old route checker is now driven by the vehicle and traffic registers | vanilla animals and boats; mods (AstikorCarts Redux, Small Ships, Immersive Vehicles, Create); dates from C16 | XL | 46 |
| E11 | Traffic: vehicles of the era moving on roads, rivers, seas and rails | R4, D | **Done (turn 196)** | B12, B14, E10 | L | 46 |
| E12 | Clothes and armour looks by era, region, class and job | R4, R3, D | **Done (turn 197)** | skin pools | M | 47 |
| E13 | Writing: books, papers, maps, letters, inscriptions, signs in local scripts | R4, D | Partly: paper, map; the history book is bought, in 13 forms by place and year (step 22) | C14 | M | 43 |
| E14 | Building materials by era: mud brick, fired brick, stone, timber, lime, concrete, steel, glass | R1, R4, I | **Done in step 33:** every building culture names its walls, roof and floor, and the years brick, cement, steel and glass reached a place come from the technology atlas | style rules | M | 33 |
| E15 | Medicine and healers by era | R4, I | **Done (turn 197)** | C20 | S | 47 |
| E16 | Lighting and energy: oil lamps, candles, gas, electricity | R4, R1, I | **Done in step 33:** part of every building culture, asked of the technology atlas year by year and by the size of the town | C16 | S | 33 |
| E17 | Games and sports: chess, polo, cricket, kites, theatre, cinema | R4, I | **Done (turn 197)** | Wikipedia | S | 47 |
| E18 | Animals and crops as items, as they spread | R4, I | **Done (turn 197)** | B5, B6 | M | 47 |
| E19 | **Turn 95:** banking and credit: money-lenders, banks, savings, loans, interest, bills of exchange (hundi) | R4, I | Not yet | Wikipedia | M | 44 |
| E20 | **Turn 95:** post and messages: couriers, post offices, telegrams, telephones (they set the speed of news) | R4, I | Not yet | Wikipedia, the technology atlas | S | 37 |
| E21 | **Turn 95:** clothes the player can wear to blend in (people react to strange clothes) | R4, R3, I | **Done (turn 197)** | E12 | M | 47 |
| E22 | **Turn 95:** vanilla things that do not belong (enchanting, potions, diamond and netherite gear, ender pearls): locked or renamed by era, as a setting | R4, I | **Done (turn 197)** | E8 | S | 47 |

### F. What players can do (this feeds R5 and R6)

| ID | System | Needed for | Now | Facts and method | Size | Step |
|---|---|---|---|---|---|---|
| F1 | Ways to change history: stop or help an event (works now), kill or save a person, win or lose a battle, take the crown, found a town, bring an invention early, tell people the future, trade, sabotage, marriages | R5, D | Partly: stopping an event | G1 | L | 48 |
| F2 | Reputation, sides and loyalty | R5, I | Old code (reputation) | — | M | 42 |
| F3 | Law and crime by era: guards, courts, punishment | R3, I | Not yet | C18 | M | 42 |
| F4 | Property per timeline: houses, land, shops | R5, I | **Done in step 52:** `player/Property` - deeds per (universe, branch), one place one deed, sell/give/release recorded with every change of hands, confiscation for operators, and the same blocks lawfully owned by different people on different branches | A10 | M | 52 |
| F5 | Player roles: merchant, soldier, courtier, ruler, scholar | R5, I | Partly: selling | — | M | 48 |
| F6 | The story campaign (Chrono-Nexus) | R6, I | **Done in step 56:** `chrononexus/Campaign` per decision 7 - the story in six stations; a chapter not kept is continued, never failed; the pressure is a gauge; a player is never erased; the old engine's countdown is left untouched and uncalled | decision 7 | — | 56 |
| F7 | Several players: shared or separate timelines; who may change history | R5, R6, D | **Done in step 52:** `player/Together` - shared or separate with no third state, changing history needs BOTH axes (Agency's in-world and Permissions' server) with the refusal naming whichever said no, and two hands on one thing keep the first and refuse the second by name (speed votes stay the live mechanism) | A11 | M | 52 |
| F8 | **Turn 95:** borders and permits: crossing from one state to another (tolls, customs, passports from the First World War, quarantine) | R2, R3, I | Not yet | C18 | M | 42 |
| F9 | **Turn 95:** time travel for players: how a player reaches another year inside the game. Today only admin commands do it, and the old time machine item only prints "use the command". It must fit "only /ee date moves back" (turn 64) and decision 3 | R5, R6, D | Old code (a placeholder) | — | L | 48 |
| F10 | **Turn 95:** who you are: start year and place, local or time traveller, your family line (the grandfather paradox needs it), your starting kit | R5, R6, I | **Done in step 52:** `player/WhoYouAre` - the card made once and never edited, the family line checked at making (a parent born after their child refused), `chainToYou` and `ancestorsAliveAt` for the grandfather paradox, a traveller's line carried not recorded | — | M | 52 |
| F11 | **Turn 95:** tasks tied to real history: errands and roles (deliver a letter to the palace, help build a landmark) | R3, R5, I | Not yet | knowledge cards | M | 48 |

### G. Alternative timelines and the butterfly effect (R5)

| ID | System | Needed for | Now | Facts and method | Size | Step |
|---|---|---|---|---|---|---|
| G1 | What counts as a change: events, people, places, knowledge, goods | R5, D | Partly: events only | — | M | 48 |
| G2 | Which later events depend on the change | R5, D | **Done in step 49:** `timeline/Depends` and the what-if engine, 232 checks over six parts | C9 | L | 49 |
| G3 | The "what if" engine: heirs, war results from each side's strength, borders, money, people, inventions, faiths; effects spread with distance and time; big trends resist change | R5, D | Partly: later events are taken away | rules, no AI (turn 47); Seshat and Maddison for strength | XL | 49 |
| G4 | Written "what if" stories for the 100 biggest events | R5, D | **Done in step 50:** stories are readings of the packs in a voice, on a surface the record has standing there, and not one invents an event; the 100 biggest events are step 51's list | data files | L | 50 |
| G5 | New knowledge for each timeline: cards, papers, talk from templates | R5, D | **Done in step 50:** `knowledge/BranchKnowledge` - a claim is AUTHORED with a name or MODELLED with nobody's, two branches of one year share nothing, and a claim no card asks for is reported | — | L | 50 |
| G6 | The world follows the timeline: buildings, landmarks, roads | R5, R1, D | **Partly, in step 51:** `terrabridge/BranchWorld` decides what stands on a branch from the record and refuses what it cannot place; drawing it is one narrow `Port` that Terra++ has yet to implement, and with none the class refuses every decision instead of pretending | Terra++'s branch hook | L | 51 |
| G7 | The timeline tree in the book; travel between timelines | R5, D | **Done in step 51:** `timeline/BranchTree` walks both ways, draws orphans and loops as broken rather than as absent, pages the book, and travels - with the rule that **a branch cannot be entered before it split** and a branch with no save cannot be entered at all | — | M | 51 |
| G8 | Cheap saves of each timeline (only the differences) | R5, R7, I | **Done in step 51:** `timeline/BranchSave` - the root whole once, each branch as changed + removed + its pins, and `diff` checks the cheap copy key by key against a full save and names the branch whose delta introduced each disagreement; 22.4% of the cost on the fixture | A10 | M | 51 |
| G9 | Fixed points: events that resist change and become paradoxes if forced | R5, R6, D | **Done in step 53:** `timeline/FixedPoints` - a declared register; it resists by refusing the in-place change and naming the branch, forcing breaks it on the record and books its paradox, rebuilding gives the weight back | — | M | 53 |
| G10 | **Turn 95:** the book shows both what really happened and what happened in your timeline | R5, I | **Done in step 50:** `knowledge/VoicedCard` holds more than one answer to one question on one day, each with a voice and a provenance; the answers `Question.at` silently dropped are now reported by `shadowed()` | G5 | S | 50 |

### H. Paradoxes and new universes (R6)

| ID | System | Needed for | Now | Facts and method | Size | Step |
|---|---|---|---|---|---|---|
| H1 | Paradox kinds: grandfather (undo the cause of your own arrival, or destroy a dated fixed point), causal loop (give people a thing or idea that has no origin), predestination (your attempt causes the event), meeting yourself, telling the future | R6, D | **Done in step 53:** `timeline/Paradox` - the five kinds as five tests, each answering with the paradox or with the words that clear it; grandfather reads the frozen family line (step 52), causal loop reads the technology atlas's own origin years | — | L | 53 |
| H2 | One paradox counter shared with Terra++ (events, people and things add to it) | R6, D | **Done in step 53:** `timeline/Stress` - one counter in named parts, every addition explained, repair brings it down, Terra++ reaches it through one seam whose `absent()` says not counted rather than zero | the Terra++ hook | M | 53 |
| H3 | Rupture: a new universe with other land (sea level, height, upside down, mirrored) | R6, D | **Done in step 54:** `terrabridge/LandSpec` + `timeline/Ruptures` + `timeline/RuptureEngine` - the land spec and the check key by key against what Terra++ reports; a rupture needs its copy taken first and must change the land to count | gen. via Terra++ (this mod checks) | M | 54 |
| H4 | Broken logic: time runs backwards, eras mixed, events loop or come out of order, effects before causes, doubles of famous people, money values upside down, scrambled languages | R6, D | **Done in step 55:** `timeline/BrokenLogic` - a rule set of seven kinds, each naming what it bends; `diff` key by key; `scan` proves three kinds from dated entries and names the four it can never prove | rule sets per universe | L | 55 |
| H5 | Broken physics within Minecraft: gravity (`forge:entity_gravity`), a fixed or racing sun, light, water that boils away (ultrawarm), exploding beds, extreme weather, strange mobs, floating blocks | R6, D | **Done in step 54:** `terrabridge/BrokenPhysics` - nine facts, each naming its mechanism (Minecraft attribute, dimension-type flag, or mod-side rule); four of nine are mod-side or half so and no screen may say Minecraft applied those | the Forge attribute; dimension types | L | 54 |
| H6 | The story goes on in the new universe: its own history, people, papers and book | R6, D | **Done in step 55:** `story/UniverseStory` + `story/UniverseBook` - the four surfaces keyed (universe, place), the mark computed from the year, the AD 3000 guardrail enforced, and every surface read through the rule set naming every rule applied | A1 with the universe; G3 rules | L | 55 |
| H7 | Travel: portals and rifts, the way back | R6, D | **Done in step 56:** `timeline/Passage` - one crossing books both legs at once (the way back before the way out); a return is only along your own ticket; nobody is stranded; rift tickets say they are unstable | — | M | 56 |
| H8 | Repair: rebuilding a fixed point lowers the stress | R6, I | **Done in step 56:** `timeline/Repairs` - one call joining `FixedPoints.restore` to `Stress.repair`, the fall that happened reported, the clamp at zero said out loud | — | S | 56 |

### I. Performance (R7)

| ID | System | Needed for | Now | Facts and method | Size | Step |
|---|---|---|---|---|---|---|
| I1 | Measuring: per-system times (exists), Spark, the 30-minute test walk | R7, D | **Done in step 57:** `core/PerfBudget` + the walk probe - 30 places x 16 years x 8 registers, budgets each naming their source, every blow named in words; Spark stays the live tool | — | M | 57 |
| I2 | Time budgets per system per tick | R7, D | Partly | A14 | M | every step |
| I3 | Heavy work off the game thread: loading, planning, path searches | R7, D | **Done in step 57:** `core/OffThread` - work is a class, not a place; loads measured at 1.2-1.4 s; a job on the wrong side refused by name; results hand back before they touch the world | — | M | 57 |
| I4 | Far away means numbers only: people, vehicles, armies | R7, D | **Done in step 57:** `core/Distances` - past 128 blocks people, vehicles and armies are counts, not bodies; the population engine remembers them | — | L | 57 |
| I5 | Drawing crowds on the client: detail by distance, hiding what cannot be seen | R7, D | **Done in step 57:** `core/Distances` - the draw thins at 24 and 64 and hides at 160 or the client's own view, whichever is nearer; the lines are game defaults and say so | — | M | 57 |
| I6 | Data size and memory limits | R7, I | Partly. **Step 26:** measured (`probe_memory.sh`: 160 MB → 128 MB of data registers); budgets checked by `/ee check all` (opened tiles 48 MB, compressed tiles 16 MB, all data 64 MB) | the rest of A4 | M | 26 |
| I7 | Network: packet sizes and rates | R7, I | **Done in step 57:** `network/PacketBudget` - a packet over Minecraft's limit refused by name and by how much; rate budgets named in words over any window | — | S | 57 |
| I8 | Waiting while Terra++ rebuilds after a time jump | R7, D | **Done in step 57:** `terrabridge/RebuildWait` - the wait is a state, not a stall: queued/rebuilt/left in words, a second wait refused, no invented chunks | A12 | M | 57 |
| I9 | Performance mods for your pack (checked to work with Terra++) | R7, I | Done in step 58 | Spark, ModernFix, FerriteCore, Entity Culling, Embeddium, Canary | S | 58 |
| I10 | **Turn 95:** a hardware and settings guide for players (memory, view distance) | R7, I | Done in step 58 | — | S | 58 |
| I11 | **Turn 95:** disk use: world saves grow as chunks are rebuilt for many years; cache limits | R7, I | **Done in step 57:** `core/CacheLimits` - caches evict oldest first and count every drop; a chunk keeps 12 rebuilt years (game default) and the save line says which copies go | Terra++ | S | 57 |

### J. Look and sound (indirect)

| ID | System | Needed for | Now | Facts and method | Size | Step |
|---|---|---|---|---|---|---|
| J1 | Screens: talk, trade, book, paper, map, compass | all, I | Partly (step 24: trading is on Minecraft's own trade screen, drawn with the game's pictures; the talk keeps one price question instead of one option per good. The look of all screens is checked in your final test) | — | M | 24 |
| J2 | Sounds of the era: calls to prayer, temple and church bells, markets, trains, cars | R3, I | Old code (crowd sound, historical sound) | — | M | 43 |
| J3 | Signs and inscriptions in local scripts | R1, I | Not yet | C14 | M | 43 |
| J4 | Sky and air: smoke, haze, dust | R1, I | Not yet | — | S | 43 |
| J5 | First steps for a new player | all, I | Done in step 59 | — | S | 59 |
| J6 | **Turn 95:** game text in other languages (Hindi, Telugu, Urdu and others), optional | all, I | Not yet | — | M | later |

### K. Tools (indirect)

| ID | System | Needed for | Now | Facts and method | Size | Step |
|---|---|---|---|---|---|---|
| K1 | Data tools (fetch and build scripts) | all, I | Done, and growing | — | — | every data step |
| K2 | Checks: `/ee check all`, probes, spot checks | all, I | Partly | — | — | every step |
| K3 | Records: README, the test checklist, the requirements, this plan | all, I | Partly | — | — | every step |
| K4 | Delivering data: inside the mod, or downloaded | all, I | **Done (step 26):** decision 5, everything inside the mod in one pack ("core"); masters for the scripts stay out of the jar; a size budget of 64 MB | region packs only if the data outgrows the budget | M | 26 |
| K5 | Upgrading saved worlds between versions | all, I | Partly | — | S | every step |
| K6 | **Turn 95:** the known problems list (part 8), carried from step to step until each is fixed | all, I | Partly (part 8) | — | — | every step |

## 4. What needs what

- The trade screen (E3) needs money as items (E1).
- Event scenes (D9) need events (C8), looks (D2, E12) and weapons (E9).
- Old towns (B9) need town sizes (C5), building materials (E14) and era styles.
- The "what if" engine (G3) needs:
  - the cause-and-effect graph (C9);
  - rulers who decide (D12);
  - the key with timelines (A1).
- The world following a timeline (G6) needs the Terra++ link (A12).
- Paradoxes (H1–H6) need timelines (G), fixed points (G9) and the shared counter (H2).
- Once the data grows past today's size, everything needs storage that streams by region and era (A4). That is why
  step 26 comes early.

## 5. The order of work: steps 21–61

| Step | What | Systems |
|---|---|---|
| **Phase 0: the turn-90 points** | | |
| 21 | People stay while you talk or trade — **done in turn 97** (with the map position fix, Minecraft's mobs off, first years for technologies and vehicles, the slow crowd cycle) | D15, D19, A12, C16 |
| 22 | The history book is bought from villagers — **done in turn 98** (13 forms by place and year, from clay tablets to the notebook; knotted cords, message and tally sticks where nobody writes; sellers, prices, the talk) | E13 |
| 23a | Real money for the placeholder places, every region at once — **done in turn 99** (401 kinds of money from Viking weighed silver and manillas to the euro in Bulgaria 2026; placeholders for people from 41.5% to 0.0%; a day's pay per place) | E2 |
| 23b | Money as items for every place and era: coins, notes, shells, weighed metal; paying with them; purses become coins — **done in turn 100** (16 looks; pieces for 398 monies in every year; a day's pay in at most 9 pieces; exact change everywhere; tested from Bombay 1948 to Edo 1700, Calabar 1800, Moscow 2026 and barter in Sydney 1500) | E1 |
| 24 | Minecraft's trade screen — **done in turn 101** (the villager's trade screen with real slots: buy with any mix of money taken here and get change, sell a lot at a time, change any amount, bigger and smaller pieces, swap goods where people have no money, cowries as small change in Calabar; tested in Bombay 1948, Calabar 1800, Cahokia 1150, Moscow 2026 and Edo 1700) | E3, J1 |
| **Phase 1: history data (R2)** | | |
| 25 | The history data fix — **done in turn 102** (rulers, state names by period, occupations, the Nizam, coastal squares, 2025–2026, languages and faiths by period, news lines, famous people; each change listed and reversible) | C1, C25 |
| 26 | Foundations for big data: the key, streaming storage, estimate marks, licences, data delivery — **done in turn 103** (one key and one query for every system; tiles by land and century, famous people 40 → 8 MB with the same answers; recorded/estimated marks; the data list with hashes, licences and credits checked in game; memory measured and budgeted; plus the Second World War occupations and 89 border cities fixed) | A1, A3, A4, A5, A7, I6, K4 |
| 27 | The card pipeline: famous people, organisations, knowledge for every place — **done in turn 105** (148,510 people and 26,855 groups as cards in tiles, cross-checked with the year pages; every place names its people and groups with links; nobody known before their time; the ruler linked to the ruler's card) | C10, C12, C22 |
| 28 | Events, natural events, cause and effect — **done in turn 106** (32,542 event cards with the cause-and-effect graph stored both ways; the news linked to them; "What happened here before?"; 5,884 storm landfalls and 1,844 other natural events; occupied land of the Second World War and six disputed lands in the ruler line) | C8, C9, C21 |
| 29 | Local rulers, divisions, place names, towns' lives, population — **done in turn 107** (30,151 towns with names by era, people by year, founding, provinces by era and who runs them; every history site that is a town takes its name of the year: Bombay 1900, Edo 1700, Léopoldville 1955; 538 ties between states: allegiance, vassals, realms, NATO and the Warsaw Pact) | C2, C3, C4, C5, C6, C28 |
| 30a | The technology atlas (turn 94, `TECHNOLOGY_PLAN.md`); the later steps that need it read it — **done in turn 108** (130 technologies in 16 fields, the year each reached each of 258 countries: recorded from Wikipedia, from CHAT, or estimated by the spread rules; how common, cities first; losses; "What new things are there here?"; the fastest travel by place; a country grid for every point) | C16 |
| 30b | Economy, faiths, languages — **done in turn 109** (who reads, by land, year, town size and sex; the script of each language by years; 35 systems of measures and every country's metric year; wealth and hard times; 19,828 holy places, the festivals and pilgrimages of 30 faiths, the Christian and Islamic feast days by the calendar) | C13, C14, C17, C26, C27 |
| **Phase 2: the Earth through time (R1)** | | |
| 31 | Check Terra++'s buildings and roads by year in the test places — **checked in turn 110** (Terra++'s own dating code run outside Minecraft on today's OSM at 21 test places: 19,272 ways at all 31 test places, only 0.9% carry a start_date; undated structures fall to the 14 region population floors, so today's map is drawn in antiquity — Ur 2500 BC 156/156 shown, Cusco 1500 850/850, Rome AD 100 367; Cahokia 1100 and Greenland 1000 show nothing at all; Angkor 1150 is right because its ancient temples are the dated anchors; `OsmDateInferencer` is dead code) | B7 |
| 32 | Famous buildings, walls and ruins by year — **done in turn 114** (23,534 famous buildings with a point, a start year and where known an end year; 1,330 dated from the site packs and 1,334 from the gazetteer where Wikidata is silent, all marked estimated; 1,092 walls, gates, citadels and forts for B16 with castles left out on purpose; 2,569 with a real end year and 555 flagged as ruins for B19; a Terra++ hook hands them out in Terra++'s own structure shape; 16 probe checks pass, 10 µs a lookup) | B8, B16, B19 |
| 33 | Old towns: houses, insides, streets, materials, lights | B9, B11, B13, B20, E14, E16, B25 |
| 34 | Roads, railways, waterways and industry of the past — **done in turn 121** (`ways.grid.gz`: 124,240 squares with the first year a railway, a dated road or a canal reached them, years -514..2026, merged from OpenHistoricalMap (1,076 tiles), the mod's Itiner-e Roman roads and this step's dated works; `ways_works.json.gz`: 110,447 works in 14 kinds, 82,304 with a recorded year and 28,143 estimated from the technology atlas and flagged; `minerals.json.gz`: 143,302 deposit sites, 57 minerals; a Terra++ hook answers "may this be drawn here yet?" — 15 hook checks and the register probe pass; B26 rest houses are thin at 121) | B12, B14, B15, B18, B24, B26 |
| 35 | Water, fields, forests and climate by era | B2, B3, B4, B17, B22, B23 |
| 36 | Building life; player buildings across time | B10, B21, B27 |
| **Phase 3: people act out history (R3)** | | |
| 37 | Event time, calendars, news by era and how fast it travels | A2, C23, C24, D8, C29, E20 |
| 38 | Who people are: jobs, families, daily life, needs, migrations, health | D2, D3, D4, D5, D6, C7, C20, D17 |
| 39 | Event scenes | D9 |
| 40 | Armies in action | D10 |
| 41 | Famous people at their homes; families and dynasties | D11, C11 | ✅ Done (turn 149) |
| 42 | Law, reputation, social order, reactions | C18, D7, D13, F2, F3, D18, F8 |
| 43 | Sounds, signs, writing, sky | J2, J3, J4, E13 |
| **Phase 4: things of the world (R4)** | | |
| 44 | Goods, prices, food, a working economy | E4, E5, E6, D16, E19 |
| 45 | Weapons and army gear | E9, C19, A13 | **Done (turn 189)** |
| 46 | Vehicles, traffic, working animals | E10, E11, D14, A13 | **Done (turn 196)** |
| 47 | Tools, what can be made when, clothes, animals and crops, wildlife, culture | E7, E8, E12, E15, E17, E18, B5, B6, C15, E21, E22 | **Done (turn 197): seven parts, eleven systems, 520 checks. See README.md** |
| **Phase 5: changing history (R5)** | | |
| 48 | Ways to change history; what counts as a change; player roles | F1, F5, G1, F9, F11 |
| 49 | Cause and effect, the "what if" engine, rulers decide | G2, G3, D12 |
| 50 | Written stories and new knowledge for each timeline | G4, G5, G10 |
| 51 | Connect to Terra++'s timelines; the timeline tree; cheap saves | A12, G6, G7, G8, A17 |
| 52 | Several players in time; property; saves per timeline | A10, A11, F4, F7, F10, A16 |
| **Phase 6: paradoxes and universes (R6)** | | |
| 53 | Paradox kinds, fixed points, one paradox counter | H1, H2, G9 |
| 54 | The rupture check and broken physics | H3, H5 |
| 55 | Broken logic, and the story in the new universe | H4, H6 |
| 56 | Travel between universes; repair; the old campaign | H7, H8, F6 |
| **Phase 7: performance and the finish (R7)** | | |
| 57 | Performance: the long test walk and fixes | I1, I3, I4, I5, I7, I8, I11 |
| 58 | Checking performance mods | I9, I10 |
| 59 | First steps for new players | J5 |
| 60 | Your final test in the real game | all |
| 61 | Fixes from your test | all |

In every step: fact checks (A6), on/off settings (A8), tests (A9), time budgets (A14, I2), records (K1–K3), save
upgrades (K5) and the known problems list (K6). Each phase also reviews its own group of old systems (A15). Game text
in other languages (J6) comes after step 59, if wanted.

## 6. Decisions (my defaults from turn 96; the user now only says "next")

The user (turn 96): "from here onwards i will only say next till completion of the project. dont stick to particular
place or year. think of each and every location and year." So I take these defaults, unless the user changes one.

| # | Question | My default | Why |
|---|---|---|---|
| 1 | The history data fix (C25) | **Do it** (step 25). Wikipedia first, every change listed and reversible — **done in turn 102** | requirement 2 cannot be met with known wrong answers |
| 2 | Terra++ changes | **Mod side first**, through Terra++'s own public hooks. A Terra++ change only where nothing else works, kept as a separate listed patch for the user's own Terra++ build | Terra++ is the user's other project |
| 3 | Several players and time | **One shared date and timeline per world**; universes are separate dimensions, so players can be in different universes. Time travel moves the world's date for everyone, by the same allowed path as `/ee date` (turn 64), with a vote or operator permission when several people play | Terra++ builds each chunk for one year, so two players cannot see two years in the same place |
| 4 | Data that forbids commercial use (Seshat) | **Do not use it**; open data and Wikipedia instead | keeps the mod free of licence limits |
| 5 | Data delivery | **Inside the mod**, split into region packs if it grows too big; no download server is needed | there is no server to host downloads |
| 6 | Vehicles and weapons | **Use other mods when installed**, simple built-in ones otherwise | works with and without the mods |
| 7 | The old Chrono-Nexus campaign | **Fold its useful parts** (time machine, paradox countdown) into time travel (F9) and paradoxes (H); switch its fantasy parts off by default | requirement 6 replaces it |
| 8 | The turn-90 picks | loose coins, Minecraft's own trade screen, one "History book" item | as proposed in turn 90 |
| 9 | The technology atlas (step 30a) | **Yes** | `TECHNOLOGY_PLAN.md` |
| 10 | Minecraft's monsters, raids and wandering traders (D19) | **Off by default in step 21**, with a setting to switch them back on | they do not belong in a replica of history |

## 7. Honest limits

- **Size:** 166 systems (turn 95; counts after **step 31**):
  - 32 done and 70 partly done (B9, B11, B13, B20, B25, E14 and E16 moved to done with step 33;
    B8, B16 and B19 moved to done with step 32; B7 moved from "in Terra++" to partly: checked in
    step 31 and found to work only where the map is dated);
  - 14 in old code that is not reviewed yet;
  - **step 34 in progress (parts 1–2 of 6, turns 118–119):** rows fetched for B14, B15, B18 and
    B26 (122,080 of them, 82,304 dated) but **no pack shipped yet**, so those four are still
    counted where they were; B12 and B24 come in parts 3 and 4;
  - 4 in Terra++;
  - 46 not started;
  - nothing waiting (the history data fix was done in step 25).

  This is a very long project of 43 steps (with 23a and 23b, 30a and 30b), and the big steps take several turns each.
- **"Each and every":** recorded history is copied; where the record is empty, there are estimates, marked as
  estimates. Unrecorded history cannot be copied.
- **Data with limits:**
  - OWTRAD needs its author's permission.
  - Seshat's main databank forbids commercial use, so it is not used (decision 4); Cliopatria, its border map, is CC BY 4.0 and is used (step 26 checked every licence: `DATA_CREDITS.md`).
  - Coin photos belong to their owners, so we draw our own.
  - Wikipedia sentences need credit, so the game uses its own wording.
- **What this sandbox cannot show:** a real Terra++ world, the game's picture and true multiplayer. Look, feel and
  real speed are checked in your final test (step 60, your rule).

## 8. Known problems carried forward (turn 95)

| # | Problem | Where it gets fixed |
|---|---|---|
| 1 | People vanish while you talk or trade (the crowd is rearranged while you stand still) | **fixed in step 21** |
| 2 | Map position → block uses Terra++'s public API, which does not match the world (Charminar lands off the map) | **fixed in step 21** |
| 3 | The old technology engine has no dates; vehicle eras allow cars from 1500 | **fixed in step 21** (first years); the spread by region in step 30a |
| 4 | "Republic of India, ruled by George VI" on 1 January 1948 | **fixed in step 25** ("Dominion of India, ruled by George VI", 1947–1949; at Hyderabad "Hyderabad State, ruled by Asaf Jah VII (Nizam)" until 1948) |
| 5 | After a long jump, townspeople come back slowly (1 after 20 s, 2 after 40 s) | **looked into in step 21:** with ground, 40 people stand in 6 s; the wait is for the chunks (in a game, Terra++ building the ground; in the sandbox, ground only near the join point). The debug line names the reason. Measure in step 57 |
| 6 | One spawner cycle of 918 ms after a 3 km jump (it did not repeat) | **fixed in step 21:** places with no ground were looked up again every cycle, once more for every waiting figure (20,803 look-ups, 254 ms, in one sandbox cycle) |
| 7 | Walking through new ground still invents people where no town centre is near (step 17) | step 38 |
| 8 | The name lists are thin. Step 21 saw a crowd figure on the Bombay coast in 1948 called "Sam Stone": where the language map has no answer, the English list is used | step 30b (languages), step 38 |
| 9 | Minecraft monsters, raids and wandering traders appear in history | **fixed in step 21** (settings) |
| 10 | The old time machine item only prints a message | F9 (step 48) |
| 11 | The "Add to Xaero's map" link has never been tried in a game | your final test (step 60) |
| 12 | Step 21: every dimension is read with the prime projection; a mirror universe would turn east and west the wrong way for the mod | step 51 |
| 13 | Step 21: on a dedicated server the client dressed everybody for the year 400 (it has no clock and did not read "year_1948") | **fixed in step 21** |
| 14 | Step 21: "… has left.", walking away and the turning to face you can only be seen in a real game (the fake player has no screen) | your final test (step 60) |
| 15 | Step 22: in Rome in AD 100 the townspeople's civilization label is "republic_of_italy" (today's country); names, dress and money are right | **fixed in step 25** (the cause: people remembered from another year came back with their old label; now only people of the same people and within 100 years come back) |
| 16 | Step 22: nobody lives at Sydney in 1700: the settlement data starts with 1788, though the Eora lived there | step 38 (estimated life), step 30b |
| 17 | Step 22: the history book's forms use the product atlas's 17 areas plus 13 local rules (paper going north in Europe, inland Africa, the West African forest, the court of Kongo, the Andes, Australia, the Pacific...). A finer spread (paper in Tibet, Korea, Java; Maya books) belongs to the technology atlas | step 30a |
| 18 | Step 22: the talk box shows 9 questions. A money-changer in Bombay used all 9 with the new notes question; one with news on top would lose the last one ("Where can I get the news?") | **fixed in step 24:** buying, selling, swapping and changing moved to Minecraft's trade screen; the talk keeps "Let's trade." and one price question ("What do you buy?") instead of one option per good or money |
| 19 | Step 22: the new item pictures (13 forms) and the welcome line can only be seen in a real game | your final test (step 60) |
| 20 | Step 23a: the ruler register's half-degree cells cannot tell some twin cities apart (Kinshasa and Brazzaville, 5 km apart, both get the CFA franc); Geneva and Basel are fixed by hand with small boxes | **fixed in step 26** (S9: all 4,074 cities of 100,000 people or more and every capital checked; 89 border cities that named another country get a place of their own with their own country's history, 16 twins across the border keep theirs; Kinshasa pays in Congolese francs, Brazzaville in CFA francs) |
| 21 | Step 23a: the register names the Soviet Union for occupied Eastern Europe (1946) and Czechoslovakia (1968–1991), the Polish–Lithuanian Commonwealth for Saxony under its Saxon kings, "British Africa" for Palestine in 1940. The money rows work around them; other parts of the game still see them | **fixed in step 25** (Czechoslovakia, the Republic of Poland, Hungary, the Kingdoms of Romania and Bulgaria, Allied-occupied Germany, Iran; the Electorate of Saxony; Mandatory Palestine, the Emirate of Transjordan, Iraq); the money probes pass unchanged |
| 22 | Step 23a: hyperinflations (Germany 1923, Hungary 1946, Greece 1944, Yugoslavia 1992–1994, Zimbabwe 2006–2008, Venezuela 2016–2021) jump between yearly wage anchors | step 44 (prices and wages through time, E4) |
| 23 | Step 23a: commodity money is coarse: at Calabar 1800 a day is 3 manillas, so every small thing costs 1 manilla (cowries are taken as small change); salt bars, homespun cloth and the made beaver likewise. Step 23b made them pieces you hold, but there is still no piece smaller than 1 manilla | **fixed for manillas in step 24:** under 4 manillas prices and payments are in cowries (a notebook 266 cowries, paid with a manilla and 29 cowries back). Salt bars, homespun cloth and the made beaver have no small money in the data yet: step 44 |
| 24 | Step 23a: one money per place, with a few "also taken": ports where rupees, thalers and Spanish dollars passed side by side show only the main one | **partly in step 24:** the trade screen takes every money a place takes (fixed rate, or small change by what it buys) and the money-changer changes any money, any amount; the data still lists only 4 places with money "also taken" (trade coins at ports: Spanish dollar, Maria Theresa thaler, Venetian ducat): step 44 |
| 25 | Step 23b: the look of a piece follows a rule of thumb by value and era, not every real coin: a 5-penninge piece in Oslo 1200 never existed (only pennies did), some brass coins show as silver (the sestertius), and where modern coins end and notes begin differs from country to country (the €5 note is right, a $1 coin is shown where the US used notes) | step 44 (prices and wages through time, with a per-money list of real coins where it matters) |
| 26 | Step 23b: `/ee reset confirm` and `/ee purse reset` cannot take pieces from players who are offline, or out of chests: pieces are items. A new story campaign therefore starts with whatever money players kept | step 52 (several players in time; property) |
| 27 | Step 23b: barter keeps a written tab ("goods worth about 1 day's work"), and coins are taken as metal only through a trader; swapping goods for goods, and paying with metal by weight, need a screen | **fixed in step 24:** goods for goods on the trade screen, at what he pays for yours; a trader takes coins as metal by what they buy; the tab pays first, and what you give too much he owes you |
| 28 | Step 23b: the money-changer changes all of one money at once (refused above 2,304 pieces: "Change less at a time") | **fixed in step 24:** he changes what you put in the slots (5 euros of 38 in Moscow 2026: 49 rubles) |
| 29 | Step 23b, seen in the server session: a merchant in Edo 1700 has a Chinese name ("Liu Wang"); the townspeople's name pools mix regions for traders | step 30b (languages), step 38 (who people are), as problem 8 |
| 30 | Step 24: Minecraft's trade screen can only be seen in a real game (the fake player has no screen); its look was checked from pictures drawn with the game's own textures and font, its server side with the fake player clicking the real menu | your final test (step 60) |
| 31 | Step 24: old money is changed by what it bought in its day, not by the metal in it (a sicca rupee of 1857 brings about 8 O.S. rupees in 1948) | step 44 (prices and wages through time; metal value of coins) |
| 32 | Step 24, seen in the server session: names at Cahokia 1150 borrow from other American peoples ("Isabel of Tenochtitlan", "Tupac of Cusco") | step 30b, step 38, as problems 8 and 29 |
| 33 | Step 24, seen in the server session: at Hyderabad 1948 the test world stood nobody up after a jump from Moscow (all 13 spots "inside a player's bubble"); Bombay, Calabar, Cahokia, Moscow and Edo were fine | step 57 (performance and spawning in a real world) |
| 34 | Step 25: the fact check still finds 44 "wrong" and 207 "likely wrong" lines. Most are names it cannot confirm, because it compares a corrected period name with the old state's dates (the Restored Toungoo Kingdom after 1599, the post-Angkor Kingdom of Cambodia, "Tibet"); also 821 runs of years with no ruler named (mostly before 1800, where no list exists), 213 guessed end years and 83 news lines placed at sea | **step 26:** the guessed end years are marked as estimates (findings 1,549 → 1,329); the rest in step 27 (the card pipeline) and step 28 (events) |
| 35 | Step 25, seen in the server session: Italians in Rome 2026 get names from the Mediterranean list, some of them Greek ("Polites Sophia Nikolaou") | step 30b (languages), step 38 (who people are), as problems 8 and 29 |
| 36 | Step 25: "people here speak …" uses one point per language (Glottolog) plus 32 points added for big languages; a village far from every point of its own language can still name a neighbour's | step 30b (languages) |
| 37 | Step 26: only the famous people are tiles; places and events (70 MB) and the border map (26 MB) still load whole at start | step 34 (places, events and the map together; step 28 kept the events where the event index reads them, and added 7,728 more: 73 MB now) |
| 38 | Step 26: between a border city and its twin across the border the answer follows the nearer city (a straight line, not the real border); villages near a border still take their map square's state | step 34 (finer borders) |
| 39 | Step 26: Palestine's towns keep the record's answer (the West Bank is named "State of Israel", Gaza "Gaza/Hamas"), and Crimea is left as the record has it | **fixed in step 28** (`history/disputed_lands.json`: the West Bank, the Gaza Strip, the Golan Heights, Crimea, Northern Cyprus and Western Sahara say who holds the land and who claims it) |
| 40 | Step 26: occupied lands now name their own state, but nobody says "under German occupation" or "under Japanese occupation" yet | **fixed in step 28** (`history/occupations.json.gz`, 7,302 squares read from the record before step 26's fix: "German troops have held this land since 1940") |
| 41 | ✅ Fixed in step 41 (D11): 352 people with a card were within 30 km of Cambridge in 1928 and only 6 of them were born there; T. H. White is one of the 352 and not one of the 6. Was (step 27): people are placed by their birthplace: someone born in Bombay who lived in England (T. H. White) is talked about in Bombay, and the famous of a city who were born elsewhere are not "from here" | step 38 (who people are): residences and places of work (step 29 built the town list, not residences) |
| 42 | Step 27: names and descriptions are today's: "Mahatma Gandhi" before 1914, Victoria's card is "Victoria", a description may name a later country ("a university in Bologna, Italy" in 1100) | partly fixed in step 29 (the place line uses the town's name of the year); card descriptions still use today's names: step 30b (languages) |
| 43 | Step 27: Wikidata's own mistakes stay in the groups: a few impossible founding years (a tile company "founded" in 1600 in Delhi, the Egyptian Army "in 3400 BC"), orders dissolved without an end year (the Humiliati in 1610); temples, mosques, libraries and hotels count as groups when Wikidata files them under a business | a fact check of the cards (step 28's audit), then fixes like step 25 |
| 44 | Step 27: some rulers have no card or another name (Cosimo II in Florence 1610, Emperor Go-Yōzei), so "Who rules here?" names them without a link; the year pages' famous line ("People here talk about Musa I of Mali") has no link where the cards have nobody alive | step 38 (who people are; step 29 named town and province heads, not the rulers' cards) |
| 45 | Step 27: the first talk in a new busy area takes up to about 0.1 s while its tiles open (later talks there take under a millisecond) | step 34 (tiles opened ahead as the player moves) |
| 46 | Step 27: the card pool is 148,510 of 1,959,134 people with a mapped birthplace (the cap of 300 per box and century keeps the data at 8.5 MB); in busy lands the less famous are left out | region packs if the 64 MB budget is outgrown (decision 5) |
| 47 | Step 28: the cause-and-effect graph is thin: Wikidata has causes for 2,284 events and effects for 1,534; most battles only say which war they belong to | step 49 (rules where the data is silent) |
| 48 | Step 28: an event's sides are Wikidata's participants, best known first: the Second World War names the United States, Mexico, Australia, the United Kingdom and Egypt (Germany and Japan come under "Axis powers") | step 40 (armies in action: the sides of a war) |
| 49 | Step 28: 765 natural events placed only by their country sit at the country's middle point (a flood "in the United States" is told around Kansas) | step 35 (water and climate by era) |
| 50 | Step 28: storms before about 1940 often have no winds in IBTrACS and are left out; a storm's winds are those at landfall | step 35 |
| 51 | Step 28: occupations cover only the Second World War; other occupied land (Iraq 2003, the Baltic states 1940) says nothing yet; the outlines of disputed land are rough | step 40 (armies in action: who holds land in a war; step 29 did divisions by era, not occupations) |
| 52 | Step 28: the event cards' "point in time" and start years come from Wikidata, checked against the history data only for its own events (133 years taken from it); linked events (wars, treaties) are not cross-checked with Wikipedia yet | a fact check of the cards (with problem 43) |
| 53 | Step 29: town heads are thin: 1,578 of 30,151 towns have a head with dated holders, and many lists have gaps (Mumbai's mayors: two); zamindars, and nawabs and rajas Wikidata does not tie to the town's province, are not named | step 38 (who people are) and region packs |
| 54 | Step 29: population figures are Wikidata's: some count the city, some the urban area (Hyderabad 9.2 million); many big towns have only recent counts (Paris from 1990, Tokyo from 2005) | step 30b (with the economy), or Wikipedia's census tables |
| 55 | Step 29: founding years are Wikidata's ("People say ..."); 307 refoundings were caught (older names or counts), others may remain | a fact check of the towns (like step 25) |
| 56 | Step 29: names by era cover 3,892 towns; Greek, Arabic, Chinese and Japanese names are not spelled in Latin letters (Edo comes from the hand table); spellings (Peking, Canton) are not changed; villages under 20,000 people have no names by era | step 30b (languages: spelling by era) |
| 57 | Step 29: provinces come by town, not as areas between towns; a district's province is today's; some names are bare ("Seine" for the Seine department) | step 34 (the places and the border map in tiles, with areas) |
| 58 | Step 29: ties between states are few: 385 Cliopatria relation rows (mostly before 1600) and 16 military alliances; tribute and trade partners not yet; a short alliance without membership years takes its own years (Greece among the Allies from 1914) | step 30b (trade partners) and step 40 (wars' sides) |
| 59 | Step 29: the old treaty simulation (`DiplomaticTreatyEngine`, `FactionRelationshipSystem`) is still not reviewed; recorded ties do not feed it yet | step 49 (cause and effect, the "what if" engine, rulers decide) |
| 60 | Step 29: town heads' titles are Wikidata's office names, some in lower case ("the mayor of Paris"), some long | a wording pass with the talk (step 38) |
| 61 | Step 30a: only 11% of the technology atlas's country years are recorded (3,499 from Wikipedia, 226 from CHAT); the rest are estimates from the nearest land, so small or remote lands can get a technology too early (electric light in Botswana in the 1880s, television in Lithuania in 1939) or late | more records by hand (each step that uses a technology adds its own), region packs |
| 62 | Step 30a: inside a country a technology spreads by distance and era speed only: lands that held it back (printing in Mughal India before 1800) are not modelled; rivers are not on the country grid (steamboats on the Nile, the Mississippi and the Yangtze do not count) | step 34 (waterways of the past) |
| 63 | Step 30a: "how common" comes from CHAT for 10 household things (national figures to 2000-2008, then a curve) and from a curve for the rest; the gap between cities and villages is a fixed rule | step 30b (economy: income by place and era) |
| 64 | Step 30a: not replaced yet: the old technology engine (7 technologies per civilization, with no place), the world-wide medicine steps, Terra++'s own "no railways before 1825" rule (the mod's place-aware rule is ready, Terra++ does not call it) | step 31 (Terra++ by year), step 42 (health), step 49 (the engine) |
| 65 | Step 30a: 130 technologies, not the planned 150; the old 7 are not mapped to the atlas; buildings, weapons, tools and recipes do not ask it yet | steps 33, 40, 45, 46, 47 |
| 66 | Step 30a: the country grid is 0.1 degrees (about 11 km): a town within a few kilometres of a border can get its neighbour's country | a finer grid if needed (step 57) |
| 67 | Step 30b: reading before a land's first figure is a rule (back from the first figure, a third every 50 years after printing; a fixed share before) and the gap between men and women a formula | more figures by hand (step 38: who people are) |
| 68 | Step 30b: one system of measures per land and era (the seer of Bengal was not Bombay's); the metric year is estimated for 164 small or colonial lands; prices are not shown in these units yet | step 44 (goods and prices) |
| 69 | Step 30b: wealth is national (65 lands take their region's figures); the gap between rich and poor inside a land, prices, wages, taxes and banks are not here yet | step 44 |
| 70 | Step 30b: holy places are Wikidata's famous ones (5+ articles); a village temple is not on the list; 7,000 without a founding year are named only from 1900 | region packs; step 33 (old towns) |
| 71 | Step 30b: feast days by the calendar only for the Christian and Islamic feasts (the tabular Islamic calendar can be a day or two off); Diwali, Holi, the lunar new year and Passover are named but not dated | step 37 (local calendars) |
| 72 | Step 30b: a place's faiths come from its state's record; an empire's shares count the whole empire (London 1900 lists Muslims, from the British Empire's figures) | a fact check of the faith data |
| 73 | Step 31: Cahokia 1100 and Greenland's Norse farms 1000 show nothing at all — the region population floor is 1500 and 1800, after the year they are tested for | the floors, or better, the mod's population gate (A12) |
| 74 | Step 31: Greenland falls between two region boxes (lon −50…−25) and gets the 1800 global fallback, while Nuuk at lon −51.7 gets 1500; Hawaii gets 1800 because the Oceania box stops at the equator | same; the boxes need to cover the world without holes |
| 75 | Step 31: Fiji and New Zealand get 1700 though settled c. 1000 BC and c. 1350; the Aleutians get Siberia's 1600, an accident of a box crossing the dateline | same |
| 76 | Step 31: only 0.9% of mapped OSM structures carry an explicit start_date (181 of 19,272 at all 31 test places); the rest fall to the region floor, so today's map is drawn in antiquity — Ur 2500 BC 156 of 156 shown, Cusco 1500 all 850, Lagos 1960 all 1,087 dated to -2000, Rome AD 100 367 features with a median date of 321, Pataliputra 300 BC 98 modern roads | steps 32–33 build the past; A12 gates today's map |
| 77 | Step 31: with dated anchors present the gravity model pulls everything toward them — right when the anchors are old (Angkor 1150: median 1145, five years out), wrong when they are modern (Athens 430 BC: 1,440 ways → 6 shown, median 1136; Baghdad 900: median 2017; Timbuktu 1350: median 2016; Sydney 1850: 1,478 ways → 4 shown, median 2021, including 2 railways before Australia's first) | steps 32–33 |
| 78 | Step 31: `OsmDateInferencer.inferStartYear()` is dead code — never called anywhere in the codebase; only `inferFromBuildingSubtype()` is used, from `StructureDateEstimator.adjustBySubtype()`. `HistoricalStructureManager` implements the same chain independently | delete it, or wire it up (a Terra++ patch, decision 2) |
| 79 | Step 31: an explicit `start_date` is used as-is and skips both the population and the technology floor (1 structure at Mohenjo-daro is dated before its region's floor) | clamp explicit dates too |
| 80 | Step 32: 20,965 of the 23,534 famous buildings have no end year in Wikidata, and the register reads "we do not know when it ended" as "it has not ended" — so 89% of them stand forever. Only 2,569 have a real end year and 555 more are flagged as ruins without a date | an end date from somewhere else: the gazetteer's site spans, the town register (step 29), the event pack (step 28); until then B19 is right where it has data and silent where it does not |
| 81 | Step 32: three of the 31 test places still answer nothing — Greenland's Norse farms 1000 (no gazetteer site, nothing notable within 25 km of the Eastern Settlement), and the Amazon 1500 and the Sahara 1000 (correctly empty) | the three Norse sites are listed in `logs/step32_part2_notes.md` |
| 82 | Step 32: nothing in play calls the register yet — it loads, answers and is checked, but no placement or player-facing system asks it. The Terra++ patch that would make it matter is written down, not applied (decision 2) | step 33, and the listed Terra++ patch |
| 83 | Step 32: some Wikidata end dates are inherited from elsewhere on the item rather than historical (the Palatine Hill "until 1453"), and 1,334 start dates come from the mod's gazetteer rather than from a record — all marked estimated | a fact check of the building dates; the same treatment step 12 gave the rulers |

## 9. The world-wide test set (turn 96)

No place or year comes first (turn 96). Every step is checked on:

- **The world sample:** 400 random land points in each of 7 years (2500 BC, 500 BC, AD 1, 1000, 1500, 1900, 2000), as
  in step 4's probe. The checks report how many answers are recorded, estimated or missing.
- **The named places**, on every continent and in every era:

| Era | Places and years |
|---|---|
| Before 1000 BC | Ur 2500 BC; Giza 2500 BC; Mohenjo-daro 2500 BC; Anyang 1200 BC |
| 1000 BC – AD 500 | Athens 430 BC; Pataliputra 300 BC; Rome AD 100; Teotihuacan AD 500 |
| 500 – 1500 | Chang'an 750; Baghdad 900; Greenland's Norse farms 1000; Cahokia 1100; Angkor 1150; Great Zimbabwe 1300; Timbuktu 1350 |
| 1500 – 1800 | Tenochtitlan 1500; Cusco 1500; the Amazon 1500; Vijayanagara 1520; Delhi 1650; Edo 1700; London 1700; Paris 1789 |
| 1800 – now | Sydney 1850; New York 1920; Hyderabad 1948; Lagos 1960; Moscow 1980; São Paulo 2020; Siberia 1900; the Sahara 1000 |

- **Empty land counts too:** a desert, an ice sheet or a forest with nobody must answer "nobody lives here" correctly.

## Changes to this file

- Turn 92 (2026-10-14): written from the research and the 7 requirements.
- Turn 94 (2026-10-14): C16 became the technology atlas (`TECHNOLOGY_PLAN.md`); step 30 split into 30a and 30b.
- Turn 95 (2026-10-14): 29 systems that had been left out were added (marked "Turn 95"), and part 8, the known problems list.
- Turn 96 (2026-10-14): part 6 now holds my defaults (the user only says "next" from now on); part 9, the world-wide test set; "India first" became "every region at once".
- Turn 97 (2026-10-14): step 21 done: A12, C16, D15 and D19 updated; known problems 1, 2, 3, 6, 9 fixed, 5 looked into, 12–14 new; the counts in part 7.
- Turn 98 (2026-10-14): step 22 done: E13 updated (still partly: letters, inscriptions and signs come in step 43); known problems 15–19 new. The counts in part 7 are unchanged.
- Turn 99 (2026-10-14): step 23 split into 23a (real money everywhere, E2) and 23b (money as items, E1); step 23a done: E2 done, E1 updated; known problems 20–24 new; the counts in part 7 (8 done, 59 not started).
- Turn 100 (2026-10-14): step 23b done: E1 done; known problem 23 updated, 25–29 new; the counts in part 7 (9 done, 75 partly done). Next: step 24, Minecraft's trade screen (E3).
- Turn 101 (2026-10-14): step 24 done: E3 done, J1 updated (still partly); known problems 18, 27 and 28 fixed, 23 fixed for manillas, 24 partly; 30–33 new; the counts in part 7 (10 done, 58 not started). Next: step 25, the history data fix (my default since turn 96).
- Turn 102 (2026-10-15): step 25 done: C1 and C25 done (the history data fix, `fix_history_data.py`, every change in `step25_changes.csv`, undone with `--undo`); known problems 4, 15 and 21 fixed; 34–36 new; part 6 decision 1 done; the counts in part 7 (11 done, nothing waiting). Next: step 26, foundations for big data.
- Turn 103 (2026-10-15): step 26 done: A1, A3, A5, A7 and K4 done, A4 and I6 partly (tiles for the famous people, memory measured and budgeted); C1 updated (S8: rebels and the Second World War's occupations; S9: border cities); known problem 20 fixed, 34 updated, 37–40 new; part 7: Seshat's licence made clear; the counts in part 7 (15 done, 72 partly, 57 not started). Next: step 27, the card pipeline.
- Turn 105 (2026-10-15): step 27 done: C10 and C12 done, C22 partly (people and groups for every place; events in step 28), A4 updated (the cards are tiles); known problems 39 and 40 moved to step 28 (they are events, not cards), 41–46 new; the counts in part 7 (17 done, 71 partly, 56 not started). Next: step 28, events, natural events, cause and effect.
- Turn 106 (2026-10-15): step 28 done: C8, C9 and C21 done, C22 updated (event cards, the place's past); known problems 39 and 40 fixed, 37 moved to step 34, 47–52 new; the counts in part 7 (20 done, 70 partly, 16 old, 55 not started). Next: step 29, local rulers, divisions, place names, towns' lives, population.
- Turn 107 (2026-10-15): step 29 done: C4 done, C3 and C28 partly (were not started and old code), C2, C5 and C6 updated (the town list: names by era, people by year, founding, provinces, heads; ties between states); known problem 42 partly fixed, 41 and 44 moved to step 38, 51 to step 40, 53–60 new; the counts in part 7 (21 done, 71 partly, 15 old, 54 not started). Next: step 30a, the technology atlas.
- Turn 108 (2026-10-15): step 30a done: C16 partly (was old code: the technology atlas, the country grid, the new talk question, vehicles by place); known problems 61-66 new; the counts in part 7 (21 done, 72 partly, 14 old, 54 not started). Next: step 30b, economy, faiths and languages.
- Turn 109 (2026-10-15): step 30b done: C26 done, C27 partly (were not started), C13, C14 and C17 updated (reading and scripts, measures, wealth and hard times, holy places, festivals, pilgrimages, feast days); known problems 67-72 new; the counts in part 7 (22 done, 73 partly, 14 old, 52 not started). Next: step 31, Terra++'s buildings and roads by year.
- Turn 110 (2026-10-15): step 31 done: B7 checked, not changed (it is a check). Terra++'s own dating
  code was compiled out of `terra3/` and run outside Minecraft on today's OSM at 21 of the 31 test
  places (`terra_check.py`, `probes/terra/TerraDatingProbe.java`, `probe_terra.sh`,
  `logs/step31_terra_report.txt`): 19,272 ways at all 31 places, 181 with an explicit start_date (0.9%); undated
  structures fall to the 14 region population floors, so today's map is drawn in antiquity, and
  Cahokia 1100 and Greenland 1000 show nothing; Angkor 1150 is right because its temples are dated.
  `OsmDateInferencer.inferStartYear()` found to be dead code. Known problems 73-79 new; the counts
  in part 7 (22 done, 74 partly, 14 old, 4 in Terra++, 52 not started). Next: step 32, famous
  buildings, walls and ruins by year (B8, B16, B19).
- Turn 117 (2026-10-16): step 33 done: what a town is made of, by place and year (`history/building_culture.json.gz`, 109 building cultures, 258 countries, 77 Wikipedia articles). B9, B11, B13, B20, B25, E14 and E16 done; the counts in part 7 (32 done, 70 partly, 46 not started). Next: step 34, roads and waterways of the past.
- Turn 215 (2026-10-21): step 61 done, and the plan’s steps 21-61 are complete. Part 8 is triaged in `testing/Findings.java` (all 83 rows, each in exactly one of ten buckets; the record was the earlier sessions per the user’s choice). Problem 60 fixed (`TownFacts.prettyTitle`); 82 verified stale; 78 verified Terra++’s tree. The remaining work is named in the register, and step 60’s real-game run is outstanding.
- Turn 189 (2026-10-19): step 45 done: E9 done, C19 done, A13 partly (the weapons half; the vehicles half is step 46). Known problems for the next step: the wiring half of part 6 (WarGearStacks, WeaponYearGate and the six edited call sites) is syntax-checked only and has never run; `tools/gradle_compile.sh` has still never run since step 41; ammunition obeys the year rules only for Musket Mod; nothing yet joins the armoury to step 40's Sides, Battles and Morale.
