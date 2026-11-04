import copy,unittest
import apply_451_491_ce_context as m
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
 def test_earthquake_uncertain(self):
  a=self.after('q85738344');self.assertEqual(a['effect'],'note');self.assertIn('454',a['name'])
 def test_wei(self):
  a=self.after('wpr_647bc32aa6');self.assertEqual((a['lat'],a['lon']),(40.097,113.367));self.assertIn('retains power',a['name'])
 def test_isaurian(self):
  a=self.after('wpy_e58a889863');self.assertEqual((a['lat'],a['lon']),(41.00556,28.975))
 def test_clovis(self):
  self.assertEqual(self.after('wpy_f939f6743a')['effect'],'note');self.assertEqual(self.after('wpd_c547c23aeb')['effect'],'note')
 def test_additions(self):self.assertEqual({a['event']['start'] for a in self.a},{451,491})
 def test_no_hazard_edits(self):self.assertFalse(any(u['pack']=='events_hazards.json.gz' for u in self.u))
if __name__=='__main__':unittest.main()
