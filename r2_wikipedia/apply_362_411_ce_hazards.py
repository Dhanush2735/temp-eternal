#!/usr/bin/env python3
"""Guarded cross-pack moves. Atomic per pack, not atomic across packs."""
import argparse,copy,gzip,hashlib,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent
H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
M=ROOT/'r2_wikipedia/reviews/362_411_ce_hazards_2026-10.json.gz'
STAGE=Path('/tmp/eternal-362-411-ce-hazards-stage')
HAZ='events_hazards.json.gz';REG='events_wikipedia_regional.json.gz'
SHA='288fec5a58ff0e45c67ad5d1ccba260c44c5df2aa01e01dba0113a58a13d7e72'
IDS={'hz_649d3e6c28', 'hz_76edb835e1', 'hz_29a9bb89d5', 'hz_6995e0f2bb', 'hz_dcbe0aeaac', 'hz_92881866e4', 'hz_5c0067a55c', 'hz_8af8620e9a', 'hz_dec8487c6c', 'hz_9c57b32e89', 'hz_431b04926d', 'hz_2fddf1ca76', 'hz_4b700e2afc', 'hz_e5efe35a96', 'hz_1f9aeef47f', 'hz_fe31c66645', 'hz_a347c5d27b', 'hz_468657a6db', 'hz_c0c48e2f62', 'hz_066d11ab68', 'hz_5ec562c146', 'hz_1ecf35204c'}
def load(path):
 with (gzip.open(path,'rt',encoding='utf8') if str(path).endswith('.gz') else open(path,encoding='utf8')) as f:return json.load(f)
def validate(m):
 sha=hashlib.sha256(json.dumps(m,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 if sha!=SHA or m.get('schema')!='eternal-r2-362-411-ce-hazards-v1' or len(m.get('moves',[]))!=22:raise ValueError('Manifest does not match review')
 if {u['event_id'] for u in m['moves']}!=IDS:raise ValueError('Wrong IDs')
 if sorted(u['source_index'] for u in m['moves'])!=[u['source_index'] for u in m['moves']]:raise ValueError('Moves must be in original order')
 for u in m['moves']:
  b,a=u['before'],u['after'];id=u['event_id']
  if u['from_pack']!=HAZ or u['to_pack']!=REG or b['id']!=id or a['id']!=id:raise ValueError('Wrong move')
  if set(a)!=set(b)|{'r2SourceEvidence'} or {k for k in b if a[k]!=b[k]}-{'name','start','end','kind','effect','confidence'}:raise ValueError('Unexpected changes')
  if (a['kind'],a['effect'])!=('cultural','note') or a['confidence'] not in ('wikipedia_region',) or not a['r2SourceEvidence']['sources']:raise ValueError('Invalid note')
def transform(doc,m,pack,reverse=False):
 o=copy.deepcopy(doc);rows=o['events']
 for u in m['moves']:
  src,dst=(REG,HAZ) if reverse else (HAZ,REG);old,new=(u['after'],u['before']) if reverse else (u['before'],u['after']);hits=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==u['event_id']]
  if pack==src:
   if len(hits)!=1 or rows[hits[0]]!=old:raise ValueError('Missing/changed source '+u['event_id'])
   del rows[hits[0]]
  elif pack==dst:
   if hits:raise ValueError('Duplicate destination '+u['event_id'])
   if reverse:rows.insert(u['source_index'],copy.deepcopy(new))
   else:rows.append(copy.deepcopy(new))
 return o
def check_index(reverse):
 packs=load(H/'index.json')['packs']
 if not {HAZ,REG}.issubset(packs):raise ValueError('Required packs not indexed')
 counts={i:0 for i in IDS}
 for p in packs:
  d=load(H/p)
  for sec in ('events','sites'):
   for row in d.get(sec,[]):
    if isinstance(row,dict) and row.get('id') in IDS:
     id=row['id'];counts[id]+=1
     if (p,sec)!=((REG if reverse else HAZ),'events'):raise ValueError('Unexpected indexed ID '+id)
 if any(n!=1 for n in counts.values()):raise ValueError('Missing or duplicate IDs '+str(counts))
def run(action):
 m=load(M);validate(m);rev=action=='rollback';check_index(rev);outputs={}
 for p in (HAZ,REG):
  d=load(H/p);out=transform(d,m,p,rev)
  if transform(out,m,p,not rev)!=d:raise ValueError('Roundtrip failed '+p)
  outputs[p]=out
 for p,d in outputs.items():write_atomic_gzip((STAGE if action=='stage' else H)/p,d)
 print(action,len(m['moves']),'cross-pack moves; writes atomic per pack, not across packs')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
