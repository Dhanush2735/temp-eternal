# Core review and fixes (step 14)

"Core" here means the parts every other world system stands on:
simulation engine, clock, tick scheduler, world state + saving/loading, data installer/loader,
Terra++ bridge, plus their helpers (AsyncTaskManager, PerformanceMonitor, VersionManager, PersistenceManager).
Paths below are under `eternal/src/main/java/com/eternalengine/`.

## Short answer

The core is implemented and it works: the world starts, the clock runs, the systems tick, the state is
saved safely, and `/ee check all` passes 88 of 88 in your game. But it can be improved a lot.
Many core features are written but never connected (nothing switches them on), and one gap matters
for every other system: **most of what the simulation does is forgotten when the server restarts.**

## Done in step 14 (the user chose all of A-D, and "pause when nobody is online")

All ten problems below are fixed, plus five more found along the way. Details file by file:
`java_changes_step14.md`. Tests: a real Forge server, `/ee check all` 91 passed, 0 failed (87 before, plus 4
new core checks), and the hands-on tests listed there.

| # | Fixed |
|---|---|
| 1 | Wars, outbreaks, trade routes, world flags, relations, territory, populations, the clock's position in the year and the operator's pause are saved and come back after a restart. The event chain remembers what already happened: 0 events replayed after a restart (19 before). |
| 2 | Each system has its own safety net: an error costs that system one run, everything else (and the autosave) goes on; logged once with the stack trace, then at most once a minute; listed in `/ee check all` and `/ee performance`. |
| 3 | `/ee reset` explains, `/ee reset confirm` within a minute really resets (backup first); `/ee reload` really re-reads the config files and the data; `/ee historian` removed. |
| 4 | The server config's intervals are used (read at world start, on config changes and by `/ee reload`); the unused schedules are gone. |
| 5 | `/ee pause` and `/ee resume` (kept over a restart); history stops while nobody is online (`pauseWhenEmpty`, on); in Terra++ time the day/night cycle is paused with it and switched back on afterwards. |
| 6 | VIP speed votes are counted (more than half of the VIP players online); the 13 big-event slowdowns switch on by year range with a chat line; a "year changed" signal (the event chain uses it); the ticks inside the year are saved. |
| 7 | `/ee speed status` and `/ee check all` say which clock runs and how many real minutes a year takes. |
| 8 | Time per system in `/ee performance`; a full tick moves the remaining scheduled systems to the next tick; a system that keeps the tick over budget runs less often until the server recovers. |
| 9 | The Terra++ time look-ups are made once, not on every call. |
| 10 | Data version and an install record per world: after a mod update a world gets new and fixed files, files the owner changed are kept; the 11 unused history copies are no longer installed; `/ee data status`. Old saves are converted by `VersionManager` (with a backup). |
| +1 | Terra++ time: `/ee year set` rounded down and often landed one year early (11,220 of 20,404 year/scale pairs); changing the speed moved the year itself (1948 at 10x → 25x gave a year past 9000). Both fixed (not testable here: no Terra++ time in the sandbox). |
| +2 | In single player the previous world's wars, flags, civilization values and timeline branches leaked into the next world opened in the same game. Each world now starts from its own save. |
| +3 | Backups follow `backupIntervalMinutes` (30); before, every 5-minute save made one and the 10 kept reached back only 50 minutes. |
| +4 | `/ee speed set 7` said "Base speed set to 7x" and changed nothing; it now says which speeds are allowed. |
| +5 | The world state was loaded twice at every start (and an old save converted twice). |

Still open, and not core: armies, caravans, courts, treaties, reputation and VIP slots keep their own memory,
which is not saved (they start empty after a restart); the cache-size settings in the config are not used.

## What already works well (keep as it is)

| Part | Works |
|---|---|
| Saving | `PersistenceManager.saveJsonAtomic`: temp file + atomic rename, a backup before every write, backup rotation, recovery from the last good backup on load. |
| What is saved | year, speed, active timeline branch, all branches (with stopped-event pins), every civilization (population, treasury, tech level, religion, government). Autosave every 5 min (`autoSaveIntervalMinutes`), and on stop. |
| Data install | the world-start automatic install (step 11); the history registers are read straight from the mod jar, so they are always the current data. |
| Engine start/stop | start loads the state, installs data, loads 133 civs, starts the systems; stop saves. |
| Terra++ bridge | coordinates and terrain go through one class (`terrabridge/TerraBridge.java`), null-safe, availability is checked once and cached. |
| Spawner | `PresenceLocalSpawner.tick` throttles itself (every 40 ticks). |

## What was wired but not connected (the review, before the fixes)

