# Villager plan (updated turn 57, 2026-10-13; step order from turn 91)

**Turn 91:** the user's 7 requirements are in `REQUIREMENTS.md`, the master list. **Turn 92:** every system they need (137; 166 after turn 95) and the order of work (steps 21–61) are in `SYSTEMS_PLAN.md`. Real-game testing happens at the final stage (step 38); every step is tested here before that.

This is the plan for villagers: talk, mind and history knowledge. It replaces the step list from turns 43–48. The world-systems review (groups 3 to 8) goes on alongside it, and each group connects its own villager part when it is reviewed.

## Decisions so far

- **Turn 47:** AI chat dropped (not reliable). All talk is data-only.
- **Turn 48:** talk menu (A) with mood wording (B), then villager chatter (C).
- **Turns 50–51:** money, trade, war, disease and loyalty are connected later, each when its group is reviewed. Steps 1–2 only add the "joints".
- **Turn 53:** event cards. Every event gets what / when / where / who / source, follow-up questions, a marker, and a clock that slows down near big events.
- **Turn 55 ("Yes"):** linked cards and the history book are added. Knowledge becomes a web: every name in an answer can be asked about. MCA ideas are borrowed (tracker compass, journal, family tree, letters), but not its code.
- **Turn 56:** the user asked for three changes.
  - **No source names in the game:** no Wikipedia or other source anywhere a player can see. People say how they know in their own words ("It's all in today's paper"). The sources stay in the data files, for checking only.
  - **The newspaper and the map are goods** the player buys, for example at a paper stand.
    - The newspaper is one per day, with the day's news.
    - The map shows towns and roads, and marks the places from the newspapers you own.
    - Prices are in the money of the place and time (Osmania sicca annas in 1948 Hyderabad). They will come from the trade system (group 6).
  - **A better UI.**
  - Following from the goods idea, the history book now holds only what the player has heard or read: notes with the date and who said it.

- **Turn 57:** preview 2 approved ("its perfect"). The build started with mod step 18 (see below).

## Steps

| Step | What | Status |
|---|---|---|
| 1 | **Data fix:** ruler lists, then language and faith lines, far-away famous people, broken news text, place names (1 answer in 10 is wrong today, `TALK_SPOT_CHECK.md`) | **waiting for your OK** (turn 25 said "nothing for now") |
| 2 | **People:** real names, jobs (chosen to fit goods later), town and ruler talk, the ageing fix (remembered people never age); the life record (job, money level, faith, health, one loyalty number, opinion of each player) | planned |
| 3 | **Mind:** needs, feelings, personality, decisions; the town-situation reader (wars, plagues, famines and disasters from the 122,422 dated events); mood wording (B); the mind display | planned |
| 4 | **Event cards and linked cards (data):** cards for events, people, places, groups and families, with dates, coordinates, paths of big events and links; from Wikidata (20,922 events already carry an id) plus Wikipedia, cross-checked; hand check of the most-heard cards; Hyderabad and the Deccan first | **started in step 18:** the Hyderabad 1948 pack (the 28 cards of preview 2, written from the research of turns 53–54); **step 27:** linked cards of people and groups for every place, from Wikidata cross-checked with the Wikipedia year pages; event cards are step 28, families step 41 |
| 5 | **Talk menu (A):** follow-up questions, clickable names, "Ask about…", "I don't know, ask at the palace", markers with direction and distance, the villager points, tracker compass; villager chatter (C); **buying from sellers** (newspaper, map) | **step 18 built the talk screen:** questions, gold names, "Ask about…", the court referral with distance, Back, dated answers. Buying is step 19, the compass step 20, chatter later |
| 6 | **History book and knowledge goods:**<br>• the book (the existing Chronos codex) holds your notes: names heard, what each person or paper said, the date; family trees; journal; search<br>• **newspaper item:** one per day, its names go into the book<br>• **map item:** towns and roads, plus news marks from your papers<br>• "later" facts only behind a time-traveller switch | **added** |
| 7 | **Event time:** the clock slows down near big events (`registerSlowdown` exists); villagers only know what has happened by the in-game date | **added** |
| 8 | **Friendship and greetings (E)** | planned |

**Later:**
- Meet the people: historical figures at their homes in the right years, for example the Nizam at King Kothi in 1948, through the VIP system.
- Talk extras (D), F and G.
- The crown as a fork (two parts).
- Families.
- Money, trade, war, disease and loyalty, each in its world-systems group (4 to 8).

## Mod build steps (README numbering)

