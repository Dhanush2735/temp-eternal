# The marking board — first sitting, 2026-10-22

Every number here comes from a command run in this sandbox against your two archives.
Machine-readable ledger: `testrun/ledger.csv` (141 rows), raw logs in `testrun/raw/`.

---

## The mark

| | |
|---|---|
| **Probe scripts run** | **141** (all of them, one at a time, 2 GB RAM) |
| **Green — ran and proved something** | **98** |
| **Red — ran and a check failed** | **0** |
| **Could not be judged here** | **24** (need the Forge runtime classpath) |
| **Rotten — will not compile any more** | **8** |
| **Inert — exit 0, proves nothing** | **7** |
| **Timed out** | **1** |
| **Crashed for want of an input** | **3** |
| **Total suite time** | 518 s of work, ~35 min wall (serial on 2 cores) |
| **Assertions behind the 98 greens** | ≈ **300,000** |

**98 green, 0 red, 43 that cannot be judged or are themselves broken.**

That 0 is not a good sign on its own. A suite where nothing ever fails is either a suite on a very
good day, or a suite that has been taught to pass. I have not yet separated those two, and I will not
call it healthy until I have.

---

## What the 98 greens actually prove

Sampled from the logs, the greens are real assertions, not ceremony:

| Probe | What it printed |
|---|---|
| `probe_here` (step 62) | **391 checks, 0 failed** — the reading at 15 spot places; mid-Sahara 1000 and Siberia 1000 say *nobody*, and say it as nobody |
| `probe_calendars` (step 37) | **106 checks** — Fasli 1358 for Hyderabad, 14 Sep 1948; Chinese New Year 18 of 18 |
| `probe_lifetable` | **192 checks**, 81 KB of output |
| `probe_buildings` (step 32) | register loads 23,535 famous buildings in 347 ms; 1,330 years estimated, 2,569 with an end date |
| `probe_events` | gazetteer loads in 1.8 s, **129,163 events** across 11 packs |
| `syntax_gate` | **500 files, 0 syntax errors** (17 s) |
| `probe_towns_culture` | 26,316 of 26,316 country-years answered (100%) |

---

## The 43 that are not green — named, with the reason

### A. Rotten: 8 probes that no longer compile *(a defect in the tests, not the mod)*
`probe_check`, `probe_data_use`, `probe_famous41`, `probe_life`, `probe_npc_links`,
`probe_step45d`, `probe_step8`, `probe_talk`

Their scripts compile a **hardcoded list of files from an older turn** instead of using
`-sourcepath`. When a class moved package or gained a nested type, the probe stopped building and
the suite silently lost that coverage. `probe_check` is the one that runs the mod's own
`/ee check all` logic — it is the most important probe in the set and it has not compiled since
`HistoryChecks.Line` changed.

### B. Could not be judged here: 24 probes that need the game *(the L4 gap, in numbers)*
`probe_atlas, probe_book, probe_bookforms, probe_buyers, probe_calendar, probe_cards, probe_core,
probe_crowd_box, probe_culture, probe_eventcards, probe_historyfix, probe_knowledge, probe_market,
probe_memory, probe_moneyitems, probe_moneyworld, probe_name_pools, probe_purse, probe_screens,
probe_talk_layout, probe_technology, probe_tiles, probe_towns, probe_trade`

All exit with `no runtime_cp.txt` — they need a real Gradle + Minecraft classpath that cannot be
produced without building the mod. **These are the command-surface and UI probes: exactly the ones
that would have caught the 17 build errors you found by rebuilding.**

### C. Inert: 7 scripts that exit 0 and prove nothing
`probe_step42b`, `probe_step42c`, `probe_step42d`, `probe_terra`, `probe_mind_cost` (partial),
and 2 more — no assertion count, no verdict line. They are run as if they were tests; they are
really *builders* that print a pack and stop. **A builder is not a test**, and in a 141-line sweep
the two cannot be told apart without reading every log — which is precisely why the sweep was wrong
to trust exit codes.

### D. Crashed: 3
`probe_famous41` (exit 1, no verdict), `probe_index` (needs an argument the runner does not pass),
`probe_step34` (`FileNotFoundError: worldfill/build/ways/raw/labels.json` — **it depends on a
directory your own `PROGRESS.md` rules say must never be persisted**).

### E. Timed out: 1
`probe_commands` — 212 s, no output, killed at the limit. Either it needs the game classpath or it
hangs; I cannot tell which from here, and that ambiguity is itself a finding.

