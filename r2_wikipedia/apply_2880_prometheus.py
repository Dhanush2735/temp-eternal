#!/usr/bin/env python3
"""Guarded two-pack staging/apply/rollback of two references to one tree."""
import argparse,copy,gzip,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
M=ROOT/'r2_wikipedia/reviews/2880_bce_prometheus_2026-10.json';STAGE=Path('/home/user/.cache/r2_storage/2880_prometheus_stage')
S={'wpy_b6b2e7d8a7':('events_wikipedia.json.gz',-3000,-2999,38.9975,-114.306,'older possible'), 'wpr_b2dc3b122c':('events_wikipedia_regional.json.gz',-2880,-2879,38.99887,-114.29903,'one estimate')}
def validate(m):
 u=m['updates']
 if m['schema']!='eternal-r2-2880bce-v1' or len(u)!=2 or {x['event_id'] for x in u}!=set(S):raise ValueError('Bad manifest')
 for x in u:
  id=x['event_id'];b=x['before'];a=x['after'];pack,start,end,lat,lon,qual=S[id]
  if x['pack']!=pack or b.get('id')!=id or a.get('id')!=id or set(a)-set(b)!={'r2SourceEvidence'} or {k for k in b if b[k]!=a[k]}-{'name','confidence'}:raise ValueError('Unexpected fields')
  if (a['start'],a['end'],a['lat'],a['lon'],a['radiusKm'],a['kind'],a['effect'],a['confidence'])!=(start,end,lat,lon,20,'incident','note','wikipedia_region'):raise ValueError('Bad slot or effect')
  if not all(t in a['name'] for t in ('Prometheus','same tree','date uncertain',qual)) or len(a['r2SourceEvidence']['sources'])<5:raise ValueError('Missing qualifications')
def transform(doc,m,pack,reverse=False):
 validate(m)
 if not isinstance(doc.get('events'),list):raise ValueError('No events')
 o=copy.deepcopy(doc)
 for x in [u for u in m['updates'] if u['pack']==pack]:
  hits=[i for i,r in enumerate(o['events']) if isinstance(r,dict) and r.get('id')==x['event_id']];old,new=(x['after'],x['before']) if reverse else (x['before'],x['after'])
  if len(hits)!=1 or o['events'][hits[0]]!=old:raise ValueError('Missing, duplicate or modified '+x['event_id'])
  o['events'][hits[0]]=copy.deepcopy(new)
 return o
def check_index():
 packs=json.loads((H/'index.json').read_text())['packs'];counts={i:0 for i in S}
 if any(p not in packs for p,*_ in S.values()):raise ValueError('Pack not indexed')
 for p in packs:
  with (gzip.open(H/p,'rt',encoding='utf8') if p.endswith('.gz') else open(H/p,encoding='utf8')) as f:d=json.load(f)
  for sec in ('events','sites'):
   for row in d.get(sec,[]):
    if isinstance(row,dict) and row.get('id') in counts:
     if (p,sec)!=(S[row['id']][0],'events'):raise ValueError('Shared ID')
     counts[row['id']]+=1
 if any(v!=1 for v in counts.values()):raise ValueError('Missing or duplicate ID')
def run(action):
 m=json.loads(M.read_text());validate(m);check_index();rev=action=='rollback';out={}
 # Prepare and validate both before any writes, but two atomic replacements are not crash-atomic together.
 for p in (S[id][0] for id in S):
  with gzip.open(H/p,'rt',encoding='utf8') as f:doc=json.load(f)
  result=transform(doc,m,p,rev)
  if transform(result,m,p,not rev)!=doc:raise ValueError('Roundtrip failed')
  out[p]=result
 for p,doc in out.items():write_atomic_gzip((STAGE if action=='stage' else H)/p,doc)
 print(action,'two references to one pine')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
