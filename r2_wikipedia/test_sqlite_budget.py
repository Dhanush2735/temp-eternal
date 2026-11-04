import sqlite3
import tempfile
import unittest
from pathlib import Path
from sqlite_budget import people_page_cap, is_full

class SqliteBudgetTests(unittest.TestCase):
 def test_cap_rolls_back_full_transaction_without_losing_previous_data(self):
  with tempfile.TemporaryDirectory() as d:
   db=sqlite3.connect(Path(d)/'test.db')
   db.execute('create table t(x text)');db.execute("insert into t values('kept')");db.commit()
   size=db.execute('pragma page_size').fetchone()[0];pages=db.execute('pragma page_count').fetchone()[0]
   cap=people_page_cap(db,(pages+2)*size,0,10_000_000,reserve_bytes=0)
   self.assertEqual(cap,pages+2)
   with self.assertRaises(sqlite3.Error) as raised:
    with db:
     for _ in range(100):db.execute('insert into t values(?)',('z'*6000,))
   self.assertTrue(is_full(raised.exception))
   self.assertEqual(db.execute('select x from t').fetchall(),[('kept',)])
   self.assertLessEqual(db.execute('pragma page_count').fetchone()[0],cap)
   self.assertEqual(db.execute('pragma integrity_check').fetchone()[0],'ok');db.close()
 def test_too_small_and_workspace_reserve(self):
  db=sqlite3.connect(':memory:');db.execute('create table t(x)');db.commit()
  size=db.execute('pragma page_size').fetchone()[0];pages=db.execute('pragma page_count').fetchone()[0]
  self.assertIsNone(people_page_cap(db,(pages-1)*size,0,10_000_000))
  cap=people_page_cap(db,100*size,9_800_000,10_000_000,reserve_bytes=500_000)
  self.assertEqual(cap,pages)
  with self.assertRaises(ValueError):people_page_cap(db,0,0,1)
  self.assertFalse(is_full(ValueError('database or disk is full')))
  db.close()

if __name__=='__main__':unittest.main()
