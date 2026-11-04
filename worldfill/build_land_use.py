#!/usr/bin/env python3
"""Step 35, part 3 (B3, B4): what the land was used for, at any place, in any year, 10,000 BCE to 2015 CE.

The world can be set to any date, so the land cannot be one map: the same square that is a rice
village in 1900 was wild woodland in 3000 BCE, and the crops, the pasture and the timber a
settlement can draw on all hang on which it is. Anthromes 12K (Ellis, Beusen and Klein Goldewijk,
Harvard Dataverse, CC0) is the only reconstruction that answers this for the whole Earth across
the whole span: 73 gridded time steps, 10,000 BCE to 2015 CE, each a 5-arcminute map of which of
19 anthropogenic biomes covers every land cell.

    73 steps x 6,480,000 cells is 473,000,000 numbers. Shipped as maps that is far too much, so
    the pack is the earliest map plus what changed: 2,393,643 changed cells over 12,000 years,
    which is 1.6 changes per land cell across the whole of human history.

    python3 build_land_use.py                build history/land_use.grid.gz into the mod
    python3 build_land_use.py --check        read it back and rebuild every step against the source
    python3 build_land_use.py --places       what the land was, at the places history records
    python3 build_land_use.py --hyde         check the areas against HYDE 3.3's regional totals

Grid: 0.1 degrees, 3600 x 1800, row 0 = 90N, column 0 = 180W — numbered exactly as
history/countries.grid.gz and history/ways.grid.gz are, so one square means the same thing in all
three. Each 0.1 degree cell takes the class of the 5-arcminute cell holding its centre.

File layout (history/land_use.grid.gz, gzip; big-endian, as Java's DataInputStream reads it):
  int magic 0x45454C55 ("EELU"), int version 1, int width 3600, int height 1800
  int nSteps 73; int[nSteps] year of each step (the mod's own year numbers: -10000 .. 2015)
  int nPalette; per entry: int code, UTF name, UTF level, UTF short answer
  int landCells, int totalChanges
  per row: int nRuns, then per run: unsigned short length, unsigned byte value (0 = ocean, else palette index)
  for step 1 .. nSteps-1: int nChanges, then per change, in rising cell order:
      varint gap from the previous changed cell (the first is the cell index itself), unsigned byte value
"""
import gzip
import io
import os
import re
import struct
import sys
import time
import zipfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modpack as M                       # noqa: E402
from measure_anthromes import (           # noqa: E402
    ZIP, CACHE, NROWS, NCOLS, H, W, NAMES, LEVEL, RS, CS, resample, steps, load_raw,
)

OUT = os.path.join(M.HISTORY, "land_use.grid.gz")
MAGIC = 0x45454C55          # "EELU"
VERSION = 1

# The six levels of the classification, and the one-word answer the game wants from each.
SHORT = {"settlement": "town", "village": "village", "cropland": "cropland", "rangeland": "pasture",
         "woodland": "woodland", "wild": "wildland", "ice": "ice", "ocean": "ocean"}
LEVELNAME = {"settlement": "Dense settlements", "village": "Villages", "cropland": "Croplands",
             "rangeland": "Rangelands", "woodland": "Seminatural lands", "wild": "Wildlands",
             "ice": "Ice", "ocean": "Ocean or no data"}

# Codes 63 and 70 both mean ice in the source grids: 63 is the ice sheet, 70 appears in seven
# cells (high mountains, and one island) and is folded into 63 here.
MERGE_70_TO = 63


def palette():
    """[(code, name, level, short)] with index 0 = ocean, then the classes by rising code."""
    codes = sorted(c for c in NAMES if c != 70)
    out = [(0, LEVELNAME["ocean"], "ocean", SHORT["ocean"])]
    for c in codes:
        lv = LEVEL[c]
        out.append((c, NAMES[c] + (" (with code 70)" if c == MERGE_70_TO else ""),
                    LEVELNAME[lv], SHORT[lv]))
    return out


def index_of_code():
    return {c: i for i, (c, _, _, _) in enumerate(palette())}


