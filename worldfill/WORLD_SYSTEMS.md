# All world systems of the mod (2026-10-12; core rows updated after step 14)

Read from the code (`eternal/src/main/java/com/eternalengine`, 277 files). The simulation engine owns
52 systems and runs the automatic ones every game tick. All of them are switched on by default,
except the AI brain and the web console.

**How a system starts:**

- **auto:** runs by itself.
- **auto, once started:** runs by itself after a command or a player starts it.
- **command:** does something only when an `/ee` command (or a menu) asks.

**Where its facts come from:**

- **history data:** the collected data (places, the border map, rulers, events, people and the rest).
- **civilization table:** the hand-made list of 133 civilizations.
- **built-in:** a few facts written into the code.
- **map:** Terra++ / OpenStreetMap.

**In numbers:** 69 systems.

- **39 auto.** One of them, temporal rebuilding, has nothing to do yet.
- **6 auto once started.**
- **22 command or menu only.**
- **2 off by default.**
- **11 use the history data:** numbers 6, 8–13, 18, 19, 21 and 22.

## 1. Core: time, saving, the real-world map

| # | System | What it does | Starts | Facts from |
|---|---|---|---|---|
| 1 | Simulation engine | the master switch: ticks every system below, each in its own safety net, measures lag per system; pause (`/ee pause`, and while nobody is online), `/ee reset`, `/ee reload` (step 14) | auto | — |
| 2 | Clock | the game year and speed (Eternal Engine clock, normal speed one year every 2 minutes, or Terra++ time; `/ee year`, `/ee speed`); VIP votes, big-event slowdowns, year signal (step 14) | auto | — |
| 3 | Tick scheduler | spreads system updates over ticks so the server does not lag; intervals from the server config (step 14) | auto | — |
| 4 | World state | the central store: civilizations, wars, diseases, trade routes, flags; saved and restored at restart (step 14); autosave | auto | — |
| 5 | Saving and loading | all file reading and writing, backups every 30 minutes | auto | — |
| 6 | Foundation data installer and loader | copies the 13 data files into each world and keeps them up to date after a mod update (step 14); loads civilizations, events, VIPs, buildings, names and skins | auto (world start) | all data files |
| 7 | Terra++ bridge | real-world map: places on Earth to blocks and back; present-day and dated map places | auto | map |

## 2. People and places (the systems that use the history data most)

