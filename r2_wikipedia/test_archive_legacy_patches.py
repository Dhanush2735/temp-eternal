import json,tempfile,unittest
from pathlib import Path
from archive_legacy_patches import pack,restore,read_checked,ARCHIVE,MANIFEST

class ArchiveTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  (self.root/'java_changes_a.patch').write_bytes(b'hello\n'*20)
  (self.root/'java_changes_b.patch').write_bytes(b'hello\n'*21)
  (self.root/'game_asset.txt').write_bytes(b'unchanged')
 def test_verified_round_trip_and_repeated_restore(self):
  original={p.name:p.read_bytes() for p in self.root.glob('*.patch')};r=pack(self.root)
  self.assertEqual(r['files'],2);self.assertFalse(any(self.root.glob('*.patch')))
  self.assertEqual(read_checked(self.root)[1],original);self.assertEqual(restore(self.root),2);self.assertEqual(restore(self.root),2)
  self.assertEqual({p.name:p.read_bytes() for p in self.root.glob('*.patch')},original)
  self.assertEqual((self.root/'game_asset.txt').read_bytes(),b'unchanged')
 def test_corrupt_archive_does_not_restore(self):
  pack(self.root);p=self.root/ARCHIVE;p.write_bytes(p.read_bytes()+b'x')
  with self.assertRaises(ValueError):restore(self.root)
  self.assertFalse(any(self.root.glob('*.patch')))
 def test_conflicting_file_not_overwritten_or_partial_restore(self):
  pack(self.root);p=self.root/'java_changes_b.patch';p.write_bytes(b'new user content')
  with self.assertRaises(FileExistsError):restore(self.root)
  self.assertFalse((self.root/'java_changes_a.patch').exists());self.assertEqual(p.read_bytes(),b'new user content')
 def test_bad_path_rejected(self):
  pack(self.root);m=self.root/MANIFEST;j=json.loads(m.read_text());j['files'][0]['name']='../java_changes_a.patch';m.write_text(json.dumps(j))
  with self.assertRaises(ValueError):restore(self.root)
