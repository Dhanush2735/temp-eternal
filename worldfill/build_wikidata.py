#!/usr/bin/env python3
"""Step 3a: the Wikidata battles, sieges, treaties and wars the mod does not have yet.

The survey (survey/sources/wikidata_eras.py -> wikidata_items.json.gz) found, for 3000 BC - AD
2026, battles, sieges, treaties and wars that are dated and can be placed, but are missing from
events_world.json. Most have no coordinates of their own: they are placed through P276
(location), which is only trusted when the location is a specific place (a town, a fort, a
river crossing), not a country, a sea or a whole region.

Writes events_wikidata_more.json into the mod (registered after events_world.json):

  battle / siege   one pin per item; own P625, else the P625 of a specific P276 location
                   (confidence "wikidata" or "wikidata_location"); start = P580/P585 year,
                   end = P582 year + 1 (at most 10 years), else start + 1
  treaty           one pin at the place of signing (P625, else a specific P276), one year
  war              a theatre pin per cluster of the war's own battles (P361 "part of" the war,
                   located battles only, clusters of battles within 800 km of each other);
                   centred on the cluster, radius = farthest battle + 25 km (60..300 km),
                   years = the years of that cluster's battles, inside the war's P580..P582.
                   A war with no located battles gets no pin: no guessing a theatre from a
                   country's centre.

Usage: python3 build_wikidata.py [--dry-run]     (queries are cached in ~/.cache/wd_cache)
"""
import collections, gzip, hashlib, json, math, os, re, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modpack as M        # noqa: E402

UA = "EternalEngineWorldFill/1.0 (historical data build; research use)"
CACHE = "/home/user/.cache/wd_cache"
ITEMS = "/home/user/survey/sources/wikidata_items.json.gz"
PACK = "events_wikidata_more.json.gz"   # gzipped; HistoryGazetteer reads .gz packs
REPORT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_wikidata_report.json")
FIRST, LAST = -3000, 2026

# a P276 location is too coarse to place a battle if it is one of these (or bigger than 20,000 km2)
COARSE = {   # labels checked against Wikidata 2026-10-11
    "Q6256",      # country
    "Q3624078",   # sovereign state
    "Q3024240",   # historical country
    "Q7275",      # state
    "Q48349",     # empire
    "Q417175",    # kingdom
    "Q1250464",   # realm
    "Q5107",      # continent
    "Q9430",      # ocean
    "Q165",       # sea
    "Q33837",     # archipelago
    "Q82794",     # region
    "Q1620908",   # historical region
    "Q34876",     # province
    "Q10864048",  # first-level administrative division
    "Q35657",     # U.S. state
    "Q107390",    # federated state
    "Q1763527",   # constituent country
    "Q28575",     # county
    "Q47168",     # county of the United States
    "Q11828004",  # province of Canada
    "Q16110",     # region of Italy
    "Q6465",      # department of France
    "Q2577883",   # occupied territory
    "Q161243",    # dependent territory
    "Q46395",     # British Overseas Territories
    "Q1335818",   # supranational union
    "Q19953632",  # former administrative territorial entity
    "Q4022",      # river (its single coordinate can be far from where the fighting was)
}
MAX_AREA_M2 = 2.0e10


def sparql(q, tries=6):
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.sha1(q.encode()).hexdigest()
    path = f"{CACHE}/{key}.json"
    if os.path.exists(path):
        return json.load(open(path))
    for i in range(tries):
        r = subprocess.run(["curl", "-s", "-G", "--max-time", "300", "-A", UA,
                            "-H", "Accept: application/sparql-results+json",
                            "--data-urlencode", "query=" + q, "https://query.wikidata.org/sparql"],
                           capture_output=True, text=True)       # GET: WDQS 429s POST from this client
        try:
            rows = json.loads(r.stdout)["results"]["bindings"]
            json.dump(rows, open(path, "w"))
            time.sleep(1.0)
            return rows
        except Exception:
            print("   retry", i, r.stdout[:120].replace("\n", " "), file=sys.stderr, flush=True)
            time.sleep(15 * (i + 1))
    raise RuntimeError("WDQS query failed")


