#!/usr/bin/env python3
"""Guarded reversible reviewed edits, additions and hazard moves; not cross-pack atomic."""
import argparse,copy,gzip,hashlib,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/1550_1510_bce_context_2026-10.json.gz';STAGE=ROOT/'.cache/r2_storage/1550_1510_stage';W='events_wikipedia.json.gz';R='events_wikipedia_regional.json.gz';HAZ='events_hazards.json.gz';WAR='events_wars.json.gz';D='events_wikipedia_decades.json.gz'
MANIFEST_SHA='4d2bd6908319e0c9b2990a7035037e64539acc38fe763334b1ae24072ab930c4'
def validate(m):
 if hashlib.sha256(json.dumps(m,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()!=MANIFEST_SHA:raise ValueError('Manifest differs from approved review')
 if m.get('schema')!='eternal-r2-1550-1510-v1' or len(m['updates'])!=8 or len(m['moves'])!=23 or len(m['additions'])!=10:raise ValueError('Invalid manifest')
 ids=[]
 for u in m['updates']+m['moves']:
  b,a=u['before'],u['after'];id=u['event_id'];ids.append(id)
  if b['id']!=id or a['id']!=id or set(a)!=set(b)|{'r2SourceEvidence'} or {k for k in b if a[k]!=b[k]}-{'name','start','end','lat','lon','radiusKm','kind','effect','confidence'}:raise ValueError('Unexpected edit '+id)
 for u in m['updates']:
  if u['pack'] not in (W,R,WAR,D):raise ValueError('Wrong update pack')
 for u in m['moves']:
  if u['from_pack'] not in (HAZ,WAR) or u['to_pack']!=R:raise ValueError('Wrong move packs')
 for x in m['additions']:
  ids.append(x['event']['id'])
  if x['pack']!=R or not x['event']['id'].startswith('r2_'):raise ValueError('Wrong addition')
 for e in [u['after'] for u in m['updates']+m['moves']]+[a['event'] for a in m['additions']]:
  if e['kind']!='cultural' or e['effect']!='note' or 'uncertain' not in e['name'] or e['end']<=e['start'] or not e['r2SourceEvidence']['sources']:raise ValueError('Invalid note')
 if len(ids)!=len(set(ids)):raise ValueError('Duplicate manifest IDs')
def transform(doc,m,pack,reverse=False):
 validate(m);o=copy.deepcopy(doc);rows=o.get('events')
 if not isinstance(rows,list):raise ValueError('Missing events')
 for u in (x for x in m['updates'] if x['pack']==pack):
  old,new=(u['after'],u['before']) if reverse else (u['before'],u['after']);hits=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==u['event_id']]
  if len(hits)!=1 or rows[hits[0]]!=old:raise ValueError('Missing/changed source '+u['event_id'])
  rows[hits[0]]=copy.deepcopy(new)
 for x in (y for y in m['additions'] if y['pack']==pack):
  e=x['event'];hits=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==e['id']]
  if reverse:
   if len(hits)!=1 or rows[hits[0]]!=e:raise ValueError('Missing/changed addition '+e['id'])
   del rows[hits[0]]
  else:
   if hits:raise ValueError('Duplicate addition '+e['id'])
   rows.append(copy.deepcopy(e))
 # Ascending original source indices ensure exact ordering on rollback.
 for x in m['moves']:
  src,dst=(x['to_pack'],x['from_pack']) if reverse else (x['from_pack'],x['to_pack']);old,new=(x['after'],x['before']) if reverse else (x['before'],x['after'])
  hits=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==x['event_id']]
  if pack==src:
   if len(hits)!=1 or rows[hits[0]]!=old:raise ValueError('Missing/changed move '+x['event_id'])
   del rows[hits[0]]
  elif pack==dst:
   if hits:raise ValueError('Duplicate target '+x['event_id'])
   if reverse:rows.insert(x['source_index'],copy.deepcopy(new))
   else:rows.append(copy.deepcopy(new))
 return o
def check_index(m,reverse):
 packs=json.loads((H/'index.json').read_text())['packs']
 if not {W,R,HAZ,WAR,D}.issubset(packs):raise ValueError('Missing indexed packs')
 loc={u['event_id']:u['pack'] for u in m['updates']};loc.update({u['event_id']:(R if reverse else u['from_pack']) for u in m['moves']});loc.update({a['event']['id']:(R if reverse else None) for a in m['additions']});counts={id:0 for id in loc}
 for p in packs:
  with (gzip.open(H/p,'rt',encoding='utf8') if p.endswith('.gz') else open(H/p,encoding='utf8')) as f:d=json.load(f)
  for sec in ('events','sites'):
   for row in d.get(sec,[]):
    if not isinstance(row,dict) or row.get('id') not in loc:continue
    id=row['id']
    if (p,sec)!=(loc[id],'events'):raise ValueError('Shared or unexpected ID '+id)
    counts[id]+=1
 for id,n in counts.items():
  if n!=(0 if loc[id] is None else 1):raise ValueError('Wrong ID count '+id)
def run(action):
 m=json.load(gzip.open(M,'rt',encoding='utf8'));validate(m);rev=action=='rollback';check_index(m,rev);outputs={}
 for p in (W,HAZ,R,WAR,D):
  with gzip.open(H/p,'rt',encoding='utf8') as f:d=json.load(f)
  out=transform(d,m,p,rev)
  if transform(out,m,p,not rev)!=d:raise ValueError('Roundtrip failed '+p)
  outputs[p]=out
 for p,d in outputs.items():write_atomic_gzip((STAGE if action=='stage' else H)/p,d)
 print(action,'8 corrections, 23 moves, 10 additions; atomic per pack, not cross-pack')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
