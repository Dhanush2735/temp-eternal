#!/usr/bin/env python3
"""Guarded quarantine of two demonstrably prehistoric hazards; reversible per pack."""
import argparse,copy,gzip,hashlib,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent
H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
M=ROOT/'r2_wikipedia/reviews/62_111_ce_geologic_quarantine_2026-10.json'
SHA='9d1b94f5b947d3ddb308a9d7bf39d596a3d518e51eb7d9693d9df9f3e348ce88'
IDS={'hz_f23b68d313'}
def load(p):
 with (gzip.open(p,'rt') if str(p).endswith('.gz') else open(p)) as f:return json.load(f)
def validate(m):
 if hashlib.sha256(json.dumps(m,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()!=SHA or m.get('schema')!='eternal-r2-geologic-62-111-quarantine-v1':raise ValueError('Review changed')
 if {r['event_id'] for r in m['records']}!=IDS or len(m['records'])!=1:raise ValueError('Wrong IDs')
 if sorted(r['source_index'] for r in m['records'])!=[r['source_index'] for r in m['records']]:raise ValueError('Bad order')
 if any(r['before']['id']!=r['event_id'] or not r['source'] for r in m['records']):raise ValueError('Invalid record')
def transform(doc,m,reverse=False):
 d=copy.deepcopy(doc);a=d['events']
 for r in m['records']:
  hits=[i for i,x in enumerate(a) if isinstance(x,dict) and x.get('id')==r['event_id']]
  if reverse:
   if hits:raise ValueError('ID already exists')
   a.insert(r['source_index'],copy.deepcopy(r['before']))
  else:
   if len(hits)!=1 or a[hits[0]]!=r['before']:raise ValueError('Before-image differs')
   del a[hits[0]]
 return d
def run(action):
 m=load(M);validate(m);reverse=action=='rollback';counts={x:0 for x in IDS}
 for p in load(H/'index.json')['packs']:
  d=load(H/p)
  for sec in ('events','sites'):
   for r in d.get(sec,[]):
    if isinstance(r,dict) and r.get('id') in IDS:
     counts[r['id']]+=1
     if p!='events_hazards.json.gz' or sec!='events':raise ValueError('Unexpected indexed ID')
 if any(v!=(0 if reverse else 1) for v in counts.values()):raise ValueError('Missing/duplicate indexed ID')
 d=load(H/'events_hazards.json.gz');out=transform(d,m,reverse)
 if transform(out,m,not reverse)!=d:raise ValueError('Roundtrip mismatch')
 path=(Path('/tmp/eternal-62-geologic-stage') if action=='stage' else H)/'events_hazards.json.gz';write_atomic_gzip(path,out);print(action,'1 research-quarantined prehistoric misdates; one pack atomic')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
