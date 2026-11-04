# Preliminary batch: 112–161 CE

**Status: partly worked; 0 fully collected years.** This pass covers 50 consecutive years, but existing partial work overlaps this range and the old aggregate of 3,168 partly worked years is unreconciled. It would be misleading to add 50 to it.

## Sources and coverage

The 50 chronological year titles resolved to 50 distinct annual pages. Their titles, revision IDs and raw wikitext are archived in `year_titles_112_161_CE.json` and `year_wikitext_112_161_CE.json.gz`. Raw revisions do not expand transclusions. Only selected year sections and linked articles have been examined; neither a resolved title nor an archived page means a year is fully collected.

The recorded title-file inventory now finds **3,150 distinct chronological title resolutions**: 2,989 BCE and 161 CE. This is not a count of completed or even individually reviewed years. Separate evidence for 3000–2990 BCE exists outside those title files.

`indexed_start_scan_112_161_CE.txt.gz` preserves a scan of **222 indexed records starting in the interval, including 39 hazards**. Earlier-starting overlaps were not included; most of those 222 records remain unreviewed.

## Changes to indexed gameplay data

Seventeen guarded existing-row updates were staged and applied across four indexed packs, with stable IDs and full before/after images:

- The Betar siege row previously represented the entire 132–135 revolt as a continuous siege. The linked article dates Betar's fall to 135, but does not establish that the siege began in 132. The active event is anchored to 135; the earlier starting date remains uncertain. Pack-specific end-boundary behavior is still unresolved.
- The 139 Mcurn earthquake account has uncertain date and location: sources differ between Mcurn and Nisibis and may draw on later traditions. Its precise-site automatic lockdown was replaced by a contextual note. Burnswark's approximately 140 date and the archaeological interpretation of its Roman assault were qualified; its existing military effect remains.
- Roman Syria was already a province from 64 BCE. The 116 entry no longer asserts that Trajan first made it a province. For Ctesiphon, the 115 annual page and the campaign article's detailed 116 narrative conflict; the existing 115 reference remains with uncertainty, not a definitive chronological resolution.
- Nahapana and Gautamiputra's relative reign and conflict dates have competing interpretations, including a proposed c.124 victory and proposals decades earlier. The 119, 124 and 125 entries are now qualified regional notes; the sources do not establish that Nahapana died at the stored battlefield point.
- Jerusalem's control during the Bar Kokhba revolt is disputed. The row asserting a rebel occupation, renewed sacrifices, and total destruction of a legion was changed to a qualified note and its incorrect Masada coordinate moved to a Jerusalem regional reference. The Aelia Capitolina chronology is also qualified.
- Vologases IV's accession was separated from Mithridates V's 140 end: the linked biography places Vologases IV's succession in 147. A row that placed Pacorus II's death in 147 was corrected to the biography's 110 chronology, with a Ctesiphon-area reference instead of its previous Kabul-area coordinate.
- The Hadrianic Pantheon's construction date is uncertain and c.126 may be a dedication, not a proven demolition and start date. The Antioch earthquake's very large death estimates are not an exact known total.
- Three Chinese earthquake titles had converted NOAA's categorical `deathsAmountOrder` values into exact totals. The labels now avoid invented death counts. The original disruptive earthquake effects remain, with epicentre, magnitude and area explicitly uncertain.

Thirteen hazardous rows were moved with their original IDs to indexed regional **notes**, avoiding a definite damaging effect when the linked source does not justify one:

- GVP's San Martín date is **120 CE ±200 years**, Mílos **140 ±300**, Izu-Oshima O2 **150 ±50**, and Liamuiga tephra unit F **160 ±200**. Fournaise 120, Pelée 130, Masaya 150 and two distinct Ata tephra entries 130 and 150 are marked uncertain by GVP. Confirmed eruption does not mean a confirmed exact year. The two Ata entries remain separate.
- NOAA's early-second-century Bithynia earthquake and Marmara sea-wave records have differing date interpretations; the original earthquake title also treated a deaths category as exactly three deaths. The Kyongju water report is linked to the earthquake and NOAA lists the sea-wave record with `eventValidity=0` and `oceanicTsunami=false`. The 142 Rhodes sea wave is linked to the earthquake and has alternative dating in NOAA's comments. These moves preserve the reports, not a claim that no earthquake or wave occurred. The 123 Kyongju and 142 Rhodes earthquake effects remain active.

