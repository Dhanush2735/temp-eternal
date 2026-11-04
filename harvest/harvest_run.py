#!/usr/bin/env python3
"""Streaming Wikipedia year-page harvester (v2).

Fetches one page at a time, geocodes that page's places, and writes events immediately,
so the output file always holds real, finished records even if a live run is interrupted.
Dedupes pages and events across the whole run.

v2 (see FIXES.md):
  * every year is looked up the way the census does it (harvester.find_year_page)
  * ONE year convention in the raw output: positive = BC, negative = AD. v1 wrote
    explicit "N BC" years as -N (the mod's convention) and everything else in the
    harvester convention, so postprocess.py turned stated BC years into AD years.
  * Births / Deaths / people / reference sections are skipped (harvester.bullets)
  * --snapshot re-runs the whole harvest offline from the census snapshot, geocoding
    from the census caches only (no network at all)
  * --overview also reads the decade / century / millennium pages that no year maps
    to, keeping only bullets with no counterpart on a year page

A page whose live fetch fails transiently (HTTP 429 / transport) is NOT dropped: it is
re-queued and retried on a later pass. Only a definitive "no such article" counts as missing.

Usage:
  python3 harvest_run.py --snapshot --overview out.jsonl          # offline, 3000 BC .. AD 2026
  python3 harvest_run.py --years 3000:-2026 out.jsonl              # live API
  python3 harvest_run.py yearlist.txt out.jsonl                    # v1 form, live API
Year convention on the command line and in the output: positive = BC, negative = AD.
"""
import argparse, collections, html as _html, json, os, re, sys, time

sys.path.insert(0, "/home/user/harvest")
import harvester as H                                        # noqa: E402
from harvester import (find_year_page, bullets, place_from_bullet, named_event,  # noqa: E402
                       clean_name, event_text, is_birth_death, classify)

CACHE = "/home/user/harvest/geo_cache.json"
OFFLINE_CACHES = [
    "/home/user/harvest/geo_cache.json",
    "/home/user/survey/census/geo_cache_census.json",
    "/home/user/survey/census/work/geo_cache_overview.json",
]
MAX_PASSES = 5
SCHEMA = 2
FIRST_YEAR_H, LAST_YEAR_H = 3000, -2026      # 3000 BC .. AD 2026, harvester convention

BC_YEAR = re.compile(r'(?<!\w)(\d{1,4})\s*(?:BC|BCE)\b(?!\s*centur)', re.I)
CENTURY_MENTION = re.compile(r'\b\d{1,2}(?:st|nd|rd|th)\s+century', re.I)
AD_YEAR = re.compile(r'(?<!\w)(\d{3,4})\s*(?:AD|CE)\b', re.I)


def bullet_year(line, page_year_h):
    """The year of one bullet, in the harvester convention (positive = BC, negative = AD).
    An explicit "N BC" / "N AD" in the bullet wins; otherwise the page's year."""
    m = BC_YEAR.search(line)
    if m and not CENTURY_MENTION.search(line):
        return int(m.group(1))
    m2 = AD_YEAR.search(line)
    if m2:
        return -int(m2.group(1))
    return page_year_h


