import copy,unittest
import apply_239_190_bce_context as m
class Tests(unittest.TestCase):
 def setUp(self):
  self.man=m.load(m.M);m.validate(self.man);self.us=self.man['updates'];self.doc={'events':[copy.deepcopy(u['before']) for u in self.us]};self.rows={u['event_id']:u['after'] for u in self.us}
 def test_roundtrip(self):self.assertEqual(m.transform(m.transform(self.doc,self.us),self.us,True),self.doc)
 def test_no_mutation(self):
  d=copy.deepcopy(self.doc);m.transform(self.doc,self.us);self.assertEqual(self.doc,d)
 def test_missing(self):
  with self.assertRaises(ValueError):m.transform({'events':[]},self.us)
 def test_changed(self):
  d=copy.deepcopy(self.doc);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.us)
 def test_duplicate(self):
  d=copy.deepcopy(self.doc);d['events'].append(copy.deepcopy(self.us[0]['before']))
  with self.assertRaises(ValueError):m.transform(d,self.us)
 def test_changed_after(self):
  d=m.transform(self.doc,self.us);d['events'][0]['name']='changed'
  with self.assertRaises(ValueError):m.transform(d,self.us,True)
 def test_manifest_guard(self):
  d=copy.deepcopy(self.man);d['updates'][0]['after']['lat']=0
  with self.assertRaises(ValueError):m.validate(d)
 def test_stable_ids(self):
  for u in self.us:self.assertEqual(u['before']['id'],u['after']['id'])
 def test_world_dates(self):
  dates={'q378957':-218,'q200056':-202,'q207250':-217,'q271873':-218,'q175985':-225,'q179591':-216,'q999235':-217,'q1055755':-206,'q847402':-205,'q848056':-207,'q870783':-218,'q391087':-197,'q630781':-217,'q675000':-222,'q1500211':-218,'q1591145':-209,'q778730':-209,'q728550':-208,'q1788933':-215,'q3623158':-225,'q3636293':-216,'q1974201':-217,'q815210':-219,'q26518412':-218,'q3270429':-207}
  for id,y in dates.items():
   a=self.rows[id];self.assertEqual((a['start'],a['end'],a['effect']),(y,y+1,'military_presence'));self.assertIn('inclusive',a['r2SourceEvidence']['review_note'])
 def test_aous_location(self):
  a=self.rows['q3233509'];self.assertEqual((a['start'],a['lat'],a['lon'],a['effect']),(-198,40.29667,20.01889,'note'))
 def test_gaixia(self):
  a=self.rows['q1349891'];self.assertEqual((a['start'],a['end'],a['effect']),(-203,-201,'note'))
 def test_war_and_quake(self):
  for id in ('q2060017','q6271'):self.assertEqual(self.rows[id]['effect'],'note')
 def test_evidence(self):
  for u in self.us:self.assertTrue(u['after']['r2SourceEvidence']['sources'])
if __name__=='__main__':unittest.main()
