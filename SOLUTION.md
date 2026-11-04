# The solution — measured, in five parts

_2026-10-24, after the Geneva correction. Every number below was produced by a probe in `worldfill/probes/`,
not estimated._

## The measurement that reframed everything

The first audits drew each year from a town's **founding year**, so the 20,361 undated towns were invisible to
them. `UndatedAudit` samples only those, at years drawn across 3000 BC – 2025:

```
undated towns, 600 samples
  register could answer  : 189  (31.5%)
  register said "nobody" : 411  (68.5%)

by era (answered / sampled)
  3000–1000 BC   :   6 / 247 =  2.4%
  1000 BC–AD 1   :  31 / 121 = 25.6%
  AD 1–1000      :  64 / 113 = 56.6%
  AD 1000–1500   :  33 /  54 = 61.1%
  AD 1500–1800   :  24 /  32 = 75.0%
  AD 1800–2025   :  31 /  33 = 93.9%
```

**The shape of the gap is now known: it is deepest in deep time, and it is mostly silence, not error.**

## Part 1 — Stop saying "nobody" when the truth is "not recorded" ✅ done this turn

The largest single defect was not missing data. It was **one wrong word**.

Geneva, 121 BC, before the fix:

```
-121  (nobody)      ← a claim. Rome took the town that year.
```

`Source` now splits the two states:

| state | means | shown as |
|---|---|---|
| `REGISTER` / `DOMINION` | recorded | the polity, dated |
| `PACK_CAPITAL` | declared heuristic | the name + "from the pack, nearest capital N km" |
| **`UNKNOWN`** | **inhabited, but the source does not cover it** | **"(not recorded - the source does not cover this place and year)"** |
| `NONE` | genuinely empty — open water, ice | "(nobody)" |

New entry point `WhoRuled.answerForSettlement(...)`: any caller holding a **place** rather than a coordinate
gets `UNKNOWN` instead of a false "nobody". After the change, Geneva:

```
  -500  (not recorded - the source does not cover this place and year)
  -121  (not recorded - the source does not cover this place and year)
    400  Western Roman Empire [395-442]
   1200  Holy Roman Empire [1034-1259]
   1815  Swiss Confederation [1815-2026]
```

**Effect:** the whole class of false "nobody" answers — Geneva −121, Geneva −58, and the 68.5% of undated-town
samples that land on inhabited ground — becomes honest instead of wrong. **Gates: `command_surface` 220/220
PASS, 4 passed 0 failed.**

## Part 2 — Fill the field that can be filled, and rename it honestly

20,356 towns have a blank founding year. Geneva proves some of those are **documented and unfilled**:
Wikipedia gives "an Allobrogian border town… when the Roman Republic took it in 121 BC", plus Caesar's
*Genava*.

- Add `existedBy` to the town schema — **"existed at least by"**, never "founded". A first mention is not a
  birth, and Celtic hillforts have neither.
- Backfill in **priority order**: capitals and towns on the game's own routes first, then towns with a
  population series, then the rest. Every row carries its source.
- Where no source gives even a first mention, the field stays null and the answer is `UNKNOWN` — declared,
  not guessed.

## Part 3 — Use the settlement itself as a witness

Once `existedBy` exists, a town that existed in year Y is evidence that **someone** held that ground, exactly
as Athens was evidence in the pilot. So `WhoRuled` gains a fourth layer, **`SETTLEMENT_PRESENCE`**: register
silent, pack silent, but the town existed by that year ⇒ answer the town, dated, with the source of its
`existedBy`. This is the Athens fix generalised from 133 pack capitals to 30,151 towns.

## Part 4 — Declare the deep time instead of painting it

Before 1000 BC the register answers **2.4%** of cells. No source can close that: Cliopatria is the only
world-scale polity register, and it is thin there.

- The engine answers `UNKNOWN` for those cells (**Part 1 now makes this possible**).
- The gap is published: `verify/coverage_by_era.csv`, one row per era, with the count and the reason.
- The requirement text says so plainly: **"3000 BC – 3000 AD, with pre-1000 BC answered where a source
  exists and declared silent elsewhere."**

This is the difference between a project that is 2.4% done in deep time and one that **lies about it**.

## Part 5 — Make all of it a gate

The audit stays a script until it lives in `/ee check all`. Then:

- **`checkTruthAudit`** — 200 dated towns + 200 undated towns, fails above 2% wrong among *recorded* answers,
  and fails if any inhabited sample reports `NONE` instead of `UNKNOWN`.
- **`checkNoFalseNobody`** — every sample that is a known town must never display "(nobody)".
- **`checkCoverageByEra`** — records the per-era numbers; fails on a **drop**, not on the absolute value, so a
  regression is caught while declared gaps stay declared.

## What each part buys, in rows

| part | attacks | status |
|---|---|---|
| 1 · UNKNOWN vs NONE | the false-emptiness defect, the biggest error class found | **done, gated** |
| 2 · `existedBy` backfill | R2-2 "places that existed" (currently ✅, actually 2/3 undated) | next |
| 3 · settlement as witness | the Athens/Geneva silence class at world scale | after 2 |
| 4 · declared deep time | R2's 3000 BC end, honestly | after 1 |
| 5 · audits as gates | every future regression | ongoing |

## What this solution does not do

It does not make 100% "everything proven". It makes **100% of every answer either recorded, or a named
heuristic, or declared unknown** — no fourth state, and nothing green by eye. That is the reachable target,
and it is now three measured steps away instead of a mystery.
