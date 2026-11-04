#!/usr/bin/env python3
# ============================================================
# Step 34 part 3 (B12, B14, B15): the dated ways of
# OpenHistoricalMap, tiled and binned into the ways grid.
#
#   python3 fetch_ohm_ways.py --test         one tile, and what it costs
#   python3 fetch_ohm_ways.py --fetch        every land tile -> build/ohm/tiles/
#   python3 fetch_ohm_ways.py --status       which tiles are done
#
# Why it looks like this:
#
#  * OpenHistoricalMap is the only source that carries the *geometry* of a road
#    or a railway with the year it was opened: 233,930 railway ways with a
#    start_date (97% of all its railway ways), 1,159,898 highways, 10,277
#    waterways. Wikidata (part 2) gives the named works but only a point each —
#    1,800 of its 29,771 railway lines have a coordinate at all.
#  * The whole point of this part is the grid, not the geometry: for every
#    0.1° cell, the first year a railway, a dated road and a canal existed
#    there. So the geometry is fetched tile by tile, binned, and thrown away —
#    nothing large is ever kept on disk.
#  * Highways are capped at ways opened before 1900 (314,140 of the 1,159,898).
#    After 1900 roads are everywhere, and the grid's answer is "yes" almost
#    everywhere anyway; before 1900 is where the gate earns its keep.
#  * Ways are interpolated between their nodes at ~2 km. A railway drawn as
#    two nodes 100 km apart must light up the cells it runs through, not just
#    the two it happens to touch.
#  * The licence is recorded honestly: OHM features are licensed individually
#    (CC0 preferred, some ODbL, some CC BY-SA). None is non-commercial, so the
#    pack may ship, but the file's licence line says so.
# ============================================================
import json
import math
import os
import re
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "build", "ohm", "tiles")
UA = "EternalEngineDataBuild/1.0 (history data; Eternal Engine Minecraft mod)"
EP = "https://overpass-api.openhistoricalmap.org/api/interpreter"

CELL = 0.1                      # degrees — the country grid's own cell
STEP = 0.02                     # ~2 km of interpolation along a way
TILE = 5.0                      # degrees per tile
LAT_RANGE = (-56.0, 76.0)       # nothing south of Tierra del Fuego, no North Pole
ROAD_CAP = "1900"               # highways: only ways opened before this

# kind -> (key, extra tag filter)
KINDS = {
    "rail":  ('way["railway"]["start_date"]', None),
    "road":  ('way["highway"]["start_date"]', ROAD_CAP),
    "canal": ('way["waterway"="canal"]["start_date"]', None),
}

NUM = re.compile(r"(-?\d{3,4})")


def cell_of(lat, lon):
    """0.1 degree cell index, numbered exactly as `history/countries.grid.gz`
    numbers its squares — y counted from the north, x from the antimeridian —
    so that the two grids can be read together."""
    y = int((90.0 - lat) / CELL)
    x = int((lon + 180.0) / CELL)
    if not (0 <= y < 1800 and 0 <= x < 3600):
        return None
    return y * 3600 + x


def year_of(text):
    """start_date -> int year, or None. OHM allows EDTF: 1850, 1850s, c1850,
    1850-01-01, 18th century, -0500."""
    if not text:
        return None
    m = NUM.search(text)
    if not m:
        return None
    y = int(m.group(1))
    if "bc" in text.lower() or text.strip().startswith("-"):
        y = -y
    if not -3000 <= y <= 2030:
        return None
    # OHM's first-millennium dates are not to be trusted: '0060', '0060-01-01',
    # '100', '0124' all appear in the London tile (221 of its 14,157 highway
    # ways), and '0060' may be AD 60 or a mistyped 1060. The gate must not draw
    # a road in AD 60 on the strength of one. Pre-1000 cells come from Itiner-e
    # instead, which carries real Roman dates.
    if 0 < y < 1000:
        return None
    return y


def ask(query, tries=3, timeout=300):
    last = ""
    for k in range(tries):
        try:
            t = time.time()
            r = requests.post(EP, data={"data": query}, headers={"User-Agent": UA},
                              timeout=timeout)
            if r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code}")
            return r.json(), time.time() - t, len(r.text)
        except Exception as e:  # noqa: BLE001
            last = f"{type(e).__name__}: {str(e)[:60]}"
            time.sleep(10 * (k + 1))
    return None, last, 0


def query(kind, box):
    sel = KINDS[kind][0]
    cap = KINDS[kind][1]
    filt = f'(if: t["start_date"] < "{cap}")' if cap else ""
    return (f'[out:json][timeout:600];{sel}{filt}({box});'
            f'out geom;')


def bin_tile(kind, elements):
    """Ways -> {cell: first year}. Interpolated along the way."""
    out = {}
    for e in elements:
        if e.get("type") != "way":
            continue
        start = year_of(e.get("tags", {}).get("start_date"))
        if start is None:
            continue
        end = year_of(e.get("tags", {}).get("end_date"))
        geom = e.get("geometry") or []
        pts = [(g["lat"], g["lon"]) for g in geom if g]
        for i in range(len(pts) - 1):
            (la0, lo0), (la1, lo1) = pts[i], pts[i + 1]
            d = max(abs(la1 - la0), abs(lo1 - lo0))
            n = 1 if d <= STEP else min(64, int(d / STEP))
            for k in range(n + 1):
                f = k / n
                c = cell_of(la0 + (la1 - la0) * f, lo0 + (lo1 - lo0) * f)
                if c is None:
                    continue
                cur = out.get(c)
                if cur is None or start < cur[0]:
                    out[c] = [start, end]
                elif end is not None and cur[1] is None:
                    out[c] = [cur[0], end]
        if len(pts) == 1:
            c = cell_of(*pts[0])
            if c is not None:
                cur = out.get(c)
                if cur is None or start < cur[0]:
                    out[c] = [start, end]
    return out


