# R2 preliminary batch: 312–361 CE

Reviewed 30 October 2026. This is a preliminary pass, **not completion of the 50 years**.

## Coverage

- Resolved 50 distinct annual titles and archived their Wikipedia revisions in `year_titles_312_361_CE.json` and `year_wikitext_312_361_CE.json.gz`. Raw wikitext does not expand transclusions; a resolved title is not a collected history.
- Scanned 286 indexed event records whose start falls in the interval, including 46 in the hazard pack. Earlier-starting overlaps were not scanned. Only selected records and linked articles were reviewed; most remain unreviewed.
- The title inventory now contains 3,350 distinct resolved BCE/CE chronological titles. It measures title resolution, not partial work or completed years. The older 3,168 partly-worked figure remains unreconciled; **0 years are fully collected**.

## Indexed gameplay changes

Applied 16 guarded updates across four indexed packs, with stable IDs and before/after images in `reviews/312_361_ce_context_2026-10.json.gz`. Examples:

- Gupta origins precede Chandragupta I; his c.320 accession is not the dynasty's foundation. Samudragupta's accession and campaign chronology are approximate, as are Kadamba origins.
- Aksumite Christianization is not securely dated to 325, and the stored Arabian-coast coordinate was misplaced. Ezana's relationship to Kush is debated. These uncertain, overlapping political effects are retained as notes.
- Martin's Ligugé community was not founded as a Benedictine order in 360; Benedict lived later. The first Hagia Sophia and Old St. Peter's construction claims are qualified against linked articles.
- Magnentius's proclamation reference is corrected from the Netherlands to Autun. The linked Huai execution and Min succession occurred at different locations; one Mongolian point could not represent both.
- NOAA's Xihe `deathsAmountOrder=2` is a category, not exactly two deaths. Nicomedia and Dyrrachium quake details are qualified.

Moved 15 records from the active hazard pack to indexed, non-disruptive regional notes, preserving IDs and source evidence: nine radiocarbon/tephrochronology-dated eruptions, the questionable 315 Areopolis earthquake, and five disputed tsunami reports. NOAA's 315 Areopolis source associates its date with Valentinian and Valens; later research discusses possible 363/365 events. This pass does not automatically relocate the event. One NOAA 344 Dardanelles tsunami with validity -1 and many other hazards remain active and unreviewed; this batch does not certify them. Of the original 46 hazard records, 31 were not moved; two were modified in place, and the rest may still be inaccurate. One separately indexed 358 earthquake remains active.

Sources, pinned Wikipedia revisions, uncertainty and before/after images are in the manifests. Wikipedia is a starting source; source warnings and disputed interpretations do not become established fact merely because they are recorded.

## People research

`history/sources/wikipedia_312_361_ce_people_links.json` contains 35 research leads, 21 qualified relationships and 22 event roles across 11 indexed IDs. They include Constantine and Maxentius, Huai, Min and Liu Cong, Chandragupta and Samudragupta, Ezana and Frumentius, Martin and Hilary, and opposing commanders. Associations do not prove co-presence. The file is research-only; none of these records adds a naturally spawning VIP or implements alternate-history behavior.

## Verification and rollback

- Both migrations staged before application. Canonical manifest hashes: context `0363c764fcd3dfc081905da601d8732822121a22d89d1afa4bd00b9f92b5aa1e`; hazards `8c32f2610b5b8edd72da2148d5ff19a1dd8813957db4b18377a55a198b25907e`.
- 11 batch tests and 19 resolver/pipeline tests passed, including unique indexed after-images, tamper checks and dependency-aware in-memory reversal/reapplication with the preceding 262–311 batch. Fifty unique Wikipedia revision/title pairs were verified through the API. These checks do not establish factual completeness or prove in-game behavior.
- Roll back later dependent batches first, then this batch's hazards before context, using the matching guarded installers. Writes are atomic per pack, **not across packs**. Actual rollback and saved-world effects have not been tested.
- No live game, loader, save, full integrity check, Java probe or jar rebuild was performed. The existing jar remains stale. Natural VIP spawning, historical NPC behavior and player-triggered branching are not implemented or validated here. Earlier years also remain incomplete.
