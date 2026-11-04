import copy,json,unittest
import apply_2650_2610_context as a
class BatchTest(unittest.TestCase):
 def setUp(self):
  self.m=json.loads(a.M.read_text());self.docs={p:{'events':[copy.deepcopy(u['before']) for u in self.m['updates'] if u['pack']==p]} for p in (a.W,a.R)}
 def test_roundtrip(self):
  for p,d in self.docs.items():self.assertEqual(a.transform(a.transform(d,self.m,p),self.m,p,True),d)
 def test_original_changed(self):
  self.docs[a.W]['events'][0]['name']='changed'
  with self.assertRaises(ValueError):a.transform(self.docs[a.W],self.m,a.W)
 def test_duplicate_id(self):
  self.docs[a.W]['events'].append(copy.deepcopy(self.docs[a.W]['events'][0]))
  with self.assertRaises(ValueError):a.transform(self.docs[a.W],self.m,a.W)
 def test_modified_after(self):
  d=a.transform(self.docs[a.R],self.m,a.R);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,a.R,True)
 def test_political_effect_rejected(self):
  m=copy.deepcopy(self.m);m['updates'][0]['after']['effect']='political'
  with self.assertRaises(ValueError):a.validate(m)
 def test_precision_caveat(self):
  m=copy.deepcopy(self.m);m['updates'][2]['after']['name']='Nippur rod created exactly in 2650'
  with self.assertRaises(ValueError):a.validate(m)
 def test_wrong_dates(self):
  m=copy.deepcopy(self.m);m['updates'][4]['after']['start']=-2494
  with self.assertRaises(ValueError):a.validate(m)
 def test_missing_record(self):
  self.docs[a.W]['events'].pop()
  with self.assertRaises(ValueError):a.transform(self.docs[a.W],self.m,a.W)
