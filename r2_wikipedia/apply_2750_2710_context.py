#!/usr/bin/env python3
"""Stage/apply/strict rollback for one corrected note, a site hint and one new note; pack writes are separately atomic."""
import argparse,copy,gzip,json,re
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/2750_2710_bce_context_2026-10.json';STAGE=Path('/home/user/.cache/r2_storage/2750_2710_stage');E='events_wikipedia.json.gz';S='places_pleiades.json.gz';R='events_wikipedia_regional.json.gz';T='wpy_6ff93fd0ea';I='pl_734000266';A='r2_keros_dhaskalio_phase_a_context'
def validate(m):
 if m['schema']!='eternal-r2-2750-2710-v1' or (m['tyre_event']['pack'],m['daskalio_site']['pack'],m['keros_context']['pack'])!=(E,S,R):raise ValueError('Invalid schema or packs')
 b,a=m['tyre_event']['before'],m['tyre_event']['after'];sb,sa=m['daskalio_site']['before'],m['daskalio_site']['after'];e=m['keros_context']['event']
 if b['id']!=T or a['id']!=T or set(a)-set(b)!={'r2SourceEvidence'} or {k for k in b if a[k]!=b[k]}!={'name','kind','effect'}:raise ValueError('Bad Tyre correction')
 if (a['start'],a['end'],a['lat'],a['lon'],a['radiusKm'],a['kind'],a['effect'],a['confidence'])!=(-2750,-2749,33.26667,35.2,20,'cultural','note','wikipedia_year_page') or 'date uncertain' not in a['name']:raise ValueError('Bad Tyre event')
 if sb['id']!=I or sa['id']!=I or sb['civHint']!='minoan' or sa['civHint']!='' or set(sa)-set(sb)!={'r2SourceEvidence'} or {k for k in sb if sa[k]!=sb[k]}!={'civHint'}:raise ValueError('Bad site correction')
 if (e['id'],e['start'],e['end'],e['lat'],e['lon'],e['radiusKm'],e['kind'],e['effect'],e['confidence'])!=(A,-2750,-2549,36.887,25.604,20,'cultural','note','wikipedia_region'):raise ValueError('Bad context')
 if 'dates approximate' not in e['name'] or any(len(x['r2SourceEvidence']['sources'])<3 for x in (a,sa,e)):raise ValueError('Missing provenance or caveat')
def transform(doc,m,pack,reverse=False):
 validate(m);out=copy.deepcopy(doc);sec='sites' if pack==S else 'events';rows=out.get(sec)
 if not isinstance(rows,list):raise ValueError('No rows')
 if pack in (E,S):
  u=m['tyre_event' if pack==E else 'daskalio_site'];old,new=(u['after'],u['before']) if reverse else (u['before'],u['after']);hits=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==old['id']]
  if len(hits)!=1 or rows[hits[0]]!=old:raise ValueError('Missing or changed target')
  rows[hits[0]]=copy.deepcopy(new)
 elif pack==R:
  event=m['keros_context']['event'];hits=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==A]
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
    if sec=='events' and ident!=A and re.search(r'keros|daskali|dhaskali|kavos',str(row.get('name','')),re.I):
     start=row.get('start');end=row.get('end')
     if isinstance(start,int) and isinstance(end,int) and start < -2549 and end > -2750:raise ValueError('Possible duplicate Keros note')
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
