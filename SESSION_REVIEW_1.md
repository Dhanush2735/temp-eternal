# Session review 1 — a real world, read

_2026-10-23. `newworld.zip` (27.9 MB, 246 files) — a Minecraft save from a real play session with the
mod. This is the first evidence in the whole project that does not come from my own harness. It found
two things no test I wrote had found, and it answered part of G6._

## 1. What the save is

| | |
|---|---|
| world | `New World`, Forge **47.4.10**, Minecraft 1.20.1, Eternal Engine **1.0.0**, Terra++ 2.0.0-alpha, Xaero's map/minimap |
| played | one session, **18,131 ticks ≈ 15 minutes**, saved 2026-10-23 22:14 IST |
| player | creative (`playerGameType: 1`), flew 1,020 m, walked 67 m, picked up 1 wheat seed, never died |
| biomes seen | plains, desert, forest, deep lukewarm ocean |
| the world's own clock | **430 BC** (`state.json: currentYear -430`), one branch, `main` |

**The route, reconstructed from what is in the files** (the mod records the year each person was
stood up for):

| when | where | year |
|---|---|---|
| 22:07 (backup taken here) | **Ur** (30.963 N, 46.103 E) and **Giza** (29.979 N, 31.133 E) | **2500 BC** |
| after | **Anyang** (36.126 N, 114.313 E) | 1200 BC |
| after | a site at **(32.4 N, 69.0 E)** — Pakistan/Afghanistan border | 1200 BC |
| last | back at **Anyang**, clock moved forward | **430 BC** |

So R1, R2 and R4 of the era route were actually walked. Three of the 31 are no longer hypothetical.

## 2. What the session proves

**G6 — no monsters.** Every entity in the world, counted from the region and entity files:

```
   923  eternalengine:human_npc
    82  minecraft:item          30 acacia sapling, 20 wheat seeds, 16 stick, 6 lantern …
     3  minecraft:sheep          1 pig
     0  hostile mobs — no zombie, skeleton, creeper, spider, enderman, witch, pillager, phantom
     0  wandering traders, 0 trader llamas, 0 raids
```

923 people, four animals, **not one monster**, in a world that was played at a real spawn, at night
(day time 22:51 in the save). This is the strongest evidence G6 has had: not a headless post, not a
synthetic event — a saved world. It is still not the *test* (nobody stood outside a town at midnight
and watched), so G6 stays open, but its machine half is now backed by real state.

**R1 Ur, R2 Giza, R4 Anyang — the townspeople are right at the year they were drawn for.**

- **Ur, 2500 BC:** 35 people, `sumer`, named `Gugallu Hammurabi of Babylon`, `Tamkarum Ishtar of
  Nineveh`, `Farmer Adad-guppi bar Sin` — Sumerian/Akkadian name pools by role (artisan, merchant,
  farmer, town crier). The civilization's own record: Sumer, founded 4500 BC, fell 1900 BC. **Inside
  its lifetime.**
- **Giza, 2500 BC:** 216 people, `egypt_ancient`, `Sekhet Nefertari of Thebes`, `Hemuty Hatshepsut
  son of Ra`, `Citizen Khaemwaset of Kush` — Egyptian pools. Egypt: founded 3100 BC, fell 30 BC.
  **Inside its lifetime.**
- **Anyang, 1200 BC:** 13 people, `china_shang`, `Citizen Zhu Chen`, `Merchant Guo Zhang` — Chinese
  pools. Shang: founded 1600 BC, peak **1200 BC** (the year it was drawn for, exactly). **Inside.**

**The money starts right.** The purse is opened with **6 units of `silver_weighed`** — the money
table's Mesopotamian weighed silver, which is what Ur in 2500 BC uses.

**The projection works.** Biomes at the four regions match their real places: desert at Giza, plains
and river at Ur, plains with birch and dark forest at Anyang, plains/desert/savanna at the Afghan
border. An independent check on the block↔lat/lon mapping (fitted through the three registry sites,
then used blind) put the player's logout position at 30.1 N 29.0 E — Egypt, next to Giza, which is
where the previous stop was.

