# R2 preliminary batch: 362–411 CE

Reviewed 30 October 2026. This is a preliminary pass, **not completion of the 50 years**.

## Coverage

- Resolved 50 distinct annual Wikipedia titles and archived their revisions in `year_titles_362_411_CE.json` and `year_wikitext_362_411_CE.json.gz`. Transclusions are not expanded; resolving a title is not collecting the year.
- Scanned 381 indexed records starting in the interval, including 44 hazard-pack records. Records starting earlier but overlapping this period were excluded. Only selected records and linked articles were reviewed; most remain unreviewed.
- Inventory: 3,400 distinct resolved chronological titles, not 3,400 completed or individually reviewed years. The older 3,168 partly-worked aggregate remains unreconciled. **Fully collected years: 0.**

## Indexed gameplay changes

Applied 17 guarded updates across six indexed packs. The manifest preserves IDs, source links and before/after images.

- The two 363 Pirisabora/Perisabor siege Wikidata IDs describe the same dated siege at nearly the same coordinates. One remains an active military marker; the other is retained as a note, not deleted.
- Corrected the geographical references for Mawiyya's Levantine revolt, Siyaj Kʼakʼ in the Maya lowlands, the Fei River battle and Eastern Jin succession. Each point is a regional or site proxy, not a proven campaign footprint.
- Qualified Chandragupta II's approximate succession, western expansion and marriage alliance with the Vakatakas, and an uncertain 386 Armenia treaty reference. Multiple other 384/387 treaty records remain unreviewed.
- Retained a 365 Crete earthquake marker while replacing a broad overlapping 400 km circular disruption with a contextual note. This does not simulate the documented tsunami's full, geographically varied coastal effects.
- Retained and qualified the 368–369 Cappadocia famine and the 407 Constantinople earthquake. NOAA's accounts distinguish a possible storm effect from a proven tsunami.

Moved 22 hazard-pack records to indexed, non-disruptive regional notes: 16 geological eruptions with uncertain dates, four disputed waves, one 382 earthquake whose historical basis is disputed, and an unsupported separate 375–376 famine circle. For example, Smithsonian GVP gives Sierra Negra **370 ±1100 years**, not exactly 370; NOAA cites scholarship questioning the historical source and 382 date for the Cape St Vincent event. The move preserves the research; it does not prove that the underlying eruption, quake or wave never occurred.

Of the 44 scanned hazards, 22 were not moved; two were updated in place and the others remain largely unreviewed. In particular, the separately indexed 362 Al-Karak quake remains active; its relation, if any, to the 363 events needs further research. The unreviewed hazards are not certified accurate.

## People research

`history/sources/wikipedia_362_411_ce_people_links.json` contains 45 research leads, 27 qualified relationships and 41 event roles across 12 indexed IDs. They include Julian, Jovian and Shapur II; Mawiyya, Valens and Moses; opposing Fei River leaders; Chandragupta II and Prabhavatigupta; and Siyaj Kʼakʼ and associated Maya figures. Associations do not prove that every person was physically present at a particular event. This file is research-only and does **not** add spawnable VIPs or alternate-history behavior.

## Verification and rollback

- Staged both migrations before application. Canonical manifest hashes: context `fea5eb4d6c6f6cfd2c8ba5f8f6e157b7f51b95daa4410b814a9b7e21d22a05bc`; hazards `288fec5a58ff0e45c67ad5d1ccba260c44c5df2aa01e01dba0113a58a13d7e72`.
- Eleven batch tests and 19 resolver/pipeline tests passed. They include unique indexed after-images, tamper checks and dependency-aware in-memory reversal/reapplication of this and the preceding batch. Fifty-seven distinct Wikipedia revision/title pairs were checked through the API. These checks do not establish historical completeness or validate gameplay.
- Roll back later dependent batches first, then this batch's hazards before its context, using the matching guarded installers. Writes are atomic **per pack**, not across packs. Actual rollback and saved-world effects have not been tested.
- No live game, loader, save, full integrity check, Java probe or jar rebuild was performed. The existing jar remains stale. Natural VIP spawning, historical NPC behavior and player-triggered branching remain unimplemented or unvalidated. Earlier years are still incomplete.
