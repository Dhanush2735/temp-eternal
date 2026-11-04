#!/usr/bin/env python3
"""Guarded reversible ten-move, 19-addition review; writes atomic per pack, not cross-pack."""
import argparse,copy,gzip,hashlib,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/1850_1810_bce_context_2026-10.json.gz';STAGE=ROOT/'.cache/r2_storage/1850_1810_stage';W='events_world.json.gz';R='events_wikipedia_regional.json.gz';HAZ='events_hazards.json.gz'
# Locks the entire approved manifest, including all before-images and evidence.
MANIFEST_SHA='5df240f7c0256d307c8fb1ac81040d9208fab9d6245de9d7796befec707bbc14'
def validate(m):
 raw=json.dumps(m,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
 if hashlib.sha256(raw).hexdigest()!=MANIFEST_SHA:raise ValueError('Manifest differs from approved review')
 if m.get('schema')!='eternal-r2-1850-1810-v1' or len(m['moves'])!=10 or len(m['additions'])!=19 or m['updates']:raise ValueError('Invalid manifest')
 ids=[]
 for u in m['moves']:
  b,a=u['before'],u['after'];id=u['event_id'];ids.append(id)
  if u['from_pack'] not in (W,HAZ) or u['to_pack']!=R or b['id']!=id or a['id']!=id or set(a)!=set(b)|{'r2SourceEvidence'} or {k for k in b if a[k]!=b[k]}-{'name','start','end','lat','lon','radiusKm','kind','effect','confidence'}:raise ValueError('Unexpected move')
 for item in m['additions']:
  e=item['event'];ids.append(e['id'])
  if item['pack']!=R or not e['id'].startswith('r2_'):raise ValueError('Unexpected addition')
 for e in [u['after'] for u in m['moves']]+[a['event'] for a in m['additions']]:
  if e['kind']!='cultural' or e['effect']!='note' or 'uncertain' not in e['name'] or e['end']<=e['start'] or not e['r2SourceEvidence']['sources']:raise ValueError('Invalid note')
 if len(ids)!=len(set(ids)):raise ValueError('Duplicate manifest id')
def transform(doc,m,pack,reverse=False):
 validate(m);o=copy.deepcopy(doc);rows=o.get('events')
 if not isinstance(rows,list):raise ValueError('No events')
 for item in (x for x in m['additions'] if x['pack']==pack):
  e=item['event'];hits=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==e['id']]
  if reverse:
   if len(hits)!=1 or rows[hits[0]]!=e:raise ValueError('Missing/changed addition '+e['id'])
   del rows[hits[0]]
  else:
   if hits:raise ValueError('Duplicate addition '+e['id'])
   rows.append(copy.deepcopy(e))
 # Original indices are ascending within source pack; remove by ID, restore ascending.
 for move in m['moves']:
  src,dst=(move['to_pack'],move['from_pack']) if reverse else (move['from_pack'],move['to_pack'])
  old,new=(move['after'],move['before']) if reverse else (move['before'],move['after'])
  hits=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==move['event_id']]
  if pack==src:
   if len(hits)!=1 or rows[hits[0]]!=old:raise ValueError('Missing/changed source '+move['event_id'])
   del rows[hits[0]]
  elif pack==dst:
   if hits:raise ValueError('Duplicate target '+move['event_id'])
   if reverse:rows.insert(move['source_index'],copy.deepcopy(new))
   else:rows.append(copy.deepcopy(new))
 return o
def check_index(m,reverse):
 packs=json.loads((H/'index.json').read_text())['packs']
 if not {W,R,HAZ}.issubset(packs):raise ValueError('Missing indexed pack')
 loc={u['event_id']:(R if reverse else u['from_pack']) for u in m['moves']};loc.update({a['event']['id']:(R if reverse else None) for a in m['additions']});counts={k:0 for k in loc}
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
 for p in (W,HAZ,R):
  with gzip.open(H/p,'rt',encoding='utf8') as f:doc=json.load(f)
  out=transform(doc,m,p,rev)
  if transform(out,m,p,not rev)!=doc:raise ValueError('Roundtrip failed '+p)
  outputs[p]=out
 for p,d in outputs.items():write_atomic_gzip((STAGE if action=='stage' else H)/p,d)
 print(action,'10 moves, 19 additions; atomic per pack, not cross-pack')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
