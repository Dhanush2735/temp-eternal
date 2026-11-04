#!/usr/bin/env python3
"""Step 42 part 7 (F8, borders and permits): build history/border.json.gz from borders_table.py.

Shape
-----

One table, **crossings**, keyed exactly the way `social_order.json.gz` and `justice.json.gz` are
keyed, because it is asked exactly the way they are asked: `CountryGrid.codeAt(lat, lon)` gives an
ISO3 code, and the register wants the row whose `where` holds that code, whose years hold that
year, and which has the highest `priority`.

A row says three things the mod needs separately:

  * `what`   - what the crossing physically is (a gate, a ford, a customs house, a lazaretto)
  * `demand` - what it takes from you (a gift, a toll, duty, papers, forty days, your turning back)
  * flags    - `papers` (it wants to know who you are), `quarantine` (it holds you), `closed`
               (it will not let you through at all)

Where the line is, is not in here
---------------------------------

This pack says **what a crossing is like**. It does not say where a border runs, and it never will:
the line is derived at runtime from `RulerRegister`, by asking who rules on either side of the step
you are about to take. That is the "neighbouring state" the step-42 survey said F8 needed, and it
is why this part built no state adjacency graph - the ruler register already is one, and a second
one would have been a second opinion that could disagree with the first.

Marks
-----

**Every row is estimated**, and says so. No source states, as a fact, that the frontier of a given
place in a given century was a gate where a gift was expected; these are this table's readings of
the reference works named on each row.

The *dates* on a handful of rows are not readings, though, and the builder checks them: they were
pulled out of the articles themselves.

  * quarantine is first imposed at Ragusa in **1377** - so no port anywhere holds a traveller in
    1300, and the Mediterranean does by 1400
  * the passport is standardised in **1920**, and the British Act that made it a booklet is
    **1914** - so no crossing in 1900 asks a traveller for a passport, and by 1930 they do
  * the Zollverein formally starts **1 January 1834** - so the German states stop stopping each
    other's traffic
  * sakoku runs **1633** to **1853**; the Canton System **1757** to **1842**

Checks
------

  * every `where` code is one `culture.json.gz` also knows (258 countries)
  * every row names the work it was read from, and has a name, a what, a demand and a line
  * no two rows share an id
  * exactly one row is `closed`, and it is the closed shore
  * no row is `papers` before 1914, and no row is `quarantine` before 1377
  * every country of the world gets an answer in every era
  * the world is not all one answer in any era
  * the fallback is not also a row - the defect F3 had this step
  * no crossing is both `sea` and `internal`, which would make it unreachable

Run:  python3 build_border.py            build, then check
"""
import gzip
import json
import os
import sys

import borders_table as T

HERE = os.path.dirname(os.path.abspath(__file__))
HIST = os.path.normpath(os.path.join(
    HERE, "..", "eternal", "src", "main", "resources", "data", "eternalengine", "eternal", "history"))
OUT = os.path.join(HIST, "border.json.gz")
CULTURE = os.path.join(HIST, "culture.json.gz")

TABLE = "crossings"
DEFAULT_ONLY = "open_ground"


def known_countries():
    with gzip.open(CULTURE, "rt", encoding="utf-8") as f:
        return set(json.load(f)["countries"])


def _row(r, codes):
    where = sorted({c for c in r["where"] if c in codes})
    out = {
        "id": r["id"], "name": r["name"], "what": r["what"], "demand": r["demand"],
        "line": r["line"],
        "where": where, "start": r["start"], "end": r["end"],
        "priority": r["priority"], "source": r["source"],
    }
    for flag in ("papers", "quarantine", "closed", "sea", "internal"):
        if r.get(flag):
            out[flag] = True
    if r.get("note"):
        out["note"] = r["note"]
    return out