**The mod's save path works.** `state.json`, a timestamped backup, `eternal_people.dat`,
`eternalengine_purses.dat`, `eternalengine_knowledge.dat`, `installed_data.json` with 132 checksums,
`terra_chunk_index` — all present and readable. No corruption, nothing half-written.

## 3. What it fails — two defects, found by playing

Both are the same shape: **the site's civilization is used without asking whether it still exists in
the current year.** The mod has the rule (`Civilization.isActiveInYear`: founded ≤ year < fall) and
does not apply it here.

### D1. Shang-dynasty people in 430 BC (Anyang)

```
29 townspeople at Anyang, civ china_shang, year -430
china_shang: founded -1600, peak -1200, fall -1046     ← it has been gone for 616 years
```

The civ that owns that ground in 430 BC is in the mod's own pack: **Zhou** (founded −1046, fall −256),
and the world state has it active with 10,000,000 people. The people standing there are Shang.

This is R4's question, asked at a year the route did not originally ask: *do the people belong to the
year?* They do not. **R4 fails on this**, and it would have been invisible to every test I could run
headless, because the data is consistent with itself — only a year change exposes it.

### D2. Indus Valley people 100 years after the Indus Valley fell

```
28 townspeople at (32.4 N, 69.0 E), civ indus_valley, year -1200
indus_valley: founded -3300, peak -2200, fall -1300    ← gone for a century
```

### The census of it

Across the whole registry — 285 rows whose civilization is known:

| | rows |
|---|---|
| inside their civilization's lifetime | **228** |
| **after their civilization fell** | **57** (20%) |
| before their civilization was founded | 0 |

57 is not a rounding error, and every one of them is at a site whose civ hint names a civilization
that had already fallen when the clock was moved there.

**D3 (small, real): three civilization ids that resolve to nothing.**

- **13 live NPCs** carry `CivilizationId: "indus_valley_civilization"`. The civ pack's id is
  **`indus_valley`**; `CivHints` maps the hint `indus_valley → "indus_valley_civilization"`, a target
  that exists in no pack and not in the world state. Those people have no resolvable civilization.
  (Related: `sumer → "sumerian_city_states"`, `maurya → "maurya_empire"` — the same table points at
  spellings the pack does not use.)
- **5 live NPCs** carry `CivilizationId: "jin"`, which is in neither the civ pack nor the world state.

**D4 (reported, not yet judged): the purse's start date is a sentinel.** `startDate: -24,999,899`
with `started: 1`. That is not a year anyone can be in. Either it encodes "before the record" in a
way nothing displays, or it is a bug in the opening balance.

## 4. What was nearly a fourth defect, and is not

**865 of the 923 people have no name and `civ: neutral`.** I was one step from filing that as "the
crowd is anonymous". It is not a defect: those 865 all carry the tag **`eternalengine.crowdFigure`**
plus `crowdFigureYear`, `crowdFigureSlot`, `crowdFigurePlan` — they are *drawn crowd figures*, a
visual mass that is meant to be anonymous until a player talks to one, at which point the conversation
turns it into a named townsperson. The 58 with names are the townspeople. **Self-correction 29:
counted 865 unnamed and nearly called it a fault without reading the tag that explains it.**

## 5. What this means for the scorecard

- **G6** — machine half now backed by real save state (0 hostile mobs among 923 entities). Still open.
- **R1, R2** — the data half of both passes on a real world, at the right year, with the right names,
  the right civilization and the right money. Only the *screen* is unjudged.
- **R4** — **FAILS**: at 430 BC Anyang is populated by a dynasty that fell in 1046 BC.
- Two new defects, both in the "site's civ vs the year" seam, neither reachable by my harness.
- Harness defect count: 29. Defect count: **46** (43 + D1..D3; D4 reported only).

## 6. The fix these imply

One rule, in one place: when a site's people are stood up, resolve `civHint` **through the year** —
if the hinted civilization is not alive, ask who owns that ground *in that year* (the border and
ruler layers already answer this, and the answer at Anyang in 430 BC is Zhou). That single change
covers D1, D2 and most of the 57, and the same lookup can validate the dangling ids in D3 instead of
silently keeping them. I have **not** written it yet: it changes who stands where, and I would want
your word before a change of that size — plus the Forge toolchain, which is not in the workspace this
session.
