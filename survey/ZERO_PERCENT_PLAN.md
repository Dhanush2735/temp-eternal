# Plan for the 0% categories (measured 2026-10-11)

Rule, as asked: Wikipedia is primary, other sources are secondary. Everything below was checked
today against the offline Wikipedia copy (dump 2026-10-01, `worldfill/wpdump.py`) or the live
source.

## What exists

| Category | Wikipedia (primary), measured today | Other sources (secondary) | How it shows in the game | Mod change? | Size | Effort |
|---|---|---|---|---|---|---|
| **Kings and queens** | 66 "List of state leaders in …" pages, about 1,000 reigns per century page (the 15th century has 995 spans like "(1405–1433)"); 277 per-country lists ("List of monarchs / rulers / kings of …"); state infoboxes name 2,581 leaders | Wikidata reigns (P39) once its query service recovers | "We are ruled by King Krishnadevaraya of Vijayanagara, since 1509" | yes: RulerRegister and villager talk | ~1 MB | medium |
| **Languages** | State infobox language field: 1,049 of the mod's 1,544 states (68%); 200 "Languages of …" pages for modern countries | Glottolog 5.3: 8,304 languages with map points (CC BY 4.0), for local speech where the state's language is only the court's | Villager names and greetings by language; "the court speaks Persian, we speak Telugu" | yes: name pools | <0.5 MB | medium |
| **Religions** | State infobox religion field: 973 states (63%); 321 "Religion in …" pages | Correlates of War World Religion Data 1945–2010 (shares per country every 5 years, 850 KB, free with citation) | Villager lines; later temples, churches and mosques in villages | yes | <0.5 MB | medium |
| **Famous people** | Year-page birth and death lines: 119,307 lines naming 85,175 people; 85,053 of them (99.9%) have a Wikidata id | Cross-verified notable people database (Sciences Po): 2.29 M people with birthplace and death-place coordinates, occupation and fame rank; matched by Wikidata id | Births and deaths as news where they happened; "famous locals"; real names by region and century | data-only first; optional for names | ~3 MB for 85 k people | medium |
| **Ways of life** | No usable table (articles only) | HYDE 3.2.1 land use (cropland, grazing, rice, irrigation, town vs country, same archive the mod already reads); ArchaeoGLOBE (CC0: 146 regions, 10 dates from 10,000 years ago to 1850) | Hunters, herders, farmers, rice growers, townsfolk: jobs, tools, animals | yes: villager jobs | ~1 MB | medium-high |
| **Trade routes** | Route articles exist (Silk Road, Incense trade route, Amber Road, Trans-Saharan trade, Grand Trunk Road, Royal Road, Tea Horse Road, Appian Way, Spice trade, Hanseatic League, Maritime Silk Road, Indian Ocean trade, Via Maris, King's Highway, Uttarapatha, Dakshinapatha), but no structured list | Itiner-e: Roman roads, most detailed, CC BY 4.0 (Zenodo). OWTRAD (Old World Trade Routes): land, river and sea routes of Eurasia and Africa, 4000 BC – c. 1820, 4,117 places on the World Historical Gazetteer; licence to check | Merchants and caravans on routes; busier route towns; caravan rumours | yes: merchants | ~1 MB | high |
| **Modern conflicts 1989–2024** | 9 "List of armed conflicts in …" pages; 78 "List of terrorist incidents in …" pages | UCDP GED 25.1 (CC BY 4.0): 385,918 events in 1,531 conflicts. Grouped by conflict, year and province: 27,868 hotspots; by 1° cell with 10+ deaths: 17,626 | Fighting nearby as news; soldiers on the roads | no | ~1 MB | low |

## Alternatives, per category

- **Kings and queens:**
  - Infobox leaders only: quick, but often just the first and last ruler.
  - Wikidata reigns: complete, but blocked today.
  - Keep state names only, as now.
- **Languages:**
  - Glottolog only: modern map, not history.
  - Hand-map the mod's culture ids to languages: fast, but coarse.
- **Religions:**
  - Seshat: non-commercial only.
  - Estimated spread from state religion: guesswork.
- **Famous people:**
  - Wikidata birthplaces: blocked today.
  - Read 85 k person articles' infoboxes from the dump: hours of download.
  - Fame-ranked people from the database alone: not Wikipedia-first.
- **Ways of life:**
  - D-PLACE named societies: non-commercial.
  - Rules from population density alone: no real data.
- **Trade routes:**
  - Estimated routes joining each era's big cities (Reba, Pleiades): "believable estimated life", like the population fill.
  - Roman roads only (Itiner-e).
- **Modern conflicts:**
  - ACLED: needs an account.
  - GDELT: huge and noisy.
  - Wikipedia lists only: thin before 2014.

## Recommended order

1. **Modern conflicts:** easy, data-only, about 17–28 k hotspots.
2. **Kings and queens, languages and religions:** one pass over the same state articles and leader lists, Wikipedia-first. Needs one mod change, so villagers can say who rules, what they speak and what they believe.
3. **Famous people:** births and deaths as news first, then real name pools.
4. **Ways of life:** HYDE land use plus ArchaeoGLOBE; villager jobs and animals. This is the biggest visible gain for ancient times.
5. **Trade routes:** Itiner-e plus Wikipedia route articles, OWTRAD after a licence check, and estimated routes elsewhere.

## Before starting

- **Space:**
  - The workspace is about 118.4 MB of the ~128 MB snapshot cap, and the plan needs about 6–8 MB.
  - Option A: gzip the mod's three big plain files (`deccan_rulers.json` 5.2 MB, `present_telangana.json` 4.8 MB, `events_world.json` 2.7 MB). That saves about 10 MB and needs a one-line mod change for the rulers file.
  - Option B: compress the old v1 harvest leftovers (~14 MB). Ask first.
- **Mod build:** the full compile works with
  `TOOL_XMX=300m DAEMON_XMX=440m METASPACE=280m bash worldfill/tools/gradle_compile.sh`.
- **Wikidata:** when its query service recovers, it can fill gaps as a secondary source (reigns, birthplaces, outbreaks).
- **Cache:** the state infoboxes are already cached in `~/.cache/wpdump/polity_infoboxes.jsonl.gz` (not snapshotted).
