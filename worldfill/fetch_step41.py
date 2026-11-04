#!/usr/bin/env python3
"""Step 41 (D11, C11), part 3 and 5: fetch from Wikidata the seven properties step 27 never got.

    python3 fetch_step41.py            everything, in order (each query is skipped if its file is there)
    python3 fetch_step41.py kin        only the three kinship queries
    python3 fetch_step41.py places     only the two where-a-person-was queries
    python3 fetch_step41.py --report   what came back, without fetching (exit 1 on a problem)

Step 27 fetched names, dates, birthplaces, death places, offices, works and five kinds of link.
It did **not** fetch these, and they are exactly what D11 and C11 are:

* P22 father, P25 mother, P40 child — the blood edges of a family (C11);
* P26 spouse, with P580 start and P582 end — a marriage, dated where Wikidata has the years (C11);
* P53 family — a named house, which is a dynasty for free (C11);
* P551 residence, P937 work location — where a person *was*, as opposed to where they were born
  (D11), each with its point on the map where the place has one.

The QIDs are the people on the cards: 148,510 of them, read out of the shipped
``cards/cards.tiles`` by ``read_cards.py``. Every batch is 15,000 QIDs, which is the size step 27
found worked.

Unlike step 27 this writes to ``raw/step41/``, **which is kept**: these exports are small (a few
megabytes gzipped) and re-fetching them would be fifty large queries for no reason. Nothing here is
shipped; the packs are built by ``build_kinship.py`` and ``build_presence.py``.

Every query can be run by hand on https://qlever.dev/wikidata.
"""
import gzip
import os
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw", "step41")
URL = "https://qlever.dev/api/wikidata"
BATCH = 15000