def build():
    codes = known_countries()
    doc = {
        "format": "eternal-border-1",
        "id": "border",
        "source": ("Hand-written table for step 42 (F8), read from the reference works named on "
                   "each row: Border control, Checkpoint, Custom house, Tariff, Toll (fee), "
                   "Octroi, Turnpike trust, Zollverein, Passport, Travel visa, Travel document, "
                   "Quarantine, Lazaretto, Safe conduct, Firman, Letters patent, Freedom of "
                   "movement, Sakoku, Canton System, Limes, Silk Road, Caravan, Pilgrimage, "
                   "Hajj, Grand Tour, Deportation, Exile and Wanted poster. Every row is this "
                   "table's reading and is marked estimated. Where the border itself runs is NOT "
                   "from here - it is derived from the step-31 ruler register."),
        "note": ("What a crossing demands of you, by ISO3 country and year, keyed the same way "
                 "culture.json.gz, social_order.json.gz and justice.json.gz key their rows: "
                 "CountryGrid.codeAt(lat, lon) then the row whose `where` holds that code, "
                 "highest `priority` first. Whether the step you are about to take crosses a "
                 "border at all is decided at runtime by RulerRegister: a different ruler on the "
                 "far side means a line between. The `closed` mark means you are not allowed "
                 "through; `papers` means it wants to know who you are; `quarantine` means it "
                 "holds you."),
        "counts": {},
        "gaps": [
            "Every row is this table's reading and not a measurement: no source states, for a "
            "given place and century, that its frontier was a gate where a gift was expected.",
            "Country granularity. A country with two frontiers at once - a walled coast and an "
            "open desert edge - gets one of them, and the priority decides which.",
            "Twelve rows cannot be every border post in history. The table ends with a default, "
            "and the default is the least reliable row in the pack.",
            "The dates at which one kind of crossing gives way to another are given to the "
            "century at best, except where an article gave the year: 1377 for quarantine, 1914 "
            "and 1920 for the passport, 1834 for the Zollverein, 1633 to 1853 for sakoku, 1757 "
            "to 1842 for Canton.",
            "Where the border runs is not here at all. It is the ruler register, which is a "
            "nearest-place lookup over 9,322 timelines: it knows who rules a place in a year, so "
            "it can tell you that the place a day's walk away is ruled by someone else, but it "
            "cannot tell you within about 20 km where the line between them falls.",
            "Whether a state would let *you* through - a woman alone, a slave, a debtor, a man of "
            "the wrong faith - is D7's question and not this one.",
        ],
        "countries": [],
    }

    pack = [_row(r, codes) for r in T.CROSSINGS]
    pack.sort(key=lambda r: (-r["priority"], r["id"]))
    doc[TABLE] = pack
    doc["default_" + TABLE] = _row(T.DEFAULT_CROSSING, codes)
    doc["counts"][TABLE] = len(pack)
    doc["counts"]["estimated"] = len(pack)
    doc["counts"]["recorded"] = 0
    doc["countries"] = sorted({c for r in pack for c in r["where"]})

    blob = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(blob)
    print("border.json.gz: %d crossings over %d countries (%d bytes gzipped)"
          % (doc["counts"][TABLE], len(doc["countries"]), os.path.getsize(OUT)))
    return doc


def pick(doc, code, year, by_sea=False):
    """
    The row for a country and year, the way the mod will pick it.

    `by_sea` is not decoration. A crossing marked `sea` stands at a port and is only met by a
    traveller who comes off a ship; one marked `internal` is a toll *inside* a state and is only
    met by a traveller on a road. Asking without saying which will pick a lazaretto for a man
    riding north through England in 1800, which is plainly wrong: sort the two out and the
    ordering stops having to choose between them.
    """
    best = None
    for r in doc[TABLE]:
        if code not in r["where"]:
            continue
        if r["start"] is not None and year < r["start"]:
            continue
        if r["end"] is not None and year >= r["end"]:
            continue
        if by_sea and r.get("internal", False):
            continue
        if not by_sea and r.get("sea", False):
            continue
        if best is None or r["priority"] > best["priority"]:
            best = r
    return best if best is not None else doc["default_" + TABLE]


