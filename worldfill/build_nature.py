#!/usr/bin/env python3
"""Step 28 (system C21): natural events for every place: tropical cyclones, and the floods, wildfires, landslides,
avalanches, tornadoes, heat waves, droughts, famines and epidemics Wikidata places on the map.

    python3 build_nature.py            write history/events_storms.json.gz and history/events_nature.json.gz
    python3 build_nature.py --check    rebuild in memory and compare with the files in the mod (exit 1 if they differ)

Inputs (not kept in the workspace; fetched again at any time):
  build/events/ibtracs.ALL.list.v04r01.csv  NOAA NCEI, IBTrACS version 4 (International Best Track Archive for Climate
                                            Stewardship): every tropical cyclone from 1842 on, six-hourly points
                                            (public domain, US government work)
  build/events/raw/nature_*.tsv.gz          fetch_events_wd.py nature (Wikidata, CC0)

Storms: one event where a storm comes ashore (the first point over land of each stretch over land), or, for a storm
that never comes ashore, where it passes closest to land within 60 km; only storms with tropical-storm winds (34 knots)
or more at that time. Its reach: 100 km for a tropical storm, 180 km for a hurricane, typhoon or cyclone, 250 km for a
major one (96 knots). The name: "Hurricane Katrina (winds of about 280 km/h)", "the typhoon of 1906"; a storm Wikidata
knows by name and year gets its Wikidata number as its id (q<number>), so its card opens from the news.
Other natural events: Wikidata's, with a year (to the year or better) and a point (its own, or its place's); one with
only a country is news from the whole land (regional). An event already in history/events_hazards.json.gz (the same
kind, a year apart at most, within 300 km) is left out.
"""
import csv
import gzip
import io
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_cards as bc  # noqa: E402

RAW = os.path.join(HERE, "build", "events", "raw")
IBTRACS = os.path.join(HERE, "build", "events", "ibtracs.ALL.list.v04r01.csv")
HIST = os.path.join(bc.DATA, "history")
OUT_STORMS = os.path.join(HIST, "events_storms.json.gz")
OUT_NATURE = os.path.join(HIST, "events_nature.json.gz")
HAZARDS = os.path.join(HIST, "events_hazards.json.gz")

TS_KT, HURRICANE_KT, MAJOR_KT = 34, 64, 96
COAST_KM = 60
NATURE_KINDS = ["flood", "wildfire", "landslide", "avalanche", "tornado", "heatwave", "drought", "famine", "epidemic",
                "pandemic"]
RADIUS = {"flood": 80, "wildfire": 40, "landslide": 15, "avalanche": 10, "tornado": 25, "heatwave": 250, "drought": 300,
          "famine": 250, "epidemic": 150, "pandemic": 300}
REGIONAL_RADIUS = {"heatwave": 600, "drought": 800, "famine": 600, "epidemic": 500, "pandemic": 800, "flood": 300,
                   "wildfire": 200, "landslide": 100, "avalanche": 100, "tornado": 150}
# Which hazards an event of a kind may repeat (events_hazards.json.gz kinds).
SAME_AS = {"flood": {"flood"}, "famine": {"famine"}, "epidemic": {"epidemic", "pandemic", "plague"},
           "pandemic": {"epidemic", "pandemic", "plague"}}
STORM_WORDS = re.compile(r"^(super |severe |very severe |extremely severe |)(tropical storm|typhoon|hurricane|cyclone|"
                         r"cyclonic storm|tropical cyclone|tropical depression|subtropical storm|storm)\s+",
                         re.IGNORECASE)


def jbytes(doc):
    """Deterministic gzip of a JSON document (no time stamp inside)."""
    raw = json.dumps(doc, ensure_ascii=False, separators=(",", ":"), sort_keys=False).encode("utf-8")
    buf = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buf, mtime=0, compresslevel=9) as g:
        g.write(raw)
    return buf.getvalue()


def km(a_lat, a_lon, b_lat, b_lon):
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dp, dl = p2 - p1, math.radians(b_lon - a_lon)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0088 * math.asin(min(1.0, math.sqrt(h)))


def num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------------------------------------------ storms

def storm_term(basin, kt):
    if basin in ("NA", "EP"):
        return "hurricane" if kt >= HURRICANE_KT else "tropical storm"
    if basin == "WP":
        return "typhoon" if kt >= HURRICANE_KT else "tropical storm"
    return "cyclone"


