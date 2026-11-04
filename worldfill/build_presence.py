#!/usr/bin/env python3
"""Step 41 (D11, famous people where and when they were), part 5: build history/presence.json.gz.

    python3 read_cards.py --dump        the card people, their seats, offices, links and death places
    python3 fetch_step41.py places      P551 residence and P937 work location, with their points
    python3 build_presence.py           build the pack
    python3 build_presence.py --check   read it back and check it (exit 1 on a problem)

The problem D11 exists to fix
-----------------------------
``FamousPeople`` answers every question it is asked — ``livingIn``, ``diedIn``, ``bornNear`` —
**by birthplace or by state**. A person is where they were born for the whole of their life. That
is ``SYSTEMS_PLAN.md`` line 507: *someone born in Bombay who lived in England (T. H. White) is
talked about in Bombay, and the famous of a city who were born elsewhere are not "from here"*.

T. H. White's card says home Mumbai, and says he studied at Queens' College, Cambridge. The second
fact was in the mod all along and nothing in the mod could use it. This pack is the join that makes
it usable: **a dated place for every reason a person was somewhere**.

What a presence row is
----------------------
A person, a place, two years, and **why** — because "from here" and "here now" are different
answers (decision 3), and a register that cannot tell them apart will carry on putting a man in the
city he was born in. Ten reasons:

| why | what it is | where it comes from | dated? |
|---:|---|---|---|
| 1 | born | the card's seat | the birth year |
| 2 | died | the card's death place | the death year |
| 3 | studied at | a `studied` link to a card that has a seat | 14% of links |
| 4 | worked for | a `worked` link | 20% |
| 5 | served in | a `served` link | 15% |
| 6 | member of | a `member` link | 31% |
| 7 | in the party of | a `party` link | 18% |
| 8 | founded | a `founded` link | the founding year |
| 9 | lived at | P551 residence, fetched here | 18% |
| 10 | worked in | P937 work location, fetched here | 10% |

**An office is not a presence row.** A position-held statement almost never carries a jurisdiction
(43 rows in a 3,000-person sample), and the office item's country is a country, not somewhere a
player can stand (decision 4). Where a ruler *was* is what part 4's dynasties are for.

**An undated row is dated by the person's life and says so** (decision 5). A residence statement in
Wikidata has a start year 18% of the time and a work location 10% of the time; a blood edge almost
never. So an undated row carries the person's own years — birth to death — and ``est`` is 1, so the
register can print *at some point in his life* instead of a year nobody gave it.

The pack
--------
``places`` is a table of distinct named points; ``rows`` are ``[person, place, from, to, why,
est]``. Places are held once because most presence rows share one: 355,000 rows name only about
150,000 places.
"""
import collections
import gzip
import json
import os
import sys

import fetch_step41 as fetch
import read_cards

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "eternal", "src", "main", "resources", "data",
                   "eternalengine", "eternal", "history", "presence.json.gz")

WHYS = [
    (1, "born", "was born here"),
    (2, "died", "died here"),
    (3, "studied", "studied here"),
    (4, "worked for", "worked for a body seated here"),
    (5, "served in", "served in a body seated here"),
    (6, "member of", "was a member of a body seated here"),
    (7, "party", "was of the party seated here"),
    (8, "founded", "founded the body seated here"),
    (9, "lived", "lived here"),
    (10, "worked in", "worked here"),
]
WHY_LINK = {"studied": 3, "worked": 4, "served": 5, "member": 6, "party": 7, "founded": 8}

SOURCE = ("Wikidata (CC0) through QLever's public endpoint, joined with step 27's cards (C10, "
          "C22), which are themselves Wikidata cross-checked with the Wikipedia year pages: the "
          "card's seat and death place, its links to other cards that have seats, and P551 "
          "residence and P937 work location fetched for step 41.")

