import copy,unittest
import apply_101_141_ce_context as m
class TestEdits(unittest.TestCase):
 def setUp(self): self.man=m.load(m.M);m.validate(self.man);self.u=self.man['updates'];self.d={'events':[copy.deepcopy(x['before']) for x in self.u]}
 def test_roundtrip(self): self.assertEqual(m.transform(m.transform(self.d,self.u),self.u,True),self.d)
 def test_input_unchanged(self):
  d=copy.deepcopy(self.d);m.transform(d,self.u);self.assertEqual(d,self.d)
 def test_conflict(self):
  d=copy.deepcopy(self.d);d['events'][0]['name']='other'
  with self.assertRaises(ValueError):m.transform(d,self.u)
 def test_duplicate(self):
  d=copy.deepcopy(self.d);d['events'].append(copy.deepcopy(d['events'][0]))
  with self.assertRaises(ValueError):m.transform(d,self.u)
 def test_missing(self):
  d=copy.deepcopy(self.d);d['events'].pop()
  with self.assertRaises(ValueError):m.transform(d,self.u)
 def test_manifest_tamper(self):
  x=copy.deepcopy(self.man);x['updates'][0]['after']['start']=0
  with self.assertRaises(ValueError):m.validate(x)
 def test_false_battle(self):
  a=next(x['after'] for x in self.u if x['event_id']=='wpr_36f157eff6');self.assertEqual((a['kind'],a['effect']),('cultural','note'))
 def test_wall_in_england(self):
  a=next(x['after'] for x in self.u if x['event_id']=='wpd_b3bb21a512');self.assertEqual((a['lat'],a['lon']),(55.017,-2.283))
 def test_uncertain_earthquake_non_disruptive(self):
  a=next(x['after'] for x in self.u if x['event_id']=='q19903045');self.assertEqual((a['kind'],a['effect']),('incident','note'))
 def test_earthquake_effects_in_other_packs_not_touched(self):
  self.assertFalse(any(x['pack']=='events_hazards.json.gz' for x in self.u))
 def test_pliny_one_office_not_two_claimed_appointments(self):
  for id in ('wpr_a0068d1db3','wpr_07fa8d80b7'):
   a=next(x['after'] for x in self.u if x['event_id']==id);self.assertEqual(a['effect'],'note');self.assertEqual(a['confidence'],'conflicting_dates')
if __name__=='__main__':unittest.main()
