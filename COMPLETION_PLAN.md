# How complete is each requirement, and what would finish it

_2026-10-24, written against `worldfill/REQUIREMENTS.md` as revised today (R1 and R2 now run to 3000 AD)._

## The count

**0 of 7 requirements are complete.** Three are close enough that one blocked item each stands between them
and "done"; four are still mostly open. The table is the project's own marking, corrected where I measured
something this session.

| # | requirement | done | left | verdict |
|---|---|---|---|---|
| 1 | Earth 1:1, buildings and roads, 3000 BC → 3000 AD | land, today's buildings, buildings by year (all Terra++) | past towns, past roads, famous buildings beyond a command, **the whole 2026→3000 block** | ~55%, **blocked by R1-d (past towns)** |
| 2 | Every history 3000 BC → 3000 AD | rulers, borders, 129,163 events, 30,151 towns, populations, money; **vocabulary 0 undeclared (19)**; **99.4% of polities name their people (20)**; **all 1,567 can name themselves and their years (21)** | news by the day, a *named-only* polity's economy (R2-d3), the whole 2026→3000 block | **~85%** |
| 3 | People act out history | talk, names, cards, crowds, vanilla mobs off | famous people at their homes, event scenes beyond "a few people at a spot", jobs and wages | ~45% |
| 4 | Money, vehicles and many more | money (401 kinds), news/maps/book, technology atlas | **vehicles (nothing moves)**, goods 132 of ~500, weapons not built, jobs and laws | ~50% |
| 5 | Changing history, butterfly effect | stop an event, changes add up, one written story (Mumbai 2008) | **kill or save a famous person**, a history that grows, the link to Terra++'s land | ~35% |
| 6 | Breaking a paradox | Terra++ has the mechanic; the mod has a command-only countdown | everything else — the mod is not connected to Terra++'s universes | ~15% |
| 7 | Performance | two freezes fixed, crowd settling, data budgets | **the 30-minute walk (never run)**, Terra++ rebuild stalls, no fps numbers | ~40% |

The two weakest are **R6 (15%)** and **R5 (35%)** — and they are exactly what your doubts touched today
(VIPs have no effect; killing one changes nothing). Not a coincidence: R5 is where VIP consequences were
supposed to live, and they were never wired.

## What would finish each one

### R1 — Earth 1:1 (the blocker: the mod builds no towns)

| step | what it does | how it is proven |
|---|---|---|
| R1-d | **past towns** — houses, markets, temples, walls of the era, at the right size and place, from the 30,151-town data already in hand | a check that asks "what should stand here in this year" and compares with what stands; ten test towns walked |
| R1-e | **past roads** — Roman roads, Silk Roads, Grand Trunk Road built for their years, not only drawn on the map item | the same check, for roads |
| R1-f | **famous buildings** built from the cards, not by command | Charminar, Colosseum, Angkor Wat appear in their years with no command typed |
| R1-g | **2026 → 3000** — one projected continuation per place (land, buildings, roads, population, money, technology), marked *projected*, agreeing with itself in 2100, 2400, 3000 | three future years walked: nothing stands early, everything is marked, neighbours agree |

### R2 — Every history (the blocker: the last 2% of the data, then the future)

| step | what it does | how it is proven |
|---|---|---|
| ~~R2-a~~ | ~~fix the **18 vocabulary ids**~~ — **DONE 2026-10-24, board 19**: 10 were a missing alias (mapped by fact), 18 declared with reasons, probe now reports **0 undeclared** | `probe_vocabulary` → PASS, 0 undeclared |
| ~~R2-a2~~ | ~~a source for the 18 declared polities~~ — **DONE 2026-10-24, board 23**: a second register holds all 18 (12 recorded by a source, 6 estimates), the vocabulary probe now reports **0 declared-absent**, and a check keeps the two registers from drifting | `polities_second_register.json`; "second register closes its gaps" |
| R2-a2b | the six estimate rows (Amber, Kolathun, Manipur, Somavamshi, Tomara, Zamorin) need one citation each | their `confidence` becomes `recorded` |
| ~~R2-d (naming half)~~ | ~~**52.2% of polities named from the generic pool**~~ — **DONE 2026-10-24, board 20**: name pool now chosen by the centre of each polity's recorded extent (`PlaceNamePools`), plus a new SE Asian pool. **818 → 10 (0.6%)**, guarded by a 1% budget inside `/ee check all` | in-game check: "1557 of 1567 polities get a regional name pool" |
| ~~R2-d2 (reading half)~~ | ~~every polity can say what it is and when it stood~~ — **DONE 2026-10-24, board 21**: `PolityFacts` reads name/span/centre from the register, `/ee villager nearby` names each person's civilization with a marker for record vs named-only, and a check guards it. **1,543 polities went from "no civilization" to a named state with dates**, at no tick cost | in-game check: "1567 of 1567 can name itself and its years" |
| R2-d3 | what a *named* polity still lacks: treasury, its own population, engine backing — the `*` in the display. Not fixed by bulk synthesis (R7); needs a lean per-polity economy layer instead | a named-only polity can price goods and pay wages without being a registered civilization |
| R2-b | **news by the day** everywhere, not only Hyderabad 1948 | 50 sampled place-days across 10 regions read as day-specific |
| R2-c | **2026 → 3000** — project every register forward, one shared future, marked *projected* | the four future rules (continues, one future, marked, over-writable) each as a check |

