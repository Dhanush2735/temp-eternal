import unittest
from reconcile_people import name_key,years,compare,reconcile

def date(y,rank='normal',qual=None):return {'rank':rank,'value':{'year_value':y},'qualifiers':qual or {}}
def person(name='A Person',birth=None,death=None):return {'id':'Q1','name':name,'wikipedia':{'revision_id':1},'wikidata':{'revision_id':2},'details':{'birth_date':birth or [],'death_date':death or []}}
class ReconcileTests(unittest.TestCase):
 def test_normalization_conservative(self):
  self.assertEqual(name_key('  Bolesław  I  '),name_key('bolesław I'))
  self.assertNotEqual(name_key('José'),name_key('Jose'))
  self.assertNotEqual(name_key('John Smith'),name_key('J Smith'))
 def test_agreement_is_not_identity_proof(self):
  p=person(birth=[date(100)],death=[date(180)])
  x=compare(p,100,180);self.assertEqual(x['assessment'],'name_and_years_agree_review_identity');self.assertFalse(x['identity_verified']);self.assertTrue(x['requires_review'])
 def test_conflicts_missing_and_qualifiers(self):
  p=person(birth=[date(100)],death=[date(180)])
  self.assertEqual(compare(p,110,180)['assessment'],'name_match_date_conflict')
  self.assertEqual(compare(p,None,180)['assessment'],'name_match_dates_incomplete_or_uncertain')
  p=person(birth=[date(100),date(101)],death=[date(180)])
  self.assertEqual(compare(p,100,180)['assessment'],'name_match_dates_incomplete_or_uncertain')
  p=person(birth=[date(100,qual={'P1480':[{}]})],death=[date(180)])
  self.assertEqual(compare(p,100,180)['assessment'],'name_match_dates_incomplete_or_uncertain')
  p=person(birth=[date(100,'deprecated')],death=[date(180)])
  self.assertEqual(years(p,'birth_date')['values'],[])
 def test_retains_matches_from_both_existing_sources(self):
  p=person(birth=[date(100)],death=[date(180)])
  old=[{'name':'A Person','vipId':'id','birthYear':100,'historicalDeathYear':180}]
  rows=[['A Person','description',100,180,'Q0',1,2,25],['Different','',100,180,None,0,0,1]]
  r=list(reconcile([p],old,rows))[0]
  self.assertEqual({m['dataset'] for m in r['matches']},{'existing_vips','famous_people_master'})
  self.assertTrue(all(m['requires_review'] for m in r['matches']))
  self.assertEqual(list(reconcile([person('No match')],old,rows))[0]['matches'],[])
if __name__=='__main__':unittest.main()
