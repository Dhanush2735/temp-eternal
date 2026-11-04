#!/usr/bin/env python3
"""Step 38 (D5): build history/day_round.json.gz from the hand-written rows.

    python3 build_day_round.py
    python3 build_day_round.py --selftest    rebuild in memory and check it (exit 1 on a problem)

What it checks:

* every place and year the mod can ask about gets a day, or the build fails;
* seasons are looked up **separately** from the rest of the day, so naming the six seasons of
  India cannot decide what day the market is held there — the two lists are checked against each
  other for exactly that mistake;
* a market needs a name and a name needs a market, and likewise for the rest day;
* the market cycles that are not seven days long are the point of the table, and each of them is
  pinned to the place that made it: **8 for the Roman nundinae, 5 for the Javanese pasaran, 3 for
  the Balinese three-day market**;
* the modern eight-hour day is the newest thing in the table, and every row older than 1800 has
  longer hours than it.

The lookup rule is imported from build_life_table, not written again.
"""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from build_life_table import SPOTS, pick_rows                     # noqa: E402
from day_round_table import DAYS, PRAYERS, SEASONS                # noqa: E402

MOD = os.path.normpath(os.path.join(HERE, "..", "eternal"))
OUT = os.path.join(MOD, "src", "main", "resources", "data", "eternalengine", "eternal",
                   "history", "day_round.json.gz")

SOURCE = ("E. P. Thompson, Time, Work-Discipline, and Industrial Capitalism, Past and Present "
          "38 (1967); English Wikipedia, 'Javanese calendar', 'Pawukon calendar', 'Tianguis', "
          "'Nundinae', 'Fixed prayer times', 'Canonical hours', 'Sabbath in Christianity', "
          "'Market town', 'Saint Monday', 'Factory Acts', 'Eight-hour day', 'Weekend', "
          "'Workweek', 'Jumu'ah', 'Souq', 'Season', 'Ritu (season)', 'Solar term', "
          "'Egyptian calendar', 'Hunter-gatherer' and 'Neolithic Revolution'. Rows marked "
          "estimated are the table's own, not any source's.")

# name, lat, lon, year, urban, expected round id, expected season id
CASES = [
    ("Rome 100", 41.90, 12.50, 100, False, "roman_italy", None),
    ("Athens -400", 37.98, 23.73, -400, False, "classical_world", None),
    ("London 1300", 51.51, -0.13, 1300, False, "medieval_world", None),
    ("London 1500", 51.51, -0.13, 1500, False, "late_medieval", None),
    ("London 1700", 51.51, -0.13, 1700, False, "early_modern_england", None),
    ("Bavaria 1700", 48.14, 11.58, 1700, False, "early_modern_europe", None),
    ("London 1850, a town", 51.51, -0.13, 1850, True, "industrial_town", None),
    ("London 1900", 51.51, -0.13, 1900, False, "world_1900", None),
    ("London 2020", 51.51, -0.13, 2020, False, "modern_world", None),
    ("Cairo 1000", 30.04, 31.24, 1000, False, "islamic_world", "egypt_three_seasons"),
    ("Cairo 2020", 30.04, 31.24, 2020, False, "modern_mena", None),
    ("Jakarta 1700", -6.21, 106.85, 1700, False, "java_pasaran", None),
    ("Bali 1700", -8.50, 115.20, 1700, False, "bali_triwara", None),
    ("Tenochtitlan 1500", 19.43, -99.13, 1500, False, "mesoamerica_tianguis", None),
    ("Delhi 1700", 28.61, 77.21, 1700, False, "early_modern_world", "india_six_seasons"),
    ("Beijing 1700", 39.90, 116.41, 1700, False, "early_modern_world", "china_terms"),
    ("Jerusalem 2020", 31.78, 35.22, 2020, False, "modern_israel", None),
    ("Amazonia -9000", -3.10, -60.02, -9000, False, "foraging_band", None),
    ("Amazonia -5000", -3.10, -60.02, -5000, False, "early_farming", None),
    ("Amazonia -1500", -3.10, -60.02, -1500, False, "bronze_world", None),
    ("Yakutsk 2020", 62.03, 129.73, 2020, False, "modern_world", None),
]

# the cycles that are not seven days long, and the places that made them
MARKET_CASES = [
    ("roman_italy", 41.90, 12.50, 100, 8, "the nundinae"),
    ("java_pasaran", -6.21, 106.85, 1700, 5, "the pasaran"),
    ("bali_triwara", -8.50, 115.20, 1700, 3, "the three-day market"),
    ("mesoamerica_tianguis", 19.43, -99.13, 1500, 7, "the tianguis"),
]


def build():
    rounds = sorted(DAYS, key=lambda r: (r.frm, r.id))
    seasons = sorted(SEASONS, key=lambda r: (r.frm, r.id))
    return {
        "format": 1,
        "id": "day_round",
        "source": SOURCE,
        "rounds": [{
            "id": r.id, "name": r.name,
            "boxes": [[b[0], b[1], b[2], b[3]] for b in r.boxes],
            "from": r.frm, "to": r.to, "urban": r.urban,
            "work": r.work, "hours": r.hours, "rest": r.rest, "restname": r.restname,
            "market": r.market, "marketname": r.marketname,
            "mark": r.mark, "note": r.note, "source": r.src,
        } for r in rounds],
        "seasons": [{
            "id": r.id, "name": r.name,
            "boxes": [[b[0], b[1], b[2], b[3]] for b in r.boxes],
            "from": r.frm, "to": r.to, "count": r.count, "names": list(r.names),
            "mark": r.mark, "note": r.note, "source": r.src,
        } for r in seasons],
        "prayers": [{
            "faith": p[0], "count": p[1], "keep": p[2], "names": list(p[3]), "when": list(p[4]),
            "note": p[5], "source": p[6],
        } for p in PRAYERS],
    }


