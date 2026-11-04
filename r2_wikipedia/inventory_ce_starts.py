#!/usr/bin/env python3
"""Guarded inventory of indexed event starts in an inclusive CE range, not review."""
import argparse,gzip,json,lzma
from collections import Counter
from datetime import date
from pathlib import Path
from storage_guard import within_budget
ROOT=Path(__file__).resolve().parent;H=ROOT.parent/'eternal/src/main/resources/data/eternalengine/eternal/history'

def inventory(start,end):
 if not (1<=start<=end and end-start<50):raise ValueError('Expected 1–50 CE years')
 rows=[];details=[]
 for pack in json.loads((H/'index.json').read_text())['packs']:
  with (gzip.open(H/pack,'rt',encoding='utf8') if pack.endswith('.gz') else open(H/pack,encoding='utf8')) as f:d=json.load(f)
  for e in d.get('events',[]):
   if not isinstance(e,dict):continue
   n=e.get('start')
   if isinstance(n,int) and start<=n<=end:
    rows.append([pack,e.get('id'),n,e.get('kind')]);details.append((pack,e))
 out=ROOT/f'focus/indexed_start_inventory_{start}_{end}_CE.json.xz'
 if out.exists():raise FileExistsError(out)
 d={'schema':'indexed-start-inventory-v1','range':f'{start}–{end} CE' if start!=end else f'{start} CE','date':date.today().isoformat(),'note':'Pre-update starts only; pack, id, start, kind. Not full before-images or review. Overlaps starting outside range excluded.','fields':['pack','id','start','kind'],'rows':rows}
 b=lzma.compress(json.dumps(d,ensure_ascii=False,separators=(',',':')).encode(),preset=9)
 if within_budget(125)[1]+len(b)>=125000000:raise RuntimeError('125 MB guard blocks inventory')
 with out.open('xb') as f:f.write(b)
 print('records',len(rows),'hazards',sum('hazard' in x[0] for x in rows),'bytes',len(b));return details
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('start',type=int);p.add_argument('end',type=int);p.add_argument('--show',action='store_true');a=p.parse_args();v=inventory(a.start,a.end)
 if a.show:
  for pack,row in v:print(pack,json.dumps(row,ensure_ascii=False,separators=(',',':')))
