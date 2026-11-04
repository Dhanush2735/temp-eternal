#!/usr/bin/env python3
"""
Step 46 part 2 (D14): pack the working animals — what carried the world's goods.

    python3 build_animals.py            build, then write
    python3 build_animals.py --check    check only, write nothing

The register lives in `animal_table.py`. This script only checks it and writes it out; it decides
nothing.

**What this fixes.** `trade/LogisticsManager` spawns **two to four donkeys for every caravan, in
every era, on every continent** — three donkeys at Cusco in 1500, when the Andes had llamas for
four thousand years, and three donkeys in Australia in 1700, eighty-eight years before donkeys
arrived. This pack is the lookup that replaces that: *which animal carries, here, in this year?*

**It reads, it does not rewrite.** The products atlas already dates the animals in all 17 areas, so
the years come from there. This register adds what the products atlas does not carry: what each
animal **does**, **how much and how far**, and **where it never was**.

**Two corrections to the products atlas are recorded, not hidden:**
- `reindeer` is dated −2000 in West Africa by the products atlas, which is impossible; six `never`
  entries remove them.
- `donkeys` and `horses` share a date in every area, which cannot be right — the donkey is African
  and the horse is a steppe animal. In Africa the donkey is moved earlier.

**The tsetse belt cannot be drawn at 17 areas.** West Africa holds both the Sahel, where camels and
cattle work, and the forest, where no beast survives and everything is carried on heads. The pack
says so per area rather than picking one and lying about the other.

Run from the repository root:  python3 worldfill/build_animals.py
"""

import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data",
                   "eternalengine", "eternal", "economy", "animals.json.gz")

SYS_PATH = sys.path[:]
sys.path.insert(0, HERE)
try:
    import animal_table as T
finally:
    sys.path = SYS_PATH

# Where one area holds two different transport worlds and the register refuses to choose between
# them. This is the same honesty step 44's diet had to show: 17 areas cannot separate the Sahel
# from the forest, and picking one would be a lie about the other.
MIXED = {
    "WAF": "the Sahel, where camels, cattle and donkeys work, and the forest belt, where the "
           "tsetse fly kills them and everything is carried on human heads",
    "MSA": "the savannah, which has cattle, and the Congo forest, which has none",
    "EAF": "the highlands and the coast, which have donkeys and camels, and the fly belt between",
}
TSETSE_NOTE = (
    "Alsan (2014) measures it: a one-standard-deviation rise in tsetse suitability goes with a "
    "**23-point fall in the chance a people had large domestic animals** and a **6-point fall in "
    "plough use**. The belt is why the plough never reached the forest and why the East African "
    "caravans ran on tens of thousands of professional porters (Rockel, *Carriers of Culture*, "
    "2006) rather than on beasts."
)


def build():
    problems = list(T.problems())
    animals = []
    for a in T.ANIMALS:
        years = T.resolve_years(a)
        animals.append({
            "id": a["id"],
            "name": a["name"],
            "kind": a["kind"],
            "roles": a["roles"],
            "loadKg": a["loadKg"],
            "kmPerDay": a["kmPerDay"],
            "mark": a["mark"],
            "years": years,
            "never": {k: v.replace("**", "") for k, v in a["never"].items()},
            "supersedes": a["supersedes"],
            "vanilla": a["vanilla"],
            "note": a["note"].replace("**", ""),
            "source": a["source"],
            "areas": len(years),
        })
    doc = {
        "format": "eternal-animals-1",
        "id": "animals",
        "source": ("Years from the mod's own products atlas (step 44 part C). Loads and daily "
                   "distances from the FAO working-capacity tables, Britannica, the Logistics "
                   "Cluster pack-animal table, Murra's ethnohistoric llama caravans (1965), the "
                   "pre-colonial Kano trade study (Yusuf Umar Madugu), and Rockel's *Carriers of "
                   "Culture* (2006). The tsetse effect is Alsan 2014."),
        "note": ("What carried the world's goods and drew its ploughs. THE BUG IT FIXES: "
                 "`trade/LogisticsManager` spawned two to four DONKEYS for every caravan in every "
                 "era on every continent - three donkeys at Cusco in 1500, when the Andes had "
                 "llamas for four thousand years, and three donkeys in Australia in 1700, "
                 "eighty-eight years before donkeys arrived. This is the lookup that replaces it: "
                 "*which animal carries, here, in this year?* The years are READ from the products "
                 "atlas, not rewritten; what this register adds is what each animal DOES, how much "
                 "and how far, and where it never was."),
        "corrections": [
            "**reindeer are dated -2000 in West Africa by the products atlas**, which is "
            "impossible; that is a step-44 part-C artefact where a child inherited its parent's "
            "date. Six `never` entries remove them from West, Middle and East Africa, Australia, "
            "Oceania and South-East Asia.",
            "**donkeys and horses share a date in every area**, which cannot be right: the donkey "
            "was domesticated from the African wild ass and the horse is a steppe animal that "
            "reached Africa later. The products atlas has them identical because part C derived "
            "both from the same parent. In Africa the donkey is moved earlier, marked estimated.",
            "**the tsetse belt cannot be drawn at 17 areas.** West Africa is both the Sahel, where "
            "camels work, and the forest, where nothing with four legs survives. Three areas are "
            "marked `mixed` and the register says so instead of choosing.",
        ],
        "tsetse": TSETSE_NOTE.replace("**", ""),
        "mixed": MIXED,
        "counts": {
            "animals": len(animals),
            "beasts": sum(1 for a in animals if a["kind"] == "beast"),
            "recorded": sum(1 for a in animals if a["mark"] == "recorded"),
            "estimated": sum(1 for a in animals if a["mark"] == "estimated"),
            "mixedAreas": len(MIXED),
        },
        "animals": animals,
    }
    return doc, problems


