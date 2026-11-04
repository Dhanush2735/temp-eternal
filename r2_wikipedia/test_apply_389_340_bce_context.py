import copy,unittest
import apply_389_340_bce_context as m
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
  for id,y in [('q2334746',-364),('q20987758',-373),('q3625492',-368),('q133734377',-348)]:
   a=self.rows[id];self.assertEqual((a['start'],a['end'],a['effect']),(y,y+1,'military_presence'));self.assertIn('inclusive',a['r2SourceEvidence']['review_note'])
 def test_samnite_uncertain(self):
  for id in ('q853635','q511578','q16253748'):self.assertEqual((self.rows[id]['start'],self.rows[id]['effect']),(-343,'note'))
 def test_helike_not_duplicated_damage(self):
  for id in ('q123757467','wpy_fc2055f850','wpy_515e17337f'):self.assertEqual(self.rows[id]['effect'],'note')
  self.assertEqual(self.rows['q123757467']['start'],-373);self.assertEqual(self.rows['wpy_fc2055f850']['lat'],38.222)
 def test_ongoing_war_not_continuous_combat(self):
  for id in ('q1249270','q3782240','q387020','q499229'):self.assertEqual(self.rows[id]['effect'],'note')
 def test_china(self):
  self.assertEqual(self.rows['q2065036']['effect'],'note');self.assertEqual(self.rows['wpy_e11d6c4f14']['effect'],'note')
 def test_evidence(self):
  for u in self.us:self.assertTrue(u['after']['r2SourceEvidence']['sources'])
if __name__=='__main__':unittest.main()
