import copy,unittest
import apply_1051_1091_ce_context as m
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
  for id,lat,lon in [('wpw_0dd498e7e1',37.6,14.0),('wpd_ee82436a34',35.885,14.403),('wpr_f4791a1781',47.45,18.42),('wpr_870797851d',52.35,-1.5),('wpy_0c38ae4821',38.1938,15.554)]:
   a=self.after(id);self.assertAlmostEqual(a['lat'],lat);self.assertAlmostEqual(a['lon'],lon)
 def test_uncertainty(self):
  self.assertIn('first non-Greek metropolitan of Kyiv',self.after('wpr_57569f27bf')['name']);self.assertIn('uncertain',self.after('wpr_bae666b81c')['name']);self.assertIn('1095',self.after('wpy_af8a2a3111')['r2SourceEvidence']['reason']);self.assertIn('not a direct measurement',self.after('wpy_4bfc6bfae3')['r2SourceEvidence']['reason'])
 def test_additions(self):self.assertEqual({x['event']['start'] for x in self.a},{1051,1061,1081,1091})
 def test_no_hazard_or_nature_edits(self):self.assertFalse(any(u['pack'] in ('events_hazards.json.gz','events_nature.json.gz') for u in self.u))
if __name__=='__main__':unittest.main()
