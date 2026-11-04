#!/usr/bin/env python3
"""Guarded, reversible edits; atomic per pack, not transactional across packs."""
import argparse,copy,gzip,hashlib,json,sys
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent
H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
M=ROOT/'r2_wikipedia/reviews/201_241_ce_context_2026-10.json.gz'
SHA='242bc4f83cea17f3b739b6efec8681a63de553ea9d850b6a377ade81a126233a'
STAGE=Path('/tmp/eternal-201-241-stage')
def validate(m):
 digest=hashlib.sha256(json.dumps(m,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 if digest!=SHA or m.get('schema')!='eternal-r2-201-241-ce-v1' or len(m['updates'])!=21: raise ValueError('Manifest differs from review')
 ids=[u['event_id'] for u in m['updates']]
 if len(set(ids))!=len(ids): raise ValueError('Repeated ID')
 for u in m['updates']:
  if u['pack'] not in ('events_wikipedia.json.gz','events_wikipedia_regional.json.gz','events_world.json.gz','events_wikidata_more.json.gz','events_wikipedia_decades.json.gz') or u['before']['id']!=u['event_id'] or u['after']['id']!=u['event_id']: raise ValueError('Unexpected entry')
  if u['after']['end']<=u['after']['start'] or not u['after']['r2SourceEvidence']['sources']: raise ValueError('Invalid after-image')
def transform(doc,updates,reverse=False):
 result=copy.deepcopy(doc);rows=result['events']
 for u in updates:
  before,after=(u['after'],u['before']) if reverse else (u['before'],u['after'])
  ix=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==u['event_id']]
  if len(ix)!=1 or rows[ix[0]]!=before: raise ValueError('Missing or changed '+u['event_id'])
  rows[ix[0]]=copy.deepcopy(after)
 return result
def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else open(p,encoding='utf8')) as f:return json.load(f)
def run(action):
 m=load(M);validate(m);updates=m['updates'];packs=load(H/'index.json')['packs'];expected={u['event_id']:u['pack'] for u in updates};seen={id:0 for id in expected};docs={}
 for p in packs:
  d=load(H/p)
  if p in expected.values():docs[p]=d
  for section in ('events','sites'):
   for row in d.get(section,[]):
    if isinstance(row,dict) and row.get('id') in expected:
     id=row['id'];seen[id]+=1
     if p!=expected[id] or section!='events':raise ValueError('Unexpected ID location '+id)
 if any(n!=1 for n in seen.values()):raise ValueError('IDs not unique '+str(seen))
 reverse=action=='rollback';outs={}
 for pack,doc in docs.items():
  subset=[u for u in updates if u['pack']==pack];out=transform(doc,subset,reverse)
  if transform(out,subset,not reverse)!=doc:raise ValueError('Round-trip failed')
  outs[pack]=out
 for pack,doc in outs.items():write_atomic_gzip((STAGE if action=='stage' else H)/pack,doc)
 print(action, len(updates),'records,',len(outs),'indexed packs; reversible; atomic per pack')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
