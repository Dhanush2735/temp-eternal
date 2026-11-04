#!/usr/bin/env python3
"""Step 27 (systems C10, C12, C22): fetch the facts for the knowledge cards from Wikidata (QLever's public endpoint).

The cards are built by build_cards.py from what this script saves. Nothing here is shipped: the exports are large, so
they are written to build/cards/raw/ (left out of the workspace snapshots) and can be fetched again at any time.

    python3 fetch_cards_wd.py pool          the people pool: every human with 2 or more Wikipedia articles and a
                                            birthplace on the map (QID, articles, birth and death year, the point)
    python3 fetch_cards_wd.py orgs          the organisations pool (companies, schools, papers, parties, armies,
                                            societies, orders) with a founding year and a point
    python3 fetch_cards_wd.py details       names, descriptions, dates with their precision, gender, birthplace and
                                            death place names, offices, memberships, works, for the people chosen
                                            by build_cards.py --select (build/cards/chosen_people.txt)
    python3 fetch_cards_wd.py all           everything, in that order (build_cards.py --select runs in between)

Every query is kept here, so the exports can be checked by hand on https://qlever.dev/wikidata.
"""
import gzip
import os
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "build", "cards", "raw")
URL = "https://qlever.dev/api/wikidata"

PREFIXES = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX psv: <http://www.wikidata.org/prop/statement/value/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX schema: <http://schema.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""

# The people pool, one band of article counts at a time (the counts are compared as numbers through STR: QLever
# compares the typed literal itself as text).
POOL = """SELECT ?p ?k (YEAR(?bd) AS ?by) (YEAR(?dd) AS ?dy) ?c WHERE {
  ?p wdt:P31 wd:Q5 ; wikibase:sitelinks ?s .
  BIND(xsd:integer(STR(?s)) AS ?k) FILTER(?k >= %d && ?k <= %d)
  ?p wdt:P19 ?bp . ?bp wdt:P625 ?c .
  OPTIONAL { ?p wdt:P569 ?bd }
  OPTIONAL { ?p wdt:P570 ?dd }
}"""
POOL_BANDS = [(2, 2), (3, 4), (5, 9), (10, 19), (20, 100000)]

# Organisation classes, checked by their English labels on 2026-10-15 (step 25's lesson: never trust a guessed QID).
ORG_CLASSES = {
    "company": ["Q4830453", "Q783794", "Q6881511", "Q2865305", "Q162157", "Q22687"],  # business, company, enterprise,
    # trading company, chartered company, bank
    "school": ["Q3918", "Q38723", "Q189004", "Q3914"],  # university, higher education institution, college, school
    "paper": ["Q11032"],  # newspaper
    "party": ["Q7278"],  # political party
    "army": ["Q176799", "Q772547", "Q37726", "Q52371", "Q163323"],  # military unit, armed forces, army, regiment,
    # Roman legion
    "society": ["Q170161", "Q939871", "Q178790", "Q955824", "Q414147", "Q1966910", "Q276548"],  # guild (2), labor
    # union, learned society, academy of sciences, national academy, secret society
    "order": ["Q2061186"],  # religious order
}

ORGS = """SELECT ?o ?top ?k (YEAR(?inc) AS ?iy) ?iprec (YEAR(?dis) AS ?dy) ?c1 ?c2 ?c3 WHERE {
  VALUES ?top { %s }
  ?o wdt:P31/wdt:P279* ?top .
  ?o wikibase:sitelinks ?s . BIND(xsd:integer(STR(?s)) AS ?k) FILTER(?k >= 2)
  ?o p:P571/psv:P571 ?iv . ?iv wikibase:timeValue ?inc ; wikibase:timePrecision ?iprec .
  OPTIONAL { ?o wdt:P576 ?dis }
  OPTIONAL { ?o wdt:P625 ?c1 }
  OPTIONAL { ?o wdt:P159 ?hq . ?hq wdt:P625 ?c2 }
  OPTIONAL { ?o wdt:P131 ?ad . ?ad wdt:P625 ?c3 }
}"""

