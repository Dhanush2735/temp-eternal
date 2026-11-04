"""Read retained staging snapshots: prefer current gzip, fall back to lossless xz."""
import gzip,lzma,hashlib
from pathlib import Path
NAMES={'history_candidates.jsonl.gz','people_candidates.jsonl.gz','candidates.jsonl.gz','vip_candidates.jsonl.gz','event_reconciliation.jsonl.gz','person_timelines.jsonl.gz','place_candidates.jsonl.gz'}
HERE=Path(__file__).resolve().parent
def source(path):
 p=Path(path)
 if p.exists():return p
 # Only fall back for these exact original paths, never silently substitute a
 # custom missing path. .xz content was checked against original decompressed data.
 if p.name in NAMES and p.resolve()==(HERE/p.name).resolve():
  x=p.with_suffix('.xz')
  if x.is_file():
   if p.name=='vip_candidates.jsonl.gz' and hashlib.sha256(x.read_bytes()).hexdigest()!='7e72cc40c8a4a7c69223d49ddbf1675314a5cd15a7c579740dffa27e7289f8f0':raise ValueError('VIP staging archive checksum mismatch')
   if p.name=='event_reconciliation.jsonl.gz' and hashlib.sha256(x.read_bytes()).hexdigest()!='c6b8748c936a019f7aa2a5a49622673c37d4a39a04a99591dd2221b1f302de91':raise ValueError('Event reconciliation archive checksum mismatch')
   if p.name=='person_timelines.jsonl.gz' and hashlib.sha256(x.read_bytes()).hexdigest()!='a0c58994ac06fe770ba187e9b0cb59b3f037dc5faf4d79fcb74d8ed58d94a6d3':raise ValueError('Timeline archive checksum mismatch')
   if p.name=='place_candidates.jsonl.gz' and hashlib.sha256(x.read_bytes()).hexdigest()!='04d1c9b9eb43db00979ea60755f4c617f26c857a3cffb800603f36408eb953d6':raise ValueError('Place archive checksum mismatch')
   return x
 return p
def open_text(path):
 p=source(path)
 return lzma.open(p,'rt',encoding='utf8') if p.suffix=='.xz' else gzip.open(p,'rt',encoding='utf8')
