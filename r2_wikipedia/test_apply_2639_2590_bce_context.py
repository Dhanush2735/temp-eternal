import copy,unittest
import apply_2639_2590_bce_context as m
class Tests(unittest.TestCase):
 def setUp(self):self.man=m.load(m.M);m.validate(self.man);self.a=self.man['additions'];self.doc={'events':[]}
 def test_validation(self):m.validate(self.man)
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.doc,[],False,self.a),[],True,self.a),self.doc)
 def test_input_immutable(self):
  d=copy.deepcopy(self.doc);m.transform(self.doc,[],False,self.a);self.assertEqual(self.doc,d)
 def test_duplicate(self):
  with self.assertRaises(ValueError):m.transform({'events':[self.a[0]['event']]},[],False,self.a)
 def test_missing_reversal(self):
  with self.assertRaises(ValueError):m.transform(self.doc,[],True,self.a)
 def test_changed_reversal(self):
  d=m.transform(self.doc,[],False,self.a);d['events'][1]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,[],True,self.a)
 def test_hash_guard(self):
  d=copy.deepcopy(self.man);d['additions'][0]['event']['lat']=0
  with self.assertRaises(ValueError):m.validate(d)
 def test_two_qualified_notes(self):
  self.assertEqual(len(self.a),2)
  for a in self.a:
   e=a['event'];self.assertEqual((e['kind'],e['effect']),('cultural','note'));self.assertIn('not',e['r2SourceEvidence']['review_note']);self.assertGreaterEqual(len(e['r2SourceEvidence']['sources']),3)
if __name__=='__main__':unittest.main()
