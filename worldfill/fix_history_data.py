#!/usr/bin/env python3
"""Step 25: the history data fix (systems C1 and C25 of SYSTEMS_PLAN.md).

Fixes, in groups, the wrong answers that the step-12 fact check (FACT_AUDIT.md) and the turn-51 spot check
(TALK_SPOT_CHECK.md) found, plus known problems 4, 15 and 21 of SYSTEMS_PLAN.md part 8. Wikipedia first:
names and years come from English Wikipedia; Wikidata (CC0, saved by fix_history_wd.py) only fills years
that the Wikipedia-built lists leave empty.

Every change is listed and reversible:
  worldfill/step25_changes.csv.gz    one line per change: file, rule, item, before, after, why
  worldfill/step25_changes.json.gz   the exact before-values, so `--undo` puts every file back
                                     (checked against a hash of each original)
Running the script again first undoes its last run, then applies the fix afresh, so it is safe to re-run.

Usage:
  python3 fix_history_data.py          apply (undoing an earlier run first)
  python3 fix_history_data.py --undo   put every file back as it was before step 25
"""
import collections
import csv
import gzip
import io
import hashlib
import json
import math
import os
import re
import sys
import unicodedata

HIST = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/history"
ETER = "/home/user/eternal/src/main/resources/data/eternalengine/eternal"
WF = "/home/user/worldfill"
LOG = f"{WF}/step25_changes.json.gz"
CSV_OUT = f"{WF}/step25_changes.csv.gz"  # gzipped in step 29 to save snapshot space (same lines)
OFFICES = f"{WF}/sources/step25_offices.json.gz"
NOW = 2026
SOURCE_END = 2024          # the last year Cliopatria v0.2.1 records

FILES = {
    "world": f"{HIST}/world_rulers.json.gz",
    "deccan": f"{HIST}/deccan_rulers.json.gz",
    "facts": f"{HIST}/polity_facts.json.gz",
    "people": f"{HIST}/famous_people.json.gz",
    "money": f"{ETER}/economy/money_table.json",
    "vips": f"{ETER}/vips/foundation_vips.json",
    "languages": f"{HIST}/local_languages.json.gz",
    "ev_world": f"{HIST}/events_world.json.gz",
    "ev_more": f"{HIST}/events_wikidata_more.json.gz",
    "ev_wiki": f"{HIST}/events_wikipedia.json.gz",
    "ev_regional": f"{HIST}/events_wikipedia_regional.json.gz",
    "ev_decades": f"{HIST}/events_wikipedia_decades.json.gz",
    "ev_hazards": f"{HIST}/events_hazards.json.gz",
    "ev_wars": f"{HIST}/events_wars.json.gz",
    "ev_deccan": f"{HIST}/deccan_events.json.gz",
}
LIST_KEY = {"world": ["polities", "timelines", "places"], "deccan": ["timelines", "places"], "facts": ["polities"],
            "people": ["people"], "money": ["rows"], "vips": [None], "languages": ["languages"]}
for _k in FILES:
    if _k.startswith("ev_"):
        LIST_KEY[_k] = ["events"]


# ====================================================================== files, the change list and undo

def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def jsave(path, doc):
    text = json.dumps(doc, ensure_ascii=False, separators=(",", ":"))
    if path.endswith(".gz"):
        # step 26: no time stamp and no file name inside the .gz, so the same data gives the same bytes on every run
        # and the data list's SHA-256 (manifest.json, build_manifest.py) stays valid when the script runs again
        with open(path, "wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0) as gz:
                gz.write(text.encode("utf-8"))
    else:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)


