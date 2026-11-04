"""
Step 44 part 3 (E5 part C): which of the product atlas's 17 areas each country lies in.

The technology atlas (130 technologies, each with an arrival year for 258 countries) is the
source part C is derived from, but it names its countries by ISO3 code and gives no
coordinates. To turn "steel reaches Germany in 1856" into "steel is made in EUR by 1856", each
country has to be placed in an area.

Rather than hand-write 258 codes, this reads the mod's own 0.1-degree country grid
(`history/countries.grid.gz`) and gives each country the area that most of its land lies in --
so Russia is not judged by its centroid, and France is not placed by French Guiana.

The area rule is **ported line for line** from `ProductAtlas.boxArea`, so a country is placed
by the same test the game itself uses for a point outside every survey region. If that rule
ever changes, this must change with it.
"""

import gzip
import os
import struct
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
GRID = os.path.normpath(os.path.join(HERE, "..", "eternal", "src", "main", "resources",
                                     "data", "eternalengine", "eternal", "history",
                                     "countries.grid.gz"))
MAGIC = 0x45454347


def box_area(lat, lon):
    """Ported from ProductAtlas.boxArea. Keep the two in step."""
    if lon < -130 or lon >= 170:
        if lat >= 50:
            return "EEU" if lon >= 170 else "NNA"
        return "AUS" if lat <= -32 else "PAC"
    if lon < -25:
        if lat >= 55:
            return "NNA"
        if lat >= 24:
            return "MNA"
        return "CAC" if (lat >= 13 or (lat >= 7 and lon < -77)) else "SAM"
    if lat >= 55:
        return "EUR" if lon < 25 else "EEU"
    if lon < 40 and lat >= 36:
        return "EUR" if lon < 26 else ("EEU" if lat >= 43 else "WAS")
    if lat < 37 and lon < 52 and (lon < 34 or lat < 12.5):
        if lat >= 18 or (lat >= 9 and lon >= 22 and lon < 36):
            return "NAF"
        if lat >= 0 and lon < 22:
            return "WAF"
        return "EAF" if (lon >= 30 and lat >= -27) else "MSA"
    if lon < 63 and lat < 43:
        return "WAS"
    if lat >= 45:
        return "EEU" if lon < 50 else ("CAS" if lon < 90 else "EAS")
    if lon < 92.5:
        if lat >= 37 or lon < 60:
            return "CAS"
        return "EAS" if (lat >= 30.5 and lon >= 78) else "SAS"
    if lon < 98:
        return "EAS" if lat >= 28 else "SEA"
    if lon < 150:
        if lat >= 21.5 or (lat >= 18 and lon >= 108 and lon < 117):
            return "EAS"
        if lat >= -11 and lon < 141:
            return "SEA"
        return "PAC" if lat >= 0 else "AUS"
    return "EAS" if lat >= 30 else ("PAC" if lat >= 0 else "AUS")


def _read_utf(f):
    n = struct.unpack(">H", f.read(2))[0]
    return f.read(n).decode("utf-8")


def read_grid():
    """(codes, names, {(lat, lon): country index}) for the 0.1-degree grid."""
    with gzip.open(GRID, "rb") as f:
        if struct.unpack(">i", f.read(4))[0] != MAGIC:
            raise ValueError("not a country grid")
        struct.unpack(">i", f.read(4))[0]        # version
        w, h, n = struct.unpack(">iii", f.read(12))
        codes, names = [], []
        for _ in range(n):
            codes.append(_read_utf(f))
            names.append(_read_utf(f))
            _read_utf(f)                          # sub
            f.read(8)                             # two floats, unused
            f.read(8)                             # centroid lat, lon
            f.read(4)                             # an int, unused
        cells = {}
        for y in range(h):
            k = struct.unpack(">i", f.read(4))[0]
            raw = f.read(4 * k)
            runs = struct.unpack(">%dh" % (2 * k), raw)
            acc = 0
            for j in range(0, 2 * k, 2):
                length = runs[j] & 0xFFFF
                value = runs[j + 1] & 0xFFFF
                if value > 0:
                    ci = value - 1
                    for x in range(acc, acc + length):
                        lat = 90.0 - y * 0.1 - 0.05
                        lon = -180.0 + x * 0.1 + 0.05
                        cells[(y, x)] = (ci, lat, lon)
                acc += length
    return codes, names, cells, w, h


def country_areas():
    """{ISO3: area id} -- the area holding most of each country's land."""
    codes, names, cells, w, h = read_grid()
    per = collections.defaultdict(collections.Counter)
    for ci, lat, lon in cells.values():
        per[ci][box_area(lat, lon)] += 1
    out = {}
    for ci, counts in per.items():
        if 0 <= ci < len(codes):
            out[codes[ci]] = counts.most_common(1)[0][0]
    return out, codes, names


if __name__ == "__main__":
    areas, codes, names = country_areas()
    problems = []
    if not areas:
        problems.append("no countries were placed")
    by_area = collections.Counter(areas.values())
    print("countries placed: %d of %d" % (len(areas), len(codes)))
    for a, n in by_area.most_common():
        print("   %-4s %3d  %s" % (a, n, ", ".join(sorted(c for c, v in areas.items() if v == a)[:8])))
    for want in ("IND", "GBR", "CHN", "RUS", "USA", "BRA", "NGA", "AUS", "FRA", "JPN"):
        if want in areas:
            print("   %s -> %s" % (want, areas[want]))
        else:
            problems.append(f"{want} is not in the grid")
    for p in problems:
        print("  PROBLEM " + p)
    print("country_areas: %d problem(s)" % len(problems))
