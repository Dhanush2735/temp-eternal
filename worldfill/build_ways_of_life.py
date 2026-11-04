import io
#!/usr/bin/env python3
"""Step 7.1: ways of life from ArchaeoGLOBE (CC0) -> history/ways_of_life.json.gz.

ArchaeoGLOBE (Stephens et al. 2019, Science 365:897) asked 255 archaeologists how land was used in
146 regions of the world at 10 dates, from 10,000 years ago to AD 1850. The consensus table gives,
for each region and date, how widespread five ways of life were:
  FHG   hunting, fishing and gathering      EXAGR extensive (shifting) farming
  INAG  intensive farming                   PAS   herding (pastoralism)
  URBAN towns (Absent / Present / Split = experts disagreed)
Levels: None (0), Minimal (1: under 1% of the land), Common (2: 1-20%), Widespread (3: over 20%).

The region outlines (ArchaeoGLOBE_Simplified_Regions, World Eckert IV metres) are turned back into
latitude/longitude here, so the mod needs no map projection code.

Source: ArchaeoGLOBE Project 2019, Harvard Dataverse doi:10.7910/DVN/CNCANQ (data) and
doi:10.7910/DVN/CQWUBI (regions), both CC0 1.0.
"""
import csv, gzip, json, math, os, sys

import shapefile  # pyshp

sys.path.insert(0, "/home/user/worldfill")
import modpack as M  # noqa: E402

SRC = os.path.expanduser("~/.cache/srcdata/archaeoglobe")
OUT = f"{M.HISTORY}/ways_of_life.json.gz"
REPORT = "/home/user/worldfill/ways_of_life_report.json"
SLICES = [-8050, -6050, -4050, -2050, -1050, -50, 950, 1500, 1750, 1850]   # 10 ka BP ... AD 1850
LEVEL = {"None": 0, "Minimal": 1, "Common": 2, "Widespread": 3, "Absent": 0, "Present": 1}
R = 6378137.0


def eckert4_inverse(x, y):
    """World Eckert IV (sphere of the WGS84 semi-major axis, as ESRI uses) -> (lat, lon)."""
    s = max(-1.0, min(1.0, y / (1.3265004 * R)))
    th = math.asin(s)
    lon = math.degrees(x / (0.4222382 * R * (1.0 + math.cos(th))))
    lat = math.degrees(math.asin(max(-1.0, min(1.0, (th + math.sin(th) * math.cos(th) + 2.0 * math.sin(th))
                                                 / (2.0 + math.pi / 2.0)))))
    return lat, max(-180.0, min(180.0, lon))


def eckert4_forward(lat, lon):
    phi, lam = math.radians(lat), math.radians(lon)
    target = (2.0 + math.pi / 2.0) * math.sin(phi)
    th = phi / 2.0
    for _ in range(30):
        f = th + math.sin(th) * math.cos(th) + 2.0 * math.sin(th) - target
        d = 1.0 + math.cos(2.0 * th) + 2.0 * math.cos(th)
        if abs(d) < 1e-12:
            break
        th -= f / d
    return 0.4222382 * R * lam * (1.0 + math.cos(th)), 1.3265004 * R * math.sin(th)


def main():
    # self-check of the inverse against the forward formula
    for la, lo in ((0, 0), (45, 90), (-33.9, 18.4), (64.8, -147.7)):
        b = eckert4_inverse(*eckert4_forward(la, lo))
        assert abs(b[0] - la) < 1e-6 and abs(b[1] - lo) < 1e-6, (la, lo, b)
    rows = list(csv.DictReader(open(f"{SRC}/f_3442650.csv", encoding="cp1252")))
    cols = list(rows[0].keys())
    groups = {}
    for key, prefix in (("fhg", "FHG_"), ("exagr", "EXAG"), ("inag", "INAG_"), ("pas", "PAS_"), ("urban", "URBAN_")):
        groups[key] = [c for c in cols if c.upper().startswith(prefix)]
        assert len(groups[key]) == 10, (key, groups[key])
    table = {}
    for r in rows:
        rid = int(r["Region"])
        table[rid] = {k: [LEVEL.get((r[c] or "").strip(), -1) for c in cs] for k, cs in groups.items()}
        table[rid]["name"] = r["Label"].strip()
    shp = shapefile.Reader(f"{SRC}/regions/ArchaeoGLOBE_Simplified_Regions", encoding="cp1252")
    regions, npts = [], 0
    for sr in shp.shapeRecords():
        rec = sr.record.as_dict()
        rid = int(rec["Archaeo_ID"])
        if rid not in table:
            continue
        pts, parts = sr.shape.points, list(sr.shape.parts) + [len(sr.shape.points)]
        rings = []
        for a, b in zip(parts[:-1], parts[1:]):
            ring = []
            for x, y in pts[a:b]:
                la, lo = eckert4_inverse(x, y)
                p = [round(la, 3), round(lo, 3)]
                if not ring or p != ring[-1]:
                    ring.append(p)
            if len(ring) >= 4:
                rings.append(ring)
                npts += len(ring)
        t = table[rid]
        regions.append({"id": rid, "name": t["name"], "world": rec.get("World_RG", ""),
                        "fhg": t["fhg"], "exagr": t["exagr"], "inag": t["inag"], "pas": t["pas"],
                        "urban": t["urban"], "rings": rings})
    regions.sort(key=lambda r: r["id"])
    doc = {"format": 1,
           "source": ("ArchaeoGLOBE Project 2019 (Science 365:897), consensus assessment, Harvard Dataverse "
                      "doi:10.7910/DVN/CNCANQ; regions doi:10.7910/DVN/CQWUBI; both CC0 1.0. worldfill/build_ways_of_life.py"),
           "slices": SLICES,
           "levels": "0 none, 1 minimal (<1% of land), 2 common (1-20%), 3 widespread (>20%), -1 no answer; urban 0 absent, 1 present, -1 split",
           "regions": regions}
    with open(OUT + ".tmp", "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    json.load(gzip.open(OUT + ".tmp", "rt", encoding="utf-8"))
    os.replace(OUT + ".tmp", OUT)
    rep = {"regions": len(regions), "points": npts, "bytes": os.path.getsize(OUT),
           "example": {k: v for k, v in regions[0].items() if k != "rings"}}
    json.dump(rep, open(REPORT, "w"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
