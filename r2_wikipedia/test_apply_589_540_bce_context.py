import copy,unittest
import apply_589_540_bce_context as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.us=self.man['updates'];self.doc={'events':[copy.deepcopy(u['before']) for u in self.us]};self.rows={u['event_id']:u['after'] for u in self.us}
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.doc,self.us),self.us,True),self.doc)
 def test_no_mutation(self):
  d=copy.deepcopy(self.doc);m.transform(self.doc,self.us);self.assertEqual(self.doc,d)
 def test_missing(self):
  with self.assertRaises(ValueError):m.transform({'events':[]},self.us)
 def test_changed(self):
  d=copy.deepcopy(self.doc);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.us)
 def test_duplicate(self):
  d=copy.deepcopy(self.doc);d['events'].append(copy.deepcopy(self.us[0]['before']))
  with self.assertRaises(ValueError):m.transform(d,self.us)
 def test_changed_after(self):
  d=m.transform(self.doc,self.us);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.us,True)
 def test_manifest_guard(self):
  d=copy.deepcopy(self.man);d['updates'][0]['after']['lat']=0
  with self.assertRaises(ValueError):m.validate(d)
 def test_stable_ids(self):
  for u in self.us:self.assertEqual(u['before']['id'],u['after']['id'])
 def test_stable_dates(self):
  for u in self.us:
   if u['event_id'] not in ('q1290590','q4870298'):
    for k in ('start','end'):self.assertEqual(u['before'][k],u['after'][k])
 def test_prior_evidence_preserved(self):
  for u in self.us:
   if 'r2SourceEvidence' in u['before']:self.assertEqual(u['before']['r2SourceEvidence'],u['after']['r2SourceEvidence'])
 def test_evidence(self):
  for u in self.us:self.assertTrue(u['after'].get('r2AdditionalEvidence',u['after'].get('r2SourceEvidence'))['sources'])
 def test_an_and_jerusalem(self):
  self.assertEqual((self.rows['q4870298']['start'],self.rows['q4870298']['end']),(-589,-588))
  self.assertEqual((self.rows['q1290590']['start'],self.rows['q1290590']['end']),(-589,-586))
  self.assertIn('inclusive',self.rows['q1290590']['r2SourceEvidence']['review_note'])
 def test_larissa_greece_correction(self):
  for id in ('wpr_7f43ffbf43','wpd_2db01b279c'):
   e=self.rows[id];self.assertEqual((e['lat'],e['lon'],e['effect']),(36.09806,43.32889,'note'))
 def test_traditions_notes(self):
  for id in ('wpr_b8ab016702','wpr_05f3be6db8','wpd_c30d3d3385','wpr_7b69f13997','wpr_ec7592be00'):self.assertEqual(self.rows[id]['effect'],'note')
 def test_santorini_claim_not_active_disruption(self):self.assertEqual(self.rows['wpy_887e5b9841']['effect'],'note')
 def test_disputed_lydia_preserves_dates(self):
  for id in ('q1568965','q890341','q3436155'):self.assertEqual((self.rows[id]['start'],self.rows[id]['end'],self.rows[id]['effect']),(-546,-545,'military_presence'))
if __name__=='__main__':unittest.main()
