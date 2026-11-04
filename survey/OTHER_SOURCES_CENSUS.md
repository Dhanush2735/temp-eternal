> **Progress, 2026-10-11:** all four steps of the plan are done.
> - Step 1: the fixed Wikipedia harvest, 19,368 events; see `harvest/FIXES.md`.
> - Step 2: long-lived places, 18,677 Pleiades, 10,446 CHGIS and 1,787 Reba sites.
> - Step 3: 6,040 more Wikidata battles, sieges, treaties and war theatres, plus world rulers from
>   Cliopatria.
> - Step 4: estimated people from HYDE 3.2.1.
>
> See `worldfill/README.md`.

# Other sources census: the survey's non-Wikipedia sources, 3000 BC to AD 2026

*This finishes the rest of `survey/`: §2 (Wikidata) and the sources in §3 and §6 item 6 of
`DATA_SOURCE_SURVEY.md` that were marked "not opened yet", ⚠️ or ❌. On 2026-10-11 every
source was opened (or ruled out): licence and format checked, and dated, geocoded records
counted per era from 3000 BC to AD 2026. "New" means not already in the mod's packs. Wikidata
items are matched by QID. Hazard records are matched against the mod's disasters (same year,
≤ 150 km). The Wikipedia year pages are covered separately in
[`WIKIPEDIA_CENSUS.md`](WIKIPEDIA_CENSUS.md).*

---

## Verdict

- **Every listed source is now accounted for.** 11 were downloaded and measured. 2 need an
  account (ACLED, EM-DAT). HYDE was checked but not downloaded (5.5 GB). 2 entries do not exist
  as described: "DefoeDB" has no DNS record at all, and "Million Cities / GRUMP" points at an
  unreachable, non-historical dataset. Real replacements for both are measured below.
- **Plenty of new dated, geocoded events exist, but none of them fix the empty world.** They
  are one-year point events, exactly like the Wikipedia ones. Adding all ~415,000 new ones
  (NOAA, Smithsonian, UCDP, plague) leaves the density probe at about 1% of land points with
  something within 100 km in most years. 2000 is the exception, at 7%, because UCDP covers
  1989–2024.
- **Long-lived places do fix it.** Pleiades places, CHGIS administrative seats and the
  historical-cities dataset all carry date ranges. With them, 17–22% of land points have
  something alive within 100 km from AD 1 on, and 4–9% in 2500–500 BC. Today the mod's own
  15,954 sites reach at most 1.5%, because 15,727 of them are in Telangana.
- **The survey's Wikidata section had real errors.**
  - Its "wars" class (Q124734) is actually *rebellion*.
  - Battles are not exhausted: **4,431 more** are usable through their location's coordinates
    (P276).
  - Sieges add **+900**, not "+1,500".

## 1. What each source is

| Source | What it holds | Access (tested 2026-10-11) | Licence | Span | Records |
|---|---|---|---|---|---:|
| Wikidata (§3) | battles, sieges, wars, treaties, disasters, outbreaks | open SPARQL. GET works; POST is answered with HTTP 429 from this client. | CC0 | — | see §3 |
| **NOAA NCEI hazards** | significant earthquakes, tsunamis, volcanic eruptions | open JSON API (`hazard-service/api/v1`); the survey's "moved endpoint" is this | US government data | 2150 BC– / 2000 BC– / 4360 BC– | 6,697 / 3,136 / 903 |
| **Smithsonian GVP** | Holocene eruptions, with start/end years | the website returns 403 to bots, but the **WFS is open** | not stated in the data; citation requested | Holocene → 2026 | 11,089 |
| **UCDP GED 25.1** | georeferenced conflict events, day-dated | open CSV (29 MB zip); the API needs a token (401) | CC BY 4.0 | 1989–2024 | 385,918 |
| **Correlates of War v4** | wars: inter-, intra-, extra- and non-state | open CSVs | free; citation requested | 1816–2007 | 652 wars, **no coordinates** |
| **Pleiades** | ancient places, with attested date ranges | open daily dumps | CC BY 3.0 | prehistory → modern | 42,493 places |
| **CHGIS V6** | Chinese county & prefecture seats, with begin/end years | open on Harvard Dataverse | county: CC0; prefecture: CHGIS EULA (click-through) | 763 BC–1911 | 10,522 + 5,226 |
| **Reba et al. 2016** | cities with population series (Chandler, Modelski) | open on figshare (the SEDAC mirror is unreachable) | CC BY 4.0 | 3700 BC–AD 2000 | 1,597 + 154 + 293 |
| **Plague (Biraben)** | plague outbreaks: Biraben, digitised by Büntgen 2012 + Atanasiu 2008, merged by Schmid 2015 | open on Zenodo (record 14973) | repository under EPL-1.0 | 1339–1900 | 7,711 |
| **ORBIS** | Roman network nodes + routes | `o_sites.csv` / `new_routes.topojson` behind the web app | data licence not stated; tiles CC BY-NC 3.0 | one snapshot, ~AD 200 | 844 nodes (640 named), **no dates** |
| **HYDE 3.2.1** | population & land-use grids, 5 arcmin | open on DANS, 5.5 GB; not downloaded | readme says CC BY 3.0, DANS says CC0 (conflict) | 10,000 BCE–2015 | 1000-yr steps BCE, 100-yr to 1700, 10-yr to 2000, then yearly |
| ACLED | conflict events | API: HTTP 403 without a key → **needs an account** | ACLED terms | — | not measured |
| EM-DAT | disasters | login page → **needs an account** | EM-DAT terms | — | not measured |
| "DefoeDB" | — | `defoedb.cambridge.org` has **no DNS record**: it does not exist | — | — | replaced by the plague data above |
| "Million Cities / GRUMP" | — | SEDAC unreachable; GRUMP is a ~2000 urban map anyway | — | — | replaced by Reba et al. above |

