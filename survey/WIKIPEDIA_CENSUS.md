# Wikipedia census: every year, 3000 BC to AD 2026

*This finishes `wiki_test/` and the Wikipedia part of `survey/`. The survey's other sources
(Wikidata classes, NOAA, Smithsonian, UCDP, COW, Pleiades, CHGIS, ORBIS, plague, cities, HYDE …)
are measured in [`OTHER_SOURCES_CENSUS.md`](OTHER_SOURCES_CENSUS.md). The survey sampled one
year in 50; 14 of its 100 pages were lost to HTTP 429 and the totals were extrapolated. The
wiki test spot-checked 14 years, and 12 of its 25 files were rate-limit error pages. This time
every year was measured on 2026-10-11 against live English Wikipedia and Wikidata. All 3,010
pages read are frozen in a snapshot, so every number below can be recomputed offline. The
completeness checks are in §8.*

---

## Verdict

- **All 5,026 years were resolved**, from 3000 BC to AD 2026 (there is no year 0), with 0 failures and 0 gaps.
- **2,568 years (51%) have their own article.** None exist before 669 BC. The rest redirect:
  1,301 to century pages (every year from 3000 to 1700 BC) and 1,157 to decade pages.
- Those years live on **2,707 distinct pages holding 182,263 bullet points**.
- Run through the harvester's own rules and `postprocess.py`, they yield **23,202 events**.
  That is the ceiling for a complete harvest of the pages years map to, with the current
  pipeline. It is 3.6× the 6,373 events in the current pack, and about one sixth of the
  survey's ~141,000 projection. Also reading the 292 decade/century/millennium pages that no
  year maps to would add **750–2,195** more (+3–9.5%; §3).
- **A complete harvest does not fix the empty world.** I re-ran the harvest report's density
  probe on the full total (38,519 events). The table comes out the same: at most 1% of random
  land points have an event within 100 km in nearly every year, with a peak of 4.3% in 1944.
- **Three bugs in the harvest pipeline turned up along the way** (AD titles, year sign,
  births/deaths leakage). Each is sized in §7. None were fixed here: this was a survey task,
  and nothing under `harvest/` or `eternal/` was modified.

![Coverage and yield per century](census/census_by_century.png)

---

## 1. What changed from the sample survey

| | Sample survey (`DATA_SOURCE_SURVEY.md`) | This census |
|---|---|---|
| Years measured | 100 (every 50th year, to AD 2000) | **5,026** (every year, to AD 2026) |
| Failed fetches | 14 (HTTP 429, never retried) | **0** (429s retried with backoff, never dropped) |
| Redirects | counted, not followed | followed to the page that actually holds the year |
| AD titles | bare `"500"`, often a disambiguation page | the right page for each year (§7.1) |
| "Geocodable" | bullet contains *any* wikilink | the harvester's own place rules + a Wikidata coordinate |
| Yield | extrapolated, ±40% | the harvester + `postprocess.py` run over every page |

## 2. Year coverage (the finished wiki test)

| Era | Years | Own article | → decade page | → century page | Distinct pages |
|---|---:|---:|---:|---:|---:|
| 3000–1001 BC | 2,000 | **0** | 699 | 1,301 | 84 |
| 1000–1 BC | 1,000 | 601 (60%) | 399 | 0 | 650 |
| AD 1–999 | 999 | 940 (94%) | 59 | 0 | 946 |
| 1000–1499 | 500 | 500 (100%) | 0 | 0 | 500 |
| 1500–1799 | 300 | 300 (100%) | 0 | 0 | 300 |
| 1800–2026 | 227 | 227 (100%) | 0 | 0 | 227 |
| **Total** | **5,026** | **2,568 (51%)** | **1,157** | **1,301** | **2,707** |

- **BC:** the earliest year article is 669 BC. Every year from the 5th to the 2nd century BC has
  one. From 669 BC onward, 68 years are still merged into decade pages (e.g. 753 BC → `750s BC`,
  1 BC → `0s BC`).
- **AD:** years 1–59 are merged into decade pages (`0s` … `50s`). **Every year from AD 60 on has
  its own article.**
- **Two survey figures were artefacts.** "1500–1799: 67% of years have articles" is actually
  **100%**: the two "missing" sample years (1500, 1550) were 429 failures. "AD 1–999: 79%" is
  actually **94%**.

The full per-year table is in `wiki_test/year_index.csv`. For each year it records the page,
the page type, the revision ID, and every title tested with what it resolved to.

