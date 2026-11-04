# 1940 CE: preliminary R2 review

Reviewed 3 November 2026. This is **one partly worked year, not a completed history**. Its English Wikipedia year revision was archived, and linked articles were checked selectively, not exhaustively. The raw year wikitext does not expand transclusions. Most events, linked articles, biographies and hazards still require review.

The pre-correction inventory contains **411 indexed starts**, including **99 hazard-pack starts** that were not individually reviewed. It excludes older events still active in 1940. See `year_titles_1940_1940_CE.json`, `year_wikitext_1940_1940_CE.json.xz`, and `indexed_start_inventory_1940_1940_CE.json.xz` in this folder.

## Indexed gameplay updates

Five existing records were corrected in two indexed packs, retaining their IDs. Exact source-revision URLs and prior and replacement records are preserved in the reversible review manifest.

- **Udham Singh and Michael O'Dwyer:** moved the assassination record from Amritsar to Caxton Hall, Westminster, London. Singh's later execution was at Pentonville Prison, not Caxton Hall. Sources: [Udham Singh](https://en.wikipedia.org/wiki/Udham_Singh), [Michael O'Dwyer](https://en.wikipedia.org/wiki/Michael_O%27Dwyer), [Caxton Hall](https://en.wikipedia.org/wiki/Caxton_Hall).
- **Lahore Resolution:** moved the record to a park-area proxy for the former Minto Park in Lahore. Revised the description: the resolution called for independent states with autonomous and sovereign constituent units, not merely greater autonomy. The point represents the park area, not a precisely located session. Sources: [Lahore Resolution](https://en.wikipedia.org/wiki/Lahore_Resolution), [Greater Iqbal Park](https://en.wikipedia.org/wiki/Greater_Iqbal_Park).
- **Attack on Mers-el-Kébir:** moved the year-page record from inland Algeria to the attack-area coordinate. This is not a footprint for all locations involved. A separate indexed world-battle record remains; potential overlap is untested. Source: [Attack on Mers-el-Kébir](https://en.wikipedia.org/wiki/Attack_on_Mers-el-K%C3%A9bir).
- **Trotsky attack:** moved a regional record to a Coyoacán borough proxy and reduced its previous 705 km gameplay radius to 20 km. The attack was on 20 August; Trotsky died on 21 August. The proxy is not the exact residence. A separate year-page record remains, so overlap is untested. Sources: [Assassination of Leon Trotsky](https://en.wikipedia.org/wiki/Assassination_of_Leon_Trotsky), [Coyoacán](https://en.wikipedia.org/wiki/Coyoac%C3%A1n).
- **Tripartite Pact:** moved the regional signing record to a Berlin city proxy and reduced its radius from 335 km to 20 km. This does not represent the geographic extent of the alliance. Sources: [Tripartite Pact](https://en.wikipedia.org/wiki/Tripartite_Pact), [Berlin](https://en.wikipedia.org/wiki/Berlin).

The radii are gameplay approximations, not verified event boundaries. Existing kinds and effects were retained; moving records can change where those effects apply. No hazard-pack rows were corrected in this pass. The Welles Declaration's suspect existing location remains uncorrected.

Reversible manifest: `reviews/1940_ce_context_2026-11.json.gz`, canonical SHA-256 `858822486fb7f6eb1c70814349eea89508cf721960ab90ff8891bc614737ac9d`; installer: `apply_1940_ce_context.py`. Actual apply, rollback and reapply reproduced the compressed hashes of all 26 indexed packs; two packs changed. Writes are atomic per pack, not across packs. No live-game or saved-world test was performed.

## People and sources

`history/sources/wikipedia_1940_ce_people_links.json.gz` holds **11 research leads, six qualified relationships and 11 roles** linked to the five events. These include Singh and O'Dwyer; Jinnah and Fazlul Huq; the opposing commanders Somerville and Gensoul; Trotsky and Mercader; and the three Pact signatories Ribbentrop, Ciano and Kurusu. These are historical associations, **not spawnable VIPs**, complete biographies, NPC schedules or rules for alternate timelines. Twenty Wikipedia title/revision identities were checked in `pin_verification_1940_CE_context.json.xz`; identity checks are not independent proof of every claim.

## Verification and storage

Fifteen selected new, prior-batch and archive tests passed. The original 67,349-byte progress ledger was losslessly stored as two checked XZ parts; `python3 r2_wikipedia/progress_snapshot_1939.py` verifies it and `--print` reconstructs the original bytes to standard output. The latest summaries remain readable in `PROGRESS.md`. The duplicate-ID audit was also losslessly archived as `reviews/duplicate_event_ids.json.xz`; `review_snapshot_archive.py duplicate_event_ids.json` verifies and reads it, and guarded restoration refuses overwrite or insufficient storage. These are archives of prior evidence, not deletions of the only copy or changes to Terra++.

## Remaining scope

The current title audit recognizes **4,929 distinct annual titles**: 2,989 BCE and 1,940 CE; 11 early BCE years have evidence outside this inventory. Title recognition does not mean a year was fully examined or implemented. **Fully collected years established: 0.** The five ten-year steps requested from 3000 BCE remain incomplete; this 1940 pass does not complete them. Recursive and people collectors remain parked, and natural VIP spawning, historical VIP behavior and alternate-timeline branching remain unfinished. R1 remains deferred.
