#!/usr/bin/env python3
"""
Step 46 part 6 (A13, the vehicle half): pack the resolver — which mod supplies which vehicle, and
what stands in when nothing is installed.

    python3 build_vehicle_mods.py            build, then write
    python3 build_vehicle_mods.py --check    check only, write nothing

**A13's line in the plan is "optional links; everything also works without them."** That is the
whole specification, and it imposes two duties:

1. **Never hand back nothing.** Every vehicle in part 3's register must resolve to a mod, to a
   vanilla stand-in, or to an explicit statement of why there is neither.
2. **Never pretend a stand-in is the real thing.** A boat is not a ship. A minecart is not a cart.

The third duty is the one this project keeps learning: **never invent an id.** So every provider is
marked `read` (the id came from the mod's own source), `content` (the ids come from JSON content
packs, so no id is safe and the rows are placeholders by design) or `vanilla`.
"""

import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data",
                   "eternalengine", "eternal", "economy", "vehicle_mods.json.gz")

SYS_PATH = sys.path[:]
sys.path.insert(0, HERE)
try:
    import vehicle_mod_table as T
    import vehicle_table as V
finally:
    sys.path = SYS_PATH


def build():
    ids = [v["id"] for v in V.VEHICLES]
    problems = list(T.problems(ids))

    vehicles = []
    for v in V.VEHICLES:
        chain = T.may_supply(v["id"])
        vehicles.append({
            "id": v["id"],
            "name": v["name"],
            "medium": v["medium"],
            "suppliedBy": [{"provider": p, "id": i, "mark": m} for p, i, m in chain],
            "nothing": T.NONE.get(v["id"]),
        })

    doc = {
        "format": "eternal-vehicle-mods-1",
        "id": "vehicle_mods",
        "source": ("Mod ids read from each mod's own source or documentation: AstikorCarts "
                   "Redux's EntityTypes and Items DeferredRegisters (github.com/issork/"
                   "astikor-carts), Small Ships' Modrinth and CurseForge pages and its "
                   "dockyard_recipes datapack path, Immersive Vehicles' content-pack documentation, "
                   "and Minecraft 1.20.1's own registry. No id here was guessed."),
        "note": ("A13, the vehicle half: which mod supplies which vehicle of step 46 part 3's "
                 "register, and what stands in when no mod is installed. A13's own line is "
                 "'optional links; everything also works without them', which imposes two duties: "
                 "NEVER hand back nothing, and NEVER pretend a stand-in is the real thing. A boat "
                 "is not a ship and a minecart is not a cart, and the pack says so. THE THIRD "
                 "DUTY IS THE ONE THIS PROJECT KEEPS LEARNING: never invent an id - so every "
                 "provider is marked `read` (from the mod's own source), `content` (the ids come "
                 "from JSON content packs, so no id is safe and the rows are placeholders meant to "
                 "be corrected by config) or `vanilla`."),
        "finding": ("**Two of the mods ship a config list that is exactly a question this step "
                    "already answers.** AstikorCarts Redux has `pull_animals` - which entities may "
                    "draw a cart; Small Ships has `dockyardBuildableShips` - which ships the "
                    "Dockyard will build. Both are static lists written by a pack author, and both "
                    "are the same question as part 2 (has this beast arrived here) and part 5 (may "
                    "this route be used here). So this step does not edit either config: it tells "
                    "the player what the list should hold for this place and year, through the "
                    "public surface the mod already exposes. Change the other mod through its own "
                    "hooks, never by patching its jar."),
        "providers": [{
            "id": p["id"],
            "name": p["name"],
            "modid": p["modid"],
            "licence": p["licence"],
            "mark": p["mark"],
            "gate": p["gate"],
            "entities": p["entities"],
            "items": p["items"],
            "kinds": p.get("kinds", {}),
            "parts": p.get("parts", {}),
            "config": p["config"],
            "note": p["note"].replace("**", ""),
            "source": p["source"],
        } for p in T.PROVIDERS],
        "vehicles": vehicles,
        "counts": {
            "providers": len(T.PROVIDERS),
            "vehicles": len(vehicles),
            "withMod": sum(1 for v in vehicles
                           if any(s["mark"] in ("read", "content") for s in v["suppliedBy"])),
            "vanillaOnly": sum(1 for v in vehicles
                               if v["suppliedBy"] and all(s["mark"] == "vanilla"
                                                          for s in v["suppliedBy"])),
            "nothing": sum(1 for v in vehicles if v["nothing"] and not v["suppliedBy"]),
            "read": sum(1 for p in T.PROVIDERS if p["mark"] == "read"),
            "content": sum(1 for p in T.PROVIDERS if p["mark"] == "content"),
        },
    }
    return doc, problems


