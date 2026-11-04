#!/usr/bin/env python3
"""Step 35, part 3: measure Anthromes 12K before deciding how to pack it.

Reads build/land/raw/anthromes_12K_full.zip (Harvard Dataverse, CC0) once, resamples every step to
0.1 degrees (3600 x 1800, the same grid as history/countries.grid.gz) by taking the 5-arcminute
cell that holds the centre of each 0.1 degree cell, and reports:

    python3 measure_anthromes.py            per-step class histogram, cells changed per transition
    python3 measure_anthromes.py --save     also write every resampled step to /tmp/anth/ (uint8)

Nothing is written into the mod by this script. It exists to measure, not to build.
"""
import collections
import io
import os
import re
import sys
import time
import zipfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ZIP = os.path.join(HERE, "build", "land", "raw", "anthromes_12K_full.zip")
CACHE = "/tmp/anth"          # resampled steps, so a second pass does not re-read the 47 MB zip

NROWS, NCOLS = 2160, 4320          # the source grid, 5 arcminutes
H, W = 1800, 3600                  # the packed grid, 0.1 degrees
OCEAN = 0
NODATA = -9999

# Class names, Table 1 of Ellis, Beusen and Klein Goldewijk (2020) "Anthropogenic Biomes: 10,000
# BCE to 2015 CE", Land 9(5):129, which is the paper the Anthromes 12K dataset is published with.
NAMES = {
    11: "Urban",
    12: "Mixed settlements",
    21: "Rice villages",
    22: "Irrigated villages",
    23: "Rainfed villages",
    24: "Pastoral villages",
    31: "Residential irrigated croplands",
    32: "Residential rainfed croplands",
    33: "Populated rainfed croplands",
    34: "Remote croplands",
    41: "Residential rangelands",
    42: "Populated rangelands",
    43: "Remote rangelands",
    51: "Residential woodlands",
    52: "Populated woodlands",
    53: "Remote woodlands",
    54: "Inhabited treeless and barren lands",
    61: "Wild woodlands",
    62: "Wild treeless and barren lands",
    63: "Ice, uninhabited",
    70: "Ice, uninhabited (stray code in the grids)",
}
# The six levels of the classification, and a one-word answer for the game.
LEVEL = {11: "settlement", 12: "settlement",
         21: "village", 22: "village", 23: "village", 24: "village",
         31: "cropland", 32: "cropland", 33: "cropland", 34: "cropland",
         41: "rangeland", 42: "rangeland", 43: "rangeland",
         51: "woodland", 52: "woodland", 53: "woodland", 54: "woodland",
         61: "wild", 62: "wild", 63: "ice", 70: "ice"}

# row/col of the 5-arcminute cell holding the centre of each 0.1 degree cell
RS = np.floor((np.arange(H) + 0.5) * 1.2).astype(np.int32)
CS = np.floor((np.arange(W) + 0.5) * 1.2).astype(np.int32)


def steps():
    """[(year, inner zip name)] earliest first."""
    z = zipfile.ZipFile(ZIP)
    out = []
    for n in z.namelist():
        m = re.match(r"^(\d+)(BC|AD)_anthromes\.zip$", n)
        if m:
            v = int(m.group(1))
            out.append((-v if m.group(2) == "BC" else v, n))
    out.sort()
    return out


def load_raw(z, name):
    """One step as a 5-arcminute int16 grid with NODATA for ocean."""
    inner = zipfile.ZipFile(io.BytesIO(z.read(name)))
    txt = inner.read(inner.namelist()[0]).decode("ascii", "replace")
    lines = txt.split("\n")
    i = 0
    while i < len(lines):
        p = lines[i].split()
        if len(p) == 2 and p[0].lower() in ("ncols", "nrows", "xllcorner", "yllcorner",
                                            "cellsize", "nodata_value"):
            i += 1
        else:
            break
    a = np.array(" ".join(lines[i:]).split(), dtype=np.int16).reshape(NROWS, NCOLS)
    return a


def resample(a):
    """5 arcminutes -> 0.1 degrees by nearest centre; NODATA becomes OCEAN."""
    b = a[np.ix_(RS, CS)]
    return np.where(b < 0, OCEAN, b).astype(np.uint8)


def load(z, name):
    """One step resampled to 0.1 degrees, as uint8 with 0 for ocean."""
    return resample(load_raw(z, name))


def main():
    save = "--save" in sys.argv
    if save:
        os.makedirs("/tmp/anth", exist_ok=True)
    z = zipfile.ZipFile(ZIP)
    items = steps()
    print("%d steps, %d .. %d" % (len(items), items[0][0], items[-1][0]))
    t0 = time.time()
    prev = None
    prevy = None
    total = 0
    hist_all = collections.Counter()
    stray = np.zeros((H, W), dtype=bool)
    land0 = None
    for y, name in items:
        g = load(z, name)
        if land0 is None:
            land0 = g != OCEAN
        else:
            # the land mask must be the same in every step, or the diffs are meaningless
            lm = g != OCEAN
            if not np.array_equal(lm, land0):
                n = int(np.count_nonzero(lm != land0))
                print("  WARNING: land mask differs from the first step in %d cells" % n)
        stray |= (g == 70)
        c = collections.Counter(g.ravel().tolist())
        hist_all.update(c)
        if save:
            g.tofile("/tmp/anth/%05d.bin" % (y + 10000))
        if prev is not None:
            d = int(np.count_nonzero(g != prev))
            total += d
            print("%6d -> %6d  changed %8d  (%5.2f%% of land)" %
                  (prevy, y, d, 100.0 * d / max(1, int(np.count_nonzero(land0)))), flush=True)
        prev, prevy = g, y
    print("land cells (0.1 deg): %d of %d" % (int(np.count_nonzero(land0)), H * W))
    print("total changed cells over %d transitions: %d" % (len(items) - 1, total))
    print("class histogram over all steps:")
    for k in sorted(hist_all):
        print("   %2d %-42s %10d" % (k, NAMES.get(k, "?"), hist_all[k]))
    ys, xs = np.nonzero(stray)
    print("cells that are ever class 70: %d" % len(ys))
    for r, c in list(zip(ys, xs))[:20]:
        print("   row %4d col %4d  lat %7.2f lon %8.2f" % (r, c, 90.0 - (r + 0.5) / 10.0,
                                                           -180.0 + (c + 0.5) / 10.0))
    print("%.1f s" % (time.time() - t0))


if __name__ == "__main__":
    main()
