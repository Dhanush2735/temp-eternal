#!/usr/bin/env python3
# ============================================================
# Step 32, part 3: build buildings_famous.json.gz.
#
#   python3 build_famous_buildings.py
#
# What goes in
# ------------
# Part 1's 22,281 structures Wikidata can date, plus part 2's 1,324 that the
# gazetteer dates: 23,605 famous structures, each with a point, a kind, the year
# it was built, the year it ended (B19 ruins needs this), and how famous it is.
#
# The three decisions that shape the file
# ---------------------------------------
# 1. DISPLAY KIND, BY SPECIFICITY. A structure is usually filed under several
#    Wikidata classes -- a castle is often also a fortification -- and part 1
#    found the class labels are wrong for display often enough to matter:
#    Westminster Abbey comes back typed "temple". So the kind is taken from the
#    *narrowest* class the thing belongs to, narrowest measured by how many
#    structures the class holds overall. Church building (11,291 members) beats
#    temple (12,290), so the abbey is a church. Citadel (63) beats fortification
#    (3,342). This is data-driven, not a hand list, and it needs no judgement
#    about which class is "really" right.
#
# 2. HOLY PLACES KEEP THEIR KIND. Where a structure is also one of step 30b's
#    19,828 holy places (same name, within 2 km), the holy register's kind wins:
#    it is finer ("basilica", "cathedral", "Hindu temple", "mosque") than
#    anything Wikidata's class tree gives. The building is not dropped -- B8
#    still needs it, and only B8 carries the end date -- it is flagged holy so
#    the placement layer does not build the same thing twice.
#
# 3. RECORDED BEATS ESTIMATED. Where Wikidata has a date, that date is kept even
#    when the structure also sits on a curated gazetteer site with its own
#    window: an inception year is a fact, a site window is a bound. The site is
#    still recorded, so the building can be tied back to it.
#
# Written to the mod's own history folder, in the columnar shape
# CultureAtlas uses for holy_places (lat and lon as thousandths of a degree).
# ============================================================
import gzip
import io
import json
import os
import re
import sys
import time
from collections import Counter
from math import radians, sin, cos, asin, sqrt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fetch_buildings_wd import TEST_PLACES, CLASSES  # noqa: E402

RAW = os.path.join(HERE, "build", "buildings", "raw")
LOGS = os.path.join(HERE, "logs")
HISTORY = os.path.join(HERE, "..", "eternal", "src", "main", "resources",
                       "data", "eternalengine", "eternal", "history")
OUT = os.path.join(HISTORY, "buildings_famous.json.gz")

# Wikidata class -> what the mod calls it. One place to change if the wording
# ever needs to change; the pack stores these strings.
KIND = {
    "castle": "castle", "fort": "fort", "fortification": "fortification",
    "citadel": "citadel", "city gate": "city gate", "city wall": "city wall",
    "church building": "church", "mosque": "mosque", "temple": "temple",
    "monastery": "monastery", "stupa": "stupa", "tomb": "tomb",
    "palace": "palace", "bridge": "bridge", "tower": "tower",
    "monument": "monument", "theatre building": "theatre",
    "archaeological site": "archaeological site",
    # part 5 (B16, B19): walls, ramparts and amphitheatres get a class of their
    # own, so they stop being lumped in with fortifications and theatres.
    "city walls": "city wall", "defensive wall": "wall", "rampart": "rampart",
    "amphitheatre": "amphitheatre", "Roman amphitheatre": "amphitheatre",
    "ruins": "ruins", "castle ruin": "castle ruin", "city wall": "city wall",
}

# Being a ruin is a state, not a kind. A ruined castle is still a castle, so
# these are kept out of the kind and carried on their own flag instead -- that
# is the only way B19 can know a place is a ruin when Wikidata never recorded
# the year it fell.
RUIN_CLASSES = {"ruins", "castle ruin"}

# B16: what a city's defences are made of. Castles are left out on purpose --
# a castle is a fortified house, it has its own kind, and it is B8's business;
# counting them here would bury the 26 city walls under 1,655 castles.
FORTIFICATION_KINDS = {"city wall", "wall", "rampart", "city gate", "citadel",
                       "fort", "fortification"}

