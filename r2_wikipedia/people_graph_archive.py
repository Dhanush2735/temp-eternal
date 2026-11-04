"""Losslessly compress research-only people graphs; indexed gameplay JSON is untouched.

Former .json paths transparently load as .json.gz through load_json. The conversion
manifest records raw and compressed hashes, and restore refuses overwrites.
"""
from pathlib import Path
import gzip,hashlib,json,os,tempfile
ROOT=Path(__file__).resolve().parent.parent
SOURCES=ROOT/'eternal/src/main/resources/data/eternalengine/eternal/history/sources'
MAP=ROOT/'r2_wikipedia/focus/people_graph_gzip_1812_2026-10.json'
ADDITIONAL_MAP=ROOT/'r2_wikipedia/focus/people_graph_gzip_1862_2026-11.json'
def records():
 files=json.loads(MAP.read_text())['files']
 if ADDITIONAL_MAP.exists():files+=json.loads(ADDITIONAL_MAP.read_text())['files']
 return files
def sha(b):return hashlib.sha256(b).hexdigest()
def load_json(path):
 p=Path(path)
 if p.is_file():return json.loads(p.read_bytes())
 if p.resolve().parent!=SOURCES.resolve() or not p.name.endswith('_people_links.json'):raise FileNotFoundError(p)
 r=next((r for r in records() if r['former']==p.name),None)
 if r is None:raise FileNotFoundError(p)
 from research_solid_archive import gzip_for
 comp=gzip_for('graph',r)
 if sha(comp)!=r['gzip_sha256']:raise ValueError('Compressed graph hash mismatch')
 raw=gzip.decompress(comp)
 if sha(raw)!=r['raw_sha256']:raise ValueError('Graph raw hash mismatch')
 return json.loads(raw)
def restore(name):
 if Path(name).name!=name:raise ValueError('filename only')
 p=SOURCES/name
 if p.exists():raise FileExistsError(p)
 r=next(r for r in records() if r['former']==name)
 from research_solid_archive import gzip_for
 comp=gzip_for('graph',r);raw=gzip.decompress(comp)
 if sha(comp)!=r['gzip_sha256'] or sha(raw)!=r['raw_sha256']:raise ValueError('hash mismatch')
 p.write_bytes(raw)
 return p
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('name');n=a.parse_args().name
 print('Restored exact original bytes:',restore(n))
