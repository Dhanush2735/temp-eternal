# How much of the possible data does the project have?

## The whole picture after step 8 (2026-10-12): the gaps a player would notice

Step 8 repaired wrong state ids, filled ruler lists, gave colonies their home country's rulers,
added four trade routes and added famous people where a land had none (`worldfill/README.md`, step 8).
Measured with `worldfill/coverage_people.py` (output `worldfill/coverage_people.json`; the step-7
numbers are kept in `worldfill/coverage_people_before_step8.json`).

**Share of all the world's people whose ruler is named:**

| Year | 1500 BC | 500 BC | AD 1 | 500 | 1000 | 1300 | 1500 | 1700 | 1850 | 1900 | 1950 | 2000 | 2020 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| after step 7 | 3% | 14% | 24% | 37% | 53% | 55% | 59% | 78% | 64% | 81% | 82% | 93% | 94% |
| **after step 8** | **4.6%** | **18%** | **51%** | **59%** | **57%** | **62%** | **62%** | **81%** | **86%** | **95%** | **95%** | **95%** | **96%** |
| state known at all | 6.6% | 24% | 57% | 69% | 61% | 68% | 68% | 85% | 92% | 96% | 97% | 97% | 97% |

Where the state is known, its ruler is now named for 86–98% of people from AD 1 on.

**Share of all the world's people with a famous person of their land alive:**

| Year | 500 BC | AD 1 | 500 | 1000 | 1500 | 1700 | 1850 | 1900 | 2000 |
|---|---|---|---|---|---|---|---|---|---|
| after step 7 | 15% | 46% | 58% | 44% | 63% | 76% | 90% | 95% | 97% |
| **after step 8** | **17%** | **50%** | **58%** | **45%** | **63%** | **79%** | **92%** | **95%** | **97%** |

**Categories that changed:**