def varint(n, out):
    while True:
        b = n & 0x7F
        n >>= 7
        if n:
            out.append(b | 0x80)
        else:
            out.append(b)
            break


def read_varint(buf, pos):
    shift = 0
    n = 0
    while True:
        b = buf[pos]
        pos += 1
        n |= (b & 0x7F) << shift
        if not (b & 0x80):
            return n, pos
        shift += 7


def grids(use_cache=True):
    """Yield (year, uint8 grid at 0.1 degrees) earliest first, from the cache when it is there."""
    items = steps()
    if use_cache and os.path.isdir(CACHE):
        for y, _ in items:
            p = os.path.join(CACHE, "%05d.bin" % (y + 10000))
            if not os.path.exists(p):
                break
        else:
            for y, _ in items:
                yield y, np.fromfile(os.path.join(CACHE, "%05d.bin" % (y + 10000)),
                                     dtype=np.uint8).reshape(H, W)
            return
    z = zipfile.ZipFile(ZIP)
    for y, name in items:
        g = resample(load_raw(z, name))
        if use_cache:
            os.makedirs(CACHE, exist_ok=True)
            g.tofile(os.path.join(CACHE, "%05d.bin" % (y + 10000)))
        yield y, g


def to_palette(g):
    """Source codes -> palette indices, with 70 folded into 63."""
    out = np.zeros_like(g, dtype=np.uint8)
    idx = index_of_code()
    for code, i in idx.items():
        if code == 0:
            continue
        out[g == code] = i
    if 70 in [c for c in NAMES]:
        out[(g == 70) | (g == 63)] = idx[63]
    return out


def rle_row(row):
    ch = np.nonzero(row[1:] != row[:-1])[0] + 1
    starts = np.concatenate(([0], ch))
    ends = np.concatenate((ch, [W]))
    return (ends - starts).astype(">u2"), row[starts].astype(np.uint8)


def build():
    t0 = time.time()
    pal = palette()
    years = []
    packed = []                      # palette-index grids
    for y, raw in grids():
        years.append(y)
        packed.append(to_palette(raw))
    print("%d steps, %d .. %d, %d palette entries" % (len(years), years[0], years[-1], len(pal)))
    land = int(np.count_nonzero(packed[0]))
    print("land cells: %d of %d" % (land, H * W))

    # the earliest map, row by row, run length encoded
    base = bytearray()
    b0 = packed[0]
    nruns = 0
    for r in range(H):
        lens, vals = rle_row(b0[r])
        nruns += len(lens)
        base += struct.pack(">I", len(lens))
        base += b"".join(struct.pack(">HB", int(l), int(v)) for l, v in zip(lens, vals))

    # then, per step, which cells changed
    diffs = bytearray()
    total = 0
    for s in range(1, len(packed)):
        cur = packed[s].reshape(H * W)
        prev = packed[s - 1].reshape(H * W)
        idx = np.nonzero(cur != prev)[0]
        total += len(idx)
        diffs += struct.pack(">I", len(idx))
        gaps = bytearray()
        p = -1
        for j in idx:
            j = int(j)
            varint(j - p - 1 if p >= 0 else j, gaps)
            p = j
        diffs += gaps
        diffs += cur[idx].tobytes()
    print("base map %d bytes in %d runs; %d changes in %d diff layers, %d bytes"
          % (len(base), nruns, total, len(packed) - 1, len(diffs)))

    out = bytearray()
    out += struct.pack(">IIII", MAGIC, VERSION, W, H)
    out += struct.pack(">I", len(years))
    out += b"".join(struct.pack(">i", y) for y in years)
    out += struct.pack(">I", len(pal))
    for code, name, level, short in pal:
        out += struct.pack(">I", code)
        for s2 in (name, level, short):
            b = s2.encode("utf-8")
            out += struct.pack(">H", len(b)) + b
    out += struct.pack(">II", land, total)
    out += base
    out += diffs
    raw = bytes(out)
    with gzip.GzipFile(OUT, "wb", compresslevel=9, mtime=0) as f:
        f.write(raw)
    print("wrote %s: %d bytes raw, %d gzipped (%.2f MB)" %
          (OUT, len(raw), os.path.getsize(OUT), os.path.getsize(OUT) / 1e6))
    print("%.1f s" % (time.time() - t0))


