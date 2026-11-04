#!/usr/bin/env python3
"""Losslessly consolidate historical Java snapshot archives (never active code).

Uncompressed tar bytes are packed into one solid XZ archive. Each original gzip
is reproducible and verified with GNU gzip -n -6. Manifests record both tar and
gzip SHA-256; restoration refuses changed files and fails closed if the local
gzip cannot reproduce the exact original bytes. Stop writers before maintenance.
"""
import argparse,gzip,hashlib,io,json,os,re,stat,subprocess,tarfile,tempfile
from pathlib import Path
ARCHIVE='legacy_java_snapshots.tar.xz';MANIFEST='legacy_java_snapshots.manifest.json'
PATTERN=re.compile(r'^(?:step[0-9]+[a-z]?|atlasB|turn89)_java_after\.tar\.gz$')
def sha(data):return hashlib.sha256(data).hexdigest()
def gzencode(raw):
 return subprocess.run(['gzip','-n','-6','-c'],input=raw,stdout=subprocess.PIPE,check=True).stdout
def safe_name(name):
 return Path(name).name==name and bool(PATTERN.fullmatch(name))
def read_checked(folder):
 folder=Path(folder);m=json.loads((folder/MANIFEST).read_text());archive=folder/ARCHIVE
 if sha(archive.read_bytes())!=m['archive_sha256']:raise ValueError('Archive checksum mismatch')
 records=m['files'];by={r['name']:r for r in records}
 if not records or len(by)!=len(records) or any(not safe_name(n) for n in by):raise ValueError('Invalid manifest')
 raw={}
 with tarfile.open(archive,'r:xz') as t:
  for item in t:
   if not item.isfile() or item.name not in by or item.name in raw:raise ValueError('Unexpected archive member')
   data=t.extractfile(item).read();r=by[item.name]
   if len(data)!=r['tar_size'] or sha(data)!=r['tar_sha256']:raise ValueError('Tar bytes checksum mismatch '+item.name)
   raw[item.name]=data
 if set(raw)!=set(by):raise ValueError('Missing archive member')
 return m,raw
def pack(folder):
 folder=Path(folder);archive=folder/ARCHIVE;mp=folder/MANIFEST
 if archive.exists() or mp.exists():raise FileExistsError('Archive/manifest exists')
 ps=sorted(folder.glob('*java_after.tar.gz'))
 if not ps or any(p.is_symlink() or not p.is_file() or not safe_name(p.name) for p in ps):raise ValueError('Unsafe snapshot file')
 records=[];contents={}
 for p in ps:
  binary=p.read_bytes();raw=gzip.decompress(binary)
  if gzencode(raw)!=binary:raise ValueError('Exact gzip reconstruction not supported: '+p.name)
  st=p.stat();records.append({'name':p.name,'gzip_size':len(binary),'gzip_sha256':sha(binary),'tar_size':len(raw),'tar_sha256':sha(raw),'mode':stat.S_IMODE(st.st_mode),'mtime_ns':st.st_mtime_ns});contents[p.name]=raw
 fd,tmp=tempfile.mkstemp(prefix='.java-snapshot-',suffix='.tar.xz',dir=folder);os.close(fd)
 try:
  with tarfile.open(tmp,'w:xz',preset=6) as t:
   for r in records:
    data=contents[r['name']];ti=tarfile.TarInfo(r['name']);ti.size=len(data);ti.mode=0o644;t.addfile(ti,io.BytesIO(data))
  os.replace(tmp,archive)
  m={'schema':'legacy-java-snapshot-archive-v1','archive':ARCHIVE,'archive_sha256':sha(archive.read_bytes()),'files':records,'restore_command':'python r2_wikipedia/archive_java_snapshots.py restore','note':'Archive stores exact uncompressed tar streams; restore requires gzip -n -6 capable of reproducing the recorded original gzip bytes. Both hashes are checked.'}
  mp.write_text(json.dumps(m,indent=2)+'\n')
  _,verified=read_checked(folder)
  for p,r in zip(ps,records):
   if sha(p.read_bytes())!=r['gzip_sha256'] or gzencode(verified[p.name])!=p.read_bytes():raise ValueError('Source changed or gzip mismatch')
  for p in ps:p.unlink()
  return {'files':len(ps),'original_bytes':sum(r['gzip_size'] for r in records),'archive_bytes':archive.stat().st_size,'manifest_bytes':mp.stat().st_size}
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
def restore(folder):
 folder=Path(folder);m,contents=read_checked(folder);payloads={}
 for r in m['files']:
  p=folder/r['name'];data=gzencode(contents[r['name']]);payloads[r['name']]=data
  if len(data)!=r['gzip_size'] or sha(data)!=r['gzip_sha256']:raise ValueError('Local gzip cannot reproduce exact original '+r['name'])
  if p.is_symlink() or (p.exists() and (not p.is_file() or sha(p.read_bytes())!=r['gzip_sha256'])):raise FileExistsError('Refusing to overwrite '+str(p))
 for r in m['files']:
  p=folder/r['name']
  if p.exists():continue
  fd,tmp=tempfile.mkstemp(dir=folder,prefix='.restoring-java-')
  try:
   with os.fdopen(fd,'wb') as f:f.write(payloads[r['name']]);f.flush();os.fsync(f.fileno())
   os.chmod(tmp,r['mode']);os.utime(tmp,ns=(r['mtime_ns'],r['mtime_ns']));os.replace(tmp,p)
  finally:
   if os.path.exists(tmp):os.unlink(tmp)
 return len(m['files'])
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['pack','restore','verify']);ap.add_argument('--folder',default='worldfill');ap.add_argument('--allow-over-budget',action='store_true',help='Restore even if the 125 MB workspace guard would be exceeded');a=ap.parse_args()
 if a.action=='pack':print(json.dumps(pack(a.folder),indent=2))
 elif a.action=='restore':
  from storage_guard import workspace_bytes,ROOT
  folder=Path(a.folder).resolve();m,_=read_checked(folder)
  if folder.is_relative_to(ROOT):
   extra=sum(r['gzip_size'] for r in m['files'] if not (folder/r['name']).exists())
   projected=workspace_bytes()+extra
   if projected>=125_000_000 and not a.allow_over_budget:
    raise SystemExit(f'Restoring all snapshots would use approximately {projected/1_000_000:.2f} MB, exceeding the workspace guard; arrange more space first.')
  print('Restored',restore(folder),'verified snapshots')
 else:
  m,data=read_checked(a.folder)
  for r in m['files']:
   if sha(gzencode(data[r['name']]))!=r['gzip_sha256']:raise ValueError('gzip reconstruction failed')
  print('Verified',len(data),'snapshots, including original gzip hashes')
