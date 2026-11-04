# Step 6 clean-up: raw data deleted after it went into the mod

The user's plan (turn 15): put the data already in the workspace into the mod, then delete it.
Every folder below was checked against the mod first. Code, docs and files a doc links to stay.

| Folder | Files | Size | What it was | Where it is now |
|---|---:|---:|---|---|
| `harvest/` | 31 | 16.9 MB | Wikipedia year-page harvests v1/v2: raw, merged, partial and backup event files, geo caches, logs, year lists. | v2 is in the mod as events_wikipedia.json.gz (19,368 events; the other 2,624 of its 21,992 were already in the mod, see harvest/FIXES.md); v1 was replaced by v2. |
| `wiki_test/` | 24 | 14.7 MB | 2023 snapshot of 3,010 Wikipedia year, decade and century pages, plus per-year test files. | The 2,707 year pages were rebuilt from the newer 2026 dump (events_wikipedia*, births and deaths in famous_people.json.gz); 280 of the 303 decade/century pages went in this step as events_wikipedia_decades.json.gz (23 millennium-type pages have no year range) (1,763 new events; 839 already in the mod; lines with no year of their own left out). |
| `survey/` | 22 | 8.0 MB | Census and source-survey working files: raw and post-processed census events, geo caches, work files, Wikidata samples, logs. | Measurements only; their results are written in survey/*.md. The events they counted are the year-page lines and Wikidata items already in the mod. |
| `.cache/srcdata/` | 1 | 63.0 MB | Downloaded sources: UCDP GED 25.1, plague, Smithsonian volcanoes, NOAA quakes/tsunamis/volcanoes, a land mask. | UCDP -> events_ucdp.json.gz (this step); the rest -> events_hazards.json.gz (step 5). |
| `.cache/wpdump/` | 1 | 3,774.7 MB | Offline Wikipedia: wp.sqlite index (2.7 GB), dump index files, cached year pages, list pages, war and state infoboxes. | Year pages -> events_wikipedia_regional, famous_people; list pages -> events_hazards; war infoboxes -> events_wars; state infoboxes -> polity_facts.json.gz. |

Saved space freed (workspace snapshot): about 39.6 MB. Hidden cache freed (not in snapshots): 3.84 GB.

Consequence: the step-1 to step-6 builders cannot be re-run without downloading their sources again (the Wikipedia dump index takes about 11 minutes to rebuild with worldfill/wpdump.py build).

## Files deleted

- `~/.cache/srcdata` (62.99 MB)
- `~/.cache/wpdump` (3774.75 MB)
- `~/harvest/coord_cache.json` (0.00 MB)
- `~/harvest/events_all_raw.jsonl` (2.81 MB)
- `~/harvest/events_full_raw.jsonl.partial` (0.30 MB)
- `~/harvest/events_merged_raw.jsonl` (2.46 MB)
- `~/harvest/events_raw.jsonl` (2.16 MB)
- `~/harvest/events_resume_raw.jsonl.partial` (0.43 MB)
- `~/harvest/events_resume_snap_AD567.jsonl` (0.35 MB)
- `~/harvest/events_v2_raw.jsonl.gz` (2.23 MB)
- `~/harvest/events_wikipedia_installed_5878.bak.json` (2.02 MB)
- `~/harvest/events_wikipedia_merged.json` (2.02 MB)
- `~/harvest/events_wikipedia_v2.json.gz` (1.77 MB)
- `~/harvest/geo_t3.json` (0.00 MB)
- `~/harvest/geo_test.json` (0.00 MB)
- `~/harvest/geo_test2.json` (0.00 MB)
- `~/harvest/harvest.log` (0.00 MB)
- `~/harvest/harvest2.log` (0.02 MB)
- `~/harvest/harvest_full.log` (0.02 MB)
- `~/harvest/harvest_resume.log` (0.03 MB)
- `~/harvest/harvest_run.py.bak` (0.00 MB)
- `~/harvest/harvester.py.bak` (0.01 MB)
- `~/harvest/install_report.json.gz` (0.17 MB)
- `~/harvest/postprocess.py.bak2` (0.01 MB)
- `~/harvest/postprocess_v2.log` (0.00 MB)
- `~/harvest/sample.jsonl` (0.01 MB)
- `~/harvest/smoke.jsonl` (0.00 MB)
- `~/harvest/yearlist.txt` (0.00 MB)
- `~/harvest/yearlist2.txt` (0.00 MB)
- `~/harvest/yearlist_full.txt` (0.01 MB)
- `~/harvest/yearlist_resume.txt` (0.01 MB)
- `~/harvest/yearlist_resume2.txt` (0.01 MB)
- `~/harvest/years.txt` (0.00 MB)
- `~/survey/census/census_events_postprocessed.json.gz` (1.80 MB)
- `~/survey/census/census_raw_events.jsonl.gz` (2.25 MB)
- `~/survey/census/density_probe.json` (0.00 MB)
- `~/survey/census/harvest_title_audit.json` (0.00 MB)
- `~/survey/census/pipeline_bug_impact.json` (0.00 MB)
- `~/survey/census/work/measure.json` (0.40 MB)
- `~/survey/census/work/overview_audit.out` (0.00 MB)
- `~/survey/census/work/page_types.json` (0.05 MB)
- `~/survey/census/work/place_titles.json` (0.70 MB)
- `~/survey/census/work/request_stats.json` (0.00 MB)
- `~/survey/census/work/run.log` (0.00 MB)
- `~/survey/census/work/snapshot_meta.json` (0.00 MB)
- `~/survey/census/work/titles_res.json` (1.66 MB)
- `~/survey/census/work/years.json` (0.83 MB)
- `~/survey/e_q1392.json` (0.02 MB)
- `~/survey/e_q174770.json` (0.06 MB)
- `~/survey/e_q178673.json` (0.01 MB)
- `~/survey/e_q330.json` (0.03 MB)
- `~/survey/e_q3956.json` (0.02 MB)
- `~/survey/sources/wikidata_items.json.gz` (0.14 MB)
- `~/survey/wiki_results.jsonl` (0.01 MB)
- `~/survey/wiki_survey.log` (0.00 MB)
- `~/wiki_test/b_1000.json` (0.00 MB)
- `~/wiki_test/b_1500.json` (0.00 MB)
- `~/wiki_test/b_2000.json` (0.00 MB)
- `~/wiki_test/b_2500.json` (0.00 MB)
- `~/wiki_test/b_3000.json` (0.00 MB)
- `~/wiki_test/b_500.json` (0.00 MB)
- `~/wiki_test/bc_100.json` (0.01 MB)
- `~/wiki_test/bc_1000.json` (0.00 MB)
- `~/wiki_test/bc_1500.json` (0.00 MB)
- `~/wiki_test/bc_2000.json` (0.00 MB)
- `~/wiki_test/bc_2500.json` (0.00 MB)
- `~/wiki_test/bc_3000.json` (0.00 MB)
- `~/wiki_test/bc_500.json` (0.00 MB)
- `~/wiki_test/c_1000.json` (0.00 MB)
- `~/wiki_test/c_1400.json` (0.02 MB)
- `~/wiki_test/c_1687.json` (0.03 MB)
- `~/wiki_test/c_1800.json` (0.03 MB)
- `~/wiki_test/c_1900.json` (0.07 MB)
- `~/wiki_test/c_2000.json` (0.04 MB)
- `~/wiki_test/ce_1400.json` (0.02 MB)
- `~/wiki_test/ce_1687.json` (0.03 MB)
- `~/wiki_test/ce_1800.json` (0.03 MB)
- `~/wiki_test/ce_1900.json` (0.07 MB)
- `~/wiki_test/snapshot/pages.jsonl.gz` (14.33 MB)

## Second pass (files a doc named, but data rather than results)

- The v1 harvest pack `harvest/events_wikipedia.json` (5,351 events): 4,708 (88%) are in the mod, 240 are birth/death lines (now in famous_people.json.gz or left out by the v2 rules), 176 are Nobel prize lines (left out by the v2 rules); the other 227 are mostly the same events worded differently or v1 mistakes (for example "Indianapolis 500" filed under the year 500).
- Geo caches and wiki_test test outputs.
- Kept: the small result files the survey docs show (charts, CSV tables, summaries), about 0.5 MB.

- `~/harvest/events_wikipedia.json` (1.86 MB)
- `~/harvest/geo_cache.json` (0.45 MB)
- `~/survey/census/geo_cache_census.json` (1.14 MB)
- `~/survey/census/work/geo_cache_overview.json` (0.10 MB)
- `~/wiki_test/year_index.csv` (0.58 MB)
- `~/wiki_test/ce_1000.json` (0.00 MB)
- `~/wiki_test/ce_500.json` (0.01 MB)

Second pass freed 4.1 MB.
