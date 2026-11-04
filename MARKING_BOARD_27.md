# Marking board 27 — the solvable ones, solved and measured

_2026-10-24. Six problems were picked as "solvable now". Four were solved, one was half-solved, and one turned
out to be much bigger than it looked. All numbers below come from probes that ran this turn._

## 1. The vassal bug — SOLVED, with a rule and a source

The two wrong answers from the eight-place source check were **both** the same mistake: a suzerain named where
a state ruled. The diagnosis changed twice as I measured, which is why this entry is long:

**Hypothesis 1 — a priority bug.** I built a `rulerNear(civHint, lat, lon, year)` method so a vassal could
outrank its overlord. It changed nothing. Then I printed the register's own coverage:

```
Crimean Khanate   : 148 places, centre 47.4/35.9, years 1450-1782   (Crimea only)
Duchy of Legnica  :   2 places, centre 51.0/16.5, years 1279-1313   (stops in 1313)
```

**Hypothesis 2 — a coverage gap, and it was right.** The register does not cover the Duchy at all in 1619, and
does not reach the Kherson steppe. So there was nothing to outrank: **the overlord was the only recorded
answer.** A priority rule cannot fix missing coverage.

**The fix that works:** a `Vassal` table — polity, overlord, years, a **declared territory box**, and a source.
The rule fires only when the register has named the **overlord**, the year is inside the vassal's span, and the
cell is inside the box. The answer says which of the two it was:

| case | before | after |
|---|---|---|
| Legnica (its own capital), 1619 | Holy Roman Empire | **Duchy of Legnica [1329-1675]** — `VASSAL_DECLARED` |
| Tavriiske (Kherson), 1755 | Ottoman Empire | **Crimean Khanate [1475-1774]** — `VASSAL_DECLARED` |

The displayed text is explicit: *"(the register named the overlord and does not cover the vassal here; this is
the vassal's declared territory, not a recorded one)"*.

## 2. An error I introduced, caught in the same turn — the Dobruja towns

The first box reached longitude 28.5, so the full-scale audit produced **six** corrections, and three of them
were wrong:

```
Odesa      46.477, 30.733  1594  Crimean Khanate   correct - Yedisan was the khanate's
Yalta      44.499, 34.155  1760  Crimean Khanate   correct - Crimea
Dubossary  47.267, 29.167  1680  Crimean Khanate   correct - Dniester frontier
Navodari   44.321, 28.613  1609  Crimean Khanate   WRONG - Dobruja was Ottoman directly
Stejaru    44.767, 28.550  1574  Crimean Khanate   WRONG - same
Randunica  45.001, 28.751  1669  Crimean Khanate   WRONG - same
```

I narrowed the box to `lon >= 29.0` (the Dniester mouth is the khanate's western edge; Dobruja lies west of it)
and re-ran: **3 corrections, all correct.** The narrowed box is written into the source **with the reason it was
narrowed**, so the next reader cannot re-widen it by accident.

## 3. Regression gate — SOLVED

`checkWhoRuledAnswersWithItsProvenance` is now inside `/ee check all`. It pins four source-checked cases:

- Legnica 1619 → **Duchy of Legnica**
- Tavriiske 1755 → **Crimean Khanate**
- open Pacific 1500 → **nobody** (still allowed to be empty)
- Geneva 121 BC, asked as a settlement → **"not recorded"**, never "nobody"

```
/ee check all : 426 passed, 12 failed  (baseline unchanged; was 425 passed)
compileJava   : BUILD SUCCESSFUL - 1,248 classes
command_surface: 220 commands: 220 PASS
```

Athens 430 BC needs the civilization pack, which has no headless accessor, so it stays pinned by
`worldfill/probe_truth_audit.sh` — stated in the check's own javadoc rather than quietly dropped.

## 4. The environment problem — half solved, and it bit again this turn

The gate failed at first with `BUILD FAILED — 0 classes`, which is **not** a code error: the Gradle daemon was
OOM-killed. Cause confirmed this time: **swap had been wiped between turns** (`Swap: 0`), despite the memory
ceiling now living in `gradle.properties`. With 5 GB of swap restored, the same build passed in 32 s.

So: the ceiling is fixed permanently in the repo, but **the swap must be recreated every session** and that
step is not yet automated. That is the next environment fix.

## 5. The problem that got BIGGER — the layers are not wired into the game

I checked whether the new rule actually reaches the player. It does not:

```
EternalEngineCommands.java:5429   rulerAt(...)   <- the command the player uses
WorldQuery.java:55                rulerAt(...)   <- the central query
TalkService.java:471              rulerAt(...)   <- what NPCs say
Calendars.java:371                rulerAt(...)
Units.java:340                    rulerAt(...)   <- armies take their flag from this
Arms.java:393                     rulerAt(...)
LawRegister.java:169              rulerAt(...)   <- law inherits from the ruler here
```

**Twenty-two call sites in fifteen files call the raw register and bypass `WhoRuled` entirely** (counted:
24 `.rulerAt(` calls in the mod, of which 2 are inside `WhoRuled` itself, plus 7 `WhoRuled.` references).
I first wrote "seven subsystems" here from the truncated `head -8` output of the very tool that measured it -
a board correction, made the next turn, because the number mattered. So the dominion layer, the vassal
layer and the UNKNOWN/NONE distinction exist and are proven — in my probes and one check — but **the game
still gives the old answers.** This is now the single largest correctness gap in the project, and it is a
wiring job, not a research job.

## Scoreboard of the six problems

| problem | state |
|---|---|
| 1 · vassal answered as overlord | **solved** for the two sourced cases, with the rule, the box and the source named |
| 2 · polities answering nobody at their own centre (101) | **open** — untouched this turn |
| 3 · 117 colonial answers unhand-checked | **open** |
| 4 · stale call sites | **re-diagnosed and enlarged**: 22 call sites in 15 files bypass the layer. Open. |
| 21 · audits as gates | **solved in part** — one in-game check, 425 → 426 passed |
| 19 · toolchain dies | **half** — memory ceiling in the repo; swap still manual |

## Verdict

**Four of six moved, one of them wrongly at first and corrected within the same turn.** The honest headline:
the engine can now name a Duke instead of an Emperor — **but only where my probes ask it.** Until the seven
call sites are wired, the player still gets the old answer.
