"""Losslessly gzip non-indexed Wikipedia research source files.

No active history index packs are included. load() accepts the former JSON
path; restore() writes the exact original JSON and refuses overwrites.
"""
import gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SOURCES=ROOT.parent/'eternal/src/main/resources/data/eternalengine/eternal/history/sources'
MAP=ROOT/'focus/research_sources_gzip_1812_2026-11.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def read(path):
 p=Path(path)
 if p.exists():return p.read_bytes()
 if p.resolve().parent!=SOURCES.resolve():raise FileNotFoundError(p)
 m=json.loads(MAP.read_text());r=next((r for r in m['files'] if r['former']==p.name),None)
 if not r:raise FileNotFoundError(p)
 from research_solid_archive import gzip_for
 b=gzip_for('source',r)
 if sha(b)!=r['gzip_sha256']:raise ValueError('gzip hash mismatch')
 raw=gzip.decompress(b)
 if sha(raw)!=r['raw_sha256']:raise ValueError('original hash mismatch')
 return raw
def load(path):return json.loads(read(path))
def restore(name):
 if Path(name).name!=name:raise ValueError('filename only')
 p=SOURCES/name
 if p.exists():raise FileExistsError(p)
 raw=read(p)
 with p.open('xb') as f:f.write(raw)
 return p
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('name');v=a.parse_args();print('Restored exact original JSON bytes:',restore(v.name))
