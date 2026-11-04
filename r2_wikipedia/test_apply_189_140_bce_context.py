import copy,unittest
import apply_189_140_bce_context as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.us=self.man['updates'];self.doc={'events':[copy.deepcopy(u['before']) for u in self.us]};self.rows={u['event_id']:u['after'] for u in self.us}
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.doc,self.us),self.us,True),self.doc)
 def test_no_mutation(self):
  d=copy.deepcopy(self.doc);m.transform(self.doc,self.us);self.assertEqual(self.doc,d)
 def test_missing(self):
  with self.assertRaises(ValueError):m.transform({'events':[]},self.us)
 def test_changed(self):
  d=copy.deepcopy(self.doc);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.us)
 def test_duplicate(self):
  d=copy.deepcopy(self.doc);d['events'].append(copy.deepcopy(self.us[0]['before']))
  with self.assertRaises(ValueError):m.transform(d,self.us)
 def test_changed_after(self):
  d=m.transform(self.doc,self.us);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.us,True)
 def test_manifest_guard(self):
  d=copy.deepcopy(self.man);d['updates'][0]['after']['lat']=0
  with self.assertRaises(ValueError):m.validate(d)
 def test_stable_ids(self):
  for u in self.us:self.assertEqual(u['before']['id'],u['after']['id'])
 def test_world_dates(self):
  dates={'q504739':-168,'q2542852':-145,'q587983':-146,'q1268317':-165,'q1268349':-162,'q1290572':-164,'q2617894':-148,'q7443103':-147,'q4871806':-189,'q16933440':-146}
  for id,y in dates.items():
   a=self.rows[id];self.assertEqual((a['start'],a['end'],a['effect']),(y,y+1,'military_presence'));self.assertIn('inclusive',a['r2SourceEvidence']['review_note'])
 def test_carthage(self):
  a=self.rows['q815160'];self.assertEqual((a['start'],a['end'],a['effect']),(-149,-145,'military_presence'))
 def test_uncertainty(self):
  for id in ('q1268339','q2920325','q48731681','q4872671','q6334','q76118','q2556352','wpr_de36cb7154','wpr_aafae2c613','wpr_62dd0dd4be'):self.assertEqual(self.rows[id]['effect'],'note')
 def test_bridge(self):
  self.assertNotIn("world's first",self.rows['wpr_de36cb7154']['name'])
 def test_evidence(self):
  for u in self.us:self.assertTrue(u['after']['r2SourceEvidence']['sources'])
if __name__=='__main__':unittest.main()
