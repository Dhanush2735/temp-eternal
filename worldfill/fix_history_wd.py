#!/usr/bin/env python3
"""Step 25: Wikidata look-ups for the history data fix (run once; the answers are saved, so
fix_history_data.py runs offline).

What it asks Wikidata (through the QLever endpoint, CC0), for every state of polity_facts.json.gz:
  - the office its head of state holds (P1906) and the office its head of government holds (P1313);
  - everyone who held those offices (P39) with the start (P580) and end (P582) of each term.
The fix uses these terms only to fill years the Wikipedia-built lists leave empty, to end reigns the
builder guessed, and to give a head of state where the lists named only a prime minister. Wikipedia
stays first: a Wikipedia row is never replaced by a Wikidata one.

Usage: python3 fix_history_wd.py            (writes worldfill/sources/step25_offices.json.gz)
"""
import gzip
import io
import json
import sys
import time
import urllib.parse
import urllib.request

ENDPOINT = "https://qlever.dev/api/wikidata"
HIST = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/history"
OUT = "/home/user/worldfill/sources/step25_offices.json.gz"
UA = "EternalEngineWorldFill/1.0 (historical data fix; research use)"
PFX = ("PREFIX wd: <http://www.wikidata.org/entity/> PREFIX wdt: <http://www.wikidata.org/prop/direct/> "
       "PREFIX p: <http://www.wikidata.org/prop/> PREFIX ps: <http://www.wikidata.org/prop/statement/> "
       "PREFIX pq: <http://www.wikidata.org/prop/qualifier/> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> ")


EXTRA_HEAD_OFFICES = {
    "Q70802": ["President of France", "President of the French Republic"],   # French Third Republic
    "Q187830": ["President of Austria"],               # Second Republic of Austria
    "Q33946": ["President of Czechoslovakia"],         # Czechoslovakia
    "Q209065": ["King of the Hellenes", "King of Greece"],
    "Q41": ["President of Greece", "King of the Hellenes"],
    "Q36": ["President of Poland"],                    # Republic of Poland
    "Q207272": ["President of Poland"],                # Second Polish Republic
    "Q28": ["President of Hungary", "Regent of Hungary"],
    "Q16410": ["President of Hungary"],                # Hungarian People's Republic
    "Q794": ["Supreme Leader of Iran"],
    "Q235": ["Prince of Monaco"],
    "Q34266": ["Emperor of all the Russias"],
    "Q131964": ["Emperor of Austria"],                 # Austrian Empire
    "Q28513": ["Emperor of Austria"],                  # Austria-Hungary
    "Q153136": ["Holy Roman Emperor", "Archduke of Austria"],   # Habsburg Monarchy
    "Q43287": ["German Emperor"],                      # German Empire
    "Q41304": ["President of Germany"],                # Weimar Republic
    "Q16957": ["Chairman of the State Council of East Germany", "President of East Germany"],
    "Q71084": ["Emperor of the French"],               # First French Empire
    "Q71092": ["Emperor of the French"],               # Second French Empire
    "Q790": ["President of Haiti"],
    "Q1016": ["Brotherly Leader and Guide of the Revolution"],
    "Q2347668": ["Brotherly Leader and Guide of the Revolution", "Chairman of the Revolutionary Command Council"],
    "Q191764": ["President of the State Presidium of Democratic Kampuchea"],
    "Q424": ["King of Cambodia", "Monarch of Cambodia"],
    "Q213": ["President of the Czech Republic"], "Q214": ["President of Slovakia"],
    "Q30": ["President of the United States"],
    "Q31": ["Monarch of Belgium", "King of the Belgians"],
    "Q38": ["President of Italy"], "Q172579": ["King of Italy"],
    "Q29": ["Monarch of Spain", "President of Spain"],
    "Q403": ["President of Serbia"], "Q83286": ["President of Yugoslavia"],
    "Q15102440": ["King of Yugoslavia"],              # Kingdom of Serbs, Croats and Slovenes
    "Q884": ["President of South Korea"], "Q423": ["Supreme Leader of North Korea"],
    "Q148": ["Chairman of the Chinese Communist Party", "President of the People's Republic of China"],
    "Q865": ["President of the Republic of China"],
    "Q17": ["Emperor of Japan"], "Q188712": ["Emperor of Japan"],
    "Q36": ["President of Poland", "Chairman of the State National Council"],
}


def tsv(query, tries=4):
    data = urllib.parse.urlencode({"query": PFX + query, "action": "tsv_export"}).encode()
    for i in range(tries):
        try:
            req = urllib.request.Request(ENDPOINT, data=data, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=300) as r:
                text = r.read().decode("utf-8")
            rows = [line.split("\t") for line in text.split("\n")[1:] if line.strip()]
            return rows
        except Exception as e:  # noqa: BLE001
            print("  retry", i + 1, e, file=sys.stderr)
            time.sleep(5 * (i + 1))
    raise RuntimeError("QLever failed")


