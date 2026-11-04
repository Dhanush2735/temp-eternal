"""Read losslessly compressed annual-title snapshots; current JSON wins."""
import gzip,json,hashlib
from pathlib import Path
FOCUS=Path(__file__).resolve().parent/'focus'
def source(path):
 p=Path(path)
 if p.exists():return p
 if p.resolve().parent==FOCUS.resolve() and p.name.startswith('year_titles_') and p.suffix=='.json':
  q=p.with_suffix('.json.gz')
  if q.is_file():return q
 return p
def load(path):
 p=source(path)
 with (gzip.open(p,'rt',encoding='utf8') if p.suffix=='.gz' else open(p,encoding='utf8')) as f:return json.load(f)
def paths():
 # Yield logical JSON paths once; if both exist, the current plain JSON wins.
 result={p.name:p for p in FOCUS.glob('year_titles*.json')}
 for p in FOCUS.glob('year_titles*.json.gz'):
  logical=p.with_suffix('');result.setdefault(logical.name,logical)
 return sorted(result.values())
def restore(name):
 if Path(name).name!=name:raise ValueError('filename only')
 p=FOCUS/name
 if p.exists():raise FileExistsError(p)
 m=json.loads((FOCUS/'title_gzip_1562_2026-10.json').read_text());r=next(x for x in m['files'] if x['original']==name)
 raw=gzip.decompress((FOCUS/r['compressed']).read_bytes())
 if hashlib.sha256(raw).hexdigest()!=r['raw_sha256']:raise ValueError('Raw checksum mismatch')
 p.write_bytes(raw)
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('name');args=a.parse_args();restore(args.name);print('Restored exact JSON bytes')
