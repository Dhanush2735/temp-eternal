#!/usr/bin/env python3
"""Audit retained people-origin candidate IDs against the current staging export.

An absent candidate is not necessarily an invalid source: the source page may have
been refreshed or its period classification changed. This only compares identifiers;
it does not validate historical truth. The database is opened read-only.
"""
import argparse,collections,gzip,json,sqlite3
from staged_exports import open_text as open_staged_text
from pathlib import Path


def audit(db, current_ids):
    counts=collections.Counter(); by_source=collections.Counter()
    rows=db.execute('''select s.source_title,c.candidate_id
      from origin_links l join origin_sources s on s.id=l.source_id
      join origin_candidates c on c.id=l.candidate_key''')
    for source,candidate in rows:
        if candidate.startswith(('crawl-edge:','article-link:')):
            counts['non_candidate_origin_links']+=1
        elif candidate in current_ids:
            counts['current_candidate_origin_links']+=1
        else:
            counts['retained_not_in_current_export_links']+=1
            by_source[source]+=1
    return {'counts':dict(sorted(counts.items())),
            'retained_not_in_current_export_by_source':dict(sorted(by_source.items())),
            'warning':'Read-only identifier comparison; old page revisions may remain available at their stored Wikipedia revision URLs. This does not verify origins or facts.'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--db',default='r2_wikipedia/people.sqlite3')
    ap.add_argument('--candidates',default='r2_wikipedia/candidates.jsonl.gz')
    ap.add_argument('--output',default='r2_wikipedia/candidate_origin_audit.json')
    a=ap.parse_args()
    with open_staged_text(a.candidates) as f:ids={json.loads(line)['id'] for line in f}
    c=sqlite3.connect(f'file:{Path(a.db).resolve()}?mode=ro',uri=True)
    try:r=audit(c,ids)
    finally:c.close()
    Path(a.output).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(r,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
