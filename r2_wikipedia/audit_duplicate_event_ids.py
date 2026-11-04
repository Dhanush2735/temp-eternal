#!/usr/bin/env python3
"""Inventory duplicate event IDs in indexed history packs, without changing any files.

An ID collision can make suppression affect multiple rows. Same-ID records can also be
legitimate alternate depictions; no identity, cause or historical correctness is inferred.
"""
import argparse
import gzip
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HISTORY = ROOT / 'eternal/src/main/resources/data/eternalengine/eternal/history'
OUTPUT = ROOT / 'r2_wikipedia/reviews/duplicate_event_ids.json'


def inventory(history_dir):
    by_id = defaultdict(list)
    packs = json.loads((history_dir / 'index.json').read_text(encoding='utf8'))['packs']
    event_rows = 0
    missing = 0
    for name in packs:
        path = history_dir / name
        opener = gzip.open if name.endswith('.gz') else open
        with opener(path, 'rt', encoding='utf8') as stream:
            document = json.load(stream)
        for row_number, row in enumerate(document.get('events', [])):
            event_rows += 1
            event_id = row.get('id')
            if not isinstance(event_id, str) or not event_id.strip():
                missing += 1
                continue
            by_id[event_id].append({'pack': name, 'event_index': row_number, 'record': row})
    collisions = [{'id': event_id, 'rows': rows} for event_id, rows in sorted(by_id.items()) if len(rows) > 1]
    return {
        'schema': 'eternal-r2-duplicate-event-id-audit-v1',
        'indexed_pack_count': len(packs), 'event_rows': event_rows,
        'rows_missing_valid_id': missing, 'distinct_valid_ids': len(by_id),
        'duplicated_ids': len(collisions), 'rows_in_collisions': sum(len(x['rows']) for x in collisions),
        'duplicate_row_excess': sum(len(x['rows']) - 1 for x in collisions),
        'status': 'review-only; does not establish identity, truth, source provenance or safe replacement IDs',
        'collisions': collisions,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--history-dir', type=Path, default=HISTORY)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    report = inventory(args.history_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print('Indexed rows:', report['event_rows'], 'distinct IDs:', report['distinct_valid_ids'],
          'duplicated IDs:', report['duplicated_ids'], 'rows in collisions:', report['rows_in_collisions'],
          'missing valid ID:', report['rows_missing_valid_id'])
    print('Review only:', args.output, '(no resource or saved-world changes)')


if __name__ == '__main__':
    main()
