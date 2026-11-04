# The test procedure and algorithm

_How this project is tested, in the order it must be tested, with the exact commands, the number each
step must print, and the rule for deciding what a red line means. Written 2026-10-24. It supersedes
"run the probes and look at them": every step here produces a machine-readable ledger, and no step may
be called green without a number._

**The one rule everything else serves:** a check passes when it can be re-run by someone else, in one
command, and prints a number that matches a stated baseline. A check that cannot be run is
**cannot judge here** — written down as such, never counted as a pass.

---

## The five layers

| layer | what it proves | command | time |
|---|---|---|---|
| **L0 — the files** | the source parses, every data pack parses, every shipped file matches the manifest byte for byte, each has a licence | part of `verify_all.sh` | 1 min |
| **L1 — the probes** | 143 self-contained probes: 115 pure-data, 28 that need the Minecraft classpath. Each answers its own question about the data or the engine | `verify_all.sh --all` | ~35 min |
| **L2 — the build and the command surface** | the mod compiles; all 220 commands parse and run through Minecraft's own dispatcher; `/ee check all` runs headless | part of `verify_all.sh` | ~10 min |
| **L3 — the artifact** | the jar a player installs: builds, contains what it should, ships what the manifest says | part of `verify_all.sh --all` | 2 min |
| **L4 — a live server** | the mod on a running Forge server: `/ee check all` with a world, all 212 commands over RCON, the datapack functions, a clean stop | `verify_server.sh` (dev classpath) and `verify_prod_server.sh` (shipped jar) | 8 min each |

The gates in `FINAL_VERDICT.md` map onto them: **G1** = L0, **G2/G3/G4** = L1, **G5** = L2 + L3 + L4,
**G6** = the human half (route + `FINAL_TEST.md`), **G7** = performance, of which L4 gives the
server's half.

---

## Algorithm, in full

```
TEST_PROJECT:

  PHASE A — preflight (must pass, or nothing below means anything)
    A1  provision the toolchain        bash testrun/provision.sh
    A2  swap on                        (2 GB box; the Gradle daemon dies without it)
    A3  free memory ≥ 1.2 GB           free -m      (a -Xmx2g probe on this box is killed)
    A4  disk space for the Gradle cache and a Forge server
    A5  no other server is listening on 25575/25599 (a stale one answers RCON and ruins L4)

  PHASE B — the machine half            bash verify_all.sh --all  → testrun/ledger.tsv
    B1  L0 syntax_gate                  expect: 0 syntax errors
    B2  L0 manifest                     expect: "up to date"
    B3  L2 compileJava                  expect: BUILD SUCCESSFUL + N classes
    B4  L2 command_surface              expect: "220 commands: 220 PASS, 0 ... PARSE-FAIL, 0 THROW"
    B5  L2 ee_check_all (headless)      expect: "422 passed, 12 failed, 12 known limits"
                                              the 12 are the bare-process baseline: no world, no Terra++
    B6  L1 the 28 classpath probes      expect: each ends with its own "pass=… fail=0"
    B7  L1 the 115 other probes         expect: same
    B8  L3 jar_build / jar_check / jar_contents
                                        expect: jar exists; "JAR OK: … 0 failed"
    B9  L0 manifest_after               expect: "up to date"  (a probe that rewrites a pack makes it stale)
    TOTAL                               152 checks, 0 failed

  PHASE C — the dev server               bash verify_server.sh --keep  → testrun/server_ledger.tsv
    C1  server start                    expect: "Done (…)!" within ~7 s
    C2  /ee check all (live, with world) expect: "438 passed, 0 failed, 12 known limits"
                                              (437 if the world holds nobody — see the note below)
    C3  212 commands over RCON          expect: 212 of 212 answered
    C4  10 datapack functions            expect: "Executed … command(s)" for each
    C5  clean shutdown                   expect: "All chunks are saved"

  PHASE D — the shipped jar             bash verify_prod_server.sh → testrun/prod_server_ledger.tsv
    D1  install (jar + Terra++)          expect: files in mods/
    D2  boots                            expect: "Done (…)!"
    D3  /ee check all                    expect: 436-438 passed, 0 failed, 12 known limits
    D4  212 commands                     expect: 212; 0 empty answers
    D5  clean shutdown                   expect: "All dimensions are saved"

  PHASE E — the human half              see ERA_ROUTE_PROCEDURE.md
    E1  31 era-route stops, each: date → tpll → wait for ground → card → look → judge
    E2  the FINAL_TEST.md tests that need a body or a screen
    E3  screenshots named R06_pataliputra_300bc.png, one per stop

  PHASE F — scoring
    F1  every PASS closes a row in FINAL_TEST_SCORED.md §3 with its evidence
    F2  every FAIL becomes a numbered defect with the stop, year, wrong answer, log line
    F3  every CANNOT JUDGE stays open and is listed
    F4  the run's verdict is "passed" only when no row is open
```

