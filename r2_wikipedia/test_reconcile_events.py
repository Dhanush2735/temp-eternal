import gzip,json,tempfile,unittest
from pathlib import Path
from reconcile_events import normalized,candidate_key,assessment,compare

class EventReconcileTests(unittest.TestCase):
 def setUp(self):
  self.c={'id':'r1','source':{'title':'Example','revision_id':1},'section_kind':'event_or_development_section',
   'display_text_unverified':'499 BC: A long historical event occurred in a place.',
   'explicit_leading_year':{'year':-499,'approximate':False}}
 def test_normalization_and_date_prefix(self):
  self.assertEqual(candidate_key(self.c),normalized('A long historical event occurred in a place'))
  self.assertIsNone(candidate_key({'display_text_unverified':'Short event'}))
  self.assertIsNone(candidate_key({**self.c,'section_kind':'reference_or_navigation_section'}))
 def test_year_conflict_only_indicates_review(self):
  self.assertEqual(assessment(self.c,{'start':-499}),'exact_text_same_labeled_start_year')
  self.assertEqual(assessment(self.c,{'start':499}),'exact_text_possible_start_year_conflict')
  self.assertEqual(assessment({**self.c,'explicit_leading_year':{'year':-499,'approximate':True}},{'start':-499}),'exact_text_year_not_comparable')
  self.assertEqual(assessment(self.c,{'start':True}),'exact_text_year_not_comparable')
 def test_compare_does_not_edit_events(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'events.json.gz';e={'id':'event','name':'A long historical event occurred in a place','start':499,'lat':12,'lon':34}
   with gzip.open(p,'wt') as f:json.dump({'events':[e]},f)
   before=p.read_bytes();out,stats=compare([self.c],[p]);self.assertEqual(p.read_bytes(),before)
   self.assertEqual(stats['events'],1);self.assertEqual(stats['matched_candidates'],1)
   self.assertEqual(out[0]['matches'][0]['assessment'],'exact_text_possible_start_year_conflict')
   self.assertNotIn('lat',out[0]['matches'][0]);self.assertIn('review_only',out[0]['status'])
