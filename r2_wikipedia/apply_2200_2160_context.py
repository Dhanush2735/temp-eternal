#!/usr/bin/env python3
"""Reviewed batch with strict preflight, stage and reversible pack edits."""
import argparse,copy,gzip,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/2200_2160_bce_context_2026-10.json.gz';STAGE=ROOT/'.cache/r2_storage/2200_2160_stage';W='events_wikipedia.json.gz';R='events_wikipedia_regional.json.gz'
# pack, start, exclusive end, latitude, longitude, radius, confidence, qualification
SPEC={'wpy_86773360e4': ('events_wikipedia.json.gz', -1981, -1974, 25.72056, 32.61028, 20, 'wikipedia_coord', 'uncertain'), 'wpy_940174a93b': ('events_wikipedia.json.gz', -2180, -2179, 32.0, 45.5, 200, 'wikipedia_region', 'disputed'), 'wpy_5f9d4d075d': ('events_wikipedia.json.gz', -2200, -2099, 35.30972, 24.89333, 125, 'wikipedia_region', 'approximate'), 'wpy_0634475c07': ('events_wikipedia.json.gz', -2215, -2214, 32.0, 45.5, 200, 'wikipedia_region', 'uncertain'), 'wpy_f59927a322': ('events_wikipedia.json.gz', -2218, -2217, -16.0, 135.0, 500, 'wikipedia_region', 'disputed'), 'wpr_2adae19fb6': ('events_wikipedia_regional.json.gz', -2200, -2199, 20.58, 121.9, 60, 'wikipedia_region', 'uncertain'), 'wpr_3a2c69b220': ('events_wikipedia_regional.json.gz', -2184, -2183, 30.2081, 31.071, 174, 'wikipedia_region', 'disputed'), 'wpr_aed4025ed4': ('events_wikipedia_regional.json.gz', -2184, -2183, 30.2081, 31.071, 174, 'wikipedia_region', 'disputed'), 'wpr_cb322cff15': ('events_wikipedia_regional.json.gz', -2184, -2180, 30.2081, 31.071, 174, 'wikipedia_region', 'uncertain'), 'wpr_2b5590fdef': ('events_wikipedia_regional.json.gz', -2160, -2159, 30.2081, 31.071, 174, 'wikipedia_region', 'uncertain'), 'r2_mawmluh_4_2ka_climate_context': ('events_wikipedia_regional.json.gz', -2200, -2099, 25.2622, 91.715, 50, 'wikipedia_coord', 'uncertain'), 'r2_egypt_first_intermediate_early_context': ('events_wikipedia_regional.json.gz', -2181, -2159, 29.638, 31.2209, 269, 'wikipedia_region', 'one chronology'), 'r2_shu_turul_akkad_reign_context': ('events_wikipedia_regional.json.gz', -2168, -2153, 32.0, 45.5, 200, 'wikipedia_region', 'approximate'), 'r2_unetice_early_22nd_context': ('events_wikipedia_regional.json.gz', -2199, -2149, 50.15, 14.35417, 350, 'wikipedia_region', 'approximate'), 'r2_kerma_early_22nd_context': ('events_wikipedia_regional.json.gz', -2199, -2149, 19.6008, 30.40973, 60, 'wikipedia_region', 'approximate'), 'r2_caral_early_22nd_context': ('events_wikipedia_regional.json.gz', -2199, -2149, -10.89361, -77.52028, 20, 'wikipedia_coord', 'approximate'), 'r2_harappan_early_22nd_context': ('events_wikipedia_regional.json.gz', -2199, -2149, 29.0, 70.5, 400, 'wikipedia_region', 'approximate'), 'r2_dudu_akkad_reign_context': ('events_wikipedia_regional.json.gz', -2189, -2167, 32.0, 45.5, 200, 'wikipedia_region', 'approximate')}
NEW={k for k in SPEC if k.startswith('r2_')}
def validate(m):
 if m.get('schema')!='eternal-r2-2200-2160-v1' or len(m['updates'])!=10 or len(m['additions'])!=8:raise ValueError('Invalid manifest')
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
 print(action,'ten corrections and eight additions; atomic per pack, not cross-pack')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
