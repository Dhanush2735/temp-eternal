import copy,json,unittest
import apply_2900_mesopotamia as a
class Mesopotamia2900Tests(unittest.TestCase):
 def setUp(self):self.m=json.loads(a.M.read_text());self.doc={'events':[{'id':'unrelated'}]+[copy.deepcopy(u['before']) for u in self.m['updates']]}
 def test_strict_roundtrip(self):self.assertEqual(a.transform(a.transform(self.doc,self.m),self.m,True),self.doc)
 def test_missing(self):
  self.doc['events'].pop()
  with self.assertRaises(ValueError):a.transform(self.doc,self.m)
 def test_duplicate(self):
  self.doc['events'].append(copy.deepcopy(self.doc['events'][-1]))
  with self.assertRaises(ValueError):a.transform(self.doc,self.m)
 def test_stale_original(self):
  self.doc['events'][1]['name']='changed'
  with self.assertRaises(ValueError):a.transform(self.doc,self.m)
 def test_stale_rollback(self):
  d=a.transform(self.doc,self.m);d['events'][1]['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,True)
 def test_reject_political_effect(self):
  m=copy.deepcopy(self.m);m['updates'][0]['after']['effect']='political'
  with self.assertRaises(ValueError):a.validate(m)
 def test_require_uncertainty(self):
  m=copy.deepcopy(self.m);m['updates'][1]['after']['name']='Mari founded in 2900'
  with self.assertRaises(ValueError):a.validate(m)
 def test_reject_reassigned_id(self):
  m=copy.deepcopy(self.m);m['updates'][2]['after']['id']='different'
  with self.assertRaises(ValueError):a.validate(m)
