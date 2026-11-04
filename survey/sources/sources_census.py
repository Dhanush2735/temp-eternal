#!/usr/bin/env python3
"""Finish survey §3/§6: open every non-Wikipedia source and measure it for 3000 BC - AD 2026.

For each source: access, licence, format, record type, and how many dated + geocoded records
fall in each census era. Then the density probe (the exact 400 land points of
eternal/DensityProbe.java, via census/density_probe.py) is run per source and for everything
combined, using HistoryGazetteer's rule `start <= year < end` (end <= start -> start + 1).

Raw downloads live in ~/.cache/srcdata or $SRCDATA (not persisted); fetch_sources.py re-creates them.
Writes sources_summary.json and sources_density.json next to this script.
"""
import collections, csv, gzip, io, json, math, os, re, struct, sys, zipfile
import numpy as np

SRC = os.environ.get("SRCDATA", "/home/user/.cache/srcdata")   # main disk, never snapshotted (/tmp is a RAM disk)
HERE = os.path.dirname(os.path.abspath(__file__))
HIST = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/history"
ERAS = [(-3000, -1001, "3000-1001 BC"), (-1000, -1, "1000-1 BC"), (1, 999, "AD 1-999"),
        (1000, 1499, "1000-1499"), (1500, 1799, "1500-1799"), (1800, 2026, "1800-2026")]
csv.field_size_limit(1 << 30)

# the probe's exact 400 points + helpers, from the validated port (no side effects above this cut)
_dp = open("/home/user/survey/census/density_probe.py", encoding="utf-8").read().split("def current_pack")[0]
DP = {}
exec(compile(_dp, "density_probe_head", "exec"), DP)
POINTS, YEARS, RADII = DP["points"], DP["YEARS"], DP["RADII"]
PLAT = np.radians(np.array([p[0] for p in POINTS]))
PLON = np.radians(np.array([p[1] for p in POINTS]))


def era(y):
    for lo, hi, n in ERAS:
        if lo <= y <= hi:
            return n
    return None


def ok_coord(la, lo):
    try:
        la, lo = float(la), float(lo)
    except (TypeError, ValueError):
        return None
    if math.isnan(la) or math.isnan(lo) or not (-90 <= la <= 90 and -180 <= lo <= 180) or (la == 0 and lo == 0):
        return None
    return la, lo


def probe_np(events):
    """Same numbers as density_probe.probe(): % of the 400 points with an event alive within R km."""
    ev = np.array([(la, lo, s, e) for la, lo, s, e in events], dtype=float) if events else np.zeros((0, 4))
    table = {}
    for y in YEARS:
        alive = ev[(ev[:, 2] <= y) & (y < ev[:, 3])] if len(ev) else ev
        row = []
        if len(alive):
            la, lo = np.radians(alive[:, 0]), np.radians(alive[:, 1])
            best = np.full(len(POINTS), np.inf)
            for i in range(0, len(alive), 20000):           # chunk to bound memory
                a, b = la[i:i + 20000], lo[i:i + 20000]
                dlat = a[None, :] - PLAT[:, None]
                dlon = b[None, :] - PLON[:, None]
                h = np.sin(dlat / 2) ** 2 + np.cos(PLAT)[:, None] * np.cos(a)[None, :] * np.sin(dlon / 2) ** 2
                d = 2 * 6371.0 * np.arcsin(np.minimum(1.0, np.sqrt(h)))
                best = np.minimum(best, d.min(axis=1))
        for r in RADII:
            hit = int((best <= r).sum()) if len(alive) else 0
            pct = 100.0 * hit / len(POINTS)
            row.append(math.floor(pct * 10 + 0.5) / 10)
        table[y] = {"alive": int(len(alive)),
                    "pct_within": dict(zip([f"{int(r)}km" for r in RADII], row))}
    return table


def summarize(records, kind):
    """records: list of (lat, lon, start, end) already geocoded; start/end in mod convention."""
    by = collections.Counter()
    out_of_range = 0
    for la, lo, s, e in records:
        if s > 2026 or (e - 1) < -3000:
            out_of_range += 1
            continue
        by[era(max(s, -3000))] += 1
    yrs = [s for _, _, s, _ in records]
    return {"type": kind, "geocoded_dated": len(records), "outside_3000BC_2026": out_of_range,
            "by_era_of_start": {n: by.get(n, 0) for _, _, n in ERAS},
            "year_span": [min(yrs), max(yrs)] if yrs else None,
            "median_duration_years": float(np.median([e - s for _, _, s, e in records])) if records else None}