PREFIXES = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
"""

# --- C11 --------------------------------------------------------------------
# the blood edges. child (P40) is given more than twice as often as father (P22), so the register
# stores each edge once and inverts it when it is asked for parents.
KIN = """SELECT ?p ?rel ?q WHERE {
  VALUES ?p { %s }
  { ?p wdt:P22 ?q BIND("father" AS ?rel) }
  UNION { ?p wdt:P25 ?q BIND("mother" AS ?rel) }
  UNION { ?p wdt:P40 ?q BIND("child" AS ?rel) }
}"""

SPOUSE = """SELECT ?p ?q ?fy ?ty WHERE {
  VALUES ?p { %s }
  ?p p:P26 ?st . ?st ps:P26 ?q .
  OPTIONAL { ?st pq:P580 ?f }
  OPTIONAL { ?st pq:P582 ?t }
  BIND(YEAR(?f) AS ?fy)
  BIND(YEAR(?t) AS ?ty)
}"""

HOUSE = """SELECT ?p ?q ?l WHERE {
  VALUES ?p { %s }
  ?p wdt:P53 ?q .
  OPTIONAL { ?q rdfs:label ?l . FILTER(LANG(?l) = "en") }
}"""

# --- D11 --------------------------------------------------------------------
# a place is only worth having with a point on it (decision 4), so the coordinates come with it;
# the label is fetched too so the register can name the place in its own words.
RESIDENCE = """SELECT ?p ?q ?c ?l ?fy ?ty WHERE {
  VALUES ?p { %s }
  ?p p:P551 ?st . ?st ps:P551 ?q .
  OPTIONAL { ?q wdt:P625 ?c }
  OPTIONAL { ?q rdfs:label ?l . FILTER(LANG(?l) = "en") }
  OPTIONAL { ?st pq:P580 ?f }
  OPTIONAL { ?st pq:P582 ?t }
  BIND(YEAR(?f) AS ?fy)
  BIND(YEAR(?t) AS ?ty)
}"""

WORK = RESIDENCE.replace("p:P551", "p:P937").replace("ps:P551", "ps:P937")

# --- C11, the second pass ---------------------------------------------------
# Only 14% of the edges above have both ends on a card: a famous person's father is usually not
# famous himself. An edge whose far end is a QID and nothing else is useless - the register cannot
# name him. So the 96,093 relatives with no card are fetched too: a name, a description and two
# years, which is everything a family tree needs of a node it will never open.
RELATIVE = """SELECT ?p ?l ?d ?by ?dy WHERE {
  VALUES ?p { %s }
  OPTIONAL { ?p rdfs:label ?l . FILTER(LANG(?l) = "en") }
  OPTIONAL { ?p schema:description ?d . FILTER(LANG(?d) = "en") }
  OPTIONAL { ?p wdt:P569 ?b }
  OPTIONAL { ?p wdt:P570 ?dd }
  BIND(YEAR(?b) AS ?by)
  BIND(YEAR(?dd) AS ?dy)
}"""

QUERIES = [("kin", KIN), ("spouse", SPOUSE), ("house", HOUSE),
           ("residence", RESIDENCE), ("work", WORK), ("relative", RELATIVE)]
KIN_QUERIES = ["kin", "spouse", "house"]
PLACE_QUERIES = ["residence", "work"]


def people_qids():
    """The people on the cards, from read_cards.py (which reads the shipped tiles)."""
    import read_cards
    d = read_cards.read()
    return ["Q%d" % c["qid"] for c in d["cards"] if c["kind"] == 0]


def run(query, path, retries=6):
    if os.path.exists(path) and os.path.getsize(path) > 30:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return sum(1 for _ in f) - 1
    body = PREFIXES + query
    for attempt in range(retries):
        try:
            t = time.time()
            r = requests.post(URL, data={"query": body, "action": "tsv_export"},
                              timeout=1800, stream=True)
            if r.status_code == 429 or r.status_code >= 500:
                raise RuntimeError("HTTP %d" % r.status_code)
            r.raise_for_status()
            tmp = path + ".part"
            n = 0
            with gzip.GzipFile(filename="", mode="wb", fileobj=open(tmp, "wb"), compresslevel=5, mtime=0) as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk)
                    n += chunk.count(b"\n")
            if n == 0:
                raise RuntimeError("empty answer (the query failed)")
            os.replace(tmp, path)
            print("  %s: %s rows in %.0f s" % (os.path.basename(path), f"{n - 1:,}",
                                               time.time() - t), flush=True)
            return n - 1
        except Exception as e:                        # noqa: BLE001 - every failure is retried
            wait = 15 * (attempt + 1)
            print("  %s: %s; again in %d s" % (os.path.basename(path), e, wait), flush=True)
            time.sleep(wait)
    raise SystemExit("%s: gave up" % path)


def batches(name, template, qids):
    qids = sorted(set(qids), key=lambda q: int(q[1:]))
    total = 0
    for i in range(0, len(qids), BATCH):
        vals = " ".join("wd:" + q for q in qids[i:i + BATCH])
        total += run(template % vals,
                     os.path.join(RAW, "%s_%03d.tsv.gz" % (name, i // BATCH)))
    return total


def people_qids_set():
    import read_cards
    return set(c["qid"] for c in read_cards.read()["cards"] if c["kind"] == 0)


def relative_qids():
    """The relatives named by an edge who have no card of their own."""
    on_card = people_qids_set()
    out = set()
    for name in ("kin", "spouse"):
        for r in rows(name):
            for k in ("p", "q"):
                v = qid_of(r.get(k))
                if v is not None and v not in on_card:
                    out.add(v)
    return sorted(out)


def year(cell):
    """A fetched year as a number, or None. Wikidata gives years outside any sane range for a
    handful of items, and a card cannot carry them, so they are dropped here rather than later."""
    if not cell:
        return None
    try:
        v = int(cell)
    except ValueError:
        return None
    return v if -4000 <= v <= 2100 else None


def qid_of(cell):
    """A Wikidata URI -> its number, or None for a blank node (Wikidata's 'someone, no item')."""
    c = (cell or "").strip().lstrip("<").rstrip(">")
    if not c.startswith("http://www.wikidata.org/entity/Q"):
        return None
    return int(c.rsplit("/", 1)[-1][1:])


def fetch(only=None):
    os.makedirs(RAW, exist_ok=True)
    totals = {}
    for name, template in QUERIES:
        if only and name not in only:
            continue
        if name == "relative":
            qids = ["Q%d" % q for q in relative_qids()]
            print("fetching %s relatives who have no card" % f"{len(qids):,}", flush=True)
        else:
            qids = people_qids()
            print("fetching for %s people" % f"{len(qids):,}", flush=True)
        totals[name] = batches(name, template, qids)
    for k, v in totals.items():
        print("  %-10s %s rows" % (k, f"{v:,}"))
    return totals


def unquote(cell):
    """The TSV export quotes string literals and tags labels with their language."""
    if not cell:
        return ""
    if cell.endswith("@en"):
        cell = cell[:-3]
    return cell[1:-1] if cell.startswith('"') and cell.endswith('"') else cell


def rows(name):
    out = []
    for fn in sorted(f for f in os.listdir(RAW) if f.startswith(name + "_") and f.endswith(".tsv.gz")):
        with gzip.open(os.path.join(RAW, fn), "rt", encoding="utf-8") as f:
            # QLever names the columns with their leading "?", which is not a key anyone wants
            head = [h.lstrip("?") for h in f.readline().rstrip("\n").split("\t")]
            for line in f:
                out.append(dict(zip(head, line.rstrip("\n").split("\t"))))
    return out


def report():
    problems = []

    def ok(good, text):
        print("  %s %s" % ("ok  " if good else "FAIL", text))
        if not good:
            problems.append(text)

    for name, template in QUERIES:
        got = [f for f in os.listdir(RAW) if f.startswith(name + "_")] if os.path.isdir(RAW) else []
        want = 7 if name == "relative" else 10
        ok(len(got) == want, "%s: %d batch files (want %d)" % (name, len(got), want))
    if not os.path.isdir(RAW):
        print("raw/step41: nothing fetched yet")
        return 1
    kin = rows("kin")
    spouse = rows("spouse")
    house = rows("house")
    res = rows("residence")
    work = rows("work")
    rel = rows("relative")
    named = sum(1 for r in rel if unquote(r.get("l")))
    dated = sum(1 for r in rel if r.get("by") or r.get("dy"))
    print("  ..  relative: %s people with no card, %s named (%.0f%%), %s with a year"
          % (f"{len(rel):,}", f"{named:,}", named * 100.0 / max(1, len(rel)), f"{dated:,}"))
    ok(len(rel) > 60000 and named * 10 > len(rel) * 9,
       "the relatives a tree needs to name came back with their names")

    def q(cell):
        return cell.rsplit("/", 1)[-1] if cell else None

    pp = set(q(r["p"]) for r in kin)
    print("  ..  kin: %s edges, %s people" % (f"{len(kin):,}", f"{len(pp):,}"))
    by = {}
    for r in kin:
        by[unquote(r["rel"])] = by.get(unquote(r["rel"]), 0) + 1
    print("  ..  by kind: %s" % by)
    ok(len(kin) > 50000, "kinship is worth building: %s edges" % f"{len(kin):,}")
    ok(all(k in by and by[k] > 1000 for k in ("father", "mother", "child")),
       "all three blood edges came back, and none of them is a trickle: %s" % by)

    dated = sum(1 for r in spouse if r.get("fy"))
    print("  ..  spouse: %s marriages, %s with a year" % (f"{len(spouse):,}", f"{dated:,}"))
    ok(len(spouse) > 20000, "marriages are worth building: %s" % f"{len(spouse):,}")

    named = sum(1 for r in house if r.get("l"))
    print("  ..  house: %s memberships, %s with a name" % (f"{len(house):,}", f"{named:,}"))
    ok(len(house) > 5000, "houses are worth building: %s" % f"{len(house):,}")

    for label, rs in (("residence", res), ("work", work)):
        with_point = sum(1 for r in rs if r.get("c") and r["c"].upper().startswith("POINT("))
        with_name = sum(1 for r in rs if r.get("l"))
        dated = sum(1 for r in rs if r.get("fy") or r.get("ty"))
        print("  ..  %s: %s statements, %s with a point (%.0f%%), %s named, %s dated (%.0f%%)"
              % (label, f"{len(rs):,}", f"{with_point:,}", with_point * 100.0 / max(1, len(rs)),
                 f"{with_name:,}", f"{dated:,}", dated * 100.0 / max(1, len(rs))))
        ok(with_point > 5000, "%s: enough of them carry a point to be worth a row" % label)
        ok(dated * 3 < len(rs), "%s: most are undated, so the pack must date them by the person's "
                                "life and say it did" % label)
    print("fetch_step41: %d problem(s)" % len(problems))
    return 1 if problems else 0


def main(argv):
    if "--report" in argv:
        return report()
    if "kin" in argv:
        fetch(KIN_QUERIES)
    elif "places" in argv:
        fetch(PLACE_QUERIES)
    else:
        fetch()
    return report()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
