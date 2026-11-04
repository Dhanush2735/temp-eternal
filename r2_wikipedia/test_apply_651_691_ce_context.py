import copy,unittest
import apply_651_691_ce_context as m
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
 def test_duplicate_references(self):
  for id in ('wpy_da945ae472','wpy_9cfcbf599c','wpd_991367c1b5','wpr_9a2795a39d','wpy_699d950ae2'):
   self.assertEqual(self.after(id)['effect'],'note')
 def test_locations(self):
  for id,lat,lon in [('wpy_b7d0f980c2',37.66278,62.1925),('wpd_625daf27be',32.02861,44.40083),('wpy_4d313aa658',36.274,126.9098),('wpr_e345d75805',19.37,48.24667),('wpr_5102ad7027',50.75472,-0.765),('wpy_1c1455ed2b',31.778,35.2354)]:
   a=self.after(id);self.assertAlmostEqual(a['lat'],lat);self.assertAlmostEqual(a['lon'],lon)
 def test_uncertain_date_events_are_notes(self):
  for id in ('wpy_109754e1da','wpr_697164b01c','wpy_268eed49ca','wpr_f13a0a03d6','wpy_eb7d3058a3'):
   self.assertEqual(self.after(id)['effect'],'note')
 def test_preserve_ids_and_times(self):
  for u in self.u:
   for key in ('id','start','end'):self.assertEqual(u['before'][key],u['after'][key])
 def test_additions(self):self.assertEqual({a['event']['start'] for a in self.a},{671,681,682})
 def test_no_hazard_or_nature_edits(self):self.assertFalse(any(u['pack'] in ('events_hazards.json.gz','events_nature.json.gz') for u in self.u))
if __name__=='__main__':unittest.main()
