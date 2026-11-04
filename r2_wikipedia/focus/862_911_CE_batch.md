# 862–911 CE — preliminary R2 research and gameplay-data pass

**Status: 50 years partly processed, not completed.** Archived 50 distinct annual pages and their pinned raw revisions, without expanding transclusions. Scanned **573 indexed records starting in the interval, including 65 hazards**; earlier-starting events that overlap the interval were excluded. Most records and linked articles remain unreviewed.

## Indexed gameplay-data changes

Staged and applied **30 guarded updates across six packs**, plus **eight hazard-to-note moves**:

- Extended the gazetteer-exclusive ends of the sieges of **Ragusa**, **Syracuse** and **Paris** to include their source-described final years, 868, 878 and 886. The 877–878 Syracuse siege is distinct from the 827–828 siege. NewsIndex uses different boundary conventions and needs separate testing.
- Corrected the location of **Edington/Ethandun** to a probable Wiltshire site, while noting the exact battlefield is disputed; its duplicate decade entry is now a note. Similarly, a generic 882 Cellorigo entry is contextual rather than a second damaging battle; the separately indexed 882 and 883 battles remain distinct. The first-battle article has limited inline citations.
- Corrected the **Zanj Rebellion** span to 869–883 and made the broad series a contextual note rather than a single continuous military circle. The separately indexed 871 Basra battle remains. The revolt began near Basra and included people of varied backgrounds; its composition remains debated.
- Corrected **Ahmad ibn Tulun’s** appointment and death locations from Iraq and Syria to Egyptian city references, and qualified the gradual growth of autonomy after his appointment in 868. Corrected the early **Huang Chao/Wang Xianzhi** uprising to the Changyuan region, distinguishing 874 from Huang’s documented involvement by 875; the mistaken natural-disaster classification was removed.
- Moved Icelandic settlement references from Norway to a Reykjavík proxy and identified the traditional 874 chronology as uncertain. Corrected the **Preslav council** references to the Preslav region and noted that the council is reconstructed rather than directly mentioned in surviving medieval sources. Corrected the **Bagratuni** note: Ashot’s 862 status was not the founding of the older dynasty.
- Qualified Rurik’s later chronicle tradition, the reported agreement associated with **Wedmore**, Prague Castle’s early construction, and Parantaka I’s Chola–Pandya campaigns. The latter source does not establish a complete Sri Lankan conquest in 910. The 907 Rukam inscription does not by itself prove the exact year or volcano of the eruption it records.
- Corrected six earthquake labels that had converted NOAA casualty **categories** into exact death counts. Corrected a mislabeled 887 tsunami at **Niigata**: its coordinates match NOAA event 76, not the separately indexed Nankaido event 77. The retained disruptions and their geographic footprints remain approximate.
- Moved seven geologically dated eruptions and the questionable **900 Nagapattinam tsunami** from damaging hazards to indexed notes. For example, Smithsonian GVP dates Alamagan around **870 ±100 years** and Glacier Peak around **900 ±50 years**; these do not justify exact-year triggers. NOAA marks the Nagapattinam report validity 1 and cites a literary narrative. Pelée’s approximately 890 and 910 records were both preserved as notes, not automatically merged.

**57 scanned hazards remain in the hazard pack**, including seven qualified in place; most were not reviewed. The separate 893 Dvin and Ardabil earthquake records, other duplicate/overlapping disasters, and the remaining volcano dates require further source-critical review.

## People and relationships

`history/sources/wikipedia_862_911_ce_people_links.json` records **44 people, 29 relationships and 46 event-role associations across 17 indexed event IDs**. These selected leads cover the Zanj revolt, Tang rebellions, Viking and Frankish campaigns, Bulgaria, Iceland, Armenia and other events. Roles do not establish co-presence or complete biographies, and these profiles are **not spawnable VIPs**.

## Evidence and verification

- Resolution: `year_titles_862_911_CE.json`; raw annual revisions: `year_wikitext_862_911_CE.json.gz`; scan: `indexed_start_scan_862_911_CE.txt.gz`.
- Context manifest `reviews/862_911_ce_context_2026-10.json.gz`, canonical SHA-256 `c29ecc46b3d6a48d8504a0bf85dc3881e3fc78638d6c7d92d51b757fbe636df3`; hazard manifest `reviews/862_911_ce_hazards_2026-10.json`, canonical SHA-256 `9fe70483f4f8df4fe379e68d6aa917d9a858c15d132a7e20030fef91f71b19e1`.
- **11 batch tests and 19 resolver/scope/pipeline tests passed**, including dependency-ordered in-memory reversal and reapplication of this and the preceding batch. **64 Wikipedia revision/title pairs** matched the API. The initial context layer was actually rolled back on disk and reapplied after correcting its wording; saved-world rollback was not tested. Writes are atomic per pack, not across packs.
- Sources include [Zanj Rebellion](https://en.wikipedia.org/wiki/Zanj_Rebellion), [Siege of Paris](https://en.wikipedia.org/wiki/Siege_of_Paris_(885%E2%80%93886)), [Battle of Edington](https://en.wikipedia.org/wiki/Battle_of_Edington), [Ahmad ibn Tulun](https://en.wikipedia.org/wiki/Ahmad_ibn_Tulun), [Huang Chao Rebellion](https://en.wikipedia.org/wiki/Huang_Chao_Rebellion), [Council of Preslav](https://en.wikipedia.org/wiki/Council_of_Preslav), [Settlement of Iceland](https://en.wikipedia.org/wiki/Settlement_of_Iceland), [NOAA tsunami 76](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events/76), [NOAA tsunami 5283](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events/5283), [GVP Alamagan](https://volcano.si.edu/volcano.cfm?vn=284180), and [GVP Glacier Peak](https://volcano.si.edu/volcano.cfm?vn=321020). Pinned Wikipedia article revisions are recorded in the context manifest and graph.

To roll back, reverse any later dependent layers first, then run `python r2_wikipedia/apply_862_911_ce_hazards.py rollback`, followed by `python r2_wikipedia/apply_862_911_ce_context.py rollback`.

## Limits and overall progress

No live Minecraft, loader, saved-world, full integrity or current Java test, or jar rebuild was performed. Natural VIP spawning, historical behavior and player-triggered branching remain unimplemented. Earlier years also remain incomplete.

The inventory reports **3,900 distinct chronological year titles resolved** (2,989 BCE and 911 CE). This is not a count of collected histories or individually reviewed years. The legacy **3,168 partly worked** figure is unreconciled; **fully collected years: 0**. Next preliminary interval: 912–961 CE. Snapshot capacity remains very close to its best-effort limit.
