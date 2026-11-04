import copy,gzip,json,lzma,unittest
from pathlib import Path
import apply_1932_1937_ce_context as A
R=Path(__file__).resolve().parent;H=A.H

def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else lzma.open(p,'rt',encoding='utf8') if str(p).endswith('.xz') else open(p,encoding='utf8')) as f:return json.load(f)
class BatchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=A.load(A.M);cls.packs={p:load(H/p) for p in load(H/'index.json')['packs']};cls.graph=load(H/'sources/wikipedia_1932_1937_ce_people_links.json.gz')
 def test_installed_and_reversible(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=99
  with self.assertRaises(ValueError):A.validate(m)
  for u in self.m['updates']:
   rows=[e for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict) and e.get('id')==u['event_id']];self.assertEqual(rows,[u['after']])
  for p in {u['pack'] for u in self.m['updates']}:
   group=[u for u in self.m['updates'] if u['pack']==p];old=A.transform(self.packs[p],group,True,[]);self.assertEqual(A.transform(old,group,False,[]),self.packs[p])
 def test_corrected_events(self):
  u={x['event_id']:x['after'] for x in self.m['updates']};self.assertEqual(len(u),10)
  self.assertEqual((u['wpy_497821cd7e']['start'],u['wpy_497821cd7e']['end']),(1935,1936))
  for i,lat,lon in [('wpy_37f5585e4a',13.7525,100.49417),('wpr_3a13198f25',55.05,-7.26667),('wpw_e48e6e0990',43.8225,87.6125),('wpr_b9256dd425',34.26111,108.94222),('wpw_a74e015e3d',39.4681,75.9938),('wpr_66f43881b1',-6.73028,147.00083)]:self.assertEqual((u[i]['lat'],u[i]['lon']),(lat,lon))
  self.assertNotIn('April 11',u['wpr_dd47642564']['name']);self.assertIn('Lae',u['wpr_66f43881b1']['name'])
 def test_graph(self):
  g=self.graph;ps={x['id'] for x in g['people']};idx={x.get('id') for d in self.packs.values() for x in d.get('events',[]) if isinstance(x,dict)}
  self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(17,10,20));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']))
 def test_annual_inventories(self):
  for lo,hi,count,haz in [(1932,1934,798,345),(1935,1936,429,202),(1937,1937,251,102)]:
   a=load(R/f'focus/year_titles_{lo}_{hi}_CE.json')['results'];p=load(R/f'focus/year_wikitext_{lo}_{hi}_CE.json.xz')['pages'];self.assertEqual({x['canonical_title'] for x in a},{str(y) for y in range(lo,hi+1)});self.assertEqual({x['lastrevid'] for x in a},{x['revisions'][0]['revid'] for x in p});d=load(R/f'focus/indexed_start_inventory_{lo}_{hi}_CE.json.xz');self.assertEqual(len(d['rows']),count);self.assertEqual(sum('hazard' in x[0] for x in d['rows']),haz)
 def test_hashes_and_pins(self):
  d=load(R/'focus/rollback_hashes_1932_1937_CE_context.json.xz');self.assertEqual(len(d['before']),26);self.assertEqual(d['before'],d['rollback']);self.assertEqual(d['after'],d['reapplied']);self.assertEqual(len(load(R/'focus/pin_verification_1932_1937_CE_context.json.xz')['identities']),33)
if __name__=='__main__':unittest.main()
