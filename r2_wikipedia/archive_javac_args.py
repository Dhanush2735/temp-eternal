#!/usr/bin/env python3
"""Archive historical worldfill javac argument files without deleting their contents.

A verified, self-contained archive and SHA-256 manifest replace direct patch
files. Game sources and runtime assets are untouched. Restore is explicit; it
refuses to overwrite a changed compiler argument file and verifies every byte before installation.
"""
import argparse,hashlib,json,os,stat,tarfile,tempfile
from pathlib import Path

ARCHIVE='legacy_javac_args.tar.xz'
MANIFEST='legacy_javac_args.manifest.json'

def digest(data):return hashlib.sha256(data).hexdigest()
def file_digest(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()

def read_checked(folder):
 folder=Path(folder);manifest=json.loads((folder/MANIFEST).read_text(encoding='utf8'));archive=folder/ARCHIVE
 if file_digest(archive)!=manifest['archive_sha256']:raise ValueError('Archive SHA-256 mismatch')
 records=manifest['files'];expected={r['name']:r for r in records}
 if len(expected)!=len(records):raise ValueError('Duplicate names in manifest')
 for name in expected:
  if Path(name).name!=name or not name.startswith('javac.') or not name.endswith('.args'):raise ValueError('Invalid archive path')
 result={}
 with tarfile.open(archive,'r:xz') as tar:
  for member in tar:
   if not member.isfile() or member.name not in expected or member.name in result:raise ValueError('Unexpected archive member')
   content=tar.extractfile(member).read();r=expected[member.name]
   if len(content)!=r['size'] or digest(content)!=r['sha256']:raise ValueError('Archive member checksum mismatch: '+member.name)
   result[member.name]=content
 if set(result)!=set(expected):raise ValueError('Missing archive member')
 return manifest,result

def pack(folder):
 folder=Path(folder);archive=folder/ARCHIVE;manifest_path=folder/MANIFEST
 if archive.exists() or manifest_path.exists():raise FileExistsError('Archive or manifest already exists')
 paths=sorted(folder.glob('javac.*.args'))
 if not paths:raise ValueError('No legacy compiler argument files found')
 if any(not p.is_file() or p.is_symlink() for p in paths):raise ValueError('Only regular, non-symlink compiler argument files are supported')
 records=[]
 for p in paths:
  st=p.stat();records.append({'name':p.name,'size':st.st_size,'sha256':file_digest(p),'mode':stat.S_IMODE(st.st_mode),'mtime_ns':st.st_mtime_ns})
 fd,tmp=tempfile.mkstemp(prefix='.javac-args-',suffix='.tar.xz',dir=folder);os.close(fd)
 try:
  with tarfile.open(tmp,'w:xz',preset=6) as tar:
   for p in paths:tar.add(p,arcname=p.name,recursive=False)
  os.replace(tmp,archive)
  manifest={'schema':'javac-args-archive-v1','archive':ARCHIVE,'archive_sha256':file_digest(archive),'files':records,
   'restore_command':'python r2_wikipedia/archive_javac_args.py restore','note':'Only historical compiler argument files are archived; current source files and game assets are unchanged.'}
  # Persist the manifest before any removal. If interrupted, some originals may remain.
  manifest_path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
  _,contents=read_checked(folder)
  for p,r in zip(paths,records):
   if p.read_bytes()!=contents[p.name]:raise ValueError('Original changed; refusing to remove '+p.name)
  for p in paths:p.unlink()
  return {'files':len(records),'original_bytes':sum(r['size'] for r in records),'archive_bytes':archive.stat().st_size,'manifest_bytes':manifest_path.stat().st_size}
 finally:
  if os.path.exists(tmp):os.unlink(tmp)

def restore(folder):
 folder=Path(folder);manifest,contents=read_checked(folder)
 # Preflight every path before writing anything, avoiding partial restore on conflict.
 for r in manifest['files']:
  p=folder/r['name']
  if p.is_symlink() or (p.exists() and (not p.is_file() or file_digest(p)!=r['sha256'])):
   raise FileExistsError('Refusing to overwrite differing file: '+str(p))
 for r in manifest['files']:
  p=folder/r['name']
  if p.exists():continue
  fd,tmp=tempfile.mkstemp(prefix='.restore-javac-arg-',dir=folder)
  try:
   with os.fdopen(fd,'wb') as f:f.write(contents[r['name']])
   os.chmod(tmp,r['mode']);os.utime(tmp,ns=(r['mtime_ns'],r['mtime_ns']));os.replace(tmp,p)
  finally:
   if os.path.exists(tmp):os.unlink(tmp)
 return len(manifest['files'])

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('action',choices=['pack','verify','restore']);ap.add_argument('--folder',default='worldfill');ap.add_argument('--allow-over-budget',action='store_true',help='Restore even if the resulting workspace would exceed the 125 MB guard');a=ap.parse_args()
 if a.action=='pack':print(json.dumps(pack(a.folder),indent=2))
 elif a.action=='verify':print('Verified',len(read_checked(a.folder)[1]),'archived compiler argument files')
 else:
  from storage_guard import workspace_bytes,ROOT
  folder=Path(a.folder).resolve();manifest,_=read_checked(folder)
  if folder.is_relative_to(ROOT):
   additional=sum(r['size'] for r in manifest['files'] if not (folder/r['name']).exists())
   projected=workspace_bytes()+additional
   if projected>=125_000_000 and not a.allow_over_budget:
    raise SystemExit(f'Restore would use approximately {projected/1_000_000:.2f} MB, exceeding the workspace guard. Free space or use --allow-over-budget only after arranging persistent storage.')
  print('Restored',restore(folder),'compiler argument files; verified archive retained')
if __name__=='__main__':main()
