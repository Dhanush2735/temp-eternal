import copy,json,unittest
import apply_2860_saqqara as a
class Saqqara2860Test(unittest.TestCase):
 def setUp(self):self.m=json.loads(a.M.read_text());self.e=self.m['event'];self.d={'events':[{'id':'unrelated'}]}
 def test_roundtrip(self):self.assertEqual(a.transform(a.transform(self.d,self.e),self.e,True),self.d)
 def test_duplicate(self):
  with self.assertRaises(ValueError):a.transform({'events':[self.e]},self.e)
 def test_missing_rollback(self):
  with self.assertRaises(ValueError):a.transform(self.d,self.e,True)
 def test_modified_rollback(self):
  d=a.transform(self.d,self.e);d['events'][-1]['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.e,True)
 def test_wrong_kind(self):
  m=copy.deepcopy(self.m);m['event']['effect']='political'
  with self.assertRaises(ValueError):a.validate(m)
 def test_uncertainty(self):
  m=copy.deepcopy(self.m);m['event']['name']='Construction begins in 2860'
  with self.assertRaises(ValueError):a.validate(m)
 def test_wrong_coordinates(self):
  m=copy.deepcopy(self.m);m['event']['lon']=0
  with self.assertRaises(ValueError):a.validate(m)
