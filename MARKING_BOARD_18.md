# Board 18 — one command for a whole stop

_2026-10-24. The question that produced this: "can you automate like when I press /ee test here and it
does" — followed by the twelve commands. The answer is yes, and this is it, measured on a live server._

## What was added

| command | what it does |
|---|---|
| `/ee test stop <id>` | runs one of the 31 route stops end to end |
| `/ee test here [year]` | the same wherever you stand |
| `/ee test stops` | lists the 31 stops with their coordinates and years |

The twelve steps run in order, and the five order-sensitive ones are enforced rather than documented:
the clock is set and **read back** before the jump; the ground is held open before anything is read;
the hold is released only after the world says the ground is there; the card is read after that; and
the civilisation is asked about **the id the card actually named**, not a guess.

**Steps 7–12 are not re-implemented.** They are dispatched through Minecraft's own command dispatcher,
so what a player sees is exactly what typing `/ee here`, `/ee probe`, `/ee villager nearby 64`,
`/ee villager who`, `/ee building nearby 500` and `/ee civ info <id>` produces. The command adds
sequencing, waiting, a verdict and evidence — not a second copy of the answers.

## The state machine, and why

A command may not sleep: the server thread is the thread the chunk generator needs. So each stage is
scheduled with `TickTask` and re-checks the world when it runs.

| stage | action | gives up when |
|---|---|---|
| 1–2 | set the clock, read it back (retried up to 6 times, since Terra++'s calendar can land a year or two off) | — |
| 3 | jump to the stop (route stops only) | Terra++ cannot place the coordinate |
| 4 | hold 81 chunks open (`setChunkForced`) | — |
| 5 | **measure** readiness: the chunk exists at FULL status and ≥1 of 9 sampled columns has real ground under the world's own heightmap | 180 s → *cannot judge*, with advice |
| 6 | release the hold | — |
| 7–12 | the six reads, dispatched and captured | — |
| verdict | machine half of the four-part rule | — |

## Measured, on a live Forge server

`/ee test stop R5` over RCON, on the headless server:

```
1/12  setting the clock to 430 BC
2/12  the year reads back 430 BC
3/12  jumping to Athens - block 4279265, -3412291
4/12  holding 81 chunks open around you while the ground is built
5/12  the ground is there (waited 1 s)
6/12  the hold is released
7/12  the card:
  It is 430 BC.
  You stand at Athens, a city of this year.
  The register names no ruler here in 430 BC.
  Near here the record names Athens suffers a major pestilence, believed to be caused by epidemic typhus (0.1 km away).
  Also Plague of Athens (1.4 km away).
  Also Battle of Plataea (48 km away).
8/12  the probe:
  block x=4279265 y=149 z=-3412291 · geo lat=37.9838069 lon=23.7274943 elevation=85.94m
=== verdict: PASS === the answer holds: Athens (800 BC-338 BC) in 430 BC
evidence: .../world/ee_stop_tests.tsv
```

**That is Athens, at the right coordinates, in the right year, naming the right Plague.** The evidence
row is written into the world folder so it travels with the save.

## Four bugs this exercise found — in my own new code

1. **The RCON reply closes too early.** Stages after the first tick printed into a buffer that was
   already sent, so a console run showed steps 1–2 and then silence. Every line now also goes to the
   server log, tagged `[EE test]`, which is also what makes the route testable without a human.
2. **A stand-in actor cannot be teleported.** A console run's fake body stays at spawn, so steps 8–11
   were reading the Gulf of Guinea. The reading now uses the **stop's own coordinates** for the probe,
   the people scan and the buildings, and says plainly when the body could not be moved.
3. **Bedrock passed as ground.** On a plain world Terra's surface number sits below the build limit;
   clamping it found bedrock and called an empty chunk ready. Readiness now uses the world's own
   heightmap and rejects bedrock, and reports how many of nine sample columns have real ground.
4. **The evidence file's columns did not match its header.** Fixed, and the header now names `detail`
   and `card`.

## Gate effect

- the command list grew **216 → 220** (`/ee test stops`, `/ee test stop R5`, `/ee test here`,
  `/ee test here -430`), so the surface check now exercises what the route depends on;
  `220 commands: 220 PASS, 0 PARSE-FAIL, 0 THROW` — measured;
- jar rebuilt: `689b659d…487922`, `verify_jar.py` 14 checks 0 failed.

## What it does not do, and will not pretend to

- **It cannot judge the look.** Buildings, dress, the crowd, the road — that is the human half, and the
  command says so on its last line every time.
- **It cannot do step 10 for you.** `/ee villager who` needs something standing in front of you; the
  run logs that it cannot see what you are looking at.
- **It will not move the clock backwards.** A stop earlier than the world's year is refused with the
  command that does move it, exactly as `/ee date` is.
