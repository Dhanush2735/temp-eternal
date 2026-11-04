#!/usr/bin/env python3
"""HYDE 3.2.1 population, aggregated to a 0.5-degree grid, for the eras the mod needs.

HYDE 3.2.1 (Klein Goldewijk et al. 2017; DANS doi:10.17026/DANS-25G-GEZ3, CC0 1.0 on the
record) models how many people lived in every 5-arc-minute cell of the land, 10000 BC to
AD 2017. Its baseline is one 5.3 GB zip; this reads only the grids it needs from it with HTTP
range requests (remotezip.py): the population count (popc) for 28 time slices and the maximum
land area per cell (maxln_cr), then sums both into 0.5-degree cells.

Output: ~/.cache/srcdata/hyde_05deg.npz
    years   (S,)          the slice years (historical; HYDE's "0AD" is kept as year 0)
    popc    (S, 360, 720) people per 0.5-degree cell, float32; row 0 = southernmost row
    land    (360, 720)    land area per cell, km2 (HYDE maxln_cr)
"""
import io, os, re, sys, time, zipfile
import numpy as np
try:
    import zipfile_deflate64  # noqa: F401  HYDE's baseline zip uses Deflate64 (method 9)
except ImportError:
    sys.exit("pip install zipfile-deflate64   (HYDE's baseline zip uses Deflate64)")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import remotezip as R        # noqa: E402

BASELINE = "https://archaeology.datastations.nl/api/access/datafile/5490328"
SUPPLEMENT = "https://archaeology.datastations.nl/api/access/datafile/5490327"
OUT = os.path.join(os.environ.get("SRCDATA", "/home/user/.cache/srcdata"), "hyde_05deg.npz")
SLICES = [-3000, -2000, -1000, 0] + list(range(100, 1800, 100)) + [1750, 1800, 1850, 1900, 1950, 2000, 2017]
SLICES = sorted(set(SLICES))


def read_asc(data):
    """ESRI ASCII grid (bytes) -> (header dict, float32 array, nodata -> 0)."""
    head, pos = {}, 0
    for _ in range(6):
        nl = data.index(b"\n", pos)
        k, v = data[pos:nl].split()
        head[k.decode().lower()] = float(v)
        pos = nl + 1
    arr = np.fromstring(data[pos:], dtype=np.float32, sep=" ")       # text mode: parses in C
    n, m = int(head["nrows"]), int(head["ncols"])
    assert arr.size == n * m, (arr.size, n, m)
    arr = arr.reshape(n, m)
    arr[arr == head.get("nodata_value", -9999.0)] = 0.0
    arr[arr < 0] = 0.0
    return head, arr


def to_half_degree(arr, head):
    n, m = arr.shape
    assert abs(head["cellsize"] - 1 / 12) < 1e-6 and n == 2160 and m == 4320, head
    agg = arr.reshape(360, 6, 720, 6).sum(axis=(1, 3), dtype=np.float64).astype(np.float32)
    return agg[::-1].copy()          # ASC row 0 is the north; ours is the south


def name_for(y):
    return f"{abs(y)}{'BC' if y < 0 else 'AD'}"


def main():
    if os.path.exists(OUT):
        print("exists:", OUT)
        return
    t0 = time.time()
    sup = R.open_remote_zip(SUPPLEMENT)
    head, land = read_asc(sup.read("general_files/maxln_cr.asc"))
    land05 = to_half_degree(land, head)
    del land
    print(f"land: {land05.sum():.4g} km2 in 0.5-degree cells ({time.time() - t0:.0f}s)", flush=True)
    z = R.open_remote_zip(BASELINE)
    names = set(z.namelist())
    popc = np.zeros((len(SLICES), 360, 720), dtype=np.float32)
    for i, y in enumerate(SLICES):
        member = f"baseline/asc/{name_for(y)}_pop/popc_{name_for(y)}.asc"
        assert member in names, member
        head, arr = read_asc(z.read(member))
        popc[i] = to_half_degree(arr, head)
        del arr
        print(f"  {y:6d}: {popc[i].sum() / 1e6:9.1f} million people ({time.time() - t0:.0f}s)", flush=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    np.savez_compressed(OUT, years=np.array(SLICES, dtype=np.int32), popc=popc, land=land05)
    print("wrote", OUT, f"({os.path.getsize(OUT) / 1e6:.1f} MB, {time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
