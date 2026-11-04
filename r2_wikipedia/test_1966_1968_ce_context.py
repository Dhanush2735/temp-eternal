import copy,hashlib,json,lzma,unittest
from pathlib import Path
import apply_1966_1968_ce_context as A
import fast_year_triage as T
R=Path(__file__).resolve().parent
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=A.load(A.M);cls.packs={p:A.load(A.H/p) for p in A.load(A.H/'index.json')['packs']};cls.g=A.load(A.H/'sources/wikipedia_1966_1968_ce_people_links.json.gz')
 def test_manifest(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['name']='tampered'
  with self.assertRaises(ValueError):A.validate(m)
  self.assertEqual(len(self.m['updates']),4);self.assertEqual(self.m['additions'],[])
 def test_installed_unique_and_stable_fields(self):
  for u in self.m['updates']:
   rows=[e for d in self.packs.values() for section in ('events','sites') for e in d.get(section,[]) if isinstance(e,dict) and e.get('id')==u['event_id']]
   self.assertEqual(rows,[u['after']]);self.assertEqual(tuple(u['before'][k] for k in ('start','end','kind','effect')),tuple(u['after'][k] for k in ('start','end','kind','effect')))
 def test_roundtrip_and_refuse_change(self):
  us=self.m['updates'];d=self.packs[us[0]['pack']];old=A.transform(d,us,True,[]);self.assertEqual(A.transform(old,us,False,[]),d)
  altered=copy.deepcopy(old);next(e for e in altered['events'] if e.get('id')==us[0]['event_id'])['lat']=0
  with self.assertRaises(ValueError):A.transform(altered,us,False,[])
 def test_locations_and_claims(self):
  x={u['event_id']:u['after'] for u in self.m['updates']}
  for id,coord in [('wpr_4316b31a87',(34.9,-117.017)),('wpr_6210741a92',(28.608389,-80.604333)),('wpr_8b22652adb',(38.7088,-9.2608)),('wpr_eb98ba54a1',(28.52194,-80.56139))]:self.assertEqual((x[id]['lat'],x[id]['lon']),coord)
  self.assertNotIn('first live television broadcast from orbit',x['wpr_eb98ba54a1']['name']);self.assertTrue(all(e['r2SourceEvidence']['sources'] for e in x.values()))
 def test_annual_inventory(self):
  pages=T.verify(1966,1968);self.assertEqual({p['title'] for p in pages},{'1966','1967','1968'});d=T.load(T.paths(1966,1968)[2]);self.assertEqual(len(d['rows']),1121);self.assertEqual(sum('hazard' in r[0] for r in d['rows']),290)
 def test_graph(self):
  g=self.g;ps={x['id'] for x in g['people']};events={e.get('id') for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict)};self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(10,7,10));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in events for x in g['event_roles']))
 def test_hashes_pins(self):
  with lzma.open(R/'focus/rollback_hashes_1966_1968_CE_context.json.xz','rt') as f:h=json.load(f)
  self.assertEqual(len(h['before']),26);self.assertEqual(h['before'],h['rollback']);self.assertEqual(h['after'],h['reapplied']);self.assertEqual({p for p in h['before'] if h['before'][p]!=h['after'][p]},{'events_wikipedia_regional.json.gz'})
  for p in h['after']:self.assertEqual(hashlib.sha256((A.H/p).read_bytes()).hexdigest(),h['after'][p])
  with lzma.open(R/'focus/pin_verification_1966_1968_CE_context.json.xz','rt') as f:pin=json.load(f)
  self.assertEqual(len(pin['identities']),14);self.assertEqual(len({x['pageid'] for x in pin['identities']}),14)
if __name__=='__main__':unittest.main()
