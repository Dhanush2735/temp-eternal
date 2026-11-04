#!/usr/bin/env python3
"""Post-process harvested events: reclassify, fix years, drop noise, emit datapack (v2).

Reads events_raw.jsonl and writes history/events_wikipedia.json in the shape of
history/events_world.json, so HistoricalEventDatabase.loadFromFiles() reads it as-is.

Input years must be in the harvester convention (positive = BC, negative = AD); this file
negates them into the mod's convention. harvest_run.py v2 writes "schema": 2 on every record.
v1 raw files mix the two conventions for stated BC years, so they are counted as legacy.

v2 fixes (FIXES.md): a "repair" can no longer produce year 0 (`page_year('0s BC')` was 0 and
the repair ran after the year-0 guard); BC decade pages repair to their midpoint; events
dated after MAX_YEAR (today) are dropped as not-yet-history.
"""
import json, os, re, sys, collections, hashlib

# ---------------------------------------------------------------- classification
RULES = [
    # NOTE: no trailing \b on stem alternations — "battl\b" can never match "Battle".
    ("battle", r"(?:\b|[^a-z])(battl|combat|rout(?:ed|s)?\s+(?:the|a)|"
               r"victory at|slain in battle|killed in battle|"
               r"defeat(?:s|ed|ing)?\s+(?:the|a|an)\s+(?:army|force|fleet|coalition))"),
    ("siege",  r"(?:\b|[^a-z])(siege|besiege|sack(?:ed|ing)?|"
               r"storm(?:ed|ing)?\s+the\s+city|"
               r"captur(?:e|ed|ing)\s+(?:the\s+)?city|"
               r"city\s+(?:is\s+)?(?:destroyed|falls|surrender))"),
    ("treaty", r"(?:\b|[^a-z])(treaty|peace\s+(?:agreement|treaty|of)|armistice|truce|"
               r"accord|concordat|pact|alliance\s+with|cedes?\s|cession|"
               r"annex(?:ed|ation|es))"),
    ("disaster", r"(?:\b|[^a-z])(earthquake|eruption|volcan|tsunami|flood|famine|plague|"
                 r"epidemic|pandemic|drought|fire|hurricane|cyclone|storm|pestilence|"
                 r"climatic|destroyed\s+by\s+fire|great\s+flood)"),
    ("political", r"(?:\b|[^a-z])(found(?:ed|ing|s)?|establish|"
                  r"settle(?:d|ment)|villages|cities|city\s+of|abandon(?:ed|ment)|"
                  r"occupied|occupation\s+of|unif(?:y|ied|ication)|"
                  r"crowd?n?ed|coronation|dynast(?:y|ic)|reign|ascend|throne|"
                  r"elect(?:ed|ion)|independen|revolt|revolution|rebellion|coup|"
                  r"assassin|deposed|king|queen|emperor|pharaoh|sultan|caliph|raja|"
                  r"shah|tsar|caesar|empire|kingdom|republic|caliphate|sultanate|"
                  r"conquest|conquers?|capital|mutiny|expedition)"),
    ("cultural", r"(?:\b|[^a-z])(is made|are made|was made|were made|composed|written|"
                 r"carved|recorded|attested|earliest|first\s+(?:known|extant|evidence|recorded)|"
                 r"language|script|pictograph|cuneiform|literary|text|epic|"
                 r"built|builds|building\s+of|construct|erect|"
                 r"temple|pyramid|palace|mosque|cathedral|church|monastery|stupa|"
                 r"university|school|library|theatre|amphitheatre|monument|"
                 r"invent|discover|writing|alphabet|literature|poem|"
                 r"philosoph|mathematic|civilization|culture|"
                 r"period\s+(?:starts|begins)|begins\s+to\s+be\s+built)"),
]

# Residual wiki markup that survives the harvester's de-wiki pass.
MARKUP = re.compile(r"\{\{[^}]*\}\}|<ref[^>]*>.*?</ref>|<ref[^>]*/>|\[\[|\]\]")
# External-link form: [https://... anchor text]
EXTLINK = re.compile(r"\[https?://\S+\s+([^\]]+)\]")
BAREURL = re.compile(r"https?://\S+")

def scrub(name):
    """Strip leftover wiki markup. Returns None if the text is mostly a URL."""
    s = EXTLINK.sub(lambda m: m.group(1), name)
    s = MARKUP.sub(" ", s)
    # An unclosed {{Cite ... template has no }} to match, so cut to the end of the string.
    if "{{" in s:
        s = s[:s.index("{{")]
    s = BAREURL.sub(" ", s)
    s = re.sub(r"\s{2,}", " ", s).strip(" -\u2013\u2014:,")
    if not s or BAREURL.search(s):
        return None
    if len(s) < 12:
        return None
    return s

