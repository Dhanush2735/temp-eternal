# 812–861 CE — preliminary R2 research and gameplay-data pass

**Status: 50 years partly processed, not completed.** Archived 50 distinct annual pages and their pinned raw revisions, without expanding transclusions. Scanned **490 indexed records starting in the interval, including 86 hazards**; events that began earlier but overlap the interval were excluded. Most records and linked articles remain unreviewed.

## Indexed gameplay-data changes

Staged and applied **24 guarded updates across seven packs**, plus **four hazard-to-note moves**:

- Extended the exclusive gazetteer end for the sieges of **Baghdad** and **Syracuse** to include their respective final years, 813 and 828. The Syracuse article has few inline citations. NewsIndex uses a different boundary convention and requires separate testing. For Thomas the Slav’s siege of Constantinople, the end of the siege is disputed between late 822 and spring 823; the existing 821–822 gazetteer slot is retained and qualified.
- Corrected the **Sweet Dew incident** to a Chang’an court reference; the Homs revolts to Homs; Babak’s revolt to its Badd Fort region rather than Baghdad; Babak’s execution and the Amorium captives’ execution to Samarra; and the new Abbasid court’s destination to Samarra. These are site or city proxies, not proven exact locations for every action.
- Corrected **Íñigo Arista** and Pamplona’s political context, avoiding the anachronistic claim that a Caliphate of Córdoba supported the 824 event. The Ancyra battle article names both Ancyra and Çorum; its existing point is retained as approximate rather than identifying a precise battlefield.
- Corrected **Leonine Wall** entries to Vatican Hill, Rome, and identified the wall as construction over 848–852 rather than a treaty or a separate 852 political transfer. Qualified **Ghana/Wagadu**: a written reference around 830 does not establish a founding year.
- Reclassified and qualified **Borobudur**, **Prambanan**, **al-Qarawiyyin**, and Balaputra’s **Nalanda** patronage. An inscription dated to 860 refers to a monastery at Nalanda in Bihar, not Sumatra; it does not establish the precise construction year. The Prambanan inscription’s 856 date is not proof of the whole complex’s completion. Al-Qarawiyyin began as a mosque in 857–859, not an unquestioned modern university founded in 859.
- Corrected two NOAA earthquake labels that treated casualty **categories** as exact counts of three deaths. Their dates, magnitudes and locations remain estimates. Corrected the misplaced 838 **Frisian flood** to a broad Friesland reference: its retained 50 km active radius is a gameplay approximation, not the historical flood footprint. Historical sources report 2,437 victims, not a verified modern count.
- Moved a second record of the same 838 flood, a possible **842 Channel Islands tsunami**, a disputed **858 Dvin earthquake**, and a possible **859/861 Samandag wave** out of the damaging hazard pack into indexed notes. The Channel Islands earthquake remains separately indexed. Other Dvin reports were not automatically merged. **82 scanned hazards remain in the hazard pack**, including the three qualified above; most were not reviewed.

## People and relationships

`history/sources/wikipedia_812_861_ce_people_links.json` records **42 people, 25 relationships and 40 event-role associations across 16 indexed event IDs**. These selected leads cover people connected with Abbasid, Byzantine, Carolingian, Tang, Javanese, Pala and other events. Roles do not establish co-presence or complete biographies, and these profiles are **not spawnable VIPs**.

## Evidence and verification

- Resolution: `year_titles_812_861_CE.json`; raw annual revisions: `year_wikitext_812_861_CE.json.gz`; scan: `indexed_start_scan_812_861_CE.txt.gz`.
- Context manifest `reviews/812_861_ce_context_2026-10.json.gz`, canonical SHA-256 `207017163b7715a3f8a63fcdcf72e0d596f6fd8bbca08793b032241632a7081e`; hazard manifest `reviews/812_861_ce_hazards_2026-10.json`, canonical SHA-256 `0b9088600d60d8618df503f9ffeb55d96b4251989462598aa0dd1e5fd99de313`.
- **11 batch tests and 19 resolver/scope/pipeline tests passed**, including dependency-ordered in-memory reversal and reapplication of this and the preceding batch. **69 Wikipedia revision/title pairs** matched the API. An earlier version of this batch was actually rolled back on disk in hazard-then-context order and reapplied after adding two location corrections; saved-world rollback was not tested. Writes are atomic per pack, not across packs.
- Sources include [Siege of Baghdad](https://en.wikipedia.org/wiki/Siege_of_Baghdad_(812%E2%80%93813)), [Thomas the Slav](https://en.wikipedia.org/wiki/Thomas_the_Slav), [Sweet Dew incident](https://en.wikipedia.org/wiki/Sweet_Dew_incident), [Homs revolts](https://en.wikipedia.org/wiki/Homs_revolts_(854%E2%80%93855)), [Leonine City](https://en.wikipedia.org/wiki/Leonine_City), [Shivagrha inscription](https://en.wikipedia.org/wiki/Shivagrha_inscription), [Nalanda inscription](https://en.wikipedia.org/wiki/Nalanda_inscription_of_Devapaladeva), [NOAA earthquake 225](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/225), [NOAA tsunami 67](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events/67) and [NOAA tsunami 71](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events/71). Pinned Wikipedia article revisions are recorded in the context manifest and graph.

To roll back, reverse any later dependent layers first, then run `python r2_wikipedia/apply_812_861_ce_hazards.py rollback`, followed by `python r2_wikipedia/apply_812_861_ce_context.py rollback`.

## Limits and overall progress

No live Minecraft, loader, saved-world, full integrity or current Java test, or jar rebuild was performed. Natural VIP spawning, historical behavior and player-triggered branching remain unimplemented. Earlier years also remain incomplete.

The inventory reports **3,850 distinct chronological year titles resolved** (2,989 BCE and 861 CE). This is not a count of collected histories or individually reviewed years. The legacy **3,168 partly worked** figure is unreconciled; **fully collected years: 0**. Next preliminary interval: 862–911 CE. Snapshot capacity remains close to its best-effort limit.
