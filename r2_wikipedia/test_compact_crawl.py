import sqlite3,tempfile,unittest
from pathlib import Path
import crawl
from compact_crawl import compact,snapshot
class CompactCrawlTests(unittest.TestCase):
 def test_preserves_tables_and_prioritized_queue(self):
  with tempfile.TemporaryDirectory() as d:
   db=sqlite3.connect(Path(d)/'t.db');db.executescript(crawl.SCHEMA)
   db.execute('alter table frontier add column priority integer not null default 100')
   db.execute('create index frontier_priority on frontier(status,priority,depth,title)')
   db.execute('create index queue_order on frontier(status,depth,title)')
   db.execute('insert into frontier(title,depth,status,priority) values(?,?,?,?)',('1st century',1,'pending',20))
   db.execute('insert into pages values(?,?,?,?,?,?,?,?)',(1,'A',10,'t','d','url',b'blob',1))
   db.execute('insert into edges values(?,?,?)',(1,10,'B'));db.commit()
   before=snapshot(db);self.assertEqual(compact(db),before);self.assertEqual(snapshot(db),before)
   self.assertEqual(db.execute("select count(*) from sqlite_master where name='queue_order'").fetchone()[0],0)
   self.assertEqual(crawl.choose_next(db),('1st century',1))
if __name__=='__main__':unittest.main()
