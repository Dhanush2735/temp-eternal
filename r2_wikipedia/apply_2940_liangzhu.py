#!/usr/bin/env python3
"""Stage, apply or strictly roll back one sourced cultural-period correction."""
import argparse,copy,gzip,json,re
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/2940_bce_liangzhu_2026-10.json';PACK='events_wikipedia.json.gz';ID='wpy_9f829b7b30';STAGE=Path('/home/user/.cache/r2_storage/2940_liangzhu_stage')
def validate(m):
 if (m['schema'],m['pack'],m['event_id'])!=('eternal-r2-2940-liangzhu-v1',PACK,ID):raise ValueError('Invalid manifest')
 b,a=m['before'],m['after']
 if b.get('id')!=ID or a.get('id')!=ID or set(a)-set(b)!={'r2SourceEvidence'}:raise ValueError('Invalid row')
 if {k for k in b if a[k]!=b[k]}!={'name','start','end','radiusKm','confidence'}:raise ValueError('Unexpected changed fields')
 if (b['start'],b['end'],a['start'],a['end'])!=(-2501,-2500,-3300,-2299):raise ValueError('Unexpected interval')
 if (a['lat'],a['lon'],a['radiusKm'],a['kind'],a['effect'],a['confidence'])!=(30.39556,119.99083,100,'cultural','note','wikipedia_region'):raise ValueError('Unexpected values')
 if 'dates approximate' not in a['name'] or len(a['r2SourceEvidence']['sources'])<2:raise ValueError('Missing qualification or sources')
def transform(doc,m,reverse=False):
 validate(m)
 if not isinstance(doc.get('events'),list):raise ValueError('No events')
 out=copy.deepcopy(doc);hits=[i for i,r in enumerate(out['events']) if isinstance(r,dict) and r.get('id')==ID]
 if len(hits)!=1:raise ValueError('Missing or duplicate ID')
 old,new=(m['after'],m['before']) if reverse else (m['before'],m['after'])
 if out['events'][hits[0]]!=old:raise ValueError('Changed target')
 out['events'][hits[0]]=copy.deepcopy(new);return out
def index_guard():
 packs=json.loads((H/'index.json').read_text())['packs'];count=0
 if PACK not in packs:raise ValueError('Not indexed')
 for p in packs:
  with (gzip.open(H/p,'rt',encoding='utf8') if p.endswith('.gz') else open(H/p,encoding='utf8')) as f:d=json.load(f)
  for sec in ('events','sites'):
   for r in d.get(sec,[]):
    if not isinstance(r,dict):continue
    if r.get('id')==ID:
     if p!=PACK or sec!='events':raise ValueError('Shared ID')
     count+=1
    if sec=='events' and r.get('id')!=ID and re.search(r'liangzhu',str(r.get('name','')),re.I):
     start=r.get('start',r.get('year'));end=r.get('end',start+1 if isinstance(start,int) else None)
     if isinstance(start,int) and isinstance(end,int) and start<=-2940<end:raise ValueError('Possible overlap '+str(r.get('id')))
 if count!=1:raise ValueError('Missing/shared ID')
def run(action):
 m=json.loads(M.read_text());validate(m);index_guard();rev=action=='rollback'
 with gzip.open(H/PACK,'rt') as f:doc=json.load(f)
 out=transform(doc,m,rev)
 if transform(out,m,not rev)!=doc:raise ValueError('Rollback mismatch')
 write_atomic_gzip((STAGE if action=='stage' else H)/PACK,out)
 print(action,'one Liangzhu period record')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
