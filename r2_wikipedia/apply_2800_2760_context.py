#!/usr/bin/env python3
"""Guarded regional batch: two corrected uncertain claims, two context notes."""
import argparse,copy,gzip,json,re
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/2800_2760_bce_context_2026-10.json';PACK='events_wikipedia_regional.json.gz';STAGE=ROOT/'.cache/r2_storage/2800_2760_stage'
SPEC={'wpr_c80b8b9274':(-2775,-2774,29.638,31.2209,269,'conflict disputed'),'wpr_eb589adcd2':(-2750,-2749,46.0,25.0,500,'chronology disputed'),'r2_met_cycladic_harp_date_c2800':(-2800,-2699,37.0,25.16667,100,'findspot uncertain'),'r2_tagus_early_beaker_28c':(-2800,-2699,38.72,-9.14,120,'dating approximate')}
def validate(m):
 if m.get('schema')!='eternal-r2-2800-2760-v1' or m.get('pack')!=PACK or len(m['updates'])!=2 or len(m['additions'])!=2:raise ValueError('Invalid manifest')
 allrows=[(u['event_id'],u['after']) for u in m['updates']]+[(e['id'],e) for e in m['additions']]
 if {id for id,e in allrows}!=set(SPEC):raise ValueError('Wrong IDs')
 for id,e in allrows:
  st,en,lat,lon,rad,qual=SPEC[id]
  if (e['id'],e['start'],e['end'],e['lat'],e['lon'],e['radiusKm'],e['kind'],e['effect'],e['confidence'])!=(id,st,en,lat,lon,rad,'cultural','note','wikipedia_region') or qual not in e['name'] or len(e['r2SourceEvidence']['sources'])<3:raise ValueError('Invalid event '+id)
 for u in m['updates']:
  b,a=u['before'],u['after']
  if b['id']!=u['event_id'] or a['id']!=u['event_id'] or set(a)!=set(b)|{'r2SourceEvidence'} or {k for k in b if b[k]!=a[k]}-{'name','kind','effect','r2SourceEvidence'}:raise ValueError('Unexpected field change')
def transform(doc,m,reverse=False):
 validate(m);o=copy.deepcopy(doc)
 if not isinstance(o.get('events'),list):raise ValueError('No events')
 for u in m['updates']:
  hits=[i for i,r in enumerate(o['events']) if isinstance(r,dict) and r.get('id')==u['event_id']];old,new=(u['after'],u['before']) if reverse else (u['before'],u['after'])
  if len(hits)!=1 or o['events'][hits[0]]!=old:raise ValueError('Missing/changed '+u['event_id'])
  o['events'][hits[0]]=copy.deepcopy(new)
 for e in m['additions']:
  hits=[i for i,r in enumerate(o['events']) if isinstance(r,dict) and r.get('id')==e['id']]
  if reverse:
   if len(hits)!=1 or o['events'][hits[0]]!=e:raise ValueError('Modified addition')
   del o['events'][hits[0]]
  else:
   if hits:raise ValueError('Duplicate ID')
   o['events'].append(copy.deepcopy(e))
 return o
def check_index(reverse):
 packs=json.loads((H/'index.json').read_text())['packs'];counts={id:0 for id in SPEC}
 if PACK not in packs:raise ValueError('Pack not indexed')
 for p in packs:
  with (gzip.open(H/p,'rt',encoding='utf8') if p.endswith('.gz') else open(H/p,encoding='utf8')) as f:d=json.load(f)
  for sec in ('events','sites'):
   for r in d.get(sec,[]):
    if not isinstance(r,dict):continue
    id=r.get('id')
    if id in counts:
     if (p,sec)!=(PACK,'events'):raise ValueError('Shared ID')
     counts[id]+=1
    if sec=='events' and id not in SPEC and isinstance(r.get('start'),int) and -3000<=r['start']<=-2600 and re.search(r'(?i)(met.*harp|harp.*(met|seated)|maritime.*bell beaker)',str(r.get('name',''))):raise ValueError('Potential duplicate '+str(id))
 for id,n in counts.items():
  expected=1 if reverse or id.startswith('wpr_') else 0
  if n!=expected:raise ValueError('Wrong ID count '+id)
def run(action):
 m=json.loads(M.read_text());validate(m);rev=action=='rollback';check_index(rev)
 with gzip.open(H/PACK,'rt',encoding='utf8') as f:d=json.load(f)
 out=transform(d,m,rev)
 if transform(out,m,not rev)!=d:raise ValueError('Roundtrip mismatch')
 write_atomic_gzip((STAGE if action=='stage' else H)/PACK,out);print(action,'two new references and two corrections')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('action',choices=['stage','apply','rollback']);run(a.parse_args().action)
