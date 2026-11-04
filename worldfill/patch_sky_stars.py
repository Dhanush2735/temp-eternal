#!/usr/bin/env python3
"""Step 35 (B23): repair two defects in an already-built sky_stars.json.gz.

1. Right ascension in hours. The HYG database's `ra` field is right ascension in HOURS (0..24),
   not degrees. build_sky_stars.py read it as degrees and shipped it as "right ascension degrees
   x1000", so the whole sky sat inside 24 degrees of the vernal equinox. That looks fine in a
   table and is quietly fatal in use: precession then finds no star anywhere near the pole of
   date, and the pole star comes back as Polaris at every epoch from 3000 BC to AD 3000. This
   script multiplies column 1 by 15.

2. Star names that are a bare Greek abbreviation. HYG often carries the Bayer letter with no
   constellation ("Gam" for Gamma Centauri) because the constellation lives in a separate column,
   and build_sky_stars.py only expanded the two-word form. That left 921 naked-eye stars -- among
   them Kappa Draconis, the pole star of 1500 BC -- named "Kap". This script spells the letter out
   and adds the constellation from column 7.

Both repairs are idempotent and are applied without re-fetching the 20 MB HYG file. Corrected
right ascensions agree with SIMBAD to better than 0.01 degree on nineteen bright anchors.

Usage:
    python3 patch_sky_stars.py          repair the pack (safe to run twice)
    python3 patch_sky_stars.py --check  report without writing
"""
import argparse
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "eternal", "src", "main", "resources", "data",
                   "eternalengine", "eternal", "history", "sky_stars.json.gz")

# right ascension in degrees, J2000 (SIMBAD): what column 1 times 15 ought to come to
ANCHORS = {"Sirius": 101.287, "Arcturus": 213.915, "Vega": 279.234, "Deneb": 310.358,
           "Altair": 297.696, "Capella": 79.172, "Thuban": 211.097, "Kochab": 222.676,
           "Polaris": 37.955, "Alderamin": 319.645, "Errai": 354.836, "Betelgeuse": 88.793,
           "Rigel": 78.634, "Antares": 247.352, "Spica": 201.298, "Procyon": 114.825,
           "Achernar": 24.429, "Canopus": 95.988, "Alnilam": 84.053}


def read():
    return json.loads(gzip.open(OUT, "rt", encoding="utf-8").read())


GREEK = {"Alp": "Alpha", "Bet": "Beta", "Gam": "Gamma", "Del": "Delta",
         "Eps": "Epsilon", "Zet": "Zeta", "Eta": "Eta", "The": "Theta",
         "Iot": "Iota", "Kap": "Kappa", "Lam": "Lambda", "Mu": "Mu",
         "Nu": "Nu", "Xi": "Xi", "Omi": "Omicron", "Pi": "Pi", "Rho": "Rho",
         "Sig": "Sigma", "Tau": "Tau", "Ups": "Upsilon", "Phi": "Phi",
         "Chi": "Chi", "Psi": "Psi", "Ome": "Omega"}


def looks_like_hours(doc):
    """True if column 1 is still in hours: then nothing exceeds 24 degrees."""
    return max(s[1] for s in doc["stars"]) <= 24000


def count_bare_greek(doc):
    """Rows whose whole name is a three-letter Bayer abbreviation, e.g. 'Kap'."""
    return sum(1 for s in doc["stars"] if s[0] in GREEK)


def check(doc, changed):
    stars = doc["stars"]
    worst = 0.0
    for name, true in ANCHORS.items():
        row = next((s for s in stars if s[0] == name), None)
        if row is None:
            print("  %-12s MISSING FROM PACK" % name)
            worst = 999.0
            continue
        err = abs(row[1] / 1000.0 - true)
        worst = max(worst, err)
        if err > 0.05:
            print("  %-12s pack %9.3f  true %9.3f  off by %6.3f" % (name, row[1] / 1000.0, true, err))
    bad = [s for s in stars if not (0 <= s[1] <= 360000) or not (-90000 <= s[2] <= 90000)]
    bare = count_bare_greek(doc)
    named = sum(1 for s in stars if s[0])
    print("  %d stars, %d named, %d with a position out of range, worst anchor error %.3f deg"
          % (len(stars), named, len(bad), worst))
    print("  column 1 is in %s" % ("HOURS -- still broken" if looks_like_hours(doc) else "degrees"))
    print("  %d names are a bare Greek abbreviation%s" % (bare, " -- still broken" if bare else ""))
    if not changed:
        print("  (no write: --check)")
    return 0 if (not bad and worst <= 0.05 and not looks_like_hours(doc) and bare == 0) else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    doc = read()
    if a.check:
        return check(doc, False)
    hours = looks_like_hours(doc)
    fixed_ra = fixed_names = 0
    for s in doc["stars"]:
        if hours:
            s[1] = int(round(s[1] * 15.0)) % 360000
            fixed_ra += 1
        if s[0] in GREEK:
            con = (s[7] or "").strip()
            s[0] = GREEK[s[0]] + (" " + con if con else "")
            fixed_names += 1
    if not fixed_ra and not fixed_names:
        print("sky_stars.json.gz: nothing left to repair")
        return check(doc, False)
    raw = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as fh:
        fh.write(raw)
    print("sky_stars.json.gz: right ascension hours -> degrees on %d stars, %d names spelled out, "
          "%d bytes gzipped" % (fixed_ra, fixed_names, os.path.getsize(OUT)))
    return check(read(), True)


if __name__ == "__main__":
    sys.exit(main())
