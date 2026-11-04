#!/usr/bin/env python3
"""Guarded addition/rollback of one researched Bryn Celli Ddu gameplay event."""
import argparse,copy,gzip,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent
HISTORY=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
PACK=HISTORY/'events_wikipedia.json.gz'
MANIFEST=ROOT/'r2_wikipedia/reviews/3000_bce_bryn_celli_ddu_2026-10.json'
STAGE=Path('/home/user/.cache/r2_storage/bryn_staged.json.gz')

def validate(m):
 e=m['event']
 if m.get('schema')!='eternal-r2-reviewed-new-event-v1' or m.get('target')!=PACK.name:raise ValueError('Wrong manifest')
 if e.get('id')!='r2_bryn_celli_ddu_c3000' or e.get('start')!=-3000 or e.get('end')!=-2999:raise ValueError('Unexpected ID/date')
 if not e['name'].startswith('c. 3000 BC:') or e['kind']!='cultural' or e['effect']!='note':raise ValueError('Wrong event semantics')
 if e['lat']!=53.2077 or e['lon']!=-4.2361 or e['radiusKm']!=20:raise ValueError('Wrong location/radius')
 if not e.get('r2SourceEvidence',{}).get('other_sources'):raise ValueError('No corroboration')
 return e

def transform(doc,m,reverse=False):
 e=validate(m);events=doc['events'];matches=[i for i,x in enumerate(events) if isinstance(x,dict) and x.get('id')==e['id']]
 out=copy.deepcopy(doc)
 if reverse:
  if len(matches)!=1 or events[matches[0]]!=e:raise ValueError('Installed row changed')
  del out['events'][matches[0]]
 else:
  if matches:raise ValueError('Event ID already present')
  out['events'].append(copy.deepcopy(e))
 return out

def reject_known_duplicates(e):
 idx=json.loads((HISTORY/'index.json').read_text(encoding='utf8'))
 if PACK.name not in idx['packs']:raise ValueError('Pack not indexed')
 for name in idx['packs']:
  with (gzip.open(HISTORY/name,'rt',encoding='utf8') if name.endswith('.gz') else open(HISTORY/name,encoding='utf8')) as f:d=json.load(f)
  for section in ('events','sites'):
   for row in d.get(section,[]):
    if isinstance(row,dict) and (row.get('id')==e['id'] or 'bryn celli ddu' in str(row.get('name','')).lower()):raise ValueError('Possible duplicate: '+name+' '+str(row.get('id')))

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);a=p.parse_args()
 m=json.loads(MANIFEST.read_text(encoding='utf8'));e=validate(m)
 with gzip.open(PACK,'rt',encoding='utf8') as f:doc=json.load(f)
 if a.action!='rollback':reject_known_duplicates(e)
 out=transform(doc,m,a.action=='rollback');assert transform(out,m,a.action!='rollback')==doc
 write_atomic_gzip(STAGE if a.action=='stage' else PACK,out)
 print(a.action,'completed:',e['id'])
if __name__=='__main__':main()
