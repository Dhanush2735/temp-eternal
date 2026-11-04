import copy,unittest
import apply_2539_2490_bce_context as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man)
  self.wp='events_wikipedia.json.gz';self.reg='events_wikipedia_regional.json.gz'
  self.us=self.man['updates'];self.add=self.man['additions']
 def doc(self,p):return {'events':[copy.deepcopy(u['before']) for u in self.us if u['pack']==p]}
 def sub(self,p):return [u for u in self.us if u['pack']==p],[a for a in self.add if a['pack']==p]
 def test_both_roundtrips(self):
  for p in (self.wp,self.reg):
   us,ads=self.sub(p);d=self.doc(p);o=m.transform(d,us,False,ads);self.assertEqual(m.transform(o,us,True,ads),d)
 def test_manifest_hash_guard(self):
  z=copy.deepcopy(self.man);z['updates'][0]['after']['lat']=0
  with self.assertRaises(ValueError):m.validate(z)
 def test_missing_source(self):
  us,ads=self.sub(self.wp)
  with self.assertRaises(ValueError):m.transform({'events':[]},us,False,ads)
 def test_changed_source(self):
  d=self.doc(self.wp);d['events'][0]['name']='changed';us,ads=self.sub(self.wp)
  with self.assertRaises(ValueError):m.transform(d,us,False,ads)
 def test_duplicate_addition(self):
  d=self.doc(self.reg);d['events'].append(copy.deepcopy(self.add[0]['event']));us,ads=self.sub(self.reg)
  with self.assertRaises(ValueError):m.transform(d,us,False,ads)
 def test_reverse_guards_changed_addition(self):
  us,ads=self.sub(self.reg);d=m.transform(self.doc(self.reg),us,False,ads);d['events'][-1]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,us,True,ads)
 def test_input_unchanged(self):
  d=self.doc(self.wp);original=copy.deepcopy(d);us,ads=self.sub(self.wp);m.transform(d,us,False,ads);self.assertEqual(d,original)
 def test_review_qualifications(self):
  byid={u['event_id']:u['after'] for u in self.us};a=byid['wpy_c21a706004'];self.assertEqual((a['lat'],a['lon'],a['kind'],a['effect']),(55.63139,31.54111,'cultural','note'))
  for i in ('wpy_403d82cc80','wpr_50ec0003ce'):self.assertEqual((byid[i]['kind'],byid[i]['effect']),('cultural','note'));self.assertIn('legend',byid[i]['name'])
 def test_ids_stable(self):
  for u in self.us:self.assertEqual(u['before']['id'],u['after']['id'])
 def test_new_context_uncertainty(self):
  a=self.add[0]['event'];self.assertIn('approximate',a['name']);self.assertEqual((a['kind'],a['effect']),('cultural','note'));self.assertIn('not evidence',a['r2SourceEvidence']['review_note'])
if __name__=='__main__':unittest.main()
