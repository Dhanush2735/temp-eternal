# 589–540 BCE: preliminary R2 batch

**Status: partly worked, not fully collected.** Resolved all 50 requested year titles: 16 redirect to decade pages and 34 have individual pages. Archived the 34 annual wikitext revisions in `year_wikitext_589_540.json.gz`; templates/transclusions are not expanded. Five decade pages and selected linked articles were reviewed, not the full recursive chain. A scan found 167 indexed rows starting in this range; most have not been individually reviewed.

## Indexed gameplay data

Applied **26 guarded updates across five indexed packs**, preserving IDs, plus **two guarded cross-pack moves** from the active hazard pack into regional historical notes. Examples:

- Corrected the Battle of An and second siege of Jerusalem start years to the linked articles' 589 BCE convention. Jerusalem's fall remains disputed between 587 and 586. Pteria, Thymbra and Sardis retain their inherited 546 reference year while names/evidence acknowledge competing 547/546 chronologies. This is not a claim of exact timing.
- Corrected misplaced locations for Jerusalem, Urartu, the François Vase and Xenophon's Larissa/Calah account. Larissa in Greece is not the probable Nimrud reference. The inherited 557 BCE siege/eclipsed-sun claim is now a qualified note, not certain military presence; Xenophon describes a cloud and does not establish the year.
- Qualified the Thales eclipse and Median–Lydian battle association, Tyre siege, Croesus and Bimbisara chronologies, Ishtar Gate construction, Median–Persian conflict, Suizei succession and Vijaya's founding tradition. Duplicate or overlapping records remain possible and are identified where reviewed; no claim of global deduplication.
- The 557 BCE Santorini disruption claim was converted to a note: GVP's chronology does not list a 557 BCE eruption, which is not proof that one could not have occurred. The GVP-labeled 565 BCE Etna eruption is uncertain. The historical Sparta earthquake around 550 BCE is reported by historians but was not directly detected in one fault study; this does not disprove it or identify it with the separate 464 BCE event. The Etna and Sparta records were moved out of the active hazard pack to notes rather than triggering certain damaging hazards.
- Bakening's c. 550 BCE GVP entry is listed **confirmed**, with VEI 2 and tephrochronology; it was left active. This does not establish that the exact reference year or inherited 40 km disruption radius is precise.

## Linked people for later R3 work

`eternal/src/main/resources/data/eternalengine/eternal/history/sources/wikipedia_589_540_people_links.json` records **35 figures, 26 qualified relationships and 37 roles across 13 indexed event IDs**. It includes multiple figures around An, Yanling, Jerusalem and the Persian–Lydian campaigns, as well as the artists Ergotimos and Kleitias and figures in South Asian and Japanese traditions. Some are legendary or are described only in later narratives; redlinked biographies are labeled. These are research references, not independently verified identities, proof of physical presence, or spawnable VIPs. No natural VIP spawning or alternate-history behavior was implemented here.

## Sources and uncertainty

- [Battle of An, revision 1378907784](https://en.wikipedia.org/w/index.php?title=Battle_of_An&oldid=1378907784), [Yanling, revision 1378907914](https://en.wikipedia.org/w/index.php?title=Battle_of_Yanling&oldid=1378907914), [Jerusalem siege, revision 1378907811](https://en.wikipedia.org/w/index.php?title=Siege_of_Jerusalem_(587_BC)&oldid=1378907811).
- [Pteria, revision 1378908247](https://en.wikipedia.org/w/index.php?title=Battle_of_Pteria&oldid=1378908247), [Thymbra, revision 1378908252](https://en.wikipedia.org/w/index.php?title=Battle_of_Thymbra&oldid=1378908252), [Sardis, revision 1378908298](https://en.wikipedia.org/w/index.php?title=Siege_of_Sardis_(547_BC)&oldid=1378908298), [Croesus, revision 1381764189](https://en.wikipedia.org/w/index.php?title=Croesus&oldid=1381764189), [Median–Persian conflict, revision 1378908125](https://en.wikipedia.org/w/index.php?title=Medo-Persian_conflict&oldid=1378908125).
- [Eclipse of Thales, revision 1378907867](https://en.wikipedia.org/w/index.php?title=Eclipse_of_Thales&oldid=1378907867); [Xenophon, Anabasis 3.4](https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Aabo%3Atlg%2C0032%2C006%3A3%3A4); [Nimrud, revision 1380467098](https://en.wikipedia.org/w/index.php?title=Nimrud&oldid=1380467098).
- [François Vase, revision 1382056729](https://en.wikipedia.org/w/index.php?title=Fran%C3%A7ois_Vase&oldid=1382056729); [Prince Vijaya, revision 1362554732](https://en.wikipedia.org/w/index.php?title=Prince_Vijaya&oldid=1362554732); [Bimbisara, revision 1378908081](https://en.wikipedia.org/w/index.php?title=Bimbisara&oldid=1378908081).
- GVP [Etna](https://volcano.si.edu/volcano.cfm?vn=211060&vtab=Eruptions), [Santorini](https://volcano.si.edu/volcano.cfm?vn=212040&vtab=Eruptions) and [Bakening](https://volcano.si.edu/volcano.cfm?vn=300123&vtab=Eruptions); [Sparta fault study](https://members.noa.gr/d.papan/en/publications/A44.pdf) and [Cartledge on ancient Greek earthquakes](https://ia801704.us.archive.org/25/items/omnibus02/05CartledgeEarthquakes.pdf).

Each update records more specific source links and qualifications. A Wikipedia revision is a traceable snapshot, not independent confirmation of its claims. Numerical BCE years here use the project's negative-number convention, not astronomical year numbering.

## Validation and rollback

- Context manifest canonical SHA-256: `1cf7dc48f08476ac9e4e033322257b294ee2a98feb63cae28037057bb6de465c`; hazard manifest: `0cf928f683ab57ad4421e7eea8b986c3ecf798962752678afd28e7f4c997689d`.
- Staged and applied both; **16 context and 11 hazard unit tests passed before and after application**. Verified 28 exact installed after-images and dependency-ordered in-memory rollback/reapplication over six pack objects. Actual rollback writes were not performed. Writes are atomic per pack, not transactional across packs.
- To undo, run `python r2_wikipedia/apply_589_540_bce_hazards.py rollback` **before** `python r2_wikipedia/apply_589_540_bce_context.py rollback`. Reverse these newer hazard moves before older 639–590, 689–640 and 739–690 hazard moves because source indices and shared pack state depend on order. Other shared-pack dependencies may exist.
- `HistoryGazetteer` treats event ends as exclusive; `NewsIndex` treats world-pack ends as inclusive and may display an additional year. The source JSON changed; no live game, loader, save, rebuilt jar, Java probe or full integrity test was run. Previously built jar is stale.
- Ten older CE review manifests and six year-title files were compacted without changing parsed objects or canonical hashes; see `storage_compaction_589_540.md`, `storage_compaction_589_540_extra.md`, and `storage_compaction_589_540_year_titles.md`. External/binary raw-hash dependencies were not checked.

## Progress

Under the existing shared-period accounting convention, five ten-year steps overlap five previously counted endpoints: **2,718 years partly worked, 0 fully collected**. This is not a completeness percentage or proof of independent annual histories. Next chronological window: **539–490 BCE**, while earlier windows remain incomplete.
