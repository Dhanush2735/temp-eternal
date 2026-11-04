#!/usr/bin/env python3
"""Extract *unverified candidates* from collected time-period article lists.

This does not geocode, assign exact dates, decide relevance or install data in the mod.
Every row carries its source revision, original bullet and context. Linked article pages
are collected separately; no content is inferred from a link name. Candidate count is
not a historical fact count. Re-running over the same database is deterministic.
"""
import argparse, gzip, hashlib, json, re, sqlite3, sys
from pathlib import Path
from urllib.parse import quote
from periods import classify

sys.path.insert(0,str(Path(__file__).resolve().parent.parent / 'harvest'))
import harvester

HEADING = re.compile(r'^(={2,6})\s*(.*?)\s*\1\s*$')
BULLET = re.compile(r'^([*#]+)\s*(.+)$')
LINK = re.compile(r'\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]')


def candidates(pageid, title, revid, raw):
    period=classify(title)
    if not period: return
    # Plain numeric titles sometimes describe numbers, not years. Do not silently call them years.
    if period.kind == 'year':
        if harvester.page_type(title, raw) != 'year' or harvester.nav_year(raw) != period.start:
            return
    headings={}; parents={}
    for line_no,line in enumerate(raw.splitlines(),1):
        h=HEADING.match(line)
        if h:
            level=len(h.group(1)); headings={k:v for k,v in headings.items() if k<level};headings[level]=h.group(2)
            parents={}; continue
        m=BULLET.match(line)
        if not m: continue
        depth=len(m.group(1)); text=m.group(2).strip()
        if not text: continue
        parents={k:v for k,v in parents.items() if k<depth}
        parent_context=[parents[k] for k in sorted(parents)]
        parents[depth]=text
        links=[]
        for x in LINK.finditer(text):
            target=x.group(1).strip()
            if target and not re.match(r'^(?:File|Image|Category|Template|Help|Special):',target,re.I):
                links.append({'title':target,'label':x.group(2) or target})
        key=f'{pageid}:{revid}:{line_no}'
        yield {'id':hashlib.sha256(key.encode()).hexdigest()[:24], 'status':'unverified_candidate',
          'source':{'title':title,'page_id':pageid,'revision_id':revid,'line':line_no,
                    'url':'https://en.wikipedia.org/w/index.php?title='+quote(title.replace(' ','_'))+'&oldid='+str(revid)},
          'period_context':{'kind':period.kind,'start':period.start,'end':period.end,'year_convention':'negative BCE; positive CE; no year zero'},
          'section_path':[headings[k] for k in sorted(headings)],'parent_bullets':parent_context,
          'raw_wikitext':text,'links':links}


def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--db',default='r2_wikipedia/crawl.sqlite3');a.add_argument('--out',default='r2_wikipedia/candidates.jsonl.gz');args=a.parse_args()
    c=sqlite3.connect(f'file:{Path(args.db).resolve()}?mode=ro',uri=True); count=pages=0
    with open(args.out,'wb') as f, gzip.GzipFile(filename='',fileobj=f,mode='wb',mtime=0) as out:
        for pid,title,rev,body in c.execute('select pageid,title,revid,wikitext_gzip from pages order by title'):
            if not classify(title): continue
            raw=gzip.decompress(body).decode('utf8'); n=0
            for row in candidates(pid,title,rev,raw) or ():
                out.write((json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n').encode());count+=1;n+=1
            if n:pages+=1
    print(f'Wrote {count} unverified candidate bullets from {pages} period pages to {args.out}')

if __name__=='__main__': main()
