# The marking board — tenth sitting, 2026-10-23

Board 9's verdict said G5 was closed by driving **Minecraft's own dispatcher with no server**. Then I
read the plan one more time:

> **G5** … whole mod compiles; **212 commands parse on a headless server**; 27 classpath probes green

A dispatcher with no level is not a headless server. Board 9's G5 was one step short, and this
sitting closed it: a real dedicated Forge server, a real world, a real save, the mod's own data
installed — and every command run against it.

---

## 1. The server

`./gradlew runServer` on Minecraft 1.20.1 / Forge 47.2.0, flat world, `--nogui`, driven over RCON
(there is no `mcrcon` here, so `worldfill/probes/rcon.py` speaks the protocol itself).

| | |
|---|---|
| boot | **Done (4.9 s)** on the first run, 5.4 s and 6.2 s on the later ones (world already made) |
| the mod's own data | `FoundationDataInstaller`: **13 files, 13 added, 0 failed** |
| events | **76 loaded** |
| rulers | `78495 places, 9612 timelines, **200695 spans**` — the board-9 span merge is live in the game |
| civilizations | **221** |
| Terra++ | absent, as the sandbox always said: `[TerraTimeBridge] No Terra++ time in this game (ClassNotFoundException); the Eternal Engine clock runs the year` — and the clock does run the year |
| shutdown | `/stop` → *Stopping server · Saving worlds · All dimensions are saved* |

Nothing in this run needed a client, a Terra++ jar or a player.

---

## 2. `/ee check all` on a live server: **436 passed, 0 failed, 12 known limits**

This is the number the whole marking was missing. For comparison:

| where it ran | result |
|---|---|
| `probe_check.sh`, no world (boards 5–9) | **389 checks, 377 OK, 0 failed, 12 known limits** |
| dispatcher with the engine started but no level (board 9) | 421 passed, **12 failed** |
| **a real headless server, a real world (this sitting)** | **436 passed, 0 failed, 12 known limits** |

The twelve that failed in board 9 — the date line, the save file, the server-config intervals, the
map projection, Terra++, the weapons gate and the rest — **all pass the moment there is a level**.
That is the proof that they were sandbox artefacts and not defects, and it is the kind of proof I
would not accept from reasoning alone.

---

## 3. The 212 commands: **212 of 212 answered on the live server**

| | board 9 (no world) | this sitting (live server) |
|---|---|---|
| parsed | 212 | **212** |
| answered in words | 212 | **212** |
| returned 1 and did the thing | 123 | **154** |
| asked for a player (a console has no entity — correct) | 89 | **58** |
| threw / timed out / leaked a Java message | 0 | **0** |
| no answer at all at a command's own speed | — | **0** |

**31 commands moved from "needs a running world" to actually doing their work**: `/ee data load`
(*foundation data loaded, world folder*), `/ee backup` (*Saved, and backed up to ./world/./eternalengine/backups*),
`/ee web start` (*Web console started: http://127.0.0.1:8765/?token=…*), `/ee probe 0 0` (a real
`WorldDebugSnapshot`), `/ee incident test`, `/ee vehicle test`, `/ee timeline roll` / `diverge`,
`/ee chrono paradox start`, `/ee reload`, `/ee ecs benchmark` (*100K-agent zero-heap stress
benchmark*), and the codex pages that print thousands of characters each.

Slowest command: `/ee reload` at **470 ms**; then `/ee chrono rival` 436 ms, `/ee web start` 390 ms,
`/ee data load` 377 ms, `/ee backup` 371 ms. Everything else under 370 ms.

The 58 that still ask for a player are the right 58 — `rep`, `observer`, `speed vote`, `scan chunk`,
`anomaly`, `achievements`, the player-only probes. A console has no body to stand in.

---

## 4. The shipped datapack: 9 of 10 functions ran — and the tenth was a real defect

