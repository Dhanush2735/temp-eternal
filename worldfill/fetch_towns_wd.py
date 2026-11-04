#!/usr/bin/env python3
"""Step 29 (systems C2, C3, C4, C5, C6): fetch the facts about towns from Wikidata (QLever's public endpoint).

What a villager can now say about the town they live in: its name in that year (Bombay before 1995, Mumbai after;
Edo before 1868), how many people live there (census figures), when it was founded, which province or district it
lies in (the Bombay Presidency until 1947), and who runs it (mayors, governors, chief ministers, with their years).

Nothing here is shipped: the exports go to build/towns/raw/ (left out of the workspace snapshots) and can be fetched
again at any time. build_towns.py reads them and writes history/towns.json.gz.

    python3 fetch_towns_wd.py towns      the towns: every human settlement with a coordinate and a population of at
                                         least 20,000 (any recorded figure), plus every settlement with an official
                                         name that has dates (a renamed town) and 8 or more Wikipedia articles
    python3 fetch_towns_wd.py details    for the towns chosen by build_towns.py --select (build/towns/towns.txt):
                                         names with their dates and language, population figures with their year,
                                         founding and end dates with their precision, kinds, the provinces and
                                         districts they lay in with dates, and the offices of their heads
    python3 fetch_towns_wd.py divisions  for the provinces and districts named (build/towns/divisions.txt): their
                                         names, kinds, dates and the offices of their heads
    python3 fetch_towns_wd.py parents    the province each district lies in today (P131 of the divisions)
    python3 fetch_towns_wd.py divisions2 names, dates, kinds and offices of those provinces not yet fetched
                                         (build/towns/divisions2.txt)
    python3 fetch_towns_wd.py holders    who held each of those offices, with the years, and the offices' names
                                         (build/towns/offices.txt)
    python3 fetch_towns_wd.py wiki       the towns of Wikipedia's "List of city name changes" lines that carry a year
                                         (their Wikidata numbers, from the article titles)

Every query is kept here, so the exports can be checked by hand on https://qlever.dev/wikidata.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fetch_cards_wd as fc  # noqa: E402  (the same endpoint, retries and batches)

RAW = os.path.join(HERE, "build", "towns", "raw")
BASE = os.path.join(HERE, "build", "towns")

# Settlements with any population figure of 20,000 or more (the figure is the "best" rank one, usually the latest).
T_BIG = """SELECT ?x ?k (MAX(?pop) AS ?maxpop) (SAMPLE(?c) AS ?coord) WHERE {
  ?x wdt:P31/wdt:P279* wd:Q486972 ; wdt:P1082 ?pop ; wdt:P625 ?c .
  FILTER(?pop >= 20000)
  OPTIONAL { ?x wikibase:sitelinks ?k }
} GROUP BY ?x ?k"""
# Renamed towns: an official name with a start or end date, and 8 or more articles.
T_RENAMED = """SELECT ?x ?k (SAMPLE(?c) AS ?coord) WHERE {
  ?x wdt:P31/wdt:P279* wd:Q486972 .
  ?x p:P1448 ?st .
  { ?st pq:P580 ?f } UNION { ?st pq:P582 ?t }
  ?x wdt:P625 ?c .
  ?x wikibase:sitelinks ?k .
  FILTER(xsd:integer(STR(?k)) >= 8)
} GROUP BY ?x ?k"""

D_LABEL = """SELECT ?x ?l ?lang WHERE {
  VALUES ?x { %s }
  ?x rdfs:label ?l . BIND(LANG(?l) AS ?lang) FILTER(?lang = "en" || ?lang = "mul")
}"""
# Names with dates: the official name (P1448) and the name (P2561), every language, with start and end.
D_NAMES = """SELECT ?x ?prop ?n ?lang ?f ?fp ?t ?tp WHERE {
  VALUES ?x { %s }
  { ?x p:P1448 ?st . ?st ps:P1448 ?n . BIND("o" AS ?prop) } UNION { ?x p:P2561 ?st . ?st ps:P2561 ?n . BIND("n" AS ?prop) }
  BIND(LANG(?n) AS ?lang)
  OPTIONAL { ?st pqv:P580 ?fv . ?fv wikibase:timeValue ?f ; wikibase:timePrecision ?fp }
  OPTIONAL { ?st pqv:P582 ?tv . ?tv wikibase:timeValue ?t ; wikibase:timePrecision ?tp }
  FILTER(BOUND(?f) || BOUND(?t))
}"""
# Population figures with the year they were counted (and the rank, so deprecated figures can be left out).
D_POP = """SELECT ?x ?pop ?d ?rank WHERE {
  VALUES ?x { %s }
  ?x p:P1082 ?st . ?st ps:P1082 ?pop ; wikibase:rank ?rank . ?st pq:P585 ?d .
}"""
# Founding (P571) and end (P576) with their precision; kinds (P31).
D_LIFE = """SELECT ?x ?which ?t ?prec WHERE {
  VALUES ?x { %s }
  { ?x p:P571/psv:P571 ?v . BIND("from" AS ?which) } UNION { ?x p:P576/psv:P576 ?v . BIND("to" AS ?which) }
  ?v wikibase:timeValue ?t ; wikibase:timePrecision ?prec .
}"""
D_KIND = """SELECT ?x ?cls WHERE {
  VALUES ?x { %s }
  ?x wdt:P31 ?cls .
}"""
# The provinces and districts a town lay in (P131), with dates when known.
D_ADMIN = """SELECT ?x ?d ?f ?t ?rank WHERE {
  VALUES ?x { %s }
  ?x p:P131 ?st . ?st ps:P131 ?d ; wikibase:rank ?rank .
  OPTIONAL { ?st pq:P580 ?f } OPTIONAL { ?st pq:P582 ?t }
}"""
# The office of the head of the town's government (P1313: mayor, governor, ...) and of its head of state (P1906).
D_OFFICE = """SELECT ?x ?which ?off WHERE {
  VALUES ?x { %s }
  { ?x wdt:P1313 ?off . BIND("gov" AS ?which) } UNION { ?x wdt:P1906 ?off . BIND("state" AS ?which) }
}"""
# Divisions: the same name, kind, dates and offices, plus their own dates.
V_DATES = """SELECT ?x ?which ?y WHERE {
  VALUES ?x { %s }
  { ?x wdt:P571 ?d . BIND("from" AS ?which) } UNION { ?x wdt:P580 ?d . BIND("from" AS ?which) }
  UNION { ?x wdt:P576 ?d . BIND("to" AS ?which) } UNION { ?x wdt:P582 ?d . BIND("to" AS ?which) }
  BIND(YEAR(?d) AS ?y)
}"""
V_TOP = """SELECT ?x ?top WHERE {
  VALUES ?x { %s }
  ?x wdt:P31/wdt:P279* ?top .
  VALUES ?top { wd:Q6256 wd:Q3624078 wd:Q3024240 wd:Q10864048 wd:Q13220204 wd:Q13221722 wd:Q486972 wd:Q1620908
                wd:Q133156 wd:Q1336152 wd:Q19953632 }
}"""
# The province a district lies in (P131 of the divisions; truthy statements only, so today's parent).
V_PARENT = """SELECT ?x ?parent WHERE {
  VALUES ?x { %s }
  ?x wdt:P131 ?parent .
}"""
# Who held an office, from when to when (P580/P582 on the P39 statement), with the holder's name.
H_HOLDERS = """SELECT ?off ?h ?hl ?f ?fp ?t ?tp WHERE {
  VALUES ?off { %s }
  ?h p:P39 ?st . ?st ps:P39 ?off .
  OPTIONAL { ?st pqv:P580 ?fv . ?fv wikibase:timeValue ?f ; wikibase:timePrecision ?fp }
  OPTIONAL { ?st pqv:P582 ?tv . ?tv wikibase:timeValue ?t ; wikibase:timePrecision ?tp }
  OPTIONAL { ?h rdfs:label ?hl . FILTER(LANG(?hl) = "en") }
}"""
# Article titles (English Wikipedia) to Wikidata numbers, with a point and a population.
W_TITLES = """SELECT ?title ?x ?c ?pop WHERE {
  VALUES ?title { %s }
  ?a schema:about ?x ; schema:isPartOf <https://en.wikipedia.org/> ; schema:name ?title .
  OPTIONAL { ?x wdt:P625 ?c } OPTIONAL { ?x wdt:P1082 ?pop }
}"""

PQV = "PREFIX pqv: <http://www.wikidata.org/prop/qualifier/value/>\n"


def run(query, name):
    old_raw, old_pre = fc.RAW, fc.PREFIXES
    fc.RAW = RAW
    fc.PREFIXES = old_pre + PQV
    try:
        return fc.run(query, name)
    finally:
        fc.RAW, fc.PREFIXES = old_raw, old_pre


def batches(name, template, qids, size):
    old_raw, old_pre = fc.RAW, fc.PREFIXES
    fc.RAW = RAW
    fc.PREFIXES = old_pre + PQV
    try:
        return fc.batches(name, template, qids, size)
    finally:
        fc.RAW, fc.PREFIXES = old_raw, old_pre


def main(argv):
    mode = argv[1] if len(argv) > 1 else ""
    if mode == "towns":
        run(T_BIG, "towns_big")
        run(T_RENAMED, "towns_renamed")
    elif mode == "details":
        qids = fc.read_list(os.path.join(BASE, "towns.txt"))
        print(f"details: {len(qids):,} towns")
        batches("t_label", D_LABEL, qids, 6000)
        batches("t_names", D_NAMES, qids, 6000)
        batches("t_pop", D_POP, qids, 4000)
        batches("t_life", D_LIFE, qids, 6000)
        batches("t_kind", D_KIND, qids, 6000)
        batches("t_admin", D_ADMIN, qids, 6000)
        batches("t_office", D_OFFICE, qids, 6000)
    elif mode == "divisions":
        qids = fc.read_list(os.path.join(BASE, "divisions.txt"))
        print(f"divisions: {len(qids):,}")
        batches("v_label", D_LABEL, qids, 6000)
        batches("v_names", D_NAMES, qids, 6000)
        batches("v_dates", V_DATES, qids, 6000)
        batches("v_top", V_TOP, qids, 3000)
        batches("v_office", D_OFFICE, qids, 6000)
    elif mode == "parents":
        qids = fc.read_list(os.path.join(BASE, "divisions.txt"))
        batches("v_parent", V_PARENT, qids, 6000)
    elif mode == "divisions2":
        qids = fc.read_list(os.path.join(BASE, "divisions2.txt"))
        print(f"parent provinces: {len(qids):,}")
        batches("v2_label", D_LABEL, qids, 6000)
        batches("v2_dates", V_DATES, qids, 6000)
        batches("v2_top", V_TOP, qids, 3000)
        batches("v2_office", D_OFFICE, qids, 6000)
    elif mode == "holders":
        qids = fc.read_list(os.path.join(BASE, "offices.txt"))
        print(f"offices: {len(qids):,}")
        batches("h_holders", H_HOLDERS, qids, 2000)
        batches("o_label", D_LABEL, qids, 6000)
    elif mode == "wiki":
        titles = fc.read_list(os.path.join(BASE, "wiki_titles.txt"))
        vals = " ".join(json.dumps(t) + "@en" for t in titles)
        run(W_TITLES % vals, "w_titles")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
