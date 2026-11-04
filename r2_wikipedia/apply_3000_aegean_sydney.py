#!/usr/bin/env python3
"""Apply/rollback a small reviewed 3000 BCE batch.

Dates are gameplay references only. Each pack is atomically replaced; a process
crash between two writes is not cross-file atomic. Manifest permits rollback.
"""
import argparse,copy,gzip,json,math
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent
HISTORY=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
MANIFEST=ROOT/'r2_wikipedia/reviews/3000_bce_aegean_sydney_2026-10.json'
PACKS={'events_wikipedia.json.gz','events_wikipedia_regional.json.gz'}
STAGE=Path('/home/user/.cache/r2_storage/aegean_sydney_stage')

def transform(doc,updates,additions,reverse=False):
 events=doc.get('events')
 if not isinstance(events,list):raise ValueError('Missing event list')
 out=copy.deepcopy(doc);seen=set()
 for u in updates:
  old,new,eid=u['before'],u['after'],u['event_id']
  if eid in seen or old.get('id')!=eid or new.get('id')!=eid:raise ValueError('Mismatched or duplicate ID')
  seen.add(eid)
  if old.get('start')!=-3000 or old.get('end')!=-2999:raise ValueError('Unexpected original year')
  if 'r2SourceEvidence' in old or set(new)-set(old)!={'r2SourceEvidence'}:raise ValueError('Unexpected evidence')
  changed={k for k in old if old[k]!=new[k]}
  if not changed or changed-{'name','confidence','radiusKm','kind'}:raise ValueError('Unexpected field changed')
  if not new['name'].startswith('c. 3000 BC:') or not new['r2SourceEvidence'].get('sources'):raise ValueError('Missing date label or sources')
  if new['kind']!='cultural' or new['effect']!='note':raise ValueError('Unsupported gameplay kind/effect')
  if 'confidence' in changed and new['confidence']!='wikipedia_region':raise ValueError('Unexpected confidence change')
  if 'radiusKm' in changed and (isinstance(new['radiusKm'],bool) or not 0<new['radiusKm']<=200):raise ValueError('Unsupported radius change')
  hits=[i for i,r in enumerate(events) if isinstance(r,dict) and r.get('id')==eid]
  if len(hits)!=1:raise ValueError('Missing or duplicate target ID')
  expected=new if reverse else old
  if events[hits[0]]!=expected:raise ValueError('Existing target changed')
  out['events'][hits[0]]=copy.deepcopy(old if reverse else new)
 for a in additions:
  e=a['event'];eid=e['id']
  if eid in seen or eid!='r2_knossos_early_minoan_c3000':raise ValueError('Unexpected new ID')
  seen.add(eid)
  if (e['start'],e['end'],e['lat'],e['lon'],e['radiusKm'])!=(-3000,-2999,35.29806,25.16306,20):raise ValueError('Unexpected new date or location')
  if not e['name'].startswith('c. 3000 BC:') or e['kind']!='cultural' or e['effect']!='note' or not e['r2SourceEvidence'].get('sources'):raise ValueError('Invalid new event')
  hits=[i for i,r in enumerate(out['events']) if isinstance(r,dict) and r.get('id')==eid]
  if reverse:
   if len(hits)!=1 or out['events'][hits[0]]!=e:raise ValueError('New record changed or missing')
   del out['events'][hits[0]]
  else:
   if hits:raise ValueError('New event already exists')
   out['events'].append(copy.deepcopy(e))
 return out

def duplicate_check(m):
 # Scan events only: an already-existing occupied site and a new historical
 # note about its culture are not automatically duplicate runtime records.
 idx=json.loads((HISTORY/'index.json').read_text(encoding='utf8'))
 if not PACKS.issubset(set(idx['packs'])):raise ValueError('Pack not indexed')
 for name in idx['packs']:
  with (gzip.open(HISTORY/name,'rt',encoding='utf8') if name.endswith('.gz') else open(HISTORY/name,encoding='utf8')) as f:d=json.load(f)
  for row in d.get('events',[]):
   if not isinstance(row,dict):continue
   if row.get('id')=='r2_knossos_early_minoan_c3000':raise ValueError('New ID already exists')
   start=row.get('start',row.get('year'));end=row.get('end',start+1 if isinstance(start,int) else None)
   namefield=str(row.get('name','')).lower()
   if isinstance(start,int) and isinstance(end,int) and start<=-3000<end and ('knossos' in namefield or 'cnossus' in namefield):raise ValueError('Possible existing Knossos event: '+str(row.get('id')))

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);a=p.parse_args()
 m=json.loads(MANIFEST.read_text(encoding='utf8'))
 if m.get('schema')!='eternal-r2-3000bce-aegean-sydney-v1':raise ValueError('Invalid manifest')
 if {u['pack'] for u in m['updates']}|{u['pack'] for u in m['additions']}!=PACKS:raise ValueError('Unexpected packs')
 if a.action!='rollback':duplicate_check(m)
 outputs={}
 for name in sorted(PACKS):
  with gzip.open(HISTORY/name,'rt',encoding='utf8') as f:doc=json.load(f)
  us=[u for u in m['updates'] if u['pack']==name];adds=[x for x in m['additions'] if x['pack']==name]
  out=transform(doc,us,adds,a.action=='rollback')
  if transform(out,us,adds,a.action!='rollback')!=doc:raise ValueError('Logical rollback mismatch')
  outputs[name]=out
 for name,out in outputs.items():write_atomic_gzip((STAGE if a.action=='stage' else HISTORY)/name,out)
 print(a.action,'complete:',len(m['updates']),'corrections and',len(m['additions']),'addition')
if __name__=='__main__':main()
