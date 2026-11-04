# Marking board 13 — the acceptance list, scored

_2026-10-23. Board 12 ended with "55 tests need your client". That was an assumption, not a
finding. This sitting took `FINAL_TEST.md` — the project's own acceptance list — and asked, test by
test, which of the 55 a headless server can decide, then decided those on the shipped jar._

**Result: 5 passed here, 3 half-passed, 1 failed, 46 need a player or eyes.** Two defects fell out,
both of them code rather than session work, and both invisible to every gate that came before.

## 1. What was run

`testrun/final_test_server.py` (new, re-runnable) against the production Forge server carrying
`eternalengine-1.0.0.jar` + Terra++, over RCON. Evidence: `testrun/final_test_server.tsv`,
`testrun/raw3/prod_server_final_test.log`. The full scorecard is `FINAL_TEST_SCORED.md`.

Decided by the server:

| test | what the server said |
|---|---|
| **R32** | `ee date -3000 1 1` → *"back 4500 years, into the record. The packs answer again for -3000, nothing you saw is undone and nobody is un-met: this world forks"* |
| **R33** | `ee date 3000 1 1` → *"forward …, past 2026. Nothing is recorded there, so from now on this world writes its own history"*; `ee history 2500` → 0 events |
| **G4** | `ee timeline diverge hist_rome_1_political player_intervention` → a branch at year 1500; `ee timeline divergences` lists 3; `ee codex` → *Status: Alternate Reality* |
| **F4** (server half) | `ee year set 1900` at AD 2000 → *"Only /ee date moves the date back: /ee date 1900 1 1 goes to 1 January 1900"* — the refusal names the way that works |
| **S1** | already answered by the probes at 423 points × 14 years |
| **P1** | `./verify_all.sh --all` 149 / 0 |

## 2. The failure: three readouts that do not know the year (G2)

Asked at **AD 1900** and at **AD 2500**, these answers are identical:

```
/ee civ info rome      → active: true  fallYear: 476  population: 1000000  treasury: 50000
/ee trade prices rome  → the same 13 commodities at the same silver prices, no mark
/ee population get indus_valley → Population indus_valley = 1000 … at every year tried
```

G2 asks that nothing past 2026 be presented as fact. The clock is scrupulous about saying so every
time the line is crossed; these three commands never ask it. And `active: true` beside `fallYear: 476`
contradicts the record, not only the future: in AD 2500 the mod says Rome is *active* and fell in 476.

`EternalEngineCommands.executeCivInfo` prints `civ.active()`, `civ.population()`, `civ.treasury()`
and gives the year only to `civ.getCurrentName(year)`. `Timeline.markFor(year)` already exists and
`/ee check all` verifies it — the readouts just do not call it. Fix is one file, either way the
project decides: mark them projected past `RECORDED_UNTIL`, or say outright that they report the
register rather than the world on screen.

## 3. The gap behind G5: a rule with no door

`timeline/FixedPoints.java` declares the fixed points — what each is, why it is fixed, what forcing
it costs — and `ParadoxEngine` and `Repairs` use them. **Nothing in `commands/` names the class.**
`ee timeline fixed` → *Incorrect argument for command*.

So the test's *"it refuses and names the safe way out"* cannot happen for a player, and
`ee timeline diverge hist_rome_1_political …` branched a recorded event without asking. The rule is
built and unreachable: a missing door, not a broken engine.

What *did* hold: the roll is deterministic — two identical `ee timeline roll test_event` calls both
returned `roll=0.8038` — so nothing can be re-rolled into a favourable outcome.

## 4. Self-corrections twenty-one and twenty-two

21. **My first driver passed a refused command.** `ee year set 2100` answers *"Only /ee date moves
    the date back … 2100 …"*, and my predicate looked for `2100` in the answer. It found the number in
    the refusal. Three of that run's "PASSED" rows were the command echoing my own input back —
    corrected by making every check assert the property the test names, and by re-reading each row.
22. **A slow command's answer lands on the next one.** `/ee check all` replies about twenty seconds
    after it is asked, on whatever command happens to be running; its summary arrived attached to
    `ee year set 2100` and made the year command look as though it had printed 436 checks. RCON has no
    "later". Slow commands now go last in a run.

The first draft also recorded four false failures (R32c, R33c, F4a, and the shape of the R33 message)
because the *starting year* of each check was not controlled — the clock says "forward … past 2026"
going one way and "back … inside this world's own history" going the other. Both were harness bugs;
both were found by reading the evidence line under each verdict instead of the verdict.

## 5. What this changes in the verdict

The last line of `FINAL_VERDICT.md` said "the 55 `FINAL_TEST.md` tests on your world". The true
number is **46 tests that need you** — plus **one guardrail that is broken (G2)** and **one policy
that has no way to be exercised (G5)**, both of them code, both of them fixed faster than a session.
That is a materially different answer to "how much is left", and it is the first time the acceptance
list has been counted rather than estimated.
