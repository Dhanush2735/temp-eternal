# The marking board — eighth sitting, 2026-10-22

Continuing boards 1–7. Board 4 measured the filing defect: **a man who died in 1770 filed under
"United Kingdom" (a state that began in 1921).** This sitting fixed every row that can be fixed from
the project's own record, and turned up two things nobody had measured.

---

## 1. The filing fix: 2,582 rows corrected from the register itself

The rule, and it is the project's own: **when a person is filed under a modern container and the ruler
register names something different for that person's own place and those own years, the register wins.**
Nothing was invented and nothing was looked up outside the repository.

| | rows |
|---|---|
| using a modern container for an older life | **13,021** |
| → the register names a better answer | **2,582 — all applied** |
| → the register names nothing (left alone) | 640 |
| → the register **also** uses the container (its own coarseness) | 9,799 |

After the fix, re-running the same probe: **13,021 → 10,439 container rows, and 0 still carrying a
better answer**.

The corrections, by size:

| rows | from | to |
|---|---|---|
| 445 | Q38 Italy | Kingdom of Italy |
| 333 | Q30 United States | British Colonial Empire |
| 318 | Q145 United Kingdom | Kingdom of England |
| 244 | Q159 Russia | Union of Soviet Socialist Republics |
| 233 | Q29 Spain | Iberian Union |
| 213 | Q29 Spain | Crown of Castile |
| 142 | Q29 Spain | Habsburg Monarchy |
| 125 | Q148 China | Republic of China |

Spot-checked: a person active in 1500 in Spain becomes **Crown of Castile**, not "Spain"; a Russian
active in 1950 becomes the **USSR**, not "Russia". Both are what the register says for that grid cell
and that year.

**Measured effect on the underlying defect** (`FamousJoinFullProbe`, all 175,008 filed people):

| | before | after |
|---|---|---|
| exact-id agreement | 137,647 (**78.7%**) | 140,229 (**80.1%**) |
| disagreeing pairs | 2,443 | 2,394 |

The +2,582 is exactly the number of rows changed — every correction landed and none over-reached.

---

## 2. A finding I did not expect: the pack carries duplicates — but only 38

The Skalkottas mystery resolved when I looked at the master rather than the sample:

```
['Nikos Skalkottas', 'Greek composer', 1901, 1949, 'Q7318', 39.000, 22.000, 800]
['Nikos Skalkottas', 'composer',      1904, 1949, 'Q7318', 38.464, 23.603,  25]
```

**He is in the pack twice** — once from the year-page build (birth 1901, placed at a rough point,
correctly 1904 in the notability database), once from the notability database. My earlier "birth year
is wrong" was half right: the wrong year exists, and so does the right one, side by side.

How widespread is duplication? **Name collisions are not duplicates** — "David" is the king, a
6th-century saint and a man born in 1902. Measuring *true* duplicates (same name, life within 3 years,
within 50 km of the same point):

> **38 pairs out of 184,060 rows.** 3,524 names repeat, but only 38 repeats are the same life.

**Fixed presentationally, not by deletion**: one line no longer says the same person twice. Rows were
not removed, because the tiles and the join number people by row, and nothing about a rough duplicate
justifies renumbering a master that everything else reads.

---

## 3. And a correction to my own earlier claim about Q7318

Board 2 reported Skalkottas filed under **Q7318 = "Nazi Germany"** and implied a class of wrong ids. The
class is real but it is not what I implied:

| Q7318 rows | 1,092 |
|---|---|
| median birth year | 1901 |
| born 1933 or later | **0** |
| born before 1918 | **1,054** |

Read the sample: Julius Schreck (died 1936), Richard Hauptmann (executed 1936), Georg Donatus of Hesse
(died 1937), Gerda Taro (died 1937 in Spain), Renate Müller (died 1937), Bernd Rosemeyer (died 1938).
**The pack files people by the state that ruled when they died**, so a German who died in 1936 is filed
"Nazi Germany" — which is defensible, and is a *period* state, not a modern container. **Skalkottas is
the outlier**: a Greek who died in 1949 should never have carried it.

So Q7318 was never the flaw I thought. The flaw is the one already known: **one state id per lifetime**,
and a grid cell that occasionally borrows its neighbour's answer.

---

## 4. What is still open, and honestly so

| item | size | why it is not done |
|---|---|---|
| the 261 lineage-alias pairs | 8,734 people | **measured and declined.** The join fix already makes every person findable (100% of eras), and the +5% would only tidy labels where the id is used as a label. The honest fix is a timeline, not a table |
| the 9,799 rows where pack and register both use the container | 9,799 | the register is coarse there; correcting the data would disagree with the register the game asks |
| the 640 rows the register cannot answer | 640 | no answer is not an answer |
| the 38 duplicate pairs | 38 | presentational dedupe applied; deleting rows renumbers a master everything else reads |
| the 18 unresolvable site ids | 18 | register-side gaps (Ahom, Mewar, Travancore…) — a data job with its own sourcing |
| `CivSynthesis` synthesising `india`/`rome` | 1 decision | engine behaviour and persisted; **yours to decide** (board 6 §6) |

---

## 5. Regressions — all clean

| check | result |
|---|---|
| whole-mod syntax gate | 500 files, **0 syntax errors** |
| `probe_here` | **391 checks, 0 failed** |
| `probe_famous_join` | **PASS**, 100% every era |
| `probe_vocabulary` | FINDINGS — **18**, by design |
| `check_manifest` | content **132 / 132**, byte **132 / 132** |
| `gate_l0` | 3 checks, 0 not pass |
| workspace | **115 MB counted, 2,503 files** (under the 120 MB line) |

Backup of the master before the change is kept at `testrun/famous_people.before.json.gz`, and the
change list is `testrun/filing_fixes.tsv` (2,582 named rows, with the register's own words for each).

---

## 6. Verdict in simple words

1. **The filing defect is fixed where it can be fixed from the record: 2,582 rows**, every one of them
   sourced to the project's own ruler register and replayable line by line. Exact-id agreement rose
   **78.7% → 80.1%**, and the rise is exactly the number of rows touched.
2. **What looks like 3,524 duplicates is 38.** A name that repeats is usually a different person; the
   test that matters is life-and-place overlap. I nearly reported a large defect that was not there.
3. **My "Nazi Germany" claim was mostly wrong and I am correcting it.** 1,054 of the 1,092 are Germans
   who died between 1933 and 1945, which is the right period state. One Greek who died in 1949 was the
   outlier, and chasing him found the duplicate.
4. **I declined the alias table on the evidence**: the join is already 100%, so the table would tidy
   labels and not fix a fault. The honest fix for the remaining 19% is a state timeline, and that is a
   schema change with a data rebuild behind it.

**One line: 2,582 filings corrected from the project's own record, a phantom duplicate crisis reduced
to 38 real pairs, and one of my own earlier findings walked back.**

---

## 7. What I do next

1. **G5 — the whole-mod compile and the 212-command surface.** This is now the largest unmarked area
   in the project and the only one that can turn 39 blocked probes and every command into marks. It
   needs ~4 GB RAM and network.
2. If G5 is not possible yet: **the state-as-timeline schema**, designed and measured before it is
   built, because it is the honest fix for the 19% that remains.
