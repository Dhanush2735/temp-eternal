# Java changes in step 14 (the core)

Paths under `eternal/src/main/java/com/eternalengine/`. All of these files except the two new ones already
had uncommitted changes before step 14 (from the original authors and from steps 9-11). I did not save the
pre-step-14 copies, so a clean `diff -u` of only this step's changes is not possible here (plain `git diff`
shows ~4,800 lines, mostly older work). Instead:
- this list says what changed in each file, and why;
- `step14_java_after.tar.gz` holds every touched file as it is after step 14, so the next step can make an
  exact patch against it.

## New files

| File | What it is |
|---|---|
| `core/SystemRunner.java` | Runs each world system in its own safety net and times it. If one system throws, only that run is lost; the other systems keep going. The first error is logged with its stack trace, later ones at most once a minute with a count. Errors the JVM cannot recover from (out of memory) still stop the server. |
| `core/ConfigReloadListener.java` | Applies the server config when a world loads it and when Forge sees the file change. `reloadFromDisk()` re-reads the config files for `/ee reload`, because Forge's own watcher misses editors that save by replacing the file (tested with `sed -i`). |

## Changed files

| File | Change |
|---|---|
| `core/SimulationEngine.java` | `processTick` rewritten: every system goes through `SystemRunner`, and the per-tick part of the world runs every tick. Scheduled systems that are due after the tick has used `maxTickBudgetMs` wait for the next tick (at least one runs per tick). While paused, only history stops (clock, wars, disease, trade, population, farming, religion, technology, climate, reputation, event chain, armies, caravans, contagion); spawning, sounds, overlays, block work and autosave go on. Pause has two reasons: an operator (`/ee pause`, kept in the save) and an empty server (`pauseWhenEmpty`, checked once a second). In Terra++ time a pause also stops the day/night cycle; a world flag remembers it, so it is switched back on at resume or at the next start. `start()`: clean slate per world (failures, deferred systems, metrics, slow-downs), server config intervals, data refresh (`refreshAtStart`), `restoreRunningWorld()` (wars, outbreaks, routes, event chain), an empty timeline registry before branches are restored, the year signal, and the operator's pause. New: `resetSimulation()` (`/ee reset confirm`), `pauseReason()`, `systems()`. The tick-budget warning is limited to once a minute. |
| `core/WorldStateManager.java` | The save now also holds world flags, relations, territory, populations, wars, outbreaks, trade routes, the clock's ticks inside the year, the operator's pause and `dataVersion`. Loading starts from an empty manager, so a single-player world no longer inherits the previous world's state. Each part is read on its own, so one damaged entry loses only that entry. Old saves are converted through `VersionManager`. New: `resetToDefaults()`, `getFlagsWithPrefix()`, `getStateFile()`, `getLastLoadSummary()`, `getAllActiveDiseases()`. New fields on `WarState` (cause, exhaustion), `DiseaseState` (origin, severity, deaths) and `TradeRouteState` (goods, transport, danger, opened year, coordinates). |
| `core/VersionManager.java` | Data version 2, a no-op migration 1→2, and `isReady()`. It is now used: old saves are converted with a backup first. |
| `core/SimulationTickScheduler.java` | Starts from the defaults written in the config spec and no longer reads any config while the mod is set up (the real game ignored the config, and dev runs crashed). `reloadFromConfig()` runs at world start and on config changes. Uses concurrent maps. Removed the unused schedules "era", "vipAging" and "buildings". `reduceFrequency`/`restoreFrequency` return the new multiplier; also added `getBaseInterval` and `getMultiplier`. |
| `core/PerformanceMonitor.java` | Per-system timing is now recorded (through `SystemRunner`), with averages over the last 100 runs. `evaluate()` (every 5 s) halves the rate of the costliest scheduled system after 15 s over budget, and gives back one step after 30 s under half the budget. It logs each change. `/ee performance` report: per system, costliest first, with interval, slow-down, waits and failures. Fixed the Python-style `{:.2f}` log format. |
| `core/PersistenceManager.java` | A save makes a backup only when the newest backup is `backupIntervalMinutes` old. That setting was never read before, so every 5-minute save made a backup and the 10 kept backups reached back only 50 minutes. |
| `clock/SimulationClockManager.java` | Speed votes are counted: a speed wins with more than half of the VIP players online. Votes of players who are offline or not VIP do not count. The vote is applied on the server thread. Event slowdowns are switched on by year range, with chat lines at start and end, on the Eternal Engine clock only. Year-change listeners (`addYearListener`). The ticks inside the year are restored from the save. `setBaseSpeed` returns false for an invalid speed; in Terra++ time it keeps the year. New: `describeMode()` and `realMinutesPerYear()` (which clock runs, and how fast), `describeSlowdowns()`, `tally()` and `VoteOutcome`. |
| `terrabridge/TerraTimeBridge.java` | The Terra++ time class and its methods are looked up once instead of on every call (without the fork, every call threw and caught an exception). `isAvailable()` also needs Terra++ time to be switched on. New `setTimeScaleKeepingYear()`: a new scale used to move the year itself (10x to 25x in 1948 gave a year past 9000). `dayForYear()` rounds up: the old rounding put 11,220 of 20,404 year/scale pairs in the year before, so `/ee year set 1948` could land in 1947. |
| `config/EternalEngineConfig.java` | New common setting `pauseWhenEmpty` (on by default). Clearer comment for `backupIntervalMinutes`. |
| `war/War.java`, `war/WarEngine.java` | `restoreFrom(state)`. The save also holds each war's cause, exhaustion and casualties from before a restart. |
| `disease/DiseaseEngine.java` | `restoreFrom(state)`, which also re-registers diseases nobody described. Each outbreak's origin, region severities and deaths go into the save. An outbreak that ended by itself leaves the save (before, it stayed "active" forever). |
| `trade/TradeRouteEngine.java` | `restoreFrom(state)`. A route goes into the save as soon as it opens, with everything needed to reopen it. |
| `history/EventChainEngine.java` | `restoreFrom(state)` rebuilds the "already happened" and "stopped" lists from the world flags, so a restart no longer replays the past. |
| `timeline/BranchSuppression.java`, `timeline/TimelineManager.java` | `clear()` and `clearBranches()`: back to prime history only. Used before branches are restored and by the reset. |
| `data/FoundationDataInstaller.java` | `refreshAtStart()` records what the mod installed in `<world>/eternalengine/installed_data.json` (checksums) and checks every file at each start. Missing files are copied. A file unchanged since the mod installed it is replaced when the mod ships a new version. A file the owner changed is kept. A file that differs and was installed before the record existed is also kept. The data version is a short checksum over all shipped files. The 11 history files are no longer copied (they were never read). New: `lastRefresh()`, `RefreshResult`, `FileState`. `install()` also writes the record. |
| `data/FoundationDataLoader.java` | `loadInstalled(server, engine, includeVips)`. `/ee reload` and the reset leave the VIP files alone, because reading them again would drop the current claims. |
| `commands/EternalEngineCommands.java` | New: `/ee pause`, `/ee resume`, `/ee data status`. `/ee reload` is now real: it re-reads the config files, checks the data files, and reloads civilizations, events, buildings, names, skins, population packs and stories. `/ee reset` shows what a reset does, and `/ee reset confirm` within a minute does it, after a backup. `/ee historian` is removed (no role system reads it). `/ee speed status` shows the clock, the pause and the slowdowns. `/ee speed set` refuses an invalid speed instead of saying it was set. `/ee speed vote` reports the count or the result. `/ee backup` always makes a backup. The help lists the new commands. |
| `commands/EeCommandSelfTest.java` | Dropped `ee historian`; added `ee data status`, `ee speed status`, `ee performance`. |
| `commands/EeOperationalCheck.java` | Required schedules updated (no era/vipAging/buildings; autosave and performance added). New lines in section 1: which clock runs, the pause, and four checks: the server config's intervals are in use; no system failed; the running world is saved and reads back from disk; the world's data files are this mod version's. (Since step 15 the save check only reads and the check writes no report file: `java_changes_step15.patch`.) |
| `EternalEngineMod.java` | No longer loads the world state before `start()`, which loads it itself. Before, `state.json` was read twice, and an old save was converted twice. |

