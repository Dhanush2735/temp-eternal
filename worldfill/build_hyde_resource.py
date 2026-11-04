#!/usr/bin/env python3
"""Step 4: write HYDE 3.2.1 population density as a small binary resource the mod can read.

Input: ~/.cache/srcdata/hyde_05deg.npz (hyde_grid.py): people and land area per 0.5-degree cell
for 28 time slices, 3000 BC - AD 2017.

Output: eternal/.../population/hyde_density.bin.gz, read by com.eternalengine.population.HydeGrid:

    magic "HYD1" | int cellMilliDegrees (500) | int slices | int[slices] years
    int cells | per cell: int index (row * 720 + col, row 0 = southernmost) | byte[slices] code

    code 0      : fewer than 0.005 people per km2 (nobody, for the mod's purposes)
    code 1..255 : density = 10 ^ ((code - 1) / 40 - 2.3) people per km2 of land
                  (40 steps per factor of ten, about 6% apart; 0.005 .. ~11,000 per km2)

Only cells with land are written. Density is people / HYDE's maximum land area of the cell.
"""
import gzip, io, os, struct, sys
import numpy as np

SRC = os.path.join(os.environ.get("SRCDATA", "/home/user/.cache/srcdata"), "hyde_05deg.npz")
OUT = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/population/hyde_density.bin.gz"
MIN_D = 0.005


def encode(d):
    code = np.zeros(d.shape, dtype=np.int32)
    ok = d >= MIN_D
    code[ok] = 1 + np.rint((np.log10(d[ok]) + 2.3) * 40).astype(np.int32)
    return np.clip(code, 0, 255).astype(np.uint8)


def decode(code):
    return np.where(code > 0, 10.0 ** ((code.astype(np.float64) - 1) / 40 - 2.3), 0.0)


def main():
    z = np.load(SRC)
    years, popc, land = z["years"], z["popc"], z["land"]
    landm = land > 0
    dens = np.where(landm[None], popc / np.maximum(land, 1e-9)[None], 0.0)
    codes = encode(dens)                                     # (S, 360, 720)
    idx = np.flatnonzero(landm.ravel())
    per_cell = codes.reshape(len(years), -1)[:, idx].T       # (cells, S)
    buf = io.BytesIO()
    buf.write(b"HYD1")
    buf.write(struct.pack(">ii", 500, len(years)))
    buf.write(struct.pack(">%di" % len(years), *[int(y) for y in years]))
    buf.write(struct.pack(">i", len(idx)))
    rec = np.zeros(len(idx), dtype=[("i", ">i4"), ("c", "u1", (len(years),))])
    rec["i"] = idx
    rec["c"] = per_cell
    buf.write(rec.tobytes())
    raw = buf.getvalue()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(raw)
    # round trip + error of the 8-bit code against the real densities
    back = decode(per_cell.T)
    real = dens.reshape(len(years), -1)[:, idx]
    m = real >= MIN_D
    rel = np.abs(back[m] - real[m]) / real[m]
    world = [float((decode(codes[i]) * land).sum() / 1e6) for i in range(len(years))]
    true = [float(popc[i].sum() / 1e6) for i in range(len(years))]
    print(f"cells {len(idx)}, slices {len(years)}: {years.tolist()}")
    print(f"raw {len(raw) / 1e6:.2f} MB, gzipped {os.path.getsize(OUT) / 1e6:.2f} MB -> {OUT}")
    print(f"8-bit density error: median {np.median(rel) * 100:.2f}%, max {rel.max() * 100:.2f}%")
    print("world population from the resource vs HYDE (millions):")
    for y, a, b in zip(years.tolist(), world, true):
        if y in (-3000, -1000, 0, 1000, 1500, 1800, 1900, 2000, 2017):
            print(f"  {y:6d}  {a:8.1f}  {b:8.1f}")


if __name__ == "__main__":
    main()
