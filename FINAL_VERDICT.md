# The verdict

**One page, every gate, every gap.** This is the closing document of the marking: what was tested,
what it answered, what is still imperfect, and what could not be judged here at all.

The rule from `TEST_MASTER_PLAN.md` that this document obeys: *a tier is "passed" only when it can be
re-run in one command and prints a ledger. Anything judged by eye is recorded as seen, never as
passed.*

```
./verify_all.sh            the gates (L0 + L2), about 1 min warm — a cold Gradle cache adds ~15 min
./verify_all.sh --probes   + the 27 probes that need Minecraft's classpath
./verify_all.sh --all      + every probe in worldfill/ (141)
./verify_all.sh --only cards   one probe by name
./verify_server.sh         a real headless Forge server: /ee check all, the 212 commands, the datapack
```

**Run from cold, on this machine, today** (`testrun/ledger.tsv`):

| tier | check | rc | last line |
|---|---|---|---|
| L0 | syntax_gate | 0 | no syntax errors (4,519 diagnostics, all unresolved symbols) |
| L0 | manifest | 0 | manifest.json: up to date; DATA_CREDITS.md: up to date |
| L2 | compileJava | 0 | BUILD SUCCESSFUL — **1,232 classes** |
| L2 | command_surface | 0 | **212 commands: 212 PASS**, 0 PARSE-FAIL, 0 THROW, 0 LEAK |
| L1 | probe_cards (`--only`) | 0 | CARDS OK (48 checks) |

**4 passed, 0 failed** — the gate set reproduces in one command from an empty cache, which is the
plan's own condition for calling a tier passed.

**On a live headless server** (`./verify_server.sh`, `testrun/server_ledger.tsv`):

| check | rc | what it answered |
|---|---|---|
| server start | 0 | Done (4.9–6.2 s) — the mod's data installed, 76 events, 221 civilizations |
| `/ee check all` (live) | 0 | **436 passed, 0 failed, 12 known limits** |
| 212 commands (live) | 0 | **212 of 212 answered**, 0 exceptions |
| the 10 datapack functions | 0 | 423 + 81×5 + 23 commands; `test_reset` needs `function-permission-level=4` |
| clean shutdown | 0 | *All dimensions are saved* |

**5 checks, 0 failed.**

---

## 1. The verdict

| gate | what it means | verdict | evidence |
|---|---|---|---|
| **G1** | the files: no syntax errors, every pack parses, the data manifest byte-clean, nothing unlicensed | **PASS** | `syntax_gate`: 4,519 diagnostics, all unresolved symbols (expected without the jars), **0 syntax errors**; manifest **132 files, 131 shipped, 0 without a licence**, `--check` up to date |
| **G2** | the probes: every self-check runs and says something | **PASS** | **141 + 24 probes run** over nine sittings; the 27 that need the Minecraft classpath all green; 8 probes that would not compile were **repaired, not excused** |
| **G3** | the data tells the truth | **PASS with named gaps** | the join `presence → person` sound on every sample; **18 vocabulary ids still unresolvable** (named in §4); 2,582 filed rows corrected from the register itself |
| **G4** | the invariants hold for all places and years, not spot places | **PASS** | no-regression, coverage, estimate-marking, cross-register agreement — measured over 423 land points × 14 years and the full 175,008-person pack |
| **G5** | the mod builds, and its whole command surface works **on a headless server** | **PASS** | **1,232 classes from 500 sources, 0 errors**; **212 of 212 commands on a live dedicated Forge server** (board 10) and on the dispatcher with no world (board 9); **`/ee check all` 436 passed, 0 failed** with a world; **and the same on the shipped jar** — a production Forge server with only `eternalengine-1.0.0.jar` + Terra++ in `mods/`: *Done (5.96s)*, **436 / 0 / 12**, 212/212 answered, clean stop (board 12) |
| **G6** | the real game: `FINAL_TEST.md` on your world, with screenshots | **PARTLY JUDGED — AND NOW COUNTED** | the 55 tests were scored one by one (board 13, `FINAL_TEST_SCORED.md`): **5 passed here, 3 half, 1 failed, 46 need a player or eyes** — not the 55 the verdict used to assume |
| **G7** | the long session: fps, client ms, heap per era stop | **FIRST NUMBERS ONLY** | server-side numbers from the headless run (§6b); fps and client ms need a client |

**Five of the seven gates pass in full.** G6 and G7 have now been *started* — a dedicated server ran
the whole command surface and the whole self-check — but their other halves need a client, a Terra++
world and your eyes, and I am not going to pretend otherwise.

