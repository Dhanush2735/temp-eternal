import copy,json,lzma,unittest
from pathlib import Path
import apply_3000_bce_metrology_taiwan as A
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.m=A.load(A.M);cls.d=A.load(A.H/A.PACK)
 def test_manifest(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=-10
  with self.assertRaises(ValueError):A.validate(m)
 def test_installed_reversal_and_id_uniqueness(self):
  u=self.m['updates'][0];a=self.m['additions'][0];rows=self.d['events']
  self.assertEqual([x for x in rows if x.get('id')==u['event_id']],[u['after']]);self.assertEqual([x for x in rows if x.get('id')==a['event']['id']],[a['event']])
  old=A.transform(self.d,self.m['updates'],True,self.m['additions']);self.assertEqual(A.transform(old,self.m['updates'],False,self.m['additions']),self.d)
  with self.assertRaises(ValueError):A.transform(self.d,self.m['updates'],False,self.m['additions'])
 def test_approximation_and_effect(self):
  u=self.m['updates'][0]['after'];e=self.m['additions'][0]['event']
  self.assertEqual((u['lat'],u['lon'],u['effect']),(31.32417,45.63722,'note'))
  self.assertEqual((e['start'],e['end'],e['lat'],e['lon'],e['effect']),(-3000,-2500,25.15,121.4,'note'))
  self.assertIn('not imply an origin',e['r2SourceEvidence']['review_note'])
 def test_hashes_pins(self):
  p=Path(__file__).parent/'focus/rollback_hashes_3000_BCE_metrology_taiwan.json.xz';d=json.load(lzma.open(p,'rt'));self.assertEqual(len(d['before']),26);self.assertEqual(d['before'],d['rollback']);self.assertEqual(d['after'],d['reapplied']);self.assertEqual(len(self.m['pin_identities']),7)
if __name__=='__main__':unittest.main()
