# Testing the whole project — the plan, and what I proved in the first hour

**Written 2026-10-22.** The question: *test the entire project, on every aspect — how would you do it?*
This is the answer, plus the evidence of the first pass actually run in this sandbox against your
two archives (`eternal/` + `terra3/` and `worldfill/` + `harvest/` + `survey/`).

---

## 1. The honest framing first

"Every aspect" of Eternal Engine is **four different test planes**, and no single technique covers
them. Conflating them is how a project reaches "98% done" with the player saying *"I don't see any
difference from the previous version"* (turn 220).

| Plane | The question it answers | What can decide it |
|---|---|---|
| **P. Data** | Is every shipped fact present, sourced, in range, marked recorded vs estimated, and licensed? | Headless scripts + JDK. **Runs here.** |
| **Q. Logic** | Given place + year + person, does the register answer correctly and consistently? | The register classes on a plain JDK with Minecraft stubbed. **Runs here** (the probes). |
| **R. Game** | Do the commands exist, parse, and change the world; do NPCs move, trade, talk; do blocks appear? | Needs Minecraft + Forge classes, a world save, and a real client. **Partly here, mostly not.** |
| **S. Performance** | Tick ms, memory, chunk/NPC ceilings, the 55 MB data load. | A real game run with the client's own fps/tick counters. **Not here.** |

A test plan that only does P and Q is what you already have (139 probes). A plan that only does R
is what `/ee test everything` is. **What is missing is an orchestrator that runs them all, states
what is red, and can be re-run after every change** — plus the two tiers nobody has executed yet:
the full Gradle compile and the 55-test real-game pass.

---

## 2. What already exists (inventory — orchestrate, don't rebuild)

| Asset | Count | Runs without Minecraft? |
|---|---|---|
| Probe scripts `worldfill/probe_*.sh` | **139** (+`probe.sh`, `syntax_gate.sh`) | 112 yes, **27 need the Forge runtime classpath** |
| Probe programs `worldfill/probes/*.java` | **150** | — |
| Python builders / tables in `worldfill/` | **205** (45 carry their own asserts) | yes |
| Python phase tests in `eternal/test_*.py` | **13** | yes |
| Static parse gate `syntax_gate.sh` | all **500** Java files | yes |
| In-game command datapack test | **871 lines** of `.mcfunction` | no |
| `/ee check all` (`HistoryChecks`, 20+ Parts) | the mod's own self-check | no |
| `/ee test everything` (`RuntimeSuite`, `PhotoRoute`) | runtime suite + camera pass | no |
| Ground truth | `worldfill/REQUIREMENTS.md` (7 requirements), `SYSTEMS_PLAN.md` (154 systems), `FINAL_TEST.md` (55 tests), `TEST_CHECKLIST.md` | — |

**The gap is not assets. It is: no runner, no pass/fail ledger, no coverage map, and two tiers never executed.**

---

## 3. The tiers (this is the "how")

Ordered cheapest-to-most-expensive; each tier gates the next.

### L0 — Static integrity *(runs here, ~20 s)*
`syntax_gate.sh` over all 500 files; JSON/`.json.gz` parse of every pack; the v2 schema against
`schemas/eternal-pack-v2.schema.json`; `index.json` ↔ files-on-disk both ways; `build_manifest.py`
byte-count and licence audit. **Catches:** a broken brace, a corrupt pack, an unlisted file, a pack
with no licence. **Cannot catch:** wrong types, wrong logic.

### L1 — Register/logic probes *(runs here, ~15–20 min serial)*
All 112 runnable probes, one at a time (2 GB RAM forbids parallel javac). Each probe already prints
`N checks, M failed`. Fix the ones that are **compile-rotten** (see §5) and re-run. **Catches:**
a register answering the wrong year, a packing change that broke a claim, wording regressions.
**Cannot catch:** anything that needs the game.

### L2 — Data truth audit *(runs here, ~30 min, needs network)*
This is the tier that has never been done systematically. For a stratified sample of **facts**
(not places): 500 rows drawn across all packs and all eras, each checked against its cited source —
Wikipedia/WHO/Cliopatria/HYDE/Seshat — for the number, the date, the name, and the recorded/estimated
mark. Every failure classified as *wrong / stale / unsourced / mis-marked*. **Catches:** the class of
defect the journal keeps finding by hand (Vesuvius missing, Lisbon 344 km off, Fasli 1358, smallpox
in Tenochtitlan). **This is the only way to test requirement 2 ("each and every history") rather
than test that the engine reads its own data.**

### L3 — Consistency & invariants *(runs here, ~10 min)*
Property tests rather than examples, across **all** places and **all** years rather than the 15 spot
places: monotonicity (a town's population doesn't jump without an event), coverage (a settled place
never reads "nobody"), no-regression (the same question twice gives the same answer), cross-register
agreement (ruler line vs border line — printed side by side, never merged, but a disagreement
outside the known list is a defect), and the estimate-marking rule: **no unmarked estimate anywhere**.

### L4 — Full compile + headless server *(needs ~4 GB RAM and network; the honest hard one)*
`./gradlew compileJava` with `GRADLE_USER_HOME` in a non-snapshotted dir, then a **headless Forge
server** on the generated world: `/ee check all`, the 871-line command datapack, every one of the
212 commands in `ee_command_list.txt` (exists / parses / does not throw), then the 27 classpath
probes. **Catches:** the entire class of defect nothing here can see — missing imports, wrong
signatures, bad packet registration, command-tree typos. The journal records **17 such errors found
by the user rebuilding**; this tier exists to end that.