def wd_year(v):
    """xsd:dateTime from WDQS (astronomical years: 0 = 1 BC) -> historical year, no year 0."""
    s = v.strip()
    neg = s.startswith("-")
    y = int(s.lstrip("-").split("-")[0])
    return -(y + 1) if neg else (y if y != 0 else -1)


def point(v):
    m = re.match(r"Point\(([-\d.eE]+) ([-\d.eE]+)\)", v or "")
    if not m:
        return None
    lon, lat = float(m.group(1)), float(m.group(2))
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return round(lat, 5), round(lon, 5)


def qid(v):
    return v.rsplit("/", 1)[-1]


def details(qids, stats, label):
    """label, own P625, dates, P276 locations (with coordinates, classes, area), P361 parents."""
    out = {}
    qids = sorted(set(qids))
    for i in range(0, len(qids), 150):
        chunk = qids[i:i + 150]
        q = ("SELECT ?x ?xl ?own ?d585 ?d580 ?d582 ?loc ?lc ?lt ?area ?part WHERE { VALUES ?x { %s } "
             "OPTIONAL { ?x rdfs:label ?xl FILTER(LANG(?xl)='en') } "
             "OPTIONAL { ?x wdt:P625 ?own } OPTIONAL { ?x wdt:P585 ?d585 } "
             "OPTIONAL { ?x wdt:P580 ?d580 } OPTIONAL { ?x wdt:P582 ?d582 } "
             "OPTIONAL { ?x wdt:P276 ?loc . ?loc wdt:P625 ?lc . OPTIONAL { ?loc wdt:P31 ?lt } "
             "  OPTIONAL { ?loc p:P2046/psn:P2046/wikibase:quantityAmount ?area } } "
             "OPTIONAL { ?x wdt:P361 ?part } }" % " ".join("wd:" + x for x in chunk))
        for b in sparql(q):
            x = qid(b["x"]["value"])
            d = out.setdefault(x, {"label": None, "own": None, "dates": collections.defaultdict(list),
                                   "locs": {}, "parts": set()})
            if "xl" in b:
                d["label"] = b["xl"]["value"]
            if "own" in b and d["own"] is None:
                d["own"] = point(b["own"]["value"])
            for k in ("d585", "d580", "d582"):
                if k in b and b[k]["value"][:1] in "-0123456789":
                    try:
                        d["dates"][k].append(wd_year(b[k]["value"]))
                    except ValueError:
                        pass
            if "loc" in b:
                L = d["locs"].setdefault(qid(b["loc"]["value"]), {"c": point(b["lc"]["value"]), "types": set(), "area": None})
                if "lt" in b:
                    L["types"].add(qid(b["lt"]["value"]))
                if "area" in b:
                    try:
                        L["area"] = max(L["area"] or 0, float(b["area"]["value"]))
                    except ValueError:
                        pass
            if "part" in b:
                d["parts"].add(qid(b["part"]["value"]))
        stats[label + "_queries"] += 1
        print(f"  {label}: {min(i + 150, len(qids))}/{len(qids)}", flush=True)
    return out


def years(d):
    starts = d["dates"].get("d580", []) + d["dates"].get("d585", [])
    if not starts:
        return None, None
    s = min(starts)
    ends = [e for e in d["dates"].get("d582", []) if e >= s]
    e = max(ends) + 1 if ends else s + 1
    if s == 0:
        s = 1
    return s, max(e, s + 1)