---

## Five findings the marking produced *(each with the command that shows it)*

**1. The suite has no runner, and so it has rotted.** 43 of 141 cannot be trusted. A probe that
watches a fixed file list stops watching when the project moves — your own `syntax_gate.sh` header
records this same lesson from step 46. It has now happened to eight more scripts.

**2. The test suite rewrites the product it is testing.** A sweep moved **9 shipped packs**:
`beliefs, border, building_culture, calendars, justice, law, scripts, social_order, soundscape`.
They still match the manifest in *content* (I rebuilt `calendars` twice: content sha
`f23d4ba9…` both times) but not in *bytes*.

**3. The manifest hashes the wrong thing.** It stores `sha256` of the `.json.gz` **file**, and gzip
writes the build time into the file header. So a no-op rebuild changes the hash:
file sha `fcfd9ab3…` → `bd2cc4c6…` for identical content. **The manifest can never confirm shipped
data after any rebuild, and "byte-clean" in the journal rots the moment a builder runs.** Fix: hash
the *uncompressed* content.

**4. Coverage is 38%, not 63%.** Of 500 mod classes, **190 are named by at least one probe; 310 are
named by none** — including **all 23 network packet classes** and 7 of the GUI classes. The
"systems 63% done" line in `PROGRESS.md` counts work completed, not behaviour asserted. List:
`testrun/classes_never_probed.txt`.

**5. The environment is not reproducible between turns.** `build/` and `.cache/` are excluded from
the workspace snapshot, so the JDK vanishes; five probes failed on my first sweep purely because the
tools were missing. `testrun/provision.sh` now fixes this in one command, and must run at the start
of every session.

---

## Gate status

| Gate | What it is | Result today |
|---|---|---|
| **G1 — L0 static** | syntax, JSON, index, manifest | **PASS with one exception.** 500 files 0 syntax errors · 121 packs parse, 0 broken, no duplicate keys · index ↔ disk consistent · 123/132 manifest hashes match · 9 unverifiable (finding 3) |
| **G2 — L1 probes** | the whole existing suite | **98 green / 0 red / 43 unusable.** Marked, not passed. |
| **G3 — L2 fact audit** | is the history *true* | **not started.** Needs the 500-fact draw + source checks. |
| **G4 — L3 invariants** | all places/years, not 15 spots | **not started.** |
| **G5 — L4 compile + headless server** | the whole mod, 212 commands | **blocked.** Needs ~4 GB RAM and network for Gradle; then the 24 game probes become judgeable. |
| **G6 — L5 real game** | `FINAL_TEST.md`, 55 tests | **blocked.** Needs your jar, your world, a client. |
| **G7 — L6 performance** | tick ms, heap, ceilings | **blocked** behind G6. |

---

## Verdict in simple words

**The mod is not broken. The exam is.**

Of 141 tests, 98 run today and every one of them passes — including the newest and hardest,
`/ee here` at 391 checks, and the calendars at 106. The data is intact and parses cleanly. Nothing
I ran produced a failing assertion. That is better than the 98%-done chart suggested, because for
the first time it is *measured* rather than claimed.

But the exam around those 98 is holed in four places, and every hole is in a place that matters:

- **8 tests do not compile**, including the one that runs your own `/ee check all`.
- **24 tests cannot run without the game**, and they are the command and screen tests — the ones that
  would catch a build error before you do.
- **7 "tests" prove nothing** and were being counted as if they did.
- **The suite changes the data it is checking**, and the manifest cannot tell you afterwards.

And the two questions you actually care about are still unanswered, because nothing in the 98 asks
them: **is the history true**, and **does it show up when you play**. Those are G3 and G5–G6, and I
cannot close them alone — G3 I can start now, G5 needs RAM and network, G6 needs your world.

**One line: you have a working engine, a holey exam, and no marks until today. Now you have marks —
98 green out of 141, with the 43 failures named.**

---

## What I do next, in order

1. **Repair the 8 rotten probes** *(small, mechanical — switch each to `-sourcepath`, as `probe_here.sh` already does)*, then re-run: the suite goes from 98 to ~106 judgeable.
2. **Split tests from builders** in the 7 inert scripts so exit 0 stops meaning "green".
3. **Fix the manifest** to hash content, not bytes — then it can actually guard the data.
4. **Start G3**, the fact audit: 500 rows drawn across all packs and eras, each checked against its cited source.
5. **Take G5** as soon as you give me the word on RAM/network — that is where the 24 blocked probes become marks.
