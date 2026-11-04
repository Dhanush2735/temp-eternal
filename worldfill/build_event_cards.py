#!/usr/bin/env python3
"""Step 28 (systems C8, C9, C21, C22): the event cards and the cause-and-effect graph.

    python3 fetch_events_wd.py ours                 the events the history data has with a Wikidata number
    python3 build_event_cards.py --linked           list the things their links name
    python3 fetch_events_wd.py kinds                which of them are events (a date), people or other things
    python3 build_event_cards.py --split            split them into events and other things
    python3 fetch_events_wd.py linked               fetch those
    python3 fetch_events_wd.py graph                every cause-and-effect statement between dated things
    python3 build_event_cards.py --graph            list the events of that graph without details
    python3 fetch_events_wd.py graphlinked          fetch those
    python3 fetch_events_wd.py nature               the natural events (also read by build_nature.py)
    python3 build_nature.py                         storms and other natural events for the history data
    python3 build_event_cards.py --build            write cards/events.tiles into the mod
    python3 build_event_cards.py --check            read cards/events.tiles back and check it (exit 1 on a problem)

Which events get a card: every event of the history data with a Wikidata number (battles, sieges, wars, treaties,
incidents, disasters: events_world.json, events_wikidata_more.json.gz), every dated event their links name (the wars
they are part of, their causes and effects, what came before and after), the natural events Wikidata places on the map
(events_nature.json.gz) and the storms Wikidata knows by name (events_storms.json.gz).

What a card keeps: the name, the short description (years taken out: they come from the card's own years), the first
and last year ("around" when only the decade is known), the place on the map and its name (or none: a war fought in
many places has no single point), the country, the deaths, and links to other cards: part of, its parts (the eight best
known), causes, effects, came after, came before, and who took part (people and groups with cards of their own; the
other sides, mostly states, by name). Causes without a card are kept by name (a cause always comes first); effects need
a card, because an effect may only be told after its year.

The links are the cause-and-effect graph (C9): every link is stored on both cards (a cause on the effect, the effect on
the cause; a part on the whole, the whole on the part; what came after and before), so the graph can be walked either
way. Step 49 (what depends on a change) walks it.

Cross-check: for the history data's own events, the years are compared with the history data (fixed in step 25 from
Wikipedia); where they differ by more than a year, the history data's years are used and counted in the report.

File layout: the tile format of build_cards.py (dataset "events"); kind 8 (event) rows, after the common fields:
int deaths (-2147483648 unknown); str country; str sides (the other participants by name, "; " between); str causes
(causes without a card by name); str partOf (the larger event without a card); then the links. Link roles: 8 part of,
9 has part, 10 cause, 11 effect, 12 took part, 13 won, 14 came after (the event before it), 15 came before (the event
after it). Groups "b/<y>/<x>" (5-degree boxes) and "w" (events with no single point), buckets by the century of the
first year; "i" the index (as in cards.tiles); "v" an empty list of office names.
"""
import collections
import gzip
import hashlib
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_cards as bc  # noqa: E402
import build_tiles  # noqa: E402

RAW = os.path.join(HERE, "build", "events", "raw")
BASE = os.path.join(HERE, "build", "events")
HIST = os.path.join(bc.DATA, "history")
OUT = os.path.join(bc.DATA, "cards", "events.tiles")
CARDS = os.path.join(bc.DATA, "cards", "cards.tiles")
REPORT = os.path.join(HERE, "logs", "step28_events_report.json")
UNKNOWN = bc.UNKNOWN
EVENT = 8
ROLE = {"partof": 8, "haspart": 9, "cause": 10, "effect": 11, "took": 12, "winner": 13, "after": 14, "before": 15}
INVERSE = {"partof": "haspart", "haspart": "partof", "cause": "effect", "effect": "cause", "after": "before",
           "before": "after"}
