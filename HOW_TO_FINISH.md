# How I would finish the seven requirements

_2026-10-24. **Version 2** — audited in `PLAN_AUDIT_22.md`, which found seven rows of the requirements this
plan did not schedule. Those seven are now steps: A0 (truth audit), B0 (Terra++ check), R2-a2 (a second
source for the 18), R4-b…f (goods, weapons, clothes, food, measures — restored to their full table),
R5-c/d (the land link and the papers), R3-c (jobs and wages), and a performance budget on every step._

_The method, the order, the bar for each, and the parts that are yours._

---

## 1. Three rules I would work by

**Rule 1 — Work on what unblocks the most, not what looks best.**
Every requirement is downstream of one of three things: a *register* that can answer (data), a *person*
who exists (people), or a *consequence* that follows (rules). A step that fixes a register unblocks three
others; a step that adds a building unblocks one. Order by that, not by what photographs well.

**Rule 2 — Write the pass mark before the numbers arrive.**
Every step in boards 19–21 had its bar set first: "zero undeclared", "1% budget", "1,567 of 1,567". Every
one of them passed on the first honest run. The only thing that ever went wrong was mine to fix (a check
that hung the self-test, a display that crashed on a stub) and the gates caught both. That discipline is
the single most useful thing in this project and it stays.

**Rule 3 — Name the gap rather than fake the fill.**
18 vocabulary ids became a *declared* list with reasons, not 18 invented aliases. 10 island polities stay
in the generic name pool and are counted. 1,543 polities say `*` in the display because they have a name
but no treasury. A named gap can be closed later; a fake fill poisons every answer downstream of it.

---

## 2. The method that keeps finding the real defects

Four defects so far, all the same shape:

| board | defect | size |
|---|---|---|
| 16–18 | townspeople carrying a civilization id that does not exist | 18 of 57 |
| 19 | site ids resolving to nothing | 28 |
| 20 | polities named from the generic pool | 818 of 1,567 |
| 21 | polities the game could not read at all | 1,543 of 1,567 |

None was visible in any gate. **All were found by one question:** *what happens to the ids nobody thought
of?*

So that question becomes a standing suite. For every register the mod keeps — civilizations, site hints,
name pools, events, money, towns, cards, rulers, goods, technologies — run one probe that takes the long
tail and asks what the code does with it. **The target is not "no failures"; it is "no silent fallbacks".**
A fallback that announces itself is a declared gap. A fallback that says nothing is how a world of 1,567
polities ends up sounding like one village.

**Deliverable of this phase:** `probe_long_tail.sh` — every register, one table, the count of ids that
resolve to nothing without saying so.

---

## 3. The order I would actually take, in five phases

### Phase A — make the world say true things (cheap, closes requirement 2's edges)

| step | what | bar |
|---|---|---|
| **A0** | **the truth audit** — 200 random place-and-year answers, each checked against the sources: who ruled, what happened, how many lived, what they spoke and paid | `testrun/verify/answers.csv`: **fewer than 1 in 50 wrong**, every row marked recorded / estimated / projected. This is R2's own bar and nothing in the project has ever produced it |
| R2-a2 | a second source (princely-state and Rajput genealogies, Gazetteers) for the 18 declared-absent polities | the declared list drops below 18 without inventing a single ruler |
| R2-d3 | a *named-only* polity gets an economy without becoming a registered civilization (a lean price/wage lookup keyed by polity, not an engine) | a person in Ahmadnagar is paid in the sultanate's money, and the tick cost is measured as unchanged |
| R2-b | news by the day everywhere, not only Hyderabad 1948 | 50 sampled place-days in 10 regions are day-specific |
| long tail | the standing probe above, every register | zero silent fallbacks |

**Why first:** cheapest work per unit of truth, and it is what makes Phase B's people *say* something
correct when you meet them.

### Phase B — put people in places (requirement 3 + the visible half of 1)

