#!/usr/bin/env python3
"""Step 47 part 5 (B5): pack the wild animal register."""
import gzip, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data", "eternalengine",
                   "eternal", "names", "wildlife.json.gz")
sys.path.insert(0, HERE)
try:
    import wildlife_table as W
finally:
    sys.path.pop(0)


def build():
    problems = list(W.problems())
    rows = []
    for s in W.SPECIES:
        rows.append({
            "id": s["id"], "name": s["name"], "mark": s["mark"],
            "from": {a: lo for a, (lo, _hi) in s["areas"].items()},
            "gone": {a: hi for a, (_lo, hi) in s["areas"].items() if hi is not None},
            "never": s["never"], "note": s["note"], "source": s["source"],
        })
    doc = {
        "format": "eternal-wildlife-1", "id": "wildlife",
        "areas": W.AREAS,
        "source": ("the recorded extinctions and extirpations: Jaktorow for the aurochs; the "
                   "Cincinnati Zoo for the passenger pigeon; Hobart for the thylacine; the "
                   "Mauritius records for the dodo; the Gir and 1884 records for the lion; the "
                   "Kuno reintroduction for the cheetah; Hornaday 1889 for the bison."),
        "note": ("Step 47 part 5 (B5): WILD ANIMALS BY ERA. The plan asks for 'lions and cheetahs "
                 "in India, aurochs in Europe, no horses in the Americas before 1493'. The survey "
                 "found that the only wild animal anywhere in this project was the bison, and it "
                 "was there because it was hunted in herds. This register is 14 species and, more "
                 "importantly, it is a register of RANGES ENDING: a wild animal's data is not its "
                 "birth date but the year its range stopped."),
        "finding": ("**Almost every row is one of three stories.** The animal is GONE from one "
                    "place and lives in another (the lion left Greece by 100 BC and India outside "
                    "Gujarat in 1884); the animal is gone EVERYWHERE and the year is known because "
                    "somebody was counting (the aurochs 1627, the passenger pigeon 1914, the "
                    "thylacine 1936); or the animal was NEVER THERE and the absence is the fact, "
                    "which is the plan's own horse. A horse in the Americas in 1200 is not a small "
                    "anachronism, it is the largest biological fact about the continent, and this "
                    "register keeps that as an absence with a reason rather than as a missing row."),
        "species": rows,
        "counts": {"species": len(rows),
                   "extirpatedSomewhere": sum(1 for s in W.SPECIES if any(
                       hi is not None and hi < 2026 for _lo, hi in s["areas"].values())),
                   "extinctEverywhere": sum(1 for s in W.SPECIES if not any(
                       hi is None for _lo, hi in s["areas"].values()))},
    }
    assert not problems, problems
    assert doc["counts"]["species"] >= 12
    return doc, problems


def main():
    doc, problems = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    raw = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode()
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(raw)
    print("wildlife.json.gz: %d B (%d raw), %d species, %d problems"
          % (os.path.getsize(OUT), len(raw), len(doc["species"]), len(problems)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
