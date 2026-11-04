"""Consolidate already-gzipped research files in small, guarded, verified groups.

Research only: never touch indexed game packs. Before deleting a gzip, persist
and verify its archive, both original hashes and exact gzip reconstruction, and
register its group in the manifest. Interruption may leave duplicates, not loss.
No transient persistent workspace write may cross the existing 125 MB guard.
"""
import gzip,hashlib,io,json,os,tarfile
from pathlib import Path
import research_solid_archive as A
from storage_guard import within_budget
LIMIT=125_000_000
def sha(b):return hashlib.sha256(b).hexdigest()
def build(kind,records):
 output=io.BytesIO()
 with tarfile.open(fileobj=output,mode='w:xz',preset=9) as tar:
  for r in records:
   b=(A.SOURCES/r['gzip']).read_bytes();raw=gzip.decompress(b)
   if sha(b)!=r['gzip_sha256'] or sha(raw)!=r['raw_sha256'] or gzip.compress(raw,9,mtime=0)!=b:raise ValueError('Original not exactly reproducible: '+r['gzip'])
   ti=tarfile.TarInfo(r['former']);ti.size=len(raw);ti.mtime=0;tar.addfile(ti,io.BytesIO(raw))
 return output.getvalue()
def commit(kind,records,number):
 manifest=json.loads(A.MAP.read_text()) if A.MAP.exists() else {'schema':'research-people-solid-v1','groups':[]}
 if any(r['former'] in g['members'] for g in manifest['groups'] for r in records):raise ValueError('Already registered')
 blob=build(kind,records);name=f'research_people_solid_{number:02d}.tar.xz';path=A.FOCUS/name
 if path.exists():raise FileExistsError(path)
 group={'kind':kind,'archive':name,'sha256':sha(blob),'members':[r['former'] for r in records]};updated={**manifest,'groups':manifest['groups']+[group]};encoded=(json.dumps(updated,ensure_ascii=False,indent=2)+'\n').encode()
 ok,used=within_budget(125)
 if not ok or used+len(blob)+len(encoded)+4096>=LIMIT:raise RuntimeError('Guard blocks archive plus manifest staging')
 with path.open('xb') as f:f.write(blob);f.flush();os.fsync(f.fileno())
 # Verify durable compressed bytes and every member before registration/deletion.
 allraw=A._members(name,sha(blob))
 for r in records:
  raw=allraw[r['former']]
  if sha(raw)!=r['raw_sha256'] or sha(gzip.compress(raw,9,mtime=0))!=r['gzip_sha256']:raise ValueError('Persisted archive verification failed')
 tmp=A.MAP.with_suffix('.json.tmp')
 with tmp.open('xb') as f:f.write(encoded);f.flush();os.fsync(f.fileno())
 os.replace(tmp,A.MAP)
 # Verify all originals again before removing any. If interrupted after this
 # point, registered archive or remaining originals are each usable.
 for r in records:
  if sha((A.SOURCES/r['gzip']).read_bytes())!=r['gzip_sha256']:raise ValueError('Original changed; originals retained')
 for r in records:(A.SOURCES/r['gzip']).unlink()
 print(kind,number,'files',len(records),'archive',len(blob),'saved',sum(r['gzip_bytes'] for r in records)-len(blob))
if __name__=='__main__':
 for kind in ('source','graph'):
  records=json.loads(A.MANIFESTS[kind].read_text())['files']
  for i in range(0,len(records),40):
   number=(1 if kind=='source' else 4)+i//40
   commit(kind,records[i:i+40],number)
