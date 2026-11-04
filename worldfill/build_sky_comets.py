#!/usr/bin/env python3
"""Step 35 (B23, part 2): the comets history recorded, with the year each was seen.

Usage:
    python3 build_sky_comets.py              build history/sky_comets.json.gz
    python3 build_sky_comets.py --check      read the pack back and report
    python3 build_sky_comets.py --places     the comets each test place's century saw

Unlike the eclipses, there is no catalogue of comets that can be computed: a comet comes once,
when it comes, and what survives is the record of who saw it. So this pack is written from
Wikipedia's table of **great comets** -- the ones bright enough to be noticed by people who were
not looking for them, which is exactly the kind that got written down, feared, and read as an
omen. Every row keeps the table's own words as its note.

What it carries: the name, the date of perihelion (or the year, where that is all the record
keeps), how bright it became where a magnitude is known, and the note -- "Reported by Aristotle
and Ephorus", "Recorded by ancient Babylonians and Chinese", "Visible to the naked eye for five
months". The note is the part a game wants; the date is the part that has to be right.

Source: English Wikipedia, "Great comet", table of great comets of the past two millennia
(fetched 2026-10-16). Wikipedia: CC BY-SA 4.0.
"""
import argparse
import gzip
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "eternal")
OUT = os.path.join(MOD, "src", "main", "resources", "data", "eternalengine",
                   "eternal", "history", "sky_comets.json.gz")
RAW = os.path.join(HERE, "build", "sky", "raw", "comets_wikitext.txt")

MONTHS = {m: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July", "August", "September",
     "October", "November", "December"])}

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
    ("Hyderabad", 17.3850, 78.4867, 1948),
]


def clean(text):
    """Wiki markup to plain words."""
    t = text
    t = re.sub(r"<ref[^>]*>.*?</ref>", " ", t, flags=re.S)
    t = re.sub(r"<ref[^>]*/>", " ", t)
    t = re.sub(r"\{\{r\|[^}]*\}\}", " ", t)
    t = re.sub(r"\{\{[^{}]*\}\}", " ", t)
    t = re.sub(r"\[\[([^\]|]*)\|([^\]]*)\]\]", r"\2", t)
    t = re.sub(r"\[\[([^\]]*)\]\]", r"\1", t)
    t = t.replace("'''", "").replace("''", "")
    t = re.sub(r"</?[^>]+>", " ", t)
    t = t.replace("&nbsp;", " ")
    t = re.sub(r"\s+", " ", t)
    return t.strip(" |")


def parse_date(text):
    """'25 May 44 BC' -> (-43, 5, 25);  '371 BC' -> (-370, 0, 0);  '3 July 2020' -> (2020, 7, 3).

    Astronomical years throughout, the way the rest of the mod counts them: 44 BC is -43.
    """
    t = text.strip()
    bc = bool(re.search(r"\b(BC|BCE)\b", t, re.I))
    t = re.sub(r"\b(BC|BCE|AD|CE)\b", " ", t, flags=re.I).strip()
    m = re.match(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{1,4})", t)
    if m:
        day, mon, year = int(m.group(1)), MONTHS.get(m.group(2).capitalize(), 0), int(m.group(3))
        return (-(year - 1) if bc else year), mon, day
    m = re.match(r"([A-Za-z]+)\s+(\d{1,4})", t)
    if m:
        mon, year = MONTHS.get(m.group(1).capitalize(), 0), int(m.group(2))
        return (-(year - 1) if bc else year), mon, 0
    m = re.match(r"(\d{1,4})", t)
    if m:
        year = int(m.group(1))
        return (-(year - 1) if bc else year), 0, 0
    return None


def parse_mag(text):
    """'-4.0', '0.5-1.0', '-'  -> a magnitude, or None."""
    t = text.replace("\u2212", "-").strip()
    m = re.findall(r"-?\d+(?:\.\d+)?", t)
    if not m:
        return None
    return min(float(v) for v in m)          # the brightest figure given


