#!/usr/bin/env python3
"""Step 35 (B22, part 2): the stars the world can see.

Usage:
    python3 build_sky_stars.py              build history/sky_stars.json.gz
    python3 build_sky_stars.py --check      read the pack back and report
    python3 build_sky_stars.py --places     answer the 31 test places

Source: the HYG database v3.7 (astronexus/HYG-Database, CC BY-SA 4.0), a merge of the Hipparcos,
Yale Bright Star and Gliese catalogues: 119,614 stars. What a mod needs is the naked-eye sky, so
the pack keeps what can be seen without a telescope (magnitude 6.0 or brighter) plus the named
stars a little fainter than that, and ships five numbers per star.

What is NOT in the pack, on purpose:

* the Sun, the Moon and the planets -- their places are computed from the date, not tabulated;
* any epoch but J2000. The pack is the sky as it is on 2000 Jan 1.5 TT, and the register applies
  precession and proper motion for the year the player is standing in. One pack, every era --
  which is the whole point: the sky of Ur in 2500 BC is this sky, turned.

The five numbers are right ascension and declination in degrees (J2000), the apparent visual
magnitude, the colour index (B-V, which is what tells a red star from a blue one), and the proper
motion in milliarcseconds a year.

One trap, found the hard way: HYG's `ra` column is right ascension in HOURS, not degrees. Read as
degrees it puts the whole sky inside 24 degrees of the vernal equinox, which looks fine in a table
and is quietly fatal in use -- precession then finds no star anywhere near the pole of date, and
the pole star comes back as Polaris for every epoch from 3000 BC to AD 3000. The pack column is
degrees; `patch_sky_stars_ra.py` converts an existing pack if one was built before this was known. Proper motion is what moves a star across the sky over the
12,000 years this mod spans: Barnard's Star crosses 14 degrees of it. Precession is bigger still
and is applied in code, because it is a function of the date rather than of the star.
"""
import argparse
import csv
import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "eternal")
OUT = os.path.join(MOD, "src", "main", "resources", "data", "eternalengine",
                   "eternal", "history", "sky_stars.json.gz")
HYG = os.path.join(HERE, "build", "sky", "raw", "hyg_v37.csv.gz")

MAG_LIMIT = 6.0        # the naked-eye sky, in a dark place
NAMED_LIMIT = 7.5      # a star with a name of its own is kept even if it is a little fainter

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


def designation(row):
    """A star's name: its own name if it has one, else its Bayer or Flamsteed name."""
    proper = (row.get("proper") or "").strip()
    if proper:
        return proper
    bayer = (row.get("bayer") or "").strip()
    if bayer:
        # "Alp CMa" -> "Alpha CMa"; the Greek letter is worth spelling out in a book. HYG often
        # carries the Greek abbreviation on its own, with the constellation in the `con` column,
        # so a bare "Gam" is Gamma of whatever constellation the row belongs to -- and a bare "Gam"
        # in a book about the sky is no name at all.
        greek = {"Alp": "Alpha", "Bet": "Beta", "Gam": "Gamma", "Del": "Delta",
                 "Eps": "Epsilon", "Zet": "Zeta", "Eta": "Eta", "The": "Theta",
                 "Iot": "Iota", "Kap": "Kappa", "Lam": "Lambda", "Mu": "Mu",
                 "Nu": "Nu", "Xi": "Xi", "Omi": "Omicron", "Pi": "Pi", "Rho": "Rho",
                 "Sig": "Sigma", "Tau": "Tau", "Ups": "Upsilon", "Phi": "Phi",
                 "Chi": "Chi", "Psi": "Psi", "Ome": "Omega"}
        parts = bayer.split()
        if len(parts) == 2 and parts[0] in greek:
            return greek[parts[0]] + " " + parts[1]
        if len(parts) == 1 and parts[0] in greek:
            con = (row.get("con") or "").strip()
            return greek[parts[0]] + (" " + con if con else "")
        return bayer
    flam = (row.get("flam") or "").strip()
    con = (row.get("con") or "").strip()
    if flam and con:
        return flam + " " + con
    return ""


