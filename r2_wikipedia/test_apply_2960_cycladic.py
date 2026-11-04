import copy,json,unittest
import apply_2960_cycladic as c
class Cycladic2960Test(unittest.TestCase):
 def setUp(self):self.m=json.loads(c.M.read_text())
 def test_roundtrip(self):
  a={'events':[self.m['before'],{'id':'other'}]};b=c.transform(a,self.m);self.assertEqual(c.transform(b,self.m,True),a)
 def test_wrong_original(self):
  x=copy.deepcopy(self.m['before']);x['name']='changed'
  with self.assertRaises(ValueError):c.transform({'events':[x]},self.m)
 def test_wrong_reverse(self):
  x=copy.deepcopy(self.m['after']);x['name']='changed'
  with self.assertRaises(ValueError):c.transform({'events':[x]},self.m,True)
 def test_bad_location(self):
  m=copy.deepcopy(self.m);m['after']['lat']=0
  with self.assertRaises(ValueError):c.validate(m)
 def test_bad_dates(self):
  m=copy.deepcopy(self.m);m['after']['end']=-2700
  with self.assertRaises(ValueError):c.validate(m)
