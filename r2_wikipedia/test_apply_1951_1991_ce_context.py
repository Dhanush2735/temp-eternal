import copy,unittest
import apply_1951_1991_ce_context as m
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
  for id,lat,lon in [('wpy_9772465865',39.9113,116.3805),('wpw_a401568aaa',15.49889,73.82778),('wpy_d53e664bf5',23.76444,90.38889),('wpy_f3ebb29410',24.467,54.367),('wpw_bff88eeb47',42.225,43.97),('wpr_8c761095ab',6.49722,2.605),('wpy_54f2f3e3bc',52.617,23.95)]:
   x=self.after(id);self.assertAlmostEqual(x['lat'],lat);self.assertAlmostEqual(x['lon'],lon)
 def test_context(self):
  self.assertIn('1954',self.after('wpw_e7da384650')['r2SourceEvidence']['reason'])
  self.assertIn('declaring',self.after('wpy_54f2f3e3bc')['name'])
  self.assertIn('apartheid',self.after('wpy_3405568371')['name'])
 def test_additions(self):self.assertEqual({x['event']['start'] for x in self.a},{1951})
 def test_no_hazard_or_nature_edits(self):self.assertFalse(any(u['pack'] in ('events_hazards.json.gz','events_nature.json.gz') for u in self.u))
if __name__=='__main__':unittest.main()
