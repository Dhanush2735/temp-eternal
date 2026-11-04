# R2 faster collection: 1944–1953

3 November 2026. At the user's request, a faster batch workflow was used for ten **consecutive** years. This is an acceleration of collection and triage, **not ten completed years**.

## What was collected

One MediaWiki batch resolved and archived the pinned English Wikipedia year revisions for every year **1944 through 1953**, with page/revision identity checks. A single scan inventoried **3,583 existing indexed event starts**, including **900 hazard starts**. Older events still active in the range are excluded. The archived raw wikitext does not expand transclusions and does not mean linked articles have all been followed.

| Year | Existing starts | Hazard starts |
|---|---:|---:|
| 1944 | 692 | 83 |
| 1945 | 576 | 58 |
| 1946 | 270 | 77 |
| 1947 | 276 | 65 |
| 1948 | 325 | 81 |
| 1949 | 289 | 91 |
| 1950 | 341 | 114 |
| 1951 | 269 | 114 |
| 1952 | 270 | 107 |
| 1953 | 275 | 110 |

`fast_year_triage.py` automates batch collection, revision verification, one-pass inventory, link-candidate counts and review flags. It flags seven records at a few known coarse placeholder coordinates and 59 groups with identical normalized names in the same year. **These are suggestions, not verified errors or duplicates**; it never automatically changes gameplay data. Its approximate link extraction includes references, birthdays and navigation and may miss transcluded links; the links are **not claimed to have been followed**. Existing files are checked and not overwritten, and an incomplete title/revision pair is refused. Review candidates can be inspected in `focus/fast_triage_1944_1953_CE.json.xz`; `python r2_wikipedia/fast_year_triage.py 1944 1953 --titles 1944` prints approximate linked titles for one year.

## Reviewed 1944 improvements

Three existing gameplay records in `events_wikipedia.json.gz` were updated after checking linked articles, retaining their stable IDs, year durations and effects:

- `wpy_c8284a8b77`: the [Balvano train disaster](https://en.wikipedia.org/wiki/Balvano_train_disaster) moved from Rome to a [Balvano](https://en.wikipedia.org/wiki/Balvano) town proxy, **not** the exact railway tunnel. The disaster article has a citation warning.
- `wpy_3a12af179e`: the arrest of [Anne Frank](https://en.wikipedia.org/wiki/Anne_Frank), her family and others moved to the [Anne Frank House](https://en.wikipedia.org/wiki/Anne_Frank_House) proxy. The old entry stated that an informer caused their discovery as fact; the corrected summary says the cause is **uncertain**, consistent with multiple theories discussed in the biography.
- `wpy_fdf5c4adce`: the arrival of captured Allied airmen, including [Phil Lamason](https://en.wikipedia.org/wiki/Phil_Lamason), moved from Berlin to a [Buchenwald](https://en.wikipedia.org/wiki/Buchenwald_concentration_camp) camp proxy.

Radii remain gameplay approximations. Relocating a record changes where its existing effects can apply. A full duplicate review is still needed. For example, two 1944 Chicago aviation conference/convention entries may overlap, and the record saying ICAO was created in 1944 conflicts with the [ICAO article](https://en.wikipedia.org/wiki/International_Civil_Aviation_Organization)'s 1947 formation date; neither was altered in this pass.

The reversible before/after manifest `reviews/1944_ce_context_2026-11.json.gz` has canonical SHA-256 `80016724c45ccf225873c6c9184e7bd793b9ca2de800712e92cbf682881d7763`. Actual apply, rollback, reapply reproduced compressed hashes of all **26 indexed packs**; one pack changed. Installation is atomic per pack, not across packs. **21 selected tests passed**, including batching, no-overwrite, archive and recent-batch checks. No live-game or saved-world test was performed.

`history/sources/wikipedia_1944_ce_people_links.json.gz` records **nine research leads, seven relationships and nine event roles**, including Anne, Otto, Edith and Margot Frank, their helpers, and Phil Lamason. Fourteen Wikipedia title/revision identities were verified. The graph is research-only: people are **not spawnable VIPs**, and associations do not provide NPC schedules or behavior.

## Storage and remaining work

To make the ten-year batch possible within the workspace guard, the historical `worldfill/README.md` was losslessly archived as `worldfill/README.original.md.xz`. A small README now points to the preserved original; read it with `python worldfill/archived_history_reports.py README.original.md --print`, or restore an exact verified copy to `README.original.md` using `--restore` when space permits. The original 545,083 bytes were verified against the archive before replacement. No active game data was removed for this storage change.

Only 1944 received the limited linked-source corrections listed above. The other nine years in the batch have year revisions and inventories, but are **not fully reviewed**, and their possible flags need investigation. Natural VIP spawning and alternate-timeline behavior remain unfinished. **Fully collected years: 0.** The title audit recognizes 4,942 annual titles in its two counted sets; title recognition is not complete collection. Available storage remains tight, so another batch may need further safe storage work.
