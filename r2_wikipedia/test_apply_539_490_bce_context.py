import copy,unittest
import apply_539_490_bce_context as m
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
  changed={'q3434300','q544239','q427565','q4176897','q28169617','q208261','q2362482','wpy_7eaaf9b8b3'}
  for u in self.us:
   if u['event_id'] not in changed:
    for k in ('start','end'):self.assertEqual(u['before'][k],u['after'][k])
 def test_evidence(self):
  for u in self.us:self.assertTrue(u['after']['r2SourceEvidence']['sources'])
 def test_world_corrections(self):
  for id,y in [('q3434300',-539),('q544239',-525),('q427565',-494),('q4176897',-498)]:
   self.assertEqual((self.rows[id]['start'],self.rows[id]['end'],self.rows[id]['effect']),(y,y+1,'military_presence'))
   self.assertIn('inclusive',self.rows[id]['r2SourceEvidence']['review_note'])
 def test_fall_not_babylon_battle(self):
  self.assertEqual((self.rows['q28169617']['start'],self.rows['q28169617']['effect']),(-539,'note'))
 def test_boju_site_and_duplicate(self):
  self.assertEqual((self.rows['wpy_1e85997df8']['lat'],self.rows['wpy_1e85997df8']['lon']),(31.173,115.008))
  self.assertEqual(self.rows['wpy_3144f17a28']['effect'],'note')
 def test_sungai_site(self):self.assertEqual((self.rows['wpy_34fd339ab2']['lat'],self.rows['wpy_34fd339ab2']['lon']),(5.6953,100.4541))
 def test_buddha_approximation(self):self.assertEqual(self.rows['wpd_3bfdcc5a32']['effect'],'note')
 def test_naxos_distinct(self):
  self.assertEqual(self.rows['wpd_c01b88f00a']['effect'],'note')
  self.assertNotIn('q2035061',self.rows)
 def test_492_not_marathon(self):
  self.assertEqual((self.rows['wpd_82d9fcec45']['effect'],self.rows['wpd_82d9fcec45']['lat'] ),('note',41.0))
 def test_sardis_date(self):self.assertEqual((self.rows['wpy_7eaaf9b8b3']['start'],self.rows['wpy_7eaaf9b8b3']['effect']),(-498,'note'))
 def test_prior_evidence_preserved(self):
  for u in self.us:
   if 'r2SourceEvidence' in u['before']:self.assertEqual(u['before']['r2SourceEvidence'],u['after']['r2SourceEvidence'])
if __name__=='__main__':unittest.main()
