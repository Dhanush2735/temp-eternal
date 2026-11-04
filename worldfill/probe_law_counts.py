#!/usr/bin/env python3
"""Step 42 part 1: how much law is in Wikidata, measured with the identifiers I looked up and not
with the ones I guessed. Every count is a count of DATED rows, because an undated law is a fact
about a book and not about a year."""
import urllib.request, urllib.parse, sys, time

QL = "https://qlever.dev/api/wikidata"
PRE = ("PREFIX wd: <http://www.wikidata.org/entity/>\n"
       "PREFIX wdt: <http://www.wikidata.org/prop/direct/>\n"
       "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n")

def qlever(q):
    body = urllib.parse.urlencode({"action": "tsv_export", "query": PRE + q}).encode()
    req = urllib.request.Request(QL, data=body,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=300) as f:
        return f.read().decode("utf-8", "replace")

def go(name, q, show=3):
    try:
        out = qlever(q)
        lines = [l for l in out.splitlines() if l.strip()]
        n = max(0, len(lines) - 1)
        print("%-46s %7d" % (name[:46], n))
        for l in lines[1:1 + show]:
            print("      " + l[:150])
    except Exception as e:
        print("%-46s FAILED %s" % (name[:46], str(e)[:70]))
    sys.stdout.flush()
    time.sleep(1)

print("=== law codes: Q922203 code of law ===")
go("  all", "SELECT ?c WHERE { ?c wdt:P31/wdt:P279* wd:Q922203 }")
go("  with an inception or publication year",
   "SELECT ?c ?l ?y WHERE { ?c wdt:P31/wdt:P279* wd:Q922203 . ?c wdt:P571 ?d . "
   "OPTIONAL{?c rdfs:label ?l . FILTER(LANG(?l)='en')} BIND(YEAR(?d) AS ?y) }")
go("  with P577 publication",
   "SELECT ?c ?l ?y WHERE { ?c wdt:P31/wdt:P279* wd:Q922203 . ?c wdt:P577 ?d . "
   "OPTIONAL{?c rdfs:label ?l . FILTER(LANG(?l)='en')} BIND(YEAR(?d) AS ?y) }")

print("=== capital punishment by country: 'capital punishment in X' ===")
go("  items named 'capital punishment in ...'",
   "SELECT ?c ?l WHERE { ?c rdfs:label ?l . FILTER(LANG(?l)='en') "
   "FILTER(STRSTARTS(LCASE(?l), 'capital punishment in')) }")
go("  Q8454 capital punishment, statements",
   "SELECT (COUNT(*) AS ?n) WHERE { ?s ?p wd:Q8454 }")

print("=== women's suffrage by country ===")
go("  items named \"women's suffrage in ...\"",
   "SELECT ?c ?l WHERE { ?c rdfs:label ?l . FILTER(LANG(?l)='en') "
   "FILTER(CONTAINS(LCASE(?l), \"women's suffrage in\")) }")
go("  Q205204 women's suffrage, statements",
   "SELECT (COUNT(*) AS ?n) WHERE { ?s ?p wd:Q205204 }")

print("=== slavery / abolition by country ===")
go("  items named 'slavery in ...'",
   "SELECT ?c ?l WHERE { ?c rdfs:label ?l . FILTER(LANG(?l)='en') "
   "FILTER(STRSTARTS(LCASE(?l), 'slavery in')) }")
go("  items named 'abolition of slavery in ...'",
   "SELECT ?c ?l WHERE { ?c rdfs:label ?l . FILTER(LANG(?l)='en') "
   "FILTER(STRSTARTS(LCASE(?l), 'abolition of slavery')) }")

print("=== caste and guild ===")
go("  Q484416 caste, instance of", "SELECT ?c WHERE { ?c wdt:P31/wdt:P279* wd:Q484416 }")
go("  Q170161 guild, instance of", "SELECT ?c ?l WHERE { ?c wdt:P31/wdt:P279* wd:Q170161 . "
   "OPTIONAL{?c rdfs:label ?l . FILTER(LANG(?l)='en')} }")
