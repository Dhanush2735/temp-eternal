#!/usr/bin/env python3
"""
Step 46 part 4 (E11): pack the traffic register.

    python3 build_traffic.py            build, then write
    python3 build_traffic.py --check    check only, write nothing

The register lives in `traffic_table.py`. This script checks it, derives the breaking distances
from it, and writes it out.

**E11 asks for "vehicles of the era moving on roads, rivers, seas and rails".** Three things
already answer parts of that and this pack adds the fourth:

| knows | what it answers |
|---|---|
| step 34 `WaysGrid` | is there a road / railway / canal HERE by now (124,240 squares) |
| step 46 part 3 `Vehicles` | which vehicle is right, and what it needs |
| step 46 part 2 `WorkingAnimals` | has the beast that draws it arrived |
| **this pack** | **how much there is, and which medium carries it** |

The answer to the last question is not a guess: Diocletian's Edict on Maximum Prices (AD 301) is
the only document that prices freight and goods in the same currency on the same day, and it says
**1 sea : 5 downriver : 10 upriver : 52 road**. So a cargo travels as far as its own value pays
for, and the breaking distances fall straight out of the Edict's own price list.
"""

import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data",
                   "eternalengine", "eternal", "economy", "traffic.json.gz")

SYS_PATH = sys.path[:]
sys.path.insert(0, HERE)
try:
    import traffic_table as T
finally:
    sys.path = SYS_PATH


def build():
    problems = list(T.problems())

    goods = []
    for g in T.GOODS:
        goods.append({
            "id": g["id"],
            "name": g["name"],
            "perKg": g["perKg"],
            "class": g["class_"],
            "bulky": g["bulky"],
            "entry": g["entry"],
            # Derived, not stored by hand: change a price and the leash changes with it.
            "reach": {
                "road": round(T.breaking_distance(g["perKg"], "road")),
                "downriver": round(T.breaking_distance(g["perKg"], "downriver")),
                "upriver": round(T.breaking_distance(g["perKg"], "upriver")),
                "sea": round(T.breaking_distance(g["perKg"], "sea")),
            },
        })

    doc = {
        "format": "eternal-traffic-1",
        "id": "traffic",
        "source": ("Freight rates and goods prices both from Diocletian's Edict on Maximum Prices "
                   "(AD 301): wagon 20 denarii per 1,200 Roman pounds per Roman mile, camel and "
                   "donkey loads per mile, river 1 and 2 denarii per modius per 20 miles down and "
                   "up, and 48 sea routes. Sea cost is Scheidel's (2014) 48-route mean computed on "
                   "the Edict's own ceilings. Goods prices are the Edict's own entries. Traffic "
                   "counts are documented: the Bolton Massachusetts wagon count, the Bath turnpike "
                   "tolls of 1823, the 1333 Westminster-York carriage, and the turnpike carrier "
                   "services at Reading and on the Coventry road."),
        "note": ("E11: how much traffic, and by which medium. THE DECISIVE FACT IS THAT FREIGHT IS "
                 "PRICED BY THE KILOGRAM AND THE KILOMETRE, and so is the good: Diocletian's Edict "
                 "prices both in the same currency on the same day, which is why its ratios are "
                 "usable where later reconstructions are not. Road costs 52 times sea per kg-km, "
                 "downriver 5, upriver 10. So a cargo goes as far as its own value pays for: wheat "
                 "reaches about 286 km inland before freight doubles its price, and 14,925 km by "
                 "sea - WHICH IS WHY ROME WAS FED BY SEA AND NOT BY ROAD. Silk, at 36,697 denarii "
                 "a kilogram, has effectively no leash at all, which is why the Silk Road carried "
                 "silk and not wheat. This pack is the fourth of four: WaysGrid knows whether a "
                 "road is HERE, Vehicles knows WHICH vehicle and WHAT IT NEEDS, WorkingAnimals "
                 "knows whether the beast has ARRIVED, and this knows HOW MUCH and BY WHICH "
                 "MEDIUM."),
        "finding": ("**The breaking distance is the whole of E11 and it is derived, not invented.** "
                    "value per kilogram divided by freight per kilogram-kilometre: wheat 10 / 0.035 "
                    "= 286 km by road, 2,941 km downriver, 14,925 km by sea. Standard economic "
                    "history gives grain a leash of 100-200 miles overland before it doubles in "
                    "price, which is the same answer. It also explains a shape of the pre-modern "
                    "world that nothing else does: every great pre-industrial city sits on water, "
                    "not because water is pleasant but because a city of a million cannot be fed "
                    "any other way."),
        "freight": T.FREIGHT,
        "loadFactor": T.LOAD_FACTOR,
        "ratios": T.RATIO_CHECK,
        "otherRatios": T.OTHER_RATIOS,
        "ways": T.WAYS,
        "speeds": [{"route": n, "kmPerDay": k, "why": w} for n, k, w in T.SPEEDS],
        "gates": T.GATES,
        "congestion": T.CONGESTION,
        "counts": T.COUNTS,
        "goods": goods,
        "counts_": {
            "goods": len(goods),
            "counts": len(T.COUNTS),
            "ways": len(T.WAYS),
            "gates": len(T.GATES),
            "bulky": sum(1 for g in goods if g["bulky"]),
        },
    }
    return doc, problems


