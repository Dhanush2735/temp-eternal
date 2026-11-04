# The marking board — seventh sitting, 2026-10-22

Continuing boards 1–6. Board 6 ended with the vocabulary invariant at **131 unresolvable ids**. This
sitting read all 88 site ids that were left, one at a time, and closed 70 of them.

---

## 1. The vocabulary now

| | before this sitting | after |
|---|---|---|
| alias rows in `CivHints` | 49 | **87** |
| declared regions (never mapped) | 20 | **57** |
| site hints resolvable (known + alias) | 76 | **114 of 184** |
| **site ids unresolvable** | **88** | **18** |
| **border ids unresolvable** | **2** | **0** |
| **total** | **90** | **18** |

Before the marking began, the number was **131**; it is now **18**.

## 2. The 70 that were closed, and how

Every one was read as a pair — pack id on the left, what the register actually calls it on the right.
Three kinds, and they are genuinely different:

**a) Same polity, different spelling (38 rows).** Mechanical once seen: `awadh → nawab_of_awadh`,
`sikh → sikh_empire`, `vijayanagara → vijayanagara_empire`, `hre → holy_roman_empire`,
`florence → republic_of_florence`, `inca → inca_empire`, `minoan → minoan_civilization`,
`caliphate_abbasid → abbasid_caliphate`, `china_shang → shang_dynasty`, `china_zhou → zhou_dynasty`.

**b) The Deccan sultanates, which needed knowledge rather than string matching** — the register names
them by their capital, the pack by their dynasty:

| pack id | register | why |
|---|---|---|
| `qutb_shahi` | `golconda_sultanate` | the Qutb Shahis ruled from Golconda |
| `adil_shahi` | `bijapur_sultanate` | the Adil Shahis ruled from Bijapur |
| `nizam_shahi` | `ahmadnagar_sultanate` | the Nizam Shahis ruled from Ahmadnagar |
| `imad_shahi` | `berar_sultanate` | the Imad Shahis ruled Berar |

None of these could be found by any string rule — `qutb_shahi` and `golconda_sultanate` share no
characters. They are why the last stretch needed a person.

**c) Declared regions (32 new).** `england`, `france`, `russia`, `spain`, `poland`, `prussia`,
`lithuania`, `maya`, `naples`, `oman`, `mamluk`, `toungoo`, `pallava`, `delhi_sultanate`,
`mapuche`, `tiwanaku`, `dai_viet`, `cheri`… These name **a land over centuries**, and mapping them to
one polity would be a lie told in a new direction. They are listed so a reader can tell
*"deliberately not mapped"* from *"nobody looked"*.

## 3. My own check caught two of my own errors

I wrote a sanity probe that asks a question the vocabulary probe does not: **does every alias land on a
polity that actually exists?** It found two dead rows:

```
DEAD ALIAS  china_song -> song_dynasty     (the register's polity is named "song")
DEAD ALIAS  macedon    -> macedon          (the register has "macedonian_empire")
```

Both were fixed from the register's own polity list. After: **87 of 87 aliases land on a real polity,
0 dead.** This is the second time in three sittings that a verification step caught me rather than the
world — which is the argument for writing the check before trusting the table.

## 4. What is left: 18, and they are not aliases

```
ahom  amber  bhati  bhopal_state  bundela  dogra  holkar  ikshvaku  kandy
kolathiri  ladakh  manipur  marwar  mewar  somavamshi  tomara  travancore  zamorin
```

Each carries **one site**, and each is a real state the ruler register **does not model at all** —
Ahom, Amber, Bundela, Holkar, Marwar, Mewar, Travancore, Kandy. There is no correct alias to write,
because there is no target. The fix is a **register-side addition** (new polities with extents and
dates), not a mapping, and it would be a data job with its own sourcing.

**So `probe_vocabulary` still reports FINDINGS, and should.** A check that goes green by reclassifying
its own failures is worthless; these 18 are named, counted, and left visible.

## 5. What the player sees — and what they do not

The site hint decides an NPC's civilization **only when the ruler register names no ruler** — measured
earlier at **2.1%** of joins. So this fix is **small in the game and large in the code**: it stops the
mod handing `india` and `rome` to anything that asks for a civilization id, and it makes the answer
resolvable for 114 of the 184 hints instead of 76.

The **remaining big one is untouched and still yours to decide** (board 6 §6): `CivSynthesis` still
synthesises `india` and `rome` as civilizations, because it derives from cited ids rather than from
polities. That is the case where the vocabulary problem is *visible* — a subcontinent under one name
for three thousand years — and the three options and their costs are still on that page.

## 6. Regressions — all clean

| check | result |
|---|---|
| whole-mod syntax gate | 500 files, **0 syntax errors** |
| `probe_here` (strictest) | **391 checks, 0 failed** |
| `probe_famous_join` | **PASS** (100% of eras) |
| `check_manifest` (content) | **132 / 132** |
| `gate_l0` | 3 checks, 0 not pass |
| alias sanity | **87 / 87** land on a real polity |

## 7. Gate status

| Gate | Result |
|---|---|
| **G1 L0 static** | **PASS** |
| **G2 L1 probes** | 105 probes; `probe_vocabulary` reports FINDINGS (18), by design |
| **G3 L2 truth** | join fixed; presence sound; vocabulary **114/184 resolvable, 18 open with a named cause** |
| **G4 L3 invariants** | three standing: *an index is not a source*; *no register may cite what it cannot resolve*; *an alias must land on a real polity* |
| **G5 L4 compile** | still blocked — needs ~4 GB RAM and network |
| **G6/G7** | blocked on your jar and world |

---

## 8. Verdict in simple words

1. **The private language is mostly translated.** 131 names the mod could not resolve are now 18, and
   every one of the 113 closed was closed by a decision that can be read and argued with.
2. **The hard ones were not strings.** The four Deccan sultanates needed to be known, not matched —
   `qutb_shahi` is Golconda because the Qutb Shahis ruled from Golconda. A machine would never have
   found those, which is why the automatic derivation was thrown away two sittings ago.
3. **The 18 that remain are named, not hidden**, and they are a register gap rather than a mapping gap.
4. **My table had two dead rows and my own check found them.** That is the machinery working.
5. **The game impact is small (2.1% tier) and the honesty impact is large** — the mod can now ask
   "what civilization is this?" and get an answer it can actually use, most of the time.

**One line: the vocabulary went from 131 unresolvable names to 18 named gaps, and the fix was
judgement, not string matching.**

---

## 9. What I do next

1. **The filing fixes from board 4**, still the largest untouched data defect: ~2,000 people filed
   under a modern container (Q145 United Kingdom for a man who died in 1770), and the 261-pair lineage
   alias table that recovers +5% exact-id agreement.
2. **The 18 register gaps** — add the missing polities with dates and extents, sourced, so the
   vocabulary closes for real.
3. **G5** — the whole-mod compile and the 212-command surface: the largest unmarked area in the
   project, the moment RAM and network are available.
