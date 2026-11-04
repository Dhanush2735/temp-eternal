#!/usr/bin/env python3
"""Reviewed batch with strict preflight, stage and reversible pack edits."""
import argparse,copy,gzip,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/2350_2310_bce_context_2026-10.json.gz';STAGE=ROOT/'.cache/r2_storage/2350_2310_stage';W='events_wikipedia.json.gz';R='events_wikipedia_regional.json.gz'
# pack, start, exclusive end, latitude, longitude, radius, confidence, qualification
SPEC={'wpy_5d84896301':(W,-2350,-2349,34.54944,40.89,20,'wikipedia_coord','chronology approximate'),'wpr_275ba50b29':(R,-2350,-2349,32.0,45.5,200,'wikipedia_region','chronology debated'),'wpr_6e541442c9':(R,-2350,-2349,32.0,46.0,150,'wikipedia_region','chronology approximate'),'wpr_f804b92046':(R,-2354,-2344,53.4,-8.0,200,'wikipedia_region','cause uncertain'),'wpr_6053ddb7bb':(R,-2345,-2180,29.638,31.2209,269,'wikipedia_region','one approximate chronology'),'wpr_1a396908c8':(R,-2334,-2278,32.0,46.0,150,'wikipedia_region','one approximate chronology'),'wpr_c99c90fe8d':(R,-2334,-2333,32.0,45.5,200,'wikipedia_region','dating approximate'),'wpy_e3211aa207':(W,-2334,-2333,33.1,44.1,200,'wikipedia_region','chronology approximate'),'wpr_36dd7c7369':(R,-2300,-2299,30.96165,46.10513,20,'wikipedia_coord','date approximate'),'r2_caral_continuation_context':(R,-2499,-2299,-10.89361,-77.52028,20,'wikipedia_coord','dates approximate'),'r2_mature_harappan_continuation_context':(R,-2499,-2300,29.0,70.5,400,'wikipedia_region','dates approximate'),'r2_teti_egypt_reign_context':(R,-2345,-2332,29.845,31.251,180,'wikipedia_region','one approximate chronology')}
NEW={k for k in SPEC if k.startswith('r2_')}
def validate(m):
 if m.get('schema')!='eternal-r2-2350-2310-v1' or len(m['updates'])!=9 or len(m['additions'])!=3:raise ValueError('Invalid manifest')
 entries=[(x['pack'],x['event_id'],x['after']) for x in m['updates']]+[(x['pack'],x['event']['id'],x['event']) for x in m['additions']]
 if {id for p,id,e in entries}!=set(SPEC) or {x['event']['id'] for x in m['additions']}!=NEW:raise ValueError('Wrong IDs')
 for pack,id,e in entries:
  p,st,en,lat,lon,rad,conf,qual=SPEC[id]
  if (pack,e['start'],e['end'],e['lat'],e['lon'],e['radiusKm'],e['kind'],e['effect'],e['confidence'])!=(p,st,en,lat,lon,rad,'cultural','note',conf) or qual not in e['name'] or len(e['r2SourceEvidence']['sources'])<3:raise ValueError('Invalid '+id)
 for u in m['updates']:
  b,a=u['before'],u['after']
  if b['id']!=u['event_id'] or a['id']!=u['event_id'] or set(a)!=set(b)|{'r2SourceEvidence'} or {k for k in b if a[k]!=b[k]}-{'name','start','end','lat','lon','radiusKm','kind','effect','confidence'}:raise ValueError('Unexpected change')
def transform(doc,m,pack,reverse=False):
 validate(m);o=copy.deepcopy(doc);rows=o.get('events')
 if not isinstance(rows,list):raise ValueError('No events')
 for u in (x for x in m['updates'] if x['pack']==pack):
  old,new=(u['after'],u['before']) if reverse else (u['before'],u['after']);hits=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==u['event_id']]
  if len(hits)!=1 or rows[hits[0]]!=old:raise ValueError('Missing/changed '+u['event_id'])
  rows[hits[0]]=copy.deepcopy(new)
 for a in (x for x in m['additions'] if x['pack']==pack):
  e=a['event'];hits=[i for i,r in enumerate(rows) if isinstance(r,dict) and r.get('id')==e['id']]
  if reverse:
   if len(hits)!=1 or rows[hits[0]]!=e:raise ValueError('Missing/changed addition '+e['id'])
   del rows[hits[0]]
  else:
   if hits:raise ValueError('Duplicate ID '+e['id'])
   rows.append(copy.deepcopy(e))
 return o
def check_index(reverse):
 packs=json.loads((H/'index.json').read_text())['packs'];counts={i:0 for i in SPEC}
 if not {W,R}.issubset(packs):raise ValueError('Not indexed')
 for p in packs:
  with (gzip.open(H/p,'rt',encoding='utf8') if p.endswith('.gz') else open(H/p,encoding='utf8')) as f:d=json.load(f)
  for sec in ('events','sites'):
   for r in d.get(sec,[]):
    if not isinstance(r,dict) or r.get('id') not in SPEC:continue
    id=r['id']
    if (p,sec)!=(SPEC[id][0],'events'):raise ValueError('Shared ID '+id)
    counts[id]+=1
 for id,n in counts.items():
  if n!=(0 if id in NEW and not reverse else 1):raise ValueError('Wrong count '+id)
def run(action):
 m=json.load(gzip.open(M,'rt',encoding='utf8'));validate(m);rev=action=='rollback';check_index(rev);outputs={}
 for p in (W,R):
  with gzip.open(H/p,'rt',encoding='utf8') as f:doc=json.load(f)
  out=transform(doc,m,p,rev)
  if transform(out,m,p,not rev)!=doc:raise ValueError('Roundtrip')
  outputs[p]=out
 for p,d in outputs.items():write_atomic_gzip((STAGE if action=='stage' else H)/p,d)
 print(action,'nine corrections and three additions; atomic per pack, not cross-pack')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
