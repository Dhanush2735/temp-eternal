"""Archive the converted Focus shell tests and replace each with a small wrapper.

Verified archives and hashes are persisted before wrappers are installed; a
partial run leaves either the original script or a working verified wrapper.
"""
import io,json,os,tarfile
from pathlib import Path
import probe_source_archive as P
import probe_script_archive as S
from archive_focus_probes import atomic_script
from storage_guard import within_budget
LIMIT=125_000_000
def main():
 rows=P.records();out=io.BytesIO()
 if S.ARCHIVE.exists() or S.MAP.exists():raise FileExistsError('Archive or map exists; inspect partial run')
 with tarfile.open(fileobj=out,mode='w:xz',preset=9) as t:
  for r in rows:
   raw=(P.ROOT/r['script']).read_bytes()
   if P.sha(raw)!=r['script_converted_sha256']:raise ValueError('Unexpected shell script')
   ti=tarfile.TarInfo(r['script']);ti.size=len(raw);ti.mtime=0;t.addfile(ti,io.BytesIO(raw))
 b=out.getvalue();meta=(json.dumps({'schema':'probe-shell-solid-v1','archive':S.ARCHIVE.name,'archive_sha256':S.sha(b),'member_count':len(rows)},indent=2)+'\n').encode()
 if within_budget(125)[1]+len(b)+len(meta)+1024>=LIMIT:raise RuntimeError('Guard blocks solid archive')
 with S.ARCHIVE.open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 with S.MAP.open('xb') as f:f.write(meta);f.flush();os.fsync(f.fileno())
 for r in rows:
  if S.read(r['script'])!=(P.ROOT/r['script']).read_bytes():raise ValueError('Archive verification failed')
 for r in rows:
  p=P.ROOT/r['script']
  if P.sha(p.read_bytes())!=r['script_converted_sha256']:raise ValueError('Changed script; originals or archives remain')
  atomic_script(p,S.wrapper(r['script']))
 print('wrapped',len(rows),'scripts; saved',sum(len(S.read(r['script'])) for r in rows)-sum((P.ROOT/r['script']).stat().st_size for r in rows)-len(b)-len(meta))
if __name__=='__main__':main()
