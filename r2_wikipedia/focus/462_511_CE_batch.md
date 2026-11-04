# 462–511 CE — preliminary R2 research and gameplay-data pass

**Status: partial, not 50 completed years.** Fifty annual titles and pinned raw revisions were archived; raw wikitext does not expand transclusions. A starting-year scan found **330 indexed records, including 31 hazards**. Events that started earlier and overlapped this interval were excluded. Only selected records and linked articles were reviewed; much remains unchecked.

## Indexed gameplay changes

- Applied **19 updates and one addition** across five indexed packs. The new 485 equal-field-system event uses Pingcheng as a capital reference, not a proven decree location or representation of the policy's full geographic reach.
- Corrected a Battle of the Utus row misdated 477 to a **447 duplicate note**; the existing 447 military marker remains. The year-page Battle of Orléans had been located in Italy and duplicated the 463 city-area event; it is now a note at an approximate Orléans reference. Two duplicate Vouillé military entries were made notes while the dedicated 507 battle remains active.
- Corrected the end of the 490–493 siege of Ravenna to include 493 for the history gazetteer's exclusive-end convention. The news index handles some pack end dates differently, so an extra displayed year remains possible and this is not a daily siege model.
- Removed the unsupported claim that Tikal was founded in 500 CE; its monumental architecture dates back centuries BCE. Qualified Badon's unknown date and place, Tolbiac's disputed date, Budhagupta's supposed 480 victory, Clovis's disputed baptism date, and Xiaowen's supposed cause and place of death. Moved the Northern Wei capital-change marker to a Luoyang reference and the Edessa school closure from an 800 km Cyprus-centered effect to an Edessa reference note.
- NOAA flags its 477 Constantinople earthquake entry as a duplicate. The existing earthquake row now uses **478 as an approximate placement**, with 477/478 disagreement retained in its evidence. NOAA's separately indexed possible sea wave remains; its date, effects and precise footprint are not established by this change. Corrected the 502 and 510 Korean earthquake names: NOAA's death-order category is **not** an exact count of three people. Their earthquake effects remain pending further review.
- Moved **15 hazards to non-damaging indexed notes**, preserving IDs and sources: 14 GVP eruptions with uncertain dates and one broadly dated Harra of Arhab eruption. Confirmed geological evidence is not the same as an exact calendar year or uniform 40 km damaging footprint. Of 16 hazards not moved, three were qualified in place; the others were not comprehensively reviewed.

## People and relationships

`history/sources/wikipedia_462_511_ce_people_links.json` contains **54 research leads, 33 relationships and 44 event roles across 14 indexed event IDs**. The selected links include Northern Wei rulers and Empress Dowager Feng, Palenque rulers, Baekje and Goguryeo figures, Vahan Mamikonian and associated rebels, the Edessa school, Anastasian War commanders, and Frankish and Italian rulers. Roles can span several phases and do not establish physical co-presence. These records are **not spawnable VIPs**, complete biographies or an alternate-timeline implementation.

## Evidence and files

- Year-title results: `year_titles_462_511_CE.json`; pinned raw revisions: `year_wikitext_462_511_CE.json.gz`; indexed starting-record inventory: `indexed_start_scan_462_511_CE.txt.gz`.
- Reversible manifests: `reviews/462_511_ce_context_2026-10.json.gz` (canonical SHA-256 `f2d6ad73f0b0243308b8b7ca300d91bc5ca775c232611eee85c6b459194e146d`) and `reviews/462_511_ce_hazards_2026-10.json` (canonical SHA-256 `5826be289274108ce3cd6a1ff6ccdf4c6268f03eb8fb71e420d1618455d6b4de`). They contain pinned Wikipedia revisions and source-specific evidence.
- Examples: [Battle of the Utus](https://en.wikipedia.org/wiki/Battle_of_the_Utus), [Tikal](https://en.wikipedia.org/wiki/Tikal), [Equal-field system](https://en.wikipedia.org/wiki/Equal-field_system), [NOAA earthquake 119](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/119), [NOAA earthquake 5888](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/5888), [NOAA Korean earthquake 123](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/123), and [NOAA Harra of Arhab](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/volcanoes/4967). The manifest records individual Smithsonian Global Volcanism Program links.

## Verification and rollback

Both installers were staged and applied. The initial context stage correctly rejected a copied hash; the installer was corrected before applying either layer. **11 batch tests and 19 resolver/scope/pipeline tests passed**, and **67 Wikipedia revision/title pairs** matched the API. This and the preceding batch were reversed and reapplied in memory in dependency order; saved-world effects and actual disk rollback for this batch were not tested.

Reverse later dependent batches first, then run `python r2_wikipedia/apply_462_511_ce_hazards.py rollback` followed by `python r2_wikipedia/apply_462_511_ce_context.py rollback`. Writes are atomic **per pack**, not across all packs.

No live game, loader, save, full integrity check, current Java probe or jar rebuild was performed for this batch. The jar is stale; natural VIP spawning, historical VIP behavior and player-triggered branching are unimplemented.

## Overall progress

The title inventory now finds **3,500 distinct resolved chronological titles** (2,989 BCE plus 511 CE). This is title resolution, not collection or a complete count of partly worked years. The legacy **3,168 partly worked** figure remains unreconciled. **Fully collected years: 0.** Earlier periods remain incomplete; the next preliminary interval is 512–561 CE.
