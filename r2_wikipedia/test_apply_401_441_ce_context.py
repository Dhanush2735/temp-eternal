import copy,unittest
import apply_401_441_ce_context as m
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
 def test_hippo(self):
  a=self.after('q7510087');self.assertEqual(a['end'],432);self.assertEqual(self.after('wpy_7266512c63')['effect'],'note')
 def test_danube(self):
  a=self.after('wpr_7f1221ca07');self.assertEqual((a['lat'],a['lon']),(44.61667,21.18333));self.assertEqual(a['effect'],'note');self.assertTrue(a['confidence'].endswith('_region'))
 def test_war(self):
  a=self.after('wpw_c39564c970');self.assertEqual(a['kind'],'war');self.assertEqual((a['lat'],a['lon']),(45.46542,9.18592));self.assertTrue(a['confidence'].endswith('_region'))
 def test_431_eruption(self):
  a=self.after('wpy_237cdd7a35');self.assertIn('uncertain',a['name']);self.assertEqual(a['effect'],'disruption')
 def test_additions(self):self.assertEqual({a['event']['start'] for a in self.a},{411,421,431})
 def test_no_hazard_edits(self):self.assertFalse(any(u['pack']=='events_hazards.json.gz' for u in self.u))
if __name__=='__main__':unittest.main()