# Details by batches of chosen QIDs.
D_NAMES = """SELECT ?x ?l ?d WHERE {
  VALUES ?x { %s }
  ?x rdfs:label ?l . FILTER(LANG(?l) = "en")
  OPTIONAL { ?x schema:description ?d . FILTER(LANG(?d) = "en") }
}"""
D_DATES = """SELECT ?p ?which (YEAR(?t) AS ?y) ?prec WHERE {
  VALUES ?p { %s }
  VALUES (?prop ?which) { (p:P569 "b") (p:P570 "d") }
  ?p ?prop ?st . ?st ?psv ?v . ?v wikibase:timeValue ?t ; wikibase:timePrecision ?prec .
  FILTER(STRSTARTS(STR(?psv), "http://www.wikidata.org/prop/statement/value/P5"))
}"""
D_DATES_B = """SELECT ?p (YEAR(?t) AS ?y) ?prec WHERE {
  VALUES ?p { %s }
  ?p p:P569/psv:P569 ?v . ?v wikibase:timeValue ?t ; wikibase:timePrecision ?prec .
}"""
D_DATES_D = """SELECT ?p (YEAR(?t) AS ?y) ?prec WHERE {
  VALUES ?p { %s }
  ?p p:P570/psv:P570 ?v . ?v wikibase:timeValue ?t ; wikibase:timePrecision ?prec .
}"""
D_PLACES = """SELECT ?p ?g ?bp ?bpl ?dp ?dpl ?dc WHERE {
  VALUES ?p { %s }
  OPTIONAL { ?p wdt:P21 ?g }
  OPTIONAL { ?p wdt:P19 ?bp . ?bp rdfs:label ?bpl . FILTER(LANG(?bpl) = "en") }
  OPTIONAL { ?p wdt:P20 ?dp . ?dp wdt:P625 ?dc . ?dp rdfs:label ?dpl . FILTER(LANG(?dpl) = "en") }
}"""
D_OFFICES = """SELECT ?p ?pos (YEAR(?f) AS ?fy) (YEAR(?t) AS ?ty) WHERE {
  VALUES ?p { %s }
  ?p p:P39 ?st . ?st ps:P39 ?pos .
  OPTIONAL { ?st pq:P580 ?f }
  OPTIONAL { ?st pq:P582 ?t }
}"""
D_LINK_ONE = """SELECT ?p ?prop ?o (YEAR(?f) AS ?fy) (YEAR(?t) AS ?ty) WHERE {
  VALUES ?p { %s }
  ?p p:%s ?st . ?st ps:%s ?o .
  BIND("%s" AS ?prop)
  OPTIONAL { ?st pq:P580 ?f }
  OPTIONAL { ?st pq:P582 ?t }
}"""
LINK_PROPS = [("P69", "educated"), ("P102", "party"), ("P108", "employer"), ("P241", "branch"), ("P463", "member")]
D_WORKS = """SELECT ?p ?w ?wl (YEAR(?pub) AS ?py) (YEAR(?inc) AS ?iy) WHERE {
  VALUES ?p { %s }
  ?p wdt:P800 ?w . ?w rdfs:label ?wl . FILTER(LANG(?wl) = "en")
  OPTIONAL { ?w wdt:P577 ?pub }
  OPTIONAL { ?w wdt:P571 ?inc }
}"""
D_ORG_NAMES = D_NAMES
D_ORG_PLACE = """SELECT ?o ?hql ?adl ?f WHERE {
  VALUES ?o { %s }
  OPTIONAL { ?o wdt:P159 ?hq . ?hq rdfs:label ?hql . FILTER(LANG(?hql) = "en") }
  OPTIONAL { ?o wdt:P131 ?ad . ?ad rdfs:label ?adl . FILTER(LANG(?adl) = "en") }
  OPTIONAL { ?o wdt:P112 ?f }
}"""
# The places named on cards: a building or a hospital is named by the town it stands in (step 27).
D_ORG_SEAT = """SELECT ?o ?hq ?ad WHERE {
  VALUES ?o { %s }
  OPTIONAL { ?o wdt:P159 ?hq }
  OPTIONAL { ?o wdt:P131 ?ad }
}"""
D_PLACE_KIND = """SELECT ?x ?l ?cls ?up ?upl WHERE {
  VALUES ?x { %s }
  OPTIONAL { ?x rdfs:label ?l . FILTER(LANG(?l) = "en") }
  OPTIONAL { ?x wdt:P31 ?cls }
  OPTIONAL { ?x wdt:P131 ?up . ?up rdfs:label ?upl . FILTER(LANG(?upl) = "en") }
}"""
D_TOWN_CLASS = """SELECT ?cls WHERE {
  VALUES ?cls { %s }
  ?cls wdt:P279* ?top .
  VALUES ?top { wd:Q486972 wd:Q56061 wd:Q515 wd:Q3957 wd:Q532 wd:Q5119 wd:Q15284 wd:Q1549591 wd:Q6256 wd:Q3624078 }
}"""
# Organisations that are really towns or lands (Kyoto, Washington, D.C.): left out (step 27).
D_ORG_TOWNS = """SELECT DISTINCT ?o WHERE {
  VALUES ?o { %s }
  ?o wdt:P31/wdt:P279* ?top .
  VALUES ?top { wd:Q486972 wd:Q56061 wd:Q6256 wd:Q3624078 wd:Q7275 }
}"""
D_FAME = """SELECT ?x ?k WHERE {
  VALUES ?x { %s }
  ?x wikibase:sitelinks ?k .
}"""
D_HOLDERS = """SELECT ?pos (COUNT(DISTINCT ?h) AS ?n) WHERE {
  VALUES ?pos { %s }
  ?h wdt:P39 ?pos .
} GROUP BY ?pos"""


