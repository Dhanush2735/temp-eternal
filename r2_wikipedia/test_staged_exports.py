import gzip,lzma,tempfile,unittest
from pathlib import Path
import staged_exports as e
class ExportReaderTest(unittest.TestCase):
 def test_existing_gzip(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'foo.gz'
   with gzip.open(p,'wt',encoding='utf8') as f:f.write('ok')
   with e.open_text(p) as f:self.assertEqual(f.read(),'ok')
 def test_custom_missing_does_not_fall_back(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'history_candidates.jsonl.gz'
   with lzma.open(p.with_suffix('.xz'),'wt',encoding='utf8') as f:f.write('other')
   self.assertEqual(e.source(p),p)
 def test_archived_snapshots_available(self):
  for n in ('history_candidates.jsonl.gz','people_candidates.jsonl.gz'):
   with e.open_text(e.HERE/n) as f:self.assertTrue(next(f).startswith('{'))
