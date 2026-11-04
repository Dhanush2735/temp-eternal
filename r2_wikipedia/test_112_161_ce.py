import copy,gzip,json,unittest
from pathlib import Path
import apply_112_161_ce_context as C
import apply_112_161_ce_hazards as H
ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
def load(p):
 if not Path(p).exists() and Path(p).name.endswith('_people_links.json'):
  import people_graph_archive
  return people_graph_archive.load_json(p)
 if not Path(p).exists() and Path(p).name.startswith('year_titles_'):
  import title_archive
  return title_archive.load(p)
 with (gzip.open(p,'rt') if str(p).endswith('.gz') else open(p)) as f:return json.load(f)
class BatchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.cm=C.load(C.M);cls.hm=H.load(H.M);cls.packs={p:load(DATA/p) for p in load(DATA/'index.json')['packs']};cls.graph=load(DATA/'sources/wikipedia_112_161_ce_people_links.json')
 def test_manifest_hashes(self):C.validate(self.cm);H.validate(self.hm)
 def test_context_tamper(self):
  m=copy.deepcopy(self.cm);m['updates'][0]['after']['start']=132
  with self.assertRaises(ValueError):C.validate(m)
 def test_hazard_tamper(self):
  m=copy.deepcopy(self.hm);m['moves'][0]['after']['start']=100
  with self.assertRaises(ValueError):H.validate(m)
 def test_after_images_are_unique(self):
  targets={x['event_id']:x['after'] for x in self.cm['updates']}|{x['event_id']:x['after'] for x in self.hm['moves']};self.assertEqual(len(targets),30);found={i:[] for i in targets}
  for d in self.packs.values():
   for sec in ('events','sites'):
    for r in d.get(sec,[]):
     if isinstance(r,dict) and r.get('id') in targets:found[r['id']].append(r)
  for i,a in targets.items():self.assertEqual(found[i],[a],i)
 def test_dependency_roundtrip(self):
  d=copy.deepcopy(self.packs)
  for p in (H.HAZ,H.REG):d[p]=H.transform(d[p],self.hm,p,True)
  for p in {u['pack'] for u in self.cm['updates']}:d[p]=C.transform(d[p],[u for u in self.cm['updates'] if u['pack']==p],True)
  for p in {u['pack'] for u in self.cm['updates']}:d[p]=C.transform(d[p],[u for u in self.cm['updates'] if u['pack']==p],False)
  for p in (H.HAZ,H.REG):d[p]=H.transform(d[p],self.hm,p,False)
  self.assertEqual(d,self.packs)
 def test_previous_batch_layered_roundtrip(self):
  import apply_62_111_ce_context as OC, apply_62_111_ce_hazards as OH, apply_62_111_ce_geologic_quarantine as OQ
  d=copy.deepcopy(self.packs)
  for p in (H.HAZ,H.REG):d[p]=H.transform(d[p],self.hm,p,True)
  for p in {u['pack'] for u in self.cm['updates']}:d[p]=C.transform(d[p],[u for u in self.cm['updates'] if u['pack']==p],True)
  baseline=copy.deepcopy(d);om=OC.load(OC.M);oh=OH.load(OH.M);oq=OQ.load(OQ.M)
  d[OH.HAZ]=OQ.transform(d[OH.HAZ],oq,True)
  for p in (OH.HAZ,OH.REG):d[p]=OH.transform(d[p],oh,p,True)
  for p in {u['pack'] for u in om['updates']}:d[p]=OC.transform(d[p],[u for u in om['updates'] if u['pack']==p],True)
  for p in {u['pack'] for u in om['updates']}:d[p]=OC.transform(d[p],[u for u in om['updates'] if u['pack']==p],False)
  for p in (OH.HAZ,OH.REG):d[p]=OH.transform(d[p],oh,p,False)
  d[OH.HAZ]=OQ.transform(d[OH.HAZ],oq,False)
  self.assertEqual(d,baseline)
 def test_hazards_moved_only_once(self):
  ids={r['id'] for r in self.packs[H.HAZ]['events']};self.assertTrue(ids.isdisjoint(H.IDS));self.assertTrue(all(r['after']['effect']=='note' for r in self.hm['moves']))
 def test_dates(self):
  a={u['event_id']:u['after'] for u in self.cm['updates']};self.assertEqual(a['q11794928']['start'],135);self.assertEqual(a['wpy_4c7698553a']['start'],110);self.assertEqual(a['wpy_9ccaa6a1a4']['lat'],31.77668);self.assertEqual(a['q85719675']['effect'],'note');self.assertEqual(a['wpy_f9f2ccf7d6']['effect'],'note')
 def test_noaa_categories(self):
  a={u['event_id']:u['after'] for u in self.cm['updates']}
  for i in ('hz_14cac35bab','hz_78c7b36c0d','hz_d43e0a0000'):self.assertNotIn(' dead',a[i]['name']);self.assertEqual(a[i]['effect'],'disruption')
 def test_volcanic_uncertainty(self):
  a={u['event_id']:u['after'] for u in self.hm['moves']};self.assertIn('±200',a['hz_a0e4dba4eb']['name']);self.assertIn('±300',a['hz_af9ac31f71']['name']);self.assertIn('±50',a['hz_a73f3fb033']['name']);self.assertNotEqual(a['hz_bf50663c5a']['id'],a['hz_0e0e1fed0e']['id'])
 def test_graph(self):
  g=self.graph;ps={r['id'] for r in g['people']};idx={r.get('id') for d in self.packs.values() for sec in ('events','sites') for r in d.get(sec,[]) if isinstance(r,dict)}
  self.assertEqual(len(ps),len(g['people']));self.assertTrue(all(not p['spawnable'] for p in g['people']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']))
 def test_title_resolution(self):
  a=load(ROOT/'r2_wikipedia/focus/year_titles_112_161_CE.json')['results'];self.assertEqual(len(a),50);self.assertTrue(all(r['status']=='resolved' for r in a));self.assertEqual(len({r['canonical_title'] for r in a}),50)
if __name__=='__main__':unittest.main()
