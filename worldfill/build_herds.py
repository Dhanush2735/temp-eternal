#!/usr/bin/env python3
"""
Step 46 part 7 (D14, the second half): pack the herds and the droves.

    python3 build_herds.py            build, then write
    python3 build_herds.py --check    check only, write nothing
"""

import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data",
                   "eternalengine", "eternal", "economy", "herds.json.gz")

sys.path.insert(0, HERE)
try:
    import herd_table as H
finally:
    sys.path.pop(0)


def build():
    problems = list(H.problems())
    herds = []
    for h in H.HERDS:
        herds.append({
            "id": h["id"],
            "animal": h["animal"],
            "area": h["area"],
            "year": h["year"],
            "sizeLow": h["size"][0],
            "sizeHigh": h["size"][1],
            "yields": h["yields"],
            "mark": h["mark"],
            "note": h["note"],
            "source": h["source"],
        })
    droves = []
    for d in H.DROVES:
        droves.append({
            "id": d["id"],
            "name": d["name"],
            "area": d["area"],
            "lat": d["lat"],
            "lon": d["lon"],
            "start": d["start"],
            "end": d["end"],
            "widthM": d["width"],
            "lengthKm": d["lengthKm"],
            "headPerYear": d["head"],
            "kmPerDay": d["kmPerDay"],
            "shape": d["shape"],
            "mark": d["mark"],
            "note": d["note"],
            "source": d["source"],
        })
    doc = {
        "format": "eternal-herds-1",
        "id": "herds",
        "source": ("Herds: Zeder on sheep and goat domestication in the Zagros; Helmer on Levantine "
                   "cattle; Chen on indicine cattle genomics; Larson on East Asian pigs; Peters et "
                   "al., PNAS 2022, on chickens; Outram and Librado on horses; Wiener on yak; FAO "
                   "on camelids; Wheeler on Andean camelids; Hornaday 1889 on bison. Droves: "
                   "Wikipedia's Mesta article citing Klein; the Handbook of Texas on the Chisholm "
                   "and Western trails with the US Bureau of Statistics figures; Haldane on the "
                   "Scottish drove roads; Deloche on Indian transport; Forbes on Yamal; UNESCO on "
                   "Alpine transhumance."),
        "note": ("Step 46 part 7, the second half of D14 and the half part 2 explicitly deferred. "
                 "Part 2 built the register of WORKING animals and said so: 'Herd animals are out "
                 "of scope.' This is that register. It answers what is kept in a herd, where and "
                 "from when; how many to a herd, because the herd size is what makes a road "
                 "necessary; and what a herd yields that one beast does not. THE FINDING REORDERS "
                 "THE SUBJECT: **the herd is the missing reason for the road.** Part 5 found that "
                 "a road is almost never a right of way and never found why the road is there. A "
                 "Roman road is 4 to 6 m wide, which is two carts. A Spanish canada real is 75 m "
                 "wide, and it is 75 m wide because sheep spread out while they graze and a flock "
                 "must walk and eat at the same time. The largest road-building institution in "
                 "early modern Europe was a shepherds' guild, and the traffic it moved was 2.5 "
                 "million animals a year on foot. A drove road is therefore the one road built for "
                 "animals rather than vehicles: part 3's foot medium, part 5's forced shape, and "
                 "part 2's beasts walking rather than pulling."),
        "finding": ("**A road you can eat is a different object from a road you can drive on.** "
                    "The width of a route is set by what has to fit on it, and a grazing flock "
                    "needs an order of magnitude more width than a cart. This is why the cañada is "
                    "75 m and the Via Appia is 4 m, and it is why the same century that produced "
                    "the best road engineers in Europe also produced a pastoral law that let sheep "
                    "cross a farmer's field."),
        "herds": herds,
        "droves": droves,
        "refusals": [{"claim": c, "answer": a} for c, a in H.REFUSALS],
        "counts": {
            "herds": len(herds),
            "droves": len(droves),
            "animals": len({h["animal"] for h in herds}),
            "areas": len({h["area"] for h in herds}),
            "recorded": sum(1 for h in herds if h["mark"] == "recorded"),
            "estimated": sum(1 for h in herds if h["mark"] == "estimated"),
            "widestDroveM": max(d["widthM"] for d in droves),
            "longestDroveKm": max(d["lengthKm"] for d in droves),
        },
    }
    return doc, problems