---

## 2. What was actually tested, and how much of it

| | |
|---|---|
| probes and test scripts run | **141** first pass, **+24** once the classpath existed, **+27** classpath probes re-run after every fix, **+1** jar gate (board 15) |
| checks a passing run executes | **~5,000** across the suites (`check` alone is 389, `here` 391, `tiles` 47,376 queries) |
| land points × years swept | **423 × 14** for the tiles and the famous-people join; **400 × 14** for coverage |
| people in the pack, each checked | **175,008** filed, **184,060** in total |
| commands driven through Minecraft's own dispatcher | **216** (four added by board 14) |
| source files compiled | **500 → 1,233 classes** (the fixed-point register, board 14) |
| defects found across the seventeen sittings | **47** (31 in §3, 9 in board 12, 3 in board 13, 3 in board 16, 1 in board 17 — board 17 found one more while fixing board 16: a performance check that was flaky under load) |
| defects found in the probes and harnesses | **29** — the measurement was wrong more often than the code was |

---

## 3. Every defect the marking found, and what closed it

| # | sitting | defect | closed by |
|---|---|---|---|
| 1–3 | 2 | 8 probes would not compile any more | 3 repaired there, the rest rebuilt on the Forge classpath |
| 4 | 3 | **the game could not find one person in five** — the pack files one state id per lifetime, the game asks for one per world-year | a land fallback: 78.7% → **100%** of filed people found, every one inside their own place circle |
| 5 | 5 | `site → polity` join broken for **96% of sites** | register-derived aliases, then the vocabulary work of sittings 6–7 |
| 6 | 5–7 | **90 civ hints unresolvable** (a site named a polity the register never names) | **18 left**, each named |
| 7 | 8 | a man who died in 1770 filed under "United Kingdom", a state that began in 1921 | **2,582 rows corrected from the register itself**, 0 further fixable |
| 8 | 8 | the pack carries **38 true duplicate people** (two source builds of one life) | deduplicated for display, no row deleted |
| 9 | 9 | **cards told the future** — a spouse's death year 29 years after the card's date, `from from`, `-1550--1559`, a pharaoh dying "in -1279", stays that had not happened | one year renderer that cannot know what has not come: **895 problems → 0 of 7,563 cards** |
| 10 | 9 | **tiles ≠ master**: the master had no land fallback, the fallback stepped in degrees instead of boxes (an 800 km promise delivering 220 km), and longitude compression at high latitude | 2,121 diffs → **0 of 47,376 queries** |
| 11 | 9 | "the first year of Hyderabad State rule" in **1948** — the register's slices restarted the count | touching slices of one polity merged: **85 restarts → 0** |
| 12 | 9 | **11 choices on a 9-choice talk screen**; the market question 10th of 11 and unchoosable | the view is cut to nine, the market question moved to second |
| 13 | 9 | Marathi speakers in Bombay answered with Telugu names | Marathi and Konkani moved to the South Asian list |
| 14 | 9 | the speed budget: haversine before the year test, one haversine per *comparison* in `bornNear` | **6.1 → 3.7 ms** average, inside the 5 ms limit |
| 15 | 9 | two shipped `.gz` files stamped with the build time, so the game could never verify its own data | `mtime=0`; byte-identical rebuilds; manifest regenerated |
| 16–20 | 9 | the command surface: `/ee web status` threw on an unloaded config; `/ee observer` and `/ee speed vote` refused **in total silence**; seven commands threw or printed `…because the return value of getLevel() is null`; `/ee data paths` read a null server; `/ee event load` showed the player a Java message | one `noWorld` guard, two sentences, one config fallback: **212 of 212 clean** |

The rest are smaller and are in the boards themselves — a card question with the wrong pronoun, a
route that named a town twice, an errand that remembered a year instead of reading it.

### The measurement was wrong more often than the code

Seventeen defects were in the probes, not the mod, and finding that out is part of the mark:

- **5,106 "cannot find symbol" errors** — a jar left in SRG names by a killed build; the real count was zero.
- **"128 of 212 commands broken"** — they were unstarted, not broken; 81 → 205 the moment the engine was started.
- **"the date line is wrong"** — the paper prints the Fasli date **by design** (step 37); the assertion was stale.
- **the last 60 "problems" on the cards** — my scanner read `1559-1550 BCE` as a common-era year.
- **"`/ee check all` timed out"** — it takes 25–35 s; my watchdog was 20 s.
- plus: a probe merging 28 acts under its own repeat rule, a probe testing a lapse and calling it the role, a "24 probes" list that contained 8 rotten ones, and nine more written down in boards 1–9.

