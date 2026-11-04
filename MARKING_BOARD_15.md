# Marking board 15 — G6's machine half, and the file a player installs

_2026-10-23. Board 14 closed the last two known defects. This sitting took the one open test whose
machine half had never really been asked — **G6, "a night outside town"** — and then opened the one
thing nobody had ever opened: **the jar itself**._

## 1. G6: was the spawn gate ever asked?

`FINAL_TEST.md` 51 says: *wait outside a town at night. Good: no monsters, no raids, no wandering
traders in history.*

The mod's rule was in place (`population/MinecraftMobs.java`): the natural spawner's monster picks are
cancelled, a cancelled `FinalizeSpawn` drops patrols/raids/traders, Bad Omen is refused, the skeleton
trap is dropped. `/ee check all` already tested it — but only by **posting Forge's events itself**, and
by reading the counters:

> stopped since the server started: 0 natural monster spawn attempt(s), 0 other monster(s), 0 raider(s),
> 0 trader(s); 0 Bad Omen(s)

**Zero.** On every server this project has ever run. A test that posts its own events proves the
handlers are wired; it does not prove Minecraft ever calls them. And "I stood outside a town and saw no
monsters" is exactly what a gate that never fires looks like too.

### What was added

`MinecraftMobs.realSpawnTest(level)` — a check that drives the real thing, on live world state:

1. finds open ground near the world spawn (radius 32–128, solid below, air above, chunk loaded);
2. puts the clock at midnight, restores it afterwards;
3. calls `NaturalSpawner.spawnCategoryForPosition(MobCategory.MONSTER, level, spot)` — the call the game
   makes while a player stands there — four times;
4. counts monsters in the level before and after, and reads the gate's counters.

The first version of this reported **inconclusive**, and that is the interesting part:

> inconclusive: the spawner was asked at 32, -60, 0 and nothing appeared, but no gate counted a refusal

which is precisely the trap — *nothing appeared* and *no rule ran* look identical. So the test was
given a second measurement: it calls `ForgeEventFactory.getPotentialSpawns(...)` — the exact factory
call Forge patches into `NaturalSpawner.getRandomSpawnMobAt`, i.e. the spawner's own selection step —
and asks whether **the counter moved**. Not "did the list come back empty" (an empty list could just be
a biome with no monsters in it: that would pass while proving nothing — my second version nearly did
exactly that), but *did this mod refuse it*.

On the shipped jar, on a production server, the check now reads:

> [ OK ] A real spawn attempt in the open at night: the spawner's own selection call
> (ForgeEventFactory.getPotentialSpawns, the one the game makes while a player stands there) was
> refused on live world state and nothing appeared; stopped since the server started: 0 natural monster
> spawn attempt(s), …

**`/ee check all`: 437 passed, 0 failed, 12 known limits** (`testrun/raw3/prod_server_g6c.log`) — 437,
not 436, because this is a new check and it is counted.

### What this still does not prove

The full vanilla loop (`ServerChunkCache.tickChunks` → per-chunk spawns) never reaches selection in a
headless server, and the test says so rather than claiming it: the counter that belongs to the loop
stays at 0 while the selection-step counter is what proves the refusal. **A body standing outside a
town at night is still the only way to close G6**, and the check now prints the number that body would
otherwise have to guess at. G6 stays **open**, with a smaller unknown.

One honest consequence: the check needs a level, so in the bare headless harness it fails. That moved
the documented headless baseline from 11 to **12** (`verify_all.sh`, `HEADLESS_BASELINE=12`), and the
same code reports 437/0/12 on a real server. Both numbers are written down instead of the convenient one.

## 2. The jar: 61.9 MB nobody had opened

Every check in this project until now ran against source, against `build/classes`, or against the mod
loaded out of a dev tree. The **jar** — the file a player drops into `mods/` — had been built and never
opened. `verify_jar.py` (new, 14 checks, in the gate list as `jar_contents`):

