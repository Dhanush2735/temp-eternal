#!/usr/bin/env python3
"""Step 43 part 3 (J3, signs and inscriptions in local scripts): build history/scripts.json.gz.

What this pack is for
---------------------

A sign is two questions, and they have different answers.

  1. **Is there writing here at all?** Not from this pack. It is
     `TechnologyAtlas.arrivalAt("writing") <= year && !lostAt(...)`, which is measured, dated and
     per country. Sumer -3027, Egypt -3193, Rome -509, Paris -598, Beijing -877, Yucatan -300,
     Tenochtitlan 1300, **Cuzco 1576** - the Inca had no writing, and the atlas says so.

  2. **In what script?** Answered in two tiers, and the order matters:

       * **Tier 1, measured and specific** - place -> ruler -> the polity's own languages ->
         `CultureAtlas.scriptOf(language, year)`. This is dated and exact: it says *"Persian in
         the Perso-Arabic script"* at Delhi in 1700 and *"Middle Chinese in Chinese characters"*
         at Beijing in 1000, because the script table carries year spans (Turkish was in Arabic
         letters until 1928; Tamil was Tamil-Brahmi until 600).

       * **Tier 2, this pack** - a hand-written area-and-era table, used only where tier 1 has no
         answer.

Tier 2 exists because tier 1 was **measured and found wanting**, not because it was assumed to be.
Coverage of tier 1 by era, against the share of land where writing had arrived:

        year   writing   tier 1   both
       -2500       2%       0%     0%
        -500      17%       1%     1%
          0      26%      11%    10%
        1000      38%      24%    21%
        1300      49%      30%    24%
        1700      80%      36%    33%
        1900     100%      65%    65%
        2000     100%      96%    96%

So at AD 1000, 38% of the world could write and only 24% could be given a script. The gap is "we
cannot name it", not "nobody was writing" - and the natural first guess, that the nearest living
language would name the script, measures **12%** and is worse than useless (only 18% of land has a
major language within 300 km, and just 5% of the 6,741 languages match a script key at all).

**Tier 1 also cannot be used alone**, because it is a modern chain with an undated fallback. Asked
about Cuzco in 1400 it answers *"Aymara in the Latin alphabet"* - a century before any alphabet
reached the Andes. Gating everything on the writing tech's arrival is what catches that.

So: tier 1 when it answers and the atlas says writing is here; tier 2 when tier 1 cannot; and no
script at all where writing has not arrived, which is a real and common answer.

Checks
------

  * every area the mod knows (17 of them) has at least one script row, and no row names an area
    the mod does not know - one map of the world, not two that can disagree
  * no script row covers a span that starts after it ends, and every row has a source
  * every sign kind has a name, what, line and source
  * signs that need a technology (paper for posted notices) name one the atlas knows
  * the sign kinds span the whole timeline and are not all modern

Run:  python3 build_scripts.py            build, then check
"""
import gzip
import io
import json
import os

import script_table as T

HERE = os.path.dirname(os.path.abspath(__file__))
HIST = os.path.normpath(os.path.join(
    HERE, "..", "eternal", "src", "main", "resources", "data", "eternalengine", "eternal", "history"))
OUT = os.path.join(HIST, "scripts.json.gz")
PRODUCTS = os.path.normpath(os.path.join(
    HERE, "..", "eternal", "src", "main", "resources", "data", "eternalengine", "eternal", "economy",
    "products_world.json"))
TECH = os.path.join(HIST, "technology_atlas.json.gz")


def known_areas():
    with open(PRODUCTS, encoding="utf-8") as f:
        return {a["id"] for a in json.load(f)["areas"]}


def known_techs():
    with gzip.open(TECH, "rt", encoding="utf-8") as f:
        d = json.load(f)
    ids = set()
    for t in d.get("techs", d.get("technologies", [])):
        if isinstance(t, dict) and "id" in t:
            ids.add(t["id"])
    return ids


def _script(r):
    out = {"area": r["area"], "start": r["start"], "end": r["end"], "name": r["name"],
           "what": r["what"], "line": r["line"], "source": r["source"]}
    if r.get("note"):
        out["note"] = r["note"]
    return out


def _sign(r):
    out = {"id": r["id"], "name": r["name"], "what": r["what"], "line": r["line"],
           "source": r["source"], "start": r["start"], "end": r["end"],
           "areas": r["areas"], "literacy": r["literacy"], "needs": r["needs"]}
    if r.get("note"):
        out["note"] = r["note"]
    return out


