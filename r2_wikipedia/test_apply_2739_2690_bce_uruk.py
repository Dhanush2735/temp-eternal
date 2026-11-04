import copy,unittest
import apply_2739_2690_bce_uruk as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.us=self.man['updates'];self.doc={'events':[copy.deepcopy(self.us[0]['before'])]}
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.doc,self.us),self.us,True),self.doc)
 def test_input_immutable(self):
  d=copy.deepcopy(self.doc);m.transform(self.doc,self.us);self.assertEqual(self.doc,d)
 def test_missing(self):
  with self.assertRaises(ValueError):m.transform({'events':[]},self.us)
 def test_duplicate(self):
  d=copy.deepcopy(self.doc);d['events'].append(copy.deepcopy(d['events'][0]))
  with self.assertRaises(ValueError):m.transform(d,self.us)
 def test_stale_before(self):
  d=copy.deepcopy(self.doc);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.us)
 def test_stale_after(self):
  d=m.transform(self.doc,self.us);d['events'][0]['effect']='military_presence'
  with self.assertRaises(ValueError):m.transform(d,self.us,True)
 def test_hash_guard(self):
  d=copy.deepcopy(self.man);d['updates'][0]['after']['lat']=0
  with self.assertRaises(ValueError):m.validate(d)
 def test_reference_retained(self):
  u=self.us[0]
  for k in ('id','start','end','lat','lon','radiusKm'):self.assertEqual(u['before'][k],u['after'][k])
 def test_qualified_note(self):
  a=self.us[0]['after'];self.assertEqual((a['kind'],a['effect']),('cultural','note'));self.assertIn('uncertain',a['name']);self.assertIn('arbitrary game reference',a['r2SourceEvidence']['review_note']);self.assertGreaterEqual(len(a['r2SourceEvidence']['sources']),5)
if __name__=='__main__':unittest.main()
