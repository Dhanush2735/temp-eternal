#!/usr/bin/env python3
"""Reviewed 2850–2810 contexts; preflight and strict reversible changes."""
import argparse,copy,gzip,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/2850_2810_bce_context_2026-10.json.gz';STAGE=Path('/home/user/.cache/r2_storage/2850_2810_stage')
W='events_wikipedia.json.gz';R='events_wikipedia_regional.json.gz'
SPEC={'r2_shahr_sukhteh_c3000':(W,-3000,-2619,30.59528,61.32639,20,'wikipedia_coord','dates approximate'),'wpy_d5d3fad419':(W,-2832,-2831,37.5,-118.5,100,'wikipedia_region','age disputed'),'wpr_0f1699c278':(R,-2852,-2851,32.6128,113.5392,800,'wikipedia_region','not verified history'),'r2_miaodigou_ii_regional_context':(R,-3000,-2599,34.721,111.104,100,'wikipedia_region','classification debated')}
def validate(m):
 if m.get('schema')!='eternal-r2-2850-2810-v1' or len(m['updates'])!=3 or len(m['additions'])!=1:raise ValueError('Wrong manifest')
 entries=[(u['event_id'],u['pack'],u['after']) for u in m['updates']]+[(a['event']['id'],a['pack'],a['event']) for a in m['additions']]
 if {x[0] for x in entries}!=set(SPEC):raise ValueError('Wrong IDs')
 for id,pack,e in entries:
  p,st,en,lat,lon,r,conf,caveat=SPEC[id]
  if (pack,e['start'],e['end'],e['lat'],e['lon'],e['radiusKm'],e['kind'],e['effect'],e['confidence'])!=(p,st,en,lat,lon,r,'cultural','note',conf) or caveat not in e['name'] or len(e['r2SourceEvidence']['sources'])<3:raise ValueError('Invalid '+id)
 for u in m['updates']:
  b,a=u['before'],u['after']
  if b['id']!=u['event_id'] or a['id']!=u['event_id'] or set(a)!=set(b)|{'r2SourceEvidence'} or {k for k in b if b[k]!=a[k]}-{'name','end','kind','effect','confidence','lat','lon','radiusKm','r2SourceEvidence'}:raise ValueError('Unexpected change')
def transform(doc,m,pack,reverse=False):
 validate(m);o=copy.deepcopy(doc)
 if not isinstance(o.get('events'),list):raise ValueError('Missing events')
 for u in (x for x in m['updates'] if x['pack']==pack):
  hits=[i for i,r in enumerate(o['events']) if isinstance(r,dict) and r.get('id')==u['event_id']];old,new=(u['after'],u['before']) if reverse else (u['before'],u['after'])
  if len(hits)!=1 or o['events'][hits[0]]!=old:raise ValueError('Changed '+u['event_id'])
  o['events'][hits[0]]=copy.deepcopy(new)
 for a in (x for x in m['additions'] if x['pack']==pack):
  e=a['event'];hits=[i for i,r in enumerate(o['events']) if isinstance(r,dict) and r.get('id')==e['id']]
  if reverse:
   if len(hits)!=1 or o['events'][hits[0]]!=e:raise ValueError('Changed addition')
   del o['events'][hits[0]]
  else:
   if hits:raise ValueError('Duplicate addition')
   o['events'].append(copy.deepcopy(e))
 return o
def check_index(reverse):
 packs=json.loads((H/'index.json').read_text())['packs'];counts={id:0 for id in SPEC}
 if any(v[0] not in packs for v in SPEC.values()):raise ValueError('Missing indexed pack')
 for p in packs:
  with (gzip.open(H/p,'rt',encoding='utf8') if p.endswith('.gz') else open(H/p,encoding='utf8')) as f:d=json.load(f)
  for sec in ('events','sites'):
   for row in d.get(sec,[]):
    if isinstance(row,dict) and row.get('id') in counts:
     if (p,sec)!=(SPEC[row['id']][0],'events'):raise ValueError('Shared ID')
     counts[row['id']]+=1
 for id,n in counts.items():
  if n!=(0 if id=='r2_miaodigou_ii_regional_context' and not reverse else 1):raise ValueError('Wrong count '+id)
def run(action):
 m=json.load(gzip.open(M,'rt',encoding='utf8'));validate(m);rev=action=='rollback';check_index(rev);out={}
 for p in (W,R):
  with gzip.open(H/p,'rt',encoding='utf8') as f:d=json.load(f)
  new=transform(d,m,p,rev)
  if transform(new,m,p,not rev)!=d:raise ValueError('Roundtrip failed')
  out[p]=new
 for p,d in out.items():write_atomic_gzip((STAGE if action=='stage' else H)/p,d)
 print(action,'three corrections and one new regional context')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
