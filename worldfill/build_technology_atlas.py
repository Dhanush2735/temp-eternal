#!/usr/bin/env python3
"""Step 30a (system C16): the technology atlas - which technology is in use where, in every year.

    python3 build_country_grid.py             the country of any point (history/countries.grid.gz), first
    python3 build_technology_atlas.py         download CHAT (into build/tech/, not kept) and write
                                              history/technology_atlas.json.gz into the mod
    python3 build_technology_atlas.py --check read it back and check it (exit 1 on a problem)

Sources, in this order (turn 12: Wikipedia first):
  1. technology_table.py: 129 technologies by hand from English Wikipedia's articles - where and when each began, and
     the years it reached the lands of today's countries where the record is clear ("recorded");
  2. CHAT (Comin and Hobijn 2009, NBER; 104 technologies in 161 countries, 1800-2008; public domain, ODC-PDDL on
     datahub): for the modern technologies, the first year a country's figure is above zero after zeros ("recorded",
     marked C), or only "by then" when its figures start above zero (an upper bound, B); and, for things households
     have (radio, cars, telephones ...), how common they were each year: the figure per person against a full level;
  3. everywhere else an estimate (E): the earliest arrival from any land that has it, travelling at the speed of its
     era (3 km a year before 1000 BCE, 5 to 500 CE, 8 to 1450, 25 to 1750, 60 to 1850, 150 to 1914, 300 to 1950, 500
     after; half that for what a town must build, such as railways), across the oceans after contact with the colonists
     or by sea trade (four times faster), and never earlier than what it needs, nor before the outside world reached a land (the Americas from 1492
     on, Australia 1788 ...; technologies from Europe or the Americas wait for Japan to open in 1853 and Korea in 1876;
     technologies from Europe begun between 1450 and 1800 not in Africa south of the Sahara before 1800), nor before
     a table's "not before" year (no carts or ploughs in tropical Africa before colonial times, no horses where tsetse
     flies live). "Only" technologies (porcelain, high-speed trains, atomic power stations) are never estimated.

File layout (history/technology_atlas.json.gz, JSON):
  countries: [code, ...]   (the order of history/countries.grid.gz)
  speeds: [[fromYear, kmPerYear], ...]
  techs: [{id, name, field, kind, d50, fame, maxShare, needs, replaces, source, game, first,
           arrive: [year or null per country], mark: "RCBEN..." (recorded, CHAT, CHAT by-then, estimated, never),
           places: {country index: [[lat, lon, year], ...]} (where it began inside a country; the spread starts from
           the nearest), lost: [[country, from, to], ...], native: [country, ...],
           share: {country index: [firstYear, step, permille, ...]}}, ...]
"""
import collections
import gzip
import heapq
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modpack as M                 # noqa: E402
import technology_table as TT       # noqa: E402
import build_country_grid as CG     # noqa: E402

BASE = os.path.join(HERE, "build", "tech")
CHAT_CSV = os.path.join(BASE, "FinalCHAT_72909.csv")
CHAT_URL = "https://data.nber.org/data-appendix/w15319/FinalCHAT_72909.csv"
OUT = os.path.join(M.HISTORY, "technology_atlas.json.gz")
REPORT = os.path.join(HERE, "logs", "step30a_technology_report.json")
NOW = 2026
NE_FILE = CG.NE

CROSSING = 1492   # the first year anything crossed between the Old World and the Americas (Oceania: by country)
SEA_SPEED = 1000.0  # km a year for what the ships carried across the oceans after contact
SPEEDS = [(-100000, 3.0), (-1000, 5.0), (500, 8.0), (1450, 25.0), (1750, 60.0), (1850, 150.0), (1914, 300.0),
          (1950, 500.0)]