def run(query, out_name, retries=6):
    """Runs one query and writes the TSV export, gzipped, to build/cards/raw/<out_name>.tsv.gz. Returns the rows."""
    os.makedirs(RAW, exist_ok=True)
    path = os.path.join(RAW, out_name + ".tsv.gz")
    if os.path.exists(path) and os.path.getsize(path) > 30:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return sum(1 for _ in f) - 1
    body = PREFIXES + query
    for attempt in range(retries):
        try:
            t = time.time()
            r = requests.post(URL, data={"query": body, "action": "tsv_export"}, timeout=900, stream=True)
            if r.status_code == 429 or r.status_code >= 500:
                raise RuntimeError(f"HTTP {r.status_code}")
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
            print(f"  {out_name}: {n - 1:,} rows in {time.time() - t:.0f} s", flush=True)
            return n - 1
        except Exception as e:  # noqa: BLE001 - every failure is retried
            wait = 5 * (attempt + 1)
            print(f"  {out_name}: {e}; again in {wait} s", flush=True)
            time.sleep(wait)
    raise SystemExit(f"{out_name}: gave up")


def values(qids):
    return " ".join("wd:" + q for q in qids)


def batches(name, template, qids, size):
    qids = sorted(set(qids), key=lambda q: int(q[1:]))
    total = 0
    for i in range(0, len(qids), size):
        total += run(template % values(qids[i:i + size]), f"{name}_{i // size:03d}")
    return total


def read_list(path):
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def pool():
    for lo, hi in POOL_BANDS:
        run(POOL % (lo, hi), f"pool_{lo}_{hi}")


def orgs():
    for kind, classes in ORG_CLASSES.items():
        run(ORGS % values(classes), f"orgs_{kind}")


def details():
    base = os.path.join(HERE, "build", "cards")
    people = read_list(os.path.join(base, "chosen_people.txt"))
    groups = read_list(os.path.join(base, "chosen_orgs.txt"))
    print(f"details for {len(people):,} people and {len(groups):,} organisations")
    batches("names_p", D_NAMES, people, 20000)
    batches("dates_b", D_DATES_B, people, 20000)
    batches("dates_d", D_DATES_D, people, 20000)
    batches("places", D_PLACES, people, 15000)
    batches("offices", D_OFFICES, people, 15000)
    for prop, role in LINK_PROPS:
        batches("links_" + role, D_LINK_ONE.replace("p:%s", "p:" + prop).replace("ps:%s", "ps:" + prop)
                .replace('"%s" AS', '"' + role + '" AS'), people, 15000)
    batches("works", D_WORKS, people, 15000)
    batches("names_o", D_ORG_NAMES, groups, 20000)
    batches("orgplace", D_ORG_PLACE, groups, 15000)


def holders():
    base = os.path.join(HERE, "build", "cards")
    positions = read_list(os.path.join(base, "positions.txt"))
    batches("holders", D_HOLDERS, positions, 5000)
    batches("names_pos", D_NAMES, positions, 20000)


def extra():
    """Step 27, second round: the kind of every place named on a card, the seats' items, the offices' and works'
    article counts (to name the best known first)."""
    base = os.path.join(HERE, "build", "cards")
    groups = read_list(os.path.join(base, "chosen_orgs.txt"))
    batches("orgseat", D_ORG_SEAT, groups, 15000)
    batches("fame_pos", D_FAME, read_list(os.path.join(base, "positions.txt")), 20000)
    batches("fame_work", D_FAME, read_list(os.path.join(base, "works.txt")), 20000)


def orgtowns():
    base = os.path.join(HERE, "build", "cards")
    batches("orgtown", D_ORG_TOWNS, read_list(os.path.join(base, "chosen_orgs.txt")), 10000)


def places():
    base = os.path.join(HERE, "build", "cards")
    batches("placekind", D_PLACE_KIND, read_list(os.path.join(base, "places.txt")), 10000)


def towns():
    base = os.path.join(HERE, "build", "cards")
    batches("townclass", D_TOWN_CLASS, read_list(os.path.join(base, "classes.txt")), 5000)


def linked_names():
    base = os.path.join(HERE, "build", "cards")
    other = read_list(os.path.join(base, "linked.txt"))
    batches("names_link", D_NAMES, other, 20000)


def main(argv):
    what = argv[0] if argv else "all"
    steps = {"pool": [pool], "orgs": [orgs], "details": [details], "holders": [holders], "linked": [linked_names], "extra": [extra], "places": [places],
             "towns": [towns], "orgtowns": [orgtowns],
             "all": [pool, orgs]}
    if what not in steps:
        raise SystemExit(__doc__)
    for step in steps[what]:
        print(f"{step.__name__}:", flush=True)
        step()


if __name__ == "__main__":
    main(sys.argv[1:])
