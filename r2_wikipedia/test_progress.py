import gzip,sqlite3,unittest
from unittest.mock import patch
from progress import ordinal,period_progress,percent,format_percent,discovered_period_progress,future_audit_line,recognized_year_pages

class ProgressTests(unittest.TestCase):
 def test_future_audit_not_run_or_dated(self):
  self.assertIn('not run',future_audit_line({}))
  s=future_audit_line({'as_of':'2026-10-28','counts':{'future_start_year':0,'current_start_year_day_unknown':513}})
  self.assertIn('2026-10-28',s);self.assertIn('513',s);self.assertIn('does not check other resources',s)
 def test_ordinal(self):
  self.assertEqual([ordinal(x) for x in [1,2,3,11,12,13,21,22,23,30]],['1st','2nd','3rd','11th','12th','13th','21st','22nd','23rd','30th'])
 def test_not_discovered_is_not_complete(self):
  db=sqlite3.connect(':memory:');self.addCleanup(db.close);db.execute('create table frontier(title text,status text)');db.execute('create table pages(title text)')
  db.executemany('insert into frontier values (?,?)',[('1st century BC','done'),('1st century','missing'),('2nd century','pending'),('22nd century','done')])
  db.execute("insert into pages values ('1st century BC')")
  p=period_progress(db,'century',30)
  self.assertEqual((p['loaded'],p['checked'],p['expected'],p['percent'],p['checked_percent']),(1,2,60,1.67,3.33))
  self.assertEqual(next(x['state'] for x in p['not_read'] if x['title']=='1st century'),'missing')
  self.assertEqual(next(x['state'] for x in p['not_read'] if x['title']=='30th century'),'not_discovered')
  self.assertEqual(next(x['state'] for x in p['not_read'] if x['title']=='22nd century'),'redirect_or_alias')
 def test_year_pages_require_canonical_page_type_and_matching_navigation(self):
  db=sqlite3.connect(':memory:');self.addCleanup(db.close)
  db.execute('create table pages(title text,wikitext_gzip blob)')
  entries=[('1948','valid'),('1948 (year)','valid'),('1949','wrongnav'),('1950','number'),('20th century','century'),('7000','outside')]
  db.executemany('insert into pages values (?,?)',[(t,gzip.compress(v.encode())) for t,v in entries])
  with patch('progress.harvester.page_type',side_effect=lambda t,raw: 'number' if raw=='number' else 'year'), patch('progress.harvester.nav_year',side_effect=lambda raw: 1948):
   self.assertEqual(recognized_year_pages(db),[1948])
   self.assertEqual(recognized_year_pages(db,{'1949'}),[])
   self.assertEqual(recognized_year_pages(db,{'1948 (year)'}),[1948])
 def test_queue_denominator(self):
  self.assertEqual(percent(1,10),10.0);self.assertIsNone(percent(1,0));self.assertEqual(format_percent(None),'n/a');self.assertEqual(format_percent(2.5),'2.50%')
 def test_decade_and_year_queues_are_not_universal_coverage(self):
  db=sqlite3.connect(':memory:');self.addCleanup(db.close);db.execute('create table frontier(title text,status text)')
  db.executemany('insert into frontier values (?,?)',[('1800s','done'),('1900s','pending'),('1948','done'),('1949','error'),('2000s','missing'),('Other','done')])
  d=discovered_period_progress(db,'decade'); y=discovered_period_progress(db,'year')
  self.assertEqual((d['checked'],d['currently_discovered']), (2,3));self.assertEqual((y['checked'],y['currently_discovered']), (1,2))

if __name__=='__main__':unittest.main()
