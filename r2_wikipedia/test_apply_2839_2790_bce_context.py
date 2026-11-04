import copy,unittest
import apply_2839_2790_bce_context as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.us=self.man['updates'];self.doc={'events':[copy.deepcopy(u['before']) for u in self.us]}
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.doc,self.us),self.us,True),self.doc)
 def test_input_not_mutated(self):
  d=copy.deepcopy(self.doc);m.transform(self.doc,self.us);self.assertEqual(self.doc,d)
 def test_missing(self):
  with self.assertRaises(ValueError):m.transform({'events':[]},self.us)
 def test_duplicate(self):
  d=copy.deepcopy(self.doc);d['events'].append(copy.deepcopy(d['events'][0]))
  with self.assertRaises(ValueError):m.transform(d,self.us)
 def test_stale_before(self):
  d=copy.deepcopy(self.doc);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.us)
 def test_stale_after(self):
  d=m.transform(self.doc,self.us);d['events'][1]['effect']='political'
  with self.assertRaises(ValueError):m.transform(d,self.us,True)
 def test_hash_guard(self):
  d=copy.deepcopy(self.man);d['updates'][0]['after']['lat']=0
  with self.assertRaises(ValueError):m.validate(d)
 def test_stable_ids_and_places(self):
  for u in self.us:
   for k in ('id','start','lat','lon','radiusKm'):self.assertEqual(u['before'][k],u['after'][k])
 def test_context_windows(self):
  for u in self.us[:2]:self.assertEqual((u['before']['end'],u['after']['end']),(-2889,-2789));self.assertEqual(u['after']['effect'],'note')
 def test_contested_impact_is_note(self):
  u=self.us[2];self.assertEqual((u['after']['kind'],u['after']['effect']),('cultural','note'));self.assertEqual(u['before']['end'],u['after']['end']);self.assertIn('contested',u['after']['r2SourceEvidence']['review_note'])
 def test_per_pack_roundtrip(self):
  for pack in {u['pack'] for u in self.us}:
   us=[u for u in self.us if u['pack']==pack];d={'events':[u['before'] for u in us]};self.assertEqual(m.transform(m.transform(d,us),us,True),d)
if __name__=='__main__':unittest.main()
