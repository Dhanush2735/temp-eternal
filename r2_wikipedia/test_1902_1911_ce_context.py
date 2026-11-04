import copy,gzip,lzma,json,unittest
from pathlib import Path
import apply_1902_1911_ce_context as A
ROOT=Path(__file__).resolve().parent.parent;DATA=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history';FOCUS=ROOT/'r2_wikipedia/focus'
def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else lzma.open(p,'rt',encoding='utf8') if str(p).endswith('.xz') else open(p,encoding='utf8')) as f:return json.load(f)
class BatchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=A.load(A.M);cls.packs={p:load(DATA/p) for p in load(DATA/'index.json')['packs']};cls.graph=load(DATA/'sources/wikipedia_1902_1911_ce_people_links.json.gz')
 def test_manifest_tampering(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=99
  with self.assertRaises(ValueError):A.validate(m)
 def test_current_images_unique_and_reversible(self):
  want={u['event_id']:u['after'] for u in self.m['updates']};self.assertEqual(len(want),13);found={i:[] for i in want}
  for d in self.packs.values():
   for e in d.get('events',[]):
    if isinstance(e,dict) and e.get('id') in found:found[e['id']].append(e)
  for i in want:self.assertEqual(found[i],[want[i]])
  for p in {u['pack'] for u in self.m['updates']}:
   group=[u for u in self.m['updates'] if u['pack']==p];before=A.transform(self.packs[p],group,True,[]);self.assertEqual(A.transform(before,group,False,[]),self.packs[p])
 def test_key_corrections(self):
  u={x['event_id']:x['after'] for x in self.m['updates']}
  for i in ['wpw_4fb277e1a4','wpw_dfb5dc2cf2','wpw_072aeb6aec']:self.assertEqual((u[i]['start'],u[i]['end'],u[i]['effect']),(1911,1913,'note'))
  self.assertEqual((u['wpy_fc19381b79']['start'],u['wpy_ebf3cef119']['start']),(1906,1909));self.assertEqual(u['wpy_410357fc94']['effect'],'note');self.assertEqual((u['wpy_b88200865b']['lat'],u['wpy_b88200865b']['lon']),(54.605,-5.905));self.assertIn('southern Sakhalin',u['wpy_03319fb4c3']['name']);self.assertEqual(u['wpy_03319fb4c3']['effect'],'political')
 def test_graph(self):
  g=self.graph;ps={x['id'] for x in g['people']};idx={x.get('id') for d in self.packs.values() for x in d.get('events',[]) if isinstance(x,dict)}
  self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(18,7,18));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']))
 def test_year_archives(self):
  a=load(FOCUS/'year_titles_1902_1911_CE.json')['results'];p=load(FOCUS/'year_wikitext_1902_1911_CE.json.xz')['pages'];self.assertEqual({x['canonical_title'] for x in a},{str(i) for i in range(1902,1912)});self.assertEqual({x['lastrevid'] for x in a},{x['revisions'][0]['revid'] for x in p});self.assertTrue(all('disambiguation' not in x.get('pageprops',{}) for x in p))
 def test_inventory(self):
  d=load(FOCUS/'indexed_start_inventory_1902_1911_CE.json.xz');self.assertEqual(len(d['rows']),1753);self.assertEqual(sum('hazard' in x[0] for x in d['rows']),707)
 def test_pin_identities_saved(self):
  d=load(FOCUS/'pin_verification_1902_1911_CE_context.json.xz');self.assertEqual(len(d['verified']),40)
if __name__=='__main__':unittest.main()
