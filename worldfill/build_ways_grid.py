#!/usr/bin/env python3
# ============================================================
# Step 34 part 3 (B12, B14, B15): the ways grid.
#
#   python3 build_ways_grid.py           build history/ways.grid.gz
#   python3 build_ways_grid.py --check   read it back and check it
#   python3 build_ways_grid.py --places  what each test place answers
#
# For every 0.1 degree square of land, the first year a railway, a dated road
# and a canal existed there. That is the gate: before Terra++ draws today's
# road or today's railway out of OSM, it asks this grid whether the thing
# existed in the year the player is standing in. Step 31 found Sydney in 1850
# with two railways — Australia's first opened in 1854 — and Patna in 300 BC
# with 98 modern roads. This is the answer to both.
#
# Three sources, merged by the earliest year each gives for a cell:
#
#   1. OpenHistoricalMap's dated ways (part 3 of step 34): 233,930 railway,
#      314,140 pre-1900 highway and 10,277 canal ways with a start_date,
#      fetched in tiles and binned here. Licence: individual features, CC0
#      preferred, some ODbL, some CC BY-SA; none non-commercial.
#   2. Itiner-e's Roman road network, already in the mod
#      (history/trade_routes.json.gz): 14,769 segments, years -514..700.
#      This is what carries the pre-1000 grid, because OHM's first-millennium
#      dates are not to be trusted ('0060' may be AD 60 or a mistyped 1060).
#   3. Wikidata's dated works from part 2 (82,304 rows with a year): a railway
#      station opened in 1850 is proof of a railway in its cell in 1850.
#
# File layout (history/ways.grid.gz, gzip; big-endian, like countries.grid.gz):
#
#   magic int "WAYS" | version int | w int 3600 | h int 1800 | cell float 0.1
#   palette count int, then that many (rail short, road short, canal short)
#     — first years, -32768 for "never" —
#   then for each of the h rows: run count int, then (run length ushort,
#   palette index ushort) pairs.
# ============================================================
import gzip
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modpack as M  # noqa: E402

OHM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "ohm", "tiles")
WAYS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build", "ways", "raw")
HIST = os.path.join(M.HISTORY, "trade_routes.json.gz")
OUT = os.path.join(M.HISTORY, "ways.grid.gz")

MAGIC = 0x57415953          # "WAYS"
VERSION = 1
W, H, CELL = 3600, 1800, 0.1
NONE = -32768
STEP = 0.02                 # interpolate along a line every ~2 km

# Wikidata classes that prove a line existed, from step 34 part 2.
KIND_OF_CLASS = {
    "Q728937": "rail", "Q55488": "rail", "Q928830": "rail", "Q2175765": "rail",
    "Q1311958": "rail", "Q420962": "rail",
    "Q194029": "road", "Q11410923": "road", "Q337912": "road",
    "Q12284": "canal", "Q105731": "canal", "Q1066997": "canal",
}


def cell_of(lat, lon):
    y = int((90.0 - lat) / CELL)
    x = int((lon + 180.0) / CELL)
    if not (0 <= y < H and 0 <= x < W):
        return None
    return y * W + x


# A year is only used if it can be true. Nothing in this pack is dated later than the year it was
# built (2026): a railway "opening" in 2033 is a plan, not a railway, and drawing it in 2026 would
# be a lie. The floors are what the sources can actually support -- there are no railways in
# antiquity, and no shippable source dates a canal before 1000 BC -- so a stray -1800 from a
# misread start_date is dropped rather than shipped.
MAX_YEAR = 2026
FLOOR = {"rail": 1500, "road": -3000, "canal": -1000}


def put(cells, c, kind, year):
    if year > MAX_YEAR or year < FLOOR[kind]:
        return
    cur = cells.get(c)
    if cur is None:
        cur = cells[c] = [None, None, None]
    i = {"rail": 0, "road": 1, "canal": 2}[kind]
    if cur[i] is None or year < cur[i]:
        cur[i] = year


def add_line(cells, pts, kind, year):
    """Bin a polyline into cells, interpolating so that a long straight
    segment lights up the squares it crosses, not just its two ends."""
    prev = None
    for la, lo in pts:
        if prev is not None:
            d = max(abs(la - prev[0]), abs(lo - prev[1]))
            n = 1 if d <= STEP else min(128, int(d / STEP))
            for k in range(n + 1):
                f = k / n
                c = cell_of(prev[0] + (la - prev[0]) * f, prev[1] + (lo - prev[1]) * f)
                if c is not None:
                    put(cells, c, kind, year)
        c = cell_of(la, lo)
        if c is not None:
            put(cells, c, kind, year)
        prev = (la, lo)


def from_ohm(cells):
    n = 0
    if not os.path.isdir(OHM):
        return 0
    for f in sorted(os.listdir(OHM)):
        if not f.endswith(".json"):
            continue
        for c, v in json.load(open(os.path.join(OHM, f))).items():
            c = int(c)
            for i, y in enumerate(v):
                if y is None:
                    continue
                put(cells, c, ("rail", "road", "canal")[i], int(y))
        n += 1
    return n


def from_itiner_e(cells):
    d = json.loads(gzip.open(HIST, "rt").read())
    n = 0
    for name, main, first, last, flat in d["roads"]:
        pts = [(flat[i], flat[i + 1]) for i in range(0, len(flat) - 1, 2)]
        add_line(cells, pts, "road", int(first))
        n += 1
    return n


