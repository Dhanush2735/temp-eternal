import unittest,copy
import apply_skara_brae_site as m
class Tests(unittest.TestCase):
 def setUp(self):self.man=m.load(m.M);self.u=m.validate(self.man);self.d={'sites':[copy.deepcopy(self.u['before'])]}
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.d,self.u),self.u,True),self.d)
 def test_input_unchanged(self):
  b=copy.deepcopy(self.d);m.transform(self.d,self.u);self.assertEqual(self.d,b)
 def test_missing(self):
  with self.assertRaises(ValueError):m.transform({'sites':[]},self.u)
 def test_duplicate(self):
  d=copy.deepcopy(self.d);d['sites'].append(copy.deepcopy(d['sites'][0]))
  with self.assertRaises(ValueError):m.transform(d,self.u)
 def test_changed_before(self):
  d=copy.deepcopy(self.d);d['sites'][0]['civHint']='other'
  with self.assertRaises(ValueError):m.transform(d,self.u)
 def test_changed_after(self):
  d=m.transform(self.d,self.u);d['sites'][0]['rank']='different'
  with self.assertRaises(ValueError):m.transform(d,self.u,True)
 def test_tampered_manifest(self):
  t=copy.deepcopy(self.man);t['updates'][0]['after']['occupiedEnd']=-2499
  with self.assertRaises(ValueError):m.validate(t)
 def test_dates_retained(self):self.assertEqual((self.u['before']['occupiedStart'],self.u['before']['occupiedEnd']),(self.u['after']['occupiedStart'],self.u['after']['occupiedEnd']))
if __name__=='__main__':unittest.main()
