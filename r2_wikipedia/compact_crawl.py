#!/usr/bin/env python3
"""Drop a redundant crawl queue index and verify every data table remains identical."""
import argparse,json,os,sqlite3
from pathlib import Path
from compact_people import fingerprint
TABLES=(('frontier','title'),('pages','pageid'),('edges','source_pageid,source_revid,target_title'),('resolutions','requested_title'),('scheduler_state','key'))
def snapshot(db):return {name:fingerprint(db,name,order) for name,order in TABLES}
def compact(db):
 before=snapshot(db)
 db.execute('DROP INDEX IF EXISTS queue_order');db.commit()
 db.execute('VACUUM')
 if snapshot(db)!=before:raise ValueError('A data table changed during compaction')
 if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok' or db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Database integrity or foreign keys failed')
 return before

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--db',default='r2_wikipedia/crawl.sqlite3');p.add_argument('--log',default='r2_wikipedia/crawl_compaction_log.json');args=p.parse_args()
 old=os.path.getsize(args.db);db=sqlite3.connect(args.db); db.execute('PRAGMA foreign_keys=ON');data=compact(db);db.close();new=os.path.getsize(args.db)
 r={'original_bytes':old,'compacted_bytes':new,'saved_bytes':old-new,'logical_record_fingerprints':data,'integrity':'ok','foreign_keys':'ok'}
 Path(args.log).write_text(json.dumps(r,indent=2)+'\n',encoding='utf8');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
