# Marking board 31 — R2-6 measured, R2-7 declared: the news has no days in it

_2026-10-24. Two rows that both said "partly" are now measured. One is close to done; the other turns out to be
unbuildable from its own data._

## R2-6 · a card for every town in the test set — **measured, 3 of 4 dimensions at 100%**

The row had no test set, so the first job was to define one that cannot be tuned to flatter the result:
**50 towns drawn from the town register with a fixed seed (606060)**, year drawn inside each town's life. Rows:
`testrun/verify/cards_test_set.csv`.

```
test set                          : 50 towns
towns with a place card           : 50  (100.0%)
towns with a ruler card           : 50  (100.0%)     <- measured with the layered ruler handed in
towns with a famous-people card   : 50  (100.0%)
towns with a news card            :  0  ( 0.0%)     <- see below
questions on cards                : 209
  answered in words               : 209  (100.0%)
```

**One number was my own probe's fault and one is real.**

- The **ruler card first measured 0/50** because `HistoricalPresence.nobody(...)` hands the card builder no
  ruler. I rebuilt the Result with the ruler the layered answer produces, and it measures 50/50. A zero from an
  empty input is not a gap, and it would have been dishonest to report it as one.
- The **news card is a real gap**: `LocalCards.build` **never sets `newsCard`**. It is supplied by the in-game
  pack/talk path instead, so the card builder on its own cannot produce one.

### The news data exists — the wiring does not

I indexed all thirteen event files:

```
usable events with a place and a year : 129,232
test towns with an event inside its own radius (+/-2 years) : 34 of 50  (68%)
test towns within 100 km of one                            : 37 of 50  (74%)
```

So the news card is **a wiring job, not a data gap**. Rows: `testrun/verify/news_coverage.csv`, one line per
test town naming the event that would fill its card (e.g. Otaru 1929 → *Tsunami at Sapporo, 1928*).

**R2-6 stays open, with a named, cheap next step:** `R2-e1` - set `newsCard` inside `LocalCards.build` from the
event index. Expected result: 34/50 at the same thresholds, and the 16 without an event stay honestly silent.

## R2-7 · news by the day — **blocked by its own data**

The row asks for "50 place-days across 10 regions". Before building anything I checked whether the data has a
**day** in it:

```
deccan_events.json.gz              248 rows   day-ish fields: NONE
disaster_supplement.json.gz         79 rows   day-ish fields: NONE
events.json                         83 rows   day-ish fields: NONE
events_hazards.json.gz          26,997 rows   day-ish fields: NONE
events_nature.json.gz            1,844 rows   day-ish fields: NONE
events_storms.json.gz            5,884 rows   day-ish fields: NONE
events_ucdp.json.gz             28,639 rows   day-ish fields: NONE
events_wars.json.gz              2,397 rows   day-ish fields: NONE
events_wikidata_more.json.gz     6,040 rows   day-ish fields: NONE
events_wikipedia.json.gz        19,364 rows   day-ish fields: NONE
events_wikipedia_decades          1,763 rows   day-ish fields: NONE
events_wikipedia_regional        21,907 rows   day-ish fields: NONE
events_world.json.gz            13,987 rows   day-ish fields: NONE
```

**Not one of 129,232 events carries a date, month or day.** Every row is `start`/`end` **years**.

So "news by the day" **cannot be built from these sources** — the honest state is not "partly done", it is
**declared**: the requirement needs a day-level source (a dated incident register, the full UCDP GED with its
dates, or period newspapers) before the first place-day can be produced. Writing a day-generator that invents
"MARCH 14" over a year-granular record would be exactly the kind of green-by-eye this project forbids.

**Two ways it can move:**
1. **Bring a dated source in** (UCDP GED carries exact dates; this copy dropped them), then build 50 place-days
   across 10 regions.
2. **Change the row's words** to "news by the year" — which the data *does* support today (34/50 towns, 10+
   regions) — and keep "by the day" as a declared future.

That is the user's call, not mine: the requirement text is theirs.

## Gates

No source change this turn except the two matrix rows and the probe files, so the tree is as last gated:

```
compileJava    : 1,248 classes
command_surface: 220/220 PASS
/ee check all  : 426 passed, 12 failed (baseline unchanged)
manifest       : up to date
```

## R2 after this turn

| row | state |
|---|---|
| R2-1 … R2-5, R2-9, R2-11, R2-12a, R2-12b, R2-8 | ✅ **11 closed** |
| **R2-6 cards** | **measured**: place / ruler / famous **100%** on 50 towns, 209/209 answers; news card **needs wiring** (data ready for 68%) |
| **R2-7 news by the day** | **declared blocked**: 0 of 129,232 events carry a day |
| R2-12 correct answers | 161 real cases queued (114 overlord + 47 smaller) |

**R2: 11 of 14 rows closed, and the three left are now each pinned to a named, sized task** instead of
"partly": wire the news card (small), bring a dated source (external), hand-check 161 polities (grinding).
