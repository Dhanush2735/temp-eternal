import gzip
import json
import sqlite3
import unittest
from periods import classify, priority
from extract_candidates import candidates
import crawl

class PeriodTests(unittest.TestCase):
    def test_ranges(self):
        for title, kind, lo, hi in [
            ('3rd millennium BC','millennium',-3000,-2001),
            ('1st millennium BC','millennium',-1000,-1),
            ('1st millennium','millennium',1,1000),
            ('3rd millennium','millennium',2001,3000),
            ('30th century BC','century',-3000,-2901),
            ('1st century BC','century',-100,-1),
            ('1st century','century',1,100),
            ('30th century','century',2901,3000),
            ('0s BC','decade',-9,-1),('0s','decade',1,9),
            ('1000s BC (decade)','decade',-1009,-1000),
            ('1948','year',1948,1948),('3000 BC','year',-3000,-3000),
        ]:
            p=classify(title);self.assertIsNotNone(p,title);self.assertEqual((p.kind,p.start,p.end),(kind,lo,hi))
        for x in ['31st century BC','31st century','0','0 BC','3001','3001 BC','Mahatma Gandhi','00s','00s (disambiguation)','001','01st century']:
            self.assertIsNone(classify(x),x)

    def test_queue_priority(self):
        self.assertLess(priority('3rd millennium BC'),priority('30th century BC'))
        self.assertLess(priority('30th century BC'),priority('1940s'))
        self.assertLess(priority('1940s'),priority('1948'))
        self.assertLess(priority('1948'),priority('Some person'))

class SchedulingTests(unittest.TestCase):
    def test_centuries_are_balanced_across_eras(self):
        db=sqlite3.connect(':memory:'); self.addCleanup(db.close); db.execute('create table frontier(title text,depth int,status text,priority int)')
        titles=['30th century BC','20th century BC','10th century BC','1st century','11th century','21st century']
        db.executemany('insert into frontier values(?,1,\'pending\',20)',[(x,) for x in titles])
        observed=[]
        for _ in range(6):
            title,_=crawl.choose_next(db);observed.append(title);db.execute("update frontier set status='done' where title=?",(title,))
        self.assertEqual(observed,titles)
        self.assertIsNone(crawl.choose_next(db))

    def test_ordinary_article_interleaving_rotates_source_eras_and_persists(self):
        db=sqlite3.connect(':memory:'); self.addCleanup(db.close)
        db.executescript('''create table frontier(title text,depth int,status text,priority int);
          create table pages(pageid int,title text,revid int);
          create table edges(source_pageid int,source_revid int,target_title text);
          create table scheduler_state(key text primary key,value integer not null);''')
        db.executemany('insert into pages values(?,?,?)',[(1,'30th century BC',1),(2,'20th century BC',1)])
        db.executemany('insert into frontier values(?,?,?,?)',[
          ('1940s',1,'pending',30),('First ancient topic',2,'pending',100),('Second ancient topic',2,'pending',100)])
        db.executemany('insert into edges values(?,?,?)',[(1,1,'First ancient topic'),(2,1,'Second ancient topic')])
        self.assertEqual(crawl.choose_fair(db,3),('1940s',1))
        self.assertEqual(crawl.choose_fair(db,4),('First ancient topic',2))
        self.assertEqual(crawl.choose_fair(db,9),('Second ancient topic',2))
        self.assertEqual(crawl.choose_fair(db,4,0),('1940s',1))
        for _ in range(5):crawl.advance_scheduler(db)
        self.assertEqual(db.execute("select value from scheduler_state where key='attempts'").fetchone()[0],5)
        db.execute("insert into frontier values('explicit seed',0,'pending',0)")
        self.assertEqual(crawl.choose_fair(db,4),('explicit seed',0))

    def test_year_interleaving_does_not_starve_behind_decades(self):
        db=sqlite3.connect(':memory:');self.addCleanup(db.close)
        db.executescript('''create table frontier(title text,depth int,status text,priority int);
          create table pages(pageid int,title text,revid int);
          create table edges(source_pageid int,source_revid int,target_title text);''')
        db.executemany('insert into frontier values(?,?,?,?)',[
          ('1940s',1,'pending',30),('2999 BC',2,'pending',40),('1999 BC',2,'pending',40),
          ('1990',2,'pending',40),('1991',2,'done',40),('ordinary',2,'pending',100)])
        self.assertEqual(crawl.choose_fair(db,0),('1940s',1))
        self.assertEqual(crawl.choose_fair(db,1),('2999 BC',2))
        db.execute("update frontier set status='done' where title='2999 BC'")
        self.assertEqual(crawl.choose_fair(db,11),('1999 BC',2))
        self.assertEqual(crawl.choose_fair(db,1,5,0),('1940s',1))
        self.assertEqual(crawl.choose_fair(db,4),('ordinary',2))
        db.execute("insert into frontier values('1st century',1,'pending',20)")
        self.assertEqual(crawl.choose_fair(db,1),('1st century',1))
        db.execute("insert into frontier values('explicit seed',0,'pending',0)")
        self.assertEqual(crawl.choose_fair(db,1),('explicit seed',0))

class CandidateTests(unittest.TestCase):
    def test_year_verification_and_context(self):
        raw='{{Year nav|1948}}\n== Events ==\n=== January ===\n* [[January 30]]\n** [[Person A]] visits [[Town B]].\n== Births ==\n* [[Person C]]\n'
        rows=list(candidates(5,'1948',123,raw));self.assertEqual(len(rows),3)
        r=rows[1]; self.assertEqual(r['period_context']['start'],1948)
        self.assertEqual(r['section_path'],['Events','January'])
        self.assertEqual(r['parent_bullets'],['[[January 30]]'])
        self.assertEqual([x['title'] for x in r['links']],['Person A','Town B'])
        self.assertEqual(r['status'],'unverified_candidate')
        self.assertEqual(r['source']['revision_id'],123)
        self.assertEqual(list(candidates(5,'1948',123,raw)),rows)
        self.assertEqual(list(candidates(5,'1948',123,'{{short description|A number}}\n* [[X]]')),[])
        self.assertEqual(rows[2]['section_path'],['Births'])

    def test_disambiguation_title_is_not_a_decade(self):
        self.assertEqual(list(candidates(7,'00s',19,'== Decades ==\n* [[1900s]]')),[])

    def test_period_is_context_not_event_year(self):
        rows=list(candidates(7,'30th century BC',19,'== Events ==\n* [[King]] may have lived around 2800 BC.'))
        self.assertEqual(rows[0]['period_context']['start'],-3000)
        self.assertNotIn('event_year',rows[0])
        self.assertIn('2800 BC',rows[0]['raw_wikitext'])

if __name__=='__main__':unittest.main()
