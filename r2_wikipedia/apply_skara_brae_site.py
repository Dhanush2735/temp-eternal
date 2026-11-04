#!/usr/bin/env python3
"""Guarded, reversible Skara Brae hint correction."""
import argparse,copy,gzip,hashlib,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
R=Path(__file__).resolve().parent.parent
H=R/'eternal/src/main/resources/data/eternalengine/eternal/history'
M=R/'r2_wikipedia/reviews/skara_brae_site_attribution_2026-10.json'
STAGE=Path('/tmp/eternal-skara-brae-stage')
SHA='71d629f6f5603bd2cebffec22a375fe372b3375f4dd7a9f28eb12c04f11d7937'
ID='pl_80606012';PACK='places_pleiades.json.gz'
def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else open(p,encoding='utf8')) as f:return json.load(f)
def validate(m):
 if hashlib.sha256(json.dumps(m,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()!=SHA:raise ValueError('Manifest changed')
 if m.get('schema')!='eternal-r2-skara-brae-site-v1' or len(m.get('updates',[]))!=1:raise ValueError('Invalid manifest')
 u=m['updates'][0];a=u['after'];b=u['before']
 if u['pack']!=PACK or u['site_id']!=ID or b['id']!=ID or a['id']!=ID or b['civHint']!='rome' or a['civHint']!='':raise ValueError('Unexpected change')
 if any(a.get(k)!=v for k,v in b.items() if k!='civHint') or set(a)-set(b)!={'r2SourceEvidence'}:raise ValueError('Unexpected fields')
 return u
def transform(doc,u,reverse=False):
 out=copy.deepcopy(doc);rows=out['sites'];ix=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==ID]
 if len(ix)!=1:raise ValueError('ID missing or duplicate')
 before,after=(u['after'],u['before']) if reverse else (u['before'],u['after'])
 if rows[ix[0]]!=before:raise ValueError('Target changed')
 rows[ix[0]]=copy.deepcopy(after);return out
def run(action):
 u=validate(load(M));idx=load(H/'index.json');count=0
 for p in idx['packs']:
  doc=load(H/p)
  for key in ('sites','events'):
   for row in doc.get(key,[]):
    if isinstance(row,dict) and row.get('id')==ID:
     if p!=PACK or key!='sites':raise ValueError('Unexpected ID location')
     count+=1
 if count!=1:raise ValueError('ID not unique')
 original=load(H/PACK);reverse=action=='rollback';out=transform(original,u,reverse)
 if transform(out,u,not reverse)!=original:raise ValueError('Roundtrip failed')
 write_atomic_gzip((STAGE if action=='stage' else H)/PACK,out)
 print(action,'completed for',ID)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
