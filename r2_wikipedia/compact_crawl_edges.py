#!/usr/bin/env python3
"""Losslessly remove redundant crawl-edge indexes using SQLite WITHOUT ROWID.

No titles, edges, revisions, pages, queue states or scheduler counters are dropped.
The old edges table's composite primary key and separate rowid required two copies
of every edge. No pipeline query uses the target-only index. The migration checks
logical fingerprints and integrity and commits atomically before VACUUM.
"""
import argparse,json,os,sqlite3
from pathlib import Path
from compact_crawl import snapshot


def migrate(db):
 db.execute('PRAGMA foreign_keys=ON')
 db.execute('CREATE TABLE IF NOT EXISTS scheduler_state(key TEXT PRIMARY KEY, value INTEGER NOT NULL)')
 db.commit()
 before=snapshot(db)
 schema=db.execute("select sql from sqlite_master where type='table' and name='edges'").fetchone()[0]
 try:
  db.execute('BEGIN IMMEDIATE')
  if 'WITHOUT ROWID' not in schema.upper():
   db.execute('''CREATE TABLE edges_compact(source_pageid INTEGER NOT NULL REFERENCES pages(pageid),
     source_revid INTEGER NOT NULL, target_title TEXT NOT NULL,
     PRIMARY KEY(source_pageid,source_revid,target_title)) WITHOUT ROWID''')
   db.execute('INSERT INTO edges_compact SELECT source_pageid,source_revid,target_title FROM edges')
   db.execute('DROP TABLE edges')
   db.execute('ALTER TABLE edges_compact RENAME TO edges')
  db.execute('DROP INDEX IF EXISTS target_idx')
  if snapshot(db)!=before:raise ValueError('Logical content changed; rolling back')
  if db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Foreign key failure; rolling back')
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Integrity failure; rolling back')
  db.commit()
 except BaseException:
  db.rollback();raise
 db.execute('VACUUM')
 if snapshot(db)!=before:raise ValueError('Content changed after vacuum')
 if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Post-vacuum integrity failure')
 return before


def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--db',default='r2_wikipedia/crawl.sqlite3')
 ap.add_argument('--log',default='r2_wikipedia/crawl_edge_compaction_log.json')
 a=ap.parse_args();old=os.path.getsize(a.db)
 db=sqlite3.connect(a.db);data=migrate(db);db.close();new=os.path.getsize(a.db)
 result={'original_bytes':old,'compacted_bytes':new,'saved_bytes':old-new,'logical_record_fingerprints':data,'integrity':'ok','foreign_keys':'ok'}
 Path(a.log).write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
