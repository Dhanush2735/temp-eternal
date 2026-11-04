# 712–761 CE — preliminary R2 research and gameplay-data pass

**Status: 50 years partly processed, not completed.** All 50 distinct annual pages and their pinned raw revisions were archived, without expanding transclusions. The starting-record scan covered **515 indexed records, including 49 hazards**; it excludes events that began earlier but overlap the interval. Most records and linked articles remain unreviewed.

## Changes to indexed game data

**20 guarded updates across six packs** and **four hazard-to-note moves** were staged and applied. Selected changes include:

- Corrected the 715 Battle of Compiègne's longitude from west of Greenwich to the approximate French battle reference. The battle article needs more citations.
- Included 718 in the 717–718 siege of Constantinople under the gazetteer's exclusive-end convention. The news index uses different boundary rules and needs separate testing.
- Preserved the **732 and 740 battles of Akroinon as separate events**. A distinct English article and Wikidata item describe the 732 campaign. The initial assumption that the 732 entry was a duplicate was corrected before final application; further source review remains necessary.
- Corrected Antioch in Pisidia, Luoyang and Guangzhou records that had been assigned distant locations. These points are city or archaeological-site references, not precise reconstructed event sites.
- Corrected Quiriguá's 734 title claim and its 738 victory over Copán, including a record that incorrectly placed the victory in 736. Duplicate 738 and 750 declaration records were converted to notes.
- Qualified Debal's 711/712 chronology and uncertain location; Sanjaya's accession chronology; Borobudur's estimated construction dates; and Kailasa Temple's attribution and approximate date. No precise 760 completion or pre-Buddhist Borobudur shrine is claimed.
- Replaced the misplaced offshore Bashmurian-revolt reference with a broad northern Nile Delta proxy and described the revolts as an intermittent series c.720–832 rather than continuous warfare. The exclusive end 833 is a span for the series note, not years of continuous fighting.
- NOAA's 746 earthquake record is flagged as a possible duplicate and discusses 746/749; Wikipedia indexes a 749 event and discusses multiple possible quakes. The NOAA 746 hazard and associated uncertain wave report were moved to notes, while the existing 749 event remains active as an approximation. NOAA's `deathsAmountOrder=3` is a category, **not three reported deaths**. Two other uncertain tsunami hazards were also moved to notes. The remaining **45 scanned hazards were not moved and are largely unreviewed**.

## People and relationships

`history/sources/wikipedia_712_761_ce_people_links.json` records **43 people, 28 relationships and 38 event-role associations across 16 indexed event IDs**, including Sindh, Frankish and Byzantine campaigns, Quiriguá, Mataram, the Abbasid transition and Tang China. These are selected, sourced research leads, not complete biographies or proof that everyone was present together. They are **not spawnable VIPs**.

## Evidence and verification

- Resolution: `year_titles_712_761_CE.json`; raw annual revisions: `year_wikitext_712_761_CE.json.gz`; starting-record scan: `indexed_start_scan_712_761_CE.txt.gz`.
- Context manifest `reviews/712_761_ce_context_2026-10.json.gz`, canonical SHA-256 `3a8758af34506d467b94e6ec2b7ac45afcd3d44fa31b1e1d9c7acdaec9d09e0d`; hazard manifest `reviews/712_761_ce_hazards_2026-10.json`, canonical SHA-256 `06e1f4697a8c6bc1f17c12cc956cfd9ddaa9eb29831dd4c118bf22cde8d82222`.
- **11 batch tests and 19 resolver/scope/pipeline tests passed**, including a dependency-ordered in-memory reversal/reapplication with the previous batch. **66 Wikipedia revision/title pairs** matched the API. An actual disk rollback of this batch and reapplication were performed to correct the Akroinon interpretation; saved-world rollback was not tested. Writes are atomic per pack, not across packs.
- Evidence includes [Battle of Akroinon (732)](https://en.wikipedia.org/wiki/Battle_of_Akroinon_(732)), [Battle of Akroinon (740)](https://en.wikipedia.org/wiki/Battle_of_Akroinon), [Siege of Constantinople (717–718)](https://en.wikipedia.org/wiki/Siege_of_Constantinople_(717%E2%80%93718)), [Kʼakʼ Tiliw Chan Yopaat](https://en.wikipedia.org/wiki/K%CA%BCak%CA%BC_Tiliw_Chan_Yopaat), [Borobudur](https://en.wikipedia.org/wiki/Borobudur), [NOAA earthquake 177](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/177) and [NOAA tsunami 59](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events/59). Pinned article revisions are in the manifests and graph.

For rollback, reverse any later dependent layers first, then run `python r2_wikipedia/apply_712_761_ce_hazards.py rollback` followed by `python r2_wikipedia/apply_712_761_ce_context.py rollback`.

## Limits and progress

No live Minecraft, loader, saved-world, full integrity or current Java test, or jar rebuild was performed. Natural VIP spawning, historical behavior and player-triggered branching remain unimplemented. Earlier years also remain incomplete.

The inventory reports **3,750 distinct chronological year titles resolved** (2,989 BCE and 761 CE). That is not a count of collected histories or individually reviewed years. The old **3,168 partly worked** figure is unreconciled; **fully collected years: 0**. Next preliminary interval: 762–811 CE. Snapshot capacity remains close to its best-effort limit.
