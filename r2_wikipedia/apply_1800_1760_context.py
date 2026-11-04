#!/usr/bin/env python3
"""Reviewed batch with strict preflight, stage and reversible pack edits."""
import argparse,copy,gzip,json,hashlib
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/1800_1760_bce_context_2026-10.json.gz';STAGE=ROOT/'.cache/r2_storage/1800_1760_stage';W='events_wikipedia.json.gz';R='events_wikipedia_regional.json.gz'
# pack, start, exclusive end, latitude, longitude, radius, confidence, qualification
SPEC={'wpy_92aac72359': ('events_wikipedia.json.gz', -1800, -1799, 56.2, 12.5, 400, 'wikipedia_region', 'uncertain'), 'wpy_ad932b5f42': ('events_wikipedia.json.gz', -1800, -1799, 30.786, 31.83, 100, 'wikipedia_region', 'uncertain'), 'wpy_6d5948e754': ('events_wikipedia.json.gz', -905, -904, 8.6279, 77.8732, 20, 'wikipedia_coord', 'uncertain'), 'wpy_60ea454f72': ('events_wikipedia.json.gz', -1800, -1699, 29.0, 70.5, 400, 'wikipedia_region', 'uncertain'), 'wpy_31c9e8ca1e': ('events_wikipedia.json.gz', -1770, -1769, 32.5425, 44.42111, 20, 'wikipedia_coord', 'uncertain'), 'wpy_5c2c59b982': ('events_wikipedia.json.gz', -1808, -1807, 35.45667, 43.2625, 100, 'wikipedia_region', 'uncertain'), 'wpr_641ca1c7e8': ('events_wikipedia_regional.json.gz', -1700, -1699, 39.9575, 26.23889, 20, 'wikipedia_coord', 'uncertain'), 'wpr_a2ee764345': ('events_wikipedia_regional.json.gz', -1792, -1749, 32.5425, 44.42111, 120, 'wikipedia_region', 'uncertain'), 'wpr_2fc4812558': ('events_wikipedia_regional.json.gz', -1775, -1760, 34.54944, 40.89, 100, 'wikipedia_region', 'uncertain'), 'r2_sin_muballit_babylon_1800_context': ('events_wikipedia_regional.json.gz', -1813, -1791, 32.5425, 44.42111, 100, 'wikipedia_region', 'uncertain'), 'r2_damiq_ilishu_isin_1800_context': ('events_wikipedia_regional.json.gz', -1814, -1791, 31.885, 45.26861, 100, 'wikipedia_region', 'uncertain'), 'r2_shamshi_adad_1800_reign_context': ('events_wikipedia_regional.json.gz', -1809, -1775, 35.45667, 43.2625, 150, 'wikipedia_region', 'uncertain'), 'r2_shibtu_mari_1770_context': ('events_wikipedia_regional.json.gz', -1773, -1760, 34.54944, 40.89, 100, 'wikipedia_region', 'uncertain'), 'r2_mari_investiture_mural_reference': ('events_wikipedia_regional.json.gz', -1775, -1760, 34.54944, 40.89, 20, 'wikipedia_coord', 'uncertain'), 'r2_sechin_alto_1800_context': ('events_wikipedia_regional.json.gz', -1800, -1759, -9.4654, -78.2426, 20, 'wikipedia_coord', 'uncertain'), 'r2_kultepe_1800_karum_context': ('events_wikipedia_regional.json.gz', -1800, -1759, 38.8536, 35.6333, 20, 'wikipedia_coord', 'uncertain'), 'r2_valdivia_1800_context': ('events_wikipedia_regional.json.gz', -1800, -1759, -1.95, -80.72, 100, 'wikipedia_region', 'uncertain'), 'r2_early_maya_region_1800_reference': ('events_wikipedia_regional.json.gz', -1800, -1799, 16.5, -90.5, 250, 'wikipedia_region', 'uncertain')}
NEW={k for k in SPEC if k.startswith('r2_')}
def validate(m):
 if hashlib.sha256(json.dumps(m,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()!='2e7cc96d07339daa75f01363f6b0afd653d096b37a5d32759631a3b459eb20e0':raise ValueError('Manifest differs from approved review')
 if m.get('schema')!='eternal-r2-1800-1760-v1' or len(m['updates'])!=9 or len(m['additions'])!=9:raise ValueError('Invalid manifest')
 entries=[(x['pack'],x['event_id'],x['after']) for x in m['updates']]+[(x['pack'],x['event']['id'],x['event']) for x in m['additions']]
 if {id for p,id,e in entries}!=set(SPEC) or {x['event']['id'] for x in m['additions']}!=NEW:raise ValueError('Wrong IDs')
 for pack,id,e in entries:
  p,st,en,lat,lon,rad,conf,qual=SPEC[id]
  if (pack,e['start'],e['end'],e['lat'],e['lon'],e['radiusKm'],e['kind'],e['effect'],e['confidence'])!=(p,st,en,lat,lon,rad,'cultural','note',conf) or qual not in e['name'] or len(e['r2SourceEvidence']['sources'])<3:raise ValueError('Invalid '+id)
 for u in m['updates']:
  b,a=u['before'],u['after']
  if b['id']!=u['event_id'] or a['id']!=u['event_id'] or set(a)!=set(b)|{'r2SourceEvidence'} or {k for k in b if a[k]!=b[k]}-{'name','start','end','lat','lon','radiusKm','kind','effect','confidence'}:raise ValueError('Unexpected change')
def transform(doc,m,pack,reverse=False):
 validate(m);o=copy.deepcopy(doc);rows=o.get('events')
 if not isinstance(rows,list):raise ValueError('No events')
 for u in (x for x in m['updates'] if x['pack']==pack):
  old,new=(u['after'],u['before']) if reverse else (u['before'],u['after']);hits=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==u['event_id']]
  if len(hits)!=1 or rows[hits[0]]!=old:raise ValueError('Missing/changed '+u['event_id'])
  rows[hits[0]]=copy.deepcopy(new)
 for a in (x for x in m['additions'] if x['pack']==pack):
  e=a['event'];hits=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==e['id']]
  if reverse:
   if len(hits)!=1 or rows[hits[0]]!=e:raise ValueError('Missing/changed addition '+e['id'])
   del rows[hits[0]]
  else:
   if hits:raise ValueError('Duplicate ID '+e['id'])
   rows.append(copy.deepcopy(e))
 return o
