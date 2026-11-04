import copy,gzip,json,lzma,unittest
from pathlib import Path
import apply_1924_1931_ce_context as A
R=Path(__file__).resolve().parent;H=A.H

def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else lzma.open(p,'rt',encoding='utf8') if str(p).endswith('.xz') else open(p,encoding='utf8')) as f:return json.load(f)
class BatchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=A.load(A.M);cls.packs={p:load(H/p) for p in load(H/'index.json')['packs']};cls.graph=load(H/'sources/wikipedia_1924_1931_ce_people_links.json.gz')
 def test_installed_and_reversible(self):
  A.validate(self.m);m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=99
  with self.assertRaises(ValueError):A.validate(m)
  for u in self.m['updates']:
   rows=[e for d in self.packs.values() for e in d.get('events',[]) if isinstance(e,dict) and e.get('id')==u['event_id']];self.assertEqual(rows,[u['after']])
  for p in {u['pack'] for u in self.m['updates']}:
   group=[u for u in self.m['updates'] if u['pack']==p];old=A.transform(self.packs[p],group,True,[]);self.assertEqual(A.transform(old,group,False,[]),self.packs[p])
 def test_corrected_events(self):
  u={x['event_id']:x['after'] for x in self.m['updates']};self.assertEqual(len(u),13)
  self.assertEqual((u['wpy_9a61d0214b']['start'],u['wpy_9a61d0214b']['end']),(1925,1926))
  for i,lat,lon in [('wpy_8fd2011d89',51.83333,12.25),('wpr_6da4916f03',38.72528,-9.15),('wpr_6dc4030781',31.2325,121.46917),('wpw_56dd9be539',5.0731,103.01126),('wpw_ff17b1d97e',5.56667,7.63333),('wpw_73ad8a39c7',24.046222,121.130444),('wpw_dde84d123d',17.651784,95.7855),('wpr_24974b6550',20.886472,72.800944),('wpr_7f5a058f55',23.06,72.58083)]:self.assertEqual((u[i]['lat'],u[i]['lon']),(lat,lon))
  self.assertIn('1932',u['wpy_27b7b3dd6d']['name']);self.assertNotIn('200-mile',u['wpr_7f5a058f55']['name'])
 def test_graph(self):
  g=self.graph;ps={x['id'] for x in g['people']};idx={x.get('id') for d in self.packs.values() for x in d.get('events',[]) if isinstance(x,dict)}
  self.assertEqual((len(ps),len(g['relationships']),len(g['event_roles'])),(22,13,20));self.assertTrue(all(not x['spawnable'] for x in g['people']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']))
 def test_annual_inventories(self):
  for lo,hi,count,haz in [(1924,1929,1235,562),(1930,1931,412,187)]:
   a=load(R/f'focus/year_titles_{lo}_{hi}_CE.json')['results'];p=load(R/f'focus/year_wikitext_{lo}_{hi}_CE.json.xz')['pages'];self.assertEqual({x['canonical_title'] for x in a},{str(y) for y in range(lo,hi+1)});self.assertEqual({x['lastrevid'] for x in a},{x['revisions'][0]['revid'] for x in p});d=load(R/f'focus/indexed_start_inventory_{lo}_{hi}_CE.json.xz');self.assertEqual(len(d['rows']),count);self.assertEqual(sum('hazard' in x[0] for x in d['rows']),haz)
 def test_hashes_and_pins(self):
  d=load(R/'focus/rollback_hashes_1924_1931_CE_context.json.xz');self.assertEqual(len(d['before']),26);self.assertEqual(d['before'],d['rollback']);self.assertEqual(d['after'],d['reapplied']);self.assertEqual(len(load(R/'focus/pin_verification_1924_1931_CE_context.json.xz')['identities']),38)
if __name__=='__main__':unittest.main()
