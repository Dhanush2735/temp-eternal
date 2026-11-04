#!/usr/bin/env python3
"""Step 35 (B23, part 2): every eclipse of the Sun and the Moon, with the geometry to place it.

Usage:
    python3 build_sky_eclipses.py              build history/sky_eclipses.bin.gz
    python3 build_sky_eclipses.py --check      read the pack back and report
    python3 build_sky_eclipses.py --places     what the 31 test places saw, in their own year
    python3 build_sky_eclipses.py --selftest  the geometry against NASA's own numbers

Sources (both public domain, US government work):
  * Solar: NASA's Five Millennium Catalogue of Solar Eclipses, -1999 to +3000, as the Besselian
    elements dump `eclipse_besselian_from_mysqldump2.csv` (11,898 eclipses).
  * Lunar: NASA's Five Millennium Catalogue of Lunar Eclipses, fetched century by century by
    `fetch_lunar_eclipses.py` (12,064 eclipses).

Why the pack carries the Besselian elements rather than a list of paths. A table of paths would
have to choose a resolution and would only ever answer "inside or outside"; the elements are what
NASA itself publishes, and from them a place's own circumstances can be computed exactly -- how
deep the eclipse was *there*, not merely whether it was somewhere. The register runs the same
geometry this script does, in Java, for the place the player is standing in.

The three things that had to be got right, each found by a failing check:

1. **The polynomials are not centred on greatest eclipse.** Evaluating x, y at t = 0 gives a point
   a degree or two from NASA's "point of greatest eclipse"; the least distance from the axis to
   the Earth's centre is at t* = a few minutes away, and it reproduces NASA's `gamma` to five
   decimal places. So the greatest point is found by minimising x(t)^2 + y(t)^2.
2. **The hour angle mu is in Terrestrial Time, not universal time.** The Earth's clock error
   Delta-T has to come off it -- 1/240 of a degree per second. For a modern eclipse that is a
   minute of longitude; for the eclipse of 585 BCE it is **five hours**, and without it Thales'
   eclipse lands 77 degrees away, in the Pacific.
3. **The umbral radius l2 is (Sun's radius - Moon's radius), not the other way round** -- it is
   negative for a total eclipse. The magnitude at a place is (l1' - D) / (l1' + l2'), where D is
   the distance from the place to the axis and the cone radii are corrected to the observer's own
   plane by l' = l - zeta * tan f. This reproduces NASA's published magnitudes to 1e-4, and gives
   0 on the penumbral edge and exactly 1 on the umbral edge, which is how it was checked.
"""
import argparse
import csv
import gzip
import json
import math
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sky_time
import fetch_lunar_eclipses

MOD = os.path.join(HERE, "..", "eternal")
OUT = os.path.join(MOD, "src", "main", "resources", "data", "eternalengine",
                   "eternal", "history", "sky_eclipses.bin.gz")
SOLAR = os.path.join(HERE, "build", "sky", "raw", "solar_eclipses_besselian.csv")

MAGIC = 0x45434C53          # "ECLS"
VERSION = 1

# Every eclipse in the catalogue carries polynomials valid over the same three hours either side
# of greatest eclipse, so the range is a property of the format rather than of the record.
TMIN, TMAX = -3.0, 3.0
FLATTENING = 1.0 / 298.257223563

# the record: 25 signed 32-bit integers, little endian (100 bytes). Fixed width, so the register
# can binary search the year without parsing anything else. One cone angle is stored rather than
# two: tan f1 and tan f2 differ in the fourth decimal, which moves the umbral radius by 2e-5
# Earth radii -- a hundred metres of shadow edge.
FIELDS = 25
SOLAR_RECORD = FIELDS * 4

SOLAR_PARTIAL, SOLAR_ANNULAR, SOLAR_TOTAL, SOLAR_HYBRID = 0, 1, 2, 3
LUNAR_PENUMBRAL, LUNAR_PARTIAL, LUNAR_TOTAL = 0, 1, 2

