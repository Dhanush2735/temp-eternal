# How everything in the project gets tested (turn 222)

One principle first: **every question is asked in up to three places**, and each place can only
say "true" where it actually knows:

1. **My sandbox** proves the rules (pure code, the data, the chains). Fast, every turn.
2. **Your world** proves the game obeys them (the runtime suite, in a live save).
3. **Screenshots and short clips** settle what no command can see (the look of a town, a dress, a
   frame of chat). The user captures them in game (F2 or any tool) and sends them here: they are
   read as images and judged against the same data the tests run on. A LIMIT that needs eyes
   becomes "needs a screenshot", and the analysis happens here with the user, not by guesswork.

A FAIL anywhere loops back: fix on my side, green here, rebuild, green there, report again.

---

## The map: every area and how it is tested

| Area | My side (sandbox) | Player side (runtime suite) | Eyes |
|---|---|---|---|
| **The data** (131 files: events, rulers, towns, prices, disasters, law, formations, battles...) | probes per pack, manifest + SHA byte-check, licences, `sweep_all.sh` (101+ probes) | `check all` loads and counts every pack in THIS world; the places phase reads the live registers | the era route spot-checks the wording |
| **The reading** (`/ee here`, the one-line form) | `probe_here.sh` (391 checks): nobody as nobody, estimates marked, guardrail, determinism | places phase re-asks the same rules in the live world | chat formatting at your GUI scale |
| **Talk and interaction** | talk logic probes (cards, topics) | talk to a villager at the checklist places: the always-there questions answer | the flow of the conversation |
| **Money, prices, trade** | `probe_market`, `probe_moneyworld`, `probe_buyers`, chains | **scenario E**: sell a hundred loads over some days, watch the price move and the purse add up | the trade screen |
| **People: presence, needs, households, jobs** | `probe_life`, `probe_lifetable`, households/jobs/day-round probes | `test movement` (real motion), walking-state counts; **scenario P**: a famine week, a household goes hungry in order | do they look like their century |
| **War: formations, battles, sieges** | `probe_lifetable` BattleRun (18/18), formation/battle tables | **scenario W**: declare a war, watch armies form up and a siege starve | the formations on the ground |
| **Law, rulers, borders** | `probe_step42` series, ruler register probes | `check all` part 14; ruler questions in talk at the route stops | disputed-land lines read true |
| **News, stories, knowledge** | `probe_knowledge`, `probe_cards`, story chain probes | ask villagers the news; **scenario N**: an event year, the news travels | does the story sound like its time |
| **Timeline, branches (req 5)** | chain probes (232 checks) | **scenario T** (after step 63 wires it): change one deed, watch a branch fork and carry its own story | the branch tree readable |
| **Paradox, broken dimensions (req 6)** | probes (201 + 168 + 146 + 113 checks) | **scenario X** (after step 63): break a fixed point, land in the broken world, ask what is wrong | the rupture visible |
| **Players: permissions, pockets, property** | 329 checks (step 52) | a second player is needed: LIMIT named in the report | voting, ownership |
| **Performance (req 7)** | perf probes, budgets | `/ee performance` twice around a busy market; a long walk; heap and spawner-cycle watch items | frame feel on your machine |
| **Commands** | the 215-leaf static audit | `/ee test all` smoke; every leaf answers or refuses as designed | the help text |
| **Terra++ boundary** (buildings, roads by year) | interface stubs, hook contracts | the era route: 31 place-years, data side auto (reading + presence), the rest your eyes | the standing buildings |

## The five layers of the net

1. **Per-class probes** (my side): each class alone, fast, thousands of checks.
2. **Chain probes** (my side): class meets class (the step-61 lesson: every part green while the
   chain was broken).
3. **Gates** (my side): syntax gate on every file, manifest bytes, licences, size budget.
4. **Runtime suite** (player side): the phases in `runtime/DESIGN.md` - engines, commands, places,
   living, screen - and the **scenarios** listed above (E, P, W, N, T, X), each one: set up,
   let time pass, judge the consequence, write it in the report.
5. **The human session** (`eternal/FINAL_TEST.md`, 55 tests): the final walk, once the wiring
   phase and scenarios are in. Its results are the last input.

## The regression net

Every fixed bug becomes one guard that never comes back: the 83 `Findings` rows get their own
assertion where the bug is judgeable (rows like the doubt-1 spot and the walking rule already
have them), and every future FAIL in a report gets its guard before the fix is called done.

## What "tested" means when it is all done

