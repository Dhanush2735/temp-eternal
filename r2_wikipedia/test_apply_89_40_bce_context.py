import copy,unittest
import apply_89_40_bce_context as m
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
 def test_dates(self):
  for id,y in {'q335330':-42,'q203681':-48,'q205887':-53,'q131386':-52,'q2299845':-69,'q85745835':-90,'q85745937':-90}.items():
   a=self.rows[id];self.assertEqual((a['start'],a['end'],a['effect']),(y,y+1,'military_presence'));self.assertIn('inclusive',a['r2SourceEvidence']['review_note'])
 def test_massilia(self):
  a=self.rows['q2127400'];self.assertEqual((a['start'],a['end'],a['effect']),(-49,-48,'military_presence'));self.assertIn('includes end',a['r2SourceEvidence']['review_note'])
 def test_asculum(self):
  a=self.rows['q137567'];self.assertEqual((a['start'],a['lat'],a['lon']),(-89,42.85,13.583333))
 def test_duplicates_and_disputes(self):
  for id in ('q647463','q233352','q4870221','q4871929','wpy_1c08f2f973','wpd_d12662ee46'):self.assertEqual(self.rows[id]['effect'],'note')
 def test_hyrcanus_disagreement(self):
  a=self.rows['wpy_04ca34f369'];self.assertEqual((a['start'],a['end']),(-76,-72));self.assertIn('73',a['r2SourceEvidence']['review_note'])
 def test_evidence(self):
  for u in self.us:self.assertTrue(u['after']['r2SourceEvidence']['sources'])
if __name__=='__main__':unittest.main()
