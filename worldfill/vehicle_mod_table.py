"""
Step 46 part 6 (A13, the vehicle half): which mod supplies which vehicle, and what stands in when
no mod is installed.

**A13's own line in the plan is: "optional links; everything also works without them."** That is
the whole specification, and it is a hard one — it means the mod must never hand back nothing, and
must never pretend a stand-in is the real thing.

## The rule this table holds to

**An id is only written here if it was READ, not guessed.** Three times in this project an invented
name has passed a check and been wrong in the world: step 45's unit ladder named a polity called
"Sparta" that the register does not have, step 44 invented two area codes, and step 46 part 2's
singular animal ids resolved to nothing. So every provider here is marked:

| mark | meaning |
|---|---|
| `read` | the registry id was taken from the mod's own source or documentation |
| `content` | the ids come from content packs at runtime, so NO id is safe — these are placeholders meant to be corrected by config |
| `vanilla` | no mod; a Minecraft entity that already exists |

The `content` rows are the honest ones. **Immersive Vehicles' ids are defined in JSON content
packs**, so there is no id in the mod's jar to name; a hard-coded `mts:car` would be an invention.

## What the mod actually does with its own config

Two of these mods ship a list that is *exactly* a question this step already answers:

- **AstikorCarts Redux** has a **`pull_animals`** config list — which entities may pull a cart.
- **Small Ships** has a **`dockyardBuildableShips`** config list — which ships the Dockyard offers.

Both are static lists written by a pack author. **Both are the same question as step 46 part 2**
(has this beast arrived here yet) and **part 5** (may this route be used here yet). So this step
does not edit those configs — it *tells* the player what they should hold for this place and year,
through the same public surface the mod already exposes. That is the standing rule for every mod
this project touches: **change the other mod through its own hooks, never by patching its jar.**
"""

# The mods, as read. 1.20.1 + Forge unless stated.
PROVIDERS = [
    dict(id="astikorcarts",
         name="AstikorCarts Redux",
         modid="astikorcarts",
         licence="MIT",
         mark="read",
         gate="craft",
         entities={"cart": "astikorcarts:supply_cart",
                   "wagon": "astikorcarts:animal_cart",
                   # A spawned entity, and still not a vehicle: an implement.
                   "plough": "astikorcarts:plow"},
         items={"wheel": "astikorcarts:wheel",
                "cart": "astikorcarts:supply_cart",
                "wagon": "astikorcarts:animal_cart",
                "plough": "astikorcarts:plow"},
         # Not vehicles: a plough is an IMPLEMENT (step 46 part 2 gives the ox the plough role) and
         # a wheel is a PART. Part 3's register is right not to carry them, so the check must not
         # demand that it does.
         parts={"wheel": "a part: the item you need before you can build any cart",
                "plough": "an implement: it tills, strips logs and makes paths, and step 46 part 2 "
                          "gives the plough to the ox and the water buffalo, not to a vehicle"},
         config={"pull_animals": "the list of entities that may draw a cart"},
         note="**The only vehicle mod here with a licence this project can rely on and ids read "
              "from its own source.** Four registry entries: `supply_cart` (a chest on wheels), "
              "`animal_cart` (a boat on wheels, for carrying animals) and `plow` (tills, strips "
              "logs, makes paths), plus a `wheel` item. Its config carries a **`pull_animals`** "
              "list, which is exactly step 46 part 2's question — so this step reports what that "
              "list should hold for a place and year rather than editing it.",
         source="github.com/issork/astikor-carts, AstikorCarts.java (EntityTypes and Items "
                "DeferredRegisters); CurseForge 916493; Modrinth astikorcarts-redux"),
    dict(id="smallships",
         name="Small Ships",
         modid="smallships",
         licence="All Rights Reserved",
         mark="read",
         gate="dockyard",
         entities={"sailing_ship": "smallships:cog"},
         items={},
         config={"dockyardBuildableShips": "which ships the Dockyard will build"},
         note="**Ships can only be built at a Dockyard; there are no crafting recipes at all**, "
              "so a year gate cannot empty a result slot for a ship — it has to refuse the "
              "Dockyard, which is the same shape as step 45's gun-bench refusal and reuses it. "
              "Datapack recipes live at `data/<namespace>/dockyard_recipes/<ship>.json`, so an "
              "addon adds ships at runtime and the ship list is a config, not a constant. **2.0.0 "
              "adds a Dhow and a Caravel**, two of the vehicles step 46 part 3 dates — which is "
              "the join worth having: the Dockyard opens for a dhow where the dhow reached, and "
              "not before.",
         source="modrinth.com/project/rGWEHQrP; CurseForge 450659; the Small Ships Addon page "
                "(smallships_addon:rowing_boat etc., added to dockyardBuildableShips)"),
    dict(id="immersivevehicles",
         name="Immersive Vehicles (MTS)",
         modid="mts",
         licence="All Rights Reserved",
         mark="content",
         gate="none",
         entities={},
         items={},
         kinds={"car": "a car of whatever content pack is installed",
                "bus": "a bus, if a pack adds one",
                "lorry": "a truck, if a pack adds one",
                "motorcycle": "a motorcycle, if a pack adds one",
                "electric_car": "any road car - the pack does not know what powers it",
                "aeroplane": "a fixed-wing aircraft from a pack",
                "helicopter": "a rotorcraft from a pack"},
         config={},
         note="**Cars, planes, helicopters, tanks and trucks, and every id comes from a JSON "
              "content pack.** There is no id in the mod's own jar to name, so this table carries "
              "none: a hard-coded `mts:car` would be exactly the invention this project has been "
              "caught by three times. The rows are placeholders by design and are meant to be "
              "corrected in config by whoever installs the packs.",
         source="modrinth Immersive Vehicles; TCOTS/MTS content-pack documentation"),
    dict(id="create",
         name="Create (with Steam 'n' Rails)",
         modid="create",
         licence="MIT (Create); addon licence separate",
         mark="content",
         gate="none",
         entities={},
         items={},
         kinds={"train": "a Create train, assembled by the player from blocks",
                "high_speed_train": "a Create train at speed - Create has no separate class",
                "tram": "a Create train on a street line"},
         config={},
         note="**Trains come from the Steam 'n' Rails addon, not from Create itself**, and a train "
              "in Create is assembled by the player out of blocks rather than spawned from an id. "
              "Create is already an optional dependency in `ModCompatibilityChecker`, so this is "
              "the one vehicle provider the mod already half-knew about.",
         source="ModCompatibilityChecker; Create: Steam 'n' Rails"),
    dict(id="vanilla",
         name="Minecraft itself",
         modid="minecraft",
         licence="Mojang EULA",
         mark="vanilla",
         gate="none",
         entities={"riding_horse": "minecraft:horse",
                   "donkey": "minecraft:donkey",
                   "mule": "minecraft:mule",
                   "llama": "minecraft:llama",
                   "camel": "minecraft:camel",
                   "riding_camel": "minecraft:camel",
                   "cart": "minecraft:minecart",
                   "wagon": "minecraft:minecart",
                   "raft": "minecraft:boat",
                   "canoe": "minecraft:boat",
                   "galley": "minecraft:boat",
                   "dhow": "minecraft:boat",
                   "sailing_ship": "minecraft:boat",
                   "steamship": "minecraft:boat",
                   "motor_ship": "minecraft:boat"},
         items={},
         config={},
         note="**What stands in when nothing is installed, and what it does not cover.** Vanilla "
              "has horse, donkey, mule, llama, camel, boat and minecart. It has **no ox, no "
              "elephant, no reindeer and no water buffalo** — the four working animals with no "
              "entity at all. A boat is not a ship and a minecart is not a cart, but both are at "
              "least the right shape, and saying so is better than handing back nothing.",
         source="Minecraft 1.20.1 entity registry"),
]


