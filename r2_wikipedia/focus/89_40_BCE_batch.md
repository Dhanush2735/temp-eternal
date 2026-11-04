# Preliminary batch: 89–40 BCE

**Status: partly worked, not fully collected.** All 50 English Wikipedia year titles resolved without redirects or missing pages. Their revision wikitext is archived in `year_wikitext_89_40.json.gz`, with transclusions unexpanded. The five decade pages and selected linked articles were checked, not every link. The indexed scan found 427 rows starting in this interval; it excludes earlier-starting overlaps, and most rows remain individually unreviewed. Title resolution is not year completion.

## Changes to indexed gameplay resources

Sixty-five existing rows were revised using guarded before- and after-images. Forty-eight selected world battle/siege dates were moved to the years given in their linked articles, including Philippi, Pharsalus, Carrhae, Alesia, Tigranocerta, Bibracte, Fucine Lake and Firmum. Two events, Firmum and Taenum, are dated 90 BCE in their articles despite the old records beginning in 89. Exact locations, participants and combat footprints remain incompletely verified. **World-pack NewsIndex treats the end year as inclusive, while HistoryGazetteer treats it as exclusive**; some corrected rows can therefore display for an extra year.

Additional corrections:

- The Asculum battle coordinate was near Fucine Lake rather than Ascoli Piceno. It now uses the article's city reference; this is not proof of the precise battlefield. The battle is dated 89 BCE, while the related siege began earlier.
- The 86 BCE Chaeronea duplicate, the Lutetia/Agendicum duplicate and the 57–56 BCE Octodurus duplicate were retained as contextual notes rather than separate military effects. The Artaxata account places the engagement near the Arsanias River in its lead but uses Artaxata in its infobox; its reference location remains disputed, so it is contextual.
- Massilia's 49 BCE siege was corrected in the world pack; an erroneous duplicate annual entry placed in 54 BCE became context. The siege article is flagged for excessive primary sources, insufficient citations and possible prohibited AI-generated text, so its finer details need independent checking.
- Salome Alexandra's accession was moved from 67 to approximately 76 BCE. Hyrcanus II's high-priest appointment is represented as uncertain: his biography's infobox gives c. 76 while its text says 73. The 64–63 BCE Syrian and Judean interventions were separated from an unsupported assertion of immediate Judean annexation by retaining that combined entry as context.
- The Gallic Wars are dated from 58 BCE, not the earlier preparation year used by the imported summary. The Vikram Samvat epoch is not treated as proof that a historical Vikramaditya defeated the Sakas or founded the era at that moment.
- Five large continuous military-effect circles for the First, Second and Third Mithridatic Wars, Third Servile War and Gallic Wars became regional context. Individual indexed battles remain active, subject to further review. This does not imply the wars were unreal.

## Hazards

Eight existing hazards were moved from the damaging hazards pack to regional context, preserving their IDs and before-images:

- **Leonard Range:** Smithsonian GVP confirms volcanic deposits but dates the 77 BCE eruption to ±54 years using uncalibrated radiocarbon; an exact-year 40 km damaging circle is unsupported.
- **Pantikapey and Longxi:** NOAA describes historical earthquake accounts but flags epicenters, magnitude and effects for checking. The notes do not assert that the earthquakes did not happen.
- **Dyrrachium:** NOAA's earthquake and tsunami entries reference the same possible event. The account has no evidence of damage, competing dates include 58 and 57 BCE, and NOAA flags timing and effects. The two records are not independent confirmations of two damaging hazards.
- **Etna, 56 BCE:** GVP classifies the eruption as uncertain. **Etna, c. 44 BCE:** GVP classifies an eruption as confirmed, but marks the March 44 BCE date and VEI 3 with question marks; its end is unknown. The note preserves that distinction rather than claiming no eruption occurred.
- **Laizhou Bay:** NOAA assigns low validity to the 47 BCE tsunami entry, notes competing interpretations, and flags location, timing and effects; reported height and some impacts are estimates.

The previously reviewed **70 BCE Shandong earthquake remains active**; its epicenter, magnitude and effects are uncertain. No remaining hazard's gameplay footprint was validated in a live world.

## Linked people

`history/sources/wikipedia_89_40_people_links.json` contains **52 research references, 21 qualified relationships and 58 event roles across 18 indexed IDs**. It includes opposing or associated figures—not only the best-known person—for Carrhae, Alesia, Lutetia, the Servile War, Alexandria, Philippi and other events. Namesakes Castus and Oenomaus were disambiguated to the rebel biographies. Some people are leads without a linked role; a war association does not establish presence throughout it. This graph is not independently fact-certified and does not spawn VIPs.

## Validation, rollback and storage

- Context manifest canonical SHA-256 `711cc2575ebc3d52daf84b279942a54df74a1255d1c7a94466c5ddcd76348c3a`; hazards `2ced3dcbfb3fa95a96b3f423ea39a398d6a14ce527d345457d329df6a5248e45`.
- Staging preceded application. **25 tests passed** before and after hazard application. An initial context test expected the exact word “inclusive,” while one correct review note said “includes end”; the assertion was fixed before applying. The 73 after-images and six affected pack objects were logically reversed and reapplied in memory. Graph IDs and references were structurally validated, not historically certified.
- Writes are atomic **per pack**, not across packs. Reverse this batch's hazards before its context, then reverse earlier dependent shared-pack installers in dependency order. Saved-world effects and rollback were not tested.
- Recent year-title files were compacted by whitespace only with matching parsed objects and canonical hashes; the 3000 BCE research review was losslessly compressed with byte verification. Original-path restoration and limitations are in `storage_compaction_89_40.md`; the separate project-resource copy was unchanged. External readers were not exhaustively checked. Snapshot headroom remains limited.
- No live game, loader, save, full integrity check, Java probe or jar rebuild was performed. The jar remains stale. Natural VIP spawning, historical behavior and player-triggered branching are not implemented.

## Sources

Revision-pinned examples: [Battle of Carrhae](https://en.wikipedia.org/w/index.php?title=Battle_of_Carrhae&oldid=1375201063), [Asculum](https://en.wikipedia.org/w/index.php?title=Siege_of_Asculum_(90–89_BC)&oldid=1370739009), [Artaxata](https://en.wikipedia.org/w/index.php?title=Battle_of_Artaxata&oldid=1378283983), [Siege of Massilia](https://en.wikipedia.org/w/index.php?title=Siege_of_Massilia&oldid=1380572764), [Salome Alexandra](https://en.wikipedia.org/w/index.php?title=Salome_Alexandra&oldid=1379819382), [Hyrcanus II](https://en.wikipedia.org/w/index.php?title=Hyrcanus_II&oldid=1360297281), [Gallic Wars](https://en.wikipedia.org/w/index.php?title=Gallic_Wars&oldid=1381903595), [Vikram Samvat](https://en.wikipedia.org/w/index.php?title=Vikram_Samvat&oldid=1382155751). Hazard sources: [GVP Leonard Range](https://volcano.si.edu/volcano.cfm?vn=271031&vtab=Eruptions), [GVP Etna](https://volcano.si.edu/volcano.cfm?vn=211060&vtab=Eruptions), NOAA earthquake [55](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/55), [9753](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/9753), [33](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/33), and tsunami [3714](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events/3714), [22](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events/22). Individual review notes and source links are in the manifests.

**Ledger:** 3,168 years partly worked under the existing shared-endpoint convention (+45 for this five-step batch), **0 fully collected**. These are not 3,168 complete independent annual histories. Earlier periods remain incomplete; the next preliminary interval is 39–1 BCE, then the CE transition requires careful handling because the historical calendar has no year zero.
