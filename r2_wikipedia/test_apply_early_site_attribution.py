import copy,json,unittest
import apply_early_site_attribution as b
class SiteCorrectionsTest(unittest.TestCase):
 def setUp(self):
  self.us=json.loads(b.MANIFEST.read_text(encoding='utf8'))['updates'];self.d={'sites':[copy.deepcopy(u['before']) for u in self.us]+[{'id':'untouched'}]}
 def test_roundtrip(self):
  out=b.transform(self.d,self.us);self.assertEqual(self.d,b.transform(out,self.us,True))
 def test_duplicate_rejected(self):
  with self.assertRaises(ValueError):b.transform(self.d,[self.us[0],self.us[0]])
 def test_old_record_changed_rejected(self):
  d=copy.deepcopy(self.d);d['sites'][0]['rank']='city'
  with self.assertRaises(ValueError):b.transform(d,self.us)
 def test_changed_dates_or_hints_rejected(self):
  for field,val in [('occupiedStart',-5000),('civHint','sumer'),('lat',0)]:
   u=copy.deepcopy(self.us[0]);u['after'][field]=val
   with self.assertRaises(ValueError):b.transform(self.d,[u])
 def test_rollback_changed_rejected(self):
  out=b.transform(self.d,self.us);out['sites'][0]['civHint']='other'
  with self.assertRaises(ValueError):b.transform(out,self.us,True)
 def test_input_unchanged(self):
  d=copy.deepcopy(self.d);b.transform(self.d,self.us);self.assertEqual(d,self.d)
