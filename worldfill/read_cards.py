#!/usr/bin/env python3
"""Step 41 (D11, C11), part 2: read the knowledge cards that step 27 shipped.

    python3 read_cards.py --dump    write build/cards_dump.json.gz (everything below, for the fetchers)
    python3 read_cards.py --check   check the reader against step 27's own numbers (exit 1 on a problem)

Step 27 built ``eternal/cards/cards.tiles`` from Wikidata exports it wrote to ``build/cards/raw/``.
That directory is gone - it was never in the workspace snapshot - and fetching it all again would
be about 120 large queries. **The tiles are the record** (``build_cards.py`` says so: "The card file
is the record (there is no separate master)"), and they carry everything step 41 needs:

* every card's QID, so the seven properties step 27 never fetched can be asked for by QID;
* the kind, so a person can be told from a company;
* the seat: a point in thousandths of a degree and its name;
* **offices with their years** (up to three per person) - step 27 fetched P39 and kept it;
* **links to other cards with their years** (studied at, party, worked for, served in, member of,
  founded / founded by) - and every organisation card has a seat, so a link is a dated place;
* the office names (group ``v``), so an office id can be printed.

So this reader is what makes step 41 possible without re-fetching step 27. Nothing here is shipped;
the dump goes to ``build/`` and can be rebuilt at any time.

Row layout, from ``build_cards.py``'s docstring (big-endian; ``str`` = unsigned 16-bit byte length
then UTF-8 bytes)::

    int qid; byte kind; short fame; str name; str line; short lineFrom; str early;
    int from; int to; short known; byte flags; int lat; int lon; str home;
    people only: int deathLat; int deathLon; str deathPlace;
                 byte offices, each (int office, short from, short to);
                 byte works, each (str title, short year);
    every card:  byte links, each (byte role, int qid, short from, short to)

Kinds: 0 person, 1 company, 2 school, 3 paper, 4 party, 5 army, 6 society, 7 order.
Link roles: 1 studied at, 2 party, 3 worked for, 4 served in, 5 member of, 6 founded, 7 founded by.
"""
import collections
import gzip
import io
import json
import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(HERE, "..", "eternal", "src", "main", "resources")
CARDS = os.path.join(MOD, "data", "eternalengine", "eternal", "cards", "cards.tiles")
DUMP = os.path.join(HERE, "build", "cards_dump.json.gz")

KINDS = ["person", "company", "school", "paper", "party", "army", "society", "order"]
ROLES = {1: "studied", 2: "party", 3: "worked", 4: "served", 5: "member", 6: "founded",
         7: "founded_by"}
UNKNOWN_INT = -2147483648
UNKNOWN_SHORT = -32768


class Reader:
    """A cursor over one decompressed tile blob."""

    def __init__(self, raw):
        self.b = raw
        self.o = 0

    def u8(self):
        v = self.b[self.o]
        self.o += 1
        return v

    def i16(self):
        v = struct.unpack_from(">h", self.b, self.o)[0]
        self.o += 2
        return v

    def i32(self):
        v = struct.unpack_from(">i", self.b, self.o)[0]
        self.o += 4
        return v

    def s(self):
        n = struct.unpack_from(">H", self.b, self.o)[0]
        self.o += 2
        v = self.b[self.o:self.o + n].decode("utf-8")
        self.o += n
        return v


def iter_tiles(data):
    """Every tile as (group, firstBucket, lastBucket, offset, length, rawLength, rows), plus the blob start."""
    o = 8

    def s():
        nonlocal o
        n = struct.unpack_from(">H", data, o)[0]
        o += 2
        v = data[o:o + n].decode("utf-8")
        o += n
        return v

    def i():
        nonlocal o
        v = struct.unpack_from(">i", data, o)[0]
        o += 4
        return v

    dataset = s()
    master = s()
    rows = i()
    meta = {}
    for _ in range(i()):
        k = s()
        meta[k] = s()
    out = []
    for _ in range(i()):
        g = s()
        for _ in range(i()):
            out.append((g,) + tuple(i() for _ in range(6)))
    blob = i()
    return dataset, master, rows, meta, out, o


