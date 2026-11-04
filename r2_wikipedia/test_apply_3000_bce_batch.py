import copy,json,unittest
import apply_3000_bce_batch as b

class BatchTest(unittest.TestCase):
 def setUp(self):
  self.m=json.loads(b.MANIFEST.read_text(encoding='utf8'));self.u=self.m['updates'][0];self.d={'events':[{'id':'other'},copy.deepcopy(self.u['before'])]}
 def test_forward_reverse(self):
  o=b.transform(self.d,[self.u]);self.assertEqual(o['events'][0],self.d['events'][0]);self.assertEqual(b.transform(o,[self.u],True),self.d)
 def test_cannot_change_year(self):
  u=copy.deepcopy(self.u);u['after']['start']=-3100
  with self.assertRaises(ValueError):b.transform(self.d,[u])
 def test_duplicate_rejected(self):
  d=copy.deepcopy(self.d);d['events'].append(copy.deepcopy(self.u['before']))
  with self.assertRaises(ValueError):b.transform(d,[self.u])
 def test_bad_coordinate_rejected(self):
  u=copy.deepcopy(self.u);u['after']['lat']=100
  with self.assertRaises(ValueError):b.transform(self.d,[u])
