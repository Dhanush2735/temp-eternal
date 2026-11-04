#!/usr/bin/env python3
"""
Step 45 part 5 (A13): pack the item resolver — what goes in a soldier's hand.

    python3 build_weapon_items.py            build, then write
    python3 build_weapon_items.py --check    check only, write nothing

The register lives in `weapon_items_table.py`. This script only checks it and writes it out; it
does not decide anything.

**Three rules the resolver is built on:**

1. **Item tags beat item ids**, wherever a mod publishes one. Spartan Weaponry's own wiki records
   that its registry names changed between 1.16.5 and 1.19.2 and broke datapacks that had
   hard-coded them. A tag survives that; an id does not.
2. **An unknown item is guessed from its name, and the guess is logged.** No register can list
   every item of every weapon mod. A wrong guess is visible and fixable; a missing weapon is not.
3. **A missing weapon is never an error.** With no weapon mod installed, every kind falls back to
   the vanilla item the armoury already names — part A put a `vanilla` field on all 24 kinds, and
   this pack deliberately does NOT duplicate that list. It reads it.

**This pack is data, not code.** It names mods by modid and items by id or tag. The Java asks
`ModList.get().isLoaded(modid)` and then looks the item up. Nothing here requires any mod to be
present, which is A13's whole rule: optional links, and everything also works without them.

Run from the repository root:  python3 worldfill/build_weapon_items.py
"""

import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data",
                   "eternalengine", "eternal", "war", "weapon_items.json.gz")

SYS_PATH = sys.path[:]
sys.path.insert(0, HERE)
try:
    import weapon_items_table as T
    import armory_table as A
finally:
    sys.path = SYS_PATH


def build():
    problems = list(T.problems())

    mods = [{"id": m["id"], "name": m["name"], "licence": m["licence"], "needs": m["needs"],
             "kinds": m["kinds"], "note": m["note"].replace("**", ""), "source": m["source"]}
            for m in T.MODS]
    entries = [{"mod": e["mod"], "kind": e["kind"], "tag": e.get("tag"), "item": e.get("item"),
                "mark": e["mark"], "note": e["note"].replace("**", "")} for e in T.ENTRIES]
    ammo = [{"mod": a["mod"], "kind": a["kind"], "item": a["item"], "mark": a["mark"],
             "note": a["note"].replace("**", "")} for a in T.AMMO]
    # Longest token first is applied at read time, not here, but the pack ships them in that
    # order so a reader that does not sort still gets "greatsword" before "sword".
    guess = [{"kind": k, "tokens": sorted(toks, key=len, reverse=True)}
             for k, toks in T.GUESS]
    local = {area: {k: {"name": v[0], "note": v[1]} for k, v in bykind.items()}
             for area, bykind in T.LOCAL_NAMES.items()}

    doc = {
        "format": "eternal-weapon-items-1",
        "id": "weapon_items",
        "source": ("The mods and their licences are recorded in worldfill/WEAPONS_RESEARCH.md "
                   "section 5, checked against Modrinth for 1.20.1 + Forge. Musket Mod's item ids "
                   "are read from its own source (github.com/ewewukek/mc-musketmod, Items.java). "
                   "Spartan Weaponry's tags from its GitHub wiki, Item Tags."),
        "note": ("What goes in a soldier's hand. THE MOD SHIPS NO WEAPONS OF ITS OWN (standing "
                 "instruction): it names the items of the weapon mods a player may have "
                 "installed and falls back to vanilla when they have none. Three rules: item TAGS "
                 "beat item ids, because Spartan Weaponry renamed its registry between 1.16.5 and "
                 "1.19.2 and broke datapacks that hard-coded ids; an unknown item is GUESSED from "
                 "its name and the guess is logged; and a missing weapon is never an error. The "
                 "vanilla fallback is not duplicated here - part A named one on all 24 kinds of "
                 "the armoury, and the resolver reads that."),
        "gaps": [
            "Only %d of the %d item entries are recorded from a mod's own documentation or "
            "source; the rest are estimated from the mod's naming pattern and are marked so."
            % (sum(1 for e in entries if e["mark"] == "recorded"), len(entries)),
            "**No Indian weapons exist for Java 1.20.1** - the research found only a Bedrock "
            "add-on (talwar, pata, tabar), which cannot be used. So a talwar in 1650 Agra is a "
            "modded sabre carrying the name talwar. The local names in this pack are the fix for "
            "that gap, not a claim that the item is right.",
            "**No matchlock mod exists.** India's gun from the 1500s to the 1700s was the "
            "matchlock (toradar), and no mod makes one; a musket stands in under the local name.",
            "TaCZ gun ids come from whichever gun packs are installed, so no single id is safe. "
            "Its entry is a placeholder and is meant to be corrected by config.",
            "Each gun mod has its own ammunition, which has to obey the same year rules as the "
            "weapon that fires it. Only Musket Mod's cartridge is recorded here.",
        ],
        "counts": {
            "mods": len(mods),
            "entries": len(entries),
            "recorded": sum(1 for e in entries if e["mark"] == "recorded"),
            "estimated": sum(1 for e in entries if e["mark"] == "estimated"),
            "ammo": len(ammo),
            "guessKinds": len(guess),
            "localAreas": len(local),
        },
        "mods": mods,
        "entries": entries,
        "ammo": ammo,
        "guess": guess,
        "localNames": local,
    }
    return doc, problems


