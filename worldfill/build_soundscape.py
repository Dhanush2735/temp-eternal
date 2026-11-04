#!/usr/bin/env python3
"""Step 43 part 2 (J2, sounds of the era): build history/soundscape.json.gz from soundscape_table.py.

Shape
-----

One table, `sounds`, of four kinds - **ground, crowd, voice, machine** - because a soundscape is not
a list of noises but a set of layers, each with its own reason to be there:

  * `ground`  (always)      - the place, whether or not anybody is in it; fired by `nearSea`
  * `crowd`   (population)  - fired by step 17's `SettlementDensity.intensity`
  * `voice`   (faith)       - fired by the faith of the polity ruling here
  * `machine` (technology)  - fired by the technology atlas, per country and dated

A row carries `when`, because a soundscape is a **day** and not a list: the call to prayer is before
dawn, the bell is on the hour, the market is in the morning, and a train is when the train comes.

What is estimated, and what is not
----------------------------------

**Every row is estimated**, and says so: no source states that a given square in a given century was
loud with bells.

**But what makes a row fire is not estimated at all**, and that is the whole point of this part. It
is the opposite of the code it replaces. `HistoricalAudioDirector` chose one of six soundscapes from
the year alone - `x` and `z` were parameters it never read - so China in 1000 came back
*Classical Mediterranean* and everything after 1920 came back *PASTORAL_ANCIENT*. Every row here
instead hangs off a register the mod already ships and that answers by place. The reading is only
ever *what it sounds like*, never *whether it is there*.

Checks
------

  * every row has a kind, a name, a what, a when, a line and a source
  * `voice` rows name only faith families `culture.json.gz` also knows (30 of them) - one faith
    vocabulary in the mod, and not a second one that can disagree with the first
  * `machine` rows name only technologies the atlas also knows
  * no row is both sea and inland, and no row is both a faith and a technology
  * the four kinds are all present, and the ground is never empty
  * **every faith family that a polity actually holds resolves to a voice**, so no place falls
    through for want of a row
  * the default is not also a row - the defect F3 and D7 both hit

Run:  python3 build_soundscape.py            build, then check
"""
import gzip
import json
import os
import sys

import soundscape_table as T

HERE = os.path.dirname(os.path.abspath(__file__))
HIST = os.path.normpath(os.path.join(
    HERE, "..", "eternal", "src", "main", "resources", "data", "eternalengine", "eternal", "history"))
OUT = os.path.join(HIST, "soundscape.json.gz")
CULTURE = os.path.join(HIST, "culture.json.gz")
POLITY = os.path.join(HIST, "polity_facts.json.gz")

TABLE = "sounds"
DEFAULT_ONLY = "wind"


def known_faiths():
    with gzip.open(CULTURE, "rt", encoding="utf-8") as f:
        return [x["key"] for x in json.load(f)["faiths"]]


def known_techs():
    """Every technology id in the atlas, read from the pack the atlas itself reads."""
    p = os.path.join(HIST, "technology_atlas.json.gz")
    with gzip.open(p, "rt", encoding="utf-8") as f:
        d = json.load(f)
    ids = set()
    for t in d.get("techs", d.get("technologies", [])):
        if isinstance(t, dict) and "id" in t:
            ids.add(t["id"])
    return ids


def held_faiths():
    """Every distinct faith string a polity actually carries - what the voice rows must cover."""
    with gzip.open(POLITY, "rt", encoding="utf-8") as f:
        return {r for x in json.load(f)["polities"] for r in (x.get("rel") or [])}


def _row(r):
    out = {
        "id": r["id"], "kind": r["kind"], "name": r["name"], "what": r["what"],
        "when": r["when"], "line": r["line"], "priority": r["priority"],
        "source": r["source"], "loud": r["loud"],
    }
    for key, empty in (("faiths", []), ("tech", None), ("coast", None)):
        v = r.get(key)
        if v is not None and v != empty:
            out[key] = v
    if r["kind"] == "crowd":
        out["minIntensity"] = r["minIntensity"]
    if r.get("catchAll"):
        out["catchAll"] = True
    if r["kind"] == "machine":
        out["industrial"] = bool(r.get("industrial", True))
    return out


