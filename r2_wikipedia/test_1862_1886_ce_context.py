import copy,gzip,lzma,json,unittest
from pathlib import Path
import apply_1862_1886_ce_context as A
ROOT=Path(__file__).resolve().parent.parent;DATA=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';FOCUS=ROOT/'r2_wikipedia/focus'
def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else lzma.open(p,'rt',encoding='utf8') if str(p).endswith('.xz') else open(p,encoding='utf8')) as f:return json.load(f)
class BatchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  from people_graph_archive import load_json
  cls.m=A.load(A.M);cls.packs={p:load(DATA/p) for p in load(DATA/'index.json')['packs']};cls.graph=load_json(DATA/'sources/wikipedia_1862_1886_ce_people_links.json')
 def test_manifest_tampering(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=99
  with self.assertRaises(ValueError):A.validate(m)
 def test_current_images_unique_and_reversible(self):
  want={u['event_id']:u['after'] for u in self.m['updates']};self.assertEqual(len(want),20);found={i:[] for i in want}
  for d in self.packs.values():
   for e in d.get('events',[]):
    if isinstance(e,dict) and e.get('id') in found:found[e['id']].append(e)
  for i in want:self.assertEqual(found[i],[want[i]])
  for p in {u['pack'] for u in self.m['updates']}:
   group=[u for u in self.m['updates'] if u['pack']==p];before=A.transform(self.packs[p],group,True,[]);self.assertEqual(A.transform(before,group,False,[]),self.packs[p])
 def test_key_corrections_and_duplicate_effects(self):
  u={x['event_id']:x['after'] for x in self.m['updates']}
  self.assertEqual(u['wpd_12eec79595']['start'],1863);self.assertEqual(u['wpd_6cea942419']['end'],1870);self.assertEqual(u['wpd_f86919c871']['end'],1879);self.assertEqual(u['wpd_ecedc1ecf0']['end'],1885)
  self.assertEqual(u['wpd_0458855782']['start'],1888);self.assertEqual(u['wpd_c8ce601dfd']['effect'],'note');self.assertEqual(u['wpd_7275ca8dbf']['effect'],'note');self.assertEqual(u['wpd_a09fc3031a']['effect'],'note')
  self.assertEqual((u['wpd_e99c54fe8c']['lat'],u['wpd_e99c54fe8c']['lon']),(55.8725,-4.30889))
 def test_graph(self):
  g=self.graph;ps={x['id'] for x in g['people']};idx={x.get('id') for d in self.packs.values() for x in d.get('events',[]) if isinstance(x,dict)}
  self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(35,12,35));self.assertEqual(len(ps),len(g['people']));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']))
 def test_year_archives(self):
  a=load(FOCUS/'year_titles_1862_1886_CE.json')['results'];p=load(FOCUS/'year_wikitext_1862_1886_CE.json.xz')['pages']
  self.assertEqual({x['canonical_title'] for x in a},{str(i) for i in range(1862,1887)});self.assertEqual({x['lastrevid'] for x in a},{x['revisions'][0]['revid'] for x in p});self.assertTrue(all('disambiguation' not in x.get('pageprops',{}) for x in p))
 def test_inventory(self):
  d=load(FOCUS/'indexed_start_inventory_1862_1886_CE.json.xz');self.assertEqual(len(d['rows']),3999);self.assertEqual(sum('hazard' in x[0] for x in d['rows']),803)
 def test_pin_identities_saved(self):
  d=load(FOCUS/'pin_verification_1862_1886_CE_context.json.xz');self.assertEqual(len(d['verified']),83);self.assertEqual(len({x['oldid'] for x in d['verified']}),83)
if __name__=='__main__':unittest.main()
