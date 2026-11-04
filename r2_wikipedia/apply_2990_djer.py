#!/usr/bin/env python3
"""Stage, install or undo a single source-qualified 2990 BCE event."""
import argparse,copy,gzip,json,re
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
M=ROOT/'r2_wikipedia/reviews/2990_bce_djer_2026-10.json';PACK='events_wikipedia_regional.json.gz';STAGE=Path('/home/user/.cache/r2_storage/2990_djer_stage')
ID='r2_djer_death_estimate_c2990'
def validate(m):
 e=m['event']
 if m['schema']!='eternal-r2-2990bce-v1' or m['pack']!=PACK:raise ValueError('Invalid manifest')
 if (e['id'],e['start'],e['end'],e['lat'],e['lon'],e['radiusKm'],e['kind'],e['effect'],e['confidence'])!=(ID,-2990,-2989,26.175,31.9083,100,'cultural','note','wikipedia_region'):raise ValueError('Invalid event')
 if not all(t in e['name'] for t in ('2990–2980','One estimate','dates are debated')) or len(e['r2SourceEvidence']['sources'])<4:raise ValueError('Missing qualifications or sources')
def transform(doc,event,reverse=False):
 if not isinstance(doc.get('events'),list):raise ValueError('Missing events')
 o=copy.deepcopy(doc);hits=[i for i,r in enumerate(o['events']) if isinstance(r,dict) and r.get('id')==ID]
 if reverse:
  if len(hits)!=1 or o['events'][hits[0]]!=event:raise ValueError('Missing or modified event')
  del o['events'][hits[0]]
 else:
  if hits:raise ValueError('Event exists')
  o['events'].append(copy.deepcopy(event))
 return o
def check_index(reverse):
 index=json.loads((H/'index.json').read_text())['packs']
 if PACK not in index:raise ValueError('Pack not indexed')
 matches=0
 for p in index:
  with (gzip.open(H/p,'rt',encoding='utf8') if p.endswith('.gz') else open(H/p,encoding='utf8')) as f:doc=json.load(f)
  for section in ('sites','events'):
   for r in doc.get(section,[]):
    if not isinstance(r,dict):continue
    id=r.get('id')
    if id==ID:
     if p!=PACK or section!='events':raise ValueError('ID shared across index')
     matches+=1
    if section=='events' and id!=ID and re.search(r'\bdjer\b',str(r.get('name','')),re.I):
     start=r.get('start',r.get('year'));end=r.get('end',start+1 if isinstance(start,int) else None)
     if isinstance(start,int) and isinstance(end,int) and start<=-2980 and end>-2990:raise ValueError('Possible overlapping Djer event: '+str(id))
 if matches!=(1 if reverse else 0):raise ValueError('Unexpected ID count')
def run(action):
 m=json.loads(M.read_text(encoding='utf8'));validate(m);reverse=action=='rollback';check_index(reverse)
 with gzip.open(H/PACK,'rt',encoding='utf8') as f:doc=json.load(f)
 out=transform(doc,m['event'],reverse)
 if transform(out,m['event'],not reverse)!=doc:raise ValueError('Roundtrip failed')
 write_atomic_gzip((STAGE if action=='stage' else H)/PACK,out)
 print(action,'one approximate Djer reference')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
