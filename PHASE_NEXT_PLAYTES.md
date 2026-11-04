# Next phase — P1: the play test ("the world in your hands")

_2026-10-24. The phase after the automation. This is the first phase whose evidence is a screen, not a
log. Everything before it was measured off-screen; three claims are still unproven because they need a
player: the 18 mistagged people, the crowd at Athens, and whether any of it looks right to a human._

## Where we stand (entry conditions — all green)

| gate | state |
|---|---|
| build | `BUILD SUCCESSFUL`, jar `689b659d98944ac42547f5d9106be8caedfa70a721c4dbebb74df93bee487922` (reproduced twice) |
| command surface | 220 commands, 220 PASS |
| jar integrity | 14 checks, 0 failed |
| register repair | measured on **your** world: 57 of 286 corrected, 29 Shang→Zhou, nothing lost |
| last live run | `/ee test stop R5` × 12 steps → `=== verdict: PASS ===` |

Not green, and the whole point of this phase: the 18 standing people, the Athens crowd, and R6.

## What this phase must produce

Four questions answered by a human looking at a screen, each with a pass mark that is not a feeling:

1. **Does a mistagged person get fixed on arrival?** — stand at Anyang; the town should read Zhou.
2. **Is Athens a timing problem or a real one?** — stand still ten seconds; does anyone appear?
3. **Does the era answer read correctly where the last one didn't?** — R6, which has never been walked.
4. **Does any of it look like a place?** — one screenshot per stop, which is how this project is judged.

## The run sheet — five stops, about 25 minutes

Do them in this order. At each stop: run the two commands, look, screenshot, and write the one line the
log prints. Don't skip ahead if a stop fails; the next stop's evidence is only useful if the previous
one was honest.

Before you start: install `eternal/build/libs/eternalengine-1.0.0.jar` (**not** `eternal/artifacts/`),
open `New World`, and check `/ee year` reads **430 BC**.

### Stop 1 — Athens (the open question) · ~3 min

```
/ee year
/tpll 37.9838 23.7275
```
Then **stand completely still for ten seconds** and do nothing else.

| look for | pass mark |
|---|---|
| people | someone is standing within 32 blocks (the town; not the crowd halo) |
| if nobody | run `/ee villager nearby 64`, then `/ee test here 430` and note what it prints |

Record: the `/ee villager nearby 64` count, and one screenshot facing the town.

### Stop 2 — Anyang (the defect this phase exists for) · ~5 min

```
/tpll 36.1267 114.3133
/ee villager nearby 64
```

| look for | pass mark |
|---|---|
| the 5 people formerly `jin` | each now reads **Zhou** in `/ee villager nearby` (name and civilization line) |
| `/ee check all` | "nobody stands after their own civilization fell … every one of them inside its years" |

Record: the villager list (screenshot or copy the text), and whether any of the 5 still says Jin.

### Stop 3 — the Indus site (the second broken id) · ~4 min

```
/tpll 27.3294 68.1386
/ee villager nearby 64
```

| look for | pass mark |
|---|---|
| the 13 formerly `indus_valley_civilization` | they read either **Indus Valley** or, honestly, **no civilization** — never the long broken name |

### Stop 4 — Giza (the control) · ~3 min

```
/tpll 29.9792 31.1342
/ee check all
```

| look for | pass mark |
|---|---|
| the 39 Egyptians | still `egypt_ancient` — **a fix that changes the correct cases is not a fix** |

### Stop 5 — R6, never walked · ~8 min

```
/ee year 322
/ee test here 322
```

| look for | pass mark |
|---|---|
| the card | the era answer set for −322 (Maurya, Chandragupta → Bindusara, `pana`), five events |
| the ground | people at the Mauryan site; `=== verdict: PASS ===` from the twelve steps |

Expect a **stall** here: it is first-visit Terra++ ground, ~5,900 km of it, and the same stall as R5.
That is generation time, not a bug — note how long, don't judge it as a failure.

## What to send back

Any one of these is enough for me to move; all three is best:

1. **the screenshots** (five, one per stop — Athens facing the town is the important one);
2. **the text** of `/ee villager nearby 64` at Anyang and the Indus site;
3. **the saved world** after the run — I can read the 923 people straight out of it and say, per person,
   what changed, which turns all of the above from "looks right" into a count.

With the save and no screenshots I can still prove 1–4; with screenshots and no save I can only believe them.

## What I will run here meanwhile (no waiting on you)

- the sweep and the full command surface again against the frozen jar, so the gates stay honest while the world moves;
- a read of your returned save: every NPC's civilization, year, and whether it is inside its years — a
  per-person table, not a summary;
- `verify_jar.py` on the jar you actually installed, so we know the file in your `mods/` folder is the
  one that was tested (send the sha256, or send the jar).

## What comes after this phase

**P2 — the whole route, once, end to end.** 31 stops from the oldest card to the newest, in order, with
one screenshot each, `/ee test here` at every stop, and a single marking board that says per stop
PASS / FAIL / NOT WALKED. That is the phase that can finally be called "the project is tested", and it
is only worth starting once P1 shows the standing people are fixed — otherwise the same 18 people will
fail at stop 4 and poison every stop after it.
