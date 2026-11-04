# 889–840 BCE: preliminary R2 collection

**Progress: 2,448 years partly worked, 0 fully collected.** This adds 45 to 2,403 because five decade endpoints were already counted. This is a shared-period convention, not 2,448 independently researched annual histories; earlier years remain incomplete.

## Sources checked

All 50 year titles resolved to five decade pages: [880s](https://en.wikipedia.org/w/index.php?title=880s_BC&oldid=1357668070), [870s](https://en.wikipedia.org/w/index.php?title=870s_BC&oldid=1252622878), [860s](https://en.wikipedia.org/w/index.php?title=860s_BC&oldid=1357668084), [850s](https://en.wikipedia.org/w/index.php?title=850s_BC&oldid=1249375486) and [840s](https://en.wikipedia.org/w/index.php?title=840s_BC&oldid=1306362370). See `year_titles_889_840.json`. Selected linked articles were reviewed, not the whole worldwide linked graph. Redirect resolution is not completion.

## Indexed gameplay data

Four existing records were updated and two contextual notes added, all in the indexed regional pack. Their stable existing IDs and earlier evidence are retained. They are notes, not new military or destructive triggers; runtime behavior has not been tested.

- `wpr_b6ca1e1770`: qualifies Ashurnasirpal II's death and Shalmaneser III's accession around 859/858. [Shalmaneser's biography](https://en.wikipedia.org/w/index.php?title=Shalmaneser_III&oldid=1358896149) distinguishes his accession year from a first full regnal year beginning in 858. Another accession note may duplicate it.
- `wpr_1535a222d2`: retains the decade's 859 claim about attacks in Syria and Israel as an uncertain claim. The biography and [Qarqar article](https://en.wikipedia.org/w/index.php?title=Battle_of_Qarqar&oldid=1376483973) do not establish a separate 859 attack on Israel. The inherited regional pin is not an exact campaign route.
- `q849474`: enriches Qarqar with attribution to the [Kurkh stele](https://en.wikipedia.org/w/index.php?title=Kurkh_Monoliths&oldid=1345768190), coalition and disputed outcome. Inscriptional numbers and identifications are claims; personal attendance is not established. `wpy_db249d8984` may duplicate it and remains untouched. The battle article gives 854/853 or 853; the selected slot is not an exact date.
- `r2_gonghe_840_context`: adds [Gonghe](https://en.wikipedia.org/w/index.php?title=Gonghe_Regency&oldid=1378692824) and [He of Gong](https://en.wikipedia.org/w/index.php?title=He,_Earl_of_Gong&oldid=1382069317) evidence. The Bamboo Annals/Xinian interpretation differs from Sima Qian's account of two dukes; rebellion and regency dating remain qualified.
- `r2_parshvanatha_877_tradition`: adds a non-destructive Jain birth-tradition note. The decade says 877, whereas [Pārśvanātha's biography](https://en.wikipedia.org/w/index.php?title=P%C4%81r%C5%9Bvan%C4%81tha&oldid=1381017851) gives c.872 in its infobox and distinguishes traditional 9th–8th-century dating from scholarly 8th–7th-century estimates. Varanasi is a traditional regional reference, not proof of birth in 877. An existing c.772 nirvana note concerns a different traditional life event.
- `r2_babylon_revolt_851_context`: adds a non-destructive contextual note for the conflict of Babylonian king Marduk-zakir-shumi I and his brother Marduk-bel-usati and Assyrian intervention in 851–850, as recounted in [the king's biography](https://en.wikipedia.org/w/index.php?title=Marduk-zakir-shumi_I&oldid=1358813361). Assyrian accounts are royal claims. The Babylon-area coordinate and 851 slot are reference anchors, not the exact battle site or duration.

Existing Til Barsip notes retain the disagreement between the decade's 865/Ashurnasirpal attribution and the [site article's](https://en.wikipedia.org/w/index.php?title=Til_Barsip&oldid=1375018728) 856/Shalmaneser attribution. The inclusive indexed overlap scan found 56 rows: 35 regional, 13 Wikipedia and eight decade rows; zero were in the hazard pack. Regional volcanic context exists, so this does not mean there were no hazards.

## People research

`eternal/src/main/resources/data/eternalengine/eternal/history/sources/wikipedia_889_840_people_links.json` has 29 selected people/figure references, 31 qualified relationships and 22 roles across five indexed event IDs. It includes coalition members and family, Babylonian opponents and associates, Zhou leadership interpretations, and Pārśvanātha's traditional relatives and disciples. Jain sect accounts and historical dating are distinguished; some people have shared source articles rather than verified individual biographies. Roles denote relevance, not proof of presence. Structural references and event-ID existence were checked, not every identity or claim. The graph is research-only, **not spawnable**. Natural VIP spawning and alternate-timeline branching remain unimplemented.

## Validation and rollback

`reviews/889_840_bce_context_2026-10.json.gz` canonical SHA-256: `b51ec3e9b2d6f8e8c5d15171c11aad8f51df0abff57cc39344f73cb0ec1bba04`. Sixteen targeted tests passed before and after applying; the guarded stage checked reversibility and six unique indexed after-images were verified. This batch changes one pack and the installer writes atomically per pack. Before rolling back `apply_850_810_context.py`, roll back `apply_889_840_bce_context.py`: that older manifest's Qarqar move and Gonghe addition after-images match this batch's before-images. Compatibility with every older installer was not established.

Twelve old guarded manifests were formatting-compacted; original/new raw and invariant canonical hashes and limitations are in `storage_compaction_889_840.md` and `storage_compaction_889_840_extra.md`. Earlier interrupted-compaction raw-hash and review-date provenance caveats remain. The crawler is storage-blocked and the jar is stale. No full-integrity, Java probe, live loader, Minecraft or saved-world test was performed. Continue at 839 BCE while earlier ranges remain incomplete.
