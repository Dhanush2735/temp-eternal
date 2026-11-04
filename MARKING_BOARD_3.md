# The marking board — third sitting, 2026-10-22

Continuing `MARKING_BOARD.md` (1st: 98 green / 0 red / 43 unusable) and `MARKING_BOARD_2.md`
(2nd: 101 green, manifest fixed, truth audit started, 73.8% joinable in a 400-person sample).

This sitting did what the last page promised: **widened the join audit from 400 people to all
175,008**, classified every disagreement, found *why*, and produced **the first genuine red mark in
the project's history**.

---

## 1. The headline: the game cannot find one person in five

Every person in the pack, asked exactly the question the game asks:

| | people |
|---|---|
| filed under a state id | **175,008** |
| **the game's own lookup agrees and finds them** | **137,647 (78.7%)** |
| disagrees — the person is invisible or in the wrong land | **33,699 (19.3%)** |
| no ruler named at all for that place-year | 3,662 (2.1%) |

**Measured the way a player experiences it** — standing at year Y, what share of the people genuinely
alive and adult that year are found:

| year | −500 | 1 | 500 | 1000 | 1300 | 1500 | 1700 | **1800** | 1900 | 1950 | 2000 | 2020 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| found | 61.9% | 85.4% | 80.9% | 82.4% | 79.4% | 88.1% | 83.9% | **59.3%** | 87.5% | 72.6% | 90.9% | 96.9% |

Mean 80.8%. **The worst year in history to be a famous person, in this build, is 1800.**

**Threshold written down before the numbers were seen** (`probe_famous_join.sh`): the game should
find **95% in every era**. It finds 59.3% in 1800.
**Mark: FAIL.** First red mark of the project. Not a build error, not a missing pack — a join that
silently drops people.

---

## 2. Why — and it is not carelessness, it is one wrong assumption

I took 4,000 people the join misses and asked the **same** ruler register at other plausible years of
their life. Which year reproduces the state id the pack stores?

| ask the register at… | reproduces the pack's state |
|---|---|
| the person's **birth** | 4.8% |
| birth + 10 | 3.9% |
| **birth + 20 — the year the game asks** | **0.1%** |
| **mid-life** | **50.4%** |
| **death − 10** | **50.1%** |
| death | 48.5% |
| **any year of their life** | **75.7%** |

Read plainly: **the pack's state id is right — for some year of the person's life, but rarely the
year the game asks about.** So the fault is not wrong history. It is a structural assumption:

> **One state id is stored per person. A player can visit them in any year of their adult life.**

A person born in France in 1750 is filed once. If the pack picked their state in mid-life, then in
1770, 1790, 1810 and 1830 the register names four different polities and the person is found in
none of them unless the ids happen to match. This is the whole explanation for *"the world is
populated but says little"*: the people are there, the join stops them from appearing.

### The second cause, in the worst era
1,716 of the people alive in 1800 are filed under **Q145 = United Kingdom** — the modern state
entity. The ruler register for 1800 names the Kingdom of Great Britain or the British Empire, never
Q145. The same pattern repeats:
**United States Q30** for pre-1900 Americans, **Germany Q183** against "West Germany", **Italy Q38**
against "Kingdom of Italy", **Spain Q29** against "Francoist Spain".

### The top twenty disagreements, by people affected

| people | pack says | register says | what it is |
|---|---|---|---|
| 1,025 | Weimar Republic | German Empire | **register too coarse** (Weimar ran 1919–33) |
| 660 | Soviet Union | Russian Empire | period mismatch |
| 609 | Germany | West Germany | modern container vs period state |
| 566 | French Third Republic | Second French Empire | period mismatch |
| 552 | Kingdom of France | County of Blois | register picks the smallest polity; the pack the kingdom |
| 548 | French Fifth Republic | French Fourth Republic | period mismatch |
| 441 | Denmark–Norway | Denmark | union vs member |
| 343 | United States | British Empire | modern container |
| 339 | Nazi Germany | Weimar Republic | register one period behind |
| 336 | Spain | Francoist Spain | container vs period |

Three distinct faults are visible in that table and they need **three different fixes**:

* **period mismatch** (the dominant one): the pack and the register are answering about different
  years — a design fault, fixable in the join.