S, EV = {}, {}

# ---------------------------------------------------------------- NOAA NCEI hazards
for key, fn, label in [("ncei_earthquakes", "ncei_quakes.json", "NOAA NCEI Significant Earthquake Database"),
                       ("ncei_tsunamis", "ncei_tsunamis.json", "NOAA NCEI Global Historical Tsunami Database"),
                       ("ncei_volcanoes", "ncei_volcanoes.json", "NOAA NCEI Significant Volcanic Eruptions")]:
    items = json.load(open(f"{SRC}/{fn}"))
    recs = []
    for it in items:
        c = ok_coord(it.get("latitude"), it.get("longitude"))
        y = it.get("year")
        if c and isinstance(y, int):
            y = y if y != 0 else 1
            recs.append((c[0], c[1], y, y + 1))
    S[key] = dict(label=label, access="open JSON API (hazard-service/api/v1)", licence="US government data (NOAA NCEI)",
                  items_total=len(items), **summarize(recs, "point event (year)"))
    EV[key] = recs

# ---------------------------------------------------------------- Smithsonian GVP Holocene eruptions
g = json.load(open(f"{SRC}/gvp_eruptions.json"))
recs = []
for f in g["features"]:
    p, geo = f["properties"], f.get("geometry") or {}
    co = geo.get("coordinates") or [None, None]
    c = ok_coord(co[1], co[0])
    y = p.get("StartDateYear")
    if c and isinstance(y, int):
        y = y if y != 0 else 1
        e = p.get("EndDateYear")
        e = (e + 1) if isinstance(e, int) and e >= y else y + 1
        recs.append((c[0], c[1], y, e))
S["gvp_eruptions"] = dict(label="Smithsonian GVP Volcanoes of the World: Holocene eruptions",
                          access="open WFS (webservices.volcano.si.edu/geoserver); the website itself 403s bots",
                          licence="not stated in the WFS response; GVP asks for citation",
                          items_total=len(g["features"]), **summarize(recs, "event with start/end year"))
EV["gvp_eruptions"] = recs

# ---------------------------------------------------------------- UCDP GED 25.1
recs, n = [], 0
with zipfile.ZipFile(f"{SRC}/ged251-csv.zip") as z:
    with z.open(z.namelist()[0]) as fh:
        for r in csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8")):
            n += 1
            c = ok_coord(r["latitude"], r["longitude"])
            if c and r["year"].isdigit():
                y = int(r["year"])
                recs.append((c[0], c[1], y, y + 1))
S["ucdp_ged"] = dict(label="UCDP Georeferenced Event Dataset (GED) 25.1", access="open CSV download; the API needs a token (HTTP 401)",
                     licence="CC BY 4.0 (ucdp.uu.se/downloads)", items_total=n, **summarize(recs, "point event (day-dated)"))
EV["ucdp_ged"] = recs

# ---------------------------------------------------------------- Correlates of War wars v4
cow = {}
for fn, sy, ey in [("Inter-StateWarData_v4.0.csv", "StartYear1", "EndYear1"), ("Intra-StateWarData_v4.1.csv", "StartYear1", "EndYear1"),
                   ("Extra-StateWarData_v4.0.csv", "StartYear1", "EndYear1"), ("Non-StateWarData_v4.0.csv", "StartYear", "EndYear")]:
    rows = list(csv.DictReader(open(f"{SRC}/{fn}", encoding="latin-1", newline="")))
    wars = {}
    for r in rows:
        r = {k.strip(): v for k, v in r.items() if k}
        try:
            s, e = int(r[sy]), int(r[ey])
        except (ValueError, KeyError):
            continue
        w = wars.setdefault(r["WarNum"], [s, e])
        w[0] = min(w[0], s) if s > 0 else w[0]
        w[1] = max(w[1], e)
    starts = [s for s, e in wars.values() if s > 0]
    durs = [e - s + 1 for s, e in wars.values() if s > 0 and e >= s]
    cow[fn.split("_")[0]] = {"wars": len(wars), "start_span": [min(starts), max(starts)],
                             "median_duration_years": float(np.median(durs)) if durs else None}