def place(d, stats, label):
    """Own coordinates, else a specific P276 location; returns (lat, lon, how)."""
    if d["own"]:
        return d["own"][0], d["own"][1], "wikidata"
    good = []
    for L in d["locs"].values():
        if not L["c"]:
            continue
        if L["types"] & COARSE or (L["area"] or 0) > MAX_AREA_M2:
            stats[label + "_location_too_coarse"] += 1
            continue
        good.append(L["c"])
    if not good:
        return None
    if len(good) > 1:      # several specific places: use them only if they agree within 100 km
        la = sum(g[0] for g in good) / len(good)
        lo = sum(g[1] for g in good) / len(good)
        if max(M.haversine_km(la, lo, g[0], g[1]) for g in good) > 100:
            stats[label + "_locations_disagree"] += 1
            return None
        return round(la, 5), round(lo, 5), "wikidata_location"
    return good[0][0], good[0][1], "wikidata_location"


def cluster(points, km=800):
    """Greedy single-link clusters of (lat, lon, start, end, qid)."""
    groups = []
    for p in points:
        hit = [g for g in groups if any(M.haversine_km(p[0], p[1], q[0], q[1]) <= km for q in g)]
        if not hit:
            groups.append([p]); continue
        merged = [p]
        for g in hit:
            merged += g
            groups.remove(g)
        groups.append(merged)
    return groups


