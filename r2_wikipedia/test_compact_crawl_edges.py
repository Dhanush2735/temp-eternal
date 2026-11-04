import sqlite3,tempfile,unittest
from pathlib import Path
import crawl
from compact_crawl import snapshot
from compact_crawl_edges import migrate

class CompactEdgesTests(unittest.TestCase):
 def test_preserves_edges_queue_and_scheduler_idempotently(self):
  with tempfile.TemporaryDirectory() as d:
   db=sqlite3.connect(Path(d)/'db.sqlite');db.executescript(crawl.SCHEMA)
   db.execute('DROP TABLE edges')
   db.execute('CREATE TABLE edges(source_pageid INTEGER NOT NULL REFERENCES pages(pageid), source_revid INTEGER NOT NULL, target_title TEXT NOT NULL, PRIMARY KEY(source_pageid,source_revid,target_title))')
   db.execute('CREATE INDEX target_idx ON edges(target_title)')
   db.execute('ALTER TABLE frontier ADD COLUMN priority INTEGER NOT NULL DEFAULT 100')
   db.execute("INSERT INTO pages VALUES(1,'1st century',5,'t','u','url',?,2)",(b'blob',))
   db.execute("INSERT INTO frontier(title,depth,status,priority) VALUES('Ancient topic',2,'pending',100)")
   db.executemany('INSERT INTO edges VALUES(1,5,?)',[('Ancient topic',),('Other',)])
   db.execute("INSERT INTO scheduler_state VALUES('attempts',4)");db.commit()
   original=snapshot(db);self.assertEqual(migrate(db),original);self.assertEqual(snapshot(db),original)
   self.assertEqual(crawl.choose_fair(db,4),('Ancient topic',2))
   self.assertEqual(db.execute("select count(*) from sqlite_master where name='target_idx'").fetchone()[0],0)
   self.assertIn('WITHOUT ROWID',db.execute("select sql from sqlite_master where name='edges'").fetchone()[0].upper())
   db.execute("INSERT OR IGNORE INTO edges VALUES(1,5,'Other')");db.commit()
   self.assertEqual(db.execute('select count(*) from edges').fetchone()[0],2)
   self.assertEqual(migrate(db),original)
   db.close()
if __name__=='__main__':unittest.main()
