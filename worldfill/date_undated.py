#!/usr/bin/env python3
# ============================================================
# Step 32, part 2: date the structures Wikidata cannot date.
#
#   python3 date_undated.py            join, date, and report
#
# Why this file exists
# --------------------
# Part 1 fetched only structures Wikidata can date (P571 inception or P1619
# opening). That filter is what left the ancient world empty. 9,839 of 11,656
# notable archaeological sites carry no date at all, and with them Mohenjo-daro,
# Great Zimbabwe, Hampi and Teotihuacan -- the very places B19 names.
#
# So the date comes from the mod's own gazetteer, which already knows all of
# them: mohenjo_daro -2600..-1900, teotihuacan 100..550, great_zimbabwe
# 1100..1450, hampi 1336..1565, yinxu_anyang -1300..-1046.
#
# The rule, and why it is not a blanket inheritance
# -------------------------------------------------
# A site's occupiedStart..occupiedEnd is the window the *place* was occupied.
# Handing that to every building nearby would be wrong, and the first run of
# this script proved it: it dated 629 castles and 1,095 churches from Pleiades,
# because a medieval church 3 km from a Roman villa is not a Roman villa.
#
# So a structure takes a site's date only under one of two rules.
#
#   RULE A -- it IS the site. The English label matches the site's name.
#             "Mohenjo-daro" / mohenjo_daro, "Great Zimbabwe" /
#             great_zimbabwe, "Teotihuacan" / teotihuacan. Any class, up to
#             25 km, because a match this specific is not a coincidence.
#
#   RULE B -- it is ON the site, and is the kind of thing an abandoned place
#             is made of. Within 2 km, and its class is archaeological site,
#             tomb, stupa, citadel, city gate, fort or fortification. A church,
#             mosque, palace, bridge, monastery, theatre or tower is excluded:
#             those are later buildings that happen to stand near the old one.
#
# Otherwise it stays undated. A missing date is a gap; a wrong date is a
# building standing centuries before it was built, which is the one thing R1
# cannot show.
#
# Precedence when several sites could donate follows the convention the packs
# state about themselves in their own comparedSources: a curated region pack
# outranks Pleiades, which outranks Reba. Curated first, then Pleiades and
# CHGIS, then Reba; nearest wins inside a tier.
#
# The record horizon
# ------------------
# Some ends are not abandonments, they are where the source stops: Pleiades
# ends at AD 641, the Mediterranean pack at 1453, CHGIS at 1911. A site whose
# occupiedEnd equals its pack's latest end is flagged end_is_record_horizon, so
# nothing downstream reads "not attested after 641" as "demolished in 641".
# The date stays useful -- a villa attested -30..641 does not stand in 1200 --
# and the flag keeps the difference visible.
#
# Everything this script writes is marked estimated, and carries the donating
# site and its own confidence, per system A5.
# ============================================================
import gzip
import json
import os
import re
import sys
from math import radians, sin, cos, asin, sqrt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from fetch_buildings_wd import TEST_PLACES  # noqa: E402  (the one world-wide set)

RAW = os.path.join(HERE, "build", "buildings", "raw")
WRAW = os.path.join(HERE, "build", "water", "raw")
# One label store, built by fetch_buildings_wd.py --labels and kept beside the
# buildings: step 33 added the water, material and style QIDs to it, so the
# water run reads the same file rather than a second, emptier one.
LABELS_PATH = os.path.join(HERE, "build", "buildings", "raw", "labels.json")
LOGS = os.path.join(HERE, "logs")
HISTORY = os.path.join(HERE, "..", "eternal", "src", "main", "resources",
                       "data", "eternalengine", "eternal", "history")

OPEN_END = 9999               # the gazetteer's marker for "still occupied"

# Curated region packs: hand-authored, and often the monument itself.
CURATED = {"indus_harappan", "mesopotamia", "egypt", "china", "mediterranean",
           "south_asia", "americas", "afro_islamic"}
# Scholarly gazetteers of places, imported in bulk.
GAZETTEER = {"pleiades_places", "chgis_county_seats"}
# City population estimates -- the weakest claim on a building's date.
POPULATION = {"reba_cities"}

