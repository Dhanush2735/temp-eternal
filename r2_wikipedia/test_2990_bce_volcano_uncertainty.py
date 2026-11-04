import copy,json,lzma,re,unittest
from pathlib import Path
from unittest.mock import patch
import apply_2990_bce_volcano_uncertainty as A
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.m=A.load(A.M);cls.d=A.load(A.H/A.PACK)
 def test_installed_and_roundtrip(self):
  A.validate(self.m);u=self.m['updates']
  for row in u:self.assertEqual([e for e in self.d['events'] if e.get('id')==row['event_id']],[row['after']])
  old=A.transform(self.d,u,True,[]);self.assertEqual(A.transform(old,u,False,[]),self.d)
  with self.assertRaises(ValueError):A.transform(self.d,u,False,[])
 def test_preserves_behavior_fields_and_severity_tokens(self):
  for u in self.m['updates']:
   b,a=u['before'],u['after'];self.assertEqual({k for k in b if a[k]!=b[k]},{'name'})
   self.assertEqual(re.findall(r'VEI\s+([0-9]+(?:\.[0-9]+)?)',b['name']),re.findall(r'VEI\s+([0-9]+(?:\.[0-9]+)?)',a['name']))
   self.assertEqual(re.findall(r'([0-9][0-9,]*)\s+dead',b['name']),re.findall(r'([0-9][0-9,]*)\s+dead',a['name']))
   self.assertIn('deterministic gameplay',a['r2SourceEvidence']['review_note'])
 def test_manifest_integrity(self):
  m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=-2000
  with self.assertRaises(ValueError):A.validate(m)
 def test_hashes(self):
  p=Path(__file__).parent/'focus/rollback_hashes_2990_BCE_volcano_uncertainty.json.xz';d=json.load(lzma.open(p,'rt'));self.assertEqual(len(d['before']),26);self.assertEqual(d['before'],d['rollback']);self.assertEqual(d['after'],d['reapplied'])
 def test_worldfill_archive(self):
  import sys;sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'worldfill'))
  import archived_history_reports as w
  self.assertEqual(json.loads(w.read('data_use_probe.json'))['events_total'],122432)
  with patch.object(w,'within_budget',return_value=(True,125000000)):
   with self.assertRaises(RuntimeError):w.restore('data_use_probe.json')
if __name__=='__main__':unittest.main()
