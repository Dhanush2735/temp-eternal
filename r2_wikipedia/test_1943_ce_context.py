import copy,gzip,json,lzma,unittest,sys
from pathlib import Path
import apply_1943_ce_context as A
R=Path(__file__).resolve().parent;H=A.H
def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else lzma.open(p,'rt',encoding='utf8') if str(p).endswith('.xz') else open(p,encoding='utf8')) as f:return json.load(f)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.m=A.load(A.M);cls.packs={p:load(H/p) for p in load(H/'index.json')['packs']};cls.graph=load(H/'sources/wikipedia_1943_ce_people_links.json.gz')
 def test_installed_and_reversible(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=99
  with self.assertRaises(ValueError):A.validate(m)
  for u in self.m['updates']:
   rows=[e for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict) and e.get('id')==u['event_id']];self.assertEqual(rows,[u['after']])
  for p in {u['pack'] for u in self.m['updates']}:
   group=[u for u in self.m['updates'] if u['pack']==p];old=A.transform(self.packs[p],group,True,[]);self.assertEqual(A.transform(old,group,False,[]),self.packs[p])
 def test_corrections(self):
  u={x['event_id']:x['after'] for x in self.m['updates']};self.assertEqual(len(u),4)
  for i,lat,lon in [('wpy_c23be2f604',50.04528,19.95472),('wpy_828369cf5c',41.8925,12.4775),('wpy_b3390c1e29',45.7675,4.835),('wpy_1e41c7c824',18.5523,73.9015)]:self.assertEqual((u[i]['lat'],u[i]['lon']),(lat,lon))
  self.assertIn('10 February to 3 March',u['wpy_1e41c7c824']['name']);self.assertIn('Delhi',u['wpy_1e41c7c824']['r2SourceEvidence']['review_note'])
 def test_graph(self):
  g=self.graph;ps={x['id'] for x in g['people']};idx={x.get('id') for d in self.packs.values() for x in d.get('events',[]) if isinstance(x,dict)}
  self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(10,2,10));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']))
 def test_annual_inventory(self):
  a=load(R/'focus/year_titles_1943_1943_CE.json')['results'];p=load(R/'focus/year_wikitext_1943_1943_CE.json.xz')['pages'];self.assertEqual({x['canonical_title'] for x in a},{'1943'});self.assertEqual({x['lastrevid'] for x in a},{x['revisions'][0]['revid'] for x in p});d=load(R/'focus/indexed_start_inventory_1943_1943_CE.json.xz');self.assertEqual(len(d['rows']),465);self.assertEqual(sum('hazard' in x[0] for x in d['rows']),85)
 def test_hashes_pins(self):
  d=load(R/'focus/rollback_hashes_1943_CE_context.json.xz');self.assertEqual(len(d['before']),26);self.assertEqual(d['before'],d['rollback']);self.assertEqual(d['after'],d['reapplied']);self.assertEqual(len(load(R/'focus/pin_verification_1943_CE_context.json.xz')['identities']),19)
 def test_historical_archives(self):
  sys.path.insert(0,str(R.parent/'eternal'));sys.path.insert(0,str(R.parent/'worldfill'));import archived_generated_reports as e;import archived_history_reports as w
  self.assertEqual(len(e.read('LIVE_COMMAND_AUDIT_REPORT.json')),40748);self.assertEqual(len(w.read('fact_audit_summary.json')),27082)
if __name__=='__main__':unittest.main()
