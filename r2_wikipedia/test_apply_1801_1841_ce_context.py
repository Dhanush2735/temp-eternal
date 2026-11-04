import copy,unittest
import apply_1801_1841_ce_context as m
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
  for id,lat,lon in [('wpw_c40628ad8e',30.06639,-90.48028),('wpy_c060dfd2e6',46.18611,-119.02861),('wpy_0a3542155c',-71.0,-70.0),('wpy_1d06a3b4c8',52.22722,20.94306),('wpy_802719f0a5',23.7104,90.4074)]:
   a=self.after(id);self.assertAlmostEqual(a['lat'],lat);self.assertAlmostEqual(a['lon'],lon)
 def test_uncertainty(self):
  self.assertIn('governor-general',self.after('wpy_da2689afd2')['name'])
  self.assertIn('not_estate_site',self.after('wpy_a6ef53e0c2')['confidence'])
  self.assertIn('unratified',self.after('wpr_cdc94e3392')['name'])
  self.assertNotIn('pneumonia',self.after('wpr_d957bfe826')['name'])
 def test_additions(self):self.assertEqual({x['event']['start'] for x in self.a},{1801})
 def test_no_hazard_or_nature_edits(self):self.assertFalse(any(u['pack'] in ('events_hazards.json.gz','events_nature.json.gz') for u in self.u))
if __name__=='__main__':unittest.main()
