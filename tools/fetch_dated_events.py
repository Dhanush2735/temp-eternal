#!/usr/bin/env python3
"""Fetch day-dated, georeferenced events from Wikidata - the source that makes 'news by the day' possible.

Wikidata rate-limits the SPARQL endpoint to roughly one request a minute, so this walks a short list of
event classes with a pause between each and writes one combined file. Precision 11 is a day, 10 is a month,
9 is a year; the value is kept so the caller can refuse to claim day precision it does not have.
"""
import json
import time
import urllib.parse
import urllib.request

CLASSES = [
    ("battle", "Q178561"),
    ("siege", "Q188448"),
    ("earthquake", "Q7944"),
    ("treaty", "Q131569"),
    ("volcanic eruption", "Q7692360"),
    ("massacre", "Q3199915"),
    ("rebellion", "Q124734"),
    ("famine", "Q168247"),
    ("epidemic", "Q44512"),
    ("fire", "Q168903"),
]

QUERY = """
SELECT ?e ?eLabel ?date ?coord ?prec ?placeLabel WHERE {
  ?e wdt:P31 wd:%s ; wdt:P585 ?date ; wdt:P625 ?coord .
  ?e p:P585/psv:P585 ?node . ?node wikibase:timePrecision ?prec .
  OPTIONAL { ?e wdt:P276 ?place . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
"""

OUT = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/history/dated_events.json"


def query(cls, tries=3):
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode(
        {"query": QUERY % cls, "format": "json"})
    for attempt in range(tries):
        req = urllib.request.Request(url, headers={
            "User-Agent": "EternalEngineCrossCheck/1.0 (historical simulation research)",
            "Accept": "application/sparql-results+json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read().decode())["results"]["bindings"]
        except Exception as ex:
            print("   retry %d for %s: %s" % (attempt + 1, cls, str(ex)[:70]), flush=True)
            time.sleep(75)
    return []


def parse_coord(wkt):
    # "Point(28.98 41.01)"
    try:
        inner = wkt[wkt.index("(") + 1:wkt.index(")")]
        lon, lat = inner.split()
        return float(lat), float(lon)
    except Exception:
        return None


def main():
    events = []
    seen = set()
    for name, cls in CLASSES:
        rows = query(cls)
        kept = 0
        for b in rows:
            qid = b["e"]["value"].rsplit("/", 1)[-1]
            if qid in seen:
                continue
            date = b.get("date", {}).get("value", "")
            ll = parse_coord(b.get("coord", {}).get("value", ""))
            if not date or not ll:
                continue
            try:
                y = int(date[1:5]) * (-1 if date.startswith("-") else 1)
                mo = int(date[6:8]) if not date.startswith("-") else int(date[6:8])
                d = int(date[9:11]) if not date.startswith("-") else int(date[9:11])
            except Exception:
                continue
            prec = int(b.get("prec", {}).get("value", "9") or 9)
            if prec not in (9, 10, 11):
                continue
            if not (mo and d):
                prec = 9
            label = b.get("eLabel", {}).get("value", "")
            if not label or label.startswith("Q"):
                continue
            seen.add(qid)
            events.append({"qid": qid, "name": label, "y": y, "m": mo, "d": d,
                           "lat": round(ll[0], 3), "lon": round(ll[1], 3),
                           "prec": prec, "kind": name})
            kept += 1
        print("%-20s %6d rows, %6d kept" % (name, len(rows), kept), flush=True)
        time.sleep(70)

    events.sort(key=lambda e: (e["y"], e["m"], e["d"]))
    doc = {"id": "eternal-dated-events", "format": 1,
           "source": "Wikidata Query Service, items with P31 in a list of event classes, "
                     "P585 (point in time) and P625 (coordinate); CC0",
           "rule": "precision 11 = day, 10 = month, 9 = year; a news card may tell an event only once the "
                   "date it claims has been reached",
           "count": len(events), "events": [list(e.values()) for e in events],
           "fields": ["qid", "name", "y", "m", "d", "lat", "lon", "prec", "kind"]}
    with open(OUT, "w") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    print("WROTE", OUT, len(events), "events", flush=True)


if __name__ == "__main__":
    main()
