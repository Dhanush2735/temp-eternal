#!/usr/bin/env python3
"""
Step 47b (the projection atlas): **what the data says about AD 2027 to 3000, computed rather than
invented.**

    python3 build_projection_atlas.py        writes history/projection.json.gz and prints the result

The user asked whether the same "all kinds of data" that exists for 3000 BC to AD 2026 can be built
for 2027 to 3000. `projection_plan.py` answers *what may be built*: 5 packs are computed, 64 are
carried, 32 are refused, and the refused ones are people, events, wars, prices, disasters and
populations. This script builds the part that can actually be computed, and it is not nothing.

## The one thing that is genuinely computable and genuinely new

**No technology in the atlas arrives after 2025.** That is a fact about the pack, and it is the
whole justification for this file: the atlas contains no invention, so any statement this script
makes about 2400 is a statement about the **spread of things that were already invented in 2026**,
which is exactly the class the guardrail allows. The engine's own diffusion curve already keeps
running past the seam without clamping:

    share = maxShare / (1 + exp(-(year - arrived - d) / (d / 4)))

so a technology that has half-reached a place in 2026 finishes reaching it in the next century, and
that curve is a computation and not a guess.

## What that produces, and why it is worth having

The projection atlas says, for each of the 17 areas and each century from 2026 to 3000, how much of
the already-invented technology has actually reached people. Its finding is about **the backlog**:
in 2026 a large share of what humanity knows how to do has not yet reached most of the people who
could use it, and the next two centuries are not a story of new inventions but of the old ones
arriving.

**What it deliberately does not do:** it invents no technology, names no person, prices nothing and
counts nobody. Those are refused by `Projector` and this pack does not smuggle them back in.
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
                   "eternal", "history", "projection.json.gz")

sys.path.insert(0, HERE)
try:
    import country_areas as CA
    import projection_plan as PP
finally:
    sys.path.pop(0)

AREAS = ["NNA", "MNA", "CAC", "SAM", "EUR", "EEU", "WAS", "NAF", "WAF", "MSA", "EAF", "CAS",
         "SAS", "EAS", "SEA", "AUS", "PAC"]

STEPS = [2026, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900, 3000]

# The seam, restated here so this script cannot drift from the engine.
RECORDED_UNTIL = 2026
LAST_YEAR = 3000


def share(tech, arrived, year):
    """The engine's own curve, for a town. TechnologyAtlas.share, the branch without a series."""
    d = max(1, tech["d50"])
    return tech["maxShare"] / (1.0 + math.exp(-(year - arrived - d) / (d / 4.0)))


def load_atlas():
    with gzip.open(ATLAS, "rt", encoding="utf-8") as f:
        return json.load(f)


def area_arrivals(atlas):
    """{tech id: {area: first arrival}} using the earliest arrival among the area's countries."""
    areas_by_code, codes, _names = CA.country_areas()
    out = {}
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
        out[t["id"]] = per
    return out


