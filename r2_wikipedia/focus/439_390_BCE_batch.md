# 439–390 BCE: preliminary R2 Wikipedia pass

**Status: partly worked, not fully collected.** Fifty individual year titles resolved without redirects or missing pages. Their annual revision wikitext is in `year_wikitext_439_390.json.gz`, with transclusions unexpanded; titles are in `year_titles_439_390.json`. Five decade pages and selected linked articles were partly reviewed, not all links or article references. A scan found 262 indexed rows whose starts fall in this interval; most were not individually reviewed, and the scan excludes rows starting earlier. This is not a worldwide annual history or completeness claim.

## Gameplay JSON changes

Nineteen guarded updates across four indexed packs (`reviews/439_390_bce_context_2026-10.json.gz`, canonical SHA-256 `b873f08b327718aeca729ec331559ed9a05bbe1cf58423a53af10e3a0c0a1d4e`):

- Corrected the one-year-later start of 13 existing world battle/siege rows to the years given by their linked articles: Spartolos 429, Olpae 426, Sphacteria 425, Delium 424, Mantinea 418, Melos 416, Selinus and Himera 409, Gela 405, Motya 398, and Cnidus, Nemea and Coronea 394 BCE. Stable IDs and military effects were kept. These changes do not independently establish exact days, troop strengths or affected footprints.
- Replaced the broad continuous Peloponnesian War military-presence footprint with a regional context note; existing battle events remain. Corrected the Socrates trial city reference from Boeotia to Athens, not a verified exact courtroom. Distinguished the Parthenon's building completion/dedication in 438 from decoration continuing to 432, while acknowledging that the article infobox says 432. Qualified the Sicilian expedition and moved its Demosthenes reinforcement context from 414 to 413 BCE.
- Converted an extra 425 BCE world lockdown row to a 426 BCE contextual report of the Malian Gulf earthquake/tsunami sequence. The existing earthquake and tsunami hazard rows remain. They may reflect the same sequence, not independent disasters. Casualty, magnitude, exact date and radius estimates are uncertain; the remaining active hazard parameters have **not** been validated.

Two hazard-to-regional-note moves (`reviews/439_390_bce_hazards_2026-10.json`, canonical SHA-256 `16dbff275d9c34ec702e048e98b439bcc2a08dd4b389692bce5a5768c3a81e5d`):

- NOAA earthquake event 18 is dated 432 **or 431** BCE and has an uncertain location and an anachronistic “Roman territories” label. A precise damaging footprint is not established. The move does not mean there was no earthquake.
- GVP classifies Corbetti's Wendo Koshe Younger Pumice eruption as confirmed, VEI 5, about 396 BCE **±38 years**, with calibrated radiocarbon dating. This supports an eruption, not an exact single-year damaging trigger or the modeled 40 km footprint.

Source URLs and qualification, complete before/after records and original IDs are in the manifests. Selected references: [GVP Corbetti](https://volcano.si.edu/volcano.cfm?vn=221290&vtab=Eruptions), [NOAA earthquake event 18](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/18), [NOAA Malian Gulf tsunami event 10](https://www.ngdc.noaa.gov/hazel/view/hazards/tsunami/event-more-info/10), [Wikipedia tsunami revision](https://en.wikipedia.org/w/index.php?title=426_BC_Malian_Gulf_tsunami&oldid=1366274942), [trial revision](https://en.wikipedia.org/w/index.php?title=Trial_of_Socrates&oldid=1377883389), [Parthenon revision](https://en.wikipedia.org/w/index.php?title=Parthenon&oldid=1381069514), and [expedition revision](https://en.wikipedia.org/w/index.php?title=Sicilian_Expedition&oldid=1377036788). Existing Etna eruption rows at 425 and 396 BCE remain active and their modeled footprints unverified. World-pack NewsIndex treats the stored end as inclusive, while the gazetteer uses an exclusive end, so a corrected one-year world event may display in an extra year.

## People for later R3 work

`sources/wikipedia_439_390_people_links.json` contains 42 research references, 19 qualified relations and 48 role links to 16 indexed IDs. It includes opposing commanders, accusers, authors, architects and others; identical names and disputed roles require further checking. The graph contains source links but is not a complete biography crawl or identity certification. The entries are **not spawnable VIPs**, and source authors are not assumed physically present at events.

## Verification and rollback

Fourteen context and eleven hazard tests passed after context staging/before its apply and after both applies (the combined suite was also run before hazard apply). Twenty-one exact installed after-images and five entire pack objects were checked by logical in-memory rollback and reapplication in dependency order. This is not a live game or save test. Installers write atomically **per pack**, not as a cross-pack transaction. To reverse, run `apply_439_390_bce_hazards.py rollback` before `apply_439_390_bce_context.py rollback`, and reverse this batch before older installers affecting shared packs. Check guards and dependent later batches first.

The previous jar is stale. No recent rebuilt jar, live Minecraft, loader, save, full integrity test or Java probe was run. Natural VIP spawning and alternate-history behavior remain unimplemented. Three old unreviewed scan files were losslessly compressed; byte hashes, exact restoration and dependency limitations are in `storage_compaction_439_390.md`.

## Progress

Under the existing five-shared-endpoint convention, this batch adds 45 to the ledger: **2,853 years partly worked; 0 fully collected**. This is not a percentage or a count of independent complete annual histories. Earlier periods, the unreviewed rows, linked pages and worldwide coverage remain unfinished. Continue with 389–340 BCE when requested.
