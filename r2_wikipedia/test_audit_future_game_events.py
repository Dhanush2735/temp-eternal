import datetime
import gzip
import json
import tempfile
import unittest
from pathlib import Path
from audit_future_game_events import scan

class FutureEventAuditTests(unittest.TestCase):
 def test_classifies_start_year_only_and_preserves_future_row(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'index.json').write_text(json.dumps({'packs':['a.json','b.json.gz']}))
   (p/'a.json').write_text(json.dumps({'events':[{'id':'past','start':2025,'end':2029},{'id':'same','start':2026}, {'id':'future','start':2027,'description':'unverified plan'}]}))
   with gzip.open(p/'b.json.gz','wt') as f:json.dump({'events':[{'id':'missing'},{'id':'text','start':'2028'}, {'id':'boolean','start':True}, {'id':'year-format','year':2030}, {'id':'null-start','start':None,'year':2024}]},f)
   summary,future=scan(p,datetime.date(2026,10,28));c=summary['counts']
   self.assertEqual(c['rows'],8);self.assertEqual(c['earlier_start_year'],2)
   self.assertEqual(c['current_start_year_day_unknown'],1);self.assertEqual(c['future_start_year'],2)
   self.assertEqual(c['missing_or_noninteger_start'],3)
   self.assertEqual(future[1]['date_field'],'year')
   self.assertEqual(future[0]['record']['description'],'unverified plan')
   self.assertEqual(future[0]['pack'],'a.json');self.assertEqual(future[0]['event_index'],2)
   self.assertIn('not verified history',summary['warning'])

if __name__=='__main__':unittest.main()
