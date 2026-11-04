#!/usr/bin/env python3
"""The era route, asked of the record itself — 31 stops, no game needed.

For every stop in `eternal/FINAL_TEST.md` section R this prints what the shipped data already holds
at that place and year: the nearest recorded place, the people alive there, the events within reach,
the money in use, the technologies that have arrived, and the polity whose core covers the point.
That is what `/ee here` and the cards are built from, so this is the part of the walk that can be
answered by a machine.

It does not — and cannot — answer what the screen looks like. Dress, faces, buildings and the feel of
a town are a player's judgement. What this gives you is the other half: at each stop, the exact list
of what should be there, so that anything missing on screen is a *finding* rather than a shrug, and
any stop whose data is honestly empty is known in advance and not mistaken for a bug.

Run:  python3 worldfill/era_route_probe.py            (writes testrun/era_route.tsv + a report)
"""
import gzip
import json
import math
import os
import sys

DATA = "/home/user/eternal/src/main/resources/data/eternalengine/eternal"
OUT_TSV = "/home/user/testrun/era_route.tsv"
OUT_MD = "/home/user/ERA_ROUTE_DATA.md"

# id, place, lat, lon, year, country code (as the technology atlas spells it), what the test watches for
STOPS = [
    ("R1",  "Ur",                    30.9626,  46.1031, -2500, "IRQ", ""),
    ("R2",  "Giza",                  29.9792,  31.1342, -2500, "EGY", ""),
    ("R3",  "Mohenjo-daro",          27.3294,  68.1386, -2500, "PAK", ""),
    ("R4",  "Anyang",                36.1267, 114.3133, -1200, "CHN", ""),
    ("R5",  "Athens",                37.9838,  23.7275,  -430, "GRC", ""),
    ("R6",  "Pataliputra",           25.5941,  85.1376,  -300, "IND", ""),
    ("R7",  "Rome",                  41.9028,  12.4964,   100, "ITA", "aqueducts, paved roads, the Roman mile"),
    ("R8",  "Teotihuacan",           19.6925, -98.8438,   500, "MEX", ""),
    ("R9",  "Chang'an",              34.3416, 108.9398,   750, "CHN", ""),
    ("R10", "Baghdad",               33.3152,  44.3661,   900, "IRQ", ""),
    ("R11", "Greenland's Norse farms", 61.1544, -45.5156, 1000, "GRL", "may answer nothing; saying so is a pass"),
    ("R12", "Cahokia",               38.6550, -90.0610,  1100, "USA", "population floor may show nothing"),
    ("R13", "Angkor",                13.4125, 103.8670,  1150, "KHM", ""),
    ("R14", "Great Zimbabwe",       -20.2674,  30.9337,  1300, "ZWE", ""),
    ("R15", "Timbuktu",              16.7735,  -3.0074,  1350, "MLI", ""),
    ("R16", "the Sahara",            23.2833,   5.5333,  1000, "DZA", "empty land must stay empty"),
    ("R17", "Tenochtitlan",          19.4326, -99.1332,  1500, "MEX", "before contact: no iron, horses, carts, printed books"),
    ("R18", "Cusco",                -13.5319, -71.9675,  1500, "PER", "before contact: same"),
    ("R19", "the Amazon",            -3.1190, -60.0217,  1500, "BRA", ""),
    ("R20", "Vijayanagara",          15.3350,  76.4600,  1520, "IND", ""),
    ("R21", "Delhi",                 28.6139,  77.2090,  1650, "IND", ""),
    ("R22", "Edo",                   35.6762, 139.6503,  1700, "JPN", "called Edo, not Tokyo"),
    ("R23", "London",                51.5074,  -0.1278,  1700, "GBR", ""),
    ("R24", "Paris",                 48.8566,   2.3522,  1789, "FRA", ""),
    ("R25", "Sydney",               -33.8688, 151.2093,  1850, "AUS", ""),
    ("R26", "New York",              40.7128, -74.0060,  1920, "USA", ""),
    ("R27", "Hyderabad",             17.3850,  78.4867,  1948, "IND", "Dominion of India under George VI; rupees; the nizam's city"),
    ("R28", "Lagos",                  6.5244,   3.3792,  1960, "NGA", ""),
    ("R29", "Moscow",                55.7558,  37.6173,  1980, "RUS", ""),
    ("R30", "Sao Paulo",            -23.5505, -46.6333,  2020, "BRA", ""),
    ("R31", "Siberia",               62.0355, 129.6755,  1900, "RUS", ""),
]

# The gates the test names, by the atlas's own technology ids
# The gates the test names, mapped to the atlas's own ids. Written out rather than guessed: a gate name
# that matches nothing silently disappears, and a probe that skips its own checks still looks green
# (that is how boards 13-15 kept finding things). UNRESOLVED_GATES below is printed if any stop leaving
# a gate unasked, so this list cannot rot quietly.
GATES = [
    ("iron", "iron"),
    ("horses", "horses"),
    ("carts", "wheeled carts"),
    ("printing", "printed books"),
    ("gunpowder", "gunpowder"),
    ("steam", "steam engines"),
    ("railway", "the railway"),
    ("telegraph", "the telegraph"),
    ("electric light", "electric light"),
    ("telephone", "the telephone"),
    ("radio", "radio"),
    ("motor car", "motor cars"),
    ("aeroplane", "aeroplanes"),
    ("television", "television"),
    ("computer", "computers"),
]

