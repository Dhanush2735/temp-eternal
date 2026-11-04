# The marking board — fifth sitting, 2026-10-22

Continuing boards 1–4. The fourth sitting made the famous-people join green. This sitting ran the
same audit on the **other** id joins: `presence → person` and `site → polity`.

Two corrections to my own work come first, because a marker who hides his mistakes is worth nothing.

---

## 1. Two corrections, both mine

**(a) I introduced a regression while fixing the last one.** My new geographic tile groups (`g/…`)
were picked up by `FamousPeople.all()`, which streams every group except `b/`. Result:
**368,120 people returned for a master of 184,060 — every person twice.** My own join probe caught it
on the next run. Fixed: `all()` now excludes `g/` as well, and says why in a comment (*an index is not
a source*). After the fix: **184,060**, correct.

**(b) I measured a join that does not exist.** My "Join A" asked `Presence.of(person.row())` — a row
index — against a file keyed by **Wikidata Q-number**, and reported "62% of stays fall outside the
person's life". That number was meaningless: nothing in the mod reads presence by row. The only
caller is `PlaceCards`, with `Presence.stayNear(card.qid(), …)` — a real Q-number. **Rebuilt the test
the way the code actually works**, and the join is sound.

---

## 2. Join A — `presence → person` — **sound**

The real path: `PlaceCards → Presence.stayNear(card.qid(), …)`, and `presence.json` is keyed by QID
(maximum id seen: **141,735,387** — a Q-number, not an index), so both sides are the same id space by
construction.

Spot-check on well-known people — do the stays filed under a QID overlap the life on that person's
card?

| person | qid | life | stays | result |
|---|---|---|---|---|
| Hammurabi | 36359 | −1810…−1750 | 2 | **ok** |
| Genghis Khan | 720 | 1162…1227 | 2 | **ok** |
| Napoleon | 517 | 1769…1821 | 10 | **ok** |
| Christopher Wren | 170373 | 1632…1723 | 10 | **ok** |

4 of 4 overlap; 24 dated stays, none impossible.
**Mark: PASS (spot check, 4 people — not a rate).**

---

## 3. Join B — `site → polity` — **broken for 96% of sites**

A gazetteer site carries a `civHint`; the rest of the mod treats that string as a civilization id.
The ruler register keeps its own vocabulary. Measured over all 46,864 sites that carry a hint:

| | hints | sites |
|---|---|---|
| resolvable to a polity the register knows | 28 of 184 | 1,698 (**3.6%**) |
| **not resolvable** | **156 of 184** | **45,166 (96.4%)** |

The largest offenders, and they are **pack ids, not polities**:

| sites | site hint | what it really is |
|---|---|---|
| 15,729 | `india` | a pack, covering every Indian polity from the Vedic period to 1947 |
| 10,745 | `rome` | a pack, covering kingdom, republic and empire |
| 4,547 | `china_tang` | a pack id; the register's polity is `tang_dynasty` |
| 2,314 | `china_han` | same |
| 1,142 | `byzantium` | same |
| 977 | `sasanian` | same |
| 684 | `sparta` | same |

The register's vocabulary, for contrast: `abbasid_caliphate`, `achaean_league`, `aetolian_league`,
`ahmadnagar_sultanate` … — polity slugs, 1,567 of them.

**Why it has not been catastrophic:** `HistoricalPresence.spawnCivId()` asks the **ruler first** and
the site second. So the site's unresolvable hint only decides anything when the register names no
ruler — the 2.1% tier. The other consumer, `CivSynthesis`, is not so lucky: it builds a civilization
table **from the site hints themselves**, so `india` and `rome` can appear there as if they were one
civilization each.

**Mark: FAIL as a vocabulary; LOW impact as a spawner, because it is masked by the ruler register.**

### The fix, and why the obvious version is wrong
The obvious fix — map `india → (some polity)` — is **wrong**, because `india` is not one polity:
the same site is Maratha in 1700 and Mauryan in 250 BC. The correct handling:

1. **Never let an unresolvable hint stand in for a civilization.** Treat these 156 as **region ids**,
   which is what they are. Where a civilization is needed, ask the ruler register (already the order).
2. **A short alias table for the unambiguous ones** — a pack id that *does* name one polity:
   `rome → roman_empire`, `china_tang → tang_dynasty`, `china_han → han_dynasty`,
   `china_song → song_dynasty`, `byzantium → byzantine_empire`, `sasanian → sasanian_empire`,
   `parthia → parthian_empire`, `sparta → sparta`, `macedon → macedon`… roughly 20 rows, not 156.
3. **The ambiguous ones must be resolved by year**, by the register — which already does that well.

---

## 4. Gate status

| Gate | Result |
|---|---|
| **G1 L0 static** | **PASS** — 0 syntax errors; packs parse; manifest content **132/132** |
| **G2 L1 probes** | **104 probes**, of which 102 green, plus `RegisterJoinProbe` + `SiteHintProbe` now running here |
| **G3 L2 truth** | famous join **fixed**; presence join **sound**; site→polity **96.4% unresolvable** (new, open) |
| **G4 L3 invariants** | "an index must not be listed as a source" — a **new standing invariant**, learned by breaking it |
| **G5 L4 compile** | still blocked — needs ~4 GB RAM + network |
| **G6/G7** | blocked on your jar and world |

---

## 5. Verdict in simple words

1. **The presence register is fine.** It joins on Wikidata ids on both sides, and the famous people
   whose stays I checked are at places they could plausibly have been, in years they were alive. My
   earlier "62% impossible" was my mistake, and it is worth saying plainly: **I measured the wrong id
   and got a frightening, meaningless number.**
2. **The site register speaks a different language from the ruler register.** 96 times in 100, a site
   names its land with a **pack id** — `india`, `rome`, `china_tang` — that the register has never
   heard of. It is masked because the ruler is asked first; it is not masked in `CivSynthesis`.
3. **I broke `all()` and my own probe caught it in the next run.** That is the system working — and
   also a warning: a change that looks local touched a reader two files away. Every claim in these
   four boards now rests on probes that are re-run after each change, and that is the only reason
   this regression was found in minutes instead of by you, in the game.

**One line: the people register is honest, the place register speaks its own private language, and
the fixed join is now guarded by a probe that has already earned its keep.**

---

## 6. What I do next

1. **The 20-row alias table** for unambiguous pack ids, applied where `site.civHint()` is read as a
   civilization id — small, mechanical, and it also stops `CivSynthesis` inventing `india`.
2. **A standing invariant probe**: *no register may use a name it cannot resolve* — run over sites,
   borders and events, so the next pack cannot reintroduce a private vocabulary silently.
3. **The filing fixes** from board 4 that are still open (~2,000 modern-container rows; the 261-pair
   lineage alias).
4. **G5** — the whole-mod compile and the 212-command surface — the largest area still unmarked, the
   moment RAM and network are available.
