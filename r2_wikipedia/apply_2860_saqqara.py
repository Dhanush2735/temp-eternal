#!/usr/bin/env python3
"""Install one qualified archaeological reference, with strict undo."""
import argparse,copy,gzip,json,re
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/2860_bce_saqqara_2026-10.json';PACK='events_wikipedia_regional.json.gz';STAGE=Path('/home/user/.cache/r2_storage/2860_saqqara_stage');ID='r2_saqqara_gallery_reference_c2860'
def validate(m):
 e=m['event']
 if (m['schema'],m['pack'])!=('eternal-r2-2860bce-v1',PACK):raise ValueError('Invalid manifest')
 if (e['id'],e['start'],e['end'],e['lat'],e['lon'],e['radiusKm'],e['kind'],e['effect'],e['confidence'])!=(ID,-2860,-2859,29.87111,31.21639,25,'cultural','note','wikipedia_region'):raise ValueError('Invalid event')
 if not all(s in e['name'] for s in ('One date proposed','Saqqara','timing and attribution uncertain')) or len(e['r2SourceEvidence']['sources'])<5:raise ValueError('Missing caveat')
def transform(doc,event,reverse=False):
 if not isinstance(doc.get('events'),list):raise ValueError('No events')
 o=copy.deepcopy(doc);hits=[i for i,r in enumerate(o['events']) if isinstance(r,dict) and r.get('id')==ID]
 if reverse:
  if len(hits)!=1 or o['events'][hits[0]]!=event:raise ValueError('Missing/modified event')
  del o['events'][hits[0]]
 else:
  if hits:raise ValueError('Duplicate event')
  o['events'].append(copy.deepcopy(event))
 return o
def check_index(reverse):
 packs=json.loads((H/'index.json').read_text())['packs'];n=0
 if PACK not in packs:raise ValueError('Not indexed')
 for p in packs:
  with (gzip.open(H/p,'rt',encoding='utf8') if p.endswith('.gz') else open(H/p,encoding='utf8')) as f:d=json.load(f)
  for sec in ('events','sites'):
   for r in d.get(sec,[]):
    if not isinstance(r,dict):continue
    id=r.get('id');start=r.get('start');end=r.get('end')
    if id==ID:
     if (p,sec)!=(PACK,'events'):raise ValueError('Shared ID')
     n+=1
    if sec=='events' and id!=ID and re.search(r'saqqara|sakkara|saccara|gallery tomb|tomb a\b',str(r.get('name','')),re.I) and isinstance(start,int) and isinstance(end,int) and start<=-2860<end:raise ValueError('Possible overlapping named event: '+str(id))
 if n!=(1 if reverse else 0):raise ValueError('Wrong ID count')
def run(action):
 m=json.loads(M.read_text());validate(m);rev=action=='rollback';check_index(rev)
 with gzip.open(H/PACK,'rt',encoding='utf8') as f:d=json.load(f)
 out=transform(d,m['event'],rev)
 if transform(out,m['event'],not rev)!=d:raise ValueError('Roundtrip failure')
 write_atomic_gzip((STAGE if action=='stage' else H)/PACK,out)
 print(action,'one qualified Saqqara context note')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
