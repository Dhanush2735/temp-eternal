#!/usr/bin/env python3
"""Resumable, bounded English Wikipedia link-graph collector; not an R2 data installer.

python r2_wikipedia/crawl.py --max-pages 3
python r2_wikipedia/crawl.py --max-pages 100 --delay 6
python r2_wikipedia/crawl.py --stats

A page is committed only after both its revision and rendered links have been read.
The default starting point is the user's index; period pages are prioritized worldwide.
Source wikitext and revision IDs are saved; these are NOT game-ready facts.
"""
import argparse, gzip, json, os, sqlite3, sys, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
import requests
from periods import classify, priority
import millennium_scope
from storage_guard import within_budget

API = 'https://en.wikipedia.org/w/api.php'
SEEDS = ['List of decades, centuries, and millennia']
USER_AGENT = 'EternalEngineR2Research/0.1 (personal historical data research; Python requests)'
SCHEMA = '''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS frontier(title TEXT PRIMARY KEY, depth INTEGER NOT NULL,
 status TEXT NOT NULL DEFAULT 'pending', error TEXT, attempts INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS pages(pageid INTEGER PRIMARY KEY, title TEXT NOT NULL, revid INTEGER NOT NULL,
 revision_timestamp TEXT NOT NULL, retrieved_at TEXT NOT NULL, canonical_url TEXT NOT NULL,
 wikitext_gzip BLOB NOT NULL, link_count INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS edges(source_pageid INTEGER NOT NULL REFERENCES pages(pageid),
 source_revid INTEGER NOT NULL, target_title TEXT NOT NULL,
 PRIMARY KEY(source_pageid, source_revid, target_title)) WITHOUT ROWID;
CREATE TABLE IF NOT EXISTS resolutions(requested_title TEXT PRIMARY KEY, canonical_pageid INTEGER NOT NULL,
 canonical_title TEXT NOT NULL, source_revid INTEGER NOT NULL, checked_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS scheduler_state(key TEXT PRIMARY KEY, value INTEGER NOT NULL);
'''

class Client:
 def __init__(self, delay):
  self.s=requests.Session(); self.s.headers.update({'User-Agent':USER_AGENT,'Accept-Encoding':'gzip'}); self.delay=delay; self.last=0
 def get(self, params):
  for attempt in range(5):
   time.sleep(max(0,self.delay-(time.monotonic()-self.last)))
   try:
    r=self.s.get(API,params={'format':'json','formatversion':2,'maxlag':5,**params},timeout=60); self.last=time.monotonic()
    if r.status_code in (429, 500, 502, 503, 504):
     retry=r.headers.get('Retry-After',''); time.sleep(min(60,int(retry)) if retry.isdigit() else min(60,2**attempt*2));continue
    r.raise_for_status(); data=r.json()
    if 'error' in data:
     if data['error'].get('code') in ('maxlag','ratelimited','readonly'):
      time.sleep(min(60,2**attempt*2)); continue
     raise RuntimeError(json.dumps(data['error'],ensure_ascii=False))
    return data
   except (requests.RequestException, ValueError) as e:
    if attempt==4: raise RuntimeError(str(e)) from e
    time.sleep(min(60,2**attempt*2))
  raise RuntimeError('rate-limited or temporarily unavailable after retries')
 def page(self, title):
  j=self.get({'action':'query','titles':title,'redirects':1,'prop':'revisions|info','rvprop':'ids|timestamp|content','rvslots':'main','inprop':'url'})
  p=j['query']['pages'][0]
  if p.get('missing') or p.get('invalid'): return None
  rev=p['revisions'][0]; raw=rev['slots']['main']['content']
  result=self.get({'action':'parse','oldid':rev['revid'],'prop':'links'})['parse']
  # Namespace zero article links; redlinks are kept as edges but not added to the queue.
  links={x['title']:bool(x.get('exists')) for x in result.get('links',[]) if x.get('ns')==0 and x.get('title')}
  return p,rev,raw,links

def stats(db):
 print('frontier:',dict(db.execute('select status,count(*) from frontier group by status').fetchall()))
 print('pages:',db.execute('select count(*) from pages').fetchone()[0], 'edges:',db.execute('select count(*) from edges').fetchone()[0])
 for x in db.execute('select title,revid,link_count from pages order by rowid limit 20'):print(' ',*x)

def period_band(period):
 """Six 1,000-year bands; historical BCE numbering skips year zero."""
 return (period.start + 3000) // 1000 if period.start < 0 else 3 + (period.start - 1) // 1000


