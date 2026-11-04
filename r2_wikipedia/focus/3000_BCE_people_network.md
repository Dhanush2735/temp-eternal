# 3000 BCE — connected people for alternate-timeline research

## First pass: early Egyptian royal connections

This is a **partial pass**, not a worldwide collection of everyone associated with 3000 BCE. It traces eight connected people using linked English Wikipedia biographies:

| Person | Evidence-led description |
|---|---|
| [Narmer](https://en.wikipedia.org/w/index.php?title=Narmer&oldid=1380968539) | Early Egyptian king; the Narmer–Menes identification is debated. |
| [Hor-Aha](https://en.wikipedia.org/w/index.php?title=Hor-Aha&oldid=1381182889) | A First Dynasty king normally placed after Narmer and before Djer. |
| [Djer](https://en.wikipedia.org/w/index.php?title=Djer&oldid=1374952723) | A First Dynasty king normally followed by Djet; absolute chronology is disputed. |
| [Djet](https://en.wikipedia.org/w/index.php?title=Djet&oldid=1376673981) | A First Dynasty king linked to Djer by the succession. |
| [Neithhotep](https://en.wikipedia.org/w/index.php?title=Neithhotep&oldid=1382099851) | Royal woman; possible regent, with debated family connections. |
| [Benerib](https://en.wikipedia.org/w/index.php?title=Benerib&oldid=1370759386) | Traditionally identified as Hor-Aha's consort; one interpretation questions the name or identity. |
| [Khenthap](https://en.wikipedia.org/w/index.php?title=Khenthap&oldid=1373669188) | Obscure possible queen: a later inscription names her as Djer's mother; interpretations vary. |
| [Merneith](https://en.wikipedia.org/w/index.php?title=Merneith&oldid=1382612816) | Royal woman and regent; her exact status and proposed parentage are debated. |

The project now has a source-linked research network at `history/sources/wikipedia_3000_bce_people_network.json`: eight profiles and ten relationship assertions, with uncertainty recorded individually. Existing research profiles and IDs were not deleted. [Menes](https://en.wikipedia.org/w/index.php?title=Menes&oldid=1372501796) is recorded as a disputed identification, **not** assumed to be a separate person in addition to Narmer and Hor-Aha.

Being part of this network does **not** prove that all eight people were alive together, present at one location, or alive in precisely 3000 BCE. Birth/death dates and locations are not invented. The network is **research-only**: it is not read by the VIP runtime, and none of these eight became spawnable through this pass.

## Active game-data change

Added `r2_egypt_first_dynasty_succession_context_c3000` to indexed `events_wikipedia_regional.json.gz`. It identifies the conventional sequence of Narmer, Hor-Aha, Djer and Djet as a First Dynasty context and says the dating is uncertain. The 3000 BCE slot is a reference, not proof of a succession event in that year or of simultaneous lives. The map point near Abydos is a royal-burial-area reference, not evidence of where the people were during life. It is a cultural note, not an NPC profile or a scripted alternate event.

Source: [First Dynasty of Egypt](https://en.wikipedia.org/w/index.php?title=First_Dynasty_of_Egypt&oldid=1379753537) and the biographies above. The guarded before/after addition and rollback manifest is `reviews/3000_bce_egypt_people_context_2026-10.json`; canonical SHA-256 `795734ab006e11f4ebd36916fe0327667de3897a666e7f874e1bb3c48ccc7272`. Seven tests passed before and after; staged rollback and the unique installed after-image were verified. **No Forge/game/save test, manifest integrity regeneration, or jar rebuild** was performed.

## Remaining work

Natural VIP spawning and historical/player-divergent behavior remain unimplemented. The next research must extend beyond this Egyptian network to other linked people and civilizations, preserving contested identity and chronology rather than turning hypotheses into scripted facts. Continue the chronological backfill from 2939 BCE as well as revisiting the incomplete 3000–2940 BCE range. The crawler remains blocked by its storage guard.

This is a revisit: **557 historical years partly worked, 0 fully collected**. The count includes broad-context work, not full individual histories.
