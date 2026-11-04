#!/usr/bin/env python3
"""Step 28 (systems C8, C9, C21): fetch the facts for the event cards and the cause-and-effect graph from Wikidata
(QLever's public endpoint), and the natural events Wikidata places on the map.

Nothing here is shipped: the exports go to build/events/raw/ (left out of the workspace snapshots) and can be fetched
again at any time. build_cards.py reads them (the event cards join the people and group cards in cards/cards.tiles),
and build_nature.py the natural events.

    python3 fetch_events_wd.py ours       names, dates with their precision, places, deaths, articles, and the links
                                          both ways (part of, took part, won, causes, effects, came before and after)
                                          of the events the history data already has with a Wikidata number
                                          (build/events/our_events.txt)
    python3 fetch_events_wd.py linked     the same for the events those links name (build/events/linked_events.txt,
                                          written by build_cards.py --events-linked), and the names of every other
                                          thing they name
    python3 fetch_events_wd.py graph      every cause-and-effect statement between two dated things (the wider graph)
    python3 fetch_events_wd.py graphlinked  the details of the events of that graph that have no card yet
                                          (build/events/graph_events.txt, written by build_event_cards.py --graph)
    python3 fetch_events_wd.py nature     floods, wildfires, landslides, avalanches, tornadoes, heat waves, droughts,
                                          famines, epidemics and tropical cyclones with a date (and a point when known)
    python3 fetch_events_wd.py occupations  military occupations with their years, country and occupier
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fetch_cards_wd as fc  # noqa: E402  (the same endpoint, retries and batches)

RAW = os.path.join(HERE, "build", "events", "raw")
BASE = os.path.join(HERE, "build", "events")

E_NAMES = fc.D_NAMES
E_DATES = """SELECT ?e ?which (YEAR(?t) AS ?y) ?prec WHERE {
  VALUES ?e { %s }
  { ?e p:P585/psv:P585 ?v . BIND("at" AS ?which) } UNION { ?e p:P580/psv:P580 ?v . BIND("from" AS ?which) }
  UNION { ?e p:P582/psv:P582 ?v . BIND("to" AS ?which) }
  ?v wikibase:timeValue ?t ; wikibase:timePrecision ?prec .
}"""
E_PLACE = """SELECT ?e ?c ?loc ?locl ?lc ?ctry ?ctryl WHERE {
  VALUES ?e { %s }
  OPTIONAL { ?e wdt:P625 ?c }
  OPTIONAL { ?e wdt:P276 ?loc . OPTIONAL { ?loc rdfs:label ?locl . FILTER(LANG(?locl) = "en") }
             OPTIONAL { ?loc wdt:P625 ?lc } }
  OPTIONAL { ?e wdt:P17 ?ctry . ?ctry rdfs:label ?ctryl . FILTER(LANG(?ctryl) = "en") }
}"""
E_MORE = """SELECT ?e ?k ?deaths ?cls WHERE {
  VALUES ?e { %s }
  OPTIONAL { ?e wikibase:sitelinks ?k }
  OPTIONAL { ?e wdt:P1120 ?deaths }
  OPTIONAL { ?e wdt:P31 ?cls }
}"""
# Links from an event (forward) and to it (backward), one property at a time; ?prop names the relation as the card
# keeps it, from the event's side.
FORWARD = [("P361", "partof"), ("P710", "took"), ("P1346", "winner"), ("P828", "cause"), ("P1478", "cause"),
           ("P1479", "cause"), ("P1542", "effect"), ("P1536", "effect"), ("P1537", "effect"), ("P155", "after"),
           ("P156", "before")]
BACKWARD = [("P361", "haspart"), ("P828", "effect"), ("P1478", "effect"), ("P1479", "effect"), ("P1542", "cause"),
            ("P1536", "cause"), ("P1537", "cause"), ("P155", "before"), ("P156", "after")]
E_FWD = """SELECT ?e ?prop ?o WHERE {
  VALUES ?e { %s }
  ?e wdt:PROP ?o .
  BIND("ROLE" AS ?prop)
}"""
E_BWD = """SELECT ?e ?prop ?o WHERE {
  VALUES ?e { %s }
  ?o wdt:PROP ?e .
  BIND("ROLE" AS ?prop)
}"""
# What the linked things are: a date (then it can be an event card), a human, or something else (a name only).
L_KIND = """SELECT ?x ?l ?human ?y ?k WHERE {
  VALUES ?x { %s }
  OPTIONAL { ?x rdfs:label ?l . FILTER(LANG(?l) = "en") }
  OPTIONAL { ?x wdt:P31 wd:Q5 . BIND(1 AS ?human) }
  OPTIONAL { { ?x wdt:P585 ?d } UNION { ?x wdt:P580 ?d } BIND(YEAR(?d) AS ?y) }
  OPTIONAL { ?x wikibase:sitelinks ?k }
}"""

# Every cause-and-effect statement between two dated things in Wikidata (3,151 on 2026-10-15): the wider graph (C9).
GRAPH = """SELECT ?a ?prop ?b WHERE {
  VALUES (?p ?prop) { (wdt:P828 "cause") (wdt:P1478 "cause") (wdt:P1479 "cause") (wdt:P1542 "effect")
                      (wdt:P1536 "effect") (wdt:P1537 "effect") }
  ?a ?p ?b .
  FILTER EXISTS { { ?a wdt:P585 ?da } UNION { ?a wdt:P580 ?da } }
  FILTER EXISTS { { ?b wdt:P585 ?db } UNION { ?b wdt:P580 ?db } }
}"""

# Natural events (classes checked by their English labels on 2026-10-15).
NATURE = {"flood": "Q8068", "wildfire": "Q169950", "landslide": "Q167903", "avalanche": "Q7935", "tornado": "Q8081",
          "heatwave": "Q215864", "drought": "Q43059", "famine": "Q168247", "epidemic": "Q44512", "pandemic": "Q12184",
          "cyclone": "Q8092"}
N_LIST = """SELECT ?e ?l ?d ?k (YEAR(?t) AS ?y) ?prec (YEAR(?t2) AS ?y2) ?c ?lc ?locl ?ctryc ?ctryl ?deaths WHERE {
  ?e wdt:P31/wdt:P279* wd:CLS .
  { ?e p:P585/psv:P585 ?v } UNION { ?e p:P580/psv:P580 ?v }
  ?v wikibase:timeValue ?t ; wikibase:timePrecision ?prec .
  OPTIONAL { ?e wdt:P582 ?t2 }
  ?e rdfs:label ?l . FILTER(LANG(?l) = "en")
  OPTIONAL { ?e schema:description ?d . FILTER(LANG(?d) = "en") }
  OPTIONAL { ?e wikibase:sitelinks ?k }
  OPTIONAL { ?e wdt:P625 ?c }
  OPTIONAL { ?e wdt:P276 ?loc . ?loc wdt:P625 ?lc . OPTIONAL { ?loc rdfs:label ?locl . FILTER(LANG(?locl) = "en") } }
  OPTIONAL { ?e wdt:P17 ?ctry . ?ctry wdt:P625 ?ctryc . ?ctry rdfs:label ?ctryl . FILTER(LANG(?ctryl) = "en") }
  OPTIONAL { ?e wdt:P1120 ?deaths }
}"""
OCCUPATIONS = """SELECT ?e ?l (YEAR(?f) AS ?fy) (YEAR(?t) AS ?ty) ?ctry ?ctryl ?occ ?occl WHERE {
  ?e wdt:P31/wdt:P279* wd:Q188686 .
  ?e rdfs:label ?l . FILTER(LANG(?l) = "en")
  OPTIONAL { ?e wdt:P580 ?f }
  OPTIONAL { ?e wdt:P582 ?t }
  OPTIONAL { ?e wdt:P17 ?ctry . ?ctry rdfs:label ?ctryl . FILTER(LANG(?ctryl) = "en") }
  OPTIONAL { { ?e wdt:P710 ?occ } UNION { ?e wdt:P137 ?occ } ?occ rdfs:label ?occl . FILTER(LANG(?occl) = "en") }
}"""


def run(query, name):
    old = fc.RAW
    fc.RAW = RAW
    try:
        return fc.run(query, name)
    finally:
        fc.RAW = old


def batches(name, template, qids, size):
    old = fc.RAW
    fc.RAW = RAW
    try:
        return fc.batches(name, template, qids, size)
    finally:
        fc.RAW = old


def details(prefix, qids, backward=True):
    print(f"{prefix}: {len(qids):,} events")
    batches(prefix + "names", E_NAMES, qids, 15000)
    batches(prefix + "dates", E_DATES, qids, 15000)
    batches(prefix + "place", E_PLACE, qids, 10000)
    batches(prefix + "more", E_MORE, qids, 15000)
    for prop, role in FORWARD:
        batches(f"{prefix}fwd_{prop}_{role}", E_FWD.replace("PROP", prop).replace("ROLE", role), qids, 15000)
    if backward:
        for prop, role in BACKWARD:
            batches(f"{prefix}bwd_{prop}_{role}", E_BWD.replace("PROP", prop).replace("ROLE", role), qids, 15000)


def main(argv):
    what = argv[0] if argv else ""
    if what == "ours":
        details("o_", fc.read_list(os.path.join(BASE, "our_events.txt")))
    elif what == "linked":
        details("l_", fc.read_list(os.path.join(BASE, "linked_events.txt")), backward=False)
        batches("names_x", L_KIND, fc.read_list(os.path.join(BASE, "linked_things.txt")), 15000)
    elif what == "kinds":
        batches("kind_x", L_KIND, fc.read_list(os.path.join(BASE, "linked_all.txt")), 15000)
    elif what == "graph":
        run(GRAPH, "graph")
    elif what == "graphlinked":
        details("g_", fc.read_list(os.path.join(BASE, "graph_events.txt")), backward=False)
    elif what == "nature":
        for kind, cls in NATURE.items():
            run(N_LIST.replace("CLS", cls), f"nature_{kind}")
    elif what == "occupations":
        run(OCCUPATIONS, "occupations")
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
