import copy,gzip,json,unittest
import apply_1700_1660_context as a
class BatchTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=json.loads(a.M.read_text());cls.docs={}
  with gzip.open(a.H/a.R,'rt') as f:d=json.load(f)
  installed=any(x.get('id')==cls.m['additions'][0]['event']['id'] for x in d['events'])
  for p in (a.W,a.R):
   with gzip.open(a.H/p,'rt') as f:d=json.load(f)
   cls.docs[p]=a.transform(d,cls.m,p,True) if installed else d
 def test_roundtrip(self):
  for p,d in self.docs.items():self.assertEqual(a.transform(a.transform(d,self.m,p),self.m,p,True),d)
 def test_updates_installed(self):
  for p,d in self.docs.items():
   out=a.transform(d,self.m,p)
   for u in self.m['updates']:
    if u['pack']==p:self.assertEqual([r for r in out['events'] if r.get('id')==u['event_id']],[u['after']])
 def test_changed_source(self):
  d=copy.deepcopy(self.docs[a.W]);u=next(x for x in self.m['updates'] if x['pack']==a.W);next(r for r in d['events'] if r.get('id')==u['event_id'])['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,a.W)
 def test_duplicate_source(self):
  d=copy.deepcopy(self.docs[a.W]);u=next(x for x in self.m['updates'] if x['pack']==a.W);d['events'].append(copy.deepcopy(u['before']))
  with self.assertRaises(ValueError):a.transform(d,self.m,a.W)
 def test_duplicate_addition(self):
  d=copy.deepcopy(self.docs[a.R]);d['events'].append(copy.deepcopy(self.m['additions'][0]['event']))
  with self.assertRaises(ValueError):a.transform(d,self.m,a.R)
 def test_changed_rollback(self):
  d=a.transform(self.docs[a.R],self.m,a.R);id=self.m['additions'][0]['event']['id'];next(r for r in d['events'] if r.get('id')==id)['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,a.R,True)
 def test_evidence_locked(self):
  m=copy.deepcopy(self.m);m['updates'][0]['after']['r2SourceEvidence']['review_note']='misleading'
  with self.assertRaises(ValueError):a.validate(m)
 def test_political_effect_blocked(self):
  m=copy.deepcopy(self.m);m['additions'][0]['event']['effect']='political'
  with self.assertRaises(ValueError):a.validate(m)
 def test_date_locked(self):
  m=copy.deepcopy(self.m);m['additions'][0]['event']['start']=-3000
  with self.assertRaises(ValueError):a.validate(m)
