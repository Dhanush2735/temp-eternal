#!/usr/bin/env python3
"""Harvest day-dated, georeferenced events from English Wikipedia - resumable, checkpointed.

The title list was already saved by the first pass (/tmp/titles.txt, ~2,916 articles reached from the event
categories). This pass walks it in small batches, writes a checkpoint every ten batches so an interrupted run
still leaves usable data, and stops after a cap so it always finishes.
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request

UA = "EternalEngineCrossCheck/1.0 (historical simulation research)"
OUT = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/history/dated_events.json"
CKPT = "/home/user/testrun/verify/dated_ckpt.json"
TITLES = "/home/user/testrun/verify/dated_titles.txt"
CAP = 3400          # the whole list in one run; the checkpoint makes a restart cheap either way
PAUSE = 0.9

MONTHS = {m: i + 1 for i, m in enumerate(
    ["January", "February", "March", "April", "May", "June", "July",
     "August", "September", "October", "November", "December"])}


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


def parse_date(text):
    if not text:
        return None
    t = re.sub(r"\{\{[^{}]*\}\}", " ", text)
    t = re.sub(r"<ref[^>]*>.*?</ref>", " ", t, flags=re.S)
    t = re.sub(r"\[\[([^|\]]*\|)?([^\]]*)\]\]", r"\2", t)
    bc = bool(re.search(r"BC|BCE", t))
    m = re.search(r"\b(\d{1,2})\s+(" + "|".join(MONTHS) + r")\s+(\d{3,4})\b", t, re.I)
    if m:
        return (int(m.group(3)) * (-1 if bc else 1), MONTHS[m.group(2).capitalize()], int(m.group(1)), 11)
    m = re.search(r"(" + "|".join(MONTHS) + r")\s+(\d{1,2}),?\s+(\d{3,4})\b", t, re.I)
    if m:
        return (int(m.group(3)) * (-1 if bc else 1), MONTHS[m.group(1).capitalize()], int(m.group(2)), 11)
    m = re.search(r"(" + "|".join(MONTHS) + r")\s+(\d{3,4})\b", t, re.I)
    if m:
        return (int(m.group(2)) * (-1 if bc else 1), MONTHS[m.group(1).capitalize()], 0, 10)
    m = re.search(r"\b(\d{3,4})\s*(BC|BCE)?\b", t)
    if m:
        return (int(m.group(1)) * (-1 if (bc or m.group(2)) else 1), 0, 0, 9)
    return None


def infobox_date(text):
    """The infobox's own |date=, and nothing else.

    Fixed 2026-10-27. The old version searched the first 9,000 characters of the article for any
    "|date=", which matched citation templates: "Battle of Liegnitz (1760)" was recorded as happening in
    April 2011, because a {{cite book|date=April 2011}} came first. 77 of 1,155 events were dated that way.
    Now the search starts at the infobox and citation templates are stripped before any date is read.
    """
    head = text[:9000]
    i = head.lower().find("{{infobox")
    if i < 0:
        return None
    block = head[i:]
    prev = None
    while prev != block:                    # nested citation templates, stripped inside-out
        prev = block
        block = re.sub(r"\{\{\s*(?:cite[^{}]*|citation[^{}]*)\}\}", " ", block, flags=re.I)
    for m in re.finditer(r"\|\s*date\s*=\s*([^\n|]{0,120})", block):
        p = parse_date(m.group(1))
        if p and p[0]:
            return p
    return None


def title_year(title):
    """The year a title claims for itself, e.g. "Battle of Liegnitz (1760)" -> 1760, or None."""
    m = re.search(r"\(\s*(\d{3,4})\s*\)", title)
    if not m:
        return None
    y = int(m.group(1))
    return y if 500 <= y <= 2100 else None


def contradicts(title, year):
    """True when the infobox date and the title's own year cannot both be right."""
    t = title_year(title)
    return t is not None and abs(t - year) > 30


def main():
    # The title list and the checkpoint live in the workspace, not /tmp: /tmp does not survive between
    # sessions, and the first run of this tool lost both and had to re-walk every category.
    if not os.path.exists(TITLES):
        raise SystemExit("no title list at " + TITLES + " - run tools/list_titles.py first")
    titles = [t for t in open(TITLES).read().split("\n") if t.strip()]
    done = set()
    events = []
    if os.path.exists(CKPT):
        ck = json.load(open(CKPT))
        done = set(ck["done"])
        events = ck["events"]
        print("resuming: %d already done, %d events" % (len(done), len(events)), flush=True)

    todo = [t for t in titles if t not in done][:CAP]
    print("this run: %d titles of %d remaining" % (len(todo), len(titles) - len(done)), flush=True)

    for b in range(0, len(todo), 12):
        batch = todo[b:b + 12]
        p = {"action": "query", "generator": "revisions", "grvprop": "content", "grvslots": "main",
             "titles": "|".join(batch), "prop": "coordinates|revisions",
             "rvprop": "content", "rvslots": "main", "colimit": "max"}
        pages = api(p).get("query", {}).get("pages", {})
        for _, pg in pages.items():
            co = pg.get("coordinates")
            if not co:
                continue
            rev = (pg.get("revisions") or [{}])[0].get("slots", {}).get("main", {}).get("*", "") or ""
            d = infobox_date(rev)
            if not d or not d[0] or d[0] < -3000 or d[0] > 2026:
                continue
            y, mo, dy, prec = d
            if contradicts(pg["title"], y):
                continue                    # "Battle of X (1760)" cannot have happened in 2011
            events.append([pg["title"], y, mo, dy, round(co[0]["lat"], 3), round(co[0]["lon"], 3),
                           prec, "event"])
        done.update(batch)
        if (b // 12) % 10 == 0:
            json.dump({"done": sorted(done), "events": events}, open(CKPT, "w"))
            day = sum(1 for e in events if e[6] == 11)
            print("  batch %3d: %4d events (%4d day-precise)" % (b // 12, len(events), day), flush=True)
        time.sleep(PAUSE)

    json.dump({"done": sorted(done), "events": events}, open(CKPT, "w"))
    uniq = {}
    for e in events:
        uniq[(e[0], e[1], e[2], e[3])] = e
    events = sorted(uniq.values(), key=lambda e: (e[1], e[2], e[3]))
    day = sum(1 for e in events if e[6] == 11)
    doc = {"id": "eternal-dated-events", "format": 1,
           "source": "English Wikipedia, event articles carrying a coordinate and an infobox date "
                     "(article text CC BY-SA 4.0, coordinates CC0)",
           "rule": "precision 11 = day, 10 = month, 9 = year; a news card may tell an event only once the "
                   "date it claims has been reached",
           "count": len(events), "dayPrecise": day,
           "fields": ["name", "y", "m", "d", "lat", "lon", "prec", "kind"],
           "events": events}
    with open(OUT, "w") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    print("WROTE %s with %d events, %d day-precise" % (OUT, len(events), day), flush=True)


if __name__ == "__main__":
    main()
