import copy,unittest
import apply_2439_2390_bce_context as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.us=self.man['updates'];self.docs={u['pack']:{'events':[copy.deepcopy(u['before'])]} for u in self.us}
 def test_roundtrip(self):
  for u in self.us:
   d=self.docs[u['pack']];a=m.transform(d,[u]);self.assertEqual(m.transform(a,[u],True),d)
 def test_no_mutation(self):
  for u in self.us:
   d=self.docs[u['pack']];old=copy.deepcopy(d);m.transform(d,[u]);self.assertEqual(d,old)
 def test_missing(self):
  with self.assertRaises(ValueError):m.transform({'events':[]},[self.us[0]])
 def test_changed(self):
  u=self.us[0];d=copy.deepcopy(self.docs[u['pack']]);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,[u])
 def test_duplicate(self):
  u=self.us[0];d=copy.deepcopy(self.docs[u['pack']]);d['events'].append(copy.deepcopy(u['before']))
  with self.assertRaises(ValueError):m.transform(d,[u])
 def test_changed_after(self):
  u=self.us[0];d=m.transform(self.docs[u['pack']],[u]);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,[u],True)
 def test_guard(self):
  d=copy.deepcopy(self.man);d['updates'][0]['after']['lat']=0
  with self.assertRaises(ValueError):m.validate(d)
 def test_stable(self):
  for u in self.us:
   for k in ('id','start','end','lat','lon','radiusKm','kind','effect','confidence'):self.assertEqual(u['before'][k],u['after'][k])
 def test_uncertainty(self):
  self.assertIn('does not establish',self.us[0]['after']['r2SourceEvidence']['review_note']);self.assertIn('not proof',self.us[1]['after']['r2SourceEvidence']['review_note']);self.assertTrue(all('approximate' in u['after']['name'] for u in self.us))
if __name__=='__main__':unittest.main()
