import tempfile,unittest
from pathlib import Path
from storage_guard import workspace_bytes,within_budget

class WorkspaceGuardTests(unittest.TestCase):
 def test_counts_persisted_files_not_excluded_caches(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'normal').mkdir();(p/'normal'/'one').write_bytes(b'a'*10)
   (p/'.cache').mkdir();(p/'.cache'/'discarded').write_bytes(b'b'*100)
   (p/'node_modules').mkdir();(p/'node_modules'/'discarded').write_bytes(b'c'*200)
   (p/'.netrc').write_bytes(b'd'*40)
   (p/'normal'/'link').symlink_to(p/'normal'/'one')
   self.assertEqual(workspace_bytes(p),10)
   self.assertEqual(within_budget(0.000011,p),(True,10))
   self.assertEqual(within_budget(0.000010,p),(False,10))
 def test_git_noncredential_contents_count(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'.git').mkdir();(p/'.git'/'config').write_bytes(b'1'*30)
   (p/'.git'/'HEAD').write_bytes(b'1'*7)
   self.assertEqual(workspace_bytes(p),7)
if __name__=='__main__':unittest.main()
