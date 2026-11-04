# Marking board 25 — cycle 2: the truth audit at full size, and it FAILS

_2026-10-24. 200 samples from the project's own town register. **R2's bar is "fewer than 1 in 50 wrong". The
measured rate is 1 in 29. The bar is not met, and the causes are named.**_

## The measurement

`worldfill/probes/TruthAuditProbe200.java` draws 200 towns from the 9,790 readable rows of `towns.json.gz`,
picks a year from each town's own life (founding → 2025), asks `WhoRuled` who ruled there, and writes every
row to `testrun/verify/answers.csv`.

```
towns available                 : 9,790
samples                         : 200
answered at all                 : 196  (98.0%)
  from the REGISTER             : 196  (98.0%)   recorded
  from PACK_CAPITAL (heuristic) :   0  (0.0%)
answered by nobody              :   4  (2.0%)
```

**Two facts worth having immediately:** the 50 km capital heuristic was **never** needed on real towns (the
register covers 98% of them), and the four "nobody" answers are where the register and the pack are *both*
silent.

## The wrong answers, one by one

| town | year | the register said | why it is wrong |
|---|---|---|---|
| Lac-Sainte-Marie | 1901 | British Colonial Empire | Quebec was in **Canada**, a dominion since 1867 |
| Markham | 1921 | British Colonial Empire | same — Canada since 1867 |
| Oshawa | 1921 | British Colonial Empire | same |
| Rivière-Ouelle | 1884 | British Colonial Empire | same |
| Ibiza | 1463 | **(nobody)** | Ibiza was in the **Crown of Aragon** |
| Galway | 1475 | **(nobody)** | Galway was in the **English Lordship of Ireland** |
| Mar de Ajó | 1969 | **(nobody)** | **Argentina** was a state |

```
clearly wrong : 7 of 200 = 3.5%   (1 in 29)
the bar       : fewer than 1 in 50 (2.0%)
verdict       : NOT MET
```

One more row is uncertain rather than wrong (Osorno 1684 — the town was abandoned 1602–1796, so "nobody" is
arguable); it is counted as **right** and named here so the reader can disagree with the arithmetic.

## The two causes, and they are different defects

**Cause 1 — a dominion is not a colonial empire (4 of 7).** The register's Canadian coverage stops short, so
every Canadian town dated 1867–~1930 falls back to `British Colonial Empire`. The register *does* have
`Canada` (9 of the 200 answers), which is why the same country answers correctly after the cutoff — the row is
there, the **span** is wrong or missing.

**Cause 2 — silence where a state certainly held the place (3 of 7).** `Ibiza 1463`, `Galway 1475`,
`Mar de Ajó 1969`: the register has no polity at the cell and no pack capital within 50 km, so the answer is
`(nobody)`. **The same defect the S1 pilot found at Athens** — the register's silence read as an answer — in
places the pack cannot rescue because it has no capital nearby (Aragon, the English Lordship of Ireland) or no
record at all (Argentina, which the register knows elsewhere).

## What this says about the project, plainly

**R2 is not at its bar.** 98% coverage looks impressive and is not the same thing as being right: the register
answers confidently and is wrong 3.5% of the time, which is roughly **double** what the requirement allows.
Twelve pilot samples found one defect; two hundred found two classes and seven instances. **The pilot
understated the problem by a lot — which is exactly why the full sample exists.**

## Cycle 3 — the repair, in the order the causes cost

| step | what | bar |
|---|---|---|
| **R2-a4a** | **the dominion spans**: `canada_dominion` (1867– ), plus the same audit run over Australia, New Zealand, South Africa, Ireland — every dominion that may be answering as an empire | the British-Colonial-Empire answers inside a dominion's years drop to 0 |
| **R2-a4b** | **the empty-answer class**: for every `NONE`, ask the *pack's* own civ list first (Aragon, England) before saying nobody, and record the gap where even that fails (Argentina) | every `NONE` in a settled town is either answered or **declared** with a reason |
| **R2-a4c** | a **check inside `/ee check all`** that samples 200 towns, counts `NONE` and dominion-mismatches as failures, and turns red above 2% | the audit runs in the game, not only in a script |
| **R2-a4d** | re-run the 200-sample audit | **< 2% wrong**, or the bar stays unmet |

## The gates

No source change this cycle (probes only), so the gates are unchanged and were green at the end of cycle 1:
`compileJava` 1,245 classes · 220/220 commands · `/ee check all` 425 passed, 12 baseline · manifest up to date.

One defect was in **my own probe**, not the game: a `null` founding year threw and left the first run sampling
six towns. Guarded, re-run, and recorded here rather than quietly fixed — a sampling bug that silently
narrowed the sample would have produced a flattering number.

## Verdict of this cycle

**The measurement PASSED; the requirement FAILED.** That distinction is the whole point of the loop: a cycle
that reports a red number honestly is worth more than three that report green ones. **R2's bar is currently
unmet at 3.5%, with two named causes, one of which (the dominion span) is a data repair of a single row.**