MYTH = re.compile(r"\b(Prometheus|Zeus|Odysseus|Heracles|Hercules|Noah|Atlantis|"
                  r"Gilgamesh|Thor|Odin|mythic(al)?|legendary (?:king|figure)|"
                  f"would have sprouted)\b", re.I)

NOISE = re.compile(r"\b(now (?:at|in) the|is now (?:at|in)|held (?:at|in) the|"
                   r"museum|collection of the|currently (?:at|in)|"
                   r"on display|excavated in \d{4}|discovered in \d{4})\b", re.I)

# Year-page list artifacts that are not events at a place. High-precision only:
# each pattern was audited against the full drop list with zero false positives.
#   - Nobel/prize category lines ("Literature – Naguib Mahfouz")
#   - bare numbered route/highway names ("California State Route 193")
#   - telephone / calling / postal code entries ("The international calling code for Greece")
#   - award-recipient lines ("... recipient of the Nobel Prize in Chemistry")
LIST_ARTIFACT = re.compile(
    r"^(?:physics|chemistry|physiology or medicine|medicine|literature|economics|peace)\s*[–—-]\s*\S"
    r"|\b(?:nobel prize|academy awards? for|grammy award|ballon d.or|pulitzer prize)\b"
    r"|\b(?:international (?:calling|direct dial)|calling code|dial(?:ling)? code|country code|"
    r"emergency telephone number|postal code|zip code)\b"
    r"|^(?:[A-Z][A-Za-z. ]+ )?(?:state route|state highway|national highway|route|highway|"
    r"interstate|motorway|autobahn|expressway)\s*\d", re.I)

def classify(name):
    n = name.lower()
    for kind, pat in RULES:
        if re.search(pat, n, re.I):
            return kind
    return "incident"

# ------------------------------------------------------------------ year repair
CENT = re.compile(r"(\d+)(?:st|nd|rd|th)\s+century\s+BC", re.I)
DEC  = re.compile(r"(\d+)s\s+BC", re.I)
MILL = re.compile(r"(\d+)(?:st|nd|rd|th)\s+millennium\s+BC", re.I)
YRBC = re.compile(r"^(\d{1,4})\s+BC$", re.I)

def page_year(page, fallback):
    """Best single year for a page title. BC returned negative."""
    if not page:
        return fallback
    m = CENT.search(page)
    if m:
        c = int(m.group(1))
        return -((c - 1) * 100 + 50)
    m = DEC.search(page)
    if m:
        # "750s BC" = 759..750 BC -> midpoint 755 BC; "0s BC" = 9..1 BC -> 5 BC.
        # v1 returned -750 and, for "0s BC", 0 -- a year that does not exist.
        d = int(m.group(1))
        return (-(d + 9) - max(d, 1)) // 2
    m = MILL.search(page)
    if m:
        return -((int(m.group(1)) - 1) * 1000 + 500)
    m = YRBC.match(page.strip())
    if m:
        return -int(m.group(1))
    if page.strip().isdigit():
        return int(page.strip())
    return fallback

def page_window(page):
    """Tolerance for a year given its page. Year pages are tight; century/millennium
    pages legitimately span a range, so they get a wide window."""
    if not page:
        return 600
    s = page.strip()
    if MILL.search(s):
        return 1600
    if CENT.search(s):
        return 160
    if DEC.search(s):
        return 80
    return 60          # a specific year page

def plausible(year, page):
    """True unless the year is clearly wrong (sign flip, or wildly off its page).
    Extracted bullet years are normally exact, so this must be conservative."""
    py = page_year(page, year)
    if (year < 0) != (py < 0):          # BC/AD sign disagreement
        return False
    return abs(year - py) <= page_window(page)

MAX_YEAR = int(os.environ.get("POSTPROCESS_MAX_YEAR", "2026"))   # nothing after today

# ------------------------------------------------------------------- effect map
EFFECT = {"battle": "military_presence", "siege": "military_presence",
          "treaty": "political", "political": "political",
          "disaster": "disruption", "cultural": "note", "incident": "note"}

