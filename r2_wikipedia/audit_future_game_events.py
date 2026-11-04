#!/usr/bin/env python3
"""Audit indexed event start years relative to a supplied as-of date.

Future-start rows are copied to a separate review file, without modifying resources.
A start year in the current year cannot tell us whether a day has already passed, and
future-start rows are not automatically projections: they could be plans or errors.
"""
import argparse
import collections
import datetime
import gzip
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
HISTORY=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history'


def scan(history, as_of):
    counts=collections.Counter();per_pack={};future=[]
    names=json.loads((history/'index.json').read_text(encoding='utf8'))['packs']
    for name in names:
        path=history/name
        opener=gzip.open if name.endswith('.gz') else open
        with opener(path,'rt',encoding='utf8') as f:doc=json.load(f)
        pack=collections.Counter()
        for i,row in enumerate(doc.get('events',[])):
            pack['rows']+=1;counts['rows']+=1
            # Common game formats use either start or the fallback year. Do not infer from names.
            field='start' if isinstance(row,dict) and row.get('start') is not None else 'year'
            start=row.get(field) if isinstance(row,dict) else None
            if type(start) is not int:
                kind='missing_or_noninteger_start'
            elif start>as_of.year:
                kind='future_start_year'
                future.append({'pack':name,'event_index':i,'record':row,'date_field':field,
                    'audit_status':'future_start_year_review_only','as_of':as_of.isoformat()})
            elif start==as_of.year:kind='current_start_year_day_unknown'
            else:kind='earlier_start_year'
            pack[kind]+=1;counts[kind]+=1
        per_pack[name]=dict(pack)
    summary={'schema':'eternal-r2-future-year-audit-v1','as_of':as_of.isoformat(),
        'indexed_packs':len(names),'counts':dict(counts),'per_pack':per_pack,
        'warning':'Year-only audit, not verified history or a projection classifier. Current-year events may be past or future; earlier-start events may continue or describe plans. Pack-specific end-year conventions are not interpreted. Other resources are not scanned.'}
    return summary,future


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--history-dir',type=Path,default=HISTORY)
    p.add_argument('--as-of',type=datetime.date.fromisoformat,required=True)
    p.add_argument('--summary',type=Path,default=ROOT/'r2_wikipedia/future_game_event_audit.json')
    p.add_argument('--future-output',type=Path,default=ROOT/'r2_wikipedia/future_game_event_review.jsonl.gz')
    a=p.parse_args();summary,rows=scan(a.history_dir,a.as_of)
    a.summary.parent.mkdir(parents=True,exist_ok=True);a.future_output.parent.mkdir(parents=True,exist_ok=True)
    a.summary.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    with open(a.future_output,'wb') as f,gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0) as out:
        for row in rows:out.write((json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n').encode())
    print('Indexed event rows:',summary['counts'].get('rows',0),
          'future start years:',len(rows),'current-year starts needing day review:',summary['counts'].get('current_start_year_day_unknown',0),
          'missing/noninteger starts:',summary['counts'].get('missing_or_noninteger_start',0))
    print(summary['warning'])

if __name__=='__main__':main()
