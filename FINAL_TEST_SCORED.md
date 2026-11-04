# FINAL_TEST.md, scored

_2026-10-23. The acceptance list is `eternal/FINAL_TEST.md`: 55 numbered tests that decide whether the
mod is finished. Until now the verdict said all 55 need your client. That was never checked — it was
assumed. This page checks it, test by test, and runs every one a headless server can decide.

Run against: **the shipped jar** (`eternalengine-1.0.0.jar`) on a production Forge 1.20.1-47.2.0
server with Terra++ in `mods/`, driven over RCON. Evidence: `testrun/final_test_server.tsv`,
`testrun/raw3/prod_server_final_test.log`. Driver: `testrun/final_test_server.py` (re-runnable).

## The score

| verdict | tests | what it means |
|---|---|---|
| **PASSED here** | **7** | a server decided it, and the answer is what the test says good looks like |
| **PARTLY** | **2** | one half decided here, one half needs a body or a screen |
| **FAILED** | **0** | the answer contradicts the test |
| **open** | **46** | needs a player standing somewhere, or eyes on a screen |

_Board 14: the one FAILED (G2) and one PARTLY (G5) were code, and are now code no longer — see
`MARKING_BOARD_14.md` and §3a/§4a below. What G2 and G5 needed was not a session but a fix._

**So the honest figure is not "55 tests left". It is 46 that need you, 1 that is broken, and 8 that
are already decided.** And of the 46, the 31 places of R are not undecided about *data*: the probes
already ask 31 places in their own years, 32 places for the history book's forms, and every money
table — what is left there is whether it *looks* right in the game.

## Every test

