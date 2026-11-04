#!/usr/bin/env python3
"""Step 42 part 6 (F3, law and crime by era): build history/justice.json.gz from justice_table.py.

Shape
-----

Three tables in one pack - **guards, courts, punishments** - because F3 names all three and they
are always asked together: who keeps the peace here, who judges here, and what is done to a man
here. Keyed exactly the way `social_order.json.gz` is keyed, because it is asked exactly the way
that is asked: `CountryGrid.codeAt(lat, lon)` gives an ISO3 code, and the register wants the row
whose `where` holds that code, whose years hold that year, and which has the highest `priority`.

One hard fact, and it is not in this table
------------------------------------------

Every row here is a reading, **except whether a place still puts men to death**. That is not read
from this table: it comes from the C18 law pack through `LawRegister`, which carries real
abolition dates for real polities. The `judicial_death` row is marked `death`, and
`Justice.available()` asks the law register whether this polity has abolished capital punishment
by this year before it will offer it. So a judicial death stops being an option in a country the
year that country abolished it, and this table does not have to be right about it. That is the
whole reason F3 was scheduled after C18.

Marks
-----

**Every row is estimated.** No source states, as a number or as a fact, that the peace of a given
place in a given century was kept by a kindred or by a paid watch; these are this table's readings
of the reference works named on each row. Every `source` was checked to exist before it was
written down (one batched Wikipedia query on 45 candidate titles: 43 present, 2 missing and
dropped). A source that does not exist is worse than no source.

Checks
------

  * every `where` code is one `culture.json.gz` also knows (258 countries)
  * every row names the work it was read from, and has a name, a who and a line
  * no two rows in a table share an id
  * exactly one row in `punishments` is marked `death`, and it is the judicial one
  * every country of the world gets an answer in every era, in all three tables
  * the world is not all one answer in any era

Run:  python3 build_justice.py            build, then check
"""
import gzip
import json
import os
import sys

import justice_table as T

HERE = os.path.dirname(os.path.abspath(__file__))
HIST = os.path.normpath(os.path.join(
    HERE, "..", "eternal", "src", "main", "resources", "data", "eternalengine", "eternal", "history"))
OUT = os.path.join(HIST, "justice.json.gz")
CULTURE = os.path.join(HIST, "culture.json.gz")

DEFAULT_ONLY = "kin_self"      # used by the check below

TABLES = (("guards", T.GUARDS, T.DEFAULT_GUARDS),
          ("courts", T.COURTS, T.DEFAULT_COURTS),
          ("punishments", T.PUNISHMENTS, T.DEFAULT_PUNISHMENT))


def known_countries():
    with gzip.open(CULTURE, "rt", encoding="utf-8") as f:
        return set(json.load(f)["countries"])


def _row(r, codes):
    where = sorted({c for c in r["where"] if c in codes})
    out = {
        "id": r["id"], "name": r["name"], "who": r["who"], "line": r["line"],
        "where": where, "start": r["start"], "end": r["end"],
        "priority": r["priority"], "source": r["source"],
    }
    if r.get("death"):
        out["death"] = True
    if r.get("note"):
        out["note"] = r["note"]
    return out