---

## What each number must be (the baselines to compare against)

| check | baseline | where it comes from |
|---|---|---|
| `verify_all.sh --all` | **152 passed, 0 failed** | `testrun/raw3/sweep_all_14.log` |
| `verify_all.sh` (gates only) | **5 checks, 0 failed** | `testrun/raw3/*.log` |
| headless `/ee check all` | **422 / 12 / 12** | the 12 are the bare-process baseline: no world, no Terra++, no authored events |
| live `/ee check all` | **438 / 0 / 12** | `testrun/raw3/server.log` |
| production jar `/ee check all` | **436 / 0 / 12** | `testrun/prod_server_ledger.tsv` |
| commands (dispatcher) | **220 commands, 220 PASS** | `testrun/command_surface.tsv` |
| commands (live server) | **216, 0 empty answers** | `testrun/server_commands.tsv` |
| jar | **14 jar checks, 0 failed** | `testrun/jar_contents.tsv` |
| era-route stops | **3 of 31 walked** | open — this is what Phase E exists for |

A number **above** the baseline is not automatically good: the headless check once reported
"11 failed" while the harness recorded PASS (defect 25, board 14). The count must be equal, and a
change in either direction is read, not welcomed.

---

## Triage: what to do with a red line

Follow in order. Do not stop at "it failed", and do not close a red by explaining it.

```
a check printed FAIL
│
├─ 1. Read its log: testrun/verify/<name>.log (or testrun/raw3/server.log for L4).
│     Is the FAIL a real answer, or did the check never get to run?
│
├─ 2. Classify the cause:
│     ├─ SANDBOX      missing tool, missing /tmp download, OOM kill, no swap, port in use
│     │                → fix the environment, re-run. NOT a finding about the mod.
│     │                  Precedents: the Forge cache taking 9 minutes cold; a -Xmx2g probe on a
│     │                  2 GB box killed silently; the price data missing from /tmp.
│     ├─ HARNESS      the probe or wrapper measured the wrong thing, or judged it on the wrong line
│     │                → fix the harness, and say so in the board (defects 25, 30 and the board-17
│     │                  flaky-tally and false-failure-line bugs were all here).
│     └─ MOD          the mod answered wrongly
│                  → 3.
│
├─ 3. Reduce to a probe. A defect is not understood until one probe reproduces it in under a minute,
│     against the tables alone if possible.
│
├─ 4. Fix, then prove the fix by A/B — the before/after algorithm below. "It looks right now" is not
│     proof; the same probe must fail on the old code and pass on the new.
│
├─ 5. Re-run the affected probe, then the whole of Phase B. A fix that greens its own probe and
│     reddens another is not a fix.
│
└─ 6. Record: a numbered defect in the board, with the failing line quoted, and the A/B numbers.
```

**Flakiness protocol.** Any check that has ever disagreed with itself is run twice, in both orders,
before it is believed. The per-place timing check once read 6.2 ms (limit 5) and then 3.5 ms on the
same code; the honest reading came from measuring old and new back to back on an idle machine.
Wall-clock in a shared sandbox is not a measurement, it is a sample.

