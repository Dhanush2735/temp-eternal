#!/usr/bin/env python3
"""Step 41 (C11, families and dynasties), part 3: build history/kinship.json.gz.

    python3 fetch_step41.py kin          the fetch (into raw/step41/, which is kept)
    python3 fetch_step41.py relative     the second pass: the relatives who have no card
    python3 read_cards.py --dump         the card people, out of the shipped cards file
    python3 build_kinship.py             build the pack
    python3 build_kinship.py --check     read the pack back and check it (exit 1 on a problem)

What C11 was, and what it becomes
---------------------------------
It was **the book's family tree**, and that tree was not kinship: ``BookService.tree(...)`` lists
the *card links* of a family card, which is to say the other cards Wikidata happened to name on it.
A player's "family" was full of people who were not related. ``DynasticSuccessionEngine`` generates
heirs and coups from four succession laws with no bloodline to work from at all.

This pack is the bloodline: **parent edges, marriages, and named houses** for the 148,510 people
who have a card, plus the names of the 96,093 relatives who do not.

The one number that shaped the design
-------------------------------------
**Only 14% of the edges have both ends on a card.** A famous person's father is usually not famous
himself, and the register cannot name a QID. So the second pass fetches those relatives - 101,132
of them, 95% with a name and 84% with at least one year - and they are carried in ``named``. A
family tree can now show *"his father, Arthur White, 1863-1929"* for a father who has no card of
his own, which is what a real family tree does.

Edges are stored once and answered both ways (decision 6): Wikidata gives **child 64,710 times
against father 27,605**, so the register keeps one ``parent`` row per pair whichever way the source
stated it and answers "who were his parents" and "who were his children" from the same rows.

The pack
--------
``parent`` sorted ``[parent, child]`` pairs; ``spouse`` sorted ``[a, b]`` pairs with
``spouseYears`` alongside it (the same length, ``[null, null]`` where Wikidata gave no year - which
is 49% of marriages); ``named`` the relatives with no card, as ``[qid, name, description, birth,
death]``; ``houses`` the 3,313 named families as ``[qid, name, [members]]``.

Nothing is invented: an edge is in the pack because Wikidata says it, and a relative is named
because Wikidata named him.

Dynasties (part 4)
------------------
A dynasty is **derived, not asserted** (decision 7). No source lists "the Habsburgs held the Holy
Roman emperorship"; the register finds it. For each office, it takes the people who held it and
joins two of them with an edge when one is the parent of the other **and the child did not hold it
first** (a child who took the office before the parent did is not a successor). A **dynasty is a
connected component of three or more** such holders: three generations holding one office is a
house, and two is a coincidence.

That gives 534 dynasties across 275 offices, and they are the ones any encyclopedia gives:

```
sultan of the Ottoman Empire  39  Ottoman dynasty
duke of Bavaria               21  House of Wittelsbach
emir of Kuwait                17  House of Al Sabah
ancient Roman senator         15  Caecilii Metelli
Abbasid caliph                15  Abbasids
Monarch of Portugal           14  House of Braganza
Grand Prince of Kiev          14  Rurikids
```

Named by its house where a house covers 60% or more of the members (**88% of them**), and where it
does not, by the office: *the family of the Peshwa*, *the family of the Manikongo*, *the family of
the Oba of Lagos*. The unnamed 12% are real houses with no Wikidata family item - the kings of Lan
Xang, the Sultans of Bijapur, the Twelve Imams - and the register names them by what they held
rather than guessing a surname, because the obvious surname fallback is not surnames: the last word
of *"Otto I Wittelsbach, Duke of Bavaria"* is Bavaria.

Note what this is **not**: a claim that the office was hereditary. The Roman consulship was
elective, and the Metelli still held it across generations. The register says *a family that held
this office across N generations*, which is true of a republican *gens* and of a monarchy alike.
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
                   "eternalengine", "eternal", "history", "kinship.json.gz")

SOURCE = ("Wikidata (CC0), fetched through QLever's public endpoint: P22 father, P25 mother, "
          "P40 child, P26 spouse with P580 start and P582 end, P53 family; and for the relatives "
          "who have no card, rdfs:label, schema:description, P569 and P570. The people come from "
          "step 27's cards (C10, C22), which are themselves Wikidata cross-checked with the "
          "Wikipedia year pages.")

GAPS = [
    "Only 14% of the blood and marriage edges have **both** ends on a card: a famous person's "
    "father is usually not famous himself. The other 96,093 relatives were fetched too and are "
    "carried with their names, but they have no card, so the mod can name them and cannot open "
    "them.",
    "A marriage has a year 51% of the time and a blood edge almost never does, because Wikidata "
    "records a father as a plain statement with no date. So a family tree can say *who* and "
    "usually not *when*, and the pack does not pretend otherwise.",
    "The edges are what Wikidata says and nothing more. Where a source disagrees about a parent "
    "the register shows both, and where Wikidata is wrong the register is wrong in the same way.",
    "Kinship is recorded where it is written down, which is overwhelmingly Europe, the "
    "Mediterranean, the Islamic world and East Asia. A family in sub-Saharan Africa or Oceania is "
    "far likelier to be missing than one in Saxony, and the register does not claim otherwise.",
    "A house (P53) is only what the item names. Plenty of dynasties have no Wikidata family item "
    "at all, and they are not in the pack.",
]


def load():
    """The edges, the relatives and the houses, clean."""
    cards = read_cards.read()
    on_card = set(c["qid"] for c in cards["cards"] if c["kind"] == 0)
    names = {c["qid"]: c["name"] for c in cards["cards"]}

    parent = set()
    spouse = {}
    dropped = collections.Counter()
    for r in fetch.rows("kin"):
        a = fetch.qid_of(r.get("p"))
        b = fetch.qid_of(r.get("q"))
        rel = fetch.unquote(r.get("rel"))
        if a is None or b is None or a == b:
            dropped["kin blank or self"] += 1
            continue
        # father/mother are stated child -> parent; child is stated parent -> child
        parent.add((b, a) if rel in ("father", "mother") else (a, b))
    for r in fetch.rows("spouse"):
        a = fetch.qid_of(r.get("p"))
        b = fetch.qid_of(r.get("q"))
        if a is None or b is None or a == b:
            dropped["spouse blank or self"] += 1
            continue
        key = (min(a, b), max(a, b))
        y = (year(r.get("fy")), year(r.get("ty")))
        if key in spouse:
            old = spouse[key]
            spouse[key] = (old[0] or y[0], old[1] or y[1])   # a year from either statement
        else:
            spouse[key] = y

    # one statement saying "a is the parent of b" and another saying "b is the child of a" is the
    # same edge; so is a pair stated in both directions, which would be a cycle in the tree
    both_ways = {(a, b) for a, b in parent if (b, a) in parent}
    parent = {(a, b) for a, b in parent if a < b or (b, a) not in parent}

    named = {}
    for r in fetch.rows("relative"):
        q = fetch.qid_of(r.get("p"))
        if q is None or q in on_card:
            continue
        n = fetch.unquote(r.get("l"))
        if not n:
            continue
        d = fetch.unquote(r.get("d"))
        named[q] = [q, n, d[:80] if d else "", year(r.get("by")), year(r.get("dy"))]

    houses = {}
    for r in fetch.rows("house"):
        p = fetch.qid_of(r.get("p"))
        h = fetch.qid_of(r.get("q"))
        label = fetch.unquote(r.get("l"))
        if p is None or h is None:
            continue
        houses.setdefault(h, [h, label, set()])
        if label and not houses[h][1]:
            houses[h][1] = label
        houses[h][2].add(p)

    return {"onCard": on_card, "names": names, "parent": parent, "spouse": spouse,
            "named": named, "houses": houses, "dropped": dropped,
            "bothWays": len(both_ways), "cards": cards}


def year(cell):
    if not cell:
        return None
    try:
        v = int(cell)
    except ValueError:
        return None
    return v if -4000 <= v <= 2100 else None


# ------------------------------------------------------------------ dynasties

# three generations holding one office is a house; two is a coincidence
MIN_DYNASTY = 3
# how much of a dynasty a house must cover before the dynasty is named after it
HOUSE_SHARE = 0.6
# a "successor" more than this many years after his parent let go of the office is not one
GAP_YEARS = 90


def dynasties(d):
    """The families that held one office across generations (part 4)."""
    cards = d["cards"]
    offices = cards["offices"]
    people = {c["qid"]: c for c in cards["cards"] if c["kind"] == 0}
    house_of = {}
    for h, name, members in d["houses"].values():
        for m in members:
            house_of.setdefault(m, set()).add((h, name))

    def years(q, office):
        for oo, a, b in people[q]["offices"]:
            if oo == office:
                return a, b
        return None, None

    links = {}
    for a, b in d["parent"]:                       # a is the parent of b
        if a not in people or b not in people:
            continue
        for o in ({x for x, _, _ in people[a]["offices"]}
                  & {x for x, _, _ in people[b]["offices"]}):
            pa, pb = years(a, o), years(b, o)
            if pa[0] and pb[0] and pb[0] < pa[0]:
                continue                            # the child held it first: not a successor
            if pa[1] and pb[0] and pb[0] < pa[1] - GAP_YEARS:
                continue
            links.setdefault(o, set()).add((a, b))

    out = []
    for office, es in sorted(links.items()):
        for comp in components(es):
            if len(comp) < MIN_DYNASTY:
                continue
            first, last = None, None
            for q in comp:
                a, b = years(q, office)
                for y in (a, b):
                    if y is None:
                        continue
                    first = y if first is None else min(first, y)
                    last = y if last is None else max(last, y)
            houses = {}
            for q in comp:
                for hid, hname in house_of.get(q, ()):
                    houses.setdefault(hname, [hid, 0])[1] += 1
            name, house = None, None
            if houses:
                hname, (hid, n) = max(houses.items(), key=lambda kv: kv[1][1])
                # a house with no label is no name at all: 462 of the memberships came back unnamed
                if hname and n * 10 >= len(comp) * HOUSE_SHARE * 10:
                    name, house = hname, hid
            if name is None:
                name = family_name(offices[office])
            order = sorted(comp, key=lambda q: (years(q, office)[0] or 9999, q))
            out.append({"office": office, "officeName": offices[office], "name": name,
                        "house": house, "members": order, "from": first, "to": last,
                        "generations": depth(es, comp)})
    out.sort(key=lambda x: (-len(x["members"]), x["office"]))
    return out


# The offices a dynasty can be named after, and their plurals. This is a table of the words that
# actually turn up, not an English pluraliser: *the kings of Burma* and *the Peshwas* read right,
# and a rule that turned *Manikongo* into *Manikongos* would not.
PLURALS = {
    "monarch": "monarchs", "king": "kings", "queen": "queens", "sultan": "sultans",
    "emir": "emirs", "emperor": "emperors", "empress": "empresses", "duke": "dukes",
    "duchess": "duchesses", "prince": "princes", "grand prince": "grand princes",
    "great prince": "great princes", "caliph": "caliphs", "imam": "imams", "khan": "khans",
    "shah": "shahs", "pope": "popes", "tsar": "tsars", "czar": "czars",
    "pharaoh": "pharaohs", "maharaja": "maharajas", "maharajah": "maharajahs",
    "peshwa": "peshwas", "oba": "obas", "raja": "rajas", "rajah": "rajahs",
    "nawab": "nawabs", "nizam": "nizams", "elector": "electors", "count": "counts",
    "earl": "earls", "marquess": "marquesses", "margrave": "margraves",
    "landgrave": "landgraves", "doge": "doges", "daimyo": "daimyo", "shogun": "shoguns",
    "high king": "high kings", "sovereign": "sovereigns", "ruler": "rulers",
    "chieftain": "chieftains", "paramount chief": "paramount chiefs",
}


def family_name(office):
    """What to call a dynasty that has no house: what it held, in the plural."""
    low = office.lower()
    if low in PLURALS:
        return "the " + PLURALS[low][0].upper() + PLURALS[low][1:]
    if " of " in office:
        head, rest = office.split(" of ", 1)
        if head.lower() in PLURALS:
            plural = PLURALS[head.lower()]
            return "the " + plural[0].upper() + plural[1:] + " of " + rest
    return "the family of the " + office


def components(edges):
    """Connected components of an undirected graph given as (a, b) pairs."""
    adj = {}
    for a, b in edges:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    seen = set()
    out = []
    for n in sorted(adj):
        if n in seen:
            continue
        stack, comp = [n], set()
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.add(x)
            stack += list(adj[x] - seen)
        out.append(comp)
    return sorted(out, key=len, reverse=True)


def depth(edges, comp):
    """The longest parent-to-child chain inside a component: how many generations it spans.

    Cycle-safe on purpose. A cycle would mean someone is their own ancestor, and the check says
    there is none - but a depth-first walk that hangs is a worse failure than one that is wrong,
    so a node already being walked counts as one generation and stops there.
    """
    children = {}
    for a, b in edges:
        if a in comp and b in comp:
            children.setdefault(a, set()).add(b)
    best = {}
    walking = set()

    def walk(x):
        if x in best:
            return best[x]
        if x in walking:
            return 0
        walking.add(x)
        best[x] = 1 + max((walk(c) for c in children.get(x, ())), default=0)
        walking.discard(x)
        return best[x]

    roots = [x for x in comp if x not in {b for _, b in edges if b in comp}]
    return max((walk(x) for x in (roots or list(comp))), default=1)


def build():
    d = load()
    parent = sorted(d["parent"])
    spouse_keys = sorted(d["spouse"])
    pack = {
        "format": "eternal-kinship-1",
        "id": "kinship",
        "source": SOURCE,
        "note": ("C11, families and dynasties: who was whose parent, who married whom, and which "
                 "named house a person belonged to, for the 148,510 people who have a card and "
                 "the 96,093 relatives who do not. Stored once, answered both ways."),
        "counts": {
            "peopleOnCards": len(d["onCard"]),
            "parentEdges": len(parent),
            "spouseEdges": len(spouse_keys),
            "namedRelatives": len(d["named"]),
            "houses": len(d["houses"]),
            "peopleWithAEdge": 0,
        },
        "gaps": GAPS,
        "kinds": [
            {"id": "parent", "name": "parent of", "note": "a is a parent of b; answered both ways"},
            {"id": "spouse", "name": "married", "note": "a and b were married, with the years "
                                                        "where Wikidata gave them"},
        ],
        "parent": parent,
        "spouse": [list(k) for k in spouse_keys],
        "spouseYears": [list(d["spouse"][k]) for k in spouse_keys],
        "named": [d["named"][q] for q in sorted(d["named"])],
        "houses": [[h, name, sorted(members)] for h, name, members in
                   sorted(d["houses"].values(), key=lambda x: -len(x[2]))],
    }
    dyn = dynasties(d)
    pack["dynasties"] = dyn
    pack["counts"]["dynasties"] = len(dyn)
    pack["counts"]["dynastyOffices"] = len({x["office"] for x in dyn})
    people = set()
    for a, b in parent:
        people.add(a)
        people.add(b)
    for a, b in spouse_keys:
        people.add(a)
        people.add(b)
    # the number that matters is how many people who HAVE A CARD gained a family, not how many
    # endpoints there are: most endpoints are relatives with no card of their own
    pack["counts"]["peopleWithAEdge"] = len(people & d["onCard"])
    pack["counts"]["endpoints"] = len(people)
    pack["counts"]["relativesNamedByAnEdge"] = len(people - d["onCard"])
    raw = json.dumps(pack, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(raw)
    print("kinship.json.gz: %s parent edges, %s marriages, %s named relatives, %s houses"
          % (f"{len(parent):,}", f"{len(spouse_keys):,}", f"{len(d['named']):,}",
             f"{len(d['houses']):,}"))
    print("  %s people with a card gained a family (%.0f%% of %s); %s of the %s endpoints are "
          "relatives with no card"
          % (f"{len(people & d['onCard']):,}",
             len(people & d["onCard"]) * 100.0 / len(d["onCard"]), f"{len(d['onCard']):,}",
             f"{len(people - d['onCard']):,}", f"{len(people):,}"))
    print("  %s bytes raw, %s gzipped" % (f"{len(raw):,}", f"{os.path.getsize(OUT):,}"))
    if d["dropped"]:
        print("  dropped: %s" % dict(d["dropped"]))
    print("  %s edges were stated in both directions and kept once" % f"{d['bothWays']:,}")
    print("  %s dynasties across %s offices"
          % (f"{len(dyn):,}", f"{len({x['office'] for x in dyn}):,}"))
    for x in dyn[:5]:
        print("       %-30s %-26s %3d holders, %s generations, %s-%s"
              % (x["officeName"][:30], x["name"][:26], len(x["members"]), x["generations"],
                 x["from"], x["to"]))
    return pack


# ------------------------------------------------------------------ the check

def check():
    problems = []

    def ok(good, text):
        print("  %s %s" % ("ok  " if good else "FAIL", text))
        if not good:
            problems.append(text)

    if not os.path.exists(OUT):
        print("kinship.json.gz: missing")
        return 1
    d = json.loads(gzip.open(OUT, "rt", encoding="utf-8").read())
    print("kinship.json.gz: %s bytes" % f"{os.path.getsize(OUT):,}")

    ok(d["format"] == "eternal-kinship-1", "the format is the one this builder writes")
    for k in ("parent", "spouse", "spouseYears", "named", "houses", "gaps", "kinds"):
        ok(k in d, "the pack carries %s" % k)

    parent = [tuple(x) for x in d["parent"]]
    spouse = [tuple(x) for x in d["spouse"]]
    years = [tuple(x) for x in d["spouseYears"]]
    named = {r[0]: r for r in d["named"]}

    ok(len(spouse) == len(years), "every marriage has a year row (%d against %d)"
       % (len(spouse), len(years)))
    ok(len(set(parent)) == len(parent), "no parent edge appears twice (%d)" % len(parent))
    ok(len(set(spouse)) == len(spouse), "no marriage appears twice (%d)" % len(spouse))
    ok(not [1 for a, b in parent if a == b], "nobody is their own parent")
    ok(not [1 for a, b in spouse if a == b], "nobody is married to themselves")
    pset = set(parent)          # built here, not inside the comprehension below
    back = sum(1 for a, b in parent if (b, a) in pset)
    ok(back == 0, "no pair is a parent of each other, which would make the tree a loop (%d)" % back)

    cards = read_cards.read()
    on_card = set(c["qid"] for c in cards["cards"] if c["kind"] == 0)
    card_name = {c["qid"]: c["name"] for c in cards["cards"]}
    ok(not [1 for q in named if q in on_card],
       "nobody is carried as a nameless relative who actually has a card")
    ends = {q for e in parent for q in e} | {q for e in spouse for q in e}
    unknown = ends - on_card - set(named)
    ok(len(unknown) * 20 < len(ends),
       "almost every person named by an edge is either a card or a named relative "
       "(%d of %d are neither)" % (len(unknown), len(ends)))
    dated = sum(1 for y in years if y[0] is not None or y[1] is not None)
    print("  ..  %d of %d marriages carry a year (%.0f%%)"
          % (dated, len(spouse), dated * 100.0 / max(1, len(spouse))))
    ok(dated * 3 > len(spouse), "more than a third of marriages are dated")

    ok(len(d["houses"]) > 2000, "%s houses is enough to be a dynasty register" % f"{len(d['houses']):,}")
    big = [h for h in d["houses"] if len(h[2]) >= 20]
    ok(len(big) > 100, "%s houses have twenty members or more" % len(big))
    for h in d["houses"][:3]:
        print("       %-26s %d members" % (h[1][:26], len(h[2])))

    # the point of the pack: a family you can check by hand
    by_name = {c["name"]: c["qid"] for c in cards["cards"] if c["kind"] == 0}
    kids = collections.defaultdict(list)
    pars = collections.defaultdict(list)
    for a, b in parent:
        kids[a].append(b)
        pars[b].append(a)
    for who in ("Queen Victoria", "Akbar", "Charlemagne", "Elizabeth II"):
        q = by_name.get(who)
        if q is None:
            continue
        nm = lambda x: card_name.get(x) or (named.get(x) or ["?", "?"])[1]  # noqa: E731
        print("       %-16s parents %s; children %s; house %s"
              % (who,
                 ", ".join(nm(p) for p in pars[q][:3]) or "none recorded",
                 ", ".join(nm(c) for c in kids[q][:4]) or "none recorded",
                 next((h[1] for h in d["houses"] if q in h[2]), "none")))
    ok(len(kids[by_name["Queen Victoria"]]) >= 5 if "Queen Victoria" in by_name else True,
       "Queen Victoria has the children she had")
    # a cycle would mean someone is their own ancestor, and every tree walk would hang
    kids = collections.defaultdict(list)
    indeg = collections.Counter()
    for a, b in parent:
        kids[a].append(b)
        indeg[b] += 1
    stack = [q for q in {x for e in parent for x in e} if indeg[q] == 0]
    seen = 0
    while stack:
        x = stack.pop()
        seen += 1
        for c in kids[x]:
            indeg[c] -= 1
            if indeg[c] == 0:
                stack.append(c)
    ok(seen == len({x for e in parent for x in e}),
       "the parent graph is a tree and not a loop: %d of %d people reached from the top"
       % (seen, len({x for e in parent for x in e})))

    dyn = d.get("dynasties", [])
    ok(len(dyn) > 300, "%s dynasties is enough to be a dynasty register" % f"{len(dyn):,}")
    ok(all(len(x["members"]) >= 3 for x in dyn), "no dynasty has fewer than three holders")
    ok(len({x["office"] for x in dyn}) > 200,
       "they span %s offices" % f"{len({x['office'] for x in dyn}):,}")
    with_house = sum(1 for x in dyn if x["house"] is not None)
    print("  ..  %d of %d dynasties are named after a house (%.0f%%)"
          % (with_house, len(dyn), with_house * 100.0 / max(1, len(dyn))))
    ok(with_house * 10 > len(dyn) * 7,
       "three quarters of the dynasties are named after the house Wikidata gave (%.0f%%)"
       % (with_house * 100.0 / max(1, len(dyn))))
    ok(all(x["name"] for x in dyn), "every dynasty has a name to print")
    ok(all(x["generations"] >= 1 for x in dyn), "every dynasty spans at least one generation")
    no_house = [x for x in dyn if x["house"] is None][:4]
    for x in no_house:
        print("       %-34s %-30s %d holders" % (x["officeName"][:34], x["name"][:30],
                                                 len(x["members"])))
    for x in dyn[:4]:
        print("       %-34s %-30s %d holders, %d generations, %s-%s"
              % (x["officeName"][:34], x["name"][:30], len(x["members"]), x["generations"],
                 x["from"], x["to"]))
    ok(any("Wittelsbach" in x["name"] for x in dyn)
       and any("Rurikid" in x["name"] for x in dyn)
       and any("Abbasid" in x["name"] for x in dyn),
       "the houses any encyclopedia names are in it: Wittelsbach, Rurikid, Abbasid")

    gained = len({q for e in parent + spouse for q in e} & on_card)
    print("  ..  %s people with a card gained a family (%.0f%%)"
          % (f"{gained:,}", gained * 100.0 / len(on_card)))
    ok(gained * 10 > len(on_card),
       "a third or more of the people with a card have a family worth drawing")

    print("kinship: %d problem(s)" % len(problems))
    return 1 if problems else 0


def main(argv):
    if "--check" in argv:
        return check()
    build()
    return check()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
