#!/usr/bin/env python3
"""Step 42 part 2: where the DATES are.

Reading 164 capital-punishment articles for a year each is a prose-extraction problem, and prose
extraction is where a data pack quietly goes wrong. Wikipedia's timeline pages are tables - country
and year - which is a different and far safer problem. So: which pages have tables, and what is in
them?"""
import json, urllib.request, urllib.parse, sys, time

API = "https://en.wikipedia.org/w/api.php"
UA = {"User-Agent": "eternal-engine-data-survey/1.0 (research; local)"}

PAGES = [
 "Timeline of abolition of slavery and serfdom",
 "Abolitionism",
 "Timeline of women's suffrage",
 "Women's suffrage",
 "Use of capital punishment by country",
 "Capital punishment",
 "List of countries by date of abolition of slavery",
 "Serfdom",
]

def wikitext(title):
    q = urllib.parse.urlencode({"action": "parse", "page": title, "prop": "wikitext",
                                "format": "json", "redirects": "1"})
    req = urllib.request.Request(API + "?" + q, headers=UA)
    with urllib.request.urlopen(req, timeout=90) as f:
        d = json.load(f)
    if "error" in d:
        return None
    return d["parse"]["wikitext"]["*"]

for t in PAGES:
    try:
        w = wikitext(t)
        if w is None:
            print("%-46s MISSING" % t[:46]); continue
        rows = w.count("|-")
        print("%-46s %8d chars, ~%4d table rows" % (t[:46], len(w), rows))
        # show a sample of the first table
        i = w.find('{|')
        if i >= 0:
            print("      " + w[i:i+520].replace("\n", " | ")[:500])
    except Exception as e:
        print("%-46s FAILED %s" % (t[:46], str(e)[:60]))
    sys.stdout.flush()
    time.sleep(2)
