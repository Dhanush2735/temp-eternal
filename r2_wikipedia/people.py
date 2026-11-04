#!/usr/bin/env python3
"""Discover linked people for R3, keeping the Wikipedia sources and all available details.

Discovery starts with links in the period-page candidates; it does not rely on name guesses.
Wikipedia supplies article text and identity; Wikidata is a separately labelled structured
cross-check. P31=Q5 establishes a positive identification, but its absence is NOT proof that
an article is not a person. Nothing is installed into the game by this tool.
"""
import argparse, gzip, io, json, os, re, sqlite3, sys, time
from staged_exports import open_text as open_staged_text
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import quote
import requests
from periods import classify
import millennium_scope
from extract_candidates import LINK
from origin_schema import SCHEMA as ORIGIN_SCHEMA
from storage_guard import within_budget
from sqlite_budget import people_page_cap, is_full

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'worldfill'))
from wikitext_clean import infobox_params, clean_text

UA='EternalEngineR3Research/0.1 (personal historical research; Python requests)'
SCHEMA='''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS subjects (
 id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL UNIQUE, first_source TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'pending', canonical TEXT, qid TEXT, error TEXT);
CREATE INDEX IF NOT EXISTS subject_queue ON subjects(first_source) WHERE status='pending';
CREATE INDEX IF NOT EXISTS subject_canonical ON subjects(canonical) WHERE canonical IS NOT NULL;
CREATE TABLE IF NOT EXISTS people_scheduler (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS biographies (
 pageid INTEGER PRIMARY KEY, title TEXT NOT NULL, wiki_revid INTEGER NOT NULL,
 wiki_timestamp TEXT NOT NULL, retrieved_at TEXT NOT NULL, qid TEXT NOT NULL,
 wikidata_revid INTEGER NOT NULL, wiki_gzip BLOB NOT NULL, wikidata_gzip BLOB NOT NULL);
''' + ORIGIN_SCHEMA

class Api:
 def __init__(self,delay):
  self.delay=delay;self.last=0;self.session=requests.Session();self.session.headers['User-Agent']=UA
 def get(self,url,params):
  for attempt in range(5):
   time.sleep(max(0,self.delay-(time.monotonic()-self.last)))
   try:
    r=self.session.get(url,params={'format':'json','formatversion':'2','maxlag':5,**params},timeout=90);self.last=time.monotonic()
    if r.status_code in (429,500,502,503,504):
     wait=r.headers.get('Retry-After','');time.sleep(min(60,int(wait)) if wait.isdigit() else min(60,2**(attempt+1)));continue
    r.raise_for_status();j=r.json()
    if 'error' in j:
     if j['error'].get('code') in ('maxlag','ratelimited','readonly'):
      time.sleep(min(60,2**(attempt+1)));continue
     raise RuntimeError(json.dumps(j['error'],ensure_ascii=False))
    return j
   except (requests.RequestException,ValueError) as e:
    if attempt==4:raise RuntimeError(str(e)) from e
    time.sleep(min(60,2**(attempt+1)))
  raise RuntimeError('temporary failure after retries')


def import_candidates(db,path):
 """Keep all non-period article targets, and their references, not only presumed people."""
 rows=0
 with open_staged_text(path) as f, db:
  for line in f:
   r=json.loads(line);src=r['source']
   for link in r['links']:
    title=link['title'].replace('_',' ').strip()
    if not title or classify(title):continue
    db.execute('insert or ignore into subjects(title,first_source) values(?,?)',(title,src['title']))
    db.execute('insert or ignore into origins values(?,?,?,?,?,?)',(title,src['page_id'],src['title'],src['revision_id'],src['line'],r['id']))
    rows+=1
 return rows


EXCLUDED_NAMESPACE = re.compile(r'^(?:File|Image|Category|Template|Help|Special|Wikipedia|Portal|Draft|User|Talk|MediaWiki|Module|Book|TimedText):', re.I)

def add_origin(db,title,source_id,source_title,source_revid,line,origin_id):
 title=norm_title(title)
 if not title or classify(title) or EXCLUDED_NAMESPACE.match(title): return False
 db.execute('insert or ignore into subjects(title,first_source) values(?,?)',(title,source_title))
 db.execute('insert or ignore into origins values(?,?,?,?,?,?)',(title,source_id,source_title,source_revid,line,origin_id))
 return True


