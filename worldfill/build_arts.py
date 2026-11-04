#!/usr/bin/env python3
"""Step 47 part 6 (C15): pack the music and arts register."""
import gzip, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data", "eternalengine",
                   "eternal", "names", "arts.json.gz")
sys.path.insert(0, HERE)
try:
    import arts_table as A
finally:
    sys.path.pop(0)


def build():
    problems = list(A.problems())
    rows = [{"id": a["id"], "name": a["name"], "kind": a["kind"], "year": a["year"],
             "home": a["home"], "equipment": a["equipment"], "spread": a["spread"],
             "note": a["note"], "source": a["source"]} for a in A.ARTS]
    doc = {
        "format": "eternal-arts-1", "id": "arts", "areas": A.AREAS, "kinds": A.KINDS,
        "source": ("the Hohle Fels bone flute; the Ur and Theban harp paintings; the 757 Byzantine "
                   "organ; the 868 Dunhuang Diamond Sutra; the van Eyck Ghent altarpiece; the 1839 "
                   "French Academy announcement; Edison's 1877 phonograph."),
        "note": ("Step 47 part 6 (C15): CULTURE, the last part of it. The plan's row is 'clothes, "
                 "food, music, games, customs, arts' and by the end of this part four of the six "
                 "live somewhere: clothes in part 4's 27 period garments, food in step 44's atlas "
                 "and step 45's diet register, games in part 6's 21, customs in CultureAtlas's "
                 "21,000 holy places and its feasts, scripts and measures. **Music and the arts had "
                 "nothing at all**, and this is them. There is no such thing as the year a place "
                 "got music, so the register is not of music but of THE THINGS THAT CARRY MUSIC AND "
                 "PICTURES - an instrument, a medium, a way of copying - which is a technology "
                 "history and dates honestly."),
        "finding": ("**Every art form here is older than the means of copying it, and copying "
                    "changes what the art is.** Painting is as old as people; the oil medium, the "
                    "woodblock, the engraving, the photograph and the recording each arrive late and "
                    "each changes who can own a picture or hear a piece of music. The two sharpest "
                    "dates are the phonograph in 1877, which separates a performance from the "
                    "performer for the first time in the history of the species, and photography in "
                    "1839, which arrives after the oil painting it replaces as the way to record a "
                    "face and before the cinema it makes possible in 1895."),
        "arts": rows,
        "counts": {"rows": len(rows),
                   "universal": sum(1 for r in rows if len(r["spread"]) == len(A.AREAS)),
                   "oldest": min(rows, key=lambda r: r["year"])["id"],
                   "newest": max(rows, key=lambda r: r["year"])["id"],
                   "copies": sum(1 for r in rows if r["kind"] in ("copy", "record"))},
    }
    assert not problems, problems
    assert doc["counts"]["rows"] >= 12
    return doc, problems


def main():
    doc, problems = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    raw = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode()
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(raw)
    print("arts.json.gz: %d B (%d raw), %d rows, %d problems"
          % (os.path.getsize(OUT), len(raw), len(doc["arts"]), len(problems)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