## 2. Dated, geocoded records per era (3000 BC – AD 2026)

Counted by start year. Long-lived records that began before 3000 BC are counted in the first era.

| Source | 3000–1001 BC | 1000–1 BC | AD 1–999 | 1000–1499 | 1500–1799 | 1800–2026 | **In range** | **New vs mod** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| *Point events* | | | | | | | | |
| NOAA earthquakes | 9 | 38 | 242 | 318 | 891 | 5,136 | 6,634 | **4,723** |
| NOAA tsunamis | 4 | 20 | 69 | 63 | 382 | 2,132 | 2,670 | **2,032** |
| NOAA volcanoes | 13 | 6 | 26 | 31 | 141 | 680 | 897 | **821** |
| Smithsonian eruptions | 653 | 483 | 693 | 534 | 1,282 | 6,266 | 9,911 | **9,731** |
| UCDP GED | 0 | 0 | 0 | 0 | 0 | 385,918 | 385,918 | **385,918** |
| Plague outbreaks | 0 | 0 | 0 | 2,031 | 5,595 | 85 | 7,711 | **7,711** |
| *Long-lived presence* | | | | | | | | |
| Pleiades places | 1,505 | 27,029 | 2,952 | 108 | 982 | 577 | 33,153 | all |
| CHGIS seats | 0 | 1,549 | 9,806 | 3,306 | 781 | 277 | 15,720 | all |
| Cities (Reba et al.) | 87 | 109 | 169 | 287 | 245 | 1,146 | 2,043 | all |

- **Overlaps between sources.** NOAA volcanoes are largely a subset of Smithsonian's, and many
  NOAA tsunamis are caused by NOAA earthquakes. Deduplicate before installing.
- **Data quality.** Pleiades dates are period-based, e.g. "Roman" = 30 BC–AD 300; the median
  place spans 671 years. Smithsonian has 1,178 more eruptions before 3000 BC.

## 3. Wikidata, finished (survey §2)

`sources/wikidata_eras.py` runs one query per class. For each item it fetches the earliest
date (P580 or P585) and coordinates: the item's own P625, or the P625 of its P276 location. It
then checks every QID against the 14,934 Wikidata events already in `events_world.json`.

