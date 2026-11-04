import copy,unittest
import apply_251_291_ce_context as m
class TestEdits(unittest.TestCase):
 def setUp(self): self.man=m.load(m.M);m.validate(self.man);self.u=self.man['updates'];self.d={'events':[copy.deepcopy(x['before']) for x in self.u]}
 def test_roundtrip(self): self.assertEqual(m.transform(m.transform(self.d,self.u),self.u,True),self.d)
 def test_input_unchanged(self):
  d=copy.deepcopy(self.d);m.transform(d,self.u);self.assertEqual(d,self.d)
 def test_conflict(self):
  d=copy.deepcopy(self.d);d['events'][0]['name']='other'
  with self.assertRaises(ValueError):m.transform(d,self.u)
 def test_duplicate(self):
  d=copy.deepcopy(self.d);d['events'].append(copy.deepcopy(d['events'][0]))
  with self.assertRaises(ValueError):m.transform(d,self.u)
 def test_missing(self):
  d=copy.deepcopy(self.d);d['events'].pop()
  with self.assertRaises(ValueError):m.transform(d,self.u)
 def test_manifest_tamper(self):
  x=copy.deepcopy(self.man);x['updates'][0]['after']['start']=0
  with self.assertRaises(ValueError):m.validate(x)
 def after(self,i): return next(x['after'] for x in self.u if x['event_id']==i)
 def test_conflicts_are_notes(self):
  for i in ('wpy_b3a707043b','wpr_1fa926ed46','wpr_cb8b618088','wpy_55d532a692','wpy_27857f4d07'):
   self.assertEqual(self.after(i)['effect'],'note')
 def test_luoyang_reference(self):
  for i in ('wpr_415a389502','wpd_257a6075d4'):
   a=self.after(i);self.assertEqual((a['lat'],a['lon'],a['effect']),(34.6197,112.4539,'note'))
 def test_dura_range(self):
  a=self.after('q1125035');self.assertEqual((a['start'],a['end'],a['effect']),(253,257,'note'))
 def test_coin_chronology_conflicts(self):
  self.assertIn('295',self.after('wpy_c4153a447a')['name'])
 def test_shushtar(self):
  a=self.after('wpy_773cea1354');self.assertEqual((a['lat'],a['lon']),(32.0538,48.8485))
 def test_no_hazard_pack_changes(self):
  self.assertFalse(any(x['pack']=='events_hazards.json.gz' for x in self.u))
if __name__=='__main__':unittest.main()
