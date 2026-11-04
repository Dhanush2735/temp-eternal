import copy,unittest
import apply_1589_1540_bce_context as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.us=self.man['updates'];self.doc={'events':[copy.deepcopy(u['before']) for u in self.us]}
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.doc,self.us),self.us,True),self.doc)
 def test_no_mutation(self):
  d=copy.deepcopy(self.doc);m.transform(self.doc,self.us);self.assertEqual(self.doc,d)
 def test_missing(self):
  with self.assertRaises(ValueError):m.transform({'events':[]},self.us)
 def test_changed(self):
  d=copy.deepcopy(self.doc);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.us)
 def test_duplicate(self):
  d=copy.deepcopy(self.doc);d['events'].append(copy.deepcopy(self.us[0]['before']))
  with self.assertRaises(ValueError):m.transform(d,self.us)
 def test_changed_after(self):
  d=m.transform(self.doc,self.us);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.us,True)
 def test_manifest_guard(self):
  d=copy.deepcopy(self.man);d['updates'][0]['after']['lat']=0
  with self.assertRaises(ValueError):m.validate(d)
 def test_stable_ids(self):
  for u in self.us:self.assertEqual(u['before']['id'],u['after']['id'])
 def test_stable_fields(self):
  for u in self.us:
   for k in ('start','end','radiusKm'):self.assertEqual(u['before'][k],u['after'][k])
 def test_caveats(self):
  self.assertIn('mythological traditions',self.us[4]['after']['r2SourceEvidence']['review_note']);self.assertIn('not a verified treaty',self.us[6]['after']['r2SourceEvidence']['review_note'])
 def test_addition_roundtrip(self):
  ads=self.man['additions'];d={'events':[]};self.assertEqual(m.transform(m.transform(d,[],additions=ads),[],True,ads),d)
 def test_addition_collision(self):
  ads=self.man['additions'];d={'events':[copy.deepcopy(ads[0]['event'])]}
  with self.assertRaises(ValueError):m.transform(d,[],additions=ads)
if __name__=='__main__':unittest.main()
