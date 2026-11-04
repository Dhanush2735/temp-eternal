#!/usr/bin/env python3
"""Step 42 part 1: which Wikidata properties and items actually carry law, and how many rows.

Guessed QIDs are worthless (P2596 is not 'legal system', P2482 is not 'abolition of capital
punishment'), so every identifier here is looked up by name through the Wikidata API first, and
only then counted on QLever. What matters is whether the answer is thousands of dated, placed rows
or a dozen items and a lot of prose."""
import json, urllib.request, urllib.parse, sys

API = "https://www.wikidata.org/w/api.php"
QL = "https://qlever.dev/api/wikidata"
PRE = ("PREFIX wd: <http://www.wikidata.org/entity/>\n"
       "PREFIX wdt: <http://www.wikidata.org/prop/direct/>\n"
       "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n")

def search(term, kind):
    q = urllib.parse.urlencode({"action": "wbsearchentities", "search": term, "language": "en",
                                "type": kind, "format": "json", "limit": 5})
    req = urllib.request.Request(API + "?" + q, headers={"User-Agent": "eternal-engine-data-survey/1.0 (research; contact: local)"})
    with urllib.request.urlopen(req, timeout=60) as f:
        d = json.load(f)
    return [(r["id"], r.get("label", ""), r.get("description", "")) for r in d.get("search", [])]

def qlever(q):
    body = urllib.parse.urlencode({"action": "tsv_export", "query": PRE + q}).encode()
    req = urllib.request.Request(QL, data=body,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=300) as f:
        return f.read().decode("utf-8", "replace")

def count(q):
    try:
        out = qlever(q)
        lines = [l for l in out.splitlines() if l.strip()]
        return max(0, len(lines) - 1), lines[1:4]
    except Exception as e:
        return -1, [str(e)[:100]]

for term, kind in [("legal system", "property"), ("legal code", "item"), ("date of abolition", "property"),
                   ("abolished", "property"), ("capital punishment", "item"),
                   ("women's suffrage", "item"), ("suffrage", "item"), ("slavery", "item"),
                   ("caste", "item"), ("guild", "item"), ("serfdom", "item"),
                   ("abolition of slavery", "item"), ("penalty", "item"), ("punishment", "item")]:
    hits = search(term, kind)
    print("LOOKUP %-22s (%s)" % (term, kind))
    for i, d, desc in hits:
        print("   %-12s %-42s %s" % (i, d[:42], (desc or "")[:60]))
    sys.stdout.flush()
