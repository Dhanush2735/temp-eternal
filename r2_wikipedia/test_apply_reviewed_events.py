import copy,gzip,json,tempfile,unittest
from pathlib import Path
from apply_reviewed_events import transform,write_atomic_gzip,reject_exact_year_duplicates

class ApplyTests(unittest.TestCase):
 def setUp(self):
  self.before={'id':'one','name':'A long historical event occurred in a place','start':1500,'end':1501,'lat':1,'lon':2}
  self.source={'title':'16th century','revision_id':5,'line':42}
  self.c={'id':'candidate','source':self.source,'display_text_unverified':'1550: A long historical event occurred in a place.',
     'section_kind':'event_or_development_section','explicit_leading_year':{'year':1550,'approximate':False}}
  self.doc={'id':'events','events':[self.before,{'id':'untouched','start':1000}],'sites':[]}
  self.u={'event_id':'one','candidate_id':'candidate','candidate_source':self.source,'before':self.before,
    'changes':{'start':1550,'end':1551},'corroborating_sources':['https://example.org/source'],
    'review_note':'Test evidence','reviewed_as_of':'2026-10-28'}
  self.u['candidate_snapshot']=copy.deepcopy(self.c)
  self.m={'updates':[self.u]}
 def test_apply_and_rollback_no_other_changes(self):
  old=copy.deepcopy(self.doc);new=transform(self.doc,self.m,[self.c]);self.assertEqual(self.doc,old)
  self.assertEqual(new['events'][1],self.doc['events'][1]);self.assertEqual(new['events'][0]['start'],1550)
  self.assertEqual(new['events'][0]['r2SourceEvidence']['wikipedia_source'],self.source)
  self.assertEqual(transform(new,self.m,[],reverse=True),old)
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test.gz';write_atomic_gzip(p,new)
   with gzip.open(p,'rt') as f:self.assertEqual(json.load(f),new)
 def test_radius_is_bounded_and_not_an_asserted_extent(self):
  m=copy.deepcopy(self.m);m['updates'][0]['changes']['radiusKm']=20
  self.assertEqual(transform(self.doc,m,[self.c])['events'][0]['radiusKm'],20)
  for v in (-1,0,201,float('nan'),True,'20'):
   m['updates'][0]['changes']['radiusKm']=v
   with self.assertRaises(ValueError):transform(self.doc,m,[self.c])
 def test_known_semantic_duplicates_block_stage_and_apply(self):
  m=copy.deepcopy(self.m);m['updates'][0]['known_possible_duplicate_event_ids']=['other-pack:other-id']
  with self.assertRaisesRegex(ValueError,'Unresolved possible duplicates'):transform(self.doc,m,[self.c])
 def test_exact_duplicate_checks_both_old_and_revised_titles_across_packs(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'index.json').write_text(json.dumps({'packs':['target.json','other.json']}))
   (p/'target.json').write_text(json.dumps(self.doc));(p/'other.json').write_text(json.dumps({'events':[]}))
   m=copy.deepcopy(self.m);m['updates'][0]['changes']['name']='A reworded name for the same event'
   reject_exact_year_duplicates(m,p,'target.json')
   for name in (self.before['name'],m['updates'][0]['changes']['name']):
    (p/'other.json').write_text(json.dumps({'events':[{'id':'different','name':name,'start':1550}]}))
    with self.assertRaisesRegex(ValueError,'Possible exact-text duplicate'):
     reject_exact_year_duplicates(m,p,'target.json')
   (p/'other.json').unlink()
   with self.assertRaises(FileNotFoundError):reject_exact_year_duplicates(m,p,'target.json')
 def test_stale_record_and_changed_source_are_rejected(self):
  d=copy.deepcopy(self.doc);d['events'][0]['lat']=40
  with self.assertRaises(ValueError):transform(d,self.m,[self.c])
  c=copy.deepcopy(self.c);c['source']['revision_id']=10
  with self.assertRaises(ValueError):transform(self.doc,self.m,[c])
 def test_missing_duplicate_or_unreviewed_changes_rejected(self):
  with self.assertRaises(ValueError):transform(self.doc,self.m,[])
  d=copy.deepcopy(self.doc);d['events'].append(copy.deepcopy(self.before))
  with self.assertRaises(ValueError):transform(d,self.m,[self.c])
  m=copy.deepcopy(self.m);m['updates'][0]['changes']['radiusKm']=500
  with self.assertRaises(ValueError):transform(self.doc,m,[self.c])
  c=copy.deepcopy(self.c);c['explicit_leading_year']['approximate']=True
  with self.assertRaises(ValueError):transform(self.doc,self.m,[c])
