import copy,gzip,json,unittest
from pathlib import Path
import apply_39_bce_11_ce_context as C
import apply_39_bce_11_ce_hazards as H
import apply_39_bce_11_ce_geologic_quarantine as Q
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
  cls.cm=C.load(C.M);cls.hm=H.load(H.M);cls.qm=Q.load(Q.M);cls.packs={p:load(DATA/p) for p in load(DATA/'index.json')['packs']};cls.graph=load(DATA/'sources/wikipedia_39_bce_11_ce_people_links.json')
 def test_context_hash(self):C.validate(self.cm)
 def test_hazard_hash(self):H.validate(self.hm)
 def test_context_tamper_rejected(self):
  a=copy.deepcopy(self.cm);a['updates'][0]['after']['name']='tampered'
  with self.assertRaises(ValueError):C.validate(a)
 def test_hazard_tamper_rejected(self):
  a=copy.deepcopy(self.hm);a['moves'][0]['after']['start']=7
  with self.assertRaises(ValueError):H.validate(a)
 def test_indexed_after_images_unique(self):
  targets={x['event_id']:x['after'] for x in self.cm['updates']}|{x['event_id']:x['after'] for x in self.hm['moves']};found={k:[] for k in targets}
  for p,d in self.packs.items():
   for sec in ('events','sites'):
    for row in d.get(sec,[]):
     if isinstance(row,dict) and row.get('id') in targets:found[row['id']].append(row)
  for k,v in targets.items():self.assertEqual(found[k],[v],k)
 def test_dependency_order_roundtrip(self):
  # Reverse hazards first, then context, reapply in reverse order, without writes.
  docs=copy.deepcopy(self.packs)
  docs[H.HAZ]=Q.transform(docs[H.HAZ],self.qm,True)
  for p in (H.HAZ,H.REG):docs[p]=H.transform(docs[p],self.hm,p,True)
  for p in {u['pack'] for u in self.cm['updates']}:
   us=[u for u in self.cm['updates'] if u['pack']==p];docs[p]=C.transform(docs[p],us,True)
  for p in {u['pack'] for u in self.cm['updates']}:
   us=[u for u in self.cm['updates'] if u['pack']==p];docs[p]=C.transform(docs[p],us,False)
  for p in (H.HAZ,H.REG):docs[p]=H.transform(docs[p],self.hm,p,False)
  docs[H.HAZ]=Q.transform(docs[H.HAZ],self.qm,False)
  self.assertEqual(docs,self.packs)
 def test_four_misdated_hazards_not_in_damage_pack(self):
  ids={x['id'] for x in self.packs[H.HAZ]['events']};self.assertTrue(H.IDS.isdisjoint(ids));self.assertTrue(all(x['after']['effect']=='note' for x in self.hm['moves']))
 def test_geological_quarantine(self):
  Q.validate(self.qm);ids={x['id'] for x in self.packs[H.HAZ]['events']};self.assertTrue(Q.IDS.isdisjoint(ids));saved=load(DATA/'sources/geologic_misdates_39_bce_11_ce.json');self.assertEqual(saved['records'],self.qm['records'])
 def test_selected_corrections(self):
  a={x['event_id']:x['after'] for x in self.cm['updates']};self.assertEqual(a['q3498428']['start'],-38);self.assertEqual(a['wpy_27ac4aa82c']['start'],-33);self.assertEqual(a['wpw_cb59efcb75']['start'],1955);self.assertEqual(a['q1265861']['end'],10)
 def test_graph_references(self):
  people={p['id'] for p in self.graph['people']};idx={e.get('id') for d in self.packs.values() for sec in ('events','sites') for e in d.get(sec,[]) if isinstance(e,dict)}
  self.assertEqual(len(people),len(self.graph['people']));self.assertTrue(all(not p['spawnable'] for p in self.graph['people']));self.assertTrue(all(r['from'] in people and r['to'] in people for r in self.graph['relationships']));self.assertTrue(all(r['person_id'] in people and r['event_id'] in idx for r in self.graph['event_roles']))
 def test_ce_titles_are_year_redirects_not_disambiguation(self):
  d=load(ROOT/'r2_wikipedia/focus/year_titles_1_11_CE_chronological.json');self.assertEqual(len(d['results']),11);self.assertEqual({r['canonical_title'] for r in d['results']},{'0s','10s'})
if __name__=='__main__':unittest.main()
