#!/usr/bin/env python3
# ============================================================
# Step 34 part 4 (B24): what lies under the ground.
#
#   python3 build_minerals.py           build history/minerals.json.gz
#   python3 build_minerals.py --check   read it back and check it
#   python3 build_minerals.py --places  what each test place has under it
#
# Three layers, because no one source answers the question:
#
#  1. USGS MRDS (`mrdata.usgs.gov/mrds`, public domain): 283,601 records with
#     a point and a commodity, clustered here at 1 km into 144,841 sites. It is
#     82% American and gives a production year for only 5% of them, and it
#     knows almost nothing about coal (118 sites) or oil (184).
#  2. A hand-written table of 86 famous deposits and coalfields
#     (`famous_deposits_table.py`), each naming the Wikipedia article it comes
#     from, with its coordinates taken from Wikipedia (or Wikidata where the
#     article carries none) and never written by hand. This is what supplies
#     Laurium and Almadén, Hallstatt and Golconda, the Ruhr and Donbas.
#  3. Wikidata's oil fields (209 rows) — a deposit class Wikidata does have,
#     unlike gold mines, of which Wikidata knows two.
#
# The pack answers "what is under this square, and since when" — the geology
# does not change, but whether anyone can work it does, and that is gated by
# the technology atlas in the register.
# ============================================================
import csv
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import modpack as M  # noqa: E402

MRDS = os.path.join(HERE, "build", "minerals", "raw", "mrds.csv")
WIKI = os.path.join(HERE, "build", "minerals", "raw", "wiki.json")
WDCOORD = os.path.join(HERE, "build", "minerals", "raw", "wikidata_coords.json")
WAYS = os.path.join(HERE, "build", "ways", "raw")
OUT = os.path.join(M.HISTORY, "minerals.json.gz")

# keyword -> mineral, tried in order; the first match wins. The order matters:
# "gold, silver" must be GOLD, and "fire clay" must be CLAY and not IRON.
MAP = [
    ("gold", "GOLD"), ("silver", "SILVER"), ("copper", "COPPER"), ("iron", "IRON"),
    ("lead", "LEAD"), ("zinc", "ZINC"), ("tin", "TIN"), ("coal", "COAL"),
    ("uranium", "URANIUM"), ("manganese", "MANGANESE"), ("chromium", "CHROMIUM"),
    ("tungsten", "TUNGSTEN"), ("molybdenum", "MOLYBDENUM"), ("nickel", "NICKEL"),
    ("mercury", "MERCURY"), ("antimony", "ANTIMONY"), ("aluminum", "BAUXITE"),
    ("aluminium", "BAUXITE"), ("platinum", "PLATINUM"), ("pge", "PLATINUM"),
    ("platinum group", "PLATINUM"), ("iridium", "PLATINUM"), ("osmium", "PLATINUM"),
    ("palladium", "PLATINUM"), ("diamond", "GEMS"), ("gemstone", "GEMS"),
    ("emerald", "GEMS"), ("ruby", "GEMS"), ("sapphire", "GEMS"), ("turquoise", "GEMS"),
    ("jade", "GEMS"), ("opal", "GEMS"), ("garnet", "GEMS"), ("corundum", "ABRASIVE"),
    ("emery", "ABRASIVE"), ("abrasive", "ABRASIVE"), ("salt", "SALT"), ("halite", "SALT"),
    ("potash", "POTASH"), ("nitrate", "NITRATE"), ("saltpeter", "NITRATE"),
    ("sulfur", "SULPHUR"), ("sulphur", "SULPHUR"), ("pyrite", "SULPHUR"),
    ("gypsum", "GYPSUM"), ("phosphate", "PHOSPHATE"), ("graphite", "GRAPHITE"),
    ("mica", "MICA"), ("talc", "TALC"), ("barite", "BARITE"), ("fluor", "FLUORITE"),
    ("asbestos", "ASBESTOS"), ("silica", "SILICA"), ("quartz", "SILICA"),
    ("feldspar", "FELDSPAR"), ("pumice", "PUMICE"), ("perlite", "PERLITE"),
    ("diatomite", "DIATOMITE"), ("magnesite", "MAGNESITE"), ("beryllium", "BERYLLIUM"),
    ("vanadium", "VANADIUM"), ("titanium", "TITANIUM"), ("cobalt", "COBALT"),
    ("arsenic", "ARSENIC"), ("bismuth", "BISMUTH"), ("cadmium", "CADMIUM"),
    ("lithium", "LITHIUM"), ("rare earth", "RARE_EARTH"), ("ree", "RARE_EARTH"),
    ("thorium", "RARE_EARTH"), ("monazite", "RARE_EARTH"), ("niobium", "RARE_EARTH"),
    ("tantalum", "RARE_EARTH"), ("zirconium", "RARE_EARTH"), ("petroleum", "OIL"),
    ("oil", "OIL"), ("gas", "OIL"), ("peat", "PEAT"), ("ochre", "OCHRE"),
    ("pigment", "OCHRE"), ("flint", "FLINT"), ("amber", "AMBER"), ("kaolin", "CLAY"),
    ("bentonite", "CLAY"), ("montmorillonite", "CLAY"), ("fullers", "CLAY"),
    ("clay", "CLAY"), ("shale", "CLAY"), ("dolomite", "LIMESTONE"),
    ("limestone", "LIMESTONE"), ("marble", "MARBLE"), ("granite", "GRANITE"),
    ("slate", "SLATE"), ("sandstone", "SANDSTONE"), ("geothermal", None),
    ("stone", None), ("sand", None), ("gravel", None), ("aggregate", None),
]
# sand, gravel and crushed stone are dropped on purpose: 68,891 of the 283,601
# records, and a pit of building aggregate is not what anyone means by a
# mineral deposit.


