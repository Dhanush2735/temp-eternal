import copy,json,unittest
import apply_2750_2710_context as a
class BatchTest(unittest.TestCase):
 def setUp(self):
  self.m=json.loads(a.M.read_text());self.docs={a.E:{'events':[copy.deepcopy(self.m['tyre_event']['before'])]},a.S:{'sites':[copy.deepcopy(self.m['daskalio_site']['before'])]},a.R:{'events':[]}}
 def test_roundtrip(self):
  for p,d in self.docs.items():self.assertEqual(a.transform(a.transform(d,self.m,p),self.m,p,True),d)
 def test_changed_original(self):
  self.docs[a.E]['events'][0]['name']='changed'
  with self.assertRaises(ValueError):a.transform(self.docs[a.E],self.m,a.E)
 def test_duplicate_addition(self):
  self.docs[a.R]['events'].append(self.m['keros_context']['event'])
  with self.assertRaises(ValueError):a.transform(self.docs[a.R],self.m,a.R)
 def test_modified_rollback(self):
  d=a.transform(self.docs[a.R],self.m,a.R);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,a.R,True)
 def test_no_political_effect(self):
  m=copy.deepcopy(self.m);m['tyre_event']['after']['effect']='political'
  with self.assertRaises(ValueError):a.validate(m)
 def test_no_fabricated_date(self):
  m=copy.deepcopy(self.m);m['keros_context']['event']['start']=-2800
  with self.assertRaises(ValueError):a.validate(m)
 def test_hint_blank(self):
  m=copy.deepcopy(self.m);m['daskalio_site']['after']['civHint']='minoan'
  with self.assertRaises(ValueError):a.validate(m)
