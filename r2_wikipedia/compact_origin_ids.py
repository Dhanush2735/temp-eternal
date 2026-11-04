#!/usr/bin/env python3
"""One-time lossless migration of repeated origin candidate strings to integer keys.

The SQLite backup is temporary in excluded .cache. The logical fingerprint of
all subjects, biographies and six-column origins must match before and after.
"""
import argparse,json,os,sqlite3
from pathlib import Path
from compact_people import snapshot
from origin_schema import STATEMENTS


def migrate(db):
 cols={row[1] for row in db.execute('pragma table_info(origin_links)')}
 if 'candidate_id' not in cols or 'candidate_key' in cols:
  raise ValueError('Expected first-generation origin_links with text candidate_id')
 db.execute('BEGIN IMMEDIATE')
 try:
  before=snapshot(db)
  db.execute('DROP TRIGGER origins_insert');db.execute('DROP VIEW origins')
  db.execute('ALTER TABLE origin_links RENAME TO origin_links_old')
  for s in STATEMENTS:db.execute(s)
  db.execute('INSERT INTO origin_candidates(candidate_id) SELECT DISTINCT candidate_id FROM origin_links_old ORDER BY candidate_id')
  db.execute('''INSERT INTO origin_links(subject_id,source_id,source_pageid,source_revid,source_line,candidate_key)
   SELECT l.subject_id,l.source_id,l.source_pageid,l.source_revid,l.source_line,c.id
   FROM origin_links_old l JOIN origin_candidates c ON c.candidate_id=l.candidate_id''')
  if before!=snapshot(db):raise ValueError('Logical fingerprints changed; rolling back')
  db.execute('DROP TABLE origin_links_old')
  if db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Foreign key check failed')
  db.commit();return before
 except BaseException:
  db.rollback();raise


def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--db',default='r2_wikipedia/people.sqlite3');ap.add_argument('--backup',default='/home/user/.cache/r2_compaction/people_before_origin_ids.sqlite3');ap.add_argument('--log',default='r2_wikipedia/origin_id_compaction_log.json');a=ap.parse_args()
 size0=os.path.getsize(a.db);db=sqlite3.connect(a.db);db.execute('PRAGMA foreign_keys=ON')
 if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Initial database integrity check failed')
 backup=Path(a.backup);backup.parent.mkdir(parents=True,exist_ok=True)
 if backup.exists():raise FileExistsError(f'Backup exists: {backup}')
 with sqlite3.connect(str(backup)) as out:db.backup(out)
 before=migrate(db);db.execute('VACUUM')
 if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall() or snapshot(db)!=before:raise ValueError(f'Post-migration integrity failed; restore backup {backup}')
 db.close();size1=os.path.getsize(a.db)
 report={'original_bytes':size0,'compacted_bytes':size1,'saved_bytes':size0-size1,'logical_fingerprints':before,'integrity':'ok','foreign_keys':'ok','backup_temporary':str(backup),'warning':'Backup is in excluded .cache and will not persist.'}
 Path(a.log).write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
