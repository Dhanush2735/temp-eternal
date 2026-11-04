#!/usr/bin/env python3
"""Step 47 part 5 (B6, E18): pack the crop and animal spread register."""
import gzip, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data", "eternalengine",
                   "eternal", "economy", "spread.json.gz")
sys.path.insert(0, HERE)
try:
    import spread_table as S
finally:
    sys.path.pop(0)


def build():
    rows = S.build()
    problems = S.check(rows)
    doc = {
        "format": "eternal-spread-1", "id": "spread",
        "areas": S.AREAS,
        "exchange": S.EXCHANGE_YEAR,
        "source": ("the products atlas (step 44) for every year and every area; Khoury et al. "
                   "2016, Proc. R. Soc. B 283: 20160792, for crop origins; the standard accounts "
                   "for the livestock."),
        "note": ("Step 47 part 5 (B6 and E18): CROPS AND ANIMALS AS ITEMS, AS THEY SPREAD. No new "
                 "dates were written for this register: the products atlas already dates maize in "
                 "Europe to 1520 and in Mesoamerica to 7000 BC. What was missing is the other half "
                 "of a spread, which is WHERE THE THING CAME FROM, and without it a potato in "
                 "Bengal in 1700 cannot be told from a potato that was always there. This is a "
                 "JOIN: the atlas says when, the crop origins register says where, and the year a "
                 "crop left home falls out as the earliest year it is made outside its origin "
                 "areas."),
        "finding": ("**The Columbian exchange is measurable and it took about a lifetime.** Every "
                    "American crop in this register is being made in the Old World within a century "
                    "and a half of 1492, and the chilli is in Goa by 1540 and has displaced long "
                    "pepper in Indian cooking inside fifty years: a New World fruit made South "
                    "Asian food into what the world now calls South Asian food, in less than one "
                    "lifetime. **The limit, and it is a real one:** the atlas has 133 hand-written "
                    "rows and 406 derived ones, and a derived row takes its parent's dates, which "
                    "is right for flour and wrong for sorghum (whose parent is millet, so derived "
                    "sorghum 'originates' in China) and for groundnut (which inherits West Asia "
                    "from oilseeds). So this register claims an origin only for hand-written rows "
                    "and every other row says `inherited` and names its parent."),
        "rows": rows,
        "counts": {"rows": len(rows),
                   "crops": sum(1 for r in rows if r["kind"] == "crop"),
                   "animals": sum(1 for r in rows if r["kind"] == "animal"),
                   "handOrigin": sum(1 for r in rows if r["origin"]["source"] == "hand"),
                   "poly": sum(1 for r in rows if r["poly"])},
    }
    assert not problems, problems
    return doc, problems


def main():
    doc, problems = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    raw = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode()
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(raw)
    print("spread.json.gz: %d B (%d raw), %d rows, %d problems"
          % (os.path.getsize(OUT), len(raw), len(doc["rows"]), len(problems)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