def mineral_of(text):
    t = (text or "").lower()
    for k, v in MAP:
        if k in t:
            return v
    return None


def from_mrds():
    """MRDS -> clustered sites. Clustering at 1 km keeps the pack small and
    merges the several records USGS often holds for one mine."""
    csv.field_size_limit(10_000_000)
    rows = {}
    with open(MRDS, newline="", encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            try:
                la = float(r.get("latitude") or "")
                lo = float(r.get("longitude") or "")
            except ValueError:
                continue
            if not (-90 <= la <= 90 and -180 <= lo <= 180) or (la == 0 and lo == 0):
                continue
            mins = []
            for k in ("commod1", "commod2", "commod3"):
                m = mineral_of((r.get(k) or "").strip())
                if m and m not in mins:
                    mins.append(m)
            if not mins:
                continue
            y1 = (r.get("yr_fst_prd") or "").strip()
            d = (r.get("disc_yr") or "").strip()
            y2 = (r.get("yr_lst_prd") or "").strip()
            yr = int(y1) if y1.isdigit() and 1000 <= int(y1) <= 2030 else (
                int(d) if d.isdigit() and 1000 <= int(d) <= 2030 else None)
            end = int(y2) if y2.isdigit() and 1000 <= int(y2) <= 2030 else None
            name = (r.get("site_name") or "").strip()
            if name.lower().startswith(("unnamed", "unamed", "unknown", "no name")):
                name = ""
            # MRDS also holds plants and refineries — a "(Facility) Acton
            # Refinery" is not a deposit, and a "Vanadium Operation" is a
            # chemical works that happened to be given coordinates.
            stat = (r.get("dev_stat") or "").strip()
            if stat == "Plant" or name.startswith("(Facility)") or " Operation" in name:
                continue
            st = {"Producer": 3, "Past Producer": 2, "Prospect": 1}.get(stat, 0)
            key = (round(la, 2), round(lo, 2))
            cur = rows.get(key)
            if cur is None:
                rows[key] = [round(la, 3), round(lo, 3), mins, yr, end, name, st]
                continue
            for m in mins:
                if m not in cur[2]:
                    cur[2].append(m)
            if yr is not None and (cur[3] is None or yr < cur[3]):
                cur[3] = yr
            if end is not None and (cur[4] is None or end > cur[4]):
                cur[4] = end
            if not cur[5] and name:
                cur[5] = name
            if st > cur[6]:            # the strongest evidence any record gives
                cur[6] = st
    return list(rows.values())


def from_hand():
    """The 86 famous deposits. Every row's coordinates come from Wikipedia, or
    from Wikidata where the article carries none — never from my own memory."""
    import famous_deposits_table as T
    wiki = json.load(open(WIKI, encoding="utf-8"))
    wd = json.load(open(WDCOORD, encoding="utf-8")) if os.path.exists(WDCOORD) else {}
    out = []
    for article, mins, start, end, note in T.ROWS:
        res = wiki["resolved"].get(article, {})
        c = res.get("coord")
        if c:
            la, lo = c["lat"], c["lon"]
        elif article in wd:
            la, lo = wd[article]["lat"], wd[article]["lon"]
        else:
            print(f"  WARNING: no coordinates for {article}")
            continue
        out.append([round(la, 3), round(lo, 3), list(mins), start, end, article, 3])
    return out


def from_wikidata():
    path = os.path.join(WAYS, "class_Q211748.json")
    if not os.path.exists(path):
        return []
    labels = json.load(open(os.path.join(WAYS, "labels.json"), encoding="utf-8"))
    out = []
    for r in json.load(open(path, encoding="utf-8")):
        out.append([r["lat"], r["lon"], ["OIL"], r.get("start"), r.get("end"),
                    labels.get(r["q"], ""), 2])
    return out


def build():
    mrds = from_mrds()
    hand = from_hand()
    wd = from_wikidata()
    print(f"usgs mrds:   {len(mrds):,} clustered sites "
          f"({sum(1 for r in mrds if r[3]):,} with a year)")
    print(f"by hand:     {len(hand):,} famous deposits and coalfields")
    print(f"wikidata:    {len(wd):,} oil fields")

    vocab = sorted({m for r in mrds + hand + wd for m in r[2]})
    idx = {m: i for i, m in enumerate(vocab)}
    sites = []
    for src, rows in ((0, mrds), (1, hand), (2, wd)):
        for la, lo, mins, start, end, name, st in rows:
            ids = [idx[m] for m in mins if m in idx]
            if not ids:
                continue
            sites.append([la, lo, ids, start, end, name or None, st, src])
    pack = {
        "format": "eternalengine/minerals@1",
        "about": "what lies under the ground: mineral deposits and coalfields, "
                 "with the years they were worked where any source knows them",
        "source": [
            {"name": "USGS Mineral Resources Data System (MRDS)",
             "url": "https://mrdata.usgs.gov/mrds/", "licence": "public domain (USGS)",
             "rows": len(mrds)},
            {"name": "Wikipedia (hand-written table of famous deposits, "
                     "coordinates taken from the articles)",
             "url": "https://en.wikipedia.org/", "licence": "CC BY-SA 4.0",
             "rows": len(hand)},
            {"name": "Wikidata, oil fields (Q211748)",
             "url": "https://www.wikidata.org/", "licence": "CC0", "rows": len(wd)},
        ],
        "minerals": vocab,
        "status": ["occurrence", "prospect", "past producer", "producer"],
        "sites": sites,
    }
    raw = json.dumps(pack, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with gzip.GzipFile(filename="", mode="wb", fileobj=open(OUT, "wb"), compresslevel=9, mtime=0) as f:
        f.write(raw)
    dated = sum(1 for s in sites if s[3] is not None)
    print(f"minerals.json.gz: {len(sites):,} sites, {dated:,} with a year, "
          f"{len(vocab)} minerals, {len(raw):,} bytes raw, "
          f"{os.path.getsize(OUT):,} bytes gzipped")


def check():
    d = json.loads(gzip.open(OUT, "rt").read())
    assert d["format"].startswith("eternalengine/minerals@")
    sites = d["sites"]
    bad = [s for s in sites if not (-90 <= s[0] <= 90 and -180 <= s[1] <= 180)]
    bad2 = [s for s in sites if not s[2]]
    print(f"minerals.json.gz: {len(sites):,} sites, {len(d['minerals'])} minerals, "
          f"{sum(1 for s in sites if s[3] is not None):,} with a year, "
          f"{sum(1 for s in sites if s[5]):,} named, "
          f"{sum(1 for s in sites if s[6] >= 2):,} worked (past or present)")
    print(f"  {len(bad)} sites with a bad point, {len(bad2)} with no mineral")
    from collections import Counter
    c = Counter()
    for s in sites:
        for i in s[2]:
            c[d["minerals"][i]] += 1
    print("  mineral coverage:", ", ".join(f"{k} {v:,}" for k, v in c.most_common(12)))
    return 1 if bad or bad2 else 0


def places():
    from math import cos, radians
    from fetch_town_wd import TEST_PLACES
    d = json.loads(gzip.open(OUT, "rt").read())
    sites = d["sites"]
    for name, lat, lon, year in TEST_PLACES:
        got = []
        for s in sites:
            if abs(s[0] - lat) <= 0.5 and abs(s[1] - lon) <= 0.5 / max(0.2, cos(radians(lat))):
                if s[3] is not None and s[3] > year:
                    continue
                got.extend(d["minerals"][i] for i in s[2])
        c = sorted(set(got))
        print(f"  {name:12s} {year:>6d}  {', '.join(c[:9]) if c else 'nothing recorded'}")


def main(argv):
    mode = argv[1] if len(argv) > 1 else ""
    if mode == "--check":
        sys.exit(check())
    elif mode == "--places":
        places()
    else:
        build()


if __name__ == "__main__":
    main(sys.argv)
