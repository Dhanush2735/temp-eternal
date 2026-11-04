# 412–461 CE — preliminary R2 research and gameplay-data pass

**Status: partial, not 50 completed years.** Fifty annual titles and pinned raw revisions were archived; raw wikitext does not expand transclusions. A starting-year scan found 380 indexed records, including 37 hazards; events that started earlier and overlapped this interval were not included. Only selected records and linked articles were reviewed. Many events and links remain unchecked.

## Indexed gameplay changes

- **14 existing event records updated** and **one cultural note added** across five indexed packs. A source-linked note for the death of Hypatia uses Alexandria as a city reference, not a verified precise site. This note does not spawn her.
- Corrected the Battle of the Utus marker from Constantinople to an approximate Vit River area in Bulgaria; preserved the existing military effect. Moved a Sicily raid away from Poland and made it a contextual note because its details and route need review. A duplicate decade record for the 439 capture of Carthage no longer adds a political effect in Spain.
- Qualified the approximate Kumaragupta and Skandagupta succession chronologies, corrected Northern Wei succession relationships and replaced an unhelpful central-China marker with a Pingcheng court reference. Corrected the 447 Priscus embassy claim to a contextual 448/449 association without claiming an exact court site. Qualified Venice founding, Attila's withdrawal and Leo's meeting. Nedao's exact location and the outcomes of Avarayr and Carthage require historical context, not a verified circular footprint.
- **14 hazard rows were moved to indexed cultural notes**, removing them from the damaging hazard pack while retaining their stable IDs and provenance: nine uncertainly dated eruptions, three disputed/uncertain sea-wave accounts, and two problematic earthquake entries. This is not an assertion that all underlying phenomena were fictional.
- Ilopango's Tierra Blanca Joven eruption is retained as a research note: NOAA includes an older 450 ±30 estimate and a 30,000-fatality estimate; a 2020 study places it around 431 ±2, whereas a 2019 study argued for 539/540. The existing fixed 450 hazard and definite-sounding casualty count were not retained as fact.
- NOAA's 450 Constantinople earthquake record includes research suggesting a possible duplicate of the 447 event. The 447 earthquake remains indexed separately. The 425 Palestine report includes damage at Ramleh, though Ramla was founded centuries later; that inconsistency requires further source analysis and does not disprove all seismicity in 425.
- **23 scanned hazards were not moved**; many were not reviewed. Their continued presence does not mean they are verified. Approximate locations, dates, circular gameplay effects and saved-world behavior remain limitations.

## People and relationships

`history/sources/wikipedia_412_461_ce_people_links.json` contains **48 research leads, 31 relationships and 43 event roles across 13 indexed event IDs**. Examples include Hypatia, Theon, Synesius, Orestes and Cyril; the Northern Wei succession; Aetius, Attila and Theodoric; and Armenian and Sasanian figures. Roles span different phases and are not claims that everyone was physically present. These are **not spawnable VIPs**, complete biographies, or an implemented alternate-timeline system.

## Evidence and files

- Year-title resolution: `year_titles_412_461_CE.json`; pinned raw revisions: `year_wikitext_412_461_CE.json.gz`; starting-record inventory: `indexed_start_scan_412_461_CE.txt.gz`.
- Reversible before/after manifests: `reviews/412_461_ce_context_2026-10.json.gz` (canonical SHA-256 `89cfb747893fb9fb678ab4feaafeff6df944439489c2b1f59b8e05967d1859f86`) and `reviews/412_461_ce_hazards_2026-10.json` (canonical SHA-256 `1e86e131d2ca7865d80128d085687832e069cae5af68c927d2b9db0aee1dc140`). The manifests contain pinned Wikipedia revisions and further source-specific URLs.
- Selected independent references: [NOAA earthquake 9972](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/9972), [NOAA Ilopango record](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/volcanoes/3665), [NASA on the 2020 Ilopango study](https://earthobservatory.nasa.gov/images/151948/san-salvador-a-city-among-volcanoes), and [the 2019 radiocarbon study](https://www.colorado.edu/anthropology/sites/default/files/attached-files/ilopango_tbj_qsr_acceptedversion.pdf). Other volcano-specific Smithsonian GVP links are in the hazard manifest.

## Verification and rollback

Both installers were staged and applied. Eleven batch tests and 19 resolver/scope/pipeline tests passed; 58 Wikipedia revision/title pairs were checked against the API. Batch and preceding-batch dependency-aware reversals were checked in memory. During preparation, both new layers were actually rolled back and reapplied to correct an unsupported Nedao date statement; the final manifests and hashes above are the applied versions.

Reverse later dependent batches first, then run `python r2_wikipedia/apply_412_461_ce_hazards.py rollback` followed by `python r2_wikipedia/apply_412_461_ce_context.py rollback`. Writes are atomic **per pack**, not across all packs; save-game effects have not been tested.

No live game, loader, save, full integrity check, current Java probe, or jar rebuild was performed for this batch. The distributed jar is stale; natural VIP spawning, historical VIP behavior and player-driven branching are still unimplemented.

## Overall progress

The title inventory now finds **3,450 distinct resolved chronological titles** (2,989 BCE plus 461 CE). This measures title resolution, not collection or even a complete count of partly worked years. The legacy **3,168 partly worked** figure remains unreconciled. **Fully collected years: 0.** All earlier periods remain incomplete; the next preliminary chronological interval is 462–511 CE.
