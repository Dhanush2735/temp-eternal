import copy,gzip,lzma,json,unittest
from pathlib import Path
import apply_662_711_ce_context as C
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
  cls.cm=C.load(C.M);cls.packs={p:load(DATA/p) for p in load(DATA/'index.json')['packs']};cls.graph=load(DATA/'sources/wikipedia_662_711_ce_people_links.json')
 def test_manifest_hash(self):C.validate(self.cm)
 def test_tamper(self):
  m=copy.deepcopy(self.cm);m['updates'][0]['after']['start']=257
  with self.assertRaises(ValueError):C.validate(m)
 def test_unique_after_images(self):
  targets={x['event_id']:x['after'] for x in self.cm['updates']};self.assertEqual(len(targets),10);found={i:[] for i in targets}
  for d in self.packs.values():
   for sec in ('events','sites'):
    for row in d.get(sec,[]):
     if isinstance(row,dict) and row.get('id') in targets:found[row['id']].append(row)
  for i,a in targets.items():self.assertEqual(found[i],[a],i)
 def reverse_batch(self):
  d=copy.deepcopy(self.packs)
  for p in {u['pack'] for u in self.cm['updates']}:
   d[p]=C.transform(d[p],[u for u in self.cm['updates'] if u['pack']==p],True,[])
  return d
 def test_roundtrip(self):
  d=self.reverse_batch()
  for p in {u['pack'] for u in self.cm['updates']}:
   d[p]=C.transform(d[p],[u for u in self.cm['updates'] if u['pack']==p],False,[])
  self.assertEqual(d,self.packs)
 def test_previous_batch_in_order(self):
  import apply_612_661_ce_context as OC,apply_612_661_ce_hazards as OH
  d=self.reverse_batch();baseline=copy.deepcopy(d);om=OC.load(OC.M);oh=OH.load(OH.M)
  for p in (OH.HAZ,OH.REG):d[p]=OH.transform(d[p],oh,p,True)
  for p in {u['pack'] for u in om['updates']}:d[p]=OC.transform(d[p],[u for u in om['updates'] if u['pack']==p],True,[])
  for p in {u['pack'] for u in om['updates']}:d[p]=OC.transform(d[p],[u for u in om['updates'] if u['pack']==p],False,[])
  for p in (OH.HAZ,OH.REG):d[p]=OH.transform(d[p],oh,p,False)
  self.assertEqual(d,baseline)
 def test_key_corrections(self):
  a={u['event_id']:u['after'] for u in self.cm['updates']};self.assertEqual(a['wpy_52336fe6cb']['lat'],24.48944);self.assertEqual(a['wpy_3176e9cfb2']['lon'],10.3233);self.assertEqual(a['wpy_f002f841f3']['lat'],35.8346194);self.assertEqual(a['wpd_d7d864aca3']['lat'],-6.8886);self.assertEqual(a['wpd_d7d864aca3']['effect'],'note');self.assertEqual(a['wpr_30c1c46b7e']['lon'],128.233);self.assertEqual(a['q399482']['confidence'],'disputed_chronology')
 def test_graph(self):
  g=self.graph;ps={r['id'] for r in g['people']};idx={r.get('id') for d in self.packs.values() for sec in ('events','sites') for r in d.get(sec,[]) if isinstance(r,dict)}
  self.assertEqual(len(ps),len(g['people']));self.assertTrue(all(not p['spawnable'] for p in g['people']));self.assertTrue(all(x['from'] in ps and x['to'] in ps for x in g['relationships']));self.assertTrue(all(x['person_id'] in ps and x['event_id'] in idx for x in g['event_roles']))
 def test_title_resolution_and_pinned_text(self):
  a=load(ROOT/'r2_wikipedia/focus/year_titles_662_711_CE.json')['results'];self.assertEqual(len(a),50);self.assertTrue(all(r['status']=='resolved' for r in a));self.assertEqual(len({r['canonical_title'] for r in a}),50)
  override=next(r for r in a if r['requested_title']=='711 (year)');self.assertEqual(override['canonical_title'],'AD 711');self.assertEqual(override['annual_page_override']['original_resolution']['canonical_title'],'711')
  p=load(ROOT/'r2_wikipedia/focus/year_wikitext_662_711_CE.json.xz')['pages'];self.assertEqual({x['lastrevid'] for x in a},{x['revisions'][0]['revid'] for x in p});self.assertTrue(all('disambiguation' not in x.get('pageprops',{}) for x in p))
if __name__=='__main__':unittest.main()