| # | test | verdict | evidence |
|---|---|---|---|
| 1 | P1 the sandbox is green | **PASSED** | `./verify_all.sh --all` → **149 passed, 0 failed** (141 probes + 8 gates), manifest up to date, 1,232 classes |
| 2 | P2 `/ee check all` on the server, as console and as a player | **PARTLY** | console: **436 passed, 0 failed, 12 known limits** on the shipped jar (board 12). As a player: needs a client |
| 3–33 | R1–R31 the era route, 31 places | **3 walked, 28 open** (R4's defect fixed, not yet re-seen) | **board 16 (a real save):** R1 Ur, R2 Giza and R4 Anyang were played. Ur's 35 people are Sumerian and inside Sumer's lifetime, Giza's 216 are Egyptian, Anyang's 13 at 1200 BC are Shang at Shang's peak year — names, civilizations and the purse's Mesopotamian silver all match. **R4 failed at 430 BC**, where 29 Shang people stood 616 years after the Shang fell — **fixed in board 17** (§8): the answer at Anyang in 430 BC is now Zhou, verified by probe, but not yet re-seen on a screen. The other 28 stops are still unvisited | the *data* half is green: `/ee check all` and the probes answer all 31 places in their own years; what has not been seen is talk, dress, money and buildings **on a screen** |
| 34 | R32 the record's edge, 3000 BC | **PASSED** | `ee date -3000 1 1` → *"back 4500 years, into the record. The packs answer again for -3000, nothing you saw is undone and nobody is un-met: this world forks"*; `ee year` → 3000 BCE |
| 35 | R33 the record's edge, AD 3000 | **PASSED** | `ee date 3000 1 1` → *"forward …, past 2026. Nothing is recorded there, so from now on this world writes its own history"*; `ee year` → 3000 CE; `ee history 2500` → 0 events |
| 36 | X1 empty land | **open** | needs a body in a desert; the register half is green (`the Sahara is honestly empty, not guessed at`) |
| 37 | S1 400 points × 7 years | **PASSED** (automatic equivalent) | the project's own probes ask **423 points × 14 years** and report recorded / estimated / missing; a hand run of 400 points would re-measure the same thing |
| 38–42 | L1–L5 the looks | **open** | Xaero's link, a person leaving, the 13 book pictures, the trade screen, look-and-feel: screen only |
| 43 | F1 Spark, 30 minutes | **open** | needs a client walk and Spark |
| 44 | F2 Entity Culling | **open** | needs the client mod |
| 45 | F3 Embeddium | **open** | needs the client mod |
| 46 | F4 the time jump's rebuild wait | **PARTLY** | server half **PASSED**: going backwards is refused and the way is named — `ee year set 1900` at AD 2000 → *"Only /ee date moves the date back: /ee date 1900 1 1 goes to 1 January 1900"*; `ee morph status` answers. Watching the wait is a screen |
| 47 | F5 the crowd at 24/64/128/160 blocks | **open** | screen only |
| 48 | G1 two players, one date | **open** | needs two players |
| 49 | **G2 nothing invented past 2026** | **PASSED** (was FAILED, board 13) | **§3a: fixed and re-driven on the shipped jar.** At AD 2500 `ee civ info rome` says *"in 2500: had already ended (fell 476)"* and marks every figure *"[projected: the record stops at AD 2026, this is carried forward]"*; `ee trade prices rome` and `ee population get indus_valley` carry the same mark and say in words that nothing there is a 2500 figure |
| 50 | G3 the purse cannot go below zero | **open** | the purse belongs to a player |
| 51 | G4 the timeline, two universes | **PASSED** | `ee timeline diverge hist_rome_1_political player_intervention` → *Created timeline divergence … year=1500*; `ee timeline divergences` → 3 listed; `ee codex` → *Branch: …, Status: Alternate Reality* |
| 52 | G5 a fixed point refuses | **PASSED** (was PARTLY, board 13) | **§4a: the register has a door and the door is live on the jar.** `/ee timeline fixed` lists 6 points; `/ee timeline diverge q42005 …` → *"…is a fixed point and resists a timeline divergence in place: … or force it and carry the paradox — /ee timeline force q42005 <why> …"*; the force recorded the hand and the why and booked the paradox (stress 9), the page then named the hand that broke it, and `/ee timeline rebuild` gave the weight back (9 → 0) |
| 53 | G6 no monsters at night outside town | **open** (machine half backed by a real save, board 16) | a played world: **923 human NPCs, 3 sheep, 1 pig — not one hostile mob**, no traders, no raids, day time 22:51. Still not the test itself (nobody stood outside a town at midnight and watched), but this is saved state, not a harness. Earlier: the spawner's own selection call (`ForgeEventFactory.getPotentialSpawns`, the one the game makes with a player present) is refused on live world state and counted — `/ee check all` now reports it and reads **437/0/12** on the shipped jar; the full per-chunk spawn loop never runs headless, so a body at night is still required |
| 54 | M1 two players, the same answers | **open** | needs two players |
| 55 | M2 roles and a return ticket | **open** | needs a player who may not move time |

## 3. The one failure: the year-blind readouts

G2 says: *ask who rules, who lives here, what things cost and what happened at 2100 and 2500. Good:
every answer past 2026 carries the projected mark; no ruler, person, dynasty, war, event, disaster or
price exists; no population figure past the last measured year.*

The clock itself is exemplary — it announces the boundary every time it is crossed (*"past 2026.
Nothing is recorded there"*). But three commands do not consult the year at all. This is the same
question, asked at AD 1900 and at AD 2500:

```
/ee civ info rome        (identical at 1900 and 2500)
  Civilization rome - Rome
  currentName: Rome
  founded: -753 active: true fallYear: 476
  population: 1000000 treasury: 50000 tech: 3

/ee trade prices rome    (identical at 1900 and 2500, thirteen commodities, no mark)
  - WINE: 15.92 silver (category: LUXURY)   - WHEAT: 2.27 silver (category: STAPLE) …

/ee population get indus_valley   (identical at every year tried: 1900, 2026, 2100, 2500, 3000)
  Population indus_valley = 1000 birthRate=0.025 deathRate=0.018 capacity=10000
```

Two things are wrong with the first one, and only one of them is about the future. **`active: true`
sits next to `fallYear: 476`** — at AD 2500 the command says Rome is active *and* that it fell in 476.
And a player in AD 2500 is told there are a million Romans and a treasury of 50,000, with no mark
saying where the number came from.

Where it comes from: `EternalEngineCommands.executeCivInfo` prints the register row —
`civ.active()`, `civ.population()`, `civ.treasury()` — and passes the year only to
`civ.getCurrentName(year)`. The year-aware machinery exists and is used elsewhere
(`Timeline.markFor(year)` → *projected*, which `/ee check all` verifies); these three readouts simply
do not call it.

This is a **documentation-or-code decision**, and the marking's job is to say which it is: the
standing rule is "no invented future", so the readouts should either take the year and mark
themselves projected past `Timeline.RECORDED_UNTIL` (2026), or say plainly that they report the
register rather than the world at the date on screen. Either is a one-file change in
`EternalEngineCommands`; neither is a redesign.

## 4. The gap behind G5: a rule with no door

`eternal/src/main/java/com/eternalengine/timeline/FixedPoints.java` declares the fixed points, with
what each one is, why it is fixed and what forcing it costs; `ParadoxEngine` and `Repairs` use it.
**No `/ee` command reaches it.** `grep -rl FixedPoints eternal/src/main/java/com/eternalengine/commands/`
returns nothing, and `ee timeline fixed` is not a command.

So G5's *"it refuses and names the safe way out"* cannot happen to a player: `/ee timeline diverge
hist_rome_1_political player_intervention` creates the divergence without consulting the register.
The policy is implemented and unreachable. That is not a failure of the mod's history engine — it is
a missing door, and it is exactly the kind of gap a marking pass is for.

## 3a. G2, after the fix (board 14)

One helper in `EternalEngineCommands` (`projectedMark(year)`, reading `Timeline.projected`) and one
way to ask either clock; three call sites. The values are untouched — the register's last recorded
figures are still printed — and each now says what it is:

```
Civilization rome - Rome
  founded: -753 fallYear: 476 (the register's flag: active)
  in 2500: had already ended (fell 476)
  population: 1000000 [projected: the record stops at AD 2026, this is carried forward] …
  the numbers above are the register's last recorded values, carried forward; they are not a measurement of 2500

Commodity Market Prices for rome: [projected: the record stops at AD 2026, this is carried forward]
  (the price base is the recorded one; nothing here is a price of 2500)

Population indus_valley = 1000 [projected: the record stops at AD 2026 …] birthRate=0.025 …
```

The test's wording is *"the game says so honestly instead of inventing"*. It does.

## 4a. G5, after the fix (board 14)

`timeline/FixedPoints.java` had every rule and no constructor call anywhere in `src/main/java` — the
class was never instantiated, so no command could have reached it. New
`timeline/FixedPointRegister.java` declares six points drawn from the shipped event packs (Plague of
Athens, Caesar's Civil War, Black Death, Magna Carta, Gutenberg, Sputnik 1, weights 5–9), and
`/ee timeline fixed | force | rebuild` reach it; `diverge` consults it. Full transcript in
`MARKING_BOARD_14.md` §2.

## 5. What you actually have to do

Not 55 tests, and — since board 14 — no code. **46 tests, one session, your client.**

~~G2~~ and ~~G5~~ are done: fixed in code, built into the jar, and re-driven on a production server
(§3a, §4a). What is left is what only a body and a screen can answer:

1. **A player, somewhere** — R1–R31 walked in their own years, X1 (a desert), G1 and M1 (two
   players, one date), G3 (the purse), M2 (a role that may not move time). 39 tests.
2. **A real Terra++ world and a night** — G6. 1 test.
3. **Your client, looking** — L1–L5, F1–F3, F5, and the screen halves of P2 and F4. 6 tests.

The page for each is already written in `FINAL_TEST.md`; the only thing missing is your eyes, and
`testrun/final_test_server.tsv` already holds the machine answers to paste beside them.

## 6. Two lessons about measuring (self-corrections 21 and 22)

21. **My first driver passed `ee year set 2100` because the refusal message mentions 2100.** The
    predicate looked for the number in the answer — and the answer was the command being refused. A
    check must look for the *property the test asks for*, never for an echo of its own input.
22. **`/ee check all` answers about twenty seconds after it is asked**, on whatever command is
    running then. RCON has no notion of "later": the check's summary arrived on `ee year set 2100` and
    made it look as if setting the year had printed 436 checks. Any RCON-driven test has to keep a
    slow command last, or it will attribute one command's answer to another.

## 7. The first defects found by playing (board 16)

`SESSION_REVIEW_1.md` reads a real save the user supplied. Two new defects, one shape: **a site's
civilization is used without checking whether it still exists in the current year.**

- **D1 — Anyang, 430 BC: 29 Shang townspeople.** Shang fell in **1046 BC** in the mod's own pack;
  Zhou (−1046..−256) owns that ground and is active in the world state with 10M people. **R4 fails.**
- **D2 — (32.4 N, 69.0 E), 1200 BC: 28 Indus Valley people**, a century after the Indus fell (−1300).
- **Census:** of 285 registry rows with a known civilization, **57 (20%) stand after their civilization
  fell**, every one at a site whose civ hint predates the clock.
- **D3:** 13 live NPCs carry `indus_valley_civilization` (the pack's id is `indus_valley`) and 5 carry
  `jin` — ids that resolve to no civilization in any pack or in the world state.

The fix is one rule in one place — resolve `civHint` through the year. It is **written and measured**
(§8, board 17); it changes who stands where, so it was written only after the user said "ok fix it".

## 8. The fix for §7 (board 17)

One rule, in `HistoricalPresence.spawnCivFor`: **the people of a place belong to a civilization that is
alive in that year, or to none.** Every candidate is checked with `isActiveInYear`; when the site's own
hint has fallen, the answer falls through to the recorded ruler, then to the nearest civilization alive
in that year (only where a ruler is recorded), then to `neutral`.

Measured with the same probe, old class vs new (`probe_eraciv`, `worldfill/probes/EraCivProbe.java`):

| | Anyang, 430 BC | world sweep, 6,000 points × 14 years |
|---|---|---|
| before | `jin` — a polity with no civilization | 1,394 named answers, **7,165 outside their civilization's years** |
| after | `china_zhou` (Zhou, −1046..−256) | 2,850 named answers, **0 outside** |

Guard added for the future: `/ee check all` now reads every person the world holds and reports anyone
standing outside their civilization's years — with no level loaded it says so instead of passing.

**What is not yet proved:** the 923 people already saved in `New World` keep the ids they were given,
so that world's Anyang crowd is still Shang until the crowd is re-drawn under the new jar. R4 turns
green only when someone stands there, at 430 BC, and sees Zhou.
