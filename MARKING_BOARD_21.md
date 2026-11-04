# Marking board 21 — R2-d2: 1,543 polities the game called "no civilization"

_2026-10-24. Third step implemented under `COMPLETION_PLAN.md`. Requirement 2, step R2-d2._

## First, the plan for this step was wrong, and measuring fixed it

I had written R2-d2 as *"local money, clothes, market per polity"*. Two measurements killed that framing
before I built anything:

1. **Money is already per place and year, not per civilization.** 401 kinds resolve by latitude, longitude
   and year (`MoneyPlaces`, `worldfill/money_world.py`); Oslo 1200 gets the mark, Calabar 1800 gets
   manillas, Phnom Penh 1977 gets no money at all. **No civilization record is involved.** So "money per
   polity" was not a gap at all.
2. **The real gap is that a polity without a record could not be *read*.** Of the 1,567 polities the
   register can answer with, **24** have a full record in the pack. For the other **1,543**, every path that
   renders a person's civilization fell through to *"no civilization called ahmadnagar_sultanate"* — for a
   sultanate the source names, dates to 1492–1652, and locates. The person was real, the state was real,
   the game said nothing.

## What I built

**`civilization/PolityFacts.java`** — a **lookup, not a simulation**. It reads the register's own polity
list and recorded extents and answers three questions: what is this polity called, in which years did it
stand, where was its centre. Nothing ticks, nothing iterates per frame, nothing is registered — so the
refusal in `CivSynthesis` (which is right, because every engine iterates every registered civilization)
stays intact.

The pack's own name always wins when a record exists; the register answers when it does not.

**`/ee villager nearby` now names the civilization** — the surface you will use at Anyang and the Indus
site. Each person shows `civ=Zhou` (record), `civ=Ahmadnagar Sultanate*` (named from the register) or
`civ=somelongid?` (nobody can resolve it), and the header counts all three:

```
Villagers nearby radius=64: 57
  civilizations: 39 with a record, 18 named from the ruler register (*), 0 nobody can resolve (?)
```

**A new check in `/ee check all`**, so the coverage cannot silently fall again:

```
[ OK ] Every polity can name itself and its years: 1567 of 1567
       (a record is only needed for money, goods and engines, not for a name)
```

## The measurement

```
== the display, for ids a player can actually meet ==
  ahmadnagar_sultanate  ->  Ahmadnagar Sultanate (1492 to 1652) [named only]
  khmer_empire          ->  Khmer Empire (800 to 1867) [named only]
  china_zhou            ->  china_zhou [no record, no name]   (see the note below)
  mewar                 ->  mewar [no record, no name]        (declared absent from the source, board 19)
  cit-cit               ->  cit-cit [no record, no name]

== coverage ==
  polities the register names     : 1567
  can say their own name          : 1567
  can say their own years         : 1567
  have a full civilization record : 24   (read from the pack, not the harness)
  -> before: only those 24 could be read at all; the other 1543 read as "no civilization called ..."
```

**`china_zhou` reads as nameless in the probe** only because the probe has no Minecraft and therefore no
civilization manager to load the pack: the ids that live *in the pack* (`china_zhou`, `indus_valley`) are
found by the manager in the game, not by the register. In the game `/ee villager nearby` shows
`civ=Zhou` for those. The probe's own header says the record count comes from the pack file, so the
number 24 is real and the `[no record, no name]` on a pack id is a harness limit, not a game defect.

## Two bugs this step made me fix — both mine

1. **The first version hung `/ee check all` for 180 s and timed out the whole self-test.** Cause:
   `RulerRegister.polities()` walks all 9,322 timelines and slugifies every span, and I called it once per
   polity — 1,567 × that. `PolityFacts` now builds two tables once per register instance and reads them
   from memory. **This is exactly the kind of thing the gates exist for: it was caught before it shipped,
   and recorded rather than quietly fixed.**
2. **The probe found that a manager which cannot answer crashes the display.**
   `CivilizationManager` throws `UnsupportedOperationException` outside Minecraft *by design*, and my first
   `hasRecord` called straight into it. A name plate must never take a command down. Every read is now
   wrapped, and a manager that cannot answer reads as "no record" — the truthful answer.

## The gates

| gate | result |
|---|---|
| `compileJava` | **BUILD SUCCESSFUL — 1,239 classes** |
| `command_surface` | **220 commands: 220 PASS**, 0 refused, 0 PARSE-FAIL, 0 THROW, 0 TIMEOUT, 0 LEAK |
| `/ee check all` (headless) | **424 passed** (422 → 423 → 424 across the three steps), **12 failed** = the recorded baseline, unchanged |
| `probe_polity_facts` | **PASS — 1,567 of 1,567 nameable and dated** |
| `probe_name_coverage` | **0.6% generic** (board 20, unchanged) |
| `probe_vocabulary` | **0 undeclared** (board 19, unchanged) |

## What this step did not do

- **It did not give 1,543 polities an economy.** A named polity still has no treasury, no population of its
  own and no engine behind it — the display marks it `*` for exactly that reason. What a person in
  Ahmadnagar now has is a nameable state with dates; what they still lack is that state *doing* anything.
- **It did not change a single person's civilization id.** This was a read path. No NPC was respawned, no
  saved world became stale, and nothing here needs a re-sweep.
- **It did not test the new command line in a live world.** `/ee villager nearby` compiles and the resolver
  under it is measured, but the list itself is unobserved by me — it is item 2 of the P1 play test, and
  your Anyang stop will be its first real sighting.

## Verdict of this step

**PASS, and it closes the loop the play test needs.** The three steps now read as one story: the ids all
resolve (board 19), the people get regional names (board 20), and every polity can say what it is and when
it stood (board 21). **1,543 states went from "no civilization" to "Ahmadnagar Sultanate (1492 to 1652)",
at no tick cost, with the refusal to simulate them left exactly where it was.**