| check | result |
|---|---|
| opens as a zip | 1,527 entries |
| a Forge `mods.toml`, naming `eternalengine`, version `1.0.0` | OK |
| the mod's own datapack root `data/eternalengine/eternal/` | 150 entries |
| **every shipped file, byte for byte against the manifest** | **131/131 match** |
| nothing in the jar is unclaimed by the manifest | 0 extra |
| `pack.mcmeta`, `logo.png`, `DATA_CREDITS.md` travel with it | all present |
| no build scripts or logs were zipped in | clean |
| the classes are in it | 1,233 `.class` entries |
| no build timestamp; entry timestamps fixed | reproducible |

The mod's own runtime check agrees, from inside the running jar:

> [ OK ] every data file in the mod is the one that was built and checked (131 files, 56.6 MB: size and
> SHA-256 match the list)

Two independent measurements, one from outside the file and one from inside the game, saying the same
thing about the same bytes.

### The build was not reproducible, and now it is

Two builds of identical source produced two different jars, because the manifest carried
`Implementation-Timestamp` and the zip carried real entry dates. That makes "is the jar you installed
the jar I tested?" unanswerable. `build.gradle` now drops the timestamp and sets
`preserveFileTimestamps = false` + `reproducibleFileOrder = true`. **Proved by building twice:**

```
build 1: 19930eb2fe0903f27c94285517155ab52d8b5e3f1223bf4d7d00966a13ba7509
build 2: 19930eb2fe0903f27c94285517155ab52d8b5e3f1223bf4d7d00966a13ba7509
```

That hash is in `JAR_SHA256.txt`, the jar in `mods/` on the test server was checked against it, and the
server that reported 437/0/12 is the one running exactly that file.

## 3. Three harness defects, self-corrected

- **26.** My first jar check compared raw bytes against the manifest's `contentSha256` and reported
  **124 of 131 files differ**. They did not: `contentSha256` is a *canonicalised JSON* hash (sorted
  keys, no whitespace), by design, from the 2026-10-22 gzip-timestamp work. The checker was wrong, not
  the jar. Fixed by mirroring `build_manifest.py`'s rule exactly — with a docstring saying why the two
  must agree.
- **27.** The second version could not read the binary packs (grids, `.bin.gz`) at all and called them
  differences. The manifest's own rule falls back to raw bytes for non-JSON; the checker now does too.
- **28.** "Entry timestamps are fixed" was written as *one distinct stamp*, which is wrong: zip's DOS
  format yields one or two zero-time stamps depending on the local offset. The property that matters is
  *no entry carries a build date* (and, separately, that two builds agree). Corrected before it was
  ever called a failure.

## 4. Where the gates stand

| gate | state |
|---|---|
| G1–G5 | **PASS** — unchanged this sitting |
| G6 | **machine half stronger, still open** — the spawner's own selection call is now refused and counted on live world state; a body at night is still required |
| G7 | server numbers only (unchanged) |

`FINAL_TEST.md` scorecard is unchanged in shape: **7 passed, 2 partly, 0 failed, 46 open** — G6 is one
of the 46, and it is now the best-instrumented of them.

## 5. The sweep, after all of this

`./verify_all.sh --all` → **150 passed, 0 failed, EXIT=0** (`testrun/raw3/sweep_all_8.log`) — 150
because the jar gate is a new row, not because anything was removed. In that run:

```
PASS manifest        manifest.json: up to date; DATA_CREDITS.md: up to date
PASS compileJava     BUILD SUCCESSFUL in 6s — 1233 classes
PASS ee_check_all    422 passed, 12 failed, 12 known limits (the 12 are the bare-process baseline)
PASS jar_build       eternal/build/libs/eternalengine-1.0.0.jar
PASS jar_check       JAR OK: 11 checks passed, 0 failed
PASS jar_contents    JAR OK: 14 checks passed, 0 failed
PASS manifest_after  manifest.json: up to date; DATA_CREDITS.md: up to date
```

The jar the sweep rebuilt has the same SHA-256 as the one the server ran (`19930eb2…`): the
reproducibility fix is doing its job in the ordinary build, not only in the two-build experiment.
