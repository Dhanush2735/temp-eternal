"""Use an archived Focus Java probe without permanently restoring it.

The manifest pins both source and compressed SHA-256. `extract` writes a new
copy to a caller-owned temporary directory; `restore` writes the former source
path and refuses overwrite. Test scripts use extract, preserving their usage.
"""
import gzip,hashlib,json,lzma,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PROBES=ROOT/'java_probe';MAP=ROOT/'focus/probe_source_archives_1902_2026-11.jsonl'
def sha(b):return hashlib.sha256(b).hexdigest()
def records():
 if MAP.exists():raw=MAP.read_bytes()
 else:
  meta=json.loads((MAP.parent/'probe_source_archives_1902_map.json').read_text());b=Path(str(MAP)+'.gz').read_bytes()
  if sha(b)!=meta['gzip_sha256']:raise ValueError('Probe journal gzip hash mismatch')
  raw=gzip.decompress(b)
  if sha(raw)!=meta['raw_sha256']:raise ValueError('Probe journal raw hash mismatch')
 return [json.loads(line) for line in raw.splitlines() if line]
def record(name):
 if Path(name).name!=name or not name.startswith('Focus') or not name.endswith('Probe.java'):raise ValueError('invalid probe name')
 matches=[r for r in records() if r['name']==name]
 if len(matches)!=1:raise FileNotFoundError(name)
 return matches[0]
def read(name):
 r=record(name);p=PROBES/name
 if p.exists():raw=p.read_bytes()
 else:
  b=(PROBES/(name+'.xz')).read_bytes()
  if sha(b)!=r['xz_sha256']:raise ValueError('compressed probe hash mismatch')
  raw=lzma.decompress(b)
 if len(raw)!=r['raw_bytes'] or sha(raw)!=r['raw_sha256']:raise ValueError('probe source hash mismatch')
 return raw
def write(name,destination):
 dest=Path(destination)
 if dest.exists():raise FileExistsError(dest)
 raw=read(name)
 with dest.open('xb') as f:f.write(raw)
 return dest
if __name__=='__main__':
 if len(sys.argv)!=4 or sys.argv[1] not in ('extract','restore'):raise SystemExit('usage: probe_source_archive.py extract|restore NAME DESTINATION_DIRECTORY')
 action,name,folder=sys.argv[1:];dest=Path(folder)/name
 if action=='restore' and dest.resolve().parent!=PROBES.resolve():raise SystemExit('restore destination must be java_probe directory')
 print(write(name,dest))
