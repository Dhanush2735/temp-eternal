# Preliminary batch: 62–111 CE

**Status: partly worked; 0 fully collected years.** This batch covers 50 consecutive historical years. Previously sampled 71, 81 and 91 CE overlap this interval, so it must not simply be added to the old partly-worked total. That 3,168 total remains unreconciled; a reliable aggregate of partly worked years is not yet available.

## Sources and scope

All 50 chronological `N (year)` titles redirected to 50 distinct annual pages, `AD 62` through `AD 111`, none marked as disambiguation. The resolved titles and pinned raw revisions are archived in `year_titles_62_111_CE.json` and `year_wikitext_62_111_CE.json.gz`; transclusions are not expanded. Selected annual sections and linked articles were consulted, but **resolving or archiving a year page does not mean reading all its linked articles or completing that year**.

A reproducible inventory of existing title-result files now finds **3,100 distinct resolved chronological titles**: 2,989 BCE titles and 111 CE titles. That is neither a completed-year count nor a count of fully reviewed years. Separate evidence for 3000–2990 BCE exists outside that title-file inventory.

An indexed-data scan found **302 rows starting in 62–111 CE**, including 47 hazards; earlier-starting overlaps were excluded and most candidates were not individually reviewed. The scan is preserved in `indexed_start_scan_62_111_CE.txt.gz`.

## Indexed gameplay data

Fourteen guarded existing-row updates were applied across three indexed packs:

- The annual Masada siege row incorrectly pointed to **Rome**; it now points to Masada as context. The separate siege record remains active with its disputed dates noted: traditional late 72–early 73 versus a proposed late 73–early 74. Josephus is the sole contemporary written source. The active row remains anchored to the traditional date; it does not simulate both alternatives.
- The Colosseum's 72 CE construction row was incorrectly classified as a military battle. It is now a cultural note about construction through 80; the data does not build the amphitheatre.
- The First and Second Battles of Tapae are **different events**, not duplicates. Wikidata identifies the former with Fuscus and dates it 87; the English second-battle article dates the former to 86 and the latter to 88. Both existing battle effects remain active, with the first date uncertainty and names clarified.
- The combined Bedriacum row is now context so it does not add a third military effect on top of the separately indexed first and second battles. This does not remove the two historical engagements.
- Emperor He's death and infant Emperor Shang's accession were corrected from 105 to **106**, and Emperor An's accession from 107 to **106**. Deng Sui is Shang's stepmother and regent, not his documented biological mother. Luoyang is a capital-level marker, not an exact ceremony or death site.
- Trajan's Bridge construction was corrected to 103–105 and its erroneous central-Serbia coordinate moved to the Danube bridge site. The separate completion row remains a note. White Horse Temple's 68 CE foundation is explicitly described as tradition, not a proven first introduction of Buddhism to all China. The 74 CE 'last cuneiform' claim is qualified against a broader approximately 100 CE overview.
- The 62 Pompeii earthquake record now notes the **62 versus 63** year discrepancy. Its existing game effect remains active; its radius is unverified. The 79 Vesuvius eruption remains active, with its disputed day and uncertain precise cause of Pliny the Elder's death no longer asserted as fixed facts.

## Hazards and prehistoric misdate

Eleven hazards were moved to non-damaging regional notes while retaining their original IDs:

- Smithsonian GVP confirms the White River Ash northern-lobe Churchill eruption but dates it **63 CE ±200 years** using uncalibrated radiocarbon; that is not an exact 63 CE damaging event.
- NOAA's Crete earthquake and sea-withdrawal records are linked and have conflicting dates and interpretations. NOAA's Lycia earthquake and sea-wave accounts are also linked and question the earthquake and/or tsunami interpretation. These notes do **not** claim such events could not have occurred.
- Two Korean earthquake titles wrongly turned NOAA's `deathsAmountOrder=3` into exactly **three deaths**. It is an order-of-magnitude category, not an exact casualty count; NOAA flags relevant epicenter or magnitude checks. The revised notes make no precise death-count claim.
- NOAA links the 79 Naples earthquake, sea disturbance and Vesuvius eruption. Two additional earthquake/wave effects were converted to context rather than independently stacking uncertain footprints and shared death totals; the separately indexed eruption effect remains active.
- NOAA's linked Sevastopol Bay earthquake and tsunami reports refer to an uncertain early-second-century event, possibly 103. Sources disagree about the wave and its intensity; neither note asserts an exact date or uniform damage radius.