def main(src, dst):
    stats = collections.Counter()
    seen, out = set(), []
    for line in open(src, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            # Tolerate a truncated final line: the harvester appends live, so a
            # merge run mid-write can catch a half-written record. Skip, don't crash.
            stats["drop_malformed"] += 1
            continue
        stats["raw"] += 1
        name = scrub((r.get("name") or "").strip())
        if name is None:
            stats["drop_markup"] += 1; continue

        if MYTH.search(name):
            stats["drop_myth"] += 1; continue
        if NOISE.search(name):
            stats["drop_museum"] += 1; continue
        if LIST_ARTIFACT.search(name):
            stats["drop_list_artifact"] += 1; continue
        if len(name) < 14 or len(name) > 300:
            stats["drop_length"] += 1; continue

        lat, lon = r.get("lat"), r.get("lon")
        if lat is None or lon is None or not (-90 <= lat <= 90 and -180 <= lon <= 180):
            stats["drop_coord"] += 1; continue

        # Harvester sign convention is inverted vs the mod schema:
        #   harvest:  positive = BC, negative = AD
        #   mod:      negative = BC, positive = AD   (events_world.json uses -1830..2026)
        raw_year = r.get("start")
        if not isinstance(raw_year, int):
            stats["drop_year"] += 1; continue
        if r.get("schema", 1) < 2:
            stats["legacy_v1_record"] += 1
        year = -raw_year
        page = r.get("page")
        if year < -10000 or year > MAX_YEAR or year == 0:
            stats["drop_year"] += 1; continue
        if not plausible(year, page):
            fixed = page_year(page, year)
            if fixed != year:
                stats["year_fixed"] += 1
                year = fixed
            else:
                stats["drop_year"] += 1; continue
        # The guard above ran before the repair; a repair must not create year 0 either.
        if year == 0 or year > MAX_YEAR:
            stats["drop_year_after_repair"] += 1; continue

        kind = classify(name)
        stats["kind_" + kind] += 1

        key = (name.lower()[:110], year, round(lat, 1), round(lon, 1))
        if key in seen:
            stats["drop_dupe"] += 1; continue
        seen.add(key)

        h = hashlib.sha1(f"{name}|{year}|{lat}|{lon}".encode()).hexdigest()[:10]
        out.append({
            "id": f"wpy_{h}",
            "name": re.sub(r"\s+", " ", name)[:300],
            "start": year,
            # activeIn(year) is `year >= start && year < end`. An end equal to start
            # makes the interval empty and the event permanently invisible, so point
            # events must span exactly one year (matches events_world.json's delta=1).
            "end": year + 1,
            "lat": round(lat, 5),
            "lon": round(lon, 5),
            "radiusKm": int(r.get("radiusKm", 20)),
            "kind": kind,
            "effect": EFFECT[kind],
            "confidence": "wikipedia_year_page",
        })
        stats["kept"] += 1

    out.sort(key=lambda e: e["start"])
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    # Wrapper must match history/events_world.json exactly: HistoryGazetteer.loadPack
    # reads pack "id", "sites", and "events". Without "id" the pack loads as "unknown".
    doc = {
        "id": "wikipedia_year_pages",
        "title": ("Events harvested from English Wikipedia year and century pages "
                  "(-3000 to now), geocoded via Wikidata. Overlay only. Not towns. "
                  "Not attacker spawn."),
        "sites": [],
        "comparedSources": [
            "English Wikipedia year pages, century pages and decade pages (CC BY-SA 4.0)",
            "Place coordinates resolved through Wikidata P625, with P276/P131 fallback",
        ],
        "rejected": [
            "Births and deaths of individuals",
            "Museum holdings and extant-artifact notices",
            "Mythological and legendary accounts",
            "Spawning attacker NPCs",
            "Treating an event as a city founding",
        ],
        "events": out,
    }
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)

    kinds = {k[5:]: v for k, v in stats.items() if k.startswith("kind_")}
    print(json.dumps({k: v for k, v in stats.items() if not k.startswith("kind_")}, indent=2))
    print("\nkind distribution:")
    for k, v in sorted(kinds.items(), key=lambda x: -x[1]):
        print(f"  {k:11} {v:>5}  {'#' * min(50, v // max(1, max(kinds.values()) // 50))}")
    if out:
        ys = [e["start"] for e in out]
        print(f"\nwrote {len(out)} events -> {dst}  ({os.path.getsize(dst)/1e6:.2f} MB)")
        print(f"year range: {min(ys)} .. {max(ys)}")
    return out

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/home/user/harvest/events_raw.jsonl",
         sys.argv[2] if len(sys.argv) > 2 else "/home/user/harvest/events_wikipedia.json")
