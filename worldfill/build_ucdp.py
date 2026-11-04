#!/usr/bin/env python3
"""Step 6.1: UCDP GED 25.1 -> events_ucdp.json.gz (local fighting spots, 1989-2024).

Every death-causing event UCDP recorded from 1989 to 2024 (385,918 rows) is grouped into local
fighting spots: one pin per conflict, year and province (adm_1). A pin sits at the death-weighted
centre of that year's events in that province, and its radius reaches 90% of them (each point
padded by how precisely UCDP knows where it happened).

Rules:
  * where_prec 6 (only the country is known) and 7 (international waters or airspace) are left
    out: their coordinates are a country centre, not a place anyone fought. The country-wide
    picture is already there as regional war news (events_wars.json.gz).
  * kind "conflict" is not in InWorldInterventionDetector.STOPPABLE_KINDS, so a player can never
    'stop' a modern war from one spot.
  * effect: violence against civilians (UCDP type 3) -> "lockdown" (stay off the streets);
    otherwise "military_presence" (soldiers on the roads). News only, never an attack script.
  * Names use UCDP's own actor names.

Source: UCDP Georeferenced Event Dataset (GED) Global version 25.1, CC BY 4.0.
Sundberg & Melander 2013, J. Peace Research 50(4); Davies, Pettersson & Oberg 2025.

    python3 build_ucdp.py --dry     # statistics only
    python3 build_ucdp.py           # write the pack and register it in index.json
"""
import bisect, collections, csv, hashlib, io, json, math, os, re, sys, zipfile

sys.path.insert(0, "/home/user/worldfill")
import modpack as M  # noqa: E402

SRC = os.path.expanduser("~/.cache/srcdata/ged251-csv.zip")
PACK = "events_ucdp.json.gz"
REPORT = "/home/user/worldfill/ucdp_report.json"
# How far from its coordinates an event may really be, by UCDP where_prec.
UNCERTAINTY_KM = {1: 5, 2: 25, 3: 50, 4: 100, 5: 50}
TYPE_WORD = {1: "state-based", 2: "non-state", 3: "one-sided"}


def clean_country(c):
    """'DR Congo (Zaire)' -> 'DR Congo'; UCDP keeps old names in brackets."""
    return re.sub(r"\s*\(.*?\)", "", c or "").strip()


def centre(points):
    """Death-weighted centre; longitudes are unwrapped around the first point."""
    lon0 = points[0][1]
    sw = slat = slon = 0.0
    for la, lo, w, _p in points:
        d = lo - lon0
        if d > 180:
            lo -= 360
        elif d < -180:
            lo += 360
        sw += w
        slat += la * w
        slon += lo * w
    la, lo = slat / sw, slon / sw
    if lo < -180:
        lo += 360
    elif lo >= 180:
        lo -= 360
    return la, lo


def weighted_quantile(values, weights, q):
    pairs = sorted(zip(values, weights))
    total = sum(weights)
    acc = 0.0
    for v, w in pairs:
        acc += w
        if acc >= q * total:
            return v
    return pairs[-1][0]


def place_words(place, country):
    if not place or place == country:
        return country
    return f"{place}, {country}"


def name_of(t, place, country, dyads, deaths):
    (side_a, side_b), _ = dyads.most_common(1)[0]
    where = place_words(place, country)
    if t == 3:
        text = f"Attacks on civilians in {where} by {side_a}"
    elif t == 2:
        text = f"Clashes in {where}: {side_a} against {side_b}"
    else:
        text = f"Fighting in {where}: {side_a} against {side_b}"
    if len(dyads) > 1 and t != 3:
        text += " and others"
    if deaths >= 2:
        text += f", about {deaths:,} killed this year"
    elif deaths == 1:
        text += ", 1 killed this year"
    return text


