#!/usr/bin/env python3
"""Step 30a (system C16, foundation A1): which country of today a point lies in, for the whole Earth.

The technology atlas keeps the year each technology reached each country, so the game must know the country of any
point: a grid of 0.1 degrees (3600 x 1800 squares, about 11 km) over Natural Earth's countries (public domain).

    python3 build_country_grid.py           download Natural Earth's countries (into build/tech/, not kept) and write
                                            history/countries.grid.gz into the mod
    python3 build_country_grid.py --check   read it back and check it (exit 1 on a problem)

File layout (history/countries.grid.gz, gzip; big-endian, as Java's DataInputStream reads it):
  int magic 0x45454347 ("EECG"), int version 1, int width 3600, int height 1800 (row 0 = 90N; column 0 = 180W)
  int n countries; per country: UTF code (ADM0_A3, e.g. "IND"), UTF name, UTF UN subregion, float label lat,
      float label lon, float main town lat, float main town lon (the biggest town of the town list inside it, else the
      label point), int population estimate
  per row: int number of runs, then per run: unsigned short length, unsigned short value (0 = sea, else 1 + country)
"""
import gzip
import io
import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modpack as M   # noqa: E402

BASE = os.path.join(HERE, "build", "tech")
NE = os.path.join(BASE, "ne_10m_admin_0_countries.geojson")
NE_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_0_countries.geojson"
OUT = os.path.join(M.HISTORY, "countries.grid.gz")
TOWNS = os.path.join(M.HISTORY, "towns.json.gz")
W, H = 3600, 1800
MAGIC = 0x45454347


def load_ne():
    if not os.path.exists(NE):
        import requests
        os.makedirs(BASE, exist_ok=True)
        r = requests.get(NE_URL, timeout=600)
        r.raise_for_status()
        with open(NE, "wb") as f:
            f.write(r.content)
    return json.load(open(NE, encoding="utf-8"))["features"]


def rings(geom):
    """[(exterior, [holes])] in (lon, lat) pairs."""
    if geom["type"] == "Polygon":
        polys = [geom["coordinates"]]
    elif geom["type"] == "MultiPolygon":
        polys = geom["coordinates"]
    else:
        return []
    return [(p[0], p[1:]) for p in polys]


def px(ring):
    return [((lon + 180.0) * 10.0, (90.0 - lat) * 10.0) for lon, lat in ring]


def area(ring):
    a = 0.0
    for i in range(len(ring) - 1):
        a += ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1]
    return abs(a) / 2.0


def build():
    from PIL import Image, ImageDraw
    feats = load_ne()
    countries = []
    for f in feats:
        p = f["properties"]
        code = p["ADM0_A3"]
        countries.append({"code": code, "name": p["NAME"], "sub": p["SUBREGION"], "lat": float(p["LABEL_Y"]),
                          "lon": float(p["LABEL_X"]), "pop": int(p["POP_EST"] or 0), "geom": f["geometry"]})
    countries.sort(key=lambda c: c["code"])
    # Big countries first, so enclaves (Lesotho in South Africa, San Marino in Italy) are drawn over the holes.
    order = sorted(range(len(countries)),
                   key=lambda i: -sum(area(ext) for ext, _ in rings(countries[i]["geom"])))
    img = Image.new("I", (W, H), 0)
    draw = ImageDraw.Draw(img)
    for i in order:
        for ext, holes in rings(countries[i]["geom"]):
            draw.polygon(px(ext), fill=i + 1, outline=i + 1)
            for h in holes:
                draw.polygon(px(h), fill=0)
    data = list(img.get_flattened_data() if hasattr(img, 'get_flattened_data') else img.getdata())
    seen = set(data)
    for i, c in enumerate(countries):
        if i + 1 not in seen:      # too small for a 0.1-degree square: its label point
            x = min(W - 1, max(0, int((c["lon"] + 180.0) * 10.0)))
            y = min(H - 1, max(0, int((90.0 - c["lat"]) * 10.0)))
            data[y * W + x] = i + 1
    # Main town: the biggest town of the town list (latest count) inside each country.
    best = {}
    towns = json.load(gzip.open(TOWNS, "rt", encoding="utf-8"))["towns"]
    for t in towns:
        lat, lon = t[2] / 1000.0, t[3] / 1000.0
        pops = t[8]
        if not pops:
            continue
        people = pops[-1]
        x = min(W - 1, max(0, int((lon + 180.0) * 10.0)))
        y = min(H - 1, max(0, int((90.0 - lat) * 10.0)))
        v = data[y * W + x]
        if v and (v not in best or people > best[v][0]):
            best[v] = (people, lat, lon)
    # Where a technology spreads from inside a country when no record names a place: the biggest town of today, but
    # for China the middle of the old heartland (the biggest town of today's list is Chongqing's huge municipality).
    MAIN_OVERRIDE = {"CHN": (34.62, 112.45)}
    for i, c in enumerate(countries):
        if c["code"] in MAIN_OVERRIDE:
            la, lo = MAIN_OVERRIDE[c["code"]]
            best[i + 1] = (best.get(i + 1, (0,))[0], la, lo)
    buf = io.BytesIO()
    w = buf.write
    w(struct.pack(">iiii", MAGIC, 1, W, H))
    w(struct.pack(">i", len(countries)))

    def utf(s):
        b = s.encode("utf-8")
        w(struct.pack(">H", len(b)))
        w(b)

    for i, c in enumerate(countries):
        utf(c["code"])
        utf(c["name"])
        utf(c["sub"])
        mt = best.get(i + 1)
        w(struct.pack(">ffffi", c["lat"], c["lon"], mt[1] if mt else c["lat"], mt[2] if mt else c["lon"], c["pop"]))
    runs_total = 0
    for y in range(H):
        row = data[y * W:(y + 1) * W]
        runs = []
        cur, n = row[0], 0
        for v in row:
            if v == cur and n < 65535:
                n += 1
            else:
                runs.append((n, cur))
                cur, n = v, 1
        runs.append((n, cur))
        w(struct.pack(">i", len(runs)))
        for n, v in runs:
            w(struct.pack(">HH", n, v))
        runs_total += len(runs)
    raw = buf.getvalue()
    with open(OUT + ".tmp", "wb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", compresslevel=9, mtime=0) as g:
            g.write(raw)
    os.replace(OUT + ".tmp", OUT)
    land = sum(1 for v in data if v)
    print(f"countries.grid.gz: {len(countries)} countries, {land:,} land squares, {runs_total:,} runs, "
          f"{len(raw):,} bytes raw, {os.path.getsize(OUT):,} gzipped; main towns for {len(best)} countries")