**26 of the original 39 hazard rows were not moved**; three were modified in place as above, and many of the remainder are unreviewed. In-game footprint and severity have not been validated.

## Connected people

`history/sources/wikipedia_112_161_ce_people_links.json` records **33 research references, 15 qualified relationships and 38 event roles across 15 existing event IDs**. These include opposing Roman and Parthian figures, Bar Kokhba and Roman figures, Gautamiputra and Nahapana, and Han succession figures. A role in a broader campaign does not establish simultaneous physical presence. These are research leads, **not spawnable VIPs**, and do not implement historical or alternate-history NPC behavior.

## Checks, rollback and limits

- Context manifest canonical SHA-256: `4ff87f52a97b1e0f70ecb8f0e029089ed1b7059cc0d52876e878417b671ea991`; hazard manifest: `e49746560f3843e194a1ac3d647d04b2be1e8e6a6eae90904ab9fa64f39077b8`.
- Both installers were staged before application. **12 batch tests passed**, including unique after-images, tamper rejection, graph references, and in-memory rollback/reapplication. The previous 62–111 batch's in-memory roundtrip also passed after first reversing this later dependent batch in memory. Thirteen crawler/pipeline and compaction tests passed separately.
- A combined old-test run was stopped after timing out in the older roundtrip: it attempts to restore source-array indices without first reversing newer hazard moves and can generate a huge ordering diff. Do not run older rollback tests as if later shared-pack migrations did not exist. The dependency-aware test above covers the 62–111 case; it does not replace an actual disk rollback or saved-world test.
- Roll back **112–161 hazard moves, then 112–161 context updates**, before rolling back 62–111 quarantine, hazards and context, then earlier dependent changes. Writes are atomic per pack, not across packs; staged outputs and in-memory reversals are not a multi-pack transaction.
- The crawler database index was compacted with logical table fingerprints, foreign keys, SQLite integrity and sampled scheduler selections verified; 1,298,432 bytes were saved. `frontier_index_compaction_112_CE.json` records the operation. Sorting title ties may cost more; the crawler's storage guard can still block collection. OS free space is not equivalent to the workspace snapshot allowance.
- No live game, loader, save, full integrity check, Java probe or jar rebuild was performed. The jar remains stale. VIP natural spawning, historic NPC behavior and branching are unimplemented. Year-zero and pack-specific date boundaries remain unresolved.
- Remaining leads include the Dura-Europos 160 earthquake's unverified effect radius; numerous active radiocarbon-dated volcanic rows; and Han chronology rows using questionable capital locations (for example the 145 succession row points near Xi'an rather than Eastern Han Luoyang). The 119 Britain visit row also needs chronological investigation. These are not silently counted as fixed.

Key linked sources: [Betar](https://en.wikipedia.org/w/index.php?title=Betar_%28ancient_city%29&oldid=1375587136), [Bar Kokhba revolt](https://en.wikipedia.org/w/index.php?title=Bar_Kokhba_Revolt&oldid=1382252578), [Trajan's campaign](https://en.wikipedia.org/w/index.php?title=Trajan%27s_Parthian_campaign&oldid=1381076297), [Roman Syria](https://en.wikipedia.org/w/index.php?title=Roman_Syria&oldid=1381396762), [Gautamiputra](https://en.wikipedia.org/w/index.php?title=Gautamiputra_Satakarni&oldid=1378680869), [Nahapana](https://en.wikipedia.org/w/index.php?title=Nahapana&oldid=1358597747), [Vologases IV](https://en.wikipedia.org/w/index.php?title=Vologases_IV&oldid=1379359783), [Pantheon](https://en.wikipedia.org/w/index.php?title=Pantheon%2C_Rome&oldid=1381420787), [GVP Mílos](https://volcano.si.edu/volcano.cfm?vn=212030), [GVP Izu-Oshima](https://volcano.si.edu/volcano.cfm?vn=284010), [NOAA Bithynia](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/9969), [NOAA Kyongju sea-wave record](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/tsunamis/events/3583), and [NOAA Rhodes](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/5883). Specific review sources and exact before/after images are preserved in the manifests.

**Next:** preliminary 162–211 CE, while the earlier centuries and linked articles remain incomplete; address storage constraints and the unreviewed leads rather than treating title resolution as completion.
