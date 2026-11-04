# 1941 CE: preliminary R2 review

Reviewed 3 November 2026, after the user chose to continue forward from 1941. This is **one partly worked year, not a complete history**. The English Wikipedia year revision was archived and linked articles were checked selectively. The raw wikitext has unexpanded transclusions; linked articles, historical events, people and hazards remain largely unreviewed.

The pre-correction inventory contains **514 indexed starts**, including **113 hazard-pack starts not individually reviewed**. It excludes older records still active during 1941. The revision and inventory are in `year_titles_1941_1941_CE.json`, `year_wikitext_1941_1941_CE.json.xz` and `indexed_start_inventory_1941_1941_CE.json.xz` in this folder.

## Gameplay-data corrections

Four existing records in `events_wikipedia.json.gz` were corrected, retaining their IDs and effects:

- **Viet Minh formation:** moved the record from central Vietnam to a Pác Bó village proxy. Removed the incorrect statement that the Viet Minh simply became the Viet Cong. The new summary describes the founding of the independence coalition without asserting an exact meeting point. Sources: [Viet Minh](https://en.wikipedia.org/wiki/Viet_Minh), [Pác Bó](https://en.wikipedia.org/wiki/P%C3%A1c_B%C3%B3).
- **Takeo Yoshikawa:** moved the arrival from Tokyo to a Honolulu city proxy. His biography says he did not know of a planned Pearl Harbor attack when gathering intelligence, so the summary no longer claims that he was preparing for a known future attack. Sources: [Takeo Yoshikawa](https://en.wikipedia.org/wiki/Takeo_Yoshikawa), [Honolulu](https://en.wikipedia.org/wiki/Honolulu).
- ***Citizen Kane* premiere:** moved the record from Los Angeles to the Palace Theatre in New York, where the film premiered. This is not evidence that all cast and crew attended. Sources: [Citizen Kane](https://en.wikipedia.org/wiki/Citizen_Kane), [Palace Theatre](https://en.wikipedia.org/wiki/Palace_Theatre_(New_York_City)).
- **Haile Selassie's return:** moved the record to an Addis Ababa city proxy. The existing political effect remains; the point is not a precise route or the entire campaign. Sources: [Haile Selassie](https://en.wikipedia.org/wiki/Haile_Selassie), [Addis Ababa](https://en.wikipedia.org/wiki/Addis_Ababa), [East African campaign](https://en.wikipedia.org/wiki/East_African_campaign_(World_War_II)).

Radii are gameplay approximations, not verified event boundaries. Moving records changes where their existing effects can apply. No hazard-pack records were corrected.

Reversible before/after manifest: `reviews/1941_ce_context_2026-11.json.gz`, canonical SHA-256 `174f01db7db47871b8a86f909c19d5cd49b0b5574cf1c2a67a70f4d78626fc20`; guarded installer: `apply_1941_ce_context.py`. Actual apply, rollback and reapply reproduced compressed hashes of all 26 indexed packs; one pack changed. Writes are atomic per pack, not across packs. There was **no live-game or saved-world test**.

## People and sources

`history/sources/wikipedia_1941_ce_people_links.json.gz` contains **nine research leads, five relationships and nine event roles**. They include Hồ Chí Minh, Trường Chinh and Võ Nguyên Giáp; Yoshikawa and Nagao Kita; Orson Welles and Herman J. Mankiewicz; and Haile Selassie and Orde Wingate. The association of Trường Chinh and Giáp does not establish their presence at the Viet Minh founding meeting; a film credit does not establish premiere attendance; a campaign connection does not establish presence at Selassie's return. Kita's article carries a notability warning. These are **not spawnable VIPs**, complete biographies, schedules or behavior rules. Seventeen Wikipedia title/revision identities were checked; identity checks alone do not validate every historical claim.

## Tests and storage

Twenty-one selected tests passed, including current and previous-batch checks and archive checks. To make room, three historical generated files were losslessly archived: `worldfill/PRODUCT_ATLAS_TABLE.md.xz`, `worldfill/build_places_report.json.xz` and `eternal/structure.txt.xz`. The product atlas table is a generated human-readable reference, **not** the active product JSON; its data was not discarded. `worldfill/archived_history_reports.py PRODUCT_ATLAS_TABLE.md --print` reads its verified original bytes, or `--restore` restores it subject to the space and no-overwrite guards. The other reports have corresponding guarded helpers and notes in their documentation. Generators can still write their original paths.

The title audit recognizes **4,930 distinct annual titles** (2,989 BCE and 1,941 CE); 11 early BCE years have evidence outside this inventory. This counts titles, **not completed years**. Fully collected years established: **0**. The originally requested ten-year steps remain incomplete, and 1942 has not been collected in this pass. Recursive and people collectors are parked; natural VIP spawning and alternate-timeline behavior remain unfinished. R1 remains deferred.
