#!/usr/bin/env python3
"""Report *crawl progress*, never historical coverage or completeness."""
import argparse,collections,json,sqlite3
from pathlib import Path
from periods import classify

ROOT='List of decades, centuries, and millennia'
def run(db):
 c=sqlite3.connect(f'file:{Path(db).resolve()}?mode=ro',uri=True)
 counts=collections.Counter()
 for title,status in c.execute('select title,status from frontier'):
  p=classify(title);counts[(p.kind if p else 'other',status)]+=1
 root=[]
 for (title,) in c.execute('''select e.target_title from edges e join pages p on p.pageid=e.source_pageid
                              where p.title=? and e.source_revid=p.revid''',(ROOT,)):
  p=classify(title)
  if p: root.append((title,p))
 data={'pages_read':c.execute('select count(*) from pages').fetchone()[0],
  'edges_recorded':c.execute('select count(*) from edges').fetchone()[0],
  'frontier':{k:{s:counts[(k,s)] for s in ('done','pending','error','missing')} for k in ('millennium','century','decade','year','other')},
  'index_direct_period_links':dict(collections.Counter(p.kind for _,p in root)),
  'index_direct_millennia':[{'title':t,'start':p.start,'end':p.end} for t,p in root if p.kind=='millennium'],
  'warning':'Counts describe titles and page visits only, not verified facts or complete history. Plain year titles are candidates until their page is checked.'}
 return data
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--db',default='r2_wikipedia/crawl.sqlite3');ap.add_argument('--out');args=ap.parse_args();s=json.dumps(run(args.db),ensure_ascii=False,indent=2)+'\n';print(s,end='')
 if args.out:Path(args.out).write_text(s,encoding='utf8')