| # | Part | Problem | What the player notices | Where |
|---|---|---|---|---|
| 1 | Saving | Kept in memory but **never written**: wars, disease outbreaks, trade routes, world flags (famine, quarantine, events that happened), relations, territory, religion and technology sets, VIP states. The event chain's "already happened" and "stopped" lists are memory only too. | After a restart all wars and outbreaks are gone; every past foundation event "happens" again (up to 76 log lines); an event stopped through the event chain can happen again. | `core/WorldStateManager.java` fields l.53–89, `saveWorldState` l.303 (writes only year, speed, branches, civs); `history/EventChainEngine.java` l.23 |
| 2 | Engine | The whole tick is one `try/catch`. If one system throws, **every system after it is skipped**, including the autosave at the end, and the full error is logged 20 times a second. | One broken system silently freezes the rest of the simulation and stops autosaving. | `core/SimulationEngine.java` l.587–590, `processTick` l.626–751 (autosave l.745) |
| 3 | Admin commands | `/ee reset` prints "FULL RESET EXECUTED - This cannot be undone!" but does nothing. `/ee reload` prints "Configuration reloaded" but does nothing. `/ee historian <player>` prints "Granted historian role" but does nothing. | Messages that lie, one of them alarming. | `commands/EternalEngineCommands.java` l.4010, l.4021, l.4026 |
| 4 | Scheduler | It reads the server config at mod setup, before any server config exists, so the game always uses the built-in intervals. `updateInterval()` is never called. 4 schedules are never used ("vipAging", "buildings", "performance", "era"; there is no era system). 11 systems run every tick with no schedule at all. | Changing the war/disease/economy/... intervals in the server config has no effect. | `core/SimulationTickScheduler.java` l.81–109, l.193 |
| 5 | Pause | `SimulationEngine.pause()` / `resume()` exist but no command calls them. The clock also keeps running with nobody online. | A dedicated server left alone advances about 30 years per hour at 10x (mod clock mode). | `core/SimulationEngine.java` l.544, l.557 |
| 6 | Clock | Speed votes are stored and never counted ("resolution is handled by the VIP layer", which does not exist). The 13 event slowdowns (WW1, WW2, Black Death, ...) are listed but never switched on. There is no "the year changed" signal for other systems. Ticks inside the current year are not saved. | `/ee speed vote` does nothing; big events pass at full speed; each restart loses part of a year. | `clock/SimulationClockManager.java` l.72–91, l.280–289, l.197 |
| 7 | Clock mode | The year comes either from the Terra++ fork's time (`TerraTimeManager`: one year per 36.5 Minecraft days at 10x, about 12 real hours) or from the mod's own clock (one year per 2 minutes at 10x). Nothing tells you which one runs. | You cannot see how fast history moves in your world. | `terrabridge/TerraTimeBridge.java`, `/ee speed status` (`EternalEngineCommands` l.3921), `/ee check all` |
| 8 | Performance | Per-system timing and automatic slowing of heavy systems are written, but `endSystem()` is never called, so only whole-tick time is measured; the 10 ms tick budget (`maxTickBudgetMs`) is never enforced. | `/ee performance` cannot say which system is slow. | `core/PerformanceMonitor.java` l.83–103, l.136 |
| 9 | Terra time look-up | Every year look-up searches for the Terra++ time class by reflection again. Without the fork every call throws and catches an exception: 5.8 microseconds each in a plain JVM (measured), slower inside Forge, many calls per tick. | Small waste, not lag on its own. | `terrabridge/TerraTimeBridge.java` l.30–112, `SimulationClockManager.getCurrentYear` l.405 |
| 10 | Data installer | No data version: a world keeps the civs, events, VIPs, names, population and stories it got on first start, even after a mod update with fixed data. 11 of the 24 installed files (the history packs and README) are never read by anything, and their `index.json` lists 24 packs while only 8 are copied. `VersionManager` migrations are never used for `state.json`. | Fixes to those data files never reach an existing world unless you reinstall by hand. | `data/FoundationDataInstaller.java` l.73–151; `core/VersionManager.java` |

## Fix plan (in order of importance)

| Step | What | Size |
|---|---|---|
| A1 | Each system in its own safety net: an error in one system no longer stops the others or the autosave; errors are counted, logged at most once a minute per system, and shown in `/ee check all`. | small |
| A2 | Save and restore the running world: wars, outbreaks, trade routes, flags, relations, territory, religion/technology sets, VIP states, the event chain's lists, ticks inside the year. Old saves still load. | medium |
| A3 | Honest admin commands: `/ee reload` really reloads config and data; `/ee reset` asks for confirmation and really resets the simulation state (or is removed); `/ee historian` removed or made real. | small |
| B4 | Server config intervals really apply (read when the server starts and when the config is edited); remove or connect the unused schedules. | small |
| B5 | `/ee pause` and `/ee resume`, and an option "pause the clock when nobody is online" (on by default). | small |
| B6 | Clock: count speed votes, switch on the event slowdowns by year range, add a "year changed" signal, show the clock mode and "1 year = N real minutes" in `/ee speed status` and `/ee check all`. | small–medium |
| C7 | Per-system timing in `/ee performance`, keep the tick inside the 10 ms budget by delaying heavy systems; cache the Terra time and Terra method look-ups. | small |
| D8 | Data version for the installed files: after a mod update a world gets new and fixed files, files you edited yourself are kept; stop copying the 11 unused history files; `/ee data status` shows the installed version. | medium |

Done: Gradle build, `probe_check.sh` (unchanged), `probe_core.sh` (new, 11 of 11), real server runs with
`tools/run_test_server.sh` (four starts, including the stop/start that proves wars, outbreaks and flags come
back), new `/ee check all` lines, and `java_changes_step14.md` with `step14_java_after.tar.gz`.