class Pack(object):
    """Reads the pack back and can rebuild the map of any step."""

    def __init__(self, path=OUT):
        with gzip.open(path, "rb") as f:
            self.buf = f.read()
        b = self.buf
        p = 0
        (magic, ver, self.w, self.h) = struct.unpack_from(">IIII", b, p)
        p += 16
        assert magic == MAGIC, "bad magic 0x%08X" % magic
        assert ver == VERSION, "bad version %d" % ver
        (nsteps,) = struct.unpack_from(">I", b, p)
        p += 4
        self.years = list(struct.unpack_from(">%di" % nsteps, b, p))
        p += 4 * nsteps
        (npal,) = struct.unpack_from(">I", b, p)
        p += 4
        self.palette = []
        for _ in range(npal):
            (code,) = struct.unpack_from(">I", b, p)
            p += 4
            strs = []
            for _k in range(3):
                (n,) = struct.unpack_from(">H", b, p)
                p += 2
                strs.append(b[p:p + n].decode("utf-8"))
                p += n
            self.palette.append((code, strs[0], strs[1], strs[2]))
        (self.landCells, self.totalChanges) = struct.unpack_from(">II", b, p)
        p += 8
        self.body = p
        self.runs = []
        for _r in range(self.h):
            (n,) = struct.unpack_from(">I", b, p)
            p += 4
            arr = np.frombuffer(b, dtype=np.uint8, count=3 * n, offset=p)
            p += 3 * n
            lens = (arr[0::3].astype(np.uint16) << 8) | arr[1::3].astype(np.uint16)
            vals = arr[2::3]
            self.runs.append((lens, vals))
        self.diffpos = []
        for _s in range(len(self.years) - 1):
            (n,) = struct.unpack_from(">I", b, p)
            p += 4
            gaps = p
            cell = -1
            for _k in range(n):
                gap, p = read_varint(b, p)
                cell = gap if cell < 0 else cell + gap + 1
            self.diffpos.append((n, gaps, p))     # where the gaps start, and where the values start
            p += n
        assert p == len(b), "trailing bytes: %d vs %d" % (p, len(b))
        self._grid = None
        self._at = -1

    def base(self):
        g = np.zeros((self.h, self.w), dtype=np.uint8)
        for r, (lens, vals) in enumerate(self.runs):
            col = 0
            for l, v in zip(lens, vals):
                g[r, col:col + int(l)] = v
                col += int(l)
            assert col == self.w, "row %d is %d wide" % (r, col)
        return g

    def apply_diff(self, g, k):
        """Put step k's changes into a flat grid, in place. g must already hold step k."""
        n, gp, vp = self.diffpos[k]
        buf = self.buf
        cell = -1
        for _j in range(n):
            b = buf[gp]
            gp += 1
            gap = b & 0x7F
            shift = 7
            while b & 0x80:
                b = buf[gp]
                gp += 1
                gap |= (b & 0x7F) << shift
                shift += 7
            cell = gap if cell < 0 else cell + gap + 1
            g[cell] = buf[vp]
            vp += 1

    def step(self, s):
        """The map of step s, as palette indices, after replaying every diff up to it."""
        g = self.base().reshape(self.h * self.w)
        for k in range(min(s, len(self.diffpos))):
            self.apply_diff(g, k)
        return g.reshape(self.h, self.w)

    def grid_for(self, s):
        """The same, but remembers the last step it built and walks to the one asked for."""
        if self._grid is None or s < self._at:
            self._grid = self.base().reshape(self.h * self.w)
            self._at = 0
        while self._at < s:
            self.apply_diff(self._grid, self._at)
            self._at += 1
        return self._grid.reshape(self.h, self.w)

    def step_for_year(self, year):
        s = 0
        for i, y in enumerate(self.years):
            if y <= year:
                s = i
        return s

    def at(self, lat, lon, year):
        r = int((90.0 - lat) * 10.0)
        c = int((lon + 180.0) * 10.0)
        r = min(max(r, 0), self.h - 1)
        c = min(max(c, 0), self.w - 1)
        v = int(self.grid_for(self.step_for_year(year))[r, c])
        return self.palette[v]

    def areas(self, s):
        """km2 per palette index in step s, on a sphere of 6371.0088 km."""
        g = self.step(s)
        R = 6371.0088
        lat1 = np.radians(90.0 - np.arange(self.h) * 0.1)
        lat2 = np.radians(90.0 - (np.arange(self.h) + 1) * 0.1)
        rowkm = (R * R) * np.radians(0.1) * np.abs(np.sin(lat1) - np.sin(lat2))
        out = {}
        for i, (code, _n, _l, _s) in enumerate(self.palette):
            out[code] = float(((g == i).sum(axis=1) * rowkm).sum())
        return out


