#!/usr/bin/env python3
"""Step 2a/2b of the "<50%" plan: epidemics and disasters, Wikipedia first, other sources second.

Primary (English Wikipedia, dump 2026-10-01, read offline by wpdump.py):
  List of epidemics and pandemics; COVID-19 pandemic in <place> (one page per place);
  List of famines; List of famines in China; List of historical earthquakes; List of
  earthquakes in <year> (1900-2026); four volcanic-eruption lists; four tsunami lists;
  five flood lists.
  A row is placed by, in order: a {{coord}} in the row; the coordinates of the event's own
  article (e.g. "1556 Shaanxi earthquake"); the volcano's article; the linked or flagged
  locations (a city or site, else the region or state, as in build_regional.py).
Secondary (only where no Wikipedia row of the same kind is within 150 km and one year):
  NOAA NCEI significant earthquakes, tsunamis and volcanic eruptions; Smithsonian GVP Holocene
  eruptions; plague outbreaks 1339-1900 (Biraben, digitised by Buentgen 2012 and Atanasiu 2008,
  merged by Schmid 2015; Zenodo 14973).

Kinds are specific (epidemic, plague, pandemic, famine, earthquake, tsunami, volcano, flood):
all are in InWorldInterventionDetector.REFUSED_KINDS, so none can be "stopped".
Writes worldfill/hazards_report.json and history/events_hazards.json.gz.
Usage: python3 build_hazards.py [--dry-run]
"""
import collections, gzip, hashlib, html, json, math, os, re, subprocess, sys, time, zipfile

sys.path.insert(0, "/home/user/worldfill")
import build_regional as BR    # noqa: E402  Places, Polities, Hyde, Existing, hav
import modpack as M            # noqa: E402
import wpdump as W             # noqa: E402

LISTS = os.path.expanduser("~/.cache/wpdump/listpages.jsonl.gz")
COVID = os.path.expanduser("~/.cache/wpdump/covid_titles.json")
SRC = os.environ.get("SRCDATA", os.path.expanduser("~/.cache/srcdata"))
REPORT = "/home/user/worldfill/hazards_report.json"
PACK_FILE = "events_hazards.json.gz"
UA = "EternalEngineWorldFill/1.0 (historical data build; research use)"
log = BR.log

PAGE_KIND = [
    (r"^List of epidemics and pandemics$", "epidemic"),
    (r"^List of famines", "famine"),
    (r"earthquakes", "earthquake"),
    (r"volcanic eruptions", "volcano"),
    (r"tsunamis", "tsunami"),
    (r"floods", "flood"),
]
# local radius (km) for a row placed at a spot; region/state placements keep their own radius
LOCAL_R = {"earthquake": 50, "volcano": 40, "tsunami": 60, "flood": 50, "famine": 60,
           "epidemic": 30, "plague": 25, "pandemic": 30}
EFFECT = {"epidemic": "lockdown", "plague": "lockdown", "pandemic": "lockdown"}
WORD = {"earthquake": "Earthquake", "volcano": "Eruption", "tsunami": "Tsunami", "flood": "Flood",
        "famine": "Famine", "epidemic": "Epidemic", "plague": "Plague", "pandemic": "Pandemic"}
MAX_SPAN = {"famine": 15, "epidemic": 15, "plague": 5, "pandemic": 6}
AREA_KINDS = {"epidemic", "plague", "pandemic", "famine", "flood"}
EVENT_WORDS = r"(famine|plague|epidemic|pandemic|earthquake|eruption|tsunami|flood|fever|pox|influenza|cholera|death)"


