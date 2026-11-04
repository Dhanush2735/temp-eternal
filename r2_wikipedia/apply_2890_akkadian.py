#!/usr/bin/env python3
"""Guarded staging, installation and rollback of two Akkadian chronology notes."""
import argparse,copy,gzip,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/2890_bce_akkadian_2026-10.json';PACK='events_wikipedia.json.gz';STAGE=Path('/home/user/.cache/r2_storage/2890_akkadian_stage')
S={'wpy_f1bc01ef4a':(-2600,-2599,'2600–2500','words and names'),'wpy_7387a2ab6f':(-2400,-2399,'24th century','fully written')}
def validate(m):
 if (m['schema'],m['pack'])!=('eternal-r2-2890akkadian-v1',PACK) or len(m['updates'])!=2 or {u['event_id'] for u in m['updates']}!=set(S):raise ValueError('Bad manifest')
 for u in m['updates']:
  id=u['event_id'];b=u['before'];a=u['after'];st,en,x,y=S[id]
  if a.get('id')!=id or b.get('id')!=id or set(a)-set(b)!={'r2SourceEvidence'} or {k for k in b if a[k]!=b[k]}-{'name','start','end','lat','lon','radiusKm','confidence'}:raise ValueError('Unexpected change')
  if (a['start'],a['end'],a['lat'],a['lon'],a['radiusKm'],a['confidence'],a['kind'],a['effect'])!=(st,en,32.,45.5,250,'wikipedia_region','cultural','note'):raise ValueError('Invalid note')
  if x not in a['name'] or y not in a['name'] or 'approximate' not in a['name'] or len(a['r2SourceEvidence']['sources'])<4:raise ValueError('Missing caveats')
def transform(doc,m,reverse=False):
 validate(m)
 if not isinstance(doc.get('events'),list):raise ValueError('No events')
 o=copy.deepcopy(doc)
 for u in m['updates']:
  hits=[i for i,r in enumerate(o['events']) if isinstance(r,dict) and r.get('id')==u['event_id']];old,new=(u['after'],u['before']) if reverse else (u['before'],u['after'])
  if len(hits)!=1 or o['events'][hits[0]]!=old:raise ValueError('Missing, duplicate or changed '+u['event_id'])
  o['events'][hits[0]]=copy.deepcopy(new)
 return o
def check_index():
 packs=json.loads((H/'index.json').read_text())['packs'];counts={id:0 for id in S}
 if PACK not in packs:raise ValueError('Pack not indexed')
 for p in packs:
  with (gzip.open(H/p,'rt',encoding='utf8') if p.endswith('.gz') else open(H/p,encoding='utf8')) as f:d=json.load(f)
  for sec in ('events','sites'):
   for row in d.get(sec,[]):
    if isinstance(row,dict) and row.get('id') in counts:
     if (p,sec)!=(PACK,'events'):raise ValueError('Shared ID')
     counts[row['id']]+=1
 if any(v!=1 for v in counts.values()):raise ValueError('Missing or duplicate ID')
def run(action):
 m=json.loads(M.read_text());validate(m);check_index();rev=action=='rollback'
 with gzip.open(H/PACK,'rt',encoding='utf8') as f:doc=json.load(f)
 out=transform(doc,m,rev)
 if transform(out,m,not rev)!=doc:raise ValueError('Roundtrip failed')
 write_atomic_gzip((STAGE if action=='stage' else H)/PACK,out)
 print(action,'two approximate Akkadian references')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
