# 562–611 CE — preliminary R2 research and gameplay-data pass

**Status: partial, not 50 completed years.** Fifty annual titles resolved to 50 distinct annual pages, and their pinned raw revisions were archived. Raw wikitext does not expand transclusions. The scan found **507 indexed records starting in the interval, including 31 hazards**; records beginning earlier but overlapping it were excluded. Only selected records and linked articles were reviewed.

## Indexed gameplay-data changes

- Applied **21 guarded updates and one addition** across three indexed packs. The added 610 cultural note records Muhammad's first revelation as an Islamic traditional account, with its disputed date and an approximate Hira mountain reference; it does not invent a precise day or claim all participants were at the cave.
- Extended the existing Pavia and Sirmium siege markers to include their final calendar years under the history gazetteer's exclusive-end convention. Sirmium's surrender may have occurred in late 581 or early 582; the separate 582 row is now a context note rather than another active siege. NewsIndex handles some pack boundaries differently and may display an extra year.
- The Year of the Elephant entries are now traditional, date-qualified context, rather than two certain, overlapping military or political effects. Dhu Qar's 609 military slot remains but is explicitly qualified: the article gives a range of possible dates, not a conflict lasting from 604 to 611. Catraeth's c.570/c.600 alternatives are a note. The Chronicle's Deorham account remains an approximate active battle marker.
- Corrected city references for Authari's succession at Pavia, the Tomis siege, Martyropolis, Terracina, and Japanese court events that had been placed near Vienna, central Iran, the central Balkans or China. These are proxies, not proof of exact event locations. Removed an unsupported certain accusation that Sui emperor Yang murdered his father, while retaining the 604 succession marker. The Anji Bridge dates are approximate context, not two political events.
- Moved **20 hazard rows to indexed non-damaging notes**, preserving IDs: 19 individually checked GVP volcanic episodes whose dates or occurrence are uncertain, and the traditional 589 Cucca flood/breach. The Cucca point was near Rhodes despite referring to Veneto; the note now uses a Veronella-area reference. The precise breach and its interpretation are debated, and the original 800 km damage circle is unsupported. Eleven scanned hazards were not moved and remain for review.

## People and relationships

`history/sources/wikipedia_562_611_ce_people_links.json` contains **66 research leads, 41 relationships and 36 event roles across 15 indexed IDs**. They include Muhammad's family and associates; South Arabian and Persian figures; Sui, Chen and Japanese figures; Lombard, Gepid, Avar and Byzantine figures; Sasanian and Armenian commanders; Kentish, Roman and Palenque figures. Relationships and roles may span different years and do **not** establish co-presence. These are research records, **not spawnable VIPs**, complete biographies or an alternate-timeline implementation.

## Evidence and files

- Annual title results: `year_titles_562_611_CE.json`; raw revisions: `year_wikitext_562_611_CE.json.gz`; starting-record inventory: `indexed_start_scan_562_611_CE.txt.gz`.
- Reversible manifests: `reviews/562_611_ce_context_2026-10.json.gz` (canonical SHA-256 `ce7d3eb1a3b20a795ca03a54795dc30421b612691a4b72003349032ac146a1dd`) and `reviews/562_611_ce_hazards_2026-10.json` (`029b0b37897ce8ef2db3173f2022db0487c33231adfa4255da75e8d143999b1b`).
- Examples: [Muhammad's first revelation](https://en.wikipedia.org/wiki/Muhammad%27s_first_revelation), [Year of the Elephant](https://en.wikipedia.org/wiki/Year_of_the_Elephant), [Siege of Sirmium](https://en.wikipedia.org/wiki/Siege_of_Sirmium), [Battle of Catraeth](https://en.wikipedia.org/wiki/Battle_of_Catraeth), [Breach at Cucca](https://en.wikipedia.org/wiki/Breach_at_Cucca), [GVP Chokaisan](https://volcano.si.edu/volcano.cfm?vn=283220), and [GVP Akan](https://volcano.si.edu/volcano.cfm?vn=285070). The manifests contain pinned Wikipedia revisions and individual GVP links.

## Verification and remaining work

Both layers were staged and applied. **11 batch tests and 19 resolver/scope/pipeline tests passed**, including dependency-ordered in-memory reversal/reapply of this and the preceding batch. **87 Wikipedia revision/title pairs** in the context, hazard and people files matched the API. Actual disk rollback and saved-world effects were not tested for this batch.

Reverse later dependent batches first, then `python r2_wikipedia/apply_562_611_ce_hazards.py rollback` followed by `python r2_wikipedia/apply_562_611_ce_context.py rollback`. Writes are atomic **per pack**, not across all packs.

Many of the 507 scanned rows remain unreviewed; uncertain or mislocated events in prior intervals also remain. No live game, loader, save, full integrity check, current Java probe or jar rebuild was performed. The jar is stale; natural VIP spawning, historical VIP behavior and player-triggered branching remain unimplemented.

## Overall progress

The title inventory finds **3,600 distinct resolved chronological titles** (2,989 BCE and 611 CE). This is title resolution, not collected history or a complete count of partly worked years. The legacy **3,168 partly worked** figure remains unreconciled. **Fully collected years: 0.** Earlier periods remain incomplete; the next preliminary interval is 612–661 CE.