def build():
    doc = {
        "format": "eternal-scripts-1",
        "id": "scripts",
        "source": ("Hand-written table for step 43 (J3), read from the reference works named on "
                   "each row (Cuneiform; Brahmi script; Oracle bone script; Maya script; Quipu; "
                   "Blackletter; Cyrillic script; Ajami script; and the others). Tier 1 - the "
                   "script of a polity's own languages - is not from here at all: it is read "
                   "from `culture.json.gz`'s own dated script table at run time."),
        "note": ("What the signs at a place are written in. Two questions with two answers: "
                 "**whether there is writing here** comes from the technology atlas's `writing` "
                 "tech, dated and per country (Cuzco 1576, Auckland 1814); **which script** comes "
                 "first from the polity ruling here and its languages (dated and specific: "
                 "Persian in the Perso-Arabic script at Delhi in 1700) and, where that has no "
                 "answer, from the area-and-era table below. Where writing has not arrived, the "
                 "answer is that there are no signs, and that is recorded rather than guessed."),
        "counts": {},
        "gaps": [
            "Every script row below is this table's reading of what the region's own documents "
            "were written in. No source states that a given square in a given century had signs "
            "in a given script.",
            "The area-and-era rows are only a FALLBACK. They are consulted where the ruler's "
            "languages give no answer, which is most of the world before about 1500 and almost "
            "nowhere after 1900 - the fallback is therefore doing its heaviest work exactly where "
            "it is least reliable.",
            "Tier 1 (the polity's languages) is a MODERN chain: the language of a state today, "
            "projected back through its whole span. A polity that changed language mid-span is "
            "wrong for part of it, and the 12 polities with hand-written dated periods are the "
            "only ones that are exact.",
            "`CultureAtlas.scriptOf` falls back to 'the Latin alphabet' for 55 languages with no "
            "year bound at all, so ungated it puts Latin letters in Cuzco in 1400. Every answer "
            "here is gated on the writing technology having arrived at this place, which is what "
            "stops that.",
            "Literacy is keyed by modern country and mostly has no figures before 1950, so the "
            "`literacy` floor on a sign kind (a posted notice needs readers) is nearly always "
            "silent in the past rather than informative.",
            "Eleven kinds of sign is a sample and not a catalogue: there is no row for the "
            "wax tablet, the ostracon, the coin legend, the wax seal, or the tattoo.",
        ],
        "scripts": [_script(r) for r in T.all_scripts()],
        "signs": [_sign(r) for r in T.all_signs()],
    }
    doc["counts"] = {
        "scripts": len(doc["scripts"]),
        "areas": len({r["area"] for r in doc["scripts"]}),
        "signs": len(doc["signs"]),
    }
    with open(OUT, "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    size = os.path.getsize(OUT)
    print("scripts.json.gz: %d scripts over %d areas, %d kinds of sign (%d bytes gzipped)"
          % (doc["counts"]["scripts"], doc["counts"]["areas"], doc["counts"]["signs"], size))
    return doc


def check():
    bad = []
    areas = known_areas()
    techs = known_techs()
    rows = T.all_scripts()
    signs = T.all_signs()

    def ok(cond, msg):
        print(("ok   " if cond else "FAIL ") + msg)
        if not cond:
            bad.append(msg)

    covered = {r["area"] for r in rows}
    ok(not (covered - areas), "every script row names an area the mod knows "
                              "(%s)" % (sorted(covered - areas) or "none outside"))
    ok(not (areas - covered), "every area the mod knows has a script (%d of %d, missing %s)"
       % (len(covered & areas), len(areas), sorted(areas - covered) or "none"))

    for r in rows:
        tag = "%s/%s" % (r["area"], r["name"])
        if r["end"] is not None and r["start"] is not None and r["start"] >= r["end"]:
            bad.append(tag)
        if not r.get("source"):
            bad.append(tag)
    ok(not bad, "every script row spans a real range of years and names a source")

    bad2 = [s["id"] for s in signs
            if not (s["name"] and s["what"] and s["line"] and s["source"])]
    ok(not bad2, "every kind of sign has a name, a what, a line and a source (%s)"
       % (bad2 or "all"))

    missing = sorted({n for s in signs for n in s["needs"]} - techs)
    ok(not missing, "every technology a sign needs is in the atlas (%s)" % (missing or "all found"))

    ancient = [s for s in signs if s["start"] is not None and s["start"] < 0]
    ok(len(ancient) >= 3, "the sign kinds are not all modern (%d reach before year zero)" % len(ancient))

    print()
    print("scripts: %d problem(s)" % len(bad))
    return bad


if __name__ == "__main__":
    build()
    check()