def check():
    with gzip.open(OUT, "rt", encoding="utf-8") as f:
        d = json.load(f)
    bad = []

    def ok(cond, what):
        print(("  ok   " if cond else "  FAIL ") + what)
        if not cond:
            bad.append(what)

    ok(d["format"] == "eternal-border-1", "the format is the one this builder writes")
    for key in (TABLE, "default_" + TABLE, "countries", "gaps", "counts"):
        ok(key in d, "the pack carries %s" % key)

    codes = known_countries()
    rows = d[TABLE]
    ok(len(rows) >= 10, "crossings: %d rows" % len(rows))
    stray = sorted({c for r in rows for c in r["where"] if c not in codes})
    ok(not stray, "every country code is one culture.json.gz also knows (%s)"
       % (", ".join(stray[:8]) or "none"))
    ok(len({r["id"] for r in rows}) == len(rows), "no two rows share an id")
    for r in rows:
        ok(bool(r["source"]), "%s names the work it was read from" % r["id"])
        ok(bool(r["name"]) and bool(r["what"]) and bool(r["demand"]) and bool(r["line"]),
           "%s has a name, a what, a demand and a line" % r["id"])
        ok(r["start"] is not None, "%s has a start year" % r["id"])
        if r["end"] is not None:
            ok(r["end"] >= r["start"], "%s does not end before it begins" % r["id"])

    # The marks, and the dates that make them true.
    closed = [r["id"] for r in rows if r.get("closed")]
    ok(closed == ["closed_shore"],
       "exactly one crossing is `closed`, and it is the closed shore (%s)"
       % (", ".join(closed) or "none"))
    ok(all(r["start"] >= 1914 for r in rows if r.get("papers")),
       "no crossing asks for papers before 1914, which is when the passport became general")
    ok(all(r["start"] >= 1377 for r in rows if r.get("quarantine")),
       "no crossing holds you before 1377, which is when Ragusa imposed the trentino")
    ok(not any(r.get("sea") and r.get("internal") for r in rows),
       "no crossing is both a port and an inland toll, which would make it unreachable")
    ok(sum(1 for r in rows if r.get("sea")) >= 2 and sum(1 for r in rows if r.get("internal")) >= 2,
       "and both marks are on more than one row, or they prove nothing")
    ok(sum(1 for r in rows if r.get("papers")) >= 2,
       "and more than one crossing asks for papers, because the checkpoint is not the passport")

    # Every country, in every era, gets an answer.
    years = [-3000, -1000, -500, 0, 500, 1000, 1300, 1500, 1600, 1700, 1800, 1850, 1900, 1930,
             1950, 2000]
    for y in years:
        for sea in (False, True):
            got = {pick(d, c, y, sea)["id"] for c in codes}
            ok(len(got) > 1, "%6d %s: the world is not all one answer (%d different)"
               % (y, "by sea" if sea else "by land", len(got)))

    print()
    for c, y in (("IRQ", -1000), ("ITA", 100), ("ITA", 1300), ("ITA", 1500), ("FRA", 1450),
                 ("GBR", 1800), ("GBR", 1900), ("DEU", 1800), ("DEU", 1850), ("JPN", 1750),
                 ("JPN", 1900), ("CHN", 1800), ("CHN", 1900), ("USA", 1950), ("IND", 1600),
                 ("AUS", -500), ("BRA", 1700)):
        for sea in (False, True):
            r = pick(d, c, y, sea)
            marks = "".join(k[0].upper() for k in ("papers", "quarantine", "closed") if r.get(k))
            print("       %s %6d %-7s %-24s %-30s %-2s"
                  % (c, y, "sea" if sea else "land", r["name"][:24], r["demand"][:30], marks))
    print()

    # The dated facts, read out of the articles.
    ok(pick(d, "HRV", 1300, True)["id"] != "lazaretto",
       "Ragusa does not hold a traveller in 1300 - the trentino is 1377")
    ok(pick(d, "HRV", 1400, True)["id"] == "lazaretto",
       "and does by 1400, which is the first quarantine anywhere")
    ok(pick(d, "ITA", 1500, True)["id"] == "lazaretto",
       "a ship putting in at Venice in 1500 sits out the forty days")
    ok(pick(d, "ITA", 1500, False)["id"] != "lazaretto",
       "and a man riding over the Alps in 1500 does not, which is what the `sea` mark is for")
    ok(pick(d, "ITA", 1900, True).get("quarantine", False) is False,
       "and by 1900 the lazaretto has given way to the customs house")

    ok(pick(d, "GBR", 1900).get("papers", False) is False,
       "no crossing in 1900 asks for a passport")
    ok(pick(d, "GBR", 1930)["id"] == "passport_control",
       "and by 1930 the crossing is passport control")
    ok(pick(d, "FRA", 1960)["id"] == "checkpoint",
       "by 1960 it is the checkpoint, a barrier and a queue")

    ok(pick(d, "JPN", 1750, True).get("closed") is True,
       "Japan in 1750 is shut, which is sakoku")
    ok(pick(d, "JPN", 1900, True).get("closed", False) is False,
       "and by 1900 is open, which is after Perry")
    ok(pick(d, "CHN", 1800, True).get("closed") is True,
       "China in 1800 trades through one door, which is the Canton System")
    ok(pick(d, "CHN", 1900, True).get("closed", False) is False,
       "and by 1900 it does not, the system having ended in 1842")

    ok(pick(d, "DEU", 1850)["id"] == "zollverein",
       "the German states in 1850 do not stop each other's traffic, which is the Zollverein")
    ok(pick(d, "DEU", 1800)["id"] != "zollverein",
       "and in 1800 they do, the union having started in 1834")
    ok("1834" in pick(d, "DEU", 1850).get("note", ""),
       "and the row says the year, so the claim is checkable")

    ok(pick(d, "GBR", 1800)["id"] == "turnpike",
       "a man riding north through England in 1800 pays for the road at every gate")
    ok(pick(d, "GBR", 1800, True)["id"] != "turnpike",
       "and a ship putting in at Liverpool does not, which is what the `internal` mark is for")
    ok(pick(d, "GBR", 1900)["id"] != "turnpike",
       "by 1900 the road is free, the trusts having ended in 1888")
    ok(pick(d, "FRA", 1450)["id"] == "octroi",
       "France in 1450 takes a toll on everything carried into a town")

    ok(pick(d, "IRQ", -1000)["id"] == "tribute_gate",
       "Mesopotamia in 1000 BC is a gate and a gift")
    ok(pick(d, "IRN", 900)["id"] == "caravan_gate",
       "and the road east of it is the caravanserai and the gate toll")

    ok(pick(d, "AUS", -4000)["id"] == DEFAULT_ONLY,
       "before 3000 BC no row reaches anywhere, and the fallback answers: a frontier needs a "
       "state on both sides of it")
    ok(pick(d, "AUS", -500)["id"] != DEFAULT_ONLY,
       "by 500 BC the pack has an answer everywhere, which is the edge of the evidence and the "
       "reason the default is nearly unreachable")
    ok(all(r["id"] != DEFAULT_ONLY for r in rows),
       "and the default is not also a row, or it would shadow the fallback (%s)" % DEFAULT_ONLY)

    print()
    print("border: %d problem(s)" % len(bad))
    return len(bad)


if __name__ == "__main__":
    build()
    sys.exit(1 if check() else 0)