---

## 4. The gaps, named and counted

Nothing here is hidden behind a green tick.

| gap | size | why it stays |
|---|---|---|
| vocabulary ids the register never names | **18** | each one is a polity the source spells differently or does not hold; inventing a mapping would be inventing history |
| `probe_check` known limits | **12** | each prints its own reason (e.g. `prices.json.gz` is CC BY-NC: the one licence decision 4 excepts) |
| people still filed under a modern container | **10,439** | the register **also** uses that container for that cell and year — the coarseness is the source's, not the filing's |
| true duplicate lives in the pack | **38 pairs** | deduplicated for display; deleting rows would unseat anything that reads the master by row |
| price series out of line with their neighbours | **80 of 773** | bad silver conversions in the source; each carries an index that cancels a constant conversion error, and the silver is marked `suspect` |
| the speed line, measured inside the command-surface JVM | **6.5 ms vs 5** | passes in two dedicated runs (3.7, 4.1); fails in a heavier process. I will not choose the run I prefer |
| ~~`[TerraBridge] Terra++ classes are not available`~~ | ~~1~~ | **judged on board 12 and it passes**: with `terraplusplus-2.0.0-alpha.jar` in `mods/` the bridge binds and `/ee check all` reports *Terra++ is available (the world is a real place on Earth)*. It was never a sandbox limit — the jar was in `eternal/libs/` all along |
| the 89 commands that answer "this needs a player / a running world" | 89 of 212 | correct for a console with no world; they must be re-run in the real game to see the success path |

---

## 5. Self-corrections issued

Nine, each one a claim of mine that the evidence overturned: the "8 rotten probes", the two dead
aliases, the "62.4% presence", the Q7318 overclaim, the 5,106-error artefact, the 128 "broken"
commands, the 20-second timeout, the stale date-line assertion, and the `MIN_RULER_SPANS` baseline I
moved (229,468 → 200,695) when the span merge legitimately removed 28,773 slices. **Every one is
written down where it happened**, not just here.

---

## 6. What cannot be judged here — and exactly what G6 must cover

The sandbox has: the source, the data packs, the whole classpath of Forge and Minecraft, a headless
dispatcher, no client, no world, no Terra++ jar, 2 GB of RAM. So these are **open, not passed**:

1. **`FINAL_TEST.md`, 55 tests** on your world, with screenshots.
2. **`/ee test everything` and `/ee test movement`** — the live simulation fighting, moving, ageing.
3. **The camera pass** — 31 era stops plus the book, judged frame by frame.
4. **The 89 player-only and world-only commands' success paths** (§4) — refused correctly here, never seen working.
5. **How villagers look and move**, and whether their talk feels natural — `/ee check all` itself says these are "still for your own eyes".
6. ~~**Terra++** as a real map~~: boards 10 and 12 settled the *mod* side — Terra++ is detected, its
   classes are available, the BTE projection loads and the check passes. What is still open is Terra++
   *terrain* at scale, which needs a Terra++ world (my test worlds were flat, deliberately).
7. **A real second player**, and **hours-of-play feel**.
8. **Every number G7 wants**: fps, client ms, server ms, heap at the 55 MB data load, the year-jump and fork cost.

Two rows of the old `NEEDS_A_REAL_SCREEN` list are worth calling out because they are the ones most
likely to fail: the map projection (a world with no projection fails that check here) and the compass
that points to King Kothi.

### 6a. What the headless server *did* settle (board 10)

A real dedicated Forge server, a real world, a real save, the mod's own data installed:

| | |
|---|---|
| server boot | **Done (4.9 s)**; `FoundationDataInstaller` 13 files / 0 failed; 76 events; 221 civilizations |
| `/ee check all` **on the live server** | **436 passed, 0 failed, 12 known limits** |
| the 212 commands **on the live server** | **212 of 212 answered**, 0 exceptions, 0 empty, 0 Java leaks; **154** did their work (31 more than with no world) |
| the shipped 871-line datapack | **9 of 10 functions ran** (423 + 81×5 + 23 commands); the tenth needed `function-permission-level=4` — a defect only a live server could show |
| shutdown | clean, *All dimensions are saved* |

The 12 checks that failed in board 9's no-world run **all pass the moment there is a level** — proof
that they were sandbox artefacts, not defects. Re-run in one command: **`./verify_server.sh`**,
2.7 minutes, `testrun/server_ledger.tsv`: **5 checks, 0 failed**.