CHAT_NAMES = {
    "Bosnia-Herzegovina": ["BIH"], "Burma": ["MMR"], "Czechoslovakia": ["CZE", "SVK"],
    "Democratic Republic of the Congo": ["COD"], "Republic of the Congo": ["COG"], "Indochina": ["VNM", "LAO", "KHM"],
    "Ivory Coast": ["CIV"], "Macedonia": ["MKD"], "North Vietnam": ["VNM"], "South Vietnam": ["VNM"],
    "South Yemen": ["YEM"], "Slovak Republic": ["SVK"], "Swaziland": ["SWZ"], "Venezuala": ["VEN"],
    "Hong Kong": ["HKG"], "Taiwan": ["TWN"], "United States": ["USA"], "United Kingdom": ["GBR"],
    "South Korea": ["KOR"], "Czech Republic": ["CZE"], "Russia": ["RUS"], "Iran": ["IRN"], "Syria": ["SYR"],
    "Laos": ["LAO"], "Vietnam": ["VNM"], "Tanzania": ["TZA"], "Bolivia": ["BOL"], "Moldova": ["MDA"],
    "Dominican Republic": ["DOM"], "Central African Republic": ["CAF"], "Equatorial Guinea": ["GNQ"],
    "Guinea-Bissau": ["GNB"], "Papua New Guinea": ["PNG"], "United Arab Emirates": ["ARE"], "French Guiana": [],
}
# Units of the CHAT series used for "how common": per person = value * factor / (population in thousands * 1000).
CHAT_UNITS = {"radio": 1000.0, "tv": 1.0, "telephone": 1.0, "cellphone": 1.0, "internetuser": 1.0, "computer": 1.0,
              "vehicle_car": 1.0, "newspaper": 1.0, "atm": 1.0, "creditdebit": 1.0e6}   # card payments: millions
CHAT_SAT_DEFAULT = {"atm": 0.001}


def resolve_groups(countries, subregion_of):
    codes = [c[0] for c in countries]
    by_sub = collections.defaultdict(list)
    for code in codes:
        by_sub[subregion_of[code]].append(code)
    cache = {}

    def expand(name, seen=()):
        if name in cache:
            return cache[name]
        if name.startswith("@"):
            out = list(by_sub.get(name[1:], []))
            if not out:
                raise SystemExit(f"unknown subregion {name}")
        elif name in TT.GROUPS:
            out = []
            for part in TT.GROUPS[name]:
                if part in seen:
                    continue
                out += expand(part, seen + (name,))
        elif name in codes:
            out = [name]
        else:
            raise SystemExit(f"unknown place {name}")
        cache[name] = sorted(set(out))
        return cache[name]
    return expand


def travel(t0, km, factor=1.0):
    """The year something that left at t0 arrives km away, at the speeds of the eras it passes through (times
    `factor`: slower for what a town must build, faster across the sea after contact)."""
    if km <= 0:
        return t0
    t = float(t0)
    left = km
    for i, (start, v) in enumerate(SPEEDS):
        v *= factor
        end = SPEEDS[i + 1][0] if i + 1 < len(SPEEDS) else 1e9
        if t >= end:
            continue
        t = max(t, start)
        can = (end - t) * v
        if can >= left:
            return t + left / v
        left -= can
        t = end
    return t


# How fast a kind of technology spreads between lands (times the era's speed): what a town must build (railways,
# power stations) is slower; knowledge (printing) a little slower.
KIND_FACTOR = {"infra": 0.5, "knowledge": 0.75, "home": 0.6}
SEA_FACTOR = 4.0   # trade by sea between the Old World, the Americas and Oceania after contact


def km(a, b):
    la1, lo1 = math.radians(a[0]), math.radians(a[1])
    la2, lo2 = math.radians(b[0]), math.radians(b[1])
    d = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371.0 * 2 * math.asin(min(1.0, math.sqrt(d)))


def load_chat():
    import pandas as pd
    if not os.path.exists(CHAT_CSV):
        import requests
        os.makedirs(BASE, exist_ok=True)
        r = requests.get(CHAT_URL, timeout=600)
        r.raise_for_status()
        open(CHAT_CSV, "wb").write(r.content)
    c = pd.read_csv(CHAT_CSV, low_memory=False)
    return c


