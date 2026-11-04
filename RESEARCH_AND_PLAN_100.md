# Research + plan for 100%

_2026-10-24. Five pieces of research — two in the workspace, three on the web — and the plan they produce.
The research changed the plan in three places, so it comes first._

---

## Part 1 — What the research found

### Finding 1 — Terra++ was **built to be driven by this mod**, and the rupture is already written

The fork in `terra3/src/main/java/net/buildtheearth/terraplusplus/generator/historical/` holds 19 classes
(7,897 lines) that the mod's jar does not contain:

| class | what it is |
|---|---|
| `WorldLineRegistry` | the branch registry: `getActiveBranchId()`, `getBranches()`, `createBranch(id, parent, divergenceYear, …)`, `setActiveBranch(id)`, `save/load(worldRoot)` |
| **`WorldLineRegistry.BranchEffects`** | an interface whose javadoc says: *"Implemented by an external driver (**Eternal Engine's timeline/event system**) to give a branch meaning derived from real divergence events"* — two methods: `estimatedYearOffset(lat, lon)` and `structureExists(osmId, lat, lon)` |
| `WorldLineRegistry.setBranchEffects(branchId, effects)` | the registration point, public and static |
| `ParadoxEngine` (295 lines) | `onBlockBreak(BlockEvent.BreakEvent)`: breaking a dated block in the past accumulates per-player temporal stress with lazy decay; past a threshold `ParadoxMath.ruptures(now)` fires and **`rupture(...)` creates the next free universe and casts the player into it** |
| `TerraWorldLineCommand` | `/terra worldline status · paradox · branch list/create/switch · universe list/travel/forge` |

**So R6's rupture (R6-1) is not a thing to implement. It is a thing to build and test.** And R5's land link
(R5-5) has a purpose-built hook waiting for exactly our timeline system.

### Finding 2 — the mod compiles against the **wrong** Terra++ jar

`eternal/libs/terraplusplus-2.0.0-alpha.jar` — 423 classes — is upstream Terra++. Checked directly:

```
generator/TerraChunkGenerator        present
generator/osm/OsmStructureIndex      present
generator/UniverseTransforms         MISSING   <- fork addition
generator/historical/…  (19 classes) MISSING   <- fork addition
```

So the `historical` package cannot be called today. Three routes, in order of cost:

| route | what | cost | risk |
|---|---|---|---|
| **A. supplement jar** | compile the fork's `historical/` + `UniverseTransforms` + whatever closure they need against (alpha jar + Forge classpath) into a small jar, add to `eternal/libs/` | 1 spike + 1 step; the 19 files import only `TerraChunkGenerator`, `UniverseTransforms`, `OsmStructureIndex` from the fork | closure may be larger than those three; a shim may be needed |
| **B. build the fork** | `terra3/` is a full Gradle project at MC 1.20.1 — the **same version as the mod**, so its Forge artifacts may reuse the existing cache | 1 spike; 15–45 min if the cache is warm, ~1 h cold | Forge setup + `mc/` is a folder of API dumps (`.txt`), not a working userdev cache |
| **C. upstream** | ask the Terra++ project for a public hook | unknown wait | not in my control |

**This is a measurement, not a decision** — spike S4 below runs route A for ten minutes and reports the
closure size. That number decides A or B.

### Finding 3 — the P1 substitute exists, with one honest limitation

Headless rendering of a saved world is a solved problem: **Minecraft Overviewer** renders region files from
the command line, no client, no server, one command (`overviewer.py <world> <out>`), 1.20+ support in the
maintained community fork [4][22].

**Its documented limitation matters and I will state it every time:** *"The Overviewer will render the world,
but none of the blocks added by mods will be visible"* [5]. For this project that is acceptable — the palette
measured in the user's own save was **vanilla only** (air, deepslate, lava, stone, bedrock, grass, oak/birch/
dark-oak logs and leaves). Where the mod does use its own blocks, they would render as unknown; the mitigation
is a small custom block-texture map, and the fallback is that the image shows structure, not materials.

**What it buys:** screenshots of Athens, Anyang, Giza and the Indus site produced by me, from the save files,
repeatable, before and after a change. **What it does not buy:** the player's eye, lighting, or fps.

### Finding 4 — vehicles are from zero

