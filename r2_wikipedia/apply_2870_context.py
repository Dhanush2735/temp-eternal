#!/usr/bin/env python3
"""Guarded two-pack correction for 2870 context and a related calendar estimate."""
import argparse,copy,gzip,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/2870_bce_dholavira_calendar_2026-10.json';STAGE=Path('/home/user/.cache/r2_storage/2870_context_stage')
S={'r2_dholavira_early_c3000':('events_wikipedia.json.gz',-3000,-2599,23.88861,70.21364,20,'wikipedia_coord','chronology debated'), 'wpr_c568ec23c5':('events_wikipedia_regional.json.gz',-2874,-2873,29.638,31.2209,269,'wikipedia_region','date uncertain')}
def validate(m):
 updates=m['updates']
 if m['schema']!='eternal-r2-2870bce-v1' or len(updates)!=2 or {u['event_id'] for u in updates}!=set(S):raise ValueError('Bad manifest')
 for x in updates:
  id=x['event_id'];b=x['before'];a=x['after'];p,st,en,lat,lon,radius,conf,qual=S[id]
  if x['pack']!=p or b.get('id')!=id or a.get('id')!=id or set(a)!=(set(b)|{'r2SourceEvidence'}) or {k for k in b if a[k]!=b[k]}-{'name','start','end','kind','r2SourceEvidence'}:raise ValueError('Unexpected fields')
  if (a['start'],a['end'],a['lat'],a['lon'],a['radiusKm'],a['kind'],a['effect'],a['confidence'])!=(st,en,lat,lon,radius,'cultural','note',conf):raise ValueError('Invalid reference')
  if qual not in a['name'] or len(a['r2SourceEvidence']['sources'])<3:raise ValueError('Missing caveat')
def transform(doc,m,pack,reverse=False):
 validate(m)
 if not isinstance(doc.get('events'),list):raise ValueError('No events')
 o=copy.deepcopy(doc)
 for u in (x for x in m['updates'] if x['pack']==pack):
  hits=[i for i,r in enumerate(o['events']) if isinstance(r,dict) and r.get('id')==u['event_id']];old,new=(u['after'],u['before']) if reverse else (u['before'],u['after'])
  if len(hits)!=1 or o['events'][hits[0]]!=old:raise ValueError('Missing, duplicate, or changed '+u['event_id'])
  o['events'][hits[0]]=copy.deepcopy(new)
 return o
def check_index():
 packs=json.loads((H/'index.json').read_text())['packs'];counts={k:0 for k in S}
 if any(v[0] not in packs for v in S.values()):raise ValueError('Not indexed')
 for p in packs:
  with (gzip.open(H/p,'rt',encoding='utf8') if p.endswith('.gz') else open(H/p,encoding='utf8')) as f:d=json.load(f)
  for sec in ('events','sites'):
   for row in d.get(sec,[]):
    if isinstance(row,dict) and row.get('id') in counts:
     if (p,sec)!=(S[row['id']][0],'events'):raise ValueError('Shared ID')
     counts[row['id']]+=1
 if any(x!=1 for x in counts.values()):raise ValueError('Missing or duplicate ID')
def run(action):
 m=json.loads(M.read_text());validate(m);check_index();rev=action=='rollback';out={}
 for p in (v[0] for v in S.values()):
  with gzip.open(H/p,'rt',encoding='utf8') as f:doc=json.load(f)
  new=transform(doc,m,p,rev)
  if transform(new,m,p,not rev)!=doc:raise ValueError('Roundtrip failed')
  out[p]=new
 for p,doc in out.items():write_atomic_gzip((STAGE if action=='stage' else H)/p,doc)
 print(action,'two uncertain archaeological references')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
