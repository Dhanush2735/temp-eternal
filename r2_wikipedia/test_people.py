import gzip
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
import people


def entity(qid, typeid):
    return {'id':qid,'lastrevid':100,'claims':{'P31':[{'rank':'normal','mainsnak':{'datavalue':{'value':{'id':typeid}}}}]},'descriptions':{'en':{'value':'test'}}}

class FakeApi:
    def get(self,url,params):
        if 'en.wikipedia.org' in url:
            return {'query':{'redirects':[{'from':'Alias','to':'Person A'}], 'pages':[
              {'title':'Person A','pageid':9,'pageprops':{'wikibase_item':'Q123'},'revisions':[{'revid':10,'timestamp':'2026-01-01T00:00:00Z','slots':{'main':{'content':'{{Infobox person\n| name = Person A\n| birth_date = c. 500 BC\n}}'}}}]},
              {'title':'Building B','pageid':10,'pageprops':{'wikibase_item':'Q456'}},
              {'title':'Unknown C','pageid':11}, {'title':'Missing D','missing':True}]}}
        return {'entities':{'Q123':entity('Q123','Q5'),'Q456':entity('Q456','Q41176')}}

class PeopleTests(unittest.TestCase):
 def setUp(self):
    self.db=sqlite3.connect(':memory:');self.db.executescript(people.SCHEMA)
 def test_human_is_positive_not_missing_inference(self):
    self.assertTrue(people.is_human(entity('Q123','Q5')))
    self.assertFalse(people.is_human(entity('Q456','Q41176')))
    self.assertFalse(people.is_human({}))
    e=entity('Q123','Q5');e['claims']['P31'][0]['rank']='deprecated';self.assertFalse(people.is_human(e))
 def test_batch_and_export(self):
    names=['Person A','Alias','Building B','Unknown C','Missing D']
    self.db.executemany('insert into subjects(title,first_source) values (?,?)',[(n,'Century') for n in names])
    self.db.executemany('insert into origins values(?,?,?,?,?,?)',[(n,1,'Century',2,3,'candidate') for n in names])
    people.fetch_batch(FakeApi(),self.db,names)
    statuses=dict(self.db.execute('select title,status from subjects'))
    self.assertEqual(statuses,{'Person A':'human','Alias':'human','Building B':'unconfirmed','Unknown C':'unresolved','Missing D':'missing'})
    self.assertEqual(self.db.execute('select count(*) from biographies').fetchone()[0],1)
    with tempfile.TemporaryDirectory() as d:
     path=str(Path(d)/'people.gz');self.assertEqual(people.export(self.db,path),1)
     r=json.loads(gzip.open(path,'rt').read());self.assertEqual(r['name'],'Person A');self.assertEqual(r['wikipedia_source']['revision_id'],10)
     self.assertEqual(len(r['discovered_from']),2);self.assertEqual(r['infobox']['raw_fields']['birth_date'].strip(),'c. 500 BC')
     self.assertEqual(r['wikidata_source']['revision_id'],100)
 def test_round_robin_and_skips_checked(self):
    for src in ('era1','era2','era3'):
     for i in range(3):self.db.execute('insert into subjects(title,first_source) values(?,?)',(f'{src}-{i}',src))
    self.assertEqual(people.next_batch(self.db,4),['era1-0','era2-0','era3-0','era1-1'])
    self.db.execute("update subjects set status='human' where title='era2-0'")
    self.assertEqual(people.next_batch(self.db,3),['era1-0','era2-1','era3-0'])
 def test_rotation_survives_small_batches_and_group_removal(self):
    for src in ('era1','era2','era3'):
     for i in range(2):self.db.execute('insert into subjects(title,first_source) values(?,?)',(f'{src}-{i}',src))
    self.db.commit()
    selected=[]
    for i in range(5):
     batch=people.next_batch(self.db,1,people.scheduler_cursor(self.db));selected+=batch
     src=self.db.execute('select first_source from subjects where title=?',(batch[-1],)).fetchone()[0]
     with self.db:
      self.db.execute("update subjects set status='unconfirmed' where title=?",(batch[0],))
      people.advance_scheduler(self.db,src)
    self.assertEqual(selected,['era1-0','era2-0','era3-0','era1-1','era2-1'])
    self.assertEqual(people.scheduler_cursor(self.db),'era2')
    self.assertEqual(people.next_batch(self.db,1,people.scheduler_cursor(self.db)),['era3-1'])
    self.assertEqual(people.next_batch(self.db,0),[])
 def test_failed_batch_rolls_back_cursor_and_partial_status(self):
    class BrokenApi:
     def get(self,url,params):
      if 'en.wikipedia.org' in url:
       return {'query':{'pages':[{'title':'A','pageid':1,'pageprops':{'wikibase_item':'Q1'},'revisions':[{'revid':1,'timestamp':'t','slots':{'main':{'content':'A'}}}]}, {'title':'B','pageid':2,'pageprops':{'wikibase_item':'Q2'}}]}}
      return {'entities':{'Q1':entity('Q1','Q5'),'Q2':entity('Q2','Q5')}}
    self.db.executemany('insert into subjects(title,first_source) values (?,?)',[('A','X'),('B','Y')]);self.db.commit()
    with self.assertRaises(KeyError):people.fetch_batch(BrokenApi(),self.db,['A','B'],'Y')
    self.assertIsNone(people.scheduler_cursor(self.db))
    self.assertEqual(dict(self.db.execute('select title,status from subjects')),{'A':'pending','B':'pending'})
    self.assertEqual(self.db.execute('select count(*) from biographies').fetchone()[0],0)
 def test_scheduler_cursor_persists_across_connections(self):
    with tempfile.TemporaryDirectory() as d:
     path=Path(d)/'people.sqlite3'
     c=sqlite3.connect(path);c.executescript(people.SCHEMA)
     c.executemany('insert into subjects(title,first_source) values (?,?)',[(x,x) for x in ('a','b','c')]);c.commit()
     with c:people.advance_scheduler(c,'a')
     c.close();c=sqlite3.connect(path)
     self.assertEqual(people.next_batch(c,1,people.scheduler_cursor(c)),['b']);c.close()
 def test_biography_links_extend_chain(self):
    wiki='{{Infobox person\n| name = Person A\n}}\nPerson A knew [[Person B]] and [[Town C|the town]].\n[[Category:People]] [[File:photo.jpg]]'
    self.db.execute('insert into biographies values(?,?,?,?,?,?,?,?,?)',(9,'Person A',10,'stamp','retrieved','Q123',100,gzip.compress(wiki.encode()),gzip.compress(b'{}')))
    self.assertEqual(people.import_biography_links(self.db),2)
    self.assertEqual(set(r[0] for r in self.db.execute('select title from subjects')),{'Person B','Town C'})
    self.assertEqual(self.db.execute("select source_title,source_revid,source_line from origins where title='Person B'").fetchone(),('Person A',10,4))
    people.import_biography_links(self.db)
    self.assertEqual(self.db.execute('select count(*) from origins').fetchone()[0],2)
 def test_discovery_keeps_all_references(self):
    sample={'source':{'title':'Century','page_id':1,'revision_id':2,'line':3},'id':'c1',
      'links':[{'title':'Person A'},{'title':'10th century'},{'title':'City A'}]}
    with tempfile.TemporaryDirectory() as d:
     p=Path(d)/'c.gz'
     with gzip.open(p,'wt') as f:f.write(json.dumps(sample)+'\n')
     people.import_candidates(self.db,p);people.import_candidates(self.db,p)
     self.assertEqual(self.db.execute('select count(*) from subjects').fetchone()[0],2)
     self.assertEqual(self.db.execute('select count(*) from origins').fetchone()[0],2)

if __name__=='__main__':unittest.main()
