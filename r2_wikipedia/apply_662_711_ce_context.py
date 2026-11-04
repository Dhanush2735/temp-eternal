#!/usr/bin/env python3
"""Guarded, reversible edits; atomic per pack, not transactional across packs."""
import argparse,copy,gzip,hashlib,json,sys
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent
H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
M=ROOT/'r2_wikipedia/reviews/662_711_ce_context_2026-10.json.gz'
SHA='f17fc39c159859a028ed259ad6459f63a116f256b298bc8e1eaca12814744c8b'
STAGE=Path('/tmp/eternal-662-711-ce-context-stage')
def validate(m):
 digest=hashlib.sha256(json.dumps(m,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 if digest!=SHA or m.get('schema')!='eternal-r2-662-711-ce-context-v1' or len(m['updates'])!=10 or len(m['additions'])!=0: raise ValueError('Manifest differs from review')
 ids=[u['event_id'] for u in m['updates']]+[a['event']['id'] for a in m['additions']]
 for a in m['additions']:
  e=a['event']
  if a['pack']!='events_wikipedia_regional.json.gz' or not e['id'].startswith('r2_') or e['end']<=e['start'] or not e['r2SourceEvidence']['sources']: raise ValueError('Invalid addition')
 if len(set(ids))!=len(ids): raise ValueError('Repeated ID')
 for u in m['updates']:
  if u['pack'] not in ('events_wikipedia.json.gz','events_wikipedia_regional.json.gz','events_world.json.gz','events_wikidata_more.json.gz','events_wikipedia_decades.json.gz','events_wars.json.gz','events_nature.json.gz','deccan_events.json.gz','events_hazards.json.gz') or u['before']['id']!=u['event_id'] or u['after']['id']!=u['event_id']: raise ValueError('Unexpected entry')
  if (u['after']['end']<=u['after']['start'] and not (u['pack']=='deccan_events.json.gz' and u['after']['end']==u['after']['start'] and u['before']['start']==u['after']['start'] and u['before']['end']==u['after']['end'])) or not (u['after'].get('r2SourceEvidence') or u['after'].get('r2AdditionalEvidence'))['sources']: raise ValueError('Invalid after-image')
def transform(doc,updates,reverse=False,additions=()):
 result=copy.deepcopy(doc);rows=result['events']
 for u in updates:
  before,after=(u['after'],u['before']) if reverse else (u['before'],u['after'])
  ix=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==u['event_id']]
  if len(ix)!=1 or rows[ix[0]]!=before: raise ValueError('Missing or changed '+u['event_id'])
  rows[ix[0]]=copy.deepcopy(after)
 for item in additions:
  event=item['event'];ix=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==event['id']]
  if reverse:
   if len(ix)!=1 or rows[ix[0]]!=event:raise ValueError('Missing or changed addition '+event['id'])
   del rows[ix[0]]
  else:
   if ix:raise ValueError('Duplicate addition '+event['id'])
   rows.append(copy.deepcopy(event))
 return result
def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else open(p,encoding='utf8')) as f:return json.load(f)
def run(action):
 m=load(M);validate(m);updates=m['updates'];packs=load(H/'index.json')['packs'];expected={u['event_id']:u['pack'] for u in updates}; added={a['event']['id']:a['pack'] for a in m['additions']}; expected.update(added);seen={id:0 for id in expected};docs={}
 for p in packs:
  d=load(H/p)
  if p in expected.values():docs[p]=d
  for section in ('events','sites'):
   for row in d.get(section,[]):
    if isinstance(row,dict) and row.get('id') in expected:
     id=row['id'];seen[id]+=1
     if p!=expected[id] or section!='events':raise ValueError('Unexpected ID location '+id)
 if any(n!=(1 if id not in added or action=='rollback' else 0) for id,n in seen.items()):raise ValueError('IDs not unique '+str(seen))
 reverse=action=='rollback';outs={}
 for pack,doc in docs.items():
  subset=[u for u in updates if u['pack']==pack]; additions=[a for a in m['additions'] if a['pack']==pack];out=transform(doc,subset,reverse,additions)
  if transform(out,subset,not reverse,additions)!=doc:raise ValueError('Round-trip failed')
  outs[pack]=out
 for pack,doc in outs.items():write_atomic_gzip((STAGE if action=='stage' else H)/pack,doc)
 print(action,len(updates),'updates,',len(m['additions']),'additions,',len(outs),'indexed packs; reversible; atomic per pack')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
