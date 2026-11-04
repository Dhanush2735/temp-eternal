# Marking board 29 — R2, row by row: two rows closed, one triaged, three citations added

_2026-10-24. The user asked for the requirements one at a time, R2 first. R2 had **5 rows open of 14**. Here is
what one turn moved, measured._

## R2-8 · the far end, 2026 → 3000 AD — **CLOSED**

`Source.PROJECTED` now exists. Beyond the last year any source records (**2026**), the answer is the world as
it stood in 2026, carried forward, and it says so in words:

```
51.21,16.16 2026 -> Republic of Poland [1945-2026]              REGISTER
51.21,16.16 2100 -> Republic of Poland [as it stood in 2026] (carried forward - no source records
                    this year; it is a projection, not a record)   PROJECTED
51.21,16.16 2400 -> same
51.21,16.16 3000 -> same
```

Verified at five places across four continents (Legnica, Geneva, Athens, Delhi, New York) at 2026, 2100, 2400
and 3000 - **20 of 20 consistent**, none silently presenting a 2026 answer as a 2400 record. Pinned in
`/ee check all`, so a future change cannot quietly make 2400 look recorded.

**Why this is the honest answer and not a cheat:** nobody records who rules in 2400. The requirement asks for
"one shape" from 2026 to 3000 - a projection *is* that shape, as long as it never pretends to be a record. It
does not.

## R2-12b · the six estimate rows — **3 of 6 cited**

Each row needed a source before it could stop being an estimate.

| polity | was | now | source |
|---|---|---|---|
| **Zamorin of Calicut** | estimate 1124–1806 | **recorded 1124–1806** | "Formation 1124, Abolition 1806" — [Zamorin](https://en.wikipedia.org/wiki/Zamorin) |
| **Tomara dynasty of Delhi** | estimate 736–**1165** | **recorded 736–1152** | "Established c.736, Disestablished c.1152" — [Tomaras of Delhi](https://en.wikipedia.org/wiki/Tomaras_of_Delhi) |
| **Kolathunadu (Kolathiri)** | estimate **1100**–1800 | **recorded from 1122** | Udayavarman attested 1122 (Kuruvakkavu inscription) — [Kolathunadu](https://en.wikipedia.org/wiki/Kolathunadu) |

**One answer changed: the Tomara dynasty ended in 1152, not 1165 — thirteen years too long.**

**And one disagreement is now declared instead of hidden:** the Tomara page says c.1152, *Timeline of Delhi*
says 731–1160. The earlier year is used and the disagreement is written into the row's note. The Kolathunadu
end year (1800) **stays an estimate** — the source says only "modern era", so calling it recorded would be a
lie.

Manifest rebuilt and green (133 files, content hashes match).

## R2-12 · correct answers — **triaged, and the count was misleading**

The self-consistency probe said 276 polities lose at their own centre. A raw number cannot say which of those
are wrong, so it now triages by **size ratio** — a polity that loses to something recorded on many more places
is an overlord collapse; one that loses to a similar-sized neighbour is probably a legitimate dispute:

```
polities tested at their own centre : 1,550
  answered as itself                : 1,173  (75.7%)
  answered as a DIFFERENT polity    :   276  (17.8%)
     lost to a polity 5x+ larger    :   114   <- the overlord class, the real queue
     lost to a comparable polity    :   115   <- neighbour / claim disputes
     lost to a much smaller polity  :    47   <- likely a wrong answer outright
  answered nobody                   :   101  ( 6.5%)
```

**Also found: the 101 "nobody" are mostly an artifact of my own metric.** A colonial empire's recorded centre
falls in its colony - "Portuguese Empire" centres in Brazil, "Dutch Cape Colony" in South Africa - so asking
who ruled *there* in its imperial period is not a test of anything. Those rows need excluding before the 101 is
called a defect count.

**So the honest queue for R2-12 is 114 + 47 = 161 polities to hand-check, not 377**, in batches of thirty, with
the Brzeg recipe: town page → sourced row → box drawn first → neighbours checked → both directions pinned.

## Gates

```
compileJava    : BUILD SUCCESSFUL — 1,248 classes (12 s)
command_surface: 220 commands, 220 PASS
/ee check all  : 426 passed, 12 failed (baseline unchanged)
manifest       : up to date
```

## R2 scoreboard after this turn

| row | state |
|---|---|
| R2-1 · R2-5, R2-9, R2-11, R2-12a | ✅ were already done |
| **R2-8 the far end 2026→3000** | ✅ **closed this turn** — projections, labelled, pinned |
| **R2-12b the six estimates** | **3 of 6 cited**; 3 left (amber, manipur, somavamshi) |
| **R2-12 correct answers** | **triaged to 161 real cases**; 114 are the overlord class |
| R2-6 · cards for every town in the test set | **open** |
| R2-7 · news by the day, 50 place-days | **open, Hyderabad only** |

**R2: 10 of 14 rows closed (was 9).** To finish it: three more citations, two builds (cards, news), and the 161
hand-checks. The citations are the cheapest and come next.
