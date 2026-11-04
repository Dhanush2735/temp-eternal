import copy,json,unittest
import apply_2950_context as c
class Context2950Test(unittest.TestCase):
 def setUp(self):self.m=json.loads(c.M.read_text());self.doc={'events':[self.m['before'],{'id':'other'}]}
 def test_roundtrip(self):self.assertEqual(c.transform(c.transform(self.doc,self.m),self.m,True),self.doc)
 def test_bad_old(self):
  d=copy.deepcopy(self.doc);d['events'][0]['name']='modified'
  with self.assertRaises(ValueError):c.transform(d,self.m)
 def test_duplicate(self):
  d=copy.deepcopy(self.doc);d['events'].append(self.m['event'])
  with self.assertRaises(ValueError):c.transform(d,self.m)
 def test_changed_reverse(self):
  d=c.transform(self.doc,self.m);d['events'][-1]['name']='changed'
  with self.assertRaises(ValueError):c.transform(d,self.m,True)
 def test_bad_caveat(self):
  m=copy.deepcopy(self.m);m['event']['name']='Merneith reigns in 2950'
  with self.assertRaises(ValueError):c.validate(m)
 def test_bad_effect(self):
  m=copy.deepcopy(self.m);m['after']['effect']='political'
  with self.assertRaises(ValueError):c.validate(m)