| Category | After step 7 | After step 8 |
|---|---|---|
| Rulers' names | 1,094 states, 15,324 reigns | **1,165 states, 17,700 reigns**; colonies name their home monarch or president; the Roman Republic names its consuls |
| State ids (behind rulers, languages, faiths, people) | 92 wrong (Han China had the Chauhan dynasty's id; the two Koreas shared one) | **repaired** |
| Languages | 71% of states | **73%** (1,048 of 1,434) |
| Religions | 65% of states | **67%** (960); measured shares now per country for 230 states |
| Trade routes | 10 routes, 364 towns | **14 routes, 411 towns** (4 with estimated years) |
| Famous people | 183,754 | **184,193** (+439 where a land had nobody) |

**All 17 categories, simple average:** about 75% of the free open data (was 70–75%).

**What is still missing, and why:**
- **Nobody to name:** the Indus Valley, the Greek city-states, Sumer, the Maya and the Etruscans were never
  one state with one ruler.
- **No dates in the sources:** the Kalabhras, the Sangam-era Cholas, Pandyas and Cheras, the Hyksos and
  Egypt's Third Dynasty have kings but no dated reigns in Wikipedia.
- **No famous people on record:** 3,582 of 4,152 land-and-period gaps have nobody in Wikidata with a
  birthplace either.
- **Hyderabad 1799–1946:** the border map puts the city under the British, so villagers name the British
  monarch rather than the Nizam.
- **Ancient times overall:** before 1000 BC, 92–96% of people live where no state is recorded at all.


## The whole picture after step 7 (2026-10-11)

"Possible data" means the free, open data that was found and counted for each category, the same
yardstick as the first measurement below. Measured with `worldfill/coverage_people.py` (people
weighted by the mod's HYDE grid; output in `worldfill/coverage_people.json`), the step-5 recount
(`worldfill/coverage_after.json`) and the step-6/7 build reports.

### One-number answer

| Compared with | Share |
|---|---:|
| Free, open history data: events (battles, wars, treaties, disasters, epidemics, year-page events) | **about 83%** (93,793 events vs ~19,650 known still missing). It was 26% at the first count. |
| …the same, counting UCDP's 385,918 modern conflict events (1989–2024) | **about 95%** (UCDP's events are now in, grouped into 28,639 spots). It was 7.5%. |
| All 17 categories below, simple average of each category's main share | **about 70–75%** (it depends on how you score population, which is all estimates, and ways of life) |
| Everything historians know (books, archives, non-English records) | still a few percent at most (a judgement, not measured) |
| Everything that actually happened | a tiny fraction; most of life was never written down |

### By category

| Category | In the mod | Share of the open data | Change since the first count |
|---|---:|---|---|
| Battles | 13,254 | **~95%** of the battles open data can place (date + place). About 70% of all 18,642 Wikidata battle items, many of which have no date or place. | was 94% / 63% |
| Sieges | 3,987 | **~98%** of placeable; over 90% of all 3,916 | was 98% / 91% |
| Wars | 2,960 | **89%** of the 3,294 wars on Wikipedia's lists | was 47% |
| Treaties | 2,554 | **~70%** (vs Wikidata's 3,611) | was ~25–50% |
| Epidemics and plague | 5,558 | **~80%**: 97.9% of plague outbreaks; Wikipedia epidemic lists; COVID-19 for 405 places | was ~2% |
| Disasters (quakes, tsunamis, eruptions, floods, famines) | 25,374 | **~95%** | was ~17% |
| Wikipedia year-page events | ~43,000 | **82%** of event lines, plus 1,763 from decade and century pages | was 42% |
| Modern conflicts 1989–2024 | 28,639 spots | **~99%** of UCDP events placed (98.7%); 92% of the deaths | was 0% |
| Borders (which state ruled) | 1,544 states | 100% of the best open map (Cliopatria). Share of people for whom the state is known: 2.7% (2500 BC), 23% (500 BC), 55% (AD 1), 68% (1500), 85% (1700), 98% (2000) | unchanged |
| Rulers' names | 15,324 reigns, 1,094 states | **Share of all people whose ruler is named:** 3% (1500 BC), 14% (500 BC), 24% (AD 1), 37% (500), 53% (1000), 59% (1500), 78% (1700), 64% (1850), 81% (1900), 93% (2000), 94% (2020) | was ~0% |
| Population | every land cell, every era | 100% of the map has an estimate (HYDE model). Real counts only for ~1,700 cities. | unchanged |
| Places where people lived | 46,864 | **~85%** of the open place lists (mostly the Roman world, China and Telangana) | unchanged |
| Languages | 997 states + 6,709 languages | 71% of states have their official languages. The people's own language comes from all of Glottolog's 6,709 living languages, from AD 1500 on. | was 0% |
| Religions | 911 states + shares | 65% of states have their faiths. Measured shares 1945–2010 for 219 states (Correlates of War data). | was 0% |
| Famous people | 183,754 | **8%** of the 2.29 million notable people in the open database. It includes everyone born before 1500 with a known birthplace, plus the most famous later people. A famous person of the land is alive for 46% of the world's people in AD 1, 63% in 1500, 76% in 1700 and 97% in 2000. | was 0% |
| Ways of life | 146 regions × 10 dates | 100% of ArchaeoGLOBE (8050 BC – AD 1850). After 1850 it is an estimate. HYDE's farmland and grazing maps are not used. | was 0% |
| Trade routes | 10 routes, 364 towns, 14,769 Roman road sections | 10 of 16 main route articles; all of Itiner-e's Roman roads. OWTRAD's Eurasia-wide network is not used. Roughly a third to a half of the routes known for pre-modern times (a judgement). | was 0% |

### Where the gaps are

- **Ancient times.** The open record itself is thin. The mod has 1,221 events for 3000–1001 BC and
  4,018 for 1000–1 BC, against 78,171 for 1800 to now. In 1500 BC the state is known for only 6.5%
  of people and the ruler's name for 3%: most people then lived outside any state that the open
  maps record.
- **Big states with no ruler's name.** The mod knows the state but not who ruled it that year. Shares
  are of all the world's people, checked with the same grid as `coverage_people.py`:

  | Year | State known, ruler not named | Biggest holes |
  |---|---:|---|
  | AD 1 | 31% | Han dynasty 21% (only 3 reigns recorded), Satavahana 5.6% (none covering AD 1) |
  | 500 | 32% | Gupta Empire 16.6% (none covering 500), White Huns 4.9%, Kalabhra 3.3% |
  | 1850 | ~20% | "British Colonial Empire" 19.2% (British India; should be Queen Victoria) |
  | 1900 | 15% | Kingdom of Great Britain 2.8%, Dutch East Indies 2.8%, British Africa 1.6%, French Indochina 1.5% |
  | 500 BC | 9% | Greek city-states 1.8%; the Chinese states Wu, Yue, Jin and Qi about 1% each |

  Filling these from Wikipedia's ruler lists, and giving colonies their home country's monarchs,
  would lift the named share to about 50% in AD 1, about 60% in 500, about 85% in 1850 and about
  93% in 1900. Before 1000 BC the real limit is the map: 92–96% of people live where no state is
  recorded.
- **Population** is a model everywhere except ~1,700 cities.
- **Famous people:** only the best-known 8% of everyone notable.
- **Trade routes:** only 10 big routes plus Roman roads.
- **Ways of life after 1850:** an estimate.
- **Everything from non-open or non-English sources** is not counted at all.


## Update after step 7 (2026-10-11): fetching the 0% categories from new sources

| Category | After step 6 (data on disk) | After step 7 (new sources fetched) | Source added |
|---|---|---|---|
| Kings and queens | 913 states, 4,824 reigns. Share of ruled land with a named ruler: 1300 15%, 1500 42%, 1700 70%, 1850 37%, 1950 24%, 2000 14% | **1,094 states, 15,324 reigns, 4,338 heads of government.** Share: 1500 BC 58%, 500 BC 79%, AD 1 61%, 500 67%, 1000 66%, 1300 80%, 1500 71%, 1700 83%, 1850 83%, 1900 70%, 1950 79%, 2000 97%, 2020 99% | Wikipedia "List of state leaders in …" (62 century and decade pages) |
| Ways of life | estimate only (population model) | **real data:** 146 regions × 10 dates, 8050 BC – AD 1850 (estimate only after 1850) | ArchaeoGLOBE (CC0) |
| Languages | 997 states (court/official) | + **the people's language** from AD 1500 (6,709 living languages, 137 major) | Glottolog 5.3 |
| Religions | 911 states (infobox list) | + **measured shares** every 5 years 1945–2010 for 219 states | Correlates of War World Religion Data |
| Famous people | 72,594 (country level) | **183,754**, of which 148,586 with their exact birthplace ("born near here") | Sciences Po notable-people database |
| Trade routes | 0 | **10 routes with 364 towns** (Silk Road, Maritime Silk Road, Incense route, Trans-Saharan, Grand Trunk Road, Royal Road, Hanseatic League, Via Maris, King's Highway, Tea Horse Road) + **14,769 Roman road sections** | Wikipedia route articles; Itiner-e |
| Modern conflicts | 28,639 local spots (UCDP) | unchanged | – |

Spot checks, all right:

| Place and year | Ruler |
|---|---|
| London 1616 | James VI and I |
| Kraków 1600 | Sigismund III Vasa |
| Beijing 1700 | Kangxi |
| Moscow 1800 | Paul I |
| Washington 1863 | Abraham Lincoln |
| Mexico 1865 | Maximilian I |
| Delhi 1600 | Akbar |
| Cairo 1300 | al-Nasir Muhammad |
| Babylon 600 BC | Nebuchadnezzar II |
| Persepolis 500 BC | Darius I |
| Thebes 1300 BC | Horemheb |
| Rome AD 100 | Trajan |

Still missing: trade routes outside these 10, for example the Amber Road, Uttarapatha and the
Indian Ocean routes. Their Wikipedia leads give no dates, and OWTRAD's licence is unclear. Ruler
names are still thin in a few places and times, such as Babylon in 1700 BC and Japan in the Warring
States period.


## Update after step 6 (2026-10-11): the 0% categories, from data already in the workspace

The user's plan: put the data already in the workspace into the mod, then delete the raw copies.
Builders and results: `worldfill/README.md` (step 6) and `history/README.md` (Part 10). What was
deleted, and where its content now lives: `worldfill/CLEANUP_STEP6.md`.

| Category | Before | After | From |
|---|---:|---:|---|
| Modern conflicts 1989–2024 | 0 local spots (278 wars as country-wide news) | **28,639 local spots**, holding 92% of UCDP's 3.96 million recorded deaths (events placed to a province or better: 98.7%) | UCDP GED 25.1 |
| Kings and queens | 0 (1,078 "X becomes king" news lines) | **913 states with named rulers** (4,824 reigns; 499 heads of government). Share of ruled land with a named ruler that year: 500 BC 69%, AD 1 20%, 500 45%, 1000 39%, 1300 15%, 1500 42%, 1700 70%, 1850 37%, 1900 53%, 1950 24%, 2000 14%, 2020 23% | state infoboxes; year-page accession and death lines |
| Languages | 0 | **997 of 1,403 states (71%)** | state infoboxes |
| Religions | 0 | **911 of 1,403 states (65%)** | state infoboxes |
| Famous people | 0 (28 birth lines) | **72,594 people** in 849 states (88% of the 82,649 people on the year pages); 52,244 with both birth and death year | year pages, Births and Deaths |
| Ways of life | 0 | an **estimate** wherever the population model has people, always labelled "not a record" | HYDE density, place rank, era |
| Trade routes | 0 | 0: no trade-route data was on disk | (needs a download) |
| Decade and century pages | not read | **+1,763 events** (839 more were already in the mod) | wiki_test snapshot |

Notes:
- "Share of ruled land" counts the 0.5-degree cells of the Cliopatria register that some state rules
  that year (every 7th cell), and asks whether that state has a named ruler covering the year.
  A reign is never guessed: between known reigns the answer is "no name".
- Some names are wrong where the year pages themselves are loose (a prince described as "Mughal
  emperor"). Lines naming a relation ("son of …") are dropped. The spot checks (Paris 1650 Louis XIV,
  Constantinople 1000 Basil II, Istanbul 1700 Mustafa II, Beijing 1700 Kangxi, Agra 1650 Shah Jahan,
  Rome 1500 Alexander VI, Isfahan 1600 Abbas I, Cuzco 1520 Huayna Capac) all came out right.
- Events now total 122,432. Searches use a per-year index: the same answers on 10,062 test queries,
  about 240 times faster.


## Update after step 5 (2026-10-11): the categories under 50%, Wikipedia first

Measured again after installing `events_wikipedia_regional.json.gz`,
`events_hazards.json.gz` and `events_wars.json.gz` (see `worldfill/README.md`, step 5).
Open-source coverage is now counted record by record: a record counts as covered when an
installed event of the same kind is within 150 km and one year (30 km for plague). The
script is `worldfill/coverage_recount.py` and the result is in `worldfill/coverage_after.json`.

| Category | Before | After | How |
|---|---:|---:|---|
| Wikipedia year-page events | 42% | **82%** | 47,243 of 57,338 event lines (see the correction below). 7,296 lines still name no place the method can find |
| Epidemics and plague | ~2% | **~80%** | 97.9% of the 7,711 plague outbreaks; Wikipedia epidemic list; COVID-19 for 405 places. Wikidata's ~1,900 outbreak items were not checkable (WDQS outage) and are counted as missing |
| Disasters | ~17% | **~95%** | Earthquakes 99.6% of NOAA's; tsunamis 89.4%; eruptions 99.6% of NOAA's and 99.9% of the Smithsonian's |
| Wars | 47% (of Wikidata's 1,130) | **89%** (of the 3,294 wars on Wikipedia's lists) | 2,397 new wars plus 547 already in the mod; 350 rows have no place |
| Treaties | ~25–50% | **~70%** | 2,486 treaties vs Wikidata's 3,611 items (a count, not a match) |
| Battles, sieges, borders, population, places | unchanged | unchanged | see below |
| Famous people, king/queen names, ways of life, trade routes, languages, religions | 0% | 0% | next step |
| Modern conflict events 1989–2024 (UCDP) | 0% | 0% | not attempted |
| **All events measured** | 26% | **~83%** | 92,030 events vs ~18,000 known still missing. Counting UCDP's 385,918 modern events: 7.5% → ~19% |

**Correction to the earlier "22%".** The earlier 100,970 "event lines" counted every bullet
outside Births and Deaths, including people lists, references and leader lists that are not
events. With the harvest's own section rules, there are 57,338 event lines (60,883 bullets,
minus 1,073 birth/death lines and 2,472 too short). So the honest before figure was 42%, not 22%.

**In the game (through the mod's own HistoryGazetteer, `worldfill/probe_events.sh`):**
- Local pins still win everywhere they exist: 0 rule violations at 11 test spots.
- Land points with some event or news in a given year rose to 5% (1500), 10% (1850), 13% (1900)
  and 26% (1944). Before, local pins alone gave 0–1%.
- A query takes 2.3 ms (92,030 events).

---

## Before step 5 (first measurement, 2026-10-11)

**"Share"** means: what the mod has, divided by what exists in the free, open data that was
found and counted. Sources:
- `OTHER_SOURCES_CENSUS.md` and `WIKIPEDIA_CENSUS.md`;
- the build reports in `worldfill/`;
- Wikidata totals queried today;
- a new border check that uses the mod's own lookup rule.

## One-number answer

| Compared with | Share |
|---|---:|
| Free, open history data (events) | **about 26%** (40,725 of ~157,000) |
| …the same, counting UCDP's 385,918 modern conflict events (1989–2024) | **about 7.5%** |
| Everything historians know (books, archives, non-English records) | a few percent at most (a judgement, not measured) |
| Everything that actually happened | a tiny fraction; most of life was never written down |

## By category

| Category | In the mod | What exists (open) | Share |
|---|---:|---|---|
| Battles | 12,599 | Wikidata: 18,642 battle items, 12,419 with date + place (+ ~900 Wikipedia-only) | **94%** of placeable; 63% of all Wikidata battles |
| Sieges | 3,703 | Wikidata: 3,916 items, 3,634 with date + place | **98%** of placeable; 91% of all |
| Borders (who ruled) | 1,544 states | Cliopatria (all of it); Wikidata lists 3,868 "historical country" items | 100% of the best open map; ~40% by name |
| Population | every land cell, every era | HYDE 3.2.1 model | 100% coverage, but **estimates**. Uses 1 of 17 HYDE layers and 28 of its 68 dates in range. Real city figures: all ~1,700 cities of Reba et al. |
| Places where people lived | 46,864 (31,100 world + 15,700 Telangana) | Pleiades dwelling places 21,352; CHGIS counties 10,522; CHGIS prefectures 5,226 (EULA); Reba cities | **~85%** of the open lists. Pleiades non-dwelling sites (21,141 temples, forts, mines…) are not used. The lists cover mostly the Roman world and China. |
| Treaties | 1,775 | Wikidata: 3,611 items, 1,186 with date + place | **76%** of placeable; ~25–50% of all |
| Wars (as war zones) | 533 | Wikidata ~1,130 dated; Correlates of War 652 (no places) | **~47%** |
| Wikipedia year-page events (English) | ~22,000 | 100,970 event lines (+16,455 on decade/century pages); ~24,000 with an exact place | **~95%** of the exact-place ones; **~22%** of all event lines. About 74,000 lines name only a country, or no place at all. |
| Disasters (quakes, tsunamis, volcanoes, floods, famines) | 3,340 | + NOAA 4,723 quakes / 2,032 tsunamis, Smithsonian 9,731 eruptions, Wikidata 425 | **~17%** |
| Epidemics and plague | ~200 (keyword count) | Plague outbreaks 7,711 (1339–1900); Wikidata outbreaks 1,901 (mostly COVID by region) + 70 | **~2%** |
| Modern conflict events, 1989–2024 | 0 | UCDP GED 385,918 | 0% |
| Famous people | 0 | 2.29 million (cross-verified notable people database, CC BY-SA) | 0% |
| Kings and queens by name | ~325 coronation/accession lines | Wikidata reigns (count blocked by today's WDQS outage) | ~0% |
| Ways of life, farmland, trade routes, languages, religions, buildings | 0 | ArchaeoGLOBE, HYDE land use, ORBIS, Glottolog… | 0% |

## Borders: for what share of people does the mod know the ruler?

This uses the mod's rule: the nearest register place within 60 km
(`RulerRegister.MAX_KM`). People are weighted by HYDE, using its land areas.

| Year | 2500 BC | 1500 BC | 500 BC | AD 1 | 500 | 1000 | 1300 | 1500 | 1700 | 1850 | 1900 | 2000 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| People | 2.7% | 6.5% | 22.7% | 55.3% | 69.5% | 60.8% | 67.9% | 68.1% | 85.4% | 93.5% | 97.8% | 98.4% |
| Land | 0.2% | 1.1% | 6.2% | 14.1% | 17.7% | 22.2% | 30.9% | 32.5% | 45.3% | 62.3% | 89.7% | 99.3% |

The early numbers are low partly because most people then really lived outside any state, and
partly because Cliopatria leaves out small kingdoms and chiefdoms. World population from the same
grid: 232 M in AD 1, 503 M in 1500 and 6,111 M in 2000, matching HYDE.

## How the 26% was counted

Records that exist but are not in the mod:
- 78,978 Wikipedia event lines;
- 6,929 battles, 337 sieges, 597 wars and 2,704 treaties (Wikidata);
- 16,911 disasters;
- 9,682 outbreaks.

That is 116,138 records, against the mod's 40,725 → 26.0%. Adding UCDP gives 7.5%.

## Caveats

- **Overlaps:** some unplaced Wikipedia lines describe the same battles or treaties that are
  already in the mod through Wikidata. The true share may be nearer 30%.
- **Wikidata totals:** they count direct `P31` only, not subclasses (for example, naval battles
  filed under a subclass), so the real totals are somewhat higher.
- **Ancient eras:** the open record itself is thin. English Wikipedia year pages hold only 822
  lines for 3000–1001 BC, and the mod has 296 events there.
- **Not included in the 26%:** famous people and the other 0% categories; counting them would
  swamp the number.
