import copy,json,lzma,unittest
from pathlib import Path
import apply_1956_1960_ce_context as A
import fast_year_triage as T
import archive_generated_aux as aux
R=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=A.load(A.M);cls.packs={p:A.load(A.H/p) for p in A.load(A.H/'index.json')['packs']};cls.g=A.load(A.H/'sources/wikipedia_1956_1960_ce_people_links.json.gz')
 def test_manifest_install_and_roundtrip(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['name']='tampered'
  with self.assertRaises(ValueError):A.validate(m)
  for x in self.m['updates']:
   rows=[e for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict) and e.get('id')==x['event_id']];self.assertEqual(rows,[x['after']]);self.assertEqual(tuple(x['before'][k] for k in ('start','end','kind','effect')),tuple(x['after'][k] for k in ('start','end','kind','effect')))
  for p in {x['pack'] for x in self.m['updates']}:
   us=[x for x in self.m['updates'] if x['pack']==p];old=A.transform(self.packs[p],us,True,[]);self.assertEqual(A.transform(old,us,False,[]),self.packs[p])
 def test_locations_and_qualified_claims(self):
  x={u['event_id']:u['after'] for u in self.m['updates']};self.assertEqual((x['wpy_dfd3a90770']['lat'],x['wpy_dfd3a90770']['lon']),(-90.0,0.0));self.assertEqual((x['wpr_ab3d2c7806']['lat'],x['wpr_ab3d2c7806']['lon']),(28.43944,-80.57333));self.assertEqual((x['wpy_c053212422']['lat'],x['wpy_c053212422']['lon']),(40.70194,-73.96889));self.assertIn('about 300 kilotons',x['wpr_3f43f582c3']['name']);self.assertIn('over 100',x['wpy_2157f80113']['name'])
 def test_years_and_inventory(self):
  pages=T.verify(1956,1960);self.assertEqual({p['title'] for p in pages},{str(n) for n in range(1956,1961)});d=T.load(T.paths(1956,1960)[2]);self.assertEqual(len(d['rows']),1438);self.assertEqual(sum('hazard' in r[0] for r in d['rows']),554)
 def test_graph(self):
  g=self.g;ps={x['id'] for x in g['people']};events={e.get('id') for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict)};self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(14,5,14));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in events for x in g['event_roles']))
 def test_hashes_pins(self):
  with lzma.open(R/'focus/rollback_hashes_1956_1960_CE_context.json.xz','rt') as f:h=json.load(f)
  self.assertEqual(len(h['before']),26);self.assertEqual(h['before'],h['rollback']);self.assertEqual(h['after'],h['reapplied']);self.assertEqual({p for p in h['before'] if h['before'][p]!=h['after'][p]},{'events_wikipedia.json.gz','events_wikipedia_regional.json.gz'})
  with lzma.open(R/'focus/pin_verification_1956_1960_CE_context.json.xz','rt') as f:p=json.load(f)
  self.assertEqual(len(p['identities']),25)
 def test_aux_archives(self):
  self.assertEqual(len(aux.read('survey/sources/sources_summary.json')),11860);self.assertEqual(len(aux.read('worldfill/sources/money/wikidata_currencies.tsv')),282865)
if __name__=='__main__':unittest.main()