## 3. The funnel: from bullet points to events

| Era | Bullets | Births/deaths filtered | No place link | With a place | Geocoded | **Kept** |
|---|---:|---:|---:|---:|---:|---:|
| 3000–1001 BC | 822 | 32 | 127 | 663 | 284 | **196** |
| 1000–1 BC | 6,199 | 627 | 813 | 4,759 | 1,999 | **1,638** |
| AD 1–999 | 19,043 | 4,032 | 2,774 | 12,237 | 3,645 | **3,265** |
| 1000–1499 | 23,465 | 9,357 | 5,011 | 9,097 | 4,903 | **3,929** |
| 1500–1799 | 43,525 | 29,302 | 6,121 | 8,102 | 4,622 | **4,056** |
| 1800–2026 | 89,209 | 37,943 | 28,078 | 23,188 | 11,201 | **10,118** |
| **Total** | **182,263** | **81,293 (45%)** | **42,924 (24%)** | **58,046 (32%)** | **26,654 (15%)** | **23,202 (13%)** |

- **Why the survey's headline was so high.** 180,043 bullets (98.8%) contain some wikilink. That
  is the survey's "99% geocodable", and it is where the ~141,000 came from. But a link is not a
  place, and a place does not always have coordinates.
- **Where the losses are.** Births and deaths account for almost half of all bullets. Of the
  bullets that do have a place link, only 46% resolve to Wikidata coordinates.
- **From geocoded to raw records.** The harvester drops 19 geocoded bullets whose cleaned
  name is under 12 characters and 33 exact duplicates, so 26,654 geocoded become 26,602 raw
  records (`census_raw_events.jsonl.gz`).
- **What postprocess drops.** Too short or too long: 2,594. List artefacts: 630. Museum
  notices: 119. Bad year: 57 (see §7.2). That is 3,400, leaving 23,202. In addition, 1,847
  years were "repaired".
- **Kinds kept.** 8,764 incident, 8,227 political, 2,004 battle, 1,341 disaster, 1,172 cultural,
  965 treaty, 729 siege.
- **Pages not counted.** 292 more pages exist that no year maps to: 248 decade, 37 century and 7
  millennium pages (e.g. `1640s`, `17th century`). They hold 16,455 bullets, 7,725 of them with
  a place. They are left out of the totals above because the harvester never fetches them.
  `census/overview_audit.py` measured what they would add: it geocoded their 3,124 new place
  titles (0 unresolved) and matched every resulting record against the year-page records.

  | Of the 2,983 records the harvester would emit from them | Records |
  |---|---:|
  | Same event text as a year-page record in the same period | 534 (18%) |
  | Same place in the same period, different wording (may or may not be the same event) | 1,605 (54%) |
  | No counterpart on any year page | 844 (28%) |
  | **Kept by `postprocess.py`: new only / new + same-place** | **750 / 2,195** |

  So they overlap less than first assumed. Reading them would add 3–9.5% to the 23,202. In
  3000–1001 BC, 48–99 of the additions would land on the 196 existing events. Another 110–273
  of the additions fall outside 3000 BC–AD 2026. These are undated bullets on `21st century`,
  `3rd millennium` and `4th millennium BC`, which the harvester can only date to the page
  midpoint.

## 4. The sample survey's estimates vs the census

| Era | Survey: years with articles | Census | Survey: est. geocodable events | Census: geocoded | Census: kept |
|---|---:|---:|---:|---:|---:|
| 3000–1001 BC | 0% | 0% | ~900 (3000–700 BC) | 284 | 196 |
| 1000–1 BC | 55% | 60% | ~8,000 | 1,999 | 1,638 |
| AD 1–999 | 79% | 94% | ~26,000 | 3,645 | 3,265 |
| 1000–1499 | 100% | 100% | ~27,000 | 4,903 | 3,929 |
| 1500–1799 | 67% | 100% | ~26,000 | 4,622 | 4,056 |
| 1800–now | 100% | 100% | ~54,000 | 11,201 | 10,118 |
| **Total** | | **51%** | **~141,000** | **26,654** | **23,202** |

The survey's "~900 for 3000–700 BC" was the closest of its guesses. The census finds 1,193
bullets on the 114 pages that cover that range, and 318 events survive from them.

## 5. Today's pack vs a complete harvest