| # | System | What it does | Starts | Facts from |
|---|---|---|---|---|
| 8 | Historical presence | answers "who lived here in this year, and how many" | auto | history data |
| 9 | Population ladder | how many people live in a place in a year (census, then estimates) | auto | history data, 6 census regions |
| 10 | Villager spawner | puts townspeople where people lived, and an "event scene" (2–3 villagers spreading the news); since step 17 it waits for the history data loaded in the background (no freeze) and remembers everyone past 128 blocks from every player | auto | history data |
| 11 | Crowd figures | the drawn crowd that makes big towns look full (first stood in step 16; since step 17 taken out past 128 blocks from every player, the same people on return) | auto | history data |
| 12 | Villager talk | the 6 talk lines (ruler, language and faith, a famous person, way of life, trade route, Roman road) and the news | auto | history data |
| 13 | Human NPC | the villager itself; right-click it to hear the news, or the current year | auto | history data |
| 14 | Villager manager and virtualizer | keeps track of villagers; far-away ones become "virtual" to save lag; since step 17 a place really remembers its people (Minecraft's despawn no longer deletes them) | auto | — |
| 15 | Agent virtualization | up to 100,000 background people, shown near players | auto, once a command fills it | — |
| 16 | Villager behavior | basic villager behavior (a foundation) | command | — |
| 17 | Names and skins | villager names (11 culture name pools, thin) and looks by culture and era; since step 17 names follow the language spoken at the place | auto | built-in, skin pool, local languages |
| 18 | Crowd sound | crowd noise that grows with the number of people (since step 17 worked out once a second) | auto | history data |
| 19 | Current affairs | briefings for AI bots and for right-clicked villagers | auto | history data, world state |

## 3. History and alternative timelines

| # | System | What it does | Starts | Facts from |
|---|---|---|---|---|
| 20 | Event chain | the 76 foundation events "happen" in their years (invisible flags) | auto | 76 foundation events |
| 21 | Timeline manager | alternative timelines and their "what if" stories | auto | history data, story files |
| 22 | In-world intervention | fighting at a live event can split off an alternative timeline | auto (player actions) | history data |
| 23 | Reality rifts | rifts (particles) at the places where timelines split | auto, once a timeline splits | — |
| 24 | Chrono-Nexus campaign | a campaign game mode with phases and a paradox countdown | command | — |
| 25 | Chronos codex | menu screen: timeline tree, atlas, VIP dossier (3 people written into the code) | menu | civilization table, built-in |

## 4. States and society (run on the civilization table)

| # | System | What it does | Starts | Facts from |
|---|---|---|---|---|
| 26 | Civilizations and territory | the list of civilizations and who owns which area | auto | civilization table |
| 27 | Population growth | births and deaths per civilization | auto | civilization table |
| 28 | Migration | people move away from famine, disease and oppression | auto | civilization table |
| 29 | Social classes | class shares (pre-industrial, industrial from 1750) | auto | civilization table |
| 30 | Urbanization | how many live in towns | auto | civilization table |
| 31 | Economy | treasury income and spending | auto | civilization table |
| 32 | Farming and famine | food security and famine warnings per civilization | auto | civilization table, built-in rules |
| 33 | Climate | the Little Ice Age and the Year Without a Summer | auto | built-in (2 events) |
| 34 | Religion | religions spread between civilizations | auto | built-in (3 religions) |
| 35 | Technology | technologies unlock, eras change | auto | built-in (7 technologies) |
| 36 | Faction relations | how friendly two civilizations are | command | civilization table |

## 5. War

| # | System | What it does | Starts | Facts from |
|---|---|---|---|---|
| 37 | War | wars between civilizations, armies, battles, war weariness | auto, once a command (`/ee war declare`) or a broken treaty starts one | civilization table |
| 38 | Sieges | soldiers attack walls; damage goes through the block queue | command | — |

## 6. Trade and transport

| # | System | What it does | Starts | Facts from |
|---|---|---|---|---|
| 39 | Trade routes | routes between civilizations and the trade income | auto, once a command opens a route | — |
| 40 | Caravans, ships, prices, bandits | caravans and merchant ships travel the routes; prices change; bandits ambush | auto, once a command sends a caravan or ship | — |
| 41 | Vehicles | route checks for carts, ships and other vehicles | command | — |

## 7. Disease and disasters

| # | System | What it does | Starts | Facts from |
|---|---|---|---|---|
| 42 | Disease | the Black Death (1347), cholera (1817) and influenza (1918) start in their years and spread between regions | auto | built-in (3 diseases) |
| 43 | Contagion in the world | sick villagers infect others; quarantine gates; plague doctors and field hospitals | auto, once a command infects someone | — |
| 44 | Disasters | famine, great flood, volcanic winter, earthquake, great fire in the world | command | — |

## 8. Rulers, court and VIPs

| # | System | What it does | Starts | Facts from |
|---|---|---|---|---|
| 45 | VIP system | a player can become a historical person (102 VIPs); VIPs die after their real death year | auto (claimed by command or menu) | 102 VIPs |
| 46 | VIP commands and authority | what a VIP can order, and how loyal people are | menu | — |
| 47 | VIP takeover | taking a VIP's place through actions in the world | auto (player actions) | — |
| 48 | Reputation | player actions change how people see you | auto (player actions) | — |
| 49 | Royal court | throne room and court | command | — |
| 50 | Diplomacy and treaties | treaties between civilizations; breaking one can start a war | command | civilization table |
| 51 | Dynasties and coups | succession laws, heirs, coups | command | — |
| 52 | Imperial command | a grand-strategy dashboard | command | — |

## 9. Buildings and blocks

| # | System | What it does | Starts | Facts from |
|---|---|---|---|---|
| 53 | Block update queue | changes blocks safely, a few per tick (sieges, disasters, landmarks) | auto | — |
| 54 | Temporal rebuilding | tears down and rebuilds buildings when the year changes | auto, but nothing gives it work yet | — |
| 55 | Building history | records of buildings over time | auto (load) | 2 foundation buildings, saves |
| 56 | Building date guess | guesses when a building was built | command | map |
| 57 | Architecture style | builds in the style of a civilization and era | command | built-in |
| 58 | Landmark generator | builds famous landmarks and monuments | command | map |
| 59 | Anomaly detection | finds blocks that do not fit the era | command (and admin or historian briefings) | — |

## 10. Map, sound and look

| # | System | What it does | Starts | Facts from |
|---|---|---|---|---|
| 60 | Map overlays | shows caravans, wars and epidemics on the map every 5 seconds | auto | world state |
| 61 | Historical audio | era music and sounds | command | built-in |
| 62 | Heraldry | banners and crests | command | built-in |

## 11. Incidents

| # | System | What it does | Starts | Facts from |
|---|---|---|---|---|
| 63 | Incident creator | makes up incidents scaled to difficulty | command | — |

## 12. AI and tools

| # | System | What it does | Starts | Facts from |
|---|---|---|---|---|
| 64 | AI brain bridge | lets an outside AI model propose actions; they are checked and only logged for now | off by default | — |
| 65 | Mindcraft bot bridge | connects AI player bots | command | current affairs |
| 66 | Web console | a local web chat for developers | off by default | — |
| 67 | Telemetry | debug snapshots of a map column | command, briefings | map |
| 68 | Player, chunk and entity data | stores per-player, per-chunk and per-NPC data | auto | — |
| 69 | Commands and `/ee check all` | all `/ee` commands, and the self-check report | command | everything |

**Not built:** an "era system" is listed in the tick but switched off in the code (the class does not exist).
