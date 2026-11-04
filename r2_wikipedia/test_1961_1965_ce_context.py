import copy,json,lzma,unittest,sys
from pathlib import Path
import apply_1961_1965_ce_context as A
import fast_year_triage as T
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/'worldfill'))
import archived_history_reports as archive
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=A.load(A.M);cls.packs={p:A.load(A.H/p) for p in A.load(A.H/'index.json')['packs']};cls.g=A.load(A.H/'sources/wikipedia_1961_1965_ce_people_links.json.gz')
 def test_manifest_install_and_roundtrip(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['name']='tampered'
  with self.assertRaises(ValueError):A.validate(m)
  for x in self.m['updates']:
   rows=[e for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict) and e.get('id')==x['event_id']];self.assertEqual(rows,[x['after']]);self.assertEqual(tuple(x['before'][k] for k in ('start','end','kind','effect')),tuple(x['after'][k] for k in ('start','end','kind','effect')))
  for p in {x['pack'] for x in self.m['updates']}:
   us=[x for x in self.m['updates'] if x['pack']==p];old=A.transform(self.packs[p],us,True,[]);self.assertEqual(A.transform(old,us,False,[]),self.packs[p])
 def test_locations(self):
  x={u['event_id']:u['after'] for u in self.m['updates']};self.assertEqual((x['wpy_028f5bfc6f']['lat'],x['wpy_028f5bfc6f']['lon']),(52.5075,13.39028));self.assertEqual((x['wpr_7d49a97c1d']['lat'],x['wpr_7d49a97c1d']['lon']),(45.92028,63.34222));self.assertEqual((x['wpr_b7d9bb594e']['lat'],x['wpr_b7d9bb594e']['lon']),(53.209375,80.80395));self.assertEqual((x['wpy_2074cb5a23']['lat'],x['wpy_2074cb5a23']['lon']),(15.219,108.913))
 def test_years_and_inventory(self):
  pages=T.verify(1961,1965);self.assertEqual({p['title'] for p in pages},{str(n) for n in range(1961,1966)});d=T.load(T.paths(1961,1965)[2]);self.assertEqual(len(d['rows']),1673);self.assertEqual(sum('hazard' in r[0] for r in d['rows']),510)
 def test_graph(self):
  g=self.g;ps={x['id'] for x in g['people']};events={e.get('id') for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict)};self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(8,4,9));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in events for x in g['event_roles']))
 def test_hashes_pins(self):
  with lzma.open(R/'focus/rollback_hashes_1961_1965_CE_context.json.xz','rt') as f:h=json.load(f)
  self.assertEqual(len(h['before']),26);self.assertEqual(h['before'],h['rollback']);self.assertEqual(h['after'],h['reapplied']);self.assertEqual({p for p in h['before'] if h['before'][p]!=h['after'][p]},{'events_wikipedia.json.gz','events_wikipedia_regional.json.gz'})
  with lzma.open(R/'focus/pin_verification_1961_1965_CE_context.json.xz','rt') as f:p=json.load(f)
  self.assertEqual(len(p['identities']),16)
 def test_prototype_archives(self):
  self.assertEqual(len(archive.read('npc_talk_ui_preview.html')),55091);self.assertEqual(len(archive.read('npc_knowledge_ui_preview.html')),101962)
if __name__=='__main__':unittest.main()