def import_crawl_edges(db, crawl_path):
 """Import discovered existing namespace-0 links from every visited graph page, not only period bullets."""
 count=0
 c=sqlite3.connect(f'file:{Path(crawl_path).resolve()}?mode=ro',uri=True)
 with db:
  for title,pid,src,rev in c.execute('''select e.target_title,p.pageid,p.title,e.source_revid
    from edges e join pages p on p.pageid=e.source_pageid and p.revid=e.source_revid
    join frontier f on f.title=e.target_title where f.status != 'missing'
    order by p.title,e.target_title'''):
   if add_origin(db,title,pid,src,rev,0,f'crawl-edge:{pid}:{rev}'):count+=1
 c.close();return count


def import_biography_links(db):
 """Follow explicit wikilinks in saved biographies. Templates need the full crawler later."""
 count=0
 rows=db.execute('select pageid,title,wiki_revid,wiki_gzip from biographies order by title').fetchall()
 with db:
  for pid,src,rev,blob in rows:
   for no,line in enumerate(gzip.decompress(blob).decode('utf8').splitlines(),1):
    for m in LINK.finditer(line):
     if add_origin(db,m.group(1),pid,src,rev,no,f'article-link:{pid}:{rev}:{no}'):count+=1
 return count


def next_batch(db,n,cursor=None):
 """Round-robin by first source, starting after the last persisted source when supplied.

 This is fairness between discovered source pages, not a guarantee of geographic or era coverage.
 Selection is read-only: advance the cursor in the same transaction as the batch outcome.
 """
 groups=[r[0] for r in db.execute("select distinct first_source from subjects where status='pending' order by first_source")]
 result=[]
 if not groups or n<=0:return result
 if cursor is not None:
  # Python's ordering matches SQLite's BINARY collation on valid Unicode strings.
  from bisect import bisect_right
  offset=bisect_right(groups,cursor)%len(groups)
  groups=groups[offset:]+groups[:offset]
 data={g:[x[0] for x in db.execute("select title from subjects where status='pending' and first_source=? order by id limit ?",(g,n))] for g in groups}
 for i in range(n):
  for g in groups:
   if i<len(data[g]):
    result.append(data[g][i])
    if len(result)>=n:return result
 return result


def scoped_next_batch(db,crawl_db,n,cursor=None):
 """Round-robin pending titles linked from reached current-revision source pages.

 The origin must match a current reached page's ID and revision. A linked title
 is a candidate only, not proof of a person or of a date in the millennium.
 Returns (title, source title) pairs; the latter drives the independent cursor.
 """
 g=millennium_scope.graph(crawl_db);canonical=g['visited_canonical']
 valid={(pid,rev) for pid,title,rev in crawl_db.execute('select pageid,title,revid from pages') if title in canonical}
 # Follow already-saved human biographies reached through this chain, even if
 # that biography has not also been fetched as a standalone crawler page.
 biographies={title:(pid,rev) for pid,title,rev in db.execute('select pageid,title,wiki_revid from biographies')}
 links=db.execute('''select distinct s.canonical,o.source_pageid,o.source_revid
   from subjects s join origin_links l on l.subject_id=s.id join origin_sources o on o.id=l.source_id
   where s.status='human' and s.canonical is not null''').fetchall()
 changed=True
 while changed:
  changed=False
  for title,pid,rev in links:
   person=biographies.get(title)
   if (pid,rev) in valid and person and person not in valid:valid.add(person);changed=True
 groups={}
 for title,sid,src,pid,rev in db.execute('''select s.title,s.id,o.source_title,o.source_pageid,o.source_revid
   from subjects s join origin_links l on l.subject_id=s.id join origin_sources o on o.id=l.source_id
   where s.status='pending' order by o.source_title,s.id'''):
  if (pid,rev) in valid:groups.setdefault(src,{})[sid]=title
 names=sorted(groups)
 if not names or n<=0:return []
 if cursor is not None:
  from bisect import bisect_right
  offset=bisect_right(names,cursor)%len(names);names=names[offset:]+names[:offset]
 rows={k:list(groups[k].values()) for k in names};result=[];seen=set();i=0
 while len(result)<n:
  for name in names:
   if i<len(rows[name]) and rows[name][i] not in seen:
    title=rows[name][i];seen.add(title);result.append((title,name))
    if len(result)>=n:break
  i+=1
  if i>=max(map(len,rows.values())):break
 return result


