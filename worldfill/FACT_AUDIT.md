# Fact check of the mod's history data (step 12, 2026-10-12)

## After step 30b (turn 109, 2026-10-15): reading, measures, wealth, holy places

Step 30b added `history/culture.json.gz` (literacy from Our World in Data, wealth from the Maddison Project, metric
years from Wikipedia, and the hand tables of `culture_table.py`: measures, scripts, faiths, hard times) and
`history/holy_places.json.gz` (19,828 places of worship from Wikidata). Checked: India's literacy against the census
figures (6.2% in 1901), Britain's against Buringh and van Zanden; the metric years against Wikipedia's table (France 1795,
India 1956, Japan 1924); the holy places' kinds (a "cathedral library" or "structure of worship" says nothing rather
than that), their faiths (from Wikidata or their kind), and their years (63 famous ones dated by hand from their
articles; 938 with neither a faith nor a year left out, mostly ruins); the feast days by the calendar (Christmas,
Easter, Eid al-Fitr 2024 on 10 April). The findings below (1,329) are unchanged. What stays unchecked: known problems
67-72 of `SYSTEMS_PLAN.md` (reading before the figures is a rule; one system of measures per land; faith shares of
empires).

## After step 30a (turn 108, 2026-10-15): the technology atlas

Step 30a added `history/technology_atlas.json.gz` (130 technologies; 3,499 country years written by hand from
Wikipedia's articles in `technology_table.py`, 226 from CHAT, 26,155 estimated and marked "E") and
`history/countries.grid.gz` (Natural Earth). Checked: the five places of `TECHNOLOGY_PLAN.md`; that no technology is
anywhere before its first year, and nothing from the Old World is in the Americas before contact or in Australia before
1788 (`--check`, part 19 of `/ee check all`, `probe_technology.sh` with 500 land points in 13 years); records that come
before what they need are counted in `logs/step30a_technology_report.json` (13: early electric trams with their own
power stations, tall buildings recorded before lifts were estimated there, the steel of Kaman-Kalehöyük before the
Iron Age) and kept, as records; an estimate of what such a record needs is pulled back to the record's year. The findings below (1,329) are unchanged. What stays unchecked: the estimates themselves (known problem 61).

## After step 29 (turn 107, 2026-10-15): towns through time and the ties between states

Step 29 added `history/towns.json.gz` (30,151 towns from Wikidata, Wikipedia's list of city name changes and a hand
table written from the towns' Wikipedia articles) and `history/state_relations.json.gz` (538 ties from Cliopatria and
Wikidata's military alliances). Checked: every hand-table town's Wikidata number against its English name (the first
guesses for Kanpur, Vadodara, Mysore, Kisangani, Lubumbashi, Bujumbura, Samara, Tver and Almaty were wrong and were
replaced by the numbers of their articles); Wikipedia's list of city name changes is coarse (it leaves out spelling
changes such as Christiania to Kristiania), so it fills only the years Wikidata leaves open, and the towns' own articles
win over both (turn 12); founding years that come after a town's older names or counts (307, e.g.
Istanbul 1453, Tokyo 1868) are left out, Hyderabad's is Wikipedia's 1591, Mumbai's 1507 is left out; offices named by
three or more places (15 general ones such as "mayor") are left out; alliance memberships without years are left out
unless the alliance lasted 15 years or less. `probe_towns.sh` checks 42 renamed places, every town's counts and a sweep
of 400 towns in 13 years. The findings below (1,329) are unchanged. What stays unchecked: known problems 53-60 of
`SYSTEMS_PLAN.md` (thin head lists, city or urban-area counts, remaining refoundings, short alliances' years).

## After step 28 (turn 106, 2026-10-15): the event cards and natural events

Step 28 added the event cards (`cards/events.tiles`, 32,542 events from Wikidata) and two event files for the history
data (`events_storms.json.gz`, 5,884 storm landfalls from NOAA's IBTrACS; `events_nature.json.gz`, 1,844 floods,
wildfires and other natural events from Wikidata). Checked: the history data's own events against their cards (the
history data's years kept where Wikidata differs by more than a year: 133 events); a war's "point in time" is not taken
as its start (it is often the last year: World War I, 1918); natural events already in `events_hazards.json.gz` (the
same kind, a year apart, within 300 km) left out (178). `probe_eventcards.sh` words 2,503 sampled event cards in five
years each (11,202 wordings) and finds no later year, no unknown link and no source name. The findings below (1,329)
are unchanged: the new files are new, not changes of the old ones. What stays unchecked is known problem 52 of
`SYSTEMS_PLAN.md` (the linked events' years against Wikipedia).

## After step 27 (turn 105, 2026-10-15): the knowledge cards

Step 27 added a new data file, `cards/cards.tiles` (148,510 people and 26,855 groups from Wikidata). It was checked
against the famous people master (the Wikipedia year pages): 65,416 people are in both with the same name and one year
the same; where the other year differs, the Wikipedia year is used (1,560 birth years and 464 death years differed by
more than a year; the rest agree or differ by one year). Left out: 26 impossible lives (dead before birth or older than 120), 31 remains and mummies, 1,865 people and
602 groups with no English name, 3,210 "companies" that are towns. Every card is worded for its date and checked by
`probe_cards.sh` (7,444 cards of the world sample in 11 years: no later year, no unknown link, no source name). The
findings of the history data below are unchanged (1,329): the cards are a new file, not a change of the old ones. Known
mistakes that stay in the cards are known problem 43 of `SYSTEMS_PLAN.md`.

## After step 26 (turn 103, 2026-10-15)

Step 26 marked the 213 guessed end years as estimates in the data (A5; the check no longer counts a marked estimate as
a finding), fixed rebel- and occupier-held land (S8: Syria, Afghanistan, the Second World War) and gave 89 border cities
their own country (S9). The same check: **1,329 findings** (wrong 44, likely wrong 199, odd 242, missing 844). The
share of people who hear a wrong line is unchanged (the check has no rule for occupations or border cities, which is
why they were found by hand); a state is named for 98.4% of the world's people in 2020 (was 98.3%).

## After step 25 (turn 102, 2026-10-15): the fix

Step 25 fixed the problems below in groups (`fix_history_data.py`; every change in `step25_changes.csv`, all of them
undone with `python3 fix_history_data.py --undo`; see `README.md`, step 25). The same check, run again:

| | Step 12 | After step 25 |
|---|---:|---:|
| Findings | 4,005 | 1,549 |
| Wrong (sure) | 1,543 | 44 |
| Likely wrong | 333 | 207 |
| Odd | 1,253 | 455 |
| Missing | 876 | 843 |

| Share of the world's people who hear a wrong ruler, language or faith line | 1300 | 1500 | 1700 | 1800 | 1850 | 1900 | 1950 | 2000 | 2020 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Step 12 | 1.6% | 0.9% | 1.8% | 5.3% | 12.1% | 17.6% | 7.1% | 2.7% | 2.5% |
| After step 25 | 0.2% | 0.7% | 1.5% | 0.5% | 0.2% | 0.03% | 0.1% | 0.01% | 0.04% |

"People here talk about X" names someone born more than 1,000 km away in 1–5% of the picks (was 17–44%).

What is left: mostly names the check cannot confirm, because it compares a corrected period name with the old state's
dates (the Restored Toungoo Kingdom after 1599, the post-Angkor Kingdom of Cambodia, "Tibet"); 821 runs of years with no
ruler named, mostly before 1800; 213 guessed end years; 83 news lines placed at sea. The check itself learned two things
in step 25: the faith of the year (England is Anglican from 1534), and that a Council of State's chairman (Liberia
1994–1996) or a junta's president (Peru) is a head of state, not a prime minister. The rest of this page is the step-12
report as it was.

**Nothing in the mod was changed.** The check only reads the data and writes a list of problems.

## The short answer

- The check went through everything the mod uses: 22,288 rulers and heads of government, the border
  map's 1,543 state names, 122,432 events, 184,193 famous people, 46,864 places, 14 trade routes, the
  languages and faiths of 1,313 states, and the small foundation files.
- It found **4,005 problems**:
  - **1,543 wrong** (sure);
  - **333 likely wrong** (strong sign; worth a look);
  - **1,253 odd** (broken text, guesses, things that sound wrong);
  - **876 missing** (gaps, for example years with no ruler named).
- Almost all of them come from a **few repeated patterns** with one cause each. They can be fixed in
  groups, not one by one.
- **How many players would hear a wrong line** about who rules them, or about their language or faith:
  - before 1700: under 2% of the world's people;
  - 1850–1900: 12–18% (mostly two mistakes: Russia and Britain, below);
  - 1950: 7%;
  - 2000 and 2020: under 3%.
- **Places and trade routes:** no problems found.

## How the check works

Every rule is a test a fact can fail. Some examples:

- a reign that goes on after the ruler died;
- a "republic" ruled by a king;
- a faith listed before it was founded;
- a news line whose own words name another year.

**Wikidata as an outside witness.** Wikidata was asked through the QLever service (CC0) for three things:

- the birth and death years for 17,197 ruler names and spellings;
- the years of 1,544 states that carry the border map's names;
- the jobs of 15,823 matched people.

**False alarms.** People who share a name with someone else (another "Charles VII") are left out, so a
namesake does not cause a false alarm. Each rule was tried, then corrected until its samples were right.
The rules marked "likely" are right roughly half the time or better. The rules marked "wrong" were right
in every sample I read.

"Seen in game" means a player can actually hear it. A ruler counts only in the years their state is on
the map and they are the one the game names; a language only if it is one of the two the game says.

**Files:**

- `fact_audit.py`: the check. Run it again after fixes; it takes about 1 minute.
- `fact_audit_wd.py`: the Wikidata look-ups.
- `fact_audit_findings.csv.xz`: all 4,005 problems, with the area, the rule, how sure, whether it is seen
  in game, the item and the details.
- `fact_audit_summary.json`: the counts, the examples, and the people-weighted numbers.
- `fact_audit_wikidata.json.gz`: the Wikidata answers, saved so the check runs offline.

## What players would hear

Share of the world's people (HYDE population map) whose villagers say at least one wrong line. Only the
ruler line and the language-and-faith line are counted here, not news or famous people.

| Year | Any wrong line | Wrong ruler line | Wrong language or faith line |
|---|---:|---:|---:|
| 1000 BC | 0% | 0% | 0% |
| 500 BC | 0.9% | 0.9% | 0% |
| AD 1 | 0.2% | 0.04% | 0.2% |
| 1000 | 0.3% | 0.2% | 0.1% |
| 1300 | 1.6% | 1.2% | 0.4% |
| 1500 | 0.9% | 0.8% | 0.1% |
| 1700 | 1.8% | 1.8% | 0% |
| 1800 | 5.3% | 5.3% | 0% |
| 1850 | 12.1% | 12.1% | 0.03% |
| 1900 | 17.6% | 17.5% | 0.1% |
| 1950 | 7.1% | 5.1% | 2.0% |
| 2000 | 2.7% | 1.3% | 1.4% |
| 2020 | 2.5% | 1.3% | 1.1% |

The wrong lines that reach the most people:

1. "Russian Empire, ruled by Ivan Durnovo (Chairman of the committee of ministers)". In most years
   from 1810 to 1917, Russia names its prime minister instead of the Tsar.
2. "French Consulate, ruled by English claimants to the throne of France".
3. "Islamic Republic of Pakistan, ruled by George VI" (1947–1955).
4. "Kingdom of Great Britain" for the United Kingdom, every year from 1801 to today.
5. "French Second Republic, ruled by Orléanist claimants to the throne of France".
6. "French Third Republic, ruled by Pierre Waldeck-Rousseau (President of the Council of ministers)".
   From 1870 to 1940, France mostly names its prime minister instead of its president.
7. "Austria-Hungary, ruled by Ernest von Koerber (Ministers-President)".
8. "The government uses Korean and Korean Sign" (South Korea).
9. "Qi, ruled by Sun Tzu (Ruler of Qi)". Sun Tzu was a general and writer, not a ruler.

## The problems, by area

### 1. Rulers

1. **Heads of government named as the ruler: 154 rows, all heard in game.**
   - **Cause:** some ruler lists mix kings and presidents with prime ministers. The game names whoever
     took office last, so the prime minister hides the head of state.
   - **Where:** French Third Republic 47, Monaco 30, Russian Empire 22, Portugal 15, Hungary 11, Peru 6,
     USSR 5 (for example Kosygin and Ryzhkov), Serbia, Vietnam, Liberia, Lebanon.
   - **Fix:** move those rows to the head-of-government list.
2. **Claimants named as the ruler: 14 rows, 8 heard.** These are French rows such as "English claimants
   to the throne of France" and "Orléanist claimants…". **Fix:** delete them.
3. **A state, a title or a group named as the ruler: 30 rows.** Examples:
   - "Bahmani Sultanate, ruled by Shah (Sultan)": the name was lost, 7 rows;
   - "Republic of Vietnam (ruler)";
   - "Kingdom of Hungary" as ruler of Bohemia, 1526–1867;
   - "Phanariote rule";
   - "Civil War period".
4. **Wrong years.**
   - Impossible lengths, 3 rows: Otto V of Bavaria 1347–1949, Habbus al-Muzaffar AD 20–1038, Niskala
     Wastu Kancana 104 years.
   - **Reign goes on after the ruler died, 33 rows.** For example, Ladislaus the Posthumous until 1490
     (he died in 1457); de Gaulle as prime minister until 1983; Josiah Gumede of Zimbabwe Rhodesia until
     2004; Michael VII Doukas until 1124.
   - A BC year written as AD: Tan'gun "AD 2333".
   - **Guessed end years, 224 rows (107 heard).** When the source gave no end year, the builder
     (`build_polity_facts.py`) put "start + 25 years".
5. **Not a ruler at all.** Qi's list includes Sun Tzu and Xun Kuang (found automatically). Reading that
   list by hand also turns up Guan Zhong (a chancellor), Yin Wen and Sun Bin (a philosopher and a
   strategist).
6. **Missing rulers: 849 gaps, 122 of them since 1800.** These are not wrong lines (the game then says
   only the state's name), but players notice them:
   - India 1970–1973 (V. V. Giri);
   - Iran 1981–1988 (Khomeini; the list also has "Shah 1980–1980");
   - Indonesia 1958–1997 (Sukarno's later years and all of Suharto);
   - the Netherlands 1981–2012 (Queen Beatrix);
   - Venezuela 1869–1951 and 2003–2024;
   - Peru 1957–1989, Uruguay 1952–1984.
7. **Smaller things:**
   - 55 names with nicknames in quotes that are said aloud (Charles VI "the Mad" "the Beloved");
   - 62 very long reigns with nothing to compare against (mostly traditional dates);
   - 19 people listed twice.

### 2. State names (the border map)

1. **A name used after its state ended: 82 names.** Examples:
   - "Kingdom of Great Britain" for the UK, 1801–today;
   - "Estado Novo" for Portugal until today (it ended in 1974);
   - "Mali Federation" until today (it lasted 1959–1960);
   - "Denmark-Norway" until 1940;
   - "First Hellenic Republic" for Greece until 1940;
   - "Empire of Haiti" until 1915;
   - "Ngô Dynasty" for Vietnam until 1406 (it ended in 965);
   - "Sultanate of Malacca" until 1861;
   - "Swedish Empire" until 1814.
2. **A republic ruled by a monarch: 17 lines.**
   - India 1947–49, Pakistan 1947–55, Kenya 1963, Nigeria 1961–62, the Gambia 1967–69, Trinidad and
     Tobago 1963–75, Tunisia 1956, Burundi 1963–66;
   - Iran 1980 (the Shah);
   - Florence 1569–74 (by then the Grand Duchy of Tuscany);
   - the "Italian Republic" of 1805–13 (by then the Kingdom of Italy);
   - Greece 1920;
   - France 1793–94 and 1852;
   - Austria 2011 (Otto von Habsburg).
3. **A kingdom or empire ruled by a president: 36 lines.**
   - "Empire of Haiti" with Haiti's presidents, 1806–1915;
   - "Kingdom of Cambodia" with Lon Nol, Pol Pot (1963–69) and Hun Sen (2015–24);
   - "German Empire, ruled by Friedrich Ebert" (1919).
4. **A name used before its state began: 31 names, about half of them real.** For example, "Later
   Zhou" (a 10th-century AD dynasty) for 750 BC, "Netherlands Antilles" from 1815, "Sultanate of Oman"
   from 1744.
5. **Capitals.**
   - Moroni (Comoros) is on the map as Cabo Verde.
   - Dili in 2000 is shown as Indonesia.
   - Bangui, Maseru, Vientiane and Djibouti sit right on a border, where a map square is too big.
   - 10 capitals have no state at all: eight small island states, but also Baku and Aden.
6. **Hyderabad 1799–1948 is shown under the British instead of the Nizam.** This is already known.

### 3. Events (news lines)

1. **A day of the month read as the year: 150 disasters.** For example, "1531 Lisbon earthquake" is
   dated AD 26 and "1896 Sanriku earthquake" AD 15, so the news comes in the wrong era.
2. **The text names another year: 135.** For example, "AD 8 – Ovid is banished from Rome" is told in
   AD 1 (news of AD 2 to AD 9 all landed in AD 1); "1820: Joseph Smith's First Vision" in 1824; "the Suez
   Canal is opened in 1869" in 1864.
3. **No name, only a Wikidata number: 948 events.** The player hears "Word from nearby: Q60317590".
4. **Broken text: 837 more lines.**
   - 506 start with a day number because the month was cut off ("13 – A group of mercenaries…");
   - 179 have a gap where text was cut out;
   - 50 contain table bars;
   - 33 are scanning errors from the 1909 Deccan gazetteer ("eiglit famines were recoVded").
5. **Placed at sea: 82, about half of them real.** News is put at the middle of Indonesia, which is in
   the sea; "Battle for Outpost Vegas" (Korea) sits near Iwo Jima. The rest are small islands the map
   cannot see.
6. **A known weakness, not counted as errors.** 20,303 news lines are placed by a country named in the
   sentence, and 6,380 of them are heard up to 600 km away or more. For example, rice farming in
   Southeast Asia is told in Xi'an in 700 because the sentence mentions China.

### 4. Famous people

1. **Impossible lifespans: 126.** Sophilos is listed as living 600 BC–AD 600, so he is "talked about"
   for 1,200 years.
2. **Died before being born: 4.**
3. **Broken text: 17.** For example "Ava of Ribagorza, Peerage person ID=416500", and "Killed in the
   crash of a private plane" used as a name.
4. **From far away.** "People here talk about…" names someone born more than 1,000 km away in 34–43% of
   cases (1800–2000), for example Birinchi Kumar Barua (from Assam) in Hyderabad in 1948. It is not
   false, but it sounds wrong. The game picks from everyone of the same country.

### 5. Languages and faiths

1. **Not a spoken language: 29 entries, 17 said in game.**
   - sign languages: Korean Sign, Uruguayan Sign;
   - writing systems: Cyrillic, Chosŏn'gŭl, Hangul, Vietnamese alphabet;
   - leftover text: "Over 77", "Official", "None at the federal level", "Regional/local".
2. **Not a faith name: 7 entries, 4 said.** "The main faith here is From 5th century: Hinduism–Buddhism"
   (Champa), "Protestant majority", "Majority religion", "Religion: Buddhism".
3. **Older than its time: 4 entries, 1 said in game.** Frisia (612–787) speaks "Dutch". Not said in
   game: Holland (1260–1362) has "Dutch Reformed" and Lithuania (1220–1449) has "Calvinism".
4. **Known from earlier, not tested automatically.** "The main faith here is…" uses the state's first
   faith, often the ruler's: Islam for Hyderabad State, where most people were Hindu. Also, "people here
   speak Persian" in Varanasi in 1600 uses the court language.

### 6. The small foundation files (read by hand)

- **Right:** the dates and places of the 76 events and 102 VIPs.
- **Placeholder numbers:**
  - Every war has 5,000 soldiers and 20,000 civilians killed; the game never shows these numbers.
  - Every event lasts 1 year, the Spanish flu and the Black Death too. The event chain uses this.
- **Odd assignments:**
  - Archimedes is under Athens.
  - The Buddha is under the Maurya Empire.
  - Nobunaga and Hideyoshi are under the Tokugawa Shogunate.
  - Chandragupta II's "birth year" is the year he became king.

## What this check cannot see

- **A wrong fact that looks normal:** a wrong ruler with believable years, or a battle at a believable
  place in the wrong year. Only reading against sources finds those.
- **Mistakes Wikipedia or Wikidata share:** the mod's data and its witness come from the same world
  encyclopedia, so a mistake in both looks correct.
- **Some "likely" items turn out fine** (for some rules, about half). The CSV lets you look at each one.

## Suggested order for fixing (most heard first)

1. **Ruler lists:** move prime ministers out, delete claimants and non-person rows, and use the
   Wikidata death years to correct end years.
2. **State names by period:** a small table of names with their years (United Kingdom from 1801, Estado
   Novo until 1974, Dominion of India 1947–50, Kingdom of Cambodia vs Khmer Republic…). Add the Nizam for
   Hyderabad.
3. **Language and faith leftovers:** 36 entries to delete or clean.
4. **Events:**
   - redate the 150 disasters;
   - give the AD 1–10 page its own years;
   - give names to (or hide) the 948 number-only events;
   - trim the leftover day numbers.
5. **Famous people:** drop the 130 impossible lifespans, and prefer people born nearby.
6. **Then add the main rules to `/ee check all`,** so these mistakes cannot come back.

Historical report snapshot is archived as XZ with raw/archive hashes and guarded restoration via `archived_history_reports.py`. The original scripts still write newly generated reports to their original paths.
