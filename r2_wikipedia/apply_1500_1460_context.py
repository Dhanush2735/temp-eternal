#!/usr/bin/env python3
"""Fail-closed corrections; each output atomic, not atomic across packs."""
import argparse,copy,gzip,hashlib,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent
H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
M=ROOT/'r2_wikipedia/reviews/1500_1460_bce_context_2026-10.json'
STAGE=Path('/tmp/eternal-1500-1460-stage')
SHA='f53cf6f2de6ba41c28f3f4c1bb856adaf694d54f44c8572d5c989c49688de5de'
PACKS=('events_wikipedia.json.gz','events_wikipedia_regional.json.gz','events_wikipedia_decades.json.gz')
def validate(m):
 if hashlib.sha256(json.dumps(m,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()!=SHA:raise ValueError('Manifest changed')
 if m.get('schema')!='eternal-r2-1500-1460-v1' or len(m['updates'])!=6:raise ValueError('Bad manifest')
 ids=[]
 for u in m['updates']:
  a,b=u['after'],u['before'];ids.append(u['event_id'])
  if u['pack'] not in PACKS or a['id']!=u['event_id'] or b['id']!=u['event_id'] or set(a)!=set(b)|{'r2SourceEvidence'}:raise ValueError('Bad update')
  if a['start']!=b['start'] or a['end']!=b['end'] or a['kind']!='cultural' or a['effect']!='note' or not a['r2SourceEvidence']['sources']:raise ValueError('Bad fields')
 if len(set(ids))!=len(ids):raise ValueError('Duplicate ID')
def transform(doc,m,pack,reverse=False):
 validate(m);out=copy.deepcopy(doc)
 for u in (x for x in m['updates'] if x['pack']==pack):
  old,new=(u['after'],u['before']) if reverse else (u['before'],u['after'])
  hits=[i for i,x in enumerate(out['events']) if isinstance(x,dict) and x.get('id')==u['event_id']]
  if len(hits)!=1 or out['events'][hits[0]]!=old:raise ValueError('Missing, duplicate, or modified source '+u['event_id'])
  out['events'][hits[0]]=copy.deepcopy(new)
 return out
def check_index(m):
 packs=json.loads((H/'index.json').read_text())['packs']; expected={u['event_id']:u['pack'] for u in m['updates']}; counts={id:0 for id in expected}
 if not set(PACKS).issubset(packs):raise ValueError('Pack missing from index')
 for p in packs:
  with (gzip.open(H/p,'rt',encoding='utf8') if p.endswith('.gz') else open(H/p,encoding='utf8')) as f:d=json.load(f)
  for sec in ('events','sites'):
   for x in d.get(sec,[]):
    if isinstance(x,dict) and x.get('id') in expected:
     id=x['id'];counts[id]+=1
     if p!=expected[id] or sec!='events':raise ValueError('ID appears in unexpected pack '+id)
 if any(n!=1 for n in counts.values()):raise ValueError('ID not unique')
def run(action):
 m=json.loads(M.read_text());validate(m);check_index(m);rev=action=='rollback';outputs={}
 for p in PACKS:
  with gzip.open(H/p,'rt',encoding='utf8') as f:d=json.load(f)
  out=transform(d,m,p,rev)
  if transform(out,m,p,not rev)!=d:raise ValueError('Rollback check failed')
  outputs[p]=out
 for p,d in outputs.items():write_atomic_gzip((STAGE if action=='stage' else H)/p,d)
 print(action,'6 corrections; 3 individually atomic pack writes, not cross-pack atomic')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('action',choices=['stage','apply','rollback']);run(a.parse_args().action)
