#!/usr/bin/env python3
"""Data-use check, part 1: population-weighted sample points for probes/DataUseProbe.java.

Each point stands for an equal share of the world's people in its year (HYDE 3.2.1 grid, the mod's
own population/hyde_density.bin.gz), placed at a random spot inside its 0.5-degree cell.
Writes ~/.cache/data_use/points.tsv (year, lat, lon). Usage: python3 data_use_sample.py [points-per-year]
"""
import os
import sys

import numpy as np

sys.path.insert(0, "/home/user/worldfill")
sys.path.insert(0, "/home/user/harvest")
import build_regional as BR  # noqa: E402

YEARS = [-1000, -500, 1, 500, 1000, 1300, 1500, 1700, 1800, 1850, 1900, 1950, 2000, 2020]
OUT = os.path.expanduser("~/.cache/data_use/points.tsv")


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    hyde = BR.Hyde()
    cells = np.nonzero(hyde.cell >= 0)[0]
    lat0 = -90 + (cells // 720) * 0.5
    lon0 = -180 + (cells % 720) * 0.5
    rng = np.random.default_rng(12)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        for y in YEARS:
            ppl = hyde.people(lat0 + 0.25, lon0 + 0.25, y)
            pick = rng.choice(len(cells), size=n, p=ppl / ppl.sum())
            for i in pick:
                f.write(f"{y}\t{lat0[i] + rng.random() * 0.5:.4f}\t{lon0[i] + rng.random() * 0.5:.4f}\n")
    print("wrote", OUT, n * len(YEARS), "points")


if __name__ == "__main__":
    main()
