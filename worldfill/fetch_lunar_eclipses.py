#!/usr/bin/env python3
"""Step 35 (B23): fetch NASA's Five Millennium Catalog of Lunar Eclipses, century by century.

Usage:
    python3 fetch_lunar_eclipses.py --fetch     all 50 century pages -> build/sky/raw/lunar/
    python3 fetch_lunar_eclipses.py --status    how many are here

The catalogue is only published as HTML: one page per century, -1999..-1900 through 2901..3000,
12,064 eclipses in all. Each row carries the calendar date, the TD of greatest eclipse, the
eclipse type (N penumbral, P partial, T total), the umbral magnitude, the durations, and the
point where the Moon stood in the zenith at greatest eclipse -- which is what lets us say where
an eclipse was seen from.

NASA's dates are Julian before 1582 Oct 15 and Gregorian after; the mod's KnowledgeDate is
proleptic Gregorian, so the parser keeps the raw date and turns it into a Julian Day Number,
which the builder converts. Public domain (US government work, Espenak & Meeus).
"""
import argparse
import json
import os
import re
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "build", "sky", "raw", "lunar")
UA = "EternalEngineDataBuild/1.0"

# 50 century pages, -1999..-1900 through 2901..3000. The names are NASA's and they are not quite
# regular -- the BCE centuries are zero padded ("LE-0999--0900.html") and the century that spans
# the year zero is "LE-0099-0000.html" with one dash, not two -- so the list is read from NASA's
# own index rather than built from arithmetic.
INDEX = "https://eclipse.gsfc.nasa.gov/LEcat5/LEcatalog.html"


def build_page_list(verbose=True):
    """[(firstYearOfCentury, fileName), ...] in NASA's own order."""
    for attempt in range(4):
        try:
            req = urllib.request.Request(INDEX, headers={"User-Agent": UA})
            body = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
            break
        except Exception as e:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
    names = re.findall(r'href="(LE[^"]+\.html)"', body)
    out = []
    for i, n in enumerate(names):
        m = re.match(r"LE(-?\d{4})-+-?(\d{4})\.html", n)
        if not m:
            continue
        start = int(m.group(1))
        out.append((start, n))
    if verbose:
        print("%d century pages in the index" % len(out), flush=True)
    return out


def fetch(limit=None, sleep=0.4, verbose=True):
    os.makedirs(RAW, exist_ok=True)
    pages = build_page_list()
    done = 0
    for i, (start, name) in enumerate(pages):
        if limit and done >= limit:
            break
        path = os.path.join(RAW, name)
        if os.path.exists(path) and os.path.getsize(path) > 20000:
            continue
        url = "https://eclipse.gsfc.nasa.gov/LEcat5/" + name
        for attempt in range(4):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA})
                body = urllib.request.urlopen(req, timeout=90).read()
                if b"<pre>" not in body:
                    raise ValueError("no <pre> table in %s" % name)
                open(path, "wb").write(body)
                done += 1
                if verbose:
                    print("[%d/%d] %s %d bytes" % (i + 1, len(pages), name, len(body)),
                          flush=True)
                break
            except Exception as e:
                if attempt == 3:
                    print("FAILED %s: %s" % (name, e), flush=True)
                else:
                    time.sleep(2 ** attempt)
        time.sleep(sleep)
    return done


def status():
    if not os.path.isdir(RAW):
        print("no pages yet")
        return 0
    files = [f for f in os.listdir(RAW) if f.endswith(".html")]
    rows = 0
    for f in files:
        body = open(os.path.join(RAW, f), encoding="utf-8", errors="replace").read()
        rows += len(ECLIPSE_ROW.findall(body))
    print("%d century pages, %d eclipse rows" % (len(files), rows))
    return len(files)


# 05024  0080 Sep 17  23:35:36   9738 -23739  <a ...> 77</a>   P   t-  -0.6082  1.7661  0.7182
#   329.1  180.3    -      3S   46E
ECLIPSE_ROW = re.compile(
    r"<a href=\"\.\./5MCLEmap/[^\"]+\"[^>]*>(\d{5})</a>"      # catalogue number
    r"\s+(-\d{4}|\d{1,4})\s+([A-Z][a-z]{2})\s+(\d{1,2})"      # year month day
    r"\s+(\d{2}:\d{2}:\d{2})"                                  # TD of greatest eclipse
    r"\s+(-?\d+)"                                              # delta T
    r"\s+(-?\d+)"                                              # luna number
    r"\s+(?:<a[^>]*>\s*)?(-?\d+)(?:\s*</a>)?"                  # saros series; a negative one is
                                                               # not linked, because NASA has no
                                                               # page for a series below zero
    r"\s+([NPT][m+\-*bex]?)"                                    # type: N penumbral, P partial,
                                                               # T total; second char marks the
                                                               # middle of a saros series (m),
                                                               # a central total (+/-), a total
                                                               # penumbral (*), or the first (b)
                                                               # or last (e) of a series
    r"\s+([a-z+-]{0,2})"                                       # quincena solar eclipse marker
    r"\s+(-?\d+\.\d+)"                                         # gamma
    r"\s+(-?\d+\.\d+)"                                         # penumbral magnitude
    r"\s+(-?\d+\.\d+)"                                         # umbral magnitude
    r"\s+([\d.]+)\s+([\d.]+|-)\s+([\d.]+|-)"                   # durations: penumbral partial total
    r"\s+(\d+)([NS])\s+(\d+)([EW])"                            # zenith point
)

# NASA's dates: Gregorian after 1582 Oct 15, Julian before 1582 Oct 04. The mod's KnowledgeDate
# is proleptic Gregorian, so the builder converts through the Julian Day Number.
MONTHS = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}


def parse_all():
    """Every eclipse in every page that is here, as a plain list of dicts."""
    out = []
    if not os.path.isdir(RAW):
        return out
    for f in sorted(os.listdir(RAW)):
        if not f.endswith(".html"):
            continue
        body = open(os.path.join(RAW, f), encoding="utf-8", errors="replace").read()
        for m in ECLIPSE_ROW.finditer(body):
            g = m.groups()
            lat = int(g[16]) * (1 if g[17] == "N" else -1)
            lon = int(g[18]) * (1 if g[19] == "E" else -1)
            out.append({
                "cat": int(g[0]),
                "year": int(g[1]), "month": MONTHS[g[2]], "day": int(g[3]),
                "td": g[4], "deltaT": int(g[5]), "luna": int(g[6]), "saros": int(g[7]),
                "type": g[8], "qse": g[9],
                "gamma": float(g[10]), "penMag": float(g[11]), "umbMag": float(g[12]),
                "durPen": float(g[13]),
                "durPar": float(g[14]) if g[14] != "-" else None,
                "durTot": float(g[15]) if g[15] != "-" else None,
                "zenithLat": lat, "zenithLon": lon,
            })
    out.sort(key=lambda r: r["cat"])
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--parse", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    a = ap.parse_args()
    if a.status:
        status()
    elif a.fetch:
        n = fetch(limit=a.limit)
        print("%d pages written" % n)
    elif a.parse:
        rows = parse_all()
        print(json.dumps(rows[:2], indent=1))
        print("%d eclipses parsed" % len(rows))
    else:
        print(__doc__)
