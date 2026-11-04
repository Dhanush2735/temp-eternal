import copy,json,unittest
import apply_2850_2810_context as a
class BatchTest(unittest.TestCase):
 def setUp(self):
  self.m=json.loads(a.gzip.open(a.M,'rt',encoding='utf8').read());self.docs={p:{'events':[copy.deepcopy(x['before']) for x in self.m['updates'] if x['pack']==p]} for p in (a.W,a.R)}
 def test_roundtrips(self):
  for p,d in self.docs.items():self.assertEqual(a.transform(a.transform(d,self.m,p),self.m,p,True),d)
 def test_modified_original(self):
  self.docs[a.W]['events'][0]['name']='altered'
  with self.assertRaises(ValueError):a.transform(self.docs[a.W],self.m,a.W)
 def test_strict_rollback(self):
  d=a.transform(self.docs[a.R],self.m,a.R);d['events'][-1]['name']='altered'
  with self.assertRaises(ValueError):a.transform(d,self.m,a.R,True)
 def test_double_apply(self):
  d=a.transform(self.docs[a.R],self.m,a.R)
  with self.assertRaises(ValueError):a.transform(d,self.m,a.R)
 def test_caveats(self):
  m=copy.deepcopy(self.m);m['updates'][1]['after']['name']='oldest'
  with self.assertRaises(ValueError):a.validate(m)
 def test_effect(self):
  m=copy.deepcopy(self.m);m['updates'][2]['after']['effect']='political'
  with self.assertRaises(ValueError):a.validate(m)
 def test_location(self):
  m=copy.deepcopy(self.m);m['additions'][0]['event']['lat']=0
  with self.assertRaises(ValueError):a.validate(m)