S["cow_wars"] = dict(label="Correlates of War: wars v4 (inter-, intra-, extra-, non-state)", access="open CSV download",
                     licence="free; citation requested (no explicit licence on the page)", type="war with start/end year",
                     geocoded_dated=0, note="No coordinates: only participants and a WhereFought region code. Needs geocoding (e.g. via each war's Wikipedia article) before use.",
                     files=cow, items_total=sum(v["wars"] for v in cow.values()),
                     by_era_of_start={n: (sum(v["wars"] for v in cow.values()) if n == "1800-2026" else 0) for _, _, n in ERAS})

# ---------------------------------------------------------------- Pleiades places
recs, n, undated = [], 0, 0
with gzip.open(f"{SRC}/pleiades-places-latest.csv.gz", "rt", encoding="utf-8", newline="") as fh:
    for r in csv.DictReader(fh):
        n += 1
        c = ok_coord(r.get("reprLat"), r.get("reprLong"))
        if not c:
            continue
        try:
            s, e = int(float(r["minDate"])), int(float(r["maxDate"]))
        except (ValueError, TypeError):
            undated += 1
            continue
        if e < s:
            continue
        recs.append((c[0], c[1], s, e + 1))
S["pleiades"] = dict(label="Pleiades gazetteer of ancient places", access="open daily CSV/JSON dumps (atlantides.org)",
                     licence="CC BY 3.0 (pleiades.stoa.org/credits)", items_total=n, geocoded_undated=undated,
                     **summarize(recs, "place with attested date range"))
EV["pleiades"] = recs


# ---------------------------------------------------------------- CHGIS V6 time-series points
def read_dbf(b, enc="utf-8"):
    nrec, hlen, rlen = struct.unpack("<I", b[4:8])[0], struct.unpack("<H", b[8:10])[0], struct.unpack("<H", b[10:12])[0]
    fields, pos = [], 32
    while b[pos] != 0x0D:
        fields.append((b[pos:pos + 11].split(b"\x00")[0].decode("ascii"), chr(b[pos + 11]), b[pos + 16]))
        pos += 32
    rows = []
    for i in range(nrec):
        rec = b[hlen + i * rlen: hlen + (i + 1) * rlen]
        if rec[:1] == b"*":
            continue
        p, row = 1, {}
        for name, ft, fl in fields:
            s = rec[p:p + fl].decode(enc, errors="replace").strip(); p += fl
            if ft in "NF":
                try:
                    row[name] = float(s)
                except ValueError:
                    row[name] = None
            else:
                row[name] = s
        rows.append(row)
    return rows, [f[0] for f in fields]


def read_shp_points(b):
    pts, pos = [], 100
    while pos + 8 <= len(b):
        clen = struct.unpack(">i", b[pos + 4:pos + 8])[0] * 2
        st = struct.unpack("<i", b[pos + 8:pos + 12])[0]
        pts.append(struct.unpack("<2d", b[pos + 12:pos + 28]) if st == 1 else (None, None))
        pos += 8 + clen
    return pts


chg = {}
for key, fn in [("county", "chgis_Q9VOF5_v6_time_cnty_pts_utf_wgs84.zip"), ("prefecture", "chgis_WW1PD6_v6_time_pref_pts_utf_wgs84.zip")]:
    with zipfile.ZipFile(f"{SRC}/{fn}") as z:
        dbf = next(x for x in z.namelist() if x.endswith(".dbf"))
        shp = next(x for x in z.namelist() if x.endswith(".shp"))
        rows, fields = read_dbf(z.read(dbf))
        pts = read_shp_points(z.read(shp))
    recs = []
    for r, (x, y) in zip(rows, pts):
        c = ok_coord(r.get("Y_COOR") or y, r.get("X_COOR") or x)
        b0, e0 = r.get("BEG_YR"), r.get("END_YR")
        if c and b0 is not None and e0 is not None and e0 >= b0:
            b0 = int(b0) if int(b0) != 0 else 1
            recs.append((c[0], c[1], b0, int(e0) + 1))
    chg[key] = dict(items_total=len(rows), fields=fields[:20], **summarize(recs, "administrative seat with begin/end year"))
    EV[f"chgis_{key}"] = recs
