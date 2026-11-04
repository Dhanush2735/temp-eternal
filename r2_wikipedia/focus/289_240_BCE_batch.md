# 289–240 BCE: preliminary R2 batch

**Status: partly worked, not fully collected.** The batch resolved all 50 English Wikipedia year titles without redirects or missing pages and archived their revision wikitext in `year_wikitext_289_240.json.gz`; templates remain unexpanded. The five decade pages and selected linked articles were examined only in part. A starting-year scan found 262 indexed rows in this interval; most were not individually reviewed, and records that start earlier but overlap this interval are outside that count. No claim of worldwide or annual completeness is warranted.

## Changes in indexed gameplay JSON

The guarded context manifest updates **20 existing rows in five indexed packs**, retaining IDs and exact before-images. No new effect-bearing events were added.

- Twelve imported world-battle rows were moved to the linked article's BCE year: Arretium, Lake Vadimo, Asculum, Thermopylae, the Strait of Messina, Beneventum, Sparta, Messana, Adys, the Bagradas River, Phintias and the 278 BCE siege of Syracuse. These linked accounts have varying reliability; some explicitly rely heavily on ancient primary sources. The world-pack NewsIndex treats `end` inclusively, while HistoryGazetteer uses an exclusive end; a battle may therefore still display for an extra year. See each row's source evidence for the revision-pinned article.
- Aspis is recorded as an uncertain 256/255 BCE siege and Lilybaeum as 277/276 BCE context, rather than inventing a precise date or activating a continuous multi-year siege. First Punic War is dated 264–241 BCE and changed from a continuous 293 km military circle to regional context; it involved multiple campaigns and places. Other indexed battles remain.
- The 258 BCE Handan entry now identifies Zhao, not Zhou, as the state. The related 257 BCE entry has been moved from a point in Shaanxi to the existing Handan city reference and changed to a note, so the two year-page entries do not impose separate military triggers for the same siege. This city point is not a surveyed siege location. The [linked battle article](https://en.wikipedia.org/w/index.php?title=Battle_of_Handan&oldid=1370442559) gives 259–257 BCE; details need more review.
- Ashoka's accession, coronation and conversion entries are now contextual rather than exact political triggers. The [biography](https://en.wikipedia.org/w/index.php?title=Ashoka&oldid=1380594000) gives approximately 268 BCE for the reign and 269 BCE for coronation, and describes a gradual drawing toward Buddhism after the Kalinga war. It does not establish the imported exact 16 May accession or exact 266 conversion. The two broad accession records overlap and should not be read as independent events.

## Hazards

Five rows were moved from the active hazard pack to regional notes. `Disasters.java` processes hazard-pack rows regardless of their descriptive `kind` or `effect`, so merely relabeling them there would not prevent damaging effects. Moves preserve IDs and source before-images; they **do not prove that the underlying events did not happen**.

- **Delphi:** [NOAA earthquake 24](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/24) records 282 BCE from an old catalog, while a [modern study of ancient narratives](https://shs.cairn.info/revue-dialogues-d-histoire-ancienne-2023-1-page-9?lang=en) discusses earthquake, landslide and hail in the attack around 279/278 BCE. The similarity is a research lead, not proof of a single event. Exact date, magnitude and 50 km damage footprint are unestablished.
- **Lysimachia:** [NOAA earthquake 23](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/23) catalogs 282 BCE, while [Dmitriev's historical analysis](https://grbs.library.duke.edu/index.php/grbs/article/download/641/721/2611) dates Justin's account to approximately 287/286 BCE. These are not independent instrument measurements. The retained note keeps the catalog's anchor, not a verified exact event year.
- **Methana:** [Smithsonian GVP](https://volcano.si.edu/volcano.cfm?vn=212020&vtab=Eruptions) lists a confirmed eruption around 258 BCE **±18 years**, VEI 3, with unknown end. The exact-year, 40 km damage trigger is unsupported.
- **Campi Flegrei del Mar di Sicilia:** [GVP](https://volcano.si.edu/volcano.cfm?vn=211070&vtab=Eruptions) lists a confirmed submarine eruption around 253 BCE **±12 years**, unknown end. Confirmation does not establish the modeled exact-year, 40 km damage trigger.
- **Cádiz:** [NOAA earthquake 10516](https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/earthquakes/10516) includes conflicting 241/246 BCE reports and scholarship questioning their occurrence or date, with no identified contemporary account. Its offshore catalog position is not a verified epicenter; the damaging radius is unsupported.

The Chiguchin hazard remains active pending deeper review despite its previously recorded uncertainties. Other hazards and overlapping events have not been exhaustively checked.

## People and relationships

`history/sources/wikipedia_289_240_people_links.json` records **21 selected people, 15 qualified relationships and 26 event roles across 10 indexed IDs**, drawing on linked biographies and event articles. It includes figures on opposing sides, for example Pyrrhus and Roman commanders, Regulus and Xanthippus, and Bai Qi and Zhao commanders; Ashoka, Bindusara, Karuvaki and Tivala have qualified family links. These are research references only. Neither exact personal presence nor all biographical claims have been verified, and **none is a naturally spawnable VIP**. This is not a complete biography crawl.

## Verification and rollback

Context canonical SHA-256: `2e42b326db19f1b672c8ec5f85ad0c228a02539225c8056e12f2aa5d5f387223`; hazard manifest: `c8e53659d3536f71fa37e44b2bd086a5d0f1752ebf380e329e611639c40fa62f`. Stage succeeded; 14 context and 11 hazard tests passed both before and after application. All 25 installed after-images matched, and an in-memory dependency-ordered reverse/reapply round trip matched all six affected pack objects. Reverse **hazards before context**, and reverse this batch before older dependent shared-pack installers. Writes are atomic per pack, not across packs; interruption between pack writes requires recovery. This logical test is not a live loader, save, Forge build or Minecraft test.

Using the project's existing convention that five step endpoints overlap, this documented preliminary batch adds 45 to the ledger: **2,988 partly worked, 0 fully collected**. The number is not a count of complete independent year histories. The game jar remains stale; natural VIP spawning, historical following and alternate-history branching are not implemented. Next chronological interval is 239–190 BCE; earlier intervals remain incomplete.
