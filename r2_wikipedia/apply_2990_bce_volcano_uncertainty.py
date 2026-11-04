#!/usr/bin/env python3
"""Strict reversible hazard-label annotations; does not alter actual event timing."""
import argparse,gzip,hashlib,json
from pathlib import Path
from guarded_cache_pack_writer import write_atomic_gzip
from apply_1940_ce_context import transform
R=Path(__file__).resolve().parent;H=R.parent/'eternal/src/main/resources/data/eternalengine/eternal/history';PACK='events_hazards.json.gz';M=R/'reviews/2990_bce_volcano_uncertainty_2026-11.json.gz'
SHA='f603bef56980ce623539f53dba9464495f07526eeb8643ce31c479944b2384af'
def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else open(p,encoding='utf8')) as f:return json.load(f)
def validate(m):
 h=hashlib.sha256(json.dumps(m,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 ids={'hz_2ccea0927a','hz_c7405250d4','hz_8d2df04470'}
 if h!=SHA or m.get('schema')!='eternal-r2-2990-bce-volcano-uncertainty-v1' or len(m['updates'])!=3 or m['additions'] or {u['event_id'] for u in m['updates']}!=ids:raise ValueError('Manifest mismatch')
 for u in m['updates']:
  b=u['before'];a=u['after']
  if u['pack']!=PACK or b['id']!=u['event_id'] or a['id']!=u['event_id'] or {k for k in b if a[k]!=b[k]}!={'name'} or set(a)-set(b)!={'r2SourceEvidence'}:raise ValueError('Unexpected modification')
def run(action):
 m=load(M);validate(m);packs=load(H/'index.json')['packs'];assert PACK in packs
 ids={u['event_id'] for u in m['updates']};seen={i:[] for i in ids};target=None
 for p in packs:
  d=load(H/p)
  if p==PACK:target=d
  for section in ('events','sites'):
   for row in d.get(section,[]):
    if isinstance(row,dict) and row.get('id') in seen:seen[row['id']].append((p,section))
 if any(v!=[(PACK,'events')] for v in seen.values()):raise ValueError('Unexpected ID locations')
 reverse=action=='rollback';out=transform(target,m['updates'],reverse,[])
 if transform(out,m['updates'],not reverse,[])!=target:raise ValueError('Roundtrip failed')
 path=(Path('/tmp/eternal-2990-volcano-stage')/PACK) if action=='stage' else H/PACK
 write_atomic_gzip(path,out);print(action,'3 hazard labels; unchanged gameplay year/effects')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
