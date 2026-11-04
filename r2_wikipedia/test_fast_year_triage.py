import gzip,json,lzma,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import fast_year_triage as T
import apply_1944_ce_context as A

def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else lzma.open(p,'rt',encoding='utf8') if str(p).endswith('.xz') else open(p,encoding='utf8')) as f:return json.load(f)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.pages=T.verify(1944,1953);cls.triage=T.analyze(1944,1953,write=False);cls.m=A.load(A.M)
 def test_all_intervening_years(self):
  self.assertEqual({int(p['title']) for p in self.pages},set(range(1944,1954)));self.assertEqual(set(map(int,self.triage['year_summary'])),set(range(1944,1954)));self.assertEqual((self.triage['starts'],self.triage['hazards']),(3583,900));self.assertEqual(self.triage['year_summary']['1944']['starts'],692)
 def test_approx_links_and_caveats(self):
  p=next(p for p in self.pages if p['title']=='1944');self.assertIn('Anne Frank',T.links(p));self.assertIn('not necessarily followed',self.triage['status']);self.assertGreater(self.triage['year_summary']['1944']['candidate_mainspace_links'],100)
 def test_existing_idempotent(self):
  with patch.object(T.collector,'collect',side_effect=AssertionError('must not refetch')),patch.object(T.inventory,'inventory',side_effect=AssertionError('must not rescan to new inventory')):self.assertEqual(T.prepare(1944,1953),self.triage)
 def test_refuse_incomplete(self):
  with tempfile.TemporaryDirectory() as d,patch.object(T,'F',Path(d)):
   (Path(d)/'year_titles_3_4_CE.json').write_text('{}')
   with self.assertRaises(RuntimeError):T.prepare(3,4)
   self.assertFalse((Path(d)/'year_wikitext_3_4_CE.json.xz').exists())
 def test_no_wrong_range(self):
  for x,y in [(0,1),(2,1),(1,51)]:
   with self.assertRaises(ValueError):T.prepare(x,y)
 def test_manifest_and_roundtrip(self):
  A.validate(self.m);packs=load(A.H/'index.json')['packs'];events={p:load(A.H/p) for p in packs};self.assertEqual(len(self.m['updates']),3)
  for u in self.m['updates']:
   rows=[e for d in events.values() for e in d.get('events',[]) if isinstance(e,dict) and e.get('id')==u['event_id']];self.assertEqual(rows,[u['after']])
  g=self.m['updates'];cur=events[g[0]['pack']];self.assertEqual(A.transform(A.transform(cur,g,True,[]),g,False,[]),cur)
 def test_frank_uncertainty(self):
  u=next(x['after'] for x in self.m['updates'] if x['event_id']=='wpy_3a12af179e');self.assertEqual((u['lat'],u['lon']),(52.37525,4.88432));self.assertIn('uncertain',u['name']);self.assertNotIn('informer',u['name'])
 def test_graph_hashes(self):
  h=load(T.F/'rollback_hashes_1944_CE_context.json.xz');self.assertEqual(len(h['before']),26);self.assertEqual(h['before'],h['rollback']);self.assertEqual(h['after'],h['reapplied']);g=load(A.H/'sources/wikipedia_1944_ce_people_links.json.gz');self.assertEqual((len(g['people']),len(g['relationships']),len(g['event_roles'])),(9,7,9));self.assertTrue(all(not p['spawnable'] for p in g['people']));self.assertEqual(len(load(T.F/'pin_verification_1944_CE_context.json.xz')['identities']),14)
 def test_readme_archive(self):
  import sys;sys.path.insert(0,str(T.ROOT.parent/'worldfill'));import archived_history_reports as w
  b=w.read('README.original.md');self.assertEqual(len(b),545083);self.assertIn(b'World fill: recorded history first',b)
if __name__=='__main__':unittest.main()
