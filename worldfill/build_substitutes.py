"""
Builds economy/substitutes.json.gz: what stands in for what, and how hard a shock hits which
kind of work.

Step 44 part E (E5: disruptions and replacements). The disruption half needs no new pack — the
mod already ships 37,201 disasters, 84 climate periods with a yield impact and 14 trade routes,
and `Shortages` reads those directly. The replacement half does: no register anywhere says what
people use instead, and it cannot be derived from what a thing is made of, so it is hand-written
here and shipped.

Also carries WHICH shocks reach WHICH kind of work, so the Python and the Java cannot drift: the
rule lives in one file and both read the same numbers.
"""
import gzip
import io
import json
import os
import sys

import product_substitutes as S

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data", "eternalengine",
                   "eternal", "economy", "substitutes.json.gz")


def build(products):
    problems = list(S.check_against(products))
    rows = []
    for pid, subs in S.SUBSTITUTES.items():
        rows.append({"id": pid, "instead": [{"id": s, "how": how, "why": why}
                                            for s, how, why in subs]})
    rows.sort(key=lambda r: r["id"])

    doc = {
        "id": "substitutes",
        "format": "1",
        "about": ("What people use when the thing they would use is not there, and how hard a "
                  "shock to the land, the hands, the roofs or the road hits each kind of work. "
                  "Part E of step 44 (E5, disruptions and replacements)."),
        "count": len(rows),
        "links": sum(len(r["instead"]) for r in rows),
        "source": "written by hand for this mod; every id is checked against products_world.json",
        "note": ("A substitute is only offered where and when the atlas says it exists: this table "
                 "says what would stand in, not what is to hand."),
        "howGood": {
            "good": "people would barely notice the difference",
            "serves": "it does the job, badly",
            "last resort": "eaten or burned when there is nothing else — the famine case",
        },
        "substitutes": rows,
        # field, hand, roof, trade — the share of each shock that reaches this kind of work
        "shocksReach": {k: list(v) for k, v in S.WORK_SENSITIVITY.items()},
        "shocksReachDefault": list(S.DEFAULT_SENSITIVITY),
        "gaps": ("Only 38 of 529 products have a substitute written. The rest are left blank "
                 "rather than guessed at; a product with no row here has no answer, and the "
                 "mod says so."),
    }
    return doc, problems


def write(path, doc):
    raw = io.BytesIO()
    with gzip.GzipFile(fileobj=raw, mode="wb", compresslevel=9, mtime=0) as gz:
        gz.write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    data = raw.getvalue()
    with open(path, "wb") as fh:
        fh.write(data)
    return len(data)


def main():
    ppath = os.path.join(ROOT, "eternal", "src", "main", "resources", "data", "eternalengine",
                         "eternal", "economy", "products_world.json")
    with open(ppath, encoding="utf-8") as fh:
        products = json.load(fh)["products"]

    doc, problems = build(products)
    if problems:
        for p in problems:
            print("  PROBLEM", p)
        print("nothing written")
        return 1

    n = write(OUT, doc)
    print("substitutes.json.gz: %d products, %d links, %d kinds of work, %d bytes" % (
        doc["count"], doc["links"], len(doc["shocksReach"]), n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