# ------------------------------------------------------------------ wikitext tables
def split_top(s, sep):
    """Split on sep outside [[...]] and {{...}}."""
    out, depth_l, depth_t, cur, i = [], 0, 0, [], 0
    while i < len(s):
        two = s[i:i + 2]
        if two == "[[":
            depth_l += 1; cur.append(two); i += 2; continue
        if two == "]]" and depth_l:
            depth_l -= 1; cur.append(two); i += 2; continue
        if two == "{{":
            depth_t += 1; cur.append(two); i += 2; continue
        if two == "}}" and depth_t:
            depth_t -= 1; cur.append(two); i += 2; continue
        if not depth_l and not depth_t and s.startswith(sep, i):
            out.append("".join(cur)); cur = []; i += len(sep); continue
        cur.append(s[i]); i += 1
    out.append("".join(cur))
    return out


ATTR = re.compile(r'^\s*(?:[a-z-]+\s*=\s*(?:"[^"]*"|\'[^\']*\'|[^\s|]+)\s*)+$', re.I)


def cell_parts(raw):
    """'rowspan="2" | text' -> (attrs, text)."""
    parts = split_top(raw, "|")
    if len(parts) >= 2 and ATTR.match(parts[0] or " "):
        return parts[0], "|".join(parts[1:])
    return "", raw


def span(attrs, name):
    m = re.search(name + r'\s*=\s*"?(\d+)', attrs or "", re.I)
    return int(m.group(1)) if m else 1


def tables(text):
    """Every wikitable -> (header names, rows of raw cell strings), rowspans filled in."""
    out = []
    for m in re.finditer(r"(?ms)^\{\|(.*?)^\|\}", text):
        body = m.group(1)
        if "wikitable" not in body.split("\n", 1)[0]:
            continue
        rows, cur, heads = [], None, []
        for line in body.split("\n")[1:]:
            s = line.strip()
            if s.startswith("|-"):
                if cur is not None:
                    rows.append(cur)
                cur = []
                continue
            if s.startswith("|+") or s.startswith("{|"):
                continue
            if cur is None:
                cur = []
            if s.startswith("!"):
                cur.extend(("h", c) for c in split_top(s[1:], "!!"))
            elif s.startswith("|"):
                cur.extend(("d", c) for c in split_top(s[1:], "||"))
            elif cur:
                k, c = cur[-1]
                cur[-1] = (k, c + "\n" + line)
        if cur:
            rows.append(cur)
        grid, carry, hdr_rows = [], {}, []
        for r in rows:
            is_head = bool(r) and all(k == "h" for k, _ in r)
            line, col, src = [], 0, list(r)
            while src or any(c >= col for c in carry):
                if col in carry:
                    n, val = carry[col]
                    line.append(val)
                    carry[col] = (n - 1, val)
                    if n - 1 <= 0:
                        del carry[col]
                    col += 1
                    continue
                if not src:
                    break
                _k, c = src.pop(0)
                a, t = cell_parts(c)
                rs = span(a, "rowspan")
                for _ in range(span(a, "colspan")):
                    line.append(t)
                    if rs > 1:
                        carry[col] = (rs - 1, t)
                    col += 1
            if not line:
                continue
            if is_head and not grid:
                hdr_rows.append([clean(x)[0] for x in line])
            else:
                grid.append(line)
        # header rows stacked: "Belligerents" over "Victorious party" -> "belligerents: victorious party"
        names = []
        width = max((len(h) for h in hdr_rows), default=0)
        for i in range(width):
            parts = []
            for h in hdr_rows:
                v = h[i] if i < len(h) else ""
                if v and (not parts or parts[-1] != v):
                    parts.append(v)
            names.append(": ".join(parts))
        out.append(([n.lower() for n in names], grid))
    return out


# ------------------------------------------------------------------ cell cleaning
REF = re.compile(r"<ref[^>]*/>|<ref[^>]*>.*?</ref>|<!--.*?-->", re.S | re.I)
LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]")
TPL = re.compile(r"\{\{([^{}]*)\}\}")
FLAGS = {"flag", "flagcountry", "flagicon", "flagu", "flagdeco", "flag icon", "country flag"}