| Era | Current pack (6,373) | Complete harvest | × |
|---|---:|---:|---:|
| 3000–1001 BC | 182 | 196 | 1.1 |
| 1000–1 BC | 521 | 1,638 | 3.1 |
| AD 1–999 | 1,089 | 3,265 | 3.0 |
| 1000–1499 | 420 | 3,929 | **9.4** |
| 1500–1799 | 645 | 4,056 | **6.3** |
| 1800–2026 | 3,497 | 10,118 | 2.9 |
| Year 0 (does not exist) | 19 | 0 | — |
| **Total** | **6,373** | **23,202** | 3.6 |

**19 events in today's pack are dated year 0.** All come from the `0s BC` page. Their raw year
fails the plausibility check, and the "repair" sets them to `postprocess.page_year('0s BC')`,
which returns 0. The repair runs *after* the `year == 0` guard, so they slip through. This is
another side of §7.2.

The 3rd and 2nd millennia BC have little more to give. The pages that years map to yield 196
events. Fixing the sign bug would add 56 (§7.2), and reading the overview pages 48–99 (§3).
That is still only about 300–350 events for 2,000 years. Most of what a complete harvest would
add is AD 1000–1799, which pass 1 sampled only every 3rd or 4th year and pass 3 never reached.

## 6. The empty-world question

`density_probe.py` is an exact Python port of `eternal/DensityProbe.java`. It uses the same
`java.util.Random(42)` sequence, so it samples the same 400 land points, with the same land
boxes, the same `HistoryGazetteer` loading rules and the same haversine formula. On today's data
it reproduces the harvest report's published table digit for digit, which validates the port.
The table below shows the percentage of random land points with an event within R km.

| Year | A: today, 21,690 events (25 / 50 / 100 km) | B: complete harvest, 38,519 events (25 / 50 / 100 km) |
|---:|---|---|
| −2500 | 0.0 / 0.0 / 0.0 | 0.0 / 0.0 / 0.0 |
| −1500 | 0.0 / 0.0 / 0.0 | 0.0 / 0.0 / 0.0 |
| −500 | 0.0 / 0.0 / 0.3 | 0.0 / 0.0 / 0.3 |
| 1 | 0.0 / 0.0 / 0.0 | 0.0 / 0.0 / 0.3 |
| 500 | 0.0 / 0.3 / 0.3 | 0.0 / 0.0 / 0.0 |
| 1000 | 0.0 / 0.0 / 0.0 | 0.0 / 0.0 / 0.0 |
| 1300 | 0.0 / 0.0 / 0.8 | 0.0 / 0.0 / 0.8 |
| 1500 | 0.0 / 0.0 / 0.0 | 0.0 / 0.0 / 0.0 |
| 1700 | 0.0 / 0.0 / 0.5 | 0.0 / 0.0 / 1.0 |
| 1850 | 0.0 / 0.0 / 0.0 | 0.0 / 0.0 / 0.0 |
| 1900 | 0.0 / 0.0 / 0.0 | 0.0 / 0.0 / 0.0 |
| 1944 | 0.3 / 1.3 / 4.3 | 0.3 / 1.3 / 4.3 |
| 2000 | 0.0 / 0.3 / 1.0 | 0.0 / 0.3 / 1.0 |

**Finishing the harvest leaves this table essentially unchanged.** A point event is active for
exactly one year (`start <= year < end`, with `end = start + 1`). So 23,202 events spread over
5,026 years add only about 4–5 live events worldwide in any given year. That is the measured
version of the harvest report's conclusion: the world stays empty unless events last longer or
presence is generated from a regional rate. Having more Wikipedia points does not help.

(The one hit at AD 500 in today's data is "Florida State Road 500". It is junk from the `500`
disambiguation page, placed in Florida in the year 500. See §7.1.)

## 7. Bugs in the harvest pipeline (found and sized, not fixed)

### 7.1 For AD years, the bare number is often not the year article

`harvester.targets_for_year()` fetches `"500"` for AD 500. The survey and the wiki test did the
same. But `500`, `999`, `1000`, `747`, `911` and others are **disambiguation pages**, and `1`,
`2` and `100` are **articles about the numbers**. The real year pages are `AD 500`, … or, for
AD 1–59, the decade pages. The census resolves `N (year)`, `AD N` and `N` for every year. It
prefers a real year article, checked against the year stated in its `{{Year nav}}` template,
over decade or century redirects. This also catches stale redirects such as `386 (year)` →
`380s`, when the article `386` exists.

