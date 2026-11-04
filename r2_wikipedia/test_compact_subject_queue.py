import sqlite3
import unittest
import people
import compact_subject_queue as compact

class QueueCompactionTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:')
        self.db.executescript(people.SCHEMA)
        self.db.execute('DROP INDEX subject_queue')
        self.db.execute(compact.OLD_SQL)
        for src in ('C','A','B'):
            for i in range(4):
                title=f'{src}-{i}'
                self.db.execute('insert into subjects(title,first_source) values (?,?)',(title,src))
                self.db.execute('insert into origins values(?,?,?,?,?,?)',(title,1,src,2,i,f'{src}-{i}'))
        self.db.execute("update subjects set status='unconfirmed' where title='A-0'")
        self.db.commit()
    def tearDown(self): self.db.close()
    def test_migration_preserves_data_and_queue_order(self):
        before=compact.full_snapshot(self.db); expected=people.next_batch(self.db,20)
        self.assertEqual(compact.migrate_copy(self.db),before)
        self.assertEqual(compact.full_snapshot(self.db),before)
        self.assertEqual(people.next_batch(self.db,20),expected)
        self.assertEqual(self.db.execute("select sql from sqlite_master where name='subject_queue'").fetchone()[0],compact.NEW_SQL)
        self.assertIn('subject_queue',str(self.db.execute("explain query plan select title from subjects where status='pending' and first_source=? order by id limit 1",('B',)).fetchall()))
    def test_second_migration_refuses(self):
        compact.migrate_copy(self.db)
        with self.assertRaises(ValueError):compact.migrate_copy(self.db)
    def test_schema_for_fresh_database(self):
        c=sqlite3.connect(':memory:');c.executescript(people.SCHEMA)
        self.assertIn("WHERE status='pending'",c.execute("select sql from sqlite_master where name='subject_queue'").fetchone()[0]);c.close()

if __name__=='__main__':unittest.main()
