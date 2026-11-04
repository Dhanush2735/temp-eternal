"""Restore exact original VIP staging gzip after freeing sufficient space.

Existing gzip is never overwritten. The normal readers prefer a newer gzip if
present and otherwise verify and read the archived xz via staged_exports.
"""
import gzip,hashlib,os,tempfile
from pathlib import Path
from staged_exports import source
from storage_guard import within_budget
ROOT=Path(__file__).resolve().parent
P=ROOT/'vip_candidates.jsonl.gz'
EXPECTED='aa21725fd93237a7e0fef204ae6aec1262763332ba1e17a5b0449c95c429f7b1'
RAW='475b3243160b2aaca9d1ac52040d3348e3bff403238d44a75929a8a965efe672'
SPECS={'vip':(P,RAW,EXPECTED),'timelines':(ROOT/'person_timelines.jsonl.gz','8b958c94248a5c26126aab6bde9c2579791f91ee10d281d20fbb4b277de39391','76af1608a0dccfd842b064d37a7f948d6f0ca42e4caeb2bfe514758bd12a9c6b'),'places':(ROOT/'place_candidates.jsonl.gz','7effff1c6e2f647a5cd7b4d5a5230b738449d816def8d6c31cf10e06384fd117','6dfcea9aa5a459a1af8e6a6936856dbd9223c9bd616c9c8ad1efb647b5c623ab'),'events':(ROOT/'event_reconciliation.jsonl.gz','8b631a7a40e3f468bbfc7a9af650830dd2d136045d238b0ca0dd06808fb395bb','7764909415903e311115435d7a8d562e659141a12692fb06f6fd92c6746e7239')}
def restore(kind='vip'):
 import lzma
 p,raw_hash,gzip_hash=SPECS[kind]
 if p.exists():raise FileExistsError(p)
 x=source(p);raw=lzma.decompress(x.read_bytes())
 if hashlib.sha256(raw).hexdigest()!=raw_hash:raise ValueError('Raw SHA-256 mismatch')
 b=gzip.compress(raw,compresslevel=9,mtime=0)
 if hashlib.sha256(b).hexdigest()!=gzip_hash:raise ValueError('Gzip bytes differ from original; refusing restore')
 if within_budget(125)[1]+len(b)>=125000000:raise RuntimeError('125 MB guard refuses restore; free space first')
 cache=ROOT.parent/'.cache/r2-atomic-pack-stage';cache.mkdir(parents=True,exist_ok=True)
 if os.stat(cache).st_dev!=os.stat(ROOT).st_dev:raise RuntimeError('Staging is on a different filesystem')
 fd,tmp=tempfile.mkstemp(dir=cache,prefix='vip-restore-')
 try:
  with os.fdopen(fd,'wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
  os.link(tmp,p)  # atomic no-overwrite publication
 finally:os.unlink(tmp)
 return p
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('kind',choices=SPECS,default='vip',nargs='?');print('Restored',restore(ap.parse_args().kind))
