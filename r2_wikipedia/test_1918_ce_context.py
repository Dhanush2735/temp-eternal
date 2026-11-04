import copy,gzip,hashlib,json,lzma,unittest
from pathlib import Path
import apply_1918_ce_context as A
import restore_vip_staging as V
from staged_exports import open_text,source
R=Path(__file__).resolve().parent;H=A.H
def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else lzma.open(p,'rt',encoding='utf8') if str(p).endswith('.xz') else open(p,encoding='utf8')) as f:return json.load(f)
class BatchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.m=A.load(A.M);cls.packs={p:load(H/p) for p in load(H/'index.json')['packs']};cls.graph=load(H/'sources/wikipedia_1918_ce_people_links.json.gz')
 def test_manifest(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=99
  with self.assertRaises(ValueError):A.validate(m)
 def test_current_unique_and_reversible(self):
  want={u['event_id']:u['after'] for u in self.m['updates']};self.assertEqual(len(want),4);found={i:[] for i in want}
  for d in self.packs.values():
   for e in d.get('events',[]):
    if isinstance(e,dict) and e.get('id') in found:found[e['id']].append(e)
  for i in want:self.assertEqual(found[i],[want[i]])
  for p in {u['pack'] for u in self.m['updates']}:
   g=[u for u in self.m['updates'] if u['pack']==p];b=A.transform(self.packs[p],g,True,[]);self.assertEqual(A.transform(b,g,False,[]),self.packs[p])
 def test_corrections(self):
  u={x['event_id']:x['after'] for x in self.m['updates']};self.assertEqual((u['wpr_774b870d14']['lat'],u['wpr_774b870d14']['lon']),(52.13472,23.65694));self.assertEqual((u['wpy_e62e9f12bd']['lat'],u['wpy_e62e9f12bd']['lon']),(39.867,25.267));self.assertEqual(u['wpr_2635f11dc4']['effect'],'political');self.assertIn('uncertain',u['wpr_5f7242cf3c']['name'])
 def test_graph(self):
  g=self.graph;ps={x['id'] for x in g['people']};idx={x.get('id') for d in self.packs.values() for x in d.get('events',[]) if isinstance(x,dict)};self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(7,4,7));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']))
 def test_year_and_inventory(self):
  a=load(R/'focus/year_titles_1918_1918_CE.json')['results'];p=load(R/'focus/year_wikitext_1918_1918_CE.json.xz')['pages'];self.assertEqual({x['canonical_title'] for x in a},{'1918'});self.assertEqual({x['lastrevid'] for x in a},{x['revisions'][0]['revid'] for x in p});self.assertTrue(all('disambiguation' not in x.get('pageprops',{}) for x in p));d=load(R/'focus/indexed_start_inventory_1918_1918_CE.json.xz');self.assertEqual(len(d['rows']),435);self.assertEqual(sum('hazard' in x[0] for x in d['rows']),66)
 def test_pins(self):self.assertEqual(len(load(R/'focus/pin_verification_1918_CE_context.json.xz')['verified']),16)
 def test_vip_archive_roundtrip(self):
  self.assertFalse(V.P.exists());x=source(V.P);raw=lzma.decompress(x.read_bytes());self.assertEqual(hashlib.sha256(raw).hexdigest(),V.RAW);self.assertEqual(hashlib.sha256(gzip.compress(raw,9,mtime=0)).hexdigest(),V.EXPECTED)
  with open_text(V.P) as f:self.assertEqual(f.read().encode(),raw)
 def test_vip_restore_blocks_when_full(self):
  with self.assertRaises(RuntimeError):V.restore()
  self.assertFalse(V.P.exists())
if __name__=='__main__':unittest.main()
