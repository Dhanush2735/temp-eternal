import copy,unittest
import apply_2001_2021_ce_context as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.u=self.man['updates'];self.d={'events':[copy.deepcopy(x['before']) for x in self.u]}
 def after(self,id):return next(x['after'] for x in self.u if x['event_id']==id)
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.d,self.u),self.u,True),self.d)
 def test_immutable(self):
  d=copy.deepcopy(self.d);m.transform(self.d,self.u);self.assertEqual(self.d,d)
 def test_missing(self):
  self.d['events'].pop()
  with self.assertRaises(ValueError):m.transform(self.d,self.u)
 def test_duplicate(self):
  self.d['events'].append(copy.deepcopy(self.d['events'][0]))
  with self.assertRaises(ValueError):m.transform(self.d,self.u)
 def test_changed(self):
  self.d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(self.d,self.u)
 def test_changed_rollback(self):
  d=m.transform(self.d,self.u);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.u,True)
 def test_tampered_manifest(self):
  a=copy.deepcopy(self.man);a['updates'][0]['after']['start']=0
  with self.assertRaises(ValueError):m.validate(a)
 def test_ids_dates_preserved(self):
  for u in self.u:self.assertEqual((u['before']['id'],u['before']['start'],u['before']['end']),(u['after']['id'],u['after']['start'],u['after']['end']))
 def test_locations(self):
  for id,lat,lon in [('wpy_29b73d4930',34.832,67.8267),('wpy_d184d4c2f2',28.6172,77.2081),('wpy_8dfdc25515',26.024334,89.583338),('wpy_81ac3f27c5',5.169,-52.6903),('wpy_205f992a53',38.88972,-77.00917)]:
   x=self.after(id);self.assertAlmostEqual(x['lat'],lat);self.assertAlmostEqual(x['lon'],lon)
 def test_mars_disclosed(self):
  for id in ['wpy_0039df8b09','wpr_12d7ad088d']:
   x=self.after(id);self.assertIn('Earth',x['name']);self.assertIn('proxy',x['confidence'])
 def test_bouazizi(self):
  x=self.after('wpy_3f7ade5d38');self.assertEqual((x['kind'],x['effect']),('incident','note'));self.assertIn('17 December 2010',x['name'])
 def test_no_future_or_hazard(self):
  self.assertTrue(all(u['after']['start'] in (2001,2011,2021) and u['pack']!='events_hazards.json.gz' for u in self.u));self.assertEqual(self.man['additions'],[])
 def test_provenance(self):
  for u in self.u:self.assertTrue(u['after']['r2SourceEvidence']['sources']);self.assertTrue(u['after']['r2SourceEvidence']['reason'])
if __name__=='__main__':unittest.main()
