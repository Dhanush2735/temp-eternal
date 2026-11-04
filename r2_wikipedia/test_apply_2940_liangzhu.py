import copy,json,unittest
import apply_2940_liangzhu as c
class Liangzhu2940Test(unittest.TestCase):
 def setUp(self):self.m=json.loads(c.M.read_text());self.doc={'events':[self.m['before'],{'id':'other'}]}
 def test_roundtrip(self):self.assertEqual(c.transform(c.transform(self.doc,self.m),self.m,True),self.doc)
 def test_changed_original(self):
  d=copy.deepcopy(self.doc);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):c.transform(d,self.m)
 def test_changed_reverse(self):
  d=c.transform(self.doc,self.m);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):c.transform(d,self.m,True)
 def test_duplicates(self):
  d=copy.deepcopy(self.doc);d['events'].append(self.m['before'])
  with self.assertRaises(ValueError):c.transform(d,self.m)
 def test_bad_end(self):
  m=copy.deepcopy(self.m);m['after']['end']=-2000
  with self.assertRaises(ValueError):c.validate(m)
 def test_bad_class(self):
  m=copy.deepcopy(self.m);m['after']['confidence']='wikipedia_coord'
  with self.assertRaises(ValueError):c.validate(m)
