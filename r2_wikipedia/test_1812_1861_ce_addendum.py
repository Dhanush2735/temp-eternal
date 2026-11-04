import copy,gzip,lzma,json,unittest
from pathlib import Path
import apply_1812_1861_ce_addendum as A
import apply_1812_1861_ce_context as C
ROOT=Path(__file__).resolve().parent.parent;DATA=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
def load(p):
 if not Path(p).exists() and Path(p).name.startswith('year_wikitext_'):
  from annual_archive import load_json
  return load_json(p)
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else lzma.open(p,'rt',encoding='utf8') if str(p).endswith('.xz') else open(p,encoding='utf8')) as f:return json.load(f)
class BatchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  from people_graph_archive import load_json
  cls.m=A.load(A.M);cls.packs={p:load(DATA/p) for p in load(DATA/'index.json')['packs']};cls.graph=load_json(DATA/'sources/wikipedia_1812_1861_ce_people_links.json')
 def transform(self,d,module,m,rev):
  for p in {u['pack'] for u in m['updates']}:d[p]=module.transform(d[p],[u for u in m['updates'] if u['pack']==p],rev,[])
 def test_manifest_and_tampering(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=99
  with self.assertRaises(ValueError):A.validate(m)
 def test_after_images_unique(self):
  want={u['event_id']:u['after'] for u in self.m['updates']};self.assertEqual(len(want),14);found={i:[] for i in want}
  for d in self.packs.values():
   for e in d.get('events',[]):
    if isinstance(e,dict) and e.get('id') in found:found[e['id']].append(e)
  for i in want:self.assertEqual(found[i],[want[i]])
 def test_current_and_prior_in_order(self):
  d=copy.deepcopy(self.packs);self.transform(d,A,self.m,True);base=copy.deepcopy(d);old=C.load(C.M)
  self.transform(d,C,old,True);self.transform(d,C,old,False);self.assertEqual(d,base)
  self.transform(d,A,self.m,False);self.assertEqual(d,self.packs)
 def test_key_corrections(self):
  u={x['event_id']:x['after'] for x in self.m['updates']}
  self.assertEqual(u['wpy_e4de9a4ed4']['start'],1812);self.assertEqual(u['wpd_178559e7f3']['end'],1817)
  self.assertEqual((u['wpd_d85eb7d33b']['lat'],u['wpd_d85eb7d33b']['lon']),(37.87444,32.49306));self.assertEqual(u['wpd_d976909614']['effect'],'note')
 def test_graph(self):
  g=self.graph;ps={x['id'] for x in g['people']};idx={x.get('id') for d in self.packs.values() for x in d.get('events',[]) if isinstance(x,dict)}
  self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(27,10,28));self.assertEqual(len(ps),len(g['people']));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']))
 def test_year_archives(self):
  a=load(ROOT/'r2_wikipedia/focus/year_titles_1812_1861_CE.json')['results'];p=load(ROOT/'r2_wikipedia/focus/year_wikitext_1812_1861_CE.json.xz')['pages']
  self.assertEqual({x['canonical_title'] for x in a},{str(i) for i in range(1812,1862)});self.assertEqual({x['lastrevid'] for x in a},{x['revisions'][0]['revid'] for x in p});self.assertTrue(all('disambiguation' not in x.get('pageprops',{}) for x in p))
 def test_inventory(self):
  d=load(ROOT/'r2_wikipedia/focus/indexed_start_inventory_1812_1861_CE.json.xz');self.assertEqual(len(d['rows']),5844);self.assertEqual(sum('hazard' in x[0] for x in d['rows']),1240)
if __name__=='__main__':unittest.main()
