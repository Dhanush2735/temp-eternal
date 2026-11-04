import copy,gzip,lzma,json,unittest
from pathlib import Path
import apply_1887_1901_ce_context as A
ROOT=Path(__file__).resolve().parent.parent;DATA=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';FOCUS=ROOT/'r2_wikipedia/focus'
def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else lzma.open(p,'rt',encoding='utf8') if str(p).endswith('.xz') else open(p,encoding='utf8')) as f:return json.load(f)
class BatchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=A.load(A.M);cls.packs={p:load(DATA/p) for p in load(DATA/'index.json')['packs']};cls.graph=load(DATA/'sources/wikipedia_1887_1901_ce_people_links.json.gz')
 def test_manifest_tampering(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=99
  with self.assertRaises(ValueError):A.validate(m)
 def test_current_images_unique_and_reversible(self):
  want={u['event_id']:u['after'] for u in self.m['updates']};self.assertEqual(len(want),12);found={i:[] for i in want}
  for d in self.packs.values():
   for e in d.get('events',[]):
    if isinstance(e,dict) and e.get('id') in found:found[e['id']].append(e)
  for i in want:self.assertEqual(found[i],[want[i]])
  for p in {u['pack'] for u in self.m['updates']}:
   group=[u for u in self.m['updates'] if u['pack']==p];before=A.transform(self.packs[p],group,True,[]);self.assertEqual(A.transform(before,group,False,[]),self.packs[p])
 def test_key_dates_and_locations(self):
  u={x['event_id']:x['after'] for x in self.m['updates']}
  self.assertEqual(u['wpd_af501198f1']['start'],1893);self.assertEqual(u['wpd_5e9f05918e']['start'],1898);self.assertEqual(u['wpd_5ed57053a3']['start'],1895)
  self.assertEqual((u['wpw_6063ac3903']['lat'],u['wpw_6063ac3903']['lon']),(23.133,-82.383));self.assertEqual(u['wpd_6edc9dffb7']['effect'],'note');self.assertEqual(u['wpd_24201583e9']['effect'],'note')
 def test_graph(self):
  g=self.graph;ps={x['id'] for x in g['people']};idx={x.get('id') for d in self.packs.values() for x in d.get('events',[]) if isinstance(x,dict)}
  self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(19,9,20));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']))
 def test_year_archives(self):
  a=load(FOCUS/'year_titles_1887_1901_CE.json')['results'];p=load(FOCUS/'year_wikitext_1887_1901_CE.json.xz')['pages'];self.assertEqual({x['canonical_title'] for x in a},{str(i) for i in range(1887,1902)});self.assertEqual({x['lastrevid'] for x in a},{x['revisions'][0]['revid'] for x in p});self.assertTrue(all('disambiguation' not in x.get('pageprops',{}) for x in p))
 def test_inventory(self):
  d=load(FOCUS/'indexed_start_inventory_1887_1901_CE.json.xz');self.assertEqual(len(d['rows']),2780);self.assertEqual(sum('hazard' in x[0] for x in d['rows']),572)
 def test_pin_identities_saved(self):
  d=load(FOCUS/'pin_verification_1887_1901_CE_context.json.xz');self.assertEqual(len(d['verified']),46)
if __name__=='__main__':unittest.main()