def choose_priority(db,current):
 """Choose a pending title at one priority, balancing periods across era bands."""
 if current not in (10,20,30,40):
  return db.execute("select title,depth from frontier where status='pending' and priority=? order by depth,title limit 1",(current,)).fetchone()
 attempts=[0]*6;pending=[]
 for title,depth,status in db.execute("select title,depth,status from frontier where priority=? and status in ('pending','done','missing')",(current,)):
  p=classify(title)
  if p is None:continue
  band=period_band(p)
  if not 0<=band<6:continue
  if status=='pending':pending.append((band,p.start,depth,title))
  else:attempts[band]+=1
 if not pending:return None
 band,_,depth,title=min(pending,key=lambda x:(attempts[x[0]],x[0],x[2],x[1],x[3]))
 return title,depth


def choose_next(db):
 """Chronology-priority selector; the queue is not a coverage measure."""
 current=db.execute("select min(priority) from frontier where status='pending'").fetchone()[0]
 return None if current is None else choose_priority(db,current)


def choose_fair(db,attempt,other_every=5,year_every=10):
 """Interleave year-title candidates and ordinary linked articles across eras.

 Every year_every-th slot, offset from ordinary-article slots, favors a year
 candidate once overview priorities are checked. This prevents years from being
 starved by the decade queue; a checked title is not a completed year.
 Every other_every-th attempt favors a non-period-title candidate, rotating era bands.

 The counter is persisted across short runs. Explicit priority-zero seeds still
 come first. Titles can redirect to period pages and imperfect classification can
 pick navigational or out-of-range period titles. Sources may link to articles
 of any era; no factual time coverage is implied. When no such linked title
 exists, use the BFS queue.
 """
 top=db.execute("select min(priority) from frontier where status='pending'").fetchone()[0]
 if top is None or top in (0,10,20):return choose_next(db)
 # Offset by one from the ordinary slot so the default 5/10 intervals do not collide.
 if year_every and attempt%year_every==1:
  year=choose_priority(db,40)
  if year:return year
 if not other_every or (attempt+1)%other_every:return choose_next(db)
 sources=[[] for _ in range(6)]
 for pid,title in db.execute('select pageid,title from pages'):
  p=classify(title)
  if p:
   band=period_band(p)
   if 0<=band<6:sources[band].append(pid)
 start=(attempt//other_every)%6
 for i in range(6):
  matches=[]
  for pid in sources[(start+i)%6]:
   row=db.execute("""select f.title,f.depth from edges e join pages p on p.pageid=e.source_pageid and p.revid=e.source_revid
     join frontier f on f.title=e.target_title where e.source_pageid=? and f.status='pending' and f.priority=100
     order by (lower(f.title) like '%century%' or lower(f.title) like '%millennium%'), (f.depth=1), f.depth,f.title limit 1""",(pid,)).fetchone()
   if row:matches.append(row)
  if matches:return min(matches,key=lambda r:(('century' in r[0].casefold() or 'millennium' in r[0].casefold()),r[1]==1,r[1],r[0]))
 return db.execute("select title,depth from frontier where status='pending' and priority=100 order by depth,title limit 1").fetchone() or choose_next(db)


def advance_scheduler(db,key='attempts'):
 db.execute("insert into scheduler_state values(?,1) on conflict(key) do update set value=value+1",(key,))


def main():
 ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--db',default='r2_wikipedia/crawl.sqlite3'); ap.add_argument('--max-pages',type=int,default=3); ap.add_argument('--delay',type=float,default=6.0);ap.add_argument('--max-db-mb',type=float,default=12.0,help='Stop before starting the next page when the database exceeds this size');ap.add_argument('--max-workspace-mb',type=float,default=125.0,help='Approximate persisted workspace ceiling in decimal MB, checked before each page');ap.add_argument('--stats',action='store_true');ap.add_argument('--retry-errors',action='store_true');ap.add_argument('--seed',action='append',default=[],help='Prioritize an additional exact Wikipedia article title; may be repeated');ap.add_argument('--other-every',type=int,default=5,help='Try a linked ordinary article every N requests; 0 disables interleaving');ap.add_argument('--year-every',type=int,default=10,help='Try a year-title candidate on an offset every N requests after overview pages; 0 disables');ap.add_argument('--scope',choices=['third-millennium-bc'],help='Follow the 3rd millennium BCE link chain first; other period titles remain deferred context'); args=ap.parse_args()
 if args.max_pages<0 or args.delay<0 or args.max_db_mb<=0 or args.max_workspace_mb<=0 or args.other_every<0 or args.year_every<0: ap.error('invalid limits')
 db_path=Path(args.db)
 if not db_path.exists() and Path(str(db_path)+'.xz').exists():
  ap.error('Staging database is parked; restore with r2_wikipedia/park_staging_databases.py before using the collector. The storage guard still applies.')
 db=sqlite3.connect(args.db);db.executescript(SCHEMA)
 if 'priority' not in [r[1] for r in db.execute('pragma table_info(frontier)')]:
  db.execute('alter table frontier add column priority integer not null default 100')
  db.executemany('update frontier set priority=? where title=?',[(priority(t),t) for (t,) in db.execute('select title from frontier').fetchall()])
 # Rebuild the optional queue index only with workspace reserve. Do not let
 # startup silently consume the remaining snapshot budget after maintenance.
 allowed,used=within_budget(args.max_workspace_mb)
 has_queue_index=db.execute("select 1 from sqlite_master where type='index' and name='frontier_priority'").fetchone() is not None
 queue_ready=has_queue_index or (allowed and used+2_000_000<args.max_workspace_mb*1_000_000)
 if queue_ready:
  db.execute('create index if not exists frontier_priority on frontier(status,priority,depth)')
 else:
  print('Queue index not rebuilt: insufficient workspace reserve; collection remains stopped.',flush=True)
 db.executemany('insert or ignore into frontier(title,depth,priority) values(?,0,?)',[(s,priority(s)) for s in SEEDS])
 if args.scope:
  db.execute('insert or ignore into frontier(title,depth,priority) values(?,0,?)',(millennium_scope.ROOT,priority(millennium_scope.ROOT)))
 for title in args.seed:
  db.execute("insert into frontier(title,depth,priority) values(?,0,0) on conflict(title) do update set depth=0,priority=0",(title,))
 db.commit()
 if args.retry_errors:db.execute("update frontier set status='pending',error=null where status='error'");db.commit()
 if args.stats:stats(db);return
 if not queue_ready:
  print('STOP: provision workspace before rebuilding the queue index and crawling.',flush=True)
  return
 c=Client(args.delay)
 for i in range(args.max_pages):
  allowed,used=within_budget(args.max_workspace_mb)
  if not allowed:
   print(f'STOP: estimated persistent workspace {used/1_000_000:.2f} MB reached {args.max_workspace_mb:.2f} MB guard; provision storage first.',flush=True);break
  if os.path.getsize(args.db) >= args.max_db_mb * 1024 * 1024:
   print('STOP: database size limit reached; increase only with adequate persistent storage.',flush=True);break
  key='scope:third-millennium-bc' if args.scope else 'attempts'
  state=db.execute('select value from scheduler_state where key=?',(key,)).fetchone()
  if args.scope:
   if not db.execute('select 1 from pages where title=?',(millennium_scope.ROOT,)).fetchone():
    row=db.execute("select title,depth from frontier where title=? and status='pending'",(millennium_scope.ROOT,)).fetchone()
   else:
    selection=millennium_scope.choose(db,state[0] if state else 0)
    row=db.execute('select title,depth from frontier where title=?',(selection[0],)).fetchone() if selection else None
  else:row=choose_fair(db,state[0] if state else 0,args.other_every,args.year_every)
  if not row:break
  title,depth=row
  try:
   item=c.page(title)
   with db:
    advance_scheduler(db)
    if args.scope:advance_scheduler(db,key)
    if item is None:
     db.execute("update frontier set status='missing',attempts=attempts+1,error=null where title=?",(title,));print('MISSING',title,flush=True);continue
    p,rev,raw,links=item; pid=p['pageid'];rid=rev['revid']; retrieved=datetime.now(timezone.utc).isoformat()
    db.execute('''INSERT INTO pages VALUES(?,?,?,?,?,?,?,?)
      ON CONFLICT(pageid) DO UPDATE SET title=excluded.title, revid=excluded.revid,
      revision_timestamp=excluded.revision_timestamp, retrieved_at=excluded.retrieved_at,
      canonical_url=excluded.canonical_url, wikitext_gzip=excluded.wikitext_gzip,
      link_count=excluded.link_count''',(pid,p['title'],rid,rev['timestamp'],retrieved,p.get('canonicalurl','https://en.wikipedia.org/wiki/'+quote(p['title'].replace(' ','_'))),gzip.compress(raw.encode('utf-8'),mtime=0),len(links)))
    db.execute('''insert into resolutions values(?,?,?,?,?) on conflict(requested_title) do update set
      canonical_pageid=excluded.canonical_pageid, canonical_title=excluded.canonical_title,
      source_revid=excluded.source_revid, checked_at=excluded.checked_at''',(title,pid,p['title'],rid,retrieved))
    db.executemany('insert or ignore into edges values(?,?,?)',[(pid,rid,t) for t in links])
    db.executemany('insert or ignore into frontier(title,depth,priority) values(?,?,?)',[(t,depth+1,priority(t)) for t,exists in links.items() if exists])
    db.execute("update frontier set status='done',attempts=attempts+1,error=null where title=?",(title,))
    # Canonical target may be queued separately after a redirect.
    db.execute("update frontier set status='done' where title=?",(p['title'],))
   print('READ',title,'->',p['title'],'revision',rid,'links',len(links),'depth',depth,flush=True)
  except Exception as e:
   with db:
    advance_scheduler(db)
    if args.scope:advance_scheduler(db,key)
    db.execute("update frontier set status='error',attempts=attempts+1,error=? where title=?",(str(e)[:1000],title))
   print('ERROR',title,str(e),file=sys.stderr,flush=True)
 stats(db)
if __name__=='__main__':main()
