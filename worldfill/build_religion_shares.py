import io
#!/usr/bin/env python3
"""Step 7.5: religion shares 1945-2010 from the Correlates of War World Religion Data v1.1.

WRP_national.csv (Maoz & Henderson 2013, International Interactions 39:265-291; free to use with
citation) gives, for every state every 5 years from 1945 to 2010, the share of its people in each
religion and branch. Each country-year is tied to the Cliopatria state ruling the country's own
point that year (Wikipedia article coordinates, then RulerRegister's grid), so the Soviet Union and
Russia, West Germany and Germany, are told apart. The top faiths (5% or more) are added to the
state's entry in history/polity_facts.json.gz as "relY": [[year, [[faith, percent], ...]], ...].
"""
import collections, csv, gzip, json, os, sys

sys.path.insert(0, "/home/user/worldfill")
import modpack as M  # noqa: E402
import wpdump as W  # noqa: E402
import build_polity_facts as PF  # noqa: E402

SRC = os.path.expanduser("~/.cache/srcdata/cow")
FACTS = f"{M.HISTORY}/polity_facts.json.gz"
REPORT = "/home/user/worldfill/religion_shares_report.json"
ALIAS = {"German Federal Republic": "West Germany", "German Democratic Republic": "East Germany",
         "Yemen Arab Republic": "North Yemen", "Yemen People's Republic": "South Yemen",
         "Republic of Vietnam": "South Vietnam", "Korea": "Korean Empire", "Swaziland": "Eswatini",
         "Ivory Coast": "Ivory Coast", "Congo": "Republic of the Congo", "Burkina Faso": "Burkina Faso",
         "Federated States of Micronesia": "Federated States of Micronesia", "Samoa": "Samoa",
         "Antigua & Barbuda": "Antigua and Barbuda", "St. Lucia": "Saint Lucia",
         "St. Vincent and the Grenadines": "Saint Vincent and the Grenadines", "St. Kitts and Nevis": "Saint Kitts and Nevis",
         "Myanmar": "Myanmar", "East Timor": "East Timor", "Macedonia": "North Macedonia"}
FAMILIES = [("chrstgenpct", "Christianity"), ("islmgenpct", "Islam"), ("hindgenpct", "Hinduism"),
            ("budgenpct", "Buddhism"), ("judgenpct", "Judaism"), ("sikhgenpct", "Sikhism"), ("jaingenpct", "Jainism"),
            ("shntgenpct", "Shinto"), ("taogenpct", "Taoism"), ("confgenpct", "Confucianism"),
            ("zorogenpct", "Zoroastrianism"), ("bahgenpct", "the Bahá'í Faith"), ("syncgenpct", "syncretic faiths"),
            ("anmgenpct", "traditional religions"), ("nonreligpct", "no religion"), ("othrgenpct", "other faiths")]
CHRIST = [("chrstcatpct", "Catholic Christianity"), ("chrstprotpct", "Protestant Christianity"),
          ("chrstorthpct", "Orthodox Christianity"), ("chrstangpct", "Anglican Christianity")]
ISLAM = [("islmsunpct", "Sunni Islam"), ("islmshipct", "Shia Islam")]


def f(row, k):
    try:
        return float(row.get(k) or 0)
    except ValueError:
        return 0.0


def label(row, key, name):
    total = f(row, key)
    if key == "chrstgenpct" and total > 0:
        for k, n in CHRIST:
            if f(row, k) >= 0.6 * total:
                return n
    if key == "islmgenpct" and total > 0:
        for k, n in ISLAM:
            if f(row, k) >= 0.7 * total:
                return n
    return name


def main():
    names = {}
    for line in open(f"{SRC}/cow_codes.csv", encoding="utf-8", errors="replace").read().replace("\r", "\n").split("\n")[1:]:
        parts = line.split(",")
        if len(parts) >= 3 and parts[1].strip().isdigit():
            names[int(parts[1])] = ",".join(parts[2:]).strip()
    reg = PF.Register()
    wiki = W.Wiki()
    point = {}
    st = collections.Counter()
    for code, nm in names.items():
        hit = wiki.lookup(ALIAS.get(nm, nm))
        info = wiki.info(hit[1]) if hit else None
        g = info.get("geo") if info else None
        point[code] = ((g["lat"], g["lon"]) if g else None, info.get("qid") if info else None)
    known = {q for _n, q in reg.pols if q}
    out = collections.defaultdict(list)
    for row in csv.DictReader(open(f"{SRC}/WRP_national.csv", encoding="utf-8", errors="replace")):
        year, code = int(row["year"]), int(row["state"])
        pt, qid = point.get(code, (None, None))
        q = None
        if pt:
            pol = reg.at(pt[0], pt[1], year)
            q = pol[1] if pol else None
        if not q and qid in known:
            q = qid
        if not q:
            st["country_years_without_state"] += 1
            continue
        shares = sorted(((round(100 * f(row, k), 1), label(row, k, n)) for k, n in FAMILIES), reverse=True)
        top = [[n, p] for p, n in shares if p >= 5.0][:3]
        if top:
            out[q].append([year, top])
            st["country_years"] += 1
    doc = json.load(gzip.open(FACTS, "rt", encoding="utf-8"))
    by = {p["q"]: p for p in doc["polities"]}
    qname = {q: n for n, q in reg.pols if q}
    for q, rows in out.items():
        rows.sort()
        merged, seen = [], set()
        for y, top in rows:              # one row per year (two COW states can share a Cliopatria state)
            if y not in seen:
                seen.add(y)
                merged.append([y, top])
        if q not in by:
            by[q] = {"q": q, "n": qname.get(q, q)}
            doc["polities"].append(by[q])
            st["new_state_entries"] += 1
        by[q]["relY"] = merged
        st["states_with_shares"] += 1
    if "build_religion_shares" not in doc["source"]:
        doc["source"] += ("; religion shares 1945-2010 from the Correlates of War World Religion Data v1.1 (Maoz & Henderson 2013), "
                          "worldfill/build_religion_shares.py")
    if "relY rows" not in doc["note"]:
        doc["note"] += "; relY rows are [year, [[faith, percent of people], ...]] (CoW World Religion Data, every 5 years 1945-2010)"
    with open(FACTS + ".tmp", "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as fh:
        json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
    json.load(gzip.open(FACTS + ".tmp", "rt", encoding="utf-8"))
    os.replace(FACTS + ".tmp", FACTS)
    india = next((p for p in doc["polities"] if p.get("n") == "Republic of India"), {})
    rep = {**dict(st), "example_india": india.get("relY", [])[-2:], "bytes": os.path.getsize(FACTS)}
    json.dump(rep, open(REPORT, "w"), ensure_ascii=False, indent=1)
    print(json.dumps(rep, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
