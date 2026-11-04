import copy,unittest
import apply_339_290_bce_context as m
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
  for id,y in [('q123215',-329),('q192938',-334),('q200716',-338),('q201526',-333),('q213074',-326),('q991390',-319),('q2237798',-335),('q1291237',-293),('q635839',-295),('q1407018',-317),('q684113',-315),('q1887733',-305),('q28933',-334),('q4115121',-334)]:
   a=self.rows[id];self.assertEqual((a['start'],a['end'],a['effect']),(y,y+1,'military_presence'));self.assertIn('inclusive',a['r2SourceEvidence']['review_note'])
 def test_cyropolis_location(self):self.assertEqual((self.rows['q7509958']['start'],self.rows['q7509958']['lat'],self.rows['q7509958']['lon']),(-329,40.28333,69.63333))
 def test_battle_alternatives(self):
  for id in ('q1887690','q1799032','q2890214'):self.assertEqual(self.rows[id]['effect'],'note')
 def test_annual_granicus(self):self.assertEqual((self.rows['wpy_ee7ea0574f']['effect'],self.rows['wpy_ee7ea0574f']['lat']),('note',40.31671))
 def test_wars_not_continuous_combat(self):
  for id in ('q3953988','q3984897','q1925514','q2910041','q797952','q2543376_t1','q2543376_t2'):self.assertEqual(self.rows[id]['effect'],'note')
 def test_evidence(self):
  for u in self.us:self.assertTrue(u['after']['r2SourceEvidence']['sources'])
if __name__=='__main__':unittest.main()
