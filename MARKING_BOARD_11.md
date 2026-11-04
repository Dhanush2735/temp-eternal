# Marking board 11 — the full sweep, and the pack the sweep broke

_2026-10-23. This sitting's question: after nine sittings of engine edits, do all 141 probes still
pass? Answer: they did not — six failed. This board records the six, what each one really was, the
one that was the mod's own fault, and the re-run that followed the fixes._

## 1. The first sweep

`./verify_all.sh --all`, one command, every probe:

```
141 passed, 6 failed
```

Failure was **not** spread across the mod. Every failing name was in the same corner: probes that
lift code out of the mod and compile it against nothing but Gson, plus one probe whose *fetch input*
was missing from the disk.

| probe | what the log said | what it really was | verdict |
|---|---|---|---|
| `probe_builders` | `worldfill/probe_builders.sh: No such file` | the probe was deleted in an earlier sitting; it stayed on the classpath-probe list | **probe list wrong**, not the mod |
| `probe_famous41` | javac `cannot find symbol` → `_1` fixed, then `package com.eternalengine.clock does not exist` | two causes: it hard-codes `JDK=/home/user/tools/jdk17`, and its javac line never listed `clock/Timeline.java` | **probe wrong**, not the mod |
| `probe_index` | `worldfill/probe_index.sh: line 30: $1: unbound variable` | script dereferences `$1` under `set -u`; the argument is only a dump path | **probe wrong**, not the mod |
| `probe_step44` | missing prices input | needed `worldfill/fetch_prices.sh` (120 MB GitHub mirror → 973 `.tab` in `/tmp/fc`); after the fetch: **32 checks, 0 failed** | **missing fetch**, not the mod |
| `probe_life` | javac `cannot find symbol LifeTable / Households / Jobs / DayRound / Needs` | the lifted range now reaches step 38's `people()` section, and the generated runner's import block never had `com.eternalengine.people.*` | **probe wrong**, not the mod |
| `probe_step34` | missing `build/ways/raw/labels.json` | see §2 — this one was **the mod's fault** | **FAIL, fixed** |

## 2. The one that was mine, and the mod's

`probe_step34.sh` rebuilds three packs before it runs. Two of them were already guarded — the minerals
builder is only run if its 137 MB USGS file is on disk. The **grid builder was not**. On this box the
OpenHistoricalMap tiles and the Wikidata rows live in `worldfill/build/`, which does not survive
between sessions. So the probe ran `build_ways_grid.py` with **no sources at all**, and the builder
cheerfully wrote a grid containing only the Itiner-e roads:

```
the 32,000-cell ways grid I shipped:  183,580 bytes
the grid that sweep wrote over it:     16,817 bytes
```

That is not a cosmetic loss. The grid is what answers *"may this place draw a railway in this year?"*,
and with the Wikidata works gone **every** railway vanished from it. Proof from the same probe run:

```
FAIL New York in 1920 may not draw a railway
FAIL Moscow in 1980 may not draw a railway
   note: New York 1920 grid says false, works say true
```

— the works pack (2,114,353 bytes, untouched, byte-identical to the manifest) still knew about 77,184
stations, and the grid said no railway had ever reached New York. If I had only "fixed the script and
re-run", the sweep would have gone green on top of a crippled pack. **A probe that rebuilds its own
input is not a test; it is a mutation.**

Three things were done, in this order:

1. **Restored the pack.** `eternal/build/resources/main/…/ways.grid.gz` still held the pre-sweep
   copy. Its raw payload (465,958 bytes) was rewritten with `GzipFile(mtime=0)` and put back:
   `183,580` bytes, sha `5452ae5f33023be5…` — **the exact sha in `manifest.json`**. Content never
   changed; only the container was regzipped deterministically.
2. **Guarded the builder.** `build_ways_grid.py` now refuses to write when it has 0 OHM tiles *and*
   0 dated Wikidata rows:

   ```
   ways.grid.gz: refusing to overwrite the shipped pack — 0 OpenHistoricalMap tiles and
     0 dated Wikidata works on disk, so this would keep only the Itiner-e roads.
   ```

   A builder must never replace a good pack with a worse one. Verified: running it now leaves the
   shipped sha untouched.
3. **Guarded the probe.** `probe_step34.sh` only rebuilds the grid when the sources are actually on
   disk, and otherwise checks the pack that ships — the same pattern the minerals pack already used.
   Only then did its own failures surface, which is how §3's last bug was found.

## 3. The last bug, and the one-liner that hid it

With the pack safe, `probe_step34` still failed, at the *second* javac:

```
Error: Could not find or load main class WaysHookProbe
```

The javac line ends in `| grep -vE "^Note:|warning" | head -20 || true` — which turns a compile
failure into silence, then `set -e` kills the script later at the class load. Reading the errors by
hand gave the real cause:

```
TerraOsmBridge.java:5: error: cannot find symbol  class LandUseGrid
```

The probe passed `-sourcepath ".../buildings/stubs:$SRC/../../java"`, and

```
eternal/src/main/java/com/eternalengine/../.. = eternal/src/main/java   ← wanted
eternal/src/main/java/com/eternalengine/../../java = eternal/src/main/java/java   ← what that gives
```

one directory too deep, so four mod files on the sourcepath were never found. `$SRC/../../java` →
`$SRC/../..`: **15 checks passed, 0 failed**, and the hook probe's answers reappear.

