#!/usr/bin/env python3
"""Guarded site pack stage/apply/rollback; per-file atomic, not cross-file atomic."""
import argparse,copy,gzip,json,os,stat,tempfile
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent
HISTORY=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
MANIFEST=ROOT/'r2_wikipedia/reviews/early_site_attribution_2026-10.json'
STAGE=Path('/home/user/.cache/r2_storage/early_site_stage')
P='places_pleiades.json.gz';A='americas.json';PACKS={P,A}
SPECS={'pl_377547413':(P,-3550,-1799),'pl_229296321':(P,-5000,-3299),'caral':(A,-2600,-2000)}
def validate(u):
 id=u['site_id'];b=u['before'];a=u['after']
 if id not in SPECS or b.get('id')!=id or a.get('id')!=id:raise ValueError('Bad site ID')
 if (u['pack'],a['occupiedStart'],a['occupiedEnd'])!=SPECS[id]:raise ValueError('Bad pack or date')
 if a.get('civHint')!='' or not b.get('civHint'):raise ValueError('Unexpected hint')
 if set(a)-set(b)!={'r2SourceEvidence'} or 'r2SourceEvidence' in b:raise ValueError('Evidence mismatch')
 changes={k for k in b if b[k]!=a[k]}
 allowed={'civHint','occupiedStart','occupiedEnd'} if id=='pl_377547413' else ({'civHint','note'} if id=='caral' else {'civHint'})
 if 'civHint' not in changes or changes-allowed:raise ValueError('Unexpected changes')
 e=a['r2SourceEvidence']
 if not e.get('sources') or not e.get('review_note'):raise ValueError('Missing evidence')
def transform(doc,updates,reverse=False):
 if not isinstance(doc.get('sites'),list):raise ValueError('Missing site list')
 out=copy.deepcopy(doc);seen=set()
 for u in updates:
  validate(u);id=u['site_id']
  if id in seen:raise ValueError('Duplicate update')
  seen.add(id);hits=[i for i,r in enumerate(out['sites']) if isinstance(r,dict) and r.get('id')==id]
  if len(hits)!=1:raise ValueError('Missing or duplicate ID: '+id)
  expected,replacement=(u['after'],u['before']) if reverse else (u['before'],u['after'])
  if out['sites'][hits[0]]!=expected:raise ValueError('Changed target: '+id)
  out['sites'][hits[0]]=copy.deepcopy(replacement)
 return out
def atomic_json(path,doc):
 path.parent.mkdir(parents=True,exist_ok=True);mode=stat.S_IMODE(path.stat().st_mode) if path.exists() else None
 fd,tmp=tempfile.mkstemp(prefix='.reviewed-sites-',suffix='.json',dir=path.parent)
 try:
  with os.fdopen(fd,'w',encoding='utf8') as f:json.dump(doc,f,ensure_ascii=False,indent=2);f.write('\n')
  with open(tmp,encoding='utf8') as f:
   if json.load(f)!=doc:raise ValueError('Write mismatch')
  if mode is not None:os.chmod(tmp,mode)
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def check_shared_ids():
 idx=json.loads((HISTORY/'index.json').read_text(encoding='utf8'))
 if not PACKS.issubset(idx['packs']):raise ValueError('Not indexed')
 counts={k:0 for k in SPECS}
 for name in idx['packs']:
  with (gzip.open(HISTORY/name,'rt',encoding='utf8') if name.endswith('.gz') else open(HISTORY/name,encoding='utf8')) as f:doc=json.load(f)
  for row in doc.get('sites',[]):
   if isinstance(row,dict) and row.get('id') in counts:
    if SPECS[row['id']][0]!=name:raise ValueError('Shared ID')
    counts[row['id']]+=1
 if any(n!=1 for n in counts.values()):raise ValueError('Missing or duplicate site ID')
def run(action):
 m=json.loads(MANIFEST.read_text(encoding='utf8'));updates=m['updates']
 if m.get('schema')!='eternal-r2-early-sites-v1' or len(updates)!=len(SPECS) or {u['site_id'] for u in updates}!=set(SPECS):raise ValueError('Bad manifest')
 for u in updates:validate(u)
 check_shared_ids();outputs={}
 for p in sorted(PACKS):
  with (gzip.open(HISTORY/p,'rt',encoding='utf8') if p.endswith('.gz') else open(HISTORY/p,encoding='utf8')) as f:doc=json.load(f)
  group=[u for u in updates if u['pack']==p];out=transform(doc,group,action=='rollback')
  if transform(out,group,action!='rollback')!=doc:raise ValueError('Rollback mismatch')
  outputs[p]=out
 for p,out in outputs.items():
  path=(STAGE if action=='stage' else HISTORY)/p
  (write_atomic_gzip if p.endswith('.gz') else atomic_json)(path,out)
 print(action,'completed: three site records')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
