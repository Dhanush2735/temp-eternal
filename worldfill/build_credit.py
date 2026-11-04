#!/usr/bin/env python3
"""
Step 44 part 8 (E19): pack the credit table, so the game can ask what it costs to borrow.

    python3 build_credit.py            build, then write
    python3 build_credit.py --check    check only, write nothing

The table lives in `credit_table.py` and is hand-written, because the numbers are scattered
through the literature and no dataset carries them together. This script only checks it and writes
it out in the shape the Java reads.

Every row carries a mark — **recorded** (a document states the rate), **measured** (worked out
from many records, like the 1,563 cash waqfs of Bursa), or **estimated** — and that mark is shown
to the player, because the Ottoman and English figures are solid enough to lean on and the African
and Andean rows deliberately are not: pre-colonial West Africa had credit without a price for
credit, and the Inca had no money at all.

Run from the repository root:  python3 worldfill/build_credit.py
"""

import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data",
                   "eternalengine", "eternal", "economy", "credit.json.gz")

SYS_PATH = sys.path[:]
sys.path.insert(0, HERE)
try:
    import credit_table as T
finally:
    sys.path = SYS_PATH


def build():
    problems = list(T.problems())

    rows = []
    for r in T.RATES:
        rows.append({
            "id": r["id"], "boxes": [list(b) for b in r["boxes"]],
            "from": r["from"], "to": r["to"],
            "low": r["low"], "high": r["high"],
            "kind": r["kind"], "lender": r["lender"],
            "lawful": r["lawful"], "instead": r["instead"],
            "mark": r["mark"], "note": r["note"], "source": r["source"],
        })

    doc = {"kinds": T.KINDS, "kindWords": T.KIND_WORDS, "lenderWords": T.LENDER_WORDS,
           "rows": rows}
    return doc, problems


def main(argv):
    doc, problems = build()
    for p in problems:
        print("  PROBLEM " + p)

    with_rate = sum(1 for r in doc["rows"] if r["low"] is not None)
    print("credit: %d rows, %d with a rate, %d recording an absence"
          % (len(doc["rows"]), with_rate, len(doc["rows"]) - with_rate))

    if problems or "--check" in argv:
        return 1 if problems else 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    # mtime=0 so the same table always produces the same bytes: what ships is reproducible
    with gzip.GzipFile(OUT, "wb", mtime=0) as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    print("  wrote %s (%d bytes)" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
