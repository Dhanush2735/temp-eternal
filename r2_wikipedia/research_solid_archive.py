"""Read losslessly consolidated, non-indexed research JSON archives.

The original per-file gzip streams are reproducible and their recorded SHA-256
is verified before they are returned or restored. Raw JSON hashes are checked
independently. The original manifests remain the authority for file names and
hashes. This archive is not used by the game loader or active history packs.
"""
import functools,gzip,hashlib,io,json,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FOCUS=ROOT/'focus'
SOURCES=ROOT.parent/'eternal/src/main/resources/data/eternalengine/eternal/history/sources'
MAP=FOCUS/'research_people_solid_2026-11.json'
MANIFESTS={'source':FOCUS/'research_sources_gzip_1812_2026-11.json','graph':FOCUS/'people_graph_gzip_1812_2026-10.json'}
def sha(b):return hashlib.sha256(b).hexdigest()
@functools.lru_cache(maxsize=8)
def _members(filename,digest):
 b=(FOCUS/filename).read_bytes()
 if sha(b)!=digest:raise ValueError('Solid archive hash mismatch')
 result={}
 with tarfile.open(fileobj=io.BytesIO(b),mode='r:xz') as t:
  for item in t:
   if not item.isfile() or Path(item.name).name!=item.name or item.name in result:raise ValueError('Invalid archive member')
   result[item.name]=t.extractfile(item).read()
 return result
def raw_for(kind,record):
 manifest=json.loads(MAP.read_text());matches=[g for g in manifest['groups'] if g['kind']==kind and record['former'] in g['members']]
 if len(matches)!=1:raise FileNotFoundError(record['former'])
 group=matches[0];raw=_members(group['archive'],group['sha256'])[record['former']]
 if len(raw)!=record['raw_bytes'] or sha(raw)!=record['raw_sha256']:raise ValueError('Raw JSON hash mismatch')
 return raw
def gzip_for(kind,record):
 p=SOURCES/record['gzip']
 if p.exists():b=p.read_bytes()
 else:b=gzip.compress(raw_for(kind,record),compresslevel=9,mtime=0)
 if len(b)!=record['gzip_bytes'] or sha(b)!=record['gzip_sha256']:raise ValueError('Exact original gzip cannot be reproduced with this gzip implementation')
 return b
def restore_gzip(kind,name):
 if kind not in MANIFESTS or Path(name).name!=name:raise ValueError('Invalid filename or kind')
 records=json.loads(MANIFESTS[kind].read_text())['files']
 extra=FOCUS/'people_graph_gzip_1862_2026-11.json'
 if kind=='graph' and extra.exists():records+=json.loads(extra.read_text())['files']
 rec=next((r for r in records if r['gzip']==name),None)
 if rec is None:raise FileNotFoundError(name)
 dest=SOURCES/name
 if dest.exists():raise FileExistsError(dest)
 b=gzip_for(kind,rec)
 with dest.open('xb') as f:f.write(b)
 return dest
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('kind',choices=MANIFESTS);p.add_argument('gzip_name');a=p.parse_args();print('Restored exact gzip bytes:',restore_gzip(a.kind,a.gzip_name))
