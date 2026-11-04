import unittest
from build_timelines import bounded_years,build

def date(y,before=0,after=0):return {'snaktype':'value','year_value':y,'before':before,'after':after,'precision':9}
def claim(qid='Q123',qual=None):return {'rank':'normal','statement_id':'s','value':{'entity_id':qid},'qualifiers':qual or {},'reference_hashes':['ref']}
class TimelineTests(unittest.TestCase):
 def test_bound_requires_both_qualified_unambiguous_dates(self):
  c=claim(qual={'P580':[date(1888)],'P582':[date(1891)]});x=bounded_years(c);self.assertEqual((x['start_year'],x['end_year']),(1888,1891));self.assertIn('not_a_spawn',x['precision'])
  for qual in ({'P580':[date(1888)]},{'P580':[date(1888)],'P582':[date(1891)],'P1480':[{}]},
      {'P580':[date(1892)],'P582':[date(1891)]},{'P580':[date(1888),date(1889)],'P582':[date(1891)]},
      {'P580':[date(1888,before=2)],'P582':[date(1891)]}):
   self.assertIsNone(bounded_years(claim(qual=qual)))
 def test_birthplace_is_only_birth_not_lifetime(self):
  p={'id':'Qperson','name':'Example','wikipedia':{'revision_id':1},'wikidata':{'revision_id':2},'details':{'birth_date':[{'value':{'year_value':1900}}], 'birth_place':[claim()], 'residence':[claim('Q999')], 'offices':[claim('Qjob')]}}
  places={'Q123':{'name':'City','source_url':'source','wikidata_revision':2,'coordinate_claims':[{'id':'coordinate'}]}}
  rows=build(p,places);self.assertEqual(len(rows),3)
  birth=rows[0];self.assertEqual(birth['time_scope'],'birth_event_only');self.assertIsNone(birth['explicit_year_index']);self.assertEqual(birth['place_source']['url'],'source')
  self.assertTrue(all(x['status']=='unreviewed_not_spawnable' for x in rows))
  self.assertEqual(rows[1]['time_scope'],'qualified_interval_or_unknown');self.assertIsNone(rows[1]['explicit_year_index'])
  self.assertNotIn('place_id',rows[2]);self.assertEqual(rows[2]['kind'],'office')
if __name__=='__main__':unittest.main()
