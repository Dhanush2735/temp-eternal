import copy,json,unittest
import apply_2890_akkadian as a
class Akkadian2890Test(unittest.TestCase):
 def setUp(self):self.m=json.loads(a.M.read_text());self.d={'events':[{'id':'other'}]+[copy.deepcopy(u['before']) for u in self.m['updates']]}
 def test_roundtrip(self):self.assertEqual(a.transform(a.transform(self.d,self.m),self.m,True),self.d)
 def test_missing(self):
  self.d['events'].pop()
  with self.assertRaises(ValueError):a.transform(self.d,self.m)
 def test_duplicate(self):
  self.d['events'].append(copy.deepcopy(self.d['events'][-1]))
  with self.assertRaises(ValueError):a.transform(self.d,self.m)
 def test_stale(self):
  self.d['events'][1]['name']='different'
  with self.assertRaises(ValueError):a.transform(self.d,self.m)
 def test_stale_rollback(self):
  d=a.transform(self.d,self.m);d['events'][1]['name']='different'
  with self.assertRaises(ValueError):a.transform(d,self.m,True)
 def test_bad_effect(self):
  m=copy.deepcopy(self.m);m['updates'][0]['after']['effect']='political'
  with self.assertRaises(ValueError):a.validate(m)
 def test_bad_year(self):
  m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=-2890
  with self.assertRaises(ValueError):a.validate(m)
 def test_missing_caveat(self):
  m=copy.deepcopy(self.m);m['updates'][1]['after']['name']='first Akkadian text in 2400'
  with self.assertRaises(ValueError):a.validate(m)
