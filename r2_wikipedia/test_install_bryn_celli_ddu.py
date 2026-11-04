import copy,json,unittest
import install_bryn_celli_ddu as b

class NewEventTest(unittest.TestCase):
 def setUp(self):
  self.m=json.loads(b.MANIFEST.read_text(encoding='utf8'));self.d={'events':[{'id':'other'}],'sites':[]}
 def test_install_and_logical_rollback(self):
  o=b.transform(self.d,self.m);self.assertEqual(b.transform(o,self.m,True),self.d)
 def test_duplicate_rejected(self):
  d=b.transform(self.d,self.m)
  with self.assertRaises(ValueError):b.transform(d,self.m)
 def test_wrong_date_rejected(self):
  m=copy.deepcopy(self.m);m['event']['start']=-3100
  with self.assertRaises(ValueError):b.transform(self.d,m)
 def test_changed_installed_row_cannot_rollback(self):
  d=b.transform(self.d,self.m);d['events'][-1]['name']='different'
  with self.assertRaises(ValueError):b.transform(d,self.m,True)
