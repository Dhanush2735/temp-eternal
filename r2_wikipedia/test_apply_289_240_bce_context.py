import copy,unittest
import apply_289_240_bce_context as m
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
  for id,y in [('q6891',-255),('q963839',-256),('q1160070',-275),('q2478491',-264),('q2292431',-284),('q1482311',-283),('q756413',-279),('q3636302',-279),('q4873050',-276),('q61999900',-249),('q18924894',-278),('q581393',-272)]:
   a=self.rows[id];self.assertEqual((a['start'],a['end'],a['effect']),(y,y+1,'military_presence'));self.assertIn('inclusive',a['r2SourceEvidence']['review_note'])
 def test_dates_uncertain(self):
  for id in ('q815118','q7510190'):self.assertEqual(self.rows[id]['effect'],'note')
 def test_handan(self):
  self.assertIn('Zhao',self.rows['wpy_f8b0bde180']['name']);self.assertEqual((self.rows['wpy_cda85e1360']['lat'],self.rows['wpy_cda85e1360']['lon'],self.rows['wpy_cda85e1360']['effect']),(36.61161,114.48937,'note'))
 def test_ashoka_uncertainty(self):
  for id in ('wpr_1007b432bb','wpd_511f42c70f','wpy_6a3486362d'):self.assertEqual(self.rows[id]['effect'],'note')
  self.assertNotIn('May 16',self.rows['wpr_1007b432bb']['name'])
 def test_war_coverage(self):self.assertEqual((self.rows['q6286']['start'],self.rows['q6286']['effect']),(-264,'note'))
 def test_evidence(self):
  for u in self.us:self.assertTrue(u['after']['r2SourceEvidence']['sources'])
if __name__=='__main__':unittest.main()