| step | what | bar |
|---|---|---|
| **B0** | **verify Terra++ itself** in the test places — today's buildings, roads, railways, bridges, walls, trees: does anything stand before its time or after its end? *(needs your client: this is R1's biggest row and it has never been checked)* | ten test places, one screenshot and one `/ee building nearby` per place, `testrun/verify/terra_check.csv` |
| R3-a | **famous people at home in their years**, from the 148,510-person card data | the seven test events of the requirements doc: the named person stands where the card says |
| R3-c | **jobs, wages and daily rounds** — a town's people have trades, a working day and pay that matches the money data *(shared with R4's last row)* | a town shows trades, a day's pay in its own money, and a daily round by trade |
| R1-d | **past towns** — houses, markets, temples, walls, at the right size and era, from the 30,151-town data | a check that asks "what should stand here this year" and compares; ten test towns walked |
| R1-e | past roads built in the world for their years | the same check, for roads |
| R1-f | famous buildings built from the cards, without a command | Charminar, Colosseum, Angkor Wat appear in their own years |

**Why here:** this is the phase your save showed most plainly — Athens had ground and no houses, and the
only person who could have been standing there (Pericles) was a VIP record with nowhere to stand.

### Phase C — make things follow (requirements 5 and 4)

| step | what | bar |
|---|---|---|
| R5-a | **kill or save a famous person → the timeline bends**: successor, changed border, changed events | kill Pericles in 430 BC; Athens' next ten years differ in rulers, events and papers |
| R5-b | a butterfly that grows year after year | the doc's own test: stop Operation Polo 1948, then read 1958 and 1998 |
| R5-c | **the land changes too** — connect the mod's branches to Terra++'s timeline branches, so a changed history changes the buildings *(needs your client to see)* | the same place in two branches shows different buildings |
| R5-d | **people, papers and the book follow the new history** — talk, cards and the book read each timeline's own past | a paper in a changed timeline says what changed and why |
| R3-b | event scenes with sides, clothes, weapons | the seven test events |
| R4-a | **vehicles that exist and move**, in their own years: carts, chariots, horses, camels, elephants, boats, ships, then trains, trams, cars, buses, bicycles, planes | one route per vehicle walked; a check that none appears early |
| R4-b | **goods 132 → ~400** with the chains from raw to made, and shortages that bite | one table per kind |
| R4-c | **weapons you can get**, with era rules and licences | a check per era and region |
| R4-d | **clothes, food, tools, animals, crops, building materials** by place and year | one table per kind |
| R4-e | **reading, scripts, weights, measures** for every place and year | a check that a measure and a script answer for every test cell |
| R4-f | **jobs and wages, and the laws** (weapon licences) *(the same work as R3-c)* | a town's pay and its laws match its place and year |

**Why after B:** a consequence needs a person to happen to. This is the phase that answers your "no VIPs"
and "VIP interaction is thin" doubts, because it is where VIPs stop being records and start doing things.

### Phase D — the future (the invented half of 1 and 2)

**My decision, since you left choices to me:** build the **one marked road**, not a year-by-year
simulation.

- A single projected continuation per place, walked in steps (2026 → 2100 → 2400 → 3000), marked
  *projected*, agreeing with itself: a city's size, water, roads, people and money consistent across the
  years.
- It is **over-writable**: a changed history (R5) or a broken paradox (R6) replaces the projection wherever
  it touches, so the future is the default road, not a cage.

**Why this way:** a full simulated future is the largest block in the list and doubles R1 and R2, and it
cannot be checked against anything — so its only quality bar is internal consistency, which the marked
road gives at a tenth of the cost. If you want the full simulation instead, say so; it is a different
plan and I will cost it honestly.

### Phase E — connect, then judge (requirements 6 and 7)

**R6 splits three ways, and the plan says which is whose:**

| step | whose | what | bar |
|---|---|---|---|
| R6-a | **mine** | the mod names its **fixed points** (events that must happen, meeting yourself, future things in the past) and feeds Terra++'s paradox counter | `/ee paradox fixed` names them; the counter moves when a fixed point is broken |
| R6-b | **mine** | the story goes on in the broken universe: people from other eras, events out of order, rulers who should not be — from rules, not chaos | given a rupture, the next twenty years are internally consistent in their *brokenness* |
| R6-c | **Terra++** | the rupture itself: break a dated building → warning → stress → a new universe with other physics | **needs your client. I cannot produce this and will not claim it** |
| R6-d | **yours + mine** | portals in and out; broken physics Minecraft allows (gravity, day length, time speed, weather, mobs) | a round trip that survives a restart |
| R6-e | **decision yours** | the old campaign's paradox countdown (time machine) — keep it apart or join it in | one line from you |

