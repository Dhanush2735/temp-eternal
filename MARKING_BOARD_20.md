# Marking board 20 — R2-d: half the world was named "Villager Alex Stone"

_2026-10-24. Second step implemented under `COMPLETION_PLAN.md`. Requirement 2, step R2-d._

## First: my own previous claim was wrong, and the code said so

On board 19 I wrote that "only 1.4% of the polities the register can name have a civilization record" and
called that the real blocker. Checking before building, the project had already refused that fix on
purpose, and written down why (`RulerRegister.deccanPolities`):

> *CivSynthesis registers every polity it is handed as a simulated civilization, and the population,
> agriculture, economy, migration and technology engines all iterate every registered civilization.
> World polities stay names on NPCs.*

Bulk-synthesising 1,542 civilizations would have made every engine iterate 12× its list **per tick** — R2
paid for with R7. The same comment makes a second claim: those NPCs are still named, because
`VillagerNameDatabase.cultureFor` needs no record. **That second claim is the one I tested.**

## The measurement (before any change)

A new probe, `worldfill/probes/NameCoverageProbe.java`, asks `cultureFor` for every polity id the register
can answer with:

```
pool            polities   share
african              52    3.3%
americas             14    0.9%
deccan               12    0.8%
east_asian          128    8.2%
global              818   52.2%     <-- "Villager Alex Stone"
indic                76    4.9%
mediterranean       294   18.8%
mesopotamian         13    0.8%
north_african        51    3.3%
persianate          109    7.0%
```

**818 of 1,567 polities — 52.2% — fell through to the generic pool.** A town in Ahmadnagar, Achaea, Angkor
or Ayutthaya was peopled by "Villager Alex Stone". `cultureFor` reads the civ id as a *string* and matches
keywords, so it covered the ids somebody thought of and failed silently for the rest — and no keyword list
can be completed by hand against a register that holds ~1,500 polities and grows.

## The fix: read *where* the polity was, not how it is spelled

The register already holds the one thing a keyword can only guess at — `RulerRegister.Extent`, the centre
of the cells each polity actually ruled. New class `PlaceNamePools`:

1. turns that centre into one of the game's own name pools by latitude and longitude (nine boxes, most
   specific first: Deccan before India, Mesopotamia before the Persianate world);
2. runs **only after every keyword has failed**, so every id that was named correctly yesterday is named
   the same today;
3. invents no history — the pool is chosen by place, the same rule a person standing there would use.

One new pool was needed: **`southeast_asian`** (Thai, Khmer, Vietnamese, Malay, Javanese), because ~118
polities from Ayutthaya to Majapahit had a region and no pool at all. Written in the same style as the
existing ten, and marked illustrative like they are.

## The measurement (after)

```
pool            polities   share
african              83    5.3%
americas             71    4.5%
deccan               24    1.5%
east_asian          195   12.4%
global               10    0.6%     <-- from 52.2%
indic               101    6.4%
mediterranean       635   40.5%
mesopotamian         40    2.6%
north_african        94    6.0%
persianate          196   12.5%
southeast_asian     118    7.5%
```

**818 → 10 polities (52.2% → 0.6%).** The ten that remain are Pacific islands — Fiji, Mauritius,
Micronesia, New Hebrides — with no pool written for them. That is a *missing pool*, honestly counted, not a
resolver failing.

## Made permanent: it is now a check in the game

`/ee check all` carries a new line, with a **1% budget** written before the numbers were seen:

```
[ OK ] Every polity names its people: 1557 of 1567 polities get a regional name pool
       (10 island polities have no pool written for them)
```

Above 1% it fails and names the first offender, so the resolver cannot quietly stop answering again.

## The gates

| gate | result |
|---|---|
| `compileJava` | **BUILD SUCCESSFUL — 1,238 classes** |
| `command_surface` | **220 commands: 220 PASS**, 0 refused, 0 PARSE-FAIL, 0 THROW, 0 TIMEOUT, 0 LEAK |
| `/ee check all` (headless) | **423 passed** (was 422 — the new check), **12 failed** = the recorded baseline, unchanged |
| `probe_name_coverage` | **FINDINGS → 10 of 1,567** (0.6%, inside the budget) |
| `probe_vocabulary` | still **PASS — 0 undeclared** |

## What this step did not do

- **It did not give 1,542 polities a civilization record** — that remains the wrong trade (it costs R7). What
  a person in Ahmadnagar still lacks is the *civ-level* things: local money, local clothes, a local market.
  They now have a name, a language-flavoured identity and a pool of occupation words. That is the honest
  half of the fix, and the other half is R4's work, one polity at a time.
- **It did not touch any existing name.** A regression here would have been invisible in aggregate numbers,
  which is why the check is a budget and not a count of successes.
- **The pools are coarse by design** — eleven (now twelve) pools for the world, not one per dynasty. The
  project chose that deliberately and this step keeps the choice.

## What this step found that matters

The same shape of defect as board 19, and as your 18 townspeople, and as the 18 vocabulary ids:

> **A name that resolves to nothing is not an error anywhere. It is a silent fallback, and silent fallbacks
> are how a world of 1,567 polities ends up sounding like one village.**

Every one of these four defects was invisible in the gates and visible only by asking the data directly.
That is the method this phase is now using: for each register, ask "what happens to the ids nobody thought
of?" — and count it.

## Verdict of this step

**PASS, and user-visible.** Half the world's townspeople were generically named; 99.4% of them now are not.
No gate moved, the regression is now guarded inside the game, and the "1.4% of polities have a record"
claim I made on board 19 is corrected here: **the record is not what names a person — and the naming was
the part that was actually broken.**
