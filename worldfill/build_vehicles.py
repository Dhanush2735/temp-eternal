#!/usr/bin/env python3
"""
Step 46 part 3 (E10 A): pack the vehicle register — every way there has been of getting somewhere.

    python3 build_vehicles.py            build, then write
    python3 build_vehicles.py --check    check only, write nothing

The register lives in `vehicle_table.py`. This script only checks it and writes it out.

**It reads, it does not rewrite.** Three registers in the mod already date these things: the
products atlas (34 transport goods, per area), the technology atlas (spread curves for 258
countries) and the armoury (the war chariot, the elephant, the mounted bow, with their never-maps).
This register names which one owns each vehicle's date and lets the mod answer it.

**What is new is the `needs` column.** The other registers say *when a thing exists*. They do not
say *what it runs on*, and that is the whole of E11: a train needs a railway **here**, a canal boat
needs a canal **here**, a cart needs a beast that has arrived **here**. Step 34's `WaysGrid` already
answers the road/rail/canal half for 124,240 squares; this register is what joins a vehicle to it.

**A systematic finding is recorded, not patched around.** The products atlas dates `rickshaws` and
`wheelbarrows` at EUR −3000 — the exact date of `carts` — and `oars` at −10000 in all 17 areas.
Those are template copies from step 44 part C, where a child inherited a parent's row unchanged.
This register has met that artefact four times now, so the rule is stated once: a products-atlas
date is used only where it is independently sensible, and six vehicles carry explicit sourced dates
instead. All six are listed in the pack.

Run from the repository root:  python3 worldfill/build_vehicles.py
"""

import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data",
                   "eternalengine", "eternal", "economy", "vehicles.json.gz")

SYS_PATH = sys.path[:]
sys.path.insert(0, HERE)
try:
    import vehicle_table as T
finally:
    sys.path = SYS_PATH

# Vehicles whose date is answerable only by the technology atlas, because it stores a spread curve
# per country rather than a flat year per area.
ATLAS_TECHS = {"chariot"}


def build():
    problems = list(T.problems())
    vehicles = []
    for v in T.VEHICLES:
        kind, key = v["yearsFrom"]
        vehicles.append({
            "id": v["id"],
            "name": v["name"],
            "medium": v["medium"],
            "needs": v["needs"],
            "beast": v["beast"],
            "people": v["people"],
            "loadKg": v["loadKg"],
            "kmPerDay": v["kmPerDay"],
            "years": T.years_for(v),
            "never": T.never_for(v),
            "end": T.end_for(v),
            "atlasId": key if kind == "tech" else None,
            "yearSource": kind,
            "supersedes": v["supersedes"],
            "vanilla": v["vanilla"],
            "mark": v["mark"],
            "note": v["note"].replace("**", ""),
            "source": v["source"],
            "corrected": T.CORRECTED.get(v["id"]),
        })
    doc = {
        "format": "eternal-vehicles-1",
        "id": "vehicles",
        "source": ("Dates from three of the mod's own registers: the products atlas (step 44 part "
                   "C), the technology atlas (step 30a) and the armoury (step 45 part 2). Speeds "
                   "and capacities are the mod's own, carried over from VehicleType wherever it "
                   "already named one. The six corrected dates are sourced in `corrections`."),
        "note": ("Every way there has been of getting somewhere, covering the plan's E10 list: "
                 "porters, palanquins, carts, chariots, horses, camels, elephants, bicycles, "
                 "rickshaws, trams, buses, cars, lorries; rafts, dhows, galleys, junks, sailing "
                 "ships, steamships; trains; balloons, airships, planes. THE DATES ARE READ, NOT "
                 "REWRITTEN - three registers already owned them. What is new is the `needs` "
                 "column: the other registers say when a thing exists, but not what it runs on, "
                 "and that is the whole of E11. A train needs a railway HERE, a canal boat a canal "
                 "HERE, a cart a beast that has arrived HERE - and step 34's WaysGrid already "
                 "answers the road, rail and canal half for 124,240 squares."),
        "corrections": list(T.CORRECTED.values()),
        "finding": ("**A systematic artefact in step 44 part C, met four times.** The products "
                    "atlas dates `rickshaws` and `wheelbarrows` at EUR -3000 - the exact date of "
                    "`carts` - and `oars` at -10000 in all 17 areas. Those are template copies: "
                    "part C derived each child from a parent, and several children inherited the "
                    "parent's row unchanged. The same artefact put reindeer in West Africa and "
                    "gave donkeys the horse's date (both corrected in part 2). The rule now "
                    "stated once: a products-atlas date is used only where it is independently "
                    "sensible, and anything else carries an explicit sourced date marked "
                    "estimated."),
        "counts": {
            "vehicles": len(vehicles),
            "mediums": len(set(v["medium"] for v in vehicles)),
            "recorded": sum(1 for v in vehicles if v["mark"] == "recorded"),
            "estimated": sum(1 for v in vehicles if v["mark"] == "estimated"),
            "corrected": sum(1 for v in vehicles if v["corrected"]),
            "byAtlas": sum(1 for v in vehicles if v["atlasId"]),
        },
        "vehicles": vehicles,
    }
    return doc, problems