S["chgis_v6"] = dict(label="CHGIS V6 time-series points (China Historical GIS)",
                     access="open on Harvard Dataverse (county points; prefecture points behind a click-through EULA)",
                     licence="county points CC0 1.0; prefecture points CHGIS V6 EULA", layers=chg,
                     type="administrative seat with begin/end year",
                     geocoded_dated=sum(v["geocoded_dated"] for v in chg.values()),
                     by_era_of_start={n: sum(v["by_era_of_start"][n] for v in chg.values()) for _, _, n in ERAS})

# ---------------------------------------------------------------- Reba et al. 2016 historical urban population
reba, recs_all = {}, []
for key, fn in [("chandler", "reba_2059494_chandlerV2.csv"), ("modelski_ancient", "reba_2059497_modelskiAncientV2.csv"),
                ("modelski_modern", "reba_2059500_modelskiModernV2.csv")]:
    rows = list(csv.DictReader(open(f"{SRC}/{fn}", encoding="latin-1", newline="")))
    cols = [k for k in rows[0] if k and re.fullmatch(r"(BC|AD)_\d+", k)]
    yr = {k: (-int(k[3:]) if k.startswith("BC") else int(k[3:])) for k in cols}
    recs, obs = [], collections.Counter()
    for r in rows:
        c = ok_coord(r.get("Latitude"), r.get("Longitude"))
        ys = sorted(yr[k] for k in cols if (r.get(k) or "").strip() not in ("", "0"))
        if not c or not ys:
            continue
        for y in ys:
            obs[era(y)] += 1
        recs.append((c[0], c[1], ys[0], ys[-1] + 1))
    reba[key] = dict(cities=len(rows), year_columns=len(cols), span=[min(yr.values()), max(yr.values())],
                     observations_by_era={n: obs.get(n, 0) for _, _, n in ERAS}, **summarize(recs, "city with population series"))
    recs_all += recs
EV["reba_cities"] = recs_all
S["reba_urban"] = dict(label="Reba, Reitsma & Seto 2016: historical urban population 3700 BC - AD 2000",
                       access="open on figshare (SEDAC mirror unreachable)", licence="CC BY 4.0 (figshare)", layers=reba,
                       type="city with population series", geocoded_dated=len(recs_all),
                       by_era_of_start={n: sum(v["by_era_of_start"][n] for v in reba.values()) for _, _, n in ERAS})

# ---------------------------------------------------------------- plague (Biraben via Buentgen 2012 + Atanasiu 2008, merged 2015)
txt = open(f"{SRC}/plague/europe-pnas/resources/plague-db-europe.txt", encoding="utf-8").read()
recs, src = [], collections.Counter()
for m in re.finditer(r'\{:lat ([-\d.]+), :lon ([-\d.]+), :name "((?:[^"\\]|\\.)*)", :source "((?:[^"\\]|\\.)*)", :year (-?\d+)\}', txt):
    c = ok_coord(m.group(1), m.group(2))
    if c:
        y = int(m.group(5))
        recs.append((c[0], c[1], y, y + 1)); src[m.group(4)] += 1
S["plague_biraben"] = dict(label="Historical plague outbreaks 1339-1900 (Biraben, digitised by Buentgen et al. 2012 and Atanasiu et al. 2008; merged by Schmid et al. 2015)",
                           access="open on Zenodo (record 14973)", licence="repository under Eclipse Public License 1.0 (Zenodo metadata)",
                           sources=dict(src), items_total=len(recs), **summarize(recs, "point event (year)"))
EV["plague_biraben"] = recs

# ---------------------------------------------------------------- ORBIS
rows = list(csv.DictReader(io.StringIO(open(f"{SRC}/orbis_o_sites.csv", encoding="latin-1").read().replace("\r", "\n"))))
named = [r for r in rows if r["label"].strip() not in ("", "x")]
S["orbis"] = dict(label="ORBIS (Stanford Geospatial Network Model of the Roman World)", access="o_sites.csv + new_routes.topojson behind the web app",
                  licence="not stated for the data; map tiles CC BY-NC 3.0 (AWMC)", type="network node, single time slice (~AD 200)",
                  items_total=len(rows), named_sites=len(named), geocoded_dated=0,
                  note="No dates: one reconstruction of the Roman network around AD 200. Useful for routes/travel, not as dated events.")

