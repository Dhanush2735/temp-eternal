# 512–561 CE — preliminary R2 research and gameplay-data pass

**Status: partial, not 50 completed years.** All 50 annual titles resolved to distinct annual pages, with raw pinned revisions archived; raw wikitext does not expand transclusions. A starting-year scan found **498 indexed records, including 53 hazards**. Events starting earlier and overlapping this interval were excluded. Only selected records and linked articles were reviewed; much remains unchecked.

## Indexed gameplay changes

- Applied **20 guarded updates and one addition** across six indexed packs. Added a political marker for the 532 Nika revolt, with the Hippodrome as a city reference; its complete footprint and casualty count are not asserted.
- The Justinianic outbreak and the first plague pandemic were previously overlapping independent Constantinople-centered disruption circles. Both umbrella rows are now context notes; the existing Pelusium 541 and Constantinople 542 local disruption markers remain. The pandemic continued in waves beyond the initial outbreak, and the 541 note is **not** its end. Neither local marker models all affected regions or years. Removed an unsupported precise mortality claim from the Constantinople entry.
- The 536 climatic anomaly is represented as context rather than an exact local damaging eruption of Krakatau or a worldwide disruption centered on France. The volcanic source and regional effects remain uncertain.
- Corrected the Vandalic War and Rome/Ravenna sieges to include their documented final calendar years under the history gazetteer's exclusive-end convention. NewsIndex handles some pack boundaries differently and may display an extra year. The Lazic War row now includes the 562 treaty but is a context note: a constant 300 km military circle does not represent its shifting fronts. Individual military events remain.
- Corrected Baekje policy and capital references, moved Elephanta Caves to the island near Mumbai, and moved the Naranjo ruler entry from Calakmul to Naranjo. Qualified the Sondani battle's competing dates, the decline of the Gupta empire, and the Bagradas clash's location and effect. The former Sicily point for Bagradas is replaced by a Carthage-area **regional reference**, not a claimed exact site.
- Qualified the 512 Yingxian earthquake: NOAA's heading says Shaanxi while its account says Shanxi, and flags its location, magnitude and effects for checking. The reported 5,130 deaths are an estimate, not a verified precise total. The 551 Beirut earthquake marker remains; its chronology, source and casualties are uncertain.
- Moved **24 hazard rows to indexed non-damaging notes**, preserving IDs: 18 individually checked GVP volcanic episodes with uncertain dates and six disputed or mislocated sea-wave reports. NOAA's 551 Levant wave has coordinates in the Sea of Marmara despite an account of Byblos, Beirut and Tripoli; the note uses Beirut only as a reference. The Kos 554/558 account is not asserted to be a duplicate. Of the 53 scanned hazards, 29 were not moved; one of those was qualified in place, and many remain unreviewed.

## People and relationships

`history/sources/wikipedia_512_561_ce_people_links.json` contains **57 research leads, 35 relationships and 44 event roles across 15 indexed IDs**. These include imperial and military figures, Baekje and Silla rulers, Northern Wei figures, Yashodharman and Mihirakula, Palenque and Calakmul rulers, and Aksumite/Arabian figures. Roles may span different phases and do not establish co-presence. These records are **not spawnable VIPs**, complete biographies or an alternate-timeline implementation. Some event associations are leads explicitly requiring further verification.

## Evidence and files

- Year results: `year_titles_512_561_CE.json`; raw revisions: `year_wikitext_512_561_CE.json.gz`; indexed starting-record inventory: `indexed_start_scan_512_561_CE.txt.gz`.
- Reversible manifests: `reviews/512_561_ce_context_2026-10.json.gz` (canonical SHA-256 `014201321eb0da45caf10326949414929357774644b1549c0676b9a1615d0f90`) and `reviews/512_561_ce_hazards_2026-10.json` (`37124014600c1944089f37d79466b685511fb1e782f7bc912855f7c9afa381c4`).
- Examples: [Plague of Justinian](https://en.wikipedia.org/wiki/Plague_of_Justinian), [First plague pandemic](https://en.wikipedia.org/wiki/First_plague_pandemic), [volcanic winter of 536](https://en.wikipedia.org/wiki/Volcanic_winter_of_536), [Seong of Baekje](https://en.wikipedia.org/wiki/Seong_of_Baekje), [Naranjo](https://en.wikipedia.org/wiki/Naranjo), [Elephanta Caves](https://en.wikipedia.org/wiki/Elephanta_Caves), [NOAA earthquake 125](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/125), [NOAA Levant wave 47](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events/47), and [GVP Harunasan](https://volcano.si.edu/volcano.cfm?vn=283122). The manifests contain individual pinned Wikipedia revisions and source-specific links.

## Verification and remaining work

The first hazard stage correctly refused inherited validation rules; those were adjusted for this manifest before either layer was applied. After applying, the Naranjo point was checked against its linked article; both layers were actually rolled back in hazard-then-context order, the coordinate corrected, and both staged and applied again. **11 batch tests and 19 resolver/scope/pipeline tests passed**, including dependency-ordered in-memory reversal/reapply of this and the preceding batch. **72 Wikipedia revision/title pairs** matched the API. Saved-world effects were not tested.

Reverse any later dependent batches first, then `python r2_wikipedia/apply_512_561_ce_hazards.py rollback` followed by `python r2_wikipedia/apply_512_561_ce_context.py rollback`. Writes are atomic **per pack**, not across all packs.

Examples requiring further review include the 543 Edessa siege row located in central Iran, a 540 Milan/Ravenna claim, the independently catalogued 553 Beirut earthquake, other 512–561 hazards and earlier-starting overlaps. These are not corrected merely by this batch. No live game, loader, save, full integrity check, current Java probe or jar rebuild was performed. The jar is stale; natural VIP spawning, historical VIP behavior and player-triggered branching remain unimplemented.

## Overall progress

The title inventory finds **3,550 distinct resolved chronological titles** (2,989 BCE and 561 CE). This measures title resolution, not collected history or a complete count of partly worked years. The legacy **3,168 partly worked** figure remains unreconciled. **Fully collected years: 0.** Earlier periods remain incomplete; the next preliminary interval is 562–611 CE.
