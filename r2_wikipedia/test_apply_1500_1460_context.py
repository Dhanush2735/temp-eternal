import copy,gzip,json,unittest
import apply_1500_1460_context as a
class BatchTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=json.loads(a.M.read_text());cls.docs={}
  for p in a.PACKS:
   with gzip.open(a.H/p,'rt') as f:d=json.load(f)
   u=next(x for x in cls.m['updates'] if x['pack']==p)
   row=next(x for x in d['events'] if x.get('id')==u['event_id'])
   cls.docs[p]=a.transform(d,cls.m,p,True) if row==u['after'] else d
 def test_roundtrip(self):
  for p,d in self.docs.items():self.assertEqual(a.transform(a.transform(d,self.m,p),self.m,p,True),d)
 def test_changed_source_rejected(self):
  u=self.m['updates'][0];d=copy.deepcopy(self.docs[u['pack']]);next(x for x in d['events'] if x.get('id')==u['event_id'])['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,u['pack'])
 def test_duplicate_rejected(self):
  u=self.m['updates'][0];d=copy.deepcopy(self.docs[u['pack']]);d['events'].append(copy.deepcopy(u['before']))
  with self.assertRaises(ValueError):a.transform(d,self.m,u['pack'])
 def test_changed_manifest_rejected(self):
  m=copy.deepcopy(self.m);m['updates'][0]['after']['name']='changed'
  with self.assertRaises(ValueError):a.validate(m)
 def test_index(self):a.check_index(self.m)
 def test_rollback_changed_rejected(self):
  u=self.m['updates'][0];d=a.transform(self.docs[u['pack']],self.m,u['pack']);next(x for x in d['events'] if x.get('id')==u['event_id'])['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,u['pack'],True)
