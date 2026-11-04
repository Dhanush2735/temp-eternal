import copy,unittest
import apply_1901_1941_ce_context as m
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
  for id,lat,lon in [('wpy_b97c552161',50.75056,-1.26972),('wpr_ba665b63a8',30.5619,114.3404),('wpw_1135615398',32.68972,69.83),('wpr_ac2a356141',50.45,8.05),('wpr_12a7fa80b2',34.5553,69.2075)]:
   x=self.after(id);self.assertAlmostEqual(x['lat'],lat);self.assertAlmostEqual(x['lon'],lon)
 def test_uncertainty(self):
  self.assertIn('unknown',self.after('wpy_2fe97eb18d')['name'])
  self.assertIn('later leads',self.after('wpr_12a7fa80b2')['name'])
  self.assertIn('1922',self.after('wpy_a7c493b055')['name'])
 def test_additions(self):self.assertEqual({x['event']['start'] for x in self.a},{1911})
 def test_no_hazard_or_nature_edits(self):self.assertFalse(any(u['pack'] in ('events_hazards.json.gz','events_nature.json.gz') for u in self.u))
if __name__=='__main__':unittest.main()
