#!/usr/bin/env python3
"""Temporarily remove two derived queue indexes, preserving all data.

Stop database writers first. Each copy is logically fingerprinted, sampled for
queue ordering, integrity-checked and atomically installed. Recreate indexes by
running the collectors once there is adequate workspace reserve. This can slow
manual queue queries until then. SQLite file bytes change; table data do not.
"""
import hashlib, json, os, sqlite3, stat
from pathlib import Path
from contextlib import closing
from compact_people import fingerprint
from compact_crawl import snapshot as crawl_snapshot
from compact_origin_links import full_snapshot
from crawl import choose_next, choose_priority, choose_fair
from people import next_batch
ROOT=Path(__file__).resolve().parent
CACHE=Path('/home/user/.cache/r2_park_queue_indexes')
SPECS=[('crawl.sqlite3','frontier_priority','CREATE INDEX frontier_priority ON frontier(status,priority,depth)'),('people.sqlite3','subject_queue',"CREATE INDEX subject_queue ON subjects(first_source) WHERE status='pending'")]
def verify(db):
 if db.execute('pragma integrity_check').fetchone()[0]!='ok':raise ValueError('integrity check')
 if db.execute('pragma foreign_key_check').fetchall():raise ValueError('foreign keys')
def schema(db,excluded):
 return list(db.execute("select type,name,tbl_name,sql from sqlite_master where name not like 'sqlite_%' and name!=? order by type,name",(excluded,)))
def snapshot(db,kind):
 if kind=='crawl.sqlite3':return crawl_snapshot(db)
 d=full_snapshot(db);d['origin_links_table']=fingerprint(db,'origin_links','subject_id,source_id,source_line');d['people_scheduler']=fingerprint(db,'people_scheduler','key');return d
def choice(db,kind):
 if kind=='crawl.sqlite3':return {'next':choose_next(db),'priority':{str(p):choose_priority(db,p) for p in (0,10,20,30,40,100)},'fair':[choose_fair(db,n) for n in (0,1,4,5,9,10)]}
 return {str(n):next_batch(db,n) for n in (1,5,25)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run_one(name,index,ddl):
 p=ROOT/name
 if not p.is_file():raise FileNotFoundError('Database absent or parked; restore before maintenance: '+str(p))
 if any(Path(str(p)+x).exists() for x in ('-wal','-journal','-shm')):raise ValueError('Stop and checkpoint all database writers: '+name)
 CACHE.mkdir(parents=True,exist_ok=True);work=CACHE/(name+'.work');backup=CACHE/(name+'.backup')
 if work.exists() or backup.exists():raise FileExistsError('Maintenance files already exist')
 src=sqlite3.connect(p,timeout=0);dest=None
 try:
  verify(src);found=src.execute("select sql from sqlite_master where type='index' and name=?",(index,)).fetchone()
  if not found or found[0].casefold()!=ddl.casefold():raise ValueError('Unexpected index; refusing migration: '+str(found))
  before=snapshot(src,name);sch=schema(src,index);selected=choice(src,name);oldsize=p.stat().st_size;oldsha=sha(p)
  with closing(sqlite3.connect(backup)) as b:src.backup(b)
  with closing(sqlite3.connect(work)) as w:src.backup(w)
  dest=sqlite3.connect(work);dest.execute('PRAGMA foreign_keys=ON');dest.execute('DROP INDEX '+index);dest.commit();dest.execute('VACUUM');verify(dest)
  if snapshot(dest,name)!=before or schema(dest,index)!=sch or choice(dest,name)!=selected:raise ValueError('data, schema or queue selection changed')
  dest.close();dest=None
  if work.stat().st_size>=oldsize:raise ValueError('no space saved')
  os.chmod(work,stat.S_IMODE(p.stat().st_mode));src.execute('BEGIN EXCLUSIVE')
  try:
   if snapshot(src,name)!=before or schema(src,index)!=sch:raise ValueError('source changed')
   with open(work,'rb') as f:os.fsync(f.fileno())
   os.replace(work,p)
  finally:src.rollback()
  result={'database':name,'parked_index':index,'restore_ddl':ddl,'old_bytes':oldsize,'new_bytes':p.stat().st_size,'saved_bytes':oldsize-p.stat().st_size,'before_file_sha256':oldsha,'after_file_sha256':sha(p),'table_fingerprints':before,'sample_queue_choices':selected,'integrity':'ok','foreign_keys':'ok','note':'Logical content preserved; SQLite bytes changed. Excluded-cache backup is temporary. Collector rebuilds index only when workspace reserve permits.'}
  return result
 finally:
  if dest:dest.close()
  src.close()
if __name__=='__main__':
 report=[]
 for spec in SPECS:
  result=run_one(*spec);report.append(result);print(result['database'],result['saved_bytes'],'bytes saved',flush=True)
 (ROOT/'focus/queue_indexes_parked_1662_2026-10.json').write_text(json.dumps({'records':report},ensure_ascii=False,indent=2)+'\n')
