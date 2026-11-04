import copy,unittest
import apply_1489_1440_bce_punt as m
class Tests(unittest.TestCase):
 def setUp(self):self.man=m.load(m.M);m.validate(self.man);self.a=self.man['additions'];self.d={'events':[]}
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.d,[],False,self.a),[],True,self.a),self.d)
 def test_duplicate(self):
  d=m.transform(self.d,[],False,self.a)
  with self.assertRaises(ValueError):m.transform(d,[],False,self.a)
 def test_modified_manifest(self):
  d=copy.deepcopy(self.man);d['additions'][0]['event']['lat']=0
  with self.assertRaises(ValueError):m.validate(d)
 def test_changed_reverse(self):
  d=m.transform(self.d,[],False,self.a);d['events'][0]['effect']='political'
  with self.assertRaises(ValueError):m.transform(d,[],True,self.a)
 def test_source_and_uncertainty(self):
  e=self.a[0]['event'];self.assertEqual((e['kind'],e['effect']),('cultural','note'));self.assertIn('not Punt',e['r2SourceEvidence']['review_note']);self.assertIn('Nehsi',e['r2SourceEvidence']['review_note'])
if __name__=='__main__':unittest.main()