def scheduler_cursor(db,key='last_source'):
 row=db.execute('select value from people_scheduler where key=?',(key,)).fetchone()
 return row[0] if row else None


def advance_scheduler(db,last_source,key='last_source'):
 if last_source is not None:
  db.execute('insert into people_scheduler(key,value) values(?,?) on conflict(key) do update set value=excluded.value',(key,last_source))


def is_human(entity):
 for claim in entity.get('claims',{}).get('P31',[]):
  if claim.get('rank')=='deprecated':continue
  if claim.get('mainsnak',{}).get('datavalue',{}).get('value',{}).get('id')=='Q5':return True
 return False


def norm_title(t):return t.replace('_',' ').strip()


def fetch_batch(api,db,titles,last_source=None,scheduler_key='last_source'):
 wp=api.get('https://en.wikipedia.org/w/api.php',{'action':'query','titles':'|'.join(titles),'redirects':1,
   'prop':'revisions|pageprops|info','ppprop':'wikibase_item','rvprop':'ids|timestamp|content','rvslots':'main','inprop':'url'})['query']
 # Follow MediaWiki's normalization and redirect map, including chains.
 mapping={norm_title(x['from']):norm_title(x['to']) for x in wp.get('normalized',[])+wp.get('redirects',[])}
 pages={norm_title(p['title']):p for p in wp.get('pages',[])}
 resolved={}
 for title in titles:
  key=norm_title(title); seen=set()
  while key in mapping and key not in seen:seen.add(key);key=mapping[key]
  resolved[title]=pages.get(key)
 qids=sorted({p.get('pageprops',{}).get('wikibase_item') for p in resolved.values() if p and p.get('pageprops',{}).get('wikibase_item')})
 entities={}
 if qids:
  entities=api.get('https://www.wikidata.org/w/api.php',{'action':'wbgetentities','ids':'|'.join(qids),
     'props':'claims|labels|descriptions|info','languages':'en'})['entities']
 now=datetime.now(timezone.utc).isoformat()
 with db:
  for title in titles:
   p=resolved[title]
   if not p or p.get('missing') or p.get('invalid'):
    db.execute("update subjects set status='missing',error=null where title=?",(title,));continue
   q=p.get('pageprops',{}).get('wikibase_item')
   if not q:
    db.execute("update subjects set status='unresolved',canonical=?,error='Wikipedia page has no Wikidata item' where title=?",(p['title'],title));continue
   e=entities.get(q)
   if not e or e.get('missing'):
    db.execute("update subjects set status='unresolved',canonical=?,qid=?,error='Wikidata entity unavailable' where title=?",(p['title'],q,title));continue
   if not is_human(e):
    db.execute("update subjects set status='unconfirmed',canonical=?,qid=?,error='No non-deprecated human (P31=Q5) statement' where title=?",(p['title'],q,title));continue
   rev=p['revisions'][0];wiki=rev['slots']['main']['content']
   db.execute('''INSERT INTO biographies VALUES(?,?,?,?,?,?,?,?,?)
     ON CONFLICT(pageid) DO UPDATE SET title=excluded.title,wiki_revid=excluded.wiki_revid,
     wiki_timestamp=excluded.wiki_timestamp,retrieved_at=excluded.retrieved_at,qid=excluded.qid,
     wikidata_revid=excluded.wikidata_revid,wiki_gzip=excluded.wiki_gzip,wikidata_gzip=excluded.wikidata_gzip''',
     (p['pageid'],p['title'],rev['revid'],rev['timestamp'],now,q,e['lastrevid'],gzip.compress(wiki.encode(),mtime=0),
      gzip.compress(json.dumps(e,ensure_ascii=False,separators=(',',':')).encode(),mtime=0)))
   db.execute("update subjects set status='human',canonical=?,qid=?,error=null where title=?",(p['title'],q,title))
  # Commit selection position together with the outcomes so an interrupted request retries safely.
  advance_scheduler(db,last_source,scheduler_key)


