import copy,json,unittest
import correct_stonehenge_wording as s

class StonehengeWordingTest(unittest.TestCase):
 def setUp(self):
  self.m=json.loads(s.MANIFEST.read_text(encoding='utf8'))
  self.doc={'events':[{'id':'unrelated'},copy.deepcopy(self.m['before'])],'sites':[]}
 def test_forward_and_rollback_preserve_everything_else(self):
  revised=s.transform(self.doc,self.m)
  self.assertEqual(revised['events'][0],self.doc['events'][0])
  self.assertEqual(s.transform(revised,self.m,True),self.doc)
 def test_changed_year_or_coordinates_rejected(self):
  m=copy.deepcopy(self.m);m['after']['start']=-3100
  with self.assertRaises(ValueError):s.transform(self.doc,m)
  m=copy.deepcopy(self.m);m['after']['lat']=0
  with self.assertRaises(ValueError):s.transform(self.doc,m)
 def test_duplicate_or_modified_original_rejected(self):
  doc=copy.deepcopy(self.doc);doc['events'].append(copy.deepcopy(self.m['before']))
  with self.assertRaises(ValueError):s.transform(doc,self.m)
  doc=copy.deepcopy(self.doc);doc['events'][1]['name']='modified'
  with self.assertRaises(ValueError):s.transform(doc,self.m)