# the 31 test places, as every register knows them (step 31)
TEST_PLACES = [
    ("Ur", 30.9625, 46.1031, -2500), ("Mohenjo-daro", 27.3245, 68.1375, -2500),
    ("Giza", 29.9792, 31.1342, -2500), ("Anyang", 36.0996, 114.3524, -1200),
    ("Zhouyuan", 34.4936, 107.8128, -1000), ("Rome", 41.8925, 12.4853, 100),
    ("Chang'an", 34.2657, 108.9457, 700), ("Baghdad", 33.3128, 44.3615, 900),
    ("Cahokia", 38.6536, -90.2459, 1100), ("Angkor", 13.4125, 103.8669, 1150),
    ("Cusco", -13.5163, -71.9785, 1500), ("Tenochtitlan", 19.4348, -99.1313, 1500),
    ("Vijayanagara", 15.3350, 76.4600, 1520), ("Delhi", 28.6139, 77.2090, 1650),
    ("Edo", 35.6852, 139.7528, 1700), ("London", 51.5074, -0.1278, 1700),
    ("Paris", 48.8566, 2.3522, 1789), ("Sydney", -33.8688, 151.2093, 1850),
    ("New York", 40.7128, -74.0060, 1920), ("Moscow", 55.7520, 37.6175, 1980),
    ("Sao Paulo", -23.5505, -46.6333, 2020), ("Lagos", 6.5244, 3.3792, 1960),
    ("Cape Town", -33.9249, 18.4241, 1900), ("Yakutsk", 62.0355, 129.6755, 1900),
    ("Reykjavik", 64.1466, -21.9426, 1900), ("Greenland Norse", 60.9500, -45.4200, 1000),
    ("Great Zimbabwe", -20.2675, 30.9339, 1400), ("Timbuktu", 16.7735, -3.0074, 1350),
    ("the Amazon", -3.1000, -60.0200, 1500), ("the Sahara", 23.4162, 25.6628, 1000),
    ("Hyderabad", 17.3850, 78.4867, 1948),
]


# ---------------------------------------------------------------------------
# the geometry
# ---------------------------------------------------------------------------

def norm(v):
    return math.sqrt(sum(c * c for c in v))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def poly(c0, c1, c2, c3, t):
    return c0 + t * (c1 + t * (c2 + t * c3))


def axis_point(x, y, d_deg, mu_deg, dt_s):
    """Where the shadow axis meets the Earth, from the elements at one instant.

    x, y    : where the axis crosses the fundamental plane, in Earth radii
    d_deg   : declination of the axis
    mu_deg  : its Greenwich hour angle, in Terrestrial Time
    dt_s    : Delta-T in seconds, which turns Terrestrial Time into the Earth's own rotation
    """
    zeta = math.sqrt(max(0.0, 1.0 - x * x - y * y))
    d = math.radians(d_deg)
    lam = math.radians(-(mu_deg - dt_s / 240.0))
    z = (math.cos(d) * math.cos(lam), math.cos(d) * math.sin(lam), math.sin(d))
    yn = (-z[2] * z[0], -z[2] * z[1], 1.0 - z[2] * z[2])
    n = norm(yn)
    yh = tuple(v / n for v in yn)
    xh = cross(yh, z)
    p = tuple(x * xh[i] + y * yh[i] + zeta * z[i] for i in range(3))
    lat_gc = math.degrees(math.asin(max(-1.0, min(1.0, p[2]))))
    lon = math.degrees(math.atan2(p[1], p[0]))
    lat = math.degrees(math.atan(math.tan(math.radians(lat_gc)) / (1.0 - FLATTENING) ** 2))
    return lat, lon


def observer_plane(lat_deg, lon_deg, d_deg, mu_deg, dt_s):
    """A place's (xi, eta, zeta) in the fundamental plane at one instant.

    zeta is how far the place is above the fundamental plane, towards the Sun: positive means
    the Sun is up there, which is the only case in which an eclipse can be seen at all.
    """
    lat_gc = math.atan(math.tan(math.radians(lat_deg)) * (1.0 - FLATTENING) ** 2)
    d = math.radians(d_deg)
    lam = math.radians(-(mu_deg - dt_s / 240.0))
    z = (math.cos(d) * math.cos(lam), math.cos(d) * math.sin(lam), math.sin(d))
    yn = (-z[2] * z[0], -z[2] * z[1], 1.0 - z[2] * z[2])
    n = norm(yn)
    yh = tuple(v / n for v in yn)
    xh = cross(yh, z)
    p = (math.cos(lat_gc) * math.cos(math.radians(lon_deg)),
         math.cos(lat_gc) * math.sin(math.radians(lon_deg)),
         math.sin(lat_gc))
    return (sum(p[i] * xh[i] for i in range(3)),
            sum(p[i] * yh[i] for i in range(3)),
            sum(p[i] * z[i] for i in range(3)))


