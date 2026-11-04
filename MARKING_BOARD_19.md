# Marking board 19 — R2-a: the vocabulary ids that resolve to nothing

_2026-10-24. First step actually implemented under `COMPLETION_PLAN.md`. Requirement 2, step R2-a._

## What was wrong, exactly

The marking turn recorded **"18 vocabulary ids still unresolvable"**. I re-derived the number from the
data instead of trusting it, and found the gap is **two different defects wearing one number**:

| kind | count | what it is |
|---|---|---|
| a missing alias | **10** | the ruler register already holds a polity whose slug is *exactly* the hint (`nepal`, `carthage`, `assyria`, `kalinga`, `teotihuacan`, `anuradhapura`, `mali_empire`, `songhai_empire`, `french_india`, `jaunpur_sultanate`). `CivHints` simply had no row for them. **Pure bug, no history involved.** |
| a missing source | **18** | `ahom, amber, bhati, bhopal_state, bundela, dogra, holkar, ikshvaku, kandy, kolathiri, ladakh, manipur, marwar, mewar, somavamshi, tomara, travancore, zamorin` — all real polities, none of them in Cliopatria v0.2.1, the register's only source. **No alias can be honest here: an alias claims two names mean one polity, and there is nothing on the other side to mean.** |

How the 10 were found, with no judgement used: slugify every polity name in `world_rulers.json.gz` with
`RulerRegister.civHintFor`, then look for an exact hit against every hint the sites cite. Ten hits.

## What I changed

1. **`CivHints.ALIASES` +10 rows** — each one a restatement, not a mapping: hint `nepal` → polity `nepal`.
   87 aliases → **97**.
2. **`CivHints.ABSENT_FROM_SOURCE`** — a new declared set holding the 18, each with a one-line reason.
   Declared, not aliased, and not deleted: the hint stays in the data (it is true — Mewar *was* a polity),
   it is simply a gap the source cannot close.
3. **`CivHints.declaredAbsent(hint)`** — so any check can count declarations separately.
4. **`worldfill/probes/VocabularyProbe.java`** — a fourth class in the report. The bar is now
   **zero *undeclared***: a gap we have named is a fact about the source, a gap we have not named is a bug.

## The measurement

```
kind      hints   occurrences   known   aliasable   region   UNKNOWN
site        184         46864      28          86       52         0
border       16            16       1          12        3         0
declared absent from the register's source: 18 id(s), 18 occurrence(s)
PASS - every cited id is known, aliasable, a declared region, or a declared absent polity
```

**Before: 28 distinct ids resolved to nothing (18 + 10). After: 0 undeclared, 18 declared, 10 mapped.**

## The gates, re-run after the change

| gate | result |
|---|---|
| `compileJava` | **BUILD SUCCESSFUL — 1,236 classes** |
| `command_surface` | **220 commands: 220 PASS**, 0 refused, 0 PARSE-FAIL, 0 THROW, 0 TIMEOUT, 0 LEAK |
| `/ee check all` (headless) | **422 passed, 12 failed, 12 known limits** — the 12 failed are the recorded bare-process baseline (no world, no Terra++), unchanged, so no regression |
| `probe_vocabulary` | **PASS — 0 undeclared** |

## What this step did **not** do, and what the 18 actually cost

I did not invent rulers for Mewar or Travancore. To close the 18 honestly needs a second source that
holds them (princely-state and Rajput genealogies), then a polity row each and a year span — a data step,
not a mapping step.

**What the mod does at those 18 sites is unchanged and correct**: `CivHints.resolve` returns empty, and the
caller (`HistoricalPresence.aliveHint`) falls through to the year-aware layers, which answer from whoever
the register says ruled that cell in that year. So this step fixed a *diagnostic* defect, not a wrong
answer — and the honest thing to say is that the 18 were never making a wrong civilization; they were
making an invisible one.

## The bigger thing this step exposed

```
ruler register polity ids     1,567
civilization records in pack    133
```

**1.4% of the polities the register can name have a civilization record** — names, clothes, money, food,
a way of life. That is why a Mewar site can be ruled correctly by year and still put nobody convincing in
the street. **This is the real R2/R3 blocker, and it is bigger than the 18.** It is now step R2-d in
`COMPLETION_PLAN.md`; R2-a's remainder (finding a source for the 18) is R2-a2.

## Verdict of this step

**PASS, and honestly small.** One silent defect made visible and counted, one factual gap closed, ten
free corrections, no regression in any gate. The number that mattered moved from 28 to 0. But the finding
matters more than the fix: **the vocabulary was not the problem — the size of the civilization pack is.**
