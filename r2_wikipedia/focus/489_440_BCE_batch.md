# 489–440 BCE: preliminary R2 batch

**Status: partly worked, not fully collected.** Resolved all 50 year titles with no redirects and archived their exact-revision wikitexts in `year_wikitext_489_440.json.gz`; transclusions are unexpanded. Five decade pages and selected linked articles were partially reviewed, not the full recursive chain. A scan found 285 indexed rows starting in this range; most remain individually unreviewed, and start-year scanning misses events that began earlier.

## Indexed gameplay data

Applied **20 guarded updates across four indexed packs**, preserving IDs, and **two moves from the active hazard pack into regional notes**.

- Adjusted the start years of nine world-pack battles to the linked articles' BCE years: Plataea, Mycale, Himera, Lize, Cremera, Mount Algidus, Tanagra, Oenophyta and Coronea. The source date is not proof of an exact day, battlefield footprint or narrative details. `NewsIndex` treats the world-pack end as inclusive, while `HistoryGazetteer` treats it as exclusive; an extra displayed year remains possible.
- Replaced a continuous broad-radius military effect for the 480–479 Persian invasion with a regional context note; separate battle records remain. The disputed date of the Eurymedon battle, given as 469 or 466 in its linked article, is now a note rather than a single certain 466 military trigger.
- Qualified Babylonian rebel kings' 484 revolt and the uncertain claim that Xerxes removed the Marduk statue. Corrected references wrongly located in Babylon or Sparta for Sardis, the Egyptian revolt and reconquest, Mardonius's Greek campaign and Athens's rebuilding. Eion's reference was moved from Ionia to the Strymon area. Points and radii are regional approximations, not proof of exact activities across their whole extent.
- Recast the early Qufu temple as a tradition associated with consecration of Confucius's former house; the existing temple complex should not be assumed to have existed in its present form in 478 BCE.
- Moved the Popa 442 BCE disruption to a note: GVP classifies that eruption as uncertain and cites a local legend, with no physical evidence for an eruption that recent. The Cotopaxi 455 BCE disruption was also moved to a note: GVP displays a 455 BCE fatalities subentry attached to an eruption listed at 2640 BCE ±200 years, an internal catalog anomaly that does not substantiate a separate exact 455 BCE eruption. Neither finding proves no event occurred.

The 479 BCE Potidaea and Sparta-related world hazards and the 480 BCE Salamis-region hazards were **not fully reviewed or changed**. A historical account, the existence and dating of a wave, its cause, and a specific simulated damaging earthquake or radius are different claims. Other unreviewed or duplicated hazards and events may remain. GVP lists the 479–475 BCE Etna and c.475 BCE Vulcano eruptions as confirmed with uncertain dates; those hazard records remain active, but their gameplay radii are unverified.

## Linked people for later R3 work

`eternal/src/main/resources/data/eternalengine/eternal/history/sources/wikipedia_489_440_people_links.json` contains **41 research figures, 19 qualified relationships and 48 roles across 13 indexed event IDs**. These include multiple Greek and Persian figures at Plataea and Mycale, three at Himera, rulers of Wu and Yue at Lize, both Babylonian rebel kings, and figures in the traditional Roman narratives. Some roles come only from ancient accounts or article infoboxes; presence and identity require further verification. References are **not spawnable VIPs**, and natural spawning and alternate-history behavior were not implemented.

## Sources and interpretation

- [Plataea](https://en.wikipedia.org/w/index.php?title=Battle_of_Plataea&oldid=1375049994), [Mycale](https://en.wikipedia.org/w/index.php?title=Battle_of_Mycale&oldid=1370270282), [Himera](https://en.wikipedia.org/w/index.php?title=Battle_of_Himera_(480_BC)&oldid=1370265653), [Lize](https://en.wikipedia.org/w/index.php?title=Battle_of_Lize&oldid=1370447809), [Cremera](https://en.wikipedia.org/w/index.php?title=Battle_of_the_Cremera&oldid=1370277739).
- [Mount Algidus](https://en.wikipedia.org/w/index.php?title=Battle_of_Mount_Algidus&oldid=1370269924), [Tanagra](https://en.wikipedia.org/w/index.php?title=Battle_of_Tanagra_(457_BC)&oldid=1370590497), [Oenophyta](https://en.wikipedia.org/w/index.php?title=Battle_of_Oenophyta&oldid=1370452076), [Coronea](https://en.wikipedia.org/w/index.php?title=Battle_of_Coronea_(447_BC)&oldid=1370437651), [Eurymedon](https://en.wikipedia.org/w/index.php?title=Battle_of_the_Eurymedon&oldid=1370277798).
- [Babylonian revolts](https://en.wikipedia.org/w/index.php?title=Babylonian_revolts_(484_BC)&oldid=1379546559), [Qufu Temple](https://en.wikipedia.org/w/index.php?title=Temple_of_Confucius,_Qufu&oldid=1365740774), [Persian invasion](https://en.wikipedia.org/w/index.php?title=Second_Persian_invasion_of_Greece&oldid=1381554985), [Delian League](https://en.wikipedia.org/w/index.php?title=Delian_League&oldid=1376370545).
- GVP [Popa](https://volcano.si.edu/volcano.cfm?vn=275080&vtab=Eruptions), [Cotopaxi](https://volcano.si.edu/volcano.cfm?vn=352050&vtab=Eruptions), [Etna](https://volcano.si.edu/volcano.cfm?vn=211060&vtab=Eruptions), and [Vulcano](https://volcano.si.edu/volcano.cfm?vn=211050&vtab=Eruptions). Each update records its own sources. Wikipedia revisions preserve consulted material, not independent verification. BCE numbers use the project's negative-number convention rather than astronomical year numbering.

## Validation and rollback

- Context canonical SHA-256: `60c9ea8972621e160586c46d2a31b399c467af56ec3aaea8f8a15f7c1264c9f4`. Hazard manifest: `814c8cb532e859ffd7c28af6777b28f33ba65fb070ffbf9ff62a45767f4c4bbc`.
- Staged and applied; **15 context and 11 hazard tests passed before and after**, 22 installed after-images verified, and six pack objects round-tripped in memory reversing hazards before context. An initial hazard test rejected the word “unsupported” instead of “uncertain”; the assertion was corrected before application. No final actual rollback was performed. Writes are atomic per pack, not across packs.
- Undo using `python r2_wikipedia/apply_489_440_bce_hazards.py rollback` before `python r2_wikipedia/apply_489_440_bce_context.py rollback`. Reverse newer hazards before 539–490 and earlier hazard installers; other shared-pack dependencies and semantic overlaps remain possible.
- No live game, loader, save, rebuilt jar, Java probe or full integrity test was run; the jar is stale. Existing reader-endpoint and saved-world effects remain unverified.
- To recover snapshot headroom, `focus/gandhi_project_raw.json` was losslessly compressed to `.json.gz`; original and gzip SHA-256s, byte verification and the restoration command are in `focus/gandhi_project_details.md`. The earlier report describing JSON minification remains historical provenance. The separate crawler storage guard remains unresolved.

## Progress

Five step endpoints were previously counted under the existing shared-period convention: **2,808 years partly worked, 0 fully collected**. This is not a completeness percentage or a count of independently completed year histories. Next chronological window: **439–390 BCE**, with earlier windows still incomplete.