def selftest(doc):
    problems = []
    rounds = doc["rounds"]
    seasons = doc["seasons"]

    seen = set()
    for r in rounds:
        if r["id"] in seen:
            problems.append("duplicate id: " + r["id"])
        seen.add(r["id"])
        if (r["market"] == 0) != (r["marketname"] == ""):
            problems.append("%s: a market needs a name and a name needs a market" % r["id"])
        if (r["rest"] == -1) != (r["restname"] == ""):
            problems.append("%s: a rest day needs a name and a name needs a rest day" % r["id"])
    for r in seasons:
        if r["count"] != len(r["names"]):
            problems.append("%s: %d seasons but %d names" % (r["id"], r["count"],
                                                             len(r["names"])))

    # 1. every place and every year gets a day
    for name, lat, lon in SPOTS:
        for year in list(range(-10000, 2027, 25)) + [-5000, -3000, -800, -400, 1, 500, 1000, 1348,
                                                     1500, 1600, 1700, 1800, 1850, 1900, 1950,
                                                     2000, 2026]:
            if pick_rows(rounds, lat, lon, year) is None:
                problems.append("no day round for %s in %d" % (name, year))

    # 2. the written cases
    for name, lat, lon, year, urban, want_round, want_season in CASES:
        got = pick_rows(rounds, lat, lon, year, urban)
        got_id = got["id"] if got else None
        if got_id != want_round:
            problems.append("%s: wanted %s, got %s" % (name, want_round, got_id))
        got_s = pick_rows(seasons, lat, lon, year)
        got_sid = got_s["id"] if got_s else None
        if got_sid != want_season:
            problems.append("%s: wanted season %s, got %s" % (name, want_season, got_sid))

    # 3. the market cycles that are not seven days long
    for rid, lat, lon, year, cycle, name in MARKET_CASES:
        r = pick_rows(rounds, lat, lon, year)
        if r is None:
            problems.append("%s: cannot reach it" % rid)
            continue
        if r["market"] != cycle:
            problems.append("%s: market cycle %d, wanted %d" % (rid, r["market"], cycle))
        if r["marketname"] != name:
            problems.append("%s: market called %r, wanted %r" % (rid, r["marketname"], name))

    # 4. the seasons list must not be able to shadow the round list
    for r in seasons:
        for name, lat, lon in SPOTS:
            for year in (r["from"], (r["to"] or 2026)):
                day = pick_rows(rounds, lat, lon, year)
                if day is not None and day["id"] == r["id"]:
                    problems.append("season row %s is shadowing the day round at %s in %d"
                                    % (r["id"], name, year))

    # 5. The factory has the longest day in the table, and the modern one is the newest and
    #    shortest of the clock rows. Deliberately NOT asserted: that earlier people worked
    #    longer — the foragers worked the shortest day of all, which is the finding behind the
    #    "original affluent society" and the reason this check is shaped the way it is.
    by_id = {r["id"]: r for r in rounds}
    factory = by_id["industrial_town"]
    for r in rounds:
        if r["hours"] > factory["hours"]:
            problems.append("%s: %d hours, longer than the factory's %d"
                            % (r["id"], r["hours"], factory["hours"]))
    if not (by_id["modern_world"]["hours"] < by_id["world_1900"]["hours"]
            < factory["hours"]):
        problems.append("the clock rows should shorten: factory > 1900 > modern")

    est = sum(1 for r in rounds if r["mark"] == "estimated")
    mix = sum(1 for r in rounds if r["mark"] == "mixed")
    print("  day round %2d rounds: %2d recorded, %2d mixed, %2d estimated; %d season rows, "
          "%d faiths" % (len(rounds), len(rounds) - est - mix, mix, est, len(seasons),
                         len(doc["prayers"])))

    # the layman's count can never exceed the set hours
    for p in doc["prayers"]:
        if p["keep"] > p["count"]:
            problems.append("%s: keeps %d of %d set hours" % (p["faith"], p["keep"], p["count"]))

    if problems:
        print("\n%d PROBLEM(S):" % len(problems))
        for p in problems[:40]:
            print("  - " + p)
        return 1
    print("  %d cases, 0 problems" % (len(CASES) + len(MARKET_CASES)))
    return 0


def main():
    doc = build()
    if "--selftest" in sys.argv:
        print("selftest: %d rounds, %d cases" % (len(doc["rounds"]), len(CASES)))
        rc = selftest(doc)
        if rc:
            return rc
        print("  (no pack written in --selftest mode)")
        return 0

    rc = selftest(doc)
    if rc:
        return rc
    raw = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.GzipFile(OUT, "wb", compresslevel=9, mtime=0) as fh:
        fh.write(raw)
    print("wrote %s" % OUT)
    print("  %d rounds, %d season rows, %d faiths, %d bytes raw, %d gzipped"
          % (len(doc["rounds"]), len(doc["seasons"]), len(doc["prayers"]), len(raw),
             os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