One additional row, `hz_f23b68d313`, had placed the **Chicxulub impact in 66 CE**. The impact occurred about 66 million years ago. It is now non-indexed research, with the complete original before-image and source retained in `history/sources/geologic_misdates_62_111_ce.json`.

**35 of the original 47 scanned hazard rows were not moved or quarantined by this pass** and may remain active and unreviewed. The 76 CE Cyprus earthquake and tsunami, among others, still need individual assessment. No hazard model or affected radius has been validated in a live game.

## Connected people

`history/sources/wikipedia_62_111_ce_people_links.json` contains **37 research references, 18 qualified relationships and 51 event roles across 16 existing indexed IDs**. It includes figures on opposing sides of Bedriacum, Masada, Jerusalem and Tapae; Roman, Han and Batavian participants; and writers associated with the Pompeii earthquake and Vesuvius eruption. It distinguishes witnesses from later narrators, and patrons from architects. Some links resolve to group or annual pages rather than individual biographies; exact identity, role and presence remain to be verified. These references are **not spawnable VIPs** and do not implement alternate-history behavior.

## Checks and rollback

- Context manifest canonical SHA-256: `f2c24895c734fe8a395543addd63fe4b80c0d15080f6d6a0487ea6fb0590915c`; hazard moves: `c204cae5b70c3b945873599b5634e46753e9affa122e239516c8cc5bcce806c9`; geological quarantine: `9d1b94f5b947d3ddb308a9d7bf39d596a3d518e51eb7d9693d9df9f3e348ce88`.
- All three installers were staged before application. **12 Python tests passed after application**, including checks of 25 unique indexed after-images and dependency-ordered in-memory logical reversal/reapplication. One first run failed because the test demanded the literal word “category” in both differently worded notes; the assertion was corrected to check the actual NOAA field, then all passed. No game data was changed to make the test pass.
- Reverse **geological quarantine, then hazard moves, then context updates**, before earlier dependent shared-pack installers. Writes are atomic per pack, not across packs. Actual rollback writes, loader, save and live-world behavior were not tested.
- Storage was reclaimed by formatting canonical-hash-locked manifests without changing their parsed data or validation results; raw byte hashes and limited reference-scan caveats are recorded in `storage_compaction_62_111_CE.md` and its supplement. The short progress ledger's redundant older sections were removed only after confirming each is retained verbatim in `progress_before_39_1_BCE.md.xz`. Storage remains close to the snapshot limit.
- No full integrity check, Java probe, live game or rebuilt jar. The jar is stale. Natural VIP spawning, historical VIP behavior, and player-triggered branching remain unimplemented. Pack-specific NewsIndex end boundaries and the internal year-zero transition remain unresolved.

Sources include [Masada](https://en.wikipedia.org/wiki/Siege_of_Masada), [Bedriacum](https://en.wikipedia.org/wiki/Battle_of_Bedriacum), [first Tapae Wikidata entity](https://www.wikidata.org/wiki/Q1476280), [second Tapae](https://en.wikipedia.org/wiki/Second_Battle_of_Tapae), [Shang of Han](https://en.wikipedia.org/wiki/Emperor_Shang_of_Han), [Trajan's Bridge](https://en.wikipedia.org/w/index.php?title=Trajan%27s_Bridge&oldid=1359411915), [Pompeii earthquake](https://en.wikipedia.org/wiki/AD_62_Pompeii_earthquake), [Vesuvius](https://en.wikipedia.org/w/index.php?title=Eruption_of_Mount_Vesuvius_in_79_AD&oldid=1381093639), [GVP Churchill](https://volcano.si.edu/volcano.cfm?vn=315030), [NOAA Crete](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/5880), [NOAA Lycia](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/10540), [NOAA Kyongju](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/62), [NOAA tsunami 2284](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events/2284), and [Chicxulub crater](https://en.wikipedia.org/wiki/Chicxulub_crater). Additional evidence and review caveats are preserved in the manifests.

**Next:** 112–161 CE, while earlier years remain incomplete and the unresolved distinct-year coverage inventory, hazard review and workspace capacity are addressed.
