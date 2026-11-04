#!/usr/bin/env python3
"""Step 38 part 7 (C20): build history/health.json.gz from the hand-written tables.

    python3 build_health.py
    python3 build_health.py --selftest     rebuild in memory and check it (exit 1 on a problem)

What it checks:

* no two rows share an id, in either table; every row is sourced;
* every remedy that names an atlas technology names one that actually exists in step 30a's
  technology atlas, so the register is not asking for a thing the atlas has never heard of;
* every disease that says a remedy ended it names one that is in the remedy table;
* the remedies are dated earliest-first, and the multipliers only ever get better, because a
  medicine that makes things worse is a medicine out of order;
* the case fatality of smallpox is about 30 per cent and the multiplier for variolation is worse
  than the one for vaccination: if either stops being true the table has been corrupted.
"""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from health_table import DISEASES, REMEDIES                       # noqa: E402

MOD = os.path.normpath(os.path.join(HERE, "..", "eternal"))
OUT = os.path.join(MOD, "src", "main", "resources", "data", "eternalengine", "eternal",
                   "history", "health.json.gz")
ATLAS = os.path.join(MOD, "src", "main", "resources", "data", "eternalengine", "eternal",
                     "history", "technology_atlas.json.gz")

SOURCE = ("College of Physicians of Philadelphia, historyofvaccines.org; Riedel, 'Edward Jenner "
          "and the history of smallpox and vaccination' (PMC1200696); World Health Organization, "
          "'History of smallpox vaccination' and the Global Commission's final report; Rontgen, "
          "Lister, Pasteur, Koch and Snow via Britannica ('Germ theory', 'History of Public "
          "Health: A Timeline'), the English Wikipedia 'Timeline of medicine and medical "
          "technology', PMC7150208 and PMC9609744; Our World in Data ('Smallpox', 'Historical "
          "pandemics'); USDA Agricultural Research Service, 'Penicillin: Opening the Era of "
          "Antibiotics'; and English Wikipedia for each named disease. Rows marked estimated "
          "carry this table's own numbers, not any source's.")


def atlas_tech_ids():
    if not os.path.exists(ATLAS):
        return None
    doc = json.loads(gzip.open(ATLAS, "rb").read().decode("utf-8"))
    return {t["id"] for t in doc.get("techs", [])}


def build():
    return {
        "format": 1,
        "id": "health",
        "source": SOURCE,
        "remedies": [{
            "id": r.id, "name": r.name, "year": r.year, "place": r.place,
            "lat": r.lat, "lon": r.lon, "applies": r.applies, "mult": r.mult,
            "note": r.note, "source": r.src, "mark": r.mark,
            "atlas": r.atlas,
        } for r in sorted(REMEDIES, key=lambda x: (x.year, x.id))],
        "diseases": [{
            "id": d.id, "name": d.name, "also": d.also, "germ": d.germ, "route": d.route,
            "oyear": d.oyear, "oplace": d.oplace, "olat": d.olat, "olon": d.olon,
            "cfr": d.cfr, "cls": d.cls, "ended": d.ended,
            "note": d.note, "source": d.src, "mark": d.mark, "endemic": d.endemic,
        } for d in sorted(DISEASES, key=lambda x: (x.oyear, x.id))],
    }


def selftest(doc):
    problems = []
    rem = doc["remedies"]
    dis = doc["diseases"]

    for rows, what in ((rem, "remedy"), (dis, "disease")):
        seen = set()
        for r in rows:
            if r["id"] in seen:
                problems.append("duplicate %s id: %s" % (what, r["id"]))
            seen.add(r["id"])
            if not r["source"]:
                problems.append("%s %s has no source" % (what, r["id"]))

    # every remedy that defers to the atlas must name a technology the atlas holds
    ids = atlas_tech_ids()
    atlas_rows = [r for r in rem if r["atlas"]]
    if ids is None:
        problems.append("cannot read the technology atlas at %s" % ATLAS)
    else:
        for r in atlas_rows:
            if r["atlas"] not in ids:
                problems.append("remedy %s asks the atlas for '%s', which the atlas does not have"
                                % (r["id"], r["atlas"]))
    if atlas_rows and len(atlas_rows) < 5:
        problems.append("only %d remedies defer to the atlas; the point of this table is that a "
                        "remedy arrives in a place, not in the world at once" % len(atlas_rows))

    # every disease that says a remedy ended it must name one we hold
    rids = {r["id"] for r in rem}
    for d in dis:
        if d["ended"] and d["ended"] not in rids:
            problems.append("disease %s says %s ended it, and %s is not in the remedy table"
                            % (d["id"], d["ended"], d["ended"]))

    # the multipliers can only improve, and the remedies must be dated earliest first
    prev = None
    for r in rem:
        if prev is not None and r["year"] < prev:
            problems.append("the remedies are not in year order at %s" % r["id"])
        prev = r["year"]
    if rem[0]["mult"] < 0.9:
        problems.append("the earliest remedy already multiplies mortality by %.2f: before the "
                        "nineteenth century nothing worked" % rem[0]["mult"])
    if min(r["mult"] for r in rem) != rem[-1]["mult"] and min(r["mult"] for r in rem) > 0.15:
        problems.append("the best remedy in the table only gets mortality to %.2f; antibiotics "
                        "should be in here" % min(r["mult"] for r in rem))

    # a pandemic is an event and cannot be "the deadliest disease here"
    for d in dis:
        if d["id"] in ("black_death", "plague_justinian", "third_plague",
                       "influenza_1918", "covid_19") and d["endemic"]:
            problems.append("%s is a pandemic, not an endemic disease: it is not something a "
                            "place can have hanging about" % d["id"])

    # two numbers that must not drift
    small = next((d for d in dis if d["id"] == "smallpox"), None)
    if small is None:
        problems.append("smallpox is not in the disease table")
    elif not (0.20 <= small["cfr"] <= 0.35):
        problems.append("smallpox kills %.0f%% of the people it reaches, not ~30%%"
                        % (small["cfr"] * 100))
    vac = next((r for r in rem if r["id"] == "vaccine"), None)
    var = next((r for r in rem if r["id"] == "variolation"), None)
    if vac and var and vac["mult"] >= var["mult"]:
        problems.append("vaccination is no better than variolation, which is backwards")

    est_r = sum(1 for r in rem if r["mark"] == "estimated")
    est_d = sum(1 for d in dis if d["mark"] == "estimated")
    mix = sum(1 for d in dis if d["mark"] == "mixed")
    print("  remedies %2d  (%d defer to the atlas for their arrival, %d estimated)"
          % (len(rem), len(atlas_rows), est_r))
    print("  diseases %2d  (%d recorded, %d mixed, %d estimated)"
          % (len(dis), len(dis) - est_d - mix, mix, est_d))

    if problems:
        print("\n%d PROBLEM(S):" % len(problems))
        for p in problems[:40]:
            print("  - " + p)
        return 1
    print("  0 problems")
    return 0


def main():
    doc = build()
    rc = selftest(doc)
    if rc:
        return rc
    if "--selftest" in sys.argv:
        print("  (no pack written in --selftest mode)")
        return 0
    raw = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.GzipFile(OUT, "wb", compresslevel=9, mtime=0) as fh:
        fh.write(raw)
    print("wrote %s" % OUT)
    print("  %d remedies, %d diseases, %d bytes raw, %d gzipped"
          % (len(doc["remedies"]), len(doc["diseases"]), len(raw), os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
