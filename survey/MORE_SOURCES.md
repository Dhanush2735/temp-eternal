# More sources: what is still out there (checked 2026-10-11)

Short version: yes. More free data exists, and the downloads work today.
Only a few of these sources would change what a player actually sees.

## A. Changes what the player sees (recommended)

| # | Source | What it adds in the game | Size | Licence | Checked today |
|---|---|---|---|---|---|
| 1 | **HYDE 3.2.1 land use + town/country split** (same archive as step 4) | Estimated people become farmers, herders or rice growers. Urban and rural headcounts say whether a spot should be a town or a village. | A small 0.5° grid per layer once shrunk | Same as step 4 (readme CC BY 3.0, record CC0) | Every era has `cropland`, `grazing`, `pasture`, `rangeland`, rice (irrigated and rainfed), `tot_irri`, `popc`, `popd`, `rurc`, `urbc` and `uopp`. Step 4 only used `popc`. Read the members `baseline/asc/{yr}_lu/…` and `{yr}_pop/rurc_…`/`urbc_…` with `worldfill/remotezip.py` (`open_remote_zip`) from `archaeology.datastations.nl/api/access/datafile/5490328`. |
| 2 | **ArchaeoGLOBE** (Harvard Dataverse: data `doi:10.7910/DVN/CNCANQ`, regions `doi:10.7910/DVN/CQWUBI`) | Way of life for 146 world regions at 10 dates (10k, 8k, 6k, 4k, 3k, 2k and 1k BP, AD 1500, 1750 and 1850): hunting-gathering, herding, light farming, heavy farming and towns. Ancient estimated people stop being generic villagers. | 72 KB consensus table (file id 3442650); simplified regions 0.4 MB | CC0 1.0 | Downloaded and read: 146 regions, columns `FHG`/`PAS`/`EXAGR`/`INAG`/`URBAN` × date. Around 2000 BC: Southern India has foraging widespread with farming and herding common; Australia is foragers only; Egypt has heavy farming widespread. |
| 3 | **Glottolog 5.3** (`github.com/glottolog/glottolog-cldf`, `cldf/languages.csv`) | The local language for each map spot, giving better name pools where NPC names are still generic (8% of cell-years). | 2.5 MB | CC BY 4.0 | Downloaded: 8,618 languages, 8,304 of them with a map point |
| 4 | **historical-basemaps** (`github.com/aourednik/historical-basemaps`, `geojson/world_YYYY.geojson`) | A second opinion on who ruled where, to fix wrong kingdom labels (Antioch → Nabataea, Rome after 1500 → Naples). | About 1.2 MB per map; 49 maps from 3000 BC to 2010 | **GPL-3.0**: fine for an open-source mod, a problem for a closed one | 200 OK, updated 2026-09-15 |

## B. More rumours (nice extras)

- **NOAA NCEI** earthquakes, tsunamis and volcanoes (public domain). Endpoint checked earlier today.
- **Smithsonian GVP** Holocene eruptions. Checked earlier today.
- **Plague outbreaks in Europe, 1347–1900** (Zenodo record 14973). Checked earlier today.
- **NASA Five Millennium Canon of Solar Eclipses**, starting 1999 BC (public domain), for "the sun went dark at noon" rumours. `eclipse.gsfc.nasa.gov/SEcat5/` returned 200 today.
- **IBTrACS** storms and hurricanes since the 1840s (public domain). 333 MB raw; 200 today.
- **Correlates of War** (wars 1816–2007) and **UCDP GED** (1989–2024). Checked earlier today.
- **Notable people, 3500 BC–2018** (Sciences Po Dataverse `doi:10.21410/7E4/RDAG3O`, `cross-verified-database.csv.gz`, 261.5 MB, CC BY-SA 4.0). Useful for "a famous poet lives in this town" and for real local names by century.
- **ORBIS** Roman network (sites and routes). Checked earlier today.
- **Imperial Gazetteer of India, 1908** (`dsal.uchicago.edu/reference/gazetteer/`, 200 today). Founding stories for Indian towns, but it is page-by-page text and slow to collect.

## C. Blocked or not usable right now

- **Wikidata query service:** today it returns HTTP 429, "Aggressively rate-limiting to 1 req / min … during active wdqs outage", with Retry-After 1000 s. Real ruler names with reign dates would come from here, so try again later.
- **D-PLACE Ethnographic Atlas v3.3:** CC BY-NC 4.0 (non-commercial only).
- **Cliopatria:** v0.2.1 (2026-10-03) is the newest release and is already in the mod.
- **Found earlier:**
  - DefoeDB and SEDAC are down.
  - The ACLED and UCDP APIs need keys; the UCDP CSV download works without one.
  - EM-DAT requires a login.

## Limits

- **Space:** the workspace snapshot is about 115.5 MB of the ~128 MB cap (eternal 61.4, harvest 19.4, wiki_test 15.3, survey 9.8, terra3 9.2).
  - Raw downloads go to `~/.cache/srcdata/` (not saved); only shrunk results go into the mod.
  - Big extras need old test files compressed or removed first. Ask the user before deleting anything.
- **Duplicates:** every new event pack goes through `harvest/install_pack.py` duplicate removal.

## Recommended order

1. HYDE land use + town/country split.
2. ArchaeoGLOBE ways of life.
3. Optionally, a hazards + eclipses rumour pack.

After that, return to the visible fixes: show more people in big places, and shorten the rumours.
