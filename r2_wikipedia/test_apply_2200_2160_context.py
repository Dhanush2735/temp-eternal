import copy,json,unittest
import apply_2200_2160_context as a
class BatchTest(unittest.TestCase):
 def setUp(self):
  self.m=json.loads(a.M.read_text());self.docs={p:{'events':[copy.deepcopy(u['before']) for u in self.m['updates'] if u['pack']==p]} for p in (a.W,a.R)}
 def test_roundtrip(self):
  for p,d in self.docs.items():self.assertEqual(a.transform(a.transform(d,self.m,p),self.m,p,True),d)
 def test_changed_original(self):
  self.docs[a.W]['events'][0]['name']='changed'
  with self.assertRaises(ValueError):a.transform(self.docs[a.W],self.m,a.W)
 def test_duplicate_addition(self):
  self.docs[a.R]['events'].append(self.m['additions'][0]['event'])
  with self.assertRaises(ValueError):a.transform(self.docs[a.R],self.m,a.R)
 def test_changed_rollback(self):
  d=a.transform(self.docs[a.R],self.m,a.R);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,a.R,True)
 def test_political_effect(self):
  m=copy.deepcopy(self.m);m['updates'][0]['after']['effect']='political'
  with self.assertRaises(ValueError):a.validate(m)
 def test_date(self):
  m=copy.deepcopy(self.m);m['additions'][0]['event']['start']=-3000
  with self.assertRaises(ValueError):a.validate(m)
 def test_missing_caveat(self):
  m=copy.deepcopy(self.m);m['additions'][0]['event']['name']='Puabi died precisely in 2550'
  with self.assertRaises(ValueError):a.validate(m)
 def test_duplicate_original(self):
  self.docs[a.W]['events'].append(copy.deepcopy(self.docs[a.W]['events'][0]))
  with self.assertRaises(ValueError):a.transform(self.docs[a.W],self.m,a.W)