| Mod step | What | Status |
|---|---|---|
| 18 | Knowledge core (packs, dates, levels, distances, notes) and the talk screen | **done, turn 57** |
| 18b | Fixes from the user's game log: the date with Terra++ time, no early or stale news, townspeople step out of walls | **done, turn 58** |
| 18c | The talk box fits every screen size (it ran off the right edge at 1920 x 1080); the date line at the top of the screen from the approved preview (date and place) | **done, turn 60** |
| 18d | One calendar: the date follows the Minecraft days with both clocks; sleeping, `/time add` and `/time set` only move it forward; only `/ee date` moves it back; a new speed keeps the date | **done, turn 65** |
| 18e | The user's log after 18d: the stand-still after joining (the people spawner built a far chunk), Terra++'s own time commands follow the calendar's rules, `/ee date` does Terra++'s whole time jump | **done, turn 67** |
| 18f | The date line at the top right of the screen removed (the user did not like it); the talk box keeps its date | **done, turn 69** |
| 19a | The purse: money is a number per player and per kind of money; every place and year has its money (the money table: 41 kinds of money, 69 place rows, 3000 BCE to now, barter where there was none); the start money is a day's pay; `/ee purse`, `/ee money` | **done, turn 82** |
| 19b | Earning: merchants buy your goods (10 goods with items, priced by the trade engine through a day's pay); a money-changer swaps money for a cut; "Who buys goods here?"; one money-changer in each market; `/ee market`; `/ee reset confirm` empties purses | **done, turn 84** |
| 19c | Sellers: merchants, paper sellers and newsletter writers keep a fixed stand; "Show me your goods." opens the trade screen (the approved preview: trades on the left, the picked trade on the right, Buy, "‹ Back to …"); merchants sell the goods they buy at full worth, a few lots a day, and the local products (product atlas part A: 13 cards in `economy/products.json`); `/ee shop`; protocol 5 | done (turn 85) |
| 19d | The newspaper item (one a day, dated, its news kept on the item; a pack's checked papers on their days, else last year's and ongoing events; prices; an advertisement), the newspaper screen, names into the history book; the free town crier (calls out the news); the handwritten newsletter (a day's pay) before print; who brings the news where and when (`NewsEras`); `/ee paper` | done (turn 85) |
| 19e | The map item (a pack's own map, else the gazetteer's towns and the roads of the year), news marks from the papers read while carrying it, the map screen, "Add to Xaero's map" (Xaero's own share link; untested here); `/ee map` | done (turn 85) |
| 19f | Sellers take the money of the place or money it also takes (Indian rupees in Hyderabad, at 7 for 6); old money ("That old Mughal rupee is not taken any more") and foreign money are refused, and the money-changer is named; on another road of history papers print the new history first, and a pack's papers stop where the change happened | done (turn 85) |
| 19 (product atlas) | Part A: the Hyderabad 1948 goods (with 19c, done); B: "is it here?" for 146 regions and `/ee products here` (done, turn 86: 129 products, 17 areas, merchants sell up to 8 kinds of the place, brought from far at twice the price); C: grow to about 400 kinds; D: chains; E: disruptions | A and B done; C, D, E planned |
| 19g | Somebody buys in every settled place: a trader in towns (buys at 60 in 100, changes money keeping 10), a pedlar in villages with money (50 in 100), anybody swaps a little where people swap and nobody trades; buyers take the atlas products (twice as much when brought from far); the trader takes coins as metal where people swap; no more wrong hints | done (turn 88) |
| 20 | The history book (your notes) and the tracker compass: the book item given once on joining; names in groups with a search, notes with the day and who said it, linked names, journal, family tree, "later" only with the time traveller setting; "Track on the compass" (book) and "Track it on my compass" (talk) point any compass there, with the distance on the action bar; `/ee book`; protocol 6 | done (turn 88) |
| Turn 89 | The 7.5-second freeze after joining: ground look-ups no longer wait for Terra++'s land-cover map; the spawner spends at most 50 ms a cycle standing people up and logs where its time goes | done (turn 89) |
| 21 | People stay while you talk or trade (nobody is moved, swapped or removed while busy) | **done in turn 97:** held until goodbye, 8 blocks away or 2 minutes idle; they stop and face you; a crowd figure you talk to becomes a townsperson; "… has left." instead of a silent close. With it: map positions from the world's own projection, Minecraft's mobs off (settings), first years for technologies and vehicles, the slow crowd cycle fixed (README, step 21) |
| 22 | The history book is bought from villagers (no longer given on joining) | **done in turn 98:** 13 forms by place and year (notebook, parchment, palm leaf, birch bark, bark paper, papyrus, bamboo slips, wax tablets, clay tablets, rune sticks; knotted cords, message stick, tally stick where nobody writes); merchants, traders, pedlars, paper sellers and newsletter writers sell it; anybody else says where, or gives the local memory aid |
| 23a | Real money for the placeholder places, every region at once | **done in turn 99:** 401 kinds of money (was 41) in 1,006 rows; every region and era named, from Viking weighed silver, Icelandic cloth and manillas to every modern currency and the euro in Bulgaria 2026; a day's pay of the place for shared monies; placeholders for people from 41.5% to 0.0% |
| 23b | Money you can hold for every place and time: coins, notes, shells, weighed metal as items; paying with them; purses become coins | **done in turn 100:** money is pieces in the inventory in 16 looks (gold, silver, copper, holed cash, nickel, paper, cowries, cacao beans, cut silver, weighed copper, manillas, nzimbu shells, salt bars, cloth, beaver pelts, bullet coins); each of the 398 monies with coins has the pieces of its year; paying gives exact change; merchants and money-changers pay in pieces; barter keeps a written tab |
| 24 | The Minecraft trade screen: buy, sell, change money, swap goods, old money | **done in turn 101:** the villager's trade screen with real slots ("Let's trade."): clicking a trade fills the two slots from the bag; any mix of money taken here pays, change back; selling a lot at a time; changing any amount; bigger and smaller pieces; swapping goods where people have no money (the tab pays, too much is owed back); old and foreign money refused with the reason; cowries as small change in Calabar; the talk keeps one price question instead of one option per good; protocol 8 |
| 25 | The history data fix (my default since turn 96: do it) | **done in turn 102:** rulers, state names by period, occupations, the Nizam's Hyderabad State, coastal squares and 2025–2026, faiths by period, news lines and famous people fixed; 8,680 changes listed in `step25_changes.csv`, reversible with `fix_history_data.py --undo`; Rome's townspeople keep the right label across years |
| 26 | Foundations for big data: the key (place, date, timeline, universe), streaming storage, estimate marks, licences | **done in turn 103:** one key and one query for every system; famous people as tiles (40 → 8 MB, the same answers); recorded/estimated marks; the data list with hashes, licences and credits; Second World War occupations and 89 border cities fixed (Kinshasa's townspeople are Congolese, not from Brazzaville) |
| 27 | The card pipeline: Wikidata + Wikipedia, cross-checked, for every place (was step 21) | **done in turn 105:** 148,510 famous people and 26,855 groups (schools, companies, parties, papers, armies, societies, orders) as cards in tiles, cross-checked with the Wikipedia year pages; every place names its people ("Anyone famous from here?") and groups ("What groups are there here?"), each a card worded for the date (who, what they did, where from with the compass, links); nobody is known before their time; "Who rules here?" links the ruler's card; the book finds and tracks them |
| 28 | Events, natural events, cause and effect, with the occupations and disputed land of step 26 (known problems 39 and 40) | **done in turn 106:** 32,542 event cards (what, when, where, who took part, why, what came of it, its parts) with the cause-and-effect graph stored both ways; the news names its event with a card; "What happened here before?" at every place; 5,884 storm landfalls and 1,844 other natural events; "German troops have held this land since 1940"; six disputed lands say who holds and who claims them |
| 29 | Local rulers, divisions, place names, towns' lives, population | **done in turn 107:** 30,151 towns with names by era (every history site that is a town takes its name of the year: Bombay 1900, Edo 1700, Léopoldville 1955), people by year from census figures, founding, "Which province is this?" and "Who runs this town?" by era; 538 ties between states ("Which states is it tied to?": allegiance, vassals, realms, NATO, the Warsaw Pact) |
| 30a | The technology atlas (`TECHNOLOGY_PLAN.md`) | **done in turn 108:** 130 technologies, the year each reached each of 258 countries (recorded from Wikipedia, from CHAT, or estimated and marked), the spread inside a country, how common (cities first), losses and versions; villagers say "What new things are there here?"; the fastest travel follows the place; the country grid |
| 30b | Economy, faiths, languages | **done in turn 109:** who reads (by land, year, town size and sex) and in which script; 35 systems of measures and every country's metric year; wealth and hard times; 19,828 holy places, the festivals and pilgrimages of 30 faiths, Christian and Islamic feast days by the calendar; four new questions on the place card |
| 31 | Check Terra++'s buildings and roads by year in the test places | next |
| 37 | Event time: slowdowns near big events, news by the day everywhere, local calendars, how fast news travels (was step 22) | planned |
| 30–61 | The rest of the order of work | see `SYSTEMS_PLAN.md`, part 5 |

## Decisions for step 19 and after (approved in turns 73-81)

- The purse is a number, not coin items. A start money of a day's pay. **Replaced in turn 90-91:** money you can hold, as items, for every place and time (step 23).
- News before newspapers: a free town crier, and a costly handwritten newsletter.
- The map is our own item, with an "Add to Xaero's map" button.
- Weapons: all five ways (join a side, buy, take, make, rewards), strict year rules; the mods Spartan Weaponry, Epic
  Knights (+ Antique Legacy), Musket Mod and TaCZ; vanilla weapons without them. Indian weapons get local names now,
  their own items later. Weapon laws (licences) yes. Modern guns cannot be crafted; diamond and netherite swords locked
  (a setting).
- Product atlas: start with about 120 kinds (grow to about 400), about 100-150 holdable items; it starts with the
  Hyderabad 1948 goods (part A).
- Step 19b (turn 84, "go"): a merchant pays 70 in 100 of a good's worth; full price for the first lot of each good in
  a Minecraft day, half for the next, then he has enough; he pays out at most 8 days' pay a day. The money-changer
  keeps 2 in 100 where a fixed rate is known and 10 in 100 for old or far-away money (he values it by what it buys).
  All four are settings. The first sale gives the start money; `/ee reset confirm` empties every purse.
- Steps 19c-19f (turn 85, "Go for next. i will test after completing step 19"): my defaults, built without stopping
  for tests. Sellers ask the full worth (merchants buy at 70 in 100); a paper costs a sixteenth of a day's pay from 1900
  (a quarter before 1830, a twelfth to 1899), a handwritten newsletter a day's pay, a map half a day's pay (three days'
  drawn by hand); prices are rounded to the biggest coin no more than an eighth of the price. Printed papers reach a
  region's cities in its year (South Asia 1840, an estimate; the first was 1780) and its towns 50 years later; villages
  have a crier. Papers print only what has surely happened by their day: a pack's checked papers, else events still
  going on and last year's. No stand blocks are placed; sellers stand still at their spot instead.

- Step 19g (turn 88, "ok and next" to fixes A-D of turn 87): a trader in every town, a pedlar in every village with
  money, anybody swaps a little where people swap and nobody trades; buyers take the atlas products; the town trader
  changes money (10 in 100), and where people swap takes coins as metal. Terms from the merchant settings: trader -10
  and half the money, pedlar -20 and a quarter, anybody -20 and an eighth. Wages (E) later, with villager jobs.

- Step 20 (turn 88, "ok and next"): the history book as in preview 2 (a new item given once per player, not the old
  Chronos codex screen); the tracker compass is any vanilla compass pointed with the lodestone needle (one is given the
  first time a player tracks without a compass); the time traveller view is a setting (off).

## Rules for every step

1. **Villagers only repeat checked data.** Better silent than wrong. A missing answer hides its button.
2. **No source names in the game** (turn 56). People say how they know in their own words, and estimates are said as estimates ("some say about 200,000"). The real sources stay in the data files for checking.
3. **Sad or sensitive events are told in neutral words,** whatever the mood.
4. **No future knowledge for villagers.** Only the history book shows "later", behind a switch.
5. **Who knows what:**
   - ordinary villagers know everyday things and news;
   - officials and scholars know more;
   - the book knows everything.

## Previews

- `npc_talk_ui_preview.html.xz`: archived static talk menu, moods, mind display and chatter (turn 49).
- `npc_knowledge_ui_preview.html.xz`: archived static preview 2 (turn 56), Hyderabad on 12–18 September 1948.

These two original HTML previews can be verified or restored byte-for-byte using `python worldfill/archived_history_reports.py ORIGINAL_NAME [--restore]`; restoration needs workspace headroom and refuses overwrite. They are prototypes, not active game code.
  - Talk box, trade screen, newspaper, map item, history book of your notes, hotbar.
  - No source names.

## Still open

- May I fix the history data (step 1)?
- Your game tests: the calendar (TEST_CHECKLIST step 8), the purse (step 9), earning money (step 10), sellers,
  newspapers and maps (step 11), the product atlas (step 12), buyers everywhere (step 13) and the history book and
  compass (step 14, new).
