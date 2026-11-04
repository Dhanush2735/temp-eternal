import sqlite3,unittest
from compact_origin_ids import migrate
from compact_people import snapshot

SCHEMA='''
PRAGMA foreign_keys=ON;
CREATE TABLE subjects(id INTEGER PRIMARY KEY,title TEXT NOT NULL UNIQUE,first_source TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'pending',canonical TEXT,qid TEXT,error TEXT);
CREATE TABLE biographies(pageid INTEGER PRIMARY KEY,title TEXT NOT NULL,wiki_revid INTEGER NOT NULL,wiki_timestamp TEXT NOT NULL,retrieved_at TEXT NOT NULL,qid TEXT NOT NULL,wikidata_revid INTEGER NOT NULL,wiki_gzip BLOB NOT NULL,wikidata_gzip BLOB NOT NULL);
CREATE TABLE origin_sources(id INTEGER PRIMARY KEY,source_pageid INTEGER NOT NULL,source_title TEXT NOT NULL,source_revid INTEGER NOT NULL,UNIQUE(source_pageid,source_title,source_revid));
CREATE TABLE origin_links(subject_id INTEGER NOT NULL REFERENCES subjects(id),source_id INTEGER NOT NULL REFERENCES origin_sources(id),source_pageid INTEGER NOT NULL,source_revid INTEGER NOT NULL,source_line INTEGER NOT NULL,candidate_id TEXT NOT NULL,PRIMARY KEY(subject_id,source_pageid,source_revid,source_line)) WITHOUT ROWID;
CREATE VIEW origins AS SELECT s.title,p.source_pageid,p.source_title,p.source_revid,l.source_line,l.candidate_id FROM origin_links l JOIN subjects s ON s.id=l.subject_id JOIN origin_sources p ON p.id=l.source_id;
CREATE TRIGGER origins_insert INSTEAD OF INSERT ON origins BEGIN SELECT 1; END;
'''
class OriginIdsMigrationTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:');self.db.executescript(SCHEMA)
  self.db.executemany('insert into subjects(id,title,first_source) values (?,?,?)',[(1,'A','S'),(2,'B','S')])
  self.db.execute("insert into origin_sources values (1,10,'S',50)")
  self.db.executemany('insert into origin_links values (?,?,?,?,?,?)',[(1,1,10,50,2,'shared'),(2,1,10,50,2,'shared'),(1,1,10,50,3,'another')]);self.db.commit()
 def test_migration_preserves_every_origin_and_insert_semantics(self):
  before=snapshot(self.db);self.assertEqual(migrate(self.db),before);self.assertEqual(snapshot(self.db),before)
  self.assertEqual(self.db.execute('select count(*) from origin_candidates').fetchone()[0],2)
  self.db.execute("insert or ignore into origins values('A',10,'S',50,2,'duplicate')")
  self.assertEqual(self.db.execute('select count(*) from origins').fetchone()[0],3)
  self.db.execute("insert into origins values('B',10,'S',50,4,'new')")
  self.assertEqual(self.db.execute("select candidate_id from origins where title='B' and source_line=4").fetchone()[0],'new')
  with self.assertRaises(sqlite3.IntegrityError):self.db.execute("insert into origins values('unknown',10,'S',50,4,'new')")
  self.assertEqual(self.db.execute('pragma foreign_key_check').fetchall(),[])
 def test_migrating_twice_does_not_mutate(self):
  migrate(self.db);after=snapshot(self.db)
  with self.assertRaises(ValueError):migrate(self.db)
  self.assertEqual(snapshot(self.db),after)
