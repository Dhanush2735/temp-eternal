# The marking board — sixth sitting, 2026-10-22

Continuing boards 1–5. Board 5 ended with: **96.4% of site civHints are ids the ruler register has
never heard of.** This sitting built the resolver, wired it, and wrote the invariant that stops it
coming back.

---

## 1. What was tried first, and rejected

The obvious move was to **derive** the alias table: for each unknown hint, ask the register what it
names for the sites carrying it, and take the answer. Run over all cited ids, it produced:

```
hittite            -> union_of_soviet_socialist_republics   100%
hawaii_kingdom     -> united_states_of_america             100%
mississippian      -> united_states_of_america              92%
numidia            -> people's_democratic_republic_of_algeria 100%
```

**Every one of those is wrong, and they are wrong for one honest reason:** a site record does not say
*which years its hint applies to*, so the question was asked of the wrong year and answered by the
modern state that holds the ground today. **A table derived from a question that cannot be answered is
worse than no table**, so it was thrown away. That is recorded in the source, above the table.

## 2. What was built instead — a generator that proposes, a person who decides

The one objective question that *can* be asked is: **"is there exactly ONE register id containing this
string?"** It was run over all cited ids; its output was then read row by row. Four proposals were
rejected and the reasons are written into the file:

| proposed | rejected because |
|---|---|
| `rome → prome_kingdom` | "rome" is a substring of "prome". Kept as `roman_empire` |
| `japan_kamakura → japan` | Kamakura, Muromachi and Tokugawa are not one polity; `japan` is a country id |
| `pallava → late_pallava_empire` | only the *late* empire matched; the early one is not this |
| `hittite`, `hawaii_kingdom`, `mississippian` → a modern successor | the nearest match is the modern state, which is not what the pack means |

**`civilization/CivHints.java`** — 49 aliases, in two blocks (hand-written, then generator-proposed
and kept), plus a `REGIONS` set of ids that are **deliberately never mapped**. Every alias is checked
against the register **at use**: if the register does not carry the target, `resolve()` returns empty
rather than a name that does not exist.

**Why the regions are not mapped, in one line:** `india` is the Mauryas in 250 BC and the Marathas in
1700; `rome` is a kingdom, a republic and an empire. **No single alias is honest for them** — only the
year is, and the ruler register already answers by year.

## 3. Wired where it matters

`HistoricalPresence.spawnCivId()` — the branch that decides an NPC's civilization when **no ruler is
named** — used to return the site's raw pack id. It now goes through `CivHints.resolve(...)`, falling
back to the raw id when nothing can be resolved.

## 4. The invariant, measured before and after

`worldfill/probe_vocabulary.sh` — *no register may cite an id the rest of the mod cannot resolve*:

| kind | hints | occurrences | known | aliasable | region | **UNKNOWN** |
|---|---|---|---|---|---|---|
| site, before | 184 | 46,864 | 28 | 19 | 16 | **121** |
| **site, after** | 184 | 46,864 | 28 | **48** | **20** | **88** |
| border, before | 16 | 16 | 1 | 3 | 2 | **10** |
| **border, after** | 16 | 16 | 1 | **11** | **2** | **2** |

**Unresolvable ids: 131 → 90.** Borders are nearly clean (2 left). The site vocabulary is 48% classified.

**Not zero, and I will not pretend otherwise.** The remaining 88 are the awkward ones — Deccan sultanates
and minor Indian states (`delhi_sultanate`, `qutb_shahi`, `bahmani`, `awadh`, `bhopal_state`,
`caliphate_abbasid`) where the register's spelling does not contain the pack's, so neither rule can
reach them without a person reading the pair and deciding.

## 5. Regressions — all clean

| check | result |
|---|---|
| `syntax_gate.sh` on the two edited files | **0 syntax errors** |
| `probe_here` (the newest, strictest probe) | **391 checks, 0 failed** |
| `build_manifest.py` | 132 files, **0 without a licence** |
| `check_manifest.py` | content **132/132** |
| `gate_l0.py` | 3 checks, 0 not pass |

## 6. One thing I did not change, and why it needs your decision

`CivSynthesis.reconcile()` synthesises a civilization for **every** cited id — including `india` and
`rome`. So those two still exist in the running game as single civilizations covering a subcontinent
for three thousand years. I did not touch it, because:

* it is **engine behaviour**: every synthesised civilization becomes a region each engine iterates;
* it is **persisted** (the class's own comment worries about a second boot synthesising again);
* changing it changes what the player's NPCs are, which is your call, not a test's.

**The options, and what each costs:**

| option | change | cost |
|---|---|---|
| leave it | nothing | NPCs in the 2.1% no-ruler tier are "india" for three millennia |
| stop synthesising region ids | one filter in `reconcile` | they fall through to the ruler register or to no civilization; needs a live run to judge |
| synthesise **per era** | split `india` into its periods by year | correct, and a data build |

## 7. Gate status

| Gate | Result |
|---|---|
| **G1 L0 static** | **PASS** — 0 syntax errors; packs parse; manifest content **132/132** |
| **G2 L1 probes** | **105 probes**; `probe_vocabulary` added |
| **G3 L2 truth** | famous join fixed; presence join sound; site vocabulary **48% classified, 88 open** |
| **G4 L3 invariants** | two new standing invariants: *an index is not a source*; *no register may cite a name it cannot resolve* |
| **G5 L4 compile** | still blocked — needs ~4 GB RAM + network |
| **G6/G7** | blocked on your jar and world |

---

## 8. Verdict in simple words

1. **The alias table exists, it is small, and it refuses to guess.** 49 rows, each checked against the
   register when it is used. The rows a machine proposed were read by hand; four were thrown out, and
   the file says which and why.
2. **My first method was wrong and I threw it away rather than ship it.** Deriving aliases from the
   data gave "hittite → USSR", because a site does not record which years its hint covers. That answer
   was confident, tidy and false — the exact failure mode the marking is supposed to catch.
3. **131 unresolvable ids are now 90**, and the two remaining border ids are named. What is left is not
   mechanical: those pairs need a person to read them.
4. **Nothing regressed.** The strictest probe still passes 391 of 391 and the manifest still verifies.
5. **One real decision is now waiting for you**: whether `india` and `rome` should keep existing as
   single civilizations in the running game. That is design, not testing, and I have laid out the three
   options and their costs.

**One line: the vocabulary is half fixed and fully measured, the guessing was caught and rejected, and
the one thing left needs a decision only you can make.**

---

## 9. What I do next

1. **The remaining 88**, in the order they cost: the Deccan and Indian sultanate spellings (a person
   reads the pairs; ~30 rows would cover most of them).
2. **The filing fixes** still open from board 4: ~2,000 modern-container rows, the 261-pair lineage
   alias.
3. **G5** — the whole-mod compile and the 212-command surface — the largest unmarked area, the moment
   RAM and network are available.
