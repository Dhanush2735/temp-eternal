#!/usr/bin/env python3
"""Guarded corrections to reviewed records; writes atomic per pack only."""
import argparse,copy,gzip,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/2650_2610_bce_context_2026-10.json';STAGE=ROOT/'.cache/r2_storage/2650_2610_stage'
W='events_wikipedia.json.gz';R='events_wikipedia_regional.json.gz'
# id: pack,start,end,latitude,longitude,radius,confidence,required qualification
SPEC={'wpy_92a5ef9fcd':(W,-2650,-2649,23.88611,70.21667,20,'wikipedia_coord','dating debated'), 'wpy_caae285631':(W,-2750,-2599,32.0,45.5,250,'wikipedia_region','period debated'), 'wpr_2163f58b67':(R,-2650,-2649,32.12644,45.23338,20,'wikipedia_coord','dating and function uncertain'), 'wpr_688f334891':(R,-2650,-2649,29.638,31.2209,269,'wikipedia_region','evidence and dating uncertain'), 'wpr_2dc753b8b2':(R,-2613,-2497,29.638,31.2209,269,'wikipedia_region','dates debated')}
def validate(m):
 if m.get('schema')!='eternal-r2-2650-2610-v1' or len(m['updates'])!=len(SPEC) or {u['event_id'] for u in m['updates']}!=set(SPEC):raise ValueError('Invalid manifest')
 for u in m['updates']:
  id=u['event_id'];b,a=u['before'],u['after'];pack,st,en,lat,lon,rad,conf,qual=SPEC[id]
  if u['pack']!=pack or b['id']!=id or a['id']!=id or (a['start'],a['end'],a['lat'],a['lon'],a['radiusKm'],a['kind'],a['effect'],a['confidence'])!=(st,en,lat,lon,rad,'cultural','note',conf) or qual not in a['name'] or len(a['r2SourceEvidence']['sources'])<3:raise ValueError('Invalid event '+id)
  if set(a)!=set(b)|{'r2SourceEvidence'} or {k for k in b if a[k]!=b[k]}-{'name','start','end','lat','lon','radiusKm','kind','effect','confidence'}:raise ValueError('Unexpected change '+id)
def transform(doc,m,pack,reverse=False):
 validate(m);out=copy.deepcopy(doc);rows=out.get('events')
 if not isinstance(rows,list):raise ValueError('Missing events')
 for u in (x for x in m['updates'] if x['pack']==pack):
  old,new=(u['after'],u['before']) if reverse else (u['before'],u['after']);hits=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==u['event_id']]
  if len(hits)!=1 or rows[hits[0]]!=old:raise ValueError('Missing or changed '+u['event_id'])
  rows[hits[0]]=copy.deepcopy(new)
 return out
def check_index():
 packs=json.loads((H/'index.json').read_text())['packs'];counts={id:0 for id in SPEC}
 if not {W,R}.issubset(packs):raise ValueError('Pack unindexed')
 for pack in packs:
  with (gzip.open(H/pack,'rt',encoding='utf8') if pack.endswith('.gz') else open(H/pack,encoding='utf8')) as f:d=json.load(f)
  for sec in ('events','sites'):
   for r in d.get(sec,[]):
    if not isinstance(r,dict) or r.get('id') not in SPEC:continue
    id=r['id']
    if (pack,sec)!=(SPEC[id][0],'events'):raise ValueError('Shared id '+id)
    counts[id]+=1
 if any(n!=1 for n in counts.values()):raise ValueError('Missing/duplicate ID')
def run(action):
 m=json.loads(M.read_text());validate(m);check_index();out={};rev=action=='rollback'
 for p in (W,R):
  with gzip.open(H/p,'rt',encoding='utf8') as f:doc=json.load(f)
  result=transform(doc,m,p,rev)
  if transform(result,m,p,not rev)!=doc:raise ValueError('Roundtrip failed')
  out[p]=result
 for p,d in out.items():write_atomic_gzip((STAGE if action=='stage' else H)/p,d)
 print(action,'five corrections (atomic per pack, not cross-pack)')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
