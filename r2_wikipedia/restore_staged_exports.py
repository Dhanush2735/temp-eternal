#!/usr/bin/env python3
"""Restore exact former gzip snapshots from the retained lossless xz archives.

Recreates both gzip files in the project. This uses about 2.3 MB of persistent
space; remove only the restored gzip copies if space is needed again. Fails if
one already exists or a verified checksum does not match.
"""
import gzip,hashlib,lzma,os,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
EXPECTED={'history_candidates':'d9f17dd2864ac9cb5be022b945b703496b74b767a0a148eaf597b5f881a76a36','people_candidates':'b663006deadac3fc100d7365a7f54b64339630e44d21a3276f3207d3102e4584'}
def digest(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  while b:=f.read(1<<20):h.update(b)
 return h.hexdigest()
def main():
 outs=[ROOT/(name+'.jsonl.gz') for name in EXPECTED]
 if any(p.exists() for p in outs):raise FileExistsError('Refusing to overwrite existing exports')
 temp=[]
 try:
  for name,want in EXPECTED.items():
   fd,path=tempfile.mkstemp(dir=ROOT,prefix='.restoring-',suffix='.gz');os.close(fd);p=Path(path);temp.append(p)
   with lzma.open(ROOT/(name+'.jsonl.xz'),'rb') as src,open(p,'wb') as raw,gzip.GzipFile(filename='',fileobj=raw,mode='wb',mtime=0) as dst:
    while b:=src.read(1<<20):dst.write(b)
   if digest(p)!=want:raise ValueError('Restored content failed checksum '+name)
  for p,out in zip(temp,outs):os.replace(p,out)
  print('Restored both verified gzip exports; archives retained.')
 finally:
  for p in temp:p.unlink(missing_ok=True)
if __name__=='__main__':main()