| Class (QID) | Dated + geocoded | …own P625 only | Already in mod | **New** | New by era (3000–1001 BC / 1000–1 BC / AD 1–999 / 1000–1499 / 1500–1799 / 1800–2026) |
|---|---:|---:|---:|---:|---|
| battle (Q178561) | 12,419 | 8,001 | 7,988 | **4,431** | 9 / 198 / 372 / 631 / 990 / 2,231 |
| siege (Q188055) | 3,634 | 2,736 | 2,734 | **900** | 1 / 63 / 70 / 291 / 352 / 123 |
| war (Q198) | 1,135 | 87 | 2 | **1,133** | 3 / 123 / 89 / 219 / 299 / 400 |
| treaty (label, as in the survey) | 1,186 | 69 | 0 | **1,186** | 1 / 6 / 13 / 192 / 271 / 703 |
| flood (Q8068) | 361 | 110 | 0 | **361** | 0 / 2 / 0 / 4 / 11 / 344 |
| famine (Q168247) | 27 | 10 | 0 | 27 | 0 / 0 / 0 / 4 / 5 / 18 |
| earthquake (Q7944) | 2,274 | 2,240 | 2,237 | 37 | the mod's "disasters" are these |
| disease outbreak (Q3241045) | 1,901 | 336 | 0 | 1,901 | 1,894 of them after 1800 (mostly COVID-19 by region) |
| epidemic / pandemic (by label) | 59 / 11 | 14 / 0 | 0 | 59 / 11 | almost all after 1500 |

- **The survey's own-coordinate counts were right, but it missed the P276 route.** The mod's
  7,989 battles match the 8,001 that have their own coordinates. Only 13 of the 4,431 new
  battles have their own P625; the rest are placed via their location's coordinates. Wars work
  the same way: 85 of 1,133 have their own P625.
- **Wrong class IDs in the survey.**
  - Q124734, used for "wars", is *rebellion*.
  - Q131361, Q4426883 and Q17000908 are *irony*, *Viktor Soyfer* and *Australian Construction
    Contracts*.
  - The survey already noticed that the last three returned nothing.
- **Wars and treaties are multi-year or place-anchored.** Wars carry start and end dates. Of all
  the event data here, they come closest to the "longer events" the density result calls for.

## 4. The empty-world probe with these sources

This is the same probe as in `WIKIPEDIA_CENSUS.md` §6: the exact 400 land points of
`DensityProbe.java`, and `HistoryGazetteer`'s `start <= year < end` rule. Point events last one
year. Places, seats and cities stay alive for their whole date range. The table shows the
percentage of land points with something alive within **100 km** (50 km in brackets).

| Year | A: today's events (21,690) | + all new point events (≈415k) | Mod's existing sites (15,954)¹ | Sites + Pleiades + CHGIS + cities | Pleiades alone | Cities alone |
|---:|---:|---:|---:|---:|---:|---:|
| −2500 | 0.0 | 0.0 | 0.8 (0.5) | **4.0** (1.5) | 3.8 | 0.3 |
| −1500 | 0.0 | 0.3 | 0.3 (0.3) | **5.0** (2.8) | 5.0 | 0.5 |
| −500 | 0.3 | 0.3 | 0.8 (0.3) | **8.8** (6.0) | 8.3 | 1.0 |
| 1 | 0.0 | 0.0 | 1.0 (0.0) | **19.3** (12.8) | 15.5 | 0.5 |
| 500 | 0.3 | 0.3 | 0.5 (0.0) | **18.3** (12.0) | 13.8 | 0.8 |
| 1000 | 0.0 | 0.0 | 0.5 (0.0) | **18.3** (12.3) | 12.8 | 2.8 |
| 1300 | 0.8 | 1.0 | 1.0 (0.3) | **19.3** (13.5) | 12.8 | 4.8 |
| 1500 | 0.0 | 1.0 | 1.5 (0.3) | **19.3** (13.8) | 12.8 | 6.3 |
| 1700 | 0.5 | 1.0 | 1.5 (0.3) | **19.0** (14.0) | 12.8 | 7.3 |
| 1850 | 0.0 | 0.8 | 1.5 (0.3) | **19.8** (13.5) | 12.8 | 9.3 |
| 1900 | 0.0 | 0.5 | 1.5 (0.3) | **21.5** (14.3) | 12.8 | 11.5 |
| 1944 | 4.3 | 4.5 | 1.5 (0.3) | **16.8** (10.3) | 12.8 | 7.0 |
| 2000 | 1.0 | 7.0 | 1.5 (0.3) | **16.8** (11.3) | 13.0 | 5.3 |

¹ Only 227 sites have an explicit `occupiedStart`; the mod estimates the rest in Java. This
column is the upper bound, with every site alive until `occupiedEnd`. The lower bound
(explicit starts only) gives the same figures: 15,727 of the sites are in Telangana, so only a
handful of the 400 world points are near any site.

