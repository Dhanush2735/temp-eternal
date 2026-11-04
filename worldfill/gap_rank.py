#!/usr/bin/env python3
"""Rank the states the mod knows but whose ruler it cannot name, by share of the world's people
(HYDE grid), summed over every 50th year from 3000 BC to 2020. Usage: gap_rank.py [out.json]"""
import sys, gzip, json, collections
import numpy as np
sys.path.insert(0, '/home/user/worldfill'); sys.path.insert(0, '/home/user/harvest')
import modpack as M, build_regional as BR, build_polity_facts as PF
hyde = BR.Hyde(); reg = PF.Register()
facts = json.load(gzip.open(f"{M.HISTORY}/polity_facts.json.gz", "rt", encoding="utf-8"))
heads = {p["q"]: p.get("head", []) for p in facts["polities"]}
cells = np.nonzero(hyde.cell >= 0)[0]
lat = -90 + 0.25 + (cells // 720) * 0.5; lon = -180 + 0.25 + (cells % 720) * 0.5
years = list(range(-3000, 2021, 50))
miss = collections.Counter(); nm = {}; yrs = collections.defaultdict(list)
per_year_missing = {}
for y in years:
    ppl = hyde.people(lat, lon, y); tot = ppl.sum()
    m_here = collections.Counter()
    for i in np.nonzero(ppl > 0)[0]:
        pol = reg.at(float(lat[i]), float(lon[i]), y)
        if not pol or not pol[1]: continue
        q = pol[1]
        if not any(r[2] <= y <= r[3] for r in heads.get(q, ())):
            m_here[q] += ppl[i] / tot; nm[q] = pol[0]
    for q, w in m_here.items():
        miss[q] += w; yrs[q].append(y)
    per_year_missing[y] = sum(m_here.values())
tot_missing = sum(miss.values())
out = []
cum = 0
for q, w in miss.most_common(150):
    cum += w
    out.append([q, nm[q], round(100*w/len(years), 3), round(100*cum/tot_missing, 1), len(heads.get(q, ())), min(yrs[q]), max(yrs[q])])
json.dump({"rank": out, "per_year_missing_pct": {y: round(100*v, 1) for y, v in per_year_missing.items()}}, open('/home/user/worldfill/' + (sys.argv[1] if len(sys.argv) > 1 else 'ruler_gaps_now.json') + '', 'w'), indent=0)
for r in out[:90]: print(r)
