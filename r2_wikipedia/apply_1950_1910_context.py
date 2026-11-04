#!/usr/bin/env python3
"""Reviewed batch with strict preflight, stage and reversible pack edits."""
import argparse,copy,gzip,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip
ROOT=Path(__file__).resolve().parent.parent;H=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';M=ROOT/'r2_wikipedia/reviews/1950_1910_bce_context_2026-10.json.gz';STAGE=ROOT/'.cache/r2_storage/1950_1910_stage';W='events_wikipedia.json.gz';R='events_wikipedia_regional.json.gz';N='events_nature.json.gz'
# pack, start, exclusive end, latitude, longitude, radius, confidence, qualification
SPEC={'wpy_767ff3335c': ('events_wikipedia.json.gz', -1953, -1952, 21.8, 31.35, 180, 'wikipedia_region', 'uncertain'), 'wpy_2d38ee2677': ('events_wikipedia.json.gz', -1942, -1941, 51.19028, 11.16972, 20, 'wikipedia_coord', 'approximate'), 'wpr_227b87c9c2': ('events_wikipedia_regional.json.gz', -1924, -1923, 31.885, 45.26861, 100, 'wikipedia_region', 'uncertain'), 'wpr_758ef8354a': ('events_wikipedia_regional.json.gz', -1920, -1919, 35.86405, 102.81025, 20, 'wikipedia_coord', 'disputed'), 'q113381157': ('events_nature.json.gz', -1920, -1919, 35.8408, 102.6102, 50, 'wikipedia_region', 'disputed'), 'r2_senusret_i_reign_context': ('events_wikipedia_regional.json.gz', -1961, -1916, 29.56001, 31.22094, 150, 'wikipedia_region', 'approximate'), 'r2_amenemhat_ii_reign_context': ('events_wikipedia_regional.json.gz', -1926, -1894, 29.808, 31.225, 150, 'wikipedia_region', 'approximate'), 'r2_ishme_dagan_isin_reign_context': ('events_wikipedia_regional.json.gz', -1954, -1934, 31.885, 45.26861, 100, 'wikipedia_region', 'approximate'), 'r2_lipit_ishtar_isin_reign_context': ('events_wikipedia_regional.json.gz', -1935, -1923, 31.885, 45.26861, 100, 'wikipedia_region', 'approximate'), 'r2_ur_ninurta_isin_reign_context': ('events_wikipedia_regional.json.gz', -1924, -1895, 31.885, 45.26861, 100, 'wikipedia_region', 'approximate'), 'r2_ikunum_assur_reign_context': ('events_wikipedia_regional.json.gz', -1935, -1920, 35.45667, 43.2625, 100, 'wikipedia_region', 'approximate'), 'r2_sargon_i_assur_reign_context': ('events_wikipedia_regional.json.gz', -1921, -1880, 35.45667, 43.2625, 100, 'wikipedia_region', 'approximate'), 'r2_gungunum_larsa_reign_context': ('events_wikipedia_regional.json.gz', -1932, -1905, 31.28583, 45.85361, 100, 'wikipedia_region', 'approximate'), 'r2_lipit_ishtar_law_reference': ('events_wikipedia_regional.json.gz', -1930, -1929, 32.1278, 45.2333, 60, 'wikipedia_region', 'uncertain'), 'r2_william_hippopotamus_meir_reference': ('events_wikipedia_regional.json.gz', -1920, -1919, 27.40889, 30.71056, 20, 'wikipedia_coord', 'uncertain'), 'r2_kultepe_karum_ii_context': ('events_wikipedia_regional.json.gz', -1945, -1899, 38.85, 35.633, 20, 'wikipedia_coord', 'approximate'), 'r2_senusret_i_pyramid_lisht_reference': ('events_wikipedia_regional.json.gz', -1940, -1939, 29.56001, 31.22094, 20, 'wikipedia_coord', 'uncertain'), 'r2_unetice_mid_20th_context': ('events_wikipedia_regional.json.gz', -1949, -1899, 50.15, 14.35417, 350, 'wikipedia_region', 'approximate'), 'r2_caral_mid_20th_context': ('events_wikipedia_regional.json.gz', -1949, -1899, -10.89361, -77.52028, 20, 'wikipedia_coord', 'approximate'), 'r2_sintashta_mid_20th_context': ('events_wikipedia_regional.json.gz', -1949, -1899, 52.486222, 60.188278, 200, 'wikipedia_region', 'approximate'), 'r2_kerma_mid_20th_context': ('events_wikipedia_regional.json.gz', -1949, -1899, 19.6008, 30.40973, 60, 'wikipedia_region', 'approximate'), 'r2_harappan_mid_20th_context': ('events_wikipedia_regional.json.gz', -1949, -1899, 29.0, 70.5, 400, 'wikipedia_region', 'approximate'), 'r2_shimao_mid_20th_context': ('events_wikipedia_regional.json.gz', -1959, -1909, 38.5657, 110.3252, 20, 'wikipedia_coord', 'approximate'), 'r2_taosi_mid_20th_context': ('events_wikipedia_regional.json.gz', -1959, -1909, 35.8906028, 111.4971722, 20, 'wikipedia_coord', 'approximate'), 'r2_minoan_mm_ia_mid_20th_context': ('events_wikipedia_regional.json.gz', -1959, -1909, 35.30972, 24.89333, 125, 'wikipedia_region', 'approximate')}
NEW={k for k in SPEC if k.startswith('r2_')}
def validate(m):
 if m.get('schema')!='eternal-r2-1950-1910-v1' or len(m['updates'])!=5 or len(m['additions'])!=20:raise ValueError('Invalid manifest')
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
 if not {W,R,N}.issubset(packs):raise ValueError('Not indexed')
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
 for p in (W,R,N):
  with gzip.open(H/p,'rt',encoding='utf8') as f:doc=json.load(f)
  out=transform(doc,m,p,rev)
  if transform(out,m,p,not rev)!=doc:raise ValueError('Roundtrip')
  outputs[p]=out
 for p,d in outputs.items():write_atomic_gzip((STAGE if action=='stage' else H)/p,d)
 print(action,'five corrections and twenty additions; atomic per pack, not cross-pack')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