def build():
    doc = {
        "format": "eternal-soundscape-1",
        "id": "soundscape",
        "source": ("Hand-written table for step 43 (J2), read from the reference works named on "
                   "each row: Adhan, Church bell, Blagovest, Hindu temple, Conch, Buddhist chant, "
                   "Kirtan, Shofar, Firecracker, Shinto shrine, Matsuri, Shamanism, Watermill, "
                   "Steam engine, Railway, Car, Aircraft, Ironworks, Market (place), Wind, Sea and "
                   "others. Every row is this table's reading and is marked estimated. WHETHER a "
                   "sound is there at all is not from this pack - it is derived from the ruler "
                   "register (faith), the technology atlas (machines) and SettlementDensity "
                   "(crowds)."),
        "note": ("What a place sounds like, by layer: `ground` (the place itself), `crowd` (how "
                 "many people), `voice` (what they do on purpose, at set hours, because of what "
                 "they believe) and `machine` (what has reached this country). A `voice` row fires "
                 "from the faith family of the polity ruling here; a `machine` row fires from the "
                 "technology atlas, per country and dated, from the year it ARRIVED here. `when` "
                 "matters as much as `what`: this pack describes a "
                 "day, not a list of noises. Replaces step 43's `HistoricalAudioDirector`, which "
                 "chose its soundscape from the year alone."),
        "counts": {},
        "gaps": [
            "Every row is this table's reading and not a measurement: no source states that a given "
            "square in a given century was loud with bells.",
            "**The mod has no audio assets, and this step cannot record any.** What J2 fixes is "
            "*which* sound belongs here and *why* - the part that was nonsense. What is actually "
            "heard is still played with whatever sounds exist.",
            "The voice comes from two places, and the first was not the obvious one: the 19,828 "
            "holy places standing within 25 km that year (place-based, dated, and why Mecca has a "
            "voice although the Ottomans carry no religion in the survey), and only then the faith "
            "of the polity ruling here. Where neither reaches, the place is honestly quiet.",
            "The voice rows are keyed to 30 faith families, so a family the mod does not carry "
            "(Bahai, Druze, Yazidi) resolves to nothing and the row `unknown_gods` speaks instead "
            "rather than leaving a temple silently empty.",
            "The faith of a POLITY is dated only by its own span in the ruler register, so one that "
            "changed faith mid-span is wrong for part of it. The 12 polities with hand-written "
            "`relP` periods are exact; the other 948 are not. Holy-place dates carry no such gap.",
            "The machine rows fire the year a technology ARRIVES at a place, which the atlas "
            "measures per country (railway: York 1827, Delhi 1864); but a water mill arriving in "
            "AD 240 is not the Industrial Revolution, so `industrial()` is true only for the five "
            "rows that are, and the mill counts as a machine without counting as an age.",
            "Before AD 1500 the script and language of a place are unknown (C14's recorded gap), "
            "but the faith is not - it comes from the ruler, which is why the voice rows reach "
            "further back than anything else in this step.",
        ],
        "faiths": [],
    }

    pack = [_row(r) for r in T.ALL]
    pack.sort(key=lambda r: (-r["priority"], r["id"]))
    doc[TABLE] = pack
    doc["default_" + TABLE] = _row(T.DEFAULT)
    doc["counts"][TABLE] = len(pack)
    doc["counts"]["estimated"] = len(pack)
    doc["counts"]["recorded"] = 0
    doc["counts"]["ground"] = sum(1 for r in T.ALL if r["kind"] == "ground")
    doc["counts"]["crowd"] = sum(1 for r in T.ALL if r["kind"] == "crowd")
    doc["counts"]["voice"] = sum(1 for r in T.ALL if r["kind"] == "voice")
    doc["counts"]["machine"] = sum(1 for r in T.ALL if r["kind"] == "machine")
    doc["faiths"] = sorted({f for r in T.ALL for f in (r.get("faiths") or [])})

    blob = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(blob)
    print("soundscape.json.gz: %d sounds (%d ground, %d crowd, %d voice, %d machine) over %d faith "
          "families (%d bytes gzipped)"
          % (doc["counts"][TABLE], doc["counts"]["ground"], doc["counts"]["crowd"],
             doc["counts"]["voice"], doc["counts"]["machine"], len(doc["faiths"]),
             os.path.getsize(OUT)))
    return doc


