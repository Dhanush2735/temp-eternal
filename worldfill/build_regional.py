#!/usr/bin/env python3
"""Step 1 of the "<50%" plan: the English Wikipedia year-page lines the harvest skipped.

Wikipedia is the primary source. Every line comes from an English Wikipedia year page (dump
2026-10-01, read offline by wpdump.py), and its place comes first from Wikipedia itself: the
coordinates of the articles the line links to (Wikipedia's geo_tags table), with their short
descriptions. Secondary sources only fill in what Wikipedia cannot say:
  * Cliopatria (history/world_rulers.json.gz): where a linked state was in that year
  * HYDE 3.2.1 (population/hyde_density.bin.gz): where that state's people lived, for its centre

Every link in a line is tried, and the most specific place wins:
  1 a city, site, battle or building                   radius 20 km   -> a normal local event
  2 a district                                         radius 25-40 km -> a normal local event
  3 a region, river, island or people ("Spartans")     radius 60-400 km
  4 a state or country, with its extent in that year   radius 60-800 km
Lines placed at radius > 60 km get confidence "wikipedia_region": the mod treats them as news
only. They never become a local event to stop, and never win over a closer local event
(HistoryGazetteer.nearestLocalEvent / nearestEvent).

Lines already in the mod are skipped:
  * same text and year as a v2 harvest record (harvest/events_v2_raw.jsonl.gz);
  * same event as any installed pin (same words within the event's radius and +-1 year).

Usage: python3 build_regional.py [--dry-run]
Writes worldfill/regional_report.json and history/events_wikipedia_regional.json.gz.
"""
import collections, gzip, hashlib, html, json, math, os, re, struct, sys, time

import numpy as np

sys.path.insert(0, "/home/user/harvest")
sys.path.insert(0, "/home/user/worldfill")
import harvester as H          # noqa: E402  bullet parsing, the v2 rules
import harvest_run as HR       # noqa: E402  bullet_year
import postprocess as P        # noqa: E402  scrub, filters, kinds, year repair
import modpack as M            # noqa: E402  pack I/O
import wpdump as W             # noqa: E402  offline Wikipedia

RES = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/"
PAGES_JSON = "/home/user/harvest/events_v2_raw.jsonl.pages.json"
V2_RAW = "/home/user/harvest/events_v2_raw.jsonl.gz"
PAGE_CACHE = os.path.expanduser("~/.cache/wpdump/yearpages.jsonl.gz")
LAND05 = os.path.expanduser("~/.cache/srcdata/morecheck/land05.npy")
REPORT = "/home/user/worldfill/regional_report.json"
PACK_FILE = "events_wikipedia_regional.json.gz"
REGIONAL = "wikipedia_region"
POINT = "wikipedia_coord"


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ------------------------------------------------------------------ HYDE people per cell
class Hyde:
    def __init__(self):
        b = gzip.open(RES + "population/hyde_density.bin.gz", "rb").read()
        off = 4
        _md, ns = struct.unpack(">ii", b[off:off + 8]); off += 8
        self.years = list(struct.unpack(">" + "i" * ns, b[off:off + 4 * ns])); off += 4 * ns
        nc, = struct.unpack(">i", b[off:off + 4]); off += 4
        rec = np.frombuffer(b[off:off + nc * (4 + ns)], dtype=np.uint8).reshape(nc, 4 + ns)
        idx = rec[:, :4].copy().view(">i4").ravel()
        codes = rec[:, 4:]
        self.dens = np.where(codes > 0, 10.0 ** ((codes.astype(np.float64) - 1) / 40 - 2.3), 0.0)
        self.cell = np.full(360 * 720, -1, dtype=np.int64)
        self.cell[idx] = np.arange(nc)
        rows = idx // 720
        if os.path.exists(LAND05):
            land = np.load(LAND05)
            self.area = land[rows, idx % 720].astype(np.float64)
        else:                                   # full cell area; fine for weights
            self.area = (0.5 * 111.32) ** 2 * np.cos(np.radians(-90 + 0.25 + rows * 0.5))

    def people(self, lat, lon, year):
        r = np.clip(((np.asarray(lat) + 90) / 0.5).astype(int), 0, 359)
        c = np.clip(((np.asarray(lon) + 180) / 0.5).astype(int), 0, 719)
        ci = self.cell[r * 720 + c]
        ys = self.years
        j = max([i for i, v in enumerate(ys) if v <= year] or [0])
        k = min(j + 1, len(ys) - 1)
        t = 0.0 if ys[k] == ys[j] else min(1.0, max(0.0, (year - ys[j]) / (ys[k] - ys[j])))
        ok = ci >= 0
        out = np.zeros(len(ci))
        da, db = self.dens[ci[ok], j], self.dens[ci[ok], k]
        both = (da > 0) & (db > 0)
        d = np.where(both, np.exp(np.log(np.where(both, da, 1)) * (1 - t) + np.log(np.where(both, db, 1)) * t),
                     da * (1 - t) + db * t)
        out[ok] = d * self.area[ci[ok]]
        return out


