"""Read or reconstruct the exact pre-compaction R2 progress ledger."""
import hashlib,lzma,sys
from pathlib import Path
R=Path(__file__).resolve().parent;F=R/'focus'
SPECS=[('progress_snapshot_1939_part1.md.xz', 'c2a28c7e1a80a7dd4be1e8ce1cf0a8ae7fb99605df1236aee5a0e43b76493ba2', '4b4c1154fb70f957489bfd07682a69ebb6aa506ad0bd4437dfe1937d5757facb', 28748), ('progress_snapshot_1939_part2.md.xz', '57ff46a25fc3f6eb656b0a2f4180254fffe5877e48b505a83338c6641c2c9565', '9ce32d23e46447a149ba326bda2e3330f0200e8c7d0d270ce9cfb6e3d1183d7b', 38601)]
ORIGINAL_SHA='67c373e3a731206c994a89ec71dcfa6a6e5d7842fa90bd2cc3c89d41b909e64b'
def sha(b):return hashlib.sha256(b).hexdigest()
def read():
 out=[]
 for name,raw_hash,xz_hash,length in SPECS:
  b=(F/name).read_bytes()
  if sha(b)!=xz_hash:raise ValueError('progress archive mismatch')
  d=lzma.decompress(b)
  if sha(d)!=raw_hash or len(d)!=length:raise ValueError('progress segment mismatch')
  out.append(d)
 data=b''.join(out)
 if sha(data)!=ORIGINAL_SHA:raise ValueError('original ledger mismatch')
 return data
if __name__=='__main__':
 if sys.argv[1:]==['--print']:
  sys.stdout.buffer.write(read())
 else:print('Verified original progress ledger bytes:',len(read()))
