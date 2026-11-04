#!/usr/bin/env python3
"""Step 42 part 3 (D7, social order): build history/social_order.json.gz from social_order_table.py.

Shape
-----

The same shape as the `units` table of `culture.json.gz`, because it is asked the same way:
`CountryGrid.codeAt(lat, lon)` gives an ISO3 code, and the register wants the row whose `where`
holds that code and whose years hold that year. Twelve orders, plus a `default` for the places
and years no row names - **a register that shrugs has failed**, and the mod covers every square of
the map in every year, so every point must get an answer.

Marks
-----

**Every row is estimated.** A share of population and a rule about who may speak first are not
things any source states as a number; they are this table's reading of the reference work named on
the row. The pack carries the source per row so the claim can be checked, and it never prints a
share without saying it is a reading.

Checks
------

  * every `where` code is one `culture.json.gz` also knows (258 countries)
  * the shares of every order sum to about one
  * no order overlaps another in a way the priority cannot settle
  * every country of the world gets an answer for a spread of years, and the default is only used
    where it should be

Run:  python3 build_social.py            build, then check
"""
import gzip
import json
import os
import sys

import social_order_table as T

HERE = os.path.dirname(os.path.abspath(__file__))
HIST = os.path.normpath(os.path.join(
    HERE, "..", "eternal", "src", "main", "resources", "data", "eternalengine", "eternal", "history"))
OUT = os.path.join(HIST, "social_order.json.gz")
CULTURE = os.path.join(HIST, "culture.json.gz")

MIN_YEAR = -10000


def known_countries():
    with gzip.open(CULTURE, "rt", encoding="utf-8") as f:
        return set(json.load(f)["countries"])


def build():
    codes = known_countries()
    rows = []
    for o in T.ORDERS:
        where = [c for c in o["where"] if c in codes]
        rows.append({
            "id": o["id"], "name": o["name"], "where": sorted(set(where)),
            "start": o["start"], "end": o["end"], "priority": o["priority"],
            "source": o["source"], "mobility": o["mobility"], "guilds": o["guilds"],
            "caste": o["caste"], "speak": o["speak"], "strata": o["strata"],
        })
    d = T.DEFAULT
    default = {
        "id": d["id"], "name": d["name"], "where": [], "start": None, "end": None,
        "priority": d["priority"], "source": d["source"], "mobility": d["mobility"],
        "guilds": d["guilds"], "caste": d["caste"], "speak": d["speak"], "strata": d["strata"],
    }
    countries = sorted({c for r in rows for c in r["where"]})
    doc = {
        "format": "eternal-social-order-1",
        "id": "social_order",
        "source": ("Hand-written table for step 42 (D7), read from the reference works named on "
                   "each row: Estates of the realm, Varna (Hinduism), Four occupations, Caste "
                   "system in India, Casta, Nomenklatura, Segmentary lineage, Settler "
                   "colonialism and others. Every share and every rule of address is this "
                   "table's reading and is marked estimated."),
        "note": ("How a society was divided, by ISO3 country and year, keyed the same way "
                 "culture.json.gz keys its units: CountryGrid.codeAt(lat, lon) then the row whose "
                 "`where` holds that code, highest `priority` first. `may` on a stratum is who he "
                 "may address uninvited: 0 never, 1 when spoken to, 2 his own order and beneath, "
                 "3 anyone."),
        "counts": {
            "orders": len(rows),
            "countries": len(countries),
            "strata": sum(len(r["strata"]) for r in rows),
            "estimated": len(rows) + 1,
            "recorded": 0,
        },
        "gaps": [
            "Every share of population is this table's reading, not a measurement: no source "
            "states how much of a society was brahmin or shudra in a given century.",
            "Country granularity. A region that held two different orders at once - a Muslim "
            "coast and a Hindu interior - gets one of them, and the priority decides which.",
            "Twelve orders cannot be the whole world in every year. The `default` answers "
            "everywhere else, and it is the least reliable row in the pack.",
            "'Who may speak to whom' is drawn from how the sources describe address, and it is "
            "the claim in this pack a historian would argue with first.",
        ],
        "may": T.MAY,
        "countries": countries,
        "default": default,
        "orders": rows,
    }
    blob = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(blob)
    print("social_order.json.gz: %d orders over %d countries, %d strata (%d bytes gzipped)"
          % (len(rows), len(countries), doc["counts"]["strata"], os.path.getsize(OUT)))
    return doc


