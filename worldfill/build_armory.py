#!/usr/bin/env python3
"""
Step 45 part 2 (E9 A): pack the armoury, so the game can ask what weapons exist here.

    python3 build_armory.py            build, then write
    python3 build_armory.py --check    check only, write nothing

The register lives in `armory_table.py`. This script only checks it and writes it out; it does not
decide anything. The dates come from three places and the Java joins them at runtime:

- **hand-written per-area years**, for the melee family, because the product atlas derives those
  from *materials* (spears from bows, daggers from copper, shields from leather) and gets them
  wrong;
- **the technology atlas**, for the thirteen kinds that have a tech row, which is 258 countries
  with spread-modelled arrival years;
- **the product atlas**, for the rest.

Run from the repository root:  python3 worldfill/build_armory.py
"""

import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data",
                   "eternalengine", "eternal", "war", "armory.json.gz")

SYS_PATH = sys.path[:]
sys.path.insert(0, HERE)
try:
    import armory_table as T
finally:
    sys.path = SYS_PATH


def build():
    problems = list(T.problems())

    rows = []
    for k in T.ARMORY:
        # A None year means "never", and that is already said in `never`. Dropping it here keeps
        # a JSON null out of the pack, which the Java would otherwise read as an integer.
        years = None
        if k["years"] is not None:
            years = {a: y for a, y in k["years"].items() if y is not None}
            for a in (k.get("never") or {}):
                years.pop(a, None)
        rows.append({
            "id": k["id"], "arm": k["arm"], "name": k["name"],
            "role": k["role"], "use": k["use"],
            "tech": k["tech"], "product": k["product"], "material": k["material"],
            "years": years, "end": k.get("end") or {}, "endTech": k.get("endTech"),
            "never": k.get("never") or {},
            "supersedes": k.get("supersedes") or [],
            "vanilla": k["vanilla"], "mark": k["mark"], "note": k["note"],
            "source": k["source"],
        })

    doc = {"areas": T.AREAS, "d10Arms": T.D10_ARMS, "roles": T.ROLES, "rows": rows}
    return doc, problems


def main(argv):
    doc, problems = build()
    for p in problems:
        print("  PROBLEM " + p)

    hand = sum(1 for r in doc["rows"] if r["years"] is not None)
    print("armory: %d kinds, %d hand-dated, %d from the atlases, %d recorded absences"
          % (len(doc["rows"]), hand, len(doc["rows"]) - hand,
             sum(len(r["never"]) for r in doc["rows"])))

    if problems or "--check" in argv:
        return 1 if problems else 0

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    # mtime=0 so the same register always produces the same bytes: what ships is reproducible
    with gzip.GzipFile(OUT, "wb", mtime=0) as fh:
        fh.write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    print("  wrote %s (%d bytes)" % (os.path.relpath(OUT, ROOT), os.path.getsize(OUT)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
