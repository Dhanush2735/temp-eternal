import copy,json,unittest
import apply_morocco_sumer as b
class MoroccoSumerTest(unittest.TestCase):
 def setUp(self):
  self.m=json.loads(b.MANIFEST.read_text(encoding='utf8'));self.u=self.m['updates'][0];self.s=self.m['updates'][1];self.a=self.m['additions'][0]
 def test_event_update_roundtrip(self):
  d={'events':[copy.deepcopy(self.u['before']),{'id':'other'}]};o=b.transform(d,'events',[self.u],[]);self.assertEqual(b.transform(o,'events',[self.u],[],True),d)
 def test_site_roundtrip(self):
  d={'sites':[copy.deepcopy(self.s['before'])]};o=b.transform(d,'sites',[self.s],[]);self.assertEqual(b.transform(o,'sites',[self.s],[],True),d)
 def test_addition_roundtrip(self):
  d={'events':[{'id':'other'}]};o=b.transform(d,'events',[],[self.a]);self.assertEqual(b.transform(o,'events',[],[self.a],True),d)
 def test_bad_field_rejected(self):
  u=copy.deepcopy(self.s);u['after']['occupiedEnd']=0
  with self.assertRaises(ValueError):b.transform({'sites':[self.s['before']]},'sites',[u],[])
 def test_bad_new_location_rejected(self):
  a=copy.deepcopy(self.a);a['record']['lat']=0
  with self.assertRaises(ValueError):b.transform({'events':[]},'events',[],[a])
 def test_existing_or_modified_new_rejected(self):
  d={'events':[]};o=b.transform(d,'events',[],[self.a])
  with self.assertRaises(ValueError):b.transform(o,'events',[],[self.a])
  o['events'][0]['name']='changed'
  with self.assertRaises(ValueError):b.transform(o,'events',[],[self.a],True)
 def test_changed_original_rejected(self):
  row=copy.deepcopy(self.u['before']);row['name']='other'
  with self.assertRaises(ValueError):b.transform({'events':[row]},'events',[self.u],[])
