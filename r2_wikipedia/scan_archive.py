"""Read or restore exact historical indexed-scan snapshots consolidated in a tar.xz.

Existing requested files take precedence; only former paths listed in the map
are eligible for fallback. All restored raw and xz bytes are hash checked.
"""
import hashlib, json, lzma, tarfile
from pathlib import Path
FOCUS = Path(__file__).resolve().parent / 'focus'
MAP = FOCUS / 'indexed_scan_solid_1612_2026-10.json'
def sha(b): return hashlib.sha256(b).hexdigest()
def read_former(path):
    p = Path(path)
    if p.resolve().parent != FOCUS.resolve(): raise FileNotFoundError(p)
    m = json.loads(MAP.read_text())
    item = next((r for r in m['files'] if r['former'] == p.name), None)
    if not item: raise FileNotFoundError(p)
    archive = FOCUS / m['archive']
    if sha(archive.read_bytes()) != m['archive_sha256']: raise ValueError('Scan archive checksum mismatch')
    with tarfile.open(archive, 'r:xz') as tar:
        raw = tar.extractfile(item['member']).read()
    if sha(raw) != item['raw_sha256']: raise ValueError('Scan member checksum mismatch')
    return raw

def read(path):
    p = Path(path)
    return lzma.decompress(p.read_bytes()) if p.exists() else read_former(p)

def restore(path):
    p = Path(path)
    if p.exists(): raise FileExistsError(p)
    m = json.loads(MAP.read_text())
    item = next(r for r in m['files'] if r['former'] == p.name)
    compressed = lzma.compress(read_former(p), preset=9)
    if sha(compressed) != item['compressed_sha256']: raise ValueError('Original xz byte hash mismatch')
    p.write_bytes(compressed)
    return True

if __name__ == '__main__':
    import argparse
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('name', help='former indexed_start_scan_*.txt.xz name')
    x = a.parse_args()
    if Path(x.name).name != x.name: raise ValueError('filename only')
    restore(FOCUS / x.name)
    print('Restored original, byte-identical xz.')
