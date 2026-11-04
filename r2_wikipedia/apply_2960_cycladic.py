#!/usr/bin/env python3
"""Guarded installation/rollback of one contextual interval, one atomic file."""
import argparse,copy,gzip,json,shutil
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent; H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/2960_cycladic_context_2026-10.json';STAGE=Path('/home/user/.cache/r2_storage/2960_cycladic_stage');PACK='events_wikipedia.json.gz';ID='wpy_df3135a5e0'
def validate(m):
 if (m['schema'],m['pack'],m['event_id'])!=('eternal-r2-2960-cycladic-v1',PACK,ID):raise ValueError('Invalid manifest')
 b,a=m['before'],m['after']
 if b.get('id')!=ID or a.get('id')!=ID or set(a)!=set(b):raise ValueError('Invalid row')
 if (b['start'],b['end'],a['start'],a['end'])!=(-3000,-2999,-3100,-2899):raise ValueError('Unexpected chronology')
 if {k for k in a if a[k]!=b[k]}!={'start','end','name','r2SourceEvidence'}:raise ValueError('Unexpected changed fields')
 if (a['lat'],a['lon'],a['radiusKm'],a['confidence'],a['kind'],a['effect'])!=(37.0,25.16667,100,'wikipedia_region','cultural','note'):raise ValueError('Unexpected gameplay values')
 if 'dates vary' not in a['name'] or 'Grotta' not in a['name'] or not a['r2SourceEvidence'].get('sources'):raise ValueError('Missing caveat')
def transform(doc,m,reverse=False):
 validate(m);out=copy.deepcopy(doc);hits=[i for i,r in enumerate(out['events']) if isinstance(r,dict) and r.get('id')==ID]
 if len(hits)!=1:raise ValueError('Missing/shared ID')
 old,new=(m['after'],m['before']) if reverse else (m['before'],m['after'])
 if out['events'][hits[0]]!=old:raise ValueError('Row modified')
 out['events'][hits[0]]=copy.deepcopy(new);return out
def index_guard():
 packs=json.loads((H/'index.json').read_text())['packs']
 if PACK not in packs:raise ValueError('Not indexed')
 count=0
 for p in packs:
  with (gzip.open(H/p,'rt',encoding='utf8') if p.endswith('.gz') else open(H/p,encoding='utf8')) as f:d=json.load(f)
  for sec in ('events','sites'):
   for r in d.get(sec,[]):
    if isinstance(r,dict) and r.get('id')==ID:
     if p!=PACK or sec!='events':raise ValueError('Shared ID')
     count+=1
 if count!=1:raise ValueError('Missing/shared ID')
def run(action):
 m=json.loads(M.read_text());index_guard()
 with gzip.open(H/PACK,'rt') as f:doc=json.load(f)
 rev=action=='rollback';out=transform(doc,m,rev)
 if transform(out,m,not rev)!=doc:raise ValueError('Rollback mismatch')
 write_atomic_gzip((STAGE if action=='stage' else H)/PACK,out)
 if action=='stage':shutil.copy2(H/'events_wikipedia_regional.json.gz',STAGE/'events_wikipedia_regional.json.gz')
 print(action,'updated one regional period note')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
