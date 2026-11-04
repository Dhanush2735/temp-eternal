# 189–140 BCE: preliminary R2 batch

**Status: partly worked, not fully collected.** All 50 English Wikipedia year titles resolved without redirects or missing pages. Their revision wikitext is archived in `year_wikitext_189_140.json.gz`, with transclusions unexpanded. Five decade pages and selected linked articles were examined only in part. A scan found 216 indexed rows starting in the interval; most were not individually reviewed, and earlier-starting overlaps are excluded. This is not worldwide or complete annual coverage.

## Indexed gameplay changes

The guarded context manifest updates **21 existing rows across three indexed packs**, preserving IDs and exact before-images. No new effect-bearing event was added.

- Ten one-year-late imported battle starts were corrected using their linked articles, including the distinct battles of Pydna in **168 and 148 BCE**, Emmaus, Beth Zur, Beth Zechariah, Corinth and Scarpheia. The siege of Carthage now begins at approximately **149 BCE**, rather than 148. In the world pack, NewsIndex treats `end` inclusively but HistoryGazetteer uses an exclusive end; an extra display year may remain. Ancient accounts, battlefield coordinates, military radius and casualty totals require more checking.
- Beth Horon is a contextual **166/165 BCE** account and the Ascent of Lebonah a **167/166 BCE** account. The articles identify uncertain chronology and reliance on ancient sources; Lebonah's exact location is disputed. These ranges represent alternatives, not continuous fighting. The earlier generic Beth Horon link resolves to a disambiguation page; the manifest points to the specific ancient battle.
- The siege of Eucratideia is contextualized around **169 BCE**: the linked article relies heavily on Justin, reports implausible force figures, and neither an exact year nor site identity is independently established. The Vijithapura campaign is contextualized as **161 or 162 BCE** because its article flags disputed accuracy and insufficient sourcing.
- The Third Punic, Third Macedonian and Galatian War records are regional notes rather than broad continuous military circles overlapping individual indexed battles. The latter two start dates were corrected to the linked articles' **171** and **189 BCE**, respectively.
- The **Pons Aemilius** annual note no longer calls the bridge completed in 179 BCE or the world's first stone bridge. Its [linked article](https://en.wikipedia.org/w/index.php?title=Pons_Aemilius&oldid=1354183457) describes construction beginning in 179, later completion/arches and conflicting 151/142 references. Two **Corlea Trackway** annual notes now refer to the same construction around **148–147 BCE**, rather than presenting two independent precisely dated events; the [site article](https://en.wikipedia.org/w/index.php?title=Corlea_Trackway&oldid=1365047341) discusses dendrochronology and uncertainty about its purpose.

## Hazard review

Three rows were moved from the active hazard pack to indexed regional notes. `Disasters.java` processes hazard rows regardless of their `kind` or `effect`, so a relabel alone would not stop damage. These moves **do not prove the events did not occur**.

- **Gamchen:** [Smithsonian GVP](https://volcano.si.edu/volcano.cfm?vn=300210&vtab=Eruptions) lists a confirmed eruption around 188 BCE **±80 years**, based on tephrochronology, with unknown end. It cannot substantiate an exact-year, 40 km damage circle.
- **Gansu:** [NOAA earthquake 30](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/30) records a historical account of landslides and 760 deaths in the Wudu region, but flags epicenter, magnitude and effects for checking; its comment gives magnitude 6–7 rather than an established exact 7. The modeled 50 km damaging radius is not established.
- **Etna:** [GVP](https://volcano.si.edu/volcano.cfm?vn=211060&vtab=Eruptions) lists a confirmed reported eruption dated 141 BCE December 31 **±365 days**, with unknown end. This does not establish the exact trigger year or 40 km damaging circle. The earlier evidence, including the unresolved reported deaths, is retained unchanged as `r2SourceEvidence`; this pass adds separate evidence. The prior installer had retained it active pending research; reversing this pass restores that exact prior state.

The **183 BCE Vulcano** hazard remains active: GVP lists a confirmed eruption with unknown end and discusses contested interpretations of Vulcanello's formation. Its modeled damage radius is not validated here. Other hazards and overlapping records remain unreviewed.

## Connected people

`history/sources/wikipedia_189_140_people_links.json` records **30 selected people, 17 qualified relationships and 37 roles across 14 indexed IDs**. It includes both sides and namesake distinctions—for example Paullus and Perseus, the participants in the later Pydna battle, Carthaginian and Roman siege leaders, Maccabean and Seleucid figures, and Sri Lankan figures associated with traditional accounts. These are research references, not a comprehensive biography crawl or proof of precise physical presence. **No VIP is made spawnable.**

## Verification, rollback and capacity

Context canonical SHA-256: `c7ba4744e0fa44ec3204ffdea3275e1fdf1d8175a014ff87f6ffe18864975001`; hazard manifest: `d9bcf1dfc4221f37c55e6b1acb9dadcbf71d131ea88c7878e4a8bf756927f43c`. The hazard stage initially rejected the already-evidenced Etna row because the copied validator allowed only a new `r2SourceEvidence` field. Before application, the validator was changed to guard a separate `r2AdditionalEvidence` field while requiring the old evidence to remain identical.

Stage and application succeeded. Thirteen context and eleven hazard tests passed before and after application; a further prior-evidence preservation test was added and passed afterward, making **25 current tests**. All 24 installed after-images matched, and an in-memory dependency-ordered reverse/reapply round trip matched four pack objects. Reverse this batch's **hazards before context**, and reverse it before older dependent installers, particularly the earlier `150_110` Etna context installer. Writes are atomic per pack, not across packs; interruption between writes requires recovery. These checks do not substitute for live game, loader, save, full integrity, Java probe or rebuilt-jar testing.

Five unreviewed CE overlap scans were compressed without data loss to improve capacity; `focus/storage_compaction_189_140.md` records byte hashes, verification and restoration commands. Their original paths change to `.gz`; external dependencies were not checked. Natural VIP spawning, historical following and player-triggered branching remain unimplemented; the jar is stale.

Under the existing five-shared-endpoint convention, this preliminary batch adds 45 to the ledger: **3,078 partly worked, 0 fully collected**. This is not a count of complete independent year histories. Next chronological interval: **139–90 BCE**; previous periods remain incomplete.
