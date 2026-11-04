# Group 2, people and places: review (2026-10-12)

The 12 systems from `WORLD_SYSTEMS.md` (#8 to #19). How this was checked:
- **A live run, for the first time with a player in a town.** In the sandbox, a fake player stood in Kolkata in
  1850, and the mod's own spawner, talk, crowd and sound ran for it. The tools are the sandbox-only test helper
  (`testmod/`, `EE_TEST_HELPER=1 tools/run_test_server.sh run`) and `eetest player join`, `eetest people`,
  `eetest crowd walk`. A player run of `/ee check all` gave **ALL 93 CHECKS PASSED**.
- **Reading the code** of each system, looking for crashes, things never saved, things never called, and lag.

## The verdict in one line

The systems work, and villagers stand, talk and fit the place's history. But **a place forgets most of its
people**, **the names are often from the wrong region**, and **the first villager costs a 1.3-second freeze**.

## System by system

| # | System | Verdict | Evidence |
|---|---|---|---|
| 8 | Historical presence | **works** | `/ee check all` sections 7 to 12: the same answers as when the data was built, at 400 points x 13 years and 52 places |
| 9 | Population ladder | **works** | Census numbers for only 6 regions; estimates (HYDE) everywhere else. That's a data limit, not a bug |
| 10 | Villager spawner | **works since step 16, two problems** | 36 townspeople at Kolkata 1850, with talk. Problem 1: the people are forgotten (see #14). Problem 2: its first run took **1,290 ms** on the game's main thread, because it loads the history data the first time. That is the "Tick budget exceeded! Avg: 270ms" and "Can't keep up!" in your log right after you joined |
| 11 | Crowd figures | **works since step 16** | 352 to 795 figures, all findable by their own ID, nobody twice. Open: figures you walk away from keep standing |
| 12 | Villager talk | **works** | "This land belongs to the British Empire, ruled by Victoria", "People here speak Bengali", the way of life, the Grand Trunk Road. They never say the town's name |
| 13 | Human NPC (the villager) | **works** | The look is painted by your game client from the villager's ID (on the server every skin reads "default", which is normal). Only your eyes can check it |
| 14 | Villager memory | **broken by Minecraft's own despawn** | Walk 208 blocks away and back: only **17 of 37** people were the same, 20 were strangers. The memory has room for 64 per place and works, but Minecraft's despawn rule deletes townspeople first (every tick, without telling the mod). The spawner's own copy of that rule, which does remember them, only runs every 2 seconds. Only crowd figures are marked "keep" |
| 15 | Background agents | **dormant** | Nothing in the code ever fills it; it costs 0.003 ms per tick |
| 16 | Villager behavior | **a foundation only** | Reached by commands; no effect on its own |
| 17 | Names and skins | **names from the wrong region** | Kolkata 1850 got Telugu Hyderabad names ("Ryot Kishtaiah Setty", "Vepari Ahmed Qureshi"). The name list follows the *ruling state's* ID, and any ID containing "india" goes to the Deccan (Telugu) list. A culture it doesn't know gets a general English list: probably your "Alex Stone" in Hyderabad 1948. The talk already knows the right answer: "People here speak Bengali" |
| 18 | Crowd sound | **works, but the costliest system** | 0.80 ms on **every tick** (worst 60 ms). It recounts people and looks up the population 20 times a second, just to decide whether a sound is due |
| 19 | Current affairs | **works** (code read) | Right-click briefings; a right-click needs a real client |

## Proposed fixes

| | Fix | What you would notice | Size |
|---|---|---|---|
| **A** | **Keep the people.** Townspeople leave only through the spawner, which remembers them, not through Minecraft's despawn, which forgets them | Walk away and come back: the same people, with the same names | small |
| **B** | **Names fit the place.** The name list follows the language people speak at the place (the same data the talk uses), and falls back to the ruler's culture before 1500 or where no language is known. "india" no longer means Telugu | Bengali-region names in Kolkata, Telugu names in Hyderabad, no English names in India | small–medium |
| **C** | **No lag.** (1) The history data loads in the background when the world starts, so the first villager doesn't freeze the game. (2) Crowd sound checks once a second instead of 20 times | No freeze when you join; the costliest system costs about 20 times less | small |
| **D** | **Talk extras** (optional, new content): villagers also say the town's name ("This is Calcutta") and, where known, the head of government | One or two more lines of talk | medium |

Kept as designed unless you say otherwise:
- The job word in front of a name ("Ryot", "Vepari", "Shilpi": the period's words for farmer, trader, craftsman).
- The two dormant systems (#15, #16).

Open question from step 16: should crowd figures far from every player be cleared? Each figure's identity is
fixed by its spot, so the same people would come back on return. In the walk test the count grew from 352 to 758
over 60 blocks.

## Also done in this step: the last two core blemishes (from your log)

- The state was saved twice at every shutdown. Now once: checked in the test server's log.
- A new single-player world paused history for about a second before you joined, switching the day/night cycle
  off and on and saving. Single player now waits 15 seconds before a "nobody is online" pause. Dedicated servers
  pause at once, as before.

## Done in step 17 (you skipped the choice, so the recommended options: A, B, C, and clear far figures)

| | What changed | Test result (sandbox: a fake player in Kolkata, 1850) |
|---|---|---|
| A | The spawner's people are out of Minecraft's despawn (`HumanNpcEntity.removeWhenFarAway`). Once every 2 seconds the spawner checks all its people in the world: past 128 blocks from every player they are remembered, then removed (`PresenceLocalSpawner.forgetFar`) | Jump 1,000 blocks away and back: **33 of 37** the same people (before: Minecraft deleted all of them on the next tick, unremembered) |
| B | Names follow the language people speak at the place (from 1500 on), else the ruling state. "india", British Raj and the East India Company get the Indian list, not the Deccan's | Kolkata now gets North Indian names ("Karigar Durga Gupta"; before: "Ryot Kishtaiah Setty"). `probe_name_pools.sh`: 11 of 11 places get their expected list (Hyderabad: Telugu; Bombay: Indian, before Greek-Roman; Lagos: Yoruba region African) |
| C | The history data loads in the background when the world starts, and the spawner and crowd sound wait for it. Crowd sound works out the crowd once a second | Spawner's worst moment **1,290 → 116 ms**; crowd sound **0.80 → 0.054 ms** per tick; average mod time per tick 3.28 → 0.48 ms; "loaded in 3.9 s in the background, so nobody waited for it" |
| Crowd | Figures past 128 blocks from every player are taken out (they need no memory: their identity is their place) | Walk away: the figures there were taken out (352 → 36 near the start); walk back: they stood again as mostly the same people (470 standing, 104 new identities ever seen) |

`/ee check all` as that player: **ALL 94 PASSED**; from the console: 91 passed, 0 failed. `probe_core.sh` 11/11,
`probe_check.sh` 73/70/0/3, `probe_crowd_box.sh` 8/8: all unchanged.

**What is still limited:**
- Walking slowly through new ground still invents people along the way. Where no town centre is within
  128 blocks, the district follows the player, so every few steps there is a new district with new people. After
  a 208-block walk away and back, 8 of 38 were the same. In the sandbox the town centre is never in range: the old
  Terra++ jar's projections disagree, so the centre comes out in the wrong place. In your Terra++ world a town's
  centre should hold the district still, but that is not tested.
- Name lists are thin (12 to 27 names each). There are none for English, French, Spanish, Russian and other European languages (those
  places keep the old list, which is often the Greek-Roman one), none for Bengali or Tamil (they share the Indian
  and Deccan lists), and the Persian, North African and Mesopotamian lists are rulers' and gods' names. Real lists
  per language would be a data step (Wikipedia/Wikidata).
- Kept as designed: the job word in front of a name ("Karigar", "Ryot"), and the two dormant systems.