# ---------------------------------------------------------------- not measurable from here
S["hyde"] = dict(label="HYDE 3.2.1 (History Database of the Global Environment)", access="open on DANS (doi:10.17026/dans-25g-gez3); 5.5 GB",
                 licence="readme: CC BY 3.0; DANS record: CC0 1.0 (conflict; assume CC BY 3.0)", type="population/land-use grids (5 arcmin)",
                 note="10,000 BCE-2015 CE; 1000-yr steps BCE, 100-yr to 1700, 10-yr to 2000, yearly 2000-2015 (readme). Not downloaded (5.3 GB baseline).",
                 geocoded_dated=None)
S["acled"] = dict(label="ACLED", access="API refuses requests without a key (HTTP 403); needs an account", licence="ACLED terms of use", geocoded_dated=None)
S["emdat"] = dict(label="EM-DAT", access="public.emdat.be is a login page; data needs an account", licence="EM-DAT terms (account)", geocoded_dated=None)
S["defoedb"] = dict(label="'DefoeDB (plague 1347-1666)'", access="defoedb.cambridge.org has no DNS record: the database does not exist",
                    note="The survey's entry appears to be invented. The real dataset for this purpose is the Biraben/Buentgen plague data measured above.",
                    geocoded_dated=None)
S["million_cities_grump"] = dict(label="'Million Cities / GRUMP'", access="SEDAC (sedac.ciesin.columbia.edu) unreachable",
                                 note="GRUMP is a ~2000 urban-extent map, not historical. The historical city dataset is Reba et al. 2016, measured above.",
                                 geocoded_dated=None)

# ---------------------------------------------------------------- density probe
def load_pack(fn):
    j = json.load(open(f"{HIST}/{fn}", encoding="utf-8"))
    return DP["load_events"](j)


base = []
for fn in json.load(open(f"{HIST}/index.json"))["packs"]:
    base += load_pack(fn)
wiki_now = DP["load_events"](json.load(open("/tmp/events_wikipedia_rebuild_check.json"))) if os.path.exists("/tmp/events_wikipedia_rebuild_check.json") else None

# validate probe_np against the exact port on a source small enough for the slow version
chk = EV["plague_biraben"] + EV["ncei_volcanoes"]
assert probe_np(chk) == DP["probe"](chk, POINTS), "numpy probe disagrees with the exact port"

D = {"validation": "probe_np == density_probe.probe on plague+NCEI volcanoes: OK"}
for k, recs in EV.items():
    D[k] = {"records": len(recs), "table": probe_np(recs)}
point_sources = ["ncei_earthquakes", "ncei_tsunamis", "ncei_volcanoes", "gvp_eruptions", "ucdp_ged", "plague_biraben"]
long_sources = ["pleiades", "chgis_county", "chgis_prefecture", "reba_cities"]
today = base + (wiki_now or [])
D["A_today_packs_plus_wikipedia_6373"] = {"records": len(today), "table": probe_np(today)}
D["C_today_plus_new_point_events"] = {"records": len(today) + sum(len(EV[k]) for k in point_sources),
                                      "table": probe_np(today + [r for k in point_sources for r in EV[k]])}
D["D_today_plus_everything_open"] = {"records": len(today) + sum(len(EV[k]) for k in point_sources + long_sources),
                                     "table": probe_np(today + [r for k in point_sources + long_sources for r in EV[k]])}

json.dump(S, open(f"{HERE}/sources_summary.json", "w"), indent=1, ensure_ascii=False)
json.dump(D, open(f"{HERE}/sources_density.json", "w"), indent=1)

# ---------------------------------------------------------------- print
E = [n for _, _, n in ERAS]
print(f"{'source':22}{'dated+geo':>10}" + "".join(f"{e[:12]:>13}" for e in E))
for k, v in S.items():
    if v.get("geocoded_dated"):
        print(f"{k:22}{v['geocoded_dated']:>10}" + "".join(f"{v['by_era_of_start'].get(e, 0):>13}" for e in E))
