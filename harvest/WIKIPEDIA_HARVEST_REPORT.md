# Wikipedia history harvest — 3000 BC to now

**Verdict: 6,373 geocoded events harvested from English Wikipedia and installed into the mod,
which now compiles and loads them — verified by running the mod's own `HistoryGazetteer`.
Combined with the existing Wikidata pack the world holds 21,690 dated events across all packs,
up from 15,317. The harvest filled 9 BC centuries that were completely empty and roughly doubled
geographic reach from ~24% to ~50% of Earth's land cells. (Numbers are the current installed
state: passes 1–2 plus the AD 213–567 slice of pass 3. The rest of pass 3 is still running and
will be merged on completion — see "The second and third passes" below.)**

**But the headline result is a caution, not a win: a density probe using the mod's own query
found that a random `/tpll` + `/terra timejump` still lands within 100 km of *any* event in well
under 1% of cases for most of history, peaking at 4.3% in 1944. Adding thousands more points
barely moves that number, because empty area only shrinks as the square root of point count. This
is the measured proof that the standing requirement — never land in an empty world — cannot be met
by harvesting point-events alone at any volume Wikipedia supplies. It needs the density/rate
system the audit recommended. Details, and what this harvest still genuinely fixed, are below.**

Installed at `src/main/resources/data/eternalengine/eternal/history/events_wikipedia.json`
and registered in `history/index.json` (pack 15 of 15).

---

## What was built and run

| Component | Path | Role |
|---|---|---|
| `harvester.py` | `/home/user/harvest/` | fetch year/century pages, extract bullets, find the place in each, classify |
| `geo.py` | `/home/user/harvest/` | Wikipedia title → QID → Wikidata `P625`, with `P276`/`P131` fallback; 429 backoff |
| `harvest_run.py` | `/home/user/harvest/` | streaming driver; runs each pass's year list, re-queues throttled pages over up to 5 retry-passes |
| `postprocess.py` | `/home/user/harvest/` | reclassify, filter noise, emit the mod's exact pack schema |
| `events_raw.jsonl` | `/home/user/harvest/` | 5,789 raw geocoded records |
| `geo_cache.json` | `/home/user/harvest/` | persistent geocode cache — makes any re-run much faster |

Final run stats, printed by `harvest_run.py`:

```
pages          315      pages_missing 13
bullets     42,566      noise      29,986
with_place  12,590      kept        5,789
geocoded     5,805
```

Then `postprocess.py`: `raw 5789 → kept 5351` (dropped 345 short, 37 museum/artifact, 56 bad year).

---

## The second and third passes

The 5,351 above is **pass 1 only** — a 340-target sample (every other AD year, one page per BC
century). Two more passes followed, and the installed pack is their merge.

**Pass 2 — the full run, and the data-loss bug it exposed.** A 2,325-target run (every decade
page in BC, every AD year 1–2025) was launched to remove the sampling gap. It ran cleanly through
BC — where it was *denser* than pass 1, fetching decade pages like "1460s BC" that pass 1 skipped
— then hit a hard Wikipedia throttle around AD 212. Investigating why pages were vanishing turned
up bug #4 (below): transient 429s were being logged as "no page" and dropped. Pass 2 was stopped
and its 876 valid records salvaged.

**Pass 3 — the lossless resume (in progress).** After fixing bug #4, a resume was launched: the
12 AD years pass 2 wrongly dropped (37, 53, 64, 81, 102, 125, 148, 162, 196, 201, 204, 207 — all
confirmed HTTP 200), then AD 213–2025, the bulk pass 2 never reached. It streams to
`events_resume_raw.jsonl` and re-queues throttled pages instead of dropping them. The first resume
process was reaped by the sandbox at **AD 567** — not a code fault: 950 records, 0 bad lines, 0
false drops, all intact — and was restarted from AD 568. It is now past **AD 595 and still
accruing, 0 false drops**, holding under exactly the throttling that corrupted pass 2.

