# 1942 CE preliminary review

Reviewed 3 November 2026. One English Wikipedia annual revision was archived and a selective sample of linked articles reviewed. The pre-change inventory has **409 indexed starts, including 85 hazard starts**; these hazards were not individually reviewed. Raw wikitext does not expand transclusions. This is **not a complete year**.

Four existing records were corrected, retaining IDs and gameplay effects:

- `wpy_75f2c588cd`: the escape of Airey Neave and Anthony Luteyn now uses a [Colditz Castle](https://en.wikipedia.org/wiki/Colditz_Castle) location proxy rather than a generic point in Germany. [Luteyn's biography](https://en.wikipedia.org/wiki/Anthony_Luteyn) describes their escape and assistance by Pat Reid and Howard Wardle.
- `wpy_0ed4b4b0b8`: Hajime Toyoshima's crash and capture by Matthias Ulungura now use a [Melville Island](https://en.wikipedia.org/wiki/Melville_Island_(Northern_Territory)) proxy rather than inland Australia. The capture occurred near Snake Bay; the island coordinate is not the exact site. Sources: [Toyoshima](https://en.wikipedia.org/wiki/Hajime_Toyoshima), [Ulungura](https://en.wikipedia.org/wiki/Matthias_Ulungura).
- `wpy_0a5ec2721b`: the [Sobibor extermination camp](https://en.wikipedia.org/wiki/Sobibor_extermination_camp) record now uses the camp-site proxy and the linked article's estimated **170,000–250,000** murdered. The article identifies operation in May 1942–October 1943; no exact opening day is asserted by the updated annual summary.
- `wpy_a2eeb16145`: [Treblinka extermination camp](https://en.wikipedia.org/wiki/Treblinka_extermination_camp) construction now uses the camp-site proxy, with the linked article's estimated **800,000–925,000** murdered over its 1942–1943 operation.

Site proxies and existing radii are not verified historical boundaries. The camp records retain existing `political` effects and annual record durations; those mechanics are not a simulation of the camps' actual operation. Moving them changes where existing effects can apply. Similar records were inspected by keyword; the 1943 uprising and other later mentions are separate events, not deleted. A full duplicate review has not been performed.

The before/after manifest `reviews/1942_ce_context_2026-11.json.gz` has canonical SHA-256 `72b1ca778459dceda860cd08b12eff3774e41deab293e0bc75d3f4d7965f6f9c`. The guarded installer `apply_1942_ce_context.py` applied, rolled back and reapplied the changes. Compressed hashes of all **26 indexed packs** were reproduced, with one pack changed. Writes are atomic per pack, not across packs. Nineteen selected tests passed; **no live-game or saved-world test**.

`history/sources/wikipedia_1942_ce_people_links.json.gz` records **10 people, four relationships and 13 event associations** as research-only, not spawnable VIPs. These include escapees and helpers, Ulungura and Toyoshima, and camp officials and builders. Associations with the camps do not establish a person's presence at the exact opening or beginning of construction. Fifteen article identities and revisions were verified; this is not independent verification of every historical claim.

To make space, generated historical references `eternal/FIELD_DOSSIER.md` and `eternal/field_spec.json` were archived losslessly with checksum-verified restoration through `eternal/archived_generated_reports.py`; they are not active gameplay data. Generators still use the original output paths.

The year-title audit recognizes **4,931 distinct titles**, not completed years. **Fully collected years: 0.** 1942 remains partial; 1943 was not collected in this pass. Natural VIP spawning and alternate-timeline behavior remain unfinished.
