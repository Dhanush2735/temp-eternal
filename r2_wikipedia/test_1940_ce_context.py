import copy,gzip,hashlib,json,lzma,unittest
from pathlib import Path
from unittest.mock import patch
import apply_1940_ce_context as A
import progress_snapshot_1939 as P
import review_snapshot_archive as R
ROOT=Path(__file__).resolve().parent;H=A.H

def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else lzma.open(p,'rt',encoding='utf8') if str(p).endswith('.xz') else open(p,encoding='utf8')) as f:return json.load(f)
class BatchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=A.load(A.M);cls.packs={p:load(H/p) for p in load(H/'index.json')['packs']};cls.graph=load(H/'sources/wikipedia_1940_ce_people_links.json.gz')
 def test_installed_and_reversible(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=99
  with self.assertRaises(ValueError):A.validate(m)
  for u in self.m['updates']:
   rows=[e for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict) and e.get('id')==u['event_id']];self.assertEqual(rows,[u['after']])
  for p in {u['pack'] for u in self.m['updates']}:
   group=[u for u in self.m['updates'] if u['pack']==p];old=A.transform(self.packs[p],group,True,[]);self.assertEqual(A.transform(old,group,False,[]),self.packs[p])
 def test_locations(self):
  u={x['event_id']:x['after'] for x in self.m['updates']};self.assertEqual(len(u),5)
  for i,lat,lon in [('wpy_8bd7375523',51.49861,-0.135139),('wpy_935dbc6bfb',31.5928,74.3126),('wpy_5df90608bc',35.71944,-0.68889),('wpr_deef9cb100',19.35,-99.16222),('wpr_dddcaeb86f',52.52,13.405)]:self.assertEqual((u[i]['lat'],u[i]['lon']),(lat,lon))
  self.assertIn('independent states',u['wpy_935dbc6bfb']['name'])
 def test_graph(self):
  g=self.graph;ps={x['id'] for x in g['people']};idx={x.get('id') for d in self.packs.values() for x in d.get('events',[]) if isinstance(x,dict)}
  self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(11,6,11));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']))
 def test_annual_inventory(self):
  a=load(ROOT/'focus/year_titles_1940_1940_CE.json')['results'];p=load(ROOT/'focus/year_wikitext_1940_1940_CE.json.xz')['pages'];self.assertEqual({x['canonical_title'] for x in a},{'1940'});self.assertEqual({x['lastrevid'] for x in a},{x['revisions'][0]['revid'] for x in p});d=load(ROOT/'focus/indexed_start_inventory_1940_1940_CE.json.xz');self.assertEqual(len(d['rows']),411);self.assertEqual(sum('hazard' in x[0] for x in d['rows']),99)
 def test_hashes_and_pins(self):
  d=load(ROOT/'focus/rollback_hashes_1940_CE_context.json.xz');self.assertEqual(len(d['before']),26);self.assertEqual(d['before'],d['rollback']);self.assertEqual(d['after'],d['reapplied']);self.assertEqual(len(load(ROOT/'focus/pin_verification_1940_CE_context.json.xz')['identities']),20)
 def test_progress_archive(self):
  self.assertEqual(hashlib.sha256(P.read()).hexdigest(),P.ORIGINAL_SHA)
  with patch.object(P,'SPECS',[(P.SPECS[0][0],'bad',P.SPECS[0][2],P.SPECS[0][3])]):
   with self.assertRaises(ValueError):P.read()
 def test_duplicate_audit_archive(self):
  self.assertEqual(json.loads(R.read('duplicate_event_ids.json'))['duplicated_ids'],34)
  with patch.object(R,'within_budget',return_value=(True,125000000)):
   with self.assertRaises(RuntimeError):R.restore('duplicate_event_ids.json')
if __name__=='__main__':unittest.main()