def chat_series(c, codes, ne_names):
    """{column: {code: [(year, value, population)]}} for every CHAT column a technology names."""
    import pandas as pd
    cols = sorted({t["chat"] for t in TT.TECHS if t["chat"]})
    for col in cols + ["xlpopulation"]:
        c[col] = pd.to_numeric(c[col], errors="coerce")
    name_to_codes = {}
    for name in c["country_name"].dropna().unique():
        if name in CHAT_NAMES:
            name_to_codes[name] = CHAT_NAMES[name]
        elif name in ne_names:
            name_to_codes[name] = [ne_names[name]]
        else:
            name_to_codes[name] = []
    out = {col: collections.defaultdict(list) for col in cols}
    own = collections.defaultdict(set)   # codes that have a series under their own name (not a former union)
    for name, codes_ in name_to_codes.items():
        if len(codes_) == 1 and name not in ("Czechoslovakia", "Indochina", "North Vietnam", "South Vietnam",
                                              "South Yemen"):
            own[codes_[0]].add(name)
    for name, g in c.groupby("country_name"):
        targets = name_to_codes.get(name, [])
        for col in cols:
            rows = [(int(y), float(v), float(p) if p == p else None) for y, v, p in
                    zip(g["year"], g[col], g["xlpopulation"]) if v == v]
            for code in targets:
                former = name in ("Czechoslovakia", "Indochina", "North Vietnam", "South Vietnam", "South Yemen")
                if former and own.get(code):
                    # A former union's figures fill only the years before the country's own series.
                    first_own = None
                    for oname in own[code]:
                        og = c[c["country_name"] == oname]
                        ys = [int(y) for y, v in zip(og["year"], og[col]) if v == v]
                        if ys:
                            first_own = min(ys) if first_own is None else min(first_own, min(ys))
                    rows_c = [r for r in rows if first_own is None or r[0] < first_own]
                else:
                    rows_c = rows
                out[col][code] += rows_c
    for col in out:
        for code in out[col]:
            merged = {}
            for y, v, p in out[col][code]:
                if y not in merged or v > merged[y][0]:
                    merged[y] = (v, p)
            out[col][code] = sorted((y, v, p) for y, (v, p) in merged.items())
    return out


def chat_arrival(rows):
    """(year, mark): the first year above zero; 'C' when zeros (or nothing) came before in the series, else 'B'."""
    seen_zero = False
    for y, v, _ in rows:
        if v <= 0:
            seen_zero = True
            continue
        return y, ("C" if seen_zero else "B")
    return None, None


