#!/usr/bin/env python3
"""Step 47 part 4 (E12, E21): pack the period wardrobe."""
import gzip, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data", "eternalengine",
                   "eternal", "names", "wardrobe.json.gz")
sys.path.insert(0, HERE)
try:
    import wardrobe_table as W
finally:
    sys.path.pop(0)


def build():
    problems = list(W.problems())
    rows = [{"name": g["name"], "part": g["part"], "female": g["female"],
             "arrival": g["arrival"], "cultures": g["cultures"], "roles": g["roles"],
             "mark": g["mark"], "note": g["note"], "source": g["source"]}
            for g in W.GARMENTS]
    doc = {
        "format": "eternal-wardrobe-1", "id": "wardrobe",
        "source": ("Egyptian and Mesopotamian textile finds and the Roman tunica; Roman sumptuary "
                   "practice for the toga; Greek vase painting for the chiton and peplos; Han and "
                   "Tang tomb figures for the hanfu; Ottoman and Safavid regulation for the kaftan; "
                   "European tailoring history for the doublet and hose in the 1340s; Heian court "
                   "dress for the kimono; Mesoamerican and Andean textile history for the huipil and "
                   "poncho; Sahelian textile trade for the boubou."),
        "note": ("Step 47 part 4 (E12): THE PERIOD WARDROBE. **The bug: SkinPoolDatabase's 40 "
                 "garments all arrive in 1873 or later** - jeans 1873, button_down 1900, crew_tee "
                 "1913 - so the code returns an EMPTY outfit for any year before the pool's modern "
                 "turning point, and **every person in the world before 1945 is dressed in "
                 "nothing**. The plan called E12 'partly: looks by era' and it is not: it is looks "
                 "by the MODERN era, and six thousand years of the world are bare. The pools carry a "
                 "`lower` (dhoti, sari, tunic, robe, wrap) and a handful of cultural items, so the "
                 "missing half is precise and a little comic: **the top half of the body**. A weaver "
                 "in the Deccan in 1400 wears a dhoti and no shirt. This pack adds 25 garments that "
                 "exist before the machine age, with the year each arrives, the part of the body it "
                 "covers and which culture pools wear it, drawn by the same code from the same "
                 "palette as the modern ones."),
        "finding": ("**The wardrobe is a technology, and its dates are the history of tailoring.** "
                    "Almost everything before 1300 is a rectangle: the tunic, the chiton, the hanfu, "
                    "the huipil, the poncho and the wrapper are all cloth with holes in and none of "
                    "them needs a curved seam. The doublet of the 1340s is the first European "
                    "garment CUT to a body, and everything fitted that Europe has worn since "
                    "follows from that one change in a tailor's technique - in the same decade as "
                    "the Black Death."),
        "garments": rows,
        "counts": {"garments": len(rows), "before1873": sum(1 for r in rows if r["arrival"] < 1873),
                   "cultures": len({c for r in rows for c in r["cultures"]}),
                   "recorded": sum(1 for r in rows if r["mark"] == "recorded"),
                   "estimated": sum(1 for r in rows if r["mark"] == "estimated"),
                   "earliest": min(r["arrival"] for r in rows)},
    }
    return doc, problems


def check(doc):
    bad = []
    def ok(c, what):
        print(("  ok   " if c else "  FAIL ") + what)
        if not c: bad.append(what)
    c = doc["counts"]
    ok(doc["format"] == "eternal-wardrobe-1", "the format is the one this builder writes")
    ok(c["garments"] >= 24, "%d garments" % c["garments"])
    ok(c["before1873"] == c["garments"], "every one of them is before 1873")
    ok(c["earliest"] <= -3000 or c["earliest"] == -3000,
       "the earliest is %d, at the world's first year" % c["earliest"])
    ok(c["cultures"] == 11, "all 11 culture pools have something to wear")
    # THE FIX, STATED AS A TEST.
    for cult in W_NAMES:
        tops = [r for r in doc["garments"] if cult in r["cultures"]
                and r["part"] in ("top", "dress")]
        ok(bool(tops), "the %s pool has an upper garment before the machine age" % cult)
    # The 1340s, which is the finding.
    dbl = next(r for r in doc["garments"] if r["name"] == "doublet")
    ok(1340 <= dbl["arrival"] <= 1350, "the doublet is dated to the 1340s")
    ok("curved seam" in dbl["note"] or "cut and sewn" in dbl["note"],
       "and the row says what it invented: cutting rather than draping")
    # A rectangle needs no tailor, and the oldest rows must be rectangles.
    for name in ("tunic", "chiton", "hanfu", "huipil", "poncho", "wrapper_top"):
        g = next((r for r in doc["garments"] if r["name"] == name), None)
        ok(g is not None and g["arrival"] < 1200,
           name + " is a rectangle and predates the tailor")
    # The trap this register exists to prevent.
    sh = next(r for r in doc["garments"] if r["name"] == "sherwani")
    ok(sh["arrival"] >= 1700, "the sherwani is dated late, as the 19th-century coat it is")
    ok("error" in sh["note"], "and its note names the error of dressing a Mughal nobleman in one")
    ok("guild" in doc["finding"] or "tailor" in doc["finding"], "the finding names the tailor")
    return bad


W_NAMES = W.CULTURES


def main(argv):
    doc, problems = build()
    for p in problems: print("  PROBLEM " + p)
    c = doc["counts"]
    print("wardrobe: %d garments, all before 1873, earliest %d, %d recorded and %d estimated"
          % (c["garments"], c["earliest"], c["recorded"], c["estimated"]))
    bad = check(doc)
    if problems or bad or "--check" in argv:
        return 1 if (problems or bad) else 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with gzip.GzipFile(OUT, "wb", mtime=0) as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    print("  wrote %s (%d bytes)" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
