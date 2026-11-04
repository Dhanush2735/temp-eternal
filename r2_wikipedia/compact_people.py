#!/usr/bin/env python3
"""Losslessly normalize the people-discovery graph, then reclaim free SQLite pages.

Backs up the original DB under /home/user/.cache before any change. All six columns
of every origin row, every subject, and every biography are checked by count and SHA256
before committing and after VACUUM. Existing user/game data is never changed.
"""
import argparse,hashlib,json,os,sqlite3,time
from pathlib import Path
from origin_schema import STATEMENTS


def fingerprint(db,table,order):
 h=hashlib.sha256();count=0
 for row in db.execute(f'SELECT * FROM {table} ORDER BY {order}'):
  for v in row:
   if isinstance(v,bytes):tag=b'B';data=v
   elif v is None:tag=b'N';data=b''
   else:tag=b'T';data=str(v).encode('utf8')
   h.update(tag);h.update(len(data).to_bytes(8,'big'));h.update(data)
  count+=1
 return {'rows':count,'sha256':h.hexdigest()}


def snapshot(db):
 return {t:fingerprint(db,t,order) for t,order in (
  ('subjects','id'),('biographies','pageid'),
  ('origins','title,source_pageid,source_revid,source_line,source_title,candidate_id'))}


def migrate(db):
 obj=db.execute("select type from sqlite_master where name='origins'").fetchone()
 if not obj or obj[0]!='table':raise ValueError('Expected legacy origins table; already migrated or invalid database.')
 db.execute('BEGIN IMMEDIATE')
 try:
  before=snapshot(db)
  db.execute('ALTER TABLE origins RENAME TO origins_legacy')
  for s in STATEMENTS:db.execute(s)
  db.execute('''INSERT OR IGNORE INTO origin_sources(source_pageid,source_title,source_revid)
   SELECT DISTINCT source_pageid,source_title,source_revid FROM origins_legacy
   ORDER BY source_pageid,source_revid,source_title''')
  db.execute('''INSERT OR IGNORE INTO origin_candidates(candidate_id)
   SELECT DISTINCT candidate_id FROM origins_legacy ORDER BY candidate_id''')
  db.execute('''INSERT INTO origin_links(subject_id,source_id,source_pageid,source_revid,source_line,candidate_key)
   SELECT s.id,p.id,o.source_pageid,o.source_revid,o.source_line,c.id
   FROM origins_legacy o JOIN subjects s ON s.title=o.title
   JOIN origin_sources p ON p.source_pageid=o.source_pageid AND p.source_title=o.source_title AND p.source_revid=o.source_revid
   JOIN origin_candidates c ON c.candidate_id=o.candidate_id''')
  after=snapshot(db)
  if before!=after:raise ValueError('Logical data mismatch before commit')
  db.execute('DROP TABLE origins_legacy')
  if db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Foreign key check failed')
  db.commit()
  return before
 except BaseException:
  db.rollback();raise


def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--db',default='r2_wikipedia/people.sqlite3');ap.add_argument('--backup',default='/home/user/.cache/r2_compaction/people_before.sqlite3');ap.add_argument('--log',default='r2_wikipedia/compaction_log.json');a=ap.parse_args()
 size0=os.path.getsize(a.db);db=sqlite3.connect(a.db);db.execute('PRAGMA foreign_keys=ON')
 if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Initial integrity check failed')
 backup=Path(a.backup);backup.parent.mkdir(parents=True,exist_ok=True)
 if backup.exists():raise FileExistsError(f'Backup exists; choose a new backup path: {backup}')
 target=sqlite3.connect(str(backup));db.backup(target);target.close()
 before=migrate(db);db.execute('VACUUM')
 if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError(f'Integrity failed after VACUUM; backup: {backup}')
 if db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError(f'Foreign keys failed after VACUUM; backup: {backup}')
 after=snapshot(db)
 if before!=after:raise ValueError(f'Data changed after VACUUM; backup: {backup}')
 db.close();size1=os.path.getsize(a.db)
 report={'original_bytes':size0,'compacted_bytes':size1,'saved_bytes':size0-size1,
  'logical_record_fingerprints':before,'backup_temporary':str(backup),'integrity':'ok','foreign_keys':'ok',
  'note':'All origin rows, subjects and biography blobs matched before and after. Backup is temporary and excluded from workspace snapshots.'}
 Path(a.log).write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
