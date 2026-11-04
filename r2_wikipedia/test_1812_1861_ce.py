import copy,gzip,json,unittest
from pathlib import Path
import apply_1812_1861_ce_context as C
import apply_1762_1811_ce_context as P
import apply_1762_1811_ce_hazards as PH
ROOT=Path(__file__).resolve().parent.parent;DATA=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'
def load(p):
 with (gzip.open(p,'rt',encoding='utf8') if str(p).endswith('.gz') else open(p,encoding='utf8')) as f:return json.load(f)
class BatchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m=C.load(C.M);cls.packs={p:load(DATA/p) for p in load(DATA/'index.json')['packs']}
 def transform(self,d,module,m,reverse):
  for p in {u['pack'] for u in m['updates']}:
   d[p]=module.transform(d[p],[u for u in m['updates'] if u['pack']==p],reverse,[])
 def test_manifest(self):C.validate(self.m)
 def test_tamper_rejected(self):
  m=copy.deepcopy(self.m);m['updates'][0]['after']['start']=1824
  with self.assertRaises(ValueError):C.validate(m)
 def test_after_images_and_duplicate(self):
  a={r['event_id']:r['after'] for r in self.m['updates']};self.assertEqual(len(a),3)
  matches={i:[] for i in a}
  for d in self.packs.values():
   for r in d.get('events',[]):
    if r.get('id') in matches:matches[r['id']].append(r)
  for i in a:self.assertEqual(matches[i],[a[i]])
  self.assertEqual((a['wpy_5b7908a326']['start'],a['wpy_5b7908a326']['effect']),(1821,'note'))
  self.assertEqual((a['wpy_8d21ec4c6e']['lat'],a['wpy_8d21ec4c6e']['lon']),(37.167,12.717))
  self.assertEqual((a['wpr_a7035a94fe']['lat'],a['wpr_a7035a94fe']['lon']),(-35.304,174.122))
 def test_current_roundtrip(self):
  d=copy.deepcopy(self.packs);self.transform(d,C,self.m,True);self.transform(d,C,self.m,False);self.assertEqual(d,self.packs)
 def test_previous_layer_order(self):
  d=copy.deepcopy(self.packs);self.transform(d,C,self.m,True);base=copy.deepcopy(d);pm=P.load(P.M);hm=PH.load(PH.M)
  for p in (PH.HAZ,PH.REG):d[p]=PH.transform(d[p],hm,p,True)
  self.transform(d,P,pm,True);self.transform(d,P,pm,False)
  for p in (PH.HAZ,PH.REG):d[p]=PH.transform(d[p],hm,p,False)
  self.assertEqual(d,base)
if __name__=='__main__':unittest.main()