| step | what | bar |
|---|---|---|
| R7-a | **the 30-minute walk** with time jumps, numbers written down | no tick > 250 ms, average < 50 ms |
| R7-b | the Terra++ rebuild stall (your ~5,900 km at R5) either faster or covered by a waiting screen | a time jump that does not look like a freeze |
| R7-c | fps and client ms | **yours** — no server can measure a client |
| **R7-d** | **a performance budget on every step** — each board records its own server tick cost | a step that adds more than 5 ms of tick fails its own board |

---

## 4. What I need from you, and when

Three things, none of which I can do myself:

1. **The P1 play test** (already written as `PHASE_NEXT_PLAYTES.md`) — five stops, 25 minutes: Athens,
   Anyang, the Indus site, Giza, R6. It is the only way to see whether the 18 standing people are fixed,
   whether Athens is timing or a bug, and whether `/ee villager nearby` reads right in the world.
2. **The final fps walk** — requirement 7's second half, and the only judge of "does 3000 AD look like a
   place".
3. **One decision, if you disagree with mine:** the marked road vs the full simulated future (Phase D).

Nothing else is blocked on you. Every other step can run here, measured, with a board.

---

## 5. The bar for "requirement complete"

A requirement is done when **one command reproduces its evidence**, not when a board says so:

| # | complete when | evidence artifact |
|---|---|---|
| 1 | the "what should stand here this year" check passes in ten towns and the three future years are consistent and marked | `testrun/verify/place_check.log` + three screenshots |
| 2 | the registers answer for every test cell and 200 random answers hold fewer than 1 in 50 wrong | `testrun/verify/answers.csv` (the 200, with recorded/estimated/projected marks) |
| 3 | the seven test events are acted out with the right named people at the right place and year | seven screenshots + `ee event` log |
| 4 | one table per kind and a walk per vehicle | `testrun/verify/kinds/*.csv` |
| 5 | Operation Polo stopped → 1948, 1958, 1998 read differently and believably | one board, three years, three screenshots |
| 6 | the Charminar broken in 1700 → five named kinds of break | one board, five screenshots |
| 7 | the 30-minute walk inside 250 ms/50 ms, and your final game test with no freeze over 1 s | `testrun/verify/walk.csv` + your numbers |

**Until each of those artifacts exists, the requirement is not complete — whatever the boards say.** That
is the rule I would hold myself to, and the reason my answers to you have been "partly" more often than
"done".

---

## 6. One requirement cannot be met as worded

**R1 says "1:1 replica of Earth". It is not 1:1 and cannot be.** The project's own measurements:

- 1 km is **1,036 blocks at Hyderabad and 1,294 at Beijing** — the scale varies by place;
- true north is turned from Minecraft north (**29°** at Hyderabad);
- heights above 1,000 m and depths below 2,000 m are **squashed** (Everest is 1,969 blocks).

So the reachable bar is **"near 1:1, with the distortion measured, documented and constant enough to
navigate by"** — and 435 places already convert to a block and back within 1 m. Any plan that promises
literal 1:1 is promising something the world generator cannot deliver. This is written into
`REQUIREMENTS.md`, not just here.

## 7. What this costs, and what I would tell you plainly

Roughly **25–30 steps** of the size of boards 19–21. Three are done. The visible half (Phase B) is perhaps
eight of them; the future (Phase D) is the largest single block; Phase E's last item is yours.

The project is not close to finished. It **is** close to being honest about itself, which is a different
and more valuable thing: five of seven gates pass, four classes of silent defect have been found and
counted, and every gap now has a name and a place in a plan.

**If you want the shortest path to something you can stand in and believe:** skip ahead to **Phase B**
(R3-a then R1-d). It is the phase where the world starts looking like the past rather than being merely
correct about it — and it is what your own screenshots have been asking for since Athens.
