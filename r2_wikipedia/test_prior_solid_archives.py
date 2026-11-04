import json,tempfile,unittest
from pathlib import Path
import restore_prior_solid_archives as A
class RestoreTests(unittest.TestCase):
 def test_both_originals_exact_and_no_overwrite(self):
  with tempfile.TemporaryDirectory() as d:
   for kind,(old,_) in A.SPECS.items():
    m=json.loads((A.FOCUS/old).read_text());p=Path(d)/m['archive'];A.restore(kind,p);self.assertEqual(A.sha(p.read_bytes()),m['archive_sha256'])
    with self.assertRaises(FileExistsError):A.restore(kind,p)
if __name__=='__main__':unittest.main()