def wikidata_cyclones():
    """(NAME, year) -> qid, from Wikidata's tropical cyclones (labels like "Hurricane Katrina")."""
    out = {}
    for c in bc.rows_in(RAW, "nature_cyclone"):
        q = bc.qid_of(c[0])
        label = bc.literal(c[1])
        y = bc.year_of(c[4]) if len(c) > 4 else None
        if not q or not label or y is None:
            continue
        name = STORM_WORDS.sub("", label).strip()
        name = re.sub(r"\s*\(\d{4}\)$", "", name).strip().upper()
        if not name or re.search(r"\d", name):
            continue
        out.setdefault((name, y), q)
    return out


def storms():
    if not os.path.exists(IBTRACS):
        raise SystemExit(f"{IBTRACS} is missing: download IBTrACS v04r01 (see the docstring)")
    names = wikidata_cyclones()
    by_sid = {}
    order = []
    with open(IBTRACS, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        head = next(r)
        next(r)  # units
        col = {h: i for i, h in enumerate(head)}
        winds = [i for h, i in col.items() if h.endswith("_WIND")]
        for row in r:
            tt = row[col["TRACK_TYPE"]]
            if not (tt.startswith("main") or tt == "PROVISIONAL"):
                continue
            sid = row[col["SID"]]
            lat, lon = num(row[col["LAT"]]), num(row[col["LON"]])
            d2l = num(row[col["DIST2LAND"]])
            if lat is None or lon is None or d2l is None:
                continue
            kt = max([w for w in (num(row[i]) for i in winds) if w is not None] or [0.0])
            t = row[col["ISO_TIME"]]
            if sid not in by_sid:
                by_sid[sid] = {"basin": row[col["BASIN"]], "name": row[col["NAME"]], "points": []}
                order.append(sid)
            if lon > 180:
                lon -= 360
            by_sid[sid]["points"].append((t, lat, lon, d2l, kt))
    events = []
    stats = {"storms": len(by_sid), "landfalls": 0, "near coast": 0, "named by Wikidata": 0, "too weak": 0}
    for sid in order:
        s = by_sid[sid]
        pts = s["points"]
        hits = []
        on_land = False
        for i, (t, lat, lon, d2l, kt) in enumerate(pts):
            land = d2l <= 0
            if land and not on_land:
                before = max(p[4] for p in pts[max(0, i - 2):i + 1])
                hits.append((t, lat, lon, before, "ashore"))
            on_land = land
        if not hits:
            near = min(pts, key=lambda p: p[3])
            if near[3] <= COAST_KM:
                hits.append((near[0], near[1], near[2], near[4], "near"))
        strongest = max((p[4] for p in pts), default=0.0)
        n = 0
        for t, lat, lon, kt, how in hits:
            if kt < TS_KT:
                stats["too weak"] += 1
                continue
            year = int(t[:4])
            term = storm_term(s["basin"], kt)
            raw_name = s["name"].strip().upper()
            named = raw_name not in ("", "UNNAMED", "NOT_NAMED", "NONAME") and not re.search(r"\d", raw_name)
            if named:
                name = term.title() + " " + raw_name.title()
            else:
                name = f"the {term} of {year}"
            if kt >= HURRICANE_KT:
                name += f" (winds of about {int(round(kt * 1.852 / 10.0)) * 10} km/h)"
            q = names.get((raw_name, year)) if named else None
            if q is None and named:
                q = names.get((raw_name, year - 1)) or names.get((raw_name, year + 1))
            n += 1
            if q:
                eid = f"q{q}" if n == 1 else f"q{q}_{n}"
                if n == 1:
                    stats["named by Wikidata"] += 1
            else:
                eid = f"tc_{sid}" if n == 1 else f"tc_{sid}_{n}"
            radius = 250 if kt >= MAJOR_KT else 180 if kt >= HURRICANE_KT else 100
            stats["landfalls" if how == "ashore" else "near coast"] += 1
            events.append({"id": eid, "name": name, "start": year, "end": year + 1, "lat": round(lat, 3),
                           "lon": round(lon, 3), "radiusKm": radius, "kind": "cyclone", "effect": "disruption",
                           "confidence": "ibtracs", "windKt": int(round(kt)), "strongestKt": int(round(strongest))})
    events.sort(key=lambda e: (e["start"], e["id"]))
    doc = {"id": "storms", "title": "Tropical cyclones where they came ashore or passed close to land, 1842 on (NOAA "
           "NCEI IBTrACS v04r01, public domain); names and numbers matched with Wikidata. Overlay only. Never stoppable. "
           "Not towns.", "source": "worldfill/build_nature.py", "sites": [], "events": events}
    return doc, stats


# ------------------------------------------------------------------------------------------------ other nature

def hazards_index():
    with gzip.open(HAZARDS, "rt", encoding="utf-8") as f:
        doc = json.load(f)
    idx = {}
    for e in doc["events"]:
        idx.setdefault(e["start"], []).append(e)
    return idx


def nature():
    hz = hazards_index()
    seen = {}
    stats = {}
    for kind in NATURE_KINDS:
        for c in bc.rows_in(RAW, f"nature_{kind}"):
            q = bc.qid_of(c[0])
            if not q:
                continue
            prec = int(c[5]) if len(c) > 5 and c[5] else 0
            y = bc.year_of(c[4]) if len(c) > 4 else None
            if y is None or prec < 9:
                continue
            y2 = bc.year_of(c[6]) if len(c) > 6 and c[6] else None
            own = bc.point(c[7]) if len(c) > 7 else None
            loc = bc.point(c[8]) if len(c) > 8 else None
            ctry = bc.point(c[10]) if len(c) > 10 else None
            deaths = num(c[12]) if len(c) > 12 else None
            old = seen.get(q)
            rec = {"q": q, "kind": kind, "name": bc.literal(c[1]), "year": y, "end": y2, "own": own or loc,
                   "ctry": ctry, "deaths": deaths}
            if old is None or (old["own"] is None and rec["own"] is not None):
                seen[q] = rec
    events = []
    for q in sorted(seen):
        r = seen[q]
        kind = r["kind"]
        if r["own"]:
            lat, lon = r["own"]
            regional = False
        elif r["ctry"]:
            lat, lon = r["ctry"]
            regional = True
        else:
            stats["no place"] = stats.get("no place", 0) + 1
            continue
        if not -3000 <= r["year"] <= 2026:
            continue
        dup = False
        for yy in (r["year"] - 1, r["year"], r["year"] + 1):
            for h in hz.get(yy, []):
                if h["kind"] in SAME_AS.get(kind, ()) and km(lat, lon, h["lat"], h["lon"]) <= 300:
                    dup = True
                    break
            if dup:
                break
        if dup:
            stats["already a hazard"] = stats.get("already a hazard", 0) + 1
            continue
        end = r["end"] if r["end"] is not None and r["end"] >= r["year"] else r["year"]
        events.append({"id": f"q{q}", "name": r["name"], "start": r["year"], "end": min(end, r["year"] + 5) + 1,
                       "lat": round(lat, 3), "lon": round(lon, 3),
                       "radiusKm": REGIONAL_RADIUS[kind] if regional else RADIUS[kind], "kind": kind,
                       "effect": "disruption", "confidence": "wikidata_region" if regional else "wikidata"})
        stats[kind] = stats.get(kind, 0) + 1
    events.sort(key=lambda e: (e["start"], e["id"]))
    doc = {"id": "nature", "title": "Floods, wildfires, landslides, avalanches, tornadoes, heat waves, droughts, famines "
           "and epidemics with a year and a place (Wikidata, CC0); those already in events_hazards.json.gz are left out. "
           "An event placed only by its country is news from the whole land. Overlay only. Never stoppable. Not towns.",
           "source": "worldfill/build_nature.py", "sites": [], "events": events}
    return doc, stats


def main(argv):
    check = "--check" in argv
    bad = 0
    for path, build in ((OUT_STORMS, storms), (OUT_NATURE, nature)):
        doc, stats = build()
        data = jbytes(doc)
        name = os.path.basename(path)
        if check:
            same = os.path.exists(path) and open(path, "rb").read() == data
            print(f"{name}: {'up to date' if same else 'OUT OF DATE (run build_nature.py)'}")
            bad += 0 if same else 1
            continue
        with open(path, "wb") as f:
            f.write(data)
        print(f"{name}: {len(doc['events']):,} events, {len(data):,} bytes; " + ", ".join(f"{k} {v:,}" for k, v in
                                                                                       stats.items()))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