`EternalEngineEntities` registers exactly two entity types: `human_npc` and `rival_variant`. R4's vehicle row
(carts, chariots, horses, camels, elephants, boats, ships, trains, trams, cars, buses, bicycles, planes)
has **no partial implementation to build on** — caravans and ships exist as off-screen records only.

### Finding 5 — the toolchain does not survive between sessions

Measured this session: after the workspace snapshot, `~/.cache/jdk17` and `build/gradle-home` are **gone** —
both directory names are excluded from the snapshot. The consequence for planning:

- every working session starts with `provision.sh` + Gradle/Forge warm-up: **~10–15 min** before the first
  compile;
- the caches cannot be moved into the snapshot: a JDK is ~180 MB and the Forge cache ~1 GB, against a
  **128 MB workspace budget**.

So the real unit of work is **one session = setup + 2–4 steps**, not "one step, whenever".

---

## Part 2 — What that does to the feasibility estimates

| # | requirement | before research | now | what moved it |
|---|---|---|---|---|
| 1 | Earth, towns, 3000 AD | ~35% | **~40%** | Overviewer gives me images of what stands (finding 3), so towns can be judged by me, not only by you |
| 2 | Every history | ~85% | **~85%** | unchanged — but A0 is still unrun |
| 3 | People act out history | ~50% | **~55%** | images make a town judgeable; scenes still need you |
| 4 | Money, vehicles | ~50% | **~45%** | vehicles are confirmed from zero (finding 4) |
| 5 | Changing history | ~40% | **~65%** | `BranchEffects` is a purpose-built hook for our timelines (finding 1) |
| 6 | Breaking a paradox | ~20% | **~60%** | the rupture is **already written**; the work is a jar and a test (findings 1–2) |
| 7 | Performance | ~30% | **~35%** | unchanged; fps is still structurally yours |

**All seven closed, with your 40 minutes: was ~40–50% → now ~60–65%.** The two big movers are R5 and R6,
because the hardest parts of both already exist in the fork and were invisible from the mod's side.

---

## Part 3 — The plan

### Stage 0 — four spikes, before any phase commits (each ≤ 1 session)

A spike exists to **kill or confirm an assumption cheaply**. Each ends in a one-line verdict, and a bad
verdict changes the phase rather than failing it.

| spike | question | how | kills | verdict format |
|---|---|---|---|---|
| **S1 (A0)** | is the history *correct*, not just resolvable? | 50 random place-years, each checked against Wikipedia/Wikidata; wrong-rate | if > 1 in 12 wrong, R2 becomes a data-repair project and every later phase moves | `wrong 2 of 50 (4%) → R2 repairable at ~6 steps` |
| **S2** | can I build one town of the past? | one town, one era (Anyang 430 BC), 30 houses + a wall + a market, from the 30,151-town data; render it with Overviewer | if the image reads as a heap, R1-d needs a different approach (prefab templates, not procedural) | `town built in 1 step; image shows street grid: yes/no` |
| **S3** | can I make one vehicle move? | one cart that follows a road, one boat that follows a river | if entity pathing fights Terra++ terrain, R4-a needs a rail-based approach instead | `cart moved 200 blocks along a road: yes/no` |
| **S4** | can the mod reach Terra++'s `historical` package? | route A: compile the 19 files against alpha+Forge; count errors and missing closure | if the closure is big, switch to route B (build the fork) | `compiled 19/19 classes, closure = 3 extra files` |

**Order: S1 and S4 first** (they change the most), then S2, then S3.

### Stage 1 — the phases, after the spikes

**Phase A — truth (1–2 sessions)**
`A0` truth audit at full size (200 samples) · `R2-a2b` the six estimate rows · `R2-b` news by day ·
`R2-d3` a named polity's economy · the long-tail suite.
*Artifacts:* `verify/answers.csv` (< 2% wrong), `verify/news.csv`, `verify/money_polity.csv`.

**Phase B — people and places (6–8 sessions)**
`B0` verify Terra++'s buildings via Overviewer images · `R3-a` famous people at home · `R3-c`/`R4-f` jobs,
wages, licences · `R1-d` past towns · `R1-e` past roads · `R1-f` famous buildings.
*Artifacts:* `verify/terra_check.csv`, 10 town images, `verify/jobs.csv`, `verify/landmarks.csv`.

