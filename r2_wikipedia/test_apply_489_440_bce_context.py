import copy,unittest
import apply_489_440_bce_context as m
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
 def test_date_changes_guarded(self):
  changed={'q204636','q503982','q1138660','q914210','q2487876','q2705449','q1187461','q975376','q930550'}
  for u in self.us:
   if u['event_id'] not in changed:
    for k in ('start','end'):self.assertEqual(u['before'][k],u['after'][k])
 def test_world_dates_and_effects(self):
  for id,y in [('q204636',-479),('q503982',-479),('q1138660',-480),('q914210',-478),('q2487876',-477),('q2705449',-458),('q1187461',-457),('q975376',-457),('q930550',-447)]:
   self.assertEqual((self.rows[id]['start'],self.rows[id]['end'],self.rows[id]['effect']),(y,y+1,'military_presence'))
   self.assertIn('inclusive',self.rows[id]['r2SourceEvidence']['review_note'])
 def test_corrected_locations(self):
  for id,lat,lon in [('wpy_756d6576ef',38.4889,28.0408),('wpy_d6fe7d3787',37.9839,23.7275),('wpy_c28c4c3992',30.8,30.9),('wpy_50e943a37c',40.82,23.84)]:self.assertEqual((self.rows[id]['lat'],self.rows[id]['lon']),(lat,lon))
 def test_babylon_revolts_notes(self):
  for id in ('wpy_dc9f60b3b0','wpd_912f8f1e66'):self.assertEqual(self.rows[id]['effect'],'note')
 def test_eurymedon_qualifies_date(self):
  r=self.rows['wpy_aa0adf824d'];self.assertEqual(r['effect'],'note');self.assertIn('469 or 466',r['name'])
 def test_regional_invasion_not_constant_combat(self):self.assertEqual(self.rows['q1122337']['effect'],'note')
 def test_evidence(self):
  for u in self.us:self.assertTrue(u['after']['r2SourceEvidence']['sources'])
if __name__=='__main__':unittest.main()
