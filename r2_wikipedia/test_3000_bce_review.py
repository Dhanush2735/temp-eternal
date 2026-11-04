import gzip,json,tempfile,unittest
from pathlib import Path
import create_3000_bce_review as f

class ReviewSelectionTests(unittest.TestCase):
 def test_locked_source_and_missing_fails_closed(self):
  title='30th century BC';old=f.SELECT
  try:
   f.SELECT={title:{'revision':12,'around_3000':[10]}}
   row={'source':{'title':title,'line':10,'revision_id':12},'id':'id1','raw_wikitext':'c. 3000 BC: something'}
   with tempfile.TemporaryDirectory() as d:
    p=Path(d)/'input.gz'
    with gzip.open(p,'wt',encoding='utf8') as out:out.write(json.dumps(row)+'\n')
    x=f.create(p);self.assertEqual(len(x['records']),1)
    self.assertEqual(x['records'][0]['record_status'],'unreviewed_not_game_ready')
    row['source']['revision_id']=13
    with gzip.open(p,'wt',encoding='utf8') as out:out.write(json.dumps(row)+'\n')
    with self.assertRaises(ValueError):f.create(p)
    with gzip.open(p,'wt',encoding='utf8') as out:pass
    with self.assertRaises(ValueError):f.create(p)
  finally:f.SELECT=old

if __name__=='__main__':unittest.main()
