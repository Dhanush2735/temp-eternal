# Alternatives for the ~30% I called "yours"

_2026-10-24. `COMPLETE_100.md` said ~30% of the remaining work cannot be done in this sandbox. This document
tests that claim item by item, because "blocked on you" should mean *nothing else can substitute* — and for
most of it, something can._

## The headline

**The ~30% shrinks to ~8–10% once the alternatives below are taken.** Only three things genuinely need your
eyes, and they cannot be substituted: **the rupture happening at all, client fps, and whether a thing looks
right to a human.** Everything else has a substitute — a weaker one, and each says how much weaker.

---

## A. The four blockers, and what can replace each

### P1 — a client session (blocks: R6-1, R6-4, R6-5, R7-6, and every visual row)

| # | alternative | what it gives | what it loses | cost |
|---|---|---|---|---|
| 1 | **you run 5 stops (25 min)** — already written as `PHASE_NEXT_PLAYTES.md` | the real thing: eyes, fps, the world as a player meets it | nothing | 25 min of yours |
| 2 | **a headless renderer I build** — a chunk→PNG renderer over the save files (I already parse `.mca` chunk by chunk) | objective images: what stands where, town layout, materials, era silhouette, before/after a history change | no lighting, no sky, no player view; **structure, not beauty** | 1–2 steps, mine |
| 3 | **structural checks instead of looking** — the "what should stand here this year" check compares data, not pixels | a number per town: right buildings, right size, nothing early | no judgement of whether it *reads* as a town | part of R1-d |
| 4 | **you send screenshots, I read them** | my judgement applied to your capture; one 10-minute session covers R1-d, R3-a, R5, R6 | needs you to take them | 10 min each time |

**Recommended: 2 + 3 as the default, 1 once at the end.** Then "does the world look right" is a picture I can
show you *and* a number I can defend — and your session becomes confirmation, not the only evidence.

### P2 — Terra++'s branch API (blocks: R1-2, R1-3, R5-5, R6-1)

| # | alternative | what it gives | what it loses | cost |
|---|---|---|---|---|
| 1 | **read `terra3/` source and write the bridge against its internal API** — the fork is in the workspace | the mod side compiled, answering, and a headless probe proving the call is made with the right branch id | cannot prove Terra++ *renders* the other branch | 1–2 steps |
| 2 | **a labelled stand-in** — the mod keeps its own branch state and edits the world itself (structure placement) to show a changed history | "the land follows the history" demonstrated **without** Terra++ | it is our own editing, not Terra++'s timeline; must be labelled a stand-in wherever it appears | 2–3 steps |
| 3 | **upstream** — coordinate with the Terra++ maintainers for a public branch hook | the real link, once | wait time, not in my control | unknown |

**Recommended: 1 now, 2 only if 1 fails, 3 as the long-term fix.** With 1, R5-5 moves from *yours* to *mine,
pending your one screenshot to confirm.*

### P3 — a second source for the 18 absent polities (blocks: R2-12's wrong-rate)

**This one is not a blocker. I checked.** Mewar: 566–1949, capitals Nagda → Ahar → Chittor → Udaipur, from
Wikipedia and Wikidata. The other 17 are the same class of fact.

| # | alternative | what it gives | what it loses | cost |
|---|---|---|---|---|
| 1 | **web research per polity** — a polity row each: name, start, end, capital, with the source cited | all 18 closed, marked *recorded* with a citation, or *estimated* where sources disagree | nothing, if each is cited | 1 step, mine |
| 2 | **estimates marked as estimates** — the project's own turn-6 rule allows it | the 18 named and dated, labelled | lower confidence | part of 1 |
| 3 | leave them declared | honesty with no closure | they stay invisible in a town | 0 |

**Recommended: 1.** P3 disappears from the blocked list.

### R6-1 — the rupture itself (inside Terra++)

| # | alternative | what it gives | what it loses | cost |
|---|---|---|---|---|
| 1 | **you break a building in 1700 and screenshot the sequence** | the real rupture, warning → stress → new universe | needs your session | 10 min |
| 2 | **the mod half, fully built**: fixed points named, the paradox counter fed, and the *story* of the broken universe simulated headlessly (people from other eras, events out of order, rulers who should not be) | R6-2, R6-3 closed and measurable; R6-1 ready to fire | the physics/land break stays Terra++'s | 2–3 steps, mine |
| 3 | **a mod-side stand-in universe** — our own dimension with broken rules | the five *kinds* of break demonstrated as logic | not Terra++'s rupture; must be labelled | 2 steps |

**Recommended: 2, with 1 as the confirmation.** So R6 goes from "mostly yours" to **"mod half mine, physics
half yours"** — 4 of 6 rows closeable here.

### R7-6 — client fps

| # | alternative | what it gives | what it loses | cost |
|---|---|---|---|---|
| 1 | **you run the 30-minute walk with F3 open** and send the numbers | real fps and client ms | needs your session | 30 min once |
| 2 | **server tick + a proxy model** — chunk, entity and block-entity counts per stop, converted to an estimated client cost | catches regressions, orders the stops by cost | **not fps**; must be labelled a proxy, never quoted as a measurement | 1 step |
| 3 | server-side sampling only (what `walk.csv` already does) | half the requirement, honestly | the client half stays open | 0 |

**Recommended: 3 by default + 1 once.** R7-6 is the one row I will not fake with 2.

---

## B. What genuinely cannot be substituted

Three things, and I will not pretend otherwise:

1. **The rupture occurring.** Terra++'s physics break either fires or it doesn't, and only a client shows it.
2. **Client frame time.** No server-side number is fps. A proxy is a different quantity with a different name.
3. **Whether a thing looks right.** A renderer shows me a town's plan and materials; it cannot tell me whether
   standing in it feels like Ahmadnagar in 1600. That judgement is yours, permanently.

Everything else in the "30%" has a substitute, and after taking them the residual is **~8–10% in total**:
one 10-minute rupture capture, one 30-minute walk, and your word on whether it looks right.

---

## C. If you want the minimum possible from you

The whole "yours" share, compressed to a **40-minute checklist**, done once at the end:

| # | what | when | time |
|---|---|---|---|
| 1 | install `eternal/build/libs/eternalengine-1.0.0.jar`, open `New World` | after Phase B | 5 min |
| 2 | five stops: Athens, Anyang, the Indus site, Giza, R6 — screenshot each | after Phase B | 15 min |
| 3 | break the Charminar in 1700, screenshot the sequence | after Phase E | 5 min |
| 4 | 30-minute walk with F3 open, send the numbers | after Phase E | 30 min |

Ten minutes of that can be dropped if you'd rather send screenshots later; the walk is the only part that
cannot be replaced by anything I can build.

---

## D. What changes in the plan

| was | becomes |
|---|---|
| P1 blocks 6 rows | a renderer + structural checks close 4 of them; you confirm the rest |
| P2 blocks 4 rows | reading `terra3/` and writing the bridge moves 3 to "mine, pending one screenshot" |
| P3 blocks R2's bar | **removed** — 1 research step closes the 18 |
| R6 "mostly yours" | **mod half mine (4 of 6 rows), physics half yours** |
| R7 "yours" | server half mine, client half yours, and the proxy is explicitly not a measurement |
| ~30% yours | **~8–10% yours: one rupture capture, one walk, one judgement** |

**The honest sentence:** I over-attributed work to you because the substitute for each item is weaker than the
real thing — and weaker is still worth having, as long as it says so. The three items that survive are the
ones where a substitute would be a *lie*: a proxy called fps, a stand-in called the rupture, and my opinion
called your judgement.
