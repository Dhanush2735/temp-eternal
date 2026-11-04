import copy,unittest
import apply_1451_1491_ce_context as m
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
 def test_ids_and_intended_date_changes(self):
  for u in self.u:
   self.assertEqual(u['before']['id'],u['after']['id'])
   if u['event_id'] not in ('q9366875','q2988608'):
    self.assertEqual((u['before']['start'],u['before']['end']),(u['after']['start'],u['after']['end']))
  self.assertEqual(self.after('q9366875')['start'],1461)
  self.assertEqual(self.after('q2988608')['start'],1481)
 def test_locations(self):
  for id,lat,lon in [('wpy_3264787e7e',38.2675,21.9389),('wpy_fcca555af2',41.005,39.73),('wpy_0bbcbc6797',-6.267,14.248),('wpr_db86f92468',48.1486,17.1077)]:
   a=self.after(id);self.assertAlmostEqual(a['lat'],lat);self.assertAlmostEqual(a['lon'],lon)
 def test_uncertainty(self):
  self.assertEqual(self.after('wpr_bab2c164dd')['effect'],'note')
  self.assertEqual(self.after('q2339983')['effect'],'note')
  self.assertIn('disputed',self.after('q2339983')['name'])
  self.assertIn('1500s',self.after('wpy_edb0c731e4')['name'])
 def test_additions(self):self.assertEqual({x['event']['start'] for x in self.a},{1451,1481})
 def test_no_hazard_or_nature_edits(self):self.assertFalse(any(u['pack'] in ('events_hazards.json.gz','events_nature.json.gz') for u in self.u))
if __name__=='__main__':unittest.main()
