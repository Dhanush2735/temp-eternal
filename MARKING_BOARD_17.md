# Marking board 17 — the fix: nobody stands after their own civilization has fallen

_2026-10-23. Board 16 read a real save and found the defect: at Anyang in 430 BC the town held 29
Shang-dynasty townspeople, and one person in five in the whole register stood under a civilization
that had already ended. This is the repair, and the measurement that shows it worked._

## 1. The cause, stated exactly

`HistoricalPresence.spawnCivId()` decided whose people stand at a place. Its order was:

```
occupant → ruler → site's civHint → present map → ohm → hinterland → border → neutral
```

The fourth entry is the defect. **A site's `civHint` says who founded the place, not who holds it
now.** Anyang's hint is `china_shang` for all time. So when the clock moved to 430 BC — 616 years
after the Shang fell in 1046 BC — the place still answered "Shang", and the spawner filled it with
Shang names.

Two extra faults fell out of the same seam:

- the ruler branch hands back a **ruler-register polity slug** (`jin`) which is not a civilization id
  in any pack: 5 live NPCs carried `jin`, which resolves to nothing, so they had no civilization,
  no name pool, no standing;
- the `CivHints` alias table (`indus_valley → indus_valley_civilization`) maps a pack id to a
  **polity** spelling: 13 live NPCs carried an id that exists nowhere. That is why the Indus-site
  crowd had Hindi names — nothing knew whose they were.

## 2. The fix

One rule, in one place: **the people of a place belong to a civilization that is alive in that year,
or to none.** The answer is now computed where the year, the manager and the ruler register are all
in hand (`HistoricalPresence.spawnCivFor`), stored on the result, and every candidate is checked with
`Civilization.isActiveInYear`:

| # | candidate | why |
|---|---|---|
| 1 | the occupant | already filtered to civilizations alive this year |
| 2 | the site's own hint | **only if that civilization still stands** — the fix |
| 3 | the hinterland's hint | same test |
| 4 | the recorded ruler | the register is asked by year already; its polity spelling rarely matches a civ id, so a miss falls through |
| 5 | the nearest civilization alive this year, **only when a ruler is recorded here** | somebody is known to have held this ground, so the people take the nearest living civilization of that year — at Anyang in 430 BC, **Zhou**. Without a recorded ruler nothing is assumed |
| 6 | the border (its own years), the map layers | as before |
| 7 | `neutral` | the honest answer when the record names nobody |

The 1,000 km bound on step 5 is deliberate: wide enough for a steppe empire whose capital is far from
its frontier, narrow enough that empty sea and desert are not filled with somebody's townsfolk.

## 3. The measurement: before and after, same probe

`worldfill/probes/EraCivProbe.java` (new, in the gate list as `probe_eraciv`) asks the game's own
question at the places that were played, then sweeps 6,000 random points × 14 years and requires
**every** answer to be a sentinel or a civilization alive in that year.

The same probe, run against the old class and the new one:

| | Anyang, 430 BC | the world sweep |
|---|---|---|
| **before** | `jin` — a polity with no civilization at all | 1,394 named answers, **7,165 outside their civilization's years** |
| **after** | `china_zhou` (Zhou, −1046..−256) | 2,850 named answers, **0 outside** |

The named-answer count rises from 1,394 to 2,850 because the old answers were often ids that resolved
to no civilization at all; they are now real ones or an honest "none".

The places that were played, after the fix:

```
  Ur                          -2500  sumer                Sumerian City-States (founded -4500, fell -1900)
  Giza                        -2500  egypt_ancient        Ancient Egypt (founded -3100, fell -30)
  Anyang                      -1200  china_shang          Shang Dynasty (founded -1600, fell -1046)
  Anyang                       -430  china_zhou           Zhou Dynasty (founded -1046, fell -256)
  Indus site (32.45,69.04)    -1200  neutral              no civilization named (the record names none)
  Mohenjo-daro                -2500  indus_valley         Indus Valley Civilization (-3300..-1300)
```

`EraCiv: 16 passed, 0 failed`.

## 4. The guard, so it cannot come back quietly

Two additions that will shout if the seam is reopened:

1. **In-game:** `/ee check all` now carries *"Nobody stands after their own civilization fell"*. It
   asks **both** halves of the world: the people places remember (`PeopleMemory.everyone()`, new) and
   every loaded person actually standing in the level, applying the same year rule to what is really
   there rather than to what the code intends.
2. **Offline:** `probe_eraciv`, part of `verify_all.sh`, with the 6,000-point sweep.

### The guard, tested on a live server rather than trusted

A first version passed on the server saying *"0 person(s) held"* — which proves nothing, and this
project does not accept nothing as green. So the guard was made to read standing people too, and then
made to bite, on the headless Forge server with a real world:

| what the world held | year | the guard said |
|---|---|---|
| nothing but 6 rival-dimension variants (not people of the history world) | −430 | *"this world holds no person to ask, so nothing was proved here"* — counted as neither pass nor fail |
| one NPC, civilization `china_shang` | −430 | **[FAIL]** 1 of 1 outside its civilization's years — the exact defect of Anyang |
| the same NPC, changed to `china_zhou` | −430 | **[ OK ]** "1 person(s) held under a named civilization (1 standing in the loaded world), every one of them inside its years" |

