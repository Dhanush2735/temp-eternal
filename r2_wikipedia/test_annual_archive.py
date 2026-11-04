import hashlib,json,lzma,tarfile,tempfile,unittest
from pathlib import Path
import annual_archive as A
class AnnualArchiveTests(unittest.TestCase):
 def test_all_raw_hashes_and_exact_xz_restorable(self):
  m=json.loads(A.MAP.read_text());archive=A.FOCUS/m['archive']
  self.assertEqual(A.sha(archive.read_bytes()),m['archive_sha256'])
  with tarfile.open(archive,'r:xz') as tf:
   self.assertEqual(set(tf.getnames()),{r['member'] for r in m['files']})
   for r in m['files']:
    raw=tf.extractfile(r['member']).read()
    self.assertEqual(A.sha(raw),r['raw_sha256'])
    self.assertEqual(A.sha(lzma.compress(raw,preset=9)),r['compressed_sha256'])
 def test_fallback_and_custom_missing_path(self):
  p=A.FOCUS/'year_wikitext_312_361_CE.json.xz'
  self.assertEqual(len(A.load_json(p)['pages']),50)
  with self.assertRaises(FileNotFoundError):A.read_former(Path('/tmp')/p.name)
 def test_original_solid_archive_exactly_restorable(self):
  original=json.loads((A.FOCUS/'annual_ce_12_1511_original_1612.json').read_text())
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/original['archive']
   self.assertTrue(A.restore_original_solid_archive(p))
   self.assertEqual(A.sha(p.read_bytes()),original['archive_sha256'])
   with self.assertRaises(FileExistsError):A.restore_original_solid_archive(p)
 def test_current_file_takes_precedence(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'year_wikitext_312_361_CE.json.xz'
   p.write_bytes(lzma.compress(b'{"current":true}'))
   self.assertEqual(A.load_json(p),{'current':True})
if __name__=='__main__':unittest.main()