def q(cell):
    cell = cell.strip()
    if cell.startswith("<http://www.wikidata.org/entity/"):
        return cell[len("<http://www.wikidata.org/entity/"):-1]
    return None


def lit(cell):
    cell = cell.strip()
    if cell.startswith('"'):
        return cell[1:cell.rfind('"')]
    return cell or None


def year(cell):
    v = lit(cell)
    if not v:
        return None
    neg = v.startswith("-")
    try:
        y = int(v.lstrip("-+").split("-")[0])
    except ValueError:
        return None
    return -y if neg else y


def main():
    pf = json.load(gzip.open(f"{HIST}/polity_facts.json.gz", "rt", encoding="utf-8"))
    states = sorted({p["q"] for p in pf["polities"]} | {"Q1775277", "Q1990567", "Q174193", "Q161885", "Q193714"})
    offices = {}
    for i in range(0, len(states), 300):
        part = states[i:i + 300]
        rows = tsv("SELECT ?s ?h ?g WHERE { VALUES ?s { " + " ".join("wd:" + s for s in part) + " } "
                   "OPTIONAL { ?s wdt:P1906 ?h } OPTIONAL { ?s wdt:P1313 ?g } }")
        for r in rows:
            s, h, g = q(r[0]), q(r[1]) if len(r) > 1 else None, q(r[2]) if len(r) > 2 else None
            d = offices.setdefault(s, {"head": [], "gov": []})
            if h and h not in d["head"]:
                d["head"].append(h)
            if g and g not in d["gov"]:
                d["gov"].append(g)
        print("offices", i + len(part), "/", len(states))
    # States whose Wikidata item names no office (mostly the historical items the map uses), by the office's
    # English label: the office of the same country under its own article.
    for s_, labs in EXTRA_HEAD_OFFICES.items():
        rows = tsv("SELECT ?o ?l WHERE { VALUES ?l { " + " ".join(json.dumps(l) + "@en" for l in labs) + " } "
                   "?o rdfs:label ?l }")
        d = offices.setdefault(s_, {"head": [], "gov": []})
        for r in rows:
            o = q(r[0])
            if o and o not in d["head"]:
                d["head"].append(o)
    print("extra offices:", sum(1 for s_ in EXTRA_HEAD_OFFICES if offices.get(s_, {}).get("head")))
    all_off = sorted({o for d in offices.values() for k in ("head", "gov") for o in d[k]})
    labels, holders = {}, {}
    for i in range(0, len(all_off), 150):
        part = all_off[i:i + 150]
        vals = " ".join("wd:" + o for o in part)
        for r in tsv("SELECT ?o ?l WHERE { VALUES ?o { " + vals + " } ?o rdfs:label ?l FILTER(LANG(?l)=\"en\") }"):
            labels[q(r[0])] = lit(r[1])
        rows = tsv("SELECT ?o ?p ?pl ?st ?en ?sx WHERE { VALUES ?o { " + vals + " } ?p p:P39 ?x . ?x ps:P39 ?o . "
                   "OPTIONAL { ?x pq:P580 ?st } OPTIONAL { ?x pq:P582 ?en } OPTIONAL { ?p wdt:P21 ?sx } "
                   "OPTIONAL { ?p rdfs:label ?pl FILTER(LANG(?pl)=\"en\") } }")
        for r in rows:
            o, pq_, name = q(r[0]), q(r[1]), lit(r[2]) if len(r) > 2 else None
            st = year(r[3]) if len(r) > 3 else None
            en = year(r[4]) if len(r) > 4 else None
            female = 1 if len(r) > 5 and q(r[5]) in ("Q6581072", "Q1052281") else 0
            if not name or st is None:
                continue
            holders.setdefault(o, []).append([name, pq_, st, en, female])
        print("holders", i + len(part), "/", len(all_off), "rows so far", sum(len(v) for v in holders.values()))
    for o in holders:
        holders[o] = sorted({tuple(x) for x in holders[o]}, key=lambda x: (x[2], x[3] or 9999))
    out = {"source": "Wikidata (CC0) through QLever (qlever.dev/api/wikidata), fetched "
                     + time.strftime("%Y-%m-%d") + " by worldfill/fix_history_wd.py",
           "offices": offices, "labels": labels, "holders": holders}
    with open(OUT, "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as f:
        json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
    print("states with a head office:", sum(1 for d in offices.values() if d["head"]),
          "offices:", len(all_off), "terms:", sum(len(v) for v in holders.values()))


if __name__ == "__main__":
    main()
