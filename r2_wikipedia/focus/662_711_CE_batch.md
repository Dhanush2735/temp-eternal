# 662–711 CE — preliminary R2 research and gameplay-data pass

**Status: partial, not 50 completed years.** Resolved and archived 50 distinct annual pages and their raw pinned revisions; raw wikitext does not expand transclusions. `711 (year)` redirects to the disambiguation page `711`, so the documented override uses the actual annual page `AD 711` instead. Scanned **487 indexed records starting in the interval, including 46 hazards**; earlier-starting overlaps were excluded. Most records and linked articles remain unreviewed.

## Indexed gameplay-data changes

Applied **10 guarded updates across four packs**:

- Kept the active Baekgang and Karbala battle records and converted duplicate year/decade records to context notes. Karbala was not Kufa; later divisions of the Muslim community cannot be reduced to one immediate event.
- Corrected the year-page battle of **al-Harra** from Baghdad to a Medina-area reference, and the mixed **Carthage/Constantinople** entry from Baghdad to a Carthage reference. Both are contextual notes alongside existing active battle records. The Carthage article needs more inline citations.
- Corrected **Wolji Pond (Anapji)** to its Gyeongju site and changed the record from political effect to cultural context.
- Corrected a 664 **Heling/Kalingga** entry: Yijing's later account reports Huining's arrival, while Yijing began his own journey in 671. The former point was in China despite referring to Java. Pekalongan is a broad north-Java proxy; the kingdom's precise capital is unknown and identifications are debated.
- Qualified the North African conquest as multi-phase, not completed across the region in the late 670s; reduced the unsupported 500 km political effect to a note. Corrected the **698 Balhae/Parhae** foundation record's broad reference from western Jilin toward the Dunhua region; it is not an exact founding site or proof of a uniform political radius.
- Moved the **705 end of Wu Zetian's reign** from a central-China proxy to Luoyang, a court reference, reducing its unsubstantiated 800 km political footprint. The traditional **674–678 siege of Constantinople** chronology is marked disputed, while retaining the existing active slot. The current exclusive-end convention omits 678 from that slot; separate 668 and 669 siege records and the chronology still need reconciliation.

**All 46 scanned hazards remain unreviewed and unchanged.** Some may be wrongly dated, duplicated or misplaced.

## People and relationships

`history/sources/wikipedia_662_711_ce_people_links.json` records **44 research leads, 26 relationships and 37 event-role associations across 13 indexed IDs**. These include people associated with Karbala and the Second Fitna, North Africa and Iberia, the Jinshin War, Baekgang, Balhae, Tang China and Palenque. Associations may span years and do not establish co-presence or complete biographies. They are **not spawnable VIPs**.

## Evidence and verification

- Title results: `year_titles_662_711_CE.json`; raw annual revisions: `year_wikitext_662_711_CE.json.gz`; starting-record scan: `indexed_start_scan_662_711_CE.txt.gz`.
- Reversible review: `reviews/662_711_ce_context_2026-10.json.gz`, canonical SHA-256 `f17fc39c159859a028ed259ad6459f63a116f256b298bc8e1eaca12814744c8b`.
- Staged and applied. **8 batch tests and 19 resolver/scope/pipeline tests passed**; the batch and previous layer also passed dependency-ordered in-memory reversal/reapplication. **59 Wikipedia revision/title pairs** matched the API. No actual disk rollback or saved-world test was performed. Writes are atomic per pack, not across packs.
- Sources include [Kalingga kingdom](https://en.wikipedia.org/wiki/Kalingga_kingdom), [Yijing](https://en.wikipedia.org/wiki/Yijing_(monk)), [Battle of Karbala](https://en.wikipedia.org/wiki/Battle_of_Karbala), [Battle of al-Harra](https://en.wikipedia.org/wiki/Battle_of_al-Harra), [Wolji Pond](https://en.wikipedia.org/wiki/Donggung_Palace_and_Wolji_Pond), [Parhae](https://en.wikipedia.org/wiki/Parhae) and [Wu Zetian](https://en.wikipedia.org/wiki/Wu_Zetian). Pinned revisions are recorded in the manifest and graph.

Reverse later dependent batches first, then `python r2_wikipedia/apply_662_711_ce_context.py rollback`.

## Storage maintenance

Losslessly gzip-compressed **33 older CE review manifests**, saving approximately 805 KB. Original-byte SHA-256 values are recorded in `reviews/ce_manifest_compression_2026-10.json`; each corresponding installer now reads its compressed manifest with its existing gzip-aware loader. Canonical hash validation succeeded for every manifest, and **443 synthetic tests across all 33 installers passed**. Batch report manifest paths were updated. No source history, active game data or rollback images were removed by compression.

## Limits and overall progress

Most of the 487 scanned rows and their linked articles remain unchecked; earlier periods are incomplete too. No live Minecraft, loader, save, full integrity or current Java test, or jar rebuild was performed. Natural VIP spawning, historical behavior and player-triggered branching are not implemented.

The inventory reports **3,700 distinct chronological titles resolved** (2,989 BCE and 711 CE); this is not collected history or a complete partial-work count. The legacy **3,168 partly worked** figure is unreconciled. **Fully collected years: 0.** Next preliminary interval: 712–761 CE.