MAX = {"partof": 2, "haspart": 8, "cause": 6, "effect": 6, "took": 8, "winner": 2, "after": 2, "before": 2}
MAX_SIDES = 5
OUR_FILES = ["events_world.json", "events_wikidata_more.json.gz", "events_nature.json.gz", "events_storms.json.gz"]
LEAD_YEARS = re.compile(r"^(c\.\s*)?\d{3,4}(\s*(BCE|BC|CE|AD))?(\s*[\u2013\-]\s*\d{2,4}(\s*(BCE|BC|CE|AD))?)?\s+")
KIND_WORD = {"battle": "battle", "siege": "siege", "war": "war", "treaty": "treaty", "incident": "event",
             "disaster": "disaster", "political": "event", "cyclone": "storm", "flood": "flood", "wildfire": "wildfire",
             "landslide": "landslide", "avalanche": "avalanche", "tornado": "tornado", "heatwave": "heat wave",
             "drought": "drought", "famine": "famine", "epidemic": "epidemic", "pandemic": "pandemic"}


def rows(prefix, required=True):
    return bc.rows_in(RAW, prefix, required)


def our_events():
    """qid -> (lat, lon, start, end-inclusive, kind) from the history data's files that use Wikidata numbers."""
    out = {}
    for f in OUR_FILES:
        path = os.path.join(HIST, f)
        if not os.path.exists(path):
            continue
        op = gzip.open if f.endswith(".gz") else open
        with op(path, "rt", encoding="utf-8") as fh:
            doc = json.load(fh)
        for e in doc.get("events", []):
            m = re.fullmatch(r"q(\d+)(?:_\d+)?", str(e.get("id", "")))
            if not m:
                continue
            q = int(m.group(1))
            if q in out:
                continue
            out[q] = (float(e["lat"]), float(e["lon"]), int(e["start"]), int(e["end"]) - 1, e.get("kind", "event"),
                      e.get("confidence", ""))
    return out


def card_qids():
    """The QIDs of cards/cards.tiles (people and groups): kind by QID (0 person, 1-7 group)."""
    data = open(CARDS, "rb").read()
    tiles, blob = bc.iter_tiles(data)
    import zlib
    kinds = {}
    for t in tiles:
        if not t[0].startswith("b/"):
            continue
        body = zlib.decompress(data[blob + t[3]: blob + t[3] + t[4]])
        p = 0
        while p < len(body):
            q, kind = struct.unpack_from(">ib", body, p)
            kinds[q] = kind
            p = bc.skip_row(body, p)
    return kinds


def linked_lists():
    ours = {int(x[1:]) for x in open(os.path.join(BASE, "our_events.txt")).read().split()}
    linked = set()
    for c in list(rows("o_fwd_")) + list(rows("o_bwd_")):
        o = bc.qid_of(c[2])
        if o and o not in ours:
            linked.add(o)
    with open(os.path.join(BASE, "linked_all.txt"), "w") as f:
        f.writelines(f"Q{q}\n" for q in sorted(linked))
    print(f"{len(linked):,} linked things; run fetch_events_wd.py kinds, then this again with --split")


def split_linked():
    kind = {}
    for c in rows("kind_x_"):
        x = bc.qid_of(c[0])
        if not x:
            continue
        k = kind.get(x, "other")
        if len(c) > 2 and c[2] == "1":
            k = "human"
        elif len(c) > 3 and c[3] and k != "human":
            k = "event"
        kind[x] = k
    ev = sorted(q for q, k in kind.items() if k == "event")
    other = sorted(q for q, k in kind.items() if k != "event")
    with open(os.path.join(BASE, "linked_events.txt"), "w") as f:
        f.writelines(f"Q{q}\n" for q in ev)
    with open(os.path.join(BASE, "linked_things.txt"), "w") as f:
        f.writelines(f"Q{q}\n" for q in other)
    print(f"{len(ev):,} linked events, {len(other):,} other linked things")


def graph_list():
    """The events of Wikidata's wider cause-and-effect graph that have no details yet (fetch_events_wd.py graphlinked)."""
    have = {int(x[1:]) for x in open(os.path.join(BASE, "our_events.txt")).read().split()}
    have |= {int(x[1:]) for x in open(os.path.join(BASE, "linked_events.txt")).read().split()}
    new = set()
    for c in rows("graph"):
        for cell in (c[0], c[2]):
            q = bc.qid_of(cell)
            if q and q not in have:
                new.add(q)
    with open(os.path.join(BASE, "graph_events.txt"), "w") as f:
        f.writelines(f"Q{q}\n" for q in sorted(new))
    print(f"{len(new):,} events of the wider graph without details")


