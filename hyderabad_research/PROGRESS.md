# Hyderabad-area Wikipedia research — first collection

**Status: in progress. No year is fully collected.** The user subsequently requested that implementation start; a read-only in-game pilot preview is now being implemented alongside unfinished research. This is the first source archive and a small research index, not the full 3000 BCE–3000 CE collection.

## What is saved

- `wikipedia_foundation_2026-11.json.xz`: 26 English Wikipedia revisions, including Hyderabad, local places, history, and people, plus two period pages.
- `wikipedia_people_2026-11.json.xz`: 11 revisions, including connected poets and historical figures. One entry, **Mahbub Ali Khan**, is a different person: the Bangladeshi naval officer. It is retained as a documented false positive, not a Hyderabad person.
- `wikipedia_corrections_2026-11.json.xz`: 8 revisions, including the correct Hyderabad ruler, **Mahboob Ali Khan (Asaf Jah VI)**, and other linked biographies and places.
- Across the three archives there are **43 distinct revision identities**; the repeated period article is counted only once. These are selected source revisions, not all connected articles. Every archived article has its page ID, exact revision ID, timestamp, original wikitext and SHA-256 of the wikitext. Wikipedia text is available under CC BY-SA; attribution and applicable reuse terms are required. Source links can be constructed as `https://en.wikipedia.org/w/index.php?oldid=REVISION`.
- `research_candidates.json`: 22 provisional place, event, person, and relationship claims, linked to pinned revisions and carrying uncertainty notes. These are research records, **not** spawnable characters or active gameplay JSON.
- `collect_foundation.py` saves bounded, revision-pinned sources; `build_notes.py` verifies all raw hashes and creates the provisional notes. Both enforce the existing Hyderabad pilot storage guard.

## Coverage ledger

| Range | What was checked | Fully collected years |
|---|---|---:|
| 3000–2951 BCE | All 50 individual English Wikipedia year-title requests were resolved. Each redirects to the same [30th century BC](https://en.wikipedia.org/w/index.php?oldid=1371895853) article. The century and [3rd millennium BC](https://en.wikipedia.org/w/index.php?oldid=1383592843) article revisions were archived. There are no individually researched local-year records. | 0 of 50 |
| 2950 BCE–2026 CE | Selected Hyderabad-area source revisions and a few provisional claims have been collected. The required millennium/century/decade/year chains and relevant connected articles have not been systematically completed. | 0 |
| 2027–3000 CE | No future local history can be verified; no future scenarios have been designed or collected. Future content must be explicitly labeled as scenarios, not historical facts. | 0 |

**All intervening years are in scope; a redirect to a century is not evidence for every year.** Gaps mean “not yet known or researched,” not proof that nothing happened. The calendar convention for BCE/year zero still needs a separate implementation decision.

## Initial research findings and cautions

- Wikipedia identifies Muhammad Quli Qutb Shah with Hyderabad’s founding in 1591 ([city history](https://en.wikipedia.org/w/index.php?oldid=1376916956), [biography](https://en.wikipedia.org/w/index.php?oldid=1373146972)). Earlier local history belongs to the geographic area, not the city. Existing game data also has a 1589 entry; the conflict still needs investigation.
- [Hasmathpet cairns](https://en.wikipedia.org/w/index.php?oldid=1376761069) are described as second-century-BCE burials. This does not date them to 3000 BCE or prove an event in each year.
- [Hussain Sagar](https://en.wikipedia.org/w/index.php?oldid=1376754474) is dated to 1562 in Wikipedia. Its article and [Hussain Shah Wali’s biography](https://en.wikipedia.org/w/index.php?oldid=1359353593) credit different figures; verify contributions before implementation. Historical lake outlines are not established by current maps.
- The archive follows connections among [Muhammad Quli Qutb Shah](https://en.wikipedia.org/w/index.php?oldid=1373146972), [Hayat Bakshi Begum](https://en.wikipedia.org/w/index.php?oldid=1356985385), [Sultan Muhammad Qutb Shah](https://en.wikipedia.org/w/index.php?oldid=1381371387), and [Abdullah Qutb Shah](https://en.wikipedia.org/w/index.php?oldid=1381371317). Family links do not establish day-to-day whereabouts or behavior.
- [Bhagmati](https://en.wikipedia.org/w/index.php?oldid=1360405197) is linked to local narratives, but Wikipedia describes her existence and the city's naming story as debated. Do not treat these claims as certain.
- The [1908 Musi flood](https://en.wikipedia.org/w/index.php?oldid=1376429967) article gives inconsistent fatality estimates; the [Amjad Hyderabadi](https://en.wikipedia.org/w/index.php?oldid=1380752773) biography also conflicts internally on his birth year. Keep those details unresolved.
- The [2013 Hyderabad blasts](https://en.wikipedia.org/w/index.php?oldid=1383059195) article identifies Dilsukhnagar, but its infobox coordinates appear near Charminar, and its timings/injury totals differ within the article. Do not use those coordinates without verification. The initially searched title `2013 Dilsukhnagar blasts` was missing; the archived article is `2013 Hyderabad blasts`.
- The pilot is intended to include the broader Hyderabad area, including Malkajgiri. Its precise boundary is not yet verified; historical Hyderabad State must not be confused with a present-day city boundary.

## Remaining work before implementation

1. Continue chronologically through **every intervening year**, recording title resolution and the full millennium → century → decade → year chain where available, then examine relevant Hyderabad-area linked history, people, places and relationships; log missing articles, redirects, uncertainty and unresolved links.
2. Verify identities and local relevance, inspect article citations and contradictory claims, and distinguish regional evidence from actual city evidence. Pin followed article revisions. Source archives alone are not the same as reviewed facts.
3. Continue researching the entire requested range and identify unavoidable gaps, including future years. Do not invent events or represent an incomplete collection as complete. User review will be needed where evidence does not exist or scope cannot be closed.
4. The user subsequently authorized implementation to start. A small read-only Hyderabad preview is now connected in source code; continue Hyderabad-limited implementation carefully, including safe temporal changes, people/NPC behavior, world data and `/ee check`. Review the pilot before any worldwide expansion.
