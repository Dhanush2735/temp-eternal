#!/usr/bin/env python3
"""events_raw.jsonl -> events_wikipedia.json in the Eternal Engine history schema.

Matches the shape of history/events_world.json so FoundationDataLoader /
HistoricalEventDatabase.loadFromFiles() can read it unchanged:
    { "events": [ {id,name,start,end,lat,lon,radiusKm,kind,effect,confidence}, ... ] }
Dedupes on (name, start, rounded coords). Assigns stable ids.
"""
import json, sys, collections, hashlib, os

EFFECT = {
    "battle":    "military_presence",
    "siege":     "military_presence",
    "treaty":    "political",
    "political": "political",
    "disaster":  "disruption",
    "incident":  "note",
}

def main(src, dst):
    seen, out = set(), []
    stats = collections.Counter()
    for line in open(src, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        stats["raw"] += 1
        name = r.get("name", "").strip()
        if len(name) < 12 or len(name) > 400:
            stats["drop_length"] += 1; continue
        lat, lon = r.get("lat"), r.get("lon")
        if lat is None or lon is None:
            stats["drop_nocoord"] += 1; continue
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            stats["drop_badcoord"] += 1; continue
        start = r.get("start")
        if not isinstance(start, int) or start < -10000 or start > 2100:
            stats["drop_year"] += 1; continue
        key = (name.lower()[:120], start, round(lat, 1), round(lon, 1))
        if key in seen:
            stats["drop_dupe"] += 1; continue
        seen.add(key)
        kind = r.get("kind", "incident")
        h = hashlib.sha1(f"{name}|{start}|{lat}|{lon}".encode()).hexdigest()[:10]
        out.append({
            "id":         f"wpy_{h}",
            "name":       name,
            "start":      start,
            "end":        r.get("end", start),
            "lat":        round(lat, 5),
            "lon":        round(lon, 5),
            "radiusKm":   int(r.get("radiusKm", 20)),
            "kind":       kind,
            "effect":     EFFECT.get(kind, "note"),
            "confidence": r.get("confidence", "wikipedia_year_page"),
        })
        stats["kept"] += 1
    out.sort(key=lambda e: e["start"])
    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        json.dump({"events": out}, f, ensure_ascii=False, indent=1)
    print(json.dumps(stats, indent=2))
    print(f"\nwrote {len(out)} events -> {dst}  ({os.path.getsize(dst)/1e6:.1f} MB)")
    return out

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/home/user/harvest/events_raw.jsonl",
         sys.argv[2] if len(sys.argv) > 2 else "/home/user/harvest/events_wikipedia.json")