End of check on the live server with the fixed person: **438 passed, 0 failed, 12 known limits**
(the 438th is this new check, which the headless harness cannot run). Two bugs in the guard itself were
found this way and fixed: it reported a healthy world *in the same line* as a failure, and it counted a
rival-dimension variant as a person with a civilization.

## 5. What else this session had to fix, and one thing it caught me at

- The toolchain is not in the workspace between sessions (`build/` and `.cache/` are excluded from
  snapshots), so JDK 17 was re-downloaded and the whole Forge userdev cache rebuilt — 702 MB — before
  a single line could be compiled. Worth knowing: **a "no known defects" verdict decays if the
  evidence can't be rebuilt.**
- A **performance check caught my first version**: *"one place's full answer takes 5.9 ms on average
  (limit 5 ms)"*. I nearly accepted it as my regression — it was not. Measuring old and new
  back-to-back in both orders gave 3.5 vs 3.6 ms (new first) and 3.4 vs 4.7 ms (old first): the
  number was dominated by the order the runs happened and by the machine's load, and my change adds
  nothing measurable to the null-manager path the check exercises. **Self-correction 30: a wall-clock
  check in a shared sandbox is flaky, and the honest way to read a flaky check is to run the two
  variants in both orders, not to believe one number.** The check itself should probably measure best
  of five rounds rather than three; noted, not changed.
- The jar is rebuilt and reproducible: **`4170bca6…`** (`JAR_SHA256.txt`), 14 jar checks 0 failed.

## 6. The world you already played (board 17b)

The first fix repairs everybody drawn from now on. It does nothing for the 923 people already saved
in `New World` — and telling the user to walk about until the crowd happens to be re-drawn is not a
fix, it is homework. So the same question is asked again of the people who are already there.

**`WhoBelongsHere`** — one rule, three doors:

| door | when | why there |
|---|---|---|
| a person joins a level | on load from a save, on a crowd draw, on a recall from a place's memory | a person is in the world exactly when they join it, so this cannot be forgotten and never misses a chunk that loads later |
| the year is moved (`/ee year set`) | immediately | moving the clock past a civilization's fall must not leave its people standing for another minute |
| once a minute, while the world runs | every loaded person, plus the people a place remembers but is not standing up | the clock moves on its own; a person drawn in one century must not still be standing in another |

What it does **not** do: change a name, an age, a role, a coat or a memory. Only whose person they are.
Nothing is guessed from a place the projection cannot name (a NaN coordinate leaves the person alone
and the in-game check reports them) — wiping a name because a lookup failed would be worse than the
defect being repaired.

### Measured

`probe_repair` (in the gate list), asking the rule itself on the real tables — **9 passed, 0 failed**:

```
OK   Anyang 430 BC: a person carrying china_shang is put right (now china_zhou)
OK   the Indus site 1200 BC: a person carrying the dangling indus_valley_civilization id is put right (now neutral)
OK   Rome 100 CE: a Roman is left alone
OK   open ocean 1500: a person with no civilization is left alone
OK   Anyang 1200 BC: a Shang is left alone
OK   a person carrying the ruler-register spelling 'jin' is given a real civilization in 430 BC (now china_zhou)
OK   the repair is idempotent: running it again leaves china_zhou in place
OK   the sweep: 3000 people asked again over 8 years, 2090 of them put right, and not one left outside their civilization's years
OK   a repaired person is given exactly what a person born there this year would be given (400 of 400 agree)
```

And on the live Forge server, with the old ids put back into the world on purpose:

```
[Civilization] Human NPC was china_shang after its time; now neutral in -430
[Civilization] Human NPC was china_shang after its time; now neutral in -430
[Civilization] Human NPC was indus_valley_civilization after its time; now neutral in -430
```

— a person summoned carrying the Shang in 430 BC, and another carrying the dangling Indus alias, both
corrected the moment they entered the world; a person carrying `china_zhou` (right for that year) was
left untouched. The check then read, on that world:

```
[ OK ] Nobody stands after their own civilization fell: 1 person(s) held under a named civilization
       (1 standing in the loaded world), every one of them inside its years
end of check: 438 passed, 0 failed, 12 known limits
```

*(The two corrected people read "neutral" because the headless server's test world puts those blocks
in the Gulf of Guinea, where nobody rules in 430 BC — an honest answer, not a failure to answer. The
Anyang answer itself is the `china_zhou` line above and the 22nd row of the sweep.)*

## 7. What the user should do next

Nothing to sweep, and nothing to re-draw: install the jar and open the world. Every person already in
it is put right as they load (§6). To see it:

1. load the new jar on that world, at **430 BC**, stand at Anyang (`/tpll 36.126 114.313`);
2. move a few hundred blocks away and back (the crowd is re-planned per chunk and per year), or simply
   walk into a town that has not been drawn yet;
3. `/ee check all` — the new line reads the people standing around you *and* the people the places
   remember, and says how many fall outside their civilization's years. On an unvisited world it will
   say honestly that it has nobody to ask; walk into Anyang first, then run it. It should read
   **0 outside**;
4. `/ee villager who` (or the town crier) at Anyang should now name **Zhou**, not Shang.

R4 in `FINAL_TEST.md` can only be called passed when that has been seen on the screen.

## 8. The jar to install

`eternal/build/libs/eternalengine-1.0.0.jar`,
sha256 `eba0c1debe3af6a92b78f42c962f024ce3cc39003b1e4f78df825df5f0c16b58` (`JAR_SHA256.txt`);
`verify_jar.py` 14 checks, 0 failed.
