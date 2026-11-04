import copy,gzip,json,lzma,unittest,sys
from pathlib import Path
import apply_1942_ce_context as A
R=Path(__file__).resolve().parent;H=A.H
def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else lzma.open(p,'rt',encoding='utf8') if str(p).endswith('.xz') else open(p,encoding='utf8')) as f:return json.load(f)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.m=A.load(A.M);cls.packs={p:load(H/p) for p in load(H/'index.json')['packs']};cls.graph=load(H/'sources/wikipedia_1942_ce_people_links.json.gz')
 def test_installed_and_reversible(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=99
  with self.assertRaises(ValueError):A.validate(m)
  for u in self.m['updates']:
   rows=[e for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict) and e.get('id')==u['event_id']];self.assertEqual(rows,[u['after']])
  for p in {u['pack'] for u in self.m['updates']}:
   group=[u for u in self.m['updates'] if u['pack']==p];old=A.transform(self.packs[p],group,True,[]);self.assertEqual(A.transform(old,group,False,[]),self.packs[p])
 def test_locations_and_uncertainty(self):
  u={x['event_id']:x['after'] for x in self.m['updates']};self.assertEqual(len(u),4)
  for i,lat,lon in [('wpy_75f2c588cd',51.131,12.8074),('wpy_0ed4b4b0b8',-11.55,130.933),('wpy_0a5ec2721b',51.44722,23.59361),('wpy_a2eeb16145',52.63111,22.05306)]:self.assertEqual((u[i]['lat'],u[i]['lon']),(lat,lon))
  for i in ['wpy_0a5ec2721b','wpy_a2eeb16145']:self.assertIn('estimated',u[i]['name']);self.assertEqual(u[i]['effect'],'political')
 def test_graph(self):
  g=self.graph;ps={x['id'] for x in g['people']};idx={x.get('id') for d in self.packs.values() for x in d.get('events',[]) if isinstance(x,dict)}
  self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(10,4,13));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']))
 def test_annual_inventory(self):
  a=load(R/'focus/year_titles_1942_1942_CE.json')['results'];p=load(R/'focus/year_wikitext_1942_1942_CE.json.xz')['pages'];self.assertEqual({x['canonical_title'] for x in a},{'1942'});self.assertEqual({x['lastrevid'] for x in a},{x['revisions'][0]['revid'] for x in p});d=load(R/'focus/indexed_start_inventory_1942_1942_CE.json.xz');self.assertEqual(len(d['rows']),409);self.assertEqual(sum('hazard' in x[0] for x in d['rows']),85)
 def test_hashes_pins(self):
  d=load(R/'focus/rollback_hashes_1942_CE_context.json.xz');self.assertEqual(len(d['before']),26);self.assertEqual(d['before'],d['rollback']);self.assertEqual(d['after'],d['reapplied']);self.assertEqual(len(load(R/'focus/pin_verification_1942_CE_context.json.xz')['identities']),15)
 def test_historical_archives(self):
  sys.path.insert(0,str(R.parent/'eternal'));import archived_generated_reports as e
  self.assertEqual(len(e.read('FIELD_DOSSIER.md')),65046);self.assertEqual(len(e.read('field_spec.json')),54786)
if __name__=='__main__':unittest.main()
