# How I must think and test

Written 2026-10-22 (turn 233) from the Secunderabad lessons (turns 230-232). These rules exist
because the user found a bug my tests could not: a market town standing in 3000 BC. They are the
answer to "how can you match my expectations of logical thinking and testing?" - not a promise,
a checklist. If a rule here is not being followed, the work is not done.

## Thinking rules

1. **World first, code second.** Every system starts with a claim a player could verify: "at
   PLACE in YEAR, the player sees X and never Y". If that sentence cannot be written, the system
   is not understood yet, and no code should be touched.

2. **The one-second glance.** Before anything visible ships, ask: what would a person say in one
   second looking at this screen? ("A market town in the stone age. That is wrong.") That
   sentence is the specification. Encode it as a test.

3. **Ordinary cases first.** For every system ask: where is the most ordinary place and year this
   touches? What does the empty case show? What does the silent case show? Highlights (famous
   places in famous years) are the last thing to check, not the first.

4. **Defaults claim the least.** Every `orElse`, `else` and `default` that produces content must
   produce the smallest honest claim: countryside not village, nobody not somebody, unknown not
   average. A default that invents abundance is a bug even when it compiles. (The Secunderabad
   bug was exactly `orElse(SettlementRank.VILLAGE)`.)

5. **Facts wear their labels.** "The model says", "the data says", "history says", "I checked".
   Never present a guess, a fallback band or a model output as history. (I once quoted
   `floorBand`'s 200-person floor as "250 foragers who really lived there".)

6. **Fix the answer, not the listeners.** When a source returns a wrong answer, correct the
   source. Consumer-side patches are defense in depth only, never the fix. (Turn 230 taught
   three call sites to distrust `rank()` while `rank()` kept lying.)

7. **Sibling sweeps.** When a bug is found, name its error shape (silent default, untested
   composition, year-blind lookup, fabricated fallthrough...) and grep the whole codebase for the
   same shape. Fixing one instance is not the fix.

## Testing rules

1. **Claims before machinery.** A test that checks the code's own rules (budgets, consistency,
   coverage of branches) is never the acceptance test. The acceptance test is a claim: place,
   year, what must be visible, what must be absent.

2. **A test must FAIL when the answer lies, never explain it.** A test message that apologizes
   for the output ("is only the model's countryside") is not a test.

3. **Expectations come from evidence, not from the function under test.** Compute what should be
   true from the raw inputs (sites, maps, towns, borders, years). Never ask the accused function
   what the correct answer is.

4. **Every test set includes the ordinary case.** At least one place nobody would put on a
   postcard, in a year nothing happened. Routes, probes, scenario runs: all of them.

5. **The player's eyes stay in the loop, with frames.** The test takes the screenshots, and the
   frames include ordinary stops, not only the postcards. Where a wall blocks a check, the run
   states an in-run alternative (turn 227 rule).

6. **When the user finds a bug:** correct the source, add the test that would have caught it, run
   the sibling sweep, and write it all down - in the same turn.

## Communication rules

1. Verdicts in simple words, always. Plain language first; detail after.
2. Every claim wears its status: proved (ran and saw), declared (stated on authority, sourced),
   or guessed (say so).
3. End every reply with the step-count line from `PROGRESS.md`. Never mix step numbers with turn
   numbers.
4. No em-dashes anywhere in written output.

## How the user can check me

- `claim-*` lines in every `/ee test everything` report show place, year and PASS/FAIL for world
  claims, including cells away from the player.
- The photo route's ordinary stops (R32+) put the boring world in the frames on purpose.
- If the user finds a bug before I do, the next run must contain the claim that would have caught
  it. That is the measure: the user's finds should shrink toward zero.
