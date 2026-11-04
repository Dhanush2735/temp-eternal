import io
#!/usr/bin/env python3
"""Step 8.1: repair wrong Wikidata ids on the world border map (world_rulers.json.gz).

Cliopatria v0.2.1 gives some polities the Wikidata id of a different thing. For example, "Han
Dynasty" carries Q1068371 (the Chauhan dynasty of India), "Joseon" carries Old Choson's, and "Syria"
carries Assyria's. "Republic of Korea" and "Democratic People's Republic of Korea" share North
Korea's id. Rulers, languages, faiths and famous people are all keyed by this id, so such a state
shows another state's facts or none.

Every fix below was checked by hand. The method:
  * name vs. the id's own Wikipedia article (words and years);
  * ids shared by several map names;
  * ids that point at a city, island, person, war, period or disambiguation page.
The right article is given by title and resolved to its id offline from the Wikipedia dump.

The script:
  1. sets the new ids in history/world_rulers.json.gz (names unchanged);
  2. moves reigns in history/polity_facts.json.gz from the old id to the new one when they fall
     inside the fixed polity's years and outside the years of any polity keeping the old id. States
     that share an id at the same time (the two Koreas) are split later by
     fill_rulers.py, by name, from Wikipedia's lists;
  3. gives new ids the language, religion and capital of their own infobox (enwiki dump 2026-10-01);
  4. re-tags famous people (history/famous_people.json.gz) born in a fixed polity.
Writes worldfill/fix_state_ids_report.json.
"""
import collections, gzip, json, os, shutil, sqlite3, sys

sys.path.insert(0, "/home/user/worldfill")
import modpack as M  # noqa: E402
import wpdump as W  # noqa: E402
import build_polity_facts as PF  # noqa: E402
from build_notable_people import active_year  # noqa: E402
from wikitext_clean import infobox_params, clean_items, years_of, clean_person  # noqa: E402

WORLD = f"{M.HISTORY}/world_rulers.json.gz"
FACTS = f"{M.HISTORY}/polity_facts.json.gz"
PEOPLE = f"{M.HISTORY}/famous_people.json.gz"
BACKUP = os.path.expanduser("~/.cache/step8_backup")
REPORT = "/home/user/worldfill/fix_state_ids_report.json"