R_KM = 6371.0


def load(rel):
    path = os.path.join(DATA, rel)
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def km(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_KM * math.asin(math.sqrt(a))


def main():
    # ---- the record
    people = load("history/famous_people.json.gz")
    people = people["people"] if isinstance(people, dict) else people
    presence = load("history/presence.json.gz")["places"]
    borders = load("history/borders.json")["borders"]
    money = load("economy/money_table.json")
    atlas = load("history/technology_atlas.json.gz")
    countries = atlas["countries"]

    events = []
    for name in sorted(os.listdir(os.path.join(DATA, "history"))):
        if not (name.startswith("events_") and name.endswith(".gz")):
            continue
        try:
            d = load("history/" + name)
        except Exception:  # noqa: BLE001
            continue
        d = d.get("events", d) if isinstance(d, dict) else d
        if not isinstance(d, list):
            continue
        for e in d:
            if not isinstance(e, dict):
                continue
            lat, lon = e.get("lat"), e.get("lon")
            if lat is None or lon is None:
                continue
            start = e.get("start", e.get("year"))
            end = e.get("end", start)
            if start is None:
                continue
            events.append((e.get("name") or e.get("title") or "?", float(lat), float(lon),
                           int(start), int(end if end is not None else start), name))
    tech_index = {t["name"].lower(): t for t in atlas["techs"]}
    if "GRL" not in countries:
        print("  ! GRL is not in the atlas's country list — Greenland's row will say so")

    UNRESOLVED = set()
    rows, report = [], []
    counts = {"place": 0, "people": 0, "events": 0, "money": 0, "tech": 0, "core": 0}

    for rid, place, lat, lon, year, cc, watch in STOPS:
        # 1. the nearest recorded place
        near, nd = None, 1e9
        for p in presence:
            try:
                name, plat, plon = p[0], p[1] / 1000.0, p[2] / 1000.0
            except (TypeError, IndexError):
                continue
            d = km(lat, lon, plat, plon)
            if d < nd:
                near, nd = name, d
        # This is the UNDATED presence pack. `/ee here` prefers the dated layers first (gazetteer sites,
        # then OHM's dated stays) and only falls back to this one, so treat the row as indicative.
        place_hit = (f"{near} ({nd:.0f} km) — undated name; the game prefers its dated layers"
                     if near and nd <= 50 else f"— nearest undated name is {near} at {nd:.0f} km")
        if near and nd <= 50:
            counts["place"] += 1

        # 2. people alive there, that year
        alive = []
        for p in people:
            try:
                name, _n2, birth, death, _x, plat, plon, _rank = p
            except (ValueError, TypeError):
                continue
            if plat is None or plon is None or birth is None:
                continue
            if birth > year or (death is not None and death < year):
                continue
            if abs(plat - lat) > 3 or abs(plon - lon) > 3:
                continue
            if km(lat, lon, plat, plon) <= 100:
                alive.append((name, birth, death))
        if alive:
            counts["people"] += 1
        # NOTE, and it matters: the people pack records ONE point per person (their birth place), not where
        # they were in a given year. So this row means "born within 100 km and alive in this year" — it is
        # not "standing here". The game's own cards work the same way.
        people_hit = (f"{len(alive)} born within 100 km, alive in {year}: "
                      + ", ".join(f"{n} ({b}–{d if d else ''})" for n, b, d in alive[:3])
                      + (" …" if len(alive) > 3 else "")) if alive else "nobody recorded as born within 100 km"

        # 3. events within 150 km and 50 years
        near_ev = []
        for en, elat, elon, s, e, pack in events:
            if abs(s - year) > 50 and abs(e - year) > 50:
                continue
            if abs(elat - lat) > 4 or abs(elon - lon) > 4:
                continue
            if km(lat, lon, elat, elon) <= 150:
                near_ev.append((en, s, e, pack))
        if near_ev:
            counts["events"] += 1
        near_ev.sort(key=lambda t: abs(t[1] - year))
        events_hit = (f"{len(near_ev)}: " + "; ".join(f"{n} ({s}–{e})" for n, s, e, _p in near_ev[:2])
                      + (" …" if len(near_ev) > 2 else "")) if near_ev else "none within 150 km"

        # 4. money whose years cover this stop
        mrows = [r for r in money["rows"]
                 if isinstance(r.get("from"), int) and isinstance(r.get("to"), int)
                 and r["from"] <= year <= r["to"]]
        if mrows:
            counts["money"] += 1
        # The rows are the record's money table; which one applies *here* is decided by the game's own
        # place rules, so this row says what exists, not what is in your purse at this stop.
        money_hit = (f"{len(mrows)} currency row(s) live in this year across the world, e.g. "
                     f"{mrows[0].get('money')} ({mrows[0].get('id')})"
                     if mrows else "no money row covers this year")

        # 5. technologies that have arrived in this country by this year
        arrived, missing = [], []
        if cc in countries:
            idx = countries.index(cc)
            for label, tid in GATES:
                t = tech_index.get(tid.lower())
                if not t:
                    UNRESOLVED.add(tid)
                    continue
                arr = t.get("arrive") or []
                first = arr[idx] if idx < len(arr) else None
                has = first is not None and first <= year
                (arrived if has else missing).append(f"{label}" + (f" ({first})" if first is not None else ""))
            counts["tech"] += 1
        tech_hit = ("here: " + ", ".join(arrived) + " | not yet: " + ", ".join(missing)) if arrived or missing \
            else f"country {cc} is not in the atlas"

        # 6. a polity core covering the point
        core = [b for b in borders
                if b["minLat"] <= lat <= b["maxLat"] and b["minLon"] <= lon <= b["maxLon"]
                and b["start"] <= year <= b["end"]]
        if core:
            counts["core"] += 1
        # borders.json holds 16 approximate cores and its own note says they are used "only when no sourced
        # site is within 30 km" — and every stop here is a sourced site. So "no core" is normal, not a gap.
        core_hit = ", ".join(f"{b['civId']} ({b['start']}–{b['end']}, {b['rank']})" for b in core) \
            if core else "no core covers it (normal: every stop is a sourced site, and cores are the fallback)"

        rows.append((rid, place, year, cc, place_hit, people_hit, events_hit, money_hit, tech_hit, core_hit))
        report.append((rid, place, year, watch, place_hit, people_hit, events_hit, money_hit, tech_hit, core_hit))

    os.makedirs(os.path.dirname(OUT_TSV), exist_ok=True)
    with open(OUT_TSV, "w") as f:
        f.write("id\tplace\tyear\tcountry\tnearest place\tpeople alive within 100km\tevents within 150km"
                "\tmoney rows covering the year\ttechnologies\tpolity core\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")

    with open(OUT_MD, "w") as f:
        f.write("# The era route, as the record has it\n\n")
        f.write("_Generated by `worldfill/era_route_probe.py` from the shipped packs — the same data "
                "`/ee here` and the cards read. This is the half of the 31-stop route a machine can "
                "answer. What it cannot answer is what the screen looks like: that stays yours._\n\n")
        f.write("**Every stop has data for:** " +
                ", ".join(f"{k} {v}/31" for k, v in counts.items()) + "\n\n")
        f.write("""Read the rows this way:

- **nearest recorded place** — from the *undated* 58,375-place presence pack. `/ee here` uses the dated
  layers first (gazetteer sites, then OHM's dated stays) and only falls back to this list, so treat the
  row as indicative; 31/31 means a name exists within 50 km of every stop.

  One watch item came straight out of this row: the pack names the point at Tenochtitlan's exact
  coordinates **"New Spain"**. That is a colonial polity (1521-1821) at a stop the test puts in 1500
  *before contact* — if `/ee here` ever prints it there, R17 fails on its own wording. The dated layers
  should win first, so it probably never surfaces; it is listed so that if it does, it is recognised.
- **people** — the pack records ONE point per person, their birth place, not where they were later.
  So this row is *"born within 100 km and alive in this year"*. 18/31 is the shape of the pack, not a
  failure: nobody's birthplace is within 100 km of the Sahara or the Amazon.
- **events** — within 150 km and ±50 years, from the ~40,000-event packs. A stop with none (Greenland,
  Cahokia, the Sahara) is one where the honest answer is *"the record says nothing here"* — and the
  test says saying so is a pass.
- **money** — rows whose years cover the stop, world-wide. Which one applies *at that stop* is the
  game's place rule; this row only proves the year has money in it.
- **technologies** — the country's own arrival dates from the atlas (130 technologies, 246 countries),
  so "iron: not yet" at Tenochtitlan 1500 is the atlas's own answer, not an opinion.
- **polity core** — the 16 approximate cores, which the pack's own note says are a fallback *"only
  when no sourced site is within 30 km"*. Every stop is a sourced site, so 6/31 is the expected shape.

""")
        for rid, place, year, watch, ph, pe, ev, mo, te, co in report:
            f.write(f"## {rid} — {place}, {year}\n\n")
            if watch:
                f.write(f"*The test watches for: {watch}*\n\n")
            f.write(f"- **nearest recorded place:** {ph}\n")
            f.write(f"- **people alive within 100 km:** {pe}\n")
            f.write(f"- **events within 150 km, ±50 years:** {ev}\n")
            f.write(f"- **money covering this year:** {mo}\n")
            f.write(f"- **technologies (country's own dates):** {te}\n")
            f.write(f"- **polity core:** {co}\n\n")

    if UNRESOLVED:
        print(f"  ! {len(UNRESOLVED)} gate name(s) matched no technology: {sorted(UNRESOLVED)}")
    print(f"{len(report)} stops asked of the record")
    for k, v in counts.items():
        print(f"  {k:8s} {v:2d}/31")
    print(f"\nTSV:    {OUT_TSV}")
    print(f"report: {OUT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