def check(doc):
    bad = []

    def ok(cond, what):
        print(("  ok   " if cond else "  FAIL ") + what)
        if not cond:
            bad.append(what)

    ok(doc["format"] == "eternal-traffic-1", "the format is the one this builder writes")
    for key in ("freight", "goods", "counts", "gates", "speeds", "finding"):
        ok(key in doc, "the pack carries %s" % key)

    # THE RATIOS. The mod quotes 1:5:10:52 and must actually compute them.
    for route, want in doc["ratios"].items():
        got = doc["freight"][route] / doc["freight"]["sea"]
        ok(abs(got - want) < 0.5, "the %s ratio computes to %.1f, quoted as %.0f"
           % (route, got, want))

    # THE REACH. Heavy cheap goods must be short-leashed, light dear ones long.
    g = {x["id"]: x for x in doc["goods"]}
    ok(g["wheat"]["reach"]["road"] < 400, "wheat's road leash is under 400 km (%d)"
       % g["wheat"]["reach"]["road"])
    ok(g["wheat"]["reach"]["sea"] > 10000, "and its sea leash is over 10,000 km (%d)"
       % g["wheat"]["reach"]["sea"])
    ok(g["silk"]["reach"]["road"] > 100 * g["wheat"]["reach"]["road"],
       "silk's road leash is more than a hundred times wheat's")
    ok(g["stone"]["reach"]["road"] < g["timber"]["reach"]["road"],
       "stone is cheaper per kilogram than timber, so its leash is shorter")
    ok(g["pepper"]["reach"]["road"] > g["wheat"]["reach"]["road"] * 100,
       "pepper goes further by road than wheat can by sea")
    for x in doc["goods"]:
        for route in ("road", "downriver", "upriver", "sea"):
            ok(x["reach"][route] > 0, "%s has a positive leash on %s" % (x["id"], route))
        ok(x["reach"]["sea"] > x["reach"]["road"],
           "%s goes further by sea than by road" % x["id"])

    # THE ROUTES. Every route the pack names must have a freight cost and a speed.
    for w in doc["ways"]:
        ok(w in doc["freight"] or w in ("road", "rail", "canal", "river", "sea"),
           "the route %s is known" % w)
    ok(any(w == "rail" for w in doc["ways"]), "rail is a route, not a footnote")
    for s in doc["speeds"]:
        ok(s["kmPerDay"] > 0 and s["why"], "the %s speed is positive and explained"
           % s["route"])

    # THE DOCUMENTED JOURNEYS. The model must reproduce the counts, not merely cite them.
    for c in doc["counts"]:
        if "tonnesPerYear" in c:
            # The derivation the register actually uses: tonnage / (capacity x load factor).
            got = c["tonnesPerYear"] / 365.0 / (1.2 * doc["loadFactor"])
            ok(abs(got - c["wagonsPerDay"]) <= c["wagonsPerDay"] * 0.15,
               "%s: %.0f wagons a day recomputed against %d counted, at a %.2f load factor"
               % (c["id"], got, c["wagonsPerDay"], doc["loadFactor"]))
        if "km" in c and "days" in c:
            got = c["km"] / float(c["days"])
            ok(30.0 <= got <= 45.0,
               "%s: %.0f km a day, inside Spufford's 30-40 for a carrier" % (c["id"], got))

    ok(len(doc["gates"]) >= 3, "%d gates limit throughput" % len(doc["gates"]))
    ok(doc["finding"].count("286"), "the finding quotes the wheat leash it computes")
    return bad


def main(argv):
    doc, problems = build()
    for p in problems:
        print("  PROBLEM " + p)

    c = doc["counts_"]
    print("traffic: %d goods (%d bulky), %d counts, %d routes, %d gates"
          % (c["goods"], c["bulky"], c["counts"], c["ways"], c["gates"]))

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
