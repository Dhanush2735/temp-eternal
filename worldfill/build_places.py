#!/usr/bin/env python3
"""Step 2: long-lived places as dated sites (Pleiades, CHGIS V6, Reba et al. 2016).

A Wikipedia or Wikidata event lasts one year, so it cannot keep the map populated. Places do:
an ancient town, a county seat or a city is "occupied" for centuries, the mod spawns its people
while it stands, and HistoryGazetteer.estimatedHinterland() already grows unnamed countryside
villages (labelled estimated) up to 80 km around every dated town and city.

Writes three history packs (gzipped, *.json.gz) into the mod and registers them in index.json:

  places_pleiades.json  Pleiades gazetteer of ancient places (CC BY 3.0): settlements, villas,
                        forts, stations, sanctuaries with their attested date range, capped at
                        AD 640 (Pleiades' own scope ends with late antiquity; a later "modern"
                        attestation only says the place still exists, not who lived there)
  places_chgis.json     CHGIS V6 county-level seats, China 763 BC - AD 1911 (CC0 1.0); a seat
                        still standing when the data ends in 1911 stays open to the present
  places_reba.json      Reba, Reitsma & Seto 2016 historical urban population (CC BY 4.0):
                        cities from their first recorded population to the next survey year
                        after their last one (open to the present if listed in the last year)

Rules shared by all three:
  * "estimatorAnchor": false - the places are on the map, but the settlement-year estimator does
    not pull the undated present-day (Telangana) places toward them, so their curated estimated
    years stay exactly as they were (HistoryGazetteer reads the flag);
  * a curated site (the eight region packs) always wins: a new site within 10 km of one loses
    exactly the years the curated site covers, and keeps the rest;
  * a Reba city that Pleiades already names (within 5 km) loses the years up to AD 640, so the
    ancient name shows in antiquity and the modern name afterwards;
  * civHint is one of the mod's 133 authored civilizations, so a site only claims a polity in
    years that polity existed (otherwise HistoricalPresence falls through to rulers / borders),
    and NPC names come from that civ's culture pool. China uses the dynasty of the record's
    years; elsewhere Civs.pick scores civs by how much of the site's life they existed, whether
    their name maps to a real name pool, and capital distance. A Reba city's life is split at
    AD 641 and 1500 so each era gets its own civHint.

Usage: python3 build_places.py [--dry-run]
"""
import collections, csv, gzip, json, math, os, re, struct, sys, zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modpack as M        # noqa: E402

SRC = os.environ.get("SRCDATA", "/home/user/.cache/srcdata")
CIVS = f"{M.MOD}/src/main/resources/data/eternalengine/eternal/civilizations/foundation_civilizations.json"
CURATED = ["indus.json", "mesopotamia.json", "egypt.json", "china.json", "mediterranean.json",
           "south_asia.json", "americas.json", "afro_islamic.json"]
OPEN = 9999                 # occupiedEnd for "still there"
FLOOR = -5000               # earliest occupiedStart written (the simulation starts at 3000 BC);
                            # Pleiades has Palaeolithic minDates down to -2,600,000, and the
                            # settlement-year estimator averages anchor start years
PLEIADES_CAP = 640
MIN_SEGMENT = 25            # years; shorter leftovers after subtracting curated spans are dropped
REPORT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_places_report.json")
csv.field_size_limit(1 << 30)


# ------------------------------------------------------------------ civilizations
class Civs:
    """Pick the authored civilization a site belongs to.

    score = (share of the site's life the civ existed) x (1.0 if the civ's name maps to a real
    name pool in VillagerNameDatabase.cultureFor, else 0.9) / (1 + capital distance / 400 km),
    over civs with a capital within 2,500 km that existed at some point of the site's life.
    No such civ: the nearest capital with a real name pool within 2,500 km, else the nearest."""

    def __init__(self):
        from culture_pools import culture_for
        self.civs = json.load(open(CIVS, encoding="utf-8"))
        for c in self.civs:
            c["fall"] = c.get("fallYear", OPEN)
            c["pool"] = culture_for(c["id"])

    def pick(self, lat, lon, s, e):
        e = min(e, 2027)
        life = max(1, e - s)
        best, near_pool, near_any = None, None, None
        for c in self.civs:
            d = M.haversine_km(lat, lon, c["capitalLat"], c["capitalLon"])
            if near_any is None or d < near_any[0]:
                near_any = (d, c["id"])
            if d > 2500:
                continue
            if c["pool"] != "generic" and (near_pool is None or d < near_pool[0]):
                near_pool = (d, c["id"])
            ov = min(e, c["fall"]) - max(s, c["foundingYear"])
            if ov <= 0:
                continue
            score = (ov / life) * (1.0 if c["pool"] != "generic" else 0.9) / (1 + d / 400)
            if best is None or score > best[0]:
                best = (score, c["id"])
        return (best or near_pool or near_any)[1]