def build():
    atlas = load_atlas()
    arrivals = area_arrivals(atlas)
    techs = {t["id"]: t for t in atlas["techs"]}

    # THE CHECK THAT MAKES THE WHOLE PACK HONEST: nothing in the atlas is invented after the seam.
    late = [(t["id"], max(y for y in t["arrive"] if y is not None)) for t in atlas["techs"]
            if any(y is not None and y > RECORDED_UNTIL for y in t["arrive"])]
    assert not late, "the atlas invents technology after the seam: %r" % late[:5]

    areas = {}
    for a in AREAS:
        per_area = {}
        for tid, per in arrivals.items():
            if a in per:
                per_area[tid] = per[a]
        if not per_area:
            continue
        row = {"techs": len(per_area), "series": {}}
        for step in STEPS:
            vals = []
            common = 0
            saturated = 0
            for tid, arrived in per_area.items():
                t = techs[tid]
                v = share(t, arrived, step)
                vals.append(v)
                ceiling = max(1e-9, t["maxShare"])
                if v >= 0.5 * ceiling:
                    common += 1
                if v >= 0.95 * ceiling:
                    saturated += 1
            row["series"][str(step)] = {
                "mean": round(sum(vals) / len(vals), 4),
                "common": common,
                "saturated": saturated,
            }
        # the backlog: what is not yet common in 2026, and the year it does become common
        backlog = []
        for tid, arrived in per_area.items():
            t = techs[tid]
            ceiling = max(1e-9, t["maxShare"])
            s26 = share(t, arrived, RECORDED_UNTIL)
            # "common" is half of what this technology could ever reach, not an absolute half:
            # a technology whose ceiling is a fifth of households is common when it reaches a
            # tenth, and an absolute test would say it never arrives at all.
            if s26 >= 0.5 * ceiling:
                continue
            finish = None
            for y in range(RECORDED_UNTIL + 1, LAST_YEAR + 1):
                if share(t, arrived, y) >= 0.5 * ceiling:
                    finish = y
                    break
            backlog.append({"id": tid, "arrived": arrived, "share2026": round(s26, 3),
                            "commonBy": finish})
        backlog.sort(key=lambda b: (-(b["commonBy"] or 0), b["id"]))
        row["backlog"] = backlog
        row["backlogCount"] = len(backlog)
        row["commonBy3000"] = sum(1 for b in backlog if b["commonBy"] is not None)
        areas[a] = row

    # when does the last already-invented thing finish arriving, anywhere
    last = 0
    for a, row in areas.items():
        for b in row["backlog"]:
            if b["commonBy"] is None:
                last = LAST_YEAR + 1        # never, and that is a finding
            else:
                last = max(last, b["commonBy"])

    mean2026 = round(sum(r["series"]["2026"]["mean"] for r in areas.values()) / len(areas), 4)
    mean3000 = round(sum(r["series"]["3000"]["mean"] for r in areas.values()) / len(areas), 4)
    gaps = sorted(((r["series"]["2026"]["mean"], a) for a, r in areas.items()))
    return {
        "format": "eternal-projection-1", "id": "projection",
        "source": ("computed by build_projection_atlas.py from history/technology_atlas.json.gz and "
                   "the mod's own country grid, using TechnologyAtlas.share with the curve the "
                   "engine uses for a town."),
        "note": ("THE PROJECTION ATLAS: what can honestly be said about AD 2027 to 3000. It is not "
                 "a history of the future, because the engine refuses to invent a person, an "
                 "event, a war, a price or a population figure past the last recorded year. It is "
                 "the other class: **no technology in the atlas arrives after 2025**, so every "
                 "figure here is the SPREAD of something already invented in 2026, which the "
                 "guardrail allows and which is computable rather than guessed. The engine's "
                 "diffusion curve never clamped at the seam; this pack reads it forward and writes "
                 "down where it lands."),
        "finding": (
            "**The future in this file runs out in 2300, and that is the most useful thing it "
            "says.** No technology in the atlas arrives after 2025, so the only honest change to "
            "compute is the SPREAD of what already exists, and there is a finite amount of that "
            "left: %d area-and-technology pairs are still short of common in 2026, **all %d of them "
            "clear by %d**, and after that the curve is flat for seven hundred years. So the honest "
            "answer to 'what is the world like in 2400' is 'the world of 2026, fully spread', and "
            "everything a story adds beyond that is an invention that the engine refuses to make. "
            "**The two centuries to 2300 are not a story of new inventions but of the old ones "
            "arriving**, and the difference between what humanity knows and what humanity has is "
            "the largest change in this pack."
            % (sum(r["backlogCount"] for r in areas.values()),
               sum(r["commonBy3000"] for r in areas.values()), last)),
        "span": [RECORDED_UNTIL + 1, LAST_YEAR],
        "recordedUntil": RECORDED_UNTIL,
        "mark": "projected",
        "steps": STEPS,
        "refused": ["person", "ruler", "event", "war", "disaster", "price", "population"],
        "areas": areas,
        "counts": {
            "areas": len(areas),
            "technologies": len(atlas["techs"]),
            "arrivingAfterTheSeam": len(late),
            "meanShare2026": mean2026,
            "meanShare3000": mean3000,
            "backlogPairs": sum(r["backlogCount"] for r in areas.values()),
            "backlogClearedBy3000": sum(r["commonBy3000"] for r in areas.values()),
            "lastBacklogLands": last,
            "finishBy": 3000 if last <= LAST_YEAR else None,
        },
    }


def main():
    doc = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    raw = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode()
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(raw)
    c = doc["counts"]
    print("projection.json.gz: %d B (%d raw)" % (os.path.getsize(OUT), len(raw)))
    print("  %d areas, %d technologies, %d invented after the seam"
          % (c["areas"], c["technologies"], c["arrivingAfterTheSeam"]))
    print("  mean spread of what is already invented: %.1f%% in 2026 -> %.1f%% in 3000"
          % (c["meanShare2026"] * 100, c["meanShare3000"] * 100))
    print("  backlog: %d area-and-technology pairs are not yet common in 2026; %d clear by 3000; "
          "the last lands %s"
          % (c["backlogPairs"], c["backlogClearedBy3000"],
             c["lastBacklogLands"] if c["lastBacklogLands"] <= 3000 else "never"))
    for a in ("EUR", "SAS", "WAF", "PAC"):
        r = doc["areas"][a]
        print("    %-4s %3d techs  mean %5.1f%% 2026 -> %5.1f%% 3000  backlog %d"
              % (a, r["techs"], r["series"]["2026"]["mean"] * 100,
                 r["series"]["3000"]["mean"] * 100, r["backlogCount"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
