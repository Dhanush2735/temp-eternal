#!/usr/bin/env python3
"""
Step 47 part 2 (E7): pack the tools.

    python3 build_tools.py            build, then write
    python3 build_tools.py --check    check only, write nothing
"""

import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data",
                   "eternalengine", "eternal", "economy", "tools.json.gz")

sys.path.insert(0, HERE)
try:
    import tool_table as T
finally:
    sys.path.pop(0)


def build():
    problems = list(T.problems())
    A = T.atlas()
    tools = []
    for t in T.TOOLS:
        if "from_atlas" in t:
            src = A[t["from_atlas"]]
            made = dict(src["made"])
            origin = "atlas:" + t["from_atlas"]
        else:
            made = dict(t["made"])
            origin = "written"
        tools.append({
            "id": t["id"],
            "name": t["name"],
            "family": t["family"],
            "made": made,
            "replaces": t["replaces"],
            "vanilla": t["vanilla"],
            "beforeWorld": bool(t.get("before_world")),
            "origin": origin,
            "note": t["note"],
            "source": t["source"],
        })
    doc = {
        "format": "eternal-tools-1",
        "id": "tools",
        "source": ("21 of the 27 rows read their dates from step 44's products atlas by id; the 6 "
                   "written here cite Wikipedia (warp-weighted loom, loom, treadle loom, movable "
                   "type, Zacharias Janssen, sundial), Britannica (history of printing, the "
                   "mouldboard plough), Barber's Prehistoric Textiles, the Smith College Museum of "
                   "Ancient Inventions, EXARC's reconstruction of the horizontal treadle loom, "
                   "Hoffmann on the 11th-century shift to the treadle, and Needham's Science and "
                   "Civilisation in China."),
        "note": ("Step 47 part 2 (E7): tools and inventions as ITEMS. The products atlas is a "
                 "register of what a place makes and sells; this is a register of the thing in a "
                 "person's hands, what it does, what it REPLACED, and what in Minecraft stands for "
                 "it. THE RULE THIS REGISTER EXISTS TO ENFORCE: **a tool's date is not its "
                 "material's date.** Step 44 derives a product from its parent, and for tools the "
                 "parent is a material, so a microscope whose parent is glass became as old as "
                 "glass: 2500 BC in West Asia. Step 46 found the same fault in reindeer and in "
                 "donkeys. Three instances make it a class of error, so every row here is either "
                 "read from the atlas by id or written by hand with a source, and never derived "
                 "from a material."),
        "finding": ("**Two of the seven things the plan names had no row at all.** The atlas has "
                    "`woodblock_prints`, which is the print and not the press, and it has no "
                    "`loom` of any kind: no warp-weighted loom, no treadle loom, nothing that turns "
                    "fibre into cloth. Those are the register's two main additions. And the "
                    "treadle loom is the sharper of them, because it is not only a machine: it is "
                    "expensive, so it moved weaving out of the household and into guilds, and the "
                    "guilds excluded women. **A tool can reorganise who is allowed to work.**"),
        "tools": tools,
        "counts": {
            "tools": len(tools),
            "families": len({t["family"] for t in tools}),
            "fromAtlas": sum(1 for t in tools if t["origin"].startswith("atlas:")),
            "written": sum(1 for t in tools if t["origin"] == "written"),
            "noVanilla": sum(1 for t in tools if t["vanilla"].endswith("_placeholder")),
            "beforeWorld": sum(1 for t in tools if t["beforeWorld"]),
        },
    }
    return doc, problems


def check(doc):
    bad = []

    def ok(cond, what):
        print(("  ok   " if cond else "  FAIL ") + what)
        if not cond:
            bad.append(what)

    ok(doc["format"] == "eternal-tools-1", "the format is the one this builder writes")
    c = doc["counts"]
    ok(c["tools"] >= 25, "%d tools" % c["tools"])
    ok(c["families"] >= 8, "over %d families of work" % c["families"])
    ok(c["fromAtlas"] >= 18, "%d dates read from the products atlas" % c["fromAtlas"])

    # THE TWO THINGS THE ATLAS DID NOT HAVE.
    ids = {t["id"] for t in doc["tools"]}
    ok("loom_warp_weighted" in ids, "the warp-weighted loom is here, and the atlas has no loom")
    ok("loom_treadle" in ids, "and the treadle loom, which is the one that changed who weaves")
    ok("printing_movable" in ids,
       "and movable type, which the atlas had only as woodblock prints")

    # THE BUG, CHECKED IN THE PACK AND NOT ONLY IN THE TABLE.
    mic = next(t for t in doc["tools"] if t["id"] == "microscope")
    ok(min(mic["made"].values()) >= 1500,
       "the microscope is no longer dated to the age of glass (earliest %d)" % min(mic["made"].values()))
    ok("2500 BC" in mic["note"], "and the row records the bug it corrects")

    # THE DIRECTION OF SPREAD, EVERY TIME.
    for tool, east, west in (("printing_movable", "EAS", "EUR"), ("loom_treadle", "EAS", "EUR")):
        t = next(x for x in doc["tools"] if x["id"] == tool)
        ok(t["made"][east] < t["made"][west],
           "%s reaches China (%d) before Europe (%d)" % (tool, t["made"][east], t["made"][west]))

    # EVERY TOOL RESOLVES OR SAYS IT CANNOT: A13's rule, applied to an inventory.
    for t in doc["tools"]:
        ok(bool(t["vanilla"]), t["id"] + " names a vanilla item or a placeholder")
        if t["vanilla"].endswith("_placeholder"):
            ok("vanilla" in t["note"].lower(),
               t["id"] + " has no vanilla item and says so in its own note")

    # A TOOL WITH NO PREDECESSOR IS RARE, AND THE PACK SAYS WHICH.
    no_pred = [t["id"] for t in doc["tools"] if t["replaces"] is None]
    ok(len(no_pred) <= 6, "%d tools claim no predecessor: %s" % (len(no_pred), ", ".join(no_pred)))

    # The tractor is the row that ends step 46's working animals, and it must say so.
    tr = next(t for t in doc["tools"] if t["id"] == "tractor")
    ok("horse" in tr["replaces"].lower(), "the tractor names the animal it removed")
    ok("working animals" in tr["note"], "and points at step 46")

    ok("guild" in doc["finding"], "the finding names the guild")
    return bad


def main(argv):
    doc, problems = build()
    for p in problems:
        print("  PROBLEM " + p)
    c = doc["counts"]
    print("tools: %d over %d families; %d read from the atlas, %d written here; %d with no "
          "vanilla item, %d older than the world"
          % (c["tools"], c["families"], c["fromAtlas"], c["written"], c["noVanilla"],
             c["beforeWorld"]))
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