def build():
    codes = known_countries()
    doc = {
        "format": "eternal-justice-1",
        "id": "justice",
        "source": ("Hand-written table for step 42 (F3), read from the reference works named on "
                   "each row: Hundred (county division), Tithing, Constable, Hue and cry, "
                   "Sheriff, Watchman (law enforcement), Metropolitan Police, Bow Street Runners, "
                   "Gendarmerie, Muhtasib, Qadi, Yamen, Bugyo, Panchayati raj, Feud, Weregild, "
                   "Diya (Islam), Outlaw, Stocks, Pillory, Flagellation, Hanging, Capital "
                   "punishment, Penal transportation, Prison, Fine (penalty), Thing (assembly), "
                   "Manorial court, Assizes, Court of Common Pleas, Sharia court, Indian Penal "
                   "Code, People's Court, Show trial, Secret police, Militia, Druzhina and "
                   "others. Every row is this table's reading and is marked estimated. Whether a "
                   "polity still puts men to death is NOT from here - it is the C18 law pack."),
        "note": ("Who keeps the peace, who judges and what is done to a man, by ISO3 country and "
                 "year, keyed the same way culture.json.gz and social_order.json.gz key their "
                 "rows: CountryGrid.codeAt(lat, lon) then the row whose `where` holds that code, "
                 "highest `priority` first. The `death` mark on a punishment means it is a "
                 "judicial killing and is gated by the law register's own abolition dates."),
        "counts": {},
        "gaps": [
            "Every row is this table's reading and not a measurement: no source states, for a "
            "given place and century, that the peace was kept by a kindred or by a paid watch.",
            "Country granularity. A region that kept two peaces at once - a Muslim coast and a "
            "highland interior - gets one of them, and the priority decides which.",
            "Three tables of a dozen rows each cannot be the whole world in every year. Each ends "
            "with a default, and the defaults are the least reliable rows in the pack.",
            "The dates at which one kind of guard or court gives way to another are given to the "
            "century at best. A row that says 1200 means 'by then, somewhere in this region', "
            "not 'from 1200 everywhere in it'.",
            "Before about 2400 BC the pack names no court anywhere, because no source it was read "
            "from describes one - Urukagina's reforms (c. 2380 BC) are the earliest thing called "
            "law. The fallback answers there, and that is the edge of the evidence and not a "
            "measurement.",
            "Whether a polity has abolished capital punishment is NOT from this table. It is the "
            "step-42 C18 law pack, which was read from real abolition dates; this table only says "
            "which punishments exist to be abolished.",
        ],
        "countries": [],
    }

    all_countries = set()
    estimated = 0
    for key, rows, default in TABLES:
        pack = [_row(r, codes) for r in rows]
        pack.sort(key=lambda r: (-r["priority"], r["id"]))
        doc[key] = pack
        doc["default_" + key] = _row(default, codes)
        doc["counts"][key] = len(pack)
        all_countries |= {c for r in pack for c in r["where"]}
        estimated += len(pack)
    doc["countries"] = sorted(all_countries)
    doc["counts"]["estimated"] = estimated
    doc["counts"]["recorded"] = 0

    blob = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(blob)
    print("justice.json.gz: %d guards, %d courts, %d punishments over %d countries (%d bytes gzipped)"
          % (doc["counts"]["guards"], doc["counts"]["courts"], doc["counts"]["punishments"],
             len(doc["countries"]), os.path.getsize(OUT)))
    return doc


def pick(doc, key, code, year):
    """The row for a country and year, the way the mod will pick it."""
    best = None
    for r in doc[key]:
        if code not in r["where"]:
            continue
        if r["start"] is not None and year < r["start"]:
            continue
        if r["end"] is not None and year >= r["end"]:
            continue
        if best is None or r["priority"] > best["priority"]:
            best = r
    return best if best is not None else doc["default_" + key]


def pick_all(doc, key, code, year):
    """
    Every row that applies, strongest first - the way the mod reads `punishments`.

    <p>Punishment is not one answer. A place has a <b>repertoire</b>: what is done to a man
    depends on the crime and on who he is, and a blood-price, a flogging, a fine and a hanging
    all sat side by side for most of history. Picking the single highest-priority row would
    silently delete all the others - and it killed the default outright, because `corporal` and
    `judicial_death` cover every country from before history, so the blood-price could never win
    and the fallback row was dead code.
    """
    hits = [r for r in doc[key]
            if code in r["where"]
            and (r["start"] is None or year >= r["start"])
            and (r["end"] is None or year < r["end"])]
    hits.sort(key=lambda r: -r["priority"])
    return hits if hits else [doc["default_" + key]]