def read(path=CARDS):
    """Every card, as a dict; plus the meta, the office names and the index."""
    data = open(path, "rb").read()
    dataset, master, rows, meta, tiles, blob_at = iter_tiles(data)
    by_group = collections.defaultdict(list)
    for t in tiles:
        by_group[t[0]].append(t)

    offices = []
    if "v" in by_group:
        t = by_group["v"][0]
        r = Reader(zlib.decompress(data[blob_at + t[3]: blob_at + t[3] + t[4]]))
        for _ in range(r.i32()):
            offices.append(r.s())

    qids = []
    if "i" in by_group:
        t = by_group["i"][0]
        raw = zlib.decompress(data[blob_at + t[3]: blob_at + t[3] + t[4]])
        d = io.BytesIO(raw)

        def vi():
            v = 0
            shift = 0
            while True:
                b = d.read(1)[0]
                v |= (b & 0x7F) << shift
                shift += 7
                if not b & 0x80:
                    return v
        n = struct.unpack(">i", d.read(4))[0]
        prev = 0
        for _ in range(n):
            prev += vi()
            qids.append(prev)

    cards = []
    per_group_qids = []
    for g in sorted(by_group):
        if not g.startswith("b/"):
            continue
        group_qids = []
        for t in by_group[g]:
            raw = zlib.decompress(data[blob_at + t[3]: blob_at + t[3] + t[4]])
            r = Reader(raw)
            while r.o < len(raw):
                try:
                    c = card(r)
                    cards.append(c)
                    group_qids.append(c["qid"])
                except Exception:          # noqa: BLE001 - a short tile tail is a hard error
                    raise SystemExit("cards: a row in group %s ran off the end at %d of %d"
                                     % (g, r.o, len(raw)))
        per_group_qids.append(group_qids)
    return {"dataset": dataset, "master": master, "rows": rows, "meta": meta,
            "offices": offices, "index": qids, "cards": cards,
            "perGroup": per_group_qids}


def card(r):
    c = {}
    c["qid"] = r.i32()
    c["kind"] = r.u8()
    c["fame"] = r.i16()
    c["name"] = r.s()
    c["line"] = r.s()
    c["lineFrom"] = r.i16()
    c["early"] = r.s()
    c["from"] = r.i32()
    c["to"] = r.i32()
    c["known"] = r.i16()
    flags = r.u8()
    c["fromAround"] = bool(flags & 1)
    c["toAround"] = bool(flags & 2)
    c["female"] = bool(flags & 4)
    c["male"] = bool(flags & 8)
    c["lat"] = r.i32() / 1000.0
    c["lon"] = r.i32() / 1000.0
    c["home"] = r.s()
    if c["kind"] == 0:
        dlat = r.i32()
        dlon = r.i32()
        c["deathLat"] = None if dlat == UNKNOWN_INT else dlat / 1000.0
        c["deathLon"] = None if dlon == UNKNOWN_INT else dlon / 1000.0
        c["deathPlace"] = r.s()
        c["offices"] = []
        for _ in range(r.u8()):
            off = r.i32()
            a = r.i16()
            b = r.i16()
            c["offices"].append((off, None if a == UNKNOWN_SHORT else a,
                                 None if b == UNKNOWN_SHORT else b))
        c["works"] = []
        for _ in range(r.u8()):
            title = r.s()
            year = r.i16()
            c["works"].append((title, None if year == UNKNOWN_SHORT else year))
    c["links"] = []
    for _ in range(r.u8()):
        role = r.u8()
        q = r.i32()
        a = r.i16()
        b = r.i16()
        c["links"].append((ROLES.get(role, "role%d" % role), q,
                           None if a == UNKNOWN_SHORT else a,
                           None if b == UNKNOWN_SHORT else b))
    return c


# ------------------------------------------------------------------ the check