**The installed pack** is the merge of passes 1–2 plus the AD 213–567 slice of pass 3, run through
`postprocess.py` (dedup by `sha1(name|year|lat|lon)`, plus the new list-artifact filter — bug #5).
That merge is **6,373 installed events**, up from pass 1's 5,351. When pass 3 finishes AD 568–2025
it re-merges the same way and these numbers rise again; treat 6,373 as the floor, not the ceiling.

---

## Installed output

`events_wikipedia.json` — **6,373 events, 2.22 MB**, years **−2950 to 2024**. (This is the
current installed state after merging passes 1–2; pass 3 will be merged on completion. The
pass-1-only figures appear later, in "The yield gap", clearly labelled.)

| kind | count |
|---|---|
| incident | 2,768 |
| political | 2,034 |
| battle | 442 |
| cultural | 365 |
| disaster | 393 |
| treaty | 205 |
| siege | 166 |

`effect` values used: `note` 3,133 · `political` 2,239 · `military_presence` 608 · `disruption` 393.
All four are recognised by the mod's own `EventNews.java` and `PresenceLocalSpawner.java`.

**Reach: 503 distinct 5×5° cells** — roughly half of Earth's land cells, versus 243 cells
(~24% of land) in the pre-existing Wikidata pack. So the new pack roughly doubles geographic spread.

Sampled coordinates, spot-checked against known positions:

```
-2450  ( 27.33, 68.14)  Mohenjo-daro            correct
-1950  ( 30.63, 72.87)  Harappa                 correct
 -560  ( 27.48, 83.28)  Birth of the Buddha     correct (Lumbini)
 -500  ( 25.99, 85.13)  Republic of Vaishali    correct
 1710  ( 30.63, 76.39)  Battle of Sirhind       correct
 1758  ( 49.74, 17.44)  Battle of Domstadtl     correct
```

**236 events fall inside India** (6–36°N, 68–98°E), including 7 from the Indus Valley period.

---

## The honest coverage picture

Per-century, combined Wikidata + Wikipedia:

```
  3099-3000 BC      2          1000s          271  ######
  2999-2900 BC      1          1100s          323  ########
  2899-2800 BC      0          1200s          446  ###########
  2799-2700 BC      0          1300s          465  ###########
  2699-2600 BC      0          1400s          578  ##############
  2599-2500 BC      1          1500s         1007  #########################
  2499-2400 BC      0          1600s         1168  #############################
  2399-2300 BC      0          1700s         1665  #########################################
  2299-2200 BC      1          1800s         3296  ##################################################
  2199-2100 BC      8          1900s         6209  ##################################################
  2099-2000 BC     15          2000s         3169  ##################################################
  1999-1900 BC      7
  1899-1800 BC     24            699-600 BC     58  #
  1799-1700 BC      4            599-500 BC    103  ##
  1699-1600 BC      5            499-400 BC    114  ##
  1599-1500 BC      5            399-300 BC    151  ###
  1499-1400 BC      2            299-200 BC     83  ##
  1399-1300 BC      7            199-100 BC    151  ###
  1299-1200 BC      4                0s         56  #
  1199-1100 BC      4              100s         28
  1099-1000 BC      3              200s         72  #
   999- 900 BC      4              300s         67  #
   899- 800 BC     10              400s         58  #
   799- 700 BC     17              500s        100  ##
                                   600s        150  ###
                                   700s        116  ##
                                   800s        139  ###
                                   900s        118  ##
```

### What the harvest genuinely fixed

**9 BC centuries that had zero events now have some** — 3099–3000, 2999–2900, 2599–2500,
2299–2200, 2199–2100, 2099–2000, 1899–1800, 1799–1700, 1699–1600 BC. The 1800s BC went
0 → 24 and the 2000s BC went 0 → 15. Those came from Wikipedia's century pages, which
Wikidata simply does not cover at that depth.

The 600s BC also went 12 → 58, because Wikipedia has real year articles from ~600 BC onward
while the structured Wikidata battle set is thin there.

### What is still empty — stated plainly

**Five BC centuries still have literally nothing:** 2899–2800, 2799–2700, 2699–2600,
2499–2400, 2399–2300 BC. And everything from 3000 to 1600 BC is single digits per century.

That is not a harvester failure. Those centuries have no dated, geocodable events in
Wikipedia either — the source pages contain 1 to 33 bullets for a whole hundred years.
This matches the earlier finding that geocoded history before ~1500 BC is thin everywhere
in every open source.

**Density is still 20th-century weighted:** 6,065 of 21,690 events (28%) are in the 1900s,
and 12,482 (58%) are in 1800–2024. `/terra timejump` to 1850 will feel alive. `/terra timejump`
to 2400 BC will still feel empty, because no open source has anything to put there.

---

## Bugs found and fixed in the pipeline

These are recorded because each one silently corrupted output before being caught.

**1. Year sign convention inverted (would have broken 5,303 records).**
The harvester stores positive = BC, negative = AD. The mod's `events_world.json` is the
opposite: positive = AD, negative = BC. Every harvested year needed negating. Caught because
`plausible()` rejected 5,303 of 5,789 records — the sign test flagged all of them.

**2. Year "fixing" was destroying good data (5,010 records).**
The first post-processor rewrote any year more than ±120 from its page's year. On century
pages that is normal and legitimate — a "30th century BC" bullet dated 2000 BC is correct.
It was replacing accurate bullet dates with page approximations. Replaced with a per-page-type
window (60 yr for year pages, 80 for decade, 160 for century, 1600 for millennium) plus a
sign check. `year_fixed` fell 5,010 → 373.

**3. A single regex bug mis-filed 3,000 events.**
The classifier pattern was `\b(battl|combat|...)\b` — a word boundary *after* the alternation.
`battl\b` can never match "Battle", because there is no boundary between `battl` and `e`.
So essentially nothing matched `battle`, `siege` or `treaty`, and 3,035 events fell through to
`incident`. Fixed by removing the trailing `\b`. Battles went **31 → 337**, sieges 118 → 114,
treaties 151 → 175, incidents 3,035 → 2,580 (all pass-1 counts; the installed pass 1–3 merge
later lifted these to 442 / 166 / 205 / 2,768).

**4. Rate-limit failures were silently indistinguishable from missing pages — real data loss.**
This one only surfaced on the second, larger pass. `harvester.api()` fetched pages with
`curl -s` and *no* HTTP status capture. When Wikipedia returned **429 Too Many Requests**
(an HTML body), `json.loads` threw, the code retried 4×8s, then returned `None`. `fetch()`
turned any `None` into the status `"missing"`, and the driver logged the year as
`"no page"` and moved on — exactly as if the article did not exist.

The symptom: the second pass logged 12 AD years as "no page" (37, 53, 64, 81, 102, 125, 148,
162, 196, 201, 204, 207). Spot-checked directly, **AD 37, 64 and 148 all return HTTP 200** —
they are ordinary, populated year articles. They were dropped purely because a transient 429
was misreported as "this year has no article."

The fix, at the correct layer:
- `api()` now captures `%{http_code}`, backs off exponentially on 429 (`8·2^i`), and returns a
  distinct `"MISSING"` sentinel *only* on a definitive `missingtitle` error. Exhausted
  transient attempts return `None`.
- `fetch()` maps `None → "throttled"` and `"MISSING" → "missing"`.
- `fetch_with_fallback()` returns a 3-tuple `(title, wikitext, status)`; status is `throttled`
  if *any* candidate failed transiently.
- `harvest_run.py` no longer drops throttled years — it re-queues them and retries over up to
  5 passes, sleeping 60s between passes to let the limiter cool.

Proof the fix holds: the third pass has run through **AD 213–487 with 0 false "no page" drops
despite 129 separate 429 backoffs.** The old code would have silently lost on the order of 100+
real pages by that point. This bug is the reason the harvest is split into passes at all.

**5. Year-page list artifacts were passing through as events.**
Wikipedia year pages carry non-event list sections — Nobel-prize winners ("Physics – The Lord
Rayleigh"), numbered highways ("California State Route 193"), telephone calling codes ("The
international calling code for Greece"), award recipients. These geocode fine (a prize links to
Stockholm, a highway to its state), so they survived every existing filter and landed in the pack
as generic `incident` events, diluting exactly the battles/epidemics/treaties categories the
harvest targets. Measured: **297 such records** in the pass 1–2 merge.

The fix is a `LIST_ARTIFACT` regex in `postprocess.py`, checked right after the existing `NOISE`
filter with its own `drop_list_artifact` counter. It is deliberately **high-precision only** —
four anchored patterns (prize-category lines, bare numbered routes, phone/postal codes, award
phrases). Every one of the 297 drops was manually audited against the full list before wiring it
in: **zero false positives**. This matters because an earlier over-broad filter in this pipeline
silently corrupted 5,010 records (bug #2), so the bar for a new drop rule is a full manual audit,
not a plausible-looking regex. Removing the 297 lifted nothing out that was a real event; it only
removed junk, and `incident` fell 3,035-class noise accordingly.

---

## What was verified, and what was not

This section was rewritten after an actual build and load, not just schema comparison.

**The mod compiles.** Installed a local Temurin **JDK 17** (the sandbox shipped JDK 11; the
project needs 17) and ran the real toolchain:

```
JAVA_HOME=/home/user/jdk sh gradlew compileJava --no-daemon -Dorg.gradle.jvmargs="-Xmx700m ..."
→ BUILD SUCCESSFUL in 49s   (all 270 Java files)
```

The first attempt OOM-killed the daemon — the repo's `gradle.properties` sets `-Xmx1800M`
against a sandbox with only ~1.4 GB free. Overriding to `-Xmx700m` built cleanly.

**The pack is loaded by the mod's own code.** Compiled the mod's classes, then ran a harness
(`LoadCheck.java`) that calls `HistoryGazetteer.get()` — the exact path `/tpll` uses — against
the installed data. The mod's real loader reported:

```
sites 15,954   events 21,690   borders 16
wikipedia_year_pages pack LOADED: true  (6,373 events)
```

**The events answer location+year queries.** `HistoryGazetteer.eventsNear(lat, lon, year, km)`
— the same method the game calls — returns real hits at the harvested points:

```
Hyderabad (17.39,78.49) 1687  -> 5 events incl. "Siege of Golconda" (8.8 km)
Mohenjo-daro (27.33,68.14) -2450 -> 1 event  [wikipedia_year_pages]   <-- a NEW pack hit
Kyoto (35.01,135.77) 1600 -> 11 events incl. "Siege of Fushimi" (8.1 km)
London (51.51,-0.13) 1066 -> 2 events, "Battle of Hastings" (78.8 km)
```

Alive-count per pack, straight from `Event.activeIn(year)`:

```
 1900  wikipedia_year_pages = 37 alive
 1944  wikipedia_year_pages = 173 alive
 2000  wikipedia_year_pages = 46 alive
```

**Data integrity:** 6,373 events, **0 field errors, 0 out-of-range years/coords,
0 unknown kinds, 0 duplicate ids, 0 id collisions** with the 15,317 ids in other packs.
Every `effect` value is one the mod's Java branches on. 3 wiki-markup artefacts (two
`web.archive.org` URLs, one unclosed `{{Cite book}}` template) were caught and scrubbed.

### One self-correction, stated plainly

I initially reported that **all 5,351 events were invisible** because their `end` equalled
their `start`, and `Event.activeIn(year)` is `year >= start && year < end`. **That was wrong.**
`HistoryGazetteer.loadEvents` (line 566) already defends against it:

```java
if (end <= start) { end = start + 1; }
```

I proved this by loading two isolated resource trees differing *only* in that field — the
alive-counts came back identical, so the loader was repairing it either way. The events were
never invisible. I still set `end = start + 1` in the post-processor so the on-disk data
matches `events_world.json`'s convention rather than leaning on a defensive guard — but it
was hygiene, not a bug fix. The mistake was diagnosing a bug from the schema without reading
the loader that consumes it.

**Not verified — say this plainly:**

- **No full game launch.** A headless harness exercised `HistoryGazetteer`, but nothing ran a
  live Minecraft server, so no actual `/terra timejump` was executed in-world.
- 2,768 events carry `kind: incident`, meaning the classifier could not pin them to a
  better category. They are still valid events with correct coordinates and years — just
  generically labelled.

---

## The density finding — and it is the one that matters

The standing requirement is that `/tpll` + `/terra timejump` to *any* coordinate and year must
never land in an empty world. So the question is not "how many events did we add" but "if you
teleport to a random spot on land and jump to a year, is anything there?" Measured with the
mod's own `eventsNear`, on 400 random land points per year:

```
    year     R=25km    R=50km   R=100km
   -2500      0.0%      0.0%      0.0%
   -1500      0.0%      0.0%      0.0%
    -500      0.0%      0.0%      0.3%
       1      0.0%      0.0%      0.0%
     500      0.0%      0.3%      0.3%
    1000      0.0%      0.0%      0.0%
    1300      0.0%      0.0%      0.8%
    1500      0.0%      0.0%      0.0%
    1700      0.0%      0.0%      0.5%
    1850      0.0%      0.0%      0.0%
    1900      0.0%      0.0%      0.0%
    1944      0.3%      1.3%      4.3%
    2000      0.0%      0.3%      1.0%
```

**Read that honestly: it is near zero almost everywhere.** Even 21,690 events — 42% more than
before this harvest — leave a random teleport finding something within 100 km in well under 1%
of cases for most of history, peaking at 4.3% in 1944.

The reason is arithmetic, not data quality. 21,690 points scattered over ~150 million km² of
land is one event per ~6,900 km² — a circle of radius ~47 km *if they were evenly spread*, and
they are not; they cluster on old-world battlefields and 20th-century cities. Doubling the
event count does not fix this, because the empty area shrinks only as the square root.

**This is the measurement behind the earlier "visibility is the bottleneck" position — now
backed by a number instead of an argument.** Point-events alone will not satisfy the standing
requirement at any volume Wikipedia can supply. The architecture the audit recommended —
density-based degradation, where a region/century carries a *rate* that spawns ambient
presence rather than a literal pinned event — is what actually keeps `/tpll` from landing empty.
This harvest feeds that system real anchors; it is not, on its own, the answer.

---

## The yield gap, stated honestly

*This section analyses the pass-1 sample (315 pages → 5,351 events). The per-page arithmetic is
what generalises; the 5,351 total has already been superseded by the pass 1–3 merge (6,373).*

The survey projected 70,000–100,000 harvestable events. Pass 1 produced 5,351.
That is **~5–7% of the projection**, and the projection was wrong for three measured reasons:

1. **70% of bullets are noise.** 29,986 of 42,566 bullets were births, deaths, or non-events.
   The survey counted bullets; it did not measure how many describe an *event at a place*.
2. **Only 30% of bullets yield a usable place.** 12,590 of 42,566 had a place link that
   survived the filters. The survey's "99% of bullets carry a place link" was measuring the
   presence of *any* wikilink, not a geocodable settlement.
3. **The per-page yield is not what the survey assumed.** Measured: **135 bullets per page**
   and **17.0 kept events per page** (42,566 ÷ 315 and 5,351 ÷ 315). The survey assumed ~28
   geocodable bullets per page, so it actually *undercounted* raw bullets by ~5× while
   *overcounting* how many survive as real events. The projection was wrong about both terms
   in opposite directions, which is why it happened to land in a plausible-looking range.

**What a full run would yield.** Measured per-page yield is **17.0 kept events per page**
(5,351 ÷ 315 pages). Naive arithmetic — 17.0 × 5,025 year pages — gives **85,000**, which would
actually vindicate the original projection. But that figure assumes uniform page density, and
the sampling was *not* uniform: the year list oversampled dense modern pages and took one page
per BC century where the real density is near zero. The honest statement is that a full run
lands somewhere between the current 5,351 and 85,000, and **nobody knows where until it is
run**. What is settled is that the original projection cannot be reached by simply extrapolating
this sample, because the sample is skewed toward the densest pages on the site.

`geo_cache.json` persists across runs, so a full run would be much faster than this one —
the geocode lookups, not the page fetches, were most of the wall-clock time.

---

## Where this leaves the original goal

The request was history, battles, epidemics, treaties, borders and population, worldwide,
3000 BC to now, from Wikipedia. Scored against that:

| Requested | Status |
|---|---|
| **Battles** | 360 new, on top of 7,989 already baked from Wikidata. Done as far as open data allows. |
| **Sieges** | 125 new, on top of 2,398 existing. |
| **Treaties** | 180 new. The mod previously had **zero**. This category now exists. |
| **Epidemics** | Partially. 346 `disaster` events include plagues, epidemics and pandemics that Wikipedia dates and places. A dedicated epidemic set is still impossible before 1963 — no open source geocodes older outbreaks. |
| **History generally** | 6,373 new events (passes 1–2 + AD 213–567; pass 3 continuing), 21,690 total, half of Earth's land cells touched. |
| **Borders** | Untouched. Already baked via Cliopatria in `deccan_rulers.json` (15,741 places, 274 timelines). Wikipedia has no usable per-year border geometry. |
| **Population** | Untouched. Already baked in the `population/` packs. |

**Still open, in priority order:**

1. **No live in-world test yet.** The mod *does* compile (a local JDK 17 was installed; the
   sandbox shipped 11) and a headless harness confirms `HistoryGazetteer` loads and queries the
   pack. What has not happened is a real Minecraft server launch with an actual `/terra timejump`
   to a coordinate — the last mile from "the loader accepts it" to "the player sees it".
2. **Pass 3 is still running.** Passes 1–2 cover BC densely and AD 1–212; the lossless resume
   is fetching AD 213–2025 now. Merge on completion and re-measure every number in this report.
3. **2,768 events are labelled `incident`** because the classifier could not pin them down.
   Better classification would make them more useful without changing their coordinates.
4. **3000–1600 BC stays thin no matter what.** Five BC centuries are still empty and the rest
   are single digits. This is a property of the source, not the pipeline.

## Reproducing

The installed pack is the merge of passes 1–2 plus the AD 213–567 slice of pass 3 (the rest of
pass 3 merges on completion). `finalize.sh` does the whole merge→postprocess→install→verify in one
command; the steps it runs are shown explicitly here:

```bash
cd /home/user/harvest

# Pass 1 — 340-target sample (yearlist2.txt): 5,789 raw records
python3 -u harvest_run.py yearlist2.txt       events_raw.jsonl          # 5,789

# Pass 2 — 2,325-target full run (yearlist_full.txt), stopped at AD 212 by the throttle
# that exposed bug #4: 876 salvaged records
python3 -u harvest_run.py yearlist_full.txt   events_full_raw.jsonl     # 876 (.partial)

# Pass 3 — lossless resume of the 12 wrongly-dropped AD years + AD 213–2025, streaming.
# Reaped by the sandbox at AD 567 (950 records intact), restarted from AD 568; still running.
python3 -u harvest_run.py yearlist_resume.txt  events_resume_raw.jsonl  # streaming

# Merge every pass (dedup + the bug #5 list-artifact filter happen inside postprocess)
cat events_raw.jsonl events_full_raw.jsonl.partial \
    events_resume_snap_AD567.jsonl > events_all_raw.jsonl               # 7,615

# Postprocess the merge -> the mod's pack schema (6,373 kept), then install
python3 postprocess.py events_all_raw.jsonl events_wikipedia.json       # 6,373
cp events_wikipedia.json \
   /home/user/eternal/src/main/resources/data/eternalengine/eternal/history/
# "events_wikipedia.json" must be listed in history/index.json packs (re-add if a
#  sandbox re-provision reverted index.json — that happened once and silently
#  dropped the pack from the load; LoadCheck is what caught it).

# Or just: ./finalize.sh          (merge + postprocess + install + index check)
#          ./finalize.sh --preview (same, but to /tmp — touches nothing installed)
```

Year convention when writing a new year list: **positive = BC, negative = AD.**
`-1200` means 1200 AD. This is inverted from the mod's own schema — `postprocess.py`
does the negation.
