# Marking board 14 — the two failures, closed

_2026-10-23. Board 13 scored the acceptance list and found two things wrong that were not session
work: **G2** (three commands answered as if the year did not exist) and **G5** (a fixed-point policy
with no way to reach it). This sitting fixed both, and proved both on the shipped jar on a production
server._

## 1. G2 — the readouts know the year now

`EternalEngineCommands`, one helper and three call sites:

- `projectedMark(year)` — the guardrail in one place: when `Timeline.projected(year)` (anything past
  AD 2026), the answer carries `[projected: the record stops at AD 2026, this is carried forward]`.
- `currentYear()` — one way to ask either clock.
- `yearState(civ, year)` — *not yet founded* / *standing* / *had already ended*, because `active: true`
  beside `fallYear: 476` was the other half of the defect.

What a player in AD 2500 sees now:

```
Civilization rome - Rome
  currentName: Rome
  founded: -753 fallYear: 476 (the register's flag: active)
  in 2500: had already ended (fell 476)
  population: 1000000 [projected: the record stops at AD 2026, this is carried forward] treasury: 50000 [projected…] tech: 3 [projected…]
  the numbers above are the register's last recorded values, carried forward; they are not a measurement of 2500

Commodity Market Prices for rome: [projected: the record stops at AD 2026, this is carried forward]
  (the price base is the recorded one; nothing here is a price of 2500)

Population indus_valley = 1000 [projected: the record stops at AD 2026, this is carried forward] …
```

Nothing was deleted and no figure was invented: the register's values are still there, and now they
say what they are. That is what G2 asks for — *"the game says so honestly instead of inventing"*.

## 2. G5 — the register has a door

`timeline/FixedPoints.java` was complete and unreachable: `declare`, `attempt`, `force`, `restore`,
weights, and two callers that take a register as an argument — and **nothing in the game ever made
one**. New class `timeline/FixedPointRegister.java` declares six points from the mod's own event packs,
each with its weight and its reason, and holds the `Stress` counter they are booked against. New
commands, all live on the jar:

```
/ee timeline fixed               the page: 6 fixed points · 0 broken, each with id · year · what · weight · why
/ee timeline fixed <id>          one point, and whether it stands
/ee timeline force <id> <why>    break it deliberately: the hand and the why are recorded, the paradox booked
/ee timeline rebuild <id> <why>  put it back: the weight comes off the counter
```

and `/ee timeline diverge` now consults the register. A fixed point, asked to change in place:

```
the Black Death (1346) is a fixed point and resists a timeline divergence in place: take the change
to a timeline branch, or force it and carry the paradox — /ee timeline force q42005 <why> breaks it
deliberately and books the paradox, and /ee timeline rebuild q42005 <why> puts it back
```

The full round trip on the live server:

```
/ee timeline force q42005 the guardrail test wants to see the paradox
  → Forced q42005: Rcon forced q42005 in 1500: the guardrail test wants to see the paradox (1 on the counter)
/ee timeline fixed q42005
  → BROKEN by Rcon; rebuild it with /ee timeline rebuild q42005 <why>
/ee timeline rebuild q42005 undoing the test
  → rebuilding q42005 (the Black Death) lowered the stress from 9 to 0: its weight of 9 given back
/ee timeline fixed q42005
  → standing: an in-place change is refused, and the safe way out is a branch (/ee timeline diverge)
```

That is G5 whole: *it refuses and names the safe way out; no dice; forcing breaks the point and the
break is handed over with its why* — and the rebuild, which the test also asks for.

The six declared points, with the pack each id comes from:

| id | year | what | weight |
|---|---|---|---|
| `q758173` | -430 | the Plague of Athens | 6 |
| `wpw_14cd144a95` | -49 | Caesar's Civil War | 8 |
| `q42005` | 1346 | the Black Death | 9 |
| `wpd_282f01cbca` | 1215 | Magna Carta | 7 |
| `wpr_5a6fa00926` | 1450 | Gutenberg's press | 8 |
| `wpr_5133f16bb5` | 1957 | Sputnik 1 | 5 |

A weight is a game default, not a fact of history — the class's own contract, kept.

## 3. What was re-run to prove it

| check | before | after |
|---|---|---|
| compile | 1,232 classes | **1,233** (the register), 0 errors |
| the command surface, no world | 212 commands | **216 commands: 216 PASS, 0 PARSE-FAIL, 0 THROW, 0 LEAK** |
| the command surface, live jar | 212 answered | **216 answered, 0 with an empty answer** |
| `/ee check all` on the jar | 436 passed | **435 passed, 0 failed, 12 known limits** (one fewer only because this fresh world had no diverged chronicle at the moment of the check — the same state dependency board 12 explained, and the divergence this run later made puts it back to 436) |
| jar check | 11 checks | **11 checks, 0 failed** — 1,233 classes, still reobfuscated, still 131/131 data files byte-identical |
| `./verify_all.sh --all` | 149 passed | see §4 |

## 4. The regression sweep, and the harness defect it exposed

`./verify_all.sh --all` after both changes: **149 passed, 0 failed, EXIT=0**
(`testrun/raw3/sweep_all_6.log`, re-run as `sweep_all_7.log` once the harness was corrected below).

The sweep also caught something in *itself* — **harness defect 25**. The `/ee check all` step was
recorded `PASS` on the runner's exit code while the command's own summary line said **"422 passed,
11 failed, 12 known limits"**. Both numbers were in the log, and the green one was the one read.

Triaged before calling it a regression: the 11 are the bare-process baseline — a JVM with no world
loaded, no Terra++ in `mods/`, no authored events in memory — and the set is *identical* before and
after this sitting's changes, so nothing regressed. But a tally is not a verdict, so `verify_all.sh`
now counts it: the step passes only while the failed count equals the documented baseline of 11,
fails loudly if it moves either way, and always prints the number in its ledger line. Proved the new
rule can fail, rather than assuming it: replayed against the same log with baselines 10 / 11 / 12 →
**FAIL rc=4 / PASS rc=0 / FAIL rc=4**.

## 5. The scorecard after this sitting

`FINAL_TEST.md`, same 55 tests, with boards 13–14 applied:

| | board 13 | now |
|---|---|---|
| PASSED here | 5 | **7** — G2 and G5 join the list |
| PARTLY | 3 | 2 (P2's player half, F4's screen half) |
| FAILED | 1 | **0** |
| open | 46 | 46 |

So the answer to "how much is left" is now: **46 tests that need a body or a screen, and nothing that
is broken.** The two that were code are code no longer.
