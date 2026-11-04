import copy,unittest
import apply_1601_1641_ce_context as m
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
 def test_ids_and_dates_preserved(self):
  for u in self.u:
   self.assertEqual(u['before']['id'],u['after']['id'])
   self.assertEqual((u['before']['start'],u['before']['end']),(u['after']['start'],u['after']['end']))
 def test_locations(self):
  for id,lat,lon in [('wpr_ff862b6e4d',46.45583,16.9975),('wpr_1689c0925e',58.55,31.267),('wpr_9cd0a3eaf0',48.50694,26.49028),('wpy_6c552909f2',51.483,-9.367),('wpy_3dd89d80f0',32.74352,129.87302),('wpr_29a572b3fb',51.49917,-0.12472)]:
   a=self.after(id);self.assertAlmostEqual(a['lat'],lat);self.assertAlmostEqual(a['lon'],lon)
 def test_uncertainty(self):
  self.assertIn('conflict',self.after('wpy_62b7eb3ed2')['name'])
  self.assertIn('unknown',self.after('wpr_27e7d0ed97')['name'])
  self.assertIn('Zhu Youjiao',self.after('wpr_9624c11fb6')['name'])
 def test_additions(self):self.assertEqual({x['event']['start'] for x in self.a},{1621,1641})
 def test_no_hazard_or_nature_edits(self):self.assertFalse(any(u['pack'] in ('events_hazards.json.gz','events_nature.json.gz') for u in self.u))
if __name__=='__main__':unittest.main()
