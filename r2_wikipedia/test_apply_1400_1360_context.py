import copy,gzip,json,unittest
import apply_1400_1360_context as a
class BatchTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=json.loads(a.gzip.open(a.M,'rt',encoding='utf8').read());cls.docs={}
  with gzip.open(a.H/a.R,'rt') as f:d=json.load(f)
  installed=any(x.get('id')==cls.m['additions'][0]['event']['id'] for x in d['events'])
  for p in (a.W,a.R,a.D):
   with gzip.open(a.H/p,'rt') as f:d=json.load(f)
   cls.docs[p]=a.transform(d,cls.m,p,True) if installed else d
 def test_roundtrip_all_packs(self):
  for p,d in self.docs.items():self.assertEqual(a.transform(a.transform(d,self.m,p),self.m,p,True),d)
 def test_changes_present(self):
  for u in self.m['updates']:
   d=a.transform(self.docs[u['pack']],self.m,u['pack']);self.assertEqual([x for x in d['events'] if x.get('id')==u['event_id']],[u['after']])
 def test_additions_present(self):
  d=a.transform(self.docs[a.R],self.m,a.R)
  for u in self.m['additions']:self.assertEqual([x for x in d['events'] if x.get('id')==u['event']['id']],[u['event']])
 def test_changed_input_rejected(self):
  u=self.m['updates'][0];d=copy.deepcopy(self.docs[u['pack']]);next(x for x in d['events'] if x.get('id')==u['event_id'])['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,u['pack'])
 def test_duplicate_input_rejected(self):
  u=self.m['updates'][0];d=copy.deepcopy(self.docs[u['pack']]);d['events'].append(copy.deepcopy(u['before']))
  with self.assertRaises(ValueError):a.transform(d,self.m,u['pack'])
 def test_duplicate_addition_rejected(self):
  d=copy.deepcopy(self.docs[a.R]);d['events'].append(copy.deepcopy(self.m['additions'][0]['event']))
  with self.assertRaises(ValueError):a.transform(d,self.m,a.R)
 def test_changed_manifest_rejected(self):
  m=copy.deepcopy(self.m);m['updates'][0]['after']['name']='changed'
  with self.assertRaises(ValueError):a.validate(m)
 def test_wrong_rollback_rejected(self):
  d=a.transform(self.docs[a.R],self.m,a.R);u=self.m['additions'][0];next(x for x in d['events'] if x.get('id')==u['event']['id'])['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,a.R,True)
 def test_index(self):
  with gzip.open(a.H/a.R,'rt') as f:d=json.load(f)
  installed=any(x.get('id')==self.m['additions'][0]['event']['id'] for x in d['events'])
  a.check_index(self.m,installed)