def build():
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    countries, _rows = CG.read()
    codes = [c[0] for c in countries]
    idx = {code: i for i, code in enumerate(codes)}
    feats = json.load(open(NE_FILE, encoding="utf-8"))["features"]
    subregion_of = {f["properties"]["ADM0_A3"]: f["properties"]["SUBREGION"] for f in feats}
    ne_names = {}
    for f in feats:
        p = f["properties"]
        for k in ("NAME", "NAME_LONG", "ADMIN", "NAME_EN", "FORMAL_EN", "NAME_SORT"):
            if p.get(k):
                ne_names.setdefault(p[k], p["ADM0_A3"])
    expand = resolve_groups(countries, subregion_of)
    main_pt = [(c[5], c[6]) for c in countries]
    n = len(codes)
    dist = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = km(main_pt[i], main_pt[j])
            dist[i][j] = dist[j][i] = d
    americas = set(expand("AMERICAS"))
    oceania = set(expand("OCEANIA"))
    europe = set(expand("EUROPE"))
    ssa = set(expand("SSA"))
    zone = [1 if codes[i] in americas else 2 if codes[i] in oceania else 0 for i in range(n)]
    contact = {idx[c]: y for c, y in TT.CONTACT.items() if c in idx}
    for i in range(n):          # small lands of the Americas and Oceania without a year of their own
        if zone[i] and i not in contact:
            contact[i] = TT.ZONE_CONTACT["americas"] if zone[i] == 1 else TT.ZONE_CONTACT["pacific"]
    chat = chat_series(load_chat(), codes, ne_names)
    report = collections.Counter()

    by_id = {t["id"]: t for t in TT.TECHS}
    order, temp, done = [], set(), set()

    def visit(tid):
        if tid in done:
            return
        if tid in temp:
            raise SystemExit(f"needs go round in a circle at {tid}")
        temp.add(tid)
        for nd in by_id[tid]["needs"]:
            visit(nd)
        temp.discard(tid)
        done.add(tid)
        order.append(tid)
    for t in TT.TECHS:
        visit(t["id"])

    result = {}
    for tid in order:
        t = by_id[tid]
        arrive = [None] * n
        mark = ["N"] * n
        places = {}
        rec_level = [9] * n       # 0 = the country itself was named, 1 = through a group
        children = collections.defaultdict(list)
        for child, parent in TT.PARENT.items():
            children[parent].append(child)
        for r in t["origins"] + t["records"]:
            members = expand(r["where"])
            members = members + [c for m in members for c in children.get(m, []) if c in idx]
            level = 0 if r["where"] in idx else 1
            for code in members:
                i = idx[code]
                lv = level if code in expand(r["where"]) else 1     # a child of a named land counts as a group
                if lv < rec_level[i] or (lv == rec_level[i] and (arrive[i] is None or r["year"] < arrive[i])):
                    arrive[i] = r["year"]
                    mark[i] = "R"
                    rec_level[i] = lv
                if r["at"] and lv == 0:
                    # every named place of a country: the spread inside it starts from the nearest of them
                    places.setdefault(i, []).append([round(r["at"][0], 3), round(r["at"][1], 3), r["year"]])
        # A record that came through a group never falls before a land was settled (Iceland in Scandinavia, 874).
        for code, y in TT.SETTLED.items():
            if code in idx:
                i = idx[code]
                if arrive[i] is not None and rec_level[i] == 1 and arrive[i] < y:
                    arrive[i] = y
        first = min(a for a in arrive if a is not None)
        origin_codes = {codes[i] for i in range(n) if arrive[i] is not None and arrive[i] == first}
        # CHAT, for lands without a record of their own
        upper = [None] * n
        if t["chat"]:
            for code, rows in chat[t["chat"]].items():
                if code not in idx:
                    continue
                i = idx[code]
                y, m = chat_arrival(rows)
                if y is None or (arrive[i] is not None and rec_level[i] == 0):
                    continue
                if y < first:
                    continue   # a figure before the technology existed: a series that counts something older
                if m == "C":
                    arrive[i] = y if arrive[i] is None else min(arrive[i], y)
                    mark[i] = "C" if arrive[i] == y else mark[i]
                    report["CHAT arrivals"] += 1
                else:
                    upper[i] = y
        # floors for estimates
        floors = [None] * n
        native = []
        old_world_origin = not any(code in americas or code in oceania for code in origin_codes)
        for i in range(n):
            f = None
            if i in contact and arrive[i] is None:
                f = contact[i]
            if i in contact and arrive[i] is not None and arrive[i] < contact[i]:
                native.append(i)
            floors[i] = f
        for code, y in TT.SETTLED.items():
            if code in idx and arrive[idx[code]] is None:
                i = idx[code]
                floors[i] = max(floors[i] or -10 ** 6, y)
        nb_level = [9] * n
        for r in t["not_before"]:
            members = expand(r["where"])
            members = members + [c for m in members for c in children.get(m, []) if c in idx]
            level = 0 if r["where"] in idx else 1
            for code in members:
                i = idx[code]
                if level <= nb_level[i]:
                    floors[i] = max(floors[i] or -10 ** 6, r["year"]) if level == nb_level[i] else r["year"]
                    nb_level[i] = level
        euro_origin = all(code in europe for code in origin_codes) and 1440 <= first <= 1800
        western_origin = all(code in europe or code in americas for code in origin_codes) and first >= 1500
        for i in range(n):
            if euro_origin and codes[i] in ssa:
                floors[i] = max(floors[i] or -10 ** 6, TT.EARLY_MODERN_EUROPE_FLOOR[1])
        isolation = {idx[c]: (a, b) for c, a, b, _ in TT.ISOLATION if c in idx}
        for nd in t["needs"]:
            na = result[nd]["arrive"]
            for i in range(n):
                if na[i] is None:
                    floors[i] = 10 ** 6       # never: what it needs never came
                else:
                    floors[i] = max(floors[i] or -10 ** 6, na[i])

        def constrained(i, year):
            f = floors[i]
            if f is not None and year < f:
                year = f
            if western_origin and i in isolation:
                a, b = isolation[i]
                if a <= year < b:
                    year = b
            if upper[i] is not None and year > upper[i]:
                year = upper[i]
            return year

        kf = KIND_FACTOR.get(t["kind"], 1.0)
        if not t["only"]:
            best = [math.inf] * n
            heap = []
            for i in range(n):
                if arrive[i] is not None:
                    best[i] = arrive[i]
                    heapq.heappush(heap, (arrive[i], i))
            settled = [False] * n
            while heap:
                tm, u = heapq.heappop(heap)
                if settled[u] or tm > best[u]:
                    continue
                settled[u] = True
                if tm >= NOW:
                    continue
                row = dist[u]
                for v in range(n):
                    if settled[v] or arrive[v] is not None:
                        continue
                    if zone[u] != zone[v]:
                        # Nothing crossed between the Old World, the Americas and Oceania before 1492. What the
                        # colonists had at home came with them (the land's contact year decides); what came later
                        # travelled by sea trade.
                        cy = contact.get(v, CROSSING)
                        # (the conquests of the Americas and the convict colony of Australia; a first sighting of a
                        # Pacific island is not a colony)
                        colonists = zone[v] == 1 or codes[v] == "AUS"
                        if tm <= cy and t["kind"] != "infra" and colonists:
                            cand = constrained(v, max(cy, CROSSING + row[v] / SEA_SPEED))
                        else:
                            sea = SEA_FACTOR if tm < 1850 else 1.0
                            cand = constrained(v, travel(max(tm, CROSSING), row[v], sea * kf))
                    else:
                        cand = constrained(v, travel(tm, row[v], kf))
                    if cand < best[v]:
                        best[v] = cand
                        heapq.heappush(heap, (cand, v))
            for i in range(n):
                if arrive[i] is None and best[i] < math.inf and best[i] <= NOW:
                    arrive[i] = int(math.floor(best[i]))
                    mark[i] = "E"
                    report["estimated arrivals"] += 1
                elif arrive[i] is None and upper[i] is not None:
                    arrive[i] = upper[i]
                    mark[i] = "B"
        # a recorded arrival before what it needs is kept (it is a record); counted for the report
        for nd in t["needs"]:
            na = result[nd]["arrive"]
            for i in range(n):
                if arrive[i] is not None and mark[i] in "RC" and (na[i] is None or arrive[i] < na[i]):
                    report[f"records before what they need ({tid} before {nd})"] += 1
        for i in range(n):
            if arrive[i] is not None and arrive[i] > NOW:
                arrive[i] = None
                mark[i] = "N"
        lost = []
        for r in t["lost"]:          # R(where, from, to): the third field carries the end year
            for code in expand(r["where"]):
                lost.append([idx[code], r["year"], int(r["note"])])
        share = {}
        if t["chat"] and t["chat_sat"]:
            col = t["chat"]
            unit = CHAT_UNITS.get(col, 1.0)
            for code, rows in chat[col].items():
                if code not in idx:
                    continue
                i = idx[code]
                pts = []
                for y, v, p in rows:
                    if col.startswith("pct"):
                        s = v if v <= 1.5 else v / 100.0     # a share already (0.9), sometimes in percent
                    else:
                        if not p or p <= 0:
                            continue
                        s = v * unit / (p * 1000.0) / t["chat_sat"]
                    pts.append((y, max(0.0, min(t["max_share"], s))))
                if not pts:
                    continue
                y0 = pts[0][0] - pts[0][0] % 5
                y1 = pts[-1][0]
                vals = []
                for y in range(y0, y1 + 1, 5):
                    vals.append(int(round(1000 * interp(pts, y))))
                share[i] = [y0, 5] + vals
                report["share series"] += 1
        for i in list(places):
            pl = sorted(places[i], key=lambda p: p[2])
            if arrive[i] is None or pl[0][2] > arrive[i]:
                # the country's year comes from elsewhere (a group record, CHAT): its biggest town starts then too
                pl.insert(0, [round(main_pt[i][0], 3), round(main_pt[i][1], 3), arrive[i]])
            places[i] = [p for p in pl if p[2] is not None]
        result[tid] = {"arrive": arrive, "mark": mark, "places": places, "lost": lost, "share": share,
                       "native": sorted(native), "first": first}
        report["technologies"] += 1

    # A land with a record of a technology had what it needs by then: an estimate of the need that came later is
    # pulled back to that year (a tram line of 1883 had its own power station).
    pulled = 0
    fixed = {(tid, i) for tid in result for i in range(n) if result[tid]["mark"][i] in "RC"}
    for tid in reversed(order):
        t = by_id[tid]
        r = result[tid]
        for nd in t["needs"]:
            q = result[nd]
            for i in range(n):
                a = r["arrive"][i]
                if a is not None and (tid, i) in fixed and q["mark"][i] == "E" and q["arrive"][i] is not None \
                        and q["arrive"][i] > a and a >= TT.SETTLED.get(codes[i], -10 ** 6):
                    q["arrive"][i] = a
                    fixed.add((nd, i))      # what it needs in turn is pulled back too
                    pulled += 1
    report["estimates pulled back to a record that needs them"] = pulled

    techs_out = []
    for t in TT.TECHS:
        r = result[t["id"]]
        techs_out.append({
            "id": t["id"], "name": t["name"], "field": t["field"], "kind": t["kind"], "d50": t["d50"],
            "fame": t["fame"], "maxShare": t["max_share"], "needs": t["needs"], "replaces": t["replaces"],
            "source": t["source"], "game": t["game"], "first": r["first"], "arrive": r["arrive"],
            "mark": "".join(r["mark"]), "places": {str(k): v for k, v in sorted(r["places"].items())},
            "lost": r["lost"], "native": r["native"],
            "share": {str(k): v for k, v in sorted(r["share"].items())}})
        for m in "RCBEN":
            report[f"marks {m}"] += r["mark"].count(m)
    data = {
        "format": 1, "id": "technology_atlas",
        "source": ("English Wikipedia's articles on each technology, by hand (worldfill/technology_table.py, CC BY-SA "
                   "4.0 facts in the mod's own words); CHAT, the Cross-country Historical Adoption of Technology data "
                   "(Comin and Hobijn 2009, NBER working paper 15319; public domain, ODC-PDDL); estimates by the "
                   "rules of build_technology_atlas.py where neither says."),
        "rule": ("arrival in a country: the record, else CHAT's first year above zero, else the earliest arrival from "
                 "any land with it at the speed of its era, never before what it needs or before the outside world "
                 "reached the land; inside a country it spreads from the place it began (or the biggest town) at the "
                 "same speeds; how common: a curve from arrival (half the towns after d50 years; cities sooner, "
                 "villages later), or CHAT's figures per person for things households have."),
        "countries": codes,
        "speeds": [[a, v] for a, v in SPEEDS],
        "zones": TT.ZONE_CONTACT,
        "techs": techs_out,
    }
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with open(OUT + ".tmp", "wb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", compresslevel=9, mtime=0) as g:
            g.write(raw)
    json.loads(gzip.open(OUT + ".tmp").read())
    os.replace(OUT + ".tmp", OUT)
    report["json bytes"] = len(raw)
    report["gzip bytes"] = os.path.getsize(OUT)
    with open(REPORT, "w") as f:
        json.dump(dict(sorted(report.items())), f, indent=1)
    for k, v in sorted(report.items()):
        print(f"  {k}: {v:,}")


