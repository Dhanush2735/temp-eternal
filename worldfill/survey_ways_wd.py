#!/usr/bin/env python3
# ============================================================
# Step 34, part 1: the survey. Which Wikidata classes hold the roads,
# railways, waterways, works and deposits of the past, and how much is in each.
#
#   python3 survey_ways_wd.py --labels   what are these QIDs, really?
#   python3 survey_ways_wd.py --counts   how many items, with a point, with a year
#   python3 survey_ways_wd.py --dates    which properties carry the year, and how often
#   python3 survey_ways_wd.py --places   what the test places would gain
#
# Step 33's lesson, kept: a QID is not what its English label suggests until the
# label has been read back. Q9070 turned out to be an airport in Uruguay and not
# a sewer, so every candidate here is checked the same way before it is counted.
# ============================================================
import json
import os
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "build", "ways", "raw")
LOGS = os.path.join(HERE, "logs")
UA = "EternalEngineDataBuild/1.0 (history data; Eternal Engine Minecraft mod)"
ENDPOINTS = [
    ("wdqs", "https://query.wikidata.org/sparql", 180),
    ("wdqs-mirror", "https://query-main.wikidata.org/sparql", 240),
]

# ---------------------------------------------------------------- candidates
# Each: (guess at what it is, QID). --labels reads back what Wikidata says.
CANDIDATES = [
    # B14 railways
    ("railway line", "Q728937"),
    ("railway station", "Q55488"),
    ("railway", "Q11446"),
    ("rail transport", "Q87066"),
    ("tram line", "Q2175765"),
    ("railway tunnel", "Q1311075"),
    ("heritage railway", "Q1062310"),
    # B15 waterways
    ("canal", "Q12284"),
    ("port", "Q44782"),
    ("lighthouse", "Q39715"),
    ("bridge", "Q12280"),
    ("ship canal", "Q1195942"),
    ("aqueduct", "Q474"),
    ("lock", "Q42948"),
    ("harbour", "Q6982865"),
    ("ferry terminal", "Q1147714"),
    ("dry dock", "Q1265832"),
    # B18 industry and utilities
    ("mine", "Q820477"),
    ("factory", "Q83405"),
    ("power station", "Q15911783"),
    ("airport", "Q1248784"),
    ("watermill", "Q185156"),
    ("windmill", "Q38720"),
    ("telegraph station", "Q1140843"),
    ("telegraph line", "Q178891"),
    ("oil refinery", "Q18605661"),
    ("steam mill", "Q1127095"),
    ("sawmill", "Q214945"),
    ("steelworks", "Q1294684"),
    ("shipyard", "Q190928"),
    ("textile mill", "Q2106892"),
    ("hydroelectric power station", "Q15911783"),
    ("coal-fired power station", "Q1349813"),
    ("telephone exchange", "Q1347995"),
    ("gasworks", "Q1495314"),
    ("cement plant", "Q1051399"),
    # B24 what lies under the ground
    ("ore deposit", "Q17303275"),
    ("gold mine", "Q1339087"),
    ("coal mine", "Q8347850"),
    ("copper mine", "Q1339085"),
    ("salt mine", "Q1258342"),
    ("oil field", "Q1799315"),
    ("mineral deposit", "Q18376078"),
    ("diamond mine", "Q1213476"),
    ("iron mine", "Q1339086"),
    ("silver mine", "Q1339088"),
    ("quarry", "Q1339089"),
    ("mineral", "Q7946"),
    # B26 rest houses and road marks
    ("caravanserai", "Q192242"),
    ("milestone", "Q484523"),
    ("road marker", "Q1147779"),
    ("hospice", "Q192242"),
    ("khan", "Q641991"),
    ("post station", "Q1549591"),
    ("coaching inn", "Q11424"),
    ("guest house", "Q1193122"),
    ("serai", "Q745049"),
    ("trading post", "Q1520715"),
    # B12 roads of the past beyond the Roman
    ("road", "Q34442"),
    ("Roman road", "Q200113"),
    ("highway", "Q34442"),
    ("ancient road", "Q1520715"),
    ("trade route", "Q2166557"),
    ("pilgrim route", "Q1520715"),
]

# How many sitelinks an item must have to be worth a row: step 32 used 5,
# step 33's water works 3. Railways and mines are written about less than
# monuments, so --counts reports several floors and the decision is made after.
FLOORS = [1, 3, 5]


