import copy,unittest
import apply_539_490_bce_hazards as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.small=copy.deepcopy(self.man)
  for n,u in enumerate(self.small['moves']):u['source_index']=n
  self.h={'events':[copy.deepcopy(u['before']) for u in self.small['moves']]};self.r={'events':[]}
 def test_validate(self):m.validate(self.man)
 def test_hash_guard(self):
  x=copy.deepcopy(self.man);x['moves'][0]['after']['lat']=0
  with self.assertRaises(ValueError):m.validate(x)
 def test_hazard_roundtrip(self):self.assertEqual(m.transform(m.transform(self.h,self.small,m.HAZ),self.small,m.HAZ,True),self.h)
 def test_regional_roundtrip(self):self.assertEqual(m.transform(m.transform(self.r,self.small,m.REG),self.small,m.REG,True),self.r)
 def test_immutable(self):
  d=copy.deepcopy(self.h);m.transform(self.h,self.small,m.HAZ);self.assertEqual(self.h,d)
 def test_missing_source(self):
  with self.assertRaises(ValueError):m.transform({'events':[]},self.small,m.HAZ)
 def test_changed_source(self):
  d=copy.deepcopy(self.h);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.small,m.HAZ)
 def test_duplicate_destination(self):
  d={'events':[copy.deepcopy(self.small['moves'][0]['after'])]}
  with self.assertRaises(ValueError):m.transform(d,self.small,m.REG)
 def test_stale_after(self):
  d=m.transform(self.r,self.small,m.REG);d['events'][0]['effect']='disruption'
  with self.assertRaises(ValueError):m.transform(d,self.small,m.REG,True)
 def test_uncertain_dates_and_locations_retained(self):
  for u in self.man['moves']:
   a,b=u['after'],u['before']
   for k in ('id','start','end','lat','lon','radiusKm'):self.assertEqual(a[k],b[k])
   self.assertIn('uncertain',a['name']);self.assertEqual((a['kind'],a['effect']),('cultural','note'))
 def test_one_removed_and_added(self):
  self.assertEqual(m.transform(self.h,self.small,m.HAZ)['events'],[])
  self.assertEqual(len(m.transform(self.r,self.small,m.REG)['events']),2)
if __name__=='__main__':unittest.main()
