import io
#!/usr/bin/env python3
"""Step 7.2: famous people with their real birthplace, merged into history/famous_people.json.gz.

Source: the cross-verified database of notable people (Laouenan, Bhargava, Eymeoud, Gergaud,
Plique & Wasmer 2022, Scientific Data 9:290; Sciences Po, doi:10.21410/7E4/RDAG3O), CC BY-SA 4.0.
2,291,817 people from Wikipedia and Wikidata; 1,654,727 have a birth year and birthplace coordinates.

Kept (with birthplace and birth year): everyone born before 1500, the 400,000 most visible born
1500-1799, the 200,000 most visible born 1800-1899 and the 100,000 most visible born 1900 or later
(visibility = the database's own 5-criteria ranking). About 149,000 people.

Each kept person becomes a row like the year-page people ([name, description, birth, death,
state, lat, lon, radiusKm]) with lat/lon = the birthplace and radiusKm = 25: the mark of an exact
birthplace (the year-page rows are placed at a country, radius 40-800). state = the Cliopatria state
ruling the birthplace in the person's active years. A person already on the year pages (same name,
birth year within 1) keeps the year-page description and gains the exact birthplace.
"""
import collections, csv, gzip, json, os, re, shutil, sys, time

sys.path.insert(0, "/home/user/worldfill")
import modpack as M  # noqa: E402
import build_polity_facts as PF  # noqa: E402

SRC = os.path.expanduser("~/.cache/srcdata/sciencespo/cross-verified-database.csv.gz")
PEOPLE = f"{M.HISTORY}/famous_people.json.gz"
BACKUP = os.path.expanduser("~/.cache/famous_people_yearpages_only.json.gz")
REPORT = "/home/user/worldfill/notable_people_report.json"
BIRTHPLACE_KM = 25
LIMITS = [(1500, None), (1800, 400000), (1900, 200000), (10 ** 6, 100000)]   # born before X: rank limit
OCC = {"football": "footballer", "basket": "basketball player", "film": "film-maker", "music": "musician",
       "militar": "soldier", "sport": "athlete", "athletic": "athlete", "hockey": "hockey player",
       "baseball": "baseball player", "guitar": "guitarist", "player": "player", "religious": "cleric",
       "politic": "politician", "tennis": "tennis player", "cycling": "cyclist", "golf": "golfer",
       "rugby": "rugby player", "cricket": "cricketer", "boxing": "boxer", "chess": "chess player",
       "swimming": "swimmer", "skiing": "skier", "volley": "volleyball player", "handball": "handball player",
       "racing": "racing driver", "noble": "noble", "royal": "royal", "business": "businessperson",
       "law": "lawyer", "medicine": "physician", "art": "artist", "dance": "dancer", "theatre": "actor",
       "television": "television presenter", "radio": "radio presenter", "comics": "comics artist"}


def norm_name(s):
    s = re.sub(r"_", " ", s or "")
    s = re.sub(r"\s*\([^()]*\)\s*$", "", s)
    return re.sub(r"\s+", " ", s).strip()


def key(name):
    return re.sub(r"[^a-z0-9]+", "", PF.strip_accents(norm_name(name).lower()))


def limit_for(birth):
    for before, lim in LIMITS:
        if birth < before:
            return lim
    return 0


def active_year(b, d):
    if d is not None:
        return min(d, b + 40)
    return b + 35


