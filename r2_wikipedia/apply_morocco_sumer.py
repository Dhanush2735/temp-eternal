#!/usr/bin/env python3
"""Guarded three-pack stage/apply/rollback; individually atomic, not crash-atomic as a group."""
import argparse,copy,gzip,json,re
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;HISTORY=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
MANIFEST=ROOT/'r2_wikipedia/reviews/3000_morocco_sumer_2026-10.json';STAGE=Path('/home/user/.cache/r2_storage/morocco_sumer_stage')
P='events_wikipedia.json.gz';Q='events_wikipedia_regional.json.gz';S='places_pleiades.json.gz';PACKS={P,Q,S}
SPECS={'wpy_2e31a84306':(P,'events'),'pl_594703044':(S,'sites')};NEW='r2_oued_beht_farming_c3000'
def validate_update(u):
 id=u['id'];b=u['before'];a=u['after']
 if id not in SPECS or (u['pack'],u['section'])!=SPECS[id] or b.get('id')!=id or a.get('id')!=id:raise ValueError('Invalid update')
 if set(a)-set(b)!={'r2SourceEvidence'} or 'r2SourceEvidence' in b:raise ValueError('Unexpected evidence')
 changed={k for k in b if a[k]!=b[k]}
 allowed={'name','kind','effect','confidence','radiusKm'} if id=='wpy_2e31a84306' else {'civHint'}
 if not changed or changed-allowed:raise ValueError('Unexpected fields')
 if id=='wpy_2e31a84306' and (a['start'],a['end'],a['lat'],a['lon'],a['radiusKm'],a['kind'],a['effect'],a['confidence'])!=(-3000,-2999,32.0,45.5,100,'cultural','note','wikipedia_region'):raise ValueError('Unexpected Sumer fields')
 if id=='pl_594703044' and (b['civHint'],a['civHint'])!=('rome',''):raise ValueError('Unexpected site hint')
 if not a['r2SourceEvidence'].get('sources') or not a['r2SourceEvidence'].get('review_note'):raise ValueError('Missing evidence')
def validate_add(a):
 r=a['record']
 if (a['pack'],a['section'],r['id'],r['start'],r['end'],r['lat'],r['lon'],r['radiusKm'],r['kind'],r['effect'],r['confidence'])!=(Q,'events',NEW,-3000,-2999,33.8837,-5.93388,20,'cultural','note','wikipedia_coord'):raise ValueError('Invalid addition')
 if not r['name'].startswith('c. 3000 BC:') or not r['r2SourceEvidence'].get('sources'):raise ValueError('Missing evidence or approximation')
def transform(doc,section,updates,additions,reverse=False):
 if not isinstance(doc.get(section),list):raise ValueError('Missing section')
 out=copy.deepcopy(doc);seen=set()
 for u in updates:
  validate_update(u);id=u['id']
  if id in seen:raise ValueError('Duplicate update')
  seen.add(id);hits=[i for i,r in enumerate(out[section]) if isinstance(r,dict) and r.get('id')==id]
  if len(hits)!=1:raise ValueError('Missing or duplicate id')
  old,new=(u['after'],u['before']) if reverse else (u['before'],u['after'])
  if out[section][hits[0]]!=old:raise ValueError('Modified row')
  out[section][hits[0]]=copy.deepcopy(new)
 for a in additions:
  validate_add(a);r=a['record'];id=r['id']
  if id in seen:raise ValueError('Duplicate id')
  seen.add(id);hits=[i for i,x in enumerate(out[section]) if isinstance(x,dict) and x.get('id')==id]
  if reverse:
   if len(hits)!=1 or out[section][hits[0]]!=r:raise ValueError('Modified new row')
   del out[section][hits[0]]
  else:
   if hits:raise ValueError('Existing ID')
   out[section].append(copy.deepcopy(r))
 return out
def check_index(reverse):
 idx=json.loads((HISTORY/'index.json').read_text(encoding='utf8'))
 if not PACKS.issubset(set(idx['packs'])):raise ValueError('Not indexed')
 counts={id:0 for id in SPECS};newcount=0
 for p in idx['packs']:
  with (gzip.open(HISTORY/p,'rt',encoding='utf8') if p.endswith('.gz') else open(HISTORY/p,encoding='utf8')) as f:doc=json.load(f)
  for section in ('sites','events'):
   for r in doc.get(section,[]):
    if not isinstance(r,dict):continue
    id=r.get('id')
    if id in SPECS:
     if (p,section)!=SPECS[id]:raise ValueError('Shared update ID')
     counts[id]+=1
    if id==NEW:
     if (p,section)!=(Q,'events'):raise ValueError('Shared addition ID')
     newcount+=1
    if section=='events' and not reverse and id!=NEW:
     start=r.get('start',r.get('year'));end=r.get('end',start+1 if isinstance(start,int) else None)
     if isinstance(start,int) and isinstance(end,int) and start<=-3000<end and re.search(r'oued\s*(?:beht|baht)|baht\s*river',str(r.get('name','')),re.I):raise ValueError('Possible duplicate Oued Beht event')
 if any(v!=1 for v in counts.values()) or newcount!=(1 if reverse else 0):raise ValueError('Missing or duplicate IDs')
def run(action):
 m=json.loads(MANIFEST.read_text(encoding='utf8'));updates=m['updates'];adds=m['additions'];reverse=action=='rollback'
 if m.get('schema')!='eternal-r2-morocco-sumer-v1' or len(updates)!=2 or {x['id'] for x in updates}!=set(SPECS) or len(adds)!=1:raise ValueError('Bad manifest')
 for u in updates:validate_update(u)
 for a in adds:validate_add(a)
 check_index(reverse);outs={}
 for p in sorted(PACKS):
  with gzip.open(HISTORY/p,'rt',encoding='utf8') as f:doc=json.load(f)
  section='sites' if p==S else 'events';us=[x for x in updates if x['pack']==p];ad=[x for x in adds if x['pack']==p]
  out=transform(doc,section,us,ad,reverse)
  if transform(out,section,us,ad,not reverse)!=doc:raise ValueError('Rollback mismatch')
  outs[p]=out
 for p,doc in outs.items():write_atomic_gzip((STAGE if action=='stage' else HISTORY)/p,doc)
 print(action,'completed: 1 event correction, 1 site correction, 1 new event')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
