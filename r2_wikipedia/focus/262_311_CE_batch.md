# 262–311 CE: preliminary R2 pass

**Status: partially worked, not fully collected.** This pass resolved and archived the revisions of all 50 annual Wikipedia titles. It examined selected entries and linked articles, not every link or every year’s full history. Raw wikitext does not expand transclusions. The starting scan covered 254 indexed records beginning in the interval, including 28 hazards; earlier-starting overlaps were excluded.

## Indexed game data

- **28 guarded updates** across five indexed packs, with original IDs preserved. Examples: correct the 306 claim that Constantinople was already the new capital and that persecution had ended throughout the empire; describe the 280 Jin conquest of Wu after a campaign spanning late 279–280; correct the Jin successor Huai to Hui’s half-brother; move Bonosus’s Cologne reference from the Netherlands to Germany; qualify the Tikal Stela 29 inscription date and unsupported claim it was the oldest Maya stela; and remove unsupported exact casualty figures where NOAA uses categorical codes.
- **22 hazard records moved to indexed non-damaging notes:** 19 eruptions with uncertain nominal years; two linked tsunami accounts NOAA rates improbable; and a Salamis earthquake catalogued at 300 with a disputed date. No later Salamis earthquake is automatically created. Parinacota’s old VEI 4 claim is qualified against the current GVP value of 0. The Witori source reports damage and evacuations, but its estimated date is 310 ±100 years, not an exact 310 event.
- **Six of the 28 scanned hazards remain in the hazard pack:** five earthquakes modified in place with uncertainty and one 303 Vesuvius eruption not reviewed in this pass. The 262 earthquake’s separate Wikidata lockdown was changed to a note to avoid a second effect for the same account. The retained earthquake footprints and chronology remain approximations, not validated simulations.
- China’s Wei–Shu and Jin–Wu 800 km political circles were changed to contextual notes where duplicative or unsupported. A small Luoyang political proxy for Jin’s 266 establishment and the existing 280 annual proxy remain; they do not model entire territories.

The detailed before/after records, source links and reasons are in `reviews/262_311_ce_context_2026-10.json.gz` and `reviews/262_311_ce_hazards_2026-10.json`. Wikipedia links used in the selected corrections are pinned to revision IDs; NOAA and GVP URLs are current references rather than versioned snapshots. Both migrations were staged before application. Their canonical SHA-256 hashes are:

- Context: `ba1e907e60e799a3ad013a976e3e539e1501fa6ca4ddaa50d37338a26d3ac58b`
- Hazards: `2b1037ec4eda2209a7a86ac744f23a177c6dd46b72033361c76d3b4e2010aef1`

Reversal requires `apply_262_311_ce_hazards.py rollback` **before** `apply_262_311_ce_context.py rollback`, and both before older installers touching the same packs. Writes are atomic per pack, not transactional across packs. Round trips were tested in memory, not on a saved game.

## People and relationships

`history/sources/wikipedia_262_311_ce_people_links.json` contains **40 people, 31 qualified relationships and 44 event roles across 14 indexed IDs**. They include Palmyrene and Roman figures, participants on different sides of the Wei–Shu and Jin–Wu campaigns, Jin court figures, and Tetrarchs. These are source-linked research leads, **not spawnable VIPs**; an association does not prove everyone was physically present at a battle. A potentially misleading conflation between the Palmyrene general Zabbai and the separately described ancestral namesake was excluded.

## Checks and limits

- 11 batch tests passed, including manifest tamper checks, exact indexed after-images, current and previous batch dependency-ordered in-memory reversals, people graph references, and title/revision archives. Another 19 resolver, scope and pipeline tests passed.
- **62 pinned Wikipedia revision/title pairs** in this batch’s context manifest and people graph were checked against the API and matched.
- Title inventory: **3,300 distinct resolved chronological titles** in archived title-result files (2,989 BCE and 311 CE). This measures title resolution only, not examined histories, partially worked years, or completion. The older aggregate of **3,168 partly worked years remains unreconciled** and must not be incremented by 50.
- **Fully collected years: 0.** The initial 3000–2990 BCE years have separate research but are absent from this particular title-file inventory. Earlier and current ranges require much more linked-article work.
- No live game, loader, save-world, full integrity, current Java probe, or rebuilt jar was tested. The existing jar is stale. Natural VIP spawning, history-following behaviour and player-triggered branching remain unimplemented.

The next chronological preliminary interval is **312–361 CE**; earlier intervals remain incomplete.
