import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import people

class PeopleStorageTests(unittest.TestCase):
 def test_full_import_rolls_back_and_does_not_fetch(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'p.sqlite3';out=Path(d)/'export.gz'
   db=sqlite3.connect(path);db.executescript(people.SCHEMA)
   db.execute("insert into subjects(title,first_source) values('kept','src')");db.commit();db.close()
   original_size=path.stat().st_size
   # Leave two pages of headroom, then try to import substantially more.
   mb=(original_size+2*4096)/(1024*1024)
   def oversized_import(c,ignored):
    with c:
     for i in range(1000):c.execute('insert into subjects(title,first_source) values(?,?)',(f'{i}-'+('z'*3000),'src'))
    return 1000
   args=['people.py','--db',str(path),'--out',str(out),'--max-check','1','--max-db-mb',str(mb)]
   with patch('sys.argv',args), patch.object(people,'within_budget',return_value=(True,1_000_000)), patch.object(people,'import_candidates',side_effect=oversized_import), patch.object(people,'fetch_batch') as fetch:
    people.main()
    fetch.assert_not_called()
   db=sqlite3.connect(path)
   self.assertEqual(db.execute('select title from subjects').fetchall(),[('kept',)])
   self.assertEqual(db.execute('pragma integrity_check').fetchone()[0],'ok')
   self.assertLessEqual(path.stat().st_size,original_size+2*4096)
   self.assertTrue(out.exists());db.close()

if __name__=='__main__':unittest.main()
