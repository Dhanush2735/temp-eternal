#!/usr/bin/env python3
"""Walk the event categories and save the candidate article titles into the workspace.

The first pass wrote this list to /tmp, which does not survive between sessions, so it had to be rebuilt.
It lives in testrun/verify/dated_titles.txt now and the harvest resumes against it.
"""
import json
import time
import urllib.parse
import urllib.request

UA = "EternalEngineCrossCheck/1.0 (historical simulation research)"
OUT = "/home/user/testrun/verify/dated_titles.txt"

SEEDS = [
    "Category:Battles involving Spain", "Category:Battles involving France",
    "Category:Battles involving England", "Category:Battles involving the Kingdom of England",
    "Category:Battles involving Great Britain", "Category:Battles involving the Ottoman Empire",
    "Category:Battles involving the Holy Roman Empire", "Category:Battles involving Russia",
    "Category:Battles involving China", "Category:Battles involving Japan",
    "Category:Battles involving Poland", "Category:Battles involving Sweden",
    "Category:Battles involving Denmark", "Category:Battles involving Portugal",
    "Category:Battles involving the Dutch Republic", "Category:Battles involving Austria",
    "Category:Battles involving Prussia", "Category:Battles involving Italy",
    "Category:Battles involving India", "Category:Battles involving the Mughal Empire",
    "Category:Battles involving the Maratha Empire", "Category:Battles involving Vietnam",
    "Category:Battles involving Korea", "Category:Battles involving Persia",
    "Category:Battles involving Hungary", "Category:Battles involving Byzantium",
    "Category:Battles involving ancient Rome", "Category:Battles involving Greece",
    "Category:Battles involving Egypt", "Category:Battles involving Mexico",
    "Category:Battles involving Brazil", "Category:Battles involving the United States",
    "Category:Battles involving Scotland", "Category:Battles involving Ireland",
    "Category:Battles involving Norway", "Category:Battles involving Finland",
    "Category:Battles involving Serbia", "Category:Battles involving Bulgaria",
    "Category:Battles involving Romania", "Category:Battles involving Africa",
    "Category:Sieges", "Category:Earthquakes by country", "Category:Earthquakes",
    "Category:Volcanic eruptions", "Category:Epidemics", "Category:Famines",
    "Category:Massacres", "Category:Urban fires", "Category:Peace treaties",
]


def api(params, tries=4):
    params["format"] = "json"
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode())
        except Exception:
            if attempt == tries - 1:
                return {}
            time.sleep(4 * (attempt + 1))
    return {}


def members(cat):
    out, cont = [], None
    while True:
        p = {"action": "query", "list": "categorymembers", "cmtitle": cat,
             "cmlimit": "500", "cmnamespace": "0"}
        if cont:
            p["cmcontinue"] = cont
        d = api(p)
        out.extend(m["title"] for m in d.get("query", {}).get("categorymembers", []))
        cont = d.get("continue", {}).get("cmcontinue")
        if not cont:
            return out
        time.sleep(0.3)


def main():
    titles = set()
    for cat in SEEDS:
        m = members(cat)
        titles.update(m)
        print("%-46s %4d (total %d)" % (cat[9:55], len(m), len(titles)), flush=True)
        time.sleep(0.5)
    titles = sorted(titles)
    with open(OUT, "w") as f:
        f.write("\n".join(titles))
    print("WROTE %s with %d titles" % (OUT, len(titles)), flush=True)


if __name__ == "__main__":
    main()
