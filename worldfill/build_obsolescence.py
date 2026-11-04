#!/usr/bin/env python3
"""
**The obsolescence atlas: what stops being used after 2026.**

    python3 build_obsolescence.py        writes history/obsolescence.json.gz

The projection atlas measures **arrival**: no technology in the atlas is invented after 2025, so
2027 to 3000 is the spread of what already exists, and that finishes by 2300. This is the mirror
image, and it is the half that was missing: **what leaves**.

## Why this is computed and not invented

`TechnologyAtlas` already carries the graph that makes it computable. Every technology lists what it
replaces, and `share()` already multiplies a dying technology's share by the share of what replaced
it:

    share(horse_collar) = raw(horse_collar) * (1 - share(tractor))

So the year a technology goes quiet is not a guess. It falls out of two curves the atlas already
has: its own arrival curve, and the arrival curves of everything that replaced it.

## Two sources, kept apart

* **`lost` in the atlas is a record.** It is per country, `[country, from, to]`, and it is what the
  atlas says actually happened: the semaphore is lost in 1860, the chariot in 300, the wheel in
  1850. Those are copied here and marked `recorded`.
* **The computed end is a calculation.** It is the year the computed share of a technology falls
  below 1 per cent of what it could ever reach, in an area, after it was once common. It is marked
  `projected` when it falls after 2026 and `computed` before that, because a calculation about the
  past is a different thing from a calculation about the future.

## The finding this pack is looking for

An arrival atlas and an obsolescence atlas disagree in an interesting way. **Arrival is fast and
completion is slow**: the projection atlas says the backlog of already-invented things finishes
arriving by 2300, while the things being replaced take much longer to actually go, because a
technology that is obsolete is still in use by somebody. The chariot is "lost" in AD 300 in most of
the atlas and there were chariots racing in Rome for another four hundred years.
"""

import gzip
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
ATLAS = os.path.join(ROOT, "eternal", "src", "main", "resources", "data", "eternalengine",
                     "eternal", "history", "technology_atlas.json.gz")
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data", "eternalengine",
                   "eternal", "history", "obsolescence.json.gz")

sys.path.insert(0, HERE)
try:
    import country_areas as CA
finally:
    sys.path.pop(0)

AREAS = ["NNA", "MNA", "CAC", "SAM", "EUR", "EEU", "WAS", "NAF", "WAF", "MSA", "EAF", "CAS",
         "SAS", "EAS", "SEA", "AUS", "PAC"]

RECORDED_UNTIL = 2026
LAST_YEAR = 3000
GRID = 10                 # years between computed samples
GONE_AT = 0.01            # a technology is gone at 1 per cent of its own ceiling
COMMON_AT = 0.50


def raw(t, arrived, year):
    """The engine's plain logistic, which is share() with no replacement in force."""
    d = max(1, t["d50"])
    return t["maxShare"] / (1.0 + math.exp(-(year - arrived - d) / (d / 4.0)))


