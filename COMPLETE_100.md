# The 100% plan

_2026-10-24. Answers "how would you complete the requirements 100%?" — and it is a different document from
`HOW_TO_FINISH.md`, because 100% needs a **traceability matrix**: every one of the **53 rows** in
`worldfill/REQUIREMENTS.md` mapped to a step, an owner and a file that proves it. Nothing summarised away._

---

## Part 0 — Four definitions have to be fixed first, or 100% is unmeasurable

Three of your seven requirements, as worded, cannot be marked complete because they are not measurable.
Every one of these is a **sentence change you have to agree to**, not a code change:

| # | as worded | cannot be measured because | the measurable form |
|---|---|---|---|
| 1 | "1:1 replica of Earth" | the world is not 1:1 and cannot be: 1 km = **1,036 blocks at Hyderabad, 1,294 at Beijing**; north turned 29°; Everest is 1,969 blocks | **near 1:1, distortion measured and documented** — 435 places already round-trip within 1 m |
| 2 | "replicate each and every history, 3000 BC to 3000 AD" | after today there is no history to replicate; before today no source records everything | **every answer marked recorded / estimated / projected; fewer than 1 in 50 wrong on 200 random samples** |
| 3 | "the project contains everything as IRL" | "everything" is unbounded | **every row of this matrix has an artifact** — 53 rows, each with a file |
| 4 | "improve the performance" | "improve" is comparative, not a bar | **no tick > 250 ms, average < 50 ms, no freeze > 1 s in your game** |

**This is the first thing I need from you: "yes" to those four, or your own wording.** Without it, 100% is a
feeling, not a certificate.

---

## Part 1 — The three lanes, and the four things I cannot do here

100% needs work in three lanes. Only one is mine.

| lane | who | what only they can do |
|---|---|---|
| **M** — mine | this sandbox, no client, no network | data, code, probes, headless servers, checks, saves read off disk |
| **Y** — yours | your machine, with a client | see the world, judge a scene, measure fps, trigger the rupture, walk the route |
| **J** — joint | both | the mod↔Terra++ links; anything that must be *shown* after being built |

### The four prerequisites (P1–P4)

| # | prerequisite | lane | blocks | fallback if it never happens |
|---|---|---|---|---|
| **P1** | **A client with the jar** — one session, jar installed, `New World` opened | Y | R6-1, R6-4, R6-5, R7-6, all visual checks in R1/R3/R5 | those rows stay **declared open**, honestly counted; 100% is unreachable |
| **P2** | **Terra++ branch API** — its timeline branches reachable from the mod, plus a way to trigger a time jump from code | J | R1-2, R1-3, R5-5, R6-1 | the mod can *name* a branch and cannot *show* it; R5-5/R6 declare open |
| ~~**P3**~~ | ~~a second source for the 18~~ | **DONE board 23** | nothing — the blocker is gone | — |
| **P4** | **Your sign-off on Part 0** | Y | the definition of "done" itself | no certificate is possible |

**P3 is closed (board 23). P1 and P2 are the two that decide whether 100% is reachable at all.** P2 is partly inside Terra++ — I can
write the mod side and prove it compiles and answers, but I cannot make Terra++ render a different branch.

---

## Part 2 — The traceability matrix: 53 rows, 36 steps

Legend: **✅ done** (artifact exists) · **M** mine · **Y** yours · **J** joint · **⛔ unreachable as worded**
Artiffact = the file that proves it.

### Requirement 1 — Earth, 3000 BC → 3000 AD (7 rows)

