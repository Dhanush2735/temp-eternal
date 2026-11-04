import copy,unittest
import apply_2539_2490_bce_boat as m
class Tests(unittest.TestCase):
 def setUp(self):self.man=m.load(m.M);m.validate(self.man);self.us=self.man['updates'];self.d={'events':[copy.deepcopy(self.us[0]['before'])]}
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.d,self.us),self.us,True),self.d)
 def test_changed_before(self):
  d=copy.deepcopy(self.d);d['events'][0]['name']='other'
  with self.assertRaises(ValueError):m.transform(d,self.us)
 def test_duplicate(self):
  d={'events':self.d['events']*2}
  with self.assertRaises(ValueError):m.transform(d,self.us)
 def test_reverse_guard(self):
  d=m.transform(self.d,self.us);d['events'][0]['name']='other'
  with self.assertRaises(ValueError):m.transform(d,self.us,True)
 def test_hash(self):
  d=copy.deepcopy(self.man);d['updates'][0]['after']['name']='other'
  with self.assertRaises(ValueError):m.validate(d)
 def test_no_first_claim(self):
  a=self.us[0]['after'];self.assertIn('earlier examples',a['name']);self.assertEqual((a['kind'],a['effect']),('cultural','note'))
 def test_id_and_location_stable(self):
  u=self.us[0]
  for k in ('id','start','end','lat','lon','radiusKm'):self.assertEqual(u['before'][k],u['after'][k])
if __name__=='__main__':unittest.main()
