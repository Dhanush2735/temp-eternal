#!/usr/bin/env python3
"""Reviewed batch with strict preflight, stage and reversible pack edits."""
import argparse,copy,gzip,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/2100_2060_bce_context_2026-10.json.gz';STAGE=ROOT/'.cache/r2_storage/2100_2060_stage';W='events_wikipedia.json.gz';R='events_wikipedia_regional.json.gz'
# pack, start, exclusive end, latitude, longitude, radius, confidence, qualification
SPEC={'wpy_1272829ae3': ('events_wikipedia.json.gz', -2100, -1999, 30.59528, 61.32639, 20, 'wikipedia_coord', 'disputed'), 'wpr_69a1ad91c3': ('events_wikipedia_regional.json.gz', -2070, -2069, 32.6128, 113.5392, 800, 'wikipedia_region', 'uncertain'), 'wpr_55fde6a476': ('events_wikipedia_regional.json.gz', -2100, -2099, 51.17889, -1.82611, 20, 'wikipedia_coord', 'uncertain'), 'wpy_b3aba82c82': ('events_wikipedia.json.gz', -2100, -2049, 52.486222, 60.188278, 200, 'wikipedia_region', 'approximate'), 'wpy_ac82fa6e89': ('events_wikipedia.json.gz', -2099, -2059, 35.30972, 24.89333, 125, 'wikipedia_region', 'approximate'), 'r2_shulgi_ur_reign_context': ('events_wikipedia_regional.json.gz', -2094, -2045, 30.9628, 46.1035, 120, 'wikipedia_region', 'approximate'), 'r2_intef_iii_thebes_reign_context': ('events_wikipedia_regional.json.gz', -2063, -2054, 25.72056, 32.61028, 100, 'wikipedia_region', 'approximate'), 'r2_ur_nammu_code_reference': ('events_wikipedia_regional.json.gz', -2100, -2099, 30.9628, 46.1035, 120, 'wikipedia_region', 'uncertain'), 'r2_ur_ziggurat_reference': ('events_wikipedia_regional.json.gz', -2100, -2099, 30.96278, 46.10306, 20, 'wikipedia_coord', 'uncertain'), 'r2_unetice_early_21st_context': ('events_wikipedia_regional.json.gz', -2099, -2049, 50.15, 14.35417, 350, 'wikipedia_region', 'approximate'), 'r2_kerma_early_21st_context': ('events_wikipedia_regional.json.gz', -2099, -2049, 19.6008, 30.40973, 60, 'wikipedia_region', 'approximate'), 'r2_caral_early_21st_context': ('events_wikipedia_regional.json.gz', -2099, -2049, -10.89361, -77.52028, 20, 'wikipedia_coord', 'approximate'), 'r2_harappan_early_21st_context': ('events_wikipedia_regional.json.gz', -2099, -2049, 29.0, 70.5, 400, 'wikipedia_region', 'approximate'), 'r2_shimao_early_21st_context': ('events_wikipedia_regional.json.gz', -2109, -2059, 38.5657, 110.3252, 20, 'wikipedia_coord', 'approximate'), 'r2_taosi_early_21st_context': ('events_wikipedia_regional.json.gz', -2109, -2059, 35.8906028, 111.4971722, 20, 'wikipedia_coord', 'approximate'), 'r2_egypt_first_intermediate_late_context': ('events_wikipedia_regional.json.gz', -2109, -2059, 29.638, 31.2209, 269, 'wikipedia_region', 'approximate')}
NEW={k for k in SPEC if k.startswith('r2_')}
def validate(m):
 if m.get('schema')!='eternal-r2-2100-2060-v1' or len(m['updates'])!=5 or len(m['additions'])!=11:raise ValueError('Invalid manifest')
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
 print(action,'five corrections and eleven additions; atomic per pack, not cross-pack')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
