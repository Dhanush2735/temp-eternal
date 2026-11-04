import copy,unittest
import apply_351_391_ce_context as m
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
 def test_sepphoris_war(self):
  a=self.after('wpw_8e35ffc77a');self.assertEqual((a['lat'],a['lon']),(32.74556,35.27861));self.assertEqual(a['kind'],'war')
 def test_xingtai(self):self.assertEqual(self.after('wpy_269cb5e685')['lon'],114.5048)
 def test_jin_capital(self):self.assertEqual(self.after('wpy_26c90841ea')['lon'],118.79647)
 def test_pyongyang(self):
  a=self.after('wpy_98fbbd143b');self.assertEqual(a['effect'],'note');self.assertEqual(a['lat'],39.01667)
 def test_sugar(self):self.assertIn('lacks a citation',self.after('wpy_50d6d1855e')['name'])
 def test_vesta(self):self.assertEqual(self.after('wpr_95f7c6312c')['effect'],'note')
 def test_rapa_nui(self):self.assertIn('disputed',self.after('wpr_b4c30c9b03')['name'])
 def test_serapeum(self):self.assertEqual(self.after('wpr_172f29f7b6')['lat'],31.1839)
 def test_additions(self):self.assertEqual({a['event']['start'] for a in self.a},{351,381})
 def test_no_hazard_edits(self):self.assertFalse(any(u['pack']=='events_hazards.json.gz' for u in self.u))
if __name__=='__main__':unittest.main()