def elements_at(e, t):
    """(x, y, d, mu, l1, l2) at t hours from the reference instant."""
    return (poly(e["x0"], e["x1"], e["x2"], e["x3"], t),
            poly(e["y0"], e["y1"], e["y2"], e["y3"], t),
            poly(e["d0"], e["d1"], e["d2"], 0.0, t),
            poly(e["mu0"], e["mu1"], e["mu2"], 0.0, t),
            poly(e["l10"], e["l11"], e["l12"], 0.0, t),
            poly(e["l20"], e["l21"], e["l22"], 0.0, t))


def greatest_of(e):
    """The instant of greatest eclipse: where the axis comes closest to the Earth's centre."""
    lo, hi = e["tmin"], e["tmax"]
    best_t, best_q = lo, None
    steps = 4000
    for i in range(steps + 1):
        t = lo + (hi - lo) * i / steps
        x, y = elements_at(e, t)[0], elements_at(e, t)[1]
        q = x * x + y * y
        if best_q is None or q < best_q:
            best_q, best_t = q, t
    step = (hi - lo) / steps
    for _ in range(40):
        step *= 0.5
        for t in (best_t - step, best_t + step):
            x, y = elements_at(e, t)[0], elements_at(e, t)[1]
            if x * x + y * y < best_q:
                best_q, best_t = x * x + y * y, t
    return best_t, math.sqrt(best_q)


def local_magnitude(e, lat, lon):
    """How deep the eclipse was at one place: >1 total, 0..1 partial, <0 not visible there.

    This is the number the register will report, and it is the same geometry NASA uses: for each
    instant the place's distance from the axis is compared with the shadow's own radius, the
    cone radii being corrected to the plane the observer is standing in.
    """
    best = -1.0
    lo, hi = e["tmin"], e["tmax"]
    steps = 160
    for i in range(steps + 1):
        t = lo + (hi - lo) * i / steps
        x, y, d, mu, l1, l2 = elements_at(e, t)
        xi, eta, zeta = observer_plane(lat, lon, d, mu, e["dt"])
        if zeta <= 0.0:
            continue                      # the Sun is below the horizon there
        dist = math.hypot(x - xi, y - eta)
        l1p = l1 - zeta * e["tan_f1"]
        l2p = l2 - zeta * e["tan_f2"]
        denom = l1p + l2p                  # twice the Sun's radius, in these units
        if dist <= abs(l2p):
            # inside the umbra (or the antumbra): one disc lies wholly inside the other, and the
            # magnitude is the ratio of the two diameters -- above 1 for a total eclipse, below
            # 1 for an annular one. l2 is (Sun - Moon), so it is negative where the Moon is
            # the bigger of the two.
            m = (l1p - l2p) / denom
        else:
            m = (l1p - dist) / denom       # the fraction of the Sun's diameter that is covered
        if m > best:
            best = m
    return best


def local_lunar(e, lat, lon):
    """Was a lunar eclipse above the horizon at this place, and how deep?

    A lunar eclipse is visible from anywhere the Moon is up, which is half the Earth; the
    catalogue gives the point where the Moon stood in the zenith, so a place sees it if it is
    within a quarter of the Earth's circumference of that point.
    """
    d = haversine_km(lat, lon, e["zenithLat"], e["zenithLon"])
    return d <= 10000.0, d


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


# ---------------------------------------------------------------------------
# reading the two catalogues
# ---------------------------------------------------------------------------

def type_code(t):
    t = t[0].upper()
    if t == "P":
        return SOLAR_PARTIAL
    if t == "A":
        return SOLAR_ANNULAR
    if t == "H":
        return SOLAR_HYBRID
    return SOLAR_TOTAL


