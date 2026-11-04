"""Minimal NBT reader: enough for level.dat, playerdata and the mod's .dat files."""
import gzip, struct, sys, json

def _read(f, t):
    if t == 0: return None
    if t == 1: return struct.unpack('>b', f.read(1))[0]
    if t == 2: return struct.unpack('>h', f.read(2))[0]
    if t == 3: return struct.unpack('>i', f.read(4))[0]
    if t == 4: return struct.unpack('>q', f.read(8))[0]
    if t == 5: return struct.unpack('>f', f.read(4))[0]
    if t == 6: return struct.unpack('>d', f.read(8))[0]
    if t == 7:
        n = struct.unpack('>i', f.read(4))[0]; return list(f.read(n))
    if t == 8:
        n = struct.unpack('>h', f.read(2))[0]; return f.read(n).decode('utf-8', 'replace')
    if t == 9:
        it = struct.unpack('>b', f.read(1))[0]
        n = struct.unpack('>i', f.read(4))[0]
        return [_read(f, it) for _ in range(n)]
    if t == 10:
        out = {}
        while True:
            tt = struct.unpack('>b', f.read(1))[0]
            if tt == 0: return out
            nl = struct.unpack('>h', f.read(2))[0]
            name = f.read(nl).decode('utf-8', 'replace')
            out[name] = _read(f, tt)
    if t == 11:
        n = struct.unpack('>i', f.read(4))[0]
        return [struct.unpack('>i', f.read(4))[0] for _ in range(n)]
    if t == 12:
        n = struct.unpack('>i', f.read(4))[0]
        return [struct.unpack('>q', f.read(8))[0] for _ in range(n)]
    raise ValueError(f"tag {t}")

def load(path):
    with open(path, 'rb') as f:
        head = f.read(2)
        f.seek(0)
        f = gzip.open(path, 'rb') if head == b'\x1f\x8b' else f
        tt = struct.unpack('>b', f.read(1))[0]
        nl = struct.unpack('>h', f.read(2))[0]
        name = f.read(nl).decode('utf-8', 'replace')
        return name, _read(f, tt)

if __name__ == '__main__':
    n, d = load(sys.argv[1])
    print(n)
    print(json.dumps(d, indent=1, default=str)[:int(sys.argv[2]) if len(sys.argv) > 2 else 4000])
