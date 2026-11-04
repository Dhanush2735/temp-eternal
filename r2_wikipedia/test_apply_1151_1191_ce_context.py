import copy,unittest
import apply_1151_1191_ce_context as m
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
  for id,lat,lon in [('wpy_70806fc464',53.9825,-1.88722),('wpy_eaea368951',24.711,118.45),('wpr_4b1f23c532',30.0444,31.2357),('wpd_eb153bfbda',52.259,-7.11),('wpy_3645b27188',46.94806,7.4475)]:
   a=self.after(id);self.assertAlmostEqual(a['lat'],lat);self.assertAlmostEqual(a['lon'],lon)
 def test_uncertainty(self):
  self.assertIn('1154',self.after('wpy_70806fc464')['name']);self.assertIn('1170',self.after('q126959950')['name']);self.assertIn('1180',self.after('q1116528')['name']);self.assertIn('not',self.after('wpw_59c728bf2e')['r2SourceEvidence']['reason'])
 def test_additions(self):self.assertEqual({x['event']['start'] for x in self.a},{1151,1161,1181,1191})
 def test_no_hazard_or_nature_edits(self):self.assertFalse(any(u['pack'] in ('events_hazards.json.gz','events_nature.json.gz') for u in self.u))
if __name__=='__main__':unittest.main()
