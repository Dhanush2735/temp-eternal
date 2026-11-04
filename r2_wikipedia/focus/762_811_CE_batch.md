# 762–811 CE — preliminary R2 research and gameplay-data pass

**Status: 50 years partly processed, not completed.** Archived 50 distinct annual pages and their pinned raw revisions, without expanding transclusions. Scanned **411 indexed records starting in the interval, including 52 hazards**; events that began earlier but overlap the interval were excluded. Most records and linked articles remain unreviewed.

## Indexed gameplay-data changes

Staged and applied **23 guarded updates across six packs**, plus **four hazard-to-note moves**:

- Corrected the 776–777 siege of **Ancyra** from western Anatolia to an Ankara city reference, and the 763 Tibetan occupation of **Chang’an** from Lhasa to a Chang’an reference. The city points do not establish exact activity sites.
- Extended the exclusive gazetteer ends for the sieges of **Pavia** and **Barcelona** to include their respective final years, 774 and 801. NewsIndex uses a different boundary convention and requires separate testing.
- Corrected the broad **Saxon Wars** series to the source's 772–804 span and treated it as context rather than a single continuously active military zone. The 762–763 Alid revolt likewise spans separate fronts and is not one 20 km battle; the separate Bakhamra battle remains indexed.
- Converted the legendary **Brávellir** narrative to a qualified note rather than a certain battle in 800. Corrected Otford's duplicate year-page record to Kent, noting that its outcome is inferred rather than recorded.
- Corrected the 778 Frankish Iberian campaign: Barcelona's conquest is associated with the 800–801 siege, not that campaign. Corrected Schäftlarn Abbey, the Lateran council and the 802 Byzantine succession references. Qualified Baghdad's population ranking and shifted an incorrectly Baltic British-Isles reference to Lindisfarne as an example, not the extent of all Norse activity.
- Reclassified **Kalasan** and **Sewu** temple records from political treaties to cultural notes. Qualified the date of the Leshan Giant Buddha, where the linked article gives conflicting start dates and a different completion year from the indexed record. Qualified the conventional 802 date for Jayavarman II and used Mahendraparvata as a site reference, not a proven ritual point.
- Qualified the Gyeongju earthquake: Wikipedia dates it to **779** while NOAA lists a similar report in **780**; magnitude and epicentre estimates also differ. The existing 779 disruption remains an approximation.
- Moved three uncertain tsunami/flood reports and the disputed 793 Verona earthquake report out of the damaging hazard pack into indexed notes. NOAA's `deathsAmountOrder=3` is a category, not a report of three deaths. The separate 803 Mopsuestia earthquake remains indexed; a flood is not automatically a tsunami. The remaining **48 scanned hazards were not moved and are largely unreviewed**.

## People and relationships

`history/sources/wikipedia_762_811_ce_people_links.json` records **50 people, 30 relationships and 37 event-role associations across 15 indexed event IDs**. These selected research leads include people connected to Frankish, Alid, Tang, Tibetan, Japanese, Khmer and Byzantine events. They do not establish complete biographies or co-presence and are **not spawnable VIPs**.

## Evidence and verification

- Resolution: `year_titles_762_811_CE.json`; raw annual revisions: `year_wikitext_762_811_CE.json.gz`; scan: `indexed_start_scan_762_811_CE.txt.gz`.
- Context manifest `reviews/762_811_ce_context_2026-10.json.gz`, canonical SHA-256 `df9df71863bd9b2916af9859e929b99351b191d47d56393a931ff2375da3cddf`; hazard manifest `reviews/762_811_ce_hazards_2026-10.json`, canonical SHA-256 `d99d1771dfe27098ba3f520e0741a3abe3cd78f63a176961c6962d2201b2808b`.
- **11 batch tests and 19 resolver/scope/pipeline tests passed**, including dependency-ordered in-memory reversal and reapplication of this and the preceding batch. **74 Wikipedia revision/title pairs** matched the API. This batch was not rolled back on disk, and saved-world rollback was not tested. Writes are atomic per pack, not across packs.
- Sources include [Saxon Wars](https://en.wikipedia.org/wiki/Saxon_Wars), [Siege of Pavia](https://en.wikipedia.org/wiki/Siege_of_Pavia_(773%E2%80%93774)), [Siege of Barcelona](https://en.wikipedia.org/wiki/Siege_of_Barcelona_(801)), [Trisong Detsen](https://en.wikipedia.org/wiki/Trisong_Detsen), [Kalasan](https://en.wikipedia.org/wiki/Kalasan), [Sewu](https://en.wikipedia.org/wiki/Sewu), [Jayavarman II](https://en.wikipedia.org/wiki/Jayavarman_II), [NOAA earthquake 192](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/192) and [NOAA tsunami 64](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events/64). Pinned article revisions are recorded in the manifests and graph.

To roll back, reverse any later dependent layers first, then run `python r2_wikipedia/apply_762_811_ce_hazards.py rollback`, followed by `python r2_wikipedia/apply_762_811_ce_context.py rollback`.

## Limits and overall progress

No live Minecraft, loader, saved-world, full integrity or current Java test, or jar rebuild was performed. Natural VIP spawning, historical behavior and player-triggered branching remain unimplemented. Earlier years also remain incomplete.

The inventory reports **3,800 distinct chronological year titles resolved** (2,989 BCE and 811 CE). This is not a count of collected histories or individually reviewed years. The legacy **3,168 partly worked** figure is unreconciled; **fully collected years: 0**. Next preliminary interval: 812–861 CE. Snapshot capacity remains close to its best-effort limit.
