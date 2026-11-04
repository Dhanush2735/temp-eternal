import copy,json,unittest
import apply_2800_2760_context as a
class BatchTest(unittest.TestCase):
 def setUp(self):self.m=json.loads(a.M.read_text());self.d={'events':[copy.deepcopy(u['before']) for u in self.m['updates']]}
 def test_roundtrip(self):self.assertEqual(a.transform(a.transform(self.d,self.m),self.m,True),self.d)
 def test_old_changed(self):
  self.d['events'][0]['name']='different'
  with self.assertRaises(ValueError):a.transform(self.d,self.m)
 def test_duplicate(self):
  self.d['events'].append(self.m['additions'][0])
  with self.assertRaises(ValueError):a.transform(self.d,self.m)
 def test_rollback_changed(self):
  d=a.transform(self.d,self.m);d['events'][-1]['name']='different'
  with self.assertRaises(ValueError):a.transform(d,self.m,True)
 def test_uncertain(self):
  m=copy.deepcopy(self.m);m['additions'][0]['name']='Harp made at Keros'
  with self.assertRaises(ValueError):a.validate(m)
 def test_no_political_effect(self):
  m=copy.deepcopy(self.m);m['updates'][0]['after']['effect']='political'
  with self.assertRaises(ValueError):a.validate(m)
 def test_location(self):
  m=copy.deepcopy(self.m);m['additions'][0]['lon']=0
  with self.assertRaises(ValueError):a.validate(m)