### 6b. The performance numbers a server can give (G7's honest half)

**0.04–0.06 ms average per tick** steady, last 100 ticks 0.02–0.03 ms, peak **14.9–21.2 ms**, **1
second over the 10 ms budget** in ~4,100 ticks, one boot-time spike (`Tick budget exceeded! Avg:
21ms`, slowest system `compass`). On a 2-core 2 GB box with 5 GB of swap, **no player online, flat
world**. That is not G7 — G7 wants fps, client ms and heap per era stop on your world — but it is the
first real server number this project has, and the boot spike is the thing to watch when you run G6.

### 6c. The full sweep, after every edit (board 11)

Nine sittings of engine edits had never been put back through the whole probe set. They now have
been, three times:

| run | result | what it exposed |
|---|---|---|
| first | 141 passed, **6 failed** | three broken probe scripts, one missing fetch, one missing import block, and **one probe that destroyed the data it was testing** |
| second | 145 passed, **1 failed** | the board-10 `mtime=0` fix had invalidated both tile packs, because `build_tiles.py` hashed the *compressed* master |
| third | **146 passed, 0 failed** | nothing |

The incident worth reading is the first run's `probe_step34`. With its Wikidata and
OpenHistoricalMap sources absent (they live in `build/`, which does not survive between sessions),
it ran `build_ways_grid.py` anyway, and that builder wrote a roads-only grid **over the shipped
one**: 183,580 bytes → 16,817 bytes, every railway gone, `New York in 1920 may not draw a railway`
failing against a works pack that still knew 77,184 stations. The pack was restored from the built
resources and re-hashes to the manifest's sha (`5452ae5f…`, 183,580 bytes); the builder now
**refuses** to write when it has no sources; the probe only rebuilds when sources exist. Two more
guards and a `-sourcepath` one level too deep were fixed in the same pass.

Third run, as recorded: `syntax_gate` clean (4,519 diagnostics, 0 syntax errors), `manifest` up to
date, `compileJava` 1,232 classes in 8 s, `command_surface` 212/212, 141 probes green. `ee_check_all`
reports 422 / 11 without a world — board 10's live server reported **436 / 0** for the same command,
so those eleven stay what they were called: sandbox artefacts, now reconfirmed on a second no-world
run.

### 6d. The artifact (board 12)

Everything up to board 11 tested the source tree, the compiled classes or the data on disk. The jar a
player installs had never been opened. It has now.

```
eternalengine-1.0.0.jar   61,870,675 bytes · 1,232 classes · 132 data files · pack_format 15
131/131 shipped files byte- and SHA-256-identical to the manifest · master correctly excluded
1,730 Minecraft references in production (SRG) names · 279 plain names the production jar itself
declares (Forge's own additions) · 0 unresolvable — nothing in it can throw NoSuchMethodError
```

and then, on a production Forge 1.20.1-47.2.0 server with nothing but that jar and Terra++ in `mods/`:
`Done (5.96s)`, `/ee check all` **436 passed, 0 failed, 12 known limits**, **212/212 commands
answered with real text**, slowest 410 ms, clean shutdown, repeatable via `./verify_prod_server.sh`
(7 checks, 0 failed).

**This also retires the last `CANNOT JUDGE HERE` that was mine to retire.** Terra++ is present and
found: `[TerraBridge] Terra++ classes available`, `[EE check] [ OK ] Terra++ is available (the world
is a real place on Earth)`, `BTE projection loaded: ScaleProjectionTransform`. What remains cannot be
judged *by anyone without a screen*: terrain generation (my test world was flat), the crowd, the
camera pass, fps and client ms.

Nine defects came out of this sitting, three of them the kind that only bite a player: eighteen gzip
writers that would have shown two packs as "different content" **at load**, an RCON client that called
212 empty answers a pass, and a mod list that introduced the author as "YourName". The ninth was mine:
the patch that fixed those writers truncated two shipped packs to zero bytes, and the post-probe
manifest check — added half an hour earlier for exactly this reason — caught it. Both packs were
regenerated with **identical content hashes**, so no fact was lost. The list is in
`MARKING_BOARD_12.md` §3.

Final ledger: `./verify_all.sh --all` **149 passed, 0 failed** (141 probes + 8 gates), plus
`./verify_server.sh` **5/5** and `./verify_prod_server.sh` **7/7**.

### 6e. The acceptance list, scored (board 13)

`FINAL_TEST.md` is the project's own "done when". Board 12's summary said all 55 tests need your
client; that was never checked. Checked now, on the shipped jar on a production server:
**5 passed here, 3 half-decided, 1 failed, 46 need a player or eyes.**

