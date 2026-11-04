# Preliminary batch: 212–261 CE

**Status: partly worked; 0 fully collected years.** This batch overlaps earlier sampled work. The legacy total of 3,168 partly worked years has not been reconciled, so adding 50 to it would be misleading.

## Collection and scope

All 50 chronological titles resolved to distinct annual pages; none was marked as a disambiguation page at retrieval. `year_titles_212_261_CE.json` records the title and pinned revision for each year; `year_wikitext_212_261_CE.json.gz` preserves their raw revisions. Transclusions are not expanded. Only selected annual content and linked articles were checked, **not every linked article**.

The archived `indexed_start_scan_212_261_CE.txt.gz` contains **288 indexed records beginning in the interval, including 40 hazards**. It excludes earlier-starting events that overlap the interval. Most candidates remain unreviewed.

The title-file inventory now finds **3,250 distinct chronological title resolutions**: 2,989 BCE and 261 CE. This is not a count of completed or individually reviewed years. Separate work on 3000–2990 BCE exists outside this title-file inventory.

## Indexed game data changes

Seventeen existing rows were updated across six indexed packs, and one political event was added:

- Added the **Constitutio Antoniniana** in 212: Caracalla extended citizenship to free inhabitants of the empire, not enslaved people; the exclusion of *dediticii* is debated. Its 20 km Rome political effect is a capital-centered gameplay proxy, **not** the extent of the law or a verified signing site.
- Corrected the claim that peace and unity were restored across China in 256. Wei, Shu and Wu remained separate; Shu fell in 263 and Wu in 280. The unsupported 256 political effect is now a note. Ma Jun's south-pointing chariot is identified with the third century, not a securely established invention in 255; a differential gear remains a possible reconstruction rather than a proven surviving mechanism.
- The 220 Han abdication row now uses Xuchang, the late Han capital, as a contextual proxy rather than the old Xi'an point; the ceremony's exact location and day are not inferred from that proxy. Two 605 km decade-derived duplicates became notes. The 229 Sun Quan row no longer asserts that Jianye was founded then or that all Cambodia and Laos became vassals.
- Corrected the 238 Battle of Carthage marker from a Numidian point to a **Carthage city reference**, with the actual nearby battlefield location unresolved. Julia Maesa's return to Emesa uses a Homs reference instead of an 800 km circle in Italy. The 230 Nisibis campaign marker was moved from central Iran to a Nisibis reference; its timing and footprint remain approximate.
- The 224 Battle of Hormozdgan's precise site is unresolved. Its Shushtar point is now a research note rather than a certain military footprint. The 217 Nisibis battle remains active; a 60 km campaign effect at the same location is now a note, with the war's start corrected to 216.
- Gordian III's death circumstances remain disputed. The old certain-murder assertion is now contextual. The 256 assertion of a definite Roman loss of Dacia is qualified: formal withdrawal came under Aurelian around 271–275, although control was under severe pressure earlier. The Valerian/Gallienus row no longer asserts that two separate empires were formally created, and the 260 Valerian capture row is a note linked to the separately indexed Edessa battle.
- The Plague of Cyprian row now records disputed dates and unknown cause. The existing 249–255 Antioch-centered disruption is retained as a limited local game proxy, **not** evidence that the epidemic ended in 255 or that its circle represents the whole epidemic. A separate Rome reference remains; duplicate and temporal effects still need a gameplay review.

## Hazards

Fifteen IDs moved from the active hazard pack to indexed, non-damaging regional notes. Fourteen are confirmed GVP eruptions whose exact nominal years are not established: Calbuco 220 ±75, Pelée 220 ±75, Taveuni 220 ±100, Sundoro 230 (?), Hekla/Vatnafjöll 250 ±2500, Krafla 250 ±300, Nasudake 250 ±200, The Quill 250 ±150, Seguam 250 ±500, Quetrupillán 255 ±48, Barú 260 ±150, Katla 260 (?), Miyakejima 260 ±500, and Taupo 260 (?). These ranges are database dating expressions, not fixed active-game years. GVP's Taupo table gives 260 (?) while a 2022 bulletin mentions around 232, underscoring the dating uncertainty.

The fifteenth is the 258 Tyrrhenian sea-wave account: NOAA calls it a **possible** tsunami, rates its validity 2, and links it to the Roman earthquake account. The earthquake remains active, but NOAA flags its epicenter, magnitude and effects for checking. The wave is no longer a second certain 60 km hazard.

**25 of the 40 scanned hazards were not moved**; many remain unreviewed and may still use unsupported nominal dates or effects. The 243, 251 and 253 earthquake entries also remain active; their NOAA records were inspected, not independently verified. GVP and NOAA entries can share source material, so they are not automatically independent confirmation.

## Connected people

`history/sources/wikipedia_212_261_ce_people_links.json` contains **36 research references, 25 qualified relationships and 35 event roles across 15 indexed event IDs**. They include figures on opposing sides at Xiaoyao Ford, Hormozdgan, Carthage, Nisibis and Edessa, alongside associated dynastic families and epidemic witnesses. A campaign association does not establish that every person was physically present at every place or phase. These are research leads, **not spawnable VIPs**, and do not implement historical behavior or branching.

## Verification, provenance and rollback

- Context manifest canonical SHA-256: `d445cdadec53d215ff25426066af632732d5b1622bd2b06010fe5579b58607a1`; hazard moves: `d9ad2a1af9add8cfda34d231d49b21f9bb2dd1b25cf03efff173dcc499f2a4d3`.
- Both migrations were staged before application. **12 batch tests passed**, including unique after-images, hash tamper rejection, archived title checks, and dependency-aware in-memory reversal/reapplication of this batch and the preceding one. **19 resolver, scope and pipeline tests passed.** All **49 distinct pinned Wikipedia revision/title pairs** in the context manifest and people graph matched the API. These are data checks, not gameplay tests.
- To reverse, roll back **212–261 hazards, then context**, before earlier shared-pack installers. Writes are atomic per pack, not across all packs. Rollback/reapplication was tested in memory; actual disk rollback and saved-world behavior were not tested for this batch.
- No live game, loader, save, full integrity check, Java probe or jar rebuild was performed; the jar is stale. Natural VIP spawning, historical VIP behavior and player-triggered branching are not implemented. Year-zero and pack-specific end-boundary semantics remain unresolved.

Selected sources: [Constitutio Antoniniana](https://en.wikipedia.org/w/index.php?title=Constitutio_Antoniniana&oldid=1378893633), [Three Kingdoms](https://en.wikipedia.org/w/index.php?title=Three_Kingdoms&oldid=1376621262), [Battle of Carthage](https://en.wikipedia.org/w/index.php?title=Battle_of_Carthage_%28238%29&oldid=1370436419), [Hormozdgan](https://en.wikipedia.org/w/index.php?title=Battle_of_Hormozdgan&oldid=1370265788), [Plague of Cyprian](https://en.wikipedia.org/w/index.php?title=Plague_of_Cyprian&oldid=1368586538), [Edessa](https://en.wikipedia.org/w/index.php?title=Battle_of_Edessa&oldid=1379471894), [GVP Taupo](https://volcano.si.edu/volcano.cfm?vn=241070), [GVP Hekla](https://volcano.si.edu/volcano.cfm?vn=372070), and [NOAA 258 wave](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events/3427). Full before/after images and evidence links are retained in the review manifests.

**Next:** preliminary 262–311 CE, while earlier years and linked articles remain incomplete.
