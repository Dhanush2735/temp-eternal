import copy, unittest
import apply_3000_djet_officials as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.u=self.man['updates'];self.b=self.u[0]['before'];self.a=self.u[0]['after'];self.doc={'events':[copy.deepcopy(self.b)]}
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.doc,self.u),self.u,True),self.doc)
 def test_unchanged(self):
  m.transform(self.doc,self.u);self.assertEqual(self.doc,{'events':[self.b]})
 def test_duplicate(self):
  with self.assertRaises(ValueError):m.transform({'events':[self.b,self.b]},self.u)
 def test_missing(self):
  with self.assertRaises(ValueError):m.transform({'events':[]},self.u)
 def test_stale(self):
  d=copy.deepcopy(self.doc);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.u)
 def test_reverse_stale(self):
  d=m.transform(self.doc,self.u);d['events'][0]['start']=0
  with self.assertRaises(ValueError):m.transform(d,self.u,True)
 def test_hash_guard(self):
  d=copy.deepcopy(self.man);d['updates'][0]['after']['lat']=0
  with self.assertRaises(ValueError):m.validate(d)
 def test_data_unchanged(self):
  for k in ('id','start','end','lat','lon','radiusKm','kind','effect'):self.assertEqual(self.a[k],self.b[k])
 def test_sources_and_caveat(self):
  self.assertIn('not establish',self.a['r2SourceEvidence']['review_note']);self.assertIn('Amka',self.a['name']);self.assertIn('Sekhemkasedj',self.a['name']);self.assertGreaterEqual(len(self.a['r2SourceEvidence']['sources']),6)
if __name__=='__main__':unittest.main()
