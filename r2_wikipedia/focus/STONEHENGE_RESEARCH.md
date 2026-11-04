# Stonehenge — linked Wikipedia research

## What the linked articles add

The [Stonehenge article, revision 1377824638](https://en.wikipedia.org/w/index.php?title=Stonehenge&oldid=1377824638), gives a site reference point of **51.17889° N, 1.82611° W**, and describes multiple construction phases rather than a single construction date.

- The detailed article dates the first circular ditch-and-bank enclosure to **about 3100 BCE**. [English Heritage](https://www.english-heritage.org.uk/visit/places/stonehenge/history-and-stories/building-stonehenge/) uses **about 3000 BCE**. Neither provides an exact year.
- The first enclosure was about 110 metres across. A ring of **56 Aubrey holes** belongs to the early monument. Their original purpose is uncertain: the detailed article considers timber and bluestones. See also [Aubrey holes, revision 1376816188](https://en.wikipedia.org/w/index.php?title=Aubrey_holes&oldid=1376816188), and the [BBC account of a 2008 excavation interpretation](https://news.bbc.co.uk/2/hi/uk_news/england/wiltshire/7660860.stm). An archaeological hypothesis is not a confirmed reconstruction.
- Wikipedia describes human-bone deposits dating as early as about 3000 BCE and later use as a cremation cemetery. This does not date every burial to 3000 BCE.
- Wikipedia places a second phase around 2900–2600 BCE and a major sarsen phase around 2600–2400 BCE. These are later context, not events to place in exactly 3000 BCE.

## What was added and what needs correction

The sources, selected raw wikitext lines, place reference, findings and remaining uncertainties are now in the **project source JSON** at `eternal/src/main/resources/data/eternalengine/eternal/history/sources/wikipedia_3000_bce.json`. This is not indexed by the game.

There is already a Stonehenge record in the game's indexed `events_wikipedia.json.gz`: ID `wpy_73ad8709b2`. Its previous text stated that the first version had **56 wooden posts**, which is stronger than the linked article supports. It now says the pits’ original use is uncertain. The record still uses the existing one-year gameplay slot of 3000 BCE, although the date is approximate.

A wording-only correction was **installed** after Python transformation and logical rollback tests and Java 17 headless loader probes passed, including the full resource tree. It retains the existing ID, coordinates, radius and reference year; it does not resolve the engine's limited handling of approximate dates. The temporary Java 17 installation is not part of the saved workspace. Its before/after snapshot is in `reviews/stonehenge_early_wording_2026-10.json`. No full Forge build or live gameplay test was performed.

Other Stonehenge entries exist in game packs. Their dates, location and possible overlaps have not been fully reviewed. This research is not a complete article-chain collection or a completed year.
