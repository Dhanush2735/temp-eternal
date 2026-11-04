import copy,unittest
import apply_689_640_bce_context as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.us=self.man['updates'];self.doc={'events':[copy.deepcopy(u['before']) for u in self.us]}
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
 def test_stable_fields(self):
  for u in self.us:
   for k in ('start','end'):
    if u['event_id'] not in ('q6646260','wpy_3523a44f0d','wpd_3abccb2ba6'):self.assertEqual(u['before'][k],u['after'][k])
 def test_prior_evidence_preserved(self):
  for u in self.us:
   if 'r2SourceEvidence' in u['before']:self.assertEqual(u['before']['r2SourceEvidence'],u['after']['r2SourceEvidence']);self.assertIn('r2AdditionalEvidence',u['after'])
 def test_all_cultural_notes(self):
  for u in self.us:
   if u['event_id']!='q6646260':self.assertEqual((u['after']['kind'],u['after']['effect']),('cultural','note'))
   else:self.assertEqual(u['after']['effect'],'military_presence')
 def test_date_and_world_pack_boundaries(self):
  events={u['event_id']:u['after'] for u in self.us};e=events['q6646260'];self.assertEqual((e['start'],e['end']),(-689,-688));self.assertIn('inclusive for NewsIndex',e['r2SourceEvidence']['review_note'])
 def test_thebes_geography_and_chronology(self):
  events={u['event_id']:u['after'] for u in self.us};e=events['wpy_3523a44f0d'];self.assertEqual((e['start'],e['lat'],e['lon']),(-663,25.72056,32.61028))
 def test_nitocris_and_jin_context(self):
  self.assertEqual({x['event']['id'] for x in self.man['additions']},{'r2_liji_657_context','r2_nitocris_656_context'})
 def test_additions_not_disasters(self):
  for a in self.man['additions']:self.assertEqual((a['event']['kind'],a['event']['effect']),('cultural','note'))
 def test_addition_roundtrip(self):
  add=self.man['additions'];d={'events':[]};o=m.transform(d,[],False,add);self.assertEqual(m.transform(o,[],True,add),d)
if __name__=='__main__':unittest.main()
