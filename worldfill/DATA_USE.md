# How well the mod uses its data (step 13, 2026-10-12)

**Nothing in the mod was changed.** This is a reading of the code plus measurements made with the mod's
own lookup code.

## The short answer

- **The history data is used well for two things.**
  1. **Who you meet.** Villagers appear where people really lived, in about the right numbers.
  2. **What they say.** They talk about who rules them, what people speak and believe, famous people,
     how people live, trade routes and roads, and news.

  It also drives the alternative-timeline mechanic and the briefings given to AI bots.
- **The game's simulation systems do not use it.** War, disease, trade caravans, the economy, farming,
  religion, technology, climate, dynasties and buildings run on two things only:
  - a small hand-made table of 133 civilizations;
  - lists written into the code: 3 diseases, 3 religions, 7 technologies, 2 climate events.

  Wars, sieges and trade routes start only when a command starts them. A battle or a plague in the data
  never makes soldiers march or a disease spread. It only becomes a line of news.
- **Some data is only partly used:**
  - heads of government (4,588) appear in a command, never in talk;
  - only 137 of 6,709 languages can be named;
  - only the first faith of each state is said;
  - villagers never say the name of the town they live in;
  - the recorded populations of 1,787 cities were dropped when the data was built.
- **Four files are copied into every world but never read:** religions, technologies, climate events and
  the news templates. The game uses its own built-in copies instead.

## Where each kind of data goes

| Data | Size | Used by | What it gives the player | How much of it reaches players |
|---|---:|---|---|---|
| Named places | 46,864 | presence, villager spawning | villagers appear; the town's size and jobs | a named place is near 4% (1000 BC) to 32% (1900) of people. The town's name is told only to AI bots and in `/ee` commands |
| Population model (HYDE) + census points for 6 Indian regions | world grid | presence, crowd size, crowd sound | how many people you see and hear | 88–100% of the places where people lived count as inhabited |
| Border map | 187,941 cells + 15,741 Deccan places | the ruler line; the villager culture group (names, skins); famous-people matching | "This land belongs to …" | the state is named for 8% of people (1000 BC), 56% (AD 1), 62–70% (500–1500), 85–96% (1700 on) |
| Heads of state | 17,700 | the ruler line | "… ruled by …" | 70% are said at some time; 24% never (their state is not on the map then); 6% hidden behind a later ruler |
| Heads of government | 4,588 | only the `/ee here` command | nothing in talk | 0% in talk |
| State languages | 2,351 | the language line (first two only) | "The government uses …" | 73% |
| People's languages (Glottolog) | 6,709 | the language line, from 1500 | "… people here speak …" | only the 137 major languages (2%) can be said; heard by 12–26% of people after 1500 (only when different from the state's) |
| Faiths | 2,054 entries + measured shares for 230 states | the faith line | "The main faith here is …" | only the first faith per state (954); the shares are heard by 74–89% of people after 1945 |
| Famous people | 184,193 | the famous-person line | "Sad news this year: … has died", "… was born near here", "People here talk about …" | 99% can be heard somehow. A villager picks from 5 people (1500), 22 (1800), 237 (1900), 470 (2000). "Born near here" reaches under 0.5% of people |
| Ways of life (ArchaeoGLOBE) | 146 regions × 10 dates | the way-of-life line | "Most people around here farm …" | a real survey answer for 7–24% of people before 1850; the rest is estimated |
| Trade routes, Roman roads | 14 routes / 411 towns; 14,769 road sections | the trade and road lines | "Merchants on the Silk Road pass through here" | 1–4% and 6–8% of people (roads only in the Roman world, AD 1–1500); **not** used by the trade caravans |
| Events | 122,432 | the news line, the "event scene" (2–3 extra villagers who repeat the news, with a guard for military events), what a right-clicked villager says, AI briefings, the alternative timeline | "Word from nearby: …" | 90% are the news you hear when standing on their spot in their year; 11,086 are hidden by another event at the very same spot. 42,245 can be stopped by a player, but only 1 has a written story |
| Foundation civilizations | 133 | the simulation systems, the codex "Atlas" | numbers inside the simulation (population, treasury, technology) | all used |
| Foundation events | 76 | the event chain | flags only: nothing visible happens | used, but invisible |
| VIPs | 102 | VIP role-play (a player takes on a historical person) | spawn point, lifetime | used. The codex "VIP Dossier" still shows 3 people written into the code |
| Names, skins | 11 name pools (in the code), skin pool | villager names and looks | names by broad culture group | used, but coarse |
| Religions, technologies, climate events, news templates | 4 files | nothing | nothing | 0%: the game uses built-in copies |

