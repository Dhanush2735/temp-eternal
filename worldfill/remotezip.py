#!/usr/bin/env python3
"""Read members of a huge remote zip with HTTP Range requests, without downloading all of it.

HYDE 3.2.1's baseline is a single 5.3 GB zip on DANS; the world-fill build needs a few
population grids from it. zipfile only needs seek() and read(), so this file-like object
fetches the byte ranges zipfile asks for (in 1 MB blocks, a few cached).
"""
import collections, io, time, urllib.request, zipfile

UA = "EternalEngineWorldFill/1.0 (historical data build; research use)"


class RemoteFile(io.RawIOBase):
    BLOCK = 1 << 20

    def __init__(self, url, size=None, cache_blocks=24):
        self.url, self.pos = url, 0
        self.cache = collections.OrderedDict()
        self.cache_blocks = cache_blocks
        self.size = size if size is not None else self._probe_size()
        self.requests = 0
        self.bytes = 0

    def _get(self, start, end, tries=6):
        for i in range(tries):
            try:
                req = urllib.request.Request(self.url, headers={"Range": f"bytes={start}-{end}", "User-Agent": UA})
                with urllib.request.urlopen(req, timeout=300) as r:
                    data = r.read()
                self.requests += 1
                self.bytes += len(data)
                if len(data) != end - start + 1:
                    raise IOError(f"short read {len(data)} != {end - start + 1}")
                return data
            except Exception as e:                       # noqa: BLE001
                if i == tries - 1:
                    raise
                time.sleep(3 * (i + 1))

    def _probe_size(self):
        req = urllib.request.Request(self.url, headers={"Range": "bytes=0-0", "User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as r:
            cr = r.headers.get("Content-Range", "")
        return int(cr.rsplit("/", 1)[-1])

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=0):
        if whence == 0:
            self.pos = off
        elif whence == 1:
            self.pos += off
        else:
            self.pos = self.size + off
        return self.pos

    def _block(self, b):
        if b in self.cache:
            self.cache.move_to_end(b)
            return self.cache[b]
        start = b * self.BLOCK
        end = min(self.size, start + self.BLOCK) - 1
        data = self._get(start, end)
        self.cache[b] = data
        if len(self.cache) > self.cache_blocks:
            self.cache.popitem(last=False)
        return data

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        n = max(0, min(n, self.size - self.pos))
        if n == 0:
            return b""
        if n > 4 * self.BLOCK:                      # big member: one request, no caching
            data = self._get(self.pos, self.pos + n - 1)
            self.pos += n
            return data
        out = bytearray()
        while n > 0:
            b, o = divmod(self.pos, self.BLOCK)
            chunk = self._block(b)[o:o + n]
            out += chunk
            self.pos += len(chunk)
            n -= len(chunk)
        return bytes(out)

    def readinto(self, buf):
        data = self.read(len(buf))
        buf[:len(data)] = data
        return len(data)


def open_remote_zip(url, size=None):
    return zipfile.ZipFile(RemoteFile(url, size))


if __name__ == "__main__":
    import sys
    z = open_remote_zip(sys.argv[1])
    for i in z.infolist()[: int(sys.argv[2]) if len(sys.argv) > 2 else 50]:
        print(i.filename, i.file_size, i.compress_size)
    print(len(z.infolist()), "members")
