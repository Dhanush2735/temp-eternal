# The command order — what to type, in what order

_The same test procedure, expressed as commands. Order matters in five places and each one has bitten
this project already, so they are marked **⚠ ORDER**._ Every command below is real: `ee` commands are
the mod's, `/tpll` is Terra++'s, `/forceload` is vanilla. `(op)` = needs permission level 2.

---

## A. Once per session (before any stop)

```
1   /ee check all                    (op)   the pre-flight gate; ~20 s, answers in the log and chat
2   /ee data paths                          the shipped data is installed
3   /ee civ active                         a non-zero number of civilizations alive this year
4   /ee year                               what year the world thinks it is
5   /ee probe                              Terra++ can say where you are (lat/lon finite)
6   /ee status                             the simulation engine is running
```

**Gate:** step 1 must end `438 passed, 0 failed, 12 known limits` (on a world with people). Any `[FAIL]`
line — stop here, send it. Steps 2–6 catch the harness being broken before you blame a stop.

⚠ **ORDER — never run `ee check all` twice inside ~30 s.** The second call is refused with *"A check is
already running"*, and a refusal that looks like a failure is the classic false alarm.

---

## A2. The one-command version (board 18)

Everything in section B is now a single command:

```
/ee test stop R5          (op)  run stop R5: clock, year, jump, hold, wait, release, then all six reads
/ee test here             (op)  the same at wherever you stand, in the year the world is in
/ee test here -300        (op)  ...and move the clock to 300 BC first (forward only)
/ee test stops            (op)  list the 31 stops
```

It prints the twelve numbered steps, runs steps 7–12 through Minecraft's own dispatcher (so what you
see is exactly what typing them gives), scores the machine half of the judgement
(**PASS** / **FAIL** / **cannot judge**), and appends a row to `ee_stop_tests.tsv` in the world folder
with the year, the coordinates, whether the ground arrived, how long it took, the verdict and the full
card. Everything is also written to the server log, tagged `[EE test]`.

You still do the part that needs a body: **step 8's look** — buildings, dress, crowd, the road under
your feet — and step 10, `/ee villager who`, which needs something standing in front of you.

From the console the command runs route stops with a stand-in actor: the stop's own coordinates are
used for the reading, so nothing depends on a body being there.

---

## B. One route stop — the exact 12 commands (what `/ee test stop` does for you)

This is the per-stop loop, in the only order that works. `R5` is used as the example; the numbers come
from `ERA_ROUTE_PROCEDURE.md`'s answer key.

### B1. Set the year **before** you move

```
1   /ee date -430 1 1         (op)   set the clock to 430 BC, 1 January
2   /ee year                         confirm: it answers 430 BCE
```

⚠ **ORDER — the year first, the teleport second.** `/tpll` lands you in a place, and the place is read
against the clock at the moment you arrive: who rules, what money, which crowd is drawn. Teleport first
and you get one city's answer measured against another city's year.

⚠ **Order of years.** The clock only goes **forward** (`/ee date` refuses to go back, by design). The
route is sorted so it never needs to: R1→R31 climbs in time. If you must go back, `/ee history <year>`
looks at a past year **without moving the clock** — that is the command to use for going backwards.

### B2. Jump, then make sure there is ground

```
3   /tpll 37.9838 23.7275                            Terra++ places you on that point of Earth
4   /execute at @s run forceload add ~-96 ~-96 ~96 ~96   (op) hold the 12×12 chunks around you open
5   /ee scan chunk 8                                 (op) repeat every 3 s until it stops saying "air"
6   /execute at @s run forceload remove ~-96 ~-96 ~96 ~96  release the hold
```

⚠ **ORDER — hold before you wait, release after.** `forceload` tells the server "this area matters,
build it and keep it"; without it the chunk you are standing in can be unloaded again while you watch
the void. Relative coordinates (`~`) with `at @s` are what make this work at any location without
computing anyone's block numbers.

**How to read step 5** (this is the measurement, not a guess):

| `ee scan chunk 8` says | means | do |
|---|---|---|
| `surfaces={minecraft:grass_block=…}` etc. | the ground exists — you can go on | step 7 |
| `surfaces={minecraft:air=…}` only | the chunk has not been built yet | wait another 3 s |
| `ChunkTelemetryScan failed …` | no level / no player position | you are probably running it from console, not as yourself |

**Patience:** a first-time jump to another continent can take 3–5 minutes. **Never** re-run `/tpll` at a
stalled stop — each one queues more generation work and makes it slower.

### B3. Ask the place, then ask its people

```
7   /ee here                     the card: where, what year, who rules, money, what happened, technology
8   /ee probe                    Terra++'s own view: lat, lon, elevation, terrain type, world cover
9   /ee villager nearby 64       the people within 64 blocks: names, civilizations, roles
10  /ee villager who             who the villager you are looking at is, and whose they are
11  /ee building nearby 500      what stands here (if anything) within 500 m
12  /ee civ info <the id from step 7>   that civilization's own record: founded, fell, population
```

You read steps 7–12 against the answer key, in this order: **civilization → money → people → look**.
Worst of the four is the stop's verdict.

### B4. Only when a stop looks wrong — the diagnostic commands

