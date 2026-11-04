#!/usr/bin/env python3
"""Losslessly replace the people queue index with a smaller pending-only index.

Run as an exclusive maintenance operation with no active people collectors or writers.
A temporary copy is migrated and verified before atomic installation. The temporary
backup is in excluded cache and is NOT durable across workspace snapshots.
"""
import argparse
import hashlib
import json
import os
import sqlite3
from contextlib import closing
from pathlib import Path
from compact_origin_links import full_snapshot
from people import export, next_batch

OLD_SQL = 'CREATE INDEX subject_queue ON subjects(status,first_source,id)'
NEW_SQL = "CREATE INDEX subject_queue ON subjects(first_source) WHERE status='pending'"


def verify(db):
    if db.execute('pragma integrity_check').fetchone()[0] != 'ok':
        raise ValueError('SQLite integrity check failed')
    if db.execute('pragma foreign_key_check').fetchall():
        raise ValueError('Foreign-key check failed')


def migrate_copy(db):
    """Apply on a disposable copy, verifying all saved logical data and queue order."""
    verify(db)
    index = db.execute("select sql from sqlite_master where type='index' and name='subject_queue'").fetchone()
    if index is None or index[0] != OLD_SQL:
        raise ValueError('Expected original subject_queue index; already migrated or unsupported')
    before = full_snapshot(db)
    batches = {n: next_batch(db, n) for n in (1, 5, 50, 1000)}
    db.execute('BEGIN IMMEDIATE')
    try:
        db.execute('DROP INDEX subject_queue')
        db.execute(NEW_SQL)
        if full_snapshot(db) != before or any(next_batch(db,n)!=v for n,v in batches.items()):
            raise ValueError('Logical contents or pending queue order changed')
        verify(db)
        db.commit()
    except BaseException:
        db.rollback()
        raise
    db.execute('VACUUM')
    if full_snapshot(db) != before or any(next_batch(db,n)!=v for n,v in batches.items()):
        raise ValueError('Post-vacuum logical contents or pending queue order changed')
    verify(db)
    return before


def digest_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--db', default='r2_wikipedia/people.sqlite3')
    ap.add_argument('--backup', default='/home/user/.cache/r2_compaction/people_before_queue.sqlite3')
    ap.add_argument('--working', default='/home/user/.cache/r2_compaction/people_queue_migrated.sqlite3')
    ap.add_argument('--log', default='r2_wikipedia/subject_queue_compaction_log.json')
    a=ap.parse_args()
    dbpath=Path(a.db).resolve(); backup=Path(a.backup).resolve(); work=Path(a.working).resolve()
    if len({dbpath,backup,work}) != 3: raise ValueError('Database, backup, and working paths must differ')
    for p in (backup,work):
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists():raise FileExistsError(f'Refusing to overwrite {p}')
    if dbpath.stat().st_dev != work.parent.stat().st_dev:raise ValueError('Working copy must be on the same filesystem for atomic replacement')
    # Avoid replacing a database with live rollback/WAL state; users must stop writers first.
    for suffix in ('-journal','-wal','-shm'):
        if Path(str(dbpath)+suffix).exists():raise ValueError('Live SQLite sidecar exists; stop writers and checkpoint first')
    original_size=dbpath.stat().st_size
    source=sqlite3.connect(dbpath, timeout=0)
    verify(source)
    with closing(sqlite3.connect(backup)) as b:source.backup(b)
    with closing(sqlite3.connect(work)) as w:source.backup(w)
    source_fingerprint=full_snapshot(source)
    # Export to cache so determinism and complete biography provenance are checked too.
    source_export=work.parent/'people_queue_before_export.jsonl.gz'
    dest_export=work.parent/'people_queue_after_export.jsonl.gz'
    export(source,source_export)
    copy=sqlite3.connect(work)
    migrated_fingerprint=migrate_copy(copy)
    export(copy,dest_export)
    if source_fingerprint != migrated_fingerprint or digest_file(source_export)!=digest_file(dest_export):
        raise ValueError('Source/working copy or exported biography provenance differed; original untouched')
    copy.close()
    # With no concurrent collectors, check one final time while holding an exclusive lock.
    source.execute('BEGIN EXCLUSIVE')
    try:
        if full_snapshot(source)!=source_fingerprint:raise ValueError('Source changed during migration; original untouched')
        with open(work,'rb') as f:os.fsync(f.fileno())
        os.replace(work,dbpath)
    finally:
        source.rollback();source.close()
    result={'original_bytes':original_size,'compacted_bytes':dbpath.stat().st_size,
            'saved_bytes':original_size-dbpath.stat().st_size,'logical_fingerprints':source_fingerprint,
            'export_sha256':digest_file(dest_export),'integrity':'ok','foreign_keys':'ok',
            'queue_orders_checked':[1,5,50,1000], 'temporary_backup':str(backup),
            'note':'Backup and test exports are excluded from persisted snapshots; stop all collectors before maintenance.'}
    Path(a.log).write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
