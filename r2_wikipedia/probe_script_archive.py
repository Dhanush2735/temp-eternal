"""Load a verified Focus test shell script from its compact archive.

A wrapper invokes this script, then evaluates the verified original shell code;
$0 remains the wrapper's original pathname so the script's ROOT calculation and
arguments work unchanged. The archive contains the pre-wrapper script exactly.
"""
import hashlib,io,json,sys,tarfile
from pathlib import Path
import probe_source_archive as P
ROOT=Path(__file__).resolve().parent
MAP=ROOT/'focus/probe_shell_archive_1912_2026-11.json'
ARCHIVE=ROOT/'focus/probe_shells_1912_2026-11.tar.xz'
def sha(b):return hashlib.sha256(b).hexdigest()
def wrapper(name):
 return ('#!/usr/bin/env bash\nset -euo pipefail\nROOT="$(cd "$(dirname "$0")/.." && pwd)"\nSCRIPT="$(python3 "$ROOT/r2_wikipedia/probe_script_archive.py" "$(basename "$0")")"\neval "$SCRIPT"\n').encode()
def read(name):
 if Path(name).name!=name:raise ValueError('filename only')
 records=[r for r in P.records() if r['script']==name]
 if len(records)!=1:raise FileNotFoundError(name)
 m=json.loads(MAP.read_text());b=ARCHIVE.read_bytes()
 if sha(b)!=m['archive_sha256']:raise ValueError('Probe shell archive checksum mismatch')
 with tarfile.open(fileobj=io.BytesIO(b),mode='r:xz') as t:
  item=t.getmember(name)
  if not item.isfile() or Path(item.name).name!=item.name:raise ValueError('invalid member')
  raw=t.extractfile(item).read()
 if sha(raw)!=records[0]['script_converted_sha256']:raise ValueError('Probe shell hash mismatch')
 return raw
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('usage: probe_script_archive.py SHELL_FILENAME')
 sys.stdout.buffer.write(read(sys.argv[1]))
