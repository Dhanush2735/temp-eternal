"""Conservative connection-local SQLite growth caps for the people collector.

SQLite's max_page_count bounds the main database, including pages allocated inside a
transaction. It does not cap temporary journals, exports, other files or other processes.
"""
import sqlite3


def people_page_cap(db, db_limit_bytes, workspace_used_bytes, workspace_limit_bytes, reserve_bytes=500_000):
    if min(db_limit_bytes, workspace_limit_bytes) <= 0 or reserve_bytes < 0:
        raise ValueError('limits must be positive and reserve must be nonnegative')
    page_size=db.execute('pragma page_size').fetchone()[0]
    page_count=db.execute('pragma page_count').fetchone()[0]
    available=max(0,workspace_limit_bytes-workspace_used_bytes-reserve_bytes)
    # Reserve room for the biography export and other output that can grow alongside the DB.
    # This is an estimate; exports and transient files are not bounded by SQLite.
    workspace_db_ceiling=page_count*page_size+available//2
    cap=min(db_limit_bytes//page_size,workspace_db_ceiling//page_size)
    if cap<page_count:
        return None
    # PRAGMA does not accept bound parameters; `cap` is a calculated integer.
    effective=db.execute(f'pragma max_page_count={int(cap)}').fetchone()[0]
    return effective


def is_full(exc):
    return isinstance(exc,sqlite3.Error) and getattr(exc,'sqlite_errorcode',None)==sqlite3.SQLITE_FULL
