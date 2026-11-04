#!/usr/bin/env python3
"""Resolve a consecutive BCE year-title batch. Research metadata ONLY, not collection.

Example: python r2_wikipedia/batch_year_resolver.py --from-bce 2989 --to-bce 2940 --output r2_wikipedia/focus/year_titles_2989_2940.json
Uses at most 50 titles per request. No event extraction, linked-article traversal,
coverage counting, or gameplay changes. Unknown/failed results are not checked.
"""
import argparse, json, os, time
from datetime import datetime, timezone
from pathlib import Path
import requests

API='https://en.wikipedia.org/w/api.php'
UA='EternalEngineR2Research/0.1 (personal historical research; batch title resolution)'

def years(start,end):
 if start < end or end < 1: raise ValueError('BCE range must decrease and remain positive')
 return [f'{n} BC' for n in range(start,end-1,-1)]

def resolve_chunk(titles, data):
 if 'error' in data: raise ValueError('API error: '+str(data['error']))
 q=data.get('query')
 if not isinstance(q,dict) or not isinstance(q.get('pages'),list): raise ValueError('Invalid API response')
 links={x['from']:x['to'] for key in ('normalized','converted','redirects') for x in q.get(key,[])}
 pages={p['title']:p for p in q['pages'] if 'title' in p};result=[]
 for requested in titles:
  cur=requested;chain=[];visited=set()
  while cur in links:
   if cur in visited: raise ValueError('Redirect cycle')
   visited.add(cur);cur=links[cur];chain.append(cur)
  p=pages.get(cur)
  if p is None: raise ValueError('Unresolved API title: '+requested)
  missing=bool(p.get('missing') or p.get('invalid'))
  result.append({'requested_title':requested,'canonical_title':cur,'redirect_chain':chain,
    'status':'missing' if missing else 'resolved','pageid':None if missing else p.get('pageid'),
    'lastrevid':None if missing else p.get('lastrevid')})
  if not missing and (not isinstance(p.get('pageid'),int) or not isinstance(p.get('lastrevid'),int)):
   raise ValueError('Resolved page lacks page ID or revision: '+cur)
 return result

def request_chunk(session,titles):
 params={'action':'query','format':'json','formatversion':2,'maxlag':5,'redirects':1,'prop':'info','titles':'|'.join(titles)}
 for attempt in range(5):
  try:
   r=session.get(API,params=params,timeout=30)
   if r.status_code in (429,500,502,503,504):
    retry=r.headers.get('Retry-After','');time.sleep(min(60,int(retry)) if retry.isdigit() else min(30,2**attempt));continue
   r.raise_for_status();data=r.json()
   if data.get('error',{}).get('code') in ('maxlag','ratelimited','readonly'):
    time.sleep(min(30,2**attempt));continue
   return resolve_chunk(titles,data)
  except (requests.RequestException,ValueError) as exc:
   if attempt==4: raise RuntimeError('Batch failed; no result saved: '+str(exc)) from exc
   time.sleep(min(30,2**attempt))
 raise RuntimeError('Rate limit or service unavailable; no result saved')

def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--from-bce',type=int,required=True);a.add_argument('--to-bce',type=int,required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--delay',type=float,default=1.0);args=a.parse_args()
 try:titles=years(args.from_bce,args.to_bce)
 except ValueError as e:a.error(str(e))
 if len(titles)>1000 or args.delay<0:a.error('Range limited to 1,000 years and nonnegative delay')
 root=Path(__file__).resolve().parent.parent
 dest=args.output.resolve()
 if not dest.is_relative_to(root) or dest.exists():a.error('Output must be a new file inside the workspace')
 session=requests.Session();session.headers.update({'User-Agent':UA,'Accept-Encoding':'gzip'});rows=[]
 for i in range(0,len(titles),50):
  if i:time.sleep(args.delay)
  rows.extend(request_chunk(session,titles[i:i+50]))
 out={'schema':'year-title-resolution-v1','retrieved_at':datetime.now(timezone.utc).isoformat(),'method':'MediaWiki action=query, redirects=1, prop=info, 50 requested titles maximum per request','note':'Title resolution only. No evidence of year-specific events, linked article coverage, gameplay implementation, or completed years. Revision IDs refer to canonical targets, which can change.','results':rows}
 dest.parent.mkdir(parents=True,exist_ok=True)
 # Exclusive creation protects existing research data.
 with dest.open('x',encoding='utf-8') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
 print(f'{len(rows)} year titles checked; {sum(bool(x["redirect_chain"]) for x in rows)} redirected; {sum(x["status"]=="missing" for x in rows)} missing. Title checks are not completed years. Saved {dest}.')
if __name__=='__main__':main()