## What villagers can say, by year

The share of the world's people (HYDE population, 1,500 sample points per year) for whom each kind of
line has something to say:

| Year | Inhabited | Named place | State | Ruler | Language / faith | Famous person | Way of life (survey) | Trade route / road | News | Lines (of 6) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1000 BC | 88% | 4% | 8% | 6% | 6% | 0% | 99% (24%) | 1% / 0% | 3% | 1.1 |
| 500 BC | 92% | 9% | 24% | 19% | 18% | 17% | 100% (22%) | 1% / 0% | 3% | 1.6 |
| AD 1 | 95% | 31% | 56% | 52% | 55% | 52% | 100% (15%) | 4% / 8% | 22% | 2.7 |
| 500 | 94% | 21% | 70% | 60% | 53% | 59% | 100% (14%) | 4% / 6% | 1% | 2.9 |
| 1000 | 94% | 9% | 62% | 57% | 57% | 46% | 100% (18%) | 3% / 6% | 8% | 2.7 |
| 1300 | 96% | 16% | 66% | 61% | 60% | 59% | 100% (17%) | 4% / 6% | 12% | 3.0 |
| 1500 | 97% | 16% | 68% | 62% | 73% | 64% | 100% (8%) | 4% / 6% | 19% | 3.1 |
| 1700 | 98% | 18% | 85% | 80% | 84% | 79% | 100% (8%) | 2% / 0% | 25% | 3.5 |
| 1800 | 99% | 28% | 89% | 80% | 85% | 86% | 100% (9%) | 2% / 0% | 21% | 3.6 |
| 1900 | 99% | 32% | 95% | 94% | 86% | 94% | 99% (0%) | 1% / 0% | 42% | 3.8 |
| 2000 | 100% | 26% | 94% | 93% | 91% | 95% | 100% (0%) | 2% / 0% | 52% | 3.8 |
| 2020 | 100% | 24% | 94% | 94% | 91% | 95% | 100% (0%) | 1% / 0% | 72% | 3.8 |

**What this shows:**

- **From 1700 on, talk is rich.** Almost everyone hears who rules them, their language and faith, and
  a famous person.
- **Before AD 1, talk is thin.** Villagers mostly only say how people live, and that is usually an
  estimate.
- **News is mostly country-wide.** A news line about something right here (a battle down the road)
  reaches under 3% of people before 2000, then 14–23% because of modern conflicts and COVID-19.
- **The famous-person line is mostly obituaries in modern times.** It names someone who died that year
  first, which happens for 60–80% of people after 1850. "Born near here" almost never comes up.
- **Two oddities:**
  - **AD 1 news:** 22% of people hear news in AD 1 but only 1% in AD 500, because news from AD 2 to
    AD 9 is all dated AD 1 (found in the fact check).
  - **Roman roads:** they disappear after 1500. The road data ends around AD 500, and a rule in the
    code keeps talking about "an old Roman road" only until 1500.

## Systems that do not use the history data

