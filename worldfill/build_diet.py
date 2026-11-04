#!/usr/bin/env python3
"""
Step 44 part 6 (E6): pack the table of seats, so the game can ask what a place eats.

    python3 build_diet.py            build, then write
    python3 build_diet.py --check    check only, write nothing

The seat table itself lives in `diet_roles.py` and is hand-written, because no register records
that a lentil and a mango play different parts at a table. This script only checks it against the
product atlas and writes it out in the shape the Java reads.

Every id is checked to be a real product before it is written. `diet_roles.check_against` caught
thirteen that were not, and nine of those were crops the atlas genuinely lacked -- apples, citrus,
dates, olives, peas, palm oil, pineapple, soybeans and sweet potatoes -- which Khoury's register
has now placed. The other four were names I had written for things the atlas folds into a wider
product (barley into "wheat and barley", coriander into "cumin and coriander", gourds into
"cucumbers and gourds") and water, which is not a product at all.

Run from the repository root:  python3 worldfill/build_diet.py
"""

import gzip
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data",
                   "eternalengine", "eternal", "food", "seats.json.gz")
PRODUCTS = os.path.join(ROOT, "eternal", "src", "main", "resources", "data",
                        "eternalengine", "eternal", "economy", "products_world.json")

SYS_PATH = sys.path[:]
sys.path.insert(0, HERE)
try:
    import diet_roles as R
finally:
    sys.path = SYS_PATH


def build(products):
    """Check the table, and return it in the shape the game reads."""
    problems = R.check_against(products)

    names = {p["id"]: p["name"] for p in products}
    foods = {}
    for pid, seats in R.SEATS.items():
        # keep the seats in the order a meal is described in, not the order written
        foods[pid] = {"name": names[pid],
                      "seats": [s for s in R.SEAT_ORDER if s in seats]}

    # a seat with nothing in it, and a food that holds no seat, are both errors
    held = {s for seats in R.SEATS.values() for s in seats}
    for s in R.SEAT_ORDER:
        if s not in held:
            problems.append("seat '%s' has no food in it" % s)
    for pid, seats in R.SEATS.items():
        if not seats:
            problems.append("%s holds no seat" % pid)

    doc = {"order": list(R.SEAT_ORDER), "seatWords": R.SEAT_WORDS,
           "bareMinimum": R.BARE_MINIMUM, "foods": foods}
    return doc, problems


def main(argv):
    with open(PRODUCTS, encoding="utf-8") as fh:
        products = json.load(fh)["products"]

    doc, problems = build(products)
    for p in problems:
        print("  PROBLEM " + p)

    n_seats = sum(len(f["seats"]) for f in doc["foods"].values())
    print("diet: %d foods holding %d seats in %d kinds of place at the table"
          % (len(doc["foods"]), n_seats, len(doc["order"])))

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
