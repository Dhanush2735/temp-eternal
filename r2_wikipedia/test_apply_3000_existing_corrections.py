import copy,json,unittest
import apply_3000_existing_corrections as b
class CorrectionsTest(unittest.TestCase):
 def setUp(self):
  self.us=json.loads(b.MANIFEST.read_text(encoding='utf8'))['updates'];self.doc={'events':[copy.deepcopy(u['before']) for u in self.us]+[{'id':'other'}]}
 def test_roundtrip(self):
  a=b.transform(self.doc,self.us);self.assertEqual(self.doc,b.transform(a,self.us,True))
 def test_duplicate_ids(self):
  with self.assertRaises(ValueError):b.transform(self.doc,[self.us[0],self.us[0]])
 def test_missing_id(self):
  with self.assertRaises(ValueError):b.transform({'events':[]},self.us)
 def test_reject_changed_original(self):
  d=copy.deepcopy(self.doc);d['events'][0]['name']='edited'
  with self.assertRaises(ValueError):b.transform(d,self.us)
 def test_reject_wrong_new_date_coordinate_or_effect(self):
  for key,val in [('start',-3000),('lat',0),('effect','political')]:
   u=copy.deepcopy(self.us[0]);u['after'][key]=val
   with self.assertRaises(ValueError):b.transform(self.doc,[u])
 def test_input_not_mutated(self):
  d=copy.deepcopy(self.doc);b.transform(self.doc,self.us);self.assertEqual(self.doc,d)
 def test_modified_rollback_rejected(self):
  d=b.transform(self.doc,self.us);d['events'][0]['name']='edited'
  with self.assertRaises(ValueError):b.transform(d,self.us,True)
