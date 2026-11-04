# Preliminary batch: 162–211 CE

**Status: partly worked; 0 fully collected years.** The 50 years in this batch overlap previously sampled work. The legacy total of 3,168 partly worked years remains unreconciled and should not be increased by 50 without a distinct-year audit.

## Collection and scope

All 50 chronological titles resolved to distinct annual pages, none marked as a disambiguation page at retrieval. `year_titles_162_211_CE.json` records the titles and pinned revision IDs; `year_wikitext_162_211_CE.json.gz` stores those raw revisions. Transclusions are unexpanded. Selected annual sections and linked articles were checked, **not every linked article**.

The archived `indexed_start_scan_162_211_CE.txt.gz` contains **270 indexed records starting in this interval, including 44 hazards**. Earlier-starting overlaps are excluded. Most candidates remain unreviewed.

The title-file inventory finds **3,200 distinct chronological title resolutions**: 2,989 BCE and 211 CE. This is neither a count of completed years nor a count of individually reviewed years. Separate work on 3000–2990 BCE exists outside the title-file inventory.

## Indexed game data changes

Sixteen existing records were updated with guarded before/after images across seven indexed packs:

- The 178 CE row saying the Sasanians took over Central Asia was changed to a contextual note. The linked Sasanian overview conventionally dates the empire from **224**, and does not support that conquest in 178. The note is not an alternative exact date for Kushan decline.
- A China-centered 800 km disruptive row asserted that the Antonine Plague depopulated China as well as the Roman Empire. Its shared pathogen and connection to Chinese outbreaks are not established by the linked Roman-plague article, so the China assertion is now context only. The separate Rome-centered epidemic record remains active; its current one-year timing and 500 km circle are not a complete or validated epidemic model.
- A Hatra entry claimed **177 under Trajan**, who died in 117. The revised note points to 116–117 and explicitly records disagreement: one academic summary suggests probably 116, while the linked Diaspora Revolt account describes 117. The 197–198 Severan siege is a different event; a 199 year-page row referring to that later campaign was changed to context so it does not automatically add a second siege effect.
- The Roman–Parthian War row now starts in **161** rather than the earliest recorded battle in 163; its existing 300 km military circle remains only a regional proxy. The news and event loaders' end-boundary conventions have not been reconciled.
- Septimius Severus's Britain arrival was moved from 206 to the linked biography's **208**. Himiko's approximate reign dates and Yamatai's location are uncertain, so the 188 and 200 rows no longer impose 500 km political effects at a fixed site. The title *Shingi Waō* is not assumed to be a separate person.
- The 177 claim of a newly systematic persecution in Rome was qualified against the overview's account of largely local episodes under Marcus Aurelius. The Liang Province rebellion's southern-China proxy was replaced with a broad northwestern reference; the Yellow Turban decade row was made contextual rather than imposing a single 800 km effect. The distinct 184 year-page event remains indexed.
- Existing active Guandu and Red Cliffs battles retain their effects, with site uncertainty recorded. The Gansu earthquake entry retains its effect but now notes that NOAA flags its magnitude, epicentre and effects.

Twelve hazards were moved with their IDs from the active hazard pack to regional **notes**:

- GVP reports two distinct Cayambe eruptions at **170 (?)** and **200 (?)**; Te Kopia/Okataina at **180 (?)**; St. Helens East Dome at **190 (?)**; El Chichón **190 ±150 years**; Tengger Widodaren **190 ±50**; Wrangell **190 ±200**; Glacier Peak **200 ±50**; Cerro Chichinautzin **203 ±131**; and Salton Buttes **210 ±100**. These are confirmed eruptive periods with uncertain dates, not proof of a damaging effect in exactly the nominal year. Cayambe's two entries and Chichinautzin's different vents remain distinct.
- NOAA links the 173 Laizhou sea-flood report to an earthquake and assigns `eventValidity=2`; cited sources give different dates and one rates validity low. Its 177 Sicily sea-wave report is likewise linked to an earthquake, with validity 2 and differing quake-intensity reports. The waves became contextual notes to avoid treating each linked record as an independent certain effect; the separate earthquake effects remain active and require further review.