def check(doc):
    bad = []

    def ok(cond, what):
        print(("  ok   " if cond else "  FAIL ") + what)
        if not cond:
            bad.append(what)

    ok(doc["format"] == "eternal-weapon-items-1", "the format is the one this builder writes")
    for key in ("mods", "entries", "ammo", "guess", "localNames", "gaps", "counts"):
        ok(key in doc, "the pack carries %s" % key)

    mods = {m["id"]: m for m in doc["mods"]}
    entries = doc["entries"]
    ok(len(mods) >= 5, "%d mods named" % len(mods))
    ok(len(entries) >= 10, "%d item entries" % len(entries))
    ok(all(e["mod"] in mods for e in entries), "every entry names a mod that exists")
    ok(all(e["kind"] in {k["id"] for k in A.ARMORY} for e in entries),
       "every entry names a kind the armoury has")
    ok(all(e["tag"] or e["item"] for e in entries), "every entry has a tag or an item")
    ok(all(e["mark"] in ("recorded", "estimated") for e in entries),
       "every entry is marked recorded or estimated")
    ok(all(e["tag"] is None or e["tag"].startswith("#") for e in entries),
       "every tag is written with a leading #")

    # The vanilla fallback must not be duplicated here. Part A owns it.
    ok("vanilla" not in doc and not any("vanilla" in e for e in entries),
       "the vanilla fallback is NOT duplicated here - the armoury owns it")

    # A tag is preferred to an id, and the pack should say how often it has one.
    tagged = sum(1 for e in entries if e["tag"])
    ok(tagged > 0, "%d entries use an item tag rather than an id" % tagged)

    # The guess table must be unambiguous: one token, one kind.
    seen = {}
    clash = []
    for g in doc["guess"]:
        for t in g["tokens"]:
            if t in seen:
                clash.append((t, seen[t], g["kind"]))
            seen[t] = g["kind"]
    ok(not clash, "no guess token is claimed twice (%d tokens)" % len(seen))

    # Every mod must be usable without its dependencies being mentioned wrongly.
    ok(all(set(m["needs"]) <= set(mods) | {"cloth_config", "architectury", "geckolib", "curios",
                                           "playeranimator"}
           for m in doc["mods"]), "every dependency is a mod in the pack or a named library")

    # Local names must be real kinds and real areas.
    areas = {a for a in A.AREAS}
    kinds = {k["id"] for k in A.ARMORY}
    ok(all(a in areas for a in doc["localNames"]), "every local-name area is one the atlas has")
    ok(all(k in kinds for by in doc["localNames"].values() for k in by),
       "every local-name kind is one the armoury has")
    ok(all(v["name"] for by in doc["localNames"].values() for v in by.values()),
       "every local name says something")

    return bad


def main(argv):
    doc, problems = build()
    for p in problems:
        print("  PROBLEM " + p)

    c = doc["counts"]
    print("weapon items: %d mods, %d entries (%d recorded, %d estimated), %d ammo, %d guess "
          "kinds, %d areas with local names"
          % (c["mods"], c["entries"], c["recorded"], c["estimated"], c["ammo"],
             c["guessKinds"], c["localAreas"]))

    bad = check(doc)
    if problems or bad or "--check" in argv:
        return 1 if (problems or bad) else 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    # mtime=0 so the same register always produces the same bytes: what ships is reproducible
    with gzip.GzipFile(OUT, "wb", mtime=0) as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    print("  wrote %s (%d bytes)" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
