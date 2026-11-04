import sqlite3,unittest
from compact_people import migrate,snapshot

LEGACY='''
PRAGMA foreign_keys=ON;
CREATE TABLE subjects(id INTEGER PRIMARY KEY,title TEXT NOT NULL UNIQUE,first_source TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'pending',canonical TEXT,qid TEXT,error TEXT);
CREATE TABLE biographies(pageid INTEGER PRIMARY KEY,title TEXT NOT NULL,wiki_revid INTEGER NOT NULL,wiki_timestamp TEXT NOT NULL,retrieved_at TEXT NOT NULL,qid TEXT NOT NULL,wikidata_revid INTEGER NOT NULL,wiki_gzip BLOB NOT NULL,wikidata_gzip BLOB NOT NULL);
CREATE TABLE origins(title TEXT NOT NULL REFERENCES subjects(title),source_pageid INTEGER NOT NULL,source_title TEXT NOT NULL,source_revid INTEGER NOT NULL,source_line INTEGER NOT NULL,candidate_id TEXT NOT NULL,PRIMARY KEY(title,source_pageid,source_revid,source_line));
'''
class CompactTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:');self.db.executescript(LEGACY)
  self.db.executemany('insert into subjects(title,first_source) values (?,?)',[('Person A','Century'),('Person B','Century')])
  self.db.executemany('insert into origins values (?,?,?,?,?,?)',[('Person A',1,'Century',5,12,'c1'),('Person B',1,'Century',5,12,'c2'),('Person A',2,'Era',6,8,'c3')])
  self.db.execute('insert into biographies values (?,?,?,?,?,?,?,?,?)',(4,'Person A',9,'time','retrieved','Q1',10,b'wiki',b'data'));self.db.commit()
 def test_lossless_and_view_accepts_inserts(self):
  before=snapshot(self.db);self.assertEqual(migrate(self.db),before);self.assertEqual(snapshot(self.db),before)
  self.assertEqual(self.db.execute('select type from sqlite_master where name="origins"').fetchone()[0],'view')
  self.db.execute('insert or ignore into origins values (?,?,?,?,?,?)',('Person A',1,'Century',5,12,'duplicate'))
  self.assertEqual(self.db.execute('select count(*) from origins').fetchone()[0],3)
  self.db.execute('insert into origins values (?,?,?,?,?,?)',('Person B',2,'Era',6,9,'c4'))
  self.assertEqual(self.db.execute('select count(*) from origins').fetchone()[0],4)
  self.assertEqual(self.db.execute('pragma foreign_key_check').fetchall(),[])
 def test_missing_subject_does_not_silently_disappear(self):
  migrate(self.db)
  with self.assertRaises(sqlite3.IntegrityError):self.db.execute('insert into origins values (?,?,?,?,?,?)',('Missing',1,'Century',5,12,'c1'))
 def test_migrating_twice_does_not_mutate(self):
  migrate(self.db);after=snapshot(self.db)
  with self.assertRaises(ValueError):migrate(self.db)
  self.assertEqual(snapshot(self.db),after)
if __name__=='__main__':unittest.main()
