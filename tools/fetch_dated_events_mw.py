#!/usr/bin/env python3
"""Harvest day-dated, georeferenced events from English Wikipedia.

Wikidata's SPARQL endpoint rate-limits this sandbox to roughly one request a minute and refused the event
classes outright, so the same facts are taken from the articles themselves: walk a set of broad event
categories, then ask the API for each article's coordinates and its infobox `date` field in one request per
fifty articles. The date is parsed to whatever precision the article supports - day, month or year only - and
that precision is kept, because a card must never claim a day the source does not give.
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request

UA = "EternalEngineCrossCheck/1.0 (historical simulation research)"
OUT = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/history/dated_events.json"

SEEDS = [
    ("battle", "Category:Battles involving Spain"),
    ("battle", "Category:Battles involving France"),
    ("battle", "Category:Battles involving England"),
    ("battle", "Category:Battles involving the Kingdom of England"),
    ("battle", "Category:Battles involving Great Britain"),
    ("battle", "Category:Battles involving the Ottoman Empire"),
    ("battle", "Category:Battles involving the Holy Roman Empire"),
    ("battle", "Category:Battles involving Russia"),
    ("battle", "Category:Battles involving China"),
    ("battle", "Category:Battles involving Japan"),
    ("battle", "Category:Battles involving Poland"),
    ("battle", "Category:Battles involving Sweden"),
    ("battle", "Category:Battles involving Denmark"),
    ("battle", "Category:Battles involving Portugal"),
    ("battle", "Category:Battles involving the Dutch Republic"),
    ("battle", "Category:Battles involving Austria"),
    ("battle", "Category:Battles involving Prussia"),
    ("battle", "Category:Battles involving Italy"),
    ("battle", "Category:Battles involving India"),
    ("battle", "Category:Battles involving the Mughal Empire"),
    ("battle", "Category:Battles involving the Maratha Empire"),
    ("battle", "Category:Battles involving Vietnam"),
    ("battle", "Category:Battles involving Korea"),
    ("battle", "Category:Battles involving Persia"),
    ("battle", "Category:Battles involving Hungary"),
    ("battle", "Category:Battles involving Byzantium"),
    ("battle", "Category:Battles involving ancient Rome"),
    ("battle", "Category:Battles involving Greece"),
    ("battle", "Category:Battles involving Egypt"),
    ("battle", "Category:Battles involving Mexico"),
    ("battle", "Category:Battles involving Brazil"),
    ("battle", "Category:Battles involving the United States"),
    ("siege", "Category:Sieges"),
    ("earthquake", "Category:Earthquakes by country"),
    ("earthquake", "Category:Earthquakes"),
    ("volcanic eruption", "Category:Volcanic eruptions"),
    ("epidemic", "Category:Epidemics"),
    ("famine", "Category:Famines"),
    ("massacre", "Category:Massacres"),
    ("fire", "Category:Urban fires"),
    ("treaty", "Category:Peace treaties"),
]


def api(params, tries=4):
    params["format"] = "json"
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.loads(r.read().decode())
        except Exception as ex:
            if attempt == tries - 1:
                print("      give up: %s" % str(ex)[:60], flush=True)
                return {}
            time.sleep(3 * (attempt + 1))
    return {}


def category_members(cat):
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
        time.sleep(0.2)


MONTHS = {m: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"])}


def parse_date(text):
    """(year, month, day, precision) from an infobox date; month/day 0 when unknown."""
    if not text:
        return None
    t = re.sub(r"\{\{[^{}]*\}\}", " ", text)
    t = re.sub(r"<ref[^>]*>.*?</ref>", " ", t, flags=re.S)
    t = re.sub(r"\[\[([^|\]]*\|)?([^\]]*)\]\]", r"\2", t)
    bc = bool(re.search(r"BC|BCE", t))
    m = re.search(r"\b(\d{1,2})\s+(" + "|".join(MONTHS) + r")\s+(\d{3,4})\b", t, re.I)
    if m:
        y = int(m.group(3)) * (-1 if bc else 1)
        return (y, MONTHS[m.group(2).capitalize()], int(m.group(1)), 11)
    m = re.search(r"(" + "|".join(MONTHS) + r")\s+(\d{1,2}),?\s+(\d{3,4})\b", t, re.I)
    if m:
        y = int(m.group(3)) * (-1 if bc else 1)
        return (y, MONTHS[m.group(1).capitalize()], int(m.group(2)), 11)
    m = re.search(r"(" + "|".join(MONTHS) + r")\s+(\d{3,4})\b", t, re.I)
    if m:
        y = int(m.group(2)) * (-1 if bc else 1)
        return (y, MONTHS[m.group(1).capitalize()], 0, 10)
    m = re.search(r"\b(\d{3,4})\s*(BC|BCE)?\b", t)
    if m:
        y = int(m.group(1)) * (-1 if (bc or m.group(2)) else 1)
        return (y, 0, 0, 9)
    return None


def infobox_date(text):
    for field in ("date", "date_event", "date_start", "fatalities_format", ""):
        if not field:
            continue
        m = re.search(r"\|\s*" + field + r"\s*=\s*([^\n]{0,120})", text[:9000], re.I)
        if m:
            p = parse_date(m.group(1))
            if p and p[0]:
                return p
    return None


def fetch_batch(titles):
    """Coordinates and infobox date for up to 50 titles."""
    p = {"action": "query", "generator": "revisions", "grvprop": "content", "grvslots": "main",
         "titles": "|".join(titles), "prop": "coordinates|revisions",
         "rvprop": "content", "rvslots": "main", "colimit": "max"}
    return api(p).get("query", {}).get("pages", {})


def main():
    titles, kinds = set(), {}
    for kind, cat in SEEDS:
        mem = category_members(cat)
        for t in mem:
            titles.add(t)
            kinds.setdefault(t, kind)
        print("%-34s %5d members (total %d)" % (cat[9:43], len(mem), len(titles)), flush=True)
        time.sleep(0.2)

    titles = sorted(titles)
    import os
    with open("/tmp/titles.txt", "w") as tf:
        tf.write("\n".join(titles))
    print("TITLE LIST SAVED: %d" % len(titles), flush=True)
    events, seen_titles = [], 0
    for i in range(0, len(titles), 12):
        batch = titles[i:i + 12]
        pages = fetch_batch(batch)
        for _, pg in pages.items():
            seen_titles += 1
            co = pg.get("coordinates")
            if not co:
                continue
            rev = pg.get("revisions", [{}])[0].get("slots", {}).get("main", {}).get("*", "") or ""
            d = infobox_date(rev)
            if not d or not d[0]:
                continue
            y, mo, dy, prec = d
            if y < -3000 or y > 2026:
                continue
            events.append({"name": pg["title"], "y": y, "m": mo, "d": dy,
                           "lat": round(co[0]["lat"], 3), "lon": round(co[0]["lon"], 3),
                           "prec": prec, "kind": kinds.get(pg["title"], "event")})
        if (i // 12) % 20 == 0:
            print("   ...%d/%d titles, %d events" % (i, len(titles), len(events)), flush=True)
        time.sleep(1.6)

    uniq = {}
    for e in events:
        uniq[(e["name"], e["y"], e["m"], e["d"])] = e
    events = sorted(uniq.values(), key=lambda e: (e["y"], e["m"], e["d"]))
    day = sum(1 for e in events if e["prec"] == 11)
    doc = {"id": "eternal-dated-events", "format": 1,
           "source": "English Wikipedia, event articles with a coordinate and an infobox date "
                     "(text CC BY-SA 4.0, coordinates CC0)",
           "rule": "precision 11 = day, 10 = month, 9 = year; a news card may tell an event only once the "
                   "date it claims has been reached",
           "count": len(events), "dayPrecise": day,
           "fields": ["name", "y", "m", "d", "lat", "lon", "prec", "kind"],
           "events": [[e[f] for f in ["name", "y", "m", "d", "lat", "lon", "prec", "kind"]] for e in events]}
    with open(OUT, "w") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    print("WROTE", OUT, len(events), "events,", day, "day-precise", flush=True)


if __name__ == "__main__":
    main()