def export(db,path):
 count=0
 with open(path,'wb') as raw, gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as out:
  for pageid,title,rev,stamp,when,qid,wdrev,wiki,entity in db.execute('select * from biographies order by title'):
   w=gzip.decompress(wiki).decode(); e=json.loads(gzip.decompress(entity));fields=infobox_params(w)
   # Retain every infobox field, including source markup. Clean strings are convenience only.
   origins=[{'source_title':s,'source_pageid':pid,'source_revision':r,'line':line,'candidate_id':cid,'linked_title':link}
      for link,s,pid,r,line,cid in db.execute('''select s.title,p.source_title,p.source_pageid,p.source_revid,l.source_line,c.candidate_id
       from subjects s join origin_links l on l.subject_id=s.id join origin_sources p on p.id=l.source_id
       join origin_candidates c on c.id=l.candidate_key
       where s.canonical=? order by p.source_title,l.source_line,s.title''',(title,))]
   record={'status':'wikipedia_biography_candidate','name':title,'identity':{'wikidata_id':qid,'human_crosscheck':'P31=Q5'},
    'wikipedia_source':{'page_id':pageid,'revision_id':rev,'revision_timestamp':stamp,'retrieved_at':when,
      'url':'https://en.wikipedia.org/w/index.php?title='+quote(title.replace(' ','_'))+'&oldid='+str(rev)},
    'discovered_from':origins,'infobox':{'raw_fields':fields,'display_fields':{k:clean_text(v).strip() for k,v in fields.items()}},
    'wikidata_source':{'entity_id':qid,'revision_id':wdrev,'url':'https://www.wikidata.org/w/index.php?title='+qid+'&oldid='+str(wdrev),
       'description_en':e.get('descriptions',{}).get('en',{}).get('value'), 'claims':e.get('claims',{})},
    'note':'Raw source data; unreviewed, not a game-ready NPC. Dates and roles may be uncertain, disputed or anachronistic.'}
   out.write((json.dumps(record,ensure_ascii=False,separators=(',',':'))+'\n').encode());count+=1
 return count


