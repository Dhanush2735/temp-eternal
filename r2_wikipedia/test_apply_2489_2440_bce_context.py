import copy,unittest
import apply_2489_2440_bce_context as m
class Tests(unittest.TestCase):
 def setUp(self):self.man=m.load(m.M);m.validate(self.man);self.us=self.man['updates'];self.add=self.man['additions'];self.doc={'events':[copy.deepcopy(self.us[0]['before'])]}
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.doc,self.us,False,self.add),self.us,True,self.add),self.doc)
 def test_input_unchanged(self):
  b=copy.deepcopy(self.doc);m.transform(self.doc,self.us,False,self.add);self.assertEqual(b,self.doc)
 def test_missing(self):
  with self.assertRaises(ValueError):m.transform({'events':[]},self.us,False,self.add)
 def test_changed(self):
  d=copy.deepcopy(self.doc);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.us,False,self.add)
 def test_duplicate_add(self):
  d=copy.deepcopy(self.doc);d['events'].append(self.add[0]['event'])
  with self.assertRaises(ValueError):m.transform(d,self.us,False,self.add)
 def test_changed_added_reverse(self):
  d=m.transform(self.doc,self.us,False,self.add);d['events'][-1]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.us,True,self.add)
 def test_hash(self):
  d=copy.deepcopy(self.man);d['additions'][0]['event']['lat']=0
  with self.assertRaises(ValueError):m.validate(d)
 def test_existing_keys_stable(self):
  u=self.us[0]
  for k in ('id','start','end','lat','lon','radiusKm','kind','effect'):self.assertEqual(u['before'][k],u['after'][k])
 def test_uncertainty(self):
  a=self.add[0]['event'];self.assertIn('approximate',a['name']);self.assertEqual((a['kind'],a['effect']),('cultural','note'));self.assertIn('not evidence',a['r2SourceEvidence']['review_note']);self.assertIn('disputed',self.us[0]['after']['name'])
if __name__=='__main__':unittest.main()
