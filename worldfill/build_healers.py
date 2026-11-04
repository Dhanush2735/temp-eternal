#!/usr/bin/env python3
"""Step 47 part 6 (E15): pack the healers register."""
import gzip, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data", "eternalengine",
                   "eternal", "history", "healers.json.gz")
sys.path.insert(0, HERE)
try:
    import healers_table as H
finally:
    sys.path.pop(0)


def build():
    problems = list(H.problems())
    rows = []
    for h in H.HEALERS:
        rows.append({
            "id": h["id"], "name": h["name"], "kind": h["kind"], "year": h["year"],
            "reach": h["reach"], "tends": h["tends"], "standing": h["standing"],
            "areas": h["areas"],
            "standingChanges": [{"area": a, "year": y, "standing": st}
                                for a, y, st in h.get("standing_changes", [])],
            "note": h["note"], "source": h["source"],
        })
    doc = {
        "format": "eternal-healers-1", "id": "healers", "areas": H.AREAS,
        "tends": H.TENDS, "reach": H.REACH, "standing": H.STANDING,
        "source": ("the Edwin Smith and Ebers papyri; the Hippocratic corpus; Charaka and "
                   "Sushruta; Ibn Sina; the Baghdad pharmacy regulations; the Malleus "
                   "Maleficarum; the barber-surgeon guilds; Paracelsus in Basel; Nightingale."),
        "note": ("Step 47 part 6 (E15): MEDICINE AND HEALERS BY ERA. **The medicine half was "
                 "already done** - step 38's health register carries 14 remedies with a year, a "
                 "place, a multiplier, and MedicineSystem.tierAt asks it by coordinates, so the old "
                 "fault of the whole planet becoming modern on one day in 1945 is fixed and the "
                 "plan's row saying 'old code' is wrong. **The healers were not done at all.** A "
                 "healer is not a remedy: a remedy is a thing that works and spreads as technology "
                 "spreads, and a healer is a person you can get to. Their data is therefore a "
                 "different shape - who is available, how far you travel, what they will touch, and "
                 "whether the neighbours approve."),
        "finding": ("**Two things a one-axis register cannot say.** (1) **Surgery is four thousand "
                    "years older than anaesthesia**: trepanation is Neolithic, cataract couching is "
                    "described by Sushruta, a Roman army surgeon could ligate an artery, and the "
                    "part where the patient does not feel it starts in 1846 - so a game that gates "
                    "surgery on anaesthesia has the order of events exactly backwards. (2) **The "
                    "midwife is the oldest trained practitioner and the least respected one.** "
                    "Childbirth happens everywhere in every year, so she is the only universal "
                    "healer, which is why the coverage check demands somebody for a birth in every "
                    "area in 3000 BC; and in Europe from about 1450 to 1750 she is the one "
                    "prosecuted, which is a change in STANDING and not an arrival, so this register "
                    "carries two axes and her row uses both."),
        "healers": rows,
        "counts": {"trades": len(rows),
                   "folk": sum(1 for r in rows if r["kind"] == "folk"),
                   "professional": sum(1 for r in rows if r["kind"] == "professional"),
                   "religious": sum(1 for r in rows if r["kind"] == "religious"),
                   "institutional": sum(1 for r in rows if r["kind"] == "institution"),
                   "standingChanges": sum(len(r["standingChanges"]) for r in rows)},
    }
    assert not problems, problems
    assert doc["counts"]["trades"] >= 14
    return doc, problems


def main():
    doc, problems = build()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    raw = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode()
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(raw)
    print("healers.json.gz: %d B (%d raw), %d trades, %d problems"
          % (os.path.getsize(OUT), len(raw), len(doc["healers"]), len(problems)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
