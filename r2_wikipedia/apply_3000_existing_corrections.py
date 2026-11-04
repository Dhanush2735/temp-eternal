#!/usr/bin/env python3
"""Stage/apply/strict rollback for reviewed rows, individually atomic pack writes."""
import argparse,copy,gzip,json,re
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent
HISTORY=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
MANIFEST=ROOT/'r2_wikipedia/reviews/3000_bce_existing_corrections_2026-10.json'
STAGE=Path('/home/user/.cache/r2_storage/3000_existing_stage')
P='events_wikipedia.json.gz';Q='events_wikipedia_regional.json.gz';PACKS={P,Q}
SPECS={
 'wpy_5d4804a20a':(P,-2600,-2599,36.4,118.4,200,'wikipedia_region'),
 'wpy_75cae27825':(P,-3000,-2999,10.25861,-75.34611,50,'wikipedia_region'),
 'wpy_d3c69e6bff':(P,-3000,-2999,25.90167,32.72417,100,'wikipedia_region'),
 'wpy_0155748eec':(P,-3000,-2999,53.69473,-6.47557,20,'wikipedia_year_page'),
 'wpr_17d9b47607':(Q,-3000,-2999,29.638,31.2209,269,'wikipedia_region'),
}
def validate(u):
 before,after,id=u['before'],u['after'],u['event_id']
 if id not in SPECS or before.get('id')!=id or after.get('id')!=id:raise ValueError('Bad ID')
 if (before['start'],before['end'])!=(-3000,-2999):raise ValueError('Unexpected old year')
 if set(after)-set(before)!={'r2SourceEvidence'} or 'r2SourceEvidence' in before:raise ValueError('Evidence mismatch')
 changed={k for k in before if before[k]!=after[k]}
 if not changed or changed-{'name','lat','lon','radiusKm','start','end','confidence','kind','effect'}:raise ValueError('Unexpected fields')
 if (u['pack'],after['start'],after['end'],after['lat'],after['lon'],after['radiusKm'],after['confidence'])!=SPECS[id]:raise ValueError('Unexpected slot or coordinate')
 if after['kind']!='cultural' or after['effect']!='note' or not after['name'].startswith('c. '+('2600' if id=='wpy_5d4804a20a' else '3000')+' BC:'):raise ValueError('Unexpected label or gameplay effect')
 e=after['r2SourceEvidence']
 if not e.get('sources') or not e.get('review_note'):raise ValueError('Missing source evidence')
def transform(doc,updates,reverse=False):
 if not isinstance(doc.get('events'),list):raise ValueError('No event list')
 out=copy.deepcopy(doc);seen=set()
 for u in updates:
  validate(u);id=u['event_id']
  if id in seen:raise ValueError('Duplicate update')
  seen.add(id);hits=[i for i,r in enumerate(out['events']) if isinstance(r,dict) and r.get('id')==id]
  if len(hits)!=1:raise ValueError('Missing or duplicate ID')
  old,new=(u['after'],u['before']) if reverse else (u['before'],u['after'])
  if out['events'][hits[0]]!=old:raise ValueError('Target row changed: '+id)
  out['events'][hits[0]]=copy.deepcopy(new)
 return out
def duplicate_check():
 idx=json.loads((HISTORY/'index.json').read_text(encoding='utf8'))
 if not PACKS.issubset(set(idx['packs'])):raise ValueError('Pack not indexed')
 for fn in idx['packs']:
  with (gzip.open(HISTORY/fn,'rt',encoding='utf8') if fn.endswith('.gz') else open(HISTORY/fn,encoding='utf8')) as f:doc=json.load(f)
  for row in doc.get('events',[]):
   if not isinstance(row,dict):continue
   if row.get('id') in SPECS and fn!=SPECS[row['id']][0]:raise ValueError('Target ID shared with another pack')
   start=row.get('start',row.get('year'));end=row.get('end',start+1 if isinstance(start,int) else None);name=str(row.get('name',''))
   if row.get('id')!='wpy_5d4804a20a' and isinstance(start,int) and isinstance(end,int) and start<=-2600<end and (re.search(r'wheat',name,re.I) and re.search(r'china|shandong|yellow river',name,re.I)):
    raise ValueError('Possible duplicate Chinese wheat event: '+str(row.get('id')))
def run(action):
 m=json.loads(MANIFEST.read_text(encoding='utf8'));updates=m['updates']
 if m.get('schema')!='eternal-r2-3000bce-existing-v1' or len(updates)!=len(SPECS) or {u['event_id'] for u in updates}!=set(SPECS):raise ValueError('Bad manifest')
 for u in updates:validate(u)
 if action!='rollback':duplicate_check()
 outputs={}
 for pack in sorted(PACKS):
  with gzip.open(HISTORY/pack,'rt',encoding='utf8') as f:doc=json.load(f)
  batch=[u for u in updates if u['pack']==pack];out=transform(doc,batch,action=='rollback')
  if transform(out,batch,action!='rollback')!=doc:raise ValueError('Rollback mismatch')
  outputs[pack]=out
 for pack,out in outputs.items():write_atomic_gzip((STAGE if action=='stage' else HISTORY)/pack,out)
 print(action,'completed: five reviewed record corrections')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
