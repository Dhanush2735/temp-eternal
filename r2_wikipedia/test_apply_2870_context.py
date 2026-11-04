import copy,json,unittest
import apply_2870_context as a
class Context2870Test(unittest.TestCase):
 def setUp(self):self.m=json.loads(a.M.read_text())
 def doc(self,pack):return {'events':[{'id':'other'}]+[copy.deepcopy(u['before']) for u in self.m['updates'] if u['pack']==pack]}
 def test_roundtrip(self):
  for p,*_ in a.S.values():
   d=self.doc(p);self.assertEqual(a.transform(a.transform(d,self.m,p),self.m,p,True),d)
 def test_missing(self):
  with self.assertRaises(ValueError):a.transform({'events':[]},self.m,next(iter(a.S.values()))[0])
 def test_duplicate(self):
  p=next(iter(a.S.values()))[0];d=self.doc(p);d['events'].append(copy.deepcopy(d['events'][-1]))
  with self.assertRaises(ValueError):a.transform(d,self.m,p)
 def test_stale(self):
  p=next(iter(a.S.values()))[0];d=self.doc(p);d['events'][-1]['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,p)
 def test_stale_rollback(self):
  p=next(iter(a.S.values()))[0];d=a.transform(self.doc(p),self.m,p);d['events'][-1]['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,p,True)
 def test_no_political_effect(self):
  m=copy.deepcopy(self.m);m['updates'][0]['after']['effect']='political'
  with self.assertRaises(ValueError):a.validate(m)
 def test_caveat_required(self):
  m=copy.deepcopy(self.m);m['updates'][1]['after']['name']='Calendar began exactly 2874'
  with self.assertRaises(ValueError):a.validate(m)
 def test_year_and_place_guard(self):
  m=copy.deepcopy(self.m);m['updates'][0]['after']['lat']=35
  with self.assertRaises(ValueError):a.validate(m)
