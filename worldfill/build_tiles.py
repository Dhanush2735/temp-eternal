#!/usr/bin/env python3
"""Step 26 (system A4): storage that streams by region and era.

Builds a tile file from a data master: the rows are cut into tiles by region (a state, or a box of the map) and by era
(the century), each tile compressed on its own. The game keeps only the small compressed file in memory and opens a
tile when a player is near that place and era (com.eternalengine.data.TileStore and TileCache, with a size budget).

    python3 build_tiles.py            build every tile file
    python3 build_tiles.py --check    rebuild in memory and compare with the files in the mod (exit 1 if they differ)

Tile files built here:
  history/famous_people.tiles  from history/famous_people.json.gz (the master; it is kept in the source tree for the
                               scripts and left out of the mod's jar, see eternal/build.gradle)
  history/presence.tiles       from history/presence.json.gz (step 41, D11: the places a famous
                               person was, with the years and the reason; filed by the box of the
                               place and the century the row starts, with group "p" holding the
                               place names once)

File layout (big-endian, read by java.io.DataInputStream):
  8 bytes "EETILES1"; str dataset; str master sha256; int rows;
  int metas, then (str key, str value) each;
  int groups, then for each: str group; int tiles; then (int first bucket, int last bucket, int offset, int length,
  int rawLength, int rows): a tile holds whole buckets; small neighbouring buckets share a tile (at least
  MIN_ROWS rows, so that small tiles still compress well);
  int blob length; the blob (each tile deflate-compressed on its own).
  str = unsigned 16-bit byte length + UTF-8 bytes.

Famous people: one row = int row (its place in the master, after the rows with neither birth nor death are left out,
exactly as FamousPeople.read() does), str name, str description, int birth, int death (-2147483648 = unknown),
str state ("" = none), int lat and int lon in thousandths of a degree (the master has at most three decimals, so
lat / 1000.0 is exactly the double the master's text gives), short radiusKm.
  groups "s/<state id>" (people of a state) and "x" (people placed by distance): buckets by the century of the first
  year of their adult life (birth + 20, or death - 40);
  groups "b/<y>/<x>" (exact birthplaces, radiusKm <= 30, in 5-degree boxes): buckets by the century of birth.
"""
import gzip
import hashlib
import io
import json
import math
import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
HIST = os.path.join(HERE, "..", "eternal", "src", "main", "resources", "data", "eternalengine", "eternal", "history")
HIST = os.path.normpath(HIST)
UNKNOWN = -2147483648
BIRTHPLACE_KM = 30
BOX = 5
MIN_ROWS = 500
# The "q/" group of a person, from his QID alone so the mod can compute it without an index. It is
# a remainder and not a division: Wikidata QIDs run past 141 million, so qid // 1000 would make
# 141,735 groups of one person. 256 groups hold about 580 people and 1,400 rows each.
QID_GROUPS = 256


def s16(text):
    b = (text or "").encode("utf-8")
    if len(b) > 65535:
        b = b[:65535]
    return struct.pack(">H", len(b)) + b


def sha256_file(path):
    """The master's content hash, not its container's.

    The master is gzipped, and a gzip header carries an mtime: the same people, compressed twice
    a second apart, hash differently. The tiles record this hash to say which master they were cut
    from, and the check compares it, so hashing the file on disk made the pack go "OUT OF DATE"
    the moment anything regzipped the master without touching a single row (marking board 11,
    2026-10-23). Decompress before hashing: this value now depends on the data alone.
    """
    h = hashlib.sha256()
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_tiles(dataset, master_hash, rows, meta, groups):
    """groups: {name: {bucket: [raw row bytes, ...]}} -> the file bytes."""
    blob = io.BytesIO()
    index = []
    for g in sorted(groups):
        tiles = []
        keys = sorted(groups[g])
        cur, first = [], None
        for i, bucket in enumerate(keys):
            if first is None:
                first = bucket
            cur += groups[g][bucket]
            if len(cur) >= MIN_ROWS or i == len(keys) - 1:
                raw = b"".join(cur)
                comp = zlib.compress(raw, 9)
                tiles.append((first, bucket, blob.tell(), len(comp), len(raw), len(cur)))
                blob.write(comp)
                cur, first = [], None
        index.append((g, tiles))
    out = io.BytesIO()
    out.write(b"EETILES1")
    out.write(s16(dataset))
    out.write(s16(master_hash))
    out.write(struct.pack(">i", rows))
    out.write(struct.pack(">i", len(meta)))
    for k in sorted(meta):
        out.write(s16(k))
        out.write(s16(str(meta[k])))
    out.write(struct.pack(">i", len(index)))
    for g, tiles in index:
        out.write(s16(g))
        out.write(struct.pack(">i", len(tiles)))
        for t in tiles:
            out.write(struct.pack(">iiiiii", *t))
    data = blob.getvalue()
    out.write(struct.pack(">i", len(data)))
    out.write(data)
    return out.getvalue()


