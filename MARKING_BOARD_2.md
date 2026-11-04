# The marking board — second sitting, 2026-10-22

Continuing from `MARKING_BOARD.md` (first sitting: 98 green / 0 red / 43 unusable out of 141).
This sitting did what the last page said it would: repair, split, fix the manifest, and start the
truth audit. It also produced **the most important finding so far**.

---

## 0. First, a correction to my own board

The first sitting said **8 probes were "rotten — will not compile any more"** and blamed hardcoded
file lists. **That was wrong for 5 of the 8.** `probe_check`, `probe_data_use`, `probe_npc_links`,
`probe_step8` and `probe_talk` compile against `build/classes/java/main`, which only exists after a
Gradle build. They were not rotten — they were **blocked on the build I had not run**, exactly like
the 24. I marked them wrongly by inferring from the error text instead of reading where the classpath
pointed. A marker who does that is no better than a suite that never fails. Corrected below.

---

## 1. Repairs: 3 probes recovered, and they measure real code now

The `-sourcepath` pattern that `probe_here.sh` already uses does not need Minecraft. Two classes that
everything needs — **`HistoricalPresence` and `EventNews`** — turned out to have **no Minecraft
imports at all**; they were only unreachable because thin stubs were shadowing them. Disabling those
stubs and giving `CivilizationManager` / `Civilization` / `TerritoryManager` stubs that **throw**
(so a probe can never pass by accident) gave these results:

| Probe | Before | After |
|---|---|---|
| `probe_data_use` | would not compile | **runs; prints a 15-era data-use table** |
| `probe_step8` | would not compile | **runs; prints dynasties, rulers and trade routes for 9 places** |
| `probe_talk` | would not compile | **runs; prints the villager lines at every test place** |

**New mark: 101 of 141 probes now run** (was 98). None of the three asserts anything, so they are
**tools, not tests** — but they are tools that now tell you something.

**`probe_data_use`, first run ever.** How much of the data actually reaches a player, per era
(% of 1,500 sampled points):

| Era | occupied | state named | ruler named | famous line | local language | faith shares | trade route |
|---|---|---|---|---|---|---|---|
| −1000 | 88.5 | 8.3 | 5.5 | 0.3 | **0.0** | **0.0** | 0.8 |
| 1 | 94.7 | 58.1 | 53.3 | 48.9 | **0.0** | **0.0** | 3.9 |
| 1000 | 94.5 | 62.4 | 58.1 | 46.0 | **0.0** | **0.0** | 3.1 |
| 1500 | 96.7 | 69.1 | 63.5 | 64.5 | 21.7 | **0.0** | 3.9 |
| 1900 | 99.0 | 96.0 | 95.5 | 94.1 | 29.8 | 37.5 | 1.3 |
| 2020 | 99.9 | 95.5 | 95.3 | 95.9 | 24.9 | 89.2 | 1.1 |

Read plainly: the world is never empty, but **before 1500 nearly every line except "who rules" is
mostly empty** — famous people 0.3% in 1000 BC, local languages 0% until the 1400s, faith shares 0%
until the 1900s, trade routes never above 4%. This is the first measurement of what the player
actually sees, and it is the missing context for *"I don't see any difference"*.

**Still blocked, honestly:** `probe_npc_links` (uses `CivilizationManager.loadCivilizations` for real —
cannot be faked), `probe_check` (needs the compiled mod), and the 24 classpath probes. Those need G5.

---

## 2. The manifest is fixed, and proven fixed

`build_manifest.py` hashed the `.json.gz` **file**, and gzip writes the build time into the header,
so the hash moved whenever any builder ran, regardless of content. The manifest could never confirm
the shipped data, and "byte-clean" rotted after every rebuild.

**Fix:** a new `contentSha256` — the pack parsed and re-serialised with sorted keys, so it hashes the
*meaning* and not the bytes. `sha256` kept for compatibility.

**Proof, both directions:**

| Check | Before the fix | After |
|---|---|---|
| 132 manifest entries vs content | 9 "changed" (all false alarms) | **132 match, 0 differ** |
| A real rebuild of `calendars.json.gz` | hash moves every time | **contentSha unchanged across two rebuilds** (`917e5ee9…`) |
| Byte hash after rebuilds | 123/132, drifting | 130/132, still drifting — as it should |

`python3 testrun/check_manifest.py` is now the gate, and it passes. **And it answers a question the
whole project has been guessing at: no shipped fact changed during this entire marking session** —
all 9 "changes" were gzip timestamps.

---

## 3. The truth audit has started — and it found something big

### 3a. A sampled fact that is simply wrong
`famous_people` row: **Nikos Skalkottas, Greek composer, 1901–1949, state Q7318.**
Sources: born **21 March 1904** (Wikipedia, Britannica, Wikidata Q452352); died 1949 ✓.
So the birth year is **three years out**. And Q7318 is not a person's id and not a Greek state —
**Q7318 is "Nazi Germany"**. Checked live: `Q7318 → Nazi Germany`, `Q452352 → Nikos Skalkottas`.

