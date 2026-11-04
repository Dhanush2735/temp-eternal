import contextlib,io,sqlite3,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import crawl, people
class QueueReserveTests(unittest.TestCase):
 def test_people_stops_without_recreating_index_when_workspace_full(self):
  with tempfile.TemporaryDirectory() as d:
   db=Path(d)/'people.sqlite3';out=Path(d)/'people.gz'
   args=['people.py','--db',str(db),'--out',str(out),'--max-check','0','--stats']
   with patch.object(sys,'argv',args),patch.object(people,'within_budget',return_value=(False,999_999_999)),contextlib.redirect_stdout(io.StringIO()):people.main()
   with sqlite3.connect(db) as c:
    self.assertIsNone(c.execute("select 1 from sqlite_master where type='index' and name='subject_queue'").fetchone())
 def test_crawl_stops_without_recreating_index_when_workspace_full(self):
  with tempfile.TemporaryDirectory() as d:
   db=Path(d)/'crawl.sqlite3';args=['crawl.py','--db',str(db),'--max-pages','1']
   with patch.object(sys,'argv',args),patch.object(crawl,'within_budget',return_value=(False,999_999_999)),contextlib.redirect_stdout(io.StringIO()):crawl.main()
   with sqlite3.connect(db) as c:
    self.assertIsNone(c.execute("select 1 from sqlite_master where type='index' and name='frontier_priority'").fetchone())
    self.assertGreater(c.execute('select count(*) from frontier').fetchone()[0],0)
if __name__=='__main__':unittest.main()