def ask(body, tries=3):
    last = ""
    for _ in range(tries):
        for name, url, timeout in ENDPOINTS:
            try:
                r = requests.get(url, params={"query": body, "format": "json"},
                                 headers={"User-Agent": UA}, timeout=timeout)
                if r.status_code == 200:
                    return r.json()["results"]["bindings"], name
                last = f"{name} HTTP {r.status_code}"
            except Exception as e:
                last = f"{name} {type(e).__name__}: {e}"
            time.sleep(3)
    print("   query failed:", last[:120])
    return [], last


def labels(ids):
    out = {}
    for i in range(0, len(ids), 45):
        chunk = ids[i:i + 45]
        r = requests.get("https://www.wikidata.org/w/api.php",
                         params={"action": "wbgetentities", "ids": "|".join(chunk),
                                 "props": "labels|descriptions", "languages": "en",
                                 "format": "json"},
                         headers={"User-Agent": UA}, timeout=90)
        for qid, ent in r.json().get("entities", {}).items():
            lab = ent.get("labels", {}).get("en", {}).get("value", "—")
            des = ent.get("descriptions", {}).get("en", {}).get("value", "")
            out[qid] = (lab, des)
        time.sleep(0.4)
    return out


def main():
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    mode = sys.argv[1] if len(sys.argv) > 1 else "--labels"

    if mode == "--labels":
        seen = []
        ids = []
        for guess, qid in CANDIDATES:
            if qid not in ids:
                ids.append(qid)
                seen.append((qid, guess))
        got = labels(ids)
        print(f"{'QID':10s} {'what I guessed':28s} {'what Wikidata says':34s} description")
        for qid, guess in seen:
            lab, des = got.get(qid, ("MISSING", ""))
            flag = "" if lab.lower().startswith(guess.split()[0].lower()) else "  <-- CHECK"
            print(f"{qid:10s} {guess:28s} {lab[:34]:34s} {des[:60]}{flag}")
        return

    # The classes to count. Filled in from --labels; kept here so the counts
    # can be re-run without re-reading every label.
    classes = json.load(open(os.path.join(RAW, "classes.json"))) \
        if os.path.exists(os.path.join(RAW, "classes.json")) else [q for _, q in CANDIDATES]

    if mode == "--counts":
        rows = {}
        for qid in classes:
            body = f"""
            SELECT
              (COUNT(DISTINCT ?item) AS ?items)
              (COUNT(DISTINCT ?coord) AS ?pointed)
              (COUNT(DISTINCT ?datedItem) AS ?dated)
            WHERE {{
              ?item wdt:P31/wdt:P279* wd:{qid} .
              OPTIONAL {{ ?item wdt:P625 ?coord . }}
              OPTIONAL {{ ?item wdt:P571|wdt:P1619 ?d . BIND(?item AS ?datedItem) }}
            }}"""
            got, ep = ask(body)
            if got:
                b = got[0]
                rows[qid] = {"items": int(b["items"]["value"]),
                             "pointed": int(b["pointed"]["value"]),
                             "dated": int(b["dated"]["value"])}
                print(f"  {qid:10s} {rows[qid]['items']:>8,} items  "
                      f"{rows[qid]['pointed']:>8,} with a point  {rows[qid]['dated']:>8,} with a year")
            else:
                print(f"  {qid:10s} FAILED ({ep[:40]})")
            time.sleep(1.5)
        json.dump(rows, open(os.path.join(RAW, "counts.json"), "w"), indent=1)
        print("\n  written: build/ways/raw/counts.json")
        return

    if mode == "--dates":
        # Which property carries the year, and how often: P571 inception,
        # P1619 date of official opening, P580 start time, P1319/ P569 ...
        props = [("P571", "inception"), ("P1619", "date of official opening"),
                 ("P580", "start time"), ("P7124", "date of official closure"),
                 ("P576", "dissolved/abolished"), ("P625", "coordinate location")]
        body = """
        SELECT ?prop (COUNT(DISTINCT ?item) AS ?n) WHERE {
          VALUES ?cls { %s }
          VALUES ?prop { %s }
          ?item wdt:P31/wdt:P279* ?cls ; wdt:P625 ?coord ; ?prop ?v .
        } GROUP BY ?prop""" % (
            " ".join("wd:" + c for c in classes[:12]),
            " ".join("wdt:" + p for p, _ in props))
        got, ep = ask(body)
        named = dict(props)
        for b in got:
            p = b["prop"]["value"].rsplit("/", 1)[-1]
            print(f"  {p:6s} {named.get(p, ''):28s} {int(b['n']['value']):>9,}")
        return


if __name__ == "__main__":
    main()
