import copy,unittest
import apply_1239_1190_bce_context as m
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
   for k in ('start','end'):self.assertEqual(u['before'][k],u['after'][k])
 def test_caveats(self):
  self.assertIn('not a denial of conflict',self.us[0]['after']['r2SourceEvidence']['review_note']);self.assertIn('mythological hero',self.us[1]['after']['r2SourceEvidence']['review_note']);self.assertIn('same death',self.us[2]['after']['r2SourceEvidence']['review_note']);self.assertEqual((self.us[8]['after']['lat'],self.us[8]['after']['lon']),(35.602,35.782))
 def test_addition_roundtrip(self):
  add=self.man['additions'];d={'events':[]};o=m.transform(d,[],False,add);self.assertEqual(m.transform(o,[],True,add),d)
if __name__=='__main__':unittest.main()