# map name -> title of the right English Wikipedia article
FIXES = {
    # Zhou-era Chinese states that carried the id of a later state with the same one-word name
    "Qi": "Qi (state)", "Song": "Song (state)", "Cao": "Cao (state)", "Lu": "Lu (state)",
    "Yan": "Yan (state)", "Wu": "Wu (state)", "Yue": "Yue (state)", "Zhao": "Zhao (state)",
    "Wei": "Wei (state)", "Han": "Han (Warring States)", "Jin": "Jin (Chinese state)", "Qin": "Qin (state)",
    "Zhongshan": "Zhongshan (state)", "Western Chu": "Chu (state)", "Zhai": "Eighteen Kingdoms",
    # other Chinese states
    "Han Dynasty": "Han dynasty", "Xia": "Xia (Sixteen Kingdoms)", "Southern Liang": "Southern Liang (Sixteen Kingdoms)",
    "Liang Dynasty": "Liang dynasty", "Western Liang": "Western Liang (Sixteen Kingdoms)",
    "Later Western Liang": "Western Liang (555–587)", "Later Han": "Later Han (Five Dynasties)",
    "Southern Wu": "Yang Wu", "Min": "Min (Ten Kingdoms)", "Great Yuan": "Dayuan",
    "Great Mongol State": "Bogd Khanate of Mongolia", "Mongol Khanate": "Northern Yuan",
    # Rome, Persia, Central Asia
    "Roman Republic": "Roman Republic", "Roman Empire": "Roman Empire", "Byzantine Empire": "Byzantine Empire",
    "Kingdom of Numidia": "Numidia", "Sasanian Empire": "Sasanian Empire", "Buyid Dynasty": "Buyid dynasty",
    "Samanid Empire": "Samanid Empire", "Muzaffarids": "Muzaffarids (Iran)", "Turks": "Göktürks",
    "Oghuz Turks": "Oghuz Yabgu State", "Qarlugs": "Karluks", "Turk Shahis": "Turk Shahis",
    # South Asia
    "Kannauj-Varman Dynasty": "Varman dynasty (Kannauj)", "Harsha's Empire": "Pushyabhuti dynasty",
    "Anurādhapura": "Anuradhapura kingdom", "Ceylon": "Sri Lanka", "Kalinga": "Kalinga (region)",
    "Kathmandu": "Malla dynasty (Nepal)",
    # Europe
    "Old Kingdom of Norway": "Kingdom of Norway (872–1397)", "County of Barcelona": "County of Barcelona",
    "Kingdom of Poland": "Kingdom of Poland", "Nitra": "Principality of Nitra",
    "Principality of Polotsky": "Principality of Polotsk", "Tver": "Principality of Tver",
    "Nizhny Novgorod": "Principality of Nizhny Novgorod-Suzdal", "Strathclyde": "Kingdom of Strathclyde",
    "Aquitaine": "Duchy of Aquitaine", "Habsburg Monarchy": "Habsburg monarchy", "Georgia": "Georgia (country)",
    "Kingdom of France": "Kingdom of France", "Kingdom of Great Britain": "United Kingdom",
    "Serbia": "Kingdom of Serbia", "Yugoslavia": "Kingdom of Yugoslavia", "Danish Magnates": "Danish Realm",
    # Africa, the Americas, East and Southeast Asia
    "Barghawata Conference": "Barghawata", "Zululand": "Zulu Kingdom", "British Africa": "British Empire",
    "Portuguese Africa": "Portuguese Empire", "Cuzco": "Kingdom of Cusco", "Texcoco": "Tetzcoco (altepetl)",
    "New Granada": "United Provinces of New Granada", "Cuban Nationalists": "Republic of Cuba in Arms",
    "Mahan": "Mahan confederacy", "Joseon": "Joseon", "Kingdom of Pajana": "Kingdom of Pajang",
    "Qasimids": "Qasimid State", "Kingdom of Champasak": "Kingdom of Champasak",
    "Chiangmai": "Nakhon Chiang Mai (1775–1899)",
    # modern states carrying another state's id
    "Denmark": "Denmark", "Syria": "Syria", "Slovakia": "Slovakia", "Republic of Korea": "South Korea",
    "Republic of the Congo": "Republic of the Congo", "Guinea": "Guinea", "Republic of Vietnam": "South Vietnam",
    "Republic of China": "Taiwan", "Mexico": "Mexico", "Lebanon": "Lebanon", "Ukraine": "Ukraine",
    "Japan": "Japan", "Romania": "Romania", "Republic of Bulgaria": "Bulgaria", "Republic of Albania": "Albania",
    "Republic of Yemen": "Yemen", "Hungary": "Hungary",
}
TOL = 5   # a reign that ends up to 5 years outside the polity's map years still belongs to it


