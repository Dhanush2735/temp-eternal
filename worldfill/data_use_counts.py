#!/usr/bin/env python3
"""Data-use check, part 3: which records can ever reach a player, counted from the data and the rules
the game uses (no Minecraft needed). Writes worldfill/data_use_counts.json.

  - famous people: heard as 'People here talk about' / 'Sad news this year' only while their state is
    on the map in their grown-up years (or the year they die); 'born near here' only with an exact
    birthplace (FamousPeople.BIRTHPLACE_KM = 30)
  - heads of state: named only in years their state is on the map AND they are the latest accession
    (LeaderRegister.Facts.latest); heads of government only in /ee here
  - languages: the first two of a state are said; of the Glottolog list only the 137 major ones
  - faiths: the first faith a state lists (or the measured shares from 1945 on)
"""
import collections
import gzip
import json
import statistics
import sys

sys.path.insert(0, "/home/user/worldfill")
import fact_audit as A  # noqa: E402

OUT = "/home/user/worldfill/data_use_counts.json"


def main():
    pf = A.jload(f"{A.HIST}/polity_facts.json.gz")["polities"]
    mi = A.MapIndex()
    out = {}

    # heads of state: how many rows are ever the one the game names
    total_heads = shown = never_on_map = hidden = 0
    for p in pf:
        ivs = mi.qid_iv.get(p["q"], [])
        heads = p.get("head", [])
        named = set()
        if heads and ivs:
            lo, hi = max(min(r[2] for r in heads), -3500), min(max(r[3] for r in heads), A.NOW)
            for a, b in ivs:
                for y in range(max(a, lo), min(b, hi) + 1):
                    best = None
                    for i, r in enumerate(heads):
                        if r[2] <= y <= r[3] and (best is None or r[2] > heads[best][2]):
                            best = i
                    if best is not None:
                        named.add(best)
        for i, r in enumerate(heads):
            total_heads += 1
            if i in named:
                shown += 1
            elif A.overlap(ivs, r[2], r[3]) == 0:
                never_on_map += 1
            else:
                hidden += 1
    gov = sum(len(p.get("gov", [])) for p in pf)
    out["heads_of_state"] = {"rows": total_heads, "named_in_game": shown,
                             "state_not_on_map_then": never_on_map, "hidden_by_a_later_accession": hidden}
    out["heads_of_government"] = {"rows": gov, "where": "only the /ee here command, never villagers"}

    # languages and faiths
    langs = sum(len(p.get("lang", [])) for p in pf)
    langs_said = sum(min(2, len(p.get("lang", []))) for p in pf if mi.qid_iv.get(p["q"]))
    rels = sum(len(p.get("rel", [])) for p in pf)
    rels_said = sum(1 for p in pf if p.get("rel") and A.shown_faith(p["rel"]) and mi.qid_iv.get(p["q"]))
    shares = sum(1 for p in pf if p.get("relY"))
    ll = A.jload(f"{A.HIST}/local_languages.json.gz")["languages"]
    out["state_languages"] = {"entries": langs, "said_in_game": langs_said}
    out["state_faiths"] = {"entries": rels, "said_in_game": rels_said, "states_with_measured_shares": shares}
    out["peoples_languages"] = {"languages": len(ll), "used_in_talk": sum(1 for x in ll if x[3]),
                                "rule": "nearest major language within 300 km, from AD 1500"}

    # famous people
    rows = A.jload(f"{A.HIST}/famous_people.json.gz")["people"]
    by_state = collections.Counter()
    reach = collections.Counter()
    for name, desc, b, d, q, lat, lon, rad in rows:
        a0 = b + 20 if b is not None else d - 40
        a1 = d if d is not None else b + 70
        talk = bool(q) and A.overlap(mi.qid_iv.get(q, []), a0, a1) > 0
        died = bool(q) and d is not None and A.covers(mi.qid_iv.get(q, []), d)
        born = rad <= 30
        if talk or died:
            reach["through their state"] += 1
        if born:
            reach["born near here (exact birthplace)"] += 1
        if talk or died or born:
            reach["any way"] += 1
        else:
            reach["never"] += 1
        if q:
            by_state[q] += 1
    out["famous_people"] = {"rows": len(rows), **dict(reach)}

    # how many famous people a villager chooses from, at the HYDE-weighted sample points
    pool = collections.defaultdict(list)
    alive = collections.defaultdict(list)
    for name, desc, b, d, q, lat, lon, rad in rows:
        if q:
            a0 = b + 20 if b is not None else d - 40
            a1 = d if d is not None else b + 70
            alive[q].append((a0, a1))
    import build_polity_facts as PF
    import coverage_people as CP
    reg, dec = PF.Register(), CP.Deccan()
    pts = [ln.split("\t") for ln in open("/home/user/.cache/data_use/points.tsv")]
    for y, la, lo in pts[::5]:
        y, la, lo = int(y), float(la), float(lo)
        if y not in (1500, 1800, 1900, 2000):
            continue
        q, _ = A.where(reg, dec, la, lo, y)
        n = sum(1 for a0, a1 in alive.get(q, ()) if a0 <= y <= a1) if q else 0
        pool[y].append(n)
    out["famous_pool_median"] = {str(y): statistics.median(v) for y, v in sorted(pool.items())}

    # events, places
    out["places"] = {"sites": 46864, "reba_cities_with_recorded_populations": 1787,
                     "reba_population_numbers_in_mod": 0}
    json.dump(out, open(OUT, "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