def hav(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp, dl = p2 - p1, np.radians(np.asarray(lon2) - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.minimum(1.0, a)))


# ------------------------------------------------------------------ Cliopatria extents
class Polities:
    def __init__(self, hyde):
        w = json.load(gzip.open(RES + "history/world_rulers.json.gz", "rt"))
        self.names = [p[0] for p in w["polities"]]
        self.by_qid = collections.defaultdict(list)
        for i, p in enumerate(w["polities"]):
            if len(p) > 1 and p[1]:
                self.by_qid[p[1]].append(i)
        tls, pl = w["timelines"], w["places"]
        self.lat = np.array(pl[0::3], dtype=np.float64) / 100
        self.lon = np.array(pl[1::3], dtype=np.float64) / 100
        spans = collections.defaultdict(list)
        for c, ti in enumerate(pl[2::3]):
            s = tls[ti]
            for q in range(0, len(s), 3):
                spans[s[q]].append((c, s[q + 1], s[q + 2]))
        self.sp = {p: np.array(v, dtype=np.int64) for p, v in spans.items()}
        self.hyde = hyde
        self.cache = {}

    def extent(self, p, year):
        key = (p, year // 10)
        if key in self.cache:
            return self.cache[key]
        a = self.sp.get(p)
        res = None
        if a is not None:
            m = (a[:, 1] <= year) & (year <= a[:, 2])
            if m.any():
                cells = a[m, 0]
                la, lo = self.lat[cells], self.lon[cells]
                w = self.hyde.people(la, lo, year)
                if w.sum() <= 0:
                    w = np.ones(len(cells))
                x = np.cos(np.radians(la)) * np.cos(np.radians(lo))
                y = np.cos(np.radians(la)) * np.sin(np.radians(lo))
                z = np.sin(np.radians(la))
                X, Y, Z = (w * x).sum(), (w * y).sum(), (w * z).sum()
                clat = math.degrees(math.atan2(Z, math.hypot(X, Y)))
                clon = math.degrees(math.atan2(Y, X))
                d = hav(clat, clon, la, lo)
                r = math.sqrt((w * d * d).sum() / w.sum()) * 1.25 + 30
                res = (round(clat, 4), round(clon, 4), int(min(800, max(60, r))), int(len(cells)))
        self.cache[key] = res
        return res

    def ruler_at(self, lat, lon, year):
        """Extent of the state ruling this point in this year (nearest register cell <= 60 km)."""
        if not hasattr(self, "cell_index"):
            self.cell_index = {(int(round((la + 90 - 0.25) / 0.5)), int(round((lo + 180 - 0.25) / 0.5))): c
                               for c, (la, lo) in enumerate(zip(self.lat, self.lon))}
            self.cell_spans = collections.defaultdict(list)
            for p, a in self.sp.items():
                for c, s0, e0 in a:
                    self.cell_spans[int(c)].append((p, int(s0), int(e0)))
        r0, c0 = int((lat + 90) / 0.5), int((lon + 180) / 0.5)
        best = None
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                c = self.cell_index.get((r0 + dr, (c0 + dc) % 720))
                if c is None:
                    continue
                d = float(hav(lat, lon, self.lat[c], self.lon[c]))
                if d <= 60 and (best is None or d < best[0]):
                    best = (d, c)
        if not best:
            return None
        for p, s0, e0 in self.cell_spans[best[1]]:
            if s0 <= year <= e0:
                e = self.extent(p, year)
                if e:
                    return e, self.names[p]
        return None

    def at(self, qid, year, tol=(0, 10, 25, 50)):
        """Extent of the state with this Wikidata id in (or near) this year."""
        for dy in tol:
            for yy in ((year,) if dy == 0 else (year - dy, year + dy)):
                for p in self.by_qid.get(qid, ()):
                    e = self.extent(p, yy)
                    if e:
                        return e, self.names[p]
        return None

    def latest(self, qid):
        """The most recent extent of a state (a modern country named in an old event)."""
        # Cliopatria sometimes gives two states one Wikidata id (Republic of China and the
        # People's Republic are both Q148): take the latest, then the one with the most land.
        best = None
        for p in self.by_qid.get(qid, ()):
            a = self.sp.get(p)
            if a is None:
                continue
            y = int(min(a[:, 2].max(), 2024))
            e = self.extent(p, y)
            if e and (best is None or (y, e[3]) > (best[0], best[1][3])):
                best = (y, e, p)
        return (best[1], self.names[best[2]]) if best else None


# ------------------------------------------------------------------ what a link points at
SKIP_SD = re.compile(r"\b(continent|ocean|subcontinent|hemisphere|planet|world|landmass|supercontinent)\b", re.I)
SKIP_TITLES = {"Eurasia", "Americas", "Europe", "Asia", "Africa", "Oceania", "Worldwide", "World", "Earth",
               "North America", "South America", "Afro-Eurasia", "Global"}
PERSON_SD = re.compile(
    r"\b(king|queen|emperor|empress|pharaoh|pope|saint|bishop|archbishop|patriarch|caliph|sultan|"
    r"shah|khan|prince|princess|duke|duchess|general|admiral|philosopher|poet|writer|painter|"
    r"composer|politician|statesman|scholar|monk|priest|prophet|consort|ruler|chieftain|warlord|"
    r"physician|mathematician|astronomer|historian|explorer|merchant|noble|nobleman|military leader)"
    r"\b|\(\s*(?:c\.\s*)?\d{1,4}\s*(?:bc|bce|ad|ce)?\s*[–-]", re.I)
COUNTRY_SD = re.compile(r"\b(country|sovereign state|island nation|nation in|microstate|"
                        r"constituent country)\b", re.I)
POLITY_SD = re.compile(r"\b(empire|kingdom|caliphate|sultanate|khanate|dynasty|historical state|"
                       r"former country|former state|polity|confederation|confederacy|republic|"
                       r"principality|duchy|emirate|realm|tribal|tribe|chiefdom|city-state|"
                       r"civili[sz]ation|culture)\b", re.I)
REGION_SD = re.compile(r"\b(region|province|state of|state in|federal state|governorate|prefecture|"
                       r"oblast|krai|historical region|geographic(?:al)? region|peninsula|"
                       r"archipelago|plateau|desert|valley|coast|basin|territory|lowlands|"
                       r"highlands|steppe|delta|sea)\b", re.I)
DISTRICT_SD = re.compile(r"\b(district|county|department|municipality|commune|borough|"
                         r"subprefecture|tehsil|taluk|mandal|parish|canton)\b", re.I)
POINT_SD = re.compile(r"\b(city|town|village|capital|port|fort|fortress|castle|citadel|temple|"
                      r"church|cathedral|basilica|monastery|abbey|mosque|palace|archaeological|"
                      r"ancient city|settlement|neighbou?rhood|suburb|battle|siege|bridge|tomb|"
                      r"pyramid|stupa|shrine|ruins|oasis|hill|mountain|volcano|lake|harbou?r|"
                      r"university|college|building|monument|site|island)\b", re.I)
DEFAULT_DIMS = {1000, 10000}            # {{coord}} defaults: not a real size


def dim_radius(dim, lo, hi, default):
    if not dim or dim in DEFAULT_DIMS:
        return default
    return int(min(hi, max(lo, dim / 2000.0)))


class Places:
    """Wikipedia link target -> where it is, how big, how sure. Cached per title."""

    def __init__(self, wiki, polities):
        self.wiki, self.pol = wiki, polities
        self.memo = {}
        self.stats = collections.Counter()

    def resolve(self, target):
        if target not in self.memo:
            hit = self.wiki.lookup(target)
            self.memo[target] = None if not hit else (hit[0], self.wiki.info(hit[1]))
        return self.memo[target]

    def candidate(self, target, alias, year):
        """(rank, lat, lon, radius_km, how, title) or None."""
        r = self.resolve(target)
        if not r:
            self.stats["link_missing"] += 1
            return None
        title, info = r
        if info["disambig"] or title in SKIP_TITLES:
            return None
        sd = info["shortdesc"] or ""
        g, qid = info["geo"], info["qid"]
        if qid and qid in self.pol.by_qid:
            hit = self.pol.at(qid, year)
            if hit:
                (lat, lon, rad, _n), pname = hit
                return (4, lat, lon, rad, "state:" + pname, title)
        if not g:
            return None
        if SKIP_SD.search(sd):
            return None
        if PERSON_SD.search(sd) and not POINT_SD.search(sd):
            return None
        t, dim = g["type"], g["dim"]
        lat, lon = g["lat"], g["lon"]
        if t == "country" or COUNTRY_SD.search(sd):
            modern = self.pol.latest(qid) if qid and qid in self.pol.by_qid else None
            clat, clon = (modern[0][0], modern[0][1]) if modern else (lat, lon)
            then = self.pol.ruler_at(clat, clon, year)     # who ruled that land in that year
            if then:
                (lat2, lon2, rad, _n), pname = then
                return (4, lat2, lon2, rad, "state:" + pname, title)
            if modern:
                (lat2, lon2, rad, _n), pname = modern
                return (4, lat2, lon2, rad, "country:" + pname, title)
            return (4, lat, lon, dim_radius(dim, 150, 800, 400), "country", title)
        if POLITY_SD.search(sd) and not POINT_SD.search(sd):
            return (4, lat, lon, dim_radius(dim, 150, 600, 300), "state", title)
        if t in ("adm1st", "state") or (REGION_SD.search(sd) and not POINT_SD.search(sd)):
            return (3, lat, lon, dim_radius(dim, 60, 400, 150), "region", title)
        if t == "river":
            return (3, lat, lon, 150, "river", title)
        if t == "adm2nd" or (DISTRICT_SD.search(sd) and not POINT_SD.search(sd)):
            return (2, lat, lon, 40, "district", title)
        if t == "adm3rd":
            return (2, lat, lon, 25, "district", title)
        if t in ("waterbody", "isle"):
            rad = dim_radius(dim, 20, 400, 30)
            return (3 if rad > 60 else 1, lat, lon, rad, t, title)
        # a city, site, battle, building, mountain... A demonym link ("[[Sparta|Spartans]]")
        # means the people, not the town: widen it.
        if alias and alias != target and " " not in alias and re.search(r"(?:ans|ites|enses|ese)$", alias):
            return (3, lat, lon, 200, "people", title)
        return (1, lat, lon, 20, "site", title)


def links(line):
    for m in H.LINK_RE.finditer(line):
        target = m.group(1).strip()
        alias = (m.group(2) or "").strip()
        base = target.split("/")[-1].strip()
        if H.SKIP_LINK.match("[[" + target) or H.DATE_LINK.match(base):
            continue
        if any(target.startswith(g) for g in H.GENERIC_STOP) or base.lower() in H.STOP_EXACT:
            continue
        yield target, alias


# ------------------------------------------------------------------ year pages from the dump
def year_pages():
    pages = json.load(open(PAGES_JSON, encoding="utf-8"))
    cached = {}
    if os.path.exists(PAGE_CACHE):
        with gzip.open(PAGE_CACHE, "rt", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                cached[r["title"]] = r["text"]
    need = [t for t in pages if t not in cached]
    if need:
        log(f"fetching {len(need)} pages from the dump")
        got = W.Wiki().texts(need, workers=2, progress=lambda d, n: log(f"  streams {d}/{n}"))
        with gzip.open(PAGE_CACHE, "at", encoding="utf-8") as f:
            for t, (final, text) in got.items():
                f.write(json.dumps({"title": t, "final": final, "text": text}, ensure_ascii=False) + "\n")
                cached[t] = text
    return pages, cached


# ------------------------------------------------------------------ duplicates in the mod
TOK = re.compile(r"[^\W\d_]+")
STOPW = set("battle siege of the and in at on a an treaty sack massacre first second third".split())


def toks(s):
    return {w for w in TOK.findall((s or "").lower()) if len(w) > 2 and w not in STOPW}


class Existing:
    def __init__(self, exclude=None):
        """Every installed pin except those of the pack being rebuilt (exclude: its file name)."""
        self.by_year = collections.defaultdict(list)
        n = 0
        for x in M.existing_events(exclude={exclude or PACK_FILE}):
            if x.get("kind") == "war":
                continue
            self.by_year[int(x["_start"])].append((toks(x.get("name")), x["lat"], x["lon"],
                                                   P.classify(x.get("name") or "") == "disaster",
                                                   x["_pack"], x.get("id"), x.get("name")))
            n += 1
        log(f"existing events to match against: {n:,}")

    def match(self, e):
        et = toks(e["name"])
        lim = max(60.0, e["radiusKm"] + 20.0)
        dis = e["kind"] == "disaster"
        for y in (e["start"] - 1, e["start"], e["start"] + 1):
            for xt, la, lo, xdis, pack, xid, xname in self.by_year.get(y, ()):
                d = float(hav(e["lat"], e["lon"], la, lo))
                if d > lim:
                    continue
                if xt and xt <= et:
                    return pack, xid, xname, "same name"
                if xt and et and len(xt & et) / len(xt | et) >= 0.6:
                    return pack, xid, xname, "same wording"
                if dis and xdis and (xt & et):
                    return pack, xid, xname, "same disaster"
        return None


# ------------------------------------------------------------------ main
REGION_EFFECT = {"political": "political", "treaty": "political", "disaster": "disruption"}
LEARN_FROM = {"state", "country", "region", "people", "river", "isle", "waterbody"}
COMMON = set("""the this that these king queen emperor empress empire kingdom battle treaty siege north
south east west northern southern eastern western central upper lower great greater new old saint
christian christians muslim muslims islamic catholic church pope army navy city island river
republic dynasty state states people country land lands coast sea first second third roman catholic
during after before with from into under about""".split())
TITLE_WORDS = set("""King Queen Emperor Empress Pope Saint St Lord Lady Prince Princess Duke Duchess General
Sir Pharaoh Sultan Caliph Shah Khan Tsar Czar Count Countess Bishop Archbishop Patriarch Admiral
Consul Chancellor President Governor Marquis Earl Baron Emir Raja Maharaja Rajah Nawab""".split())
WORD = re.compile(r"[A-Za-z\u00C0-\u024F][\w'\u2019\-]*")


def build_events(pages, texts, v2, places):
    """Both passes over the year pages -> (events, stats, samples)."""
    st = collections.Counter()
    out, seen, samples = [], set(), collections.defaultdict(list)
    names = collections.defaultdict(collections.Counter)   # surface form -> region/state titles
    seen_at = collections.defaultdict(list)                 # (form, title) -> years it was linked
    unplaced = []

    def meanings(form, year):
        """Titles a name stood for, the ones used within 300 years first, then the plain article."""
        opts = sorted(vocab[form].items(),
                      key=lambda tc: (-sum(1 for y in seen_at[(form, tc[0])] if abs(y - year) <= 300), -tc[1]))
        near = [t for t, _ in opts if any(abs(y - year) <= 300 for y in seen_at[(form, t)])][:4]
        rest = [t for t, _ in opts if t not in near][:3]
        return near + ([form] if form not in near else []) + [t for t in rest if t != form]

    def emit(best, name, year, via):
        rank, lat, lon, rad, how, src = best
        key = (name.lower()[:110], year)
        if key in seen:
            st["dupe_within"] += 1
            return
        seen.add(key)
        kind = P.classify(name)
        regional = rad > 60
        h = hashlib.sha1(f"{name}|{year}|{lat}|{lon}".encode()).hexdigest()[:10]
        tag = via + how.split(":")[0]
        out.append({
            "id": f"wpr_{h}",
            "name": re.sub(r"\s+", " ", name)[:300],
            "start": year, "end": year + 1,
            "lat": round(float(lat), 5), "lon": round(float(lon), 5),
            "radiusKm": int(rad),
            "kind": kind,
            "effect": REGION_EFFECT.get(kind, "note") if regional else P.EFFECT[kind],
            "confidence": REGIONAL if regional else POINT,
            "place": src, "placedBy": tag,
        })
        st["placed_" + tag] += 1
        if len(samples[tag]) < 12:
            samples[tag].append(f"{year}: {name[:110]}  ->  {how} r={rad}")

    # ---- pass 1: the line's own links
    for n_page, (title, years) in enumerate(pages.items()):
        w = texts.get(title)
        if w is None:
            st["page_missing"] += 1
            continue
        y_h = -min(years)                          # harvester convention: positive = BC
        for raw in H.bullets(w):
            line = html.unescape(raw)
            st["bullets"] += 1
            if H.is_birth_death(line):
                st["births_deaths"] += 1
                continue
            name = H.clean_name(H.event_text(line))
            if len(name) < 12:
                st["too_short"] += 1
                continue
            yr_h = HR.bullet_year(line, y_h)
            if (name.lower()[:110], yr_h) in v2:
                st["already_harvested"] += 1
                continue
            st["candidates"] += 1
            name = P.scrub(name.strip())
            if name is None or P.MYTH.search(name) or P.NOISE.search(name) or P.LIST_ARTIFACT.search(name) \
                    or not (14 <= len(name) <= 300):
                st["drop_filters"] += 1
                continue
            year = -yr_h
            if not P.plausible(year, title):
                fixed = P.page_year(title, year)
                if fixed == year:
                    st["drop_year"] += 1
                    continue
                year = fixed
            if year == 0 or year < -10000 or year > P.MAX_YEAR:
                st["drop_year"] += 1
                continue
            best = None
            for target, alias in links(line):
                c = places.candidate(target, alias, year)
                if c and c[0] >= 3 and c[4].split(":")[0] in LEARN_FROM:
                    for form in {target.strip(), alias.strip()} - {""}:
                        names[form][c[5]] += 1
                        seen_at[(form, c[5])].append(year)
                if c and (best is None or c[0] < best[0]):
                    best = c
            if best:
                emit(best, name, year, "")
            else:
                unplaced.append((year, name, line))
        if n_page % 500 == 0:
            log(f"  {n_page}/{len(pages)} pages, {len(out)} placed")

    # ---- pass 2: plain-text names learned from Wikipedia's own links ("Egyptian" -> Ancient Egypt)
    vocab = {f: c for f, c in names.items()
             if len(f) >= 4 and f[:1].isupper() and f.lower() not in COMMON and sum(c.values()) >= 2}
    longest = max((len(f.split()) for f in vocab), default=1)
    log(f"pass 1 placed {len(out):,}; pass 2: {len(unplaced):,} unplaced lines, "
        f"{len(vocab):,} learned region/state names")
    for year, name, line in unplaced:
        text = H._dewiki(line)
        words = [m.group(0) for m in WORD.finditer(text)]
        best = None
        for i in range(len(words)):
            if not words[i][:1].isupper() or (i and words[i - 1].rstrip(".") in TITLE_WORDS):
                continue
            for n in range(min(longest, len(words) - i), 0, -1):
                form = " ".join(words[i:i + n])
                if form in vocab:
                    for t in meanings(form, year):
                        c = places.candidate(t, None, year)
                        if c and c[0] >= 3:
                            best = c
                            break
                    break
            if best:
                break
        if best:
            emit(best, name, year, "text_")
        else:
            st["no_place_found"] += 1
            if len(samples["unplaced"]) < 40:
                samples["unplaced"].append(f"{year}: {name[:150]}")
    st["learned_names"] = len(vocab)
    return out, st, samples


def era(y):
    return ("3000-1001 BC" if y < -1000 else "1000-1 BC" if y < 1 else "AD 1-999" if y < 1000
            else "1000-1499" if y < 1500 else "1500-1799" if y < 1800 else "1800-2026")


def main(dry=False):
    t0 = time.time()
    pages, texts = year_pages()
    log(f"pages: {len(texts)} of {len(pages)} in hand")
    v2 = set()
    with gzip.open(V2_RAW, "rt", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            v2.add((r["name"].lower()[:110], r["start"]))
    places = Places(W.Wiki(), Polities(Hyde()))
    out, st, samples = build_events(pages, texts, v2, places)
    log(f"matching {len(out):,} against the mod")
    ex = Existing()
    kept, dropped, why = [], [], collections.Counter()
    for e in out:
        hit = ex.match(e)
        if hit:
            why[f"{hit[0]} / {hit[3]}"] += 1
            if len(dropped) < 3000:
                dropped.append({"new": e["name"][:150], "year": e["start"], "kept_pack": hit[0],
                                "kept_id": hit[1], "kept_name": (hit[2] or "")[:150], "reason": hit[3]})
        else:
            kept.append(e)
    kept.sort(key=lambda e: (e["start"], e["name"]))
    for e in kept:
        M.check_event(e)
    by = lambda k: dict(collections.Counter(e[k] for e in kept).most_common())
    report = {
        "seconds": round(time.time() - t0), "stats": dict(sorted(st.items())),
        "placed": len(out), "duplicates_left_out": len(out) - len(kept), "installed": len(kept),
        "duplicates_by_pack_and_reason": dict(why.most_common()),
        "installed_by_confidence": by("confidence"), "installed_by_placedBy": by("placedBy"),
        "installed_by_kind": by("kind"),
        "installed_by_era": dict(sorted(collections.Counter(era(e["start"]) for e in kept).items())),
        "link_stats": dict(places.stats),
        "samples": samples, "duplicates_sample": dropped[:400],
    }
    json.dump(report, open(REPORT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in report.items() if k not in ("samples", "duplicates_sample")},
                     indent=1, ensure_ascii=False))
    if dry:
        print("dry run: nothing written to the mod")
        return
    for e in kept:
        e.pop("placedBy", None)
        e.pop("place", None)
    doc = {
        "id": "wikipedia_regional",
        "title": ("English Wikipedia year-page events that name no exact spot, placed at the "
                  "region, state or country they name (news only), plus lines placed at a site "
                  "through Wikipedia's own article coordinates. Overlay only. Not towns. Not "
                  "attacker spawn."),
        "source": "English Wikipedia dump 2026-10-01 (CC BY-SA 4.0); worldfill/build_regional.py",
        "sites": [],
        "comparedSources": [
            "English Wikipedia year, decade and century pages (dump 2026-10-01): the line and its links",
            "Wikipedia geo_tags (article coordinates) and short descriptions: where each link is",
            "Region and state names learned from the pages' own links, found in unlinked text",
            "Cliopatria v0.2.1 (world_rulers.json.gz): a linked state's extent in that year",
            "HYDE 3.2.1 (hyde_density.bin.gz): where that state's people lived (its centre)",
        ],
        "rejected": [
            "Births, deaths and people sections (same rules as the v2 harvest)",
            "Lines already harvested by v2, or the same event as an installed pin",
            "Links to continents, oceans and people; disambiguation pages",
        ],
        "events": kept,
    }
    path = M.write_pack(PACK_FILE, doc)
    added = M.register(PACK_FILE, after="events_wikipedia.json.gz")
    log(f"wrote {path} ({len(kept)} events); index.json {'updated' if added else 'already lists it'}")


if __name__ == "__main__":
    main(dry="--dry-run" in sys.argv)