def main(dry=False):
    stats = collections.Counter()
    survey = json.load(gzip.open(ITEMS, "rt"))
    existing = M.existing_events(exclude={PACK})
    have = {e["id"].upper() for e in existing if re.fullmatch(r"q\d+", str(e.get("id", "")))}
    stats["qids_already_in_mod"] = len(have)

    new = {}
    for key, kind in (("battle", "battle"), ("siege", "siege"), ("treaty (by label, as survey)", "treaty"), ("war", "war")):
        for q, y, own in survey[key]:
            if q not in have and FIRST <= y <= LAST:
                new.setdefault(q, kind)
    by_kind = collections.Counter(new.values())
    stats.update({f"survey_new_{k}": v for k, v in by_kind.items()})
    print("new items from the survey:", dict(by_kind), flush=True)

    info = details(list(new), stats, "items")
    events, wars = [], {}
    for q, kind in sorted(new.items()):
        d = info.get(q)
        if not d:
            stats[kind + "_not_returned"] += 1; continue
        if kind == "war":
            wars[q] = d; continue
        if not d["label"] or re.fullmatch(r"Q\d+", d["label"]):
            stats[kind + "_no_english_label"] += 1; continue
        s, e = years(d)
        if s is None or not (FIRST <= s <= LAST):
            stats[kind + "_undated_or_outside"] += 1; continue
        pl = place(d, stats, kind)
        if not pl:
            stats[kind + "_not_placeable"] += 1; continue
        la, lo, how = pl
        e = min(e, s + 10)
        events.append({"id": q.lower(), "name": d["label"], "start": s, "end": e, "lat": la, "lon": lo,
                       "radiusKm": 20 if kind in ("battle", "siege") else 10, "kind": kind,
                       "effect": "military_presence" if kind in ("battle", "siege") else "political",
                       "confidence": how})
        stats[kind + "_kept"] += 1
        stats[kind + "_kept_" + how] += 1

    # ---- war theatres from each war's own located battles
    located = {e["id"].upper(): e for e in existing + events if e.get("kind") in ("battle", "siege")}
    war_ids = sorted(wars)
    battles_of = collections.defaultdict(set)
    for i in range(0, len(war_ids), 100):
        chunk = war_ids[i:i + 100]
        q = ("SELECT ?w ?b WHERE { VALUES ?w { %s } ?b wdt:P361 ?w . }" % " ".join("wd:" + x for x in chunk))
        for b in sparql(q):
            battles_of[qid(b["w"]["value"])].add(qid(b["b"]["value"]))
    for w in war_ids:
        d = wars[w]
        if not d["label"] or re.fullmatch(r"Q\d+", d["label"]):
            stats["war_no_english_label"] += 1; continue
        pts = [(located[b]["lat"], located[b]["lon"], located[b]["_start"] if "_start" in located[b] else located[b]["start"],
                located[b].get("end", located[b]["start"] + 1), b) for b in battles_of.get(w, ()) if b in located]
        if not pts:
            stats["war_no_located_battles"] += 1; continue
        s, e = years(d)
        groups = [g for g in cluster(pts) if len(g) >= 2] or ([max(cluster(pts), key=len)] if len(pts) >= 1 else [])
        multi = len(groups) > 1
        for j, g in enumerate(sorted(groups, key=len, reverse=True)):
            la = sum(p[0] for p in g) / len(g)
            lo = sum(p[1] for p in g) / len(g)
            r = max(M.haversine_km(la, lo, p[0], p[1]) for p in g) + 25
            gs, ge = min(p[2] for p in g), max(p[3] for p in g)
            # The theatre lasts while its own battles were fought, inside the war's years: a war
            # recorded as 1337..1453 is not a 116-year standing overlay where no battle is known.
            ws, we = (max(s, gs), min(e, ge)) if s is not None else (gs, ge)
            if we <= ws:
                ws, we = gs, ge
            if not (FIRST <= ws <= LAST):
                stats["war_undated_or_outside"] += 1; break
            we = max(we, ws + 1)
            events.append({"id": f"{w.lower()}_t{j + 1}" if multi else w.lower(),
                           "name": d["label"] + (f" (theatre {j + 1} of {len(groups)})" if multi else ""),
                           "start": ws, "end": we, "lat": round(la, 5), "lon": round(lo, 5),
                           "radiusKm": int(min(300, max(60, round(r)))), "kind": "war",
                           "effect": "military_presence", "confidence": "wikidata_battles",
                           "battles": len(g)})
            stats["war_theatres_kept"] += 1
        stats["war_kept"] += 1

    for e in events:
        M.check_event(e)
    ids = collections.Counter(e["id"] for e in events)
    assert not [i for i, n in ids.items() if n > 1], "duplicate ids"

    doc = {
        "id": "wikidata_events_more",
        "title": "More Wikidata events: battles, sieges, treaties and war theatres missing from events_world.json "
                 "(3000 BC - AD 2026). Overlay only. Not towns. Not attacker spawn.",
        "source": "Wikidata (CC0), queried 2026-10-11 through query.wikidata.org",
        "comparedSources": [
            "Battle Q178561, siege Q188055, treaty (class label 'treaty'), war Q198, as counted in "
            "survey/OTHER_SOURCES_CENSUS.md",
            "Placed by own P625 (confidence wikidata) or by a specific P276 location (wikidata_location); "
            "countries, seas, regions and places over 20,000 km2 are never used as a location",
            "War = one pin per cluster of its own located battles (P361), radius = farthest battle + 25 km "
            "(60..300), years = the years of that cluster's battles within the war's P580..P582"],
        "rejected": ["Items already in events_world.json (same QID)", "Items without an English label",
                     "Placing an event at a country's or region's centre",
                     "Inventing a war theatre for a war with no located battles"],
        "events": events,
    }
    report = {"stats": dict(sorted(stats.items())),
              "events": len(events), "by_kind": dict(collections.Counter(e["kind"] for e in events)),
              "by_confidence": dict(collections.Counter(e["confidence"] for e in events)),
              "by_era": dict(collections.Counter(
                  ("3000-1001 BC" if e["start"] <= -1001 else "1000-1 BC" if e["start"] < 0 else
                   "AD 1-999" if e["start"] < 1000 else "1000-1499" if e["start"] < 1500 else
                   "1500-1799" if e["start"] < 1800 else "1800-2026") for e in events))}
    json.dump(report, open(REPORT, "w"), indent=1)
    print(json.dumps(report, indent=1), flush=True)
    if dry:
        return doc
    M.write_pack(PACK, doc)
    M.register(PACK, after="events_world.json")
    print("installed", PACK, len(events))
    return doc


if __name__ == "__main__":
    main(dry="--dry-run" in sys.argv)
