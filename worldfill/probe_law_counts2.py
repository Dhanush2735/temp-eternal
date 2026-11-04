#!/usr/bin/env python3
"""The two counts the first run was rate-limited out of: per-country law, which is the only form
in which a law pack can be asked 'what was the law here, in this year?'."""
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

def go(name, q, show=5):
    for attempt in range(3):
        try:
            out = qlever(q)
            lines = [l for l in out.splitlines() if l.strip()]
            n = max(0, len(lines) - 1)
            print("%-46s %7d" % (name[:46], n))
            for l in lines[1:1 + show]:
                print("      " + l[:130])
            return
        except Exception as e:
            print("   (retry %d: %s)" % (attempt, str(e)[:50]))
            time.sleep(30)
    print("%-46s FAILED" % name[:46])
    sys.stdout.flush()

go("items named 'capital punishment in ...'",
   "SELECT ?c ?l WHERE { ?c rdfs:label ?l . FILTER(LANG(?l)='en') "
   "FILTER(STRSTARTS(LCASE(?l), 'capital punishment in')) }")
time.sleep(5)
go("items named \"women's suffrage in ...\"",
   "SELECT ?c ?l WHERE { ?c rdfs:label ?l . FILTER(LANG(?l)='en') "
   "FILTER(CONTAINS(LCASE(?l), \"women's suffrage in\")) }")
time.sleep(5)
go("items named 'slavery in ...'",
   "SELECT ?c ?l WHERE { ?c rdfs:label ?l . FILTER(LANG(?l)='en') "
   "FILTER(STRSTARTS(LCASE(?l), 'slavery in')) }")
