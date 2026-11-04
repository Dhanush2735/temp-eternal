import copy,unittest
import apply_2339_2290_bce_context as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.us=self.man['updates'];self.add=self.man['additions'];self.doc={'events':[copy.deepcopy(self.us[1]['before'])]}
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.doc,self.us[1:],additions=self.add),self.us[1:],True,self.add),self.doc)
 def test_no_mutation(self):
  d=copy.deepcopy(self.doc);m.transform(self.doc,self.us[1:],additions=self.add);self.assertEqual(self.doc,d)
 def test_missing(self):
  with self.assertRaises(ValueError):m.transform({'events':[]},self.us[1:])
 def test_changed(self):
  d=copy.deepcopy(self.doc);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.us[1:])
 def test_duplicate(self):
  d=copy.deepcopy(self.doc);d['events'].append(copy.deepcopy(self.us[1]['before']))
  with self.assertRaises(ValueError):m.transform(d,self.us[1:])
 def test_addition_collision(self):
  d=copy.deepcopy(self.doc);d['events'].append(copy.deepcopy(self.add[0]['event']))
  with self.assertRaises(ValueError):m.transform(d,self.us[1:],additions=self.add)
 def test_changed_after(self):
  d=m.transform(self.doc,self.us[1:],additions=self.add);d['events'][1]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.us[1:],True,self.add)
 def test_manifest_guard(self):
  d=copy.deepcopy(self.man);d['additions'][0]['event']['lat']=0
  with self.assertRaises(ValueError):m.validate(d)
 def test_stable_updates(self):
  for u in self.us:
   for k in ('id','start','end','lat','lon','radiusKm','kind','effect','confidence'):self.assertEqual(u['before'][k],u['after'][k])
 def test_caveats(self):
  self.assertIn('alternative dates',self.us[0]['after']['r2SourceEvidence']['review_note']);self.assertIn('debated',self.us[1]['after']['r2SourceEvidence']['review_note']);self.assertIn('mythological',self.add[0]['event']['r2SourceEvidence']['review_note'])
if __name__=='__main__':unittest.main()
