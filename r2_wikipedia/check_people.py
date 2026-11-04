#!/usr/bin/env python3
"""Integrity and provenance checks for the R3 candidate database; not fact checking."""
import gzip,json,sqlite3,sys
from pathlib import Path
from staged_exports import open_text as open_staged_text
from people import is_human

p=Path('r2_wikipedia/people.sqlite3')
if not p.exists():sys.exit('missing people database')
db=sqlite3.connect(f'file:{p.resolve()}?mode=ro',uri=True);fail=[]
if db.execute('pragma integrity_check').fetchone()[0]!='ok':fail.append('SQLite integrity check')
if db.execute('pragma foreign_key_check').fetchall():fail.append('foreign key check')
rows=db.execute('select pageid,title,wiki_revid,qid,wikidata_revid,wiki_gzip,wikidata_gzip from biographies').fetchall()
for pid,title,rev,qid,wdrev,wiki,wd in rows:
 try:
  text=gzip.decompress(wiki).decode('utf8');entity=json.loads(gzip.decompress(wd));
  if not text or rev<=0 or wdrev<=0 or not is_human(entity) or entity.get('id')!=qid:fail.append(f'{title}: missing revision/source or human confirmation')
  if not db.execute('select count(*) from subjects s join origin_links l on l.subject_id=s.id where s.canonical=?',(title,)).fetchone()[0]:fail.append(f'{title}: no discovery provenance')
 except Exception as e: fail.append(f'{title}: {e}')
exports=[]
try:
 with open_staged_text('r2_wikipedia/people_candidates.jsonl.gz') as f:exports=[json.loads(l) for l in f]
 if len(exports)!=len(rows):fail.append('export count differs from database')
 if any(not r.get('discovered_from') for r in exports):fail.append('exported record lacks source link')
except Exception as e:fail.append(f'export: {e}')
print('candidate biographies:',len(rows),'export records:',len(exports))
print('subject statuses:',dict(db.execute('select status,count(*) from subjects group by status')))
print('provenance and integrity:', 'FAIL' if fail else 'PASS')
for f in fail:print('FAIL',f)
print('This checks data integrity, not whether historical statements are true or usable in-game.')
sys.exit(bool(fail))