CHINA_DYN = [(-1046, -256, "china_zhou"), (-256, -206, "china_qin"), (-206, 220, "china_han"),
             (618, 907, "china_tang"), (960, 1279, "china_song"), (1279, 1368, "mongol_empire"),
             (1368, 1644, "china_ming"), (1644, OPEN, "china_qing")]


def china_civ(lat, lon, s, e):
    """Dynasty of the record's first year; in a gap (220-618, 907-960) the first authored
    dynasty that begins inside the record's span; Jin / Western Xia for the north in their years."""
    def at(y):
        if 1127 <= y < 1234 and lat > 33.5:
            return "jin_dynasty"
        if 1038 <= y < 1227 and lon < 107 and lat > 35:
            return "western_xia"
        for a, b, cid in CHINA_DYN:
            if a <= y < b:
                return cid
        return None
    c = at(s)
    if c:
        return c
    for a, b, cid in CHINA_DYN:
        if s < a < e:
            return at(a)
    return "china_zhou" if s < -1046 else "china_tang"


# ------------------------------------------------------------------ helpers
def subtract(span, cuts):
    """[s, e) minus every [a, b) in cuts -> remaining pieces."""
    pieces = [span]
    for a, b in cuts:
        nxt = []
        for s, e in pieces:
            if b <= s or a >= e:
                nxt.append((s, e)); continue
            if s < a:
                nxt.append((s, a))
            if b < e:
                nxt.append((b, e))
        pieces = nxt
    return [(s, e) for s, e in pieces if e - s >= MIN_SEGMENT or e == OPEN]


def fix0(y):
    y = max(y, FLOOR)
    return 1 if y == 0 else y


