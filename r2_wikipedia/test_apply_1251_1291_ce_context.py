import copy,unittest
import apply_1251_1291_ce_context as m
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
  for id,lat,lon in [('wpy_def23a5df7',39.99167,116.27222),('wpy_ad4cc68191',32.70528,34.93389),('wpy_951d5863c8',55.722,-2.149),('wpr_92dfb444ef',52.2405,-0.9027),('wpy_1ada3b4b8b',52.40476,23.81952)]:
   a=self.after(id);self.assertAlmostEqual(a['lat'],lat);self.assertAlmostEqual(a['lon'],lon)
 def test_uncertainty(self):
  self.assertIn('1292',self.after('wpr_5f0d9e855f')['name']);self.assertIn('1263',self.after('wpy_41471ef1cc')['name']);self.assertIn('incorrect_year',self.after('wpy_f12c3b9071')['confidence'])
 def test_additions(self):self.assertEqual({x['event']['start'] for x in self.a},{1261,1271,1281,1291})
 def test_no_hazard_or_nature_edits(self):self.assertFalse(any(u['pack'] in ('events_hazards.json.gz','events_nature.json.gz') for u in self.u))
if __name__=='__main__':unittest.main()
