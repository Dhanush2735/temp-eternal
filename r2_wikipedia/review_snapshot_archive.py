"""Read and restore compacted inactive review snapshots with hash checks."""
import hashlib,json,lzma,os,tempfile
from pathlib import Path
from storage_guard import within_budget
ROOT=Path(__file__).resolve().parent;REVIEW=ROOT/'reviews';MANIFEST=REVIEW/'archived_review_reports_1920_2026-11.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(name):
 if Path(name).name!=name:raise ValueError('filename only')
 rows=[r for r in json.loads(MANIFEST.read_text())['files'] if r['former']==name]
 if name=='duplicate_event_ids.json':rows.append({'former':name,'archive':name+'.xz','sha256':'483464a853bb67f69413e68791615b767f0a82bd16a50a3dbab6559baa18a38a','archive_sha256':'376f8325b37f792ce669257d079f6aa81d6e0f1947031cd8714aacf4ee333b07'})
 if len(rows)!=1:raise FileNotFoundError(name)
 r=rows[0];p=REVIEW/r['archive']
 if Path(r['archive']).name!=r['archive']:raise ValueError('invalid archive path')
 b=p.read_bytes()
 if sha(b)!=r['archive_sha256']:raise ValueError('Archive checksum mismatch')
 raw=lzma.decompress(b)
 if sha(raw)!=r['sha256']:raise ValueError('Raw checksum mismatch')
 return raw
def restore(name):
 p=REVIEW/name
 if p.exists():raise FileExistsError(p)
 raw=read(name)
 if within_budget(125)[1]+len(raw)>=125000000:raise RuntimeError('125 MB guard blocks restoration')
 cache=ROOT.parent/'.cache/r2-atomic-pack-stage';cache.mkdir(parents=True,exist_ok=True)
 if os.stat(cache).st_dev!=os.stat(REVIEW).st_dev:raise RuntimeError('Staging is on a different filesystem')
 fd,tmp=tempfile.mkstemp(dir=cache,prefix='review-restore-')
 try:
  with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
  os.link(tmp,p)
 finally:os.unlink(tmp)
 return p
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('name');ap.add_argument('--restore',action='store_true');a=ap.parse_args()
 if a.restore:print('Restored',restore(a.name))
 else:print(read(a.name).decode('utf8'))
