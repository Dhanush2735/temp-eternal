import copy,unittest
import apply_301_341_ce_context as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.u=self.man['updates'];self.a=self.man['additions'];self.d={'events':[copy.deepcopy(x['before']) for x in self.u]}
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.d,self.u,False,self.a),self.u,True,self.a),self.d)
 def test_input_immutable(self):
  before=copy.deepcopy(self.d);m.transform(self.d,self.u,False,self.a);self.assertEqual(self.d,before)
 def test_source_mismatch(self):
  self.d['events'][0]['name']='different'
  with self.assertRaises(ValueError):m.transform(self.d,self.u)
 def test_duplicate_existing(self):
  self.d['events'].append(copy.deepcopy(self.d['events'][0]))
  with self.assertRaises(ValueError):m.transform(self.d,self.u)
 def test_missing_existing(self):
  self.d['events'].pop()
  with self.assertRaises(ValueError):m.transform(self.d,self.u)
 def test_duplicate_addition(self):
  self.d['events'].append(copy.deepcopy(self.a[0]['event']))
  with self.assertRaises(ValueError):m.transform(self.d,self.u,False,self.a)
 def test_changed_addition_rollback(self):
  d=m.transform(self.d,self.u,False,self.a);d['events'][-1]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.u,True,self.a)
 def test_tamper(self):
  x=copy.deepcopy(self.man);x['updates'][0]['after']['start']=0
  with self.assertRaises(ValueError):m.validate(x)
 def after(self,id):return next(x['after'] for x in self.u if x['event_id']==id)
 def test_san_marino(self):
  a=self.after('wpr_d88a359df7');self.assertEqual((a['lat'],a['lon'],a['effect']),(43.933,12.433,'note'));self.assertIn('legendary',a['name'])
 def test_seleucia(self):
  a=self.after('wpr_434ef6a765');self.assertEqual((a['lat'],a['lon']),(33.1,44.583));self.assertIn('uncertain',a['name'])
 def test_luoyang_active(self):
  a=self.after('wpr_ca6b355f4f');self.assertEqual(a['effect'],'political');self.assertEqual(a['lat'],34.6197)
 def test_armenian_tradition(self):self.assertIn('traditional',self.after('wpr_622e14a5ea')['name'])
 def test_additions(self):self.assertEqual({a['event']['start'] for a in self.a},{311,341})
 def test_no_hazard_edits(self):self.assertFalse(any(x['pack']=='events_hazards.json.gz' for x in self.u))
if __name__=='__main__':unittest.main()