def read_solar():
    """Every solar eclipse, as the pack will store it."""
    if not os.path.exists(SOLAR):
        sys.exit("missing %s -- fetch the NASA Besselian dump first" % SOLAR)
    out = []
    for row in csv.DictReader(open(SOLAR)):
        f = lambda k: float(row[k])
        e = {
            "x0": f("x0"), "x1": f("x1"), "x2": f("x2"), "x3": f("x3"),
            "y0": f("y0"), "y1": f("y1"), "y2": f("y2"), "y3": f("y3"),
            "d0": f("d0"), "d1": f("d1"), "d2": f("d2"),
            "mu0": f("mu0"), "mu1": f("mu1"), "mu2": f("mu2"),
            "l10": f("l10"), "l11": f("l11"), "l12": f("l12"),
            "l20": f("l20"), "l21": f("l21"), "l22": f("l22"),
            "tan_f1": f("tan_f1"), "tan_f2": f("tan_f2"),
            "dt": f("dt"), "tmin": TMIN, "tmax": TMAX,
            "nasa_mag": f("magnitude"), "nasa_gamma": abs(f("gamma")),
            "nasa_lat": f("lat_dd_ge"), "nasa_lon": f("lng_dd_ge"),
            "nasa_type": row["eclipse_type"][0].upper(),
            "saros": int(f("saros")) if row["saros"] not in ("", None) else 0,
        }
        # the date, moved from NASA's calendar (Julian before 1582) onto the mod's. The
        # catalogue's own date is kept too, so the self-test can find an eclipse by the date
        # NASA publishes it under.
        e["nasa_year"], e["nasa_month"], e["nasa_day"] = (int(row["year"]), int(row["month"]),
                                                          int(row["day"]))
        y, m, d = sky_time.nasa_to_mod(int(row["year"]), int(row["month"]), int(row["day"]))
        e["year"], e["month"], e["day"] = y, m, d
        e["code"] = type_code(row["eclipse_type"])
        out.append(e)
    out.sort(key=lambda e: (e["year"], e["month"], e["day"]))
    return out


def read_lunar():
    out = []
    for r in fetch_lunar_eclipses.parse_all():
        y, m, d = sky_time.nasa_to_mod(r["year"], r["month"], r["day"])
        code = LUNAR_TOTAL if r["type"].startswith("T") else (
            LUNAR_PARTIAL if r["type"].startswith("P") else LUNAR_PENUMBRAL)
        out.append({
            "year": y, "month": m, "day": d, "code": code,
            "umbMag": r["umbMag"], "penMag": r["penMag"],
            "zenithLat": r["zenithLat"], "zenithLon": r["zenithLon"],
            "durTot": r["durTot"], "durPar": r["durPar"], "saros": r["saros"],
        })
    out.sort(key=lambda e: (e["year"], e["month"], e["day"]))
    return out


# ---------------------------------------------------------------------------
# the pack
# ---------------------------------------------------------------------------

def pack_solar(e):
    """One solar eclipse as 24 int32s."""
    return struct.pack("<25i",
                       (e["year"] + 2000) * 10000 + e["month"] * 100 + e["day"],
                       e["code"],
                       int(round(e["nasa_mag"] * 1000.0)),
                       int(round(e["x0"] * 1e9)), int(round(e["x1"] * 1e9)),
                       int(round(e["x2"] * 1e9)), int(round(e["x3"] * 1e9)),
                       int(round(e["y0"] * 1e9)), int(round(e["y1"] * 1e9)),
                       int(round(e["y2"] * 1e9)), int(round(e["y3"] * 1e9)),
                       int(round(e["d0"] * 1e6)), int(round(e["d1"] * 1e6)),
                       int(round(e["d2"] * 1e6)),
                       int(round(e["mu0"] * 1e6)), int(round(e["mu1"] * 1e6)),
                       int(round(e["mu2"] * 1e6)),
                       int(round(e["l10"] * 1e7)), int(round(e["l11"] * 1e7)),
                       int(round(e["l12"] * 1e7)),
                       int(round(e["l20"] * 1e7)), int(round(e["l21"] * 1e7)),
                       int(round(e["l22"] * 1e7)),
                       int(round(e["tan_f1"] * 1e7)), int(round(e["dt"])),
                       )


