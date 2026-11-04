import gzip,io,os,subprocess,tarfile,tempfile,unittest
from pathlib import Path
import archive_java_snapshots as a
class SnapshotArchiveTest(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.d=Path(self.tmp.name)
  raw=io.BytesIO()
  with tarfile.open(fileobj=raw,mode='w') as t:
   x=b'hello';i=tarfile.TarInfo('Test.java');i.size=len(x);t.addfile(i,io.BytesIO(x))
  self.data=a.gzencode(raw.getvalue());(self.d/'step1_java_after.tar.gz').write_bytes(self.data)
 def tearDown(self):self.tmp.cleanup()
 def test_roundtrip_and_idempotence(self):
  r=a.pack(self.d);self.assertEqual(r['files'],1);self.assertFalse((self.d/'step1_java_after.tar.gz').exists());a.restore(self.d);self.assertEqual((self.d/'step1_java_after.tar.gz').read_bytes(),self.data);a.restore(self.d)
 def test_refuses_changed(self):
  a.pack(self.d);p=self.d/'step1_java_after.tar.gz';p.write_bytes(b'changed')
  with self.assertRaises(FileExistsError):a.restore(self.d)
  self.assertEqual(p.read_bytes(),b'changed')
 def test_archive_tampering(self):
  a.pack(self.d);p=self.d/a.ARCHIVE;p.write_bytes(b'broken')
  with self.assertRaises(ValueError):a.restore(self.d)
 def test_unsafe_name(self):
  self.assertFalse(a.safe_name('../step1_java_after.tar.gz'));self.assertFalse(a.safe_name('custom_java_after.tar.gz'))
