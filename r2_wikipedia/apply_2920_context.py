#!/usr/bin/env python3
"""Stage/apply/strict rollback for two notes and one site; pack writes are separately atomic."""
import argparse,copy,gzip,json,re
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/2920_bce_troy_anedjib_2026-10.json';STAGE=Path('/home/user/.cache/r2_storage/2920_context_stage');E='events_wikipedia.json.gz';S='places_pleiades.json.gz';R='events_wikipedia_regional.json.gz';T='wpy_cfc31e881d';I='pl_550595';A='r2_anedjib_death_estimate_c2920'
def validate(m):
 if m['schema']!='eternal-r2-2920bce-v1' or (m['troy_event']['pack'],m['troy_site']['pack'],m['anedjib_event']['pack'])!=(E,S,R):raise ValueError('Invalid schema or packs')
 b,a=m['troy_event']['before'],m['troy_event']['after'];sb,sa=m['troy_site']['before'],m['troy_site']['after'];e=m['anedjib_event']['event']
 if b['id']!=T or a['id']!=T or set(a)-set(b)!={'r2SourceEvidence'} or {k for k in b if a[k]!=b[k]}!={'name','kind','effect','confidence'}:raise ValueError('Bad event correction')
 if (a['start'],a['end'],a['lat'],a['lon'],a['radiusKm'],a['kind'],a['effect'],a['confidence'])!=(-2920,-2919,39.9575,26.23889,20,'cultural','note','wikipedia_coord') or 'dates vary' not in a['name']:raise ValueError('Bad Troy event')
 if sb['id']!=I or sa['id']!=I or sb['civHint']!='egypt_ancient' or sa['civHint']!='' or set(sa)-set(sb)!={'r2SourceEvidence'} or {k for k in sb if sa[k]!=sb[k]}!={'civHint'}:raise ValueError('Bad site correction')
 if (e['id'],e['start'],e['end'],e['lat'],e['lon'],e['radiusKm'],e['kind'],e['effect'],e['confidence'])!=(A,-2920,-2919,26.175,31.9083,100,'cultural','note','wikipedia_region'):raise ValueError('Bad Anedjib event')
 if not all(x in e['name'] for x in ('One estimate','debated')) or any(len(x['r2SourceEvidence']['sources'])<3 for x in (a,sa,e)):raise ValueError('Missing provenance or caveat')
def transform(doc,m,pack,reverse=False):
 validate(m);out=copy.deepcopy(doc);sec='sites' if pack==S else 'events';rows=out.get(sec)
 if not isinstance(rows,list):raise ValueError('No rows')
 if pack in (E,S):
  u=m['troy_event' if pack==E else 'troy_site'];old,new=(u['after'],u['before']) if reverse else (u['before'],u['after']);hits=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==old['id']]
  if len(hits)!=1 or rows[hits[0]]!=old:raise ValueError('Missing or changed target')
  rows[hits[0]]=copy.deepcopy(new)
 elif pack==R:
  event=m['anedjib_event']['event'];hits=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==A]
  if reverse:
   if len(hits)!=1 or rows[hits[0]]!=event:raise ValueError('Missing or changed addition')
   del rows[hits[0]]
  else:
   if hits:raise ValueError('Duplicate addition')
   rows.append(copy.deepcopy(event))
 else:raise ValueError('Unknown pack')
 return out
def check_index(reverse):
 packs=json.loads((H/'index.json').read_text())['packs'];spec={T:(E,'events'),I:(S,'sites'),A:(R,'events')};count={i:0 for i in spec}
 if not {E,S,R}.issubset(packs):raise ValueError('Unindexed pack')
 for p in packs:
  with (gzip.open(H/p,'rt',encoding='utf8') if p.endswith('.gz') else open(H/p,encoding='utf8')) as f:d=json.load(f)
  for sec in ('events','sites'):
   for row in d.get(sec,[]):
    if not isinstance(row,dict):continue
    ident=row.get('id')
    if ident in spec:
     if (p,sec)!=spec[ident]:raise ValueError('Shared ID')
     count[ident]+=1
    if sec=='events' and ident!=A and re.search(r'anedjib|\badjib\b|anezib',str(row.get('name','')),re.I):
     start=row.get('start',row.get('year'));end=row.get('end',start+1 if isinstance(start,int) else None)
     if isinstance(start,int) and isinstance(end,int) and start<=-2920<end:raise ValueError('Possible duplicate Anedjib note')
 if count!={T:1,I:1,A:1 if reverse else 0}:raise ValueError('Unexpected ID count')
def run(action):
 m=json.loads(M.read_text());validate(m);rev=action=='rollback';check_index(rev);outputs={}
 for pack in (E,S,R):
  with gzip.open(H/pack,'rt') as f:doc=json.load(f)
  out=transform(doc,m,pack,rev)
  if transform(out,m,pack,not rev)!=doc:raise ValueError('Roundtrip failed')
  outputs[pack]=out
 for pack,out in outputs.items():write_atomic_gzip((STAGE if action=='stage' else H)/pack,out)
 print(action,'two events and one site (atomic per pack; not across packs)')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