```
/ee civ active                  is the civilization the card named actually alive this year?
/ee civ list                    the ids you can ask about
/ee tech status <civ>           what that people has and has not discovered this year
/ee tech list                   the whole technology ladder with first-known years
/ee trade prices                which money is current where
/ee population get <civ>        the population the world state holds
/ee event list                  events the engine has authored
/ee event pending               events waiting to fire
/ee history <year>              what the history book says about a year (no clock change)
/ee anomaly                     whether the engine thinks something here is impossible
/ee scan chunk 4                a finer sample of the ground
```

Put any of these in the TSV's `your_note` column with the card — they are what turns "it looked wrong"
into a defect I can reproduce.

### B5. Write it down

```
13  screenshot (F2) → rename R05_athens_430bc.png
14  one TSV row: pass / fail / cannot judge + one sentence
```

---

## C. End of a session

```
1   /ee check all          (op)   ~20 s; note the line "end of check: … passed, … failed, … known limits"
2   /ee year                      the year you stopped in (the world saves it)
3   save-all flush                wait for "Saved the game"
4   /stop                         clean shutdown — never kill the window
```

⚠ **ORDER — `save-all flush` before `/stop`,** and never `/ee reset confirm` unless you mean to throw
the world state away.

---

## D. The other test flows, as command order

**The crowd and the people (G6, "does a town feel alive")**
```
/ee villager nearby 64      →  are there people, and are they this culture?
/ee villager virtual-count  →  how many the place holds but is not drawing
walk 50 blocks, stop        →  does the crowd change with the street, or is it one knot?
/ee here                    →  does the card agree with what you can see?
```

**Money (a stop's sharpest single check)**
```
/ee here                    →  the money line for this place and year
/ee trade prices            →  the world's money rows this year
/ee trade prices <civ>      →  the same for the civilization you are standing in
/ee economy treasury <civ>  →  what it holds
```

**What has happened here (events, history)**
```
/ee event list              →  authored events
/ee event pending           →  what is due
/ee history <year>          →  the book's version of the year
/ee codex                   →  the player-facing history book
```

**Buildings and the look of a place**
```
/ee building nearby 500
/ee building info <id>
/ee building history
/ee morph landmark <NAME>   (op) preview a landmark's shape at this spot
```

**Performance (G7's machine half, then the human half)**
```
/ee performance             →  tick time, what the engine costs
/ee ecs benchmark           →  the entity system's own cost
F3 in game                  →  fps and chunk count, for the human half
```

**If something is broken and I need to see it**
```
/ee probe                   →  the Terra++ snapshot at your feet
/ee scan chunk 4            →  the blocks actually present
/ee performance             →  is the server keeping up
/ee debug core              →  (op) the engine's internal state
```

---

## E. The five order mistakes (each one has already caused a false result)

| # | wrong order | what it produces | right order |
|---|---|---|---|
| 1 | `/tpll` then `/ee date` | a stop judged against the previous year's answer | `/ee date` → `/ee year` → `/tpll` |
| 2 | `/tpll` and then reading immediately | "the chunks did not load" | `/tpll` → `forceload add` → `ee scan chunk` until not air → read |
| 3 | `/ee check all` twice quickly | *"A check is already running"* read as a failure | wait for the summary, then run it again |
| 4 | `tpll` from console/RCON without `execute as` | "requires a player" | `/execute as <you> run tpll <lat> <lon>` |
| 5 | `/stop` without `save-all flush` | the year and the people are not written | `save-all flush` → `/stop` |

---

## E2. A coverage gap found while writing this (worth fixing)

The 216-command surface check runs every line of `eternal/ee_command_list.txt` through Minecraft's own
dispatcher. Three commands that exist in the mod are **not in that file**, so the surface check has
never exercised them even though this runbook depends on two of them:

| command | registered in | in `ee_command_list.txt`? |
|---|---|---|
| `/ee check all` | `EeOperationalCheck.node()` | **no** — tested separately by `verify_all.sh`, so it is covered, just not in the list |
| `/ee date <y> <m> <d>` | `EternalEngineCommands` line 1134 | **no** — nothing automated tests it |
| `/ee here` | `EternalEngineCommands` line 193 | **no** — nothing automated tests it |

That is why steps 1 and 7 of the per-stop loop are the two commands with the least automated cover
behind them. Adding the three lines would make the tally **219 commands** and the baselines in
`TEST_PROCEDURE.md` move with it; it is a one-line change to the list plus a re-run of Phase B. Until
then, the runbook exercises them by hand — which is the only cover they have.

---

## F. One-page cheat sheet

```
BEFORE:   /ee check all · /ee data paths · /ee civ active · /ee year · /ee probe
PER STOP: /ee date <y> 1 1 · /ee year
          /tpll <lat> <lon>
          /execute at @s run forceload add ~-96 ~-96 ~96 ~96
          /ee scan chunk 8      (repeat until surfaces are not all air)
          /execute at @s run forceload remove ~-96 ~-96 ~96 ~96
          /ee here · /ee probe · /ee villager nearby 64 · /ee villager who
          /ee building nearby 500 · /ee civ info <id>
          screenshot → R05_athens_430bc.png · TSV row
AFTER:    /ee check all · /ee year · save-all flush · /stop
```

Automated: `python3 era_route_drive.py --pass <rcon> --player <You> --from R5 --to R6 --pause --settle 180`
runs steps 1–6 and 9–12 for you and writes the TSV; you keep step 7–8 (look, screenshot), which is the
only part that cannot be automated.
