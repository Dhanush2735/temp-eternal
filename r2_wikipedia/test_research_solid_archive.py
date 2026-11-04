import gzip,json,unittest
from pathlib import Path
import research_solid_archive as S
import research_source_archive as A
import people_graph_archive as G
class SolidTests(unittest.TestCase):
 def test_all_groups_and_exact_raw_and_gzip(self):
  m=json.loads(S.MAP.read_text());self.assertEqual(len(m['groups']),6)
  for kind in ('source','graph'):
   records=json.loads(S.MANIFESTS[kind].read_text())['files']
   for r in records:
    raw=S.raw_for(kind,r);b=S.gzip_for(kind,r)
    self.assertEqual(S.sha(raw),r['raw_sha256']);self.assertEqual(S.sha(b),r['gzip_sha256']);self.assertEqual(gzip.decompress(b),raw)
    if kind=='source':self.assertEqual(A.read(A.SOURCES/r['former']),raw)
    else:self.assertEqual(G.load_json(G.SOURCES/r['former']),json.loads(raw))
 def test_recent_graph_gzip(self):
  for r in json.loads(G.ADDITIONAL_MAP.read_text())['files']:
   b=S.gzip_for('graph',r);self.assertEqual(S.sha(b),r['gzip_sha256']);self.assertEqual(S.sha(gzip.decompress(b)),r['raw_sha256']);self.assertEqual(G.load_json(G.SOURCES/r['former']),json.loads(gzip.decompress(b)))
 def test_reject_path_traversal(self):
  with self.assertRaises(ValueError):S.restore_gzip('source','../bad.gz')
if __name__=='__main__':unittest.main()
