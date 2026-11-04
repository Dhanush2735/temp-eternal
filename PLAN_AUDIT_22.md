# Plan audit 22 — does `HOW_TO_FINISH.md` actually complete the requirements?

_2026-10-24. I audited my own plan against every row of `worldfill/REQUIREMENTS.md`. It was set as a
**self-correction**, in the same style as the nine already recorded: a claim of mine that the evidence
overturns._

## The answer

**No.** The five phases would close roughly **55% of the remaining work**, and two requirements would
still be un-closeable by me afterwards. Seven specific holes, each a row of the requirements doc that no
phase addresses:

| # | hole | which requirement |
|---|---|---|
| 1 | **No truth audit anywhere.** Every one of my steps measures *resolution* (can the system name a thing). None measures *correctness* (is the answer true). R2's own bar is "200 random answers, fewer than 1 in 50 wrong" — and no step in the plan produces that sample | R2 |
| 2 | **R4 was scheduled as "vehicles".** Its own table has nine rows: money (done), **goods 132 → ~400 with raw-to-made chains**, **weapons**, **clothes**, **food/tools/animals/crops/materials**, **jobs and wages and licences**, **reading/scripts/measures**, technology (done). My plan covered one row of six open | R4 |
| 3 | **R5 lost its two hardest rows**: *"the land changes too"* (the link to Terra++'s branches — the row that makes a changed history visible) and *"people, papers and the book follow the new history"*. I had both on `COMPLETION_PLAN.md` and dropped them when I compressed to five phases | R5 |
| 4 | **Jobs, wages and daily rounds vanished** — they are a row in R4 *and* were step R3-c, and neither phase carried them | R3, R4 |
| 5 | **Nothing verifies Terra++ — which is R1's biggest row.** Today's buildings, roads and railways are "**in Terra++** … check in the test places", and my plan never schedules that check. It assumed the frame instead of testing it | R1 |
| 6 | **R6 was scheduled as if it were mine.** The trigger (break a dated building → stress → rupture → new universe) lives *inside Terra++* and needs a client. My plan's one row implies I would close it; I cannot | R6 |
| 7 | **No performance budget per step.** My own work adds cost (1,543 polities now read a name table, towns are to be built). R7 is "improve the performance", and a plan that adds work without measuring its cost is arguing against its own requirement | R7 |

## And one thing no plan can fix: "1:1" is not achievable

R1 says **"1:1 replica of Earth"**. The project's own measurements say it is not 1:1 and cannot be:

- 1 km is **1,036 blocks at Hyderabad and 1,294 at Beijing** — the scale varies by place;
- true north is turned from Minecraft north (29° at Hyderabad);
- heights above 1,000 m and depths below 2,000 m are **squashed** (Everest is 1,969 blocks).

So R1 as worded is **unmeetable**. What is meetable is *"near 1:1, with the distortion measured, documented
and constant enough to navigate by"*. A plan that does not say this out loud is promising something the
world generator cannot deliver — and my plan did not say it.

## What the corrected plan changes

`HOW_TO_FINISH.md` is now **version 2**, with the seven holes closed:

1. **A truth audit as a named step** (A0): 200 random place-year answers, each checked against the sources,
   reported as a CSV with a wrong-rate. It is the *first* step, because every other claim rests on it.
2. **R4 restored to its full table**: goods and chains, weapons, clothes, food/tools/animals/crops,
   jobs/wages/licences, reading/scripts/measures — six steps, not one.
3. **R2-a2 restored**: a second source for the 18 declared-absent polities.
4. **R5-c and R5-d restored**: the land link to Terra++'s branches, and papers/cards/book per timeline.
5. **Jobs and wages given their own step** (shared by R3 and R4).
6. **A Terra++ verification step** (B0) that checks what actually stands in the test places — marked as
   needing a client, so it is honestly listed as partly yours.
7. **A per-step performance budget**: every step records its tick cost, and a step that costs more than
   5 ms of server tick fails its own board.
8. **R6 split into three columns** — mod half (mine), Terra++ half (needs your client), and the decision
   about the old paradox campaign.
9. **A requirement close-out table**: for each of the seven, the exact steps and artifact that close it, so
   "complete" is a file that exists, not an opinion.

## The corrected estimate

| requirement | remaining work | closeable by me | needs you |
|---|---|---|---|
| 1 | past towns, roads, famous buildings, Terra++ check, future | 75% | the look of 3000 AD; the client check of today's buildings |
| 2 | truth audit, goods/measures edges, 18 absent polities, future | 85% | — |
| 3 | famous people, event scenes, jobs, daily rounds | 80% | that a scene reads as a scene |
| 4 | goods+chains, weapons, clothes, food, jobs, measures, vehicles | 90% | that a cart looks like a cart |
| 5 | kill/save, growing butterfly, land link, papers/book | 60% | whether the new history is *believable* |
| 6 | fixed points, counter, broken-logic story, portals | 40% | the rupture itself + five kinds of break (client) |
| 7 | the walk, the stall, per-step budgets | 70% | fps and client ms |

**Total: about 70% of what is left is mine; 30% needs your client, and R6 and the last of R1/R5/R7 cannot
be closed without it.**

## What I am not going to do

I am not going to pad the plan until it looks complete. The corrected version is longer because it is
honest, and it still says plainly: **the seven requirements cannot all be closed from this sandbox**, and
two of them (R6's rupture, R7's fps) are structurally yours.

The one line worth keeping from the audit:

> **My first plan measured the things I could measure. A completion plan has to include the things that
> need you, or it is a plan to feel finished rather than to be finished.**
