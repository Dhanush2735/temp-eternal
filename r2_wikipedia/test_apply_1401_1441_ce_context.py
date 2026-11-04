import copy,unittest
import apply_1401_1441_ce_context as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.u=self.man['updates'];self.a=self.man['additions'];self.d={'events':[copy.deepcopy(x['before']) for x in self.u]}
 def after(self,id):return next(x['after'] for x in self.u if x['event_id']==id)
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.d,self.u,False,self.a),self.u,True,self.a),self.d)
 def test_immutable(self):
  d=copy.deepcopy(self.d);m.transform(self.d,self.u,False,self.a);self.assertEqual(self.d,d)
 def test_missing(self):
  self.d['events'].pop()
  with self.assertRaises(ValueError):m.transform(self.d,self.u)
 def test_duplicate(self):
  self.d['events'].append(copy.deepcopy(self.d['events'][0]))
  with self.assertRaises(ValueError):m.transform(self.d,self.u)
 def test_changed(self):
  self.d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(self.d,self.u)
 def test_duplicate_addition(self):
  self.d['events'].append(copy.deepcopy(self.a[0]['event']))
  with self.assertRaises(ValueError):m.transform(self.d,self.u,False,self.a)
 def test_changed_rollback(self):
  d=m.transform(self.d,self.u,False,self.a);d['events'][-1]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.u,True,self.a)
 def test_tampered_manifest(self):
  a=copy.deepcopy(self.man);a['updates'][0]['after']['start']=0
  with self.assertRaises(ValueError):m.validate(a)
 def test_preserve_ids_and_times(self):
  for u in self.u:
   for k in ('id','start','end'):self.assertEqual(u['before'][k],u['after'][k])
 def test_locations(self):
  for id,lat,lon in [('wpy_2aad1b0a80',53.28,-3.825556),('wpy_bee877b03c',32.0603,118.7969),('wpr_2f6d14529f',33.5138,36.2765),('wpy_c7f9557927',42.615,21.41722)]:
   a=self.after(id);self.assertAlmostEqual(a['lat'],lat);self.assertAlmostEqual(a['lon'],lon)
 def test_uncertainty(self):
  self.assertIn('traditional',self.after('q24945556')['confidence']);self.assertIn('requires further verification',self.after('wpy_165fb64111')['name']);self.assertIn('1411',self.after('wpr_3c60cd4940')['name'])
 def test_additions(self):self.assertEqual({x['event']['start'] for x in self.a},{1401,1411,1441})
 def test_no_hazard_or_nature_edits(self):self.assertFalse(any(u['pack'] in ('events_hazards.json.gz','events_nature.json.gz') for u in self.u))
if __name__=='__main__':unittest.main()