print("\nprobe: % of 400 land points with something alive within 100 km")
print(f"{'scenario':38}" + "".join(f"{y:>7}" for y in YEARS))
for k in ["A_today_packs_plus_wikipedia_6373"] + list(EV) + ["C_today_plus_new_point_events", "D_today_plus_everything_open"]:
    print(f"{k[:38]:38}" + "".join(f"{D[k]['table'][y]['pct_within']['100km']:>7}" for y in YEARS))


# ---------------------------------------------------------------- like-for-like: existing SITES vs new long-lived sources
# The mod's 15,954 sites carry occupiedEnd; only 227 carry occupiedStart (the rest are estimated
# in Java by SettlementYearEstimator). Bound them: lower = explicit starts only; upper = every
# site alive from the beginning of the range until occupiedEnd (the most the existing sites can cover).
sites_lo, sites_hi = [], []
for fn in json.load(open(f"{HIST}/index.json"))["packs"]:
    for s in json.load(open(f"{HIST}/{fn}", encoding="utf-8")).get("sites", []):
        c = ok_coord(s.get("lat"), s.get("lon"))
        if not c:
            continue
        end = s.get("occupiedEnd", 10 ** 6)
        if "occupiedStart" in s:
            sites_lo.append((c[0], c[1], s["occupiedStart"], end))
        sites_hi.append((c[0], c[1], s.get("occupiedStart", -10 ** 6), end))
new_long = [r for k in long_sources for r in EV[k]]
D["S_lo_existing_sites_explicit_start_only"] = {"records": len(sites_lo), "table": probe_np(sites_lo)}
D["S_hi_existing_sites_all_alive_until_end"] = {"records": len(sites_hi), "table": probe_np(sites_hi)}
D["S_hi_plus_new_long_lived_sources"] = {"records": len(sites_hi) + len(new_long), "table": probe_np(sites_hi + new_long)}
json.dump(D, open(f"{HERE}/sources_density.json", "w"), indent=1)
print("\nlike-for-like presence (sites): % of 400 land points within 100 km / 50 km")
for k in ["S_lo_existing_sites_explicit_start_only", "S_hi_existing_sites_all_alive_until_end", "S_hi_plus_new_long_lived_sources"]:
    print(f"{k[:38]:38}" + "".join(f"{D[k]['table'][y]['pct_within']['100km']:>7}" for y in YEARS))
    print(f"{'   (50 km)':38}" + "".join(f"{D[k]['table'][y]['pct_within']['50km']:>7}" for y in YEARS))


# ---------------------------------------------------------------- overlap with what the mod already has
# NOAA/GVP have no Wikidata IDs; count a record as "already in the mod" if a mod event of kind
# 'disaster' has the same start year and lies within 150 km.
mod_dis = []
for fn in json.load(open(f"{HIST}/index.json"))["packs"]:
    for e in json.load(open(f"{HIST}/{fn}", encoding="utf-8")).get("events", []):
        if e.get("kind") == "disaster" and "lat" in e and "start" in e:
            mod_dis.append((float(e["lat"]), float(e["lon"]), int(e["start"])))
md = np.array(mod_dis)
for k in ["ncei_earthquakes", "ncei_tsunamis", "ncei_volcanoes", "gvp_eruptions"]:
    hit = 0
    for la, lo, s, e in EV[k]:
        if s > 2026 or e - 1 < -3000:
            continue
        cand = md[md[:, 2] == s]
        if len(cand):
            p1, p2 = math.radians(la), np.radians(cand[:, 0])
            h = np.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * np.cos(p2) * np.sin(np.radians(cand[:, 1] - lo) / 2) ** 2
            if (2 * 6371.0 * np.arcsin(np.minimum(1, np.sqrt(h))) <= 150).any():
                hit += 1
    inr = sum(1 for la, lo, s, e in EV[k] if not (s > 2026 or e - 1 < -3000))
    S[k]["in_range"] = inr
    S[k]["matches_a_mod_disaster_same_year_150km"] = hit
    S[k]["new_vs_mod"] = inr - hit
    print(f"{k:18} in range {inr:6}  already in mod (same year, <=150 km) {hit:5}  new {inr - hit:6}")
json.dump(S, open(f"{HERE}/sources_summary.json", "w"), indent=1, ensure_ascii=False)
