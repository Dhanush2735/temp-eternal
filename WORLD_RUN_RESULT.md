# Your world, run on the fixed jar — what happened

_2026-10-24. The world from `newworld1.zip` loaded on a Forge server built from the fixed source, then
asked its own questions and saved. Everything below is measured on that run, not predicted._

## What ran

```
the world            New World, the one you sent (clock 430 BC, player at Athens)
the jar              built from source: sha256 689b659d…487922 (reproducible — same digest twice)
the server           a development Forge server, the mod loaded from the fixed classes
the check            /ee check all, then save, then a re-read of the files off disk
```

## Result 1 — the register of remembered people was repaired

The world's own record of people (`data/eternal_people.dat`) holds **286 people**. Read before and
after one load on the fixed jar:

| civilization | before | after |
|---|---|---|
| egypt_ancient | 178 | **178** (untouched — Egypt was alive in 430 BC) |
| china_shang | 41 | **12** |
| **china_zhou** | 0 | **29** ← the repair |
| indus_valley | 31 | **3** |
| neutral | 1 | **29** |
| sumer | 35 | 35 |
| **total** | 286 | 286 (nobody lost, nobody doubled) |

**57 people were put right, and the numbers are not a coincidence:**

- **29 Shang → Zhou.** Exactly the count board 16 read out of the save: *29 Shang townspeople at
  Anyang in 430 BC*, 616 years after the Shang fell. They are now Zhou (−1046..−256), which is who
  held that ground.
- **28 Indus → nobody.** The Indus site's people were dated 1200 BC, a century after the Indus fell
  (−1300). They are now `neutral` — the honest answer, because the record names no successor there.
- **12 Shang and 3 Indus kept.** Those people are dated 1200 BC, a year when both civilizations
  *were* alive. The rule left them alone, which is the other half of the test.

## Result 2 — the check agreed

`/ee check all` on that loaded world reported:

```
[ OK ] Nobody stands after their own civilization fell: 257 person(s) held under a named civilization
       (0 standing in the loaded world), 29 with no civilization named and not counted,
       every one of them inside its years
```

257 named + 29 uncounted = 286, the whole register, and **not one outside its years** — where before
the same register held 43 people who could not have existed (41 Shang + 2 stray).

## Result 3 — the 18 people already standing were NOT touched (and why)

The 923 people standing in the world still carry what they were given: 13 `indus_valley_civilization`,
5 `jin`, 39 `egypt_ancient`, 866 with no civilization.

That is not the fix failing. **Those chunks were never loaded.** A headless server has no player, so
the server keeps them on disk; the repair happens when a person *enters the world*, and none did. I
force-loaded the exact chunks they stand in and the server still refused to materialise them — on top
of which this sandbox has no network route to the services Terra++ uses while it builds terrain, so
chunk work stalls with `Read timed out`. Their correction needs one thing a server here cannot fake:
**you standing nearby.**

The moment those chunks load under this jar, the same hook that fixed the 286 runs on them:
`jin` → `china_zhou`, `indus_valley_civilization` → `indus_valley` (or an honest `neutral`).

## Result 4 — Athens still cannot be answered from here

Athens has ground and, in the file, nobody in it. Crowds are only stood up near a player, and this
server has none — so a headless run cannot tell "you saved too soon" from "the crowd never came".
That question needs your screen, for about ten seconds.

## What this does and does not prove

| question | answer |
|---|---|
| does the fix work on **your** world's data? | **yes — measured**: 57 people corrected, 29 of them Shang→Zhou |
| does it leave correct people alone? | **yes** — 178 Egyptians, 35 Sumerians, 12 Shang and 3 Indus were untouched |
| is anybody lost or duplicated? | **no** — 286 before and after |
| are the 18 standing people fixed **in this run**? | **no** — their chunks never loaded; they need a player near them |
| is Athens empty because of a bug? | **still unknown** |

## The two minutes that finish it

1. install `eternal/build/libs/eternalengine-1.0.0.jar` (`689b659d…487922`) — **not**
   `eternal/artifacts/`, which is a stale September build;
2. open the world — it starts at 430 BC where you left it;
3. stand at Athens and don't move for ten seconds: **do people appear?** that answers Result 4;
4. `/ee check all` → the "nobody stands after their own civilization fell" line should read
   *every one of them inside its years*, and the count of standing people should now exceed zero;
5. walk to Anyang (`/tpll 36.1267 114.3133`): the town should be **Zhou**, not Shang.
