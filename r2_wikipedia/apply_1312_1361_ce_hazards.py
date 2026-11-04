#!/usr/bin/env python3
"""Guarded cross-pack moves. Atomic per pack, not atomic across packs."""
import argparse,copy,gzip,hashlib,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent
H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
M=ROOT/'r2_wikipedia/reviews/1312_1361_ce_hazards_2026-10.json.gz'
STAGE=Path('/tmp/eternal-1312-1361-ce-hazards-stage')
HAZ='events_hazards.json.gz';REG='events_wikipedia_regional.json.gz'
SHA='bb31968704eecf7d5c856252b47b87bd0c3867de75cc5d1132c3313dc5fcec9f'
IDS={'hz_bb3be46493', 'hz_3103b69f86', 'hz_fc367b6cc9', 'hz_b21eb488f9', 'hz_b62ffb0c38', 'hz_705c796ea5', 'hz_ac862ca3a5', 'hz_eaed0c847a', 'hz_a6f74ddf4d', 'hz_9c1c9a7059', 'hz_a6290e1609', 'hz_f5647e5861', 'hz_92481f469e', 'hz_0e8ffd8f13', 'hz_a987061c82', 'hz_640786fb4e', 'hz_a6a13b0afc', 'hz_364dd45623', 'hz_4b83f4a8fb', 'hz_c54fd287ae'}
def load(path):
 with (gzip.open(path,'rt',encoding='utf8') if str(path).endswith('.gz') else open(path,encoding='utf8')) as f:return json.load(f)
def validate(m):
 sha=hashlib.sha256(json.dumps(m,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 if sha!=SHA or m.get('schema')!='eternal-r2-1312-1361-ce-hazards-v1' or len(m.get('moves',[]))!=20:raise ValueError('Manifest does not match review')
 if {u['event_id'] for u in m['moves']}!=IDS:raise ValueError('Wrong IDs')
 if sorted(u['source_index'] for u in m['moves'])!=[u['source_index'] for u in m['moves']]:raise ValueError('Moves must be in original order')
 for u in m['moves']:
  b,a=u['before'],u['after'];id=u['event_id']
  if u['from_pack']!=HAZ or u['to_pack']!=REG or b['id']!=id or a['id']!=id:raise ValueError('Wrong move')
  if set(a)!=set(b)|{'r2SourceEvidence'} or {k for k in b if a[k]!=b[k]}-{'name','start','end','kind','effect','confidence','lat','lon','radiusKm'}:raise ValueError('Unexpected changes')
  if (a['kind'],a['effect'])!=('cultural','note') or a['confidence'] not in ('uncertain_date','uncertain_location_effect') or not a['r2SourceEvidence']['sources']:raise ValueError('Invalid note')
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
