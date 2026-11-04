import copy,unittest
import apply_2939_2890_bce_context as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.us=self.man['updates'];self.doc={'events':[copy.deepcopy(u['before']) for u in self.us]}
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.doc,self.us),self.us,True),self.doc)
 def test_immutable(self):
  d=copy.deepcopy(self.doc);m.transform(self.doc,self.us);self.assertEqual(self.doc,d)
 def test_missing(self):
  with self.assertRaises(ValueError):m.transform({'events':[]},self.us)
 def test_duplicate(self):
  d=copy.deepcopy(self.doc);d['events'].append(copy.deepcopy(d['events'][0]))
  with self.assertRaises(ValueError):m.transform(d,self.us)
 def test_stale_before(self):
  d=copy.deepcopy(self.doc);d['events'][1]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.us)
 def test_stale_after(self):
  d=m.transform(self.doc,self.us);d['events'][0]['end']=0
  with self.assertRaises(ValueError):m.transform(d,self.us,True)
 def test_manifest_guard(self):
  d=copy.deepcopy(self.man);d['updates'][0]['after']['end']=0
  with self.assertRaises(ValueError):m.validate(d)
 def test_both_slices(self):
  for u in self.us:
   a,b=u['after'],u['before'];self.assertEqual((a['id'],a['start'],a['end']),(b['id'],-3000,-2889));self.assertEqual((a['lat'],a['lon'],a['kind'],a['effect']),(b['lat'],b['lon'],b['kind'],b['effect']))
   self.assertTrue(all(a['start']<=-y<a['end'] for y in range(2890,2940)))
 def test_caveats(self):
  for u in self.us:
   a=u['after'];self.assertIn('approximate',a['name']);self.assertIn('not ',a['r2SourceEvidence']['review_note']);self.assertGreaterEqual(len(a['r2SourceEvidence']['sources']),2)
if __name__=='__main__':unittest.main()