### L5 — Real-game runtime *(needs your jar + your world + a client)*
`/ee test everything` + `/ee test movement` + the camera pass (31 era stops + the book), then the
**55 tests of `FINAL_TEST.md`**, judged frame by frame against the packs. Plus the four things
`PROGRESS.md` says are still open: a real second player, hours-of-play feel, and the `NEEDS_A_REAL_SCREEN`
rows. **Catches:** the only thing the player can actually see.

### L6 — Performance & scale *(needs L5, measured not felt)*
`etest_perf.txt` (fps, client ms, server ms per era stop), heap at the 55 MB data load, chunk/NPC
ceilings from `NPC_COST.md` / `CHUNK_CROWD.md`, and the year-jump / timeline-fork cost. **Catches:**
requirement 7, which today is asserted from design documents, not from a measurement.

---

## 4. What I ran in the first hour (baseline, real numbers)

| Step | Result |
|---|---|
| Rebuilt the layout the scripts expect (`/home/user/eternal`, `worldfill`, `terra3`, `libs`) | done — **symlinks break the probes' `worldfill/../eternal` paths; real directories are required** |
| Provisioned JDK 17 (Adoptium 17.0.20.1) into a snapshot-excluded dir | done, 4 s |
| `syntax_gate.sh` applied against **all 500 files** | **0 syntax errors**, 4,518 unresolved-symbol diagnostics (expected), **17 s** |
| `probe_here.sh` (step 62 part 1) | **391 checks, 0 failed**, 6.6 s |
| `probe_calendars.sh` (step 37) | **106 checks passed, 0 failed**, 6 s — and it **rebuilds `calendars.json.gz` + `beliefs.json.gz` in place** |
| `probe_buildings.sh` | exit 0, 7 s |
| `probe_check.sh` | **compile-rotten** — see §5 |
| `probe_commands.sh` | **> 300 s**, needs the Forge classpath |
| Probes needing `runtime_cp.txt` (a Gradle + Minecraft classpath that does not exist here) | **27 of 139** |

Sweep of all 139 was started and **stopped deliberately**: at ~2 GB RAM, serial javac runs make a
full sweep a 45+ minute job that saturates the box. It needs the runner below, not a shell loop.

---

## 5. What the first hour already found (this is the value of having a runner)

1. **No orchestrator exists.** 139 probes, zero ledger: nothing states which are green today.
2. **The suite has rotted.** `probe_check.sh` fails to compile — `import com.eternalengine.civilization.HistoryChecks.Line` no longer resolves, because the script compiles a **hardcoded file list from an older turn** instead of using `-sourcepath`. `probe_here.sh` (newest) uses `-sourcepath` and works. **Rule to enforce: a probe names the class under test, never its dependencies.**
3. **`probe_life.sh` and `probe_calendars.sh` failed** until the layout fix — they resolve `worldfill/../eternal`, so the workspace must be assembled as the project intends.
4. **Probes mutate the product.** `probe_calendars.sh` rewrote two shipped packs during a test run. Data checksums are now snapshotted (`testrun/data_checksums_before.txt`, 204 files) and every test run must end with a `diff` against it.
5. **27 probes are unrunnable here by design**, and they are the *command-surface* probes — exactly the ones that would catch a build error. That is the L4 gap stated in numbers.

---

## 6. How "every aspect" gets measured (the coverage map)

Percentages of steps are not coverage. Three matrices, generated by script, not by hand:

* **Systems:** 154 system ids in `SYSTEMS_PLAN.md` → which tier, which probe, which `/ee check` part, and **what assertion** proves it. Rows with no assertion are listed as *untested*, not as *done*.
* **Requirements:** the 7, each with a **behavioural** acceptance test (e.g. req. 5: intervene in a recorded event → a branch exists, the butterfly reaches a named later fact, and reverting does not delete it).
* **Code:** 500 classes × touched-by-a-test. A class used only as a dependency of another test is **not** covered; the rule is *the test must fail if the class is wrong*. Expect this to read far below 63%.

---

## 7. Order of execution and exit criteria

| Gate | Tier | Pass means | Est. |
|---|---|---|---|
| G1 | L0 | 0 syntax errors, every pack parses, manifest byte-clean, 0 unlicensed | 20 min |
| G2 | L1 | runner built; 112 probes green or explicitly quarantined with a reason | 2–3 h |
| G3 | L2 | 500-fact audit done; wrong-fact rate measured and written down | 3–4 h |
| G4 | L3 | invariants hold for all places/years, not spot places | 1 h |
| G5 | L4 | whole mod compiles; 212 commands parse on a headless server; 27 classpath probes green | needs RAM+network |
| G6 | L5 | `FINAL_TEST.md` 55/55 on your world, with screenshots | needs your jar + world |
| G7 | L6 | perf numbers recorded per era stop; ceilings compared to the cost docs | needs G6 |

**A tier is "passed" only when it can be re-run in one command and prints a ledger.** Anything
judged by eye is recorded as *seen*, never as *passed*.

---

## 8. What I need from you, and what I would do next

Needed for G5–G7: **the built jar or permission to spend the RAM on `gradlew`**, **the world save**,
and the **`screenshots/` folder** from a `/ee test everything` run. Everything else runs here.

My next three moves, in order:

1. **Build `worldfill/testall/`** — a runner with a per-probe timeout, a verdict ledger
   (`testrun/results.tsv`), an auto-repair pass for the hardcoded-file-list probes, and a final
   data-checksum diff so a probe can never silently change the product.
2. **Run G1 + the full L1 sweep** and publish the first honest red/green board of all 112 probes.
3. **Start the L2 fact audit** — the sample draw and the source-check harness — because that is the
   tier that tests *the history*, not the engine's ability to read its own files.

Say **go** and I start with 1 and 2; or tell me to jump straight to G5 (the whole-mod compile),
which is the single largest untested surface in the project.
