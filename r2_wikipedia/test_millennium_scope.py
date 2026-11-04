import sqlite3,unittest
import millennium_scope as s

class MillenniumScopeTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:')
  self.db.executescript('''create table pages(pageid integer,title text,revid integer);
   create table resolutions(requested_title text,canonical_title text);
   create table edges(source_pageid integer,source_revid integer,target_title text);
   create table frontier(title text,depth int,status text);''')
  self.db.executemany('insert into pages values(?,?,?)',[(1,s.ROOT,10),(2,'30th century BC',20),(3,'2nd millennium BC',30)])
  self.db.executemany('insert into edges values(?,?,?)',[
   (1,10,'30th century BC'),(1,10,'2nd millennium BC'),(1,10,'Ancient topic'),
   (1,9,'Obsolete link'),(2,20,'2990s BC'),(2,20,'2980s BC'),(2,20,'2990 BC'),
   (2,20,'2999 BC'),(2,20,'3000 BC'),(3,30,'Unrelated event')])
  self.db.executemany('insert into frontier values(?,?,?)',[(s.ROOT,0,'done'),('30th century BC',1,'done'),
   ('2nd millennium BC',1,'done'),('Ancient topic',1,'pending'),('Obsolete link',1,'pending'),
   ('2990s BC',2,'pending'),('2980s BC',2,'pending'),('2990 BC',2,'pending'),('2999 BC',2,'pending'),('3000 BC',2,'done'),('Unrelated event',2,'pending'),('unreachable',1,'pending')])
  self.db.execute("insert into resolutions values('3000 BC','30th century BC')")
 def tearDown(self):self.db.close()
 def test_current_edges_and_scope_boundary(self):
  g=s.graph(self.db);self.assertIn('Ancient topic',g['depths']);self.assertNotIn('Obsolete link',g['depths'])
  self.assertNotIn('Unrelated event',g['depths']);self.assertIn('2nd millennium BC',g['deferred_period_titles'])
  self.assertEqual(g['visited_canonical'],{s.ROOT,'30th century BC'})
  self.assertEqual(s.summary(self.db)['counts']['year_canonical_pages'],0)
 def test_selects_year_and_ordinary_without_other_scope_or_stale_edge(self):
  self.assertIn(s.choose(self.db,0)[0],{'2990s BC','2980s BC'})
  self.assertIn(s.choose(self.db,1)[0],{'2990 BC','2999 BC'})
  self.assertEqual(s.choose(self.db,4)[0],'Ancient topic')
  self.db.execute("insert into edges values(1,10,'29th century BC')")
  self.db.execute("insert into frontier values('29th century BC',1,'pending')")
  self.assertEqual(s.choose(self.db,1)[0],'29th century BC')
 def test_period_bounds_and_bands(self):
  self.assertTrue(s.in_focus('3000 BC'));self.assertTrue(s.in_focus('2001 BC'))
  self.assertFalse(s.in_focus('3001 BC'));self.assertFalse(s.in_focus('31st century BC'))
  self.assertTrue(s.in_focus('Sumer'));self.assertEqual(s.century_band(__import__('periods').classify('30th century BC')),0)
  self.assertEqual(s.century_band(__import__('periods').classify('21st century BC')),9)

if __name__=='__main__':unittest.main()