import gzip,json,sqlite3,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import place_candidates

class PlaceGuardTests(unittest.TestCase):
 def test_guard_blocks_import_and_network(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);args=['place_candidates.py','--db',str(p/'p.sqlite3'),'--input',str(p/'missing.gz'),'--output',str(p/'out.gz'),'--max-check','1']
   with patch.object(sys,'argv',args),patch.object(place_candidates,'within_budget',return_value=(False,125000000)),patch.object(place_candidates.Api,'get',side_effect=AssertionError('network must not be called')):
    place_candidates.main()
   with sqlite3.connect(p/'p.sqlite3') as db:self.assertEqual(db.execute('select count(*) from places').fetchone()[0],0)
   with gzip.open(p/'out.gz','rt') as f:self.assertEqual(f.read(),'')
if __name__=='__main__':unittest.main()