| row | today | step | owner | artifact |
|---|---|---|---|---|
| R1-1 the land 1:1 | done by Terra++ | **B0** verify in 10 test places | J | `verify/terra_check.csv` |
| R1-2 today's buildings, roads, railways, bridges | in Terra++, **never verified** | **B0** | J (needs client) | 10 screenshots + `terra_check.csv` |
| R1-3 buildings and roads by year | in Terra++, never verified | **B0** + timejump runs | J | `terra_check.csv` at 5 years |
| R1-4 famous buildings from the cards | only by command | **R1-f** build from cards, no command | M | `verify/landmarks.csv` (10 buildings, their years) |
| R1-5 **towns and villages of the past where the maps are empty** | **not built at all** | **R1-d** houses, markets, temples, walls by era & size | M | `verify/place_check.log` in 10 towns |
| R1-6 roads of the past (Roman roads, the Silk Roads, the Grand Trunk Road) | map item only | **R1-e** built for their years | M | `verify/roads.csv` |
| R1-7 **the far end: 2026 → 3000 AD** | **PARTIAL (2026-10-27, `verify/FUTURE_STORY.md`).** Built the story, not just the projection: `history/future_story.json` in **four lanes** - **124 computed** (eclipses, comet returns, asteroid passes, transits, all checkable), 5 projected states, **17 authored chapters** signed by the assistant, and silence. **13 of the 17 chapters sit on a real astronomical event** (2027 eclipse, Apophis 13 Apr 2029, the 21st century's largest lunar eclipse, J002E3 returning, Halley 2061, Sydney's next totality 3 Jun 2858); 3 sit on a dated prophecy and are about it failing. Pinned by `checkFutureStory` (every line labelled, every authored line signed, no projected line names a ruler/war/disaster/price, no empty century). Artifact `verify/future.csv`: 2026/2100/2400/3000 all **consistent** | **R1-7s** the 3 screenshots R1-7 asks for - blocked on P1 (no client session); **R1-7e** bulk-load the NASA canon (~2,240 solar eclipses to 3000) instead of the curated 100; **R1-7x** *(fixed 2026-10-27)* harness read a stale `All checks done` fragment with `tail -1` and graded a phantom 13-failure line; now reads the engine's timestamped `end of check:` tally. **R1-7z** `--only` without `--probes` silently skips the whole `/ee check all` step yet still reports green | **N** | `verify/FUTURE_STORY.md`, `history/future_story.json`, `verify/future.csv` |

### Requirement 2 — Every history, 3000 BC → 3000 AD (14 rows: R2-1 … R2-12, plus R2-12a and R2-12b)

