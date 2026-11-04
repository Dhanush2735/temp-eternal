# The era route: procedure and algorithm

_How to test R1–R31 so that the answer is evidence rather than opinion. Written 2026-10-24, after the
world stalled jumping R5 → R6. Two people run it: **you** (eyes, mouse, screenshots) and **me** (the
tables, the scoring, the fixes). The route is 31 stops; each stop costs about three minutes plus
however long its ground takes to be built the first time._

---

## 0. The rule this procedure exists for

A stop **passes** only if the world answers with the right civilization, the right money, the right
people and no future technology — and it looks like the place and year it claims. A stop **fails** if
it names something that could not have been there. A stop that could not be looked at is
**cannot judge** — never a pass. Nothing in this document may be filled in from expectation.

---

## Phase 0 — one-time setup (do once, 10 minutes)

| # | step | why |
|---|---|---|
| 0.1 | install `eternalengine-1.0.0.jar`, sha256 `eba0c1debe3af6a92b78f42c962f024ce3cc39003b1e4f78df825df5f0c16b58` | the build that carries the board-17 fixes |
| 0.2 | **copy the world folder** (`saves/New World`) somewhere safe | a route run is destructive-ish: it generates a lot of new land |
| 0.3 | in `server.properties`: `enable-rcon=true`, `rcon.port=25575`, `rcon.password=<something>`, `broadcast-rcon-to-ops=true` | lets the driver script type for you |
| 0.4 | give yourself operator (`op <you>`) | `/tpll` and `forceload` need level 2 |
| 0.5 | set view distance to **8** for the route, not 12 | halves the chunks that must exist before the screen fills that is the difference between a stall and a minute's wait |
| 0.6 | open the server log in a second window (`logs/latest.log`) | it is the only witness that can tell "slow" from "stuck" |

---

## Phase 1 — pre-flight gate (5 minutes; if any line fails, **stop**, do not walk the route)

Run these in the world you are about to test, at any year:

```
/ee check all
/ee data paths
/ee civ active
/ee probe
/ee year
```

| gate | must say | if not |
|---|---|---|
| `/ee check all` | `end of check: 438 passed, 0 failed, 12 known limits` (a fresh world with no people will say 437/0/12 and its people-check will say *"holds no person to ask"* — acceptable but note it) | any FAIL line: stop, send it to me |
| `/ee data paths` | the shipped data is installed (no "missing") | `/ee data install` then repeat |
| `/ee civ active` | a non-zero number of civilizations active this year | the world state did not load: stop |
| `/ee probe` | `geo: lat=… lon=…` finite, elevation a sane number | NaN at the world spawn: the projection is not answering — stop |
| `/ee year` | the year you expect | `/ee year set <year>` |

**Pre-flight is the control.** If a stop later misbehaves, you already know the harness was sound when
you started.

---

## Phase 2 — the per-stop algorithm

For each stop *k* in the route:

```
FOR each stop (id, place, lat, lon, year) in year order:

  1  SET THE CLOCK      /ee date <year> 1 1          # forward only; the route is sorted to allow it
  2  RECORD IT          note the year the game reports back
  3  JUMP               /tpll <lat> <lon>            # may drop you over unbuilt ground
  4  HOLD THE GROUND    /execute at @s run forceload add ~-96 ~-96 ~96 ~96
  5  WAIT UNTIL READY   repeat every 3 s, up to `--settle` seconds:
                            /ee scan chunk 8
                        READY when the surface histogram holds anything but air
                        (all-air surfaces = the chunk has not been built yet)
  6  RELEASE THE HOLD   /execute at @s run forceload remove ~-96 ~-96 ~96 ~96
  7  ASK THE PLACE      /ee here                      # the card: who, when, money, what happened
  8  LOOK AT IT         screenshot (see Phase 6 for naming)
  9  ASK THE PEOPLE     /ee villager nearby 64        # names, civilizations, roles
 10  JUDGE              apply Phase 5 to what you saw
 11  WRITE IT DOWN     one row: pass / fail / cannot judge + one sentence of what you saw
  12  next stop
```

Steps 1–6 and 9–11 are what `era_route_drive.py` does for you; you keep steps 7–8 (the eyes).

```
python3 era_route_drive.py --host 127.0.0.1 --port 25575 --pass <rcon-password> \
        --player <YourName> --from R5 --to R12 --pause --settle 180 --check-all
```

- `--pause` stops after each stop and waits for Enter — **this is the useful mode**: it is when you look.
- `--settle 180` gives the ground three minutes at each stop. The default 120 is enough when the two
  stops are on the same continent; raise it for the long hops (R5→R6 is 5,900 km; R7→R8 is 10,000 km).
- `--check-all` runs the full check **once at the end**, not per stop (it answers ~20 s late, and RCON
  has no "later").
- The report lands in `era_route_session.tsv`: what was asked, what came back, whether the ground was
  ready, how long it took, and two empty columns for you.

---

## Phase 3 — when the ground does not come: the decision tree

This is the branch that cost the last run. Follow it in order; do not skip to "it's broken".

