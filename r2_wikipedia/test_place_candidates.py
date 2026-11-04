import gzip,json,sqlite3,tempfile,unittest
from pathlib import Path
import place_candidates as pc

class FakeApi:
 def get(self,url,params):
  return {'entities':{'Q1':{'id':'Q1','lastrevid':10,'labels':{'en':{'value':'Place One'}},'claims':{'P625':[{'id':'s1','rank':'normal','mainsnak':{'snaktype':'value','datavalue':{'value':{'latitude':1,'longitude':2,'precision':0.1,'globe':'http://www.wikidata.org/entity/Q2'}}},'references':[{'hash':'ref'}]}]}},
   'Q2':{'id':'Q2','lastrevid':11,'claims':{}},'Q3':{'id':'Q3','missing':True}}}

def claim(q,rank='normal'):return {'rank':rank,'value':{'entity_id':q},'statement_id':'statement'}

class PlacesTest(unittest.TestCase):
 def setUp(self):self.db=sqlite3.connect(':memory:');self.db.executescript(pc.SCHEMA)
 def test_linked_places_are_not_person_locations(self):
  person={'id':'QPerson','details':{'birth_place':[claim('Q1')],'work_location':[claim('Q2')],'death_place':[claim('Q3','deprecated')]}}
  with tempfile.TemporaryDirectory() as d:
   inp=Path(d)/'vip.gz';out=Path(d)/'places.gz'
   with gzip.open(inp,'wt') as f:f.write(json.dumps(person)+'\n')
   pc.sync(self.db,inp);pc.sync(self.db,inp)
   self.assertEqual(self.db.execute('select count(*) from places').fetchone()[0],2)
   pc.fetch(FakeApi(),self.db,['Q1','Q2']);pc.export(self.db,out)
   rows=[json.loads(x) for x in gzip.open(out,'rt')];self.assertEqual(len(rows),2)
   one=rows[0];self.assertEqual(one['related_people'][0]['role'],'birth_place');self.assertIn('not inferred',one['note'])
   self.assertEqual(one['coordinate_claims'][0]['references'][0]['hash'],'ref')
   self.assertEqual(rows[1]['status'],'no_coordinates')
 def test_missing_is_not_a_guessed_coordinate(self):
  self.db.execute('insert into places(qid) values(?)',('Q3',));pc.fetch(FakeApi(),self.db,['Q3'])
  self.assertEqual(self.db.execute('select status,coordinates_json from places where qid=?',('Q3',)).fetchone(),('unresolved',None))
if __name__=='__main__':unittest.main()