| row | today | step | owner | artifact |
|---|---|---|---|---|
| R2-1 who ruled, borders | ✅ done — and since 2026-10-27 **a year is nameable as the span it sits in**: `clock/SpanName` names the decade, century and millennium from 15,000 BC to AD 3000, cross-checked against Wikipedia's *List of decades, centuries and millennia* (28 checks, 0 failures). `/ee year` now says `the 1940s (AD 1940 - 1949), the 20th century (AD 1901 - 2000), the 2nd millennium (AD 1001 - 2000)`. The awkward years are right: 3000 BC is the 30th century BC, **AD 2000 is the 20th century and the 2nd millennium**, the 1790s BC are 1799 - 1790 BC, there is no year 0, and nothing is named past AD 3000. Pinned by `checkSpanNames` | — | — | existing checks, `clock/SpanName.java`, `verify/SPAN_NAMES.md` |
| R2-2 places that existed | ✅ done | — | — | 30,151 towns |
| R2-3 dated events | ✅ done | — | — | 129,163 events |
| R2-4 how many lived | ✅ done | — | — | Hyde-derived, marked |
| R2-5 languages, faiths, ways of life, products, money | ✅ done | — | — | 401 money kinds |
| R2-6 detailed knowledge (cards) | ✅ **done (board 32)** on a fixed 50-town test set: place card **50/50**, ruler **50/50**, famous people **50/50**, **244/244 questions answered in words**. News card **0 -> 35/50 (70%)** after wiring `NewsIndex` (129,232 dated events) into `LocalCards.build`; the 15 without one have no dated event within 50 km and 2 years, and are named in `verify/cards_test_set.csv`. Pinned by `checkNewsTellsOnlyWhatHasHappened` | **R2-e2** raise news coverage by adding events for the 15 (or declare 70% as the bar) | M | `verify/cards_test_set.csv` |
| **R2-7 news by the day** | **✅ DONE 2026-10-27 (`verify/R2_7_NEWS_BY_THE_DAY.md`).** Your defect confirmed: year-only data told a November battle in June. Built `DatedEvents` (**1,141 events, 533 dated to the day**) and `NewsIndex.onDay()`: an event is news only when `happened <= today` on the **day key**; year-only files demoted to finished years within 2 years, labelled. Then asked "what about 2027-3000" and it caught two more defects: **77 events carried a Wikipedia page date** (Battle of Legnica "1760" recorded as April 2011 - the harvester now reads only the infobox and refuses a date contradicting the title's year) and **a 1760 event was called news in the year 3000** (the day tier had a floor but no recency rule; only 2.3% of day-dated answers are within 2 years), now split into "Word has come of ..." vs **"Not news - this place's past: ..."**. Measured: dated line 14.0% of town-years, year-only 23.9%, nothing 62.0%; **fresh news 0.3%**; no events exist after 2026, so **no fresh news 2027-3000**. Pinned by `checkNewsNeverTellsTheFuture` (silent day before, told on the day, past-not-news 400 years on) and `checkNewsIndexLosesNothing` (500 place-years identical to reading all 129,232 events). Gates: 431 passed / 12 failed baseline | **R2-7a** breadth: fresh news is rare because the record is thin; **R2-c** declared futures is what would fill 2027-3000, and I will not invent one | **Y** | `verify/R2_7_NEWS_BY_THE_DAY.md`, `history/dated_events.json` |
| R2-8 **the far end: 2026 → 3000 AD** | ✅ **done (board 29)** — `Source.PROJECTED`: beyond 2026 every answer is the last recorded state carried forward and labelled a projection. 5 places x 2026/2100/2400/3000 verified + pinned in `/ee check all` | **R2-c** richer projections (declared futures) | M | `probe_far` + the check |ared future | M | part of `verify/future.csv` |
| R2-c *(extra, not one of the 14)* **declared futures for 2027-3000** | **PILOT COLLECTED 2026-10-27 (`verify/R2C_KALAGNANAM_DECLARED_FUTURES.md`).** On your ask, Kalagnanam was read as a declared-future source: **27 datable items 2027-3166**, 11 of them dated to a single day, each carrying a grade (A = Gregorian date printed by the commentator, B = Telugu year name, C = sequence only) and its own source URL. Measured honestly with `tools/measure_prophecies.py`: **2027-2066 is filled** (11 single-day items, 9 year-windows) but **949 of the 974 years (97.4%) have nothing but a coarse span**, and **from 2069 to 3000 there is not one dated item**. Its near-term record is **0 for 5**: the 2009 mission start, the 2011 coronation, the 2024 bombing/capital move, the 2024 Hyderabad nuclear strikes and the 2025 world war have all gone by without happening, and those failures are kept in the file as `pastClaims`. Data is registered in the manifest but **deliberately not wired into the clock or the news card**: it must never become `RECORDED` fact | **R2-c1** build the `Source.PROPHECY` route (shown only in its claimed years, worded "as foretold - a prophecy, not a record", never as news, never saved as world state); **R2-c2** 2100-3000 needs a different source class entirely, or silence | **N** | `verify/R2C_KALAGNANAM_DECLARED_FUTURES.md`, `history/prophecies.json`, `verify/kalagnanam_futures.csv` |
| R2-9 vocabulary ids | ✅ done (board 19) | — | — | `probe_vocabulary`: 0 undeclared |
| R2-12a **the 18 absent polities** | ✅ **done (board 23)** — second register, 12 recorded + 6 estimates | — | — | `polities_second_register.json`; check "second register closes its gaps" |
| R2-12b the six `estimate` rows | ✅ **done (board 30)** — all six `recorded`, each with a source. Three dates corrected: tomara 1165→**1152**, amber 1128→**1028** (five-way source conflict, declared), somavamshi 850→**882**; kolathiri 1100→**1122**; zamorin 1124-1806 and manipur 1110-1949 confirmed | — | — | `polities_second_register.json`: 0 estimates |
| R2-10 can a civilization be named and dated, with or without a record? / names for every polity's people | ✅ done (boards 20–21) | — | — | 818 → 10 generic |
| R2-11 name + dates without a record | ✅ done (board 21) | — | — | 1,567 of 1,567 |
| **R2-12 correct answers** | ✅ **DONE (2026-10-27).** 15 defects fixed: Istanbul 1460 sham ruler + its 1454-65 hole (`Source.FILLED`), Berlin 1821→Prussia, Kraków 1840→Free City, Byzantium→1453, Sicily→1091, Khmer→1431, Golden Horde→1502, Ghaznavid→1186, Upper Burgundy→933, Epirus→1356–1479, Hunnic→469, New Netherland→1674, Almería→1147, Córdoba dropped. Probe faults fixed (union-midpoint, one-sample, mean-centre, colony-neighbours). Wikipedia cross-check of **all 135** tail polities. Final: core **96.6%**, clean **91.5%**, tails **136** = **55 proven fine / 28 unjudgeable / 53 unverified**, win-nowhere 0.6%, harsh whole-territory **68.2%** (low by design). Tail classifier reported as a NEGATIVE result | — | **Y** | `verify/R2_12_KNOWN_LIMITS.md`, `verify/wiki/TAILS_CROSSCHECK.md`, `verify/span_honesty.csv` |

### Requirement 3 — People act out history (6 rows)

| row | today | step | owner | artifact |
|---|---|---|---|---|
| R3-1 they talk about their history | ✅ done | — | — | talk from data only |
| R3-2 everyday life (names, clothes, jobs, rounds) | partly | **R3-c** jobs, wages, daily rounds | M (shared with R4-f) | `verify/jobs.csv` |
| R3-3 act out events (battles, sieges, crownings…) | a few people at a spot | **R3-b** sides, clothes, weapons, marches | M | the 7 test events, 7 screenshots (Y) |
| **R3-4 famous people at home in their years** | **not yet** (3 hard-coded) | **R3-a** | M | the 7 test events: the named person where the card says |
| R3-5 react to the player and changed history | partly | **R5-d** | M | a paper + a person's talk in a changed timeline |
| R3-6 only history's people in the world | ✅ done | — | — | vanilla mobs off |

### Requirement 4 — Money, vehicles and many more (10 rows)

| row | today | step | owner | artifact |
|---|---|---|---|---|
| R4-1 money | mostly (401 kinds) | **R2-d3** named-only polity gets an economy | M | `verify/money_polity.csv` |
| R4-2 goods and products (132 → ~400, with chains) | partly | **R4-b** | M | `verify/kinds/goods.csv` |
| **R4-3 vehicles: carts, chariots, horses, camels, elephants, boats and ships, trains, trams, cars, buses, bicycles, planes** | **nothing moves** | **R4-a** carts→ships→trains→trams→cars→buses→planes | M | one route per vehicle, `verify/vehicles.csv` |
| R4-4 weapons | research only | **R4-c** weapons obtainable, era rules + licences | M | `verify/kinds/weapons.csv` |
| R4-5 clothes | partly | **R4-d** | M | `verify/kinds/clothes.csv` |
| R4-6 food, tools, animals, crops, materials | partly | **R4-d** | M | `verify/kinds/food.csv` |
| R4-7 news, maps, books | ✅ done | — | — | crier → book, 13 forms |
| R4-8 reading, scripts, measures, wealth, festivals | partly | **R4-e** answer for every test cell | M | `verify/kinds/measures.csv` |
| R4-9 technology by place and year | partly (130 techs) | **R4-e2** prevalence to the last tested country | M | `verify/kinds/technology.csv` |
| **R4-10 jobs and wages, laws** | **not yet** | **R4-f** (same work as R3-c) | M | `verify/jobs.csv` |

### Requirement 5 — Changing history (6 rows)

| row | today | step | owner | artifact |
|---|---|---|---|---|
| R5-1 stop a live event, and a new timeline where it did not happen | ✅ done (Mumbai 2008) | — | — | existing story |
| R5-2 changes add up | ✅ done | — | — | — |
| **R5-3 more ways to change history: kill or save a famous person, win or lose a battle, take the crown** | **not yet** | **R5-a** | M | kill Pericles 430 BC → Athens' next 10 years differ |
| R5-4 a butterfly effect that keeps going: new rulers, borders, wars, money, buildings | partly | **R5-b** | M | stop Operation Polo → read 1948, 1958, 1998 |
| R5-5 the land changes too | in Terra++, unlinked | **R5-c** | J (P2) | same place, two branches, different buildings | **history half built 2026-10-27** (`verify/PLAYER_CHANGES_HISTORY.md`): `story/Divergence` + `story/DivergedHistory` make a fork addressable and enforce two rules (nothing before the fork changes; the sky identical in every timeline - the same 121 astronomy dates from inside all 3 forks). Two-account view works on the 3 existing scenarios; pin `checkDivergenceHonesty` + `DivergenceProbe` 19/19. **Still blocked: world half needs Terra++ (P2); 0 of 3 forks enterable - all unsigned drafts; no player-action hook yet** | **stage 2 built 2026-10-27**: `story/ForkLedger` lets a player actually cause a fork - signed by the player, so it passes the guard the unsigned drafts fail; refuses unnamed acts, empty acts, impossible dates, places off Earth, and duplicates (same act/day/square = one fork); survives a save and refuses an unsigned fork on load. Pin `checkPlayerForks` + `PlayerForkProbe` 16/16. Two miscounts caught: sky concatenated per fork (363 instead of 119) and two facts posing as events (120 vs 119). Gates 434 passed / 12 baseline, 1,261 classes |
| R5-6 papers, cards, book follow | partly | **R5-d** | M | a paper naming what changed and why |

### Requirement 6 — Breaking a paradox (6 rows)

| row | today | step | owner | artifact |
|---|---|---|---|---|
| **R6-1 the rupture** (break a dated building → stress → new universe) | **in Terra++** | **R6-c** trigger + verify | **Y (P1,P2)** | warning → rupture → new universe, screenshots |
| R6-2 more paradoxes: fixed points, meeting yourself, future things | not yet | **R6-a** mod names its fixed points, feeds Terra++'s counter | M | `/ee paradox fixed` + the counter moves |
| R6-3 the story goes on in the new universe with broken logic: people from other eras, events out of order, rulers who should not be | not yet | **R6-b** rules for a broken world | M | 20 consistent-but-broken years, one board |
| R6-4 broken physics (gravity, day, time, weather, mobs) | partly | **R6-d** | J (P1) | 5 named kinds of break |
| R6-5 portals in and out | not yet | **R6-d** | J (P1) | round trip surviving a restart |
| R6-6 the old campaign's paradox countdown (time machine) | command only | **R6-e** | **Y — one decision** | keep apart, or join in |

### Requirement 7 — Performance (6 rows)

| row | today | step | owner | artifact |
|---|---|---|---|---|
| R7-1 no freezes | two fixed | **R7-a** | M | `verify/walk.csv` |
| R7-2 steady speed with crowds | partly | **R7-a** | M | `walk.csv` |
| R7-3 Terra++ rebuilding after a jump | Terra++'s work | **R7-b** faster, or a waiting screen | J (P2) | a jump that isn't a freeze |
| R7-4 townspeople after a long jump | looked into | **R7-a** | M | `walk.csv` rows per stop |
| R7-5 memory and data size | partly | **R7-d** per-step budget ≤ 5 ms tick | M | every board records its cost |
| **R7-6 the long test walk** | **never run** | **R7-a + R7-c** | M then **Y** | `walk.csv`, then **your** fps and client ms |

**Steps: 36.** Done already: 14 rows. Open: 39 rows across those 36 steps (several steps close two rows).

---

## Part 3 — The sequence, with exit criteria

Dependencies decide the order. Lanes M and Y run **in parallel** wherever they can.

```
P0  definitions signed off (Y)  ─┬─> every phase below
P1  client session exists (Y)   ─┼─> B0, R6-c, R6-d, R7-c
P2  Terra++ branches reachable  ─┘   R1-2/3, R5-c, R6-1
P3  second source for 18        ───> A0's wrong-rate

PHASE A  truth first          A0 audit · R2-a2 · R2-e · R2-b · R2-d3 · long-tail suite
PHASE B  people and places    B0 verify · R3-a · R3-c/R4-f · R1-d · R1-e · R1-f
PHASE C  things that follow   R5-a · R5-b · R4-a · R4-b/c/d/e · R3-b · R5-d
PHASE D  the future           R1-g · R2-c
PHASE E  connect and judge    R6-a · R6-b · R5-c · R6-c/d/e · R7-a · R7-b · R7-c
PHASE F  the certificate      verify_requirements.sh — 7 lines, all green
```

**Exit criterion for every phase:** its rows' artifacts exist, its steps' boards are written, and
`verify_all.sh --all` still passes with no regression. A phase that leaves a gate red does not advance.

**Why this order and not another:** A first because every later claim rests on the answer's truth. B before
C because a consequence needs a person to happen to. D after C because the future inherits whatever rules
C establishes. E last because it needs everything before it *and* needs you at the keyboard.

---

## Part 4 — The certificate: one script, seven lines

100% is not a document. It is a run:

```bash
./verify_requirements.sh          # reads the artifacts, prints one line per requirement
```

| line | green when |
|---|---|
| R1 | `terra_check.csv` 10/10 · `place_check.log` 10/10 towns · `landmarks.csv` 10/10 in their years · `future.csv` consistent + 3 screenshots |
| R2 | `answers.csv` wrong-rate < 2% · `cards.csv` complete for the test set · 50 day-specific news samples · `future.csv` |
| R3 | 7 test events, named person in place, screenshots present · `jobs.csv` |
| R4 | `kinds/*.csv` all present and non-empty · one route per vehicle · `money_polity.csv` |
| R5 | 3 timeline artifacts (Pericles, Operation Polo 3 years, the land link) · `paper` sample |
| R6 | rupture screenshots + 5 named breaks + `paradox fixed` output + portals round trip |
| R7 | `walk.csv` inside 250 ms / 50 ms · your fps numbers filed · every board's ≤ 5 ms budget |

**Anything missing ⇒ that line is red ⇒ that requirement is not complete.** No prose can change a red line.

---

## Part 5 — What could still stop 100%, and what I'd do about it

| risk | severity | what I do |
|---|---|---|
| **P1 never happens** (no client session) | fatal for R6-1/4/5, R7-6 and every visual row | I close everything else and report **"5 of 7 closed, 2 declared blocked on P1"** — with the reason. I will not call it 100% |
| **P2 never happens** (Terra++ branches unreachable) | fatal for R5-5, R6-1 | R5 closes at 5 of 6 rows; R6 at 4 of 6. Declared, not hidden |
| **P3 fails** (no source for the 18) | caps R2's wrong-rate | the 18 stay declared; the audit reports the wrong-rate *including* them, so the number is honest |
| a step's cost pushes the tick over budget | blocks R7 while R1/R4 grow | the ≤5 ms budget is per step, so the offending step is caught at its own board, not at the end |
| the future (R1-7/R2-8) is uncheckable | lowers confidence, not completion | the artifact is *internal consistency*, stated as such; no claim of truth |
| I find another class of silent defect | — | new sub-step, added to the matrix, done before the phase advances — as boards 19–21 did |

---

## Part 6 — The honest cost, and the honest ceiling

- **35 steps** at the pace of boards 19–23 (each: measure → build → gate → board). That is roughly **35–45
  working sessions** of this kind, with the largest blocks being **R1-d (past towns)**, **R4-a (vehicles)**
  and **R1-g/R2-c (the future)**.
- **14 rows are already done** with artifacts; 39 rows remain.
- **~70% of the remaining work is mine. ~30% cannot be done in this sandbox.**

**So the direct answer to your question:** I can take this to **7 of 7 closed *if and only if* P1, P2 and P4
happen** — a client session, Terra++'s branches reachable, and four definition sentences agreed. If they do
not, the honest maximum is **5 closed and 2 declared blocked with a named reason**, and I will say that
plainly rather than print a green line I cannot defend.

**What I would start with, today:** **A0, the truth audit.** It costs one step, it is entirely mine, and it
replaces the one number this project has never computed — *how often is the world simply wrong?* If that
number comes back worse than 1 in 50, every plan above changes shape, and better to know now than after
building towns and vehicles on top of it.
