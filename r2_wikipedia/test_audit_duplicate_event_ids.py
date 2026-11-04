import gzip
import json
import tempfile
import unittest
from pathlib import Path
from audit_duplicate_event_ids import inventory


class DuplicateIdAuditTest(unittest.TestCase):
    def test_indexes_all_packs_and_preserves_full_rows(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t)
            (p/'index.json').write_text(json.dumps({'packs': ['a.json', 'b.json.gz']}))
            (p/'a.json').write_text(json.dumps({'events': [
                {'id': 'same', 'name': 'First', 'start': 123},
                {'id': 'same', 'name': 'Second', 'start': 456},
                {'id': '', 'name': 'Missing'}]}))
            with gzip.open(p/'b.json.gz', 'wt') as f:
                json.dump({'events': [{'id': 'same', 'name': 'Third'}, {'id': 'one'}]}, f)
            report = inventory(p)
            self.assertEqual((report['event_rows'], report['distinct_valid_ids'], report['rows_missing_valid_id']), (5, 2, 1))
            self.assertEqual((report['duplicated_ids'], report['rows_in_collisions'], report['duplicate_row_excess']), (1, 3, 2))
            self.assertEqual([r['record']['name'] for r in report['collisions'][0]['rows']], ['First', 'Second', 'Third'])
            self.assertEqual(report['collisions'][0]['rows'][2]['pack'], 'b.json.gz')


if __name__ == '__main__':
    unittest.main()