### R3 — People act out history (the blocker: famous people standing in their own houses)

| step | what it does | how it is proven |
|---|---|---|
| R3-a | **famous people at home in their years** from the 148,510-person card data — the Nizam at King Kothi 1948, Pericles in Athens 430 BC | walk five of the project's own test events and find the named person where the card says |
| R3-b | **event scenes** beyond a handful of people: sides, clothes, weapons, a march, a siege, a crowning | the seven test events in the requirements doc, one by one |
| R3-c | jobs, wages, daily rounds by trade | a town's people have trades and a working day |

### R4 — Money, vehicles, things (the blocker: nothing moves)

| step | what it does | how it is proven |
|---|---|---|
| R4-a | **vehicles that exist and move** — carts, chariots, horses, camels, elephants, boats, ships, then trains, trams, cars, buses, bicycles, planes, each in its own years | one route per vehicle walked in a game; a check that none appears early |
| R4-b | goods 132 → ~400 with raw-to-made chains, and shortages | one table per kind, as the doc requires |
| R4-c | weapons you can get, with era rules and licences | a check per era and region |
| R4-d | jobs, wages, laws | a town's pay matches the money data |

### R5 — Changing history (the blocker: only one event has a written story)

| step | what it does | how it is proven |
|---|---|---|
| R5-a | **kill or save a famous person** → the timeline bends: a successor, a changed border, changed events | kill Pericles in 430 BC; Athens' next ten years differ in rulers, events and papers |
| R5-b | a butterfly that **grows**: new rulers, borders, wars, money, buildings, year after year | the doc's own test — stop Operation Polo 1948, then look at 1958 and 1998 |
| R5-c | connect the mod's branches to **Terra++'s land branches** | a changed history changes the visible buildings |
| R5-d | papers, cards and the book speak each timeline | a paper in a changed timeline says what changed |

### R6 — Paradox (the blocker: the two halves are not connected)

| step | what it does | how it is proven |
|---|---|---|
| R6-a | **name the fixed points** in the mod and feed Terra++'s paradox counter | break the Charminar in 1700 → warning → rupture → new universe |
| R6-b | the story continues there with broken logic: people from other eras, events out of order, rulers who should not be | at least five kinds of break seen and named |
| R6-c | broken physics Minecraft allows: gravity, day length, time speed, weather, mobs | one check per kind |
| R6-d | portals in and out | a round trip that survives a restart |

### R7 — Performance (the blocker: the long walk has never happened)

| step | what it does | how it is proven |
|---|---|---|
| R7-a | **the 30-minute walk** through cities and years with time jumps, numbers written down | no tick > 250 ms, average < 50 ms |
| R7-b | the Terra++ rebuild stall (the ~5,900 km of first-visit ground you hit at R5) either sped up or covered by a waiting screen | a time jump that does not look like a freeze |
| R7-c | client fps and client ms per era stop — the half no server can measure | your final game test |

## The order I would do it in

Dependencies decide this, not preference:

1. **R2-a, R4-b/c** — data repairs. Cheap, unblock the rest, and they are the same defect as your 18 townspeople.
2. **R5-a → R5-b → R3-a** — a famous person must exist as a *record* before they can stand in a house or be
   killed. R5-a is your VIP doubt; R3-a is your "no VIPs / people don't move" doubt. One piece of work.
3. **R1-d → R1-e** — past towns and roads. The largest visible change, and the one your save showed most
   plainly (Athens: ground, no houses).
4. **R4-a** — vehicles that move.
5. **R3-b** — event scenes, on top of R5's timeline work.
6. **R6-a → R6-b** — the paradox wire, last of the big ones because it needs R5's branches to exist.
7. **R7-a, then R1-g and R2-c** — the future is built last because it depends on every other register being right.
8. **R7-c** — your game test, the only judge of the last half of everything.

## What this costs, honestly

These are not one more "step": by the project's own scale they are roughly **25–35 steps**, and the 2026→3000
half is the largest block, because it must be *invented consistently* rather than looked up. Two of the seven
can only be finished by you, in a game — **R7-c** (fps and client ms) and the final judgement of **R1-g**
(does 3000 AD look like a place).

## Plainly

The project is not "nearly done with a few bugs". It is a **complete frame with three of seven requirements
substantially filled**: the history data (R2) is genuinely far along, and the land and money are real. What is
missing is what you keep noticing in the world itself — **people with purpose (R3), consequences (R5), moving
things (R4)**. Those three are the difference between an excellent historical reference you can walk through
and a world that behaves like one.