def pack_lunar(e):
    """One lunar eclipse as 8 int32s."""
    return struct.pack("<8i",
                       (e["year"] + 2000) * 10000 + e["month"] * 100 + e["day"],
                       e["code"],
                       int(round(e["umbMag"] * 1000.0)),
                       int(round(e["penMag"] * 1000.0)),
                       int(round(e["zenithLat"] * 100.0)),
                       int(round(e["zenithLon"] * 100.0)),
                       int(round((e["durTot"] or 0.0) * 10.0)),
                       int(round((e["durPar"] or 0.0) * 10.0)),
                       )


def build():
    solar = read_solar()
    lunar = read_lunar()
    body = b"".join(pack_solar(e) for e in solar)
    lbody = b"".join(pack_lunar(e) for e in lunar)
    head = struct.pack("<IIIIiiii", MAGIC, VERSION, len(solar), len(lunar),
                       solar[0]["year"] if solar else 0,
                       solar[-1]["year"] if solar else 0,
                       lunar[0]["year"] if lunar else 0,
                       lunar[-1]["year"] if lunar else 0)
    raw = head + struct.pack("<I", len(body)) + body + lbody
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as fh:
        fh.write(raw)
    print("sky_eclipses.bin.gz: %d solar (%d..%d) and %d lunar (%d..%d) eclipses, "
          "%d bytes raw, %d bytes gzipped"
          % (len(solar), solar[0]["year"], solar[-1]["year"],
             len(lunar), lunar[0]["year"], lunar[-1]["year"],
             len(raw), os.path.getsize(OUT)))
    return solar, lunar


def read():
    raw = gzip.open(OUT, "rb").read()
    magic, ver, ns, nl, sy0, sy1, ly0, ly1 = struct.unpack_from("<IIIIiiii", raw, 0)
    assert magic == MAGIC and ver == VERSION, "not an eclipse pack"
    off = 32
    blen, = struct.unpack_from("<I", raw, off)
    off += 4
    solar = [struct.unpack_from("<25i", raw, off + i * 100) for i in range(ns)]
    off += blen
    lunar = [struct.unpack_from("<8i", raw, off + i * 32) for i in range(nl)]
    return solar, lunar


