"""Check or restore archived harvest/survey reports and a Worldfill research dataset."""
import hashlib,lzma,os,sys,tempfile
from pathlib import Path
from storage_guard import within_budget
ROOT=Path(__file__).resolve().parent.parent
SPECS={
 'worldfill/sources/money/wikidata_currencies.tsv':('16d8dc579027d3a55069f44dd3c3b6a1f4a1fd15a192657e904144da2e059476','360a396366506e184fafe6339622251387466f887a5b5221744879990d517312'),
 'harvest/events_v2_raw.jsonl.pages.json':('1976cbb1dc0118ff5937491737adf35b67a3a00b789afa1522517d5a0132e37f','54a93b509ace9ba3a311cf4a3c124b27b18d64793aea9fd940b43995b2f87c1c'),
 'survey/sources/sources_summary.json':('46a902a6d9deeb9b827ee96c4f41f68d98dd407e0ab4b99b9e9ee7b6459a4080','2ee9f92e3814a04aaec77dd08a34aed8d51a8a64c0948be0ec79f30da204e294'),
 'survey/sources/sources_density.json':('84faca12ee93cd1cf29bd403604550fbe1f3bebb3f9b46489fc05f50112a73ea','5289dba30d13812bb3c3aed413e3305825c43a635ea99020c7512e68c2446a13')}
def sha(b):return hashlib.sha256(b).hexdigest()
def read(name):
 rh,zh=SPECS[name];p=ROOT/name;z=p.with_name(p.name+'.xz').read_bytes()
 if sha(z)!=zh:raise ValueError('Compressed archive hash mismatch')
 raw=lzma.decompress(z)
 if sha(raw)!=rh:raise ValueError('Raw output hash mismatch')
 return raw
def restore(name):
 p=ROOT/name
 if p.exists():raise FileExistsError(p)
 data=read(name)
 if within_budget(125)[1]+len(data)>=125_000_000:raise RuntimeError('Storage guard blocks restore')
 cache=ROOT/'.cache/r2-atomic-pack-stage';cache.mkdir(parents=True,exist_ok=True)
 if os.stat(cache).st_dev!=os.stat(p.parent).st_dev:raise RuntimeError('Different staging filesystem')
 fd,tmp=tempfile.mkstemp(dir=cache,prefix='aux-report-')
 try:
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.link(tmp,p)
 finally:os.unlink(tmp)
 return p
if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('name',choices=SPECS);ap.add_argument('--restore',action='store_true');a=ap.parse_args()
 if a.restore:print('Restored:',restore(a.name))
 else:print('Verified raw bytes:',len(read(a.name)))