def check(path=CARDS, dump=None):
    """Everything step 27's own --check asserts, plus what step 41 relies on."""
    d = read(path)
    meta = d["meta"]
    cards = d["cards"]
    per_group_qids = d["perGroup"]
    problems = []
    print("cards.tiles: %s bytes" % f"{os.path.getsize(path):,}")

    def ok(good, text):
        print("  %s %s" % ("ok  " if good else "FAIL", text))
        if not good:
            problems.append(text)

    ok(len(cards) == d["rows"], "%d cards read, the file says %d" % (len(cards), d["rows"]))
    ok(len(d["index"]) == d["rows"], "the index names %d, the file says %d"
       % (len(d["index"]), d["rows"]))

    by_kind = collections.Counter(c["kind"] for c in cards)
    want = {int(k): int(v) for k, v in
            (p.split(":") for p in meta["kinds"].split(","))}
    ok(by_kind == collections.Counter(want), "kinds: %s (the file says %s)"
       % (dict(sorted(by_kind.items())), dict(sorted(want.items()))))
    people = [c for c in cards if c["kind"] == 0]
    ok(len(people) == 148510, "%d people" % len(people))

    qs = [c["qid"] for c in cards]
    ok(len(set(qs)) == len(qs), "no card appears twice (%d distinct of %d)" % (len(set(qs)), len(qs)))
    # cards are grouped by 5-degree box, so the file as a whole is not in QID order; what must hold
    # is that each card is filed under exactly one box and that the index reaches all of them
    ok(sum(len(g) for g in per_group_qids) == len(cards),
       "every card is filed under exactly one 5-degree box (%d in boxes of %d)"
       % (sum(len(g) for g in per_group_qids), len(cards)))
    ok(sorted(qs) == sorted(d["index"]), "the cards' QIDs are exactly the index's QIDs")

    ok(len(d["offices"]) == int(meta["offices"]),
       "%d office names, the file says %s" % (len(d["offices"]), meta["offices"]))
    ok(all(0 <= o < len(d["offices"]) for c in cards for o, _, _ in c.get("offices", [])),
       "every office id on a card is a real office")

    # what step 41 leans on
    seated = sum(1 for c in cards if abs(c["lat"]) <= 90 and abs(c["lon"]) <= 180
                 and not (c["lat"] == 0.0 and c["lon"] == 0.0))
    ok(seated > len(cards) * 0.9, "%d of %d cards have a seat on the map (%.0f%%)"
       % (seated, len(cards), seated * 100.0 / len(cards)))
    with_off = sum(1 for c in people if c["offices"])
    with_link = sum(1 for c in people if c["links"])
    dated_off = sum(1 for c in people for _, a, b in c["offices"] if a is not None or b is not None)
    dated_link = sum(1 for c in people for _, _, a, b in c["links"] if a is not None or b is not None)
    print("  ..  %d people hold an office, %d of those offices carry a year"
          % (with_off, dated_off))
    all_links = sum(len(c["links"]) for c in cards)
    dated_people_link = sum(1 for c in people
                            if any(a is not None or b is not None for _, _, a, b in c["links"]))
    dated_people_off = sum(1 for c in people
                           if any(a is not None or b is not None for _, a, b in c["offices"]))
    print("  ..  %d people link to another card, %d links in all, %d of them carry a year,"
          " and %d people have at least one dated link"
          % (with_link, all_links, dated_link, dated_people_link))
    print("  ..  %d people have at least one office carrying a year" % dated_people_off)
    ok(with_off > 20000, "offices are worth building D11 on: %d people hold one" % with_off)
    ok(with_link > 20000, "links are worth building D11 on: %d people have one" % with_link)

    # a link must point at a card that exists
    have = set(qs)
    dangling = sum(1 for c in cards for _, q, _, _ in c["links"] if q not in have)
    print("  ..  %d links point at a card this file does not hold (they were not chosen)"
          % dangling)
    ok(dangling * 4 < sum(len(c["links"]) for c in cards),
       "most links resolve inside the file")

    if dump:
        os.makedirs(os.path.dirname(dump), exist_ok=True)
        with open(dump, "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as f:
            json.dump({"meta": d["meta"], "offices": d["offices"], "cards": d["cards"]}, f)
        print("  wrote %s (%s bytes)" % (dump, f"{os.path.getsize(dump):,}"))

    print("cards: %d problem(s)" % len(problems))
    return 1 if problems else 0


def main(argv):
    if "--check" in argv or not argv:
        return check()
    if "--dump" in argv:
        return check(dump=DUMP)
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
