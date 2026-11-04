import copy,unittest
import apply_1701_1741_ce_context as m
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
  moves={'wpy_bf3e3dba77':(1730,1731),'wpr_db4d4e61a1':(1732,1733)}
  for u in self.u:
   self.assertEqual(u['before']['id'],u['after']['id'])
   self.assertEqual((u['after']['start'],u['after']['end']),moves.get(u['event_id'],(u['before']['start'],u['before']['end'])))
 def test_locations(self):
  for id,lat,lon in [('wpr_93e3450127',45.50889,-73.55417),('wpr_0cb2c63c93',29.9985,101.9569),('wpy_689560abf8',10.38528,-75.53861),('wpy_5dc6ccd484',55.00083,166.27306),('wpy_cce525a13b',48.20833,16.3725)]:
   a=self.after(id);self.assertAlmostEqual(a['lat'],lat);self.assertAlmostEqual(a['lon'],lon)
 def test_uncertainty(self):
  self.assertIn('uncertain',self.after('wpr_3401d8754a')['name'])
  self.assertIn('disagree',self.after('wpr_1204e3b29d')['name'])
  self.assertIn('variolation',self.after('wpy_3a00c82281')['name'])
 def test_additions(self):self.assertEqual({x['event']['start'] for x in self.a},{1701,1731})
 def test_no_hazard_or_nature_edits(self):self.assertFalse(any(u['pack'] in ('events_hazards.json.gz','events_nature.json.gz') for u in self.u))
if __name__=='__main__':unittest.main()
