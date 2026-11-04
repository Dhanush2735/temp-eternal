#!/usr/bin/env python3
"""Step 38 (C7): build history/migrations.json.gz from the hand-written records.

    python3 build_migrations.py
    python3 build_migrations.py --selftest     rebuild in memory and check it (exit 1 on a problem)

What it checks:

* every record is sourced, dated and placed, and no two records share an id;
* the four Partition rows add up to more than thirteen million, because if they do not then the
  largest migration in the history of the world is not in this table;
* the three Atlantic slave-trade routes add up to the number the Slave Voyages database says was
  landed — 10.7 million — to within a rounding;
* a route is a real distance, not a mistake: nothing under 50 km and nothing over 20,000 km,
  and a row marked as a sea route really is one that a land route could not serve.

This pack is **records, not a field**. A place in a year with no record is not a place with no
migration; it is a place where nobody counted, and the register says so out loud.
"""
import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from migrations_table import MIGRATIONS                          # noqa: E402

MOD = os.path.normpath(os.path.join(HERE, "..", "eternal"))
OUT = os.path.join(MOD, "src", "main", "resources", "data", "eternalengine", "eternal",
                   "history", "migrations.json.gz")

SOURCE = ("English Wikipedia: 'Partition of India', 'Partition of Bengal', 'Bangladesh Liberation "
          "War', 'Afghan refugees', 'Population exchange between Greece and Turkey', 'Armenian "
          "genocide', 'Flight and expulsion of Germans from Poland during and after World War "
          "II', 'Expulsion of Germans from Czechoslovakia', 'Population transfer', 'Bosnian War', "
          "'Atlantic slave trade', 'Indian indenture system', 'Coolie', 'Windrush generation', "
          "'Great Famine (Ireland)', 'Huguenots', 'Expulsion of the Moriscos', 'Great Migration "
          "(African American)', 'Dust Bowl', 'Mexican Repatriation', '1948 Palestinian expulsion "
          "and flight', 'Operation Ezra and Nehemiah', 'Deportation of the Volga Germans', "
          "'Vietnamese boat people', 'Refugees of the Syrian civil war', 'Rwandan genocide', "
          "'Bantu expansion', 'Anglo-Saxon settlement of Britain', 'Turkic migration', 'Mongol "
          "Empire' and 'Mfecane'; Voyages: The Trans-Atlantic Slave Trade Database; UNHCR and "
          "UNRWA. Rows marked estimated carry this table's own numbers, not any source's.")


def km(a_lat, a_lon, b_lat, b_lon):
    p = math.pi / 180.0
    h = (0.5 - math.cos((b_lat - a_lat) * p) / 2.0
         + math.cos(a_lat * p) * math.cos(b_lat * p) * (1 - math.cos((b_lon - a_lon) * p)) / 2.0)
    return 12742.0 * math.asin(math.sqrt(max(0.0, h)))


def build():
    rows = sorted(MIGRATIONS, key=lambda r: (r.year, r.id))
    return {
        "format": 1,
        "id": "migrations",
        "source": SOURCE,
        "migrations": [{
            "id": r.id, "name": r.name,
            "flat": r.flat, "flon": r.flon, "fname": r.fname,
            "tlat": r.tlat, "tlon": r.tlon, "tname": r.tname,
            "year": r.year, "end": r.end, "people": r.people,
            "kind": r.kind, "forced": r.forced, "sea": r.sea,
            "mark": r.mark, "note": r.note, "source": r.src,
            "km": round(km(r.flat, r.flon, r.tlat, r.tlon), 1),
        } for r in rows],
    }


def selftest(doc):
    problems = []
    rows = doc["migrations"]
    seen = set()
    for r in rows:
        if r["id"] in seen:
            problems.append("duplicate id: " + r["id"])
        seen.add(r["id"])
        if not r["source"]:
            problems.append("%s has no source" % r["id"])
        if not (50.0 <= r["km"] <= 20000.0):
            problems.append("%s: %s -> %s is %.0f km, which is not a route"
                            % (r["id"], r["fname"], r["tname"], r["km"]))
        if r["end"] is not None and r["end"] < r["year"]:
            problems.append("%s ends before it starts" % r["id"])

    by_id = {r["id"]: r for r in rows}

    # 1. the largest migration in the history of the world has to actually be in here
    partition = sum(r["people"] for r in rows if r["id"].startswith("partition_"))
    if partition < 13_000_000:
        problems.append("the four Partition rows add to only %d; the largest migration in human "
                        "history is not in this table" % partition)

    # 2. the three Atlantic routes must add to what the Slave Voyages database says was landed
    landed = sum(r["people"] for r in rows if r["id"].startswith("atlantic_slave_trade_"))
    if abs(landed - 10_700_000) > 500_000:
        problems.append("the Atlantic routes add to %d, not the 10.7 million who were landed"
                        % landed)

    # 3. a sea route is one the land could not serve
    for r in rows:
        if r["sea"] and r["km"] < 300.0:
            problems.append("%s is marked a sea route but is only %.0f km"
                            % (r["id"], r["km"]))

    # 4. the forced/voluntary split must not be a formality
    forced = sum(1 for r in rows if r["forced"])
    if forced < len(rows) // 2:
        problems.append("only %d of %d records are forced: most of this table's migrations were "
                        "not chosen" % (forced, len(rows)))

    est = sum(1 for r in rows if r["mark"] == "estimated")
    mix = sum(1 for r in rows if r["mark"] == "mixed")
    print("  migrations %2d records: %2d recorded, %2d mixed, %2d estimated"
          % (len(rows), len(rows) - est - mix, mix, est))
    print("  Partition %s people; Atlantic slave trade %s landed"
          % (f"{partition:,}", f"{landed:,}"))

    if problems:
        print("\n%d PROBLEM(S):" % len(problems))
        for p in problems[:40]:
            print("  - " + p)
        return 1
    print("  0 problems")
    return 0


def main():
    doc = build()
    if "--selftest" in sys.argv:
        print("selftest: %d migration records" % len(doc["migrations"]))
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
    print("  %d records, %d bytes raw, %d gzipped"
          % (len(doc["migrations"]), len(raw), os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