def read():
    raw = gzip.open(OUT).read()
    p = 0

    def take(fmt):
        nonlocal p
        v = struct.unpack_from(fmt, raw, p)
        p += struct.calcsize(fmt)
        return v

    def utf():
        nonlocal p
        (n,) = take(">H")
        s = raw[p:p + n].decode("utf-8")
        p += n
        return s

    magic, ver, w, h = take(">iiii")
    assert magic == MAGIC and w == W and h == H
    (n,) = take(">i")
    countries = []
    for _ in range(n):
        code, name, sub = utf(), utf(), utf()
        la, lo, mla, mlo, pop = take(">ffffi")
        countries.append((code, name, sub, la, lo, mla, mlo, pop))
    rows = []
    for _ in range(h):
        (k,) = take(">i")
        runs = [take(">HH") for _ in range(k)]
        rows.append(runs)
    return countries, rows


def country_at(countries, rows, lat, lon):
    x = int((lon + 180.0) * 10.0)
    y = int((90.0 - lat) * 10.0)
    x, y = min(W - 1, max(0, x)), min(H - 1, max(0, y))
    acc = 0
    for n, v in rows[y]:
        if x < acc + n:
            return countries[v - 1][0] if v else None
        acc += n
    return None


def check():
    countries, rows = read()
    bad = []
    for y, runs in enumerate(rows):
        if sum(n for n, _ in runs) != W:
            bad.append(f"row {y} has {sum(n for n, _ in runs)} squares")
    expect = [(17.385, 78.4867, "IND"), (48.857, 2.352, "FRA"), (-4.32, 15.31, "COD"), (-4.27, 15.27, "COG"),
              (35.68, 139.76, "JPN"), (-13.52, -71.97, "PER"), (51.507, -0.128, "GBR"), (39.90, 116.40, "CHN"),
              (40.71, -74.0, "USA"), (-33.87, 151.21, "AUS"), (-29.31, 27.48, "LSO"), (43.94, 12.45, "SMR"),
              (30.04, 31.24, "EGY"), (55.75, 37.62, "RUS"), (-23.55, -46.63, "BRA")]
    for lat, lon, want in expect:
        got = country_at(countries, rows, lat, lon)
        if got != want:
            bad.append(f"{lat},{lon}: {got}, expected {want}")
    print(f"check: {len(countries)} countries, {sum(len(r) for r in rows):,} runs; {len(bad)} problems")
    for b in bad[:20]:
        print("  " + b)
    return 1 if bad else 0


def main(argv):
    if len(argv) > 1 and argv[1] == "--check":
        return check()
    build()
    return check()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
