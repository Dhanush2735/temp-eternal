#!/usr/bin/env python3
"""Wikipedia year-page -> Eternal Engine HistoricalEvent harvester (v2).

Pipeline:
  1. find the page that really holds each year (own year article, else its decade,
     century or millennium page), the same way survey/census/census.py does
  2. split it into bullets, skipping Births / Deaths / people / reference sections
  3. keep bullets with a place wikilink; extract year, kind and name
  4. batch-resolve place titles -> coordinates (Wikidata P625, P276/P131 fallback)
  5. emit records in the events_world.json schema (harvest_run.py), then postprocess.py

v2 fixes (see FIXES.md; the v1 files are frozen in survey/census/pipeline_v1/):
  * AD years: the bare number ("500") is often a disambiguation or number article. Years
    are now looked up as "N (year)", "AD N", "N", and a page only counts as the year's
    article if it is not a disambiguation page and its {{Year nav}} names that year.
  * BC decade fallback used the century ("700s BC" for 753 BC); now the real decade.
  * Bullets under level-2 Births / Deaths / people / references sections are skipped.
  * Pages can come from the live API or, offline, from the frozen census snapshot.

Year convention in this module and in harvest_run.py's raw output:
    positive = BC, negative = AD (the "harvester convention"); postprocess.py negates it
    into the mod's convention (negative = BC).
"""
import gzip, json, os, re, subprocess, sys, time, urllib.parse

# Wikimedia's 2026 limits: 10 requests/min without contact information in the User-Agent,
# 200/min with an email or URL in it. Set HARVEST_UA to a UA that carries real contact info.
UA = os.environ.get("HARVEST_UA") or \
    "EternalEngineHarvester/2.0 (historical data build; single-user research script)"
API = "https://en.wikipedia.org/w/api.php"
STATE = "/home/user/harvest/state.json"
OUT   = "/home/user/harvest/out_events.jsonl"
CACHE = "/home/user/harvest/coord_cache.json"

SNAPSHOT = "/home/user/wiki_test/snapshot/pages.jsonl.gz"
SNAPSHOT_TITLES = "/home/user/survey/census/work/titles_res.json"

_api_last = [0.0]
API_MIN_GAP = 1.6   # seconds between page-fetch requests (be polite; avoid 429)


def api(params, tries=6, wait=8):
    """Returns parsed JSON on success, the string "MISSING" if the page does not
    exist, or None if every attempt failed transiently (429 / empty / transport).
    Callers MUST distinguish None (retry later) from "MISSING" (definitive)."""
    url = API + "?" + urllib.parse.urlencode(dict(params, format="json", formatversion="2"))
    for i in range(tries):
        gap = API_MIN_GAP - (time.time() - _api_last[0])
        if gap > 0:
            time.sleep(gap)
        r = subprocess.run(["curl", "-s", "-w", "\n%{http_code}", "--max-time", "40", "-A", UA, url],
                           capture_output=True, text=True)
        _api_last[0] = time.time()
        out = r.stdout
        code = out.rsplit("\n", 1)[-1].strip() if out else ""
        body = out.rsplit("\n", 1)[0] if out else ""
        if code == "429" or "too many requests" in body.lower():
            backoff = wait * (2 ** i)
            print("  [429] api backing off %ds" % backoff, file=sys.stderr, flush=True)
            time.sleep(backoff); continue
        if not body.strip():
            time.sleep(wait); continue
        try:
            d = json.loads(body)
        except Exception:
            time.sleep(wait); continue
        if "error" in d:
            if d["error"].get("code") == "missingtitle":
                return "MISSING"
            time.sleep(wait); continue
        return d
    return None


# ---------- page targets ----------
CENTURY_WORDS = {1: "1st", 2: "2nd", 3: "3rd"}


def century_name(n):
    """Ordinal used in Wikipedia's century/millennium titles (11th, 12th, 13th, 21st ...)."""
    if n in CENTURY_WORDS:
        return CENTURY_WORDS[n]
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    if n % 10 == 1:
        return f"{n}st"
    if n % 10 == 2:
        return f"{n}nd"
    if n % 10 == 3:
        return f"{n}rd"
    return f"{n}th"