**32 of the 44 scanned hazards were not moved**, including the Gansu record modified in place. Many remain unreviewed; effects and radii have not been tested in game.

## Connected people

`history/sources/wikipedia_162_211_ce_people_links.json` contains **30 research references, 16 qualified relationships and 34 roles across 11 existing event IDs**. It includes figures on opposing sides of the Yellow Turban rebellion, Guandu, Red Cliffs, the Roman–Parthian war and the Severan civil war, as well as Himiko and Galen. Broader campaign association is not proof that a person was physically present at every battle. These are research leads, **not spawnable VIPs**, and do not implement historical or alternate-history behavior.

## Verification, provenance and rollback

- Final context canonical SHA-256: `f1c440235b51fb82a90fa4892f3a939ef0340a7ecc38f20e1898d5a023660173`; hazard moves: `06e3e2b1b7b4fe7e0e66627e5bdd6b17102203a94b5ac6b36986f1957f49b1a6`.
- Both migrations were staged before application. A later source check found that the Hatra note's initial Diaspora Revolt revision ID actually pointed to **Kitos War**. Both migrations were rolled back on disk in dependency order, the source pin was corrected, and the corrected context and hazard migrations were staged and applied again. All **44 distinct pinned Wikipedia revision/title pairs** in this batch's context manifest and people graph then matched the API.
- **12 batch tests passed**, including 28 unique after-images, tamper guards, pinned page archive checks and in-memory dependency-ordered rollback/reapplication. The preceding 112–161 batch also round-tripped in memory after first reversing this batch. Another **13 crawler, pipeline and compaction tests passed**. These are data checks, not live gameplay tests.
- Roll back **162–211 hazards, then context**, before 112–161 hazards and context, then earlier dependent shared-pack migrations. The source-pin correction exercised a disk rollback and reapply, but writes are atomic per pack rather than across all packs; no save-file rollback was tested.
- No live game, loader, save, full integrity check, Java probe or jar rebuild was performed; the jar remains stale. Natural VIP spawning, historical VIP behavior, and branching are not implemented. Year zero and differing pack-specific end boundaries remain open.

Sources include [Sasanian Empire](https://en.wikipedia.org/w/index.php?title=Sasanian_Empire&oldid=1380663601), [Antonine Plague](https://en.wikipedia.org/w/index.php?title=Antonine_Plague&oldid=1379814349), [Trajan's campaign](https://en.wikipedia.org/w/index.php?title=Trajan%27s_Parthian_campaign&oldid=1381076297), [Roth on Hatra](https://onlinelibrary.wiley.com/doi/abs/10.1002/9781119099000.wbabat0650), [Diaspora Revolt](https://en.wikipedia.org/w/index.php?title=Diaspora_Revolt&oldid=1382208101), [Severan Hatra siege](https://en.wikipedia.org/w/index.php?title=Siege_of_Hatra_%28197%E2%80%93198%29&oldid=1380867923), [Yellow Turban rebellion](https://en.wikipedia.org/w/index.php?title=Yellow_Turban_Rebellion&oldid=1382794631), [Liang Province rebellion](https://en.wikipedia.org/w/index.php?title=Liang_Province_rebellion&oldid=1370626748), [Red Cliffs](https://en.wikipedia.org/w/index.php?title=Battle_of_Red_Cliffs&oldid=1370587339), [Himiko](https://en.wikipedia.org/w/index.php?title=Himiko&oldid=1382796329), [GVP Chichinautzin](https://volcano.si.edu/volcano.cfm?vn=341080), [GVP Salton Buttes](https://volcano.si.edu/volcano.cfm?vn=323200), [NOAA Laizhou](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events/29), and [NOAA Sicily](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events/3097). Full before/after records and sources are retained in the review manifests.

**Next:** preliminary 212–261 CE, while earlier years and their linked articles remain incomplete.
