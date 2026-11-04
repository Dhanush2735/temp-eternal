#!/usr/bin/env python3
"""Step 42 part 1: is there a law pack in Wikidata, or only in prose?

Six questions, each asked of QLever the way the pack would have to ask it. What matters is not
the cleverness of the query but whether the answer is *thousands of dated, placed rows* or
*twelve items and a lot of prose*. Nothing is fetched beyond these counts."""
import json, urllib.request, urllib.parse, sys

URL = "https://qlever.dev/api/wikidata"

PREFIXES = """PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX ps: <http://www.wikidata.org/prop/statement/>
PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
"""

QUERIES = {
 "law codes: instance of legal code (Q213554)":
  "SELECT ?c ?l ?y WHERE { ?c wdt:P31/wdt:P279* wd:Q213554 . OPTIONAL{?c rdfs:label ?l . FILTER(LANG(?l)='en')} OPTIONAL{?c wdt:P571 ?d} BIND(YEAR(?d) AS ?y) }",
 "law codes: any item with an inception, named":
  "SELECT (COUNT(*) AS ?n) WHERE { ?c wdt:P31/wdt:P279* wd:Q213554 }",
 "legal system of a country (P2596)":
  "SELECT ?c ?cl ?s ?sl WHERE { ?c wdt:P2596 ?s . OPTIONAL{?c rdfs:label ?cl . FILTER(LANG(?cl)='en')} OPTIONAL{?s rdfs:label ?sl . FILTER(LANG(?sl)='en')} }",
 "legal system: how many countries":
  "SELECT (COUNT(*) AS ?n) WHERE { ?c wdt:P2596 ?s }",
 "women's suffrage by country (P1005)":
  "SELECT ?c ?cl ?y WHERE { ?c wdt:P1005 ?d . OPTIONAL{?c rdfs:label ?cl . FILTER(LANG(?cl)='en')} BIND(YEAR(?d) AS ?y) }",
 "suffrage P1005: how many":
  "SELECT (COUNT(*) AS ?n) WHERE { ?c wdt:P1005 ?d }",
 "capital punishment: abolition (P2482) or retention":
  "SELECT ?c ?cl ?y WHERE { ?c wdt:P2482 ?d . OPTIONAL{?c rdfs:label ?cl . FILTER(LANG(?cl)='en')} BIND(YEAR(?d) AS ?y) }",
 "P2482: how many":
  "SELECT (COUNT(*) AS ?n) WHERE { ?c wdt:P2482 ?d }",
 "slavery: abolition events (Q1128649 abolition of slavery)":
  "SELECT ?c ?cl ?y WHERE { ?c wdt:P31/wdt:P279* wd:Q1128649 . OPTIONAL{?c rdfs:label ?cl . FILTER(LANG(?cl)='en')} OPTIONAL{?c wdt:P585 ?d} BIND(YEAR(?d) AS ?y) }",
 "abolition of slavery: how many":
  "SELECT (COUNT(*) AS ?n) WHERE { ?c wdt:P31/wdt:P279* wd:Q1128649 }",
 "slavery in a country: P1069 ? no - serfdom (Q1274140)":
  "SELECT (COUNT(*) AS ?n) WHERE { ?c wdt:P31/wdt:P279* wd:Q1274140 }",
 "caste (Q191228)":
  "SELECT ?c ?cl WHERE { ?c wdt:P31/wdt:P279* wd:Q191228 . OPTIONAL{?c rdfs:label ?cl . FILTER(LANG(?cl)='en')} }",
 "social class (Q844569)":
  "SELECT (COUNT(*) AS ?n) WHERE { ?c wdt:P31/wdt:P279* wd:Q844569 }",
 "guild (Q189270)":
  "SELECT ?c ?cl WHERE { ?c wdt:P31/wdt:P279* wd:Q189270 . OPTIONAL{?c rdfs:label ?cl . FILTER(LANG(?cl)='en')} }",
 "capital punishment (Q8459) by country, via P3029?":
  "SELECT (COUNT(*) AS ?n) WHERE { ?c wdt:P31/wdt:P279* wd:Q8459 }",
}

def run(q):
    body = urllib.parse.urlencode({"action": "tsv_export", "query": PREFIXES + q}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=300) as f:
        return f.read().decode("utf-8", "replace")

for name, q in QUERIES.items():
    try:
        out = run(q)
        lines = [l for l in out.splitlines() if l.strip()]
        n = max(0, len(lines) - 1)
        print("%-52s %7d rows" % (name[:52], n))
        for l in lines[1:4]:
            print("        " + l[:150])
    except Exception as e:
        print("%-52s FAILED %s" % (name[:52], str(e)[:80]))
    sys.stdout.flush()
