# Marking board 30 — R2-12b closed: every estimate is now a cited date

_2026-10-24. The last three estimate rows were checked against sources. **All six rows in the second register
are now `recorded`, each with a citation** — and four of the six dates changed, because the estimates were
wrong._

## What was checked, and what moved

| polity | estimate before | recorded now | source | change |
|---|---|---|---|---|
| **Zamorin of Calicut** | 1124–1806 | **1124–1806** | "Formation 1124, Abolition 1806" — [Zamorin](https://en.wikipedia.org/wiki/Zamorin) | none |
| **Tomara dynasty of Delhi** | 736–1165 | **736–1152** | "Established c.736, Disestablished c.1152" — [Tomaras of Delhi](https://en.wikipedia.org/wiki/Tomaras_of_Delhi) | **−13 years** |
| **Kolathunadu** | 1100–1800 | **1122–1800** | Udayavarman attested 1122 — [Kolathunadu](https://en.wikipedia.org/wiki/Kolathunadu) | **+22** at the start |
| **Kingdom of Amber** | 1128–1949 | **1028–1949** | "Established 1028; acceded to India 1949" — [Kingdom of Amber](https://en.wikipedia.org/wiki/Kingdom_of_Amber) | **−100 years** |
| **Kangleipak (Manipur)** | 1110–1949 | **1110–1949** | "Foundation of the Kangleipak Kingdom: 1110; merger with India 1949" — [Manipur (princely state)](https://en.wikipedia.org/wiki/Manipur_(princely_state)) | none |
| **Somavamshi dynasty** | 850–1110 | **882–1110** | ruler list Janmejaya I c.882 → Karṇadeva c.1110 — [Somavamshi dynasty](https://en.wikipedia.org/wiki/Somavamshi_dynasty) | **+32** at the start |

**Four of six dates were wrong by between 13 and 100 years.** Amber was a century out.

## The one I could not settle, and how that is handled

**Amber has at least five competing start years in circulation:** 966 (Dausa), 1006–1036 (Dulha Rai's reign),
1028 (the en.wiki infobox), 1093 (Dhundhar founded), 1128 (several mirrors). I did not pick the one I liked —
I used **1028, the year the page's own infobox gives**, and wrote the whole spread into the row's note so the
next reader sees the dispute instead of a false certainty.

The same rule held for two others:
- **Tomara** — c.1152 on the dynasty page, 731–1160 on *Timeline of Delhi*. The earlier year is used, the
  disagreement recorded.
- **Kolathunadu** — the start moved to the first *attestation* (1122), but the **end stays 1800**, which the
  source does not support in so many words ("modern era"). **One unsourced edge remains and is labelled.**

## Why this row matters more than its size

These six polities are the ones the primary register **cannot name at all** — they are the second register's
whole purpose. An estimate in that file is a number the engine will happily place armies and borders on. Now
every one of them is either a cited date or a cited date with its dispute attached.

```
polities_second_register.json : 6 estimates -> 0 estimates
manifest                       : up to date (content hashes match)
/ee check all                  : 426 passed, 12 failed (baseline unchanged)
```

## R2 after this turn

| row | state |
|---|---|
| R2-1 … R2-5, R2-9, R2-11, R2-12a | ✅ done earlier |
| **R2-8 the far end 2026→3000** | ✅ closed (board 29) |
| **R2-12b the six estimates** | ✅ **closed this turn** |
| R2-12 correct answers | **161 real cases triaged** (114 overlord class + 47 smaller), 30 at a time |
| R2-6 cards for every town in the test set | **open** |
| R2-7 news by the day, 50 place-days | **open, Hyderabad only** |

**R2: 11 of 14 rows closed.** Three left: **two builds** (cards, news) and **the 161 hand-checks**.

## Next, in order

1. **R2-6** — a card for every town in the test set (a build, no research).
2. **R2-7** — news for 50 place-days across 10 regions (a build, needs a news source per region).
3. **R2-12** — the 161, in batches of thirty, with the Brzeg recipe.

**R2 cannot be called 100% while 161 polities are known to answer with the wrong name** — and no amount of
closing the other two rows changes that. The 161 is the honest core of R2.
