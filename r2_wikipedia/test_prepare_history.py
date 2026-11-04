import datetime,unittest
from prepare_history import explicit_label,temporal_context,section_kind,build

class HistoryStagingTests(unittest.TestCase):
 def test_simple_years_not_ranges_or_piped_links(self):
  self.assertEqual(explicit_label('[[1402]]: [[Person]] did something')['year'],1402)
  self.assertEqual(explicit_label('[[499 BC]]: event')['year'],-499)
  self.assertEqual(explicit_label('AD 2 – An event')['year'],2)
  self.assertEqual(explicit_label('[[AD 8]] &ndash; Another event')['year'],8)
  self.assertEqual(explicit_label('[[499 BCE]] – Another event')['year'],-499)
  self.assertEqual(explicit_label('c. 2300 BC: a culture')['year'],-2300)
  self.assertTrue(explicit_label('c. 2300 BC: a culture')['approximate'])
  for s in ['[[24th century BC|2334 BC]] – 2279 BC: event','1402–1405: event','1402 – 1405: event','1402 – [[1405]]: event','1402 – c. 1405: event','AD 100 BC: event','[[1402|1403]]: event','In 1402: event','0: event']:
   self.assertIsNone(explicit_label(s),s)
 def test_future_is_context_not_projection(self):
  asof=datetime.date(2026,10,28);p={'start':2001,'end':3000}
  x=temporal_context(p,explicit_label('2030: event'),asof)
  self.assertEqual(x['classification'],'future_year_context');self.assertIn('not establish',x['warning']);self.assertNotIn('projected',x)
  self.assertEqual(temporal_context(p,None,asof)['classification'],'includes_present_year_context')
  self.assertEqual(temporal_context({'start':-3000,'end':-2001},None,asof)['classification'],'before_present_year_context')
 def test_sections_remain_distinct(self):
  self.assertEqual(section_kind(['Births','January']),'births_section');self.assertEqual(section_kind(['Deaths']),'deaths_section')
  self.assertEqual(section_kind(['Events','Europe']),'event_or_development_section');self.assertEqual(section_kind(['References']),'reference_or_navigation_section')
 def test_no_date_or_coordinates_invented(self):
  r={'id':'id1','source':{'title':'1948','revision_id':123},'section_path':['Events'],
     'period_context':{'start':1948,'end':1948,'kind':'year'},'parent_bullets':['[[January 30]]:'],
     'raw_wikitext':'[[A]] visits [[B]].','links':[{'title':'A'},{'title':'B'}]}
  out=build(r,datetime.date(2026,10,28));self.assertIsNone(out['explicit_leading_year']);self.assertIsNone(out['resolved_location'])
  self.assertFalse(out['event_date_verified']);self.assertEqual(out['parent_bullets'],['[[January 30]]:']);self.assertEqual(out['linked_articles'],r['links'])
if __name__=='__main__':unittest.main()
