import copy,gzip,json,lzma,unittest,sys
from pathlib import Path
from unittest.mock import patch
import apply_1941_ce_context as A
R=Path(__file__).resolve().parent;H=A.H
def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else lzma.open(p,'rt',encoding='utf8') if str(p).endswith('.xz') else open(p,encoding='utf8')) as f:return json.load(f)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.m=A.load(A.M);cls.packs={p:load(H/p) for p in load(H/'index.json')['packs']};cls.graph=load(H/'sources/wikipedia_1941_ce_people_links.json.gz')
 def test_installed_roundtrip(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=99
  with self.assertRaises(ValueError):A.validate(m)
  for u in self.m['updates']:
   rows=[e for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict) and e.get('id')==u['event_id']];self.assertEqual(rows,[u['after']])
  for p in {u['pack'] for u in self.m['updates']}:
   group=[u for u in self.m['updates'] if u['pack']==p];old=A.transform(self.packs[p],group,True,[]);self.assertEqual(A.transform(old,group,False,[]),self.packs[p])
 def test_corrections(self):
  u={x['event_id']:x['after'] for x in self.m['updates']};self.assertEqual(len(u),4)
  for i,lat,lon in [('wpy_718c9464ae',22.97889,106.05167),('wpy_216ec711c6',21.3,-157.85),('wpy_5a8f01da9a',40.758842,-73.984728),('wpy_23601e7f0b',9.03583,38.7525)]:self.assertEqual((u[i]['lat'],u[i]['lon']),(lat,lon))
  self.assertNotIn('Viet Cong',u['wpy_718c9464ae']['name']);self.assertNotIn('in preparation for a future attack',u['wpy_216ec711c6']['name'])
 def test_graph(self):
  g=self.graph;ps={x['id'] for x in g['people']};idx={x.get('id') for d in self.packs.values() for x in d.get('events',[]) if isinstance(x,dict)}
  self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(9,5,9));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']))
 def test_annual(self):
  a=load(R/'focus/year_titles_1941_1941_CE.json')['results'];p=load(R/'focus/year_wikitext_1941_1941_CE.json.xz')['pages'];self.assertEqual({x['canonical_title'] for x in a},{'1941'});self.assertEqual({x['lastrevid'] for x in a},{x['revisions'][0]['revid'] for x in p});d=load(R/'focus/indexed_start_inventory_1941_1941_CE.json.xz');self.assertEqual(len(d['rows']),514);self.assertEqual(sum('hazard' in x[0] for x in d['rows']),113)
 def test_hashes_pins(self):
  d=load(R/'focus/rollback_hashes_1941_CE_context.json.xz');self.assertEqual(len(d['before']),26);self.assertEqual(d['before'],d['rollback']);self.assertEqual(d['after'],d['reapplied']);self.assertEqual(len(load(R/'focus/pin_verification_1941_CE_context.json.xz')['identities']),17)
 def test_report_archives(self):
  sys.path.insert(0,str(R.parent/'worldfill'));sys.path.insert(0,str(R.parent/'eternal'));import archived_history_reports as w;import archived_generated_reports as e
  self.assertTrue(w.read('PRODUCT_ATLAS_TABLE.md').startswith(b'# Product atlas:'));self.assertEqual(len(w.read('build_places_report.json')),2639);self.assertEqual(len(e.read('structure.txt')),15223)
  with patch.object(w,'within_budget',return_value=(True,125000000)):
   with self.assertRaises(RuntimeError):w.restore('PRODUCT_ATLAS_TABLE.md')
if __name__=='__main__':unittest.main()