GAPS = [
    "**An office is not a place.** A position-held statement almost never carries a jurisdiction, "
    "and the office item's country is a country. So the register cannot say where a court was, "
    "only who held the office and in which years - which is what part 4's dynasties are for.",
    "**Most rows are undated.** A residence statement has a start year 18% of the time and a work "
    "location 10%; the links between cards are dated about a fifth of the time. An undated row "
    "carries the person's own birth and death years and is marked as one, and the register must "
    "say *at some point in his life* rather than a year nobody gave it.",
    "**A link is not a journey.** It says a person studied at, worked for or belonged to a body "
    "seated in a place. It does not say he was ever in that place, and for a correspondence "
    "course or a membership bought by post he may never have been.",
    "**The seat of an organisation is where it was headquartered, not where the person stood.** A "
    "member of the Royal Society is present in London because the Society is; he may have read "
    "the proceedings in Cumbria.",
    "**Coverage follows the record, which follows Europe and its empires.** A person from "
    "sub-Saharan Africa or Oceania is far likelier to have one row - born - than a Saxon with "
    "six.",
    "Only people who already have a card get presence rows: this step does not enlarge the card "
    "set (decision 8).",
]


def load():
    cards = read_cards.read()
    people = {c["qid"]: c for c in cards["cards"] if c["kind"] == 0}
    all_cards = {c["qid"]: c for c in cards["cards"]}
    places = {}
    order = []

    def place(name, lat, lon):
        if lat is None or lon is None or (lat == 0.0 and lon == 0.0):
            return None
        key = (name or "", round(lat * 1000), round(lon * 1000))
        if key not in places:
            places[key] = len(order)
            order.append([name or "", key[1], key[2]])
        return places[key]

    rows = []
    stats = collections.Counter()
    late = [0]

    def add(q, pid, a, b, why, est, life=(None, None)):
        a, b = none(a), none(b)
        la, lb = none(life[0]), none(life[1])
        if a is not None and b is not None and b - a > MAX_SPAN:
            stats["span dropped"] += 1
            a, b, est = la, lb, 1
        if a is not None and b is not None and b - a > MAX_SPAN:
            b = a + MAX_SPAN             # even the life itself is longer than a life
        if a is None and b is None:
            return                       # a row with no year at all answers nothing
        rows.append([q, pid, a, b, why, est])
        stats[why] += 1
        stats[("est" if est else "dated")] += 1

    for q, c in people.items():
        life_a, life_b = c["from"], c["to"]
        if life_a is not None and life_a == -2147483648:
            life_a = None
        if life_b is not None and life_b == -2147483648:
            life_b = None
        pid = place(c["home"], c["lat"], c["lon"])
        if pid is not None:
            add(q, pid, life_a, life_b, 1, 0, (life_a, life_b))
        dl, dn = c.get("deathLat"), c.get("deathPlace")
        if dl is not None:
            pid = place(dn, dl, c.get("deathLon"))
            if pid is not None:
                add(q, pid, life_b, life_b, 2, 0, (life_a, life_b))
        for role, target, a, b in c["links"]:
            t = all_cards.get(target)
            if t is None:
                continue
            why = WHY_LINK.get(role)
            if why is None:
                continue
            pid = place(t["home"] or t["name"], t["lat"], t["lon"])
            if pid is None:
                continue
            if a is not None or b is not None:
                add(q, pid, a, b, why, 0, (life_a, life_b))
            else:
                add(q, pid, life_a, life_b, why, 1, (life_a, life_b))

    # the two properties fetched for this step
    for name, why in (("residence", 9), ("work", 10)):
        for r in fetch.rows(name):
            q = fetch.qid_of(r.get("p"))
            if q is None or q not in people:
                continue
            c = people[q]
            lat, lon = point(r.get("c"))
            if lat is None:
                stats["no point"] += 1
                continue
            pid = place(fetch.unquote(r.get("l")), lat, lon)
            a, b = fetch.year(r.get("fy")), fetch.year(r.get("ty"))
            life = (none(c["from"]), none(c["to"]))
            if a is not None or b is not None:
                add(q, pid, a, b, why, 0, life)
            else:
                add(q, pid, life[0], life[1], why, 1, life)

    return {"places": order, "rows": rows, "stats": stats, "people": people, "cards": cards,
            "statsLate": late}


