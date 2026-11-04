#!/usr/bin/env python3
"""A reader for `countries.grid.gz`, for the builders that need to ask the map a question.

The mod reads this file in Java, in `civilization/CountryGrid.java`, which needs a Minecraft
classpath to compile. The builders are Python and need the same answer, so this is the same format
read the same way - and it exists so that a builder can never disagree with the mod about which
country a point is in.

Format (from `CountryGrid.load()`):

    int32   magic   0x45454347 ("EECG")
    int32   version
    int32   width   (3600)
    int32   height  (1800)
    int32   n       number of countries
    n x     utf code, utf name, utf subregion, float, float, float mainLat, float mainLon, int32
    h x     int32 k, then k x (int16 runLength, int16 value)

Everything is BIG-endian: Java's `DataInputStream` reads multi-byte values most-significant byte
first, and an `int16` read as little-endian gives run lengths of a few thousand, so every x lands
past the end of the row and the whole map reads as sea.

    value 0 is sea; otherwise 1 + the country index - exactly as the Java has it.
"""

import gzip
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
FILE = os.path.normpath(os.path.join(
    HERE, "..", "eternal", "src", "main", "resources", "data", "eternalengine", "eternal",
    "history", "countries.grid.gz"))

MAGIC = 0x45454347


class Grid:
    """The country grid: codes, names, and which country a point is in."""

    def __init__(self, path=FILE):
        with gzip.open(path, "rb") as f:
            buf = f.read()
        self._b = buf
        self._i = 0
        if self._u32() != MAGIC:
            raise ValueError("%s: not a country grid" % path)
        self._u32()                                  # version
        self.width = self._u32()
        self.height = self._u32()
        n = self._u32()
        self.codes, self.names, self.subs = [], [], []
        self.main_lat, self.main_lon = [], []
        for _ in range(n):
            self.codes.append(self._utf())
            self.names.append(self._utf())
            self.subs.append(self._utf())
            self._f32()
            self._f32()
            self.main_lat.append(self._f32())
            self.main_lon.append(self._f32())
            self._u32()
        self.rows = []
        for _ in range(self.height):
            k = self._u32()
            row = struct.unpack_from(">%dh" % (2 * k), buf, self._i)
            self._i += 4 * k
            self.rows.append(row)
        self.index = {c: i for i, c in enumerate(self.codes)}

    # ------------------------------------------------------------------ primitives

    def _u32(self):
        v = struct.unpack_from(">I", self._b, self._i)[0]
        self._i += 4
        return v

    def _f32(self):
        v = struct.unpack_from(">f", self._b, self._i)[0]
        self._i += 4
        return v

    def _utf(self):
        """Java's modified UTF-8: a 2-byte length then that many bytes."""
        n = struct.unpack_from(">H", self._b, self._i)[0]
        self._i += 2
        s = self._b[self._i:self._i + n].decode("utf-8", "replace")
        self._i += n
        return s

    # ------------------------------------------------------------------ the questions

    def _value_at(self, x, y):
        row = self.rows[y]
        acc = 0
        for k in range(0, len(row) - 1, 2):
            length = row[k] & 0xFFFF
            if x < acc + length:
                return row[k + 1] & 0xFFFF
            acc += length
        return 0

    def index_at(self, lat, lon):
        """The country of a point: its own square, else the nearest land square within 3."""
        x = min(max(int((lon + 180.0) * 10.0), 0), self.width - 1)
        y = min(max(int((90.0 - lat) * 10.0), 0), self.height - 1)
        v = self._value_at(x, y)
        if v > 0:
            return v - 1
        for r in range(1, 4):
            for dy in range(-r, r + 1):
                for dx in range(-r, r + 1):
                    if max(abs(dx), abs(dy)) != r:
                        continue
                    yy = y + dy
                    if yy < 0 or yy >= self.height:
                        continue
                    xx = (x + dx) % self.width
                    w = self._value_at(xx, yy)
                    if w > 0:
                        return w - 1
        return -1

    def code_at(self, lat, lon):
        i = self.index_at(lat, lon)
        return self.codes[i] if i >= 0 else ""

    def name_at(self, lat, lon):
        i = self.index_at(lat, lon)
        return self.names[i] if i >= 0 else ""

    def __len__(self):
        return len(self.codes)


_GRID = None


def grid():
    """One copy for the process: reading 6.5 million squares twice is not worth it."""
    global _GRID
    if _GRID is None:
        _GRID = Grid()
    return _GRID


if __name__ == "__main__":
    g = grid()
    print("countries.grid.gz: %d countries, %dx%d squares (%.1f kB)"
          % (len(g), g.width, g.height, len(g._b) / 1024.0))
    for lat, lon, want in ((47.0, 2.0, "France"), (22.0, 78.0, "India"),
                           (36.0, 138.0, "Japan"), (-22.9, -43.2, "Brazil"),
                           (39.5, -8.0, "Portugal"), (0.0, -30.0, "(sea)")):
        print("  %8.3f, %8.3f -> %-12s %s" % (lat, lon, g.code_at(lat, lon) or "(none)",
                                              g.name_at(lat, lon)))
