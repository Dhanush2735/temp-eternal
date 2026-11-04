"""Restore the exact 2026-11-01 pre-consolidation solid archives, without overwriting.

Restores byte-for-byte by preserving archived tar member metadata and order.
Destination should normally be temporary; restoring into the workspace needs
space and leaves the consolidated archive in place.
"""
import io,json,hashlib,tarfile
from pathlib import Path
FOCUS=Path(__file__).resolve().parent/'focus'
SPECS={'annual':('annual_ce_12_1661_original_1862.json','annual_ce_solid_1512_2026-10.json'), 'scan':('indexed_scan_12_1611_original_1862.json','indexed_scan_solid_1612_2026-10.json')}
def sha(b):return hashlib.sha256(b).hexdigest()
def restore(kind,dest):
 oldname,newname=SPECS[kind];old=json.loads((FOCUS/oldname).read_text());new=json.loads((FOCUS/newname).read_text());source=FOCUS/new['archive'];dest=Path(dest)
 if dest.exists():raise FileExistsError(dest)
 if sha(source.read_bytes())!=new['archive_sha256']:raise ValueError('Current archive checksum mismatch')
 created=False
 try:
  with tarfile.open(source,'r:xz') as src,tarfile.open(dest,'x:xz',preset=9) as out:
   created=True
   for r in old['files']:
    member=src.getmember(r['member']);raw=src.extractfile(member).read()
    if sha(raw)!=r['raw_sha256']:raise ValueError('Member checksum mismatch')
    out.addfile(member,io.BytesIO(raw))
  if sha(dest.read_bytes())!=old['archive_sha256']:raise ValueError('Previous archive byte checksum mismatch')
 except BaseException:
  if created:dest.unlink(missing_ok=True)
  raise
 return dest
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('kind',choices=SPECS);p.add_argument('destination');a=p.parse_args();print('Restored exact original archive:',restore(a.kind,a.destination))