def num(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def num_f(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(x) else x


# ------------------------------------------------------------------ Pleiades
PLEIADES_CITY_TAGS = {"dare:major=1", "dare:feature=major settlement"}
PLEIADES_CLASS = [
    ("city", {"urban"}),
    ("town", {"settlement", "settlement-modern", "fortified-settlement", "polis", "port", "harbor",
              "hillfort", "tell", "oppidum"}),
    ("village", {"vicus", "deme-attic", "villa", "estate", "farm", "fort", "fort-2", "fortlet",
                 "castellum", "fort-group", "castle", "station", "monastery", "sanctuary", "temple",
                 "temple-2", "nuraghe"}),
]


def read_pleiades(stats):
    out = []
    with gzip.open(f"{SRC}/pleiades-places-latest.csv.gz", "rt", encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            stats["rows"] += 1
            ft = {t.strip() for t in (r.get("featureTypes") or "").split(",")}
            tags = {t.strip() for t in (r.get("tags") or "").split(",")}
            rank = None
            for k, types in PLEIADES_CLASS:
                if ft & types:
                    rank = k; break
            if rank is None:
                stats["not_a_dwelling_place"] += 1; continue
            if rank == "town" and tags & PLEIADES_CITY_TAGS:
                rank = "city"
            la, lo = num_f(r.get("reprLat")), num_f(r.get("reprLong"))
            if r.get("locationPrecision") not in ("precise", "rough") or la is None or lo is None:
                stats["no_location"] += 1; continue
            s, e = num(r.get("minDate")), num(r.get("maxDate"))
            if s is None or e is None or e < s:
                stats["undated"] += 1; continue
            if s > PLEIADES_CAP:
                stats["only_after_640"] += 1; continue
            if e < FLOOR:
                stats["entirely_before_5000_bc"] += 1; continue
            out.append({"id": f"pl_{r['id']}", "name": (r.get("title") or "").strip() or f"Pleiades {r['id']}",
                        "lat": round(la, 5), "lon": round(lo, 5), "occupiedStart": fix0(s),
                        "occupiedEnd": min(e, PLEIADES_CAP) + 1, "rank": rank, "confidence": "pleiades"})
            stats["kept"] += 1
    return out


# ------------------------------------------------------------------ CHGIS
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
    return rows


def read_chgis(stats):
    with zipfile.ZipFile(f"{SRC}/chgis_Q9VOF5_v6_time_cnty_pts_utf_wgs84.zip") as z:
        rows = read_dbf(z.read(next(x for x in z.namelist() if x.endswith(".dbf"))))
    out = []
    for r in rows:
        stats["rows"] += 1
        la, lo, b0, e0 = r.get("Y_COOR"), r.get("X_COOR"), r.get("BEG_YR"), r.get("END_YR")
        if None in (la, lo, b0, e0) or not (-90 <= la <= 90 and -180 <= lo <= 180) or (la == 0 and lo == 0):
            stats["bad_row"] += 1; continue
        b0, e0 = int(b0), int(e0)
        if e0 > 1911:                     # a few rows carry 11911 for 1911
            stats["end_year_typo_fixed"] += 1
            e0 = 1911
        if e0 < b0:
            stats["bad_row"] += 1; continue
        name = r.get("NAME_PY") or "County seat"
        if r.get("NAME_CH"):
            name = f"{name} ({r['NAME_CH']})"
        out.append({"id": f"chgis_{int(r['SYS_ID'])}", "name": name, "lat": round(la, 5), "lon": round(lo, 5),
                    "occupiedStart": fix0(b0),
                    "occupiedEnd": OPEN if e0 >= 1911 else e0 + 1,   # 1911 = where the data stops
                    "rank": "town", "confidence": "chgis_v6"})
        stats["kept"] += 1
    return out


# ------------------------------------------------------------------ Reba et al. 2016
def read_reba(stats):
    cities = []
    for key, fn in [("chandler", "reba_2059494_chandlerV2.csv"), ("modelski_ancient", "reba_2059497_modelskiAncientV2.csv"),
                    ("modelski_modern", "reba_2059500_modelskiModernV2.csv")]:
        rows = list(csv.DictReader(open(f"{SRC}/{fn}", encoding="latin-1", newline="")))
        cols = [k for k in rows[0] if k and re.fullmatch(r"(BC|AD)_\d+", k)]
        yr = {k: (-int(k[3:]) if k.startswith("BC") else int(k[3:])) for k in cols}
        years = sorted(set(yr.values()))
        last = years[-1]
        for r in rows:
            stats["rows_" + key] += 1
            la, lo = num_f(r.get("Latitude")), num_f(r.get("Longitude"))
            obs = {}
            for k in cols:
                v = (r.get(k) or "").strip().replace(",", "")
                try:
                    p = float(v)
                except ValueError:
                    continue
                if p > 0:
                    obs[yr[k]] = p
            if la is None or lo is None or not obs:
                stats["no_coords_or_population"] += 1; continue
            first, lastobs = min(obs), max(obs)
            if lastobs == last:
                # listed in the source's final year: Chandler and Modelski modern run to the present;
                # Modelski ancient stops at AD 1000, so "still listed" there only means "until 1100"
                end = 1100 if key == "modelski_ancient" else OPEN
            else:
                end = next(y for y in years if y > lastobs)
            cities.append({"name": (r.get("City") or "").strip(), "other": (r.get("OtherName") or "").strip(),
                           "lat": la, "lon": lo, "s": first, "e": end, "obs": obs, "set": key})
    # the three datasets list many of the same cities: merge within 15 km and a shared name
    # word, or within 3 km whatever the spelling
    merged, grid = [], {}
    for c in sorted(cities, key=lambda c: c["s"]):
        words = set(re.findall(r"[^\W\d_]{3,}", (c["name"] + " " + c["other"]).lower()))
        cell = (math.floor(c["lat"]), math.floor(c["lon"]))
        hit = None
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                for m in grid.get((cell[0] + dy, cell[1] + dx), []):
                    d = M.haversine_km(c["lat"], c["lon"], m["lat"], m["lon"])
                    if d <= 3 or (d <= 15 and words & m["words"]):
                        hit = m
                        break
                if hit:
                    break
            if hit:
                break
        if hit:
            hit["s"], hit["e"] = min(hit["s"], c["s"]), max(hit["e"], c["e"])
            hit["obs"].update(c["obs"]); hit["words"] |= words
            stats["merged_across_datasets"] += 1
            continue
        c["words"] = words
        merged.append(c)
        grid.setdefault(cell, []).append(c)
    out = []
    for i, c in enumerate(merged):
        out.append({"id": f"reba_{M.slug(c['name'], 32)}_{i}", "name": c["name"],
                    "lat": round(c["lat"], 5), "lon": round(c["lon"], 5),
                    "occupiedStart": fix0(c["s"]), "occupiedEnd": c["e"], "rank": "city",
                    "confidence": "reba_2016"})
    stats["cities"] = len(out)
    return out


# ------------------------------------------------------------------ build
def apply_cuts(sites, cutters, km, stats, key, only_before=None):
    """Remove from each site the years covered by any cutter within km (only_before: cut the
    cutter's years only up to that year)."""
    grid = M.Grid(cutters)
    out = []
    for s in sites:
        cuts = []
        for c in grid.near(s["lat"], s["lon"]):
            if M.haversine_km(s["lat"], s["lon"], c["lat"], c["lon"]) <= km:
                a, b = c["occupiedStart"], c.get("occupiedEnd", OPEN)
                if only_before is not None:
                    b = min(b, only_before)
                if b > a:
                    cuts.append((a, b))
        span = (s["occupiedStart"], s["occupiedEnd"])
        pieces = subtract(span, cuts) if cuts else [span]
        if pieces == [span]:
            out.append(s); continue
        stats[key + "_trimmed"] += 1
        if not pieces:
            stats[key + "_dropped"] += 1; continue
        for j, (a, b) in enumerate(pieces):
            t = dict(s, occupiedStart=fix0(a), occupiedEnd=b)
            if len(pieces) > 1:
                t["id"] = f"{s['id']}_{j + 1}"
            out.append(t)
    return out


ERA_CUTS = [641, 1500]   # a city's life is split here so each era gets its own civHint


def split_eras(sites, stats):
    out = []
    for s in sites:
        a, b = s["occupiedStart"], s["occupiedEnd"]
        cuts = [c for c in ERA_CUTS if a < c < b]
        if not cuts:
            out.append(s); continue
        stats["reba_split_into_eras"] += 1
        bounds = [a] + cuts + [b]
        for j in range(len(bounds) - 1):
            out.append(dict(s, id=f"{s['id']}_e{j + 1}", occupiedStart=fix0(bounds[j]), occupiedEnd=bounds[j + 1]))
    return out


def main(dry=False):
    stats = {k: collections.Counter() for k in ("pleiades", "chgis", "reba", "build")}
    civs = Civs()
    curated = [s for s in M.existing_sites() if s["_pack"] in CURATED and "occupiedStart" in s]
    stats["build"]["curated_sites"] = len(curated)

    ple = read_pleiades(stats["pleiades"])
    chg = read_chgis(stats["chgis"])
    reb = read_reba(stats["reba"])

    ple = apply_cuts(ple, curated, 10, stats["build"], "pleiades_vs_curated")
    chg = apply_cuts(chg, curated, 10, stats["build"], "chgis_vs_curated")
    reb = apply_cuts(reb, curated, 10, stats["build"], "reba_vs_curated")
    reb = apply_cuts(reb, ple, 5, stats["build"], "reba_vs_pleiades", only_before=PLEIADES_CAP + 1)

    reb = split_eras(reb, stats["build"])
    for s in ple + reb:
        s["civHint"] = civs.pick(s["lat"], s["lon"], s["occupiedStart"], s["occupiedEnd"])
    for s in chg:
        s["civHint"] = china_civ(s["lat"], s["lon"], s["occupiedStart"], s["occupiedEnd"])

    ids = collections.Counter(s["id"] for s in ple + chg + reb)
    dup = [i for i, n in ids.items() if n > 1]
    assert not dup, f"duplicate ids: {dup[:5]}"
    for s in ple + chg + reb:
        M.check_site(s)

    packs = {
        "places_pleiades.json.gz": {
            "id": "pleiades_places",
            "title": "Ancient places from the Pleiades gazetteer: settlements, villas, forts, road stations "
                     "and sanctuaries, each occupied over its attested date range (capped at AD 640).",
            "source": "Pleiades (pleiades.stoa.org), daily dump pleiades-places-latest.csv, CC BY 3.0. "
                      "Attribution: Pleiades, a community-built gazetteer and graph of ancient places.",
            "spawnRadiusKm": 20,
            "estimatorAnchor": False,
            "comparedSources": [
                "Date range = Pleiades minDate..maxDate (the periods the place is attested in), not a founding "
                "or abandonment year",
                "Rank: urban or DARE major settlement = city; settlement, polis, port, hillfort, tell = town; "
                "vicus, villa, fort, station, sanctuary, temple = village",
                "Years a curated region-pack site covers within 10 km are left to that site",
                "civHint = the authored civilization that existed for most of the place's life, preferring one "
                "with a real name pool and a nearer capital (worldfill/build_places.py Civs.pick)"],
            "rejected": ["Unlocated places", "Undated places", "Places attested only after AD 640",
                         "Rivers, mountains, regions, roads, tombs and other non-dwelling features",
                         "Treating a Pleiades period boundary as a real founding or abandonment"],
            "sites": ple},
        "places_chgis.json.gz": {
            "id": "chgis_county_seats",
            "title": "County-level seats of China, 763 BC - AD 1911, from CHGIS V6 time-series points; each "
                     "record is one seat under one name and status for its begin..end years.",
            "source": "CHGIS, Version 6. Fairbank Center for Chinese Studies, Harvard University, and Center "
                      "for Historical Geographical Studies, Fudan University, 2016. County points: "
                      "doi:10.7910/DVN/Q9VOF5, CC0 1.0.",
            "spawnRadiusKm": 25,
            "estimatorAnchor": False,
            "comparedSources": [
                "occupiedEnd: a seat still standing when the series ends in 1911 stays open to the present",
                "Rank town for every county-level seat",
                "civHint = the authored dynasty of the record's years (Zhou, Qin, Han, Tang, Song, Jin, "
                "Western Xia, Yuan as mongol_empire, Ming, Qing)"],
            "rejected": ["CHGIS prefecture points (separate EULA)", "Rows without coordinates or years"],
            "sites": chg},
        "places_reba.json.gz": {
            "id": "reba_cities",
            "title": "Cities with recorded populations, 3700 BC - AD 2000 (Reba, Reitsma & Seto 2016): each "
                     "city occupied from its first recorded population to the next survey year after its last.",
            "source": "Reba, M., Reitsma, F. & Seto, K. Spatializing 6,000 years of global urbanization from "
                      "3700 BC to AD 2000. Scientific Data 3, 160034 (2016). figshare 2059494, 2059497, "
                      "2059500, CC BY 4.0.",
            "spawnRadiusKm": 30,
            "estimatorAnchor": False,
            "comparedSources": [
                "Chandler (2250 BC - AD 1975), Modelski ancient (3700 BC - AD 1000) and Modelski modern (AD 2000) "
                "merged when within 15 km and sharing a name word, or within 3 km",
                "Years up to AD 640 that a Pleiades place within 5 km covers are left to Pleiades (ancient name "
                "in antiquity, modern name after)",
                "Years a curated region-pack site covers within 10 km are left to that site",
                "A city's life is split at AD 641 and 1500; each piece has the civHint of its own era"],
            "rejected": ["Dropping out of a largest-cities list read as abandonment beyond the next survey year"],
            "sites": reb},
    }

    report = {"stats": {k: dict(v) for k, v in stats.items()},
              "sites": {p: len(d["sites"]) for p, d in packs.items()},
              "rank": {p: dict(collections.Counter(s["rank"] for s in d["sites"])) for p, d in packs.items()},
              "civHint_top": {p: collections.Counter(s["civHint"] for s in d["sites"]).most_common(12)
                              for p, d in packs.items()},
              "span": {p: [min(s["occupiedStart"] for s in d["sites"]),
                           max(s["occupiedEnd"] for s in d["sites"])] for p, d in packs.items()}}
    json.dump(report, open(REPORT, "w"), indent=1, ensure_ascii=False)
    print(json.dumps(report, indent=1, ensure_ascii=False))
    if dry:
        return packs
    prev = "afro_islamic.json"
    for p, d in packs.items():
        M.write_pack(p, d)
        M.register(p, after=prev)
        prev = p
    print("installed:", list(packs))
    return packs


if __name__ == "__main__":
    main(dry="--dry-run" in sys.argv)