PACKS = ["indus.json", "mesopotamia.json", "egypt.json", "china.json",
         "mediterranean.json", "south_asia.json", "americas.json",
         "afro_islamic.json", "places_pleiades.json.gz",
         "places_chgis.json.gz", "places_reba.json.gz"]

TIER_RADIUS_KM = {1: 10.0, 2: 2.0, 3: 2.0}
NAME_RADIUS_KM = 25.0

# Rule B: the things an abandoned place is actually made of.
ON_SITE_CLASSES = {"archaeological site", "tomb", "stupa", "citadel",
                   "city gate", "fort", "fortification",
                   # part 5: what an abandoned place is made of, once the walls
                   # and the amphitheatre are classes of their own
                   "city walls", "defensive wall", "rampart", "amphitheatre",
                   "Roman amphitheatre", "ruins", "castle ruin"}

# ---- step 33 (B25): the same two rules, for water works ------------------
# Rule B for water: the water works an abandoned place is actually made of --
# a cistern, a well, a stepwell, an aqueduct, a bath house. NOT a reservoir, a
# water tower, a fountain or a modern onsen: those are 19th- and 20th-century
# things that happen to stand near old ground, and handing them a Roman
# window would put them a thousand years before their time.
WATER_ON_SITE_CLASSES = {"cistern", "Roman cistern", "well", "holy well",
                         "stepwell", "aqueduct", "Roman baths", "bathhouse",
                         "hammam", "qanat", "drain", "latrine", "cesspit"}
# Step 35, part 4: the works of the field are NOT put in the list above, though it is tempting --
# a canal, a terrace or a mill standing two kilometres from an abandoned site is usually not of
# it. Samarkand's rowing canal would have taken a window of 712 BCE, the Hellinikon Olympic
# canoe slalom an Athenian one, and Dujiangyan, built in 256 BCE, the window of a Sui county
# seat eight centuries later. They may take a site's window when the name matches, and not
# otherwise: an undated work is honest, a work dated eight hundred years wrong is not.
# Rule A for water: with a name match, any water work may take the site's
# window -- "the Great Bath, Mohenjo-daro" is the site, and so is Marib's dam.
# A dam, a polder, a levee, an artesian well and a water wheel are name-only:
# they are modern things that happen to stand near old ground, and handing them
# a Roman window would put them a thousand years before their time.
WATER_NAME_CLASSES = WATER_ON_SITE_CLASSES | {
    "fountain", "water tower", "reservoir", "water reservoir", "hot spring bath",
    "water works", "water pump", "noria", "shadoof", "public bath", "bath house",
    "dam", "polder", "levee", "artesian well", "water wheel",
    "polder windmill", "Aflaj Irrigation System of Oman",
    # Step 35, part 4 (B17). Of the field's works only the ones that ARE the place may take a
    # window, and only on a name match: an oasis, a terrace, a chinampa, a paddy field, an
    # irrigation tank. A canal, a dam, a weir, a mill, a polder or a levee is built beside a
    # place without being of it -- Samarkand's rowing canal, opened in 2024, would have taken
    # Samarkand's window of 712 BCE, and the Samarra Barrage of 1956 a window of 1500. Those
    # ship undated, which is to say they do not ship at all: better absent than eight centuries
    # wrong. Dujiangyan, built in 256 BCE, is the price of this rule, and is recorded here so
    # that the gap is not forgotten when the written table of water works is made.
    "oasis", "terrace", "chinampa", "paddy field", "subak", "irrigation tank"}

# Rule A allows a little more, because the name match does the work: a temple
# or a palace can be the site (Tikal Temple I, Taj Mahal as a tomb).
NAME_CLASSES = ON_SITE_CLASSES | {"temple", "palace"}
# "monument" and "tower" are too generic to trust on a name alone -- "Monument
# of Liberty, Istanbul" is not Byzantine. They are allowed only when the thing
# is physically on the site, close enough that it cannot be a coincidence.
NAME_CLASSES_NEAR = NAME_CLASSES | {"monument", "tower"}
NEAR_KM = 2.0
# Never: these are building types that are essentially never the ancient place,
# however they are named. A mosque called "Jama Masjid, Champaner" and a theatre
# called "Damascus Opera House" both name the city without being of its era.
NEVER_CLASSES = {"church building", "mosque", "monastery", "theatre building",
                 "bridge"}


