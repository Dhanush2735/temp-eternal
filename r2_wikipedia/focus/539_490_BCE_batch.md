# 539–490 BCE: preliminary R2 batch

**Status: partly worked, not fully collected.** Resolved 50 year titles: six redirect to decade pages and 44 have individual pages. Archived 44 exact-revision annual wikitexts in `year_wikitext_539_490.json.gz`; transclusions are unexpanded. Read five decade pages and selected linked articles, not the full linked chain. An indexed scan found 208 rows whose start is in this range; most remain individually unreviewed. Additional relevant rows outside that start range may exist.

## Indexed gameplay data

Applied **34 guarded updates in five indexed packs** and **two moves from the active hazard pack to regional notes**, retaining IDs. Examples:

- Corrected the start years of Opis (539), Pelusium (525), Sardis (498) and Lade (494) to the linked articles' BCE years. Distinguished the 539 entry into Babylon from a battle there. The world-pack NewsIndex's inclusive end can still display an extra year; HistoryGazetteer uses an exclusive end. This has not been tested in a live game.
- Corrected the location of the Boju battle reference from Ying to the broader Macheng area, not a precisely known battlefield; retained an active battle and converted the overlapping narrative to a note. Sun Tzu's role appears in the later Shiji but is absent from earlier Zuo Zhuan. Moved the Sungai Batu site reference to Kedah and qualified its disputed BCE/CE dates. Corrected other references for Pelusium, Bodh Gaya, the Indus region and Suzhou.
- Distinguished the 499 Naxos expedition from the 490 siege, qualified the regional Ionian Revolt and first Persian invasion, and separated Mardonius's 492 campaign from Marathon in 490. Some records were changed to contextual notes rather than suggesting continuous localized military presence. Other semantic duplicates may remain.
- Qualified Second Temple completion dates, return-from-exile narratives, the claim that the Cyrus Cylinder describes a Judean return, the identity of Bardiya versus the alleged impostor Gaumata, Ajatashatru's competing chronologies, and the traditional/legendary Lake Regillus battle. Reference years in the game do not prove precise dates. Alalia's two inherited overlapping entries were distinguished as event and contextual note; full deduplication remains undone.
- The 525 BCE Lebanon earthquake and tsunami reports were moved out of the hazard pack into notes. Salamon et al.'s catalog supplement says ancient sources for the earthquake report could not be traced and notes a deformed layer dated to 525; its tsunami table calls the sea-wave report doubtful. Neither conclusion proves that no earthquake or wave occurred. Exact time, intensity and inherited disruption radii remain unsupported.

## Linked people for later R3 work

`eternal/src/main/resources/data/eternalengine/eternal/history/sources/wikipedia_539_490_people_links.json` holds **47 research references, 32 qualified relationships and 54 event roles across 18 indexed event IDs**. Multiple figures are recorded for Opis, Boju, Sardis, Lade and Marathon; two different men named Artaphernes are kept separate. Some roles come from later traditional sources or an article infobox, and presence, identities and chronology require further verification. These records are **not spawnable VIPs**. Natural VIP spawning and alternate-history behavior were not implemented.

## Sources and interpretation

- [Opis](https://en.wikipedia.org/w/index.php?title=Battle_of_Opis&oldid=1378908453), [Fall of Babylon](https://en.wikipedia.org/w/index.php?title=Fall_of_Babylon&oldid=1381909825), [Cyrus Cylinder](https://en.wikipedia.org/w/index.php?title=Cyrus_Cylinder&oldid=1379910384), [Pelusium](https://en.wikipedia.org/w/index.php?title=Battle_of_Pelusium&oldid=1381256774).
- [Boju](https://en.wikipedia.org/w/index.php?title=Battle_of_Boju&oldid=1378908918), [Macheng](https://en.wikipedia.org/w/index.php?title=Macheng&oldid=1376439912), [Sungai Batu](https://en.wikipedia.org/w/index.php?title=Sungai_Batu&oldid=1365395668), [Second Temple](https://en.wikipedia.org/w/index.php?title=Second_Temple&oldid=1382085805), [Bardiya](https://en.wikipedia.org/w/index.php?title=Bardiya&oldid=1376018932), [Ajatashatru](https://en.wikipedia.org/w/index.php?title=Ajatashatru&oldid=1379309650).
- [Ionian Revolt](https://en.wikipedia.org/w/index.php?title=Ionian_Revolt&oldid=1380751380), [Sardis](https://en.wikipedia.org/w/index.php?title=Siege_of_Sardis_(498_BC)&oldid=1370745080), [Lade](https://en.wikipedia.org/w/index.php?title=Battle_of_Lade&oldid=1376435907), [first Persian invasion](https://en.wikipedia.org/w/index.php?title=First_Persian_invasion_of_Greece&oldid=1381274426), [Marathon](https://en.wikipedia.org/w/index.php?title=Battle_of_Marathon&oldid=1380768828), [Lake Regillus](https://en.wikipedia.org/w/index.php?title=Battle_of_Lake_Regillus&oldid=1378105313).
- [Salamon et al. electronic supplement, Table 2 and Appendix 2](https://www.seismosoc.org/Publications/BSSA_html/bssa_97-3/06147-esupp/). Each gameplay update has its own source links and qualifications. A Wikipedia revision preserves what was consulted; it is not independent verification. BCE numbers follow the project's negative-number convention, not astronomical year numbering.

## Validation and rollback

- Context manifest canonical SHA-256: `ebc361c8909d1f978ef58934911436e423e256f061c34f28f4196c84e81c7451`. Hazard manifest: `07648ffc401ec1416e7f8b9ef0825487ba0fcd5b27133aa8518f29ced9ccaa8e`.
- Staged and applied both; **19 context and 11 hazard unit tests passed before and after**. Verified 36 exact after-images and dependency-ordered in-memory rollback/reapplication of six pack objects. During development an earlier 33-update revision and its hazards were actually rolled back before the final 34-update revision was staged and applied. Writes are atomic per pack, not across packs.
- Undo the final installation with `python r2_wikipedia/apply_539_490_bce_hazards.py rollback` **before** `python r2_wikipedia/apply_539_490_bce_context.py rollback`. Reverse newer hazard moves before older 589–540 and earlier hazard installers. No matching update IDs were found in the scanned older review manifests, including `500_460`, but shared packs and semantic overlap still require care; this is not proof of independence.
- No live game, loader, save, rebuilt jar, Java probe or full integrity test was run; the earlier jar is stale. Existing endpoint-display and save effects remain unverified. Natural spawning and branching are not implemented.
- To preserve snapshot headroom, the earlier Gandhi saved wikitext was compressed losslessly; restoration and hashes are recorded in `focus/gandhi_project_details.md`.

## Progress

Under the existing shared-period counting convention, five previously counted endpoints overlap: **2,763 years partly worked, 0 fully collected**. This is not a completeness percentage or proof of independent annual histories. Next chronological window: **489–440 BCE**, while earlier windows remain incomplete.
