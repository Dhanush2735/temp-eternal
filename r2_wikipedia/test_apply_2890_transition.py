import copy,json,unittest
import apply_2890_transition as a
class Transition2890Test(unittest.TestCase):
 def setUp(self):self.m=json.loads(a.M.read_text());self.d={'events':[{'id':'other'},copy.deepcopy(self.m['before'])]}
 def test_roundtrip(self):self.assertEqual(a.transform(a.transform(self.d,self.m),self.m,True),self.d)
 def test_missing(self):
  with self.assertRaises(ValueError):a.transform({'events':[]},self.m)
 def test_duplicate(self):
  self.d['events'].append(copy.deepcopy(self.d['events'][1]))
  with self.assertRaises(ValueError):a.transform(self.d,self.m)
 def test_stale(self):
  self.d['events'][1]['name']='different'
  with self.assertRaises(ValueError):a.transform(self.d,self.m)
 def test_stale_rollback(self):
  d=a.transform(self.d,self.m);d['events'][1]['name']='different'
  with self.assertRaises(ValueError):a.transform(d,self.m,True)
 def test_bad_effect(self):
  m=copy.deepcopy(self.m);m['after']['effect']='political'
  with self.assertRaises(ValueError):a.validate(m)
 def test_uncertainty(self):
  m=copy.deepcopy(self.m);m['after']['name']="Qa'a died in 2890"
  with self.assertRaises(ValueError):a.validate(m)
 def test_unexpected_location_change(self):
  m=copy.deepcopy(self.m);m['after']['lon']=10
  with self.assertRaises(ValueError):a.validate(m)
