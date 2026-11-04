#!/usr/bin/env python3
"""Shared helpers for writing history packs into the Eternal Engine mod.

The mod reads packs through HistoryGazetteer:
  * history/index.json lists the pack files ("packs": [...]); a pack that is not listed
    is never loaded, and a pack that fails to parse is skipped silently, so every write
    here is followed by a re-read and a schema check.
  * a site needs lat, lon and occupiedStart (unless presentOnly); occupiedEnd defaults to
    "forever"; activeIn / occupiedIn are start <= year < end.
  * an event needs lat, lon and year or start; end defaults to start + 1.
"""
import gzip, io, json, math, os, re

MOD = "/home/user/eternal"
HISTORY = f"{MOD}/src/main/resources/data/eternalengine/eternal/history"
INDEX = f"{HISTORY}/index.json"


def load_index():
    with open(INDEX, encoding="utf-8") as f:
        return json.load(f)


def save_index(idx):
    tmp = INDEX + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(idx, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, INDEX)


def register(pack_file, after=None):
    """Add pack_file to index.json's packs (once), right after `after` if given."""
    idx = load_index()
    packs = idx["packs"]
    if pack_file in packs:
        return False
    if after and after in packs:
        packs.insert(packs.index(after) + 1, pack_file)
    else:
        packs.append(pack_file)
    save_index(idx)
    return True


class _GzWriter:
    """A gzip writer whose header carries no build time, closing the file beneath it too.

    gzip.open() stamps the current time into the 4-byte mtime field of the header, so the same pack
    written twice has two different SHA-256s while its content is identical. The mod compares every
    shipped file's SHA-256 against the manifest at load (DataManifest.verify), so a stray timestamp
    is not cosmetic: it turns a good install into "different content". Every writer in worldfill now
    goes through here, with mtime=0 (marking board 11, 2026-10-23).
    """

    def __init__(self, path, compresslevel=9):
        self.raw = open(path, "wb")
        # text mode is wrapped here, not by GzipFile: its text support takes no encoding argument on
        # Python 3.10's signature, and the packs are UTF-8 by law.
        self.gz = gzip.GzipFile(filename="", mode="wb", compresslevel=compresslevel,
                                fileobj=self.raw, mtime=0)
        self.text = io.TextIOWrapper(self.gz, encoding="utf-8")

    def __enter__(self):
        return self.text

    def __exit__(self, *exc):
        try:
            self.text.flush()
            self.gz.close()
        finally:
            self.raw.close()
        return False


def gzopen(path, compresslevel=9):
    """Open `path` for text writing with no timestamp in the gzip header."""
    return _GzWriter(path, compresslevel)


def _open(path, mode="rt"):
    """Packs named *.gz are gzipped (HistoryGazetteer reads them through gzip)."""
    if path.endswith(".gz"):
        if "w" in mode:
            return gzopen(path, 9)
        return gzip.open(path, mode, encoding="utf-8" if "t" in mode else None)
    return open(path, mode.replace("t", ""), encoding="utf-8")


def write_pack(pack_file, doc):
    """Minified like events_world.json (gzipped when the name ends in .gz); re-read to prove it
    parses. A plain-JSON copy of the same pack under the other name is removed, so the mod never
    holds both."""
    path = f"{HISTORY}/{pack_file}"
    tmp = path + ".tmp"
    with _open(tmp if not path.endswith(".gz") else tmp + ".gz", "wt") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    real_tmp = tmp if not path.endswith(".gz") else tmp + ".gz"
    with _open(real_tmp, "rt") as f:
        json.load(f)
    os.replace(real_tmp, path)
    other = path[:-3] if path.endswith(".gz") else path + ".gz"
    if os.path.exists(other):
        os.remove(other)
    return path


def rename_in_index(old, new):
    """Point index.json at a renamed pack file (e.g. x.json -> x.json.gz)."""
    idx = load_index()
    if old in idx["packs"] and new not in idx["packs"]:
        idx["packs"][idx["packs"].index(old)] = new
        save_index(idx)
        return True
    return False


def iter_pack_docs(exclude=()):
    idx = load_index()
    for p in idx["packs"]:
        if p in exclude:
            continue
        path = f"{HISTORY}/{p}"
        if not os.path.exists(path):
            continue
        with _open(path, "rt") as f:
            yield p, json.load(f)


def existing_events(exclude=()):
    out = []
    for p, d in iter_pack_docs(exclude):
        for e in d.get("events") or []:
            if "lat" not in e or "lon" not in e:
                continue
            s = e.get("start", e.get("year"))
            if s is None:
                continue
            out.append(dict(e, _pack=p, _start=s))
    return out


def existing_sites(exclude=()):
    out = []
    for p, d in iter_pack_docs(exclude):
        for s in d.get("sites") or []:
            if "lat" in s and "lon" in s:
                out.append(dict(s, _pack=p))
    return out


def haversine_km(lat1, lon1, lat2, lon2):
    """The mod's own formula (HistoricalPresence.haversineKm)."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


class Grid:
    """1-degree buckets for 'what is near here' lookups."""

    def __init__(self, items, lat=lambda x: x["lat"], lon=lambda x: x["lon"]):
        self.cells, self._lat, self._lon = {}, lat, lon
        for it in items:
            self.cells.setdefault((math.floor(lat(it)), math.floor(lon(it))), []).append(it)

    def near(self, la, lo, ring=1):
        gy, gx = math.floor(la), math.floor(lo)
        for dy in range(-ring, ring + 1):
            for dx in range(-ring, ring + 1):
                x = gx + dx
                if x < -180:
                    x += 360
                elif x >= 180:
                    x -= 360
                yield from self.cells.get((gy + dy, x), ())


def slug(s, maxlen=48):
    s = re.sub(r"[^a-z0-9]+", "_", (s or "").lower()).strip("_")
    return s[:maxlen] or "x"


def check_event(e):
    """The fields HistoryGazetteer.loadEvents needs, with sane values."""
    assert isinstance(e.get("id"), str) and e["id"], e
    assert -90 <= e["lat"] <= 90 and -180 <= e["lon"] <= 180, e
    assert isinstance(e["start"], int) and isinstance(e["end"], int) and e["end"] > e["start"], e
    assert e["start"] != 0, e


def check_site(s):
    assert isinstance(s.get("id"), str) and s["id"], s
    assert -90 <= s["lat"] <= 90 and -180 <= s["lon"] <= 180, s
    assert isinstance(s["occupiedStart"], int), s
    assert isinstance(s.get("occupiedEnd", 9999), int) and s.get("occupiedEnd", 9999) > s["occupiedStart"], s
