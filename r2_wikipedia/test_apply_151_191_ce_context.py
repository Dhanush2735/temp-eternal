import copy,unittest
import apply_151_191_ce_context as m
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
 def test_taupo_superseded_date_no_disruption(self):
  for id in ('wpy_8dc20e7b79','wpy_66951aa56c','wpy_1e0b00243a'):
   a=next(x['after'] for x in self.u if x['event_id']==id);self.assertEqual(a['effect'],'note');self.assertLess(a['lat'],0)
 def test_elegeia_not_iraq(self):
  a=next(x['after'] for x in self.u if x['event_id']=='wpy_4be7ae58ee');self.assertEqual((a['lat'],a['lon'],a['end']),(39.9472366,41.1199969,163));self.assertEqual(a['effect'],'note')
 def test_carthage_not_scillium(self):
  a=next(x['after'] for x in self.u if x['event_id']=='wpy_88e853b0cf');self.assertEqual((a['lat'],a['lon']),(36.8528,10.3233))
 def test_no_hazard_pack_changes(self):
  self.assertFalse(any(x['pack']=='events_hazards.json.gz' for x in self.u))
 def test_uncertain_year_battle_is_note(self):
  a=next(x['after'] for x in self.u if x['event_id']=='q603598');self.assertEqual((a['end'],a['effect']),(193,'note'))
if __name__=='__main__':unittest.main()
