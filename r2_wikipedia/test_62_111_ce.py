import copy,gzip,json,unittest
from pathlib import Path
import apply_62_111_ce_context as C
import apply_62_111_ce_hazards as H
import apply_62_111_ce_geologic_quarantine as Q
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
  cls.cm=C.load(C.M);cls.hm=H.load(H.M);cls.qm=Q.load(Q.M);cls.packs={p:load(DATA/p) for p in load(DATA/'index.json')['packs']};cls.graph=load(DATA/'sources/wikipedia_62_111_ce_people_links.json')
 def test_manifest_hashes(self):C.validate(self.cm);H.validate(self.hm);Q.validate(self.qm)
 def test_tamper_context(self):
  m=copy.deepcopy(self.cm);m['updates'][0]['after']['start']=68
  with self.assertRaises(ValueError):C.validate(m)
 def test_tamper_hazards(self):
  m=copy.deepcopy(self.hm);m['moves'][0]['after']['start']=13
  with self.assertRaises(ValueError):H.validate(m)
 def test_tamper_quarantine(self):
  m=copy.deepcopy(self.qm);m['records'][0]['source_index']+=1
  with self.assertRaises(ValueError):Q.validate(m)
 def test_25_indexed_after_images_once(self):
  target={r['event_id']:r['after'] for r in self.cm['updates']}|{r['event_id']:r['after'] for r in self.hm['moves']};found={x:[] for x in target}
  for p,d in self.packs.items():
   for sec in ('events','sites'):
    for r in d.get(sec,[]):
     if isinstance(r,dict) and r.get('id') in target:found[r['id']].append(r)
  self.assertEqual(len(target),25)
  for k,v in target.items():self.assertEqual(found[k],[v],k)
 def test_logical_dependency_roundtrip(self):
  d=copy.deepcopy(self.packs);d[H.HAZ]=Q.transform(d[H.HAZ],self.qm,True)
  for p in (H.HAZ,H.REG):d[p]=H.transform(d[p],self.hm,p,True)
  for p in {u['pack'] for u in self.cm['updates']}:d[p]=C.transform(d[p],[u for u in self.cm['updates'] if u['pack']==p],True)
  for p in {u['pack'] for u in self.cm['updates']}:d[p]=C.transform(d[p],[u for u in self.cm['updates'] if u['pack']==p],False)
  for p in (H.HAZ,H.REG):d[p]=H.transform(d[p],self.hm,p,False)
  d[H.HAZ]=Q.transform(d[H.HAZ],self.qm,False)
  self.assertEqual(d,self.packs)
 def test_hazards_removed(self):
  ids={r['id'] for r in self.packs[H.HAZ]['events']};self.assertTrue(ids.isdisjoint(H.IDS|Q.IDS));self.assertTrue(all(r['after']['effect']=='note' for r in self.hm['moves']))
 def test_quarantine_nonindexed(self):
  ids=[r.get('id') for d in self.packs.values() for sec in ('events','sites') for r in d.get(sec,[]) if isinstance(r,dict)];self.assertTrue(set(ids).isdisjoint(Q.IDS));g=load(DATA/'sources/geologic_misdates_62_111_ce.json');self.assertEqual(g['records'],self.qm['records'])
 def test_key_dates_and_names(self):
  a={u['event_id']:u['after'] for u in self.cm['updates']};self.assertEqual(a['wpy_530f20b968']['start'],106);self.assertEqual(a['wpy_7092bfdc7e']['start'],106);self.assertEqual(a['wpy_40c129ff76']['lat'],31.31556);self.assertEqual(a['wpy_b58087f14e']['effect'],'note');self.assertEqual(a['wpy_39efe9cc3a']['effect'],'disruption');self.assertIn('First Battle',a['q1476280']['name']);self.assertIn('Second Battle',a['q8244453']['name'])
 def test_noaa_deaths_category_not_exact_count(self):
  for id in ('hz_da69f6810d','hz_dda59a7e23'):
   a=next(x['after'] for x in self.hm['moves'] if x['event_id']==id);self.assertNotIn('3 dead',a['name']);self.assertIn('deathsAmountOrder=3',a['r2SourceEvidence']['review_note'])
 def test_graph(self):
  g=self.graph;ps={r['id'] for r in g['people']};idx={r.get('id') for d in self.packs.values() for sec in ('events','sites') for r in d.get(sec,[]) if isinstance(r,dict)}
  self.assertEqual(len(ps),len(g['people']));self.assertTrue(all(not p['spawnable'] for p in g['people']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']))
 def test_title_resolution(self):
  a=load(ROOT/'r2_wikipedia/focus/year_titles_62_111_CE.json')['results'];self.assertEqual(len(a),50);self.assertTrue(all(r['status']=='resolved' for r in a));self.assertEqual(len({r['canonical_title'] for r in a}),50)
if __name__=='__main__':unittest.main()
