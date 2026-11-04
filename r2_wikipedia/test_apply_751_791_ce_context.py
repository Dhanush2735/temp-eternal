import copy,unittest
import apply_751_791_ce_context as m
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
 def test_uncertainty_and_corrected_sites(self):
  for id in ('wpy_df0951f27f','wpy_40f8d2a1aa','wpr_ddbbe46aab','wpr_893c722ec1','wpr_1288931255'):
   self.assertEqual(self.after(id)['effect'],'note')
  for id,lat,lon in [('wpr_0c094fa848',36.8889,49.9056),('wpy_d6abc13d41',35.79,129.33222),('wpr_40ec62d6f7',21.0285,105.8542),('wpw_373ed9e46f',42.525,72.23333)]:
   a=self.after(id);self.assertAlmostEqual(a['lat'],lat);self.assertAlmostEqual(a['lon'],lon)
 def test_conflicting_sources_and_succession(self):
  self.assertIn('782',self.after('wpr_ddbbe46aab')['name'])
  self.assertIn('born two months later',self.after('wpr_4440ad2a63')['name'])
  self.assertIn('uncertain',self.after('wpr_23a04a8091')['name'])
 def test_preserve_ids_and_times(self):
  for u in self.u:
   for key in ('id','start','end'):self.assertEqual(u['before'][key],u['after'][key])
 def test_additions(self):
  self.assertEqual({a['event']['start'] for a in self.a},{751,771,781})
  row=next(a['event'] for a in self.a if a['event']['id']=='r2_781_pepin_louis_coronations')
  self.assertIn('Pepin king of Italy',row['name']);self.assertIn('Louis king of Aquitaine',row['name'])
 def test_no_hazard_or_nature_edits(self):self.assertFalse(any(u['pack'] in ('events_hazards.json.gz','events_nature.json.gz') for u in self.u))
if __name__=='__main__':unittest.main()