**Phase C — things that follow (8–10 sessions)**
`R5-a` kill or save a famous person · `R5-b` growing butterfly · **`R5-c` connect `BranchEffects`** (now a
known API) · `R5-d` papers/book per timeline · `R4-a` vehicles · `R4-b/c/d/e` goods, weapons, clothes/food,
measures · `R3-b` event scenes.
*Artifacts:* 3 timeline boards, `verify/vehicles.csv`, `verify/kinds/*.csv`.

**Phase D — the future (3–4 sessions)**
`R1-g` + `R2-c`: one marked projected road from 2026 to 3000, internally consistent at 2100/2400/3000.
*Artifacts:* `verify/future.csv`, 3 Overviewer images.

**Phase E — connect and judge (3–5 sessions)**
`R6-a` fixed points → Terra++'s counter · `R6-b` broken-logic story · **`R6-c` build the fork and test the
existing rupture** · `R6-d` physics/portals · `R7-a` the 30-minute walk · `R7-b` the rebuild stall · `R7-c`
your fps numbers.
*Artifacts:* rupture screenshots (yours), `verify/walk.csv`, your fps file.

**Phase F — the certificate (1 session)**
`verify_requirements.sh`: seven lines, each reading its artifacts. Red line = not complete, whatever the prose.

### Stage 2 — the arithmetic, honestly

| | optimistic | realistic | pessimistic |
|---|---|---|---|
| spikes | 2 sessions | 3 | 4 (one spike fails and is redone) |
| phases | 18 sessions | **25** | 34 |
| your 40 minutes | 1 | 1 | 2 (repeat after a fix) |
| **total** | **~21 sessions** | **~28 sessions** | **~38 sessions** |

At 2–4 steps per session, each session carrying ~15 min of setup (finding 5). **The single biggest schedule
risk is not any one requirement — it is that a failed spike discredits the plan built on it.** Hence Stage 0.

---

## Part 4 — What would make me stop and re-plan

| trigger | response |
|---|---|
| **S1** wrong-rate > 8% (more than 1 in 12) | freeze all building; requirement 2 becomes a data-repair project first; re-plan with the repair cost measured |
| **S2** a town renders as a heap and two approaches fail | R1-d moves to curated prefab templates; R1's estimate drops to ~50% and the plan lengthens by ~5 sessions |
| **S3** a vehicle cannot path over Terra++ ground | vehicles become track/route-based (rails, rivers) rather than free-roaming; R4-a lengthens by ~3 sessions |
| **S4** the closure is large and route B will not build | P2 is declared blocked; R5 closes 5 of 6 rows, R6 closes 4 of 6; the plan is repaired around it |
| another class of silent defect | a new sub-step ahead of the phase that found it, as boards 19–21 did |

---

## Part 5 — What is still not mine

Unchanged by any research, and I will not pretend a tool closes them:

1. **fps and client milliseconds** — no server-side number is fps, and Overviewer renders a world, not a frame.
2. **whether a place feels right** — an isometric image shows a street grid; it does not show what standing in
   Anyang in 430 BC feels like.
3. **the rupture actually firing** — the code exists; only a client proves it fires *in your game*.
4. **one decision** — the marked future road vs a full simulated future (I recommend the marked road).

**And the honest ceiling:** if the 40 minutes never happen, the maximum is **5 of 7 closed and 2 declared
blocked**, with R7's client half and R6's proof standing open. That is a good result. It is not 100%.

---

## Sources

- [Minecraft Overviewer, docs](http://docs.overviewer.org/en/latest/) — command-line rendering of a Java world,
  no client required.
- [Overviewer FAQ: "Does Overviewer work with mod blocks?"](https://docs.overviewer.org/en/latest/faq/) — *"none
  of the blocks added by mods will be visible"*.
- [Community-maintained Overviewer (v1.20.3 / v1.21.1, Windows & Linux)](https://overviewer.gregoryam.com/) —
  1.20+ support.
- [r/Minecraft: Overviewer 1.20+ support](https://www.reddit.com/r/Minecraft/comments/14uvgx5/the_minecraft_overviewer_120_support/)
  — the 1.19.3 → 1.20 gap and the fork that closed it.
- Workspace evidence (not a web source, and the more important half): `terra3/src/.../historical/` — 19 classes,
  including `WorldLineRegistry.BranchEffects` ("implemented by an external driver (Eternal Engine's timeline/event
  system)") and `ParadoxEngine` (295 lines, rupture → new universe).
