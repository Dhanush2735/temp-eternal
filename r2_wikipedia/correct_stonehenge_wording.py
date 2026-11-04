#!/usr/bin/env python3
"""Apply or rollback a reviewed wording-only correction, preserving the legacy date.

This tool cannot add events, move dates or points, or make a broad import.
"""
import argparse,copy,gzip,json
from pathlib import Path
from apply_reviewed_events import write_atomic_gzip

ROOT=Path(__file__).resolve().parent.parent
MANIFEST=ROOT/'r2_wikipedia/reviews/stonehenge_early_wording_2026-10.json'
PACK=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history/events_wikipedia.json.gz'

def transform(doc,m,reverse=False):
 if m.get('schema')!='eternal-r2-wording-only-review-v1' or m.get('target')!='events_wikipedia.json.gz':raise ValueError('wrong manifest')
 before,after=m['before'],m['after'];eid=m['event_id']
 if before.get('id')!=eid or after.get('id')!=eid:raise ValueError('ID mismatch')
 if before.get('start')!=-3000 or before.get('end')!=-2999:raise ValueError('Unexpected original date')
 if 'r2SourceEvidence' in before or set(after)-set(before)!={'r2SourceEvidence'}:raise ValueError('Unexpected evidence fields')
 if {k for k in before if before[k]!=after[k]}!={'name'}:raise ValueError('Only wording may change')
 if not after['name'].startswith('c. 3000 BC:') or 'uncertain' not in after['name']:raise ValueError('Missing uncertainty label')
 rows=doc.get('events');
 if not isinstance(rows,list):raise ValueError('Missing event list')
 found=[i for i,x in enumerate(rows) if isinstance(x,dict) and x.get('id')==eid]
 if len(found)!=1:raise ValueError('Missing or duplicated event ID')
 i=found[0];expected=after if reverse else before;replacement=before if reverse else after
 if rows[i]!=expected:raise ValueError('Current record differs from snapshot')
 out=copy.deepcopy(doc);out['events'][i]=copy.deepcopy(replacement)
 check=copy.deepcopy(out);check['events'][i]=copy.deepcopy(expected)
 if check!=doc:raise ValueError('Unrelated data changed')
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['stage','apply','rollback']);ap.add_argument('--output',default='/home/user/.cache/r2_storage/stonehenge_staged.json.gz');a=ap.parse_args()
 m=json.loads(MANIFEST.read_text(encoding='utf8'))
 with gzip.open(PACK,'rt',encoding='utf8') as f:doc=json.load(f)
 out=transform(doc,m,a.action=='rollback')
 path=Path(a.output) if a.action=='stage' else PACK
 if a.action=='stage' and path.resolve()==PACK.resolve():raise ValueError('Stage output equals pack')
 write_atomic_gzip(path,out);print(a.action,'successful:',m['event_id'],'->',path)
if __name__=='__main__':main()
