"""Verified read and exact, guarded gzip restoration of Gandhi research archives."""
import gzip,hashlib,lzma,os,tempfile
from pathlib import Path
from storage_guard import within_budget
ROOT=Path(__file__).resolve().parent; FOCUS=ROOT/'focus'
SPECS={
 'project':('gandhi_project_raw.json','dc08d78f37c514a9dc8c61899be506b56c9356a58c6a8f7e61276f238231da53','324b304742ad8c733a9ee86dea70f644905900e9d17716d538523ade2b3db78d','0458c444e83e20b94c7a9a92106401e0934c5cfdc52dddec539835beb6bac76d'),
 'wikitext':('gandhi_wikipedia_saved_wikitext.txt','c7e3d87725145e6ac14c3e3502dbf8689cf0739f06483b07166354483472f8c5','ebbc0f584168d75db86db06f9ffe49ac4579458c5047fcd08638c59e422ba1d2','f4c75c07c5a66acb25e5dcefab12f6e964548998924bbbee6bc7e40e2a6a11b6')}
def digest(b):return hashlib.sha256(b).hexdigest()
def read(which):
 name,gh,rh,xh=SPECS[which];b=(FOCUS/(name+'.xz')).read_bytes()
 if digest(b)!=xh:raise ValueError('XZ checksum mismatch')
 raw=lzma.decompress(b)
 if digest(raw)!=rh:raise ValueError('Raw checksum mismatch')
 return raw
def restore(which):
 name,gh,rh,xh=SPECS[which];p=FOCUS/(name+'.gz')
 if p.exists():raise FileExistsError(p)
 b=gzip.compress(read(which),9,mtime=0)
 if digest(b)!=gh:raise ValueError('Gzip reproduction mismatch')
 if within_budget(125)[1]+len(b)>=125000000:raise RuntimeError('125 MB guard blocks restoration')
 cache=ROOT.parent/'.cache/r2-atomic-pack-stage';cache.mkdir(parents=True,exist_ok=True)
 if os.stat(cache).st_dev!=os.stat(FOCUS).st_dev:raise RuntimeError('Different staging filesystem')
 fd,tmp=tempfile.mkstemp(dir=cache,prefix='gandhi-restore-')
 try:
  with os.fdopen(fd,'wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
  os.link(tmp,p)
 finally:os.unlink(tmp)
 return p
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('which',choices=SPECS);a.add_argument('--restore',action='store_true');x=a.parse_args()
 if x.restore:print('Restored',restore(x.which))
 else:print('Verified raw bytes:',len(read(x.which)))
