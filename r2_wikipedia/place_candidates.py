#!/usr/bin/env python3
"""Resolve place entities referenced by VIP candidates, without guessing where people lived.

Coordinates come from Wikidata, not the English Wikipedia article. A birthplace is not
an NPC location for their whole life; this is staging data and cannot spawn an NPC.
"""
import argparse,gzip,json,os,sqlite3
from staged_exports import open_text as open_staged_text
from pathlib import Path
from datetime import datetime,timezone
from people import Api
from storage_guard import within_budget

ROLES=('birth_place','death_place','residence','work_location')
SCHEMA='''
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS places(qid TEXT PRIMARY KEY,status TEXT NOT NULL DEFAULT 'pending',
 label TEXT,revision INTEGER,checked_at TEXT,coordinates_json TEXT,error TEXT);
CREATE TABLE IF NOT EXISTS place_links(qid TEXT NOT NULL REFERENCES places(qid),person_qid TEXT NOT NULL,
 role TEXT NOT NULL,statement_id TEXT NOT NULL,PRIMARY KEY(qid,person_qid,role,statement_id));
'''

def sync(db,path):
 with open_staged_text(path) as f,db:
  for line in f:
   r=json.loads(line)
   for role in ROLES:
    for claim in r['details'].get(role,[]):
     if claim['rank']=='deprecated':continue
     q=claim['value'].get('entity_id')
     if not q or not q.startswith('Q'):continue
     db.execute('insert or ignore into places(qid) values(?)',(q,))
     db.execute('insert or ignore into place_links values(?,?,?,?)',(q,r['id'],role,claim.get('statement_id') or ''))

def fetch(api,db,qids):
 result=api.get('https://www.wikidata.org/w/api.php',{'action':'wbgetentities','ids':'|'.join(qids),'props':'claims|labels|info','languages':'en'})['entities']
 now=datetime.now(timezone.utc).isoformat()
 with db:
  for q in qids:
   ent=result.get(q)
   if not ent or ent.get('missing'):
    db.execute("update places set status='unresolved',error='entity missing' where qid=?",(q,));continue
   claims=ent.get('claims',{}).get('P625',[])
   # Save full coordinate claims including provenance, rank, qualifiers, globe and precision.
   db.execute("update places set status=?,label=?,revision=?,checked_at=?,coordinates_json=?,error=null where qid=?",
    ('resolved' if claims else 'no_coordinates',ent.get('labels',{}).get('en',{}).get('value'),ent['lastrevid'],now,json.dumps(claims,ensure_ascii=False,separators=(',',':')),q))

def export(db,path):
 with open(path,'wb') as f,gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0) as out:
  for q,status,label,rev,stamp,claims in db.execute("select qid,status,label,revision,checked_at,coordinates_json from places where status in ('resolved','no_coordinates') order by qid"):
   links=[{'person_id':pid,'role':role,'statement_id':s} for pid,role,s in db.execute('select person_qid,role,statement_id from place_links where qid=? order by person_qid,role',(q,))]
   r={'id':q,'name':label,'status':status,'wikidata_revision':rev,'retrieved_at':stamp,
      'source_url':f'https://www.wikidata.org/w/index.php?title={q}&oldid={rev}',
      'coordinate_claims':json.loads(claims),'related_people':links,
      'note':'Place coordinate statements are unreviewed. Location and date of a person are not inferred from these coordinates.'}
   out.write((json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n').encode())

def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--input',default='r2_wikipedia/vip_candidates.jsonl.gz');a.add_argument('--db',default='r2_wikipedia/places.sqlite3');a.add_argument('--output',default='r2_wikipedia/place_candidates.jsonl.gz');a.add_argument('--max-check',type=int,default=20);a.add_argument('--batch-size',type=int,default=20);a.add_argument('--delay',type=float,default=6);a.add_argument('--max-db-mb',type=float,default=2);a.add_argument('--max-workspace-mb',type=float,default=125.0,help='Approximate persisted workspace ceiling in decimal MB, checked before imports and batches');a.add_argument('--stats',action='store_true');args=a.parse_args()
 if args.max_check<0 or not 1<=args.batch_size<=50 or args.delay<0 or args.max_db_mb<=0 or args.max_workspace_mb<=0:a.error('invalid limits')
 db=sqlite3.connect(args.db);db.executescript(SCHEMA)
 allowed,used=within_budget(args.max_workspace_mb)
 if allowed and os.path.getsize(args.db)<args.max_db_mb*1024*1024:sync(db,args.input)
 else:print('STOP importing: places database or estimated workspace size limit reached',flush=True)
 api=Api(args.delay);remaining=0 if args.stats else args.max_check
 while remaining:
  allowed,used=within_budget(args.max_workspace_mb)
  if not allowed:print(f'STOP: estimated persistent workspace {used/1_000_000:.2f} MB reached {args.max_workspace_mb:.2f} MB guard');break
  if os.path.getsize(args.db)>=args.max_db_mb*1024*1024:print('STOP: places database size limit reached');break
  qids=[r[0] for r in db.execute("select qid from places where status='pending' order by qid limit ?",(min(remaining,args.batch_size),))]
  if not qids:break
  try:fetch(api,db,qids)
  except Exception as e:
   # Leave pending, not missing: this may be temporary and is safe to retry.
   print('batch error; left pending:',e);break
  remaining-=len(qids);print('checked',len(qids),flush=True)
 export(db,args.output);print('place statuses:',dict(db.execute('select status,count(*) from places group by status')));print('integrity:',db.execute('pragma integrity_check').fetchone()[0])
if __name__=='__main__':main()