def bc_century(y):   # 2950 BC -> 30th century BC
    return century_name((y - 1) // 100 + 1) + " century BC"


def bc_decade(y):    # 753 BC -> 750s BC   (v1 returned the century floor, "700s BC")
    return f"{(y // 10) * 10}s BC"


def year_candidates(ym):
    """Titles that could be year ym's own article (mod convention: negative = BC).
    The bare number is tried last: '500', '999', '1000' are disambiguation pages and
    '1'..'10', '100' are articles about numbers."""
    if ym < 0:
        return [f"{-ym} BC"]
    return [f"{ym} (year)", f"AD {ym}", f"{ym}"]


def fallback_titles(ym):
    """Decade, century and millennium pages that hold year ym, in that order."""
    n = abs(ym)
    d = (n // 10) * 10
    c = (n - 1) // 100 + 1
    m = (n - 1) // 1000 + 1
    if ym < 0:
        return [f"{d}s BC (decade)", f"{d}s BC", f"{century_name(c)} century BC",
                f"{century_name(m)} millennium BC"]
    return [f"{d}s (decade)", f"{d}s", f"{century_name(c)} century",
            f"{century_name(m)} millennium"]


def targets_for_year(y):
    """Ordered candidate page titles. y>0 = BC, y<0 = AD (harvester convention)."""
    ym = -y
    return year_candidates(ym) + fallback_titles(ym)


# ---------- page classification (identical rules to survey/census/census.py) ----------
DECADE_RE = re.compile(r"^(\d+)s( BC)?( \(decade\))?$")
CENTURY_RE = re.compile(r"^(\d+)(?:st|nd|rd|th) century( BC)?$")
MILLENNIUM_RE = re.compile(r"^(\d+)(?:st|nd|rd|th) millennium( BC)?$")
YEAR_TPL = re.compile(r"\{\{\s*(?:Year nav(?: BC)?|Year dab|Year article header|About year|"
                      r"M1 year in topic|C\d+ year in topic|BC year in topic)\s*[|}]", re.I)
SHORTDESC_YEAR = re.compile(r"\{\{\s*Short description\s*\|[^}]*calendar year", re.I)
NAV_YEAR = re.compile(r"\{\{\s*(?:Year nav(?: BC)?|About year|Year dab)\s*\|\s*(?:1\s*=\s*)?"
                      r"(-?)(\d{1,4})\s*(BC)?\s*[|}]", re.I)


def page_type(title, w):
    if DECADE_RE.match(title):
        return "decade"
    if CENTURY_RE.match(title):
        return "century"
    if MILLENNIUM_RE.match(title):
        return "millennium"
    head = (w or "")[:8000]
    if YEAR_TPL.search(head) or SHORTDESC_YEAR.search(head):
        return "year"
    return "other"


def nav_year(w):
    """The year a year article declares in its nav template (negative = BC), if any."""
    m = NAV_YEAR.search((w or "")[:8000])
    if not m:
        return None
    n = int(m.group(2))
    bc = bool(m.group(1)) or bool(m.group(3)) or "year nav bc" in m.group(0).lower()
    return -n if bc else n


# ---------- page sources ----------
class LiveSource:
    """English Wikipedia over the Action API (rate-limited; see UA above)."""

    def __init__(self):
        self._res = {}

    def resolve(self, titles):
        """title -> {canonical, missing, disambig}; None for a transient failure."""
        todo = [t for t in titles if t not in self._res]
        for i in range(0, len(todo), 50):
            chunk = todo[i:i + 50]
            d = api({"action": "query", "titles": "|".join(chunk), "redirects": "1",
                     "prop": "pageprops", "ppprop": "disambiguation"})
            if not isinstance(d, dict):
                continue
            q = d.get("query", {})
            norm = {n["from"]: n["to"] for n in q.get("normalized", [])}
            red = {r["from"]: r["to"] for r in q.get("redirects", [])}
            info = {p.get("title"): p for p in q.get("pages", [])}
            for t in chunk:
                cur, hops = norm.get(t, t), 0
                while cur in red and hops < 6:
                    cur, hops = red[cur], hops + 1
                p = info.get(cur, {})
                self._res[t] = {"canonical": cur,
                                "missing": bool(p.get("missing")) or bool(p.get("invalid")) or not p,
                                "disambig": "disambiguation" in p.get("pageprops", {})}
        return {t: self._res.get(t) for t in titles}

    def wikitext(self, title):
        """(wikitext, status) with status in ok / missing / throttled."""
        d = api({"action": "parse", "page": title, "prop": "wikitext", "redirects": "1"})
        if d == "MISSING":
            return None, "missing"
        if not d or "parse" not in d:
            return None, "throttled"
        return d["parse"]["wikitext"], "ok"


class SnapshotSource:
    """The census's frozen snapshot: 3,010 pages with revision ids, plus the title
    resolutions (redirects, disambiguation flags) recorded when they were fetched.
    Re-runs the harvest offline, with zero API calls, against exactly the measured pages."""

    def __init__(self, snapshot=SNAPSHOT, titles=SNAPSHOT_TITLES):
        self.pages = {}
        with gzip.open(snapshot, "rt", encoding="utf-8") as f:
            for line in f:
                p = json.loads(line)
                self.pages[p["title"]] = p
        with open(titles, encoding="utf-8") as f:
            self.res = json.load(f)

    def resolve(self, titles):
        out = {}
        for t in titles:
            r = self.res.get(t)
            if r is None:
                out[t] = {"canonical": t, "missing": t not in self.pages, "disambig": False}
            else:
                out[t] = {"canonical": r["canonical"],
                          "missing": bool(r["missing"] or r["invalid"]),
                          "disambig": bool(r["disambig"])}
        return out

    def wikitext(self, title):
        p = self.pages.get(title)
        return (p["wikitext"], "ok") if p else (None, "missing")

    def revid(self, title):
        p = self.pages.get(title)
        return p.get("revid") if p else None


_DEFAULT_SOURCE = [None]


def default_source():
    if _DEFAULT_SOURCE[0] is None:
        _DEFAULT_SOURCE[0] = LiveSource()
    return _DEFAULT_SOURCE[0]


def find_year_page(y, source=None):
    """The page that holds year y (harvester convention: y>0 = BC, y<0 = AD).

    A real article for this very year wins over any decade/century redirect (Wikipedia
    has stale redirects such as '386 (year)' -> '380s' while the article '386' exists).
    Disambiguation pages, number articles and year articles for another year are skipped.
    Returns (title, wikitext, status, page_kind); status in ok / missing / throttled."""
    source = source or default_source()
    ym = -y
    saw_throttle = False
    grouped = None
    cands = year_candidates(ym)
    res = source.resolve(cands)
    for t in cands:
        r = res.get(t)
        if r is None:
            saw_throttle = True; continue
        if r["missing"] or r["disambig"]:
            continue
        c = r["canonical"]
        w, st = source.wikitext(c)
        if st == "throttled":
            saw_throttle = True; continue
        if w is None:
            continue
        ty = page_type(c, w)
        if ty == "year" and nav_year(w) in (None, ym):
            return c, w, "ok", "year"
        if ty in ("decade", "century", "millennium") and grouped is None:
            grouped = (c, w, ty)
    if grouped:
        return grouped[0], grouped[1], "ok", grouped[2]
    fb = fallback_titles(ym)
    res = source.resolve(fb)
    for t in fb:
        r = res.get(t)
        if r is None:
            saw_throttle = True; continue
        if r["missing"] or r["disambig"]:
            continue
        c = r["canonical"]
        w, st = source.wikitext(c)
        if st == "throttled":
            saw_throttle = True; continue
        if w is None:
            continue
        ty = page_type(c, w)
        if ty in ("decade", "century", "millennium"):
            return c, w, "ok", ty
    return None, None, ("throttled" if saw_throttle else "missing"), None


def fetch_with_fallback(y, source=None):
    """Backward-compatible wrapper: (title, wikitext, status)."""
    title, w, status, _ = find_year_page(y, source)
    return title, w, status


# ---------- parsing ----------
SKIP_LINK = re.compile(r'^\[\[?(File|Image|Category|Help|Wikipedia|Template|Portal|Special):', re.I)
BULLET_RE = re.compile(r'(?m)^\*+\s*(.+)$')
LINK_RE   = re.compile(r'\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]')
YEAR_RE   = re.compile(r'(?<![\w])(\d{1,4})\s*(BC|BCE)\b', re.I)
YEAR_AD_RE= re.compile(r'(?<![\w])(\d{3,4})\s*(?:AD|CE)\b', re.I)
HEAD_RE   = re.compile(r"(?m)^(={2,6})\s*(.*?)\s*\1\s*$")

# Level-2 sections whose bullets are people, prizes, books or links, not events at a place.
# Measured on the snapshot (v1 + sign fix): 1,800 kept "events" came from Births/Deaths,
# 54 from "Significant people", 9 from references / prizes / fiction.
SKIP_SECTIONS = re.compile(
    r"^(?:births?|deaths?|births and deaths|people|significant people|notable people|"
    r"references|notes|further reading|external links|see also|sources|bibliography|"
    r"nobel prizes|right livelihood award|in fiction|predicted and scheduled events)\b", re.I)

KIND_RULES = [
    ("battle",   r'\b(battle|combat|defeat(?:ed|s)?\s+(?:the\s+)?(?:army|force)|rout|victory at)\b'),
    ("siege",    r'\b(siege|besiege|sack(?:ed)?|storm(?:ed)?|captur(?:e|ed|ing)\s+(?:the\s+)?city)\b'),
    ("disaster", r'\b(earthquake|eruption|volcano|flood|famine|plague|epidemic|pandemic|drought|fire|tsunami|hurricane|cyclone|pestilence)\b'),
    ("treaty",   r'\b(treaty|peace of|accord|armistice|pact|concordat|cession|annex(?:ed|ation))\b'),
    ("political",r'\b(founded|founding|establish(?:ed|ment)|unif(?:y|ied|ication)|crown(?:ed|ation)|dynasty|reign|elect(?:ed|ion)|independen|revolt|revolution|coup|assassin|throne|caliph|emperor|king|sultan|raja)\b'),
]


def classify(text):
    t = text.lower()
    for kind, pat in KIND_RULES:
        if re.search(pat, t): return kind
    return "incident"


MONTHS = {"January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"}
DATE_LINK = re.compile(
    r'^(?:\d{1,4}(?:\s*(?:BC|BCE|AD|CE))?|'
    r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
    r'(?:\s+\d{1,2})?|\d{1,2}\s+'
    r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
    r'|\d{1,4}s(?:\s*(?:BC|AD))?|'
    r'\d+(?:st|nd|rd|th)\s+century(?:\s*(?:BC|AD))?|'
    r'\d+(?:st|nd|rd|th)\s+millennium(?:\s*(?:BC|AD))?)$', re.I)
EVENT_LINK = re.compile(
    r'(battle|siege|sack|treaty|earthquake|eruption|famine|plague|flood|fire|'
    r'massacre|rebellion|revolt|council|synod|expedition|coronation|dynasty|'
    r'university|mosque|cathedral|temple|fort|palace|bridge|canal|city|empire|'
    r'kingdom|republic|caliphate|sultanate)', re.I)
GENERIC_STOP = {"List of", "Timeline of", "Category", "History of"}
STOP_EXACT = {"hunting", "constitution", "war", "peace", "fire", "famine", "plague", "summer",
              "winter", "spring", "autumn", "eclipse", "comet", "storm", "battle", "siege",
              "treaty", "council", "election", "coronation", "assassination", "rebellion",
              "crusade", "pilgrimage", "voyage", "expedition", "campaign", "reign", "dynasty",
              "christianity", "islam", "buddhism", "judaism", "hinduism", "church", "mosque",
              "papacy", "empire", "kingdom", "republic", "caliphate", "sultanate", "monarchy",
              "law", "trade", "coinage", "currency", "taxation", "slavery", "feudalism",
              "agriculture", "fishing", "mining", "metallurgy", "pottery", "weaving", "art",
              "architecture", "literature", "poetry", "music", "philosophy", "mathematics",
              "astronomy", "medicine", "alchemy", "navigation", "shipbuilding", "siege warfare"}


def _is_person(target, alias):
    t = (alias or target).split("/")[-1].strip()
    t = re.sub(r'\s*\(.*?\)\s*$', '', t)
    words = [w for w in t.split() if w[:1].isupper()]
    if not words:
        return False
    # honorifics / dynastic markers strongly imply a person
    if re.search(r'\b(I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII)\b$', t):
        return True
    if re.search(r'\b(of|the|von|van|de|del|della|al|ibn|bin|Khan|Shah|Raja|Rao)\b', t, re.I):
        return True
    # "Firstname Lastname" with exactly 2 capitalised tokens and no place hint
    if len(words) == 2 and not EVENT_LINK.search(t):
        return True
    return False


EVENT_ONLY = re.compile(
    r'^(Battle|Siege|Sack|Treaty|Council|Synod|Massacre|Rebellion|Revolt|Expedition|'
    r'Coronation|Dynasty|War|Campaign|Crusade|Eclipse|Plague|Famine|Flood|Fire|'
    r'Earthquake|Eruption|University|Mosque|Cathedral|Temple|Church|Monastery|'
    r'Palace|Fort|Castle|Bridge|Canal|Lighthouse|Pyramid|Stupa|Amphitheatre)\b', re.I)

NAMED_EVENT = re.compile(
    r'\b((?:Battle|Siege|Sack|Treaty|Massacre|Council|Synod)\s+of\s+'
    r'[A-Z][\w\-]*(?:\s+[A-Z][\w\-]*){0,3})')


def place_from_bullet(line):
    """First wikilink that is plausibly a LOCATION: skip dates, events, people, concepts."""
    for m in LINK_RE.finditer(line):
        target = m.group(1).strip()
        alias = (m.group(2) or "").strip()
        base = target.split("/")[-1].strip()
        if SKIP_LINK.match(target):
            continue
        if DATE_LINK.match(base):
            continue
        if any(target.startswith(g) for g in GENERIC_STOP):
            continue
        if base.lower() in STOP_EXACT:
            continue
        if EVENT_ONLY.match(base):
            continue
        if _is_person(target, alias):
            continue
        return target
    return None


def named_event(line):
    """A 'Battle/Siege/Treaty of X' phrase, if present — geocoded separately."""
    m = NAMED_EVENT.search(_dewiki(line))
    return m.group(1).strip() if m else None


MONTH_ALT = ("January|February|March|April|May|June|July|August|September|"
             "October|November|December")
DATE_FRAG = re.compile(
    r'^\[\[?(?:'
    r'(?:Early\s+|Late\s+|Mid-\s+|Mid\s+)?'
    r'(?:' + MONTH_ALT + r')(?:\s+\d{1,2})?'
    r'|\d{1,2}\s+(?:' + MONTH_ALT + r')'
    r'|(?:' + MONTH_ALT + r')(?:\s+or\s+(?:' + MONTH_ALT + r'))?'
    r'|(?:Spring|Summer|Autumn|Fall|Winter)'
    r'|\d{1,4}\s*(?:BC|BCE|AD|CE)'
    r'|\d{3,4}'
    r')\]?\]?(?:\s+[A-Za-z]{3,12})?\s*(?:&ndash;|&mdash;|–|—|-|:)\s*', re.I)

BIRTH_DEATH = re.compile(
    r'(?:\(d\.\s*\d|\(b\.\s*\d|\(died\s|\(born\s|\bd\.\s*\d{3,4}\b|'
    r'\bb\.\s*\d{3,4}\b|\bbirths\b|\bdeaths\b|'
    r'\(\s*\d{1,4}\s*(?:BC|BCE|AD|CE)?\s*(?:–|-|—)\s*\d{0,4}\s*(?:BC|BCE|AD|CE)?\s*\))', re.I)


def event_text(line):
    """Strip only a genuine leading date fragment; never strip a person or subject."""
    m = DATE_FRAG.match(line)
    return line[m.end():].strip() if m else line.strip()


def _dewiki(line):
    return re.sub(r'\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]',
                  lambda m: m.group(2) or m.group(1), line)


def is_birth_death(line):
    if BIRTH_DEATH.search(_dewiki(line)):
        return True
    low = line.lower()
    if low.startswith(("birth", "death", "births", "deaths")):
        return True
    return False


def bullets_with_sections(wikitext):
    """Every bullet harvester v1 read (same regex, same filters), with the level-2
    section it sits in."""
    heads = [(m.start(), len(m.group(1)), m.group(2).strip())
             for m in HEAD_RE.finditer(wikitext)]
    out, hi, top = [], 0, ""
    for m in BULLET_RE.finditer(wikitext):
        while hi < len(heads) and heads[hi][0] < m.start():
            if heads[hi][1] == 2:
                top = heads[hi][2]
            hi += 1
        line = m.group(1).strip()
        if not line or len(line) < 12:
            continue
        if SKIP_LINK.match(line):
            continue
        out.append((line, top))
    return out


def skip_section(section):
    return bool(SKIP_SECTIONS.match((section or "").strip()))


def bullets(wikitext):
    """Bullets that can be events: not in a Births / Deaths / people / references section."""
    return [line for line, sec in bullets_with_sections(wikitext) if not skip_section(sec)]


def fetch(title):
    """Live wikitext of one title (v1 API, kept for old callers)."""
    d = api({"action": "parse", "page": title, "prop": "wikitext"})
    if d == "MISSING":
        return None, "missing"
    if not d or "parse" not in d:
        return None, "throttled"
    w = d["parse"]["wikitext"]
    if w.lstrip().upper().startswith("#REDIRECT"):
        m = re.search(r'\[\[([^\]|#]+)', w)
        return None, ("redirect:" + m.group(1)) if m else "redirect"
    return w, "ok"


def clean_name(line):
    import html as _h
    s = re.sub(r'\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]',
               lambda m: m.group(2) or m.group(1).split('/')[-1], line)
    s = re.sub(r"'''?", '', s)
    s = re.sub(r'<ref[^>]*/?>.*?(</ref>|$)', '', s, flags=re.S)
    s = re.sub(r'<[^>]+>', '', s)
    s = re.sub(r'\{\{[^}]*\}\}', '', s)
    s = re.sub(r'\[\d+\]|\[\[|\]\]', '', s)
    s = _h.unescape(s)
    return re.sub(r'\s+', ' ', s).strip(' .;,:-')