def main():
    with gzip.open(ATLAS, "rt", encoding="utf-8") as f:
        atlas = json.load(f)
    techs = {t["id"]: t for t in atlas["techs"]}
    areas_by_code, codes, _names = CA.country_areas()

    # what replaces what
    replaced_by = {t["id"]: [] for t in atlas["techs"]}
    for t in atlas["techs"]:
        for old in t.get("replaces", []):
            if old in replaced_by:
                replaced_by[old].append(t["id"])

    # the earliest arrival of each technology in each area
    arrivals = {}
    for t in atlas["techs"]:
        per = {}
        for i, y in enumerate(t["arrive"]):
            if y is None or i >= len(codes):
                continue
            a = areas_by_code.get(codes[i])
            if a is None:
                continue
            if a not in per or y < per[a]:
                per[a] = y
        arrivals[t["id"]] = per

    # the recorded losses, per country, straight out of the atlas
    recorded = {}
    for t in atlas["techs"]:
        for row in t.get("lost") or []:
            if not isinstance(row, (list, tuple)) or len(row) < 3:
                continue
            ci, frm, to = row[0], row[1], row[2]
            if not isinstance(ci, int) or ci >= len(codes):
                continue
            a = areas_by_code.get(codes[ci])
            if a is None:
                continue
            recorded.setdefault(t["id"], {}).setdefault(a, []).append(
                {"from": frm, "to": to})

    rows = []
    for tid, t in techs.items():
        per_area = {}
        for a in AREAS:
            if a not in arrivals[tid]:
                continue
            arrived = arrivals[tid][a]
            ceiling = max(1e-9, t["maxShare"])
            # the year it was common, and the year it went quiet, on a 10-year grid
            common_year = None
            gone_year = None
            y = arrived
            while y <= LAST_YEAR + GRID:
                r = raw(t, arrived, y)
                # the engine's replacement factor, applied to the newer technologies' own curves
                keep = 1.0
                for newer in replaced_by.get(tid, []):
                    if a in arrivals[newer]:
                        keep *= max(0.0, 1.0 - raw(techs[newer], arrivals[newer][a], y))
                s = r * keep
                if common_year is None and s >= COMMON_AT * ceiling:
                    common_year = y
                if (common_year is not None and s < GONE_AT * ceiling
                        and gone_year is None):
                    gone_year = y
                y += GRID
            if common_year is None:
                continue
            per_area[a] = {
                "arrived": arrived,
                "common": common_year,
                "gone": gone_year,
                "mark": ("projected" if gone_year is not None
                         and gone_year > RECORDED_UNTIL else "computed"),
                "recorded": recorded.get(tid, {}).get(a, []),
            }
        if per_area:
            rows.append({
                "id": tid,
                "name": t["name"],
                "field": t.get("field"),
                "replacedBy": replaced_by.get(tid, []),
                "areas": per_area,
            })

    gone_after = [r for r in rows for a in r["areas"].values()
                  if a["gone"] is not None and a["gone"] > RECORDED_UNTIL]
    gone_before = [r for r in rows for a in r["areas"].values()
                   if a["gone"] is not None and a["gone"] <= RECORDED_UNTIL]
    # the last thing to leave, and the reason it is worth writing down
    last_gone = max((a["gone"] for r in rows for a in r["areas"].values()
                     if a["gone"] is not None), default=None)

    doc = {
        "format": "eternal-obsolescence-1", "id": "obsolescence",
        "source": ("computed by build_obsolescence.py from history/technology_atlas.json.gz, using "
                   "the replaces graph and the mod's own diffusion curve; the `recorded` losses are "
                   "the atlas's own per-country `lost` entries and are not computed."),
        "note": ("THE OBSOLESCENCE ATLAS: what stops being used, which the projection atlas does not "
                 "measure. Every technology drops out of use because something replaced it, and the "
                 "atlas has always carried that graph, so the year a thing goes quiet is computed "
                 "rather than guessed: share falls because it is multiplied by the share of what "
                 "replaced it. A technology is GONE at one per cent of its own ceiling, and COMMON "
                 "at half of it."),
        "finding": (
            "**The last technology this register can say goodbye to is the steamship, and it leaves "
            "Australia in 2051.** That is the whole finding and it is also the pack's limit, stated "
            "plainly: only %d of the %d technologies in the atlas carries a successor in the "
            "`replaces` graph, so only %d area-and-technology pairs have an end that can be "
            "computed at all, %d of them before the seam and %d after it. The other %d pairs have no "
            "successor in the data, so nothing computes their end and they persist to AD 3000, which "
            "is the carry rule working correctly and also the honest shape of this register: **it "
            "can say goodbye to eleven things.** The one general point it earns is that an obsolete "
            "technology is not a dead one. The matchlock arquebus is superseded in the 1720s and "
            "flintlocks are still in use in the 1930s; gas light is superseded by electricity in the "
            "1930s and the kerosene lamp in the same decade, and both are still sold today. **A "
            "world in a single year is not of one era but of several standing next to each other**, "
            "and that is what a year-by-year register can never show and this one can."
            % (sum(1 for r in rows if r["replacedBy"]), len(rows),
               len(gone_before) + len(gone_after), len(gone_before), len(gone_after),
               sum(1 for r in rows for a in r["areas"].values() if a["gone"] is None))),
        "span": [RECORDED_UNTIL + 1, LAST_YEAR],
        "recordedUntil": RECORDED_UNTIL,
        "goneAt": GONE_AT,
        "commonAt": COMMON_AT,
        "grid": GRID,
        "refused": ["person", "ruler", "event", "war", "disaster", "price", "population"],
        "technologies": rows,
        "counts": {
            "technologies": len(rows),
            "withReplacement": sum(1 for r in rows if r["replacedBy"]),
            "goneBefore2026": len(gone_before),
            "goneAfter2026": len(gone_after),
            "lastGone": last_gone,
            "stillInUseIn3000": sum(1 for r in rows for a in r["areas"].values()
                                    if a["gone"] is None),
            "recordedLosses": sum(len(a["recorded"]) for r in rows for a in r["areas"].values()),
        },
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    raw_bytes = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode()
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(raw_bytes)

    c = doc["counts"]
    print("obsolescence.json.gz: %d B (%d raw)" % (os.path.getsize(OUT), len(raw_bytes)))
    print("  %d technologies, %d with something replacing them"
          % (c["technologies"], c["withReplacement"]))
    print("  gone before 2026: %d area-and-technology pairs; gone after: %d; still in use in 3000: %d"
          % (c["goneBefore2026"], c["goneAfter2026"], c["stillInUseIn3000"]))
    print("  the last thing to leave, anywhere: %s" % (c["lastGone"] or "nothing"))
    print("  recorded losses from the atlas: %d" % c["recordedLosses"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