def check(doc):
    bad = []

    def ok(cond, what):
        print(("  ok   " if cond else "  FAIL ") + what)
        if not cond:
            bad.append(what)

    ok(doc["format"] == "eternal-animals-1", "the format is the one this builder writes")
    for key in ("animals", "mixed", "tsetse", "corrections", "counts"):
        ok(key in doc, "the pack carries %s" % key)

    animals = doc["animals"]
    ok(len(animals) >= 8, "%d animals" % len(animals))

    # The bug this pack exists to fix, asserted from the data itself.
    llama = next((a for a in animals if a["id"] == "llama"), None)
    camel = next((a for a in animals if a["id"] == "camel"), None)
    donkey = next((a for a in animals if a["id"] == "donkey"), None)
    porter = next((a for a in animals if a["id"] == "porter"), None)
    ok(porter is not None, "there is a porter")
    ok(llama is not None and llama["years"].get("SAM") == -4000,
       "llamas reach South America in 4000 BC, 4,500 years before the donkey")
    ok(camel is not None and "WAF" in camel["years"] and camel["years"]["WAF"] <= 500,
       "camels reach West Africa by AD 500")
    ok(donkey is not None and donkey["years"].get("SAM") == 1530,
       "donkeys reach South America only in 1530 - the date the hardcoded caravan ignores")
    ok(donkey is not None and "AUS" in donkey["years"] and donkey["years"]["AUS"] == 1788,
       "donkeys reach Australia only in 1788")
    ok(porter is not None and len(porter["years"]) == 17,
       "the porter reaches all 17 areas, so the tsetse belt is never empty")

    # No animal may reach an area it is excluded from. This is the reindeer correction.
    strays = []
    for a in animals:
        for area in a["never"]:
            if area in a["years"]:
                strays.append(a["id"] + " in " + area)
    ok(not strays, "no animal reaches an area it is excluded from" + (": " + ", ".join(strays)
                                                                      if strays else ""))
    rein = next((a for a in animals if a["id"] == "reindeer"), None)
    ok(rein is not None and "WAF" not in rein["years"],
       "reindeer are gone from West Africa, where the products atlas wrongly dated them -2000")

    # The donkey must be earlier than the horse in Africa, which is the other correction.
    horse = next((a for a in animals if a["id"] == "horse"), None)
    if donkey and horse:
        earlier = [a for a in ("WAF", "NAF", "EAF", "MSA")
                   if a in donkey["years"] and a in horse["years"]
                   and donkey["years"][a] < horse["years"][a]]
        ok(len(earlier) >= 3, "the donkey predates the horse in %d African areas" % len(earlier))

    # Every animal must reach somewhere, and do something, and say where it came from.
    ok(all(a["years"] for a in animals), "every animal reaches at least one area")
    ok(all(a["roles"] for a in animals), "every animal does something")
    ok(all(a["loadKg"] > 0 and a["kmPerDay"] > 0 for a in animals),
       "every animal carries something somewhere")
    ok(all(a["note"] and a["source"] for a in animals), "every animal is sourced")
    ok(all(a["mark"] in ("recorded", "estimated") for a in animals),
       "every animal is marked recorded or estimated")

    # Areas must be real.
    ok(all(ar in T.AREAS for a in animals for ar in a["years"]),
       "every year-area is one of the atlas's 17")
    ok(all(ar in T.AREAS for a in animals for ar in a["never"]),
       "every never-area is one of the atlas's 17")
    ok(all(ar in T.AREAS for ar in doc["mixed"]), "every mixed area is one of the atlas's 17")

    return bad


def main(argv):
    doc, problems = build()
    for p in problems:
        print("  PROBLEM " + p)

    c = doc["counts"]
    print("working animals: %d entries (%d beasts, %d recorded, %d estimated), %d mixed areas"
          % (c["animals"], c["beasts"], c["recorded"], c["estimated"], c["mixedAreas"]))

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