def check(doc):
    bad = []

    def ok(cond, what):
        print(("  ok   " if cond else "  FAIL ") + what)
        if not cond:
            bad.append(what)

    ok(doc["format"] == "eternal-vehicle-mods-1", "the format is the one this builder writes")
    for key in ("providers", "vehicles", "finding", "counts"):
        ok(key in doc, "the pack carries %s" % key)

    c = doc["counts"]
    ok(c["vehicles"] == 32, "%d vehicles, the whole of part 3's register" % c["vehicles"])
    ok(c["read"] >= 2, "%d providers have ids read from source" % c["read"])

    # THE THREE DUTIES.
    unaccounted = [v["id"] for v in doc["vehicles"] if not v["suppliedBy"] and not v["nothing"]]
    ok(not unaccounted, "every vehicle resolves or says why it cannot"
                        + (": " + ", ".join(unaccounted) if unaccounted else ""))
    ok(c["nothing"] >= 8, "%d vehicles have no provider and say why" % c["nothing"])

    # Never invent an id: a content-pack provider names no ids at all.
    for p in doc["providers"]:
        if p["mark"] == "content":
            ok(not p["entities"] and not p["items"],
               "%s names no ids, because its ids come from content packs" % p["id"])
            ok(bool(p["kinds"]), "%s claims vehicle KINDS instead, which is honest" % p["id"])

    # Every id that IS named must be namespaced and in the provider's own namespace.
    for p in doc["providers"]:
        for k, ident in p["entities"].items():
            ok(ident.count(":") == 1, "%s: %s is a namespaced id" % (p["id"], ident))
            ns = ident.split(":")[0]
            ok(ns == p["modid"] or p["mark"] == "vanilla",
               "%s: %s is in its own namespace" % (p["id"], ident))

    # THE MOD JOIN. The Small Ships Dockyard is the front door, and it is refused by part 3.
    ss = [p for p in doc["providers"] if p["id"] == "smallships"]
    ok(ss and ss[0]["gate"] == "dockyard",
       "Small Ships is gated at the DOCKYARD, because it has no crafting recipes at all")
    ak = [p for p in doc["providers"] if p["id"] == "astikorcarts"]
    ok(ak and "pull_animals" in ak[0]["config"],
       "AstikorCarts' pull_animals config is named, because it is part 2's question")
    ok(ak and ak[0]["licence"] == "MIT", "and it is the MIT one")

    # The vanilla fallback must be honest about what it does not cover.
    van = [p for p in doc["providers"] if p["id"] == "vanilla"]
    ok(van and "no ox" in van[0]["note"], "the vanilla row admits it has no ox")
    ok(van and "elephant" in van[0]["note"], "and no elephant")

    # A part is not a vehicle.
    ok(ak and "plough" in ak[0]["parts"], "the plough is recorded as an implement, not a vehicle")
    ok(all(v["id"] != "plough" for v in doc["vehicles"]),
       "and it is not smuggled into the vehicle list")

    ok(doc["finding"].count("pull_animals"), "the finding names the config it uses as a hook")
    return bad


def main(argv):
    doc, problems = build()
    for p in problems:
        print("  PROBLEM " + p)

    c = doc["counts"]
    print("vehicle mods: %d providers (%d read, %d content-pack), %d vehicles: %d by a mod, "
          "%d by vanilla only, %d with nothing"
          % (c["providers"], c["read"], c["content"], c["vehicles"], c["withMod"],
             c["vanillaOnly"], c["nothing"]))

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
