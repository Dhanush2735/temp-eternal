# The runtime test program (turn 222)

The user's brief, in their words: *"a program for runtime tests of every aspect of the project
where /ee test or /ee check is the input and i will give you world file"*. Their choices when
asked: **singleplayer**, **in-game only, no installs**. So the program lives inside the mod: one
command runs everything against the live world and writes the verdicts into the world folder; the
user sends the report files back.

## The commands (the input interface)

| Command | What it does |
|---|---|
| `/ee test everything` | The full runtime suite: every phase below, one summary page in chat, `eternal_runtime_report.json` + `eternal_runtime_report.txt` written beside the world's state file - then the camera pass runs on (view, sky, 31 era stops, book screen; `eternal_photo_report.txt` / `.json`; frames as `etest_*.png` in the screenshots folder) |
| `/ee test movement` (twice, 5 s apart) | The turn-221 doubt 2 check as real motion: sample who is near you, then judge how far they walked |
| `/ee check all` | Unchanged, and still writes **no files** (P2's rule). The suite runs it in place and puts its counters in the report |

## The phases (what "every aspect" means here)

| Phase | Aspect | How it is judged | Verdicts |
|---|---|---|---|
| 1 engines | every system the check covers (the 438) | `/ee check all` itself, counters via `EeOperationalCheck.passedCount()` | PASS/FAIL + counts |
| 2 commands | all `/ee` leaves | `/ee test all` | LIMIT for now (its summary line is the verdict; suite does not read chat) |
| 3 places | every location and year, data side | the reading's rules at the plan's own place-years + the doubt-1 spot, asked of THIS world's live registers; the registers' own summaries | PASS/FAIL |
| 4 living | people who should act | who within 32 blocks can walk (state, exact) + real motion via `/ee test movement` | PASS/FAIL + LIMIT |
| 5 screen | buildings, dress, multiplayer, frame feel | `FINAL_TEST.md`'s eyes-on items, each named with what would settle it | LIMIT (never silent) |

Verdicts: **PASS**, **FAIL**, **KNOWN** (a named project limit), **LIMIT** (this suite cannot judge
it alone; the item names what would settle it). A LIMIT is never a skip.

## The world file

The user gives the world save as a zip. Before the suite ever runs, the world is read in the
sandbox (`worldfill/runtime/`): its year, spawn, saved state, and the facts are baked into the
expectations and the check questions. Inside the game the suite also records the world's own facts
(year, position, register sizes) in the report header, so every report identifies its world.

## What is built now (turn 222) and what comes next

Built: `testing/RuntimeSuite.java` (the suite + report writer + movement test), `EeOperationalCheck`
counters, `/ee test everything` and `/ee test movement` wiring. Syntax-gate clean; live it goes when
the user rebuilds (the 17-error tradition: rebuild, paste, fix).

Next turns fill the register outward: phase 2's verdicts (expose `EeCommandSelfTest` counters),
economy flows (sell a lot, watch the price move), war and event scenes, timeline fork and paradox
doors (once step 63 wires them), the era route's data side at all 31 stops, and the world-file
reader (`worldfill/runtime/read_world.py`) for the zip the user sends.

## Limits, printed on the tin

- The suite never moves the player, never changes the year, writes exactly two files.
- Anything needing eyes is a LIMIT with its `FINAL_TEST.md` id, not a green lie.
- Minecraft-side code: checked here by syntax gate, live only after the user's rebuild.
- One run at a time (the check's counters are shared); a second run waits for the first.