Two smaller ones fell out of the same reading: `verify_all.sh` now exports `JDK17` (so probes that
expect `${JDK17:-…}` stop falling back to a JDK that is not there) and passes `probe_index` its dump
path.

## 4. The re-run, and the second failure it found

`./verify_all.sh --all` again, after every fix above, with the restored pack in place:

```
145 passed, 1 failed
FAIL probe_tiles   presence.tiles: OUT OF DATE (run build_tiles.py)
```

This one was **mine**, and it is the second-order cost of §5's determinism work. Both tile packs
record, in their header, a SHA-256 of the master they were cut from — and `build_tiles.py` computed
it with `sha256_file()`, which reads the **compressed** `.gz`. A gzip header carries an mtime, so
when the 35 `.gz` files were normalised to `mtime=0`, the masters' hashes changed while not one row
of data did, and both tile packs became "OUT OF DATE" against a master that was byte-for-byte
identical in content.

Fix, in the cause:

- `sha256_file()` now decompresses when the path ends in `.gz` and hashes the **content**. Nothing
  in the mod compares this value — `TileStore.masterHash()` is exposed and never read — so the
  convention can be made honest without touching a consumer.
- Both tile packs rebuilt: `famous_people.tiles` 12,520,386 bytes / 2,463 groups,
  `presence.tiles` 6,073,168 bytes / 1,206 groups. Built **twice**: `cmp` says identical both times,
  so the determinism the `.gz` files now have extends to the packs built from them.
- Manifest rebuilt and `--check` clean.

`probe_tiles` then, run on its own:

```
everyone: tiles 184060, master 184060
points 423 x years 14: 47376 queries, 1394558 people in the answers, 0 different
tiles 3.7 s (0.08 ms a query)   master 159.8 s (3.37 ms)   cache 47.9 of 48 MB, 421,657 hits
TILES OK: the same answers as the master
```

## 4a. The final re-run — clean

`./verify_all.sh --all`, third run, after the tile fix:

```
=== L0  PASS syntax_gate       no syntax errors (4,519 diagnostics, all unresolved symbols — expected without Minecraft jars)
=== L0  PASS manifest          manifest.json: up to date; DATA_CREDITS.md: up to date
=== L2  PASS compileJava       BUILD SUCCESSFUL in 8s — 1,232 classes
=== L2  PASS command_surface   212 commands: 212 PASS, 0 refused in words, 0 PARSE-FAIL, 0 THROW, 0 cannot judge here, 0 TIMEOUT, 0 LEAK
=== L2  PASS ee_check_all      422 passed, 11 failed, 12 known limits   ← no world: see below
=== L1  141 probes             141 passed
------------------------------------------------------------------
146 passed, 0 failed    (testrun/raw3/sweep_all_3.log; ledger testrun/ledger.tsv)
```

The 146 is 141 probes + 5 gates; it was 147 last sweep only because `probe_builders` was still on
the list. **`ee_check_all`'s `11 failed` is the sandbox-without-a-world artefact already proven on
board 10** — every one of those eleven (`Terra++ is available`, `Map positions use the world's own
projection`, `History book for sale`, `Weapons: the gate ran`, the authored chain/scenarios, …)
passed on board 10's live headless server, where the same command returned **436 passed, 0 failed,
12 known limits**. It is marked PASS by the gate for that reason, and it is not evidence against the
mod.

Final state of the shipped data after this sitting:

```
manifest.json: 132 files (131 shipped, 59,333,431 bytes; 1 master kept out of the jar); 35 sources
files without a licence: 0 []   non-commercial licences: 1 ['history/prices.json.gz']
--check: up to date
ways.grid.gz        sha256 5452ae5f33023be5…  = the sha in the manifest
famous_people.tiles sha256 1fa8d625…  presence.tiles sha256 6ab63350…  both identical on a rebuild
```

## 5. What this sitting does to the verdict

- **No engine regression from nine sittings of edits.** All 141 probes pass, including every probe
  that touches the code changed since board 10.
- **G5's evidence is intact and the data it rests on is intact.** The ways grid is byte-for-byte the
  pack the manifest licenses — checked, not assumed.
- **A destructive builder is now a refused builder**, and the manifest's determinism guarantee
  (`mtime=0` everywhere) survived the incident: the restored file re-hashes to the manifest's sha.
- **Self-corrections, now fifteen:**
  1. the 141-probe suite had never been re-run after the engine edits;
  2. 27 builders still stamped gzip mtimes;
  3. **`probe_step34` silently overwrote the shipped ways grid with a roads-only grid during the
     sweep, and the first triage ("missing fetch input, environmental") was wrong** — it was the
     probe *and* the mod's data that were damaged, and it took a restored pack plus two guards to
     make the probe honest again;
  4. **board 10's gzip fix broke the tile packs**: `build_tiles.py` hashed the compressed master, so
     `mtime=0` made `probe_tiles` fail against an unchanged master — a determinism fix that created
     a determinism defect two files away;
  5. the second sweep's tally was quoted as a tally before I read why the count was 146 and not 147
     (`probe_builders` removed from the list), i.e. a number without its own explanation.

Nothing here changes a gate verdict. G6's visual half and G7's client half remain blocked on the
user's client and world; everything a sandbox can decide is decided.
