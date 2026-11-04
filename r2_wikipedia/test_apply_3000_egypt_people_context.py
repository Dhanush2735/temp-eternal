import copy, unittest
import apply_3000_egypt_people_context as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.add=self.man['additions'];self.e=self.add[0]['event'];self.base={'events':[]}
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.base,[],additions=self.add),[],True,self.add),self.base)
 def test_source_not_mutated(self):
  m.transform(self.base,[],additions=self.add);self.assertEqual(self.base,{'events':[]})
 def test_duplicate(self):
  with self.assertRaises(ValueError):m.transform({'events':[copy.deepcopy(self.e)]},[],additions=self.add)
 def test_reverse_missing(self):
  with self.assertRaises(ValueError):m.transform(self.base,[],True,self.add)
 def test_reverse_modified(self):
  d=m.transform(self.base,[],additions=self.add);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,[],True,self.add)
 def test_hash_guard(self):
  d=copy.deepcopy(self.man);d['additions'][0]['event']['lat']=0
  with self.assertRaises(ValueError):m.validate(d)
 def test_caveats_and_context(self):
  e=self.e;self.assertEqual((e['start'],e['end'],e['effect']),(-3000,-2999,'note'));self.assertIn('not a claim',e['r2SourceEvidence']['review_note']);self.assertIn('debated',e['r2SourceEvidence']['review_note']);self.assertGreaterEqual(len(e['r2SourceEvidence']['sources']),5)
if __name__=='__main__':unittest.main()
