import copy,gzip,lzma,json,unittest
from pathlib import Path
import apply_1062_1111_ce_context as C
import apply_1062_1111_ce_hazards as H
ROOT=Path(__file__).resolve().parent.parent;DATA=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
def load(p):
 if not Path(p).exists() and Path(p).name.endswith('_people_links.json'):
  import people_graph_archive
  return people_graph_archive.load_json(p)
 if not Path(p).exists() and Path(p).name.startswith('year_titles_'):
  import title_archive
  return title_archive.load(p)
 if not Path(p).exists() and Path(p).name.startswith('year_wikitext_'):
  from annual_archive import load_json
  return load_json(p)
 with (gzip.open(p,'rt') if str(p).endswith('.gz') else lzma.open(p,'rt') if str(p).endswith('.xz') else open(p)) as f:return json.load(f)
class BatchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.cm=C.load(C.M);cls.hm=H.load(H.M);cls.packs={p:load(DATA/p) for p in load(DATA/'index.json')['packs']};cls.graph=load(DATA/'sources/wikipedia_1062_1111_ce_people_links.json')
 def test_manifest_hashes(self):C.validate(self.cm);H.validate(self.hm)
 def test_context_tamper(self):
  m=copy.deepcopy(self.cm);m['updates'][0]['after']['start']=257
  with self.assertRaises(ValueError):C.validate(m)
 def test_hazard_tamper(self):
  m=copy.deepcopy(self.hm);m['moves'][0]['after']['start']=221
  with self.assertRaises(ValueError):H.validate(m)
 def test_unique_after_images(self):
  targets={x['event_id']:x['after'] for x in self.cm['updates']}|{x['event_id']:x['after'] for x in self.hm['moves']}|{x['event']['id']:x['event'] for x in self.cm['additions']};self.assertEqual(len(targets),40);found={i:[] for i in targets}
  for d in self.packs.values():
   for sec in ('events','sites'):
    for row in d.get(sec,[]):
     if isinstance(row,dict) and row.get('id') in targets:found[row['id']].append(row)
  for i,a in targets.items():self.assertEqual(found[i],[a],i)
 def reverse_batch(self):
  d=copy.deepcopy(self.packs)
  for p in (H.HAZ,H.REG):d[p]=H.transform(d[p],self.hm,p,True)
  for p in {u['pack'] for u in self.cm['updates']}|{a['pack'] for a in self.cm['additions']}:
   d[p]=C.transform(d[p],[u for u in self.cm['updates'] if u['pack']==p],True,[a for a in self.cm['additions'] if a['pack']==p])
  return d
 def test_roundtrip(self):
  d=self.reverse_batch()
  for p in {u['pack'] for u in self.cm['updates']}|{a['pack'] for a in self.cm['additions']}:
   d[p]=C.transform(d[p],[u for u in self.cm['updates'] if u['pack']==p],False,[a for a in self.cm['additions'] if a['pack']==p])
  for p in (H.HAZ,H.REG):d[p]=H.transform(d[p],self.hm,p,False)
  self.assertEqual(d,self.packs)
 def test_previous_batch_in_order(self):
  import apply_1012_1061_ce_context as OC, apply_1012_1061_ce_hazards as OH
  d=self.reverse_batch();baseline=copy.deepcopy(d);om=OC.load(OC.M);oh=OH.load(OH.M)
  for p in (OH.HAZ,OH.REG):d[p]=OH.transform(d[p],oh,p,True)
  for p in {u['pack'] for u in om['updates']}:d[p]=OC.transform(d[p],[u for u in om['updates'] if u['pack']==p],True,[])
  for p in {u['pack'] for u in om['updates']}:d[p]=OC.transform(d[p],[u for u in om['updates'] if u['pack']==p],False,[])
  for p in (OH.HAZ,OH.REG):d[p]=OH.transform(d[p],oh,p,False)
  self.assertEqual(d,baseline)
 def test_hazards_moved(self):
  ids={r['id'] for r in self.packs[H.HAZ]['events']};self.assertTrue(ids.isdisjoint(H.IDS));self.assertTrue(all(r['after']['effect']=='note' for r in self.hm['moves']))
 def test_key_corrections(self):
  a={u['event_id']:u['after'] for u in self.cm['updates']}
  self.assertEqual((a['wpd_1444ab0382']['lat'],a['wpd_1444ab0382']['lon']),(44.576,10.456))
  self.assertEqual(a['wpd_7082013e4a']['effect'],'note')
  self.assertEqual(a['wpd_3ec6c848d0']['lat'],41.7151)
  self.assertIn('evidence of teaching',a['wpd_364b4743c0']['name'])
  self.assertEqual(a['wpw_4a29526b17']['end'],1078)
  self.assertNotIn('3 dead',a['hz_4391ab72c7']['name'])
 def test_hazard_notes(self):
  a={u['event_id']:u['after'] for u in self.hm['moves']}
  self.assertIn('±200',a['hz_d70df63668']['name'])
  self.assertIn('uncalibrated',a['hz_19eb9af50e']['r2SourceEvidence']['review_note'])
  self.assertEqual(a['hz_0fadce182d']['effect'],'note')
  self.assertIn('Aqaba',a['hz_0fadce182d']['r2SourceEvidence']['review_note'])
 def test_graph(self):
  g=self.graph;ps={r['id'] for r in g['people']};idx={r.get('id') for d in self.packs.values() for sec in ('events','sites') for r in d.get(sec,[]) if isinstance(r,dict)}
  self.assertEqual(len(ps),len(g['people']));self.assertTrue(all(not p['spawnable'] for p in g['people']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']))
 def test_title_resolution_and_pinned_text(self):
  a=load(ROOT/'r2_wikipedia/focus/year_titles_1062_1111_CE.json')['results'];self.assertEqual(len(a),50);self.assertTrue(all(r['status']=='resolved' for r in a));self.assertEqual(len({r['canonical_title'] for r in a}),50)
  p=load(ROOT/'r2_wikipedia/focus/year_wikitext_1062_1111_CE.json.xz')['pages'];self.assertEqual({x['lastrevid'] for x in a},{x['revisions'][0]['revid'] for x in p});self.assertTrue(all('disambiguation' not in x.get('pageprops',{}) for x in p))
if __name__=='__main__':unittest.main()
