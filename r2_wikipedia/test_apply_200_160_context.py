import copy,gzip,json,unittest
import apply_200_160_context as a
class BatchTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=json.loads(a.M.read_text());cls.docs={}
  with gzip.open(a.H/a.R,'rt') as f:d=json.load(f)
  installed=any(x.get('id')==cls.m['moves'][0]['event_id'] for x in d['events'])
  for p in (a.W,a.HAZ,a.R,a.WAR,a.D,a.WORLD,a.MORE,a.N):
   with gzip.open(a.H/p,'rt') as f:d=json.load(f)
   cls.docs[p]=a.transform(d,cls.m,p,True) if installed else d
 def test_roundtrip_all_packs(self):
  for p,d in self.docs.items():self.assertEqual(a.transform(a.transform(d,self.m,p),self.m,p,True),d)
 def test_all_moves(self):
  out={p:a.transform(d,self.m,p) for p,d in self.docs.items()}
  for u in self.m['moves']:
   self.assertFalse(any(x.get('id')==u['event_id'] for x in out[u['from_pack']]['events']))
   self.assertEqual([x for x in out[a.R]['events'] if x.get('id')==u['event_id']],[u['after']])
 def test_update_changed(self):
  d=copy.deepcopy(self.docs[a.W]);u=next(x for x in self.m['updates'] if x['pack']==a.W);next(x for x in d['events'] if x.get('id')==u['event_id'])['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,a.W)
 def test_move_changed(self):
  u=self.m['moves'][0];d=copy.deepcopy(self.docs[u['from_pack']]);next(x for x in d['events'] if x.get('id')==u['event_id'])['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,u['from_pack'])
 def test_move_source_duplicate(self):
  u=self.m['moves'][0];d=copy.deepcopy(self.docs[u['from_pack']]);d['events'].append(copy.deepcopy(u['before']))
  with self.assertRaises(ValueError):a.transform(d,self.m,u['from_pack'])
 def test_move_target_duplicate(self):
  d=copy.deepcopy(self.docs[a.R]);d['events'].append(copy.deepcopy(self.m['moves'][0]['after']))
  with self.assertRaises(ValueError):a.transform(d,self.m,a.R)
 def test_rollback_changed(self):
  d=a.transform(self.docs[a.R],self.m,a.R);id=self.m['moves'][0]['event_id'];next(x for x in d['events'] if x.get('id')==id)['name']='changed'
  with self.assertRaises(ValueError):a.transform(d,self.m,a.R,True)
 def test_manifest_evidence_locked(self):
  m=copy.deepcopy(self.m);m['updates'][0]['after']['r2SourceEvidence']['review_note']='misleading'
  with self.assertRaises(ValueError):a.validate(m)
 def test_manifest_effect_locked(self):
  m=copy.deepcopy(self.m);m['moves'][0]['after']['effect']='political'
  with self.assertRaises(ValueError):a.validate(m)

 def test_addition_duplicate(self):
  d=copy.deepcopy(self.docs[a.R]);d['events'].append(copy.deepcopy(self.m['additions'][0]['event']))
  with self.assertRaises(ValueError):a.transform(d,self.m,a.R)

 def test_moved_hazards_non_damaging(self):
  self.assertEqual(len(self.m['moves']),24)
  for x in self.m['moves']:
   self.assertEqual((x['to_pack'],x['after']['effect']),(a.R,'note'))