# Vehicles for which there is no provider and no stand-in, with the reason. This is the third
# legitimate answer and the most important one to write down: **a silence is worse than a null.**
# Step 46 part 2 already learned it with the porter, who is not a mob you can spawn beside a cart.
NONE = {
    "porter": "no entity and none needed - a person carries the load, and the caravan master and "
              "his guards ARE the porters; step 46 part 2's packEntityFor falls back to a donkey "
              "for the world's caravans because a spawned one needs legs",
    "litter": "no entity - two bearers and a chair; nothing in vanilla carries a passenger that "
              "way",
    "wheelbarrow": "no entity - AstikorCarts has a wheel ITEM and three carts, and no barrow",
    "sledge": "no entity - vanilla has no sled; a boat on ice is the nearest thing and it is not "
              "close",
    "elephant_howdah": "no entity - vanilla has no elephant, and part 3 already records that this "
                       "row stands in with a horse and says so",
    "chariot": "no entity - the chariot is a WEAPON KIND in step 45's armoury, not a spawned "
               "vehicle, and part 3 dates it from the technology atlas for that reason",
    "carriage": "no entity - AstikorCarts' animal_cart is a cart for animals, not a coach",
    "rickshaw": "no entity - a cart pulled by a person",
    "bicycle": "no entity, and this is the largest single gap: the bicycle is the vehicle that "
               "made a person faster than a horse on the same food",
    "junk": "no entity - Small Ships has a Cog, a Brigg, a Galley, a Drakkar, a Dhow and a "
            "Caravel, and no junk",
    "balloon": "no entity - nothing in the named mods flies slowly",
}


def provider(pid):
    for p in PROVIDERS:
        if p["id"] == pid:
            return p
    return None


def may_supply(vehicle_id):
    """[(provider id, entity or item id or None)] for a vehicle — the whole chain, best first."""
    out = []
    for p in PROVIDERS:
        hit = p["entities"].get(vehicle_id) or p["items"].get(vehicle_id)
        if hit:
            out.append((p["id"], hit, p["mark"]))
            continue
        kind = p.get("kinds", {}).get(vehicle_id)
        if kind:
            # A kind, not an id: the id comes from whichever content pack is installed.
            out.append((p["id"], "(from a content pack)", "content"))
    return out