def km(lat1, lon1, lat2, lon2):
    p1, p2 = radians(lat1), radians(lat2)
    dp, dl = radians(lat2 - lat1), radians(lon2 - lon1)
    h = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return 2 * 6371 * asin(min(1, sqrt(h)))


def norm(s):
    """Fold a name down for comparison: 'Mohenjo-daro' -> 'mohenjodaro'."""
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def names_match(label, site):
    """Is this structure the site itself, not merely near it?"""
    a = norm(label)
    if len(a) < 5:
        return False
    for b in (norm(site.get("name")), norm(site.get("id"))):
        if len(b) < 5:
            continue
        if a == b:
            return True
        short, long_ = (a, b) if len(a) <= len(b) else (b, a)
        if long_.startswith(short) or short in long_:
            return True
    return False


def tier_of(pack):
    if pack in CURATED:
        return 1
    if pack in GAZETTEER:
        return 2
    return 3


def load_sites():
    """Every gazetteer site, with its tier and whether its end can be trusted.

    A bulk pack's end years are often not abandonments but bookkeeping: Pleiades
    simply stops at AD 641, Reba splits every city's life at 641 and 1500 and
    pads the end out to the next survey year. "Cologne 800..1500" read literally
    would put Cologne in ruins after 1500. So a year that a large share of a
    pack's sites ends on is an artifact of that pack, and such sites do not
    donate an end date at all. Curated packs are exempt: their ends are
    hand-authored events (hampi 1565 is the sack of Vijayanagara).
    """
    from collections import Counter
    sites, skipped_open, skipped_end = [], 0, 0
    for f in PACKS:
        p = os.path.join(HISTORY, f)
        if not os.path.exists(p):
            print(f"  missing pack: {f}")
            continue
        opener = gzip.open if f.endswith(".gz") else open
        with opener(p, "rt", encoding="utf-8") as fh:
            d = json.load(fh)
        pack = d.get("id")
        tier = tier_of(pack)
        ss = d.get("sites", [])
        closed = [s for s in ss
                  if s.get("occupiedEnd") is not None
                  and s["occupiedEnd"] < OPEN_END
                  and s.get("occupiedStart") is not None
                  and s.get("lat") is not None]
        counts = Counter(s["occupiedEnd"] for s in closed)
        # 2% of the pack and at least 20 sites: too common to be a real event.
        artifact = {y for y, n in counts.items()
                    if n >= 20 and n >= 0.02 * len(closed)} if tier > 1 else set()
        # The pack's record horizon: its latest end, ignoring "still occupied".
        horizon = max((s["occupiedEnd"] for s in closed), default=None)
        for s in closed:
            en = s["occupiedEnd"]
            if tier > 1 and (en in artifact or en == horizon):
                skipped_end += 1
                continue
            sites.append({
                "id": s.get("id"), "name": s.get("name") or s.get("id"),
                "pack": pack, "tier": tier,
                "lat": s["lat"], "lon": s["lon"],
                "start": s["occupiedStart"], "end": en,
                "end_is_record_horizon": (en == horizon),
                "confidence": s.get("confidence", "medium"),
                "civHint": s.get("civHint"),
                "rank": s.get("rank"),
            })
    return sites, skipped_open, skipped_end


