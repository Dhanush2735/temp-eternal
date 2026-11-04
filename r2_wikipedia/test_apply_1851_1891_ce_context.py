import copy,unittest
import apply_1851_1891_ce_context as m
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
   
   if u['event_id'] not in ('wpy_efb4044e61','wpy_bb328f2c9f'):self.assertEqual((u['before']['start'],u['before']['end']),(u['after']['start'],u['after']['end']))
   else:self.assertEqual((u['after']['start'],u['after']['end']), {'wpy_efb4044e61':(1851,1852),'wpy_bb328f2c9f':(1845,1846)}[u['event_id']])
 def test_locations(self):
  for id,lat,lon in [('wpy_816906fbd3',54.3233,10.1228),('wpr_4a1679896d',37.1,-93.4075),('wpy_6f0b9134c1',47.98639,-104.00139),('wpw_48da3551f2',6.083,10.1),('wpr_102758be2f',42.1015,-72.5898)]:
   x=self.after(id);self.assertAlmostEqual(x['lat'],lat);self.assertAlmostEqual(x['lon'],lon)
 def test_uncertainty(self):
  self.assertIn('later',self.after('wpy_efb4044e61')['name'])
  self.assertIn('disputed',self.after('wpy_bb328f2c9f')['confidence'])
  self.assertIn('secret society',self.after('wpr_ca94e20ae4')['name'])
  self.assertEqual(self.after('wpy_4d81a8b8c1')['kind'],'incident')
 def test_additions(self):self.assertEqual({x['event']['start'] for x in self.a},{1871})
 def test_no_hazard_or_nature_edits(self):self.assertFalse(any(u['pack'] in ('events_hazards.json.gz','events_nature.json.gz') for u in self.u))
if __name__=='__main__':unittest.main()