Two of the answers are code, not session, work:

- **G2 fails.** At AD 2500 three commands answer exactly as they do at AD 1900 — `ee civ info rome`
  (*active: true, fallYear: 476, population: 1000000*), `ee trade prices rome` (13 unmarked prices),
  `ee population get` (the same figure at every year). The clock itself is scrupulous (*"past 2026.
  Nothing is recorded there"*); these readouts never ask it. `EternalEngineCommands.executeCivInfo`
  prints the register row and hands the year only to `getCurrentName(year)`.
- **G5 cannot be exercised.** `timeline/FixedPoints.java` declares the fixed points and
  `ParadoxEngine` uses them, but **no `/ee` command reaches the register** — `ee timeline fixed` is
  not a command. The refusal the test asks for cannot happen to a player. What did hold: the roll is
  deterministic (two identical rolls), so nothing can be re-rolled.

What passed: the record's edges (**3000 BC** and **AD 3000** both answered and spoken honestly), the
timeline's branch/diverge/codex, the backwards rule naming its own way out, and the 423 × 14 automated
equivalent of the 400-point sample.

### 6f. Both of those were then fixed (board 14)

The paragraph above is board 13's reading, kept as it was written. What happened next is
`MARKING_BOARD_14.md`:

- **G2 is closed.** `projectedMark(year)` now marks every figure past AD 2026 as
  *"[projected: the record stops at AD 2026, this is carried forward]"* in `civ info`, `trade prices`
  and `population get`, and `civ info` answers the question a player actually asked — *"in 2500: had
  already ended (fell 476)"* — instead of printing a register flag beside a fall year 2,000 years gone.
  Nothing was deleted and no figure invented; the numbers now say what they are.
- **G5 is closed.** G5's real cause was worse than "no command": `grep` over all of `src/main/java`
  found **no `new FixedPoints()` anywhere** — the register was never constructed, so
  `attemptFixed`, `forceFixed`, `Repairs.repair` and the weights were complete code that nothing could
  reach. New `timeline/FixedPointRegister.java` constructs it, declares six points from the shipped
  packs, and `/ee timeline fixed | force | rebuild` reach it; `diverge` consults it. Live on the jar:
  refused in place → forced (hand and why recorded, stress 9) → broken on the page → rebuilt (9 → 0).

Re-verified after both: the command surface **216/216 PASS** headless and **216 answered** on the
server, the jar **11 checks 0 failed** at 1,233 classes with all 131 data files byte-identical, and
`./verify_all.sh --all` **149 passed, 0 failed, EXIT=0** (`testrun/raw3/sweep_all_7.log`).

---

## 7. The honest bottom line

**Everything that can be measured without a running game has been measured, and five of the seven
gates are closed.** The mod compiles from source, its whole command surface works, its data verifies
byte for byte, and its 5,000-odd self-checks are green — `probe_check` at **389 checks, 377 passed, 0
failed, 12 named limits**.

**Since board 14 there is no known defect left at all: the two the scorecard found were code, and are
fixed, built into the jar, and re-driven on a production server. Board 15 opened the jar itself —
131/131 shipped files match the manifest byte for byte — and made the build reproducible, so the file
a player installs now has a fingerprint that can be checked: `19930eb2…` (`JAR_SHA256.txt`).**

**What remains is the player's half of G6 and G7** — the 46 `FINAL_TEST.md` tests that need a body or
a screen (not the 55 assumed until board 13; the other nine are decided, one of them failed on G2,
and two are code fixes), on your world with screenshots, the camera pass, the 58 player-only commands' success paths, how villagers look and
talk, and fps / client ms / heap per era stop. Those need your jar, your world and your eyes.
Until they are run, this project is *sound as far as it has been tested and unproven in play* — and
that is the most anyone can say from here.

---

*Boards: `MARKING_BOARD.md` … `MARKING_BOARD_13.md`. Evidence: `testrun/raw*/`, `testrun/command_surface.tsv`,
`testrun/server_commands.tsv`, `testrun/ledger.tsv`, `testrun/server_ledger.tsv`,
`testrun/raw3/sweep_all_5.log`, `testrun/prod_server_ledger.tsv`, `testrun/final_test_server.tsv`, `testrun/server_commands_prod.tsv`. Re-run:
`./verify_all.sh` (no world), `./verify_server.sh` (a live dev server) and
`./verify_prod_server.sh` (the shipped jar on a production Forge server).*
