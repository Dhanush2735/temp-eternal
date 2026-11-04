# Marking board 32 — R2-6 closed: the news card, and a regression the gate caught

_2026-10-24. R2-e1: wire the news card into the headless card builder. It went from **0 of 50 towns to 35 of 50**,
and in the process **I broke an existing guarantee and the gate caught it** — which is the whole point of having
one._

## What was built

`knowledge/NewsIndex.java` — an index of the thirteen shipped event files.

```
events indexed : 129,232        (identical to the independent Python count: a cross-check, not a hope)
```

`near(lat, lon, year)` returns the nearest event that is news at a place: inside the event's own
`radiusKm + 50 km`, and **after it has begun**, up to two years after it ends. `LocalCards.build` now uses it to
set `newsCard` and add the card, which it never did before — the reason the test set measured 0/50.

## The measured result

| card | before this turn | after |
|---|---|---|
| place | 50/50 | 50/50 |
| ruler | 50/50 | 50/50 |
| famous people | 50/50 | 50/50 |
| **news** | **0/50** | **35/50 (70%)** |
| questions answered in words | 209/209 | **244/244** |

The 15 towns without a news card have **no dated event within 50 km of them in that year**; they are named, one
row each, in `verify/cards_test_set.csv`. Silence there is the correct answer, not a failure.

## The defect my own wiring introduced, and how it was caught

First attempt: I let the new card **take over** `newsCard`. The gate went from 12 failures to **13**:

```
[FAIL] the news names an event with its own card (Marignano 1515, Hurricane Katrina 2005, Typhoon Haiyan 2013) ? 0 of 3
```

The existing event path produces a news card that **links to the event's own card** (`[[ec_...]]`), and a check
pins that it does. My card was plain text and displaced it. **The layering rule from the ruler work applies here
too: the specific, existing answer keeps priority; the new index only fills the gap where nothing existed.**

After the fix:

```
/ee check all : 427 passed, 12 failed  (was 426 / 12; the +1 is the new news check)
```

## The guard, in both directions

`checkNewsTellsOnlyWhatHasHappened` pins two source-read cases:

- **Otaru 1929** → must hear of the **tsunami at Sapporo (1928–1929)** — news that has happened;
- **Legnica 1619** → must **not** be told the plague at Wrocław, which starts in **1620** — news that has not.

That second one is a real bug I found while wiring: the first version offered *"Plague outbreak in Wroclaw,
1620-1621"* as today's news in 1619. It cost 3 of the 35 (38 → 35) to fix, and the lower number is the true one.

## R2 scoreboard

| row | state |
|---|---|
| R2-1 … R2-5, R2-9, R2-11, R2-12a, R2-12b, R2-8, **R2-6** | ✅ **12 of 14** |
| **R2-7 news by the day** | **declared blocked** — 0 of 129,232 events carries a day |
| **R2-12 correct answers** | **161 polities** to hand-check (114 overlord + 47 smaller) |

**Requirement rows closed overall: 17 of 55** (was 16).

## What R2 needs now

1. **R2-12, the 161** — the only row that is pure grinding, and the one that decides whether R2's answers can be
   called right. Thirty at a time with the Brzeg recipe.
2. **R2-7** — needs either a dated source (UCDP GED with its dates) or the requirement's words changed to "by the
   year", which the data does support today (35/50 towns across 10+ regions).

Neither is blocked on anything but decision and time — and the first one is the honest core of the requirement.
