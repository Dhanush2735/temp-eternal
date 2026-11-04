#!/usr/bin/env python3
"""Repack the people DB without changing data or schema.

Run only with all collectors stopped. The compacted copy and temporary backup are
in excluded cache by default; the backup will not persist in workspace snapshots.
Validates every physical table, schema, queue order and biography export before an
atomic replacement. Does not raise storage limits or change game files.
"""
import argparse,hashlib,json,os,sqlite3,stat
from pathlib import Path
from contextlib import closing
from compact_people import fingerprint
from people import export,next_batch


def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()


def verify(c):
    if c.execute('pragma integrity_check').fetchone()[0]!='ok':raise ValueError('Integrity failure')
    if c.execute('pragma foreign_key_check').fetchall():raise ValueError('Foreign-key failure')


def snapshot(c):
    schema=c.execute("select type,name,tbl_name,sql from sqlite_master where name not like 'sqlite_stat%' order by type,name").fetchall()
    # Include every table, including the persistent people scheduler and sqlite_sequence.
    tables=[row[1] for row in schema if row[0]=='table']
    data={}
    for name in tables:
        safe='"'+name.replace('"','""')+'"'
        cols=c.execute('pragma table_info('+safe+')').fetchall()
        if not cols:raise ValueError('No columns: '+name)
        data[name]=fingerprint(c,safe,','.join(str(i+1) for i in range(len(cols))))
    return {'schema':schema,'tables':data}


def compact(dbpath,work,backup,before_export,after_export):
    dbpath,work,backup,before_export,after_export=[Path(x).resolve() for x in (dbpath,work,backup,before_export,after_export)]
    if len({dbpath,work,backup,before_export,after_export})!=5:raise ValueError('Paths must be distinct')
    for p in (work,backup,before_export,after_export):
        p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists():raise FileExistsError('Refusing to overwrite '+str(p))
    if not dbpath.is_file():raise FileNotFoundError(dbpath)
    if dbpath.stat().st_dev!=work.parent.stat().st_dev:raise ValueError('Working file must be on same filesystem')
    for suffix in ('-journal','-wal','-shm'):
        if Path(str(dbpath)+suffix).exists():raise ValueError('SQLite sidecar exists; stop collectors and checkpoint first')
    before_size=dbpath.stat().st_size; mode=stat.S_IMODE(dbpath.stat().st_mode)
    src=sqlite3.connect(dbpath,timeout=0);dest=None
    try:
        verify(src);baseline=snapshot(src)
        cursors=(None,src.execute("select value from people_scheduler where key='last_source'").fetchone())
        saved_cursor=cursors[1][0] if cursors[1] else None
        queues={(n,cur):next_batch(src,n,cur) for cur in (None,saved_cursor) for n in (1,5,50,1000)}
        export(src,before_export)
        with closing(sqlite3.connect(backup)) as b:src.backup(b)
        src.execute('VACUUM INTO ?', (str(work),))
        dest=sqlite3.connect(work);verify(dest)
        if snapshot(dest)!=baseline:raise ValueError('Compacted schema or data differs; original untouched')
        if any(next_batch(dest,n,cur)!=v for (n,cur),v in queues.items()):raise ValueError('Queue order changed; original untouched')
        export(dest,after_export)
        if digest(before_export)!=digest(after_export):raise ValueError('Biography export differs; original untouched')
        dest.close();dest=None
        if work.stat().st_size>=before_size:raise ValueError('No space saving; original untouched')
        os.chmod(work,mode)
        # Exclusive lock and last full check reduce race risk. Collectors must still be stopped.
        src.execute('BEGIN EXCLUSIVE')
        try:
            if snapshot(src)!=baseline:raise ValueError('Source changed during maintenance; original untouched')
            with open(work,'rb') as f:os.fsync(f.fileno())
            os.replace(work,dbpath)
            dfd=os.open(dbpath.parent,os.O_RDONLY)
            try:os.fsync(dfd)
            finally:os.close(dfd)
        finally:src.rollback()
    finally:
        if dest:dest.close()
        src.close()
    return {'original_bytes':before_size,'compacted_bytes':dbpath.stat().st_size,
            'saved_bytes':before_size-dbpath.stat().st_size,'logical_snapshot':baseline,
            'export_sha256':digest(after_export),'integrity':'ok','foreign_keys':'ok',
            'queue_orders_checked':[1,5,50,1000], 'temporary_backup':str(backup),
            'note':'All physical tables and schema checked; temporary backup is excluded from snapshots. Stop all collectors before maintenance.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--db',default='r2_wikipedia/people.sqlite3')
    p.add_argument('--prefix',default='/home/user/.cache/r2_compaction/people_vacuum_2026_10')
    p.add_argument('--log',default='r2_wikipedia/people_vacuum_log.json');a=p.parse_args()
    r=compact(a.db,a.prefix+'.work.sqlite3',a.prefix+'.backup.sqlite3',a.prefix+'.before.gz',a.prefix+'.after.gz')
    Path(a.log).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Saved',r['saved_bytes'],'bytes; data, schema, queue, export and integrity checked')

if __name__=='__main__':main()