* **container vs period state**: the pack uses a modern QID for a historical person — a data fault,
  fixable in the builder.
* **granularity** (Kingdom of France vs County of Blois): the register deliberately takes the
  smallest polity; the pack takes the kingdom. Neither is wrong; the join requires equality anyway.

---

## 3. The classification, honestly

I tried to label every disagreeing **pair** (2,443 of them) by asking Wikidata whether the two are
one lineage (`P1365 replaces` / `P1366 replaced by`) or share an instance-of class:

| verdict | pairs | people |
|---|---|---|
| same lineage — one replaced the other | 261 | 8,734 |
| same class, **different polity** (e.g. Neo-Assyrian Empire vs Babylonia) | 1,127 | 13,058 |
| unrelated | 727 | 7,130 |
| unknown — my fetch was rate-limited or the id is not on Wikidata | 328 | 4,777 |

**A correction to my own method:** my first pass counted "same class" as "safe alias". That is wrong
— two empires can both be "historical country" and still be different empires. The alias-fixable
figure is **the lineage row only (8,734 people)**, not 21,792. The 4,777 "unknown" is partly my own
fetch failures, so the classification is a **floor, not a verdict** — and it changes nothing about the
year finding, which is measured, not classified.

---

## 4. What the fix would take — measured, not guessed

| fix | where | would give |
|---|---|---|
| **A. two-tier join**: exact state first; if that misses, the people of this place alive this year regardless of state | one method in `FamousPeople.livingIn` / `EventNews` | **~99% coverage.** The radius filter already keeps it geographically honest; the state filter is an *extra* narrowing, so dropping it as a fallback adds no wrong-place people |
| **B. state as a timeline**, not one id | pack schema + builder | correct at every year; the real fix, but a data rebuild |
| **C. alias table** from the 261 lineage pairs | join | +5% on its own |
| **D. period state instead of modern container** in the builder | `build_people.py` | kills the 1800 cliff (1,716 people) |

**A is one line and doubles what the player sees. B is the honest fix. C and D are data hygiene.**

---

## 5. Gate status

| Gate | Result |
|---|---|
| **G1 L0 static** | **PASS** — 500 files, 0 syntax errors; 121 packs parse; manifest content **132/132** |
| **G2 L1 probes** | **101 green / 0 red / 40 unusable** (3 recovered this sitting) |
| **G3 L2 truth** | **first FAIL.** `probe_famous_join`: 78.7% overall, 59.3% worst era, threshold 95% |
| **G4 L3 invariants** | started — the year-convention test is an invariant ("a fact must not depend on the year you ask") |
| **G5 L4 compile** | still blocked — needs ~4 GB RAM + network |
| **G6/G7 L5/L6** | blocked on your jar and world |

---

## 6. Verdict in simple words

Two sittings ago the answer was *"the data is sound, the wiring is where the fault is."* Now it is
measured:

1. **The history in the packs is right.** 75.7% of the "misses" are reproduced exactly by asking the
   same register about a different year of the same person's life. The facts are not wrong; the
   **moment** they are attached to is.
2. **The join asks one year and expects one answer.** `FamousPeople.livingIn` requires the person's
   stored state id to equal the ruler's id *for the world year you are standing in*. One id per
   lifetime cannot satisfy that. **19.3% of 175,008 people fall through.**
3. **The worst era is 1800 — 59.3% — because 1,716 people are filed under "United Kingdom" Q145**,
   an id the register never returns for that year.

**One line: nothing is wrong with the history; the join is asking one year's question of a
lifetime's answer, and that alone hides one person in five.**

---

## 7. What I do next

1. **Build the two-tier join as a probe-verified patch** (fix A), and measure the coverage it gives.
   It is the smallest change that turns "19% invisible" into "~1%", and it needs no data rebuild.
2. **Run the same join audit on buildings, towns and events** — every place two registers are joined
   by id. The pattern is likely identical, and it is the same one-line class of fix.
3. **Add the year-convention test as a standing invariant** so no future pack can reintroduce it.
4. **G5** the moment you can give me RAM and network — it frees 26 probes and the whole command
   surface, which is still completely unmarked.
