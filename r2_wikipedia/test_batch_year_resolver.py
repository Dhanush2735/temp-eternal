import unittest
import batch_year_resolver as b

class BatchYearTests(unittest.TestCase):
 def test_consecutive(self):self.assertEqual(b.years(2989,2985),['2989 BC','2988 BC','2987 BC','2986 BC','2985 BC'])
 def test_invalid_range(self):
  for a,z in ((1,2),(2,0)):
   with self.assertRaises(ValueError):b.years(a,z)
 def test_redirects_and_shared_target(self):
  j={'query':{'redirects':[{'from':'2989 BC','to':'30th century BC'},{'from':'2988 BC','to':'30th century BC'}],'pages':[{'title':'30th century BC','pageid':2,'lastrevid':42}]}}
  rows=b.resolve_chunk(['2989 BC','2988 BC'],j);self.assertEqual(len(rows),2);self.assertTrue(all(x['canonical_title']=='30th century BC' and x['lastrevid']==42 for x in rows))
 def test_direct_and_missing(self):
  j={'query':{'pages':[{'title':'2 BC','pageid':10,'lastrevid':20},{'title':'1 BC','missing':True}]}}
  rows=b.resolve_chunk(['2 BC','1 BC'],j);self.assertEqual(rows[0]['redirect_chain'],[]);self.assertEqual(rows[1]['status'],'missing')
 def test_chain_and_normalization(self):
  j={'query':{'normalized':[{'from':'2989 BC','to':'A'}],'redirects':[{'from':'A','to':'B'},{'from':'B','to':'C'}],'pages':[{'title':'C','pageid':1,'lastrevid':2}]}}
  self.assertEqual(b.resolve_chunk(['2989 BC'],j)[0]['redirect_chain'],['A','B','C'])
 def test_cycle_and_partial_fail_closed(self):
  with self.assertRaises(ValueError):b.resolve_chunk(['A'],{'query':{'redirects':[{'from':'A','to':'B'},{'from':'B','to':'A'}],'pages':[]}})
  with self.assertRaises(ValueError):b.resolve_chunk(['A'],{'query':{'pages':[]}})
 def test_revision_required(self):
  with self.assertRaises(ValueError):b.resolve_chunk(['A'],{'query':{'pages':[{'title':'A','pageid':1}]}})
 def test_api_error(self):
  with self.assertRaises(ValueError):b.resolve_chunk(['A'],{'error':{'code':'bad'}})
if __name__=='__main__':unittest.main()
