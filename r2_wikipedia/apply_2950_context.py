#!/usr/bin/env python3
"""Stage/install/undo one qualified person note and one focused correction."""
import argparse,copy,gzip,json,re
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/2950_bce_context_2026-10.json';PACK='events_wikipedia.json.gz';STAGE=Path('/home/user/.cache/r2_storage/2950_context_stage');OLD='wpy_96a91ec2ba';NEW='r2_merneith_regency_reference_c2950'
def validate(m):
 if (m['schema'],m['pack'])!=('eternal-r2-2950bce-v1',PACK):raise ValueError('Invalid manifest')
 b,a,e=m['before'],m['after'],m['event']
 if b['id']!=OLD or a['id']!=OLD or (b['start'],b['end'],a['start'],a['end'])!=(-2950,-2949,-2950,-2949):raise ValueError('Bad existing event')
 if set(a)-set(b)!={'r2SourceEvidence'} or {k for k in b if b[k]!=a[k]}!={'name','radiusKm','kind','effect','confidence'}:raise ValueError('Unexpected correction fields')
 if (a['lat'],a['lon'],a['radiusKm'],a['kind'],a['effect'],a['confidence'])!=(16.,-93.,400,'cultural','note','wikipedia_region') or 'timing varies' not in a['name']:raise ValueError('Bad correction values')
 if (e['id'],e['start'],e['end'],e['lat'],e['lon'],e['radiusKm'],e['kind'],e['effect'],e['confidence'])!=(NEW,-2950,-2949,26.175,31.9083,100,'cultural','note','wikipedia_region'):raise ValueError('Bad new event')
 if not all(t in e['name'] for t in ('may have','debated')) or any(len(x['r2SourceEvidence']['sources'])<3 for x in (a,e)):raise ValueError('Missing caveats')
def transform(doc,m,reverse=False):
 validate(m)
 if not isinstance(doc.get('events'),list):raise ValueError('Missing events')
 out=copy.deepcopy(doc);rows=out['events'];old=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==OLD];new=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==NEW]
 if len(old)!=1:raise ValueError('Old row missing or duplicated')
 if reverse:
  if len(new)!=1 or rows[old[0]]!=m['after'] or rows[new[0]]!=m['event']:raise ValueError('Changed row during rollback')
  rows[old[0]]=copy.deepcopy(m['before']);del rows[new[0]]
 else:
  if new or rows[old[0]]!=m['before']:raise ValueError('Target changed or new event exists')
  rows[old[0]]=copy.deepcopy(m['after']);rows.append(copy.deepcopy(m['event']))
 return out
def check_index(reverse):
 packs=json.loads((H/'index.json').read_text())['packs'];counts={OLD:0,NEW:0}
 if PACK not in packs:raise ValueError('Pack not indexed')
 for p in packs:
  with (gzip.open(H/p,'rt',encoding='utf8') if p.endswith('.gz') else open(H/p,encoding='utf8')) as f:doc=json.load(f)
  for section in ('sites','events'):
   for r in doc.get(section,[]):
    if not isinstance(r,dict):continue
    ident=r.get('id')
    if ident in counts:
     if p!=PACK or section!='events':raise ValueError('Shared ID')
     counts[ident]+=1
    if section=='events' and ident!=NEW and re.search(r'merneith|merit.?neith|meryt.?neith',str(r.get('name','')),re.I):
     start=r.get('start',r.get('year'));end=r.get('end',start+1 if isinstance(start,int) else None)
     if isinstance(start,int) and isinstance(end,int) and start<=-2950<end:raise ValueError('Possible overlap '+str(ident))
 if counts!={OLD:1,NEW:1 if reverse else 0}:raise ValueError('Unexpected ID count')
def run(action):
 m=json.loads(M.read_text());validate(m);reverse=action=='rollback';check_index(reverse)
 with gzip.open(H/PACK,'rt',encoding='utf8') as f:doc=json.load(f)
 out=transform(doc,m,reverse)
 if transform(out,m,not reverse)!=doc:raise ValueError('Rollback mismatch')
 write_atomic_gzip((STAGE if action=='stage' else H)/PACK,out)
 print(action,'one Mesoamerican correction and one Merneith context')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