def main(dry=False):
    z = zipfile.ZipFile(SRC)
    csv_name = [n for n in z.namelist() if n.endswith(".csv")][0]
    groups = {}
    st = collections.Counter()
    with z.open(csv_name) as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding="utf-8")):
            st["rows"] += 1
            best = int(r["best"] or 0)
            st["deaths_all"] += best
            prec = int(r["where_prec"] or 9)
            if prec >= 6:
                st["left_out_country_or_sea_only"] += 1
                st["deaths_left_out"] += best
                continue
            t = int(r["type_of_violence"])
            country = clean_country(r["country"])
            place = (r["adm_1"] or "").strip() or (r["where_coordinates"] or "").strip() or country
            key = (t, r["conflict_new_id"], int(r["year"]), country, place)
            g = groups.get(key)
            if g is None:
                g = groups[key] = {"pts": [], "dyads": collections.Counter(), "deaths": 0,
                                   "conflict": r["conflict_name"]}
            g["pts"].append((float(r["latitude"]), float(r["longitude"]), max(best, 1), prec))
            g["dyads"][(r["side_a"].strip(), r["side_b"].strip())] += max(best, 1)
            g["deaths"] += best
    events, seen = [], set()
    by_type, by_decade = collections.Counter(), collections.Counter()
    radii = []
    for (t, cid, year, country, place), g in groups.items():
        la, lo = centre(g["pts"])
        reach = [M.haversine_km(la, lo, p[0], p[1]) + UNCERTAINTY_KM[p[3]] for p in g["pts"]]
        radius = weighted_quantile(reach, [p[2] for p in g["pts"]], 0.9)
        radius = int(round(min(200.0, max(15.0, radius))))
        h = hashlib.md5(repr((t, cid, year, country, place)).encode()).hexdigest()[:8]
        eid = f"ucdp_{year}_{M.slug(place, 24)}_{h}"
        assert eid not in seen
        seen.add(eid)
        e = {"id": eid, "name": name_of(t, place, country, g["dyads"], g["deaths"]),
             "start": year, "end": year + 1, "lat": round(la, 4), "lon": round(lo, 4),
             "radiusKm": radius, "kind": "conflict",
             "effect": "lockdown" if t == 3 else "military_presence",
             "confidence": "ucdp_ged"}
        M.check_event(e)
        events.append(e)
        by_type[TYPE_WORD[t]] += 1
        by_decade[f"{year // 10 * 10}s"] += 1
        radii.append(radius)
    events.sort(key=lambda e: (e["start"], e["id"]))
    radii.sort()
    rep = {
        "source": "UCDP GED Global v25.1 (CC BY 4.0), " + csv_name,
        "rows": st["rows"],
        "rows_left_out_country_or_sea_only": st["left_out_country_or_sea_only"],
        "deaths_all": st["deaths_all"],
        "deaths_in_pins": st["deaths_all"] - st["deaths_left_out"],
        "pins": len(events),
        "pins_by_type": dict(by_type),
        "pins_by_decade": dict(sorted(by_decade.items())),
        "radius_km_median": radii[len(radii) // 2],
        "radius_km_p90": radii[int(len(radii) * 0.9)],
        "examples": [e["name"] for e in events[:: max(1, len(events) // 12)]][:12],
    }
    print(json.dumps(rep, ensure_ascii=False, indent=1))
    if dry:
        return
    doc = {
        "id": "ucdp_ged",
        "title": ("Modern conflicts 1989-2024 from the UCDP Georeferenced Event Dataset 25.1: one "
                  "local pin per conflict, year and province, at the death-weighted centre of that "
                  "year's events. Kind 'conflict' is never stoppable; news only, never attackers."),
        "source": "worldfill/build_ucdp.py; UCDP GED v25.1, CC BY 4.0 (ucdp.uu.se)",
        "sites": [],
        "events": events,
    }
    path = M.write_pack(PACK, doc)
    M.register(PACK, after="events_wars.json.gz")
    rep["pack_bytes"] = os.path.getsize(path)
    json.dump(rep, open(REPORT, "w"), ensure_ascii=False, indent=1)
    print(f"wrote {path} ({rep['pack_bytes'] / 1e6:.2f} MB), registered in index.json")


if __name__ == "__main__":
    main(dry="--dry" in sys.argv)