- **What it means.** The empty world is a duration problem, not a quantity problem. ~415,000
  extra one-year events add about 1 point in 100. ~51,000 long-lived places, seats and cities
  add 15–20. CHGIS covers China only, 763 BC–1911, which is why it drops out in 1944 and 2000.
  Pleiades is Greco-Roman and Near Eastern.
- **How they would enter the mod.** As sites or presence, which `HistoryGazetteer` already
  models with `occupiedStart`/`occupiedEnd`, rather than as events. The probe treats them as
  multi-year events only to put them on the same scale.
- **What the probe left out.** The new Wikidata items (~8,000 one-year events) were not added
  to the probe. At about 1.6 live events a year worldwide, they cannot move it.

## 5. Corrections to `DATA_SOURCE_SURVEY.md`

1. **§2 Wars** used Q124734, which is *rebellion*. Real wars (Q198): 1,740 dated in range,
   1,135 geocoded (mostly via P276), 1,133 not in the mod.
2. **§2 Battles, "nothing left to gain"**: there are **+4,431** via P276 location coordinates.
3. **§2 Sieges, "3,915 … roughly +1,500"**: 3,916 is the raw total. 3,634 are dated and
   geocoded, 2,734 are already in the mod, so the gain is **+900**.
4. **§2 Treaties and epidemics** hold up: 1,186 treaties (the survey said 1,193; Wikidata has
   changed since), and epidemics are near zero before 1800. But a real plague dataset exists:
   7,711 outbreaks 1339–1900. The "disease outbreak" class has 1,901 items, almost all modern.
5. **§3 DefoeDB** does not exist (no DNS record).
6. **§3 HYDE, "bot-blocked"**: it is open on DANS (5.5 GB), with a licence conflict (CC BY 3.0
   vs CC0).
7. **§3 Million Cities / GRUMP**: the historical dataset is Reba et al. 2016 (CC BY 4.0).
8. **§3 Smithsonian, "HTTP 403"**: only the website blocks bots. The WFS serves all 11,089
   eruptions.
9. **§3 NGDC, "endpoint moved"**: the hazard-service API works, with 6,697 quakes from 2150 BC.
10. **§3 CHGIS, "not opened"**: open on Dataverse (county points CC0), with 15,720 dated seats.
11. **§3 UCDP, "1946 onward"**: the *georeferenced* events (GED) cover 1989–2024.
12. **§3 COW**: 652 wars 1816–2007, but **without coordinates**, so they need geocoding first.
13. **§3 ORBIS**: one undated snapshot (~AD 200) of 844 network nodes. Useful for routes, not
    for events.

## 6. Files and reproduction

**`survey/sources/`**
- `fetch_sources.py`: downloads every open source into `/tmp/srcdata`. The raw data is kept
  outside the workspace (≈100 MB vs the ~128 MB snapshot cap).
- `sources_census.py` → `sources_summary.json` (per source: access, licence, counts per era,
  overlap with the mod) and `sources_density.json` (every probe table, at 25/50/100 km).
  The numpy probe is asserted to match the exact port in `census/density_probe.py`.
- `wikidata_eras.py` → `wikidata_eras.json` (per class, per era, new vs mod) and
  `wikidata_items.json.gz` (QID, year and own-coordinate flag for every dated, geocoded item).

```bash
cd ~/survey/sources
python3 fetch_sources.py && python3 sources_census.py   # ~1 min after downloading
python3 wikidata_eras.py                                # ~40 s, Wikidata query service
```

## Caveats

- **"New vs mod" for hazards is a proximity match** (same year, ≤ 150 km). Wikidata classes
  are matched exactly by QID.
- **Nothing was installed.** These are measurements. Before use, each source needs
  deduplication against the others and a kind/effect mapping.
- **Licences need a decision for redistribution.** That applies to the CHGIS prefecture EULA,
  the HYDE conflict, the plague repository (EPL-1.0) and ORBIS (unstated). UCDP, Reba et al.,
  Pleiades and the CHGIS county points are openly licensed.

Storage note: generated `sources/sources_density.json` is archived as `.json.xz`. Verify or restore with `python r2_wikipedia/archive_generated_aux.py survey/sources/sources_density.json [--restore]`; restoration requires headroom and refuses overwrite.

Storage note: generated `sources/sources_summary.json` is archived as `.json.xz`; verify or restore with `python r2_wikipedia/archive_generated_aux.py survey/sources/sources_summary.json [--restore]`. Restore requires headroom and refuses overwrite.