def unpack_solar(r):
    d = r[0]
    year = d // 10000 - 2000
    month = (d // 100) % 100
    day = d % 100
    e = {"year": year, "month": month, "day": day, "code": r[1],
         "nasa_mag": r[2] / 1000.0,
         "x0": r[3] / 1e9, "x1": r[4] / 1e9, "x2": r[5] / 1e9, "x3": r[6] / 1e9,
         "y0": r[7] / 1e9, "y1": r[8] / 1e9, "y2": r[9] / 1e9, "y3": r[10] / 1e9,
         "d0": r[11] / 1e6, "d1": r[12] / 1e6, "d2": r[13] / 1e6,
         "mu0": r[14] / 1e6, "mu1": r[15] / 1e6, "mu2": r[16] / 1e6,
         "l10": r[17] / 1e7, "l11": r[18] / 1e7, "l12": r[19] / 1e7,
         "l20": r[20] / 1e7, "l21": r[21] / 1e7, "l22": r[22] / 1e7,
         "tan_f1": r[23] / 1e7, "tan_f2": r[23] / 1e7,   # the two differ in the fourth decimal
         "dt": r[24],
         "tmin": TMIN, "tmax": TMAX}
    return e


def selftest():
    """The geometry against NASA's own published numbers."""
    solar = read_solar()
    print("%-16s %10s %10s   %9s %9s  %s" % ("eclipse", "gamma", "computed", "magnitude",
                                             "computed", "point off"))
    worst = 0.0
    mag_worst = 0.0
    for y, m, d in [("1999", "8", "11"), ("1919", "5", "29"), ("-584", "5", "28"),
                    ("2001", "6", "21"), ("1560", "8", "21"), ("2017", "8", "21"),
                    ("-1999", "6", "12"), ("2024", "4", "8"), ("2023", "10", "14"),
                    ("136", "3", "5")]:
        e = next((e for e in solar if e["nasa_year"] == int(y) and e["nasa_month"] == int(m)
                  and e["nasa_day"] == int(d)), None)
        if e is None:
            continue
        t, g = greatest_of(e)
        x, yv, dd, mu, l1, l2 = elements_at(e, t)
        lat, lon = axis_point(x, yv, dd, mu, e["dt"])
        off = math.hypot(lat - e["nasa_lat"], lon - e["nasa_lon"])
        zeta = math.sqrt(max(0.0, 1.0 - g * g))
        l1p = l1 - zeta * e["tan_f1"]
        l2p = l2 - zeta * e["tan_f2"]
        mag = (l1p - l2p) / (l1p + l2p) if (l1p + l2p) != 0 else 0.0
        worst = max(worst, off)
        mag_worst = max(mag_worst, abs(mag - e["nasa_mag"]))
        print("%-16s %10.5f %10.5f   %9.5f %9.5f  %.3f deg"
              % ("%s-%02d-%02d" % (y, int(m), int(d)), e["nasa_gamma"], g,
                 e["nasa_mag"], mag, off))
    print("\nworst point error %.3f deg (%.0f km), worst magnitude error %.5f"
          % (worst, worst * 111.0, mag_worst))
    return 0 if worst < 1.0 and mag_worst < 0.002 else 1


def check():
    solar, lunar = read()
    print("sky_eclipses.bin.gz: %d solar eclipses, %d lunar eclipses, %d bytes gzipped"
          % (len(solar), len(lunar), os.path.getsize(OUT)))
    kinds = {}
    for r in solar:
        kinds[r[1]] = kinds.get(r[1], 0) + 1
    print("  solar by kind: " + ", ".join(
        "%s %d" % (["partial", "annular", "total", "hybrid"][k], kinds.get(k, 0))
        for k in range(4)))
    lk = {}
    for r in lunar:
        lk[r[1]] = lk.get(r[1], 0) + 1
    print("  lunar by kind: " + ", ".join(
        "%s %d" % (["penumbral", "partial", "total"][k], lk.get(k, 0)) for k in range(3)))
    years = [r[0] // 10000 - 2000 for r in solar]
    print("  solar years: %d .. %d" % (min(years), max(years)))
    lyears = [r[0] // 10000 - 2000 for r in lunar]
    print("  lunar years: %d .. %d" % (min(lyears), max(lyears)))
    bad = [r for r in solar if not (-2000 <= r[0] // 10000 - 2000 <= 3000)]
    print("  dates outside the catalogue: %d" % len(bad))
    return 0 if not bad else 1


def places():
    """What each test place saw in its own year: the register's promise, checked here."""
    solar, lunar = read()
    es = [unpack_solar(r) for r in solar]
    for name, lat, lon, year in TEST_PLACES:
        here = [e for e in es if e["year"] == year]
        sol = []
        for e in here:
            m = local_magnitude(e, lat, lon)
            if m > 0.02:
                kind = "total" if m >= 1.0 else "partial"
                sol.append("%d-%02d-%02d %s %.2f" % (e["year"], e["month"], e["day"], kind, m))
        lun = []
        for r in lunar:
            y = r[0] // 10000 - 2000
            if y != year:
                continue
            mo = (r[0] // 100) % 100
            dd = r[0] % 100
            zl, zo = r[4] / 100.0, r[5] / 100.0
            if haversine_km(lat, lon, zl, zo) <= 10000.0:
                lun.append("%d-%02d-%02d %s %.2f" % (
                    y, mo, dd, ["penumbral", "partial", "total"][r[1]], r[2] / 1000.0))
        print("%-16s %6d  solar: %s" % (name, year, ", ".join(sol) if sol else "none seen"))
        print("%-16s          lunar: %s" % ("", ", ".join(lun[:6]) if lun else "none seen"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--places", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.check:
        sys.exit(check())
    elif a.places:
        places()
    elif a.selftest:
        sys.exit(selftest())
    else:
        build()
