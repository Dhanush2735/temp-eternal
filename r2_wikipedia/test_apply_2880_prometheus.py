import copy,json,unittest
import apply_2880_prometheus as a
class Prometheus2880Tests(unittest.TestCase):
 def setUp(self):self.m=json.loads(a.M.read_text())
 def make(self,pack):return {'events':[{'id':'other'}]+[copy.deepcopy(x['before']) for x in self.m['updates'] if x['pack']==pack]}
 def test_roundtrip(self):
  for pack,*_ in a.S.values():
   d=self.make(pack);self.assertEqual(a.transform(a.transform(d,self.m,pack),self.m,pack,True),d)
 def test_missing(self):
  p=next(iter(a.S.values()))[0]
  with self.assertRaises(ValueError):a.transform({'events':[]},self.m,p)
 def test_duplicate(self):
  p=next(iter(a.S.values()))[0];d=self.make(p);d['events'].append(copy.deepcopy(d['events'][-1]))
  with self.assertRaises(ValueError):a.transform(d,self.m,p)
 def test_stale(self):
  p=next(iter(a.S.values()))[0];d=self.make(p);d['events'][-1]['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,p)
 def test_stale_rollback(self):
  p=next(iter(a.S.values()))[0];d=a.transform(self.make(p),self.m,p);d['events'][-1]['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,p,True)
 def test_qualifications(self):
  m=copy.deepcopy(self.m);m['updates'][0]['after']['name']='Prometheus germinates'
  with self.assertRaises(ValueError):a.validate(m)
 def test_location_change_rejected(self):
  m=copy.deepcopy(self.m);m['updates'][1]['after']['lat']=40
  with self.assertRaises(ValueError):a.validate(m)
 def test_wrong_effect_rejected(self):
  m=copy.deepcopy(self.m);m['updates'][1]['after']['effect']='disruption'
  with self.assertRaises(ValueError):a.validate(m)
