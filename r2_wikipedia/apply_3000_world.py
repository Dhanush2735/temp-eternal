#!/usr/bin/env python3
"""Guarded stage/apply/rollback of approximate historical context notes.
Each pack is atomically replaced, but a crash across packs is not atomic.
"""
import argparse,copy,gzip,json,re
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent
HISTORY=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
MANIFEST=ROOT/'r2_wikipedia/reviews/3000_bce_world_2026-10.json'
STAGE=Path('/home/user/.cache/r2_storage/world_3000_stage')
PACKS={'events_wikipedia.json.gz','events_wikipedia_regional.json.gz'}
SPECS={
 'r2_harappa_ravi_c3000':('events_wikipedia.json.gz',30.62889,72.86389,20,'wikipedia_coord',r'harapp|ravi phase'),
 'r2_dholavira_early_c3000':('events_wikipedia.json.gz',23.88861,70.21364,20,'wikipedia_coord',r'dholav'),
 'r2_shahr_sukhteh_c3000':('events_wikipedia.json.gz',30.59528,61.32639,20,'wikipedia_coord',r'shahr[- -]?(?:e|i)?[ -]?(?:sukht|sokht)|burnt city'),
 'r2_supe_valley_c3000':('events_wikipedia_regional.json.gz',-10.89361,-77.52028,80,'wikipedia_region',r'supe|caral|norte chico'),
 'r2_valdivia_coast_c3000':('events_wikipedia_regional.json.gz',-2.36528,-80.65361,100,'wikipedia_region',r'valdivia|real alto|chanduy'),
}
def validate(a):
 e=a['event'];id=e['id']
 if id not in SPECS:raise ValueError('Unexpected event id: '+str(id))
 pack,lat,lon,radius,confidence,_=SPECS[id]
 if (a['pack'],e['lat'],e['lon'],e['radiusKm'],e['confidence'])!=(pack,lat,lon,radius,confidence):raise ValueError('Unexpected pack or location: '+id)
 if (e['start'],e['end'],e['kind'],e['effect'])!=(-3000,-2999,'cultural','note'):raise ValueError('Unexpected date or type: '+id)
 if not e['name'].startswith('c. 3000 BC:') or not e['r2SourceEvidence'].get('sources') or not e['r2SourceEvidence'].get('review_note'):raise ValueError('Missing label or evidence: '+id)
def transform(doc,adds,reverse=False):
 if not isinstance(doc.get('events'),list):raise ValueError('Missing event list')
 out=copy.deepcopy(doc);seen=set()
 for a in adds:
  validate(a);e=a['event'];id=e['id']
  if id in seen:raise ValueError('Duplicate addition id')
  seen.add(id);hits=[i for i,r in enumerate(out['events']) if isinstance(r,dict) and r.get('id')==id]
  if reverse:
   if len(hits)!=1 or out['events'][hits[0]]!=e:raise ValueError('New record modified or missing: '+id)
   del out['events'][hits[0]]
  else:
   if hits:raise ValueError('ID already exists: '+id)
   out['events'].append(copy.deepcopy(e))
 return out
def duplicate_check(m):
 idx=json.loads((HISTORY/'index.json').read_text(encoding='utf8'))
 if not PACKS.issubset(set(idx['packs'])):raise ValueError('Target pack not indexed')
 for fn in idx['packs']:
  with (gzip.open(HISTORY/fn,'rt',encoding='utf8') if fn.endswith('.gz') else open(HISTORY/fn,encoding='utf8')) as f:doc=json.load(f)
  for row in doc.get('events',[]):
   if not isinstance(row,dict):continue
   if row.get('id') in SPECS:raise ValueError('ID already indexed: '+str(row.get('id')))
   start=row.get('start',row.get('year'));end=row.get('end',start+1 if isinstance(start,int) else None)
   if isinstance(start,int) and isinstance(end,int) and start<=-3000<end:
    for spec in SPECS.values():
     if re.search(spec[-1],str(row.get('name','')),re.I):raise ValueError('Possible overlapping event: '+str(row.get('id')))
def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);a=p.parse_args()
 m=json.loads(MANIFEST.read_text(encoding='utf8'));adds=m['additions']
 if m.get('schema')!='eternal-r2-3000bce-world-v1' or len(adds)!=len(SPECS) or {x['event']['id'] for x in adds}!=set(SPECS):raise ValueError('Invalid manifest')
 for item in adds:validate(item)
 if a.action!='rollback':duplicate_check(m)
 outputs={}
 for pack in sorted(PACKS):
  with gzip.open(HISTORY/pack,'rt',encoding='utf8') as f:doc=json.load(f)
  chosen=[x for x in adds if x['pack']==pack];out=transform(doc,chosen,a.action=='rollback')
  if transform(out,chosen,a.action!='rollback')!=doc:raise ValueError('Logical rollback failed')
  outputs[pack]=out
 for pack,out in outputs.items():write_atomic_gzip((STAGE if a.action=='stage' else HISTORY)/pack,out)
 print(a.action,'complete:',len(adds),'new approximate context notes')
if __name__=='__main__':main()
