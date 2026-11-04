#!/usr/bin/env python3
"""Stage, apply, strictly roll back five focused event corrections in one atomic pack."""
import argparse,copy,gzip,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/2900_bce_mesopotamia_2026-10.json';P='events_wikipedia.json.gz';STAGE=Path('/home/user/.cache/r2_storage/2900_meso_stage')
SPECS={
'wpy_c391570504':(-2900,-2699,32.,45.5,250,'wikipedia_region','dating varies'),
'wpy_519682d05d':(-2900,-2899,34.54944,40.89,20,'wikipedia_coord','approximate'),
'wpy_7be5a5ae96':(-2900,-2899,32.,45.5,200,'wikipedia_region','proto-cuneiform'),
'wpy_90456360c7':(-2900,-2899,32.,45.5,250,'wikipedia_region','timing varies'),
'wpy_e710018ef5':(-2900,-2899,30.96222,46.10444,20,'wikipedia_coord','approximate')}
ALLOWED={'name','start','end','lat','lon','radiusKm','confidence','kind','effect'}
def validate(m):
 if m['schema']!='eternal-r2-2900bce-v1' or m['pack']!=P:raise ValueError('Bad manifest')
 updates=m['updates']
 if len(updates)!=len(SPECS) or {u['event_id'] for u in updates}!=set(SPECS):raise ValueError('Wrong event set')
 for u in updates:
  id=u['event_id'];b=u['before'];a=u['after'];start,end,lat,lon,radius,conf,caveat=SPECS[id]
  if b.get('id')!=id or a.get('id')!=id or set(a)-set(b)!={'r2SourceEvidence'} or {k for k in b if a[k]!=b[k]}-ALLOWED:raise ValueError('Invalid changed fields')
  if (a['start'],a['end'],a['lat'],a['lon'],a['radiusKm'],a['confidence'],a['kind'],a['effect'])!=(start,end,lat,lon,radius,conf,'cultural','note'):raise ValueError('Invalid slot or effect')
  if caveat not in a['name'] or len(a['r2SourceEvidence']['sources'])<3 or not a['r2SourceEvidence']['review_note']:raise ValueError('Missing qualification')
def transform(doc,m,reverse=False):
 validate(m)
 if not isinstance(doc.get('events'),list):raise ValueError('No events')
 out=copy.deepcopy(doc)
 for u in m['updates']:
  hits=[i for i,r in enumerate(out['events']) if isinstance(r,dict) and r.get('id')==u['event_id']]
  old,new=(u['after'],u['before']) if reverse else (u['before'],u['after'])
  if len(hits)!=1 or out['events'][hits[0]]!=old:raise ValueError('Missing, duplicate or changed target '+u['event_id'])
  out['events'][hits[0]]=copy.deepcopy(new)
 return out
def index_guard():
 packs=json.loads((H/'index.json').read_text())['packs'];counts={i:0 for i in SPECS}
 if P not in packs:raise ValueError('Not indexed')
 for p in packs:
  with (gzip.open(H/p,'rt',encoding='utf8') if p.endswith('.gz') else open(H/p,encoding='utf8')) as f:d=json.load(f)
  for sec in ('events','sites'):
   for r in d.get(sec,[]):
    if isinstance(r,dict) and r.get('id') in counts:
     if (p,sec)!=(P,'events'):raise ValueError('Shared ID')
     counts[r['id']]+=1
 if any(v!=1 for v in counts.values()):raise ValueError('Missing or duplicate ID')
def run(action):
 m=json.loads(M.read_text());validate(m);index_guard();rev=action=='rollback'
 with gzip.open(H/P,'rt') as f:doc=json.load(f)
 out=transform(doc,m,rev)
 if transform(out,m,not rev)!=doc:raise ValueError('Rollback failed')
 write_atomic_gzip((STAGE if action=='stage' else H)/P,out)
 print(action,'five contextual corrections in one indexed pack')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
