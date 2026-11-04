import copy,json,unittest
import apply_3000_aegean_sydney as b

class AegeanSydneyTest(unittest.TestCase):
 def setUp(self):
  self.m=json.loads(b.MANIFEST.read_text(encoding='utf8'));self.up=self.m['updates'][0];self.ad=self.m['additions'][0]
  self.doc={'events':[{'id':'other'},copy.deepcopy(self.up['before'])]}
 def test_roundtrip(self):
  out=b.transform(self.doc,[self.up],[self.ad]);self.assertEqual(b.transform(out,[self.up],[self.ad],True),self.doc)
 def test_no_mutating_dates(self):
  u=copy.deepcopy(self.up);u['after']['start']=-3200
  with self.assertRaises(ValueError):b.transform(self.doc,[u],[])
 def test_existing_id_must_be_unique(self):
  d=copy.deepcopy(self.doc);d['events'].append(copy.deepcopy(self.up['before']))
  with self.assertRaises(ValueError):b.transform(d,[self.up],[])
 def test_new_record_coordinates_locked(self):
  a=copy.deepcopy(self.ad);a['event']['lat']=0
  with self.assertRaises(ValueError):b.transform(self.doc,[self.up],[a])
 def test_cannot_readd_or_rollback_modified(self):
  o=b.transform(self.doc,[self.up],[self.ad]);o['events'][-1]['name']='modified'
  with self.assertRaises(ValueError):b.transform(o,[self.up],[self.ad],True)
