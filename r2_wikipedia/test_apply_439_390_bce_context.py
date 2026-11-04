import copy,unittest
import apply_439_390_bce_context as m
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
  for id,y in [('q176416',-425),('q1362053',-418),('q1424844',-424),('q1475533',-429),('q1278821',-409),('q1287213',-409),('q617924',-426),('q2628112',-405),('q1151812',-394),('q1671704',-394),('q733113',-394),('q3502459',-398),('q2889436',-416)]:
   a=self.rows[id];self.assertEqual((a['start'],a['end'],a['effect']),(y,y+1,'military_presence'));self.assertIn('inclusive',a['r2SourceEvidence']['review_note'])
 def test_duplicate_disaster_note(self):self.assertEqual((self.rows['q1348784']['start'],self.rows['q1348784']['effect']),(-426,'note'))
 def test_war_not_constant_combat(self):self.assertEqual(self.rows['q33745']['effect'],'note')
 def test_socrates_athens(self):self.assertEqual((self.rows['wpy_53d2c0c6af']['lat'],self.rows['wpy_53d2c0c6af']['lon']),(37.98417,23.72806))
 def test_sicilian_reinforcements(self):self.assertEqual((self.rows['wpy_dff6ab4865']['start'],self.rows['wpy_dff6ab4865']['effect']),(-413,'note'))
 def test_evidence(self):
  for u in self.us:self.assertTrue(u['after']['r2SourceEvidence']['sources'])
if __name__=='__main__':unittest.main()