---

## The A/B algorithm (how a fix is proved here)

Used for board 17, and it is the template for every future fix:

```
A/B fix proof:

  1. Keep the OLD source of the changed class(es) in .cache/old_src/<pkg>/ (not snapshotted — rebuild
     from the diff if it is ever needed again).
  2. Compile the OLD classes into .cache/old_classes.
  3. Run the SAME probe twice:
        java -cp ".cache/old_classes:<real classpath>" TheProbe      → must FAIL the way the defect did
        java -cp "<real classpath>" TheProbe                          → must pass
     The old classes go FIRST on the classpath, so they shadow the new ones.
  4. Record both numbers side by side (board 17: Anyang `jin` → `china_zhou`; the world sweep
     7,165 wrong answers → 0; named answers 1,394 → 2,850).
  5. Register the probe in verify_all.sh so the regression is permanent:
        CLASSPATH_PROBES="… repair …"      (or put a probe_<name>.sh in worldfill/)
  6. Re-run the full sweep and diff the failing set against the known baseline; the diff must be empty.
```

**Do not skip step 3.** A fix whose "before" was never measured has no proof that it changed anything.

---

## Evidence retention (what makes the verdict checkable next month)

| artifact | what it holds |
|---|---|
| `testrun/ledger.tsv` | one row per check: tier, name, exit code, last summary line |
| `testrun/server_ledger.tsv`, `testrun/prod_server_ledger.tsv` | the same for the two live-server runs |
| `testrun/verify/<name>.log` | the full output of each check |
| `testrun/raw3/*.log` | the raw run logs, including an entire server session |
| `testrun/command_surface.tsv`, `testrun/server_commands.tsv` | every command, its verdict and its first answer |
| `JAR_SHA256.txt` | the exact jar the verdict refers to |
| `screenshots/` | the human half, one per route stop |
| `MARKING_BOARD_*.md` | the narrative: what was found, what was fixed, what is still open |

**The lesson from 2026-10-23:** a "no known defects" verdict decays if the evidence cannot be rebuilt.
`build/` and `.cache/` are not in the snapshot, so a fresh session starts with no JDK, no Gradle cache,
no unpacked price data — and the first thing that happens is a red line that is not a defect. Phase A
exists because of that.

---

## Time budget

| phase | cold | warm |
|---|---|---|
| A preflight | 10 min (JDK download) | 20 s |
| B machine half | 45 min (Forge userdev cache ~9 min + 143 probes) | 35 min |
| C dev server | 10 min | 8 min |
| D shipped jar | 20 min (Forge installer downloads ~172 MB) | 8 min |
| E human half | 3–4 h for the route | — |

Do not start Phase B expecting to finish it in one tool call; run it redirected to a log and read the
log.

---

## The rule that keeps this honest

The last two defects were found not by a probe going red but by a person looking: the Anyang crowd
that was still Shang, and the first version of the fix that left saved worlds untouched. **Every green
number in Phase B says the code does what the probes ask. Only Phase E says it is a world.** Neither
half may be reported as the whole.

---

## Quick reference

```bash
bash testrun/provision.sh                 # A — toolchain (every new session)
bash verify_all.sh --all                  # B — 152 machine checks, ~35 min, ledger at testrun/ledger.tsv
bash verify_all.sh --only repair          #    one check by name
bash verify_server.sh --keep              # C — dev server, live checks, kept running
python3 worldfill/probes/rcon.py "ee check all"   #    poke the server that is still up
bash verify_prod_server.sh                # D — the shipped jar on a production Forge server
python3 era_route_drive.py --pass <rc> --player <You> --from R5 --to R6 --pause --settle 180
                                          # E — the human half, driven for you
```

Exit codes: `verify_all.sh` returns the number of failed checks; `verify_server.sh` and
`verify_prod_server.sh` likewise, so `… && echo green` is a safe habit.
