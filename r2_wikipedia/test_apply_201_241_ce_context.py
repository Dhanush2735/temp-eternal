import copy,unittest
import apply_201_241_ce_context as m
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
 def test_chengdu_location(self):
  a=next(x['after'] for x in self.u if x['event_id']=='wpy_5c91c61bc9');self.assertEqual((a['lat'],a['lon']),(30.66,104.06333))
 def test_hatra_location(self):
  a=next(x['after'] for x in self.u if x['event_id']=='wpr_ca33c17f88');self.assertEqual((a['lat'],a['lon'],a['effect']),(35.58806,42.71833,'note'))
 def test_flood_references(self):
  a=next(x['after'] for x in self.u if x['event_id']=='wpy_dc2676522e');b=next(x['after'] for x in self.u if x['event_id']=='wpy_3edb64d853');self.assertEqual(a['effect'],'disruption');self.assertEqual(b['effect'],'note')
 def test_chronology_uncertain(self):
  for i in ('wpy_8a6e372a90','wpy_227942b864','q19839899'):
   a=next(x['after'] for x in self.u if x['event_id']==i);self.assertEqual(a['effect'],'note')
 def test_no_hazard_pack_changes(self):
  self.assertFalse(any(x['pack']=='events_hazards.json.gz' for x in self.u))
if __name__=='__main__':unittest.main()
