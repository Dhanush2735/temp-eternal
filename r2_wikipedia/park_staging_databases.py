#!/usr/bin/env python3
"""Park/restore exact R2 staging SQLite databases, never active game data.

Parking makes the normal collectors and SQLite-based audits unavailable until
restoration; it is not a way around their workspace guard. Stop all writers
before using. Restore requires additional workspace space. Files are validated
before deletion and on restoration; no existing database is overwritten.
"""
import argparse,hashlib,json,lzma,os,sqlite3,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MAP=ROOT/'focus/staging_databases_parked_1812_2026-11.json'
NAMES=('crawl.sqlite3','people.sqlite3')
def sha(b):return hashlib.sha256(b).hexdigest()
def read_map():return json.loads(MAP.read_text(encoding='utf8')) if MAP.exists() else {'records':[]}
def save_map(m):
 temp=MAP.with_suffix('.tmp');temp.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(temp,MAP)
def check_sidecars(p):
 if any(Path(str(p)+s).exists() for s in ('-journal','-wal','-shm')):raise RuntimeError('SQLite sidecars exist; stop and checkpoint all users: '+str(p))
def integrity(p):
 db=sqlite3.connect(f'file:{p.resolve()}?mode=ro',uri=True)
 try:
  if db.execute('pragma integrity_check').fetchone()[0]!='ok' or db.execute('pragma foreign_key_check').fetchall():raise RuntimeError('SQLite integrity or foreign key check failed')
 finally:db.close()
def park(name):
 if name not in NAMES:raise ValueError('Unrecognized database')
 p=ROOT/name;z=ROOT/(name+'.xz');m=read_map()
 if not p.is_file() or z.exists() or any(r['name']==name for r in m['records']):raise RuntimeError('Missing database or archive already exists')
 check_sidecars(p)
 db=sqlite3.connect(p,timeout=0)
 try:
  db.execute('BEGIN EXCLUSIVE')
  if db.execute('pragma integrity_check').fetchone()[0]!='ok' or db.execute('pragma foreign_key_check').fetchall():raise RuntimeError('SQLite integrity or foreign key check failed')
  raw=p.read_bytes();rawsha=sha(raw);comp=lzma.compress(raw,preset=9)
  if lzma.decompress(comp)!=raw:raise RuntimeError('Compression roundtrip failed')
  # Persist and reread archive and its manifest before removing the original.
  with z.open('xb') as f:f.write(comp);f.flush();os.fsync(f.fileno())
  if sha(z.read_bytes())!=sha(comp) or sha(lzma.decompress(z.read_bytes()))!=rawsha:raise RuntimeError('Persisted archive failed validation')
  rec={'name':name,'archive':z.name,'raw_bytes':len(raw),'raw_sha256':rawsha,'archive_bytes':len(comp),'archive_sha256':sha(comp),'integrity':'ok','foreign_keys':'ok','status':'parked'}
  m['records'].append(rec);save_map(m)
  if sha(p.read_bytes())!=rawsha:raise RuntimeError('Database changed; original retained')
  p.unlink();return rec
 finally:db.rollback();db.close()
def unpack(name,destination=None):
 if name not in NAMES:raise ValueError('Unrecognized database')
 m=read_map();rec=next(x for x in m['records'] if x['name']==name);p=Path(destination) if destination else ROOT/name
 if p.exists():raise FileExistsError(p)
 check_sidecars(p);z=ROOT/rec['archive'];comp=z.read_bytes()
 if sha(comp)!=rec['archive_sha256']:raise ValueError('Archive hash mismatch')
 raw=lzma.decompress(comp)
 if len(raw)!=rec['raw_bytes'] or sha(raw)!=rec['raw_sha256']:raise ValueError('Database bytes mismatch')
 created=False
 try:
  with p.open('xb') as f:
   created=True;f.write(raw);f.flush();os.fsync(f.fileno())
  integrity(p)
 except BaseException:
  if created:p.unlink(missing_ok=True)
  raise
 return p
if __name__=='__main__':
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('action',choices=('park','restore','verify'));a.add_argument('name',choices=NAMES);x=a.parse_args()
 if x.action=='park':print(json.dumps(park(x.name)))
 elif x.action=='restore':print('Restored; compressed archive retained:',unpack(x.name))
 else:
  with tempfile.TemporaryDirectory() as t:unpack(x.name,Path(t)/x.name)
  print('Archive, original bytes and SQLite integrity verified')