def dms(parts):
    nums, hemis = [], []
    for p in parts:
        p = p.strip()
        if re.fullmatch(r"-?\d+(?:\.\d+)?", p):
            nums.append(float(p))
        elif p.upper() in ("N", "S", "E", "W"):
            hemis.append((len(nums), p.upper()))
        elif "=" in p:
            break
    if len(hemis) >= 2:
        i, h1 = hemis[0]
        j, h2 = hemis[1]
        a, b = nums[:i], nums[i:j]

        def val(x):
            return sum(v / 60 ** k for k, v in enumerate(x[:3]))
        lat, lon = val(a), val(b)
        lat, lon = (-lat if h1 == "S" else lat), (-lon if h2 == "W" else lon)
        return lat, lon
    if len(nums) >= 2:
        return nums[0], nums[1]
    return None


def clean(raw):
    """raw cell -> (text, links, flags, coord)."""
    s = REF.sub("", raw or "")
    s = re.sub(r"<br\s*/?>", "; ", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    links, flags, coord = [], [], None
    for _ in range(4):
        def tpl(m):
            nonlocal coord
            parts = [p.strip() for p in m.group(1).split("|")]
            name = parts[0].lower()
            args = [p for p in parts[1:] if "=" not in p]
            if name in FLAGS and args:
                flags.append(args[0])
                return args[0] if name not in ("flagicon", "flagdeco", "flag icon") else ""
            if name == "coord":
                coord = coord or dms(parts[1:])
                return ""
            if name in ("sort", "sortname", "sort name") and len(args) >= 2:
                return args[-1]
            if name in ("circa", "c.", "c"):
                return "c. " + (args[0] if args else "")
            if name in ("nowrap", "nobr", "small", "nts", "ntsh", "abbr", "hs", "lang", "transl"):
                return args[0] if args and name != "ntsh" else ""
            if name in ("dts", "date", "start date", "end date", "birth date", "death date", "dtsort"):
                return " ".join(args[:3])
            if name in ("m", "mw"):
                return args[0] if args else ""
            if name in ("bc", "bce"):
                return (args[0] + " BC") if args else " BC"
            if name in ("ad", "ce"):
                return (args[0] + " AD") if args else ""
            return " ".join(args[:1]) if name in ("convert",) else ""
        s2 = TPL.sub(tpl, s)
        if s2 == s:
            break
        s = s2
    for m in LINK.finditer(s):
        if not re.match(r"(?i)(file|image|category):", m.group(1)):
            links.append((m.group(1).strip(), (m.group(2) or "").strip()))
    s = LINK.sub(lambda m: m.group(2) or m.group(1), s)
    s = re.sub(r"'{2,}", "", s)
    s = re.sub(r"\s+", " ", html.unescape(s)).strip(" ;,")
    return s, links, flags, coord


# ------------------------------------------------------------------ dates and numbers
YR = r"(\d{1,4})(?:\s*(BCE|BC|AD|CE))?"
RANGE = re.compile(YR + r"\s*(?:–|—|-|to|and)\s*" + YR, re.I)
ONE = re.compile(r"(?<![\d,.])" + YR + r"(?![\d,]|\s*(?:million|thousand|km|m\b|%))", re.I)
CENT = re.compile(r"(\d{1,2})(?:st|nd|rd|th)\s+century(\s*(?:BCE|BC))?", re.I)
KA = re.compile(r"^\s*~?\s*(\d+(?:\.\d+)?)\s*$")


def years_of(text, ka=False):
    """Date cell -> (start, end) in mod years (BC negative), or None."""
    t = (text or "").replace(",", "")
    if ka:
        m = KA.match(t)
        if not m:
            return None
        y = int(round(1950 - float(m.group(1)) * 1000))
        return (y, y) if y >= -3000 else None
    m = RANGE.search(t)
    if m:
        a, ea, b, eb = int(m.group(1)), (m.group(2) or "").upper(), int(m.group(3)), (m.group(4) or "").upper()
        bc_b = eb.startswith("BC")
        bc_a = ea.startswith("BC") or (bc_b and not ea)
        if b < a and not bc_b and len(m.group(3)) <= 2:          # "1918-20"
            b = int(str(a)[:-len(m.group(3))] + m.group(3))
        a, b = (-a if bc_a else a), (-b if bc_b else b)
        if a <= b and 1 <= abs(a) <= 2026 and 1 <= abs(b) <= 2026:
            return a, b
    m = CENT.search(t)
    if m:
        c = int(m.group(1))
        return ((-c * 100, -(c - 1) * 100 - 1) if m.group(2) else ((c - 1) * 100 + 1, c * 100))
    m = ONE.search(t)
    if m:
        y = int(m.group(1))
        if m.group(2) and m.group(2).upper().startswith("BC"):
            y = -y
        if 1 <= abs(y) <= 2026:
            return y, y
    return None


def deaths_of(text):
    t = (text or "").strip()
    m = re.search(r"(?:c\.\s*|~|over |about |at least |up to )?\d[\d,.]*(?:\s*(?:–|-)\s*\d[\d,.]*)?"
                  r"(?:\s*(?:million|thousand))?", t, re.I)
    return m.group(0).strip() if m else ""


# ------------------------------------------------------------------ Wikipedia rows -> events
ROLE = [
    ("start", r"^(start|began|begin)"), ("end", r"^(finish|end|ended)"),
    ("ka", r"age in"), ("date", r"\b(date|year|years|time|period)\b"),
    ("deaths", r"(death|fatalit|dead|casualt|losses|killed)"),
    ("disease", r"disease"), ("mag", r"(^mag|magnitude|^m$|mw)"), ("vei", r"\bvei\b"),
    ("volcano", r"volcano"), ("loc", r"(location|countr|region|place|area|affected)"),
    ("name", r"(event|name|epidemic|pandemic|main article|details|description)"),
]


def roles(names):
    out = {}
    for i, n in enumerate(names):
        for role, pat in ROLE:
            if role not in out and re.search(pat, n):
                out[role] = i
                break
    return out


class Builder:
    def __init__(self):
        self.places = BR.Places(W.Wiki(), BR.Polities(BR.Hyde()))
        self.st = collections.Counter()
        self.samples = collections.defaultdict(list)

    def place(self, year, links, flags, coord, text, prefer_site=False):
        """Best candidate among a row's evidence (rank 1 = a spot ... 4 = a state)."""
        if coord and -90 <= coord[0] <= 90 and -180 <= coord[1] <= 180:
            return (1, coord[0], coord[1], 20, "coord", "")
        best = None
        for target, alias in links:
            c = self.places.candidate(target, alias, year)
            if c and (best is None or c[0] < best[0]):
                best = c
        for f in flags:
            c = self.places.candidate(f, None, year)
            if c and (best is None or c[0] < best[0]):
                best = c
        if best is None and text:
            for part in re.split(r"[;,/]| and ", text)[:4]:
                part = part.strip(" .()")
                if len(part) >= 4 and part[:1].isupper():
                    c = self.places.candidate(part, None, year)
                    if c and (best is None or c[0] < best[0]):
                        best = c
        return best

    def event(self, kind, name, start, end, cand, conf_local, src):
        rank, lat, lon, rad, how, _t = cand
        local = rad <= 60
        if local:
            rad = LOCAL_R.get(kind, 30)
        end = min(end, start + MAX_SPAN.get(kind, 0)) + 1
        if start == 0:
            start = 1
        if end <= start:
            end = start + 1
        h = hashlib.sha1(f"{kind}|{name}|{start}|{lat:.2f}|{lon:.2f}".encode()).hexdigest()[:10]
        tag = src + ":" + how.split(":")[0]
        self.st["placed_" + tag] += 1
        if len(self.samples[tag]) < 8:
            self.samples[tag].append(f"{start}: {name[:100]} -> {how} r={rad}")
        return {"id": f"hz_{h}", "name": re.sub(r"\s+", " ", name)[:200], "start": start, "end": end,
                "lat": round(float(lat), 5), "lon": round(float(lon), 5), "radiusKm": int(rad),
                "kind": kind, "effect": EFFECT.get(kind, "disruption"),
                "confidence": conf_local if local else BR.REGIONAL}

    def from_lists(self):
        out = []
        with gzip.open(LISTS, "rt", encoding="utf-8") as f:
            pages = [json.loads(l) for l in f]
        for pg in pages:
            title = pg["title"]
            kind = next((k for pat, k in PAGE_KIND if re.search(pat, title)), None)
            if not kind:
                continue
            page_year = None
            m = re.fullmatch(r"List of earthquakes in (\d{4})", title)
            if m:
                page_year = int(m.group(1))
            for names, grid in tables(pg["text"]):
                rl = roles(names)
                if not ({"date", "start", "ka"} & rl.keys()) and page_year is None:
                    continue
                for row in grid:
                    def cell(role):
                        i = rl.get(role)
                        return clean(row[i]) if i is not None and i < len(row) else ("", [], [], None)
                    dt = cell("date") if "date" in rl else cell("start") if "start" in rl else cell("ka")
                    if page_year:
                        yrs = (page_year, page_year)          # date cells there are "January 25"
                    else:
                        yrs = years_of(dt[0], ka="ka" in rl and "date" not in rl)
                    if not yrs or yrs[0] < -3000 or yrs[0] > 2026:
                        self.st["row_no_year"] += 1
                        continue
                    nm, lc, vo, de = cell("name"), cell("loc"), cell("volcano"), cell("deaths")
                    k = kind
                    if kind == "epidemic":
                        dis = cell("disease")[0].lower() + " " + nm[0].lower()
                        k = "plague" if "plague" in dis else "pandemic" if "pandemic" in dis else "epidemic"
                    area = k in AREA_KINDS
                    coord = dt[3] or nm[3] or lc[3] or vo[3]
                    cands = []
                    if not area:
                        # a one-off event: its own coordinates, its article, the volcano, then the place
                        c = self.place(yrs[0], nm[1][:2] + vo[1][:1], [], coord, "")
                        if c and c[0] == 1:
                            cands = [c]
                        else:
                            c2 = self.place(yrs[0], lc[1], lc[2], None, lc[0])
                            cands = [x for x in (c2 if c2 and (not c or c2[0] < c[0]) else c,) if x]
                    else:
                        # an epidemic, famine or flood covers places: one event per named place (up to 5)
                        if coord:
                            cands = [(1, coord[0], coord[1], 20, "coord", "")]
                        seen_t = set()
                        for c in [self.places.candidate(t_, a_, yrs[0]) for t_, a_ in lc[1]] + \
                                 [self.places.candidate(f_, None, yrs[0]) for f_ in lc[2]]:
                            spot = c and (round(c[1], 1), round(c[2], 1))
                            if c and spot not in seen_t:
                                seen_t.add(spot); cands.append(c)
                        if not cands:
                            c = self.place(yrs[0], [], [], None, lc[0] or nm[0])
                            cands = [c] if c else []
                        cands = cands[:5]
                    if not cands:
                        self.st["row_unplaced"] += 1
                        continue
                    where = lc[0][:60]
                    text = nm[0]
                    ev_link = next((t for t, a in nm[1] if re.search(r"\d|" + EVENT_WORDS, t, re.I)), "")
                    if kind == "volcano":
                        vname = (vo[1][0][1] or vo[1][0][0]) if vo[1] else (vo[0] or text)
                        name = f"Eruption of {vname or where}"
                    elif 6 < len(text) <= 90 and not re.fullmatch(r"[\d\s.,–-]+", text):
                        name = text
                    elif ev_link:
                        name = ev_link
                    else:
                        name = f"{WORD[k]} in {where}" if where else WORD[k]
                    d = deaths_of(de[0])
                    if d and re.fullmatch(r"[0.,\s]+", d):
                        d = ""                                   # "0" = not known, not zero dead
                    if d and len(name) < 120:
                        unit = " million" if "million" in (names[rl["deaths"]] if "deaths" in rl else "") \
                            and "million" not in d else ""
                        name += f" ({d}{unit} dead)"
                    if where and where.lower()[:20] not in name.lower() and len(name) < 110 and kind != "earthquake":
                        name += f", {where}"
                    for cand in cands:
                        out.append(self.event(k, name, yrs[0], yrs[1], cand, "wikipedia_list", "wp"))
        # COVID-19: one page per place
        for t in json.load(open(COVID)):
            place = t[len("COVID-19 pandemic in "):]
            cand = self.places.candidate(place, None, 2020)
            if not cand:
                self.st["covid_unplaced"] += 1
                continue
            out.append(self.event("pandemic", f"COVID-19 pandemic in {place}", 2020, 2022, cand,
                                  "wikipedia_list", "wp_covid"))
        return out


# ------------------------------------------------------------------ secondary sources
def fetch(url, fn):
    p = os.path.join(SRC, fn)
    if not os.path.exists(p):
        os.makedirs(SRC, exist_ok=True)
        subprocess.run(["curl", "-sSL", "--retry", "4", "-m", "900", "-A", UA, "-o", p + ".part", url], check=True)
        os.rename(p + ".part", p)
    return p


def noaa(path, name, lo):
    p = os.path.join(SRC, f"ncei_{name}.json")
    if not os.path.exists(p):
        items, page = [], 1
        while True:
            r = subprocess.run(["curl", "-sSL", "--retry", "4", "-m", "300", "-A", UA,
                                f"https://www.ngdc.noaa.gov/hazel/hazard-service/api/v1/{path}?minYear={lo}&maxYear=2026&page={page}"],
                               capture_output=True, check=True)
            d = json.loads(r.stdout)
            items += d.get("items", [])
            if page >= (d.get("totalPages") or 1):
                break
            page += 1
            time.sleep(0.4)
        os.makedirs(SRC, exist_ok=True)
        json.dump(items, open(p, "w"))
    return json.load(open(p))


def titlecase(s):
    return re.sub(r"\s+", " ", (s or "").title().replace(" :", ":")).strip()


def secondary():
    recs = []
    for it in noaa("earthquakes", "quakes", -3000):
        y, la, lo = it.get("year"), it.get("latitude"), it.get("longitude")
        if isinstance(y, int) and la is not None and lo is not None and -3000 <= y <= 2026:
            mag = it.get("eqMagnitude")
            d = it.get("deaths") or it.get("deathsAmountOrder")
            name = f"Earthquake at {titlecase(it.get('locationName'))}" + (f" (magnitude {mag}" if mag else "") \
                + ((f"; {d:,} dead" if isinstance(d, int) and d > 0 else "") + ")" if mag else "")
            recs.append(("earthquake", name, y, y, float(la), float(lo), "noaa_ncei"))
    for it in noaa("tsunamis/events", "tsunamis", -3000):
        y, la, lo = it.get("year"), it.get("latitude"), it.get("longitude")
        if isinstance(y, int) and la is not None and lo is not None and -3000 <= y <= 2026:
            d = it.get("deaths")
            recs.append(("tsunami", f"Tsunami at {titlecase(it.get('locationName'))}"
                         + (f" ({d:,} dead)" if isinstance(d, int) and d > 0 else ""), y, y, float(la), float(lo), "noaa_ncei"))
    for it in noaa("volcanoes", "volcanoes", -3000):
        y, la, lo = it.get("year"), it.get("latitude"), it.get("longitude")
        if isinstance(y, int) and la is not None and lo is not None and -3000 <= y <= 2026:
            d = it.get("deaths")
            recs.append(("volcano", f"Eruption of {titlecase(it.get('name') or it.get('location'))}"
                         + (f" ({d:,} dead)" if isinstance(d, int) and d > 0 else ""), y, y, float(la), float(lo), "noaa_ncei"))
    g = json.load(open(fetch("https://webservices.volcano.si.edu/geoserver/GVP-VOTW/ows?service=WFS&version=2.0.0"
                             "&request=GetFeature&typeName=GVP-VOTW:Smithsonian_VOTW_Holocene_Eruptions"
                             "&outputFormat=application/json", "gvp_eruptions.json")))
    for f in g["features"]:
        p, co = f["properties"], (f.get("geometry") or {}).get("coordinates") or [None, None]
        y = p.get("StartDateYear")
        if isinstance(y, int) and co[0] is not None and -3000 <= y <= 2026:
            e = p.get("EndDateYear")
            e = e if isinstance(e, int) and e >= y else y
            vei = p.get("ExplosivityIndexMax")
            recs.append(("volcano", f"Eruption of {p.get('VolcanoName') or p.get('Volcano_Name')}"
                         + (f" (VEI {vei})" if vei is not None else ""), y, min(e, y + 5), float(co[1]), float(co[0]), "gvp"))
    zp = os.path.join(SRC, "plague", "europe-pnas", "resources", "plague-db-europe.txt")
    if not os.path.exists(zp):
        rec = json.loads(subprocess.run(["curl", "-sSL", "-A", UA, "https://zenodo.org/api/records/14973"],
                                        capture_output=True, check=True).stdout)
        f = rec["files"][0]
        z = fetch(f["links"]["self"], "plague_" + f["key"])
        with zipfile.ZipFile(z) as zf:
            for m in zf.namelist():
                if m.endswith("plague-db-europe.txt"):
                    zf.extract(m, os.path.join(SRC, "plague"))
    txt = open(zp, encoding="utf-8").read()
    for m in re.finditer(r'\{:lat ([-\d.]+), :lon ([-\d.]+), :name "((?:[^"\\]|\\.)*)", :source "((?:[^"\\]|\\.)*)", :year (-?\d+)\}', txt):
        y = int(m.group(5))
        if -3000 <= y <= 2026:
            recs.append(("plague", f"Plague outbreak in {m.group(3)}", y, y, float(m.group(1)), float(m.group(2)), "plague_biraben"))
    return recs


POINT_KINDS = {"earthquake", "tsunami", "volcano"}
COMPAT = {"earthquake": {"earthquake"}, "tsunami": {"tsunami"}, "volcano": {"volcano"},
          "plague": {"plague", "epidemic", "pandemic"}}


def main(dry=False):
    t0 = time.time()
    b = Builder()
    wp = b.from_lists()
    log(f"Wikipedia lists: {len(wp):,} events")
    # one Wikipedia event per (kind, name, start)
    seen, prim = set(), []
    for e in wp:
        k = (e["kind"], e["name"].lower()[:80], e["start"])
        if k not in seen:
            seen.add(k)
            prim.append(e)
    b.st["wp_dupes_within"] = len(wp) - len(prim)
    sec = secondary()
    log(f"secondary records: {len(sec):,}")
    # spatial-ish index of primary events by (kind, year)
    idx = collections.defaultdict(list)
    for e in prim:
        for y in range(e["start"], e["end"]):
            idx[(e["kind"], y)].append(e)
    kept_sec, sec_dupe, upgraded = [], collections.Counter(), 0
    seen_sec = set()
    for kind, name, y0, y1, la, lo, src in sec:
        hit = None
        for k2 in COMPAT.get(kind, {kind}):
            for y in (y0 - 1, y0, y0 + 1):
                for e in idx.get((k2, y), ()):
                    d = float(BR.hav(la, lo, e["lat"], e["lon"]))
                    if e["confidence"] != BR.REGIONAL and (
                            d <= 150.0 if kind in POINT_KINDS else (d <= 30.0 and abs(e["start"] - y0) <= 1)):
                        hit = e                                  # the same event, already placed
                    elif e["confidence"] == BR.REGIONAL and kind in POINT_KINDS and k2 == kind \
                            and e["start"] == y0 and d <= e["radiusKm"] and not e.get("_upgraded"):
                        # Wikipedia named it for a whole country; the secondary source has the spot
                        e.update(lat=round(la, 5), lon=round(lo, 5), radiusKm=LOCAL_R[kind],
                                 confidence="wikipedia_list", _upgraded=src)
                        hit = e
                        upgraded += 1
                    if hit:
                        break
                if hit:
                    break
            if hit:
                break
        key = (kind, round(la, 1), round(lo, 1), y0)
        if hit or key in seen_sec:
            sec_dupe[f"{src} / {'same as a Wikipedia row' if hit else 'repeat in the same source'}"] += 1
            continue
        seen_sec.add(key)
        e = b.event(kind, name, y0, y1, (1, la, lo, 20, src, ""), src, src)
        kept_sec.append(e)
        for y in range(e["start"], e["end"]):
            idx[(kind, y)].append(e)
    b.st["regional_rows_given_a_precise_spot"] = upgraded
    for e in prim:
        e.pop("_upgraded", None)
    allnew = prim + kept_sec
    log(f"primary {len(prim):,} + secondary kept {len(kept_sec):,}; matching against the mod")
    ex = BR.Existing(exclude=PACK_FILE)
    kept, why = [], collections.Counter()
    for e in allnew:
        hit = ex.match(dict(e, kind="disaster"))
        if hit:
            why[f"{hit[0]} / {hit[3]}"] += 1
        else:
            kept.append(e)
    kept.sort(key=lambda e: (e["start"], e["name"]))
    for e in kept:
        M.check_event(e)
    cnt = lambda key: dict(collections.Counter(e[key] for e in kept).most_common())
    report = {"seconds": round(time.time() - t0), "stats": dict(sorted(b.st.items())),
              "wikipedia_events": len(prim), "secondary_records": len(sec),
              "secondary_left_out_as_covered_by_wikipedia": dict(sec_dupe),
              "secondary_kept": len(kept_sec), "duplicates_of_installed_pins": dict(why.most_common()),
              "installed": len(kept), "installed_by_kind": cnt("kind"), "installed_by_confidence": cnt("confidence"),
              "installed_by_era": dict(sorted(collections.Counter(BR.era(e["start"]) for e in kept).items())),
              "samples": b.samples}
    json.dump(report, open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in report.items() if k != "samples"}, indent=1, ensure_ascii=False))
    if dry:
        print("dry run: nothing written to the mod")
        return
    doc = {"id": "hazards",
           "title": ("Epidemics, plague, famines, earthquakes, tsunamis, volcanic eruptions and floods: "
                     "Wikipedia lists first, then NOAA NCEI, Smithsonian GVP and the Biraben plague data "
                     "where Wikipedia has nothing nearby. Overlay only. Never stoppable. Not towns."),
           "source": "worldfill/build_hazards.py", "sites": [],
           "comparedSources": [
               "English Wikipedia list pages (dump 2026-10-01, CC BY-SA 4.0): epidemics and pandemics, "
               "COVID-19 by place, famines, historical earthquakes, earthquakes by year 1900-2026, "
               "volcanic eruptions, tsunamis, floods",
               "NOAA NCEI Global Significant Earthquake, Tsunami and Volcano databases (US government)",
               "Smithsonian GVP Volcanoes of the World, Holocene eruptions (WFS; citation requested)",
               "Plague outbreaks 1339-1900: Biraben via Buentgen et al. 2012 and Atanasiu et al. 2008, "
               "merged by Schmid et al. 2015 (Zenodo 14973, EPL-1.0)",
           ],
           "rejected": ["Secondary records with a Wikipedia row of the same kind within 150 km and a year",
                        "Records before 3000 BC; rows with no year or no place",
                        "Events already in the mod (same words within the event's radius and a year)"],
           "events": kept}
    path = M.write_pack(PACK_FILE, doc)
    added = M.register(PACK_FILE, after="events_wikipedia_regional.json.gz")
    log(f"wrote {path} ({len(kept)} events); index.json {'updated' if added else 'already lists it'}")


if __name__ == "__main__":
    main(dry="--dry-run" in sys.argv)
