import gzip,hashlib,json,tempfile,unittest
from pathlib import Path
import title_archive as A
class TitleArchiveTests(unittest.TestCase):
 def test_all_original_hashes(self):
  m=json.loads((A.FOCUS/'title_gzip_1562_2026-10.json').read_text())
  for r in m['files']:
   z=(A.FOCUS/r['compressed']).read_bytes();self.assertEqual(hashlib.sha256(z).hexdigest(),r['compressed_sha256']);self.assertEqual(hashlib.sha256(gzip.decompress(z)).hexdigest(),r['raw_sha256'])
 def test_archive_names_and_json(self):
  paths=A.paths();self.assertEqual(len(paths),len({p.name for p in paths}));p=A.FOCUS/'year_titles_1512_1561_CE.json';self.assertIn(p,paths);self.assertEqual(len(A.load(p)['results']),50)
 def test_no_custom_fallback(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'year_titles_1512_1561_CE.json';self.assertEqual(A.source(p),p)
   p.write_text('{"fresh":true}');self.assertEqual(A.load(p),{'fresh':True})
if __name__=='__main__':unittest.main()