- Every one of the 166 systems carries at least one **live** assertion or a named LIMIT with what
  would settle it. Nothing is only "wired to nothing".
- Every one of the 7 requirements has an acceptance run: (1) the era route, (2) the places phase
  world-wide, (3) scenarios P and W, (4) scenario E, (5) scenario T, (6) scenario X, (7) the perf
  runs.
- Every world the user cares about can be certified with one command and two report files.

## Order of work

1. World-file reader (the user's zip), so expectations are the world's own facts.
2. `EeCommandSelfTest` counters (kill the first LIMIT).
3. Scenario E (economy day), then P (famine week).
4. Step 63 (the fork and paradox doors), then scenarios T and X against them.
5. Guards for the 83 rows, as each is touched.
6. The FINAL_TEST session, when the user walks it.

## The screenshot channel (the suite is the photographer)

**The user's rules, standing (turns 223-225): if anything needs to be SEEN in the game, the way to
see it is a screenshot - and the runtime test takes it. No separate photo command exists; the
camera is a phase of the one command, `/ee test everything`.** The agent never asks the user to
look and report; the player plays (or just stands there), the test shoots, and the judging happens
here against the data packs. Screenshots are the agent's eyes.

One run of `/ee test everything` photographs everything that is judged by eye, in this order:

| The question | The frame (all from the one run) |
|---|---|
| What does this exact view look like? | `etest_now_<lat>_<lon>_<year>_a/_b.png` (two frames, a second apart) |
| What does the sky look like in this year? | `etest_sky_day.png`, `etest_sky_night.png` (the clock is put back after) |
| What do the place-years look like? | the era route, 31 stops, two frames each (`etest_r07_rome_ad0100_a/_b.png`); the test pilot walks a loop through every stop, so the frames catch the world mid-stride and the walking-reaction systems run |
| Do accents, wrapping and GUI scale hold up? | `etest_book_accents.png` (a test book page, shot last so its screen blocks nothing) |

For any other century of sky or view: set the date and run the test again. The photo report
(`eternal_photo_report.txt` / `.json`) lists every frame with its watch line and the data reading
for that place-year, so the folder and the report travel together. A picture keeps its pixels, so
this channel also settles the NEEDS_A_REAL_SCREEN rows (Findings 11, 14, 19, 30: accented names,
chat readability, GUI scale).

What no screenshot can carry now has an in-run instrument anyway (turn 227): frame smoothness is
measured (`etest_perf.txt` per shot, server tick ms per stop), and hours of play is compressed into
the day-pass (a full day round borrowed and returned). What still says "human" in the report: a
real second multiplayer player, and the feel of many real hours.


## 2026-10-22 (turn 232): the discovery rule (why the USER found the Secunderabad bug first)

The bug sat in the most ordinary kind of spot in the whole world: an ordinary place in an
ordinary year. The test program never went to one. It asked questions of the player's feet and
of famous places in their famous years - a highlights reel - while machinery checks (crowd
budgets, talk honesty) passed happily around the absurd scene.

Standing rules from now on:

1. **Every run carries world claims at fixed points away from the player** (`claim-*` items in
   the living phase): ordinary cells in ordinary years plus two history itself speaks for. The
   expectation comes from the evidence fields, never from a derived boolean.
2. **The era route carries ordinary stops too** (R32 Secunderabad 3000 BC, R33 Central Australia
   3000 BC, R34 Swiss farmland 1200), so the frames show the ordinary world, not only the
   postcards.
3. **When a system ships, its last test is a claim**: "at PLACE in YEAR, what must be visible and
   what must be absent". A machinery rule (the code obeys the code) is never that claim. The
   one-second player glance ("does this scene make sense?") is the specification; encode it.
4. **Ordinary means ordinary**: for every new route or probe table, at least one stop must be a
   place nobody would put on a postcard, in a year nothing happened.


## Pointer (turn 233)

The full working method this plan now follows - thinking rules, testing rules, communication
rules - is written in `worldfill/WORKING_RULES.md`. If this plan and that file disagree,
WORKING_RULES.md wins.


## 2026-10-22 (turn 235): coverage after the autonomous build

`/ee test everything` is now the single entry the user runs. Direct tests: query-level claims
(route-claims over the 34-stop claim table) and 120 random ordinary looks (world-sampling), the
living-phase claim probes, engines and commands counters. Indirect tests: the camera route
itself - the test drives the player with /tpll and jumps time at its own discretion - and at
every stop the claim verdict is judged from the real people standing nearby and written beside
the frames. Judgment happens in the game's own report; the user interferes with nothing.
