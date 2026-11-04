import copy,unittest
import apply_851_891_ce_context as m
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
 def test_preserve_ids_and_times_except_englefield(self):
  for u in self.u:
   self.assertEqual(u['before']['id'],u['after']['id'])
   if u['event_id']!='q940959':
    for key in ('start','end'):self.assertEqual(u['before'][key],u['after'][key])
   else:self.assertEqual((u['after']['start'],u['after']['end']),(870,871))
 def test_locations(self):
  for id,lat,lon in [('wpy_721fd9bd85',34.20583,43.87972),('wpy_16c88a908d',41.1253,16.8667),('wpy_d729b755b3',37.517,-4.65),('wpy_c0d7e56b3e',41.89306,12.48278)]:
   a=self.after(id);self.assertAlmostEqual(a['lat'],lat);self.assertAlmostEqual(a['lon'],lon)
 def test_uncertainty(self):
  self.assertIn('or 850',self.after('q85745911')['name']);self.assertIn('unknown',self.after('q2237365')['name']);self.assertIn('questioned',self.after('q85738678')['name']);self.assertIn('uncertain',self.after('wpy_c2c9ed1694')['name'])
 def test_additions(self):self.assertEqual({x['event']['start'] for x in self.a},{851,861,891})
 def test_no_hazard_or_nature_edits(self):self.assertFalse(any(u['pack'] in ('events_hazards.json.gz','events_nature.json.gz') for u in self.u))
if __name__=='__main__':unittest.main()