| System | How it works today |
|---|---|
| War, sieges | wars start only with `/ee war declare` or a broken treaty; sieges only by command. The 13,254 battles and 2,960 wars in the data are news only. |
| Disease | 3 diseases written into the code (Black Death 1347, cholera 1817, influenza 1918) start "globally" in their year. The 5,558 recorded plague and epidemic outbreaks are news only. |
| Disasters (floods, earthquakes, famines) | only by command (`/ee disaster`). The 26,998 hazard events are news only. |
| Trade caravans, ships, economy | routes exist only when a command opens them (plus one Rome–Carthage example in the code). The 14 historical routes are talk only. |
| Population growth, migration, towns, classes | a growth model per civilization, from the hand-made table. Separate from the HYDE numbers the villager spawner uses. |
| Farming, famine, climate | built-in rules plus 2 climate events in the code (Little Ice Age, Year Without a Summer). ArchaeoGLOBE is talk only. |
| Religion | 3 religions in the code (the installed file has 2 and is not read). The state faiths and shares are talk only. |
| Technology | 7 technologies in the code (the installed file is not read). |
| Dynasties, royal court, treaties | their own simulation. The 17,700 real reigns are not used. |
| Buildings | Terra++/OpenStreetMap shapes plus the mod's own style rules. Places, populations and ways of life are not used. |
| Codex screen | the "Atlas" lists the simulation's civilizations; the "VIP Dossier" shows 3 people written into the code. |

## Partly used or unused data

1. **Heads of government (4,588):** only in `/ee here`.
2. **Languages:**
   - only the first two of a state's languages are said;
   - 6,572 of the 6,709 Glottolog languages are never named;
   - the language rule starts in 1500, so before that the "people here speak" part is missing.
3. **Faiths:** only the first listed faith per state, often the ruler's, not the people's (found in the
   fact check).
4. **Town names:** villagers never say where you are; only AI bots get "This is <town>, year …".
5. **City populations:** Reba et al. 2016 recorded the population of 1,787 cities. The mod kept the
   cities but not the numbers, so city sizes come from a size model.
6. **Events:**
   - 11,086 are hidden by another event at the very same spot and year (nearly half of all tsunamis
     share the spot and year of their earthquake);
   - only one news item per place per year;
   - events never change the world: no armies, no damage, no sick people;
   - 76 foundation events only set invisible flags.
7. **Ways of life after 1850:** no survey, so it is always an estimate.
8. **Four installed files nobody reads:** religions, technologies, climate events, news templates.

## How to get more out of the data (biggest effect first)

1. **Let events start the world systems.**
   - battles and wars bring soldiers or a war between the two states, in that place and year;
   - the 5,558 plague and epidemic outbreaks start outbreaks in the disease system (instead of 3);
   - famines, floods and earthquakes use the disaster system that today only runs by command.
2. **Let the 14 trade routes send caravans and ships** in their own years, through the logistics system
   that already exists.
3. **Use the real population numbers:**
   - the HYDE totals per state in the population system;
   - the 1,787 recorded city populations in the population ladder (they are a free download).
4. **Say more of what is already known (cheap):**
   - the town's name;
   - the head of government ("The prime minister is …");
   - news not only from the nearest event;
   - more "born near here".
5. **Religion and names from the data:**
   - the religion system starts from the state faiths and the measured shares;
   - villager names follow the local language, not 11 broad pools.
6. **Ways of life feed farming and building styles** (ArchaeoGLOBE says where people farmed, herded or
   lived in towns).
7. **Read the four installed files**, or stop installing them.
8. **Write more stories:** 42,245 events can be stopped by a player, but only one has a "what if" story.

## How this was measured

- `data_use_sample.py`: 1,500 sample points per year for 14 years, each standing for an equal share of
  the world's people (HYDE).
- `probes/DataUseProbe.java` with `probe_data_use.sh`: runs the mod's own lookup code at those points
  and over every event. The output is saved as `data_use_probe.json`.
- `data_use_counts.py` writes `data_use_counts.json`: which rulers, people, languages and faiths can
  ever be said, using the same rules as the game.
- "Heard at home" means the event is the news the game picks on its own spot in its first year. It is
  the best case; elsewhere it competes with nearer events.
- The rest comes from reading the code: who calls which data, and what each world system ticks on.

Storage note: historical `data_use_probe.json` is losslessly archived as `data_use_probe.json.xz`. Read/verify via `python3 worldfill/archived_history_reports.py data_use_probe.json`, or add `--restore` when space permits; restoration refuses overwrite. It is historical probe output, not a new game test.
