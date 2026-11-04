import unittest
from build_vip_candidates import decode_snak, normalize_claim, build


def ts(t,prec=11,calendar='http://www.wikidata.org/entity/Q1985727'):
 return {'snaktype':'value','datavalue':{'type':'time','value':{'time':t,'precision':prec,'before':0,'after':0,'calendarmodel':calendar}}}
def ent(q):return {'snaktype':'value','datavalue':{'type':'wikibase-entityid','value':{'id':q}}}
def claim(s,rank='normal',qual=None):return {'id':'statement-1','rank':rank,'mainsnak':s,'qualifiers':qual or {},'references':[{'hash':'ref-1'}]}

class VipStageTests(unittest.TestCase):
 def test_json_bc_year_numbering_not_rdf(self):
  # Wikibase JSON uses historical numbering (no year 0); do NOT apply SPARQL's BCE offset.
  self.assertEqual(decode_snak(ts('-0044-03-15T00:00:00Z'))['year_value'],-44)
  self.assertEqual(decode_snak(ts('-0001-01-01T00:00:00Z'))['year_value'],-1)
  self.assertEqual(decode_snak(ts('+0001-01-01T00:00:00Z'))['year_value'],1)
  self.assertIsNone(decode_snak(ts('+0000-01-01T00:00:00Z'))['year_value'])
 def test_precision_and_calendar_are_not_invented(self):
  t=decode_snak(ts('-1000-00-00T00:00:00Z',7,'julian'))
  self.assertIsNone(t['year_value']);self.assertIsNone(t['month_value']);self.assertIsNone(t['day_value']);self.assertEqual(t['calendar_model'],'julian')
  t=decode_snak(ts('+0965-00-00T00:00:00Z',9));self.assertEqual(t['year_value'],965);self.assertIsNone(t['month_value'])
  t=decode_snak(ts('+1900-02-00T00:00:00Z',10));self.assertEqual(t['month_value'],2);self.assertIsNone(t['day_value'])
 def test_unknown_qualifiers_references(self):
  c=claim(ent('Q10'),qual={'P580':[ts('+1000-00-00T00:00:00Z',9)]})
  x=normalize_claim(c);self.assertEqual(x['value']['entity_id'],'Q10');self.assertEqual(x['qualifiers']['P580'][0]['year_value'],1000);self.assertEqual(x['reference_hashes'],['ref-1'])
  self.assertEqual(decode_snak({'snaktype':'somevalue'}),{'snaktype':'somevalue'})
 def test_conflicting_dates_are_not_collapsed(self):
  row={'name':'Test Person','identity':{'wikidata_id':'Q1'},'wikipedia_source':{'revision_id':12},
       'wikidata_source':{'entity_id':'Q1','revision_id':13,'claims':{'P569':[claim(ts('+1800-01-01T00:00:00Z',9)),claim(ts('+1801-01-01T00:00:00Z',9))],
        'P19':[claim(ent('QPlace'))]}},'infobox':{'raw_fields':{}},'discovered_from':[{'source_title':'a'}]}
  r=build(row);self.assertEqual(len(r['details']['birth_date']),2);self.assertIn('multiple_birth_date_years',r['review_flags']);self.assertIn('missing_death_date',r['review_flags']);self.assertEqual(r['status'],'unreviewed_not_spawnable');self.assertNotIn('spawn_coordinates',r)

if __name__=='__main__':unittest.main()
