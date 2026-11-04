import copy,unittest
import apply_2994_2990_bce_ravi as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.us=self.man['updates'];self.u=self.us[0];self.doc={'events':[copy.deepcopy(self.u['before'])]}
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
  d=m.transform(self.doc,self.us);d['events'][0]['end']=0
  with self.assertRaises(ValueError):m.transform(d,self.us,True)
 def test_guard_hash(self):
  d=copy.deepcopy(self.man);d['updates'][0]['after']['end']=0
  with self.assertRaises(ValueError):m.validate(d)
 def test_harappa_slice(self):
  a=self.u['after'];b=self.u['before'];self.assertEqual((a['id'],a['start'],a['end']),(b['id'],-3000,-2799));self.assertEqual((a['lat'],a['lon'],a['kind'],a['effect']),(b['lat'],b['lon'],b['kind'],b['effect']))
  self.assertTrue(all(a['start']<=-y<a['end'] for y in (2994,2993,2992,2991,2990,2800)));self.assertNotIn(-2799,range(a['start'],a['end']))
 def test_caveat_and_sources(self):
  e=self.u['after']['r2SourceEvidence'];self.assertIn('not prove',e['review_note']);self.assertTrue(any('unesco' in s for s in e['sources']));self.assertIn('approximate',self.u['after']['name'])
if __name__=='__main__':unittest.main()