def infobox_facts(text):
    i = text.find("{{Infobox")
    p = infobox_params(text[i:i + 30000]) if i >= 0 else None
    f = {"lang": [], "rel": [], "cap": "", "head": [], "gov": []}
    if not p:
        return f
    for k in ("official_languages", "common_languages", "languages", "language", "national_languages", "spoken_languages"):
        for x in clean_items(PF.ERA_LIMITED.sub("", p.get(k, "")), 6):
            if PF.JUNK_ITEM.search(x):
                continue
            x = x[:-9] if x.lower().endswith(" language") else x
            if x not in f["lang"]:
                f["lang"].append(x)
    for k in ("religion", "state_religion", "official_religion", "religions"):
        for x in clean_items(PF.ERA_LIMITED.sub("", p.get(k, "")), 6):
            if not PF.JUNK_ITEM.search(x) and x not in f["rel"]:
                f["rel"].append(x)
    f["lang"], f["rel"] = f["lang"][:4], f["rel"][:4]
    cap = clean_items(p.get("capital", ""), 1, split_and=False)
    f["cap"] = cap[0] if cap else ""
    for role, who, when, tk in (("head", "leader", "year_leader", "title_leader"), ("gov", "deputy", "year_deputy", "title_deputy")):
        title = PF.display_title(p.get(tk, "")) or ("Ruler" if role == "head" else "")
        if role == "gov" and not title:
            continue
        rows = []
        for n in range(1, 60):
            if f"{who}{n}" not in p:
                continue
            nm, yrs = clean_person(p[f"{who}{n}"]), years_of(p.get(f"{when}{n}", ""))
            if nm and yrs:
                rows.append([nm, title, yrs[0], yrs[1]])
        rows.sort(key=lambda r: r[2])
        for j, r in enumerate(rows):
            if r[3] is None:
                nxt = rows[j + 1][2] if j + 1 < len(rows) else r[2] + 25
                r[3] = max(r[2], min(nxt, r[2] + 25))
        f[role] = rows
    return f