def check():
    pk = Pack()
    print("magic ok, version %d, %dx%d, %d steps %d..%d" %
          (VERSION, pk.w, pk.h, len(pk.years), pk.years[0], pk.years[-1]))
    print("palette %d entries, land cells %d, total changes %d" %
          (len(pk.palette), pk.landCells, pk.totalChanges))
    for code, name, level, short in pk.palette:
        print("   %2d  %-42s %-20s %s" % (code, name, level, short))
    bad = 0
    t0 = time.time()
    g = pk.base().reshape(pk.h * pk.w)
    seen = 0
    for s, (y, raw) in enumerate(grids()):
        if s:
            pk.apply_diff(g, s - 1)
        want = to_palette(raw).reshape(pk.h * pk.w)
        n = int(np.count_nonzero(g != want))
        if n:
            bad += 1
            print("   step %2d (year %6d) MISMATCH in %d cells" % (s, y, n))
        seen += 1
    print("rebuilt all %d steps in %.1f s; %d mismatched, %d land cells"
          % (seen, time.time() - t0, bad, int(np.count_nonzero(g))))
    return 1 if bad else 0


PLACES = [
    ("Uruk, Sumer", 32.53, 45.83, -3000),
    ("Memphis, Egypt", 29.85, 31.26, -2500),
    ("Mohenjo-daro, Indus", 27.32, 68.14, -2500),
    ("Anyang, Shang", 36.10, 114.35, -1200),
    ("Babylon", 32.54, 44.42, -600),
    ("Athens", 37.98, 23.73, -400),
    ("Pataliputra, Maurya", 25.61, 85.14, -250),
    ("Rome", 41.89, 12.49, 100),
    ("Teotihuacan", 19.69, -98.84, 500),
    ("Chang'an, Tang", 34.27, 108.90, 750),
    ("Baghdad, Abbasid", 33.31, 44.36, 900),
    ("Cahokia, Mississippi", 38.65, -90.06, 1100),
    ("Angkor, Khmer", 13.41, 103.87, 1200),
    ("Great Zimbabwe", -20.27, 30.93, 1400),
    ("Tenochtitlan, Aztec", 19.43, -99.13, 1500),
    ("Vijayanagara", 15.32, 76.46, 1500),
    ("Edo, Japan", 35.69, 139.69, 1700),
    ("London", 51.51, -0.13, 1800),
    ("Manchester", 53.48, -2.24, 1850),
    ("Punjab canal colony", 30.50, 73.00, 1900),
    ("Manhattan", 40.78, -73.97, 1900),
    ("Delhi", 28.61, 77.21, 1900),
    ("Bengal delta", 23.50, 89.50, 1900),
    ("Amazon, near Manaus", -3.10, -60.02, 1500),
    ("Sahel, Timbuktu", 16.77, -3.00, 1000),
    ("Iceland, Thingvellir", 64.15, -21.13, 1000),
    ("Greenland ice sheet", 72.00, -40.00, 1000),
    ("Sahara, Ahaggar", 23.00, 6.00, 1000),
    ("Siberia, Yakutsk", 62.03, 129.73, 1900),
    ("Great Plains, Kansas", 38.50, -98.00, 1870),
]