def check(doc):
    bad = []

    def ok(cond, what):
        print(("  ok   " if cond else "  FAIL ") + what)
        if not cond:
            bad.append(what)

    ok(doc["format"] == "eternal-vehicles-1", "the format is the one this builder writes")
    for key in ("vehicles", "corrections", "finding", "counts"):
        ok(key in doc, "the pack carries %s" % key)

    vs = doc["vehicles"]
    ok(len(vs) >= 25, "%d vehicles" % len(vs))

    # The plan's E10 list, checked against the pack rather than against the module.
    want = ["porter", "palanquin", "cart", "chariot", "horse", "camel", "elephant", "bicycle",
            "rickshaw", "tram", "bus", "car", "lorry", "raft", "dhow", "galley", "junk",
            "sailing ship", "steamship", "train", "balloon", "airship", "plane"]
    have = " ".join(v["id"] + " " + v["name"] for v in vs).lower()
    missing = [w for w in want if w not in have]
    ok(not missing, "the plan's whole E10 list is covered"
                    + ("" if not missing else " - missing " + ", ".join(missing)))

    # Every vehicle must move, carry, and say what it needs and where it came from.
    ok(all(v["kmPerDay"] > 0 for v in vs), "every vehicle goes somewhere")
    ok(all(v["needs"] for v in vs), "every vehicle needs something - there is no free travel")
    ok(all(v["medium"] in T.MEDIUMS for v in vs), "every medium is one of the six")
    ok(all(n in T.NEEDS for v in vs for n in v["needs"]), "every need is one of the eight")
    ok(all(v["mark"] in ("recorded", "estimated") for v in vs), "every vehicle is marked")
    ok(all(v["note"] and v["source"] for v in vs), "every vehicle is sourced")

    # THE JOIN: a rail vehicle must need a rail, a water vehicle water, an air vehicle air.
    rail = [v["id"] for v in vs if v["medium"] == "rail"
            and not any(n in ("rail", "tramline") for n in v["needs"])]
    ok(not rail, "every rail vehicle needs a railway" + (": " + ", ".join(rail) if rail else ""))
    watr = [v["id"] for v in vs if v["medium"] == "water" and "water" not in v["needs"]]
    ok(not watr, "every water vehicle needs water")
    air = [v["id"] for v in vs if v["medium"] == "air" and "air" not in v["needs"]]
    ok(not air, "every air vehicle needs air")
    # A beast-drawn vehicle must name its beast, so D14 can say whether it has arrived.
    beastless = [v["id"] for v in vs if "beast" in v["needs"] and not v["beast"]]
    ok(not beastless, "every beast-drawn vehicle names its beast"
                      + (": " + ", ".join(beastless) if beastless else ""))

    # A vehicle must exist somewhere, either by flat years or by the technology atlas.
    nowhere = [v["id"] for v in vs if not v["years"] and not v["atlasId"]]
    ok(not nowhere, "every vehicle reaches somewhere, or is dated by the atlas"
                    + (": " + ", ".join(nowhere) if nowhere else ""))

    # Areas must be the atlas's own 17.
    ok(all(a in T.AREAS for v in vs for a in v["years"]), "every year-area is one of the 17")
    ok(all(a in T.AREAS for v in vs for a in v["never"]), "every never-area is one of the 17")

    # The corrections must be recorded, not silent.
    ok(len(doc["corrections"]) >= 6, "%d corrected dates are shipped in the pack"
       % len(doc["corrections"]))
    ok(doc["finding"].count("template"), "the systematic finding is stated")

    # The oldest vehicles need nothing at all, which is the register's own claim about prehistory.
    nothing = [v["id"] for v in vs if v["needs"] == ["none"]]
    ok(len(nothing) >= 2, "%d vehicles need nothing at all: %s"
       % (len(nothing), ", ".join(nothing)))

    # The two joins that carry a date from ANOTHER register into this one. A vehicle dated by the
    # technology atlas must still carry the armoury's never-map, or a chariot appears in
    # Tenochtitlan; and a vehicle whose date was corrected must actually be restricted by it.
    byId = {v["id"]: v for v in vs}
    ok(len(byId["chariot"]["never"]) >= 8,
       "the chariot keeps the armoury's never-map (%d areas)" % len(byId["chariot"]["never"]))
    ok(len(byId["chariot"]["end"]) >= 8,
       "and its end-years (%d areas)" % len(byId["chariot"]["end"]))
    ok("AUS" not in byId["sledge"]["years"] and "MSA" not in byId["sledge"]["years"],
       "the corrected sledge is not in Australia or Middle Africa")
    ok(byId["balloon"]["years"]["EUR"] < byId["aeroplane"]["years"]["EUR"],
       "the corrected balloon precedes the aeroplane (1783 before 1919)")
    ok(byId["helicopter"]["years"]["EUR"] > byId["aeroplane"]["years"]["EUR"] - 100
       and byId["helicopter"]["years"]["EUR"] >= 1936,
       "the corrected helicopter follows the aeroplane (1936)")
    ok(byId["sailing_ship"]["years"]["EUR"] > -4000,
       "the corrected sailing ship is not a 200-tonne ship in 10000 BC (EUR %d)"
       % byId["sailing_ship"]["years"]["EUR"])
    # A ship that predates the sail is a boat, and the register must not call it a ship.
    ok(byId["sailing_ship"]["years"]["EUR"] > byId["canoe"]["years"]["EUR"],
       "the sailing ship comes after the canoe")

    return bad


def main(argv):
    doc, problems = build()
    for p in problems:
        print("  PROBLEM " + p)

    c = doc["counts"]
    print("vehicles: %d entries over %d mediums (%d recorded, %d estimated, %d corrected, %d by "
          "the technology atlas)"
          % (c["vehicles"], c["mediums"], c["recorded"], c["estimated"], c["corrected"],
             c["byAtlas"]))

    bad = check(doc)
    if problems or bad or "--check" in argv:
        return 1 if (problems or bad) else 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with gzip.GzipFile(OUT, "wb", mtime=0) as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    print("  wrote %s (%d bytes)" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
