# Harvester v2: what was fixed, and the rebuilt Wikipedia pack

*2026-10-11. Step 1 of the plan in `survey/OTHER_SOURCES_CENSUS.md`. The census
(`survey/WIKIPEDIA_CENSUS.md` §7) found these bugs; this note covers the fixes and the rebuilt pack.
The v1 files are frozen in `survey/census/pipeline_v1/`, so the census numbers stay reproducible.*

## The fixes

| # | Bug (census §) | Fix | File |
|---|---|---|---|
| 1 | For AD years the harvester fetched the bare number. `500`, `999` and `1000` are disambiguation pages, `1`–`10` and `100` are articles about numbers (§7.1) | Years are looked up as `N (year)`, `AD N`, then `N`. A page only counts if it is not a disambiguation page and its `{{Year nav}}` names that year. A real year article beats a stale decade redirect (`386 (year)` → `380s`). The BC decade fallback now uses the real decade (`750s BC` for 753 BC, not `700s BC`) | `harvester.py` |
| 2 | Year signs were mixed: a stated "N BC" was stored as −N, everything else as +N for BC, and `postprocess.py` negated all of them. Stated BC years turned into AD years and were then "repaired" or dropped (§7.2) | One convention in the raw output: positive = BC, negative = AD | `harvest_run.py` |
| 3 | The year-0 hole: `page_year('0s BC')` returned 0, and the repair ran after the year-0 guard (§5) | BC decade pages repair to their midpoint (`0s BC` → 5 BC, `750s BC` → 755 BC). A second guard runs after the repair. Nothing dated after 2026 is kept | `postprocess.py` |
| 4 | Births and deaths leaked into events: 1,818 of 23,202 (§7.3) | Bullets under level-2 *Births*, *Deaths*, *Significant people*, *References*, *Nobel Prizes*, *In fiction*, *Predicted and scheduled events* and similar sections are skipped | `harvester.py` |

New in v2:

- **Offline rebuild.** `harvest_run.py --snapshot` replays the harvest from the frozen census snapshot
  (3,010 pages with revision IDs). It geocodes from the census caches only, with no network calls.
- **Overview pages.** `--overview` also reads the 292 decade, century and millennium pages that no
  year maps to. It keeps a bullet only if no year page has a counterpart (same wording, or the same
  place in an overlapping period). Undated bullets that fall outside 3000 BC to AD 2026 are dropped.
- **No double pins.** `install_pack.py` leaves out events the mod already has, keeping the existing
  pin. It treats two events as the same when:
  - the pin's name is contained in the bullet text, within 60 km and ±1 year; or
  - both are disasters at the same spot; or
  - both are battles at the same spot and share a word.
  Every pair it left out is listed in `install_report.json.gz`.
- `verify.sh` uses the pinned JDK 17 from `libs/get_jdk17.sh` in `~/.cache/jdk17`, so it no longer
  downloads into the saved workspace.

## Checks

- **Same pages as the census.** The fixed harvester sends all 5,026 years (3000 BC to AD 2026) to
  exactly the pages the census found, with 0 mismatches.
- **Same records as an independent replay.** The year-page output (24,078 raw records) is identical,
  in content and order, to the census's verified replay with the sign fix and the section filter
  applied.
- **Frozen v1 copies still reproduce the census.** Re-running `pipeline_bug_impact.py` produced a
  byte-identical result (23,202 / 23,259).
- **Loads in the mod.** The installed pack loads through the mod's real `HistoryGazetteer` (JDK 17,
  `verify.sh`): pack `wikipedia_year_pages`, 19,368 events (40,725 events in total). The whole mod
  also compiles with the change (`worldfill/tools/gradle_compile.sh`).
- **Clean dates.** There are 0 events at year 0 and 0 with `end <= start`. Every id is unique.

## The funnel

| Step | Records |
|---|---:|
| Bullets read on the 2,707 year pages (after skipping 121,272 bullets in Births/Deaths/people/reference sections) | 60,991 |
| With a place link | 46,412 |
| Geocoded, named and not duplicated: year pages | 24,078 |
| Plus overview pages: no counterpart on any year page, inside 3000 BC to AD 2026 | 700 |
| **After `postprocess.py`** (2,653 too short or long, 130 museum notices, 3 list artefacts; 29 years repaired; 0 dated year 0) | **21,992** |
| Left out as already in the mod: 2,112 in `events_world.json`, 455 in `events_wikidata_more.json` (step 3), 56 in `events.json`, 1 in `mediterranean.json` | −2,624 |
| **Installed: `eternal/.../history/events_wikipedia.json.gz`** | **19,368** |

## By era

| Era | Old pack (6,373, never installed in this copy) | v2 built | v2 installed (before step 3) |
|---|---:|---:|---:|
| 3000–1001 BC | 182 | 279 | 279 |
| 1000–1 BC | 521 | 1,466 | 1,372 |
| AD 1–999 | 1,089 | 2,604 | 2,388 |
| 1000–1499 | 420 | 3,473 | 3,123 |
| 1500–1799 | 645 | 4,095 | 3,575 |
| 1800–2026 | 3,497 | 10,075 | 9,083 |
| Year 0 (does not exist) | 19 | 0 | 0 |
| **Total** | **6,373** | **21,992** | **19,820** |

"Old pack" is the 6,373-event pack the previous session installed, rebuilt from
`events_all_raw.jsonl`. `harvest/events_wikipedia.json` is older still: pass 1, 5,351 events.

**Stated BC years now survive.** Example: "c. 3000 BC: Stonehenge begins to be built" is in the pack,
dated −3000. v1 dropped it as "a date past AD 2100".

## What this does not change

- **The map stays empty.** A Wikipedia event lasts one year. The density probe still finds an event
  within 100 km of about 1% of random land points, with a peak of 4% in 1944. Long-lived places
  (step 2) and estimated presence (step 4) are what fill the map.
- **The harvester's place rules are unchanged.** It takes the first plausible place link in a
  bullet, so some events sit at a country's centroid or at a slightly wrong place, just as before.

## Files

**In `harvest/`:**
- `harvester.py`, `harvest_run.py`, `postprocess.py`: v2.
- `install_pack.py`: removes duplicates and installs the pack.
- `finalize.sh`: the whole flow. Use `--preview` for a dry run and `--live` to harvest from the API.
- `events_v2_raw.jsonl.gz` and `events_v2_raw.jsonl.pages.json`: the raw records and the year → page map.
- `events_wikipedia_v2.json.gz`: the 21,992 events before duplicate removal.
- `install_report.json.gz`: every left-out duplicate and the pin that was kept.

The three files above are gzipped to keep the saved workspace under its size cap; `finalize.sh` rebuilds them in about 10 seconds.

**In the mod:**
- `eternal/src/main/resources/data/eternalengine/eternal/history/events_wikipedia.json.gz`: the installed
  pack (gzipped; `HistoryGazetteer` reads `.json.gz` packs).
- `index.json`: now lists the pack after `events_world.json`.

## Update after step 3

The pack was re-installed after `events_wikidata_more.json.gz` (step 3, 6,040 Wikidata battles, sieges, treaties
and war theatres) went into the mod: 450 more bullets matched a new Wikidata pin by name and 5 more as the
same disaster or battle at the same spot, so 19,368 Wikipedia events are installed. War theatres are never
used for this matching: a bullet about one battle inside a war is not the war.

Storage note: the generated `events_v2_raw.jsonl.pages.json` map is archived as `.json.xz`. Verify or restore it with `python r2_wikipedia/archive_generated_aux.py harvest/events_v2_raw.jsonl.pages.json [--restore]`; restoration requires headroom and refuses overwrite.