HISTORY_PACKS = ["indus.json", "mesopotamia.json", "egypt.json", "china.json",
                 "mediterranean.json", "south_asia.json", "americas.json",
                 "afro_islamic.json"]

# ---------------------------------------------------------------------------
# Step 33 (E14 materials, B9 styles): what the building is made of and what
# style it is in, where Wikidata says (P186 material used, P149 architectural
# style). Part 1's survey: 8.5% of the items carry a material and 30% a style,
# and the styles are the regional, dated vocabulary B9 needs -- Gothic,
# Dravidian, Indo-Islamic, Safavid, Qajar, Brick Gothic.
#
# Labels are kept in a little dictionary at the top of the pack and the rows
# carry small integers: 23,534 rows times a repeated string would cost more
# than the whole dictionary.
def style_name(label):
    """Wikidata's style labels disagree with each other: 'Gothic architecture'
    beside 'baroque architecture', 'modern architecture' beside 'Gothic art'.
    The mod says 'in the X style', so the trailing word is dropped and the
    case is made uniform."""
    s = re.sub(r"\s+", " ", (label or "").strip())
    if not s:
        return ""
    s = s[:1].upper() + s[1:]
    low = s.lower()
    for suf in (" architecture", " style"):
        if low.endswith(suf):
            s = s[: -len(suf)].strip()
            break
    return s


def material_name(label):
    return re.sub(r"\s+", " ", (label or "").strip().lower())

# Step 30b's holy places carry 224 different kind strings -- "church",
# "benedictine abbey", "Eastern Orthodox cathedral", "dzong in Tibet", "areal".
# Far too many for a placement layer to act on, and most of the tail is noise.
# So a holy kind is used only when it lands on one of these canonical kinds,
# first match wins; anything else falls back to the Wikidata kind above.
# 19,713 of the 19,828 holy places land on one (99.4%).
HOLY_RULES = [
    ("cathedral", ("cathedral", "minster", "duomo")),
    ("basilica", ("basilica", "baptistery")),
    ("chapel", ("chapel", "oratory")),
    ("church", ("church", "mission")),
    ("synagogue", ("synagogue", "kenesa")),
    ("mosque", ("mosque", "masjid", "jama", "külliye")),
    ("gurdwara", ("gurdwara",)),
    ("stupa", ("stupa", "chorten", "chedi")),
    ("pagoda", ("pagoda",)),
    ("shrine", ("shrine", "iwa", "dargah", "calvary", "pilgrimage",
                "sanctuary", "lourdes", "oracle")),
    ("temple", ("temple", "mandir", "candi", "wat", "gompa", "devalaya",
                "kovil", "hieron", "amida")),
    ("tomb", ("tomb", "mausoleum", "türbe", "martyrium", "necropolis",
              "catacomb", "cemetery")),
    ("monastery", ("abbey", "monastery", "convent", "friary", "priory",
                   "nunnery", "cloister", "lavra", "mahavihara", "vihāra",
                   "kyaung", "datsan", "sufi lodge")),
    ("tower", ("campanile", "minaret")),
]


# Wikidata files ancient cities as "archaeological site", so the first build of
# this pack opened with Athens, Cairo, Damascus and Alexandria at the top of the
# famous-buildings list. They are cities, not buildings, and they are step 33's
# job (B9, old towns), not B8's.
#
# The trap is that Mohenjo-daro, Hampi, Teotihuacan and Great Zimbabwe are also
# settlements -- and they are exactly what B19 names. So the test is not "is it
# a settlement" but "is it a settlement that never ended": a living place is a
# town, a settlement with an end date is a ruin, and a ruin is a building for
# this pack's purposes.
SETTLEMENT_CLASSES = ["Q486972", "Q515", "Q3957", "Q532", "Q1549591", "Q200250"]

# A settlement with this many people on record is a town, not a ruin. Set by
# looking at the two cases that decide it: Athens 643,452 (drop) against
# Cahokia 20,000 (keep -- that figure is a peak estimate for a site nobody
# lives in). Mount Athos monasteries have populations too, which is why the
# drop also requires the thing to be presented as an archaeological site.
LIVE_POPULATION = 50000


