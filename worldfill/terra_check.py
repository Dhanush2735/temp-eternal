#!/usr/bin/env python3
"""Step 31 (system B7): check Terra++'s buildings and roads by year in the test places.

Terra++ (the user's fork in /home/user/terra3) shows today's mapped buildings and roads in the past by giving each a
start year: an explicit start_date tag, a Wikidata date by name, or an estimate (StructureDateEstimator: the dated
structures within 500 m pull the year toward theirs; with none, a floor per world region; and a floor per kind of
thing, such as no railways before 1825). This script fetches what OpenStreetMap maps today around the 31 named places of
the world-wide test set (SYSTEMS_PLAN.md part 9) and runs Terra++'s own dating code on it (probes/TerraDatingProbe.java,
compiled from the terra3 sources), first alone and then with the Eternal Engine's place-aware estimate (town growth,
settlement, the technology atlas), and compares what each shows in each year with what the mod knows of the place.

    python3 terra_check.py --fetch     download the OSM ways around each place (build/terra/, not kept; Overpass API)
    bash probe_terra.sh                compile and run the dating probe (writes logs/step31_terra_report.txt)

Not checked here: the Wikidata-by-name step (it needs the network inside the game; named buildings are few) and OHM
(OpenHistoricalMap) data, which Terra++ asks first where it has any.
"""
import json
import os
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "build", "terra")

# Overpass mirrors, tried in rotation. The main endpoint answers 502 for long
# stretches while it rebuilds slots; Terra++ itself keeps three (see
# OsmStructureIndex.OVERPASS_ENDPOINTS), so the fetcher does the same.
# overpass.osm.ch is deliberately NOT used: it answers HTTP 200 with an empty
# database (timestamp_osm_base "117750"), which would silently look like a town
# with no buildings.
URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    # overpass.osm.jp is listed in some mirrors but its certificate does not
    # match the hostname, so every request raises SSLCertVerificationError.
]
RADIUS = 400

# Endpoints go up and down minute by minute (the main one answers 502 in long
# stretches while it rebuilds slots). Each endpoint carries a penalty that is
# cleared on success and raised on failure, so a dead mirror is tried once per
# place instead of blocking the sweep.
PENALTY = {u: 0 for u in URLS}

# The named places of the world-wide test set (SYSTEMS_PLAN.md part 9), with the year each is named for.
PLACES = [
    ("Ur", 30.9625, 46.1031, -2500), ("Giza", 29.9792, 31.1342, -2500), ("Mohenjo-daro", 27.3242, 68.1356, -2500),
    ("Anyang", 36.1000, 114.3500, -1200), ("Athens", 37.9715, 23.7257, -430), ("Pataliputra (Patna)", 25.5940, 85.1370, -300),
    ("Rome", 41.8925, 12.4853, 100), ("Teotihuacan", 19.6925, -98.8438, 500), ("Chang'an (Xi'an)", 34.2611, 108.9422, 750),
    ("Baghdad", 33.3152, 44.3661, 900), ("Greenland's Norse farms", 61.1550, -45.5170, 1000),
    ("Cahokia", 38.6603, -90.0618, 1100), ("Angkor", 13.4125, 103.8670, 1150), ("Great Zimbabwe", -20.2675, 30.9339, 1300),
    ("Timbuktu", 16.7735, -3.0074, 1350), ("Tenochtitlan (Mexico City)", 19.4326, -99.1332, 1500),
    ("Cusco", -13.5163, -71.9785, 1500), ("the Amazon", -3.4653, -62.2159, 1500), ("Vijayanagara (Hampi)", 15.3350, 76.4600, 1520),
    ("Delhi", 28.6562, 77.2410, 1650), ("Edo (Tokyo)", 35.6852, 139.7528, 1700), ("London", 51.5074, -0.1278, 1700),
    ("Paris", 48.8566, 2.3522, 1789), ("Sydney", -33.8688, 151.2093, 1850), ("New York", 40.7128, -74.0060, 1920),
    ("Hyderabad", 17.3616, 78.4747, 1948), ("Lagos", 6.4541, 3.3947, 1960), ("Moscow", 55.7520, 37.6175, 1980),
    ("São Paulo", -23.5505, -46.6333, 2020), ("Siberia (Yakutsk)", 62.0355, 129.6755, 1900), ("the Sahara", 23.4162, 25.6628, 1000),
]


def slug(name):
    # Fold accents to ASCII first: "Sao Paulo" and "Sao_Paulo" must be the same
    # file name on disk and for the Java probe. str.isalnum() is True for "a",
    # which produced a file name Java's Path.of() cannot read back.
    import unicodedata

    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return "".join(c.lower() if c.isalnum() else "_" for c in ascii_name).strip("_")


def fetch():
    os.makedirs(OUT, exist_ok=True)
    for name, lat, lon, _year in PLACES:
        path = os.path.join(OUT, f"osm_{slug(name)}.json")
        if os.path.exists(path) and os.path.getsize(path) > 50:
            continue
        q = f"""[out:json][timeout:120];
(
  way["building"](around:{RADIUS},{lat},{lon});
  way["highway"](around:{RADIUS},{lat},{lon});
  way["railway"](around:{RADIUS},{lat},{lon});
  way["historic"](around:{RADIUS},{lat},{lon});
  way["amenity"="place_of_worship"](around:{RADIUS},{lat},{lon});
);
out tags geom;"""
        got = False
        for attempt in range(12):
            url = min(URLS, key=lambda u: (PENALTY[u], URLS.index(u)))
            host = url.split("/")[2]
            try:
                r = requests.post(url, data={"data": q}, timeout=120,
                                  headers={"User-Agent": "EternalEngineDataBuild/1.0 (history data; test places)"})
                if r.status_code in (429, 500, 502, 503, 504):
                    raise RuntimeError(f"HTTP {r.status_code}")
                r.raise_for_status()
                data = r.json()
                n = len(data.get("elements", []))
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f)
                PENALTY[url] = 0
                print(f"  {name}: {n} ways  [{host}]", flush=True)
                got = True
                break
            except Exception as e:  # noqa: BLE001 - retried
                PENALTY[url] = PENALTY[url] + 1
                wait = 5 + 5 * (attempt // len(URLS))
                print(f"  {name}: {e} at {host}; again in {wait} s", flush=True)
                time.sleep(wait)
        if not got:
            print(f"  {name}: FAILED - no endpoint answered; re-run to retry"
                  f" (finished places are kept)", flush=True)
        time.sleep(2)
    with open(os.path.join(OUT, "places.json"), "w", encoding="utf-8") as f:
        json.dump([{"name": n, "slug": slug(n), "lat": a, "lon": b, "year": y} for n, a, b, y in PLACES], f, indent=1)


def main(argv):
    if len(argv) > 1 and argv[1] == "--fetch":
        fetch()
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
