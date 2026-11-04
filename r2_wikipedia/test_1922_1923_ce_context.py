import copy,gzip,hashlib,json,lzma,unittest
from pathlib import Path
from unittest.mock import patch
import apply_1922_1923_ce_context as A
import gandhi_archive as G
R=Path(__file__).resolve().parent;H=A.H

def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else lzma.open(p,'rt',encoding='utf8') if str(p).endswith('.xz') else open(p,encoding='utf8')) as f:return json.load(f)
class BatchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=A.load(A.M);cls.packs={p:load(H/p) for p in load(H/'index.json')['packs']};cls.graph=load(H/'sources/wikipedia_1922_1923_ce_people_links.json.gz')
 def test_manifest_current_and_reversible(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=99
  with self.assertRaises(ValueError):A.validate(m)
  for u in self.m['updates']:
   rows=[e for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict) and e.get('id')==u['event_id']];self.assertEqual(rows,[u['after']])
  for p in {u['pack'] for u in self.m['updates']}:
   group=[u for u in self.m['updates'] if u['pack']==p];before=A.transform(self.packs[p],group,True,[]);self.assertEqual(A.transform(before,group,False,[]),self.packs[p])
 def test_corrected_events(self):
  u={x['event_id']:x['after'] for x in self.m['updates']};self.assertEqual(len(u),8)
  self.assertEqual((u['wpy_0215a7482f']['lat'],u['wpy_0215a7482f']['lon']),(44.35,9.233));self.assertEqual(u['wpy_bd66faccfd']['lon'],-8.855673);self.assertEqual(u['wpw_b6c386dc23']['lat'],-28.45)
  self.assertEqual(u['wpr_297d30672a']['lat'],51.45083);self.assertEqual(u['wpr_535fe23b5b']['lat'],43.5299);self.assertNotIn('five prisoners',u['wpr_55270da3bf']['name']);self.assertNotIn('after the creation',u['wpy_f8de427470']['name'])
 def test_graph(self):
  g=self.graph;ps={x['id'] for x in g['people']};idx={x.get('id') for d in self.packs.values() for x in d.get('events',[]) if isinstance(x,dict)}
  self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(16,7,19));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']))
 def test_annual_inventory(self):
  for year,count,haz in [(1922,234,86),(1923,181,75)]:
   a=load(R/f'focus/year_titles_{year}_{year}_CE.json')['results'];p=load(R/f'focus/year_wikitext_{year}_{year}_CE.json.xz')['pages'];self.assertEqual({x['canonical_title'] for x in a},{str(year)});self.assertEqual({x['lastrevid'] for x in a},{x['revisions'][0]['revid'] for x in p});d=load(R/f'focus/indexed_start_inventory_{year}_{year}_CE.json.xz');self.assertEqual(len(d['rows']),count);self.assertEqual(sum('hazard' in x[0] for x in d['rows']),haz)
 def test_rollback_and_pins(self):
  d=load(R/'focus/rollback_hashes_1922_1923_CE_context.json.xz');self.assertEqual(d['packs'],26);self.assertEqual(d['before'],d['rollback']);self.assertEqual(d['after'],d['reapply']);self.assertEqual(len(load(R/'focus/pin_verification_1922_1923_CE_context.json.xz')['verified']),29)
 def test_gandhi_archives(self):
  for kind,(name,gh,rh,xh) in G.SPECS.items():
   raw=G.read(kind);self.assertEqual(G.digest(raw),rh);self.assertEqual(G.digest(gzip.compress(raw,9,mtime=0)),gh)
   with patch.object(G,'within_budget',return_value=(True,125000000)):
    with self.assertRaises(RuntimeError):G.restore(kind)
if __name__=='__main__':unittest.main()