def land_mask():
    """bytearray over the 6.48 M cells: 1 where Natural Earth has land.

    Without it two thirds of the 1,944 tiles are open ocean and every one
    costs a round trip to Overpass for an empty answer.
    """
    sys.path.insert(0, HERE)
    import build_country_grid as CG
    countries, rows = CG.read()
    mask = bytearray(3600 * 1800)
    for y, runs in enumerate(rows):
        acc = 0
        for n, v in runs:
            if v:
                mask[y * 3600 + acc: y * 3600 + acc + n] = b"\x01" * n
            acc += n
    return mask


def tile_name(tlat, tlon):
    return f"{int(tlat):+03d}_{int(tlon):+04d}"


def one_tile(y, x, name):
    """Fetch one tile: three kinds, binned, written. Returns (name, cells, ok)."""
    box = f"{y},{x},{y + TILE},{x + TILE}"
    cells = {}
    for kind in KINDS:
        q = query(kind, box)
        data, dt, size = ask(q)
        if data is None:
            print(f"  {name} {kind}: FAILED {dt}", flush=True)
            return name, 0, False
        got = bin_tile(kind, data.get("elements", []))
        for c, v in got.items():
            cur = cells.get(c)
            if cur is None:
                cells[c] = [None, None, None]
                cur = cells[c]
            idx = {"rail": 0, "road": 1, "canal": 2}[kind]
            if cur[idx] is None or v[0] < cur[idx]:
                cur[idx] = v[0]
        print(f"  {name} {kind}: {len(got):>6,} cells, "
              f"{len(data.get('elements', [])):>6,} ways  {dt:.0f}s", flush=True)
    json.dump(cells, open(os.path.join(RAW, f"{name}.json"), "w"))
    return name, len(cells), True


def fetch(only=None, workers=4):
    """Tiles in parallel. One tile at a time took eight seconds a tile and
    most of that is waiting for Overpass; four at once is asked politely, with
    the retry-and-backoff of ask() absorbing the odd 429."""
    from concurrent.futures import ThreadPoolExecutor
    os.makedirs(RAW, exist_ok=True)
    lats = [y for y in range(int(LAT_RANGE[0]), int(LAT_RANGE[1]), int(TILE))]
    lons = [x for x in range(-180, 180, int(TILE))]
    mask = land_mask()
    todo, sea = [], 0
    for y in lats:
        for x in lons:
            name = tile_name(y, x)
            if only and name not in only:
                continue
            if os.path.exists(os.path.join(RAW, f"{name}.json")):
                continue
            land = False
            for i in range(int(TILE / CELL)):
                la = y + TILE - i * CELL - CELL / 2
                if not -90 < la < 90:
                    continue
                row = int((90.0 - la) / CELL)
                x0 = int((x + 180.0) / CELL)
                if 1 in mask[row * 3600 + x0: row * 3600 + x0 + int(TILE / CELL)]:
                    land = True
                    break
            if land:
                todo.append((y, x, name))
            else:
                sea += 1
    print(f"{len(todo)} land tiles to fetch, {sea} ocean tiles skipped "
          f"({workers} at a time)", flush=True)
    done = failed = 0
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for n, (name, cells, ok) in enumerate(
                pool.map(lambda t: one_tile(*t), todo), 1):
            if ok:
                done += 1
            else:
                failed += 1
            print(f"  [{n}/{len(todo)}] {name}: {cells:,} cells written"
                  f"  ({done} done, {failed} failed)", flush=True)


def test():
    box = "50,-5,55,2"   # London and the south-east: the densest part of OHM
    for kind in KINDS:
        q = query(kind, box)
        t = time.time()
        data, dt, size = ask(q)
        if data is None:
            print(f"  {kind:6s} FAILED {dt}")
            continue
        els = data.get("elements", [])
        cells = bin_tile(kind, els)
        years = [year_of(e.get("tags", {}).get("start_date")) for e in els]
        years = [y for y in years if y is not None]
        print(f"  {kind:6s} {len(els):>7,} ways  {len(cells):>7,} cells  "
              f"{size / 1e6:6.1f} MB  {time.time() - t:5.1f}s  "
              f"years {min(years) if years else '-'}..{max(years) if years else '-'}")


def status():
    if not os.path.exists(RAW):
        print("no tiles yet")
        return
    files = sorted(f for f in os.listdir(RAW) if f.endswith(".json"))
    cells = 0
    for f in files:
        cells += len(json.load(open(os.path.join(RAW, f))))
    print(f"{len(files)} tiles, {cells:,} cells")


def main(argv):
    mode = argv[1] if len(argv) > 1 else "--test"
    if mode == "--test":
        test()
    elif mode == "--fetch":
        fetch(argv[2:] or None)
    elif mode == "--status":
        status()


if __name__ == "__main__":
    main(sys.argv)