def check():
    with gzip.open(OUT, "rt", encoding="utf-8") as f:
        d = json.load(f)
    bad = []

    def ok(cond, what):
        print(("  ok   " if cond else "  FAIL ") + what)
        if not cond:
            bad.append(what)

    ok(d["format"] == "eternal-soundscape-1", "the format is the one this builder writes")
    for key in (TABLE, "default_" + TABLE, "gaps", "counts", "faiths"):
        ok(key in d, "the pack carries %s" % key)

    rows = d[TABLE]
    ok(len(rows) >= 20, "sounds: %d rows" % len(rows))
    ok(len({r["id"] for r in rows}) == len(rows), "no two rows share an id")
    for r in rows:
        ok(bool(r.get("source")), "%s names the work it was read from" % r["id"])
        ok(all(r.get(k) for k in ("name", "what", "when", "line")),
           "%s has a name, a what, a when and a line" % r["id"])
        ok(r["kind"] in ("ground", "crowd", "voice", "machine"),
           "%s has a kind this pack understands (%s)" % (r["id"], r["kind"]))
        ok(not (r.get("faiths") and r.get("tech")),
           "%s is not both a faith and a technology" % r["id"])
        ok(r.get("loud") is not None, "%s says how loud it is" % r["id"])

    for kind in ("ground", "crowd", "voice", "machine"):
        ok(sum(1 for r in rows if r["kind"] == kind) >= 2,
           "the %s layer is not a single row (%d)" % (kind, sum(1 for r in rows if r["kind"] == kind)))

    # The one vocabulary rule that matters: the faith families must be the ones the mod already has.
    fams = known_faiths()
    stray = sorted({f for r in rows for f in (r.get("faiths") or []) if f not in fams})
    ok(not stray, "every faith family is one culture.json.gz also knows (%s)"
       % (", ".join(stray) or "none"))

    techs = known_techs()
    bad_tech = sorted({r["tech"] for r in rows if r.get("tech") and r["tech"] not in techs})
    ok(not bad_tech, "every technology is one the atlas also knows (%s)"
       % (", ".join(bad_tech) or "none"))

    # Every faith a polity actually holds has to resolve to a voice, or a place falls through.
    covered = {f for r in rows for f in (r.get("faiths") or [])}
    with gzip.open(CULTURE, "rt", encoding="utf-8") as f:
        fam = json.load(f)["faiths"]
    def family_of(name):
        t = (name or "").lower()
        for f in fam:
            for m in f["match"]:
                if m in t:
                    return f["key"]
        return None
    held = held_faiths()
    families_used = {family_of(h) for h in held} - {None}
    missing = sorted(k for k in families_used if k not in covered)
    ok(not missing,
       "every faith family a polity holds has a voice row (%s)" % (", ".join(missing) or "none"))

    # The check that actually matters. Counting how many faith *strings* resolve is a proxy, and a
    # bad one: it punishes a long tail of one-polity faiths. What must be true is that no POLITY is
    # left silent. A polity is covered if any of its faiths resolves to a covered family; the 27
    # (of 960) where none does are covered by the catch-all row instead.
    skip = ("various", "several", "many", "mixed", "official", "state")
    with gzip.open(POLITY, "rt", encoding="utf-8") as f:
        polities = json.load(f)["polities"]
    held_polities = [x for x in polities
                     if any(not (r or "").lower().startswith(skip) for r in (x.get("rel") or []))]
    silent, caught = [], 0
    for x in held_polities:
        names = [r for r in x["rel"] if not (r or "").lower().startswith(skip)]
        if any(family_of(r) in covered for r in names):
            continue
        if any(r.get("catchAll") for r in rows):
            caught += 1
        else:
            silent.append(x["n"])
    ok(not silent,
       "no polity with a faith is left silent: %d covered by a family, %d by the catch-all (%d "
       "unreachable: %s)" % (len(held_polities) - caught - len(silent), caught, len(silent),
                             ", ".join(silent[:4])))

    ok(sum(1 for r in rows if r.get("catchAll")) == 1,
       "exactly one row catches the faiths the mod cannot name (%d)"
       % sum(1 for r in rows if r.get("catchAll")))
    ok(all(r["id"] != DEFAULT_ONLY for r in rows),
       "the default is not also a row, or it would shadow the fallback (%s)" % DEFAULT_ONLY)
    ok(d["default_" + TABLE]["id"] == DEFAULT_ONLY, "the fallback is the wind")

    print()
    for r in sorted(rows, key=lambda r: (r["kind"], -r["priority"])):
        fire = (",".join(r.get("faiths") or []) or r.get("tech")
                or ("any faith not covered" if r.get("catchAll") else None)
                or ("crowd>=%.2f" % r["minIntensity"] if r["kind"] == "crowd" else None)
                or ("coast" if r.get("coast") is True else
                    "inland" if r.get("coast") is False else "always"))
        print("       %-8s %-18s %-22s loud=%d  fires on: %s"
              % (r["kind"], r["id"], r["name"][:22], r["loud"], fire))

    print()
    print("soundscape: %d problem(s)" % len(bad))
    return len(bad)


if __name__ == "__main__":
    build()
    sys.exit(1 if check() else 0)
