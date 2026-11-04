#!/usr/bin/env python3
"""Reviewed batch with strict preflight, stage and reversible pack edits."""
import argparse,copy,gzip,json,hashlib
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/1700_1660_bce_context_2026-10.json.gz';STAGE=ROOT/'.cache/r2_storage/1700_1660_stage';W='events_wikipedia.json.gz';R='events_wikipedia_regional.json.gz'
# pack, start, exclusive end, latitude, longitude, radius, confidence, qualification
SPEC={'wpy_c2ab7bc00f': ('events_wikipedia.json.gz', -1700, -1699, 50.15, 14.35417, 300, 'wikipedia_region', 'uncertain'), 'wpy_889c900ba5': ('events_wikipedia.json.gz', -1750, -1749, 35.30972, 24.89333, 125, 'wikipedia_region', 'uncertain'), 'wpy_633a7385b6': ('events_wikipedia.json.gz', -1700, -1699, 30.63, 72.86, 300, 'wikipedia_region', 'uncertain'), 'wpy_fbc26e6d72': ('events_wikipedia.json.gz', -1700, -1699, 30.63, 72.86, 300, 'wikipedia_region', 'uncertain'), 'wpy_d4af8d69cc': ('events_wikipedia.json.gz', -1700, -1699, 35.30972, 24.89333, 125, 'wikipedia_region', 'uncertain'), 'wpy_9985be3fcc': ('events_wikipedia.json.gz', -1700, -1699, 35.30972, 24.89333, 125, 'wikipedia_region', 'uncertain'), 'wpy_0fbd09bd86': ('events_wikipedia.json.gz', -1700, -1699, 35.30972, 24.89333, 125, 'wikipedia_region', 'uncertain'), 'wpy_f4796cf151': ('events_wikipedia.json.gz', -1700, -1699, 35.29806, 25.16306, 20, 'wikipedia_coord', 'uncertain'), 'wpy_b5323c78b2': ('events_wikipedia.json.gz', -1700, -1699, 34.693, 112.689, 150, 'wikipedia_region', 'uncertain'), 'wpy_ba3f1917fb': ('events_wikipedia.json.gz', -1700, -1699, 34.693, 112.689, 150, 'wikipedia_region', 'uncertain'), 'wpy_5d2ff0c1af': ('events_wikipedia.json.gz', -1700, -1699, 34.693, 112.689, 150, 'wikipedia_region', 'uncertain'), 'wpy_126c7cc606': ('events_wikipedia.json.gz', -1700, -1699, 37.30111, 64.15531, 300, 'wikipedia_region', 'uncertain'), 'wpy_cbfafdbdcf': ('events_wikipedia.json.gz', -1700, -1699, 36.35136, 25.40356, 20, 'wikipedia_coord', 'uncertain'), 'wpy_c9cea0fa92': ('events_wikipedia.json.gz', -1680, -1679, 29.98, 31.13, 150, 'wikipedia_region', 'uncertain'), 'wpr_367ec0e436': ('events_wikipedia_regional.json.gz', -1700, -1690, 35.45667, 43.2625, 100, 'wikipedia_region', 'uncertain'), 'wpr_973f0bf361': ('events_wikipedia_regional.json.gz', -1691, -1673, 35.45667, 43.2625, 100, 'wikipedia_region', 'uncertain'), 'wpr_ad97967835': ('events_wikipedia_regional.json.gz', -1674, -1661, 35.45667, 43.2625, 100, 'wikipedia_region', 'uncertain'), 'wpr_7b3438dee1': ('events_wikipedia_regional.json.gz', -1662, -1649, 35.45667, 43.2625, 100, 'wikipedia_region', 'uncertain'), 'r2_abi_eshuh_1700_reign_context': ('events_wikipedia_regional.json.gz', -1712, -1683, 32.5425, 44.42111, 120, 'wikipedia_region', 'uncertain'), 'r2_ammi_ditana_1700_reign_context': ('events_wikipedia_regional.json.gz', -1683, -1646, 32.5425, 44.42111, 120, 'wikipedia_region', 'uncertain'), 'r2_kerma_1700_1660_context': ('events_wikipedia_regional.json.gz', -1700, -1659, 19.6008, 30.40973, 60, 'wikipedia_region', 'uncertain'), 'r2_erlitou_1700_1660_context': ('events_wikipedia_regional.json.gz', -1700, -1659, 34.693, 112.689, 100, 'wikipedia_region', 'uncertain'), 'r2_sechin_alto_1700_1660_context': ('events_wikipedia_regional.json.gz', -1700, -1659, -9.4654, -78.2426, 20, 'wikipedia_coord', 'uncertain'), 'r2_valdivia_1700_1660_context': ('events_wikipedia_regional.json.gz', -1700, -1659, -1.95, -80.72, 100, 'wikipedia_region', 'uncertain'), 'r2_britain_1700_1660_context': ('events_wikipedia_regional.json.gz', -1700, -1659, 51.3, -1.8, 200, 'wikipedia_region', 'uncertain')}
NEW={k for k in SPEC if k.startswith('r2_')}
def validate(m):
 if hashlib.sha256(json.dumps(m,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()!='3e31fa6ea53314a8dd0454d8668d09369ee0a9b440b0360d0d0c6e5a37824666':raise ValueError('Manifest differs from approved review')
 if m.get('schema')!='eternal-r2-1700-1660-v1' or len(m['updates'])!=18 or len(m['additions'])!=7:raise ValueError('Invalid manifest')
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
 print(action,'18 corrections and seven additions; atomic per pack, not cross-pack')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