- **The bare title is right only from AD 201 on**, with 26 exceptions after that: 311, 360,
  365, 383, 404, 411, 420, 442, 500, 502, 666, 679, 707, 711, 727, 737, 747, 757, 767, 777,
  787, 808, 888, 911, 999 and 1000.
- **Harvest:** 221 raw records came from 100 wrong pages, and **107 of them are in the current
  6,373-event pack**. Examples: "500 Brickell in Miami", "Area code 360", "+420, calling code
  of the Czech Republic", and "Hundred Years' War" from the number article `100`. Meanwhile
  **226 of the AD years the harvest asked for never had their real page harvested.**
- **Survey and wiki test:** the sampled "articles" `500` and `1000` were disambiguation pages.
  `wiki_test/ce_500.json` (5,150 chars) and `ce_1000.json` (1,232 chars) are exactly those
  pages.

### 7.2 Year signs are mixed up between `harvest_run.py` and `postprocess.py`

- **The cause.** `harvest_run.py` stores explicit "N BC" years as −N, which is the *mod's*
  convention. `postprocess.py` assumes the *harvester's* convention (+ = BC) and negates every
  year. So BC dates become AD dates.
- **Dates past AD 2100 are dropped outright.** That is most of the 3rd millennium BC. Its 10
  century pages yield 78 geocoded bullets. With the sign corrected, 69 would be kept; the
  current pipeline keeps 13, and drops 56 as "dates past AD 2100". "c. 3000 BC: Stonehenge
  begins to be built" never reaches the pack.
- **The rest are "repaired" to the page's midpoint year.** Of BC events whose bullet states a
  year, only **94 of 394 (24%)** keep it. In today's 6,373-event pack, 72 of 270 (27%) do.
- **Year 0.** The repair can also produce year 0, which does not exist (19 events today; §5).
- **With the convention corrected** (measured by replay in `census/pipeline_bug_impact.py`):
  23,259 events are kept (+57), BC events keep their stated year **394 of 440 times (90%)**, and
  "repairs" fall from 1,847 to 58.

### 7.3 Births and deaths leak into events

- **65% of all bullets (119,284) sit in Births or Deaths sections.** The harvester's text regex
  catches most of them, but **1,818 still survive into the 23,202 events (7.8%)**. Examples:
  "King Parikshit of Kuru dynasty is born" and "841 BC—Baal-Eser II, king of Tyre".
- **Possible fix:** a section-aware filter that skips bullets under `== Births ==` and
  `== Deaths ==` would remove them. The census already records the section of every bullet.

### 7.4 Not a bug, but why the harvest crawled: Wikimedia's 2026 rate limits

- **The limits.** Wikimedia introduced
  [API rate limits](https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits) in 2026:
  **10 requests/min** for clients without contact information in the User-Agent, and
  **200/min** with an email or URL in it.
- **Why it mattered here.** Every harvest and survey script uses a User-Agent without contact
  information, which puts them in the 10/min tier. That explains the constant 429s that split
  the harvest into passes and caused its bug #4.
- **How this census stayed under the cap.** It batched 50 titles per call, paced calls every
  6.2 s, and resolved place titles through Wikidata query-service sitelinks. Those queries are
  not under the cap and handle 250 titles each. The whole run took about 350 Action API calls,
  97 query-service queries, and about 40 minutes.
- **To run 20× faster:** put a real contact address in the User-Agent, for example
  `CENSUS_UA="EternalEngineSurvey/2.0 (you@example.org)" python3 census.py all`.

---

## 8. Completeness checks (what was verified, and how)

Every figure below is recomputed offline by `census/audit_checks.py` (→ `audit_checks.json`) or
`census/overview_audit.py` (→ `overview_audit.json`).

