# 612–661 CE — preliminary R2 research and gameplay-data pass

**Status: partial, not 50 completed years.** All 50 annual title resolutions led to distinct non-disambiguation annual pages; pinned raw revisions are archived, with transclusions unexpanded. The starting-record scan found **631 indexed records, including 33 hazards**. Records beginning earlier but overlapping this interval were excluded. Only selected articles and records were reviewed; most remain unchecked.

## Indexed gameplay-data changes

Nine guarded updates were applied across five indexed packs:

- Corrected **Nahavand** from an Iraqi al-Qadisiyyah-area point to a modern Nahavand city reference, and the **636 siege of Latakia** from Phrygian Laodicea to the Syrian city. These locations are proxies, not exact battle footprints.
- Corrected the siege of **Uthman's house** to a Medina city reference. The year-page succession narrative is now a contextual note rather than an additional active siege.
- Corrected the **Battle of Salsu** narrative from the Yalu to the Chongchon River. Its stored point is a river-mouth reference, not an established battlefield. The old unqualified troop totals were removed from the event title, not asserted as verified losses.
- Moved the indexed **Battle of Nahrawan** from 659 to the linked article's 658 and corrected its reference point. The year-page copy is a note rather than a second military effect; the First Fitna continued to 661.
- Replaced an assertion of the first Chinese paper money in exactly 650 with a qualified Tang-period context note. The linked overview discusses merchant receipts in Tang China and later centralized Song paper money; it does not establish an exact 650 issue.
- Qualified the **Plague of Amwas** as a 638–639 epidemic and the 25,000 figure as a reported upper estimate for troops and their relatives, not a verified overall death toll.

One additional hazard was moved to an indexed non-damaging context note: the duplicate 800 km Amwas lockdown had been centered in western Turkey. It now uses Emmaus as a reference and preserves the original ID. The separate disease-disruption record remains; its 150 km circular effect is only a game approximation. **The other 32 scanned hazards were not reviewed or moved**, and may still be wrong.

## People and relationships

`history/sources/wikipedia_612_661_ce_people_links.json` contains **27 people, 16 relationships and 29 event-role associations across 9 indexed IDs**, including figures associated with Salsu, Nahavand, Dongola, the Plague of Amwas and the First Fitna. Associations do not establish co-presence or complete biographies. These research leads are **not spawnable VIPs**.

## Evidence and verification

- `year_titles_612_661_CE.json`, `year_wikitext_612_661_CE.json.gz` and `indexed_start_scan_612_661_CE.txt.gz` archive the resolved titles, raw revisions and initial scan.
- Reversible context manifest: `reviews/612_661_ce_context_2026-10.json.gz`, canonical SHA-256 `17ba549cd3755b917577df7c0623ec5ac66b766bb76d5f48daf73611b1e34c29`. Hazard manifest: `reviews/612_661_ce_hazards_2026-10.json`, SHA-256 `49c4f390f5a77bb816db2056b74c94f142f619fd0453260e131c8197b17731e0`.
- Both layers were staged and applied. **11 batch tests plus 19 resolver/scope/pipeline tests passed**. Tests include dependency-ordered **in-memory** reversal and reapplication of this and the previous batch. **43 pinned Wikipedia revision/title pairs** matched the API. Actual disk rollback and saved-world effects were not tested.
- Selected sources: [Battle of Salsu](https://en.wikipedia.org/wiki/Battle_of_Salsu), [Battle of Nahavand](https://en.wikipedia.org/wiki/Battle_of_Nahavand), [Siege of Laodicea (636)](https://en.wikipedia.org/wiki/Siege_of_Laodicea_(636)), [Battle of Nahrawan](https://en.wikipedia.org/wiki/Battle_of_Nahrawan), [Plague of Amwas](https://en.wikipedia.org/wiki/Plague_of_Amwas), [paper money](https://en.wikipedia.org/wiki/Paper_money), and [Second battle of Dongola](https://en.wikipedia.org/wiki/Second_battle_of_Dongola). Pinned article revisions are in the manifests and people file.

Reverse later dependent batches first, then run `python r2_wikipedia/apply_612_661_ce_hazards.py rollback` before `python r2_wikipedia/apply_612_661_ce_context.py rollback`. Writes are atomic per pack, not across packs.

## Limits and progress

Most of the 631 scanned records and their linked articles remain unreviewed, as do earlier periods. There was no live Minecraft, loader, save, full integrity or current Java test, and no jar rebuild; no current runnable jar is persisted. Natural VIP spawning, historical behavior and player-triggered branching remain unimplemented.

The title inventory now reports **3,650 distinct chronological titles resolved**: 2,989 BCE and 661 CE. This is not collected history or a complete count of partly worked years. The older 3,168 partly worked figure remains unreconciled. **Fully collected years: 0.** Next preliminary interval: 662–711 CE. Workspace capacity is close to the snapshot limit and will require further safe storage work.
