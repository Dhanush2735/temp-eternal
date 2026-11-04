import copy,unittest
import apply_701_741_ce_context as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.u=self.man['updates'];self.a=self.man['additions'];self.d={'events':[copy.deepcopy(x['before']) for x in self.u]}
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
 def after(self,id):return next(x['after'] for x in self.u if x['event_id']==id)
 def test_uncertain_claims_are_notes(self):
  for id in ('wpy_4b3087f3e2','wpr_1134715fa2','wpr_47cf968e31','wpr_659cbd1206','wpr_60bb8dac6b'):
   self.assertEqual(self.after(id)['effect'],'note')
 def test_corrected_sites(self):
  for id,lat,lon in [('wpy_ecd7dcdbec',15.2636,39.6606),('wpr_1134715fa2',17.1335972,-89.2621694),('wpy_dca6044d58',47.233,8.817),('wpr_006dce30b8',51.279,1.083)]:
   a=self.after(id);self.assertAlmostEqual(a['lat'],lat);self.assertAlmostEqual(a['lon'],lon)
 def test_conflicting_claims_acknowledged(self):
  self.assertIn('703',self.after('wpd_0f4989741b')['name'])
  self.assertIn('714',self.after('wpy_4b3087f3e2')['name'])
  self.assertIn('unidentified',self.after('q504172')['name'])
 def test_preserve_ids_and_times(self):
  for u in self.u:
   for key in ('id','start','end'):self.assertEqual(u['before'][key],u['after'][key])
 def test_additions(self):self.assertEqual({a['event']['start'] for a in self.a},{711,731,741})
 def test_no_hazard_or_nature_edits(self):self.assertFalse(any(u['pack'] in ('events_hazards.json.gz','events_nature.json.gz') for u in self.u))
if __name__=='__main__':unittest.main()
