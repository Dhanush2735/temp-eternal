#!/usr/bin/env python3
"""Stage, install or undo one source-qualified legacy 2890 transition reference."""
import argparse,copy,gzip,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent
H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
M=ROOT/'r2_wikipedia/reviews/2890_bce_egypt_transition_2026-10.json'
PACK='events_wikipedia_regional.json.gz';ID='wpr_4328bf556a';STAGE=Path('/home/user/.cache/r2_storage/2890_transition_stage')
def validate(m):
 if (m['schema'],m['pack'],m['event_id'])!=('eternal-r2-2890bce-v1',PACK,ID):raise ValueError('Bad manifest')
 a=m['after'];b=m['before']
 if b.get('id')!=ID or a.get('id')!=ID or set(a)-set(b)!={'r2SourceEvidence'}:raise ValueError('Bad IDs or fields')
 if {k for k in b if b[k]!=a[k]}!={'name','kind','effect'}:raise ValueError('Unexpected field changes')
 if (a['start'],a['end'],a['lat'],a['lon'],a['radiusKm'],a['kind'],a['effect'],a['confidence'])!=(-2890,-2889,29.638,31.2209,269,'cultural','note','wikipedia_region'):raise ValueError('Bad slot or effect')
 if not all(x in a['name'] for x in ('c. 2890 BC',"Qa'a",'Hotepsekhemwy','dates debated')) or len(a['r2SourceEvidence']['sources'])<6:raise ValueError('Missing qualifications')
def transform(doc,m,reverse=False):
 validate(m)
 if not isinstance(doc.get('events'),list):raise ValueError('No events')
 o=copy.deepcopy(doc);hits=[i for i,r in enumerate(o['events']) if isinstance(r,dict) and r.get('id')==ID];old,new=(m['after'],m['before']) if reverse else (m['before'],m['after'])
 if len(hits)!=1 or o['events'][hits[0]]!=old:raise ValueError('Missing, duplicate or modified event')
 o['events'][hits[0]]=copy.deepcopy(new)
 return o
def check_index():
 packs=json.loads((H/'index.json').read_text())['packs'];n=0
 if PACK not in packs:raise ValueError('Pack not indexed')
 for p in packs:
  with (gzip.open(H/p,'rt',encoding='utf8') if p.endswith('.gz') else open(H/p,encoding='utf8')) as f:d=json.load(f)
  for section in ('events','sites'):
   for row in d.get(section,[]):
    if isinstance(row,dict) and row.get('id')==ID:
     if (p,section)!=(PACK,'events'):raise ValueError('Shared ID')
     n+=1
 if n!=1:raise ValueError('Missing or duplicate ID')
def run(action):
 m=json.loads(M.read_text());validate(m);check_index();rev=action=='rollback'
 with gzip.open(H/PACK,'rt',encoding='utf8') as f:doc=json.load(f)
 out=transform(doc,m,rev)
 if transform(out,m,not rev)!=doc:raise ValueError('Roundtrip failed')
 write_atomic_gzip((STAGE if action=='stage' else H)/PACK,out)
 print(action,'one approximate dynastic transition context')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
