import copy,json,unittest
import apply_3000_world as b
class World3000Test(unittest.TestCase):
 def setUp(self):
  self.adds=json.loads(b.MANIFEST.read_text(encoding='utf8'))['additions'];self.doc={'events':[{'id':'other'}]}
 def test_roundtrip(self):
  out=b.transform(self.doc,self.adds);self.assertEqual(b.transform(out,self.adds,True),self.doc)
 def test_no_duplicate_addition(self):
  with self.assertRaises(ValueError):b.transform(self.doc,[self.adds[0],self.adds[0]])
 def test_readd_rejected(self):
  out=b.transform(self.doc,self.adds)
  with self.assertRaises(ValueError):b.transform(out,self.adds)
 def test_modified_rollback_rejected(self):
  out=b.transform(self.doc,self.adds);out['events'][1]['name']='changed'
  with self.assertRaises(ValueError):b.transform(out,self.adds,True)
 def test_locked_date_and_location(self):
  for key,value in [('start',-3200),('lat',0),('confidence','wikipedia_region')]:
   bad=copy.deepcopy(self.adds[0]);bad['event'][key]=value
   with self.assertRaises(ValueError):b.transform(self.doc,[bad])
 def test_no_mutation(self):
  before=copy.deepcopy(self.doc);b.transform(self.doc,self.adds);self.assertEqual(self.doc,before)
