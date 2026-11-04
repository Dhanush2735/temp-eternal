import sqlite3,unittest
from audit_candidate_origins import audit

class CandidateOriginAuditTests(unittest.TestCase):
 def test_distinguishes_old_candidates_from_graph_and_biography_links(self):
  c=sqlite3.connect(':memory:');self.addCleanup(c.close)
  c.executescript('''create table origin_sources(id integer,source_title text);
   create table origin_candidates(id integer,candidate_id text);
   create table origin_links(source_id integer,candidate_key integer);''')
  c.executemany('insert into origin_sources values(?,?)',[(1,'old source'),(2,'current source')])
  c.executemany('insert into origin_candidates values(?,?)',[(1,'old-id'),(2,'current-id'),(3,'crawl-edge:1:2'),(4,'article-link:1:2:3')])
  c.executemany('insert into origin_links values(?,?)',[(1,1),(1,3),(2,2),(2,4)])
  a=audit(c,{'current-id'})
  self.assertEqual(a['counts']['retained_not_in_current_export_links'],1)
  self.assertEqual(a['counts']['current_candidate_origin_links'],1)
  self.assertEqual(a['counts']['non_candidate_origin_links'],2)
  self.assertEqual(a['retained_not_in_current_export_by_source'],{'old source':1})

if __name__=='__main__':unittest.main()