def places():
    pk = Pack()
    print("%-24s %8s  %-42s %-20s %s" % ("place", "year", "class", "level", "answer"))
    for name, lat, lon, year in PLACES:
        code, cls, level, short = pk.at(lat, lon, year)
        print("%-24s %8d  %-42s %-20s %s" % (name, year, cls, level, short))
    return 0


def load_hyde(kind):
    """{year: {region: km2}} from one of HYDE 3.3's regional tables, plus the Total row."""
    path = "/tmp/hyde_%s.txt" % kind
    if not os.path.exists(path):
        print("missing %s" % path)
        return None
    lines = [l for l in open(path) if l.strip()]
    years = [int(x) for x in lines[0].split()[1:]]
    out = {}
    for line in lines[1:]:
        p = line.split()
        reg = p[0]
        for i, v in enumerate(p[1:]):
            out.setdefault(years[i], {})[reg] = float(v)
    return out


def hyde_check():
    pk = Pack()
    crop = load_hyde("cropland_r")
    past = load_hyde("pasture_r")
    if not crop or not past:
        return 1
    # which palette codes answer to HYDE's cropland, and which to its pasture
    crop_codes = [c for c, _n, lv, _s in pk.palette if lv == "Croplands"]
    village_codes = [c for c, _n, lv, _s in pk.palette if lv == "Villages" and c != 24]
    range_codes = [c for c, _n, lv, _s in pk.palette if lv == "Rangelands"] + [24]
    s_of = {y: i for i, y in enumerate(pk.years)}
    print("thousand km2. Anthromes counts a whole square as cropland where cropping dominates it;")
    print("HYDE counts the cropped area inside it, so the grid runs high. The two agree on the trend.")
    print("%8s | %10s %10s %6s | %11s %11s %6s"
          % ("year", "grid crops", "HYDE crops", "ratio", "grid grazing", "HYDE pasture", "ratio"))
    rows = []
    for y in sorted(set(s_of) & set(crop)):
        if y < 1700:
            continue
        a = pk.areas(s_of[y])
        gc = sum(a[c] for c in crop_codes) / 1e3
        gv = sum(a[c] for c in village_codes) / 1e3
        gr = sum(a[c] for c in range_codes) / 1e3
        hc = crop[y]["Total"] / 1e3
        hp = past[y]["Total"] / 1e3
        rows.append((y, gc, hc, gr, hp))
    for y, gc, hc, gr, hp in rows:
        if y in (1700, 1750, 1800, 1850, 1900, 1950, 1980, 2000, 2015):
            print("%8d | %10.0f %10.0f %6.2f | %11.0f %11.0f %6.2f"
                  % (y, gc, hc, gc / max(1.0, hc), gr, hp, gr / max(1.0, hp)))
    xs = [r[1] for r in rows]
    ys = [r[2] for r in rows]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    r = cov / ((sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys)) ** 0.5)
    print("%d shared years 1700-2015: the grid's cropland and HYDE's correlate at r = %.4f"
          % (n, r))
    g0, h0 = rows[0][1], rows[0][2]
    print("growth 1700 -> 2015: grid x%.2f (%0.f -> %0.f), HYDE x%.2f (%0.f -> %0.f)"
          % (rows[-1][1] / g0, g0, rows[-1][1], rows[-1][2] / h0, h0, rows[-1][2]))
    print("grazing land and HYDE's managed pasture are different things: %.0f thousand km2 of"
          % rows[-1][3])
    print("grazing land in 2015 against %.0f of managed pasture, and that gap is the world's"
          % rows[-1][4])
    print("rangelands, which HYDE does not count as pasture.")
    return 0


if __name__ == "__main__":
    a = sys.argv[1] if len(sys.argv) > 1 else ""
    if a == "--check":
        sys.exit(check())
    if a == "--places":
        sys.exit(places())
    if a == "--hyde":
        sys.exit(hyde_check())
    build()