def main():
    os.makedirs(BACKUP, exist_ok=True)
    for p in (WORLD, FACTS, PEOPLE):
        b = os.path.join(BACKUP, os.path.basename(p))
        if not os.path.exists(b):
            shutil.copy2(p, b)
    st = collections.Counter()
    wiki = W.Wiki()
    con = sqlite3.connect("file:" + W.DB + "?mode=ro", uri=True)
    world = json.load(gzip.open(WORLD, "rt", encoding="utf-8"))
    pols = world["polities"]
    idx = collections.defaultdict(list)
    for k, (n, q) in enumerate(pols):
        idx[n].append(k)
    # years of every map polity
    span = {}
    for tl in world["timelines"]:
        for j in range(0, len(tl), 3):
            pp, s, e = tl[j], tl[j + 1], tl[j + 2]
            a, b = span.get(pp, (9999, -9999))
            span[pp] = (min(a, s), max(b, e))
    fixes = []
    for name, title in FIXES.items():
        ks = idx.get(name, [])
        if len(ks) != 1:
            print("SKIP (not exactly one map polity):", name, ks)
            st["skipped_names"] += 1
            continue
        hit = wiki.lookup(title)
        info = wiki.info(hit[1]) if hit else None
        dis = con.execute("SELECT disambig FROM props WHERE page_id = ?", (hit[1],)).fetchone() if hit else None
        if not info or not info.get("qid") or (dis and dis[0]):
            print("SKIP (article not found):", name, title)
            st["skipped_titles"] += 1
            continue
        k = ks[0]
        old, new = pols[k][1], info["qid"]
        if old == new:
            continue
        fixes.append({"k": k, "name": name, "old": old, "new": new, "article": hit[0], "span": span.get(k)})
    for fx in fixes:
        pols[fx["k"]][1] = fx["new"]
    # who keeps each old id after the fix
    users = collections.defaultdict(list)
    for k, (n, q) in enumerate(pols):
        users[q].append(k)
    with open(WORLD + ".tmp", "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as fh:
        json.dump(world, fh, ensure_ascii=False, separators=(",", ":"))
    chk = json.load(gzip.open(WORLD + ".tmp", "rt", encoding="utf-8"))
    assert len(chk["polities"]) == len(pols) and len(chk["places"]) == len(world["places"])
    os.replace(WORLD + ".tmp", WORLD)
    st["map_ids_fixed"] = len(fixes)

    doc = json.load(gzip.open(FACTS, "rt", encoding="utf-8"))
    by = {p["q"]: p for p in doc["polities"]}
    titles = sorted({fx["article"] for fx in fixes})
    texts = {t: text for t, (_f, text) in wiki.texts(titles, workers=2).items()}
    concurrent = []
    for fx in fixes:
        a, b = fx["span"]
        keep = [span[k] for k in users.get(fx["old"], []) if k in span]
        overlap = any(s <= b and a <= e for s, e in keep)
        fx["shares_years_with_old_users"] = overlap
        newp = by.get(fx["new"])
        if newp is None:
            newp = {"q": fx["new"], "n": fx["name"]}
            if fx["article"] != fx["name"]:
                newp["a"] = fx["article"]
            doc["polities"].append(newp)
            by[fx["new"]] = newp
            st["new_state_entries"] += 1
        f = infobox_facts(texts.get(fx["article"], ""))
        for key in ("lang", "rel"):
            if f[key] and not newp.get(key):
                newp[key] = f[key]
                st[f"filled_{key}"] += 1
        if f["cap"] and not newp.get("cap"):
            newp["cap"] = f["cap"]
            st["filled_cap"] += 1
        oldp = by.get(fx["old"])
        moved = 0
        if oldp and not overlap:
            for role in ("head", "gov"):
                stay, go = [], []
                for r in oldp.get(role, []):
                    inside = r[2] <= b + TOL and r[3] >= a - TOL
                    other = any(r[2] <= e and r[3] >= s for s, e in keep)
                    if inside and not other:
                        go.append(r)
                    elif inside and other:
                        go.append(list(r))
                        stay.append(r)
                    else:
                        stay.append(r)
                if go:
                    have = {(x[0], x[2]) for x in newp.get(role, [])}
                    newp[role] = sorted(newp.get(role, []) + [r for r in go if (r[0], r[2]) not in have], key=lambda r: (r[2], r[3]))
                    oldp[role] = stay
                    moved += len(go)
            # modern religion shares follow the state they were measured for
            if oldp.get("relY") and b >= 1945 and not any(e >= 1945 for s, e in keep):
                newp["relY"] = oldp.pop("relY")
                st["relY_moved"] += 1
        if not newp.get("head"):
            for role in ("head", "gov"):
                if f[role] and not newp.get(role):
                    newp[role] = f[role]
                    st[f"infobox_{role}_rows"] += len(f[role])
        fx["reigns_moved"] = moved
        st["reigns_moved"] += moved
        if overlap:
            concurrent.append(fx)
    doc["source"] += "" if "fix_state_ids" in doc["source"] else "; state ids repaired by worldfill/fix_state_ids.py"
    with open(FACTS + ".tmp", "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as fh:
        json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
    json.load(gzip.open(FACTS + ".tmp", "rt", encoding="utf-8"))
    os.replace(FACTS + ".tmp", FACTS)

    # famous people: re-tag those born in a fixed polity
    reg = PF.Register()          # reads the fixed world_rulers.json.gz
    olds = {fx["old"] for fx in fixes}
    news = {fx["new"] for fx in fixes}
    ppl = json.load(gzip.open(PEOPLE, "rt", encoding="utf-8"))
    for r in ppl["people"]:
        if r[4] in olds and r[5] is not None and r[6] is not None:
            b, d = r[2], r[3]
            y = active_year(b, d) if b is not None else (d - 30 if d is not None else None)
            if y is None:
                continue
            pol = reg.at(r[5], r[6], y)
            if pol and pol[1] in news and pol[1] != r[4]:
                r[4] = pol[1]
                st["famous_people_retagged"] += 1
    with open(PEOPLE + ".tmp", "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as fh:
        json.dump(ppl, fh, ensure_ascii=False, separators=(",", ":"))
    json.load(gzip.open(PEOPLE + ".tmp", "rt", encoding="utf-8"))
    os.replace(PEOPLE + ".tmp", PEOPLE)
    rep = {**dict(st), "fixes": [{k: v for k, v in fx.items() if k != "k"} for fx in fixes],
           "same_years_as_old_id_users": [fx["name"] for fx in concurrent]}
    json.dump(rep, open(REPORT, "w"), ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != "fixes"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
