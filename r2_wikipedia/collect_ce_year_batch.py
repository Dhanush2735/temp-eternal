#!/usr/bin/env python3
"""Resolve and archive a bounded batch of CE year revisions, not complete collection.

Checks the existing 125 MB persistent workspace guard before network requests
and before saving both outputs; never silently raises it. Raw wikitext does not
expand transclusions. No linked-article recursion or game updates are implied.
"""
import argparse,concurrent.futures,json,lzma,os,sys
from datetime import datetime,timezone
from pathlib import Path
import requests
from batch_year_resolver import resolve_chunk
from storage_guard import within_budget
ROOT=Path(__file__).resolve().parent;API='https://en.wikipedia.org/w/api.php'
UA='EternalEngineR2Research/0.1 (personal historical research; CE year archive)'
LIMIT=125_000_000

def budget():
 ok,used=within_budget(125)
 if not ok:raise RuntimeError(f'Existing 125 MB guard blocked collection: {used} bytes')
 return used

def query(params):
 budget()
 r=requests.get(API,params={'action':'query','format':'json','formatversion':2,'maxlag':5,**params},headers={'User-Agent':UA},timeout=45)
 r.raise_for_status();d=r.json()
 if 'error' in d:raise RuntimeError(str(d['error']))
 if 'continue' in d:raise RuntimeError('Unexpected pagination; refusing incomplete archive')
 return d

def collect(start,end):
 if start<1 or end<start or end-start>=50:raise ValueError('Range must be CE and contain 1–50 years')
 titles=[f'{n} (year)' for n in range(start,end+1)]
 info=query({'titles':'|'.join(titles),'redirects':1,'prop':'info|pageprops'})
 resolutions=resolve_chunk(titles,info);pages=info['query']['pages'];by={p['title']:p for p in pages}
 for x in resolutions:
  if x['status']!='resolved' or x['canonical_title']!=str(int(x['requested_title'].split()[0])) or 'disambiguation' in by[x['canonical_title']].get('pageprops',{}):raise ValueError('Unexpected redirect, disambiguation or missing year: '+str(x))
 ids=[x['lastrevid'] for x in resolutions];groups=[ids[i:i+10] for i in range(0,len(ids),10)]
 def fetch(g):return query({'revids':'|'.join(map(str,g)),'prop':'revisions|pageprops','rvprop':'ids|timestamp|content','rvslots':'main'})['query']['pages']
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:revision_pages=[p for group in pool.map(fetch,groups) for p in group]
 found={p['revisions'][0]['revid']:p for p in revision_pages};assert len(found)==len(ids)
 for x in resolutions:
  p=found[x['lastrevid']];assert p['title']==x['canonical_title'] and p['pageid']==x['pageid'] and 'disambiguation' not in p.get('pageprops',{});assert 'content' in p['revisions'][0]['slots']['main']
 now=datetime.now(timezone.utc).isoformat();a={'schema':'year-title-resolution-v1','retrieved_at':now,'method':'MediaWiki info, redirects, disambiguation guard and revision identity checks','note':'Title resolution is not year completeness.','results':resolutions}
 b={'schema':'year-wikitext-revisions-v1','retrieved_at':now,'note':'Pinned raw wikitext; transclusions unexpanded; linked articles not recursively collected.','pages':revision_pages}
 out1=ROOT/f'focus/year_titles_{start}_{end}_CE.json';out2=ROOT/f'focus/year_wikitext_{start}_{end}_CE.json.xz'
 if out1.exists() or out2.exists():raise FileExistsError('Output exists; no overwrite')
 raw1=(json.dumps(a,ensure_ascii=False,indent=2)+'\n').encode();raw2=lzma.compress(json.dumps(b,ensure_ascii=False,separators=(',',':')).encode(),preset=9)
 used=budget()
 if used+len(raw1)+len(raw2)>=LIMIT:raise RuntimeError(f'Guard refuses output: workspace={used}, output={len(raw1)+len(raw2)}, limit={LIMIT}; no outputs saved')
 # Two outputs are not transactional: use exclusive creates and remove the first on failure.
 created=[]
 try:
  with out1.open('xb') as f:
   created.append(out1);f.write(raw1)
  with out2.open('xb') as f:
   created.append(out2);f.write(raw2)
 except BaseException:
  for p in created:p.unlink(missing_ok=True)
  raise
 print(f'{len(ids)} distinct year titles/revisions archived; {len(raw1)+len(raw2)} bytes; no year is claimed complete')
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('start',type=int);p.add_argument('end',type=int);x=p.parse_args();collect(x.start,x.end)
