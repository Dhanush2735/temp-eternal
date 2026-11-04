#!/usr/bin/env python3
"""Compact crawler index without deleting data. Stop all database writers first.

The title suffix duplicated long strings already indexed by the frontier primary
key. SQLite can sort title ties at query time. This migration preserves all data,
checks scheduler selections and integrity, and atomically replaces a verified copy.
Temporary working and backup copies are in excluded cache, not durable snapshots.
"""
import hashlib,json,os,sqlite3,stat
from pathlib import Path
from contextlib import closing
from compact_crawl import snapshot
from crawl import choose_priority,choose_next,choose_fair
ROOT=Path(__file__).resolve().parent
DB=ROOT/'crawl.sqlite3'
CACHE=Path('/home/user/.cache/r2_compaction')
WORK=CACHE/'crawl_frontier_compact_112_work.sqlite3'
BACKUP=CACHE/'crawl_frontier_compact_112_backup.sqlite3'
LOG=ROOT/'focus/frontier_index_compaction_112_CE.json'
OLD='CREATE INDEX frontier_priority on frontier(status,priority,depth,title)'
NEW='CREATE INDEX frontier_priority ON frontier(status,priority,depth)'
def verify(db):
 if db.execute('pragma integrity_check').fetchone()[0]!='ok':raise ValueError('Integrity failure')
 if db.execute('pragma foreign_key_check').fetchall():raise ValueError('Foreign-key failure')
def choices(db):
 out={'next':choose_next(db),'priority':{p:choose_priority(db,p) for p in (0,10,20,30,40,100)},'fair':[choose_fair(db,n) for n in (0,1,4,5,9,10,11)]}
 db.execute('SAVEPOINT exercise_no_priority_zero')
 try:
  db.execute("update frontier set status='done' where status='pending' and priority=0")
  out['no_zero_fair']=[choose_fair(db,n) for n in (0,1,4,5,9,10,11)]
 finally:db.execute('ROLLBACK TO exercise_no_priority_zero');db.execute('RELEASE exercise_no_priority_zero')
 return out
def digest(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()
def main():
 if not DB.is_file():raise FileNotFoundError('Crawler database absent or parked; restore before maintenance: '+str(DB))
 if any(Path(str(DB)+suffix).exists() for suffix in ('-journal','-wal','-shm')):raise ValueError('Stop database writers and checkpoint first')
 CACHE.mkdir(parents=True,exist_ok=True)
 if WORK.exists() or BACKUP.exists() or LOG.exists():raise FileExistsError('Refusing to overwrite working, backup or log')
 src=sqlite3.connect(DB,timeout=0);dst=None
 try:
  verify(src);oldindex=src.execute("select sql from sqlite_master where name='frontier_priority'").fetchone()
  if not oldindex or oldindex[0]!=OLD:raise ValueError('Unexpected original index; original untouched')
  before=snapshot(src);before_choices=choices(src);before_size=DB.stat().st_size;oldhash=digest(DB)
  with closing(sqlite3.connect(BACKUP)) as b:src.backup(b)
  with closing(sqlite3.connect(WORK)) as w:src.backup(w)
  dst=sqlite3.connect(WORK);dst.execute('PRAGMA foreign_keys=ON');dst.execute('DROP INDEX frontier_priority');dst.execute(NEW);dst.commit();dst.execute('VACUUM');verify(dst)
  if snapshot(dst)!=before or choices(dst)!=before_choices:raise ValueError('Data or scheduler selection changed; original untouched')
  if WORK.stat().st_size>=before_size:raise ValueError('No reduction; original untouched')
  dst.close();dst=None;os.chmod(WORK,stat.S_IMODE(DB.stat().st_mode));src.execute('BEGIN EXCLUSIVE')
  try:
   if snapshot(src)!=before or choices(src)!=before_choices:raise ValueError('Source changed during maintenance')
   with open(WORK,'rb') as f:os.fsync(f.fileno())
   os.replace(WORK,DB)
  finally:src.rollback()
 finally:
  if dst:dst.close()
  src.close()
 result={'original_bytes':before_size,'new_bytes':DB.stat().st_size,'saved_bytes':before_size-DB.stat().st_size,'old_index':OLD,'new_index':NEW,'before_raw_sha256':oldhash,'after_raw_sha256':digest(DB),'table_fingerprints':before,'scheduler_choices':before_choices,'integrity':'ok','foreign_keys':'ok','note':'Index-only schema change. Cache backup does not persist; data fingerprinted. Some title-tie sorting may be slower. Stop collectors before maintenance.'}
 LOG.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('saved',result['saved_bytes'],'bytes; integrity, all crawler tables and sampled scheduler selections verified')
if __name__=='__main__':main()
