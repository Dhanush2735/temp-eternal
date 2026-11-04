#!/usr/bin/env python3
"""Step 8.3: the four trade routes left out in step 7 because their Wikipedia leads give no dates.

Towns come from each article exactly as build_wiki_routes.py finds them (linked settlements with
coordinates; strays over 1,500 km from every other town dropped). The years are ESTIMATES, written
from dated sentences in each article's history section (quoted in "years_from", which starts with
"estimated:"). Adds them to history/trade_routes.json.gz without touching the Itiner-e roads.
"""
import gzip
import io, json, os, sys

sys.path.insert(0, "/home/user/worldfill")
import modpack as M  # noqa: E402
import build_wiki_routes as BW  # noqa: E402

OUT = f"{M.HISTORY}/trade_routes.json.gz"
NEW = [
    ("Dakshinapatha", -500, 1300, "land",
     "estimated: Panini (c. 500 BCE) names the southern lands it reached; a 150 CE inscription of Rudradaman names it; "
     "the highway from Magadha to Pratishthana served the Deccan kingdoms through the Middle Ages"),
    ("Uttarapatha", -500, 1200, "land",
     "estimated: the northern high road of early Buddhist texts; Gandhara markets in c. 127 BCE, Roman trade 1-200 CE, "
     "and horse trade up to the 12th century are recorded"),
    ("Amber Road", -1600, 400, "land",
     "estimated: 'from at least the 16th century BC, amber was moved from Northern Europe to the Mediterranean'; "
     "a Roman trade and military road until the end of the Western Empire"),
    ("Indian Ocean trade", -2600, 1800, "sea",
     "estimated: Harappan-Mesopotamian sea trade from 2600-1900 BCE, then Hellenistic, Roman, Arab, Indian, Chinese "
     "and Swahili trade until the colonial era"),
]


# places that only carry the name today (modern streets and tourist roads), or that an article
# mentions in passing, are not towns of the ancient route
DROP = {
    "Amber Road": {"Antwerp", "Bern", "Häädemeeste Parish", "Ikla", "Ambarès-et-Lagrave", "Bordeaux", "Hamburg",
                   "Baarn", "Barneveld", "Amersfoort", "Ljubljana"},
    "Uttarapatha": {"Mumbai", "Mysore"},
}


def main():
    BW.ROUTES = NEW
    found, st = BW.routes()
    for r in found:
        seen, towns = set(), []
        for t in r["towns"]:
            if t[0] in DROP.get(r["name"], set()) or t[0] in seen:
                continue
            seen.add(t[0])
            towns.append(t)
        st[f"dropped:{r['name']}"] = len(r["towns"]) - len(towns)
        r["towns"] = towns
    doc = json.load(gzip.open(OUT, "rt", encoding="utf-8"))
    names = {r["name"] for r in found}
    doc["routes"] = [r for r in doc["routes"] if r["name"] not in names] + found
    if "estimated:" not in doc["note"]:
        doc["note"] += "; a route whose years_from starts with 'estimated:' has years estimated from its article's history (worldfill/add_estimated_routes.py)"
    with open(OUT + ".tmp", "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as fh:
        json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
    json.load(gzip.open(OUT + ".tmp", "rt", encoding="utf-8"))
    os.replace(OUT + ".tmp", OUT)
    rep = {"stats": st, "routes": {r["name"]: [len(r["towns"]), r["start"], r["end"], [t[0] for t in r["towns"][:12]]] for r in found},
           "routes_total": len(doc["routes"]), "towns_total": sum(len(r["towns"]) for r in doc["routes"])}
    json.dump(rep, open("/home/user/worldfill/estimated_routes_report.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps(rep, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
