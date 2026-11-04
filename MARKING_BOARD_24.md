# Marking board 24 — cycle 1 of the loop: the first truth audit, and what it caught

_2026-10-24. The first cycle of measure → fix → re-measure. This is the first time in the project that an
answer was checked against a **source** rather than against the mod's own registers._

## The measurement (S1, pilot: 12 samples, 4 continents, 2,500 years)

`worldfill/probes/TruthAuditProbe.java` asks who ruled a place in a year, then each answer is checked
against a source.

```
place              year   register's answer                verdict
Athens             -430   (nobody)                         WRONG - Athens was a polity
Rome                117   Roman Empire             [−31–394]   right
Baghdad             900   Abbasid Caliphate      [751–946]   right
Delhi              1300   Khalji Dynasty        [1294–1325]   right
Cusco              1500   Inca Empire           [1450–1539]   right
London             1700   Kingdom of England    [1662–1708]   right (England to 1707)
Kyoto              1000   Heian Japan            [793–1187]   right
Timbuktu           1400   Mali Empire           [1236–1467]   right - verified: Mali annexed 1324, Tuareg took 1433
Tenochtitlan       1500   Aztec Triple Alliance [1475–1520]   right
Ayutthaya          1600   Ayutthaya Kingdom     [1588–1768]   right
Mohenjo-daro      -2500   Indus Valley Civ.  [−2500–−1701]     right (mature phase 2600–1900 BC)
open Pacific       1500   (nobody)                         right - and refusing is the expensive-correct answer
```

**11 of 12 right, 1 wrong = 8.3%** — precisely at the threshold I wrote down before running it ("more than
1 in 12 wrong ⇒ freeze and re-plan"). One failure, with its cause visible.

## The cause, and why it mattered

The register's only source (Cliopatria) **does not cover the classical Greek poleis**, so at Athens it said
`(nobody)`. But the mod's own pack carries:

```
athens   Athens   −800 to −338   capital 37.9838, 23.7275
```

**The project's own R5 route stops at Athens in 430 BC** — the exact cell where the layered answer said
"nobody ruled here". A register's silence had been read as an answer.

## The fix (R2-a3): `WhoRuled`, an answer with its provenance attached

`civilization/WhoRuled.java` asks the register first and — **only when the register is silent** — asks the
pack: the nearest civilization capital within `PACK_CAPITAL_KM = 50` whose years include the year. Every
answer carries its `Source`:

| source | meaning | trusting it |
|---|---|---|
| `REGISTER` | a recorded polity held that cell that year | recorded |
| `PACK_CAPITAL` | register silent; a capital within 50 km whose years include the year | a **declared heuristic** — a capital 40 km away does not prove it held that exact cell, and the type says so |
| `NONE` | neither | honestly empty |

The register still wins whenever it speaks, so **no existing answer changed**.

## The re-measurement

```
Athens   -430   Athens   <- REGISTER SILENT, pack answered
answered: 11, empty: 1 of 12       wrong: 0 of 12 (0%)
```

**8.3% → 0%.** The empty one is open ocean, and refusing there is correct.

## The gates

| gate | result |
|---|---|
| cold `compileJava` | **BUILD SUCCESSFUL** — the first attempt died (Gradle daemon killed on a cold cache at 2 GB), swap + `-Xmx1200m` fixed it; **1,245 classes** |
| `command_surface` | **220 commands: 220 PASS**, 0 refused, 0 PARSE-FAIL, 0 THROW, 0 TIMEOUT, 0 LEAK |
| `/ee check all` | **425 passed**, **12 failed = the recorded baseline, unchanged** |
| `manifest` | up to date |
| `probe_truth_audit` | **0 wrong of 12** |

## What this cycle proves about the method

1. **The truth audit was worth running before any building.** It found a wrong answer at the one place the
   project's own route visits, in a defect class no gate had ever covered.
2. **A 12-sample pilot found it; a 200-sample audit may find more.** The pilot is not the requirement's bar
   (200 samples, < 1 in 50); it is the reason to believe the bar is reachable.
3. **The fix took one step and changed no existing answer** — because the layering was already there and only
   the *silence* was being misread.
4. **The cold-build failure is a real schedule fact**: a session that begins with no Gradle cache pays a
   failed daemon plus a retry, ~8 minutes, before the first compile.

## The loop this establishes

Each cycle is: **measure a row → find the worst answer → fix it → re-measure → board**, until every row in
`COMPLETE_100.md` has an artifact. The cycle is the plan; the phases are just the order of cycles.

**Cycle 1 closed:** R2-12's method (the audit exists and runs) and R2-a3 (the silence defect).
**Still open:** R2-12 at full size (200 samples), and every requirement row that needs building.

## Verdict of this cycle

**PASS, and it is the most useful step of the session** — not because it added anything, but because it is
the first time the project checked whether it is *right* instead of whether it is *resolvable*. It was wrong
once in twelve. Now it is wrong zero times in twelve, and the fix says out loud when it is guessing.
