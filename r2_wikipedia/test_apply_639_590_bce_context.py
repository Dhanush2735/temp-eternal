import copy,unittest
import apply_639_590_bce_context as m
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
  changed={'q913818','q1288667','q633560','q2401276','q1252915','q55633156'}
  for u in self.us:
   if u['event_id'] not in changed:
    for k in ('start','end'):self.assertEqual(u['before'][k],u['after'][k])
 def test_prior_evidence_preserved(self):
  for u in self.us:
   if 'r2SourceEvidence' in u['before']:self.assertEqual(u['before']['r2SourceEvidence'],u['after']['r2SourceEvidence'])
 def test_evidence(self):
  for u in self.us:self.assertTrue(u['after'].get('r2AdditionalEvidence',u['after'].get('r2SourceEvidence'))['sources'])
 def test_world_year_labels_and_reader_caveat(self):
  rows={u['event_id']:u['after'] for u in self.us}
  for id,y in [('q913818',-609),('q1288667',-597),('q633560',-605),('q2401276',-605),('q1252915',-597),('q55633156',-609)]:
   self.assertEqual((rows[id]['start'],rows[id]['end'],rows[id]['effect']),(y,y+1,'military_presence'));self.assertIn('inclusive in NewsIndex',rows[id]['r2SourceEvidence']['review_note'])
 def test_napata_reference(self):
  rows={u['event_id']:u['after'] for u in self.us};e=rows['wpy_7bca3cb7fd'];self.assertEqual((e['lat'],e['lon']),(18.53,31.84));self.assertEqual(e['effect'],'military_presence')
 def test_esahaddon_misplaced(self):
  rows={u['event_id']:u['after'] for u in self.us};self.assertEqual(rows['wpy_dc6dbad200']['effect'],'note');self.assertIn('671 BC',rows['wpy_dc6dbad200']['name'])
 def test_additions_not_disasters(self):
  for a in self.man['additions']:self.assertEqual((a['event']['kind'],a['event']['effect']),('cultural','note'))
 def test_addition_roundtrip(self):
  add=self.man['additions'];d={'events':[]};o=m.transform(d,[],False,add);self.assertEqual(m.transform(o,[],True,add),d)
if __name__=='__main__':unittest.main()