def main():
    t0 = time.time()
    if not os.path.exists(BACKUP):
        shutil.copy(PEOPLE, BACKUP)        # the year-page rows' only copy; their source is gone
    base = json.load(gzip.open(BACKUP, "rt", encoding="utf-8"))
    rows = base["people"]
    by_key = collections.defaultdict(list)
    for i, r in enumerate(rows):
        by_key[key(r[0])].append(i)
    reg = PF.Register()
    st = collections.Counter()
    new = []
    # Occupation words: only the common ones (30+ people) are kept; rare ones are often noise ("_hijo", "jesus")
    occ_count = collections.Counter()
    with gzip.open(SRC, "rt", encoding="utf-8", errors="replace") as f0:
        rd0 = csv.reader(f0)
        h0 = next(rd0)
        oi = h0.index("level3_main_occ")
        for row in rd0:
            occ_count[(row[oi] or "").strip()] += 1
    good_occ = {o for o, c in occ_count.items() if c >= 30 and re.fullmatch(r"[a-z][a-z \-]{2,24}", o)}
    good_occ -= {"jesus", "missing", "other", "unknown"}
    with gzip.open(SRC, "rt", encoding="utf-8", errors="replace") as f:
        rd = csv.reader(f)
        h = next(rd)
        ix = {k: i for i, k in enumerate(h)}
        for row in rd:
            try:
                b = int(float(row[ix["birth"]]))
                la, lo = float(row[ix["bpla1"]]), float(row[ix["bplo1"]])
            except ValueError:
                continue
            rk = int(float(row[ix["ranking_visib_5criteria"]] or 9e9))
            lim = limit_for(b)
            if lim is not None and rk > lim:
                continue
            d = None
            for c in ("death", "updated_death_date"):
                try:
                    d = int(float(row[ix[c]]))
                    break
                except ValueError:
                    continue
            if d is not None and not (0 <= d - b <= 120) or b > 2010 or (d is not None and d > 2026):
                st["bad_years"] += 1
                continue
            if not (-90 <= la <= 90 and -180 <= lo <= 180):
                continue
            name = norm_name(row[ix["name"]])
            if not name:
                continue
            occ = (row[ix["level3_main_occ"]] or "").strip()
            occ = OCC.get(occ, occ) if occ in good_occ else ""
            pol = reg.at(la, lo, active_year(b, d))
            q = pol[1] if pol else None
            st["kept"] += 1
            hit = None
            for i in by_key.get(key(name), ()):
                r = rows[i]
                if r[2] is not None and abs(r[2] - b) <= 1 or (r[2] is None and r[3] is not None and d is not None and abs(r[3] - d) <= 1):
                    hit = i
                    break
            if hit is not None:
                r = rows[hit]
                rows[hit] = [r[0], r[1] or occ, r[2] if r[2] is not None else b, r[3] if r[3] is not None else d,
                             q or r[4], round(la, 3), round(lo, 3), BIRTHPLACE_KM]
                st["matched_year_page_person"] += 1
            else:
                new.append([name, occ, b, d, q, round(la, 3), round(lo, 3), BIRTHPLACE_KM])
                st["new_people"] += 1
    out = rows + new
    out.sort(key=lambda r: (r[3] if r[3] is not None else (r[2] or 0) + 60, r[0]))
    doc = dict(base)
    doc["source"] = (base["source"] + "; plus the cross-verified database of notable people (Laouenan et al. 2022, "
                     "Sciences Po doi:10.21410/7E4/RDAG3O, CC BY-SA 4.0): exact birthplaces (radiusKm 25), "
                     "worldfill/build_notable_people.py")
    doc["note"] = ("rows are [name, description, birth, death, state, lat, lon, radiusKm]: radiusKm 25 means lat/lon is "
                   "the exact birthplace; larger radii are year-page people placed at their home land. state is the "
                   "Wikidata id of the Cliopatria state of the person's land in their active years, or null")
    doc["people"] = out
    with open(PEOPLE + ".tmp", "wb") as _gzraw, gzip.GzipFile(filename="", mode="wb", compresslevel=9, fileobj=_gzraw, mtime=0) as _gzb, io.TextIOWrapper(_gzb, encoding="utf-8", write_through=True) as fh:
        json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
    json.load(gzip.open(PEOPLE + ".tmp", "rt", encoding="utf-8"))
    os.replace(PEOPLE + ".tmp", PEOPLE)
    era = collections.Counter((r[2] // 100 * 100 if r[2] is not None else None) for r in out if r[7] == BIRTHPLACE_KM)
    rep = {"seconds": round(time.time() - t0), **dict(st), "total_people": len(out),
           "with_exact_birthplace": sum(1 for r in out if r[7] == BIRTHPLACE_KM),
           "with_state": sum(1 for r in out if r[4]),
           "birthplace_people_by_century": {str(k): v for k, v in sorted(era.items(), key=lambda x: (x[0] is None, x[0] or 0)) if k is not None and k < 1500},
           "bytes": os.path.getsize(PEOPLE),
           "examples": [f"{r[0]} | {r[1]} | {r[2]}-{r[3]} | {r[5]},{r[6]}" for r in new[:: max(1, len(new) // 10)]][:10]}
    json.dump(rep, open(REPORT, "w"), ensure_ascii=False, indent=1)
    print(json.dumps(rep, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