def famous_people():
    master = os.path.join(HIST, "famous_people.json.gz")
    with gzip.open(master, "rt", encoding="utf-8") as f:
        doc = json.load(f)
    people = []
    for r in doc["people"]:
        birth = UNKNOWN if r[2] is None else int(r[2])
        death = UNKNOWN if r[3] is None else int(r[3])
        if birth == UNKNOWN and death == UNKNOWN:
            continue
        people.append((r[0], r[1] or "", birth, death, r[4], float(r[5]), float(r[6]), int(r[7])))
    groups = {}
    living_back = died_back = died_ahead = 0
    births = 0
    states = set()
    stateless = 0
    max_radius = 0
    for row, (name, desc, birth, death, state, lat, lon, radius) in enumerate(people):
        active_from = birth + 20 if birth != UNKNOWN else death - 40
        active_to = death if death != UNKNOWN else birth + 70
        living_back = max(living_back, active_to - active_from)
        if death != UNKNOWN:
            died_back = max(died_back, death - active_from)
            died_ahead = max(died_ahead, active_from - death)
        ilat, ilon = round(lat * 1000), round(lon * 1000)
        assert ilat / 1000 == lat and ilon / 1000 == lon, (name, lat, lon)
        raw = (struct.pack(">i", row) + s16(name) + s16(desc) + struct.pack(">ii", birth, death) + s16(state or "")
               + struct.pack(">iih", ilat, ilon, radius))
        g = ("s/" + state) if state else "x"
        if state:
            states.add(state)
        else:
            stateless += 1
        groups.setdefault(g, {}).setdefault(active_from // 100, []).append(raw)
        # FIX (2026-10-22, the marking turn): the same person, in a group by the BOX of their own
        # place. The state groups answer "who of this state was alive then", which the game joins by
        # exact state id - and 19% of the pack's people are filed under an id the ruler register
        # never names for the year the player is standing in, so they were never found. With a
        # geographic group the same question can be asked of the land instead of the state:
        # "who of this place was alive then, whatever it was called".
        max_radius = max(max_radius, radius)
        gy = math.floor(lat + 90.0)
        gx = math.floor(lon + 180.0)
        groups.setdefault(f"g/{gy // BOX}/{gx // BOX}", {}).setdefault(active_from // 100, []).append(raw)
        if radius <= BIRTHPLACE_KM:
            births += 1
            cy = math.floor(lat + 90.0)
            cx = math.floor(lon + 180.0)
            born = birth if birth != UNKNOWN else death - 40
            groups.setdefault(f"b/{cy // BOX}/{cx // BOX}", {}).setdefault(born // 100, []).append(raw)
    meta = {"livingBack": living_back, "diedBack": died_back, "diedAhead": died_ahead, "birthplaces": births,
            "maxRadius": max_radius,
            "states": len(states), "stateless": stateless, "box": BOX, "birthplaceKm": BIRTHPLACE_KM, "minRows": MIN_ROWS,
            "source": doc.get("source", "")[:600]}
    data = write_tiles("famous_people", sha256_file(master), len(people), meta, groups)
    return os.path.join(HIST, "famous_people.tiles"), data, meta, len(groups)


def presence():
    """Step 41 (D11): where and when a famous person was, cut into tiles the same way.

    A row is filed **twice**, because D11 asks two questions:

    * ``b/<y>/<x>`` - the 5-degree box of **the place** - answers *who was here in this year*,
      which is the half that fixes SYSTEMS_PLAN line 507;
    * ``q/<n>`` - a bucket of a thousand people - answers *where was this person*, which is the
      *homes, courts and journeys* half, and which cannot be answered from the place boxes at all
      without reading the whole file.

    Both are bucketed by the century of the row's first year, and because a row covers a span and
    not a moment, ``maxSpan`` says how far back a query for one year has to open. The place names
    are kept once, in group ``p``, rather than repeated on every row.
    """
    master = os.path.join(HIST, "presence.json.gz")
    with gzip.open(master, "rt", encoding="utf-8") as f:
        doc = json.load(f)
    groups = {}
    table = io.BytesIO()
    table.write(struct.pack(">i", len(doc["places"])))
    for name, ilat, ilon in doc["places"]:
        table.write(s16(name) + struct.pack(">ii", ilat, ilon))
    groups["p"] = {0: [table.getvalue()]}

    max_span = 0
    for qid, place_id, a, b, why, est in doc["rows"]:
        name, ilat, ilon = doc["places"][place_id]
        raw = (struct.pack(">ii", qid, place_id)
               + struct.pack(">ii", UNKNOWN if a is None else a, UNKNOWN if b is None else b)
               + bytes((why, est)))
        if a is not None and b is not None and b > a:
            max_span = max(max_span, b - a)
        first = a if a is not None else b
        if first is None:
            continue
        century = first // 100
        # by the PLACE, for "who was here"; and again by the PERSON, for "where was he"
        cy = math.floor(ilat / 1000.0 + 90.0)
        cx = math.floor(ilon / 1000.0 + 180.0)
        groups.setdefault(f"b/{cy // BOX}/{cx // BOX}", {}).setdefault(century, []).append(raw)
        groups.setdefault("q/%d" % (qid % QID_GROUPS), {}).setdefault(century, []).append(raw)
    meta = {"maxSpan": max_span, "box": BOX, "minRows": MIN_ROWS, "qidGroups": QID_GROUPS,
            "places": len(doc["places"]),
            "whys": ";".join("%d=%s" % (w["id"], w["name"]) for w in doc["whys"]),
            "source": doc.get("source", "")[:600]}
    data = write_tiles("presence", sha256_file(master), len(doc["rows"]), meta, groups)
    return os.path.join(HIST, "presence.tiles"), data, meta, len(groups)


BUILDERS = [famous_people, presence]


def main(argv):
    check = "--check" in argv
    bad = 0
    for build in BUILDERS:
        path, data, meta, ngroups = build()
        name = os.path.basename(path)
        if check:
            same = os.path.exists(path) and open(path, "rb").read() == data
            print(f"{name}: {'up to date' if same else 'OUT OF DATE (run build_tiles.py)'}")
            bad += 0 if same else 1
            continue
        with open(path, "wb") as f:
            f.write(data)
        print(f"{name}: {len(data):,} bytes, {ngroups} groups; " +
              ", ".join(f"{k} {v}" for k, v in meta.items() if k != "source"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
