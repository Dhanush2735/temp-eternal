import copy,json,unittest
import apply_1_41_ce_context as m
class TestEdits(unittest.TestCase):
 def setUp(self):self.man=m.load(m.M);m.validate(self.man);self.u=self.man['updates'];self.d={'events':[copy.deepcopy(x['before']) for x in self.u]}
 def test_round_trip(self):self.assertEqual(m.transform(m.transform(self.d,self.u),self.u,True),self.d)
 def test_original_unchanged(self):
  d=copy.deepcopy(self.d);m.transform(d,self.u);self.assertEqual(d,self.d)
 def test_bad_before_rejected(self):
  d=copy.deepcopy(self.d);d['events'][0]['name']='unexpected'
  with self.assertRaises(ValueError):m.transform(d,self.u)
 def test_duplicate_rejected(self):
  d=copy.deepcopy(self.d);d['events'].append(copy.deepcopy(d['events'][0]))
  with self.assertRaises(ValueError):m.transform(d,self.u)
 def test_missing_rejected(self):
  d=copy.deepcopy(self.d);d['events'].pop()
  with self.assertRaises(ValueError):m.transform(d,self.u)
 def test_manifest_tamper_rejected(self):
  x=copy.deepcopy(self.man);x['updates'][0]['after']['start']=0
  with self.assertRaises(ValueError):m.validate(x)
 def test_daeso_non_military(self):
  x=next(u['after'] for u in self.u if u['event_id']=='wpy_b2b6d51455');self.assertEqual(x['effect'],'note');self.assertEqual((x['start'],x['end']),(21,23))
if __name__=='__main__':unittest.main()
