import sqlite3,unittest
import people,millennium_scope

class ScopedPeopleTests(unittest.TestCase):
 def setUp(self):
  self.db=sqlite3.connect(':memory:');self.db.executescript(people.SCHEMA)
  self.c=sqlite3.connect(':memory:');self.c.executescript('''create table pages(pageid int,title text,revid int);create table edges(source_pageid int,source_revid int,target_title text);create table resolutions(requested_title text,canonical_title text);''')
  self.c.executemany('insert into pages values(?,?,?)',[(1,millennium_scope.ROOT,10),(2,'30th century BC',20),(3,'2nd millennium BC',30)])
  self.c.executemany('insert into edges values(?,?,?)',[(1,10,'30th century BC'),(1,10,'2nd millennium BC')])
  for t in ('A','B','C','D','Alias','Via biography'):
   self.db.execute('insert into subjects(title,first_source) values(?,?)',(t,'unrelated first source'))
  self.db.executemany('insert into origins values(?,?,?,?,?,?)',[
   ('A',1,millennium_scope.ROOT,10,1,'a'),('B',2,'30th century BC',20,1,'b'),
   ('C',2,'30th century BC',19,2,'old'),('D',3,'2nd millennium BC',30,3,'outside'),
   ('A',2,'30th century BC',20,4,'duplicate'),('Alias',1,millennium_scope.ROOT,10,5,'alias'),
   ('Via biography',99,'Saved Person',50,6,'article-link:99:50:6')])
  self.db.execute("update subjects set status='human',canonical='Saved Person' where title='Alias'")
  self.db.execute("insert into biographies values(99,'Saved Person',50,'t','t','Q1',10,x'01',x'01')")
  self.db.commit()
 def tearDown(self):self.c.close();self.db.close()
 def test_current_scope_origin_and_biography_chain(self):
  got=people.scoped_next_batch(self.db,self.c,10)
  self.assertEqual({x[0] for x in got},{'A','B','Via biography'})
  self.assertEqual(len(got),3)
  self.assertNotIn('C',{x[0] for x in got});self.assertNotIn('D',{x[0] for x in got})
  self.assertEqual(people.scoped_next_batch(self.db,self.c,0),[])
 def test_independent_scope_cursor(self):
  with self.db:
   people.advance_scheduler(self.db,'global')
   people.advance_scheduler(self.db,'30th century BC','scope:third-millennium-bc')
  self.assertEqual(people.scheduler_cursor(self.db),'global')
  self.assertEqual(people.scheduler_cursor(self.db,'scope:third-millennium-bc'),'30th century BC')
 def test_failed_scoped_batch_does_not_advance_scoped_cursor(self):
  class BrokenApi:
   def get(self,url,params):raise RuntimeError('network failure')
  with self.assertRaises(RuntimeError):
   people.fetch_batch(BrokenApi(),self.db,['A'],'30th century BC','scope:third-millennium-bc')
  self.assertIsNone(people.scheduler_cursor(self.db,'scope:third-millennium-bc'))
  self.assertEqual(self.db.execute("select status from subjects where title='A'").fetchone()[0],'pending')

if __name__=='__main__':unittest.main()