def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--db',default='r2_wikipedia/people.sqlite3');a.add_argument('--crawl-db',default='r2_wikipedia/crawl.sqlite3');a.add_argument('--candidates',default='r2_wikipedia/candidates.jsonl.gz');a.add_argument('--out',default='r2_wikipedia/people_candidates.jsonl.gz');a.add_argument('--max-check',type=int,default=20);a.add_argument('--batch-size',type=int,default=20);a.add_argument('--delay',type=float,default=6);a.add_argument('--max-db-mb',type=float,default=8);a.add_argument('--max-workspace-mb',type=float,default=125.0,help='Approximate persisted workspace ceiling in decimal MB, checked before imports and batches');a.add_argument('--retry-errors',action='store_true');a.add_argument('--stats',action='store_true');a.add_argument('--scope',choices=['third-millennium-bc'],help='Check titles linked from the reached 3rd millennium BCE chain');args=a.parse_args()
 if args.max_check<0 or not 1<=args.batch_size<=50 or args.delay<0 or args.max_db_mb<=0 or args.max_workspace_mb<=0:a.error('invalid limits')
 db_path=Path(args.db)
 if not db_path.exists() and Path(str(db_path)+'.xz').exists():
  a.error('Staging database is parked; restore with r2_wikipedia/park_staging_databases.py before using the collector. The storage guard still applies.')
 crawl_path=Path(args.crawl_db)
 if not crawl_path.exists() and Path(str(crawl_path)+'.xz').exists():
  a.error('Crawl staging database is parked; restore it before using the people collector.')
 # The large optional queue index may be absent after storage maintenance. Avoid
 # rebuilding it before the workspace guard; collectors need spare space to do so.
 allowed,used=within_budget(args.max_workspace_mb)
 workspace_limit=int(args.max_workspace_mb*1_000_000)
 queue_sql="CREATE INDEX IF NOT EXISTS subject_queue ON subjects(first_source) WHERE status='pending';"
 db=sqlite3.connect(args.db)
 queue_exists=db.execute("select 1 from sqlite_master where type='index' and name='subject_queue'").fetchone() is not None
 may_build=allowed and used+2_000_000<workspace_limit
 db.executescript(SCHEMA if queue_exists or may_build else SCHEMA.replace(queue_sql,''))
 if not queue_exists and not may_build:
  print('Queue index not rebuilt: insufficient workspace reserve; collection remains stopped.',flush=True)
  allowed=False
 db_limit=int(args.max_db_mb*1024*1024)
 cap=people_page_cap(db,db_limit,used,workspace_limit) if allowed else None
 storage_stopped=False
 if allowed and cap is not None and os.path.getsize(args.db) < db_limit:
  try:
   n=import_candidates(db,args.candidates); edges=import_crawl_edges(db,args.crawl_db); bios=import_biography_links(db)
   print('discovery mentions: period bullets',n,'crawl graph',edges,'biographies',bios,flush=True)
  except sqlite3.Error as e:
   if not is_full(e):raise
   db.rollback();storage_stopped=True
   print('STOP importing: SQLite page cap reached; the current import transaction was rolled back',flush=True)
 else:
  storage_stopped=True
  print('STOP importing: people database or estimated workspace size limit reached',flush=True)
 if args.retry_errors and not storage_stopped:
  try:
   with db:db.execute("update subjects set status='pending',error=null where status='error'")
  except sqlite3.Error as e:
   if not is_full(e):raise
   db.rollback();storage_stopped=True
   print('STOP retrying errors: SQLite page cap reached',flush=True)
 print('unique titles:',db.execute('select count(*) from subjects').fetchone()[0],flush=True)
 api=Api(args.delay);remaining=0 if args.stats or storage_stopped else args.max_check
 scoped_crawl=sqlite3.connect(f'file:{Path(args.crawl_db).resolve()}?mode=ro',uri=True) if args.scope else None
 scheduler_key='scope:third-millennium-bc' if args.scope else 'last_source'
 while remaining:
  allowed,used=within_budget(args.max_workspace_mb)
  if not allowed:print(f'STOP: estimated persistent workspace {used/1_000_000:.2f} MB reached {args.max_workspace_mb:.2f} MB guard; provision storage first');break
  if os.path.getsize(args.db)>=args.max_db_mb*1024*1024:print('STOP: people database size limit reached');break
  if scoped_crawl:
   choices=scoped_next_batch(db,scoped_crawl,min(args.batch_size,remaining),scheduler_cursor(db,scheduler_key))
   titles=[title for title,_ in choices]
   last_source=choices[-1][1] if choices else None
  else:
   titles=next_batch(db,min(args.batch_size,remaining),scheduler_cursor(db))
   last_source=db.execute('select first_source from subjects where title=?',(titles[-1],)).fetchone()[0] if titles else None
  if not titles:break
  try:
   fetch_batch(api,db,titles,last_source,scheduler_key)
  except Exception as e:
   if is_full(e):
    db.rollback()
    print('STOP checking: SQLite page cap reached; batch outcome was rolled back',flush=True)
    break
   try:
    with db:
     db.executemany("update subjects set status='error',error=? where title=?",[(str(e)[:1000],t) for t in titles])
     advance_scheduler(db,last_source,scheduler_key)
   except sqlite3.Error as write_error:
    if not is_full(write_error):raise
    db.rollback()
    print('STOP checking: SQLite page cap reached while saving error; batch will be retried',flush=True)
    break
   print('BATCH ERROR:',e,file=sys.stderr,flush=True)
  remaining-=len(titles)
  print('checked',len(titles),'status',dict(db.execute('select status,count(*) from subjects group by status')),flush=True)
 count=export(db,args.out)
 print('exported',count,'identified human biographies to',args.out,flush=True)
 print('integrity:',db.execute('pragma integrity_check').fetchone()[0],flush=True)
 if scoped_crawl:scoped_crawl.close()
 db.close()
if __name__=='__main__':main()
