# The marking board — fourth sitting, 2026-10-22

Continuing `MARKING_BOARD.md` (1st), `MARKING_BOARD_2.md` (2nd), `MARKING_BOARD_3.md` (3rd).
The third sitting's red mark was: **the game's join finds 78.7% of 175,008 filed people; 1800 is the
worst era at 59.3%.** This sitting built and verified the fix.

---

## 1. The red mark is now green — and what that actually means

| measure | before | after |
|---|---|---|
| people the join returns, all 175,008 | 137,647 (**78.7%**) | **175,008 (100%)** |
| worst era in the game (1800) | 59.3% | **100%** |
| mean across 14 eras | 80.8% | **100%** |
| `probe_famous_join` verdict | **FAIL** | **PASS** |

**But read the fine print, because I nearly fooled myself.** My first version of the in-game probe
only asked whether the returned list was **non-empty**. It printed 100% immediately — a check that
could not fail. I rewrote it to test **whether this specific person is in the list** (by row). It
still reads 100%, and now it reads 100% *because the implementation returns everyone whose place
circle covers the point* — which is what the fix does. So:

> **The 100% is a tautology of the new design, not a discovery.** Its value is as a regression guard
> (it fails instantly if the geographic tiles are missing, or the century window is wrong), not as
> evidence of historical accuracy. The evidence for accuracy is the two measurements below.

**What keeps it honest — measured, not asserted:**

| property | result |
|---|---|
| every added person is inside **their own** place circle | worst distance ÷ radius = **0.856** (limit 1.000) |
| the fallback adds people from a state other than the ruler's | 205 of 4,167 returned (**4.9%**) — these are exactly the ones the old join dropped |
| distinct states among the people of one place | 1–6 (London 1800 mixes 6 polities: England, UK, British Empire…) |
| cost per lookup | **0.49 ms** (500 calls in 244 ms) |
| whole-mod syntax gate | 500 files, **0 syntax errors** |
| `probe_here` regression | **391 checks, 0 failed** (unchanged) |
| manifest | content **132/132**, byte **132/132** |

---

## 2. What was changed — three files, and why each

### a) `worldfill/build_tiles.py` — a **geographic** group, alongside the state groups
`famous_people.tiles` grouped people by **state** (`s/<qid>`) and by birthplace box (`b/…`). It now
also writes **`g/<y>/<x>`** — every person in the 5° box of their own place, bucketed by first adult
century — plus `maxRadius: 800` in the meta. Cost: the tile file grew **8.06 MB → 12.52 MB**
(+4.4 MB), 2,461 groups. The build is deterministic and re-runnable in 8 s.

### b) `FamousPeople.tiledLand` — the join asks the land, not only the state
The state's own people are asked **first and in the same order as before** (nothing about existing
behaviour changed), then `appendLandFallback` reads every geographic box within `maxRadius` of the
point and adds the people whose circle covers it, skipping rows already returned. New comment in the
source records the measurement that caused it.

### c) The **no-ruler** tier — the last 2.1%
When no ruler is named for a place-year, the old code returned **stateless people only** and dropped
everyone else. That tier now asks the land too. This is what moved −500 from 79.4% to 100%.

**And the JSON (no-tiles) path** got the same fallback in `candidates()`, so the two paths answer the
same question instead of disagreeing — they were already allowed to differ, which is its own hazard.

---

## 3. What is still wrong — the data, not the join

The join now works **despite** the bad ids, which means **the bad ids are still there**:

* **Nikos Skalkottas** is still filed under **Q7318 = Nazi Germany**, and his birth year is still
  **1901** where every source says **1904**. The join no longer hides him; nothing has made him
  right.
* **1,716 people alive in 1800** are still filed under **Q145 United Kingdom** rather than the polity
  that actually ruled them then.
* The **2,443 disagreeing pairs** (33,699 people) are untouched. They now cost nothing at the join,
  but they cost wherever the state id is used **as a label** — which includes `HistoryChecks` and any
  "people of this state" view.

**So: the join is fixed; the filing is not.** The next data fix is mechanical and I know its shape:

| fix | scope | gives |
|---|---|---|
| period state instead of modern container | ~2,000 rows (Q145/Q30/Q183/Q38/Q29 in wrong periods) | correct labels, correct "of this state" views |
| alias table from the 261 same-lineage pairs | 1 table | +5% exact-id agreement |
| state **as a timeline** per person | schema + rebuild | the honest fix: right at every year |

---

## 4. Gate status

| Gate | Result |
|---|---|
| **G1 L0 static** | **PASS** — 0 syntax errors; 121 packs parse; manifest content & bytes **132/132** |
| **G2 L1 probes** | **102 green / 0 red / 39 unusable** — `probe_famous_join` added and green after the fix |
| **G3 L2 truth** | one real error confirmed (Skalkottas); 5.3% impossible lifetimes; **join defect fixed**; filing defects open |
| **G4 L3 invariants** | **new invariant stands**: "a person filed under a state must be found in the year they lived" — was FAIL, now PASS |
| **G5 L4 compile** | **still blocked** — needs ~4 GB RAM + network (`./gradlew compileJava` + a headless server) |
| **G6/G7** | blocked on your jar, world, client |

Workspace after the change: **111 MB counted, 2,488 files** — still under the 120 MB budget line.

---

## 5. Verdict in simple words

**The bug was real, the fix is small, and it is now measured.**

1. **One person in five was invisible, and it was not the history's fault.** Three-quarters of the
   misses were reproduced exactly by asking the same register about another year of the person's
   life. The pack was right; the join was asking a single-year question of a lifetime.
2. **The fix adds a question, it does not rewrite an answer.** The state's people are still asked
   first, in the same order. Then the land is asked, using the person's own place circle — so what is
   added is always people of *this place*, never strangers (worst ratio 0.856 of their own radius).
3. **It cost 4.4 MB of tiles and 0.49 ms per lookup.** And it took a false 100% I had to catch and
   throw away before the real one meant anything.

**One line: the population is now fully visible; the population's labels are still wrong.**

---

## 6. What I do next

1. **The same join audit on buildings, towns and events** — every other place two registers meet by
   id. If the pattern holds, it is the same one-method fix and the same kind of win.
2. **The filing fixes**, in the order that pays: period states for the ~2,000 container rows, then the
   261-pair alias table, then the timeline schema if you want the honest version.
3. **A standing invariant probe** for "found in the year they lived", so this class can never come
   back silently.
4. **G5** the moment you can give me RAM and network — 39 probes and the entire command surface are
   still unmarked, and that is the largest untested area in the project.
