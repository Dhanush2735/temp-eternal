#!/usr/bin/env python3
"""Step 42 part 1: what the PRIMARY source holds. The user's standing constraint is Wikipedia
first, and step 41 showed Wikidata is thin on law (761 codes, 197 of them dated). So: how many
per-country law articles does English Wikipedia actually have? Counted through the category API,
which is cheap and does not touch QLever."""
import json, urllib.request, urllib.parse, sys, time

API = "https://en.wikipedia.org/w/api.php"
UA = {"User-Agent": "eternal-engine-data-survey/1.0 (research; local)"}

def catsize(name):
    q = urllib.parse.urlencode({"action": "query", "list": "categorymembers", "cmtitle": "Category:" + name,
                                "cmlimit": "500", "cmtype": "subcat|page", "format": "json"})
    req = urllib.request.Request(API + "?" + q, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as f:
        d = json.load(f)
    m = d.get("query", {}).get("categorymembers", [])
    subs = [x["title"] for x in m if x["ns"] == 14]
    pages = [x["title"] for x in m if x["ns"] == 0]
    return len(pages), len(subs), subs[:6], pages[:5]

NAMES = [
 "Capital punishment by country",
 "Law by country",
 "Legal codes",
 "Women's suffrage by country",
 "Suffrage by country",
 "Slavery by country",
 "Abolition of slavery",
 "Serfdom",
 "Caste",
 "Guilds",
 "Legal history by country",
 "Legal systems by country",
 "Crime by country",
 "Law enforcement by country",
 "Prisons by country",
 "Border control",
 "Passports by country",
 "Customs (tax)",
]

for n in NAMES:
    try:
        pages, subs, subnames, pagenames = catsize(n)
        print("%-32s %4d articles, %4d subcategories" % (n[:32], pages, subs))
        for s in subnames:
            print("        cat: " + s[9:70])
        for s in pagenames:
            print("            " + s[:66])
    except Exception as e:
        print("%-32s FAILED %s" % (n[:32], str(e)[:60]))
    sys.stdout.flush()
    time.sleep(0.5)
