# Reading the world you sent (newworld1.zip)

_2026-10-24. The save is the same world as the one read on board 16 — `savedAt` is identical,
2026-10-23 16:44:28 UTC — but this copy includes the `region/` folder (67 MB of terrain) that the
first one was missing, so for the first time the ground itself can be read and not only the people._

## What the save contains

| | |
|---|---|
| world | `New World`, overworld, player in creative |
| the clock | **430 BC** (`eternalengine/state.json → currentYear = -430`), 0 ticks into the year |
| the player | block **4,279,265 / -3,412,291** = **Athens**, standing where R5 is walked |
| saved | 2026-10-23 16:44:28 UTC (before any of the board-17 repairs) |
| terrain | 53 region files, 67.9 MB, in **six** places |
| people | **923 `eternalengine:human_npc`**: 866 crowd figures (no civilization by design) + **57 townspeople** carrying a civilization |
| mobs | 3 sheep, 1 pig, **no hostile mobs** |
| the player's own movement | walked 67 m, sprinted 14 m, flew 1,020 m, jumped 7 times — a short visit, not an exploration |

## The six places, and what is standing in each

Read from the chunk files themselves (biome palette, entity list, and the `presenceYear` the mod
stamps on every person it thinks with):

| cluster (region files) | biome says | people | the year they were drawn | civilizations | verdict |
|---|---|---|---|---|---|
| `r.8357/8358.-6665` | plains, meadow | **0** | — | — | **Athens — where the player is standing, with nobody in it** |
| `r.9488/9489.-4777` | desert, river, savanna | 666 | 632 undated + 34 at **2500 BC** | 627 neutral + **39 egypt_ancient** (−3100..−30) | **Giza (R2): correct.** Egypt was alive in 2500 BC |
| `r.16750/16751.-5078` | desert, savanna, sparse jungle | 147 | 134 undated + 13 at **1200 BC** | 134 neutral + **13 `indus_valley_civilization`** | **Mohenjo-daro (R3): broken id.** No civilization has that name (the pack calls it `indus_valley`) |
| `r.23056/23057.-11617` | plains, birch forest, dark forest | 110 | 105 undated + 5 at **430 BC** | 105 neutral + **5 `jin`** | **Anyang (R4): broken id, at the wrong year.** `jin` is a ruler-register spelling, not a civilization, and the Shang had fallen in 1046 BC |
| `r.1634/1635.885` | deep lukewarm ocean, plains | 0 | — | — | the world's spawn area, in open sea |
| `r.12330.-4963/-4965` | desert, plains, windswept hills | 0 | — | — | a desert site with two dropped items (an apple) and nobody |

**So the route walked was R1 → R2 → R3 → R4 → R5**, and the world stopped at R5 with the player in
Athens and the clock at 430 BC. That is consistent with everything in the earlier reports and settles
the open question of how far the last session got.

## The defect, measured on this save

Of the 57 people who carry a civilization at 430 BC:

```
      39  egypt_ancient              (−3100..−30)     alive in 430 BC  — right
      13  indus_valley_civilization  not a civilization in any pack    — wrong
       5  jin                        not a civilization in any pack    — wrong
```

**18 of 57 — 32% of the named people — carry an id that resolves to nothing.** That is exactly
D3 of board 16 (13 + 5), and the two places it happens (the Indus site at 1200 BC, Anyang at 430 BC)
are exactly D1 and D2. The census said 57 of 285 rows; the save says 18 of 57 people. Both are the same
defect, seen from two ends.

## The one new finding

**Athens has terrain and no people.** The player is standing on it, the chunks exist (1.6 MB + 1.4 MB
of region), and the entity files for those two regions are empty. Two explanations are possible and
they need the game to tell apart:

1. the save was taken seconds after the teleport, before the crowd had been drawn (the movement stats
   — 67 m walked, 1 km flown — point this way); or
2. the crowd was never drawn there at all.

On load, a crowd is stood up within a second or two where a player is. **Loading this world with the
fixed jar and doing nothing else will answer it**: if people appear at Athens, it was timing; if the
square stays empty, it is a defect worth its own probe.

## What this save cannot tell us, and what would

The repairs of board 17 are **not in this world**: it was saved before them, and every person keeps the
id they were given at spawn. Booting it with the fixed jar is the test that matters:

- the 13 `indus_valley_civilization` people should be given `indus_valley` or an honest `neutral`;
- the 5 `jin` people should be given **`china_zhou`** (Zhou, −1046..−256) — Anyang in 430 BC;
- and `/ee check all` should then read *"Nobody stands after their own civilization fell: 57 person(s)
  … every one of them inside its years"* instead of naming 18.

That is a 20-minute job from here (the Forge cache does not survive between sessions), and it is the
first thing I would do with this file.

## A trap in the workspace, found while checking this

`eternal/artifacts/eternalengine-1.0.0.jar` — 901 KB, 343 classes, built **2026-09-23** — is a stale
artifact. It does not contain `HistoricalPresence`, `WhoBelongsHere` or `EeStopTest`, so it predates
the whole defect hunt. **Do not install it.** The jar that carries the fixes is the one
`sh ./gradlew build` writes to `eternal/build/libs/` (last known sha256
`689b659d98944ac42547f5d9106be8caedfa70a721c4dbebb74df93bee487922`).
