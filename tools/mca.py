"""Read entity/region .mca files and list what is inside, by entity type."""
import struct, zlib, sys, glob, collections, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nbtread import _read

def chunks(path):
    with open(path, 'rb') as f:
        head = f.read(4096)
        if len(head) < 4096:
            return
        for i in range(1024):
            off = struct.unpack('>I', b'\x00' + head[i*4:i*4+3])[0]
            if off == 0:
                continue
            f.seek(off * 4096)
            length = struct.unpack('>i', f.read(4))[0]
            comp = struct.unpack('>b', f.read(1))[0]
            data = f.read(length - 1)
            if comp == 2:
                data = zlib.decompress(data)
            elif comp == 1:
                import gzip; data = gzip.decompress(data)
            else:
                continue
            import io
            bio = io.BytesIO(data)
            tt = struct.unpack('>b', bio.read(1))[0]
            nl = struct.unpack('>h', bio.read(2))[0]
            bio.read(nl)
            yield (i % 32, i // 32), _read(bio, tt)

def walk_entities(node, out, depth=0):
    if isinstance(node, dict):
        if 'id' in node and isinstance(node.get('id'), str) and depth < 6:
            out.append(node)
        for v in node.values():
            walk_entities(v, out, depth + 1)
    elif isinstance(node, list):
        for v in node:
            walk_entities(v, out, depth + 1)

if __name__ == '__main__':
    total = collections.Counter()
    custom = []
    for path in sorted(glob.glob(sys.argv[1])):
        ents = []
        for pos, nbt in chunks(path):
            walk_entities(nbt, ents)
        c = collections.Counter(e.get('id', '?') for e in ents)
        if c:
            print(f"\n{os.path.basename(path)}: {sum(c.values())} entities")
            for k, v in c.most_common():
                print(f"   {v:4d}  {k}")
        total.update(c)
        for e in ents:
            if 'eternalengine' in str(e.get('id', '')) or 'Human' in str(e.get('id', '')) or 'eternalengine' in str(e):
                custom.append(e)
    print("\n=== TOTAL")
    for k, v in total.most_common():
        print(f"   {v:4d}  {k}")
    if custom:
        print("\n=== first two mod entities, raw:")
        print(json.dumps(custom[0], indent=1, default=str)[:2000])
