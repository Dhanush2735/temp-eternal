import tempfile,sqlite3,unittest
from pathlib import Path
from unittest.mock import patch
import park_staging_databases as P
class ParkTests(unittest.TestCase):
 def test_roundtrip_exact_and_no_overwrite(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);(root/'focus').mkdir();db=root/'crawl.sqlite3';c=sqlite3.connect(db);c.execute('create table sample(x)');c.execute('insert into sample values (42)');c.commit();c.close();before=db.read_bytes()
   with patch.object(P,'ROOT',root),patch.object(P,'MAP',root/'focus/manifest.json'):
    P.park('crawl.sqlite3');self.assertFalse(db.exists());P.unpack('crawl.sqlite3');self.assertEqual(db.read_bytes(),before)
    with self.assertRaises(FileExistsError):P.unpack('crawl.sqlite3')
 def test_actual_archives_verified_without_restoring(self):
  with tempfile.TemporaryDirectory() as t:
   for name in P.NAMES:
    path=P.unpack(name,Path(t)/name);self.assertTrue(path.exists())
if __name__=='__main__':unittest.main()
