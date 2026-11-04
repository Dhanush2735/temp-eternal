import copy,gzip,json,lzma,unittest
from pathlib import Path
import apply_1945_1947_ce_context as A
R=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=A.load(A.M);cls.packs={p:A.load(A.H/p) for p in A.load(A.H/'index.json')['packs']};cls.graph=A.load(A.H/'sources/wikipedia_1945_1947_ce_people_links.json.gz')
 def test_installed_and_roundtrip(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['lat']=0
  with self.assertRaises(ValueError):A.validate(m)
  for u in self.m['updates']:
   rows=[e for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict) and e.get('id')==u['event_id']];self.assertEqual(rows,[u['after']]);self.assertEqual((u['before']['start'],u['before']['end'],u['before']['effect']),(u['after']['start'],u['after']['end'],u['after']['effect']))
  for p in {u['pack'] for u in self.m['updates']}:
   us=[u for u in self.m['updates'] if u['pack']==p];old=A.transform(self.packs[p],us,True,[]);self.assertEqual(A.transform(old,us,False,[]),self.packs[p])
 def test_locations_and_limits(self):
  x={u['event_id']:u['after'] for u in self.m['updates']}
  for i,c in [('wpy_d5f3455462',(51.77694,19.45472)),('wpy_24d0930b91',(51.56028,13.00556)),('wpy_1619fe6459',(50.87306,20.62667)),('wpr_0367cd5600',(35.8965,139.3379))]:self.assertEqual((x[i]['lat'],x[i]['lon']),c)
  self.assertEqual(x['wpr_0367cd5600']['radiusKm'],20);self.assertIn('not at this station',x['wpr_0367cd5600']['r2SourceEvidence']['review_note']);self.assertIn('elsewhere',x['wpy_d5f3455462']['r2SourceEvidence']['review_note'])
 def test_graph(self):
  g=self.graph;ps={x['id'] for x in g['people']};events={e.get('id') for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict)}
  self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(8,4,8));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in events for x in g['event_roles']))
 def test_hashes_and_pins(self):
  with lzma.open(R/'focus/rollback_hashes_1945_1947_CE_context.json.xz','rt') as f:h=json.load(f)
  self.assertEqual(len(h['before']),26);self.assertEqual(h['before'],h['rollback']);self.assertEqual(h['after'],h['reapplied'])
  with lzma.open(R/'focus/pin_verification_1945_1947_CE_context.json.xz','rt') as f:p=json.load(f)
  self.assertEqual(len(p['identities']),10)
if __name__=='__main__':unittest.main()
