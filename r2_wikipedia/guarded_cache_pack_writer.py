"""Stage a verified gzip pack off-snapshot on the destination filesystem.

Atomic replacement remains per pack, not across packs. The persistent 125 MB
workspace guard is checked against projected usage before each replacement.
The cache file is disposable; an interrupted stage leaves the original pack.
"""
import gzip,json,os,stat,tempfile
from pathlib import Path
from storage_guard import within_budget
ROOT=Path('/home/user');CACHE=ROOT/'.cache/r2-atomic-pack-stage';LIMIT=125_000_000
def write_atomic_gzip(path,doc):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 if not path.resolve().is_relative_to(ROOT):
  from apply_reviewed_events import write_atomic_gzip as plain
  return plain(path,doc)
 CACHE.mkdir(parents=True,exist_ok=True)
 if os.stat(CACHE).st_dev!=os.stat(path.parent).st_dev:raise RuntimeError('Cache and destination are on different filesystems')
 mode=stat.S_IMODE(path.stat().st_mode) if path.exists() else None
 fd,tmp=tempfile.mkstemp(prefix='verified-pack-',suffix='.gz',dir=CACHE)
 try:
  with os.fdopen(fd,'wb') as raw:
   with gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as out:out.write(json.dumps(doc,ensure_ascii=False,separators=(',',':')).encode('utf8'))
   raw.flush();os.fsync(raw.fileno())
  with gzip.open(tmp,'rt',encoding='utf8') as f:
   if json.load(f)!=doc:raise ValueError('Output verification failed')
  old=path.stat().st_size if path.exists() else 0;new=os.stat(tmp).st_size
  ok,used=within_budget(125)
  if not ok or used-old+new>=LIMIT:raise RuntimeError('125 MB workspace guard blocks pack replacement')
  if mode is not None:os.chmod(tmp,mode)
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