```
4–6 minutes of waiting (a first-time 5,900 km jump can genuinely take this)
│
├── screen fills in → normal, go to Phase 5. Note in the TSV how long it took.
│
├── still empty, but `ee scan chunk 8` now reports surfaces like
│   {minecraft:grass_block=…} → the ground EXISTS, your client is behind.
│      → F3+A (reload chunks) or walk 16 blocks and back. Re-photograph. Continue.
│
├── still empty and `ee scan chunk 8` says surfaces={minecraft:air=…} only
│      → generation never happened. Check `logs/latest.log`:
│        • "Preparing spawn area" / "Saving chunks" moving → it is working, wait longer
│        • "Can't keep up!" → the server is fine but slow
│        • a stack trace mentioning terraplusplus → Terra++ failed for that region:
│           record the trace, mark the stop CANNOT JUDGE, tell me
│        • absolutely nothing new for 3+ minutes → mark FAIL (grounding), tell me
│
└── the game crashed or you fell into the void
       → note the stop, restart, `/execute as <you> run tp` back to a known stop, continue with the
         NEXT stop. A stop that cannot be reached is CANNOT JUDGE, not FAIL — unless the reason is the
         mod itself, and then it is FAIL with the log line.
```

**Never** re-run `/tpll` repeatedly at a stalled stop: each jump queues another generation job at the
server and makes the stall longer.

---

## Phase 4 — the answer key (what each stop should say)

The civilisation column is the *dated core* the mod's own tables give for that ground and year (blank
means the tables name no dated core there — the game answers from its own layers, so judge by who
ruled historically). The money column is computed from the shipped `money_table.json` by the stop's
own latitude, longitude and year — it is what the card should name, not a guess:

| stop | place | year | `/tpll` | dated core | money the table gives | done |
|---|---|---|---|---|---|---|
| **R1** | Ur | 2500 BC | `30.9626, 46.1031` | sumer (-3500–-1900 | silver_weighed `mesopotamia_silver` | ☐ |
| **R2** | Giza | 2500 BC | `29.9792, 31.1342` | egypt_ancient (-3100–-30 | barter `sahara_n_barter` | ☐ |
| **R3** | Mohenjo-daro | 2500 BC | `27.3294, 68.1386` | no dated core | — ask the card | ☐ |
| **R4** | Anyang | 1200 BC | `36.1267, 114.3133` | no dated core | cowrie_cn `china_cowrie` | ☐ |
| **R5** | Athens | 430 BC | `37.9838, 23.7275` | no dated core | drachma `greek_drachma` | ☐ |
| **R6** | Pataliputra | 300 BC | `25.5941, 85.1376` | maurya (-322–-185 | pana `south_asia_pana` | ☐ |
| **R7** | Rome | AD 100 | `41.9028, 12.4964` | rome (-300–476 | denarius `roman_world` | ☐ |
| **R8** | Teotihuacan | AD 500 | `19.6925, -98.8438` | no dated core | barter `americas_barter` | ☐ |
| **R9** | Chang'an | AD 750 | `34.3416, 108.9398` | no dated core | china_cash `china_cash` | ☐ |
| **R10** | Baghdad | AD 900 | `33.3152, 44.3661` | no dated core | dirham `islamic_world` | ☐ |
| **R16** | the Sahara | AD 1000 | `23.2833, 5.5333` | no dated core | dirham `islamic_world` | ☐ |
| **R11** | Greenland's Norse farms | AD 1000 | `61.1544, -45.5156` | no dated core | vadmal `iceland_vadmal` | ☐ |
| **R12** | Cahokia | AD 1100 | `38.655, -90.061` | no dated core | barter `americas_barter` | ☐ |
| **R13** | Angkor | AD 1150 | `13.4125, 103.867` | no dated core | silver_tael `kh_silver` | ☐ |
| **R14** | Great Zimbabwe | AD 1300 | `-20.2674, 30.9337` | no dated core | barter `sub_sahara_barter` | ☐ |
| **R15** | Timbuktu | AD 1350 | `16.7735, -3.0074` | no dated core | cowrie `west_africa_cowrie` | ☐ |
| **R17** | Tenochtitlan | AD 1500 | `19.4326, -99.1332` | no dated core | cacao `mesoamerica_cacao` | ☐ |
| **R18** | Cusco | AD 1500 | `-13.5319, -71.9675` | no dated core | barter `americas_barter_late` | ☐ |
| **R19** | the Amazon | AD 1500 | `-3.119, -60.0217` | no dated core | barter `americas_barter_late` | ☐ |
| **R20** | Vijayanagara | AD 1520 | `15.335, 76.46` | no dated core | hun `south_india_hun` | ☐ |
| **R21** | Delhi | AD 1650 | `28.6139, 77.209` | mughal (1526–1857 | mughal_rupee `north_india_mughal` | ☐ |
| **R22** | Edo | AD 1700 | `35.6762, 139.6503` | no dated core | mon `japan_mon` | ☐ |
| **R23** | London | AD 1700 | `51.5074, -0.1278` | no dated core | pound_lsd `britain_lsd` | ☐ |
| **R24** | Paris | AD 1789 | `48.8566, 2.3522` | no dated core | livre `france_livre` | ☐ |
| **R25** | Sydney | AD 1850 | `-33.8688, 151.2093` | no dated core | pound_lsd `australia_pound` | ☐ |
| **R31** | Siberia | AD 1900 | `62.0355, 129.6755` | no dated core | barter `north_asia_barter_late` | ☐ |
| **R26** | New York | AD 1920 | `40.7128, -74.006` | no dated core | dollar `usa_rulers` | ☐ |
| **R27** | Hyderabad | AD 1948 | `17.385, 78.4867` | india (1947–9999 | indian_rupee_anna `south_asia_rupee` | ☐ |
| **R28** | Lagos | AD 1960 | `6.5244, 3.3792` | no dated core | franc_cfa `fr_africa_cfa` | ☐ |
| **R29** | Moscow | AD 1980 | `55.7558, 37.6173` | no dated core | ruble_su61 `ussr_ruble61` | ☐ |
| **R30** | Sao Paulo | AD 2020 | `-23.5505, -46.6333` | no dated core | real_br_new `br_box_real` | ☐ |

Three of these are worth a second look when you get there — the table's geographic answer is
questionable and the card is the court of appeal:

- **R2 Giza, 2500 BC** → `barter (sahara_n_barter)`. Egypt in the Old Kingdom used weighed metal; if
  the card offers only "barter" it is worth asking whether that is intended.
- **R16 the Sahara, 1000** → `dirham`. Defensible (trans-Saharan trade), but check the card says the
  Sahara and not a city.
- **R31 Siberia, 1900** → `barter`. Check whether a fur-and-tallow trade is what the card describes.

---

## Phase 5 — how each stop is judged (the decision rule)

Look for four things, in this order. The stop's verdict is the **worst** of the four.

| # | look at | PASS | FAIL |
|---|---|---|---|
| 1 | **civilization** — the card's "who rules here", `/ee civ info` | the power that really held that ground that year (Egypt at Giza −2500, Zhou at Anyang −430, Maurya at Pataliputra −300) | a power that had not begun or had already fallen, or a modern state in an ancient year |
| 2 | **money** — the card's money line | the coin named in the answer key above (or a defensible neighbour of it) | a coin from another continent or a century out (drachma at Anyang, dollars in 1650 Delhi) |
| 3 | **people** — `/ee villager nearby 64`, names and roles | names of that culture, roles that exist then (no "banker" in 2500 BC, no "soldier" with firearms in 300 BC) | modern names, or a role that needs technology the year does not have |
| 4 | **the look** — buildings, dress, crowd, road | a market that looks like a market: mudbrick and barley at Ur, marble and togas at Rome, no glass towers, no cars, no printed signs before printing | anything from a later century, or a place that is empty where history says a city stood |

Then one line of judgement, and only one of these three words:

- **PASS** — all four hold.
- **FAIL** — anything from a later century appears, or the card names a power/coin that could not be there.
- **CANNOT JUDGE** — the ground never came, the stop was unreachable, or you could not see it. *This
  is not a soft pass* — it stays open in the scorecard until somebody looks.

Anachronism is the one thing that can never be waved through: if you see a printed sign in 300 BC, the
stop fails even if everything else is right.

---

## Phase 6 — evidence, so the verdict can be checked by someone else

Per stop, capture exactly this:

1. **one screenshot** of the card and the scene (`F2`, then find it in `screenshots/`);
2. rename it `R06_pataliputra_300bc.png` — id, place, year, no spaces;
3. paste the `/ee here` text into the TSV's `your_note` column if the card is long;
4. note the wait in `settled_s` (already filled by the script) — a stop that needed 4 minutes is a
   finding about generation cost, not a failure.

At the end of a run, send me: the `era_route_session.tsv`, the screenshots folder, and the log's
`[EE check] end of check:` line. With those I can score every stop without asking you anything else.

---

## Phase 7 — end of a run (5 minutes)

```
/ee check all                 → note `end of check: … passed, … failed, … known limits`
/ee year                      → the year you finished in (the world saves it)
save-all flush                → wait for "Saved the game"
```
Then close the world normally. Send me the TSV, the screenshots and that end-of-check line.

---

## Time budget

| work | estimate |
|---|---|
| Phase 0 + 1 (setup, pre-flight) | 15 min, once |
| a stop already built (revisiting) | ~1 min |
| a stop three continents away, first time | 3–6 min, mostly generation |
| the whole route in one sitting | 3–4 hours — or in three sittings: R1–R10, R11–R20, R21–R31 |

The route is ordered by year so a single forward run forks the world at most once (R16 and R31 sit out
of chronological order in the sheet; use `--order=year` or simply skip them and do them separately).

---

## What I do with the result

- every **PASS** closes that stop in `FINAL_TEST_SCORED.md` §3 with the screenshot as its evidence;
- every **FAIL** becomes a numbered defect with the stop, the year, the wrong answer and the log line,
  and it is fixed before the next run;
- every **CANNOT JUDGE** stays open and is listed as open — the run's verdict is not "passed" while any
  stop is open;
- when all 31 are PASS and `/ee check all` is 0 failed, the human half of the project is green and the
  remaining work is only the final real-game playthrough.
