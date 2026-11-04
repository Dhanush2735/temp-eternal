import sqlite3,tempfile,unittest
from pathlib import Path
import people
from compact_origin_links import migrate,full_snapshot

class CompactOriginLinksTests(unittest.TestCase):
 def database(self,d):
  db=sqlite3.connect(Path(d)/'test.sqlite');db.executescript(people.SCHEMA)
  db.execute("insert into subjects(title,first_source) values('Person','Source')")
  db.execute("insert into origins values('Person',1,'Original title',50,4,'c1')")
  db.execute("insert into origins values('Person',1,'Original title',50,5,'c2')")
  db.commit();return db
 def test_migration_preserves_logical_data_and_duplicate_key(self):
  with tempfile.TemporaryDirectory() as d:
   db=self.database(d);before=full_snapshot(db);self.assertEqual(migrate(db),before)
   self.assertEqual(full_snapshot(db),before)
   # Old semantics ignore another source title and candidate for the same
   # person, page, revision and line; a different line remains distinct.
   db.execute("insert into origins values('Person',1,'Renamed title',50,4,'different')")
   self.assertEqual(db.execute('select count(*) from origins').fetchone()[0],2)
   db.execute("insert into origins values('Person',1,'Renamed title',50,6,'c3')")
   self.assertEqual(db.execute('select count(*) from origins').fetchone()[0],3)
   self.assertEqual(db.execute('select source_title from origins where source_line=6').fetchone()[0],'Renamed title')
   with self.assertRaises(sqlite3.IntegrityError):db.execute("insert into origins values('Missing',1,'X',50,1,'c')")
   db.close()
 def test_inconsistent_source_metadata_refuses_and_rolls_back(self):
  with tempfile.TemporaryDirectory() as d:
   db=self.database(d);db.execute('update origin_links set source_revid=99 where source_line=4');db.commit()
   with self.assertRaisesRegex(ValueError,'Inconsistent'):migrate(db)
   self.assertIn('source_revid',[r[1] for r in db.execute('pragma table_info(origin_links)')]);db.close()
if __name__=='__main__':unittest.main()
