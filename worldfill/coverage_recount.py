#!/usr/bin/env python3
"""Recount "how much of the open data the mod has" after step 5 (the <50% plan).

For each open source record (NOAA quakes / tsunamis / volcanoes, Smithsonian eruptions, plague
outbreaks), it counts as covered when an installed event of a compatible kind is within 150 km
(30 km for plague) and one year. Wikipedia year-page and list-page coverage comes from the
build reports. Writes worldfill/coverage_after.json.
"""
import collections, gzip, json, math, os, re, sys

sys.path.insert(0, "/home/user/worldfill")
import modpack as M  # noqa: E402

SRC = os.path.expanduser("~/.cache/srcdata")
OUT = "/home/user/worldfill/coverage_after.json"
QUAKE = re.compile(r"earthquake|quake|tremor", re.I)
VOLC = re.compile(r"volcan|erupt", re.I)
TSU = re.compile(r"tsunami", re.I)
PLAGUE = re.compile(r"plague|pestilence|black death|epidemic|pandemic", re.I)


def cls(e):
    k, n = (e.get("kind") or "").lower(), e.get("name") or ""
    out = set()
    if k == "earthquake" or QUAKE.search(n):
        out.add("earthquake")
    if k == "volcano" or VOLC.search(n):
        out.add("volcano")
    if k == "tsunami" or TSU.search(n):
        out.add("tsunami")
    if k in ("plague", "epidemic", "pandemic") or PLAGUE.search(n):
        out.add("plague")
    return out


def hav(a, b, c, d):
    p1, p2 = math.radians(a), math.radians(c)
    x = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(d - b) / 2) ** 2
    return 2 * 6371 * math.asin(min(1, math.sqrt(x)))


def main():
    evs = M.existing_events()
    idx = collections.defaultdict(list)          # (class, year) -> [(lat, lon, radius)]
    for e in evs:
        cs = cls(e)
        if not cs:
            continue
        s, en = int(e["_start"]), int(e.get("end", e["_start"] + 1))
        for c in cs:
            for y in range(s - 1, min(en, s + 6) + 1):
                idx[(c, y)].append((e["lat"], e["lon"], float(e.get("radiusKm", 20))))

    def covered(c, y, la, lo, km):
        for a, b, r in idx.get((c, y), ()):
            if abs(a - la) <= (max(km, r) / 111.0) + 0.01 and hav(la, lo, a, b) <= max(km, r if r > 60 else 0):
                return True
        return False

    res = {}
    for name, fn, c in (("NOAA earthquakes", "ncei_quakes.json", "earthquake"),
                        ("NOAA tsunamis", "ncei_tsunamis.json", "tsunami"),
                        ("NOAA volcanic eruptions", "ncei_volcanoes.json", "volcano")):
        items = json.load(open(os.path.join(SRC, fn)))
        n = h = 0
        for it in items:
            y, la, lo = it.get("year"), it.get("latitude"), it.get("longitude")
            if isinstance(y, int) and la is not None and lo is not None and -3000 <= y <= 2026:
                n += 1
                h += covered(c, y, float(la), float(lo), 150)
        res[name] = (h, n)
    g = json.load(open(os.path.join(SRC, "gvp_eruptions.json")))
    n = h = 0
    for f in g["features"]:
        p, co = f["properties"], (f.get("geometry") or {}).get("coordinates") or [None, None]
        y = p.get("StartDateYear")
        if isinstance(y, int) and co[0] is not None and -3000 <= y <= 2026:
            n += 1
            h += covered("volcano", y, float(co[1]), float(co[0]), 150)
    res["Smithsonian eruptions"] = (h, n)
    txt = open(os.path.join(SRC, "plague/europe-pnas/resources/plague-db-europe.txt"), encoding="utf-8").read()
    n = h = 0
    for m in re.finditer(r'\{:lat ([-\d.]+), :lon ([-\d.]+), :name "(?:[^"\\]|\\.)*", :source "(?:[^"\\]|\\.)*", :year (-?\d+)\}', txt):
        y = int(m.group(3))
        if -3000 <= y <= 2026:
            n += 1
            h += covered("plague", y, float(m.group(1)), float(m.group(2)), 30)
    res["Plague outbreaks (Biraben)"] = (h, n)
    kinds = collections.Counter((e.get("kind") or "?") for e in evs)
    conf = collections.Counter((e.get("confidence") or "?") for e in evs)
    out = {"events_total": len(evs), "by_kind": dict(kinds.most_common()), "by_confidence": dict(conf.most_common()),
           "source_coverage": {k: {"covered": a, "records": b, "pct": round(100 * a / b, 1) if b else None}
                               for k, (a, b) in res.items()}}
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