def settlement_qids(qids):
    """Which of these are a kind of human settlement. Cached; chunked."""
    import requests
    cache = os.path.join(RAW, "settlement_qids.json")
    out = set(json.load(open(cache))) if os.path.exists(cache) else set()
    todo = [q for q in qids if q not in out]
    if not todo:
        return out
    ua = "EternalEngineDataBuild/1.0 (history data; Eternal Engine Minecraft mod)"
    pre = ("PREFIX wd: <http://www.wikidata.org/entity/>\n"
           "PREFIX wdt: <http://www.wikidata.org/prop/direct/>\n")
    # Q486972 "human settlement" is the parent of city, town, village, big city
    # and metropolis, so one path catches all six. DISTINCT: the path hits the
    # same item several times.
    body = (pre + "SELECT DISTINCT ?x WHERE {\n  VALUES ?x { %s }\n"
            "  ?x wdt:P31/wdt:P279* wd:Q486972\n}")
    # 150 at a time. A GET carries the query in the URL, and at 600 QIDs the
    # request comes back empty and instant -- the URL is too long. That failure
    # is silent unless it is counted, so it is counted below.
    STEP = 150
    failed = 0
    for i in range(0, len(todo), STEP):
        chunk = todo[i:i + STEP]
        q = body % " ".join("wd:" + c for c in chunk)
        got = None
        for _ in range(3):
            try:
                r = requests.get("https://query.wikidata.org/sparql",
                                 params={"query": q},
                                 headers={"Accept": "application/sparql-results+json",
                                          "User-Agent": ua}, timeout=180)
                if r.status_code == 200:
                    got = json.loads(r.text, strict=False)["results"]["bindings"]
                    break
            except Exception:  # noqa: BLE001
                pass
            time.sleep(3)
        if got is None:
            failed += 1
        else:
            for b in got:
                out.add(b["x"]["value"].rsplit("/", 1)[-1])
        if (i // STEP) % 20 == 0 or i + STEP >= len(todo):
            print(f"    settlements {i + len(chunk):,}/{len(todo):,} "
                  f"({len(out):,} are, {failed} chunk(s) failed)", flush=True)
    if failed:
        print(f"  WARNING: {failed} chunk(s) failed; the settlement filter is "
              f"incomplete. Re-run to fill the gaps.")
    json.dump(sorted(out), open(cache, "w"))
    return out


def population_of(qids):
    """Largest population Wikidata records for each, as {qid: people}.

    Presence alone is not enough: Mount Athos monasteries have populations (the
    brothers living in them) and must not be dropped, while Cahokia carries a
    20,000 that is a peak estimate for a place nobody lives in. So the number
    matters, not just whether there is one.
    """
    import requests
    cache = os.path.join(RAW, "population_qids.json")
    out = json.load(open(cache)) if os.path.exists(cache) else {}
    todo = [q for q in qids if q not in out]
    if todo:
        ua = "EternalEngineDataBuild/1.0 (history data; Eternal Engine Minecraft mod)"
        pre = ("PREFIX wd: <http://www.wikidata.org/entity/>\n"
               "PREFIX wdt: <http://www.wikidata.org/prop/direct/>\n")
        body = (pre + "SELECT ?x ?pop WHERE {\n  VALUES ?x { %s }\n"
                "  ?x wdt:P1082 ?pop\n}")
        STEP = 150
        failed = 0
        for i in range(0, len(todo), STEP):
            chunk = todo[i:i + STEP]
            q = body % " ".join("wd:" + c for c in chunk)
            got = None
            for _ in range(3):
                try:
                    r = requests.get("https://query.wikidata.org/sparql",
                                     params={"query": q},
                                     headers={"Accept": "application/sparql-results+json",
                                              "User-Agent": ua}, timeout=180)
                    if r.status_code == 200:
                        got = json.loads(r.text, strict=False)["results"]["bindings"]
                        break
                except Exception:  # noqa: BLE001
                    pass
                time.sleep(3)
            if got is None:
                failed += 1
            else:
                for b in got:
                    qid = b["x"]["value"].rsplit("/", 1)[-1]
                    try:
                        v = float(b["pop"]["value"])
                    except ValueError:
                        continue
                    if v > out.get(qid, 0):
                        out[qid] = v
        if failed:
            print(f"  WARNING: {failed} chunk(s) failed; re-run to fill the gaps.")
        json.dump(out, open(cache, "w"))
    print(f"  {sum(1 for v in out.values() if v >= LIVE_POPULATION):,} of "
          f"{len(qids):,} settlements have {LIVE_POPULATION:,} people or more "
          f"on record", flush=True)
    return out


def canon_holy(kind):
    """Step 30b's kind -> a kind the mod can place, or None to fall back."""
    s = (kind or "").lower()
    for out, keys in HOLY_RULES:
        if any(x in s for x in keys):
            return out
    return None


def km(lat1, lon1, lat2, lon2):
    p1, p2 = radians(lat1), radians(lat2)
    dp, dl = radians(lat2 - lat1), radians(lon2 - lon1)
    h = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return 2 * 6371 * asin(min(1, sqrt(h)))


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


class Grid:
    def __init__(self, cell=0.25):
        self.cell = cell
        self.b = {}

    def add(self, lat, lon, item):
        self.b.setdefault((int(lat // self.cell), int(lon // self.cell)),
                          []).append(item)

    def near(self, lat, lon):
        i, j = int(lat // self.cell), int(lon // self.cell)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                yield from self.b.get((i + di, j + dj), ())


def main():
    labels = json.load(open(os.path.join(RAW, "labels.json"), encoding="utf-8"))
    props_path = os.path.join(RAW, "props.json")
    props = json.load(open(props_path, encoding="utf-8")) if os.path.exists(props_path) else {}
    if props:
        print(f"  {sum(1 for v in props.values() if v.get('style')):,} of "
              f"{len(props):,} items carry a style, "
              f"{sum(1 for v in props.values() if v.get('material')):,} a material "
              f"(step 33, Wikidata P149 and P186)")

    # ---- part 1: what Wikidata dates --------------------------------------
    class_size = Counter()          # rows per class, dated and undated alike
    wd = {}
    for f in sorted(os.listdir(RAW)):
        if f.startswith("class_") and f.endswith(".json"):
            for r in json.load(open(os.path.join(RAW, f), encoding="utf-8")):
                q = r["qid"]
                class_size[r["class"]] += 1
                if q in wd:
                    if r["class"] not in wd[q]["classes"]:
                        wd[q]["classes"].append(r["class"])
                else:
                    wd[q] = {"qid": q, "lat": r["lat"], "lon": r["lon"],
                             "start": r["start"], "end": r["end"],
                             "sitelinks": r["sitelinks"],
                             "dated_by": r["dated_by"],
                             "classes": [r["class"]]}
        elif f.startswith("undated_") and f.endswith(".json"):
            for r in json.load(open(os.path.join(RAW, f), encoding="utf-8")):
                class_size[r["class"]] += 1
    print(f"  {len(wd):,} structures dated by Wikidata")

    # ---- part 2: what the gazetteer dates ---------------------------------
    gz_path = os.path.join(RAW, "gazetteer_dated.json")
    gz = json.load(open(gz_path, encoding="utf-8")) if os.path.exists(gz_path) else []
    print(f"  {len(gz):,} structures dated from the gazetteer (estimated)")
    clash = [r["qid"] for r in gz if r["qid"] in wd]
    if clash:
        print(f"  {len(clash)} dated twice; Wikidata wins")

    # ---- holy places, for the kind ----------------------------------------
    holy_grid = Grid()
    holy_n = 0
    hp = os.path.join(HISTORY, "holy_places.json.gz")
    if os.path.exists(hp):
        with gzip.open(hp, "rt", encoding="utf-8") as fh:
            for r in json.load(fh)["places"]:
                # [name, lat*1000, lon*1000, kind, faith, from, to, articles]
                holy_grid.add(r[1] / 1000.0, r[2] / 1000.0,
                              (norm(r[0]), r[3], r[1] / 1000.0, r[2] / 1000.0))
                holy_n += 1
    print(f"  {holy_n:,} holy places on hand (step 30b) for the finer kind")

    # ---- curated gazetteer sites, to tie a building back to its site ------
    site_grid = Grid()
    site_n = 0
    for f in HISTORY_PACKS:
        p = os.path.join(HISTORY, f)
        if not os.path.exists(p):
            continue
        with open(p, encoding="utf-8") as fh:
            d = json.load(fh)
        for s in d.get("sites", []):
            if s.get("lat") is None:
                continue
            site_grid.add(s["lat"], s["lon"],
                          (s.get("id"), s["lat"], s["lon"], d.get("id")))
            site_n += 1
    print(f"  {site_n} curated gazetteer sites")

    def kind_of(classes):
        """The narrowest class it belongs to: fewest members worldwide.

        Ruin classes are skipped here on purpose -- they are a state, not a
        kind, and "castle ruin" is narrower than "castle", so leaving them in
        would rename every ruined castle. They are used only if there is
        nothing else to go on.
        """
        cands = [c for c in classes if c in KIND and c not in RUIN_CLASSES]
        if not cands:
            cands = [c for c in classes if c in KIND]
        if not cands:
            return "structure"
        return KIND[min(cands, key=lambda c: (class_size.get(c, 1 << 30), c))]

    rows = []
    stats = Counter()

    for r in wd.values():
        kind = kind_of(r["classes"])
        name = labels.get(r["qid"])
        if not name:
            stats["no_label"] += 1
            continue
        lat, lon = r["lat"], r["lon"]
        holy = None
        for hn, hk, hlat, hlon in holy_grid.near(lat, lon):
            if hn == norm(name) and km(lat, lon, hlat, hlon) <= 2.0:
                holy = canon_holy(hk)
                break
        site = None
        for sid, slat, slon, _pack in site_grid.near(lat, lon):
            if km(lat, lon, slat, slon) <= 10.0:
                site = sid
                break
        if holy:
            stats["holy_kind_used"] += 1
        if site:
            stats["on_curated_site"] += 1
        rows.append([r["qid"], name, round(lat * 1000), round(lon * 1000),
                     holy or kind, r["start"], r["end"], r["sitelinks"],
                     "inception" if r["dated_by"] == "inception" else "opening",
                     1 if holy else 0, site,
                     1 if (RUIN_CLASSES & set(r["classes"])) else 0])

    for r in gz:
        if r["qid"] in wd:
            continue                      # a recorded date always wins
        name = r.get("label")
        if not name:
            stats["no_label"] += 1
            continue
        lat, lon = r["lat"], r["lon"]
        holy = None
        for hn, hk, hlat, hlon in holy_grid.near(lat, lon):
            if hn == norm(name) and km(lat, lon, hlat, hlon) <= 2.0:
                holy = canon_holy(hk)
                break
        rows.append([r["qid"], name, round(lat * 1000), round(lon * 1000),
                     holy or kind_of(r["classes"]), r["start"], r["end"],
                     r["sitelinks"], "gazetteer", 1 if holy else 0, r["site"],
                     1 if (RUIN_CLASSES & set(r["classes"])) else 0])

    # ---- repair ends that are not after their start ------------------------
    # 33 of them: Hagia Sophia is 532..404 in Wikidata (the 404 belongs to a
    # predecessor church on the same site), the Cathedral of Christ the Saviour
    # 2000..1931 (the demolition against the rebuild). Such a row can never
    # stand in any year, so the end is dropped and the start kept.
    repaired = 0
    for r in rows:
        if r[6] is not None and r[6] <= r[5]:
            r[6] = None
            repaired += 1
    print(f"\n  {repaired} end dates dropped: they were not after the start "
          f"year, so the building could never have stood")

    # ---- drop living settlements -------------------------------------------
    print(f"\n  asking Wikidata which of these are settlements "
          f"({len(rows):,} to check)")
    settle = settlement_qids(sorted({r[0] for r in rows}))
    pop = population_of(sorted(settle))
    kept, dropped, kept_ruins = [], 0, 0
    for r in rows:
        # r = [qid, name, lat, lon, kind, from, to, sitelinks, src, holy, site]
        if r[0] in settle:
            if r[6] is not None:
                kept_ruins += 1          # a settlement with an end date: a ruin
            elif (r[4] == "archaeological site"
                  and pop.get(r[0], 0) >= LIVE_POPULATION):
                dropped += 1             # a city, not a building: step 33's
                continue
        kept.append(r)          # the qid stays to the end: step 33 needs it to
                                # look the material and the style up
    rows = kept
    print(f"  {dropped:,} dropped: a kind of settlement, presented as an "
          f"archaeological site, with {LIVE_POPULATION:,} people or more and no "
          f"end date -- a city, not a building")
    print(f"  {len(settle) - dropped:,} settlements kept as ruins "
          f"({kept_ruins:,} of them because they have an end date)")

    # Best known first, so a reader that takes the top N gets the famous ones.
    rows.sort(key=lambda r: -r[7])          # sitelinks (the qid is still field 0)

    # ---- step 33: the style and the materials, where Wikidata records them --
    # Narrowest wins, the same rule as the kind: of the styles an item carries,
    # the one fewest items carry is the one that says most about it. Materials
    # are all kept, because a building is of several things at once -- the
    # Colosseum is of travertine and concrete, and dropping either would be a
    # choice Wikidata does not make for us.
    style_count = Counter()
    for v in props.values():
        for s in v.get("style", []):
            style_count[s] += 1
    style_ids, mat_ids = {}, {}

    def style_of(qid):
        cands = props.get(qid, {}).get("style", [])
        if not cands:
            return -1
        best = min(cands, key=lambda s: (style_count.get(s, 0), s))
        s = style_name(labels.get(best))
        if not s:
            return -1
        return style_ids.setdefault(s, len(style_ids))

    def materials_of(qid):
        out = []
        for m in props.get(qid, {}).get("material", []):
            n = material_name(labels.get(m))
            if not n or n in out:
                continue
            out.append(mat_ids.setdefault(n, len(mat_ids)))
        return out

    rows = [r[1:] + [style_of(r[0]), materials_of(r[0])] for r in rows]
    styles = [k for k, _ in sorted(style_ids.items(), key=lambda kv: kv[1])]
    materials = [k for k, _ in sorted(mat_ids.items(), key=lambda kv: kv[1])]
    print(f"  styles: {len(styles)}; materials: {len(materials)}; "
          f"{sum(1 for r in rows if r[11] >= 0):,} rows carry a style, "
          f"{sum(1 for r in rows if r[12]):,} carry a material")

    pack = {
        "format": 1,
        "id": "buildings_famous",
        "source": ("Wikidata (CC0), fetched 2026-10-15: structures of 18 kinds "
                   "(temples, churches, mosques, castles, forts, palaces, "
                   "bridges, towers, tombs, monasteries, stupas, citadels, "
                   "city gates, theatres, monuments, archaeological sites) with "
                   "a map point, 5 or more Wikipedias, and a build year "
                   "(inception, else date of official opening). Where Wikidata "
                   "has no date at all, the year is the mod's own gazetteer's "
                   "occupation window for the site the structure stands on, and "
                   "is marked estimated."),
        "note": ("One row: [name, lat*1000, lon*1000, kind, from, to, "
                 "sitelinks, source, holy, site, ruin, style, materials]. source is "
                 "inception, opening "
                 "or gazetteer (estimated). holy is 1 where step 30b's holy "
                 "places know this building under a finer kind. site is the "
                 "curated gazetteer site it stands on, where there is one. "
                 "ruin is 1 where Wikidata calls the thing a ruin even though "
                 "it never recorded the year it fell -- without it, a ruin "
                 "with no end date would show as still standing. "
                 "style is an index into styles, -1 where Wikidata records no "
                 "architectural style (P149); materials is a list of indices into "
                 "materials, empty where it records none (P186). 30% carry a style "
                 "and 8.5% a material, so most of what a town is made of comes from "
                 "the building-culture table of step 33, not from here. "
                 "to is null where the end is unknown. Kinds are taken from the "
                 "narrowest Wikidata class, because the broad ones misdescribe: "
                 "Westminster Abbey is filed as a temple."),
        "styles": styles,
        "materials": materials,
        "count": len(rows),
        "buildings": rows,
    }
    with open(OUT, "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as fh:
        json.dump(pack, fh, ensure_ascii=False, separators=(",", ":"))

    size = os.path.getsize(OUT)
    print(f"\n  {len(rows):,} buildings -> {OUT.split('/')[-1]} "
          f"({size / 1e6:.2f} MB)")
    print(f"  {stats['holy_kind_used']:,} take their kind from the holy places")
    print(f"  {stats['on_curated_site']:,} stand on a curated gazetteer site")
    if stats["no_label"]:
        print(f"  {stats['no_label']} dropped: no English label")

    # ---- report ------------------------------------------------------------
    kinds = Counter(r[3] for r in rows)
    srcs = Counter(r[7] for r in rows)
    print("\n  kind")
    for k, v in kinds.most_common():
        print(f"    {k:22s} {v:>7,}")
    print("  where the year came from")
    for k, v in srcs.most_common():
        print(f"    {k:22s} {v:>7,}")
    print(f"\n  with an end date (B19 ruins)   "
          f"{sum(1 for r in rows if r[5] is not None):,}")
    print(f"  standing before 1900           "
          f"{sum(1 for r in rows if r[4] < 1900):,}")
    print(f"  standing before AD 1           "
          f"{sum(1 for r in rows if r[4] < 1):,}")
    print(f"  holy (also in holy_places)     "
          f"{sum(1 for r in rows if r[8]):,}")
    print(f"  known ruins (B19)              "
          f"{sum(1 for r in rows if r[10]):,}")
    print(f"  walls, gates and forts (B16)   "
          f"{sum(1 for r in rows if r[3] in FORTIFICATION_KINDS):,}")
    print(f"  amphitheatres                  "
          f"{sum(1 for r in rows if r[3] == 'amphitheatre'):,}")
    print(f"  with a style (B9, step 33)     "
          f"{sum(1 for r in rows if r[11] >= 0):,}")
    print(f"  with a material (E14)          "
          f"{sum(1 for r in rows if r[12]):,}")
    top = Counter(styles[r[11]] for r in rows if r[11] >= 0)
    print("  the styles, most common first")
    for k, v in top.most_common(10):
        print(f"    {k:26s} {v:>6,}")
    mt = Counter(m for r in rows for m in r[12])
    print("  the materials, most common first")
    for k, v in mt.most_common(10):
        print(f"    {materials[k]:26s} {v:>6,}")

    rep = {"count": len(rows), "bytes": size,
           "by_kind": dict(kinds), "by_source": dict(srcs),
           "with_end": sum(1 for r in rows if r[5] is not None),
           "before_1900": sum(1 for r in rows if r[4] < 1900),
           "before_1": sum(1 for r in rows if r[4] < 1),
           "holy": sum(1 for r in rows if r[8]),
           "ruin": sum(1 for r in rows if r[10]),
           "fortification": sum(1 for r in rows if r[3] in FORTIFICATION_KINDS),
           "on_site": stats["on_curated_site"]}
    with open(os.path.join(LOGS, "step32_pack_report.json"), "w",
              encoding="utf-8") as f:
        json.dump(rep, f, indent=1)
    print("\n  written: logs/step32_pack_report.json")

    # ---- does the pack still answer the test places? ----------------------
    ok = 0
    for name, lat, lon, yr in TEST_PLACES:
        n = sum(1 for r in rows
                if km(lat, lon, r[1] / 1000.0, r[2] / 1000.0) <= 25
                and r[4] <= yr and (r[5] is None or yr < r[5]))
        if n:
            ok += 1
    print(f"  test places answered by the pack: {ok} of {len(TEST_PLACES)}")


if __name__ == "__main__":
    main()