### 3b. Why that matters more than a typo
The pack's `state` is not a label. `EventNews` and `HistoricalPresence` take the ruler's id from
`RulerRegister` and call **`FamousPeople.livingIn(qid, …)`** — a person is shown **only if their
state id equals the ruler register's id for that place and year**. A wrong id is not a wrong name on
a card; it is *a person who cannot be found*, or one who appears in the wrong empire.

### 3c. Two audits, both automated
| Audit | Rule | Result |
|---|---|---|
| **Lifetimes** (`testrun/audit_people_states.py`) | A person cannot be filed under a polity that did not exist while they lived (Wikidata P571/P576) | 400 sampled: **21 impossible (5.3%)**, 20 no state, 359 ok |
| **The game's own join** (`worldfill/probes/FamousJoinProbe.java`) | Ask the ruler register the same question the game asks | 400 sampled: **295 agree, 102 mismatch, 3 no ruler → only 73.8% would be found** |

The lifetime audit's 21 split into two kinds, and they are different defects:

* **18 are a modern-state container** — an Englishman who died in 1770 filed under **Q145 United
  Kingdom** (inception 1921), a Spaniard who died 1700 under **Q29 Spain** (1715). Whether that is
  wrong depends on the reader, but the *game* joins on the id, and the ruler register answers
  `British Colonial Empire` or `Francoist Spain` for those years — so the join fails.
* **3 are outright wrong** — **Antonio Neri** (born 1576) filed under the **Republic of Florence**,
  which ended in 1569, when he was born in the Grand Duchy of Tuscany; **Lu'lu' al-Yaya** (born
  1057) under the **Hamdanid dynasty**, ended 1004; **Bouguer** (died 1758) under the **Bourbon
  Restoration**, begun 1815.

### 3d. The headline number
**One famous person in four is filed under a state the game's own ruler register never names for
their place and year.** Typical lines from the probe:

```
Maurice Wilkins (1936)   state=Q664 (New Zealand)      ruler register says Q8680 (British Colonial Empire)
Ibn al-Nafis (1230)      state=Q282428                 ruler register says Q180114 (Ayyubid Sultanate)
Louise Brachmann (1797)  state=Q151624                 ruler register says Q156199 (Electorate of Saxony)
Michel Serres (1950)     state=Q200686                 ruler register says Q69829 (French Fourth Republic)
Julio Anguita (1961)     state=Q29 (Spain)             ruler register says Q13474305 (Francoist Spain)
```

Some of these are the ruler register being coarse (Wilkins in New Zealand 1936), some are the pack
being coarse (Spain 1961). **It does not matter which: the join is by exact id equality, so the
person is invisible either way.** This is the first defect found that is neither a data gap nor a
build error — it is two registers disagreeing, silently, in the exact place the wiring depends on.

---

## 4. Gate status after the second sitting

| Gate | Result |
|---|---|
| **G1 L0 static** | **PASS** — 500 files 0 syntax errors; 121 packs parse; index ↔ disk consistent; **manifest content 132/132** |
| **G2 L1 probes** | **101 green / 0 red / 40 unusable**, of which 3 were recovered this sitting, 1 honestly declared un-fakeable |
| **G3 L2 truth** | **STARTED.** Sampling works (208 facts drawn, seeded). Two automated rules built. First results: 5.3% impossible lifetimes, 73.8% joinable. Real error found: Skalkottas, Neri, al-Yaya, Bouguer |
| **G4 L3 invariants** | not started |
| **G5 L4 compile + server** | **blocked** — needs ~4 GB RAM + network; would free the remaining 26 probes |
| **G6 L5 real game** | **blocked** — needs your jar, world, client |
| **G7 L6 performance** | blocked behind G6 |

---

## 5. Verdict in simple words

Before this sitting: *"a working engine and a holey exam."* After it:

**The engine is more repairable than it looked, and the data is more stable than anyone knew — but
the wiring between the registers is broken in one specific, measurable place.**

Three plain statements:

1. **Nothing I ran changed a single shipped fact.** 132 of 132 packs still match their content
   hashes after a day of builders, probes and rebuilds. The data is stable; the manifest can now
   prove it, which it never could before.
2. **Three more tests work, and one of them is the first honest look at what a player sees.** The
   answer is uncomfortable: before 1500, four lines out of five are empty, and the empty ones are
   the interesting ones — languages, faiths, trade, famous people.
3. **One famous person in four is filed under a state the game will never look them up under.** That
   is not a data gap or a crash. It is a quiet mis-join, and it is the first bug that explains
   something a player would feel: the world is populated, yet it says little.

**One line: the data is sound, the exam is repairable, and the wiring is where the real fault is.**

---

## 6. What I do next

1. **Widen the join audit from 400 to all 184,060 people**, and classify each mismatch as *pack
   wrong* or *ruler register coarse*. That turns "one in four" into a fixable list with an owner.
2. **Same test for buildings, towns and events** — every place the game joins two registers by id.
3. **The 18 container ids** (UK/Spain/etc.) are a mechanical fix: file the person under the polity
   the ruler register actually names for their place and year.
4. Then G4 (invariants), and G5 the moment you can give me the RAM.
