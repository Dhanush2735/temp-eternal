import copy,unittest
import apply_2589_2540_bce_context as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.us=self.man['updates'];self.a=self.man['additions'];self.doc={'events':[copy.deepcopy(self.us[0]['before'])]}
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.doc,self.us,False,self.a),self.us,True,self.a),self.doc)
 def test_immutable(self):
  d=copy.deepcopy(self.doc);m.transform(self.doc,self.us,False,self.a);self.assertEqual(self.doc,d)
 def test_missing_update(self):
  with self.assertRaises(ValueError):m.transform({'events':[]},self.us,False,self.a)
 def test_changed_update(self):
  d=copy.deepcopy(self.doc);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.us,False,self.a)
 def test_duplicate_addition(self):
  d=copy.deepcopy(self.doc);d['events'].append(self.a[0]['event'])
  with self.assertRaises(ValueError):m.transform(d,self.us,False,self.a)
 def test_changed_added_reverse(self):
  d=m.transform(self.doc,self.us,False,self.a);d['events'][-1]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.us,True,self.a)
 def test_hash_guard(self):
  d=copy.deepcopy(self.man);d['additions'][0]['event']['lat']=0
  with self.assertRaises(ValueError):m.validate(d)
 def test_stable_existing_location(self):
  u=self.us[0]
  for k in ('id','start','end','lat','lon','radiusKm','kind','effect'):self.assertEqual(u['before'][k],u['after'][k])
 def test_qualified_sources(self):
  n=self.a[0]['event'];self.assertIn('approximate',n['name']);self.assertEqual((n['kind'],n['effect']),('cultural','note'));self.assertIn('not proven',n['r2SourceEvidence']['review_note']);self.assertIn('Nin-kisalsi',self.us[0]['after']['r2SourceEvidence']['review_note'])
if __name__=='__main__':unittest.main()
