#!/usr/bin/env python3
"""Apply locked, sourced 3000 BCE corrections, retaining old gameplay reference years.

Stages both packs first and validates all expected rows. Each file write is atomic;
there is no cross-file crash-atomic transaction. The manifest enables strict rollback.
"""
import argparse,copy,gzip,json,math
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent
HISTORY=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
MANIFEST=ROOT/'r2_wikipedia/reviews/3000_bce_batch_2026-10.json'
STAGE=Path('/home/user/.cache/r2_storage/3000_bce_stage')
PACKS={'events_wikipedia.json.gz','events_wikipedia_regional.json.gz'}

def transform(doc,updates,reverse=False):
 if not isinstance(doc.get('events'),list):raise ValueError('Missing events')
 out=copy.deepcopy(doc);ids=set()
 for u in updates:
  old,new=u['before'],u['after'];eid=u['event_id']
  if eid in ids or old.get('id')!=eid or new.get('id')!=eid:raise ValueError('Duplicate or mismatched ID')
  ids.add(eid)
  if old.get('start')!=-3000 or old.get('end')!=-2999:raise ValueError('Unexpected year range')
  if set(new)-set(old)!={'r2SourceEvidence'} or 'r2SourceEvidence' in old:raise ValueError('Evidence mismatch')
  changed={k for k in old if old[k]!=new[k]}
  if not changed or changed-{'name','lat','lon','kind','effect'}:raise ValueError('Unsupported field change')
  if 'kind' in changed and new['kind']!='cultural':raise ValueError('Invalid kind change')
  if 'effect' in changed and new['effect']!='note':raise ValueError('Invalid effect change')
  if not new['name'].startswith('c. 3000 BC:') or not new['r2SourceEvidence'].get('sources'):raise ValueError('Missing approximation or sources')
  for key,low,high in [('lat',-90,90),('lon',-180,180)]:
   val=new[key]
   if isinstance(val,bool) or not isinstance(val,(int,float)) or not math.isfinite(val) or not low<=val<=high:raise ValueError('Invalid coordinates')
  hits=[i for i,r in enumerate(doc['events']) if isinstance(r,dict) and r.get('id')==eid]
  if len(hits)!=1:raise ValueError('Missing or duplicate event: '+eid)
  i=hits[0];expected=new if reverse else old;replacement=old if reverse else new
  if doc['events'][i]!=expected:raise ValueError('Record has changed: '+eid)
  out['events'][i]=copy.deepcopy(replacement)
 check=copy.deepcopy(out)
 for u in updates:
  for i,r in enumerate(check['events']):
   if r.get('id')==u['event_id']:check['events'][i]=copy.deepcopy(u['after'] if reverse else u['before']);break
 if check!=doc:raise ValueError('Unexpected unrelated change')
 return out

def run(action):
 m=json.loads(MANIFEST.read_text(encoding='utf8'))
 if m.get('schema')!='eternal-r2-3000bce-batch-corrections-v1':raise ValueError('Wrong manifest')
 updates=m['updates'];packs={u['pack'] for u in updates}
 if packs!=PACKS:raise ValueError('Unexpected target packs')
 if not packs.issubset(set(json.loads((HISTORY/'index.json').read_text())['packs'])):raise ValueError('Pack not indexed')
 docs={};outputs={}
 for name in sorted(packs):
  with gzip.open(HISTORY/name,'rt',encoding='utf8') as f:docs[name]=json.load(f)
  outputs[name]=transform(docs[name],[u for u in updates if u['pack']==name],action=='rollback')
  assert transform(outputs[name],[u for u in updates if u['pack']==name],action!='rollback')==docs[name]
 if action=='stage':
  for name,out in outputs.items():write_atomic_gzip(STAGE/name,out)
 else:
  for name,out in outputs.items():write_atomic_gzip(HISTORY/name,out)
 print(action,'completed:',len(updates),'records in',len(packs),'packs')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
