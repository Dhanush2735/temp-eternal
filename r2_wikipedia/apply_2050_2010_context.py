#!/usr/bin/env python3
"""Reviewed batch with strict preflight, stage and reversible pack edits."""
import argparse,copy,gzip,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/2050_2010_bce_context_2026-10.json.gz';STAGE=ROOT/'.cache/r2_storage/2050_2010_stage';W='events_wikipedia.json.gz';R='events_wikipedia_regional.json.gz'; HAZ='events_hazards.json.gz'
# pack, start, exclusive end, latitude, longitude, radius, confidence, qualification
SPEC={'wpy_db8ab9c63c': ('events_wikipedia.json.gz', -2050, -2049, 19.6008, 30.40973, 60, 'wikipedia_region', 'approximate'), 'wpy_4b64c0191c': ('events_wikipedia.json.gz', -2049, -2048, 52.96806, 0.52139, 20, 'wikipedia_coord', 'inference'), 'wpy_18f39f0412': ('events_wikipedia.json.gz', -2040, -2039, 25.72056, 32.61028, 150, 'wikipedia_region', 'uncertain'), 'wpr_2926aea3f7': ('events_wikipedia_regional.json.gz', -2040, -2039, 30.2081, 31.071, 174, 'wikipedia_region', 'uncertain'), 'wpr_38d204150e': ('events_wikipedia_regional.json.gz', -2025, -2003, 31.28583, 45.85361, 80, 'wikipedia_region', 'disputed'), 'wpr_fe6d5b677f': ('events_wikipedia_regional.json.gz', -2018, -1984, 31.885, 45.26861, 80, 'wikipedia_region', 'approximate'), 'wpr_5605a9718a': ('events_wikipedia_regional.json.gz', -2055, -2003, 25.72056, 32.61028, 150, 'wikipedia_region', 'approximate'), 'r2_amar_sin_ur_reign_context': ('events_wikipedia_regional.json.gz', -2046, -2036, 30.9628, 46.1035, 120, 'wikipedia_region', 'approximate'), 'r2_shu_sin_ur_reign_context': ('events_wikipedia_regional.json.gz', -2037, -2027, 30.9628, 46.1035, 120, 'wikipedia_region', 'approximate'), 'r2_ibbi_sin_ur_reign_context': ('events_wikipedia_regional.json.gz', -2028, -2003, 30.9628, 46.1035, 120, 'wikipedia_region', 'approximate'), 'r2_unetice_mid_21st_context': ('events_wikipedia_regional.json.gz', -2049, -1999, 50.15, 14.35417, 350, 'wikipedia_region', 'approximate'), 'r2_caral_mid_21st_context': ('events_wikipedia_regional.json.gz', -2049, -1999, -10.89361, -77.52028, 20, 'wikipedia_coord', 'approximate'), 'r2_harappan_mid_21st_context': ('events_wikipedia_regional.json.gz', -2049, -1999, 29.0, 70.5, 400, 'wikipedia_region', 'approximate'), 'r2_shimao_mid_21st_context': ('events_wikipedia_regional.json.gz', -2059, -2009, 38.5657, 110.3252, 20, 'wikipedia_coord', 'approximate'), 'r2_taosi_mid_21st_context': ('events_wikipedia_regional.json.gz', -2059, -2009, 35.8906028, 111.4971722, 20, 'wikipedia_coord', 'approximate'), 'r2_minoan_mm_ia_mid_21st_context': ('events_wikipedia_regional.json.gz', -2059, -2009, 35.30972, 24.89333, 125, 'wikipedia_region', 'approximate'), 'r2_sintashta_mid_21st_context': ('events_wikipedia_regional.json.gz', -2049, -1999, 52.486222, 60.188278, 200, 'wikipedia_region', 'approximate'), 'hz_8c3e8bede6': ('events_wikipedia_regional.json.gz', -2050, -2049, 33.361, 126.53, 40, 'gvp_region', 'uncertain')}
NEW={k for k in SPEC if k.startswith('r2_')}
def validate(m):
 if m.get('schema')!='eternal-r2-2050-2010-v1' or len(m['updates'])!=7 or len(m['additions'])!=10 or len(m.get('moves',[]))!=1:raise ValueError('Invalid manifest')
 entries=[(x['pack'],x['event_id'],x['after']) for x in m['updates']]+[(x['pack'],x['event']['id'],x['event']) for x in m['additions']]+[(x['to_pack'],x['event_id'],x['after']) for x in m['moves']]
 if {id for p,id,e in entries}!=set(SPEC) or {x['event']['id'] for x in m['additions']}!=NEW:raise ValueError('Wrong IDs')
 for pack,id,e in entries:
  p,st,en,lat,lon,rad,conf,qual=SPEC[id]
  if (pack,e['start'],e['end'],e['lat'],e['lon'],e['radiusKm'],e['kind'],e['effect'],e['confidence'])!=(p,st,en,lat,lon,rad,'cultural','note',conf) or qual not in e['name'] or len(e['r2SourceEvidence']['sources'])<3:raise ValueError('Invalid '+id)
 for u in m['updates']+m['moves']:
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
 for move in m['moves']:
  src,dst=(move['to_pack'],move['from_pack']) if reverse else (move['from_pack'],move['to_pack'])
  old,new=(move['after'],move['before']) if reverse else (move['before'],move['after'])
  hits=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==move['event_id']]
  if pack==src:
   if len(hits)!=1 or rows[hits[0]]!=old:raise ValueError('Missing/changed move source')
   del rows[hits[0]]
  elif pack==dst:
   if hits:raise ValueError('Duplicate move target')
   rows.insert(move['source_index'],copy.deepcopy(new)) if reverse else rows.append(copy.deepcopy(new))
 return o
def check_index(reverse):
 packs=json.loads((H/'index.json').read_text())['packs'];counts={i:0 for i in SPEC}
 if not {W,R,HAZ}.issubset(packs):raise ValueError('Not indexed')
 for p in packs:
  with (gzip.open(H/p,'rt',encoding='utf8') if p.endswith('.gz') else open(H/p,encoding='utf8')) as f:d=json.load(f)
  for sec in ('events','sites'):
   for r in d.get(sec,[]):
    if not isinstance(r,dict) or r.get('id') not in SPEC:continue
    id=r['id']
    expected=HAZ if id=='hz_8c3e8bede6' and not reverse else SPEC[id][0]
    if (p,sec)!=(expected,'events'):raise ValueError('Shared ID '+id)
    counts[id]+=1
 for id,n in counts.items():
  if n!=(0 if id in NEW and not reverse else 1):raise ValueError('Wrong count '+id)
def run(action):
 m=json.load(gzip.open(M,'rt',encoding='utf8'));validate(m);rev=action=='rollback';check_index(rev);outputs={}
 for p in (W,R,HAZ):
  with gzip.open(H/p,'rt',encoding='utf8') as f:doc=json.load(f)
  out=transform(doc,m,p,rev)
  if transform(out,m,p,not rev)!=doc:raise ValueError('Roundtrip')
  outputs[p]=out
 for p,d in outputs.items():write_atomic_gzip((STAGE if action=='stage' else H)/p,d)
 print(action,'seven corrections, ten additions and one cross-pack correction; atomic per pack, not cross-pack')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
