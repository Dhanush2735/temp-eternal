import copy,unittest
import apply_1389_1340_bce_witori as m
class Tests(unittest.TestCase):
 def test_manifest(self):m.validate(m.load(m.M))
 def test_roundtrip(self):
  x=m.load(m.M)['updates'];d={'events':[copy.deepcopy(x[0]['before'])]};out=m.transform(d,x);self.assertEqual(m.transform(out,x,True),d);self.assertIn('no date',out['events'][0]['r2SourceEvidence']['review_note'])
 def test_tamper(self):
  x=m.load(m.M);x['updates'][0]['after']['name']='changed'
  with self.assertRaises(ValueError):m.validate(x)
 def test_stale(self):
  x=m.load(m.M)['updates'];d={'events':[copy.deepcopy(x[0]['before'])]};d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,x)
if __name__=='__main__':unittest.main()