def interp(pts, y):
    if y <= pts[0][0]:
        return pts[0][1]
    for (y0, v0), (y1, v1) in zip(pts, pts[1:]):
        if y0 <= y <= y1:
            return v0 + (v1 - v0) * (y - y0) / (y1 - y0) if y1 > y0 else v1
    return pts[-1][1]


def check():
    data = json.load(gzip.open(OUT, "rt", encoding="utf-8"))
    codes = data["countries"]
    idx = {c: i for i, c in enumerate(codes)}
    techs = {t["id"]: t for t in data["techs"]}
    bad = []

    def at(tid, code):
        return techs[tid]["arrive"][idx[code]]

    def has(tid, code, year):
        a = at(tid, code)
        if a is None or a > year:
            return False
        for i, f, to in techs[tid]["lost"]:
            if i == idx[code] and f <= year < to:
                return False
        return True

    expect = [("railway", "IND", 1948, True), ("car", "IND", 1948, True), ("radio", "IND", 1948, True),
              ("television", "IND", 1948, False), ("paper", "IND", 1500, True), ("printing_press", "IND", 1500, False),
              ("iron", "PER", 1500, False), ("wheel", "PER", 1500, False), ("horses", "PER", 1500, False),
              ("printing_press", "GBR", 1700, True), ("steam_engine", "GBR", 1700, False),
              ("woodblock", "CHN", 1100, True), ("gunpowder", "CHN", 1100, True), ("iron", "AUS", 1700, False),
              ("writing", "AUS", 1700, False), ("horses", "MEX", 1400, False), ("railway", "JPN", 1860, False),
              ("railway", "JPN", 1880, True), ("writing", "IND", -1000, False), ("writing", "IND", 0, True),
              ("television", "BTN", 1990, False), ("wheel", "COD", 1700, False), ("plough", "ETH", 1000, True)]
    for tid, code, year, want in expect:
        if has(tid, code, year) != want:
            bad.append(f"{tid} in {code} {year}: {not want}, expected {want} (arrival {at(tid, code)})")
    for t in data["techs"]:
        ys = [a for a in t["arrive"] if a is not None]
        if not ys:
            bad.append(f"{t['id']}: nowhere")
            continue
        if min(ys) < t["first"]:
            bad.append(f"{t['id']}: an arrival before its first year")
        if len(t["arrive"]) != len(codes) or len(t["mark"]) != len(codes):
            bad.append(f"{t['id']}: list lengths")
        for nd in t["needs"]:
            for i, a in enumerate(t["arrive"]):
                b = techs[nd]["arrive"][i]
                if a is not None and t["mark"][i] == "E" and (b is None or a < b):
                    bad.append(f"{t['id']} estimated before {nd} in {codes[i]}")
                    break
    # Old World technologies nowhere in the Americas or Australia before contact (estimates and records alike)
    for tid in ("iron", "wheel", "horses", "printing_press", "gunpowder", "steel", "glass", "plough"):
        for code, year in (("PER", 1532), ("MEX", 1519), ("USA", 1513), ("BRA", 1500), ("AUS", 1788)):
            a = at(tid, code)
            if a is not None and a < year:
                bad.append(f"{tid} in {code} in {a}, before contact ({year})")
    print(f"check: {len(data['techs'])} technologies, {len(codes)} countries; {len(bad)} problems")
    for b in bad[:30]:
        print("  " + b)
    return 1 if bad else 0


def main(argv):
    if len(argv) > 1 and argv[1] == "--check":
        return check()
    build()
    return check()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
