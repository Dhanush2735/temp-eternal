#!/usr/bin/env python3
"""Normalize redundant page/revision columns from people-provenance links.

The old table repeated page ID and revision ID both in every origin link and in
its source row. The origins view and original duplicate-key behavior are kept.
A BEFORE INSERT trigger compares source page/revision, including when one page
has multiple source titles. The migration refuses inconsistent old data.
"""
import argparse,json,os,sqlite3
from pathlib import Path
from compact_people import fingerprint,snapshot


def full_snapshot(db):
 data=snapshot(db)
 for name,order in (('origin_sources','id'),('origin_candidates','id'),('sqlite_sequence','name')):
  data[name]=fingerprint(db,name,order)
 return data


def migrate(db):
 db.execute('PRAGMA foreign_keys=ON')
 cols={x[1] for x in db.execute('pragma table_info(origin_links)')}
 if not {'source_pageid','source_revid','candidate_key'} <= cols:
  raise ValueError('Expected second-generation origin links; already migrated or invalid')
 db.commit();db.execute('BEGIN IMMEDIATE')
 try:
  before=full_snapshot(db)
  bad=db.execute('''select count(*) from origin_links l join origin_sources p on p.id=l.source_id
       where l.source_pageid != p.source_pageid or l.source_revid != p.source_revid''').fetchone()[0]
  if bad:raise ValueError('Inconsistent source metadata; migration refused')
  if db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Existing foreign-key failures')
  db.execute('DROP TRIGGER origins_insert');db.execute('DROP VIEW origins')
  db.execute('ALTER TABLE origin_links RENAME TO origin_links_old')
  db.execute('''CREATE TABLE origin_links(subject_id INTEGER NOT NULL REFERENCES subjects(id),
    source_id INTEGER NOT NULL REFERENCES origin_sources(id),source_line INTEGER NOT NULL,
    candidate_key INTEGER NOT NULL REFERENCES origin_candidates(id),
    PRIMARY KEY(subject_id,source_id,source_line)) WITHOUT ROWID''')
  db.execute('''INSERT INTO origin_links(subject_id,source_id,source_line,candidate_key)
    SELECT subject_id,source_id,source_line,candidate_key FROM origin_links_old''')
  db.execute('''CREATE VIEW origins AS SELECT s.title AS title,p.source_pageid AS source_pageid,
    p.source_title AS source_title,p.source_revid AS source_revid,l.source_line AS source_line,
    c.candidate_id AS candidate_id FROM origin_links l JOIN subjects s ON s.id=l.subject_id
    JOIN origin_sources p ON p.id=l.source_id JOIN origin_candidates c ON c.id=l.candidate_key''')
  db.execute('''CREATE TRIGGER origin_links_original_key BEFORE INSERT ON origin_links BEGIN
    SELECT CASE WHEN EXISTS (SELECT 1 FROM origin_links l
     JOIN origin_sources existing ON existing.id=l.source_id
     JOIN origin_sources incoming ON incoming.id=NEW.source_id
     WHERE l.subject_id=NEW.subject_id AND l.source_line=NEW.source_line
       AND existing.source_pageid=incoming.source_pageid AND existing.source_revid=incoming.source_revid)
    THEN RAISE(IGNORE) END; END''')
  db.execute('''CREATE TRIGGER origins_insert INSTEAD OF INSERT ON origins BEGIN
    SELECT CASE WHEN NOT EXISTS(SELECT 1 FROM subjects WHERE title=NEW.title)
                THEN RAISE(ABORT,'origin subject missing') END;
    INSERT OR IGNORE INTO origin_sources(source_pageid,source_title,source_revid)
     VALUES(NEW.source_pageid,NEW.source_title,NEW.source_revid);
    INSERT OR IGNORE INTO origin_candidates(candidate_id) VALUES(NEW.candidate_id);
    INSERT OR IGNORE INTO origin_links(subject_id,source_id,source_line,candidate_key)
     VALUES((SELECT id FROM subjects WHERE title=NEW.title),
       (SELECT id FROM origin_sources WHERE source_pageid=NEW.source_pageid AND source_title=NEW.source_title AND source_revid=NEW.source_revid),
       NEW.source_line,(SELECT id FROM origin_candidates WHERE candidate_id=NEW.candidate_id)); END''')
  if full_snapshot(db)!=before:raise ValueError('Logical contents changed; rollback')
  db.execute('DROP TABLE origin_links_old')
  if db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Foreign-key check failed')
  if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Integrity check failed')
  db.commit()
 except BaseException:
  db.rollback();raise
 db.execute('VACUUM')
 if full_snapshot(db)!=before:raise ValueError('Logical contents changed after vacuum')
 if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Post-vacuum integrity failed')
 return before


def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--db',default='r2_wikipedia/people.sqlite3');ap.add_argument('--backup',default='/home/user/.cache/r2_compaction/people_before_links_v3.sqlite3');ap.add_argument('--log',default='r2_wikipedia/origin_links_compaction_log.json');a=ap.parse_args()
 old=os.path.getsize(a.db);db=sqlite3.connect(a.db)
 backup=Path(a.backup);backup.parent.mkdir(parents=True,exist_ok=True)
 if backup.exists():raise FileExistsError('Choose a fresh temporary backup path')
 with sqlite3.connect(backup) as copy:db.backup(copy)
 before=migrate(db);db.close();new=os.path.getsize(a.db)
 report={'original_bytes':old,'compacted_bytes':new,'saved_bytes':old-new,'fingerprints':before,'integrity':'ok','foreign_keys':'ok','temporary_backup':str(backup),'note':'The backup is excluded from persisted workspace snapshots.'}
 Path(a.log).write_text(json.dumps(report,indent=2)+'\n',encoding='utf8');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
