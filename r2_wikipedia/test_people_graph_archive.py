import gzip,hashlib,json,unittest
from pathlib import Path
import people_graph_archive as A

class GraphArchiveTests(unittest.TestCase):
 def test_all_recorded_graphs_exact(self):
  m=json.loads(A.MAP.read_text());self.assertGreaterEqual(len(m['files']),95)
  for r in m['files']:
   from research_solid_archive import gzip_for
   comp=gzip_for('graph',r);raw=gzip.decompress(comp)
   self.assertEqual(A.sha(comp),r['gzip_sha256']);self.assertEqual(A.sha(raw),r['raw_sha256'])
   self.assertEqual(A.load_json(A.SOURCES/r['former']),json.loads(raw))
 def test_unknown_paths_rejected(self):
  with self.assertRaises(FileNotFoundError):A.load_json(A.SOURCES/'missing_people_links.json')
  with self.assertRaises(ValueError):A.restore('../bad')
 def test_refuse_existing(self):
  m=json.loads(A.MAP.read_text());name=m['files'][0]['former'];p=A.SOURCES/name
  self.assertFalse(p.exists(), 'refusing to overwrite or remove a preexisting graph')
  try:
   A.restore(name)
   with self.assertRaises(FileExistsError):A.restore(name)
  finally:p.unlink(missing_ok=True)
if __name__=='__main__':unittest.main()
