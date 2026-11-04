import sqlite3,tempfile,unittest
from pathlib import Path
import people,vacuum_people

class PeopleVacuumTests(unittest.TestCase):
 def test_compaction_preserves_all_tables_queue_and_export(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);db=p/'people.sqlite';c=sqlite3.connect(db);c.executescript(people.SCHEMA)
   c.executemany('insert into subjects(title,first_source) values(?,?)',[(f'person-{i:05d}','test') for i in range(2000)])
   c.execute('delete from subjects where id<1500');c.execute("insert into people_scheduler values('last_source','test')");c.commit()
   before=vacuum_people.snapshot(c);c.close()
   r=vacuum_people.compact(db,p/'work',p/'backup',p/'before',p/'after')
   self.assertGreater(r['saved_bytes'],0)
   c=sqlite3.connect(db);self.addCleanup(c.close)
   self.assertEqual(vacuum_people.snapshot(c),before)
   self.assertEqual(c.execute("select value from people_scheduler where key='last_source'").fetchone()[0],'test')
   self.assertTrue((p/'backup').exists())
 def test_refuses_existing_backup(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'backup').write_text('do not overwrite')
   with self.assertRaises(FileExistsError):vacuum_people.compact(p/'db',p/'work',p/'backup',p/'before',p/'after')

if __name__=='__main__':unittest.main()
