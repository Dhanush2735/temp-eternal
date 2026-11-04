import copy,gzip,json,lzma,unittest
from pathlib import Path
import apply_1912_1917_ce_context as A
R=Path(__file__).resolve().parent;H=A.H
def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else lzma.open(p,'rt',encoding='utf8') if str(p).endswith('.xz') else open(p,encoding='utf8')) as f:return json.load(f)
class BatchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=A.load(A.M);cls.packs={p:load(H/p) for p in load(H/'index.json')['packs']};cls.graph=load(H/'sources/wikipedia_1912_1917_ce_people_links.json.gz')
 def test_manifest(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=99
  with self.assertRaises(ValueError):A.validate(m)
 def test_unique_and_reversible(self):
  want={u['event_id']:u['after'] for u in self.m['updates']};self.assertEqual(len(want),6);found={i:[] for i in want}
  for d in self.packs.values():
   for e in d.get('events',[]):
    if isinstance(e,dict) and e.get('id') in found:found[e['id']].append(e)
  for i in want:self.assertEqual(found[i],[want[i]])
  for p in {u['pack'] for u in self.m['updates']}:
   group=[u for u in self.m['updates'] if u['pack']==p];before=A.transform(self.packs[p],group,True,[]);self.assertEqual(A.transform(before,group,False,[]),self.packs[p])
 def test_corrections(self):
  u={x['event_id']:x['after'] for x in self.m['updates']}
  for i in ('wpy_4ca2bab401','wpy_8fab9cfaf1'):self.assertEqual((u[i]['start'],u[i]['end'],u[i]['lat'],u[i]['lon']),(1915,1916,51.417,-8.55))
  self.assertEqual((u['wpy_21f7523f95']['lat'],u['wpy_21f7523f95']['lon'],u['wpy_21f7523f95']['effect']),(59.9375,30.30861,'political'))
  self.assertIn('Ancon',u['wpy_507ff8a59e']['name']);self.assertEqual(u['wpr_a983b40aa4']['effect'],'political')
 def test_graph(self):
  g=self.graph;ps={x['id'] for x in g['people']};idx={x.get('id') for d in self.packs.values() for x in d.get('events',[]) if isinstance(x,dict)}
  self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(12,5,12));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']))
 def test_years(self):
  a=load(R/'focus/year_titles_1912_1917_CE.json')['results'];p=load(R/'focus/year_wikitext_1912_1917_CE.json.xz')['pages'];self.assertEqual({x['canonical_title'] for x in a},{str(i) for i in range(1912,1918)});self.assertEqual({x['lastrevid'] for x in a},{x['revisions'][0]['revid'] for x in p});self.assertTrue(all('disambiguation' not in x.get('pageprops',{}) for x in p))
 def test_inventory(self):
  d=load(R/'focus/indexed_start_inventory_1912_1917_CE.json.xz');self.assertEqual(len(d['rows']),1686);self.assertEqual(sum('hazard' in x[0] for x in d['rows']),393)
 def test_pins(self):self.assertEqual(len(load(R/'focus/pin_verification_1912_1917_CE_context.json.xz')['verified']),28)
if __name__=='__main__':unittest.main()
