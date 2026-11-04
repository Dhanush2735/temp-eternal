import copy,json,unittest
import apply_2920_context as c
class Context2920Test(unittest.TestCase):
 def setUp(self):self.m=json.loads(c.M.read_text())
 def test_roundtrip_all(self):
  for pack,key,sec in [(c.E,'troy_event','events'),(c.S,'troy_site','sites'),(c.R,None,'events')]:
   doc={sec:[{'id':'other'}]+([self.m[key]['before']] if key else [])}
   self.assertEqual(c.transform(c.transform(doc,self.m,pack),self.m,pack,True),doc)
 def test_changed_troy(self):
  d={'events':[copy.deepcopy(self.m['troy_event']['before'])]};d['events'][0]['name']='modified'
  with self.assertRaises(ValueError):c.transform(d,self.m,c.E)
 def test_duplicate_new(self):
  with self.assertRaises(ValueError):c.transform({'events':[self.m['anedjib_event']['event']]},self.m,c.R)
 def test_changed_site_rollback(self):
  d=c.transform({'sites':[self.m['troy_site']['before']]},self.m,c.S);d['sites'][0]['name']='changed'
  with self.assertRaises(ValueError):c.transform(d,self.m,c.S,True)
 def test_no_assigned_civ(self):
  m=copy.deepcopy(self.m);m['troy_site']['after']['civHint']='troy'
  with self.assertRaises(ValueError):c.validate(m)
 def test_no_political_effect(self):
  m=copy.deepcopy(self.m);m['troy_event']['after']['effect']='political'
  with self.assertRaises(ValueError):c.validate(m)
 def test_doubt_required(self):
  m=copy.deepcopy(self.m);m['anedjib_event']['event']['name']='Anedjib dies'
  with self.assertRaises(ValueError):c.validate(m)