def check(doc):
    bad = []

    def ok(cond, what):
        print(("  ok   " if cond else "  FAIL ") + what)
        if not cond:
            bad.append(what)

    ok(doc["format"] == "eternal-herds-1", "the format is the one this builder writes")
    c = doc["counts"]
    ok(c["herds"] >= 24, "%d herd rows" % c["herds"])
    ok(c["droves"] >= 10, "%d droves" % c["droves"])
    ok(c["animals"] >= 10, "%d animals" % c["animals"])
    ok(c["areas"] >= 10, "over %d areas" % c["areas"])
    ok(c["estimated"] > 0, "%d rows are estimated rather than recorded" % c["estimated"])

    # THE FINDING, checked rather than asserted in prose.
    ok(c["widestDroveM"] >= 50,
       "the widest drove is %d m, against the 4 to 6 m of a vehicle road" % c["widestDroveM"])

    # No projection past the recorded horizon without a mark.
    ok(all(h["mark"] in ("recorded", "estimated", "projected") for h in doc["herds"]),
       "every herd row carries a mark")

    # The Mesta myth, refused in data as well as in prose.
    mesta = [h for h in doc["herds"] if h["id"] == "sheep_castile"]
    ok(mesta and "fewer than 100" in mesta[0]["note"],
       "the Castilian row refuses the giant-flock myth in the row itself")

    # The chicken, on the new date.
    ch = [h for h in doc["herds"] if h["id"] == "chicken_thailand"]
    ok(ch and ch[0]["year"] == -1650, "the chicken is dated 1650 BC, not 8000 BC")
    ok(ch and "Ban Non Wat" in ch[0]["note"], "and names the site")

    # The bison ends.
    bi = [h for h in doc["herds"] if h["id"] == "bison_plains"]
    ok(bi and bi[0]["animal"] == "bison", "the bison is carried as a wild herd")
    ok(bi and "1889" in bi[0]["note"], "and ends in 1889, in its own words")

    # The droves that ended, ended.
    ch = [d for d in doc["droves"] if d["id"] == "chisholm"]
    ok(ch and ch[0]["end"] == 1884, "the Chisholm Trail ends in 1884")
    ok(ch and "barbed wire" in ch[0]["note"], "and says what closed it")
    ca = [d for d in doc["droves"] if d["id"] == "canada_real"]
    ok(ca and ca[0]["widthM"] == 75.0, "the canada real is 75 m wide")
    ok(ca and ca[0]["end"] == 1836, "and is abolished in 1836")

    # Every drove that names a law shape names one part 5 has.
    shapes = {"closed", "toll", "forced", "gauge", "side", "speed", "hours", "labour", "ban"}
    for d in doc["droves"]:
        if d["shape"] is not None:
            ok(d["shape"] in shapes, "%s borrows part 5's %s shape" % (d["id"], d["shape"]))

    # Every row says something and cites something.
    for h in doc["herds"]:
        ok(len(h["note"]) > 60, h["id"] + " explains itself")
    ok(len(doc["refusals"]) >= 4, "%d claims are refused" % len(doc["refusals"]))
    ok("eat" in doc["finding"], "the finding is the one-line version: a road you can eat")
    return bad


def main(argv):
    doc, problems = build()
    for p in problems:
        print("  PROBLEM " + p)
    c = doc["counts"]
    print("herds: %d rows over %d animals and %d areas (%d recorded, %d estimated); %d droves, "
          "widest %d m, longest %d km"
          % (c["herds"], c["animals"], c["areas"], c["recorded"], c["estimated"], c["droves"],
             c["widestDroveM"], c["longestDroveKm"]))
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