def clean_event_line(text):
    s = LEAD_YEARS.sub("", " ".join((text or "").split()))
    return bc.clean_line(s)


def build():
    report = collections.Counter()
    ours = our_events()
    people_groups = card_qids()

    names, lines = {}, {}
    for prefix in ("o_names_", "l_names_", "g_names_"):
        for c in rows(prefix, required=not prefix.startswith("g_")):
            q = bc.qid_of(c[0])
            if q and q not in names:
                names[q] = bc.literal(c[1])
                lines[q] = bc.literal(c[2]) if len(c) > 2 else ""
    other_names, other_fame = {}, {}
    for prefix in ("names_x_", "kind_x_"):
        for c in rows(prefix, required=False):
            q = bc.qid_of(c[0])
            if q and len(c) > 1 and c[1] and q not in other_names:
                other_names[q] = bc.literal(c[1])
            if q and len(c) > 4 and c[4]:
                other_fame[q] = max(other_fame.get(q, 0), int(c[4]))

    dates = collections.defaultdict(lambda: collections.defaultdict(list))
    for prefix in ("o_dates_", "l_dates_", "g_dates_"):
        for c in rows(prefix, required=not prefix.startswith("g_")):
            q, which, y = bc.qid_of(c[0]), bc.literal(c[1]), bc.year_of(c[2])
            if q and y is not None and c[3]:
                dates[q][which].append((y, int(c[3])))

    # Places: the event's own point; else its place's point, when it has one place only (a war fought "in Africa"
    # and "in Europe" has no single point); the country only when there is one.
    own_point, loc_points, loc_names, countries = {}, collections.defaultdict(dict), {}, collections.defaultdict(set)
    for prefix in ("o_place_", "l_place_", "g_place_"):
        for c in rows(prefix, required=not prefix.startswith("g_")):
            q = bc.qid_of(c[0])
            if not q:
                continue
            own = bc.point(c[1]) if len(c) > 1 else None
            if own and q not in own_point:
                own_point[q] = own
            loc = bc.qid_of(c[2]) if len(c) > 2 else 0
            if loc:
                lp = bc.point(c[4]) if len(c) > 4 else None
                if loc not in loc_points[q] or (lp and not loc_points[q][loc]):
                    loc_points[q][loc] = lp
                if len(c) > 3 and c[3]:
                    loc_names.setdefault((q, loc), bc.literal(c[3]))
            if len(c) > 6 and c[6]:
                countries[q].add(bc.literal(c[6]))
    point, place_name, country = {}, {}, {}
    for q in set(own_point) | set(loc_points):
        locs = loc_points.get(q, {})
        if q in own_point:
            point[q] = own_point[q]
        elif len(locs) == 1 and list(locs.values())[0]:
            point[q] = list(locs.values())[0]
        if len(locs) == 1:
            place_name[q] = loc_names.get((q, list(locs)[0]), "")
    for q, cs in countries.items():
        if len(cs) == 1:
            country[q] = next(iter(cs))

    fame, deaths = {}, {}
    for prefix in ("o_more_", "l_more_", "g_more_"):
        for c in rows(prefix, required=not prefix.startswith("g_")):
            q = bc.qid_of(c[0])
            if not q:
                continue
            if len(c) > 1 and c[1]:
                fame[q] = max(fame.get(q, 0), int(c[1]))
            if len(c) > 2 and c[2]:
                try:
                    d = int(float(c[2]))
                    if d >= 0:
                        deaths[q] = max(deaths.get(q, 0), d)
                except ValueError:
                    pass

    # Natural events (and storms known by name) from the nature exports.
    nature = {}
    for kind in ["flood", "wildfire", "landslide", "avalanche", "tornado", "heatwave", "drought", "famine", "epidemic",
                 "pandemic", "cyclone"]:
        for c in rows(f"nature_{kind}", required=False):
            q = bc.qid_of(c[0])
            if not q or q in nature:
                continue
            nature[q] = c
    for q, c in nature.items():
        if q not in names:
            names[q] = bc.literal(c[1])
            lines[q] = bc.literal(c[2]) if len(c) > 2 else ""
        if len(c) > 3 and c[3]:
            fame[q] = max(fame.get(q, 0), int(c[3]))
        y = bc.year_of(c[4]) if len(c) > 4 else None
        if y is not None and c[5] and not dates.get(q):
            dates[q]["at"].append((y, int(c[5])))
            if len(c) > 6 and c[6]:
                y2 = bc.year_of(c[6])
                if y2 is not None:
                    dates[q]["to"].append((y2, int(c[5])))
        own = bc.point(c[7]) if len(c) > 7 else None
        lp = bc.point(c[8]) if len(c) > 8 else None
        if q not in point and (own or lp):
            point[q] = own or lp
        if len(c) > 9 and c[9] and q not in place_name:
            place_name[q] = bc.literal(c[9])
        if len(c) > 11 and c[11] and q not in country:
            country[q] = bc.literal(c[11])
        if len(c) > 12 and c[12]:
            try:
                deaths[q] = max(deaths.get(q, 0), int(float(c[12])))
            except ValueError:
                pass

    # Links, both ways.
    links = collections.defaultdict(lambda: collections.defaultdict(set))
    for prefix in ("o_fwd_", "o_bwd_", "l_fwd_", "g_fwd_", "graph"):
        for c in rows(prefix, required=prefix.startswith("o_")):
            e, role, o = bc.qid_of(c[0]), bc.literal(c[1]), bc.qid_of(c[2])
            if e and o and role in ROLE and e != o:
                links[e][role].add(o)

    # Which events become cards: a name and a first year.
    cards = {}
    for q in sorted(set(names) | set(ours)):
        name = names.get(q, "")
        if not name or re.fullmatch(r"Q\d+", name):
            report["events without an English name"] += 1
            continue
        if bc.SOURCE_WORDS.search(name):
            continue
        d = dates.get(q, {})
        if d.get("from"):  # a start time first: a "point in time" of a war is often its last year (World War I, 1918)
            start, s_around, _ = bc.pick_dates(d["from"])
            end, e_around, _ = bc.pick_dates(d.get("to") or [])
        else:
            start, s_around, _ = bc.pick_dates(d.get("at") or [])
            end, e_around, _ = bc.pick_dates(d.get("to") or [])
        mine = ours.get(q)
        if mine is not None:
            o_start, o_end = mine[2], mine[3]
            if start is None or abs(start - o_start) > 1:
                if start is not None:
                    report["first year taken from the history data"] += 1
                start, s_around = o_start, False
            if end is None or end < start or (abs(end - o_end) > 1 and mine[4] != "war"):
                end, e_around = max(o_end, start), False
        if start is None:
            report["events without a year"] += 1
            continue
        if end is None or end < start:
            end = start
        if end - start > 400:
            end = start  # an "ongoing" period, not one event
        if not -3500 <= start <= 2026:
            continue
        if mine is not None and mine[5] != "wikidata_region":
            lat, lon = mine[0], mine[1]
        elif q in point:
            lat, lon = point[q]
        else:
            lat = lon = None
        line = clean_event_line(lines.get(q, ""))
        ly = bc.line_year(line)
        line_from = ly if ly and ly > start else None
        kind = mine[4] if mine is not None else ""
        cards[q] = {"name": name, "line": line, "lineFrom": line_from, "from": start, "to": end,
                    "flags": (1 if s_around else 0) | (2 if e_around else 0), "lat": lat, "lon": lon,
                    "home": place_name.get(q, ""), "fame": fame.get(q, 0), "deaths": deaths.get(q),
                    "country": country.get(q, ""), "kind": kind, "links": collections.defaultdict(set),
                    "sides": [], "causes": [], "partOf": ""}
    report["event cards"] = len(cards)

    # Links between cards, both ways; the rest by name where that is safe.
    def label(o):
        if o in cards:
            return cards[o]["name"]
        return names.get(o) or other_names.get(o) or ""

    edges = 0
    for e in sorted(links):
        if e not in cards:
            continue
        for role in sorted(links[e]):
            for o in sorted(links[e][role]):
                if role in ("took", "winner"):
                    if o in people_groups:
                        cards[e]["links"][role].add(o)
                    elif role == "took":
                        n = label(o)
                        if n and not re.fullmatch(r"Q\d+", n) and n not in [x[1] for x in cards[e]["sides"]]:
                            cards[e]["sides"].append((-other_fame.get(o, 0), n))
                    continue
                if o in cards:
                    cards[e]["links"][role].add(o)
                    cards[o]["links"][INVERSE[role]].add(e)
                    edges += 1
                elif role == "cause":
                    n = label(o)
                    if n and not re.fullmatch(r"Q\d+", n):
                        cards[e]["causes"].append(n)
                elif role == "partof" and not cards[e]["partOf"]:
                    n = label(o)
                    if n and not re.fullmatch(r"Q\d+", n):
                        cards[e]["partOf"] = n
    report["links between event cards (each stored on both cards)"] = edges

    # Rows.
    groups = {}
    order = sorted(cards, key=lambda q: (-cards[q]["fame"], q))
    graph = collections.Counter()
    for q in order:
        cd = cards[q]
        lk = []
        for role in ("partof", "cause", "effect", "after", "before", "haspart", "took", "winner"):
            targets = sorted(cd["links"].get(role, ()), key=lambda o: (-(cards[o]["fame"] if o in cards else 0), o))
            for o in targets[:MAX[role]]:
                if role in ("took", "winner"):
                    lk.append((ROLE[role], o, None, None))
                else:
                    lk.append((ROLE[role], o, cards[o]["from"], cards[o]["to"]))
                graph[role] += 1
        raw = bytearray()
        raw += struct.pack(">ibh", q, EVENT, min(32767, cd["fame"]))
        raw += bc.s16(cd["name"]) + bc.s16(cd["line"]) + struct.pack(">h", bc.short(cd["lineFrom"])) + bc.s16("")
        raw += struct.pack(">ii", cd["from"], cd["to"]) + struct.pack(">h", bc.short(cd["from"]))
        raw += struct.pack(">b", cd["flags"])
        if cd["lat"] is None:
            raw += struct.pack(">ii", UNKNOWN, UNKNOWN)
        else:
            raw += struct.pack(">ii", round(cd["lat"] * 1000), round(cd["lon"] * 1000))
        raw += bc.s16(cd["home"])
        raw += struct.pack(">i", UNKNOWN if cd["deaths"] is None else min(cd["deaths"], 2_000_000_000))
        raw += bc.s16(cd["country"]) + bc.s16("; ".join(n for f, n in sorted(cd["sides"])[:MAX_SIDES]))
        raw += bc.s16("; ".join(cd["causes"][:4])) + bc.s16(cd["partOf"])
        raw += struct.pack(">b", len(lk))
        for role, o, fy, ty in lk:
            raw += struct.pack(">bihh", role, o, bc.short(fy), bc.short(ty))
        if cd["lat"] is None:
            g = "w"
        else:
            by, bx = bc.box_of(cd["lat"], cd["lon"])
            g = f"b/{by}/{bx}"
        groups.setdefault(g, {}).setdefault(cd["from"] // 100, []).append((q, bytes(raw)))

    tile_of, plain, tile_no = {}, {}, 0
    for g in sorted(list(groups) + ["i", "v"]):
        if g in ("i", "v"):
            tile_no += 1
            continue
        keys = sorted(groups[g])
        cur, members = 0, []
        for i, bucket in enumerate(keys):
            members += [q for q, raw in groups[g][bucket]]
            cur += len(groups[g][bucket])
            if cur >= build_tiles.MIN_ROWS or i == len(keys) - 1:
                for q in members:
                    tile_of[q] = tile_no
                tile_no += 1
                cur, members = 0, []
        plain[g] = {b: [raw for q, raw in groups[g][b]] for b in keys}
    qs = sorted(tile_of)
    idx = bytearray(struct.pack(">i", len(qs)))
    prev = 0
    for q in qs:
        idx += bc.varint(q - prev)
        prev = q
    for q in qs:
        idx += bc.varint(tile_of[q])
    plain["i"] = {0: [bytes(idx)]}
    plain["v"] = {0: [struct.pack(">i", 0)]}
    placeless = sum(1 for cd in cards.values() if cd["lat"] is None)
    meta = {"events": len(cards), "placeless": placeless, "box": bc.BOX, "minRows": build_tiles.MIN_ROWS,
            "source": "Wikidata (CC0), the history data's events, NOAA IBTrACS for storm landfalls"}
    for role, n in sorted(graph.items()):
        meta["links_" + role] = n
    digest = hashlib.sha256()
    for q in qs:
        digest.update(struct.pack(">i", q))
    data = build_tiles.write_tiles("events", digest.hexdigest(), len(cards), meta, plain)
    assert len(bc.iter_tiles(data)[0]) == tile_no
    report["events with no single point"] = placeless
    report["events with a cause"] = sum(1 for cd in cards.values() if cd["links"].get("cause") or cd["causes"])
    report["events with an effect"] = sum(1 for cd in cards.values() if cd["links"].get("effect"))
    report["events part of a larger one"] = sum(1 for cd in cards.values() if cd["links"].get("partof") or cd["partOf"])
    report["events with people or groups taking part (cards)"] = sum(1 for cd in cards.values() if cd["links"].get("took"))
    report["events with sides by name"] = sum(1 for cd in cards.values() if cd["sides"])
    report["events with deaths"] = sum(1 for cd in cards.values() if cd["deaths"] is not None)
    report["events of the history data with a card"] = sum(1 for q in ours if q in cards)
    for role, n in sorted(graph.items()):
        report["links kept: " + role] = n
    return data, dict(sorted(report.items())), meta


def check():
    if not os.path.exists(OUT):
        print("events.tiles: missing")
        return 1
    import zlib
    data = open(OUT, "rb").read()
    tiles, blob = bc.iter_tiles(data)
    idx_tile = [t for t in tiles if t[0] == "i"][0]
    raw = zlib.decompress(data[blob + idx_tile[3]: blob + idx_tile[3] + idx_tile[4]])
    n = struct.unpack_from(">i", raw, 0)[0]
    pos, qs, prev = 4, [], 0

    def varint():
        nonlocal pos
        v, shift = 0, 0
        while True:
            b = raw[pos]
            pos += 1
            v |= (b & 0x7F) << shift
            shift += 7
            if not b & 0x80:
                return v

    for _ in range(n):
        prev += varint()
        qs.append(prev)
    tile_nos = [varint() for _ in range(n)]
    found = collections.defaultdict(set)
    seen = 0
    problems = 0
    for i, t in enumerate(tiles):
        if not (t[0].startswith("b/") or t[0] == "w"):
            continue
        body = zlib.decompress(data[blob + t[3]: blob + t[3] + t[4]])
        p, cnt = 0, 0
        while p < len(body):
            q = struct.unpack_from(">i", body, p)[0]
            p = skip_event(body, p)
            found[i].add(q)
            cnt += 1
        if cnt != t[6]:
            problems += 1
        seen += cnt
    missing = sum(1 for q, tn in zip(qs, tile_nos) if q not in found.get(tn, ()))
    ok = not problems and not missing and seen == n
    print(f"events.tiles: {len(data):,} bytes, {len(tiles)} tiles, {seen:,} events, index {n:,} -> "
          f"{'OK' if ok else 'PROBLEMS'}")
    return 0 if ok else 1


def skip_event(b, p):
    def sk(p):
        return p + 2 + struct.unpack_from(">H", b, p)[0]
    p += 7
    p = sk(p)
    p = sk(p)
    p += 2
    p = sk(p)
    p += 8 + 2 + 1 + 8
    p = sk(p)
    p += 4
    for _ in range(4):
        p = sk(p)
    n = b[p]
    return p + 1 + n * 9


def main(argv):
    if "--linked" in argv:
        linked_lists()
        return 0
    if "--split" in argv:
        split_linked()
        return 0
    if "--graph" in argv:
        graph_list()
        return 0
    if "--check" in argv:
        return check()
    if "--build" in argv:
        data, report, meta = build()
        with open(OUT, "wb") as f:
            f.write(data)
        os.makedirs(os.path.dirname(REPORT), exist_ok=True)
        with open(REPORT, "w") as f:
            json.dump({"file": "cards/events.tiles", "bytes": len(data), "meta": meta, "report": report}, f, indent=1)
        print(f"events.tiles: {len(data):,} bytes")
        for k, v in report.items():
            print(f"  {k}: {v:,}")
        return check()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