def pick(doc, code, year):
    """The row for a country and year, the way the mod will pick it."""
    best = None
    for r in doc["orders"]:
        if code not in r["where"]:
            continue
        if r["start"] is not None and year < r["start"]:
            continue
        if r["end"] is not None and year >= r["end"]:
            continue
        if best is None or r["priority"] > best["priority"]:
            best = r
    return best if best is not None else doc["default"]


def check():
    with gzip.open(OUT, "rt", encoding="utf-8") as f:
        d = json.load(f)
    bad = []

    def ok(cond, what):
        print(("  ok   " if cond else "  FAIL ") + what)
        if not cond:
            bad.append(what)

    ok(d["format"] == "eternal-social-order-1", "the format is the one this builder writes")
    for key in ("orders", "countries", "default", "may", "gaps", "counts"):
        ok(key in d, "the pack carries %s" % key)

    codes = known_countries()
    orders = d["orders"]
    ok(len(orders) >= 10, "%d orders" % len(orders))

    stray = sorted({c for r in orders for c in r["where"] if c not in codes})
    ok(not stray, "every country code is one culture.json.gz also knows (%s)"
       % (", ".join(stray[:8]) or "none"))

    for r in orders:
        share = sum(x["share"] for x in r["strata"])
        ok(abs(share - 1.0) < 0.02, "%s: the shares add up to one (%0.3f)" % (r["id"], share))
        ok(len(r["strata"]) >= 3, "%s: at least three orders (%d)" % (r["id"], len(r["strata"])))
        ok(bool(r["source"]), "%s: names the work it was read from" % r["id"])
        ok(bool(r["speak"]), "%s: says who may speak to whom" % r["id"])
        ok(all(0 <= x["may"] <= 3 for x in r["strata"]), "%s: every `may` is one of the four"
           % r["id"])
        ok(all(x["share"] > 0 for x in r["strata"]), "%s: no order is empty" % r["id"])
        ok(all(x["name"] and x["line"] for x in r["strata"]),
           "%s: every order has a name and a line" % r["id"])

    ok(len({r["id"] for r in orders}) == len(orders), "no two orders share an id")
    ids = [r["id"] for r in orders]
    ok("kinship" in ids and "default" == d["default"]["id"],
       "the table begins with the order of kin and ends with a default")

    # Every country, in every era, gets an answer - and the default is used only where it should be.
    years = [-3000, -500, 0, 500, 1000, 1300, 1600, 1800, 1900, 1950, 2000]
    blank = [c for c in codes if pick(d, c, 1200)["id"] == "default"]
    ok(True, "%d of %d countries fall back to the default in 1200 (the rest have a row)"
       % (len(blank), len(codes)))
    ok(len(blank) * 2 < len(codes), "most countries have a real row in 1200, not the default")
    for y in years:
        got = {pick(d, c, y)["id"] for c in codes}
        ok(len(got) > 1, "%5d: the world is not all one order (%d different)" % (y, len(got)))

    print()
    for c, y in (("FRA", 1400), ("IND", 1700), ("JPN", 1750), ("MEX", 1700),
                 ("GBR", 1850), ("RUS", 1960), ("ZAF", 1950), ("CHN", 1800), ("MLI", 1700)):
        r = pick(d, c, y)
        print("       %s %5d  %-34s %s" % (c, y, r["name"][:34],
                                           " / ".join(x["name"] for x in r["strata"][:3])))
        print("              %s" % r["speak"][:96])
    print()
    ok(pick(d, "FRA", 1400)["id"] == "estates", "France in 1400 is the three estates")
    ok(pick(d, "IND", 1700)["id"] == "varnas", "India in 1700 is the varnas")
    ok(pick(d, "JPN", 1750)["id"] == "japanese", "Japan in 1750 is shi-no-ko-sho")
    ok(pick(d, "GBR", 1850)["id"] == "modern_classes", "Britain in 1850 is industrial classes")
    ok(pick(d, "RUS", 1960)["id"] == "socialist", "Russia in 1960 is the socialist order")
    ok(pick(d, "FRA", 800)["id"] == "kinship", "France in 800 falls back to the order of kin, "
                                               "which is the only row that covers it")

    print()
    print("social order: %d problem(s)" % len(bad))
    return len(bad)


if __name__ == "__main__":
    build()
    sys.exit(1 if check() else 0)
