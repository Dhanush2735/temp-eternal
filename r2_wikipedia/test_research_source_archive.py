import gzip,json,unittest
import research_source_archive as A
class ArchiveTests(unittest.TestCase):
 def test_all_exact(self):
  m=json.loads(A.MAP.read_text());self.assertEqual(len(m['files']),116)
  for r in m['files']:
   from research_solid_archive import gzip_for
   b=gzip_for('source',r);raw=gzip.decompress(b)
   self.assertEqual(A.sha(b),r['gzip_sha256']);self.assertEqual(A.sha(raw),r['raw_sha256']);self.assertEqual(A.read(A.SOURCES/r['former']),raw);json.loads(raw)
 def test_no_missing_or_traversal(self):
  with self.assertRaises(FileNotFoundError):A.read(A.SOURCES/'unknown.json')
  with self.assertRaises(ValueError):A.restore('../escape')
if __name__=='__main__':unittest.main()
