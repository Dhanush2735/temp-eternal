import copy,unittest
import apply_801_841_ce_context as m
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
   for key in ('id','start','end'):self.assertEqual(u['before'][key],u['after'][key])
 def test_changed_locations_and_actor(self):
  x=self.after('wpr_41b90917b9');self.assertAlmostEqual(x['lat'],37.4981083);self.assertAlmostEqual(x['lon'],27.5268083);self.assertIn('Cretan raiders attack',x['name'])
  for id,lat,lon in [('wpr_e65ea2e1f5',15.3694,44.191),('wpy_dbd23f632a',38.11111,13.35167),('wpy_32293fca81',31.9,35.2),('wpr_0fa9adc23e',51.4875,-0.1684)]:
   a=self.after(id);self.assertAlmostEqual(a['lat'],lat);self.assertAlmostEqual(a['lon'],lon)
 def test_uncertainty(self):
  self.assertIn('another account gives 804',self.after('wpr_93606800cc')['name']);self.assertIn('earlier Gaelic',self.after('wpd_1ba31df056')['name']);self.assertIn('sources differ',self.after('wpy_32293fca81')['name'])
 def test_additions(self):self.assertEqual({x['event']['start'] for x in self.a},{801,821,841})
 def test_no_hazard_or_nature_edits(self):self.assertFalse(any(u['pack'] in ('events_hazards.json.gz','events_nature.json.gz') for u in self.u))
if __name__=='__main__':unittest.main()
