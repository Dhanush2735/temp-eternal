#!/usr/bin/env python3
"""Apply or reverse a reviewed 3000 BCE update and addition in one indexed pack."""
import argparse,gzip,hashlib,json
from pathlib import Path
from guarded_cache_pack_writer import write_atomic_gzip
from apply_1940_ce_context import transform
ROOT=Path(__file__).resolve().parent;H=ROOT.parent/'eternal/src/main/resources/data/eternalengine/eternal/history'
M=ROOT/'reviews/3000_bce_metrology_taiwan_2026-11.json.gz';PACK='events_wikipedia_regional.json.gz'
SHA='1fb238d7ab01964e3f2a6436f7f81aa83a7c8375f02e2b673d4958f70a2e2aed'
def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else open(p,encoding='utf8')) as f:return json.load(f)
def validate(m):
 h=hashlib.sha256(json.dumps(m,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 if h!=SHA or m.get('schema')!='eternal-r2-3000-bce-metrology-taiwan-v1' or len(m['updates'])!=1 or len(m['additions'])!=1:raise ValueError('Manifest mismatch')
 u=m['updates'][0];add=m['additions'][0]
 if u['pack']!=PACK or add['pack']!=PACK or u['event_id']!='wpr_8bb078f921' or u['before']['id']!=u['event_id'] or u['after']['id']!=u['event_id'] or add['event']['id']!='r2_dapenkeng_taiwan_c3000':raise ValueError('Unexpected target')
 if not u['after']['r2SourceEvidence']['sources'] or not add['event']['r2SourceEvidence']['sources'] or add['event']['end']<=add['event']['start']:raise ValueError('Invalid source or date')
def run(action):
 m=load(M);validate(m);packs=load(H/'index.json')['packs'];assert PACK in packs
 ids=[m['updates'][0]['event_id'],m['additions'][0]['event']['id']];seen={i:[] for i in ids};target=None
 for p in packs:
  d=load(H/p)
  if p==PACK:target=d
  for section in ('events','sites'):
   for e in d.get(section,[]):
    if isinstance(e,dict) and e.get('id') in seen:seen[e['id']].append((p,section))
 if seen[ids[0]]!=[(PACK,'events')] or seen[ids[1]]!=([(PACK,'events')] if action=='rollback' else []):raise ValueError('Missing or duplicate target ID: '+str(seen))
 reverse=action=='rollback';out=transform(target,m['updates'],reverse,m['additions'])
 if transform(out,m['updates'],not reverse,m['additions'])!=target:raise ValueError('Roundtrip failed')
 path=(Path('/tmp/eternal-3000-metrology-taiwan-stage')/PACK) if action=='stage' else H/PACK
 write_atomic_gzip(path,out);print(action,'1 update, 1 addition, one indexed pack')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['stage','apply','rollback']);run(p.parse_args().action)