# ------------------------------------------------------------------ geocoding
def load_cache(path=CACHE):
    if os.path.exists(path):
        try:
            return json.load(open(path, encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_cache(c):
    tmp = CACHE + ".tmp"
    json.dump(c, open(tmp, "w", encoding="utf-8"))
    os.replace(tmp, CACHE)


class LiveGeocoder:
    def __init__(self):
        self.cache = load_cache()

    def lookup(self, titles):
        need = sorted({t for t in titles if t and t not in self.cache})
        if need:
            from geo import resolve_places_v2
            self.cache = resolve_places_v2(need, CACHE)
            save_cache(self.cache)
        return self.cache


class OfflineGeocoder:
    """Cache-only: the harvest cache, the census cache and the overview cache, merged.
    Titles none of them knows are counted and skipped, never guessed."""

    def __init__(self, paths=OFFLINE_CACHES):
        self.cache = {}
        for p in paths:
            self.cache.update(load_cache(p))
        self.unknown = set()

    def lookup(self, titles):
        for t in titles:
            if t and t not in self.cache:
                self.unknown.add(t)
        return self.cache


# ------------------------------------------------------------------ period windows
def window(title):
    """Years a decade / century / millennium / year page covers (mod convention)."""
    t = re.sub(r"\s*\((decade|year)\)$", "", title.strip())
    bc = t.endswith(" BC")
    core = t[:-3] if bc else t
    m = re.fullmatch(r"(\d+)s", core)
    if m:
        d = int(m.group(1))
        return (-(d + 9), -max(d, 1)) if bc else (max(d, 1), d + 9)
    m = re.fullmatch(r"(\d+)(?:st|nd|rd|th) century", core)
    if m:
        c = int(m.group(1))
        return (-(c * 100), -((c - 1) * 100 + 1)) if bc else ((c - 1) * 100 + 1, c * 100)
    m = re.fullmatch(r"(\d+)(?:st|nd|rd|th) millennium", core)
    if m:
        k = int(m.group(1))
        return (-(k * 1000), -((k - 1) * 1000 + 1)) if bc else ((k - 1) * 1000 + 1, k * 1000)
    m = re.fullmatch(r"(?:AD )?(\d+)", core)
    if m:
        y = int(m.group(1))
        return (-y, -y) if bc else (y, y)
    return None


def overlaps(a, b):
    return bool(a and b and a[0] <= b[1] and b[0] <= a[1])


STOP = set("""a an the of in at on to and or by for from with as is are was were be been
his her its their into after during under over against between who which that this
january february march april may june july august september october november december
c ca circa bc ad bce ce king emperor""".split())


def toks(s):
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    return {w for w in re.findall(r"[a-z]+", s.lower()) if len(w) > 2 and w not in STOP}


def jacc(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


# ------------------------------------------------------------------ one page
def parse_page(w, stats):
    rows = []
    for line in bullets(w):
        stats["bullets"] += 1
        line = _html.unescape(line)
        if is_birth_death(line):
            stats["noise"] += 1
            continue
        place = place_from_bullet(line)
        if not place:
            stats["noise"] += 1
            continue
        stats["with_place"] += 1
        rows.append((line, place, named_event(line)))
    return rows


def process_page(y, title, w, seen_keys, geo, sink, stats, emitted=None, layer="year"):
    """Parse one page, geocode its places, emit raw records (harvester convention).
    y is the page's fallback year in the harvester convention."""
    stats["bullets_skipped_sections"] += len(H.bullets_with_sections(w)) - len(bullets(w))
    rows = parse_page(w, stats)
    cache = geo.lookup([t for _, p, e in rows for t in (p, e)])
    out = []
    for line, place, evname in rows:
        co = cache.get(evname) if evname else None
        src = evname
        if not co:
            co = cache.get(place)
            src = place
        if not co:
            continue
        stats["geocoded"] += 1
        name = clean_name(event_text(line))
        if len(name) < 12:
            stats["noise"] += 1
            continue
        yr = bullet_year(line, y)
        key = (name.lower()[:110], yr, round(co[0], 1), round(co[1], 1))
        if key in seen_keys:
            stats["dupes"] += 1
            continue
        seen_keys.add(key)
        kind = classify(line)
        rec = {
            "id": "wp_%d_%d" % (yr, len(seen_keys)),
            "name": name[:400],
            "start": yr, "end": yr,
            "lat": co[0], "lon": co[1],
            "radiusKm": 20,
            "kind": kind,
            "effect": ("military_presence" if kind in ("battle", "siege") else "political"),
            "confidence": "wikipedia_year_page",
            "place": src, "page": title,
            "layer": layer, "schema": SCHEMA,
        }
        out.append(rec)
    if sink is not None:
        for rec in out:
            sink.write(json.dumps(rec, ensure_ascii=False) + "\n")
        sink.flush()
    stats["kept"] += len(out)
    if emitted is not None:
        emitted.extend(out)
    return out


# ------------------------------------------------------------------ overview pages
def structural_titles(last_ad=2026):
    out = []
    for d in range(3000, -1, -10):
        out += [f"{d}s BC", f"{d}s BC (decade)"]
    for d in range(0, last_ad + 1, 10):
        out += [f"{d}s", f"{d}s (decade)"]
    out += [f"{H.century_name(c)} century BC" for c in range(30, 0, -1)]
    out += [f"{H.century_name(c)} century" for c in range(1, 22)]
    out += [f"{H.century_name(m)} millennium BC" for m in (4, 3, 2, 1)]
    out += [f"{H.century_name(m)} millennium" for m in (1, 2, 3)]
    return out


def harvest_overview(source, seen_pages, page_years, year_records, seen_keys, geo, sink, stats):
    """Decade / century / millennium pages no year maps to. Keeps only bullets with no
    counterpart on a year page: not the same wording (content-word Jaccard >= 0.5) and not
    the same place in an overlapping period. Undated bullets get the page's midpoint; any
    that fall outside 3000 BC .. AD 2026 are dropped (their real date is unknown)."""
    home_win = {p: (min(ys), max(ys)) for p, ys in page_years.items()}
    by_place = collections.defaultdict(list)
    for r in year_records:
        r_w = home_win.get(r["page"])
        t = toks(r["name"])
        for k in (r["place"], (round(r["lat"], 1), round(r["lon"], 1))):
            by_place[k].append((r_w, t))
    titles = structural_titles()
    res = source.resolve(titles)
    todo = []
    for t in titles:
        r = res.get(t)
        if not r or r["missing"] or r["disambig"]:
            continue
        c = r["canonical"]
        if c in seen_pages or c in todo:
            continue
        todo.append(c)
    for c in todo:
        w, st = source.wikitext(c)
        if w is None or H.page_type(c, w) not in ("decade", "century", "millennium"):
            continue
        win = window(c)
        if not win:
            continue
        seen_pages.add(c)
        stats["overview_pages"] += 1
        mid = (win[0] + win[1]) // 2
        local = collections.Counter()
        recs = process_page(-mid, c, w, seen_keys, geo, None, local, layer="overview")
        for k in ("bullets", "with_place", "geocoded", "noise", "dupes"):
            stats["overview_" + k] += local[k]
        for rec in recs:
            ym = -rec["start"]
            if not (-3000 <= ym <= 2026):
                stats["overview_outside_range"] += 1
                continue
            ew = (ym, ym) if rec["start"] != -mid else win
            tk = toks(rec["name"])
            cands = by_place.get(rec["place"], []) + by_place.get(
                (round(rec["lat"], 1), round(rec["lon"], 1)), [])
            cands = [t for hw, t in cands if overlaps(hw, ew) or overlaps(hw, win)]
            if any(jacc(tk, t) >= 0.5 for t in cands):
                stats["overview_text_match"] += 1
                continue
            if cands:
                stats["overview_place_match"] += 1
                continue
            stats["overview_new"] += 1
            sink.write(json.dumps(rec, ensure_ascii=False) + "\n")
        sink.flush()


# ------------------------------------------------------------------ the run
def harvest(years, out_path, source=None, geo=None, overview=False):
    stats = collections.Counter()
    source = source or H.default_source()
    geo = geo or LiveGeocoder()
    seen_pages, seen_keys = set(), set()
    page_years = collections.defaultdict(list)       # page -> years (mod convention)
    year_records = []
    sink = open(out_path + ".partial", "w", encoding="utf-8")

    queue = list(years)
    for pass_no in range(1, MAX_PASSES + 1):
        if not queue:
            break
        if pass_no > 1:
            print("  === pass %d: retrying %d throttled pages ===" % (pass_no, len(queue)), flush=True)
            time.sleep(60)                    # let the rate limiter cool before retrying
        retry = []
        for y in queue:
            title, w, status, kind = find_year_page(y, source)
            if w is None:
                if status == "throttled":
                    retry.append(y)           # transient -- do NOT drop, retry next pass
                    continue
                stats["pages_missing"] += 1
                print("  %s: no page" % y, flush=True)
                continue
            page_years[title].append(-y)
            stats["page_kind_" + kind] += 0   # make the key exist
            if title in seen_pages:
                stats["pages_reused"] += 1
                continue
            seen_pages.add(title)
            stats["pages"] += 1
            stats["page_kind_" + kind] += 1
            process_page(y, title, w, seen_keys, geo, sink, stats, year_records)
            if stats["pages"] % 250 == 0:
                print("  %-16s pages=%-5d bullets=%-6d kept=%d"
                      % (title[:16], stats["pages"], stats["bullets"], stats["kept"]), flush=True)
        stats["pages_throttled"] += len(retry)
        queue = retry

    if queue:
        print("  WARNING: %d pages still throttled after %d passes: %s"
              % (len(queue), MAX_PASSES, queue[:20]), flush=True)
    if overview:
        harvest_overview(source, seen_pages, page_years, year_records, seen_keys, geo, sink, stats)

    sink.close()
    os.replace(out_path + ".partial", out_path)
    if isinstance(geo, OfflineGeocoder):
        stats["titles_not_in_offline_caches"] = len(geo.unknown)
    stats = dict(sorted(stats.items()))
    print(json.dumps(stats, indent=2), flush=True)
    with open(out_path + ".pages.json", "w", encoding="utf-8") as f:
        json.dump({p: sorted(ys) for p, ys in page_years.items()}, f, ensure_ascii=False)
    return stats


def parse_years(spec):
    a, b = (int(x) for x in spec.split(":"))
    step = -1 if b < a else 1
    return [y for y in range(a, b + step, step) if y != 0]


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("args", nargs="+", help="[yearlist.txt] out.jsonl")
    ap.add_argument("--years", default=None, help="range in harvester convention, e.g. 3000:-2026")
    ap.add_argument("--snapshot", action="store_true", help="offline: census snapshot + census caches")
    ap.add_argument("--overview", action="store_true", help="also read unmapped decade/century/millennium pages")
    a = ap.parse_args()
    if len(a.args) == 2:
        years = [int(t) for t in open(a.args[0]).read().split()]
        out = a.args[1]
    else:
        out = a.args[0]
        years = parse_years(a.years or f"{FIRST_YEAR_H}:{LAST_YEAR_H}")
    if a.snapshot:
        src, geo = H.SnapshotSource(), OfflineGeocoder()
    else:
        src, geo = H.LiveSource(), LiveGeocoder()
    print("harvesting %d year targets -> %s (%s)" % (len(years), out, "snapshot" if a.snapshot else "live"),
          flush=True)
    harvest(years, out, src, geo, overview=a.overview)
