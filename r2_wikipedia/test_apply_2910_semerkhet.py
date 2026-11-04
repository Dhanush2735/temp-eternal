import copy,json,unittest
import apply_2910_semerkhet as d
class SemerkhetDeathTest(unittest.TestCase):
 def setUp(self):self.m=json.loads(d.M.read_text());self.e=self.m['event']
 def test_roundtrip(self):
  a={'events':[{'id':'existing'}]};b=d.transform(a,self.e);self.assertEqual(d.transform(b,self.e,True),a)
 def test_duplicate(self):
  with self.assertRaises(ValueError):d.transform({'events':[self.e]},self.e)
 def test_modified_rollback(self):
  row=copy.deepcopy(self.e);row['name']='modified'
  with self.assertRaises(ValueError):d.transform({'events':[row]},self.e,True)
 def test_bad_coordinates(self):
  m=copy.deepcopy(self.m);m['event']['lat']=0
  with self.assertRaises(ValueError):d.validate(m)
 def test_uncertainty_required(self):
  m=copy.deepcopy(self.m);m['event']['name']='Semerkhet died in 2910'
  with self.assertRaises(ValueError):d.validate(m)
