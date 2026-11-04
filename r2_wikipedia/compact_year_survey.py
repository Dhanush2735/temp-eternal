#!/usr/bin/env python3
"""Compact preliminary year survey: pins + counts, NOT revision archives or link following."""
import argparse,concurrent.futures,hashlib,json,lzma,re
from pathlib import Path
import collect_ce_year_batch as C
from batch_year_resolver import resolve_chunk
from storage_guard import workspace_bytes
import fast_year_triage as T

def survey(start,end):
 if not 1<=start<=end or end-start>=50:raise ValueError('Expected 1–50 consecutive CE years')
 out=T.F/f'compact_survey_{start}_{end}_CE.json.xz'
 if out.exists():raise FileExistsError(out)
 titles=[f'{y} (year)' for y in range(start,end+1)]
 info=C.query({'titles':'|'.join(titles),'redirects':1,'prop':'info|pageprops'})
 resolutions=resolve_chunk(titles,info);by={p['title']:p for p in info['query']['pages']}
 for r in resolutions:
  if r['status']!='resolved' or r['canonical_title']!=r['requested_title'].split()[0] or 'disambiguation' in by[r['canonical_title']].get('pageprops',{}):raise ValueError('Unexpected year identity')
 ids=[x['lastrevid'] for x in resolutions]
 def fetch(group):return C.query({'revids':'|'.join(map(str,group)),'prop':'revisions|pageprops','rvprop':'ids|timestamp|content','rvslots':'main'})['query']['pages']
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:pages=[p for group in pool.map(fetch,[ids[i:i+10] for i in range(0,len(ids),10)]) for p in group]
 if {(p['title'],p['pageid'],p['revisions'][0]['revid']) for p in pages}!={(r['canonical_title'],r['pageid'],r['lastrevid']) for r in resolutions}:raise ValueError('Year revision identities do not match')
 summary={}
 for p in pages:
  rev=p['revisions'][0];text=rev['slots']['main']['content'];y=p['title']
  summary[y]={'pageid':p['pageid'],'revid':rev['revid'],'revision_timestamp':rev['timestamp'],'wikitext_sha256':hashlib.sha256(text.encode()).hexdigest(),'candidate_mainspace_links':len(T.links(p)),'indexed_event_starts':0,'indexed_hazard_starts':0,'coordinate_flags':0}
 packs=C.json.loads((T.H/'index.json').read_text())['packs']
 import gzip
 for pack in packs:
  with (gzip.open(T.H/pack,'rt',encoding='utf8') if pack.endswith('.gz') else open(T.H/pack,encoding='utf8')) as f:d=json.load(f)
  for e in d.get('events',[]):
   if not isinstance(e,dict) or type(e.get('start')) is not int or not start<=e['start']<=end:continue
   s=summary[str(e['start'])];s['indexed_event_starts']+=1;s['indexed_hazard_starts']+=int('hazard' in pack);s['coordinate_flags']+=int((e.get('lat'),e.get('lon')) in {(0.0,-30.0),(37.5,-79.0),(65.0,90.0)})
 doc={'schema':'r2-compact-year-survey-v1','range':[start,end],'scope':'Preliminary counts and revision identities only; raw annual wikitext was NOT archived. Linked articles were NOT followed. No gameplay edits or people profiles. No year fully collected.','caveats':'Counts are pre-edit indexed starts, not distinct verified events; raw-wikitext candidate links include references, navigation and other irrelevant links; templates are unexpanded; coordinate flags are unverified heuristics. Later Wikipedia revision deletion could prevent retrieval.','years':summary}
 raw=lzma.compress(json.dumps(doc,ensure_ascii=False,separators=(',',':')).encode(),preset=9)
 if workspace_bytes()+len(raw)>=125_000_000:raise RuntimeError('Storage guard refuses output')
 with out.open('xb') as f:f.write(raw)
 return doc
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('start',type=int);p.add_argument('end',type=int);a=p.parse_args();d=survey(a.start,a.end);print(json.dumps(d,indent=2))