def problems(vehicle_ids):
    """Everything that would make this table wrong.

    `vehicle_ids` is the list of ids in step 46 part 3's register, so a provider naming a vehicle
    that does not exist is caught at build time rather than at 3 a.m. in a world.
    """
    bad = []
    known = set(vehicle_ids)

    seen = set()
    for p in PROVIDERS:
        if p["id"] in seen:
            bad.append("duplicate provider " + p["id"])
        seen.add(p["id"])
        if p["mark"] not in ("read", "content", "vanilla"):
            bad.append(p["id"] + ": unknown mark " + p["mark"])
        if p["gate"] not in ("craft", "dockyard", "none"):
            bad.append(p["id"] + ": unknown gate " + p["gate"])
        if not p["note"] or not p["source"]:
            bad.append(p["id"] + ": no note or no source")
        # THE RULE. A mod whose ids come from content packs must carry NO ids.
        if p["mark"] == "content" and (p["entities"] or p["items"]):
            bad.append(p["id"] + " draws its ids from content packs and yet names some: "
                                  "that is an invention")
        if p["mark"] == "content":
            for k in p.get("kinds", {}):
                if k not in known:
                    bad.append(p["id"] + " claims the kind " + k + ", which the register lacks")
        # A read mod must actually name something, or the mark means nothing.
        if p["mark"] == "read" and not (p["entities"] or p["items"]):
            bad.append(p["id"] + " is marked read and names nothing")
        parts = p.get("parts", {})
        for key, ident in list(p["entities"].items()) + list(p["items"].items()):
            if ident.count(":") != 1:
                bad.append(p["id"] + ": " + ident + " is not a namespaced id")
            else:
                ns, path = ident.split(":")
                if ns != p["modid"] and p["mark"] != "vanilla":
                    bad.append(p["id"] + ": " + ident + " is not in its own namespace")
                if p["mark"] == "vanilla" and ns != "minecraft":
                    bad.append("vanilla names " + ident)
            # A provider may only name a vehicle the register has - unless it says the thing is a
            # part or an implement rather than a vehicle, which is a different list.
            if p["mark"] != "vanilla" and key not in known and key not in parts:
                bad.append(p["id"] + " supplies " + key + ", which the vehicle register does "
                                                          "not carry")

    # Every vehicle in part 3's register must be ANSWERABLE: some provider, or a vanilla stand-in,
    # or an explicit statement that nothing stands in.  A silence is worse than a null.
    for vid in vehicle_ids:
        chain = may_supply(vid)
        if not chain and vid not in NONE:
            bad.append("no provider, no stand-in and no statement of why for " + vid
                       + " - a silence is worse than a null")
        if chain and vid in NONE:
            bad.append(vid + " is listed as having no answer AND resolved by " + chain[0][0])
    for vid in NONE:
        if vid not in known:
            bad.append("NONE names " + vid + ", which the vehicle register does not carry")
        if not NONE[vid] or len(NONE[vid]) < 20:
            bad.append("NONE names " + vid + " but does not say why")

    # A part must be declared as one and must say what it is.
    for p in PROVIDERS:
        for k, why in p.get("parts", {}).items():
            if not why or len(why) < 20:
                bad.append(p["id"] + " calls " + k + " a part and does not say what it is")
            # A part MAY be a spawned entity: AstikorCarts' plow is a real entity you hitch to a
            # beast, and it is still not a vehicle in part 3's register. That is exactly why the
            # parts list exists, so this is not a clash and must not be checked as one.

    # The rule that catches the most: at least one mod must be a real, read id set.
    if not any(p["mark"] == "read" for p in PROVIDERS):
        bad.append("no provider has read ids, so the whole table is a guess")
    return bad


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import vehicle_table

    ids = [v["id"] for v in vehicle_table.VEHICLES]
    p = problems(ids)
    print("vehicle mods: %d providers, %d vehicles to place"
          % (len(PROVIDERS), len(ids)))
    for prov in PROVIDERS:
        n = len(prov["entities"]) + len(prov["items"])
        print("  %-18s %-7s %-8s %2d ids  %s"
              % (prov["id"], prov["mark"], prov["gate"], n, prov["name"]))
    print("\nwhat resolves to what:")
    for vid in ids:
        chain = may_supply(vid)
        if chain:
            print("  %-18s %s" % (vid, " -> ".join("%s:%s" % (p_, i) for p_, i, _ in chain)))
        elif vid in NONE:
            print("  %-18s NOTHING, and it says why" % vid)
        else:
            print("  %-18s UNACCOUNTED FOR" % vid)
    for b in p:
        print("  PROBLEM " + b)
    print("vehicle_mod_table: %d problem(s)" % len(p))
