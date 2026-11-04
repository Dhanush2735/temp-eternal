#!/usr/bin/env python3
"""Reviewed batch with strict preflight, stage and reversible pack edits."""
import argparse,copy,gzip,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/1900_1860_bce_context_2026-10.json.gz';STAGE=ROOT/'.cache/r2_storage/1900_1860_stage';W='events_wikipedia.json.gz';R='events_wikipedia_regional.json.gz'
# pack, start, exclusive end, latitude, longitude, radius, confidence, qualification
SPEC={'wpy_d63fc48c19': ('events_wikipedia.json.gz', -1900, -1899, 37.7, 22.8, 200, 'wikipedia_region', 'uncertain'), 'wpy_6723ffdf8c': ('events_wikipedia.json.gz', -1900, -1899, 31.885, 45.26861, 150, 'wikipedia_region', 'uncertain'), 'wpy_ea8afd288e': ('events_wikipedia.json.gz', -1917, -1916, 29.65, 91.1, 300, 'wikipedia_region', 'uncertain'), 'wpy_05fa69a828': ('events_wikipedia.json.gz', -1900, -1899, 29.65, 91.1, 300, 'wikipedia_region', 'uncertain'), 'wpy_f64f2c0f1d': ('events_wikipedia.json.gz', -1860, -1859, 21.5, 30.97, 180, 'wikipedia_region', 'uncertain'), 'wpr_91175f45ba': ('events_wikipedia_regional.json.gz', -1900, -1699, 14.85, -92.45, 100, 'wikipedia_region', 'uncertain'), 'wpr_d6410a49ca': ('events_wikipedia_regional.json.gz', -1900, -1499, 14.85, -92.45, 60, 'wikipedia_region', 'uncertain'), 'wpr_8be6d9e6fa': ('events_wikipedia_regional.json.gz', -1900, -1899, 22.52139, 72.24944, 20, 'wikipedia_coord', 'uncertain'), 'wpr_f647e86f4d': ('events_wikipedia_regional.json.gz', -2008, -1973, 35.45667, 43.2625, 60, 'wikipedia_region', 'uncertain'), 'wpr_4d8aee1120': ('events_wikipedia_regional.json.gz', -1887, -1877, 29.23333, 30.96667, 60, 'wikipedia_region', 'uncertain'), 'r2_puzur_ashur_ii_assur_reign_context': ('events_wikipedia_regional.json.gz', -1881, -1872, 35.45667, 43.2625, 100, 'wikipedia_region', 'uncertain'), 'r2_naram_sin_assur_reign_context': ('events_wikipedia_regional.json.gz', -1873, -1822, 35.45667, 43.2625, 100, 'wikipedia_region', 'uncertain'), 'r2_bur_suen_isin_reign_context': ('events_wikipedia_regional.json.gz', -1896, -1873, 31.885, 45.26861, 100, 'wikipedia_region', 'uncertain'), 'r2_lipit_enlil_isin_reign_context': ('events_wikipedia_regional.json.gz', -1874, -1867, 31.885, 45.26861, 100, 'wikipedia_region', 'uncertain'), 'r2_erra_imitti_isin_reign_context': ('events_wikipedia_regional.json.gz', -1868, -1860, 31.885, 45.26861, 100, 'wikipedia_region', 'uncertain'), 'r2_enlil_bani_isin_reign_context': ('events_wikipedia_regional.json.gz', -1860, -1835, 31.885, 45.26861, 100, 'wikipedia_region', 'uncertain'), 'r2_sumuel_larsa_reign_context': ('events_wikipedia_regional.json.gz', -1895, -1865, 31.28583, 45.85361, 100, 'wikipedia_region', 'uncertain'), 'r2_nur_adad_larsa_reign_context': ('events_wikipedia_regional.json.gz', -1866, -1849, 31.28583, 45.85361, 100, 'wikipedia_region', 'uncertain'), 'r2_sithathoriunet_pectoral_lahun_reference': ('events_wikipedia_regional.json.gz', -1887, -1877, 29.23333, 30.96667, 20, 'wikipedia_region', 'uncertain'), 'r2_erlitou_chronology_1900_reference': ('events_wikipedia_regional.json.gz', -1900, -1899, 34.6925, 112.69, 100, 'wikipedia_region', 'uncertain')}
NEW={k for k in SPEC if k.startswith('r2_')}
def validate(m):
 if m.get('schema')!='eternal-r2-1900-1860-v1' or len(m['updates'])!=10 or len(m['additions'])!=10:raise ValueError('Invalid manifest')
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
 print(action,'ten corrections and ten additions; atomic per pack, not cross-pack')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