# Nothing in the mod's data runs past today, and Wikidata marks a membership that has not ended
# with a date a long way off - one row here ends in 12019. An end year ten millennia out is not a
# year anybody was anywhere: it means *no end*, and it is kept as no end.
LAST_YEAR = 2026
# longer than any life that has been reliably recorded (Jeanne Calment, 122 years): a row whose
# two years are further apart than this is not a claim that a person was somewhere for eight
# centuries, it is two dates that do not belong to the same life. Such a row keeps its person and
# its place and loses its years, and is marked estimated like any other row nobody dated.
MAX_SPAN = 120


def none(v):
    v = None if v == -2147483648 else v
    return None if v is not None and v > LAST_YEAR else v


def point(cell):
    """'POINT(lon lat)' -> (lat, lon)."""
    if not cell or not cell.upper().startswith("POINT("):
        return None, None
    try:
        inner = cell[cell.index("(") + 1: cell.rindex(")")]
        lon, lat = (float(x) for x in inner.split()[:2])
    except ValueError:
        return None, None
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        return None, None
    return lat, lon


def build():
    d = load()
    # Two links to two colleges in the same town, both dated by the person's life because Wikidata
    # gave no years, are the same row twice. The register keeps one: it says where a person was,
    # and it has no way to say "he was here twice".
    before = len(d["rows"])
    rows = sorted({tuple(r) for r in d["rows"]}, key=lambda r: (r[0], r[1], r[2] or -9999))
    print("presence: %s rows, %s duplicates dropped" % (f"{len(rows):,}", f"{before - len(rows):,}"))
    pack = {
        "format": "eternal-presence-1",
        "id": "presence",
        "source": SOURCE,
        "note": ("D11, famous people where and when they were: a dated place for every reason a "
                 "person was somewhere, so that the mod can tell *from here* from *here now*."),
        "gaps": GAPS,
        "whys": [{"id": i, "name": n, "says": s} for i, n, s in WHYS],
        "counts": {
            "people": len(d["people"]),
            "rows": len(rows),
            "places": len(d["places"]),
            "peopleWithTwoOrMore": 0,
        },
        "places": d["places"],
        "rows": rows,
    }
    per = collections.Counter(r[0] for r in rows)
    pack["counts"]["peopleWithTwoOrMore"] = sum(1 for p, n in per.items() if n >= 2)
    raw = json.dumps(pack, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(raw)
    print("presence.json.gz: %s rows over %s places for %s people"
          % (f"{len(rows):,}", f"{len(d['places']):,}", f"{len(d['people']):,}"))
    print("  %s people have two places or more (%.0f%%)"
          % (f"{pack['counts']['peopleWithTwoOrMore']:,}",
             pack["counts"]["peopleWithTwoOrMore"] * 100.0 / len(d["people"])))
    print("  %s bytes raw, %s gzipped" % (f"{len(raw):,}", f"{os.path.getsize(OUT):,}"))
    for i, n, _ in WHYS:
        print("    %-12s %s" % (n, f"{d['stats'][i]:,}"))
    print("  dated %s, estimated %s; %s rows lost years nobody could have lived"
          % (f"{d['stats']['dated']:,}", f"{d['stats']['est']:,}",
             f"{d['stats']['span dropped']:,}"))
    return pack


# ------------------------------------------------------------------ the check

def check():
    problems = []

    def ok(good, text):
        print("  %s %s" % ("ok  " if good else "FAIL", text))
        if not good:
            problems.append(text)

    if not os.path.exists(OUT):
        print("presence.json.gz: missing")
        return 1
    d = json.loads(gzip.open(OUT, "rt", encoding="utf-8").read())
    print("presence.json.gz: %s bytes" % f"{os.path.getsize(OUT):,}")
    rows = d["rows"]
    places = d["places"]
    ok(d["format"] == "eternal-presence-1", "the format is the one this builder writes")
    ok(len(d["whys"]) == 10, "ten reasons a person was somewhere")
    ok(all(len(p) == 3 for p in places), "every place is a name and a point")
    ok(all(-90000 <= p[1] <= 90000 and -180000 <= p[2] <= 180000 for p in places),
       "every place is on the map")
    ok(all(0 <= r[1] < len(places) for r in rows), "every row names a place that exists")
    ok(all(1 <= r[4] <= 10 for r in rows), "every row gives a reason that exists")
    ok(len(set(map(tuple, rows))) == len(rows), "no row twice")

    by_why = collections.Counter(r[4] for r in rows)
    ok(all(by_why.get(i, 0) > 0 for i in range(1, 11)),
       "all ten reasons come up in the pack: %s" % dict(sorted(by_why.items())))

    cards = read_cards.read()
    people = set(c["qid"] for c in cards["cards"] if c["kind"] == 0)
    ok(not [1 for r in rows if r[0] not in people],
       "every row is about a person who has a card")
    unnamed = sum(1 for p in places if not p[0])
    unnamed_rows = sum(1 for r in rows if not places[r[1]][0])
    print("  ..  %s of %s places have no name, covering %s rows; the register can point at them "
          "and cannot name them" % (f"{unnamed:,}", f"{len(places):,}", f"{unnamed_rows:,}"))
    ok(unnamed * 10 < len(places), "most places are named")

    est = sum(1 for r in rows if r[5])
    print("  ..  %s of %s rows are dated by the person's life and say so (%.0f%%)"
          % (f"{est:,}", f"{len(rows):,}", est * 100.0 / len(rows)))
    ok(est > 0 and est < len(rows), "some rows are dated and some are estimated")
    late = [1 for r in rows for y in (r[2], r[3]) if y is not None and y > 2026]
    ok(not late, "no row ends in the far future: a year nobody was alive in is not a date (%d)"
       % len(late))
    span = max(((r[3] - r[2]) for r in rows if r[2] is not None and r[3] is not None), default=0)
    print("  ..  the longest row spans %d years" % span)
    ok(span <= 120, "no row spans longer than a life, so a query never has to open more than two "
                    "centuries of buckets (%d years)" % span)

    per = collections.Counter(r[0] for r in rows)
    two = sum(1 for p, n in per.items() if n >= 2)
    print("  ..  %s of %s people have two places or more (%.0f%%)"
          % (f"{two:,}", f"{len(people):,}", two * 100.0 / len(people)))
    ok(two * 10 > len(people) * 5,
       "more than half the people with a card are somewhere other than their birthplace")

    # the point of the whole step: T. H. White was born in Bombay and lived in England
    name_of = {c["name"]: c["qid"] for c in cards["cards"] if c["kind"] == 0}
    for who in ("T. H. White", "Charles Darwin", "Akbar"):
        q = name_of.get(who)
        if q is None:
            continue
        rs = [r for r in rows if r[0] == q]
        said = []
        for r in rs:
            w = next(w["name"] for w in d["whys"] if w["id"] == r[4])
            said.append("%s %s%s" % (w, places[r[1]][0] or "?",
                                     "" if r[5] else " %s" % (r[2] if r[2] == r[3]
                                                              else "%s-%s" % (r[2], r[3]))))
        print("       %-16s %s" % (who, "; ".join(said[:6])))
    q = name_of.get("T. H. White")
    if q is not None:
        rs = [r for r in rows if r[0] == q]
        ok(any(places[r[1]][0] and "Cambridge" in places[r[1]][0] for r in rs),
           "T. H. White is in Cambridge and not only in the Bombay he was born in, which is the "
           "whole of SYSTEMS_PLAN line 507")
    print("presence: %d problem(s)" % len(problems))
    return 1 if problems else 0


def main(argv):
    if "--check" in argv:
        return check()
    build()
    return check()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