## Tests (2026-10-12, sandbox)

- `tools/quick_javac.sh` (new: a type check in seconds) and the Gradle build: BUILD SUCCESSFUL.
- `probe_core.sh` + `probes/CoreProbe.java` (new): 11 of 11 pass: vote counting, the Terra++ day rounding over 20,404 year/scale pairs, the safety net.
- `probe_check.sh`: 73 checks, 70 OK, 0 failed, 3 known (unchanged).
- A real Forge 1.20.1 server (`tools/run_test_server.sh`), four starts of one world:
  1. A new world: `/ee check all` 91 passed, 0 failed, 3 known (87 before, plus 4 new core checks). I added a war, an outbreak and a trade route, then:
     - `/ee pause`: the year stood still for 30 s at 50x. `/ee resume`: it moved on.
     - `/ee speed set 7` was refused.
     - `/ee year set 460`: the slowdown for the fall of Rome switched on (50x → 5x) and 19 past events fired at once.
  2. After the restart, the war (exhaustion still growing), the outbreak and the trade route were back. The 19 past events were remembered: 0 fired again.
     - `pauseWhenEmpty` edited in place: "History paused: nobody is online".
     - `/ee reset` then `/ee reset confirm`: year −3000, speed 10x, nothing left, backup made.
  3. An old-format save was converted (with a backup). Data files: one updated, one kept as edited, one kept as unrecorded.
     - The server config was edited with `sed -i` (not seen by Forge). `/ee reload` applied it: war 10→30.
     - `/ee check all` 91 passed.
  4. An operator's pause survived the restart. The old save was converted once and loaded once. `/ee check all` 91 passed.
- Not tested here: Terra++ time (the Terra++ jar in the sandbox has no `TerraTimeManager`), votes by real VIP players, and the "slows a heavy system" step (the test server never went over budget).
