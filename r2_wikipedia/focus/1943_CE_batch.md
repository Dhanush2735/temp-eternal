# 1943 CE preliminary R2 review

Reviewed 3 November 2026. One English Wikipedia annual revision was archived; raw wikitext does not expand transclusions, and linked articles were selectively reviewed. The pre-change inventory contains **465 indexed starts**, including **85 hazard starts not individually reviewed**. Older active records are not counted. **This year is not complete.**

## Installed gameplay-data corrections

Four existing records were corrected in `events_wikipedia.json.gz`, retaining their IDs, effects and year-level duration:

- `wpy_c23be2f604`: [Kraków Ghetto](https://en.wikipedia.org/wiki/Krak%C3%B3w_Ghetto) liquidation moved from Warsaw to a ghetto location proxy in Kraków. Liquidation occurred over an extended period, with its final phase in 1943. The existing political effect was not reviewed for its wider gameplay implications.
- `wpy_828369cf5c`: [raid on the Roman Ghetto](https://en.wikipedia.org/wiki/Raid_on_the_Roman_Ghetto) moved from Berlin to a Roman Ghetto proxy. This is not a map of every arrest location. The record retains that the public response of Pius XII is historically contested; it does not resolve the debate.
- `wpy_b3390c1e29`: [Lucie Aubrac and Raymond Aubrac](https://en.wikipedia.org/wiki/Lucie_Aubrac)'s rescue event moved from Berlin to a Lyon city proxy, not the precise vehicle-ambush location.
- `wpy_1e41c7c824`: Gandhi's 1943 fast moved from a Pune city proxy to the Aga Khan Palace site, and the summary now reflects **10 February–3 March**, rather than showing only the ending date. The annual Wikipedia page says Pune, but its linked [list of fasts](https://en.wikipedia.org/wiki/List_of_fasts_undertaken_by_Mahatma_Gandhi) says Delhi. The [Rajghat chronology](https://rajghat.gov.in/chronology) independently places this fast at Aga Khan Palace jail in Pune. The [palace article](https://en.wikipedia.org/wiki/Aga_Khan_Palace) supports Gandhi's detention there but incorrectly implies Mahadev Desai survived until 1944; he died in 1942. This conflict is retained in the evidence rather than silently ignored.

Location proxies and unchanged 20 km radii are not verified event boundaries. Moving a record changes where its existing effects may apply. No new indexed records were added.

## Duplicates and outstanding errors

- Operation Iskra (`wpy_a8c5871d82`) is incorrectly placed in Siberia; it appears to overlap an existing indexed Operation Spark record (`q233278`). It was **not moved** because relocating its `military_presence` effect could stack with the existing record. Dedupe and stacking require review.
- The Lyngiades massacre (`wpy_eff0fef9ac`) is incorrectly placed near Berlin; another indexed record (`q27972892`) already marks the event in Greece. It was **not moved** pending overlap and effect review.
- The Bougainville landing (`wpy_868fed3962`) is incorrectly located in Virginia and combines the Bougainville landing with the name Operation Goodtime; the [linked operation](https://en.wikipedia.org/wiki/Battle_of_the_Treasury_Islands) concerns the Treasury Islands. Both campaigns have existing indexed records. It remains unchanged pending careful event-identity and duplication review.

## Verification and people

The reversible manifest `reviews/1943_ce_context_2026-11.json.gz` has canonical SHA-256 `f257095c721bc9d464832a36e41819b52907d09444cf5973933419b705c3e4d2`. Actual apply, rollback and reapply reproduced compressed hashes of **all 26 indexed packs**; one pack changed. Installation is atomic per pack, not across packs. **21 selected tests passed.** There was no live-game or saved-world test.

`history/sources/wikipedia_1943_ce_people_links.json.gz` contains **10 research leads, two relationships and 10 event associations**. They include Gandhi, Kasturba Gandhi and Sushila Nayyar; Lucie and Raymond Aubrac; and people connected to the Kraków and Rome records. Contextual associations do not automatically prove attendance at a specific event. The file is **not spawnable VIP data**, a complete biography collection, or an NPC schedule. Nineteen Wikipedia title/revision identities were checked; identity checks do not establish every factual claim.

For storage, the historical generated `worldfill/fact_audit_summary.json` and `eternal/LIVE_COMMAND_AUDIT_REPORT.json` were archived losslessly as `.xz`. Their respective `archived_history_reports.py` and `archived_generated_reports.py` verify and restore them with no-overwrite and storage guards; generators still write the original paths. They are reports, not active gameplay data.

**Fully collected years: 0.** 1943 is partial, and 1944 was not collected in this pass. Natural VIP spawning and alternate-timeline behavior remain unfinished. Terra++ integration remains as documented separately in `TERRA3_REPLACEMENT.md`.
