#!/usr/bin/env python3
"""Step 28 (known problems 39 and 40 of step 26): occupied and disputed land.

    python3 build_occupations.py            write history/occupations.json.gz
    python3 build_occupations.py --check    rebuild in memory and compare (exit 1 if it differs)

Occupations of the Second World War. Step 26 (rule S8 of fix_history_data.py) gave occupied lands back their own
state: Denmark is "the Kingdom of Denmark, ruled by Christian X" in 1942, not Germany. What that took away, the
occupation itself, is kept here: the map squares whose record named an occupying power in 1937-1949 (Germany, Italy,
Japan, Bulgaria, Hungary; Finland and Romania in Soviet land; British, American and Australian troops in Iceland,
Greenland, Iran and the Indies; Soviet troops at the war's end) and that now name another state. The record before the
fixes is read back from the undo log of fix_history_data.py (step25_changes.json.gz), so nothing is guessed: the squares
and years are exactly those the fix changed. The game says, after the state and its ruler: "German troops have held
this land since 1940."

Disputed land (the West Bank, Gaza, the Golan Heights, Crimea, Northern Cyprus, Western Sahara) is a short hand-written
table in history/disputed_lands.json, in the mod's own words; it is read as it is (no build step).

File layout: {"cellDegrees": 0.5, "groups": [{"spans": [[who, from, to], ...], "cells": [lat*100, lon*100, ...]}]}:
every square of a group has the same spans; "who" is the word for the troops ("German", "Japanese", "Soviet").
"""
import collections
import gzip
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fix_history_data as fx  # noqa: E402

DATA = os.path.normpath(os.path.join(HERE, "..", "eternal", "src", "main", "resources", "data", "eternalengine", "eternal"))
WORLD = os.path.join(DATA, "history", "world_rulers.json.gz")
OUT = os.path.join(DATA, "history", "occupations.json.gz")
LOG = os.path.join(HERE, "step25_changes.json.gz")

# The occupying powers of fix_history_data.py's S8 (WW2_AXIS, WW2_IN_SOVIET, WW2_ALLIED), and the Soviet Union and
# Great Britain under the names the record used; the years each may count.
OCCUPIER = {"Q7318": ("German", 1937, 1946), "Q172579": ("Italian", 1937, 1946), "Q188712": ("Japanese", 1937, 1946),
            "Q147909": ("Bulgarian", 1937, 1946), "Q28": ("Hungarian", 1937, 1946), "Q33": ("Finnish", 1939, 1945),
            "Q203493": ("Romanian", 1940, 1945), "Q8680": ("British", 1939, 1946), "Q161885": ("British", 1939, 1946), "Q145": ("British", 1939, 1946),
            "Q30": ("American", 1940, 1949), "Q149805": ("British", 1940, 1947), "Q408": ("Australian", 1941, 1946),
            "Q15180": ("Soviet", 1939, 1949)}


# Allied troops count only in the lands they held in the war without ruling them (the hosts of S8's WW2_ALLIED_HOSTS,
# by the names the record now gives); elsewhere a British or American name in the record was a colony or a rename.
HOSTS = {"British": {"Kingdom of Iceland", "Imperial State of Iran", "Kingdom of Iraq", "Dutch East Indies", "Greenland"},
         "American": {"Kingdom of Iceland", "Greenland", "Dutch East Indies"},
         "Australian": {"Dutch East Indies"}}


def jbytes(doc):
    raw = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    buf = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buf, mtime=0, compresslevel=9) as g:
        g.write(raw)
    return buf.getvalue()


def ruler_at(polities, timelines, tl, year):
    t = timelines[tl]
    for j in range(0, len(t), 3):
        if t[j + 1] <= year <= t[j + 2]:
            return polities[t[j]] if t[j] < len(polities) else None
    return None


def build():
    with gzip.open(LOG, "rt", encoding="utf-8") as f:
        log = json.load(f)
    with gzip.open(WORLD, "rt", encoding="utf-8") as f:
        cur = json.load(f)
    info = log["files"]["world"]
    orig = {}
    for lk in ("polities", "timelines", "places"):
        items = cur[lk]
        if lk == "places":
            items = [items[3 * i:3 * i + 3] for i in range(len(items) // 3)]
        rev = info["lists"].get(lk)
        orig[lk] = fx.undo_list(items, rev) if rev else items
    curp = [cur["places"][3 * i:3 * i + 3] for i in range(len(cur["places"]) // 3)]
    spans_of = {}
    stats = collections.Counter()
    for i in range(min(len(orig["places"]), len(curp))):
        op, cp = orig["places"][i], curp[i]
        if op[0] != cp[0] or op[1] != cp[1]:
            continue  # not the same square (the list was edited before this point)
        held = []
        for y in range(1937, 1950):
            a = ruler_at(orig["polities"], orig["timelines"], op[2], y)
            b = ruler_at(cur["polities"], cur["timelines"], cp[2], y)
            if not a or not b or len(a) < 2 or not a[1] or a[1] not in OCCUPIER:
                continue
            word, y0, y1 = OCCUPIER[a[1]]
            if not y0 <= y <= y1 or (len(b) > 1 and b[1] == a[1]) or b[0] == a[0]:
                continue
            if b[0] == "Allied-occupied Germany":
                continue  # the state's name says it already
            if word in HOSTS and b[0] not in HOSTS[word]:
                continue
            if word == "Soviet" and b[0] in ("Union of Soviet Socialist Republics", "Soviet Union"):
                continue
            held.append((word, y))
        if not held:
            continue
        spans = []
        for word, y in held:
            if spans and spans[-1][0] == word and spans[-1][2] == y - 1:
                spans[-1][2] = y
            else:
                spans.append([word, y, y])
        key = json.dumps(spans)
        spans_of.setdefault(key, []).append((op[0], op[1]))
        for word, y0, y1 in spans:
            stats[word] += y1 - y0 + 1
    groups = []
    for key in sorted(spans_of):
        cells = sorted(spans_of[key])
        groups.append({"spans": json.loads(key), "cells": [v for c in cells for v in c]})
    doc = {"id": "occupations", "title": "Map squares held by an occupying power in the Second World War, 1937-1949, "
           "read from the record before step 26's fix (S8 of fix_history_data.py). Overlay only.",
           "source": "worldfill/build_occupations.py", "cellDegrees": 0.5, "groups": groups}
    return doc, stats, sum(len(g["cells"]) // 2 for g in groups)


def main(argv):
    doc, stats, squares = build()
    data = jbytes(doc)
    if "--check" in argv:
        same = os.path.exists(OUT) and open(OUT, "rb").read() == data
        print(f"occupations.json.gz: {'up to date' if same else 'OUT OF DATE (run build_occupations.py)'}")
        return 0 if same else 1
    with open(OUT, "wb") as f:
        f.write(data)
    print(f"occupations.json.gz: {squares:,} squares in {len(doc['groups']):,} groups, {len(data):,} bytes; square-years "
          + ", ".join(f"{k} {v:,}" for k, v in stats.most_common()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