| Check | Result |
|---|---|
| Every year from 3000 BC to AD 2026 appears once in `year_index.csv` | **5,026 of 5,026**; none missing, none extra, no year 0 |
| Each year's page is in the snapshot, at the same revision | **5,026 of 5,026**; 0 revision mismatches |
| A year sent to a decade/century page although its own article exists | **0** (every candidate title checked) |
| Snapshot pages that are empty, redirects or error pages | **0 of 3,010**. Page `429` mentions "HTTP 429" only in its hatnote. |
| The 303 snapshot pages that no year maps to | 292 overview pages (measured in §3) + 11 number articles (`1`–`10`, `100`) fetched as title candidates |
| Does the census replay match the real harvest? | On the 726 pages both read, **7,196 of the harvest's 7,203 records are reproduced word for word (99.9%)**. The 7 differences are on 3 pages edited since (`1390`, `1596`, `540 BC`). |
| The 102 harvest pages the census does not use | the wrong pages of §7.1 (`20`, `100`, `360`, `500` …) plus spelling variants (`1640s_BC`, `500s BC (decade)`) |
| The 25 `wiki_test` files | all valid `action=parse` responses. The 10 small files (124–147 bytes) are genuine redirects, e.g. `3000 BC` → `30th century BC`. |
| Parser coverage | Census and harvester share the same code (`import harvester`): nested `**` bullets are included, while prose and tables are skipped by design. Geocoding follows `geo.py`'s rules and was seeded with the harvest's own cache. |
| Restore of the two zip exports | All 1,078 files are back, byte-identical, apart from deliberate changes. One exception: `jdk_new` (Temurin 17, 50 MB) does not fit the workspace; see `libs/get_jdk17.sh`. |

## 9. Files

**`survey/`**
- `WIKIPEDIA_CENSUS.md`: this report. `DATA_SOURCE_SURVEY.md` now carries a note pointing here.
- `census/census.py`: the census itself. Stages: `resolve fetch classify measure geocode
  report retest`; each one resumes if interrupted.
- `census/census_by_century.csv`, `census_by_century.png`, `census_summary.json`.
- `census/census_pages.csv`: the funnel for each of the 2,707 pages years map to, plus the 292
  pages that were measured but not counted.
- `census/census_raw_events.jsonl.gz`: 26,602 raw records in the harvest's own format.
- `census/census_events_postprocessed.json.gz`: 23,202 events in the mod's pack format.
  **Not installed**, because it still carries the bugs in §7.2 and §7.3.
- `census/geo_cache_census.json`: 35,008 title → coordinate entries (the harvest cache plus
  20,692 new ones). `harvest/geo_cache.json` was not touched.
- `census/harvest_title_audit.*`, `pipeline_bug_impact.*`, `density_probe.*`: the measurements
  behind §5–§7.
- `census/overview_audit.*`: what the 292 overview pages would add (§3).
  `census/work/geo_cache_overview.json` holds their 3,124 newly geocoded titles, kept separate
  so the census cache stays frozen.
- `census/audit_checks.*`: the completeness checks of §8, plus exact values for §4, §5 and §7.2.
- `OTHER_SOURCES_CENSUS.md` and `sources/`: the survey's non-Wikipedia sources.
- `census/work/`: intermediate state (title resolutions, the year → page mapping, page types,
  request counts, the run log).
- `e_q*.json`: the five empty Wikidata files, now filled. Q174770 and Q178673 are a Spanish
  author and "vocal register", so those two IDs look like typos; they were fetched as written.

**`wiki_test/`**
- The 25 original files. The 12 that held HTTP 429 error pages now hold the real responses,
  fetched with the same call (`action=parse&prop=wikitext`).
- `year_index.csv`: one row per year from 3000 BC to AD 2026.
- `snapshot/pages.jsonl.gz`: all 3,010 pages read, with wikitext and revision IDs (latest
  revision 2026-10-11 09:08 UTC), 14.3 MB. The harvest could be re-run from this offline,
  without any API calls.

## 10. Reproduce

```bash
cd ~/survey/census
python3 census.py all                        # full run over the network (~40 min at 10 req/min)
python3 census.py classify measure report    # offline, from the snapshot
python3 harvest_title_audit.py && python3 pipeline_bug_impact.py && python3 density_probe.py
python3 overview_audit.py                    # offline once work/geo_cache_overview.json exists
python3 audit_checks.py                      # offline; needs the harvest/ raw files
```

## Caveats

- **These numbers describe the current harvester.** "Kept" means the harvester's existing
  rules: the first plausible place link (or a named event) must have a Wikidata coordinate.
  Better place-finding or classification would change the numbers. It would not change the
  density result, which comes from one-year event windows.
- **Wikipedia changes daily.** The snapshot pins the exact revisions that were measured.
- **The density probe is coarse by design.** It uses `DensityProbe.java`'s rough land boxes and
  400 points, exactly as the harvest report did. It counts point events only, not sites,
  population or crowds. `OTHER_SOURCES_CENSUS.md` runs the same probe on long-lived places,
  administrative seats and cities, and on the mod's existing sites.
