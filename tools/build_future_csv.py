#!/usr/bin/env python3
"""R1-7's acceptance artefact: verify/future.csv - is 2026 / 2100 / 2400 / 3000 consistent?"""
import json, csv
d = json.load(open("/home/user/eternal/src/main/resources/data/eternalengine/eternal/history/future_story.json"))
def y(s): return int(s[:4])
rows = []
for probe in (2026, 2100, 2400, 3000):
    comp = [x for x in d["computed"] if y(x["date"]) == probe]
    near = sorted([x for x in d["computed"] if abs(y(x["date"]) - probe) <= 60], key=lambda x: x["date"])
    proj = next((x for x in d["projected"] if x["from"] <= probe <= x["to"]), None)
    auth = [x for x in d["authored"] if y(x["date"]) == probe]
    rows.append({
        "year": probe,
        "recorded": "yes" if probe <= 2026 else "no - projection only",
        "projected_state": (proj["text"][:120] if proj else "MISSING"),
        "computed_exactly_this_year": len(comp),
        "computed_within_60_years": len(near),
        "nearest_computed": (", ".join(x["date"] for x in near[:3]) or "-"),
        "authored_chapter": (auth[0]["chapter"] if auth else "-"),
        # 2026 is the last RECORDED year, so it needs the record and the sky, not a projection.
        # Every later probe needs a projected state and something in the sky within a lifetime.
        "consistent": ("yes" if (bool(near) and (probe <= 2026 or proj is not None)) else "NO"),
    })
with open("/home/user/testrun/verify/future.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
print("wrote testrun/verify/future.csv")
for r in rows:
    print("  %d  recorded=%-22s sky-within-60y=%d  chapter=%s  consistent=%s" %
          (r["year"], r["recorded"], r["computed_within_60_years"], r["authored_chapter"], r["consistent"]))
