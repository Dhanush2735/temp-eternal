# 989–940 BCE: preliminary R2 collection

**Progress:** 2,358 years partly worked, **0 fully collected**. This adds 45 to 2,313 because five decade endpoints were already counted. The convention counts years sharing a researched period; it does **not** mean each has its own researched history or that all links have been followed. Earlier years remain incomplete.

## What was checked

All 50 year titles resolve to five shared decade pages, not independent year articles: [980s](https://en.wikipedia.org/w/index.php?title=980s_BC&oldid=1346076775), [970s](https://en.wikipedia.org/w/index.php?title=970s_BC&oldid=1361566608), [960s](https://en.wikipedia.org/w/index.php?title=960s_BC&oldid=1368386374), [950s](https://en.wikipedia.org/w/index.php?title=950s_BC&oldid=1353805969), and [940s](https://en.wikipedia.org/w/index.php?title=940s_BC&oldid=1353805117). Title results and target revisions: `year_titles_989_940.json`. Selected linked articles and biographies were read; this is not the whole worldwide linked graph. Some sources conflict, contain red links, or mix traditions with historical reconstruction.

## Implemented in indexed game history

- **Solomon and Adonijah:** Updated existing accession note `wpd_5fb4cb75a0` rather than duplicating it. The displayed name now identifies the rival succession account, and additional evidence explains the roles of Bathsheba, Nathan, Zadok, Benaiah, Joab and Abiathar as **biblical narrative**, not independently verified individual actions or a proven 962 BCE date. The inherited point east of the Jordan was changed to a broad Jerusalem reference; it does not certify the location of every scene. Existing source evidence and ID are retained. See [Adonijah](https://en.wikipedia.org/wiki/Adonijah), [Bathsheba](https://en.wikipedia.org/wiki/Bathsheba), [Benaiah](https://en.wikipedia.org/wiki/Benaiah) and [Solomon](https://en.wikipedia.org/wiki/Solomon).
- **Zhou–Chu:** Added `r2_zhou_chu_957_context`, a non-destructive regional cultural note. [Zhou–Chu War](https://en.wikipedia.org/wiki/Zhou%E2%80%93Chu_War) reconstructs campaigns under King Zhao around 961–957 BCE, while [King Mu](https://en.wikipedia.org/wiki/King_Mu_of_Zhou) offers conflicting reign dates. The one-year slot is a reference, not proof of a battle in that year; the broad Hubei-region point is not a battlefield or an occupation boundary. Individual details and troop figures require source-critical review. It overlaps existing Zhao and Mu context but adds campaign information.

The indexed update and addition are visible to the history-data readers as notes; the research evidence itself is not an NPC or a guarantee of runtime behavior. No new military battle or destructive hazard was enabled. Exact behavior in Minecraft has **not** been tested.

## Other checks and limitations

- [Dʿmt](https://en.wikipedia.org/wiki/D%CA%BFmt) gives conflicting chronologies; [Yeha](https://en.wikipedia.org/wiki/Yeha) does not independently establish a 980 BCE founding. Existing `wpy_be3b0cc76b` already flags the issue; no duplicate note added.
- [Solomon's Temple](https://en.wikipedia.org/wiki/Solomon%27s_Temple) says the construction date and builder are debated. Existing 957 note already qualifies the claim. Hiram king of Tyre and Hiram the craftsman are kept distinct in the research graph.
- [Kurukshetra War](https://en.wikipedia.org/wiki/Kurukshetra_War) is an epic tradition; 950 BCE is not an established battle date. [Kuru kingdom](https://en.wikipedia.org/wiki/Kuru_kingdom) and [Parikshit](https://en.wikipedia.org/wiki/Parikshit) involve separate historical and later legendary questions. Existing `r2_kurukshetra_950_tradition` remains qualified; no new battle trigger.
- Existing Egyptian dynasty transition note already distinguishes Psusennes II from the decade page's different name and flags the alternate chronology. [Iuput](https://en.wikipedia.org/wiki/Iuput) and [Maatkare B](https://en.wikipedia.org/wiki/Maatkare_B) add family and institutional leads, not proof that everyone was present at the transition.
- The decade page's Palenque “Snake Spine” lead has no working named linked biography; [Palenque](https://en.wikipedia.org/wiki/Palenque) does not substantiate a 967 BCE historical ruler. No claim added.
- An inclusive scan of the indexed hazard pack found zero overlapping records. This is **not** a world-event audit, proof of no disasters, or verification of other packs.

## People and alternate-history research

`eternal/src/main/resources/data/eternalengine/eternal/history/sources/wikipedia_989_940_people_links.json` contains 28 selected person/figure references, 27 qualified relationships and 24 event roles linked to six existing/new game event IDs. The graph includes rival succession factions, Zhou campaign leaders, Egyptian relatives and epic figures, distinguishing narrative from historical evidence. Its 26 unique article titles resolved, but that check does not verify identities, revisions or individual claims. This research-only graph is not spawnable and provides no invented life dates or spawn coordinates; natural VIP spawning and player-driven historical branching remain unimplemented.

## Validation and rollback

`reviews/989_940_bce_context_2026-10.json.gz`, canonical SHA-256 `4119a1d80de9ce6fae6034fc47e59c6697efced362630e7717c2a35abb218f78`, holds one update and one addition. Fourteen targeted tests passed both before and after application; staging checked reversibility; both installed after-images were found exactly once in the indexed packs. The installer `apply_989_940_bce_context.py` writes atomically **per pack**, not across packs. For rollback of overlapping older work, reverse this installer **before** `apply_1000_960_bce_context.py`; the older installer expects its original after-image. Shared events, existing notes, saved-world effects and duplicate suppression were not exhaustively reviewed.

Four old locked manifests were losslessly compacted; raw and canonical hashes are recorded and verified in `storage_compaction_989_940.md`. Earlier interrupted-compaction raw-hash provenance and review-date discrepancies remain unresolved. The crawler is still storage-blocked; the jar is stale. No recent full-integrity, Java probe, live loader, Minecraft or save test was run. Continue from 939 BCE only as preliminary work; full linked collection and implementation still remain.
