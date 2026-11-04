#!/usr/bin/env python3
"""Reviewed batch with strict preflight, stage and reversible pack edits."""
import argparse,copy,gzip,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/2150_2110_bce_context_2026-10.json.gz';STAGE=ROOT/'.cache/r2_storage/2150_2110_stage';W='events_wikipedia.json.gz';R='events_wikipedia_regional.json.gz'; HAZ='events_hazards.json.gz'
# pack, start, exclusive end, latitude, longitude, radius, confidence, qualification
SPEC={'wpy_260a5e939c': ('events_wikipedia.json.gz', -2157, -2143, 31.41139, 46.40722, 50, 'wikipedia_region', 'approximate'), 'wpy_8e54a3a645': ('events_wikipedia.json.gz', -2100, -1999, 31.3259, 45.6374, 160, 'wikipedia_region', 'uncertain'), 'wpy_f90966ad2f': ('events_wikipedia.json.gz', -2116, -2115, 31.3259, 45.6374, 150, 'wikipedia_region', 'uncertain'), 'wpy_3f95a82df6': ('events_wikipedia.json.gz', -2112, -2093, 30.9628, 46.1035, 120, 'wikipedia_region', 'approximate'), 'wpr_8800b2fc4b': ('events_wikipedia_regional.json.gz', -2144, -2123, 31.562028, 46.177583, 50, 'wikipedia_region', 'approximate'), 'wpr_067ab2d1cb': ('events_wikipedia_regional.json.gz', -2124, -2123, 31.41139, 46.40722, 50, 'wikipedia_region', 'disputed'), 'wpr_c4fade4eab': ('events_wikipedia_regional.json.gz', -2120, -2119, 31.562028, 46.177583, 20, 'wikipedia_coord', 'approximate'), 'wpr_1c3c4c7f3e': ('events_wikipedia_regional.json.gz', -2138, -2137, 30.9628, 46.1035, 150, 'wikipedia_region', 'uncertain'), 'r2_la_erabum_sippar_mace_reference': ('events_wikipedia_regional.json.gz', -2150, -2149, 33.058829, 44.252153, 20, 'wikipedia_coord', 'approximate'), 'r2_intef_ii_thebes_reign_context': ('events_wikipedia_regional.json.gz', -2112, -2062, 25.72056, 32.61028, 100, 'wikipedia_region', 'approximate'), 'r2_shimao_mid_22nd_context': ('events_wikipedia_regional.json.gz', -2150, -2109, 38.5657, 110.3252, 20, 'wikipedia_coord', 'approximate'), 'r2_taosi_mid_22nd_context': ('events_wikipedia_regional.json.gz', -2150, -2109, 35.8906028, 111.4971722, 20, 'wikipedia_coord', 'approximate'), 'r2_egypt_first_intermediate_mid_context': ('events_wikipedia_regional.json.gz', -2159, -2109, 29.638, 31.2209, 269, 'wikipedia_region', 'approximate'), 'r2_unetice_mid_22nd_context': ('events_wikipedia_regional.json.gz', -2149, -2099, 50.15, 14.35417, 350, 'wikipedia_region', 'approximate'), 'r2_kerma_mid_22nd_context': ('events_wikipedia_regional.json.gz', -2149, -2099, 19.6008, 30.40973, 60, 'wikipedia_region', 'approximate'), 'r2_caral_mid_22nd_context': ('events_wikipedia_regional.json.gz', -2149, -2099, -10.89361, -77.52028, 20, 'wikipedia_coord', 'approximate'), 'r2_harappan_mid_22nd_context': ('events_wikipedia_regional.json.gz', -2149, -2099, 29.0, 70.5, 400, 'wikipedia_region', 'approximate'), 'hz_f90d76e294': ('events_wikipedia_regional.json.gz', -2150, -2149, 31.1, 35.5, 80, 'noaa_region', 'uncertain')}
NEW={k for k in SPEC if k.startswith('r2_')}
def validate(m):
 if m.get('schema')!='eternal-r2-2150-2110-v1' or len(m['updates'])!=8 or len(m['additions'])!=9 or len(m.get('moves',[]))!=1:raise ValueError('Invalid manifest')
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
    expected=HAZ if id=='hz_f90d76e294' and not reverse else SPEC[id][0]
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
 print(action,'eight corrections, nine additions and one cross-pack correction; atomic per pack, not cross-pack')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
