import copy,json,lzma,unittest,sys
from pathlib import Path
import apply_1948_1953_ce_context as A
R=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=A.load(A.M);cls.packs={p:A.load(A.H/p) for p in A.load(A.H/'index.json')['packs']};cls.graph=A.load(A.H/'sources/wikipedia_1948_1953_ce_people_links.json.gz')
 def test_installed_and_roundtrip(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['lat']=0
  with self.assertRaises(ValueError):A.validate(m)
  for u in self.m['updates']:
   rows=[e for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict) and e.get('id')==u['event_id']];self.assertEqual(rows,[u['after']]);self.assertEqual(tuple(u['before'][k] for k in ('start','end','kind','effect','radiusKm')),tuple(u['after'][k] for k in ('start','end','kind','effect','radiusKm')))
  for p in {u['pack'] for u in self.m['updates']}:
   us=[u for u in self.m['updates'] if u['pack']==p];old=A.transform(self.packs[p],us,True,[]);self.assertEqual(A.transform(old,us,False,[]),self.packs[p])
 def test_corrections(self):
  x={u['event_id']:u['after'] for u in self.m['updates']}
  for i,c in [('wpr_a971951de4',(31.77889,35.22556)),('wpr_6e50ae77b1',(15.6321,121.1448)),('wpr_8b34f9b810',(33.60611,73.06444)),('wpy_6021487998',(-0.945,36.595))]:self.assertEqual((x[i]['lat'],x[i]['lon']),c)
  self.assertIn('estimates vary',x['wpy_b808a9186e']['name']);self.assertIn('not the exact',x['wpy_6021487998']['r2SourceEvidence']['review_note']);self.assertEqual(x['wpr_8b34f9b810']['radiusKm'],800)
 def test_graph(self):
  g=self.graph;ps={x['id'] for x in g['people']};events={e.get('id') for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict)}
  self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(9,6,8));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in events for x in g['event_roles']))
 def test_hashes_and_pins(self):
  with lzma.open(R/'focus/rollback_hashes_1948_1953_CE_context.json.xz','rt') as f:h=json.load(f)
  self.assertEqual(len(h['before']),26);self.assertEqual(h['before'],h['rollback']);self.assertEqual(h['after'],h['reapplied'])
  with lzma.open(R/'focus/pin_verification_1948_1953_CE_context.json.xz','rt') as f:p=json.load(f)
  self.assertEqual(len(p['identities']),16)
 def test_archived_reports(self):
  sys.path[:0]=[str(R.parent/'eternal'),str(R.parent/'worldfill')];import archived_generated_reports as e;import archived_history_reports as w
  self.assertEqual(len(e.read('AUTO_COMMAND_TEST_REPORT.md')),33835);self.assertEqual(len(w.read('money_coverage_report.json')),16566);self.assertEqual(len(w.read('hazards_report.json')),12304)
if __name__=='__main__':unittest.main()
