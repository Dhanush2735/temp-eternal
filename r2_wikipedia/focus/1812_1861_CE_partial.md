# R2: 1812–1861 CE, limited continuation

Reviewed 2026-10-31. **This 50-year interval has not been collected.** Existing prior work covered selected ten-year endpoints only. No new annual titles or annual revision archives were collected in this continuation: the collector's 125,000,000-byte workspace reserve remains exceeded. Unrestricted collection was not started and the reserve was not changed.

## Three existing indexed event corrections

1. `wpy_5b7908a326`: a copy of the 1821 Central American Act of Independence was wrongly assigned to 1824. Corrected to 1821 and changed to a non-damaging contextual note because another 1821 political record, `wpy_bcc697e7f3`, already exists. The linked article's infobox and body conflict over location; Guatemala City is a regional reference, not an asserted exact signing location. The independence process and provincial responses were not simultaneous.
2. `wpy_8d21ec4c6e`: corrected Graham Island's misplaced coordinates to the island between Sicily and Tunisia. Changed this extra generic disruption record to a contextual note; this does not mean the eruption posed no hazard.
3. `wpr_a7035a94fe`: corrected the 1841 separate-colony record from a British coordinate to Okiato in New Zealand, an early colonial-capital reference. This is a reference point, not the geographic extent of the colony or a statement excluding Māori presence.

The guarded context manifest is `reviews/1812_1861_ce_context_2026-10.json.gz`; canonical SHA-256 `218b60496f18a77a5b6762fab9f305aa16b24c880fde857beba5f00efe70a9bc`. Apply/rollback tool: `apply_1812_1861_ce_context.py`. Wikipedia source links are revision-pinned within the manifest. Four title/revision identities were independently checked in `pin_verification_1812_1861_CE_partial.json.xz`; identity verification alone does not establish historical completeness.

Actual disk apply, rollback and reapply reproduced canonical hashes of all 26 indexed packs, with two changed; `rollback_hashes_1812_1861_CE.json` records the hashes. Reverse any later layers before this context layer, then earlier batch layers. Writes are atomic per pack, not across packs. No hazard inventory or hazard moves were attempted for this interval. The game, loader, saved worlds and current build were not tested.

## Lossless storage cleanup

Compressed 95 pre-existing **research-only** people-link JSON files individually to `.json.gz`, saving 1,554,050 bytes before manifest and code overhead. Gameplay pack index and active VIP data were not changed by compression. `people_graph_gzip_1812_2026-10.json` records compressed and original byte hashes. `r2_wikipedia/people_graph_archive.py` transparently loads an original filename from its `.json.gz` equivalent and can restore the exact original bytes without overwriting. Thirty-seven affected research tests now use this fallback. Existing older reports refer to the original `.json` names; use the loader or restore command for those names.

Twelve current/archive/previous-layer/storage checks and 12 previous-batch checks passed. The archive test read and hash-checked all 95 compressed graphs and verified refusal to overwrite. One initial test invocation included a nonexistent test method; it was corrected and the relevant graph test passed. Storage remains above the 125 MB collector ceiling despite cleanup. No SQLite research database, gameplay pack or original research content was deleted.

## Progress and next work

The previous title inventory remains 4,800 recognized distinct year-title resolutions, not collected-year completions; the older 3,168 partly worked count remains unreconciled. **Zero years are established fully collected.** No newly linked people were added in this continuation; existing people-link graphs remain research-only and do not make VIPs spawnable. Natural VIP spawning, historical behavior and alternate-timeline branching remain unimplemented. The four older hash-locked layers with 2026-10-31 dates created on 2026-10-30 remain uncorrected. R1 and comprehensive game review remain deferred.

Resume the 1812–1861 full preliminary pass only after enough safe, verifiable workspace capacity is recovered without weakening the collector guard. Every earlier period also remains incomplete.
