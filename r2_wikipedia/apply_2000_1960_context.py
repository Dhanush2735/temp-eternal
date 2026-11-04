#!/usr/bin/env python3
"""Reviewed batch with strict preflight, stage and reversible pack edits."""
import argparse,copy,gzip,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/2000_1960_bce_context_2026-10.json.gz';STAGE=ROOT/'.cache/r2_storage/2000_1960_stage';W='events_wikipedia.json.gz';R='events_wikipedia_regional.json.gz'
# pack, start, exclusive end, latitude, longitude, radius, confidence, qualification
SPEC={'wpy_ea791ce370': ('events_wikipedia.json.gz', -2000, -1999, 17.4069, 103.2414, 20, 'wikipedia_coord', 'disputed'), 'wpy_7ccff70f11': ('events_wikipedia.json.gz', -2000, -1999, 19.28167, -103.69111, 80, 'wikipedia_region', 'disputed'), 'wpy_41cdea47a8': ('events_wikipedia.json.gz', -2100, -1999, 21.53083, -105.24722, 40, 'wikipedia_region', 'approximate'), 'wpy_83ad4a8bc1': ('events_wikipedia.json.gz', -2000, -1999, 45.15639, 10.79111, 30, 'wikipedia_region', 'uncertain'), 'wpy_bc4e70f65a': ('events_wikipedia.json.gz', -1900, -1899, 35.29806, 25.16306, 20, 'wikipedia_coord', 'approximate'), 'wpy_b3f29630bb': ('events_wikipedia.json.gz', -2000, -1949, 36.0, 138.0, 500, 'wikipedia_region', 'approximate'), 'wpy_d167a8b1bd': ('events_wikipedia.json.gz', -1999, -1949, 29.0, 70.5, 400, 'wikipedia_region', 'approximate'), 'wpy_bb2fcab9b5': ('events_wikipedia.json.gz', -2000, -1999, 30.62889, 72.86389, 20, 'wikipedia_coord', 'disputed'), 'wpy_932aed2f28': ('events_wikipedia.json.gz', -2000, -1899, 27.32917, 68.13889, 20, 'wikipedia_coord', 'speculative'), 'wpy_fc667305b9': ('events_wikipedia.json.gz', -2000, -1999, 51.17889, -1.82611, 20, 'wikipedia_coord', 'uncertain'), 'wpy_a55af1230d': ('events_wikipedia.json.gz', -2000, -1999, 18.2014, 121.664, 60, 'wikipedia_region', 'uncertain'), 'wpy_24012ebb6a': ('events_wikipedia.json.gz', -2000, -1999, 48.0, 44.0, 400, 'wikipedia_region', 'disputed'), 'wpy_ead68c6855': ('events_wikipedia.json.gz', -2000, -1999, 40.18, 44.51, 250, 'wikipedia_region', 'disputed'), 'wpr_aa0d9f56b9': ('events_wikipedia_regional.json.gz', -2000, -1999, 71.233, -179.417, 100, 'wikipedia_region', 'uncertain'), 'wpr_e1dba9658f': ('events_wikipedia_regional.json.gz', -2000, -1999, 27.93139, 30.87528, 20, 'wikipedia_coord', 'approximate'), 'wpr_8dd3b24345': ('events_wikipedia_regional.json.gz', -1981, -1951, 29.569, 31.225, 150, 'wikipedia_region', 'approximate'), 'wpy_daf6a957ed': ('events_wikipedia.json.gz', -1974, -1934, 35.45667, 43.2625, 100, 'wikipedia_region', 'approximate'), 'r2_mentuhotep_iii_reign_context': ('events_wikipedia_regional.json.gz', -2009, -1996, 25.72056, 32.61028, 150, 'wikipedia_region', 'approximate'), 'r2_mentuhotep_iv_reign_context': ('events_wikipedia_regional.json.gz', -1997, -1990, 25.72056, 32.61028, 150, 'wikipedia_region', 'approximate'), 'r2_shu_ilishu_isin_reign_context': ('events_wikipedia_regional.json.gz', -1985, -1974, 31.885, 45.26861, 80, 'wikipedia_region', 'approximate'), 'r2_iddin_dagan_isin_reign_context': ('events_wikipedia_regional.json.gz', -1975, -1953, 31.885, 45.26861, 80, 'wikipedia_region', 'approximate'), 'r2_unetice_early_20th_context': ('events_wikipedia_regional.json.gz', -1999, -1949, 50.15, 14.35417, 350, 'wikipedia_region', 'approximate'), 'r2_caral_early_20th_context': ('events_wikipedia_regional.json.gz', -1999, -1949, -10.89361, -77.52028, 20, 'wikipedia_coord', 'approximate'), 'r2_sintashta_early_20th_context': ('events_wikipedia_regional.json.gz', -1999, -1949, 52.486222, 60.188278, 200, 'wikipedia_region', 'approximate'), 'r2_kerma_early_20th_context': ('events_wikipedia_regional.json.gz', -1999, -1949, 19.6008, 30.40973, 60, 'wikipedia_region', 'approximate'), 'r2_shimao_early_20th_context': ('events_wikipedia_regional.json.gz', -2009, -1959, 38.5657, 110.3252, 20, 'wikipedia_coord', 'approximate'), 'r2_taosi_early_20th_context': ('events_wikipedia_regional.json.gz', -2009, -1959, 35.8906028, 111.4971722, 20, 'wikipedia_coord', 'approximate'), 'r2_minoan_mm_ia_early_20th_context': ('events_wikipedia_regional.json.gz', -2009, -1959, 35.30972, 24.89333, 125, 'wikipedia_region', 'approximate')}
NEW={k for k in SPEC if k.startswith('r2_')}
def validate(m):
 if m.get('schema')!='eternal-r2-2000-1960-v1' or len(m['updates'])!=17 or len(m['additions'])!=11:raise ValueError('Invalid manifest')
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
 print(action,'seventeen corrections and eleven additions; atomic per pack, not cross-pack')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