def digest(doc):
    return hashlib.sha256(json.dumps(doc, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                          .encode("utf-8")).hexdigest()


class ListEdit:
    """A list being edited: set, delete and append, remembering the originals so they can be put back."""

    def __init__(self, items):
        self.orig = items
        self.cur = list(items)
        self.gone = set()
        self.added = []

    def __len__(self):
        return len(self.cur) + len(self.added)

    def get(self, i):
        return self.cur[i] if i < len(self.cur) else self.added[i - len(self.cur)]

    def set(self, i, value):
        if i < len(self.cur):
            self.cur[i] = value
        else:
            self.added[i - len(self.cur)] = value

    def delete(self, i):
        self.gone.add(i)

    def append(self, value):
        self.added.append(value)
        return len(self.cur) + len(self.added) - 1

    def result(self):
        return [v for i, v in enumerate(self.cur) if i not in self.gone] + self.added

    def reverse(self):
        """What undo needs: the original length, the changed and the deleted originals, how many were added."""
        changed = {i: self.orig[i] for i in range(len(self.orig)) if i not in self.gone and self.cur[i] is not self.orig[i]
                   and self.cur[i] != self.orig[i]}
        return {"n": len(self.orig), "set": changed, "del": {i: self.orig[i] for i in sorted(self.gone)},
                "app": len(self.added)}


def undo_list(items, rev):
    """Rebuild the original list from the edited one and its reverse record."""
    n, sets, dels = rev["n"], {int(k): v for k, v in rev["set"].items()}, {int(k): v for k, v in rev["del"].items()}
    kept = iter(items[:len(items) - rev["app"]] if rev["app"] else items)
    out = []
    for i in range(n):
        if i in dels:
            out.append(dels[i])
            continue
        v = next(kept)
        out.append(sets.get(i, v))
    return out


class Doc:
    """One data file, with ListEdits for its big lists."""

    def __init__(self, key):
        self.key, self.path = key, FILES[key]
        self.doc = jload(self.path)
        self.hash = digest(self.doc)
        self.lists = {}
        self.keys = {}          # top-level keys set by this run (step 26 marks): key -> new value
        for lk in LIST_KEY[key]:
            items = self.doc if lk is None else self.doc[lk]
            if key == "world" and lk == "places":
                items = [items[3 * i:3 * i + 3] for i in range(len(items) // 3)]
            self.lists[lk] = ListEdit(items)

    def set_key(self, k, value):
        """A top-level key (step 26: the recorded/estimated marks). Undo puts the old value back, or removes it."""
        self.keys[k] = value

    def finish(self):
        rev = {}
        for lk, le in self.lists.items():
            r = le.reverse()
            if r["set"] or r["del"] or r["app"]:
                rev[str(lk)] = r
        old_keys = {k: self.doc.get(k, ABSENT) for k, v in self.keys.items() if self.doc.get(k, ABSENT) != v}
        if not rev and not old_keys:
            return None
        new = self.doc
        for k in old_keys:
            new[k] = self.keys[k]
        for lk, le in self.lists.items():
            items = le.result()
            if self.key == "world" and lk == "places":
                items = [x for t in items for x in t]
            if lk is None:
                new = items
            else:
                new[lk] = items
        jsave(self.path, new)
        out = {"hash": self.hash, "lists": rev}
        if old_keys:
            out["keys"] = old_keys
        return out


def undo(quiet=False):
    if not os.path.exists(LOG):
        if not quiet:
            print("nothing to undo")
        return
    log = jload(LOG)
    for key, info in log["files"].items():
        doc = jload(FILES[key])
        for lk, rev in info["lists"].items():
            real = None if lk == "None" else lk
            items = doc if real is None else doc[real]
            if key == "world" and real == "places":
                items = [items[3 * i:3 * i + 3] for i in range(len(items) // 3)]
            items = undo_list(items, rev)
            if key == "world" and real == "places":
                items = [x for t in items for x in t]
            if real is None:
                doc = items
            else:
                doc[real] = items
        for k, v in info.get("keys", {}).items():
            if v == ABSENT:
                doc.pop(k, None)
            else:
                doc[k] = v
        if digest(doc) != info["hash"]:
            sys.exit(f"undo of {key} does not give the original back; stopping (nothing more written)")
        jsave(FILES[key], doc)
    os.remove(LOG)
    if not quiet:
        print("undone:", ", ".join(log["files"]))


CHANGES = []
ABSENT = "(absent)"     # the undo record's word for a top-level key the original file did not have


def note(file, rule, item, before, after, why=""):
    CHANGES.append((file, rule, item, str(before), str(after), why))


# ====================================================================== shared helpers

def plain(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def km(la1, lo1, la2, lo2):
    mid = math.radians((la1 + la2) / 2)
    return math.hypot((la1 - la2) * 110.57, (lo1 - lo2) * 110.57 * math.cos(mid))


def in_poly(lat, lon, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        yi, xi = poly[i]
        yj, xj = poly[j]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside


def in_box(lat, lon, box):
    return box[0] <= lat <= box[1] and box[2] <= lon <= box[3]


def yr(y):
    return f"{-y} BC" if y < 0 else str(y)


# Hyderabad State (the Nizam's dominions) after Berar was assigned in 1853, as on the 1909 Imperial Gazetteer map:
# Telangana, Marathwada and the Raichur-Gulbarga-Bidar districts. Corners checked against towns on each side
# (Kurnool, Sholapur, Ahmednagar, Buldhana, Chanda and Bhadrachalam outside; Raichur, Gulbarga, Aurangabad,
# Ajanta, Adilabad, Khammam and Paloncha inside).
HYDERABAD_STATE = [
    (19.95, 74.65), (20.30, 74.95), (20.60, 75.50), (20.45, 76.00), (20.20, 76.40), (19.95, 77.00), (19.90, 77.80),
    (19.95, 78.30), (19.90, 78.90), (19.85, 79.25), (19.45, 79.55), (19.00, 79.85), (18.80, 80.05), (18.40, 80.35),
    (17.90, 80.75), (17.60, 80.85), (17.30, 81.15), (17.10, 80.95), (16.95, 80.45), (16.85, 80.05), (16.65, 79.70),
    (16.55, 79.30), (16.15, 78.90), (16.00, 78.50), (15.88, 78.15), (15.95, 77.45), (15.65, 76.90), (15.40, 76.50),
    (15.25, 76.05), (15.75, 75.95), (16.30, 76.20), (16.90, 76.30), (17.50, 76.30), (17.80, 76.15), (18.20, 75.85),
    (18.50, 75.55), (18.80, 75.05), (19.10, 75.10), (19.35, 75.25), (19.65, 74.85)]


# ====================================================================== S. state names on the border map

KEEP = object()
STATS = collections.Counter()


class Register:
    """The world record (format 2) or the Deccan record, seen as timelines of [name, qid, start, end]."""

    def __init__(self, doc):
        self.doc, self.key = doc, doc.key
        self.tl = doc.lists["timelines"]
        self.pl = doc.lists["places"]
        if self.key == "world":
            self.pol = doc.lists["polities"]
            self.pid_by = {}
            for i in range(len(self.pol)):
                p = self.pol.get(i)
                self.pid_by.setdefault((p[0], p[1] if len(p) > 1 else None), i)
        self.reindex()

    def reindex(self):
        self.cells = collections.defaultdict(list)
        for i in range(len(self.pl)):
            self.cells[self.timeline_of(i)].append(i)

    def timeline_of(self, i):
        p = self.pl.get(i)
        return p[2] if self.key == "world" else p["timeline"]

    def latlon(self, i):
        p = self.pl.get(i)
        return (p[0] / 100.0, p[1] / 100.0) if self.key == "world" else (p["lat"], p["lon"])

    def pid(self, name, qid):
        k = (name, qid)
        if k not in self.pid_by:
            self.pid_by[k] = self.pol.append([name, qid] if qid else [name])
        return self.pid_by[k]

    def get(self, t):
        raw = self.tl.get(t)
        if self.key == "world":
            out = []
            for k in range(0, len(raw) - 2, 3):
                p = self.pol.get(raw[k])
                out.append([p[0], p[1] if len(p) > 1 else None, raw[k + 1], raw[k + 2]])
            return out
        return [[s["name"], s.get("wikidata"), s["start"], s["end"]] for s in raw]

    def put(self, t, spans):
        if self.key == "world":
            flat = []
            for n, q, s, e in spans:
                flat += [self.pid(n, q), s, e]
            self.tl.set(t, flat)
        else:
            out = []
            for n, q, s, e in spans:
                d = {"name": n, "start": s, "end": e}
                if q:
                    d["wikidata"] = q
                out.append(d)
            self.tl.set(t, out)

    def isolate(self, t, inside):
        """The timeline for just these places of timeline t: t itself when they are all of its places, else a copy."""
        if len(inside) == len(self.cells[t]):
            return t
        raw = self.tl.get(t)
        t2 = self.tl.append(list(raw) if self.key == "world" else [dict(s) for s in raw])
        for i in inside:
            p = self.pl.get(i)
            if self.key == "world":
                self.pl.set(i, [p[0], p[1], t2])
            else:
                q = dict(p)
                q["timeline"] = t2
                self.pl.set(i, q)
        keep = [i for i in self.cells[t] if i not in set(inside)]
        self.cells[t] = keep
        self.cells[t2] = list(inside)
        return t2

    def where(self, t):
        cs = self.cells[t]
        la, lo = self.latlon(cs[0]) if cs else (0, 0)
        return f"{len(cs)} {'cells' if self.key == 'world' else 'places'} at {la:.2f},{lo:.2f}"

    def state_at(self, t, y):
        for n, q, s, e in self.get(t):
            if s <= y <= e and not n.startswith("("):
                return n, q
        return None, None


def split_rename(spans, y0, y1, match, new_name, new_qid):
    """Spans matching `match` inside [y0, y1] get the new name (and qid unless KEEP); others are untouched."""
    out, changed = [], []
    for n, q, s, e in spans:
        if e < y0 or s > y1 or n.startswith("(") or not match(n, q):
            out.append([n, q, s, e])
            continue
        if s < y0:
            out.append([n, q, s, y0 - 1])
        a, b = max(s, y0), min(e, y1)
        nq = q if new_qid is KEEP else new_qid
        out.append([new_name, nq, a, b])
        changed.append((n, q, a, b))
        if e > y1:
            out.append([n, q, y1 + 1, e])
    return out, changed


def rename(reg, rule, names, y0, y1, new_name, new_qid=KEEP, region=None, qid=None, why="", pure=None):
    """Rename spans called one of `names` (and, if given, with this qid) in [y0, y1], optionally only in a region
    (a function of lat, lon)."""
    names = {names} if isinstance(names, str) else set(names)
    if pure is None:
        pure = rule.startswith("S2")
    if pure and (tuple(sorted(names)), new_name) not in PURE_RENAMES:
        PURE_RENAMES.append((tuple(sorted(names)), new_name))
    match = (lambda n, q: n in names and (qid is None or q == qid))
    for t in list(reg.cells.keys()):
        if not reg.cells[t]:
            continue
        spans = reg.get(t)
        if not any(match(n, q) and e >= y0 and s <= y1 for n, q, s, e in spans):
            continue
        cells = reg.cells[t]
        if region is not None:
            cells = [i for i in cells if region(*reg.latlon(i))]
            if not cells:
                continue
            t = reg.isolate(t, cells)
            spans = reg.get(t)
        new, changed = split_rename(spans, y0, y1, match, new_name, new_qid)
        if changed:
            reg.put(t, new)
            years = sum(b - a + 1 for _n, _q, a, b in changed)
            STATS[rule] += years * len(reg.cells[t])
            before = "; ".join(f"{n} {yr(a)}–{yr(b)}" for n, _q, a, b in changed)
            note(reg.key, rule, reg.where(t), before, f"{new_name} (same years)", why)


def drop_spans(reg, rule, names, y0, y1, why=""):
    """Better silent than wrong: these years of a name that no longer stood for a state are left unnamed."""
    names = {names} if isinstance(names, str) else set(names)
    for t in list(reg.cells.keys()):
        if not reg.cells[t]:
            continue
        spans = reg.get(t)
        if not any(n in names and e >= y0 and s <= y1 for n, q, s, e in spans):
            continue
        new, gone = [], []
        for n, q, s, e in spans:
            if n not in names or e < y0 or s > y1:
                new.append([n, q, s, e])
                continue
            if s < y0:
                new.append([n, q, s, y0 - 1])
            gone.append((n, max(s, y0), min(e, y1)))
            if e > y1:
                new.append([n, q, y1 + 1, e])
        reg.put(t, new)
        STATS[rule] += sum(b - a + 1 for _n, a, b in gone) * len(reg.cells[t])
        note(reg.key, rule, reg.where(t), "; ".join(f"{n} {yr(a)}–{yr(b)}" for n, a, b in gone), "no state named", why)


def replace_spans(reg, rule, t, new_spans, why=""):
    old = reg.get(t)
    if old != new_spans:
        reg.put(t, new_spans)
        note(reg.key, rule, reg.where(t), spans_text(old), spans_text(new_spans), why)


def spans_text(spans, lo=-99999, hi=99999):
    return "; ".join(f"{n} {yr(s)}–{yr(e)}" for n, q, s, e in spans if e >= lo and s <= hi)


def merge_same(spans):
    out = []
    for n, q, s, e in sorted(spans, key=lambda x: x[2]):
        if out and out[-1][0] == n and out[-1][1] == q and out[-1][3] >= s - 1:
            out[-1][3] = max(out[-1][3], e)
        else:
            out.append([n, q, s, e])
    return out


def extend_present(reg):
    """Cliopatria ends in 2024: the states of 2024 are still there in 2025 and 2026 (no border changed)."""
    n = 0
    for t in range(len(reg.tl)):
        if not reg.cells.get(t):
            continue
        spans = reg.get(t)
        if spans and spans[-1][3] == SOURCE_END:
            spans[-1][3] = NOW
            reg.put(t, spans)
            n += 1
            STATS["S1 the states of 2024 go on to 2026"] += (NOW - SOURCE_END) * len(reg.cells[t])
    note(reg.key, "S1 the states of 2024 go on to 2026", f"{n} timelines", f"last span ends {SOURCE_END}",
         f"ends {NOW}", "Cliopatria v0.2.1 stops in 2024; no state or border changed in 2025–2026")


POST_SOVIET = {"Q159", "Q212", "Q184", "Q217", "Q191", "Q211", "Q37", "Q230", "Q399", "Q227", "Q232", "Q265",
               "Q874", "Q813", "Q863", "Q15180", "Q34266", "Q2895", "Q23427", "Q244165", "Q907112", "Q2577597"}
USSR = "Union of Soviet Socialist Republics"


def soviet_occupation(reg):
    """Known problem 21: the record marks Soviet-occupied Eastern Europe (1945-1948), Czechoslovakia after 1968 and
    northern Iran (1942-1946) as the Soviet Union. Where the land was not Soviet in 1995 (outside today's former
    Soviet states), the state that the record names right after the 'Soviet' years takes them over; Germany,
    1945-1948, becomes Allied-occupied Germany (Wikipedia: Allied-occupied Germany; Czechoslovak Socialist
    Republic; Polish People's Republic; Anglo-Soviet invasion of Iran)."""
    rule = "S3 Soviet occupation is not the Soviet Union"
    for t in list(reg.cells.keys()):
        if not reg.cells[t]:
            continue
        spans = reg.get(t)
        if not any(n == USSR for n, q, s, e in spans):
            continue
        n95, q95 = reg.state_at(t, 1995)
        if q95 in POST_SOVIET or n95 is None:
            continue
        new = []
        for k, (n, q, s, e) in enumerate(spans):
            if n != USSR:
                new.append([n, q, s, e])
                continue
            nxt = spans[k + 1] if k + 1 < len(spans) and spans[k + 1][2] == e + 1 else None
            prv = spans[k - 1] if k > 0 and spans[k - 1][3] == s - 1 else None
            if q95 == "Q183" or (nxt and nxt[0] == "German Democratic Republic" and s < 1949):
                repl = ["Allied-occupied Germany", None]
            elif nxt and nxt[0] != USSR:
                repl = [nxt[0], nxt[1]]
            elif prv and prv[0] != USSR:
                repl = [prv[0], prv[1]]
            else:
                new.append([n, q, s, e])
                continue
            new.append([repl[0], repl[1], s, e])
            STATS[rule] += (e - s + 1) * len(reg.cells[t])
        replace_spans(reg, rule, t, new, "occupied, not annexed: the land kept its own state")


def saxony(reg):
    """Known problem 21: under its Saxon kings (August II and III, 1697-1763) Saxony stayed the Electorate of
    Saxony; it was never part of the Polish-Lithuanian Commonwealth (Wikipedia: Electorate of Saxony)."""
    rename(reg, "S3 Saxony under its Saxon kings", "Polish-Lithuanian Commonwealth", 1697, 1763,
           "Electorate of Saxony", "Q156199", region=lambda la, lo: 50.1 <= la <= 52.1 and 11.3 <= lo <= 15.05,
           why="personal union only: the Elector was also King of Poland")


BRITISH_LABELS = {"British Africa", "British Colonial Empire", "Kingdom of Great Britain", "British Empire"}
BRITISH_ISLES = (49.8, 61.0, -11.0, 2.0)


def british_names(reg):
    """'Kingdom of Great Britain' is the record's name for Britain from 1707 to today, and also for some colonies;
    'British Africa' for Palestine and Iraq. Wikipedia: Kingdom of Great Britain (1707-1800), United Kingdom of
    Great Britain and Ireland (1801-1922), United Kingdom (from 1922); Mandatory Palestine (1920-1948), Emirate of
    Transjordan (1921-1946), Mandatory Iraq (1920-1932, the Kingdom of Iraq from 1921)."""
    isles = (lambda la, lo: in_box(la, lo, BRITISH_ISLES))
    rename(reg, "S2 names by period: Britain", "Kingdom of Great Britain", 1801, 1922,
           "United Kingdom of Great Britain and Ireland", KEEP, region=isles, why="the union with Ireland, 1801")
    rename(reg, "S2 names by period: Britain", "Kingdom of Great Britain", 1923, NOW, "United Kingdom", KEEP,
           region=isles, why="the Irish Free State left in December 1922")
    rename(reg, "S3 British mandates in the Middle East", BRITISH_LABELS, 1918, 1947, "Mandatory Palestine", "Q8680",
           region=lambda la, lo: 29.4 <= la <= 33.35 and 34.2 <= lo <= 35.58, why="a League of Nations mandate")
    rename(reg, "S3 British mandates in the Middle East", BRITISH_LABELS, 1921, 1946, "Emirate of Transjordan", "Q8680",
           region=lambda la, lo: 29.2 <= la <= 33.4 and 35.58 <= lo <= 39.3, why="a League of Nations mandate")
    iraq = (lambda la, lo: 29.0 <= la <= 37.4 and 38.8 <= lo <= 48.6 and not (la < 33.4 and lo < 39.3))
    rename(reg, "S3 British mandates in the Middle East", BRITISH_LABELS, 1917, 1920, "Mandatory Iraq", "Q8680",
           region=iraq, why="British occupation, then a mandate")
    rename(reg, "S3 British mandates in the Middle East", BRITISH_LABELS, 1921, 1957, "Kingdom of Iraq", "Q149805",
           region=iraq, why="the Kingdom of Iraq from August 1921 (under mandate until 1932; British troops 1941-1947)")
    rename(reg, "S3 British colonies are not Britain", "Kingdom of Great Britain", 1707, NOW, "British Empire",
           "Q8680", region=lambda la, lo: not isles(la, lo), why="a colony, not the kingdom itself")


def hyderabad_state(reg):
    """The Nizam's Hyderabad State was a princely state under British protection from 1798 until India annexed it
    on 17 September 1948 (Wikipedia: Hyderabad State; Operation Polo). The record shows it as British."""
    poly = (lambda la, lo: in_poly(la, lo, HYDERABAD_STATE))
    rename(reg, "S4 the Nizam's Hyderabad State", {"British Empire", "British Raj", "British Colonial Empire",
                                                     "Republic of India"}, 1799, 1948, "Hyderabad State",
           "Q1240096", region=poly, why="a princely state, not British India; annexed 17 September 1948")


def present_names(reg):
    """Names by period where one record name covers several states (Wikipedia articles named in each `why`)."""
    r = "S2 names by period"
    rename(reg, r, "Republic of India", 1947, 1949, "Dominion of India", KEEP,
           why="Dominion of India, 15 August 1947 – 26 January 1950 (known problem 4)")
    rename(reg, r, "Islamic Republic of Pakistan", 1947, 1955, "Dominion of Pakistan", KEEP,
           why="Dominion of Pakistan, 14 August 1947 – 23 March 1956")
    rename(reg, r, "Estado Novo", 1974, NOW, "Portugal", "Q45", why="the Estado Novo ended on 25 April 1974")
    rename(reg, r, "Denmark-Norway", 1814, NOW, "Kingdom of Denmark", "Q35",
           region=lambda la, lo: la < 57.9, why="Denmark–Norway ended in 1814 (Treaty of Kiel)")
    rename(reg, r, "Denmark-Norway", 1814, 1904, "Sweden-Norway", "Q20", region=lambda la, lo: la >= 57.9,
           why="Norway in union with Sweden, 1814–1905")
    rename(reg, r, "Denmark-Norway", 1905, NOW, "Kingdom of Norway", "Q20", region=lambda la, lo: la >= 57.9,
           why="Norway independent from 1905")
    rename(reg, r, "First Hellenic Republic", 1832, 1923, "Kingdom of Greece", "Q209065",
           why="the First Hellenic Republic ended in 1832; the Kingdom of Greece followed")
    rename(reg, r, "First Hellenic Republic", 1924, 1935, "Second Hellenic Republic", "Q209065",
           why="Second Hellenic Republic, 1924–1935")
    rename(reg, r, "First Hellenic Republic", 1936, 1973, "Kingdom of Greece", "Q209065",
           why="the monarchy restored in 1935")
    rename(reg, r, "Empire of Haiti", 1807, 1848, "Republic of Haiti", "Q790", why="the First Empire ended in 1806")
    rename(reg, r, "Empire of Haiti", 1859, NOW, "Republic of Haiti", "Q790", why="the Second Empire ended in 1859")
    rename(reg, r, "Mali Federation", 1961, NOW, "Republic of Mali", "Q912", region=lambda la, lo: lo > -12.25,
           why="the Mali Federation broke up in August 1960")
    rename(reg, r, "Mali Federation", 1961, NOW, "Senegal", "Q1041", region=lambda la, lo: lo <= -12.25,
           why="the Mali Federation broke up in August 1960")
    rename(reg, r, "Swedish Empire", 1722, 1904, "Kingdom of Sweden", "Q34",
           why="the Swedish Empire (great-power era) ended with the Treaty of Nystad, 1721")
    rename(reg, r, "Argentine Confederation", 1862, NOW, "Argentine Republic", "Q414",
           why="the Argentine Confederation ended in 1861")
    rename(reg, r, "Libyan Arab Republic", 1977, 2010, "Libyan Arab Jamahiriya", KEEP,
           why="Libyan Arab Jamahiriya, 1977–2011")
    rename(reg, r, "Libyan Arab Republic", 2011, NOW, "Libya", "Q1016", why="Libya after 2011")
    rename(reg, r, "Khmer Rouge", 1975, 1979, "Democratic Kampuchea", KEEP, why="Democratic Kampuchea, 1975–1979")
    rename(reg, r, "Principality of Bulgaria", 1908, 1946, "Kingdom of Bulgaria", "Q147909",
           why="Bulgaria became a kingdom (tsardom) in 1908")
    rename(reg, r, "United Principalities of Moldavia and Wallachia", 1881, 1947, "Kingdom of Romania",
           "Q203493", why="the Kingdom of Romania from 1881")
    rename(reg, r, "Republic of Florence", 1569, 1859, "Grand Duchy of Tuscany", "Q154849",
           why="the Grand Duchy of Tuscany from 1569")
    rename(reg, r, "Italian Republic", 1805, 1814, "Kingdom of Italy", "Q223936",
           why="Napoleon's Italian Republic became the Kingdom of Italy in 1805")
    rename(reg, r, "German Empire", 1919, 1919, "Weimar Republic", "Q41304", why="the Weimar Republic from 1918–1919")
    rename(reg, r, "Natalia Republic", 1844, 1910, "Colony of Natal", "Q8680", why="British Natal from 1843")
    rename(reg, r, "New France", 1764, 1791, "Province of Quebec", "Q8680", why="British after 1763 (Treaty of Paris)")
    rename(reg, r, "Pahlavi Dynasty", 1925, 1979, "Imperial State of Iran", KEEP,
           why="the state is the Imperial State of Iran; the Pahlavis were its dynasty")
    rename(reg, r, "Later Zhou", -1000, 0, "Zhou Dynasty", "Q35216",
           why="Later Zhou is a 10th-century AD dynasty; before AD 1 this is the Eastern Zhou")
    rename(reg, r, "Ngô Dynasty", 966, 1053, "Đại Cồ Việt", KEEP, why="the Ngô dynasty ended in 965")
    rename(reg, r, "Ngô Dynasty", 1054, 1406, "Đại Việt", KEEP, why="named Đại Việt from 1054")
    rename(reg, r, "Khmer Empire", 1432, 1863, "Kingdom of Cambodia", KEEP,
           why="the Khmer (Angkor) Empire ended in 1431; the post-Angkor kingdom followed")
    rename(reg, r, "Sultanate of Oman", -3000, 1969, "Muscat and Oman", KEEP, why="named the Sultanate of Oman in 1970")
    rename(reg, r, "Federal Republic of Nigeria", 1960, 1963, "Federation of Nigeria", KEEP,
           why="a federation under the Queen until the republic of October 1963")
    rename(reg, r, "Republic of Kenya", 1963, 1964, "Kenya", KEEP, why="a dominion until the republic of December 1964")
    rename(reg, r, "Republic of Tunisia", 1956, 1956, "Kingdom of Tunisia", KEEP, why="a kingdom until July 1957")
    rename(reg, r, "Republic of Burundi", 1962, 1966, "Kingdom of Burundi", KEEP, why="a kingdom until November 1966")
    rename(reg, r, "Republic of The Gambia", 1965, 1969, "The Gambia", KEEP, why="a dominion until April 1970")
    rename(reg, r, "Republic of Trinidad and Tobago", 1962, 1975, "Trinidad and Tobago", KEEP,
           why="a dominion under the Queen until the republic of August 1976")
    rename(reg, r, "First Toungoo Empire", 1600, 1752, "Restored Toungoo Kingdom", KEEP,
           why="the First Toungoo Empire fell in 1599; the Restored Toungoo (Nyaungyan) kingdom followed")
    rename(reg, r, "Almohad Caliphate", 1270, 1465, "Marinid Sultanate", "Q582861", region=lambda la, lo: lo < -1.5,
           why="the Almohads lost Marrakesh to the Marinids in 1269")
    rename(reg, r, "Sultanate of Malacca", 1512, 1861, "Johor Sultanate", None,
           region=lambda la, lo: 1.2 <= la <= 4.6 and 101.0 <= lo <= 104.6,
           why="Malacca fell to Portugal in 1511; its sultans went on as the Johor Sultanate")
    drop_spans(reg, "S7 a state that was gone is not named", "Sultanate of Malacca", 1512, 1861,
               "Malacca fell to Portugal in 1511; these lands had other sultans, which the record does not name")
    rename(reg, r, "County of Savoy", 1416, 1713, "Duchy of Savoy", None, why="Savoy became a duchy in 1416")
    rename(reg, r, "County of Brabant", 1183, 1430, "Duchy of Brabant", None, why="Brabant became a duchy in 1183")
    rename(reg, r, "Roman Kingdom", -508, -1, "Roman Republic", "Q17167", why="the Roman Republic from 509 BC")
    rename(reg, r, "Kingdom of Cambodia", 1970, 1975, "Khmer Republic", KEEP, why="the Khmer Republic, 1970–1975")
    rename(reg, r, "People's Republic of Kampuchea", 1989, 1992, "State of Cambodia", KEEP,
           why="renamed the State of Cambodia in 1989")
    rename(reg, r, "People's Republic of Kampuchea", 1993, NOW, "Kingdom of Cambodia", "Q424",
           why="the monarchy was restored in September 1993")
    rename(reg, r, "Republic of Cabo Verde", 1975, NOW, "Comoros", "Q970", region=lambda la, lo: lo > 0,
           why="these cells are the Comoros (Moroni), not Cabo Verde", pure=False)
    rename(reg, r, "Republic of Indonesia", 2000, NOW, "East Timor", "Q574",
           region=lambda la, lo: -9.6 <= la <= -8.0 and 124.0 <= lo <= 127.4 and not (la > -9.0 and lo < 124.95),
           why="Indonesia left East Timor in 1999 (UN administration, then independence in 2002)", pure=False)


def city_points(reg, fill_cells):
    """Bombay and Madras were English from 1668 and 1640, but a 0.5-degree cell is bigger than either: the Bombay
    cell is Mughal and Maratha land on the mainland, and Madras shares a cell with Dutch Pulicat. Each city gets its
    own place in the record (Wikipedia: History of Mumbai; Fort St. George; Madras Presidency)."""
    rule = "S5 cities smaller than a map square"
    world = (lambda n, q, s, e: [n, q, s, e])
    cities = [
        ("Bombay", 18.94, 72.83, 1534, [["Portuguese Colonies", "Q200464", 1534, 1667],
                                         ["English Colonial Empire", "Q617219", 1668, 1708],
                                         ["British Empire", "Q8680", 1709, 1858], ["British Raj", "Q129286", 1859, 1946],
                                         ["Dominion of India", "Q668", 1947, 1949], ["Republic of India", "Q668", 1950, NOW]]),
        ("Madras", 13.08, 80.27, 1640, [["English Colonial Empire", "Q617219", 1640, 1708],
                                         ["British Empire", "Q8680", 1709, 1858], ["British Raj", "Q129286", 1859, 1946],
                                         ["Dominion of India", "Q668", 1947, 1949], ["Republic of India", "Q668", 1950, NOW]]),
    ]
    for name, la, lo, start, colonial in cities:
        base = fill_cells(la, lo)
        spans = [world(*s) for s in base if s[3] < start] + [list(s) for s in colonial]
        t = reg.tl.append([])
        reg.put(t, spans)
        i = reg.pl.append([round(la * 100), round(lo * 100), t])
        reg.cells[t] = [i]
        note(reg.key, rule, f"{name} ({la},{lo})", "the nearest map square's states", spans_text(spans, start),
             "a new place in the record for the city itself")
        STATS[rule] += NOW - start + 1


OCCUPIERS_1945 = {"British Empire", "United States of America", "French Fourth Republic"}
# step 26 (S8): who held land in the Second World War without it becoming theirs
WW2_AXIS = {"Q7318", "Q172579", "Q188712", "Q147909", "Q28"}      # Germany, Italy, Japan, Bulgaria, Hungary
WW2_ALSO = {"Q155198"}                                             # the Yugoslav Partisans, inside occupied Yugoslavia
WW2_IN_SOVIET = {"Q33", "Q203493"}                                 # Finland and Romania held Soviet land 1941-1944
WW2_ALLIED = {"Q8680", "Q30", "Q149805", "Q408"}                   # British, American, Iraq command, Australian troops
WW2_ALLIED_HOSTS = {"Q62567", "Q223", "Q207991", "Q188161"}        # Iceland, Greenland, Iran, the Dutch East Indies
WW2_GOES_ON = {("Second Polish Republic", "Republic of Poland"), ("Dutch East Indies", "Republic of Indonesia"),
               ("Greenland", "Denmark"), ("Kingdom of Iceland", "Republic of Iceland"),
               ("French Third Republic", "French Fourth Republic"), ("French Third Republic", "Vichy France"),
               ("Vichy France", "French Fourth Republic"), ("Yugoslavia", "Socialist Federal Republic of Yugoslavia")}
FRG, AUSTRIA2 = "Q713750", "Q187830"
R_S8 = "S8 rebels and occupiers are not the state"


def rebels_and_occupiers(reg):
    """Step 26. A movement or an occupying army is not the state of the land (the rule of step 25's S3, for the
    cases the fact check found next):
    - northern Syria 2014-2026 was 'Mujahideen' (rebel- and IS-held land in the civil war): it stays Syria, whose
      list of heads goes on with Ahmed al-Sharaa from December 2024 (Wikipedia: Syrian civil war; Fall of the
      Assad regime);
    - Afghanistan 1979-2005 was 'Mujahideen' and 'Taliban': it stays Afghanistan, whose list of heads already
      names each ruler, Najibullah, Rabbani, Mullah Omar and Karzai (Wikipedia: History of Afghanistan);
    - 'Cuban Communists' 1958-1959 (the rebel zone of the Sierra Maestra) stays the Republic of Cuba until Castro
      took power in January 1959;
    - lands occupied by Germany in the Second World War for at most six years, with the same state before and
      after (Denmark, Norway, the Netherlands, Belgium, Luxembourg, Greece, Yugoslavia, Czechoslovakia, the
      occupied Soviet lands, Italy in 1944, Hungary in 1944): the state went on, under occupation or in exile;
      occupied Poland stays the Second Polish Republic (its government in exile) and occupied France the French
      State (Vichy), which both governed or claimed those lands (Wikipedia: German-occupied Europe);
    - the British, American and French zones of Germany, 1945-1949, become Allied-occupied Germany, as the Soviet
      zone did in step 25; in Austria the Second Republic was founded in April 1945 (Wikipedia: Allied-occupied
      Germany; Allied-occupied Austria)."""
    for t in list(reg.cells.keys()):
        if not reg.cells[t]:
            continue
        spans = reg.get(t)
        new = [list(x) for x in spans]
        why = {}
        has_afghanistan = any(q == "Q889" for _n, q, _s, _e in spans)
        for i, (n, q, s, e) in enumerate(spans):
            prev = spans[i - 1] if i else None
            nxt = spans[i + 1] if i + 1 < len(spans) else None
            if n == "Mujahideen" and s >= 2010 and prev:
                new[i][:2] = prev[:2]
                why[i] = "rebel-held land in the Syrian civil war is still Syria"
            elif n in ("Mujahideen", "Taliban") and 1979 <= s <= 2005 and has_afghanistan:
                new[i][:2] = ["Afghanistan", "Q889"]
                why[i] = "Afghanistan stayed one state; its list of heads names each ruler"
            elif n == "Cuban Communists" and prev:
                new[i][:2] = prev[:2]
                why[i] = "the rebels' zone stayed the Republic of Cuba until January 1959"
            elif q == "Q7318" and prev and nxt and e - s <= 6:
                if prev[1] and prev[1] == nxt[1]:
                    new[i][:2] = prev[:2]
                    why[i] = "occupied by Germany in the Second World War; the state went on"
                elif prev[0] == "Second Polish Republic" and nxt[0] in ("Republic of Poland", "Polish People's Republic"):
                    new[i][:2] = prev[:2]
                    why[i] = "occupied Poland: the Second Polish Republic went on in exile"
                elif prev[0] in ("French Third Republic", "Vichy France") and nxt[0] in (
                        "French Fourth Republic", "Provisional Government of the French Republic"):
                    new[i][:2] = ["Vichy France", "Q69808"]
                    why[i] = "occupied France: the French State (Vichy) governed both zones"
            elif n in OCCUPIERS_1945 and 1945 <= s <= 1946 and prev and prev[1] == "Q7318":
                j = i
                while j < len(spans) and spans[j][0] in OCCUPIERS_1945 and spans[j][3] <= 1949:
                    j += 1
                if j < len(spans) and spans[j][1] == FRG:
                    for k in range(i, j):
                        new[k][:2] = ["Allied-occupied Germany", None]
                        why[k] = "a zone of Allied-occupied Germany, not the occupier's own land"
                elif j < len(spans) and spans[j][1] == AUSTRIA2:
                    for k in range(i, j):
                        new[k][:2] = list(spans[j][:2])
                        why[k] = "Austria's Second Republic was founded in April 1945, under Allied occupation"
        ww2_runs(new, why)
        if why:
            before = "; ".join(f"{spans[i][0]} {yr(spans[i][2])}–{yr(spans[i][3])}" for i in sorted(why))
            after = "; ".join(f"{new[i][0]} {yr(new[i][2])}–{yr(new[i][3])}" for i in sorted(why))
            STATS[R_S8] += sum(spans[i][3] - spans[i][2] + 1 for i in why) * len(reg.cells[t])
            reg.put(t, merge_same(new))
            note(reg.key, R_S8, reg.where(t), before, after, "; ".join(sorted(set(why.values()))))


def ww2_runs(new, why):
    """Step 26 (S8), the rest of the Second World War: a run of years (at most nine, all inside 1937-1946) in which
    the record names the powers that held a land - Germany, Italy, Japan, Bulgaria or Hungary (Axis-held Greece,
    Yugoslavia, Albania, the Dutch East Indies, Malaya and Borneo, Hong Kong, the Philippines, French Indochina,
    occupied China, Burma), Finland or Romania in Soviet land, British, American or Australian troops in Iceland,
    Greenland, Iran or the Indies - between two years of the same state: that state went on (under occupation, in
    exile, or as the land the occupiers left), as with the German occupations above (Wikipedia: Axis occupation of
    Greece; Japanese occupation of the Dutch East Indies; Japanese occupation of Malaya; Allied occupation of
    Iceland; Anglo-Soviet invasion of Iran). Annexations that held after the war (Austria in 1938) and states of
    their own (the Independent State of Croatia, Free France) are not touched."""
    i = 1
    while i < len(new) - 1:
        prev = new[i - 1]

        def held(x):
            _n, q, s, e = x
            if not (s >= 1937 and e <= 1946) or q == prev[1]:
                return False
            return (q in WW2_AXIS or q in WW2_ALSO or (q in WW2_IN_SOVIET and prev[1] == "Q15180")
                    or (q in WW2_ALLIED and prev[1] in WW2_ALLIED_HOSTS))

        j = i
        while j < len(new) and held(new[j]):
            j += 1
        if i < j < len(new):
            nxt = new[j]
            same = (prev[1] and prev[1] == nxt[1]) or (not prev[1] and prev[0] == nxt[0]) \
                or (prev[0], nxt[0]) in WW2_GOES_ON
            if same and new[j - 1][3] - new[i][2] + 1 <= 9:
                target = ["Vichy France", "Q69808"] if prev[0] == "French Third Republic" else list(prev[:2])
                for k in range(i, j):
                    if new[k][:2] != target:
                        new[k][:2] = list(target)
                        why[k] = "held by another power in the Second World War; the state went on"
                i = j
                continue
        i += 1


def mislabelled_cells(reg):
    """Step 26. Map squares whose record names the wrong land altogether:
    - three squares of Moldova (Bessarabia and the left bank of the Dniester) were 'Russian-occupied territories'
      from 1944: they were the Soviet Union (the Moldavian SSR) until 1991, then the Republic of Moldova
      (Transnistria is not recognised by any member of the United Nations) (Wikipedia: Moldavian SSR);
    - the square of St Croix carried the history of St Kitts: St Croix was Danish from 1733 (bought from the French
      West India Company), sold to the United States in 1917 (Wikipedia: Saint Croix; Danish West Indies)."""
    for t in list(reg.cells.keys()):
        if not reg.cells[t]:
            continue
        spans = reg.get(t)
        if not any(q == "Q106809413" and e >= 1944 for _n, q, _s, e in spans):
            continue
        new = []
        for n, q, s, e in spans:
            if q != "Q106809413" or e < 1944:
                new.append([n, q, s, e])
                continue
            if s <= 1991:
                new.append(["Union of Soviet Socialist Republics", "Q15180", s, min(e, 1991)])
            if e >= 1992:
                new.append(["Republic of Moldova", "Q217", max(s, 1992), e])
        new = merge_same(new)
        STATS["S8 squares that named the wrong land"] += sum(e - max(s, 1944) + 1 for n, q, s, e in spans
                                                           if q == "Q106809413" and e >= 1944) * len(reg.cells[t])
        replace_spans(reg, "S8 squares that named the wrong land", t, new,
                      "the Moldavian SSR until 1991, then the Republic of Moldova")
    for i in range(len(reg.pl)):
        la, lo = reg.latlon(i)
        if abs(la - 17.75) < 0.01 and abs(lo + 64.75) < 0.01:
            t = reg.isolate(reg.timeline_of(i), [i])
            spans = [x for x in reg.get(t) if x[2] < 1733]
            spans = [[n, q, s, min(e, 1732)] for n, q, s, e in spans]
            spans += [["Denmark-Norway", "Q62651", 1733, 1813], ["Kingdom of Denmark", "Q35", 1814, 1916],
                      ["United States of America", "Q30", 1917, NOW]]
            STATS["S8 squares that named the wrong land"] += NOW - 1733 + 1
            replace_spans(reg, "S8 squares that named the wrong land", t, spans,
                          "St Croix: Danish from 1733, American from 1917")


def coastal_fill(reg):
    """A cell whose centre lies in the sea is covered only by the few states whose outline reaches over the water,
    so coastal cities (Baku, Aden, Sydney ...) had no state in most years. When a cell has fewer than half the
    covered years of its third-best-covered neighbour, each empty stretch takes the state that at least three of
    its eight neighbours share in those years. Existing spans are never changed."""
    rule = "S6 coastal squares take their neighbours' state"
    idx = {}
    for i in range(len(reg.pl)):
        la, lo = reg.latlon(i)
        idx[(math.floor(la * 2), math.floor(lo * 2))] = i
    tl_of = {i: reg.timeline_of(i) for i in idx.values()}
    covered = {}
    cache = {}

    def spans_of(t):
        if t not in cache:
            cache[t] = reg.get(t)
        return cache[t]

    def cover(t):
        if t not in covered:
            covered[t] = sum(e - s + 1 for n, q, s, e in spans_of(t) if not n.startswith("("))
        return covered[t]
    plan = []
    for (y2, x2), i in idx.items():
        t = tl_of[i]
        nb = [idx.get((y2 + dy, x2 + dx)) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if dy or dx]
        nb = [j for j in nb if j is not None]
        if len(nb) < 3:
            continue
        mine = cover(t)
        theirs = sorted(cover(tl_of[j]) for j in nb)
        if mine * 2 >= theirs[-3]:
            continue
        own = spans_of(t)
        bounds = sorted({b for j in nb for n, q, s, e in spans_of(tl_of[j]) for b in (s, e + 1)})
        fills = []
        for a, b in zip(bounds, bounds[1:]):
            if any(s <= a and b - 1 <= e for n, q, s, e in own if not n.startswith("(")):
                continue
            votes = collections.Counter()
            for j in nb:
                for n, q, s, e in spans_of(tl_of[j]):
                    if s <= a and b - 1 <= e and not n.startswith("("):
                        votes[(n, q)] += 1
                        break
            if votes:
                (n, q), c = votes.most_common(1)[0]
                if c >= 3:
                    fills.append([n, q, a, b - 1])
        if fills:
            plan.append((i, t, fills))
    for i, t, fills in plan:
        t2 = reg.isolate(t, [i])
        own = reg.get(t2)
        fills = merge_same(fills)
        # the original spans stay exactly as they were; only the empty stretches are new
        reg.put(t2, sorted(own + fills, key=lambda x: x[2]))
        STATS[rule] += sum(e - s + 1 for n, q, s, e in fills)
        la, lo = reg.latlon(i)
        note(reg.key, rule, f"cell at {la:.2f},{lo:.2f}", "no state in these years", spans_text(fills),
             "at least 3 of its 8 neighbours had this state in these years")
    return plan


def fix_states(docs):
    world, deccan = Register(docs["world"]), Register(docs["deccan"])
    for reg in (world, deccan):
        extend_present(reg)
    for reg in (world, deccan):
        hyderabad_state(reg)
    for reg in (world, deccan):
        present_names(reg)
    soviet_occupation(world)
    saxony(world)
    british_names(world)
    rebels_and_occupiers(world)
    mislabelled_cells(world)
    rename(world, "S2 the state's own name", "Éire", 1938, NOW, "Ireland",
           why="Constitution of Ireland, Article 4: 'the name of the State is Éire, or, in the English language, Ireland'")

    def base_spans(la, lo):
        best = min(range(len(world.pl)), key=lambda i: km(la, lo, *world.latlon(i)))
        return world.get(world.timeline_of(best))
    plan = coastal_fill(world)
    city_points(world, base_spans)
    borrowed = border_cities(world, deccan)
    mark_estimates(docs, world, deccan, plan, borrowed)
    return world, deccan, plan


CITIES = f"{WF}/sources/step26_cities.json.gz"
R_S9 = "S9 border cities follow their own country"


def border_cities(world, deccan):
    """Step 26 (S9, known problem 20): a city on a border can lie in a map square that belongs to the neighbour, so it
    took the neighbour's whole history: Kinshasa (14.6 million people) was told it is in the Republic of the Congo,
    Tijuana, Ciudad Juarez, Mexicali and Reynosa in the United States, Johor Bahru and Batam in Singapore, Vientiane
    in Thailand, Basel in Germany, Geneva and Nice in France and Monaco. Wikidata's cities of 100,000 people or more
    (saved in sources/step26_cities.json.gz) are compared with the record in 2026; a city whose answer is another
    country gets a place of its own, with the history of the nearest square of its own country (within 150 km),
    marked as an estimate (A5: taken from a neighbouring square). A twin city across the border that would now get
    the wrong answer gets a place of its own too, keeping the history it had (the capitals of all states are in the
    list for that, whatever their size: Monaco next to Nice). Palestine's towns and towns claimed by two states keep
    the record's answer."""
    try:
        cities = jload(CITIES)["cities"]
    except FileNotFoundError:
        print("S9 skipped: no", CITIES)
        return []
    deccan_cells = set()
    for i in range(len(deccan.pl)):
        la, lo = deccan.latlon(i)
        deccan_cells.add((math.floor(la * 2), math.floor(lo * 2)))

    def km(a, b, c, d):
        r = math.pi / 180.0
        x = math.sin((c - a) * r / 2) ** 2 + math.cos(a * r) * math.cos(c * r) * math.sin((d - b) * r / 2) ** 2
        return 12742.0 * math.asin(min(1.0, math.sqrt(x)))

    grid = collections.defaultdict(list)

    def add_to_grid(i):
        la, lo = world.latlon(i)
        grid[(math.floor(la * 2), math.floor(lo * 2))].append(i)

    for i in range(len(world.pl)):
        add_to_grid(i)
    added = {}          # city qid -> place index
    added_set = set()
    borrowed = []

    def nearest(lat, lon, test=None, rings=1):
        best = None
        cy, cx = math.floor(lat * 2), math.floor(lon * 2)
        for dy in range(-rings, rings + 1):
            for dx in range(-rings, rings + 1):
                for i in grid.get((cy + dy, cx + dx), []):
                    if test and not test(i):
                        continue
                    la, lo = world.latlon(i)
                    d = km(lat, lon, la, lo)
                    if best is None or d < best[0] or (d == best[0] and i < best[1]):
                        best = (d, i)
        return best

    def state_qid(i, year=NOW):
        for n, q, a, b in world.get(world.timeline_of(i)):
            if a <= year <= b:
                return q
        return None

    # the record's id for each country today: its own id when the record uses it, else what most of its cities get
    used_now = {state_qid(i) for i in range(len(world.pl))}
    votes = collections.defaultdict(collections.Counter)
    for c in cities:
        b = nearest(c["lat"], c["lon"])
        if b and b[0] <= 60 and len(c["countries"]) == 1:
            votes[next(iter(c["countries"]))][state_qid(b[1])] += 1
    record_id = {}
    for c in cities:
        for cq in c["countries"]:
            if cq in record_id:
                continue
            if cq in used_now:
                record_id[cq] = cq
            elif votes[cq] and votes[cq].most_common(1)[0][1] >= max(3, 0.6 * sum(votes[cq].values())):
                record_id[cq] = votes[cq].most_common(1)[0][0]

    def own_ids(c):
        return {record_id[q] for q in c["countries"] if q in record_id}

    def disputed(c):
        # Palestine's towns (the record's "Gaza/Hamas" is not the West Bank's state) and towns claimed by two of
        # today's states (Crimea) keep the record's answer
        return "Q219060" in c["countries"] or len([q for q in c["countries"] if q in used_now]) >= 2

    def in_deccan(c):
        cy, cx = math.floor(c["lat"] * 2), math.floor(c["lon"] * 2)
        return any((cy + dy, cx + dx) in deccan_cells for dy in (-1, 0, 1) for dx in (-1, 0, 1))

    def add_point(c, src_i, mark):
        t = world.tl.append([])
        spans = [list(x) for x in world.get(world.timeline_of(src_i))]
        world.put(t, spans)
        i = world.pl.append([round(c["lat"] * 100), round(c["lon"] * 100), t])
        world.cells[t] = [i]
        add_to_grid(i)
        added[c["q"]] = i
        added_set.add(i)
        if mark and spans:
            borrowed.append((t, spans[0][2], spans[-1][3]))
        STATS[R_S9] += sum(min(e, NOW) - s + 1 for _n, _q, s, e in spans)
        return spans

    moved = twins = 0
    for _round in range(6):
        changed = 0
        for c in cities:                  # the biggest first
            ids = own_ids(c)
            if c["q"] in added or not ids or in_deccan(c) or disputed(c):
                continue
            now = nearest(c["lat"], c["lon"])
            if now is None or now[0] > 60 or state_qid(now[1]) in ids:
                continue
            old = nearest(c["lat"], c["lon"], test=lambda i: i not in added_set)
            if old is not None and old[0] <= 60 and state_qid(old[1]) in ids:
                add_point(c, old[1], False)         # a twin city: keeps the answer the new places took from it
                note(world.key, R_S9, f"{c['name']} ({c['lat']}, {c['lon']})", "its square's history",
                     "the same history, at a place of its own", "a twin city across the border keeps its answer")
                twins += 1
                changed += 1
                continue
            good = nearest(c["lat"], c["lon"], test=lambda i: i not in added_set and state_qid(i) in ids, rings=3)
            if good is None or good[0] > 150:
                continue
            before = state_name_now(world, now[1])
            spans = add_point(c, good[1], True)
            note(world.key, R_S9, f"{c['name']} ({c['lat']}, {c['lon']})", f"{before} (the square's state)",
                 spans_text(spans, spans[0][2] if spans else 0),
                 f"a city of {int(c['pop']):,} people in {', '.join(c['countries'].values())}; the history of the "
                 f"square {round(good[0])} km away, marked estimated")
            moved += 1
            changed += 1
        if not changed:
            break
    print(f"S9: {moved} border cities moved to their own country, {twins} twin cities kept their answer")
    return borrowed


def state_name_now(world, i):
    for n, q, a, b in world.get(world.timeline_of(i)):
        if a <= NOW <= b:
            return n
    return "-"


def mark_estimates(docs, world, deccan, plan, borrowed=()):
    """Step 26 (A5), the recorded/estimated mark of the two state records:
    - recordedUntil: the last year the source records (Cliopatria v0.2.1: 2024); later years carry the states of
      that year forward (S1), an estimate;
    - estimated (world record): [timeline, first year, last year] for each stretch a coastal square took from its
      neighbours (S6). Each such square has a timeline of its own (S6 isolates it), so the marks stay with it."""
    for reg in (world, deccan):
        docs[reg.key].set_key("recordedUntil", SOURCE_END)
    marks = []
    for i, _t, fills in plan:
        t2 = world.timeline_of(i)
        for _n, _q, a, b in merge_same(fills):
            marks.append([t2, a, b])
    for t, a, b in borrowed:              # S9: border cities' history taken from a square of their own country
        marks.append([t, a, b])
    marks.sort()
    docs["world"].set_key("estimated", marks)
    STATS["A5 coastal stretches marked estimated"] = len(marks)
    note("world", "A5 coastal stretches marked estimated", f"{len(marks)} stretches in {len(plan)} squares",
         "not marked", "marked estimated", "taken from the neighbouring squares (S6)")
    note("world", "A5 years after the record marked estimated", "every square", f"after {SOURCE_END}: not marked",
         f"recordedUntil {SOURCE_END}", "Cliopatria v0.2.1 stops in 2024; the states of 2024 are carried forward")


# ====================================================================== main

def write_change_list():
    with open(CSV_OUT, "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", newline="", write_through=True) as f:
        w = csv.writer(f)
        w.writerow(["file", "rule", "item", "before", "after", "why"])
        for row in CHANGES:
            w.writerow(row)


def main(argv):
    if "--undo" in argv:
        undo()
        return
    undo(quiet=True)
    only = [a for a in argv if not a.startswith("-")]
    keys = ["world", "deccan", "facts", "money", "vips", "people", "languages"] + [k for k in FILES if k.startswith("ev_")]
    docs = {k: Doc(k) for k in keys}
    world, deccan, _plan = fix_states(docs)
    if not only or "rulers" in only:
        fix_rulers(docs, world, deccan)
    if not only or "culture" in only:
        fix_culture(docs)
    if not only or "events" in only:
        fix_events(docs)
    if not only or "people" in only:
        fix_people(docs)
    if not only or "foundation" in only:
        fix_foundation(docs)
    sync_money(docs)
    files = {}
    for k, d in docs.items():
        r = d.finish()
        if r:
            files[k] = r
    jsave(LOG, {"note": "step 25-26 undo record: python3 fix_history_data.py --undo", "files": files})
    write_change_list()
    by_rule = collections.Counter(r[1] for r in CHANGES)
    for rule, n in sorted(by_rule.items()):
        extra = f"  ({STATS[rule]:,} place-years)" if STATS.get(rule) else ""
        print(f"{n:6d}  {rule}{extra}")
    print("changed files:", ", ".join(files), "| change list:", len(CHANGES), "lines")


# ====================================================================== R. rulers (polity_facts.json.gz)

GOV_TITLE = re.compile(r"(?i)prime minister|\bpremier\b|chancellor|\bminister|chairman of (?:the )?(?:council|committee)"
                       r"(?! of state)|grand vizier|\bvizier\b|chief minister|first minister|head of (?:the )?government|"
                       r"president of the (?:ministry|council of ministers|government(?! junta))|council president|"
                       r"grand pensionary|governmental commission")
CLAIMANT = re.compile(r"(?i)\bclaimants?\b|\bpretenders?\b")
TITLE_ONLY = {"consul", "consuls", "doge", "king", "emperor", "regent", "governor", "president", "ruler", "chief",
              "khan", "sultan", "pharaoh", "shah", "raja", "maharaja", "tsar", "prince", "duke", "count", "lord",
              "queen", "anonymous", "none", "n a", "head of the government", "head of state"}
GROUP_DROP = re.compile(r"(?i)^(phanariote rule|civil war period|rule of the dukes|consiglio degli anziani|"
                        r"domain of the .* family|trịnh lords)$")
NOT_A_RULER = {("Qi", "Sun Tzu"), ("Qi", "Xun Kuang"), ("Qi", "Guan Zhong"), ("Qi", "Yin Wen"), ("Qi", "Sun Bin")}
NAMED_AFTER_RULER = {"Wihtgar"}   # the state is named after its ruler: not a state named as the ruler
# Rows that Wikipedia contradicts outright (the article in each reason). (state qid or name, ruler name, start).
DROP_ROWS = [
    ("Islamic Republic of Iran", "Shah", 1980, "the Shah left in January 1979 (Iranian Revolution)"),
    ("Second Republic of Austria", "Otto von Habsburg", None, "a pretender: Austria abolished its monarchy in 1918"),
    ("Kingdom of Cambodia", "Pol Pot", None, "Pol Pot ruled Democratic Kampuchea (1975-1979), never the kingdom"),
    ("French First Republic", "Louis XVII", None, "Louis XVII never reigned: France was a republic (a titular king)"),
]
TO_GOV = [   # (state, name, latest start year it applies to, reason)
    ("Kingdom of Cambodia", "Hun Sen", NOW, "Hun Sen was prime minister; the king is head of state"),
    ("Kingdom of Cambodia", "Lon Nol", 1971, "Lon Nol was prime minister of the kingdom before he led the Khmer Republic"),
]
# Rows to add or correct by hand (Wikipedia article in the reason). Each: state qid, name, title, start, end.
MANUAL_HEADS = [
    ("Q36", "Bolesław Bierut", "President", 1944, 1952, "Bolesław Bierut: head of the State National Council "
                                                         "1944-1947, President of Poland 1947-1952"),
    ("Q794", "Ruhollah Khomeini", "Supreme Leader", 1979, 1989, "Supreme Leader of Iran"),
    ("Q794", "Ali Khamenei", "Supreme Leader", 1989, NOW, "Supreme Leader of Iran"),
    ("Q156199", "Augustus II the Strong", "Elector", 1694, 1733, "Augustus II the Strong: Elector of Saxony 1694-1733"),
    ("Q17435890", "Muammar Gaddafi", "Brotherly Leader and Guide of the Revolution", 1977, 2011, "Muammar Gaddafi"),
    ("Q191764", "Norodom Sihanouk", "Head of State", 1975, 1976, "Democratic Kampuchea"),
    ("Q191764", "Khieu Samphan", "President of the State Presidium", 1976, 1979, "Democratic Kampuchea"),
] + [("Q5306909", n, "President", a, b, "President of Ireland (Wikipedia: the list of presidents; step 26)")
     for n, a, b in [("Douglas Hyde", 1938, 1945), ("Seán T. O'Kelly", 1945, 1959), ("Éamon de Valera", 1959, 1973),
                     ("Erskine H. Childers", 1973, 1974), ("Cearbhall Ó Dálaigh", 1974, 1976),
                     ("Patrick Hillery", 1976, 1990), ("Mary Robinson", 1990, 1997), ("Mary McAleese", 1997, 2011),
                     ("Michael D. Higgins", 2011, 2025), ("Catherine Connolly", 2025, NOW)]] + [("Q205662", n, "Shōgun", a, b, "Tokugawa shogunate: the shōgun ruled; the emperor in Kyoto was a figurehead")
     for n, a, b in [("Tokugawa Ieyasu", 1603, 1605), ("Tokugawa Hidetada", 1605, 1623), ("Tokugawa Iemitsu", 1623, 1651),
                     ("Tokugawa Ietsuna", 1651, 1680), ("Tokugawa Tsunayoshi", 1680, 1709), ("Tokugawa Ienobu", 1709, 1712),
                     ("Tokugawa Ietsugu", 1713, 1716), ("Tokugawa Yoshimune", 1716, 1745), ("Tokugawa Ieshige", 1745, 1760),
                     ("Tokugawa Ieharu", 1760, 1786), ("Tokugawa Ienari", 1787, 1837), ("Tokugawa Ieyoshi", 1837, 1853),
                     ("Tokugawa Iesada", 1853, 1858), ("Tokugawa Iemochi", 1858, 1866), ("Tokugawa Yoshinobu", 1867, 1868)]]
NEW_FACTS = {"Q191764": ("Democratic Kampuchea", "Democratic Kampuchea")}   # states the lists did not have
CLONE_FACTS = {"Q912": ("Q216632", "Republic of Mali", "Mali")}   # Mali's presidents sat under the Mali Federation
FIGUREHEADS_TO_GOV = {"Q205662": re.compile(r"(?i)emperor of japan")}
FIX_ROWS = [  # (state qid or None, name, start, new_start, new_end, reason)
    (None, "Tan'gun", 2333, -2333, -2240, "Dangun: legendary founder, 2333 BC (a BC year written as AD)"),
    (None, "Otto V", 1347, 1347, 1379, "Otto V of Bavaria: duke 1347-1379"),
    (None, "Habbus al-Muzaffar", 20, 1019, 1038, "Habbus al-Muzaffar: ruler of Granada 1019-1038"),
    (None, "Mohammad Reza Pahlavi", None, None, 1979, "Mohammad Reza Pahlavi left Iran in January 1979"),
]
COMMUNIST_PARTY_LEADERS = {"Q15180"}   # the Soviet Union: the party's General Secretary ruled
# Whole stretches replaced by Wikipedia's list (state qid: (first year, last year, rows, reason)). The Habsburg rows
# used the archdukes' own numbering ("Leopold VI" for Emperor Leopold I) and named lands ("Archduchy of Austria") as
# rulers.
REPLACE_HEADS = {
    "Q153136": (1521, 1806, [
        ["Ferdinand I", "Archduke of Austria, King of Bohemia and Hungary", 1521, 1564],
        ["Maximilian II", "Holy Roman Emperor", 1564, 1576], ["Rudolf II", "Holy Roman Emperor", 1576, 1612],
        ["Matthias", "Holy Roman Emperor", 1612, 1619], ["Ferdinand II", "Holy Roman Emperor", 1619, 1637],
        ["Ferdinand III", "Holy Roman Emperor", 1637, 1657], ["Leopold I", "Holy Roman Emperor", 1657, 1705],
        ["Joseph I", "Holy Roman Emperor", 1705, 1711], ["Charles VI", "Holy Roman Emperor", 1711, 1740],
        ["Maria Theresa", "Archduchess of Austria, Queen of Hungary and Bohemia", 1740, 1780],
        ["Joseph II", "Holy Roman Emperor", 1780, 1790], ["Leopold II", "Holy Roman Emperor", 1790, 1792],
        ["Francis II", "Holy Roman Emperor", 1792, 1806]],
        "Wikipedia: Habsburg monarchy (the monarchs, 1521-1806)"),
}


FEMININE = {"King": "Queen", "Emperor": "Empress", "Prince": "Princess", "Grand Duke": "Grand Duchess",
            "Duke": "Duchess", "Tsar": "Tsaritsa", "Archduke": "Archduchess", "Sultan": "Sultana"}


def short_title(label, female=0):
    if not label:
        return ""
    t = re.split(r"\s+of\s+", label, maxsplit=1)[0]
    t = t[:1].upper() + t[1:]
    return FEMININE.get(t, t) if female else t


def map_years(world, deccan):
    """Years each Wikidata id is on the map (world + Deccan record), after the state-name fixes."""
    iv = collections.defaultdict(list)
    for reg in (world, deccan):
        for t, cells in reg.cells.items():
            if not cells:
                continue
            for n, q, s, e in reg.get(t):
                if q and not n.startswith("("):
                    iv[q].append((s, e))
    out = {}
    for q, lst in iv.items():
        lst.sort()
        m = []
        for s_, e_ in lst:
            if m and s_ <= m[-1][1] + 1:
                m[-1][1] = max(m[-1][1], e_)
            else:
                m.append([s_, e_])
        out[q] = m
    return out


def fix_rulers(docs, world=None, deccan=None):
    sys.path.insert(0, WF)
    import fact_audit as FA
    wd = FA.Witness()
    facts = docs["facts"].lists["polities"]
    offices = jload(OFFICES)
    O, L, H = offices["offices"], offices["labels"], offices["holders"]
    names_on_map = set()
    for reg in (world, deccan):
        for t, cells in reg.cells.items():
            if cells:
                names_on_map.update(plain(n) for n, q, s, e in reg.get(t))
    years = map_years(world, deccan)
    have = {facts.get(i)["q"] for i in range(len(facts))}
    for q_, (n_, a_) in NEW_FACTS.items():
        if q_ not in have:
            facts.append({"q": q_, "n": n_, "a": a_, "head": [], "gov": []})
            note("facts", "R9 rows from Wikipedia", n_, "-", "a new state entry", "the lists had no entry for it")
    for q_, (src, n_, a_) in CLONE_FACTS.items():
        if q_ not in have:
            base = next((facts.get(j) for j in range(len(facts)) if facts.get(j)["q"] == src), None)
            if base:
                c_ = json.loads(json.dumps(base))
                c_.update({"q": q_, "n": n_, "a": a_})
                c_["head"] = [r for r in c_.get("head", []) if r[3] >= 1960]
                c_["gov"] = [r for r in c_.get("gov", []) if r[3] >= 1960]
                facts.append(c_)
                note("facts", "R9 rows from Wikipedia", n_, f"rulers listed under {base.get('n')}",
                     "its own entry", "the Mali Federation lasted only 1959–1960")
    for i in range(len(facts)):
        p = facts.get(i)
        q, sname = p["q"], p.get("n", "")
        heads = [list(r) for r in p.get("head", [])]
        govs = [list(r) for r in p.get("gov", [])]
        before = json.dumps([heads, govs], ensure_ascii=False)
        own = {plain(sname), plain(p.get("a") or "")}
        keep = []
        for r in heads:
            name, title, s_, e_ = r[0], r[1] or "", r[2], r[3]
            low = plain(name)
            why = None
            if CLAIMANT.search(name):
                why = "R2 a claimant is not a ruler"
            elif low in TITLE_ONLY:
                why = "R2 a title is not a name"
            elif name in NAMED_AFTER_RULER:
                why = None
            elif low in own or (low in names_on_map and len(low.split()) >= 1 and low not in ("", )
                                and (len(low.split()) >= 2 or re.search(r"(?i)kingdom|empire|republic", name))):
                why = "R2 a state is not a ruler"
            elif GROUP_DROP.match(name.strip()):
                why = "R2 a period or a family is not a ruler"
            elif (sname, name) in NOT_A_RULER:
                why = "R2 not a ruler at all"
            for st, nm, start, reason in DROP_ROWS:
                if sname == st and name == nm and (start is None or start == s_):
                    why = "R2 contradicted by Wikipedia: " + reason
            if why:
                note("facts", why.split(":")[0] if why.startswith("R2 contradicted") else why,
                     f"{sname}: {name} ({title}) {yr(s_)}–{yr(e_)}", "head of state", "removed", why)
                continue
            to_gov = None
            for st, nm, upto, reason in TO_GOV:
                if sname == st and name == nm and s_ <= upto:
                    to_gov = reason
            if to_gov is None and GOV_TITLE.search(title) and low != "vladimir lenin":
                to_gov = "a head of government (prime minister, chairman of ministers) is not the head of state"
            if to_gov is None and q in FIGUREHEADS_TO_GOV and FIGUREHEADS_TO_GOV[q].search(title):
                to_gov = "the emperor reigned in Kyoto; the shōgun ruled"
            if to_gov is None and q in COMMUNIST_PARTY_LEADERS and re.search(r"(?i)presidium|supreme soviet|"
                                                                             r"interstate", title):
                to_gov = "the party's General Secretary ruled the Soviet Union; the Presidium chair was a figurehead"
            if to_gov:
                govs.append(r)
                note("facts", "R1 heads of government moved out of 'ruled by'", f"{sname}: {name} ({title}) "
                     f"{yr(s_)}–{yr(e_)}", "head of state", "head of government", to_gov)
                continue
            keep.append(r)
        heads = keep
        if q in REPLACE_HEADS:
            a_, b_, rows_, reason_ = REPLACE_HEADS[q]
            gone_ = [r for r in heads if r[2] >= a_ and r[3] <= b_]
            heads = [r for r in heads if not (r[2] >= a_ and r[3] <= b_)] + [list(r) for r in rows_]
            note("facts", "R9 rows from Wikipedia", f"{sname} {a_}–{b_}", f"{len(gone_)} rows, e.g. "
                 + "; ".join(f"{r[0]} {r[2]}–{r[3]}" for r in gone_[:3]), f"{len(rows_)} rows: "
                 + "; ".join(f"{r[0]} {r[2]}–{r[3]}" for r in rows_[:4]) + " …", reason_)
        # R3 years Wikipedia gives otherwise
        for r in heads:
            for st, nm, start, ns, ne, reason in FIX_ROWS:
                if r[0] == nm and (start is None or r[2] == start) and (st is None or st == q):
                    ns = r[2] if ns is None else ns
                    if [r[2], r[3]] != [ns, ne] and not (start is None and r[3] <= ne):
                        note("facts", "R3 impossible years corrected", f"{sname}: {nm}", f"{yr(r[2])}–{yr(r[3])}",
                             f"{yr(ns)}–{yr(ne)}", reason)
                        r[2], r[3] = ns, ne
        # R4 a reign that goes on after the ruler died ends at the death (Wikidata lifetimes, as in the fact check)
        for r in heads:
            if r[3] - r[2] > 100:
                continue
            verdict, cand = wd.lifetime_check(r[0], r[2], r[3]) if wd.ok else (None, None)
            if verdict == "after-death" and cand and cand[3] is not None and r[2] <= cand[3] < r[3]:
                note("facts", "R4 reign ends when the ruler died", f"{sname}: {r[0]}", f"until {yr(r[3])}",
                     f"until {yr(cand[3])}", f"Wikidata {cand[0]}: died {yr(cand[3])}")
                r[3] = cand[3]
        # R6 names said aloud: no quoted nicknames, no dates or markup inside the name
        for r in heads + govs:
            n0 = r[0]
            n1 = re.sub(r'\s*["“][^"”]*["”]', "", n0)
            n1 = re.sub(r"\s*\(\s*(?:born|b\.|died|d\.|r\.|reigned|c\.)?\s*\d[^)]*\)", "", n1)
            n1 = re.sub(r"\[\[|\]\]|\{\{|\}\}|<[^>]*>|&[a-z]+;", "", n1).replace("|", " ")
            n1 = re.sub(r"\s{2,}", " ", n1).strip(" ,")
            if n1 and n1 != n0:
                note("facts", "R6 tidy names", f"{sname}: {n0}", n0, n1, "nicknames, dates and markup are not said")
                r[0] = n1
        # R7 the same person and title twice, overlapping: one row
        merged = []
        for r in sorted(heads, key=lambda x: (x[2], x[3])):
            m = next((x for x in merged if plain(x[0]) == plain(r[0]) and plain(x[1] or "") == plain(r[1] or "")
                      and min(x[3], r[3]) - max(x[2], r[2]) >= 1), None)
            if m:
                note("facts", "R7 listed twice", f"{sname}: {r[0]}", f"{yr(m[2])}–{yr(m[3])} and {yr(r[2])}–{yr(r[3])}",
                     f"{yr(min(m[2], r[2]))}–{yr(max(m[3], r[3]))}", "the same person and title")
                m[2], m[3] = min(m[2], r[2]), max(m[3], r[3])
            else:
                merged.append(r)
        heads = merged
        # R9 rows Wikipedia gives that the lists missed
        for st, nm, title, a, b, reason in MANUAL_HEADS:
            if st == q:
                old = next((r for r in heads if plain(r[0]) == plain(nm)), None)
                if old:
                    if [old[1], old[2], old[3]] != [title, a, b]:
                        note("facts", "R9 rows from Wikipedia", f"{sname}: {nm}", f"{old[1]} {yr(old[2])}–{yr(old[3])}",
                             f"{title} {yr(a)}–{yr(b)}", "Wikipedia: " + reason)
                        old[1], old[2], old[3] = title, a, b
                else:
                    heads.append([nm, title, a, b])
                    note("facts", "R9 rows from Wikipedia", f"{sname}: {nm}", "-", f"{title} {yr(a)}–{yr(b)}",
                         "Wikipedia: " + reason)
        # R5 and R8 from Wikidata's office holders: end the guessed reigns, fill the empty years
        terms = []
        for o in O.get(q, {}).get("head", []):
            held = H.get(o, [])
            last = max([h[2] for h in held] or [None]) if held else None
            for name, pq_, a, b, female in held:
                if b is None:
                    # an open term counts only for the office's latest holder (a stray statement must not win)
                    b = NOW if a >= 1990 and a == last else None
                if b is None or b < a or b - a > 80:
                    continue
                terms.append([name, short_title(L.get(o, ""), female), a, b])
        for r in heads:
            nxt = min([h[2] for h in heads if h[2] > r[2]] or [99999])
            if r[3] == r[2] + 25 and nxt > r[3]:
                t_ = next((t for t in terms if plain(t[0]) == plain(r[0]) and abs(t[2] - r[2]) <= 2), None)
                cand = wd.candidates(r[0], r[2], r[3]) if wd.ok else []
                death = min([c[3] for c in cand if c[3] is not None and r[2] <= c[3] < r[3]] or [None]) \
                    if cand else None
                end = t_[3] if t_ else death
                if end is not None and r[2] <= end < r[3]:
                    note("facts", "R5 guessed end years corrected", f"{sname}: {r[0]}", f"until {yr(r[3])} (a guess)",
                         f"until {yr(end)}", "Wikidata: end of the term" if t_ else "Wikidata: died")
                    r[3] = end
        on_map = years.get(q, [])
        if terms and on_map:
            covered = set()
            for r in heads:
                covered.update(range(max(r[2], -3500), min(r[3], NOW) + 1))
            # longest terms first, so a few months of an acting holder never hide the holder of that year
            for t_ in sorted(terms, key=lambda x: (-(x[3] - x[2]), x[2])):
                gap = [y for y in range(t_[2], min(t_[3], NOW) + 1) if y not in covered
                       and any(a <= y <= b for a, b in on_map)]
                if not gap:
                    continue
                if any(plain(h[0]) == plain(t_[0]) and h[2] <= t_[3] and h[3] >= t_[2] for h in heads):
                    continue
                heads.append(list(t_))
                covered.update(range(t_[2], t_[3] + 1))
                note("facts", "R8 empty years filled from Wikidata's office holders", f"{sname}: {t_[0]}", "nobody named",
                     f"{t_[1]} {yr(t_[2])}–{yr(t_[3])}", f"Wikidata: holder of the office ({len(gap)} empty years)")
        heads.sort(key=lambda x: (x[2], x[3]))
        mark_guessed_ends(sname, heads)
        mark_guessed_ends(sname, govs)
        if json.dumps([heads, govs], ensure_ascii=False) != before:
            np_ = dict(p)
            np_["head"] = heads
            np_["gov"] = govs
            facts.set(i, np_)


def mark_guessed_ends(sname, rows):
    """Step 26 (A5): a reign whose end the builder guessed (start + 25 years, because the source gave none) gets
    the estimate mark, a fifth value 1. The game never shows it as a source; the operator's /ee who and the checks
    count it. The same test as the fact check's 'end year guessed'."""
    rows.sort(key=lambda x: (x[2], x[3]))
    for k, r in enumerate(rows):
        nxt = min([h[2] for h in rows if h[2] > r[2]] or [99999])
        guessed = r[3] > NOW or (r[3] == r[2] + 25 and nxt > r[3])
        if guessed and len(r) < 5:
            r.append(1)
            STATS["A5 reigns marked estimated (end guessed)"] += 1
            note("facts", "A5 reigns marked estimated (end guessed)", f"{sname}: {r[0]}", f"{yr(r[2])}–{yr(r[3])}",
                 "the same years, marked estimated", "the builder's guess: start + 25 years")
        elif not guessed and len(r) >= 5:
            del r[4:]


# ====================================================================== L. languages and faiths

LANG_JUNK = re.compile(r"(?i)\bsign\b|gŭl|hangul|hanja|\bscript\b|alphabet|cyrillic|latin script|devanagari|"
                       r"^(over \d+|official|none at the federal level|none at the union level|regional/local|court|middle|"
                       r"various|cisleithania|transleithania|vernacular|languages of .*|other local|as well as .*|"
                       r"none|national|recognised|recognized|minority)$|\d")
LANG_SPLIT = {"SpanishPortuguese": ["Spanish", "Portuguese"], "Persian Hindavi": ["Persian", "Hindavi"],
              "German with Hessian dialects": ["German"], "Venetian officially": ["Venetian"],
              "French officially": ["French"], "Greek popularly": ["Greek"]}
REL_FIX = {"From 5th century: Hinduism–Buddhism": ["Hinduism", "Buddhism"], "From 16th century: Islam": ["Islam"],
           "Protestant majority": ["Protestantism"], "Religion: Buddhism": ["Buddhism"], "Shia IslamOther": ["Shia Islam"],
           "Statewide majority": [], "Majority in some territories": [], "Majority religion": [],
           "Dominant confession: Roman Catholic": [], "Elector: Roman Catholic until": [], "Lutheran until": [],
           "Other religions in South Asia": [], "Roman Catholic": ["Roman Catholicism"], "Lutheran": ["Lutheranism"],
           "Catholic": ["Catholicism"]}
REL_JUNK = re.compile(r"(?i)^from |\d|century|majority|minority|^state$|religions?:|^see |;|,")
INDIA = [8.0, 30.5, 72.5, 88.6]       # the Hindu-majority plains and the Deccan (not Punjab, Sindh or east Bengal)
# Faith by period and the people's faith (Wikipedia: English Reformation; Reformation in Denmark-Norway and Holstein;
# Swedish Reformation; Scottish Reformation; Christianization of Lithuania; Religion in the Mughal Empire;
# Hyderabad State (81% Hindu, 1941 census)).
FAITH_PERIODS = {
    "Q179876": [[927, 1533, "Roman Catholicism"], [1534, 1552, "Anglicanism"], [1553, 1558, "Roman Catholicism"],
                [1559, 1707, "Anglicanism"]],
    "Q230791": [[843, 1559, "Roman Catholicism"], [1560, 1707, "Presbyterianism (the Church of Scotland)"]],
    "Q34": [[-3000, 1099, "Norse paganism"], [1100, 1526, "Roman Catholicism"], [1527, NOW, "Lutheranism"]],
    "Q756617": [[-3000, 964, "Norse paganism"], [965, 1535, "Roman Catholicism"], [1536, NOW, "Lutheranism"]],
    "Q35": [[-3000, 964, "Norse paganism"], [965, 1535, "Roman Catholicism"], [1536, NOW, "Lutheranism"]],
    "Q20": [[-3000, 1029, "Norse paganism"], [1030, 1536, "Roman Catholicism"], [1537, NOW, "Lutheranism"]],
    "Q156199": [[1356, 1538, "Roman Catholicism"], [1539, 1806, "Lutheranism"]],
    "Q762943": [[900, 1572, "Roman Catholicism"], [1573, 1795, "Dutch Reformed"]],
    "Q49683": [[1236, 1386, "Lithuanian polytheism"], [1387, 1795, "Roman Catholicism"]],
    "Q216786": [[-3000, 1499, "Hinduism"], [1500, 1832, "Islam"]],
    "Q148499": [[1157, 1538, "Roman Catholicism"], [1539, 1806, "Lutheranism"]],
    "Q157367": [[1618, 1700, "Lutheranism"]],
}
REL_SET = {"Q156199": ["Lutheranism", "Roman Catholicism"], "Q27306": ["Protestantism", "Catholicism"]}
FOLK_NAMES = {"Mughal Empire", "Mamluk Dynasty", "Khalji Dynasty", "Tughlaq Dynasty", "Sayyid Dynasty", "Lodi Dynasty",
              "Bahmani Sultanate", "Bijapur Sultanate", "Golconda Sultanate", "Ahmadnagar Sultanate", "Bidar Sultanate",
              "Berar Sultanate", "Jaunpur Sultanate", "Sur Empire", "Gujarat Sultanate", "Malwa Sultanate",
              "Carnatic Sultanate", "Delhi Sultanate", "Hyderabad State", "Kingdom of Mysore", "Nawabs of Bengal",
              "Bengal Subah", "Oudh State", "Awadh"}
# Extra points for big languages whose one Glottolog point lies far from their main towns, so "people here speak"
# does not name a neighbour's language (Vienna is not Slovak, Delhi not Eastern Panjabi, Tallinn not Latvian).
LANG_POINTS = [("German", 48.21, 16.37), ("German", 47.37, 8.54), ("German", 52.52, 13.40), ("German", 53.55, 10.00),
               ("German", 50.94, 6.96), ("German", 47.07, 15.44), ("Hindi", 28.65, 77.23), ("Hindi", 26.85, 80.95),
               ("Hindi", 25.32, 83.01), ("Hindi", 25.61, 85.14), ("Hindi", 26.91, 75.79), ("Hindi", 27.18, 78.01),
               ("Hindi", 23.26, 77.41), ("Russian", 55.76, 37.62), ("Russian", 59.94, 30.31), ("Russian", 56.84, 60.61),
               ("Russian", 55.03, 82.92), ("Russian", 47.24, 39.71), ("Marathi", 18.52, 73.86), ("Marathi", 19.08, 72.88),
               ("Marathi", 21.15, 79.09), ("Bengali", 22.57, 88.36), ("Gujarati", 23.03, 72.58), ("Tamil", 13.08, 80.27),
               ("Kannada", 12.97, 77.59), ("Telugu", 17.39, 78.49), ("Telugu", 16.51, 80.65), ("Urdu", 24.86, 67.01),
               ("Urdu", 31.55, 74.34), ("South Azerbaijani", 38.08, 46.29), ("North Azerbaijani", 40.41, 49.87),
               ("Estonian", 59.44, 24.75)]
MAKE_MAJOR = {"Estonian", "North Azerbaijani", "South Azerbaijani", "Western Farsi", "Lithuanian", "Finnish",
              "Danish", "Norwegian Bokmål", "Swedish", "Dutch", "Modern Greek", "Bulgarian", "Serbian", "Croatian",
              "Slovenian", "Albanian", "Georgian", "Hebrew", "Mongolian", "Khmer", "Lao", "Nepali"}


def clean_list(items, junk, fixes, splits=None):
    out = []
    for x in items or []:
        if x in fixes:
            out += fixes[x]
        elif splits and x in splits:
            out += splits[x]
        elif junk.search(x):
            continue
        else:
            out.append(x)
    seen, res = set(), []
    for x in out:
        if x.lower() not in seen:
            seen.add(x.lower())
            res.append(x)
    return res


def survey_ok(rows):
    """Correlates of War rows that contradict the state's other surveys (the Soviet Union '75% Catholic' in 1970-1990,
    Indonesia '98% Catholic' in 2005) are dropped; the survey before them then answers. A row is dropped when it
    has a Catholic majority while another survey of the same state has Orthodox Christians as its largest Christian
    group, or a non-Christian faith above half the people."""
    def other_says_no(y0):
        for y, sh in rows:
            if y == y0:
                continue
            chris = [f for f, v in sorted(sh, key=lambda x: -x[1]) if "Christian" in f]
            if chris and chris[0] == "Orthodox Christianity":
                return True
            if any(v >= 50 and "Christian" not in f and f not in ("no religion", "other faiths") for f, v in sh):
                return True
        return False
    keep, gone = [], []
    for y, sh in rows:
        cat = sum(v for f, v in sh if f == "Catholic Christianity")
        if cat >= 50 and other_says_no(y):
            gone.append(y)
        else:
            keep.append([y, sh])
    return keep, gone


def fix_culture(docs):
    facts = docs["facts"].lists["polities"]
    for i in range(len(facts)):
        p = facts.get(i)
        q, sname = p["q"], p.get("n", "")
        np_ = dict(p)
        lang = clean_list(p.get("lang"), LANG_JUNK, {}, LANG_SPLIT)
        if q == "Q87791" or sname in ("Frisia Kingdom", "Kingdom of Frisia", "Frisia", "Frisians"):
            lang = ["Old Frisian" if x == "Dutch" else x for x in lang]
        if sname in ("Anurādhapura", "Anuradhapura Kingdom"):
            lang = ["Sinhalese Prakrit" if x == "Sinhala" else x for x in lang]
        rel = REL_SET.get(q) or clean_list(p.get("rel"), REL_JUNK, REL_FIX)
        if sname == "Frisians":
            rel = ["Germanic paganism"]
        if lang != (p.get("lang") or []) and p.get("lang") is not None:
            note("facts", "L1 not a spoken language", sname, "; ".join(p.get("lang") or []), "; ".join(lang),
                 "sign languages, scripts and leftover words are not what people speak")
            np_["lang"] = lang
        if rel != (p.get("rel") or []) and p.get("rel") is not None:
            note("facts", "L2 not a faith name", sname, "; ".join(p.get("rel") or []), "; ".join(rel),
                 "leftover words from the infobox")
            np_["rel"] = rel
        if q in FAITH_PERIODS:
            np_["relP"] = FAITH_PERIODS[q]
            note("facts", "L3 the faith of the year", sname, "; ".join(rel[:2]) or "-",
                 "; ".join(f"{yr(a)}–{yr(b)} {f}" for a, b, f in FAITH_PERIODS[q]), "the state changed its faith")
        if sname in FOLK_NAMES and (rel[:1] and "Islam" in rel[0]):
            np_["relFolk"] = {"faith": "Hinduism"} if sname == "Hyderabad State" else {"faith": "Hinduism", "box": INDIA}
            note("facts", "L4 the people's faith beside the court's", sname, f"The main faith here is {rel[0]}",
                 f"The court follows {rel[0]}; most people here follow Hinduism",
                 "Wikipedia: most subjects of the Indian sultanates and the Mughals were Hindus")
        if p.get("relY"):
            keep, gone = survey_ok(p["relY"])
            if gone:
                np_["relY"] = keep
                note("facts", "L5 faith surveys that contradict the rest", sname, ", ".join(map(str, gone)),
                     "dropped", "the survey before answers instead")
        if np_ != p:
            facts.set(i, np_)
    # people here speak ...
    ll = docs["languages"].lists["languages"]
    for i in range(len(ll)):
        row = ll.get(i)
        if row[0] in MAKE_MAJOR and not row[3]:
            ll.set(i, [row[0], row[1], row[2], 1])
            note("languages", "L6 national languages count as major", row[0], "minor", "major",
                 "the main language of a state: people there speak it")
    for name, la, lo in LANG_POINTS:
        ll.append([name, la, lo, 1])
        note("languages", "L7 more points for big languages", f"{name} at {la},{lo}", "-", "a point",
             "one Glottolog point lay far from this town, so a neighbour's language was named")


# ====================================================================== E. events (news lines)

QLABELS = f"{WF}/sources/step25_event_labels.json.gz"


def event_labels(qids):
    """English Wikidata labels for events the packs name only by their number (saved, so later runs are offline)."""
    have = jload(QLABELS) if os.path.exists(QLABELS) else {}
    want = sorted(q for q in qids if q not in have)
    if want:
        import fix_history_wd as W
        for i in range(0, len(want), 200):
            part = want[i:i + 200]
            for r in W.tsv("SELECT ?q ?l WHERE { VALUES ?q { " + " ".join("wd:" + q for q in part) + " } "
                           "?q rdfs:label ?l FILTER(LANG(?l)=\"en\") }"):
                have[W.q(r[0])] = W.lit(r[1])
            for q in part:
                have.setdefault(q, None)
        jsave(QLABELS, have)
    return have


def lead_year(name, bc):
    """The year a year-page line starts with: '1820: …', 'AD 8 – …', '546 BC – …' (not '613 civilians …')."""
    m = re.match(r"^(c\.\s*)?(\d{1,4})\s*(BC|BCE|AD|CE)?\s*(?::|\s[–—-]\s)", name)
    if m and not m.group(1):
        y = int(m.group(2))
        if m.group(3) in ("BC", "BCE") or (m.group(3) is None and bc):
            y = -y
        return y
    m = re.match(r"^AD\s(\d{1,4})\b", name)
    return int(m.group(1)) if m else None


def fix_events(docs):
    import fact_audit as FA
    evkeys = [k for k in docs if k.startswith("ev_")]
    qids = set()
    for k in evkeys:
        ev = docs[k].lists["events"]
        for i in range(len(ev)):
            n = ev.get(i).get("name") or ""
            if re.fullmatch(r"Q\d+", n):
                qids.add(n)
    labels = event_labels(qids)
    for k in evkeys:
        ev = docs[k].lists["events"]
        fname = os.path.basename(FILES[k])
        for i in range(len(ev)):
            e = ev.get(i)
            name0 = e.get("name") or ""
            name = name0
            s_, en = e.get("start", e.get("year")), e.get("end")
            why, rule = None, None
            if re.fullmatch(r"Q\d+", name):
                lab = labels.get(name)
                if lab and not re.fullmatch(r"Q\d+", lab):
                    name, rule, why = lab, "E3 events named only by a number get their name", "Wikidata label"
                else:
                    ev.delete(i)
                    note(fname, "E3 events with no name at all removed", name0, name0, "removed", "no English name")
                    continue
            if (k == "ev_deccan" and FA.OCR.search(name)) or re.match(r"^(?:and|or|but|which|who|whom|whose|with|to|by)\s",
                                                                       name) or re.search(r"\{\{|\}\}|\[\[|\]\]|<[a-zA-Z/]", name):
                ev.delete(i)
                note(fname, "E5 unreadable lines removed", name0[:120], name0[:120], "removed",
                     "scanning errors, markup or a sentence cut in half")
                continue
            n1 = re.sub(r"^(?:\d{1,2}(?::\d\d)?\s*(?:pm|am)?\s*[:–—-]\s+|(?:ca\.|c\.|approximate date|approx\.\s*date|"
                        r"approx\.|circa)\s*[–—-]\s*|\*\s*)", "", name)
            if "|" in n1:
                tail = n1.split("|")[-1].strip()
                n1 = tail if len(tail) >= 20 else n1.replace("|", " ")
            n1 = re.sub(r"\(\s*\)", "", n1)
            n1 = re.sub(r"\s*,\s*,", ",", n1)
            n1 = re.sub(r"[\s,;:–—-]+$", "", n1).strip()
            n1 = re.sub(r"\s{2,}", " ", n1)
            if n1 and n1[0].islower() and n1 != name:
                n1 = n1[0].upper() + n1[1:]
            if n1 != name and n1:
                if rule is None:
                    rule, why = "E4 broken text tidied", "a day number, a date note, a table bar or an empty bracket"
                name = n1
            # E1/E2 the year the text itself gives
            new_s = None
            if 0 < s_ < 32:
                for y, slack in FA.years_named(name, k == "ev_hazards"):
                    if y >= 100 and slack == 1:
                        new_s = y          # E1: "1290 Zhili earthquake" was dated AD 27, its day of the month
                    break
            if new_s is None and (en is None or en - s_ <= 2):
                y = lead_year(name, s_ < 0)
                if y is not None and y != s_ and abs(y - s_) <= 60:
                    new_s = y              # E2: "AD 8 – Ovid is banished" was told in AD 1
            ch = dict(e)
            if new_s is not None:
                span_ = (en - s_) if en is not None else 0
                r2 = ("E1 a day of the month was read as the year" if 0 < s_ < 32 and new_s >= 100
                      else "E2 dated by the year its own text gives")
                note(fname, r2, name[:120], f"{yr(s_)}", f"{yr(new_s)}", "the text names the year")
                ch["start"] = new_s
                if en is not None:
                    ch["end"] = new_s + max(span_, 1 if span_ else 0)
                if "year" in ch:
                    ch["year"] = new_s
            if name != name0:
                note(fname, rule, name0[:120], name0[:120], name[:120], why)
                ch["name"] = name
            if ch != e:
                ev.set(i, ch)


# ====================================================================== P. famous people, F. foundation files

DESC_JUNK = re.compile(r"(?i)ID=|peerage person|wikimedia|disambiguation|\bQ\d{3,}\b|family name|given name|"
                       r"\bsurname\b|category:|\btaxon\b|\bspecies\b|\bgenus\b|list of|https?://|^\W|^[),;:]")
NOT_A_NAME = re.compile(r"(?i)^(killed|died|born|murdered|executed|in the|the crash|crash of)\b")


def fix_people(docs):
    rows = docs["people"].lists["people"]
    for i in range(len(rows)):
        name, desc, b, d, q, lat, lon, rad = rows.get(i)
        item = f"{name} ({yr(b) if b is not None else '?'}–{yr(d) if d is not None else '?'})"
        why = None
        if b is not None and d is not None and d < b:
            why = "P1 died before being born"
        elif b is not None and d is not None and d - b > 110:
            why = "P1 impossible lifespan"
        elif (b is not None and b > NOW) or (d is not None and d > NOW):
            why = "P1 years in the future"
        elif NOT_A_NAME.match(name or "") or re.search(r"&[a-z]+;|&#\d+;|\[\[|\{\{|<", name or ""):
            why = "P2 not a person's name"
        if why:
            rows.delete(i)
            note("famous_people.json.gz", why, item, item, "removed", "a wrong lifetime is talked about for centuries"
                 if "lifespan" in why else "")
            continue
        if desc and DESC_JUNK.search(desc):
            rows.set(i, [name, "", b, d, q, lat, lon, rad])
            note("famous_people.json.gz", "P3 broken description dropped", name, desc[:100], "(no description)",
                 "it was said aloud after the name")


def fix_foundation(docs):
    vips = docs["vips"].lists[None]
    for i in range(len(vips)):
        v = vips.get(i)
        if v.get("vipId") == "chandragupta_ii" and v.get("birthYear") == 375:
            nv = dict(v)
            nv["birthYear"] = 345
            vips.set(i, nv)
            note("foundation_vips.json", "F1 a reign's first year used as the birth year", "Chandragupta II", "born 375",
                 "born about 345 (estimate)", "Wikipedia: king from about 375; no birth year is recorded")


# ====================================================================== the money table follows the new names

PURE_RENAMES = []      # (old names, new name): the same land under its right name, so its money rows still apply


def sync_money(docs):
    rows = docs["money"].lists["rows"]
    for i in range(len(rows)):
        r = rows.get(i)
        changed = False
        where = []
        for w in r.get("where", []):
            if "ruler" in w:
                names = w["ruler"] if isinstance(w["ruler"], list) else [w["ruler"]]
                add = []
                for olds, new in PURE_RENAMES:
                    if any(o in names for o in olds) and new not in names and new not in add:
                        add.append(new)
                if add:
                    w = dict(w)
                    w["ruler"] = names + add
                    changed = True
                    note("money_table.json", "M1 money rows follow the new state names", r.get("id"),
                         "; ".join(names)[:120], "+ " + "; ".join(add), "the same land under its right name")
            where.append(w)
        if changed:
            nr = dict(r)
            nr["where"] = where
            rows.set(i, nr)
    # M2 (step 26): the money of the lands that S8 names by their own state
    for i in range(len(rows)):
        r = rows.get(i)
        if r.get("id") == "de_mark_rulers" and "Allied-occupied Germany" not in r["where"][0]["ruler"]:
            nr = json.loads(json.dumps(r))
            nr["where"][0]["ruler"].append("Allied-occupied Germany")
            rows.set(i, nr)
            note("money_table.json", "M2 money of the lands S8 names", r["id"], "; ".join(r["where"][0]["ruler"]),
                 "+ Allied-occupied Germany", "the Reichsmark stayed until the currency reform of 20 June 1948")
        if r.get("id") == "pl_zloty_old" and r.get("to") == 1939:
            nr = dict(r)
            nr["to"] = 1945
            rows.set(i, nr)
            note("money_table.json", "M2 money of the lands S8 names", r["id"], "1924–1939", "1924–1945",
                 "occupied Poland paid in złoty (the Bank Emisyjny's notes, 1940–1945)")
    if not any(rows.get(i).get("id") == "de_dm_allied" for i in range(len(rows))):
        rows.append({"id": "de_dm_allied", "money": "deutsche_mark", "from": 1948, "to": 1949,
                     "where": [{"ruler": ["Allied-occupied Germany"], "box": [47.2, 5.8, 55.1, 11.0]}],
                     "priority": 45, "note": "Step 26: the western zones' Deutsche Mark from 20 June 1948 (the Soviet "
                                             "zone's own mark comes from the ddr_box row)."})
        note("money_table.json", "M2 money of the lands S8 names", "de_dm_allied", "-",
             "Deutsche Mark 1948–1949 in the western zones", "the currency reform of 20 June 1948")


if __name__ == "__main__":
    main(sys.argv[1:])