class Grid:
    """Coarse lat/lon buckets, so the join is not 31k x 20k distance calls."""

    def __init__(self, cell=0.25):
        self.cell = cell
        self.b = {}

    def add(self, item):
        self.b.setdefault((int(item["lat"] // self.cell),
                           int(item["lon"] // self.cell)), []).append(item)

    def near(self, lat, lon):
        i, j = int(lat // self.cell), int(lon // self.cell)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                yield from self.b.get((i + di, j + dj), ())


def main():
    os.makedirs(LOGS, exist_ok=True)
    # Step 33: the same join, run a second time over the water and sanitation
    # works of B25 (python3 date_undated.py --water). The two rules are the
    # same; only the directory and the classes that count as "made of an
    # abandoned place" change.
    global RAW, ON_SITE_CLASSES, NAME_CLASSES, NAME_CLASSES_NEAR
    water = "--water" in sys.argv
    if water:
        RAW = WRAW
        ON_SITE_CLASSES = WATER_ON_SITE_CLASSES
        NAME_CLASSES = WATER_NAME_CLASSES
        NAME_CLASSES_NEAR = WATER_NAME_CLASSES
        print("=== the water works of B25 ===")
    print("gazetteer")
    sites, skipped_open, skipped_end = load_sites()
    print(f"  {len(sites):,} sites with a closed occupation window")
    print(f"  {skipped_open:,} skipped: still occupied (a living city's "
          f"founding year dates nothing)")
    print(f"  {skipped_end:,} skipped: the end year is the pack's own "
          f"bookkeeping (Pleiades stops at 641, Reba splits at 641 and 1500), "
          f"not an abandonment")
    horizon = sum(1 for s in sites if s["end_is_record_horizon"])
    print(f"  {horizon:,} end at the pack's record horizon (flagged)")

    grid = Grid()
    for s in sites:
        grid.add(s)

    print("\nundated structures from Wikidata")
    undated, dated_qids = {}, set()
    for f in sorted(os.listdir(RAW)):
        if f.startswith("undated_") and f.endswith(".json"):
            for r in json.load(open(os.path.join(RAW, f), encoding="utf-8")):
                q = r["qid"]
                if q in undated:
                    if r["class"] not in undated[q]["classes"]:
                        undated[q]["classes"].append(r["class"])
                else:
                    undated[q] = dict(r, classes=[r["class"]])
        elif f.startswith("class_") and f.endswith(".json"):
            for r in json.load(open(os.path.join(RAW, f), encoding="utf-8")):
                dated_qids.add(r["qid"])
    labels = {}
    if os.path.exists(LABELS_PATH):
        labels = json.load(open(LABELS_PATH, encoding="utf-8"))
    print(f"  {len(undated):,} unique structures with no Wikidata date")
    print(f"  {len(dated_qids):,} already dated by part 1 (these keep their date)")
    print(f"  {len(labels):,} English labels on hand")

    print("\njoining")
    dated_here, no_site = [], 0
    rule_a = rule_b = 0
    for q, r in undated.items():
        if q in dated_qids:              # never overwrite a recorded date
            continue
        label = labels.get(q, "")
        hit_a = hit_b = None
        for s in grid.near(r["lat"], r["lon"]):
            d = km(r["lat"], r["lon"], s["lat"], s["lon"])
            by_name = bool(label) and names_match(label, s)
            limit = NAME_RADIUS_KM if by_name else TIER_RADIUS_KM[s["tier"]]
            if d > limit:
                continue
            cls = set(r["classes"])
            if cls & NEVER_CLASSES:
                continue
            if by_name:
                if not (cls & (NAME_CLASSES_NEAR if d <= NEAR_KM
                               else NAME_CLASSES)):
                    continue
            elif not (cls & ON_SITE_CLASSES):
                continue                 # a later building beside the old one
            cand = (s["tier"], d, s)
            if by_name:
                if hit_a is None or cand[:2] < hit_a[:2]:
                    hit_a = cand
            elif hit_b is None or cand[:2] < hit_b[:2]:
                hit_b = cand
        pick = hit_a or hit_b
        if pick is None:
            no_site += 1
            continue
        s = pick[2]
        if hit_a:
            rule_a += 1
        else:
            rule_b += 1
        dated_here.append({
            "qid": q, "label": label or None,
            "lat": r["lat"], "lon": r["lon"],
            "sitelinks": r["sitelinks"],
            "classes": r["classes"],
            "start": s["start"], "end": s["end"],
            "site": s["id"], "site_name": s["name"], "site_pack": s["pack"],
            "site_tier": s["tier"],
            "site_distance_km": round(pick[1], 2),
            "matched_by": "name" if hit_a else "location",
            "end_is_record_horizon": s["end_is_record_horizon"],
            "confidence": s["confidence"],
            "civHint": s["civHint"],
            "date_source": "gazetteer",
            "estimated": True,
        })

    dated_here.sort(key=lambda r: -r["sitelinks"])
    with open(os.path.join(RAW, "gazetteer_dated.json"), "w", encoding="utf-8") as f:
        json.dump(dated_here, f)
    print(f"  {len(dated_here):,} dated from the gazetteer "
          f"({rule_a:,} by name, {rule_b:,} by location)")
    print(f"  {no_site:,} left undated: not the site, or not the kind of "
          f"thing that stands on one")

    # ---- does this fix the test places? -------------------------------------
    report_path = os.path.join(LOGS, "step32_fetch_report.json")
    coverage = None
    if os.path.exists(report_path) and not water:
        coverage = json.load(open(report_path)).get("test_place_coverage")

    fixed = 0
    if coverage:
        print("\ntest places that part 1 left empty")
        places = {p[0]: (p[1], p[2], p[3]) for p in TEST_PLACES}
        for c in coverage:
            if c["standing_in_year"] > 0:
                continue
            if c["place"] not in places:
                print(f"    ? {c['place']}")
                continue
            lat, lon, yr = places[c["place"]]
            stand = [r for r in dated_here
                     if km(lat, lon, r["lat"], r["lon"]) <= 25
                     and r["start"] <= yr < r["end"]]
            if stand:
                fixed += 1
                print(f"    FIXED {c['place']:18s} {yr:>6}  "
                      f"{len(stand)} standing: " +
                      ", ".join(f"{r['label'] or r['qid']} "
                                f"({r['start']}..{r['end']})" for r in stand[:3]))
            else:
                near = [r for r in dated_here
                        if km(lat, lon, r["lat"], r["lon"]) <= 25]
                print(f"    still empty {c['place']:18s} {yr:>6}  "
                      f"({len(near)} dated nearby, none standing in {yr})")
        print(f"\n  {fixed} of the empty places now have something standing")

    stats = {
        "gazetteer_sites_usable": len(sites),
        "sites_skipped_still_occupied": skipped_open,
        "sites_skipped_end_is_bookkeeping": skipped_end,
        "sites_end_is_record_horizon": horizon,
        "undated_unique": len(undated),
        "already_dated_by_wikidata": len(dated_qids),
        "dated_from_gazetteer": len(dated_here),
        "matched_by_name": rule_a,
        "matched_by_location": rule_b,
        "still_undated": no_site,
        "by_pack": {}, "by_tier": {}, "by_matched": {},
    }
    for r in dated_here:
        stats["by_pack"][r["site_pack"]] = stats["by_pack"].get(r["site_pack"], 0) + 1
        stats["by_tier"][r["site_tier"]] = stats["by_tier"].get(r["site_tier"], 0) + 1
        stats["by_matched"][r["matched_by"]] = \
            stats["by_matched"].get(r["matched_by"], 0) + 1
    out_name = "step33_water_dated_report.json" if water else "step32_part2_report.json"
    with open(os.path.join(LOGS, out_name), "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=1)

    print("\n  where the dates came from")
    for k, v in sorted(stats["by_pack"].items(), key=lambda kv: -kv[1]):
        print(f"    {str(k):26s} {v:>7,}")
    print("\n  a sample of what got dated")
    for r in dated_here[:12]:
        hz = " (horizon)" if r["end_is_record_horizon"] else ""
        print(f"    {(r['label'] or r['qid'])[:34]:36s} "
              f"{r['site_pack'][:14]:16s} {r['matched_by']:9s} "
              f"{r['start']:>6}..{r['end']:<6}{hz}")
    if water:
        print("\n  written: build/water/raw/gazetteer_dated.json")
        print("           logs/step33_water_dated_report.json")
    else:
        print("\n  written: build/buildings/raw/gazetteer_dated.json")
        print("           logs/step32_part2_report.json")


if __name__ == "__main__":
    main()