def rows_from_wikitext():
    if not os.path.exists(RAW):
        sys.exit("missing %s -- fetch the article first" % RAW)
    text = open(RAW, encoding="utf-8").read()
    body = text[text.find("Great comets of the past two millennia"):]
    out = []
    for block in body.split("|-"):
        cells = []
        for c in re.split(r"\n\|", block):
            c = c.strip()
            if not c or c.startswith("!"):
                continue
            c = re.sub(r"^align=center\s*\|?", "", c)
            c = re.sub(r"data-sort-value=\"[^\"]*\"\s*\|?", "", c)
            cells.append(c.strip().strip("|").strip())
        if len(cells) < 7:
            continue
        designation, name = cells[0], cells[1]
        if "bgcolor" in designation or designation.startswith("}"):
            continue
        # The columns are fixed -- designation, name, image, dimensions, total magnitude,
        # maximum brightness, perihelion date, remarks -- so the date is taken by position and
        # not by searching: a brightness of "-4.0" looks exactly like a year to a regex, and
        # reading it as one is how the comets of 87 BC and 44 BC went missing.
        if len(cells) < 7:
            continue
        parsed = parse_date(cells[6]) if len(cells) > 6 else None
        if parsed is None:
            for c in cells[2:8]:
                p = parse_date(c)
                if p is not None and re.search(r"(BC|AD|\b1[5-9]\d\d\b|\b20\d\d\b)", c):
                    parsed = p
                    break
        if parsed is None:
            continue
        year, month, day = parsed
        # what people actually saw: the maximum brightness, and the total magnitude only where
        # the table has no brightness for that apparition
        mag = parse_mag(cells[5]) if len(cells) > 5 else None
        if mag is None:
            mag = parse_mag(cells[4]) if len(cells) > 4 else None
        note = clean(cells[7])[:220] if len(cells) >= 8 else ""
        nm = clean(name) or clean(designation)
        if not nm or len(nm) > 60:
            nm = clean(designation)
        out.append({"name": nm, "year": year, "month": month, "day": day,
                    "mag": mag, "note": note, "designation": clean(designation)})
    out.sort(key=lambda r: (r["year"], r["month"], r["day"]))
    return out


def build():
    rows = rows_from_wikitext()
    pack = [[r["name"], r["year"], r["month"], r["day"],
             int(round(r["mag"] * 100.0)) if r["mag"] is not None else None,
             r["note"]] for r in rows]
    doc = {
        "format": "eternalengine/sky_comets@1",
        "about": "The great comets of the past two and a half millennia: those bright enough to "
                 "be seen by people who were not looking for them, which is why they were "
                 "written down.",
        "source": "English Wikipedia, article \"Great comet\", table of great comets of the past "
                  "two millennia, fetched 2026-10-16. Wikipedia: CC BY-SA 4.0.",
        "note": "One row: [name, year, month or 0, day or 0, brightest magnitude x100 or null, "
                "note]. Years are astronomical, as the rest of the mod counts them: 44 BC is "
                "-43. The date is perihelion, when the comet was brightest; where the record "
                "keeps only a year, month and day are 0. The note is the table's own words, "
                "trimmed.",
        "count": len(pack),
        "comets": pack,
    }
    raw = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as fh:
        fh.write(raw)
    dated = sum(1 for r in rows if r["day"])
    print("sky_comets.json.gz: %d comets (%d with a full date, %d with a magnitude), "
          "%d bytes raw, %d bytes gzipped"
          % (len(rows), dated, sum(1 for r in rows if r["mag"] is not None),
             len(raw), os.path.getsize(OUT)))
    return rows


def read():
    return json.loads(gzip.open(OUT, "rt", encoding="utf-8").read())


def check():
    doc = read()
    rows = doc["comets"]
    years = [r[1] for r in rows]
    named = sum(1 for r in rows if r[0])
    noted = sum(1 for r in rows if r[5])
    print("sky_comets.json.gz: %d comets, %d named, %d with a note, years %d..%d"
          % (len(rows), named, noted, min(years), max(years)))
    print("  brightest recorded: " + ", ".join(
        "%s (%.1f)" % (r[0], r[4] / 100.0) for r in sorted(
            [r for r in rows if r[4] is not None], key=lambda r: r[4])[:4]))
    print("  the earliest: " + "; ".join("%s %d" % (r[0], r[1]) for r in rows[:4]))
    bad = [r for r in rows if not (-3000 <= r[1] <= 2026)]
    print("  dates outside the mod's span: %d" % len(bad))
    print()
    for r in rows:
        if r[1] in (-43, 1066, 1577, 1811, 1858, 1910, 1986, 1997):
            print("  %-30s %5d-%02d-%02d  mag %s  %s" % (
                r[0][:30], r[1], r[2], r[3],
                ("%.1f" % (r[4] / 100.0)) if r[4] is not None else "?", r[5][:70]))
    return 0 if not bad else 1


def places():
    doc = read()
    rows = doc["comets"]
    for name, lat, lon, year in TEST_PLACES:
        near = [r for r in rows if year - 60 <= r[1] <= year + 20]
        print("%-14s %6d  %s" % (name, year,
                                 "; ".join("%s (%d)" % (r[0], r[1]) for r in near[:6])
                                 or "none recorded within a lifetime"))


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
