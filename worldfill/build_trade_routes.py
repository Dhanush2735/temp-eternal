import io
#!/usr/bin/env python3
"""Step 7.4: roads and trade routes -> history/trade_routes.json.gz.

Two sources:
  * Itiner-e (de Soto, Pazout, Brughmans et al. 2025, Sci Data 12:1731; Zenodo
    doi:10.5281/zenodo.17122148, CC BY 4.0): 14,769 Roman road segments, each named after the two
    places it joins ("Tingi-Tamuda"), main or secondary. Geometry is World Mercator (EPSG:3395)
    metres; turned into lat/lon here and simplified to about 1 km (Douglas-Peucker), which is plenty
    for "a Roman road runs through here".
    Years: the segment's own construction period or date where Itiner-e gives one ("Claudius (46
    CE)", "Manius Aquilius (129-126 BCE)"); otherwise the Roman era, from 100 BC. A road is in use
    until its own end date, else AD 500; after that the mod calls it an old Roman road (to 1500).
  * Wikipedia trade-route articles (dump 2026-10-01, CC BY-SA 4.0): each route's towns are the
    settlements the article links in its route sections; its years come from the article's lead.
    The mod says "Merchants on the Silk Road pass through here" within 30 km of such a town.

    python3 build_trade_routes.py roads    # Itiner-e only
    python3 build_trade_routes.py          # both
"""
import collections, gzip, json, math, os, re, sys

sys.path.insert(0, "/home/user/worldfill")
import modpack as M  # noqa: E402

ITINERE = os.path.expanduser("~/.cache/srcdata/itinere/itinere_roads.geojson")
OUT = f"{M.HISTORY}/trade_routes.json.gz"
ROADS_CACHE = os.path.expanduser("~/.cache/srcdata/itinere/roads_simplified.json")
REPORT = "/home/user/worldfill/trade_routes_report.json"
A, E = 6378137.0, 0.0818191908426215
TOL_DEG = 0.01


def merc3395_inverse(x, y):
    lon = math.degrees(x / A)
    t = math.exp(-y / A)
    phi = math.pi / 2 - 2 * math.atan(t)
    for _ in range(8):
        es = E * math.sin(phi)
        phi = math.pi / 2 - 2 * math.atan(t * ((1 - es) / (1 + es)) ** (E / 2))
    return math.degrees(phi), lon


def merc3395_forward(lat, lon):
    phi = math.radians(lat)
    es = E * math.sin(phi)
    return A * math.radians(lon), A * math.log(math.tan(math.pi / 4 + phi / 2) * ((1 - es) / (1 + es)) ** (E / 2))


def simplify(pts, tol):
    """Douglas-Peucker on (lat, lon) with longitude scaled by cos(lat)."""
    if len(pts) <= 2:
        return pts
    k = math.cos(math.radians(sum(p[0] for p in pts) / len(pts)))
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        ax, ay = pts[a][1] * k, pts[a][0]
        bx, by = pts[b][1] * k, pts[b][0]
        dx, dy = bx - ax, by - ay
        L = dx * dx + dy * dy
        best, bi = -1.0, -1
        for i in range(a + 1, b):
            px, py = pts[i][1] * k, pts[i][0]
            if L == 0:
                d = math.hypot(px - ax, py - ay)
            else:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
                d = math.hypot(px - (ax + t * dx), py - (ay + t * dy))
            if d > best:
                best, bi = d, i
        if best > tol:
            keep[bi] = True
            stack += [(a, bi), (bi, b)]
    return [p for p, kp in zip(pts, keep) if kp]


def year_of(text):
    """'Claudius (46 CE)' -> 46; 'Manius Aquilius (129-126 BCE)' -> -129; None if no year."""
    if not text:
        return None
    m = re.search(r"(\d{1,4})(?:\s*[-–]\s*\d{1,4})?\s*(BCE|BC|CE|AD)?", text)
    if not m:
        return None
    y = int(m.group(1))
    return -y if (m.group(2) or "").upper() in ("BCE", "BC") else y


def roads():
    out, st = [], collections.Counter()
    with open(ITINERE, encoding="utf-8") as f:
        for line in f:
            line = line.strip().rstrip(",")
            if not line.startswith('{ "type": "Feature"'):
                continue
            ft = json.loads(line)
            p = ft["properties"]
            start = year_of(p.get("Cons_per_e"))
            how = "construction"
            if start is None and p.get("Lower_Date") not in (None, 9999.0):
                start, how = int(p["Lower_Date"]), "dated"
            if start is None:
                start, how = -100, "roman_era"
            end = int(p["Upper_Date"]) if p.get("Upper_Date") not in (None, 9999.0) else 500
            if end <= start:
                end = max(start + 1, 500)
            main = 1 if p.get("Type") == "Main Road" else 0
            name = (p.get("Name") or "").strip()
            for part in ft["geometry"]["coordinates"]:
                pts = [merc3395_inverse(c[0], c[1]) for c in part]
                s = simplify(pts, TOL_DEG)
                flat = []
                for la, lo in s:
                    flat += [round(la, 3), round(lo, 3)]
                if len(flat) >= 4:
                    out.append([name, main, start, end, flat])
                    st["parts"] += 1
                    st["points_in"] += len(pts)
                    st["points_out"] += len(s)
            st[how] += 1
            st["main" if main else "secondary"] += 1
    return out, st


def main(which="all"):
    for la, lo in ((41.9, 12.5), (51.5, -0.1), (30.0, 31.2)):
        b = merc3395_inverse(*merc3395_forward(la, lo))
        assert abs(b[0] - la) < 1e-7 and abs(b[1] - lo) < 1e-7
    rd, st = roads()
    json.dump(rd, open(ROADS_CACHE, "w"))
    rep = {"roads": dict(st)}
    routes = []
    if which != "roads":
        import build_wiki_routes as WR
        routes, rst = WR.routes()
        rep["routes"] = rst
    doc = {"format": 1,
           "source": ("Itiner-e (de Soto et al. 2025, Sci Data 12:1731; Zenodo doi:10.5281/zenodo.17122148; CC BY 4.0) "
                      "roads, simplified to ~1 km; Wikipedia trade-route articles (dump 2026-10-01, CC BY-SA 4.0) for route "
                      "towns. worldfill/build_trade_routes.py"),
           "note": ("roads: [name, main(1)/secondary(0), firstYear, lastYear, [lat, lon, lat, lon, ...]]; "
                    "routes: {name, start, end, kind, towns: [[name, lat, lon], ...]}"),
           "roads": rd, "routes": routes}
    with open(OUT + ".tmp", "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    json.load(gzip.open(OUT + ".tmp", "rt", encoding="utf-8"))
    os.replace(OUT + ".tmp", OUT)
    rep["bytes"] = os.path.getsize(OUT)
    json.dump(rep, open(REPORT, "w"), ensure_ascii=False, indent=1)
    print(json.dumps(rep, ensure_ascii=False, indent=1)[:3000])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "all")
