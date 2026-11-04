#!/usr/bin/env python3
"""Collect and triage a contiguous CE batch. Suggestions are not verified facts.

One MediaWiki resolution batch and one indexed-pack scan cover every year in a
range. Reruns validate existing archives and do not overwrite outputs. Titles
extracted from raw wikitext are an approximate review queue, not followed links.
This tool never edits gameplay data or creates spawnable people.
"""
import argparse,collections,gzip,json,lzma,re,sys
from pathlib import Path
import collect_ce_year_batch as collector
import inventory_ce_starts as inventory
from storage_guard import within_budget
ROOT=Path(__file__).resolve().parent; F=ROOT/'focus';H=inventory.H;LIMIT=125_000_000

def load(p):
 with (lzma.open(p,'rt',encoding='utf-8') if p.suffix=='.xz' else p.open(encoding='utf-8')) as f:return json.load(f)
def paths(start,end):
 return (F/f'year_titles_{start}_{end}_CE.json',F/f'year_wikitext_{start}_{end}_CE.json.xz',F/f'indexed_start_inventory_{start}_{end}_CE.json.xz')
def verify(start,end):
 a,b,_=paths(start,end); titles=load(a)['results'];pages=load(b)['pages'];expected={str(y) for y in range(start,end+1)}
 if len(titles)!=len(expected) or {x['canonical_title'] for x in titles}!=expected:raise ValueError('Unexpected or incomplete title resolutions')
 if len(pages)!=len(expected) or {x['title'] for x in pages}!=expected:raise ValueError('Unexpected or incomplete year pages')
 checks={(x['canonical_title'],x['pageid'],x['lastrevid']) for x in titles};found={(x['title'],x['pageid'],x['revisions'][0]['revid']) for x in pages}
 if checks!=found:raise ValueError('Revision/title mismatch')
 return pages

def links(page):
 text=page['revisions'][0]['slots']['main']['content'];out=set()
 for raw in re.findall(r'\[\[([^\[\]]+)\]\]',text):
  title=raw.split('|',1)[0].split('#',1)[0].strip().replace('_',' ')
  if title and ':' not in title:out.add(title)
 return sorted(out,key=str.casefold)

def analyze(start,end,write=True):
 pages=verify(start,end);inv=load(paths(start,end)[2]);rows=inv['rows'];byyear={str(y):{'starts':0,'hazards':0,'candidate_mainspace_links':0} for y in range(start,end+1)}
 for pack,id,year,kind in rows:
  if str(year) not in byyear:raise ValueError('Out-of-range inventory row')
  byyear[str(year)]['starts']+=1;byyear[str(year)]['hazards']+=int('hazard' in pack)
 for page in pages:byyear[page['title']]['candidate_mainspace_links']=len(links(page))
 placeholder=[];dups=collections.defaultdict(list);active=[]
 for pack in json.loads((H/'index.json').read_text())['packs']:
  with (gzip.open(H/pack,'rt',encoding='utf8') if pack.endswith('.gz') else open(H/pack,encoding='utf8')) as f:d=json.load(f)
  for e in d.get('events',[]):
   if not isinstance(e,dict) or type(e.get('start')) is not int or not start<=e['start']<=end:continue
   id=e.get('id');name=e.get('name','');active.append([pack,id,e['start'],e.get('kind')]);norm=re.sub(r'[^\w]+',' ',re.sub(r'^(?:WWII|World War II):?\s*','',name,flags=re.I).casefold()).strip()
   if norm:dups[(e['start'],norm)].append([pack,id])
   if (e.get('lat'),e.get('lon')) in {(0.0,-30.0),(37.5,-79.0),(65.0,90.0)}:placeholder.append({'year':e['start'],'pack':pack,'id':id,'coordinates':[e.get('lat'),e.get('lon')],'name':name})
 if collections.Counter(map(tuple,active))!=collections.Counter(map(tuple,rows)):raise ValueError('Indexed starts have changed since inventory; review before using triage')
 groups=[{'year':y,'name_key':n,'records':v} for (y,n),v in dups.items() if len(v)>1];groups.sort(key=lambda x:(x['year'],x['name_key']));placeholder.sort(key=lambda x:(x['year'],x['id'] or ''))
 out={'schema':'r2-fast-year-triage-v1','range':[start,end],'status':'Research triage only. No year fully reviewed; link candidates not necessarily followed, resolvable or relevant; no gameplay edits.','year_summary':byyear,'starts':len(rows),'hazards':sum(x['hazards'] for x in byyear.values()),'coordinate_review_candidates':placeholder,'possible_exact_name_duplicates':groups,'caveats':'Coordinate and duplicate flags are heuristics, not verified errors. Duplicate candidates are exact normalized names only. Events beginning before the range are excluded. Raw wikitext transclusions are not expanded; link parsing includes references, navigation, birthdays and other non-event links.'}
 if write:
  path=F/f'fast_triage_{start}_{end}_CE.json.xz';raw=lzma.compress(json.dumps(out,ensure_ascii=False,separators=(',',':')).encode(),preset=9)
  if path.exists():
   if load(path)!=out:raise FileExistsError(f'{path} exists with different contents')
  else:
   used=within_budget(125)[1]
   if used+len(raw)>=LIMIT:raise RuntimeError(f'Storage guard blocks triage: {used}+{len(raw)}')
   with path.open('xb') as f:f.write(raw)
 return out

def prepare(start,end):
 if not (1<=start<=end and end-start<50):raise ValueError('Expected 1–50 contiguous CE years')
 a,b,c=paths(start,end)
 if a.exists()!=b.exists():raise RuntimeError('Incomplete existing year archive; refusing to overwrite')
 if not a.exists():collector.collect(start,end)
 verify(start,end)
 if not c.exists():inventory.inventory(start,end)
 return analyze(start,end)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('start',type=int);p.add_argument('end',type=int);p.add_argument('--titles',type=int,help='print approximate mainspace link candidates from one archived year');a=p.parse_args()
 if a.titles is not None:
  if not a.start<=a.titles<=a.end:p.error('requested year outside batch')
  page=next(x for x in verify(a.start,a.end) if x['title']==str(a.titles));print('\n'.join(links(page)));return
 d=prepare(a.start,a.end);print(json.dumps({'range':d['range'],'starts':d['starts'],'hazards':d['hazards'],'years':d['year_summary'],'coordinate_flags':len(d['coordinate_review_candidates']),'possible_duplicate_groups':len(d['possible_exact_name_duplicates']),'status':d['status']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