def from_wikidata(cells):
    n = 0
    for cls, kind in KIND_OF_CLASS.items():
        path = os.path.join(WAYS, f"class_{cls}.json")
        if not os.path.exists(path):
            continue
        for r in json.load(open(path, encoding="utf-8")):
            if r.get("start") is None:
                continue
            c = cell_of(r["lat"], r["lon"])
            if c is not None:
                put(cells, c, kind, int(r["start"]))
                n += 1
    return n


def build():
    cells = {}
    t = from_ohm(cells)
    print(f"openhistoricalmap: {t} tiles -> {len(cells):,} cells")
    n = from_itiner_e(cells)
    print(f"itiner-e roads:    {n:,} segments -> {len(cells):,} cells")
    n = from_wikidata(cells)
    print(f"wikidata works:    {n:,} dated rows -> {len(cells):,} cells")

    # A guard, added 2026-10-23 after a full probe sweep ran this builder on a box where neither the
    # OHM tiles nor the Wikidata rows were on disk (they live in build/, which does not survive
    # between sessions). It silently rewrote the shipped pack with roads only: 183,580 bytes became
    # 16,817, and New York and Moscow lost their railways. A builder must refuse to replace a good
    # pack with a worse one - the pack already in the mod is the record of a complete fetch.
    if t == 0 and n == 0:
        raise SystemExit(
            "ways.grid.gz: refusing to overwrite the shipped pack - 0 OpenHistoricalMap tiles and\n"
            "  0 dated Wikidata works on disk, so this would keep only the Itiner-e roads.\n"
            "  Fetch the sources first (worldfill/fetch_ways_wd.py --fetch; the OHM tiles), or run\n"
            "  this with --check to verify the pack that ships.")

    pal, rows = {}, []
    def idx_of(triple):
        k = tuple(triple)
        if k not in pal:
            pal[k] = len(pal)
        return pal[k]

    for y in range(H):
        row = []
        run_start = None
        run_idx = None
        for x in range(W):
            v = cells.get(y * W + x)
            triple = [NONE if v is None or v[i] is None else v[i] for i in range(3)]
            i = idx_of(tuple(triple))
            if run_idx == i:
                continue
            if run_idx is not None:
                row.append((x - run_start, run_idx))
            run_start, run_idx = x, i
        if run_idx is not None:
            row.append((W - run_start, run_idx))
        rows.append(row)

    out = bytearray()
    out += struct.pack(">iiii f", MAGIC, VERSION, W, H, CELL)[:16 + 4]
    out += struct.pack(">i", len(pal))
    for k in sorted(pal, key=lambda k: pal[k]):
        out += struct.pack(">hhh", *k)
    for row in rows:
        out += struct.pack(">i", len(row))
        for n, v in row:
            out += struct.pack(">HH", n, v)
    raw = bytes(out)
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(raw)
    print(f"ways.grid.gz: {len(cells):,} cells, {len(pal):,} palettes, "
          f"{sum(len(r) for r in rows):,} runs, {len(raw):,} bytes raw, "
          f"{os.path.getsize(OUT):,} bytes gzipped")


def read():
    raw = gzip.open(OUT).read()
    p = 0

    def take(fmt):
        nonlocal p
        v = struct.unpack_from(fmt, raw, p)
        p += struct.calcsize(fmt)
        return v

    magic, ver, w, h = take(">iiii")
    assert magic == MAGIC and w == W and h == H, "grid header"
    (cell,) = take(">f")
    (n,) = take(">i")
    pal = [take(">hhh") for _ in range(n)]
    rows = []
    for _ in range(h):
        (k,) = take(">i")
        rows.append([take(">HH") for _ in range(k)])
    return pal, rows, ver, cell, p


def at(pal, rows, lat, lon):
    x = int((lon + 180.0) * 10.0)
    y = int((90.0 - lat) * 10.0)
    x, y = min(W - 1, max(0, x)), min(H - 1, max(0, y))
    acc = 0
    for run, v in rows[y]:
        if x < acc + run:
            return pal[v]
        acc += run
    return pal[0]


def check():
    pal, rows, ver, cell, used = read()
    bad = []
    for y, r in enumerate(rows):
        if sum(n for n, _ in r) != W:
            bad.append(("row length", y, sum(n for n, _ in r)))
            break
    if bad:
        print("FAIL:", bad)
        return 1
    land = sum(n for r in rows for n, v in r if any(x != NONE for x in pal[v]))
    print(f"ways.grid.gz: version {ver}, {len(pal):,} palettes, "
          f"{sum(len(r) for r in rows):,} runs, "
          f"{land:,} cells with something in them, {used:,} bytes")
    return 0


def places():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from fetch_town_wd import TEST_PLACES
    pal, rows, ver, cell, used = read()
    print(f"{'place':14s} {'year':>6s}  rail  road  canal   verdict")
    for name, lat, lon, year in TEST_PLACES:
        rail, road, canal = at(pal, rows, lat, lon)
        def v(y):
            if y == NONE:
                return "none"
            return "yes" if y <= year else f"{y}"
        verdict = []
        if rail != NONE and rail <= year:
            verdict.append("railway may be drawn")
        if road != NONE and road <= year:
            verdict.append("road may be drawn")
        if canal != NONE and canal <= year:
            verdict.append("canal may be drawn")
        if not verdict:
            verdict.append("no dated network — Terra++ must fall back")
        print(f"  {name:12s} {year:>6d}  {v(rail):>6s} {v(road):>6s} {v(canal):>6s}   "
              f"{'; '.join(verdict)}")


def main(argv):
    mode = argv[1] if len(argv) > 1 else ""
    if mode == "--check":
        sys.exit(check())
    if mode == "--places":
        places()
    else:
        build()


if __name__ == "__main__":
    main(sys.argv)
