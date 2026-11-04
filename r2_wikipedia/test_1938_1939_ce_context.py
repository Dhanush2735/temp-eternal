import copy,gzip,json,lzma,unittest
from pathlib import Path
import apply_1938_1939_ce_context as A
R=Path(__file__).resolve().parent;H=A.H

def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else lzma.open(p,'rt',encoding='utf8') if str(p).endswith('.xz') else open(p,encoding='utf8')) as f:return json.load(f)
class BatchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=A.load(A.M);cls.packs={p:load(H/p) for p in load(H/'index.json')['packs']};cls.graph=load(H/'sources/wikipedia_1938_1939_ce_people_links.json.gz')
 def test_installed_and_reversible(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=99
  with self.assertRaises(ValueError):A.validate(m)
  for u in self.m['updates']:
   rows=[e for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict) and e.get('id')==u['event_id']];self.assertEqual(rows,[u['after']])
  for p in {u['pack'] for u in self.m['updates']}:
   group=[u for u in self.m['updates'] if u['pack']==p];old=A.transform(self.packs[p],group,True,[]);self.assertEqual(A.transform(old,group,False,[]),self.packs[p])
 def test_corrected_events(self):
  u={x['event_id']:x['after'] for x in self.m['updates']};self.assertEqual(len(u),11)
  for i,lat,lon in [('wpy_426fed889a',48.1375,11.575),('wpy_bf89a98a97',48.1375,11.575),('wpy_62961cba2f',34.876944,113.672778),('q129151',34.876944,113.672778),('wpy_62d2f4b914',29.5637,106.5504),('wpw_6bdb4bb4c8',48.181389,23.297778),('wpr_6e6af62b63',47.73028,118.59),('wpr_5d4230855b',10.7,105.133333)]:self.assertEqual((u[i]['lat'],u[i]['lon']),(lat,lon))
  self.assertEqual((u['wpy_f9e54764e1']['kind'],u['wpy_f9e54764e1']['effect']),('political','note'));self.assertEqual((u['wpr_5d4230855b']['kind'],u['wpr_5d4230855b']['effect']),('cultural','note'))
 def test_graph(self):
  g=self.graph;ps={x['id'] for x in g['people']};idx={x.get('id') for d in self.packs.values() for x in d.get('events',[]) if isinstance(x,dict)}
  self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(24,13,24));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']))
 def test_annual_inventory(self):
  a=load(R/'focus/year_titles_1938_1939_CE.json')['results'];p=load(R/'focus/year_wikitext_1938_1939_CE.json.xz')['pages'];self.assertEqual({x['canonical_title'] for x in a},{'1938','1939'});self.assertEqual({x['lastrevid'] for x in a},{x['revisions'][0]['revid'] for x in p});d=load(R/'focus/indexed_start_inventory_1938_1939_CE.json.xz');self.assertEqual(len(d['rows']),651);self.assertEqual(sum('hazard' in x[0] for x in d['rows']),223)
 def test_hashes_and_pins(self):
  d=load(R/'focus/rollback_hashes_1938_1939_CE_context.json.xz');self.assertEqual(len(d['before']),26);self.assertEqual(d['before'],d['rollback']);self.assertEqual(d['after'],d['reapplied']);self.assertEqual(len(load(R/'focus/pin_verification_1938_1939_CE_context.json.xz')['identities']),37)
if __name__=='__main__':unittest.main()
