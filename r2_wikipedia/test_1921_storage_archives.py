import gzip,hashlib,json,lzma,unittest
from unittest.mock import patch
from pathlib import Path
import review_snapshot_archive as R
import restore_vip_staging as S
from staged_exports import source,open_text

class ArchiveTests(unittest.TestCase):
 def test_review_snapshots(self):
  rows=json.loads(R.MANIFEST.read_text())['files'];self.assertEqual(len(rows),12)
  for row in rows:
   raw=R.read(row['former']);self.assertEqual(hashlib.sha256(raw).hexdigest(),row['sha256']);json.loads(raw)
 def test_review_no_traversal_and_no_overwrite(self):
  with self.assertRaises(ValueError):R.read('../bad')
  with patch.object(R,'within_budget',return_value=(True,125000000)):
   with self.assertRaises(RuntimeError):R.restore('150_110_exact_start_before.json')
 def test_staging_roundtrip_and_read(self):
  for kind in ('places','timelines'):
   p,rawhash,gzhash=S.SPECS[kind];self.assertFalse(p.exists());raw=lzma.decompress(source(p).read_bytes());self.assertEqual(hashlib.sha256(raw).hexdigest(),rawhash);self.assertEqual(hashlib.sha256(gzip.compress(raw,9,mtime=0)).hexdigest(),gzhash)
   with open_text(p) as f:self.assertEqual(f.read().encode(),raw)
   with patch.object(S,'within_budget',return_value=(True,125000000)):
    with self.assertRaises(RuntimeError):S.restore(kind)
if __name__=='__main__':unittest.main()
