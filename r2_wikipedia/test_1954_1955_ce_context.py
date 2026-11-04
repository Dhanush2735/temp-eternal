import copy,json,lzma,unittest
from pathlib import Path
import apply_1954_1955_ce_context as A
import fast_year_triage as T
import archive_generated_aux as aux
R=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.m=A.load(A.M);cls.packs={p:A.load(A.H/p) for p in A.load(A.H/'index.json')['packs']};cls.g=A.load(A.H/'sources/wikipedia_1954_1955_ce_people_links.json.gz')
 def test_manifest_install_and_undo(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['lat']=0
  with self.assertRaises(ValueError):A.validate(m)
  for x in self.m['updates']:
   rows=[e for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict) and e.get('id')==x['event_id']];self.assertEqual(rows,[x['after']]);self.assertEqual(tuple(x['before'][k] for k in ('start','end','kind','effect')),tuple(x['after'][k] for k in ('start','end','kind','effect')))
  us=self.m['updates'];p=us[0]['pack'];old=A.transform(self.packs[p],us,True,[]);self.assertEqual(A.transform(old,us,False,[]),self.packs[p])
 def test_locations(self):
  x={u['event_id']:u['after'] for u in self.m['updates']};self.assertEqual((x['wpr_083711ce87']['lat'],x['wpr_083711ce87']['lon'],x['wpr_083711ce87']['radiusKm']),(48.8567,2.3522,20));self.assertEqual((x['wpr_ae7258df8c']['lat'],x['wpr_ae7258df8c']['lon']),(33.81,-90.53028));self.assertIn('disputed',x['wpr_ae7258df8c']['name'])
 def test_years_and_inventory(self):
  pages=T.verify(1954,1955);self.assertEqual({p['title'] for p in pages},{'1954','1955'});d=T.load(T.paths(1954,1955)[2]);self.assertEqual(len(d['rows']),565);self.assertEqual(sum('hazard' in r[0] for r in d['rows']),211)
 def test_graph(self):
  g=self.g;ps={x['id'] for x in g['people']};events={e.get('id') for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict)};self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(10,6,10));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in events for x in g['event_roles']))
 def test_hashes_pins(self):
  with lzma.open(R/'focus/rollback_hashes_1954_1955_CE_context.json.xz','rt') as f:h=json.load(f)
  self.assertEqual(len(h['before']),26);self.assertEqual(h['before'],h['rollback']);self.assertEqual(h['after'],h['reapplied'])
  with lzma.open(R/'focus/pin_verification_1954_1955_CE_context.json.xz','rt') as f:p=json.load(f)
  self.assertEqual(len(p['identities']),12)
 def test_aux_archives(self):
  self.assertEqual(len(aux.read('harvest/events_v2_raw.jsonl.pages.json')),59325);self.assertEqual(len(aux.read('survey/sources/sources_density.json')),25400)
if __name__=='__main__':unittest.main()