def load():
    """Read HYG and keep the sky a person can see, as plain tuples."""
    if not os.path.exists(HYG):
        sys.exit("missing %s -- run the HYG fetch first" % HYG)
    raw = gzip.open(HYG, "rt", encoding="utf-8", errors="replace")
    reader = csv.DictReader(raw)
    stars = []
    kept = 0
    for row in reader:
        if row["id"] == "0":
            continue                      # the Sun; the code computes it
        try:
            mag = float(row["mag"])
            # HYG carries right ascension in HOURS; the pack ships degrees
            ra = float(row["ra"]) * 15.0      # degrees, J2000
            dec = float(row["dec"])
        except (TypeError, ValueError):
            continue
        name = designation(row)
        if mag > (MAG_LIMIT if not name else NAMED_LIMIT):
            continue
        if not (-90.0 <= dec <= 90.0 and 0.0 <= ra <= 360.0):
            continue
        try:
            ci = float(row["ci"]) if row["ci"] not in ("", None) else 0.0
        except ValueError:
            ci = 0.0
        try:
            pmra = float(row["pmra"]) if row["pmra"] not in ("", None) else 0.0
            pmdec = float(row["pmdec"]) if row["pmdec"] not in ("", None) else 0.0
        except ValueError:
            pmra = pmdec = 0.0
        stars.append((
            name,
            int(round(ra * 1000.0)),
            int(round(dec * 1000.0)),
            int(round(mag * 100.0)),
            int(round(ci * 100.0)),
            int(round(pmra * 10.0)),
            int(round(pmdec * 10.0)),
            (row.get("con") or "").strip(),
        ))
        kept += 1
    stars.sort(key=lambda s: s[3])        # brightest first
    return stars, kept


def build():
    stars, kept = load()
    named = sum(1 for s in stars if s[0])
    doc = {
        "format": "eternalengine/sky_stars@1",
        "about": "The naked-eye sky: every star of magnitude 6.0 or brighter, plus the named "
                 "stars a little fainter, at epoch J2000.",
        "source": "HYG database v3.7 (astronexus/HYG-Database), a merge of Hipparcos, the Yale "
                  "Bright Star Catalogue and the Gliese catalogue, fetched 2026-10-16. "
                  "CC BY-SA 4.0.",
        "note": "One row: [name or empty, right ascension degrees x1000, declination degrees "
                "x1000, apparent visual magnitude x100, colour index B-V x100, proper motion in "
                "RA x10 mas/yr (this is mu-alpha-cos-delta, so divide by cos(dec) for a change "
                "in RA), proper motion in dec x10 mas/yr, constellation]. Epoch J2000: the "
                "register precesses to the year asked about and adds the proper motion. The Sun "
                "is not here; its place is computed.",
        "epoch": "J2000",
        "count": len(stars),
        "stars": [list(s) for s in stars],
    }
    raw = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as fh:
        fh.write(raw)
    print("sky_stars.json.gz: %d stars (%d named), %d bytes raw, %d bytes gzipped"
          % (len(stars), named, len(raw), os.path.getsize(OUT)))
    return stars


def read():
    doc = json.loads(gzip.open(OUT, "rt", encoding="utf-8").read())
    return doc


def check():
    doc = read()
    stars = doc["stars"]
    named = sum(1 for s in stars if s[0])
    bad = [s for s in stars if not (-90000 <= s[2] <= 90000) or not (0 <= s[1] <= 360000)]
    print("sky_stars.json.gz: %d stars, %d named, %d with a bad position"
          % (len(stars), named, len(bad)))
    print("  brightest: " + ", ".join("%s (%.2f)" % (s[0] or "unnamed", s[3] / 100.0)
                                      for s in stars[:6]))
    print("  faintest:  %.2f" % (stars[-1][3] / 100.0))
    print("  constellations: %d distinct" % len({s[7] for s in stars if s[7]}))
    movers = sorted(stars, key=lambda s: -(abs(s[5]) + abs(s[6])))[:3]
    print("  fastest movers: " + "; ".join(
        "%s (%.0f mas/yr)" % (s[0] or "unnamed", math.hypot(s[5], s[6]) / 10.0) for s in movers))
    return 0 if not bad else 1


def places():
    """How many of these stars can each test place see, at some point in the year?

    A star is visible from a latitude if its declination is within 90 degrees of it: the pole
    star is never seen from the equator, and the southern cross never from London. This is the
    geometry check, before any era or weather.
    """
    doc = read()
    stars = doc["stars"]
    print("%-17s %6s  %8s %8s %8s" % ("place", "year", "visible", "circum", "never"))
    for name, lat, lon, year in TEST_PLACES:
        vis = circ = nev = 0
        for s in stars:
            dec = s[2] / 1000.0
            # highest altitude this star reaches = 90 - |lat - dec|
            alt = 90.0 - abs(lat - dec)
            if alt >= 0:
                vis += 1
            # always above the horizon: the whole circle of declination is up
            if 90.0 - abs(lat - dec) >= 0 and abs(lat) + abs(dec) <= 90.0 and \
                    (lat >= 0 and dec >= (90.0 - lat)) or (lat < 0 and dec <= -(90.0 + lat)):
                circ += 1
            if alt < 0:
                nev += 1
        print("%-17s %6d  %8d %8d %8d" % (name, year, vis, circ, nev))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--places", action="store_true")
    a = ap.parse_args()
    if a.check:
        sys.exit(check())
    elif a.places:
        places()
    else:
        build()
