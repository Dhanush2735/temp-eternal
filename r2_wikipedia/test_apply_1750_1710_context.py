import copy,gzip,json,unittest
import apply_1750_1710_context as a
class BatchTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=json.loads(a.M.read_text());cls.docs={}
  with gzip.open(a.H/a.R,'rt') as f:d=json.load(f)
  installed=any(x.get('id')==cls.m['moves'][0]['event_id'] for x in d['events'])
  for p in (a.W,a.HAZ,a.R):
   with gzip.open(a.H/p,'rt') as f:d=json.load(f)
   cls.docs[p]=a.transform(d,cls.m,p,True) if installed else d
 def test_roundtrip_all_packs(self):
  for p,d in self.docs.items():self.assertEqual(a.transform(a.transform(d,self.m,p),self.m,p,True),d)
 def test_all_moves(self):
  out={p:a.transform(d,self.m,p) for p,d in self.docs.items()}
  for u in self.m['moves']:
   self.assertFalse(any(x.get('id')==u['event_id'] for x in out[a.HAZ]['events']))
   self.assertEqual([x for x in out[a.R]['events'] if x.get('id')==u['event_id']],[u['after']])
 def test_update_changed(self):
  d=copy.deepcopy(self.docs[a.W]);u=next(x for x in self.m['updates'] if x['pack']==a.W);next(x for x in d['events'] if x.get('id')==u['event_id'])['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,a.W)
 def test_move_changed(self):
  d=copy.deepcopy(self.docs[a.HAZ]);u=self.m['moves'][0];next(x for x in d['events'] if x.get('id')==u['event_id'])['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,a.HAZ)
 def test_move_source_duplicate(self):
  d=copy.deepcopy(self.docs[a.HAZ]);d['events'].append(copy.deepcopy(self.m['moves'][0]['before']))
  with self.assertRaises(ValueError):a.transform(d,self.m,a.HAZ)
 def test_move_target_duplicate(self):
  d=copy.deepcopy(self.docs[a.R]);d['events'].append(copy.deepcopy(self.m['moves'][0]['after']))
  with self.assertRaises(ValueError):a.transform(d,self.m,a.R)
 def test_addition_duplicate(self):
  d=copy.deepcopy(self.docs[a.R]);d['events'].append(copy.deepcopy(self.m['additions'][0]['event']))
  with self.assertRaises(ValueError):a.transform(d,self.m,a.R)
 def test_rollback_changed(self):
  d=a.transform(self.docs[a.R],self.m,a.R);id=self.m['moves'][0]['event_id'];next(x for x in d['events'] if x.get('id')==id)['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,a.R,True)
 def test_manifest_evidence_locked(self):
  m=copy.deepcopy(self.m);m['updates'][0]['after']['r2SourceEvidence']['review_note']='misleading'
  with self.assertRaises(ValueError):a.validate(m)
 def test_manifest_effect_locked(self):
  m=copy.deepcopy(self.m);m['additions'][0]['event']['effect']='political'
  with self.assertRaises(ValueError):a.validate(m)