`ee_command_test_datapack` (871 lines) was copied into `run/world/datapacks/` and run through the
server:

```
test_all     Executed 423 command(s)
test_part1   Executed  81 command(s)
test_part2   Executed  81 command(s)
test_part3   Executed  81 command(s)
test_part4   Executed  81 command(s)
test_part5   Executed  81 command(s)
test_part6   Executed  23 command(s)
test_reset   Executed   3 command(s)      <- only after the server setting below
```

**The defect (found, proven, fixed by a setting):** `test_reset.mcfunction` line 3 is
`ee reset confirm`, and `/ee reset` requires **permission 4**. A datapack function is *parsed* at
`function-permission-level`, which is **2** by default, so Brigadier could not resolve the node and
the server dropped the **whole function file** at load:

```
[ServerFunctionLibrary]: Failed to load function eternalengine:test_reset
java.lang.IllegalArgumentException: Whilst parsing command on line 3:
    Incorrect argument for command at position 3: ee <--[HERE]
```

That message names neither the permission nor the setting. With `function-permission-level=4` in
`server.properties` the function loads and runs. **The datapack now ships a `README.md` saying so**,
and `verify_server.sh` sets it. This is a live-server defect that no dispatcher test could ever have
found: the datapack loads in the game, not in a probe.

---

## 5. The performance numbers a headless server can give (the honest half of G7)

| | |
|---|---|
| steady state | **0.04–0.06 ms average per tick**, last 100 ticks **0.02–0.03 ms**, over 2,100–4,100 ticks |
| peak | **14.9 ms** (run 1) and **21.2 ms** (run 2) — the 10 ms budget is exceeded once per boot |
| over budget | **1 second** in ~4,100 ticks |
| startup spike | one `Tick budget exceeded! Avg: 21ms` (run 1: 14 ms), slowest system at boot `compass` 1x ms |
| per system | `spawner` 0.003, `clock` 0.003, `async-callbacks` 0.002, `blocks` 0.002, `autosave` 0.399 ms every 1,200 ticks |

**These are server-side, on a 2-core 2 GB box with 5 GB of swap, with no player online and a flat
world.** They are not G7 — G7 wants fps, client ms, server ms and heap at the 55 MB data load, per
era stop, on *your* world — but they are the first real numbers from a real server, and the boot-time
spike is worth watching when you run G6.

---

## 6. One defect that was mine

The first run died at `/ee codex chronicle` with *"rcon: connection closed"*, and I nearly wrote it up
as the server falling over. It was my RCON client: it read **one packet per answer**, and a long
answer (the codex prints thousands of characters) arrives as several — leaving the rest in the socket
put the stream out of step. The reader now drains until the socket is quiet. **The server had been
fine all along.**

---

## 7. What this changes

| gate | before this sitting | after |
|---|---|---|
| **G5 the command surface** | PASS on a dispatcher with no world | **PASS on a headless server** — the plan's own wording, now met |
| **G6 the real game** | CANNOT JUDGE HERE | **partly judged**: everything in it that does not need eyes now has a verdict (the 436-check run, the 212 commands, the datapack). The visual half — `FINAL_TEST.md`'s 55 tests, the camera pass, villagers' look and talk — is still untouched |
| **G7 the long session** | CANNOT JUDGE HERE | **first real numbers** (§5), from a server, on a flat world, with nobody online |

Re-runnable in one command, as the plan demands:

```
./verify_server.sh      ~2.7 min: start, /ee check all, 212 commands, 10 functions, stop, ledger
./verify_all.sh         the gates without a world (compile, 212 on the dispatcher, manifest)
```

`testrun/server_ledger.tsv` today: **server start 0 · `/ee check all (live)` 0 · 212 commands 0 ·
10 datapack functions 0 · clean shutdown 0 — 5 checks, 0 failed.**

What is still out of reach here, unchanged: a client, a Terra++ world, a player's body, and your
eyes.
