import copy,unittest
import apply_551_591_ce_context as m
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
 def test_monte_cassino(self):
  a=self.after('wpy_c2f2436f2f');self.assertEqual((a['lat'],a['lon']),(41.49,13.81389));self.assertEqual(a['effect'],'note')
 def test_maya(self):
  a=self.after('wpy_32664a2cfb');self.assertEqual((a['lat'],a['lon']),(16.12611,-91.78333));self.assertEqual(a['effect'],'note')
 def test_china(self):
  a=self.after('wpr_47debd6b6c');self.assertIn('later',a['name']);self.assertEqual(self.after('wpr_622573d79d')['effect'],'note')
 def test_cul_dreimhne(self):
  self.assertEqual(self.after('wpy_bc30c2d834')['effect'],'note');self.assertIn('date debated',self.after('q16245323')['name'])
 def test_additions(self):self.assertEqual({a['event']['start'] for a in self.a},{551,552,561})
 def test_no_hazard_or_nature_edits(self):self.assertFalse(any(u['pack'] in ('events_hazards.json.gz','events_nature.json.gz') for u in self.u))
if __name__=='__main__':unittest.main()
