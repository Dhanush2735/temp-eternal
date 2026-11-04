"""Read/restore losslessly consolidated annual Wikipedia revisions.

Only the exact former workspace paths in the recorded manifest fall back to the
archive; existing files always take precedence. Tar members are read, not extracted.
"""
import hashlib,json,lzma,tarfile
from pathlib import Path
FOCUS=Path(__file__).resolve().parent/'focus'
MAP=FOCUS/'annual_ce_solid_1512_2026-10.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def read_former(path):
 p=Path(path)
 if p.resolve().parent!=FOCUS.resolve() or not MAP.is_file():raise FileNotFoundError(p)
 data=json.loads(MAP.read_text());r=next((x for x in data['files'] if x['former']==p.name),None)
 if r is None:raise FileNotFoundError(p)
 archive=FOCUS/data['archive']
 if sha(archive.read_bytes())!=data['archive_sha256']:raise ValueError('Annual archive checksum mismatch')
 with tarfile.open(archive,'r:xz') as tf:
  f=tf.extractfile(r['member'])
  if f is None:raise FileNotFoundError(r['member'])
  raw=f.read()
 if sha(raw)!=r['raw_sha256']:raise ValueError('Annual member checksum mismatch')
 return raw

def load_json(path):
 p=Path(path)
 if p.is_file():
  with (lzma.open(p,'rt',encoding='utf8') if p.suffix=='.xz' else open(p,encoding='utf8')) as f:return json.load(f)
 return json.loads(read_former(p))

def restore(path,allow_different_xz=False):
 p=Path(path)
 if p.exists():raise FileExistsError(p)
 manifest=json.loads(MAP.read_text());r=next(x for x in manifest['files'] if x['former']==p.name)
 raw=read_former(p);compressed=lzma.compress(raw,preset=9)
 if sha(compressed)!=r['compressed_sha256'] and not allow_different_xz:
  raise ValueError('Recompressed bytes differ from former xz; raw data match. Use --allow-different-xz explicitly.')
 p.write_bytes(compressed)
 return sha(compressed)==r['compressed_sha256']
def restore_original_solid_archive(path):
 """Recreate the former CE 12–1511 tar.xz, refusing overwrite and checking its exact byte hash."""
 import io
 p=Path(path)
 if p.exists():raise FileExistsError(p)
 original=json.loads((FOCUS/'annual_ce_12_1511_original_1612.json').read_text())
 current=json.loads(MAP.read_text());archive=FOCUS/current['archive']
 if sha(archive.read_bytes())!=current['archive_sha256']:raise ValueError('Annual archive checksum mismatch')
 try:
  with tarfile.open(archive,'r:xz') as src,tarfile.open(p,'w:xz',preset=9) as dest:
   for r in original['files']:
    raw=src.extractfile(r['member']).read()
    if sha(raw)!=r['raw_sha256']:raise ValueError('Member checksum mismatch')
    item=tarfile.TarInfo(r['member']);item.size=len(raw);item.mtime=0
    dest.addfile(item,io.BytesIO(raw))
  if sha(p.read_bytes())!=original['archive_sha256']:raise ValueError('Original solid archive byte hash mismatch')
 except BaseException:
  p.unlink(missing_ok=True);raise
 return True

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('name',help='Former year_wikitext_..._CE.json.xz filename');ap.add_argument('--allow-different-xz',action='store_true');a=ap.parse_args()
 if Path(a.name).name!=a.name:raise ValueError('filename only')
 same=restore(FOCUS/a.name,a.allow_different_xz);print('Restored raw-verified archive; original compressed bytes match:',same)
