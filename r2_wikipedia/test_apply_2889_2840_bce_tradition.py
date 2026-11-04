import copy, unittest
import apply_2889_2840_bce_tradition as m
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
  d=copy.deepcopy(self.doc);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.us)
 def test_stale_after(self):
  d=m.transform(self.doc,self.us);d['events'][1]['effect']='political'
  with self.assertRaises(ValueError):m.transform(d,self.us,True)
 def test_hash_guard(self):
  d=copy.deepcopy(self.man);d['updates'][0]['after']['lat']=0
  with self.assertRaises(ValueError):m.validate(d)
 def test_stable_identifiers_dates_locations(self):
  for u in self.us:
   a,b=u['after'],u['before']
   for k in ('id','start','end','lat','lon','radiusKm'):self.assertEqual(a[k],b[k])
   self.assertEqual((a['kind'],a['effect']),('cultural','note'))
 def test_uncertainty_sources(self):
  for u in self.us:
   a=u['after'];self.assertTrue('legendary' in a['name']);self.assertIn('not evidence',a['r2SourceEvidence']['review_note']);self.assertEqual(len(a['r2SourceEvidence']['sources']),3)
 def test_per_pack_roundtrip(self):
  for u in self.us:
   d={'events':[u['before']]};self.assertEqual(m.transform(m.transform(d,[u]),[u],True),d)
if __name__=='__main__':unittest.main()
