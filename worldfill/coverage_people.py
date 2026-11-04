#!/usr/bin/env python3
"""Step 7 recount: for what share of the world's people does the mod know the state and the ruler?

People come from the mod's own HYDE 3.2.1 grid (population/hyde_density.bin.gz, 0.5-degree cells).
For each populated cell and year, the state is looked up the way RulerRegister does it (nearest
register place within 60 km, world_rulers.json.gz plus the finer deccan_rulers.json), and the ruler
from polity_facts.json.gz (a reign covering that year). Also: the share of people with a famous
person of their land alive that year, and with a way-of-life survey answer. Writes
worldfill/coverage_people.json.
"""
import collections, gzip, json, math, os, sys

import numpy as np

sys.path.insert(0, "/home/user/worldfill")
sys.path.insert(0, "/home/user/harvest")
import modpack as M  # noqa: E402
import build_regional as BR  # noqa: E402
import build_polity_facts as PF  # noqa: E402

OUT = "/home/user/worldfill/coverage_people.json"
YEARS = [-2500, -1500, -500, 1, 500, 1000, 1300, 1500, 1700, 1850, 1900, 1950, 2000, 2020]


class Deccan:
    """The finer two-level register for the Deccan, as RulerRegister merges it with the world one."""

    def __init__(self):
        d = json.load(open(f"{M.HISTORY}/deccan_rulers.json", encoding="utf-8"))
        self.tls = [[(s["name"], s["start"], s["end"], s.get("wikidata")) for s in t] for t in d["timelines"]]
        self.pl = [(p["lat"], p["lon"], p["timeline"]) for p in d["places"]]
        self.grid = collections.defaultdict(list)
        for i, (la, lo, _t) in enumerate(self.pl):
            self.grid[(math.floor((la + 90) / 0.5), math.floor((lo + 180) / 0.5))].append(i)

    def nearest(self, la, lo):
        best, bkm = None, 1e9
        cy, cx = math.floor((la + 90) / 0.5), math.floor((lo + 180) / 0.5)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                for i in self.grid.get((cy + dy, cx + dx), ()):
                    p = self.pl[i]
                    mid = math.radians((la + p[0]) / 2)
                    d = math.hypot((la - p[0]) * 110.57, (lo - p[1]) * 110.57 * math.cos(mid))
                    if d < bkm:
                        best, bkm = i, d
        return (best, bkm) if best is not None else (None, 1e9)


def main():
    hyde = BR.Hyde()
    reg = PF.Register()
    dec = Deccan()
    facts = json.load(gzip.open(f"{M.HISTORY}/polity_facts.json.gz", "rt", encoding="utf-8"))
    heads = {p["q"]: p.get("head", []) for p in facts["polities"]}
    people_rows = json.load(gzip.open(f"{M.HISTORY}/famous_people.json.gz", "rt", encoding="utf-8"))["people"]
    alive_by_state = collections.defaultdict(list)
    for r in people_rows:
        b, d, q = r[2], r[3], r[4]
        if q:
            a0 = b + 20 if b is not None else d - 40
            a1 = d if d is not None else b + 70
            alive_by_state[q].append((a0, a1))
    cells = np.nonzero(hyde.cell >= 0)[0]
    lat = -90 + 0.25 + (cells // 720) * 0.5
    lon = -180 + 0.25 + (cells % 720) * 0.5
    out = {}
    for y in YEARS:
        ppl = hyde.people(lat, lon, y)
        total = float(ppl.sum())
        known = named = famous = 0.0
        for i in np.nonzero(ppl > 0)[0]:
            la, lo, w = float(lat[i]), float(lon[i]), float(ppl[i])
            q = None
            pol = reg.at(la, lo, y)
            # the Deccan register wins where its place is nearer (both are merged in one grid in the mod)
            di, dkm = dec.nearest(la, lo)
            if di is not None and dkm <= 60:
                wkm = None
                for t in dec.tls[dec.pl[di][2]]:
                    if t[1] <= y <= t[2]:
                        q = t[3]
                        break
            if q is None and pol:
                q = pol[1]
            if not q:
                continue
            known += w
            if any(r[2] <= y <= r[3] for r in heads.get(q, ())):
                named += w
            if any(a0 <= y <= a1 for a0, a1 in alive_by_state.get(q, ())):
                famous += w
        out[str(y)] = {"people_millions": round(total / 1e6, 1),
                       "state_known_pct": round(100 * known / total, 1) if total else None,
                       "ruler_named_pct": round(100 * named / total, 1) if total else None,
                       "famous_person_of_the_land_pct": round(100 * famous / total, 1) if total else None}
        print(y, out[str(y)], flush=True)
    json.dump(out, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    main()