def check():
    with gzip.open(OUT, "rt", encoding="utf-8") as f:
        d = json.load(f)
    bad = []

    def ok(cond, what):
        print(("  ok   " if cond else "  FAIL ") + what)
        if not cond:
            bad.append(what)

    ok(d["format"] == "eternal-justice-1", "the format is the one this builder writes")
    for key in ("guards", "courts", "punishments", "countries", "gaps", "counts"):
        ok(key in d, "the pack carries %s" % key)
    for key, _, _ in TABLES:
        ok(("default_" + key) in d, "the pack carries default_%s" % key)

    codes = known_countries()
    for key, _, _ in TABLES:
        rows = d[key]
        ok(len(rows) >= 8, "%s: %d rows" % (key, len(rows)))
        stray = sorted({c for r in rows for c in r["where"] if c not in codes})
        ok(not stray, "%s: every country code is one culture.json.gz also knows (%s)"
           % (key, ", ".join(stray[:8]) or "none"))
        ok(len({r["id"] for r in rows}) == len(rows), "%s: no two rows share an id" % key)
        for r in rows:
            ok(bool(r["source"]), "%s/%s names the work it was read from" % (key, r["id"]))
            ok(bool(r["name"]) and bool(r["who"]) and bool(r["line"]),
               "%s/%s has a name, a who and a line" % (key, r["id"]))
            ok(r["start"] is not None, "%s/%s has a start year" % (key, r["id"]))
            if r["end"] is not None:
                ok(r["end"] >= r["start"], "%s/%s does not end before it begins" % (key, r["id"]))

    # The one hard mark in the pack.
    deaths = [r["id"] for r in d["punishments"] if r.get("death")]
    ok(deaths == ["judicial_death"],
       "exactly one punishment is marked `death`, and it is the judicial one (%s)"
       % (", ".join(deaths) or "none"))

    # Every country, in every era, gets an answer in all three tables.
    years = [-2400, -500, 0, 500, 1000, 1300, 1600, 1800, 1900, 1950, 2000]
    for key, _, _ in TABLES:
        for y in years:
            got = {pick(d, key, c, y)["id"] for c in codes}
            ok(len(got) > 1, "%-11s %5d: the world is not all one answer (%d different)"
               % (key, y, len(got)))

    print()
    for c, y in (("GBR", 1400), ("GBR", 1850), ("CHN", 1800), ("JPN", 1750),
                 ("IND", 1700), ("RUS", 1960), ("FRA", 1300), ("EGY", 1200),
                 ("MEX", 1700), ("USA", 1950), ("AUS", 1900)):
        g = pick(d, "guards", c, y)
        ct = pick(d, "courts", c, y)
        rep = pick_all(d, "punishments", c, y)
        print("       %s %5d  %-26s | %-24s | %s"
              % (c, y, g["name"][:26], ct["name"][:24], ", ".join(r["name"] for r in rep)))
    print()
    ok(pick(d, "guards", "GBR", 1400)["id"] == "hundred_shire",
       "England in 1400 is kept by the hundred and the shire")
    ok(pick(d, "guards", "GBR", 1850)["id"] == "police_force",
       "and by 1850 by a standing police force")
    ok(pick(d, "guards", "CHN", 1800)["id"] == "magistrate_runners",
       "China in 1800 is kept by the magistrate's runners")
    ok(pick(d, "guards", "JPN", 1750)["id"] == "bugyo_men", "Japan in 1750 by the bugyo's men")
    ok(pick(d, "courts", "IND", 1700)["id"] == "panchayat_court",
       "India in 1700 is judged by the panchayat")
    ok(pick(d, "courts", "EGY", 1200)["id"] == "qadi_court", "Egypt in 1200 by the qadi")
    ok(pick(d, "guards", "RUS", 1960)["id"] == "political_police",
       "Russia in 1960 is kept by the political police, above the militia")
    ok(pick(d, "guards", "GBR", 1850)["id"] == "police_force",
       "and Britain has no gendarmerie - it is the exception the row names")
    ok(pick(d, "guards", "FRA", 800)["id"] == "lord_household",
       "France in 800 is kept by the lord's household, which is what Francia had")
    ok(pick(d, "guards", "AUS", 800)["id"] == "kin_self",
       "and a place no row covers falls back to the kindred, which is the default")

    # Punishment is a repertoire, not a choice: several are available at once, and the blood-price
    # is the fallback only where nothing else applies at all.
    rep = [r["id"] for r in pick_all(d, "punishments", "GBR", 1300)]
    ok(len(rep) >= 3, "England in 1300 has a repertoire of %d, not one answer" % len(rep))
    ok("judicial_death" in rep, "and hanging is in it")
    ok("blood_price" not in rep,
       "but the blood-price is not - it is the fallback, and England had a state by then")
    old = [r["id"] for r in pick_all(d, "punishments", "AUS", -5000)]
    ok(old == ["blood_price"],
       "before 3000 BC, when no row reaches, the fallback answers alone (%s)" % ", ".join(old))
    ok("judicial_death" in [r["id"] for r in pick_all(d, "punishments", "FRA", 1780)],
       "France in 1780 can still hang a man")
    ok("prison_term" not in [r["id"] for r in pick_all(d, "punishments", "FRA", 1770)],
       "and in 1770 cannot yet sentence him to a term of years")
    ok("prison_term" in [r["id"] for r in pick_all(d, "punishments", "FRA", 1790)],
       "by 1790 it can, which is the change from the body to the clock")
    # The fallback is reachable in the other two tables, where it is not shadowed by a universal row.
    ok(pick(d, "guards", "AUS", 800)["id"] == "kin_self",
       "and a place no guard row covers falls back to the kindred")
    ok(pick(d, "courts", "AUS", 800)["id"] == "elder_judges",
       "and a place no court row covers falls back to the elder")
    ok(all(r["id"] != DEFAULT_ONLY for r in d["guards"])
       and all(r["id"] != DEFAULT_ONLY for r in d["courts"]),
       "no table carries its own fallback as a row as well (%s)" % DEFAULT_ONLY)

    print()
    print("justice: %d problem(s)" % len(bad))
    return len(bad)


if __name__ == "__main__":
    build()
    sys.exit(1 if check() else 0)