def check_index(reverse):
 packs=json.loads((H/'index.json').read_text())['packs'];counts={i:0 for i in SPEC}
 if not {W,R}.issubset(packs):raise ValueError('Not indexed')
 for p in packs:
  with (gzip.open(H/p,'rt',encoding='utf8') if p.endswith('.gz') else open(H/p,encoding='utf8')) as f:d=json.load(f)
  for sec in ('events','sites'):
   for r in d.get(sec,[]):
    if not isinstance(r,dict) or r.get('id') not in SPEC:continue
    id=r['id']
    if (p,sec)!=(SPEC[id][0],'events'):raise ValueError('Shared ID '+id)
    counts[id]+=1
 for id,n in counts.items():
  if n!=(0 if id in NEW and not reverse else 1):raise ValueError('Wrong count '+id)
def run(action):
 m=json.load(gzip.open(M,'rt',encoding='utf8'));validate(m);rev=action=='rollback';check_index(rev);outputs={}
 for p in (W,R):
  with gzip.open(H/p,'rt',encoding='utf8') as f:doc=json.load(f)
  out=transform(doc,m,p,rev)
  if transform(out,m,p,not rev)!=doc:raise ValueError('Roundtrip')
  outputs[p]=out
 for p,d in outputs.items():write_atomic_gzip((STAGE if action=='stage' else H)/p,d)
 print(action,'nine corrections and nine additions; atomic per pack, not cross-pack')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
