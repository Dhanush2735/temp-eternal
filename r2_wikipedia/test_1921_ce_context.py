import copy,gzip,hashlib,json,lzma,unittest
from pathlib import Path
import apply_1921_ce_context as A
import restore_vip_staging as V
from staged_exports import source,open_text
R=Path(__file__).resolve().parent;H=A.H
def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else lzma.open(p,'rt',encoding='utf8') if str(p).endswith('.xz') else open(p,encoding='utf8')) as f:return json.load(f)
class BatchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.m=A.load(A.M);cls.packs={p:load(H/p) for p in load(H/'index.json')['packs']};cls.graph=load(H/'sources/wikipedia_1921_ce_people_links.json.gz')
 def test_manifest_and_current(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=99
  with self.assertRaises(ValueError):A.validate(m)
  for u in self.m['updates']:
   rows=[e for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict) and e.get('id')==u['event_id']];self.assertEqual(rows,[u['after']])
  for p in {u['pack'] for u in self.m['updates']}:
   g=[u for u in self.m['updates'] if u['pack']==p];before=A.transform(self.packs[p],g,True,[]);self.assertEqual(A.transform(before,g,False,[]),self.packs[p])
 def test_data(self):
  u={x['event_id']:x['after'] for x in self.m['updates']};self.assertEqual(len(u),5);self.assertEqual((u['wpy_d40fb44709']['lat'],u['wpy_d40fb44709']['lon']),(52.50583,13.33278));self.assertEqual(u['wpy_2dc2c67185']['lon'],32.85472);self.assertEqual((u['wpy_3ffd6c4f36']['kind'],u['wpy_3ffd6c4f36']['effect']),('cultural','note'))
 def test_graph(self):
  g=self.graph;ps={x['id'] for x in g['people']};idx={x.get('id') for d in self.packs.values() for x in d.get('events',[]) if isinstance(x,dict)};self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(11,5,11));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']))
 def test_year_and_inventory(self):
  a=load(R/'focus/year_titles_1921_1921_CE.json')['results'];p=load(R/'focus/year_wikitext_1921_1921_CE.json.xz')['pages'];self.assertEqual({x['canonical_title'] for x in a},{'1921'});self.assertEqual({x['lastrevid'] for x in a},{x['revisions'][0]['revid'] for x in p});d=load(R/'focus/indexed_start_inventory_1921_1921_CE.json.xz');self.assertEqual(len(d['rows']),248);self.assertEqual(sum('hazard' in x[0] for x in d['rows']),68)
 def test_pins(self):self.assertEqual(len(load(R/'focus/pin_verification_1921_CE_context.json.xz')['verified']),20)
 def test_event_staging_restore(self):
  p,rawhash,gzhash=V.SPECS['events'];self.assertFalse(p.exists());raw=lzma.decompress(source(p).read_bytes());self.assertEqual(hashlib.sha256(raw).hexdigest(),rawhash);self.assertEqual(hashlib.sha256(gzip.compress(raw,9,mtime=0)).hexdigest(),gzhash)
  with open_text(p) as f:self.assertEqual(f.read().encode(),raw)
  with self.assertRaises(RuntimeError):V.restore('events')
if __name__=='__main__':unittest.main()
