import copy,unittest
import apply_601_641_ce_context as m
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
 def test_peter(self):
  a=self.after('wpr_cc94ece3e3');self.assertEqual(a['effect'],'note');self.assertAlmostEqual(a['lon'],20.15)
 def test_sisenand(self):
  a=self.after('wpr_da4cff40b4');self.assertNotIn('his son Sisenand',a['name']);self.assertAlmostEqual(a['lat'],41.6488)
 def test_naranjo(self):
  a=self.after('wpw_0b6ed3c475');self.assertIn('Naranjo',a['name']);self.assertEqual(a['effect'],'note')
 def test_hund(self):
  a=self.after('wpr_d89469c839');self.assertAlmostEqual(a['lat'],34.01735);self.assertAlmostEqual(a['lon'],72.43126)
 def test_egypt_and_tower(self):
  for id in ('wpd_6672c79e60','wpy_aeb2e72a23','wpr_87ce8c6313'):self.assertEqual(self.after(id)['effect'],'note')
 def test_additions(self):self.assertEqual({a['event']['start'] for a in self.a},{611,621})
 def test_no_hazard_or_nature_edits(self):self.assertFalse(any(u['pack'] in ('events_hazards.json.gz','events_nature.json.gz') for u in self.u))
if __name__=='__main__':unittest.main()
