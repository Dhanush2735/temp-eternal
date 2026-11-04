#!/usr/bin/env python3
"""
Step 44 part 2 (E4, prices and wages through time): build history/prices.json.gz from the
Allen-Unger Global Commodity Prices Database.

    python3 build_prices.py            build, then check
    python3 build_prices.py --check    check the pack that is already there

**What this replaces.** `CommodityPricingEngine` is twelve hardcoded numbers -- silk is 28 in
Chang'an in 800 and 28 in Amsterdam in 1650, and its supply/demand ratio has two defaults that
are both 50, so the ratio is always 1. This pack carries **measured prices: 125,588
observations, 193 markets, 160 commodities, the years 965 to 1914**, every one converted to
grams of silver so that Florence in 1350 and Allahabad in 1861 can be compared.

**Two things had to be built before a single number could be read.** The database names its
markets and gives no coordinates, so `price_markets.py` places all 193 by hand -- the obvious
shortcut of matching names against the mod's own 30,151-town gazetteer was tried and thrown
away, because three centuries of Spanish colonial naming turns Burgos, Valencia, Zaragoza and
Valladolid into Philippine towns. And it names its commodities with no vocabulary and measures
the same one in different units, so `price_table.py` gives each a canonical measure.

**Grams of silver is the unit, and it has to be.** 72 different original currencies appear,
from the Brabant groat to the Osaka monme; mapping those onto the mod's 401 currencies by name
would silently misprice things, which is the exact failure step 42 hit with its law rows. Silver
is what the database itself standardises to, so nothing is lost by keeping it.

Run:  python3 build_prices.py
"""

import collections
import csv
import gzip
import json
import os
import statistics
import sys

import price_markets as M
import price_table as T

HERE = os.path.dirname(os.path.abspath(__file__))
HIST = os.path.normpath(os.path.join(HERE, "..", "eternal", "src", "main", "resources",
                                     "data", "eternalengine", "eternal", "history"))
OUT = os.path.join(HIST, "prices.json.gz")

# A price of zero or less is a transcription artefact, not a price.
MIN_GRAMS = 1e-6
# Beyond this many grams of silver per unit, the row is almost certainly a different unit than
# the one claimed. Kept high enough to catch only absurdities: gold is ~0.03 g/g, saffron dear.
MAX_GRAMS = 1.0e6
# A series whose ordinary price is more than this many times, or less than this fraction of, the
# same good's ordinary price everywhere else is marked suspect. See the conversion test below.
SUSPECT_ABOVE = 8.0
SUSPECT_BELOW = 1.0 / 8.0
# A year counts as a shortage when grain costs this multiple of what it cost in the years around
# it. 1.8 catches the Great Famine of 1315-17 and misses ordinary bad harvests.
SHORTAGE_INDEX = 1.8
# The goods whose price movement means hunger. Everything else is a luxury or a raw material.
GRAIN = {"wheat", "rye", "barley", "oats", "rice", "millet", "maize", "spelt", "buckwheat",
         "bread", "flour", "oatmeal", "meal", "pulses", "grain", "potato"}


def dominant_measures():
    """
    The measure each commodity is mostly reported in, read out of the data and not guessed.

    **This function exists because guessing was tried first and was badly wrong.** Wheat was
    given 'Kilogram' in the table by hand; the data reports it by the litre 21,470 times and by
    the kilogram 1,323. The first build therefore kept 6% of the best-covered commodity in the
    whole database and threw away the rest. The measure is now counted, not chosen.
    """
    counts = collections.defaultdict(collections.Counter)
    if not os.path.isdir(T.DATA):
        return {}
    for fn in sorted(os.listdir(T.DATA)):
        if not fn.endswith(".tab"):
            continue
        src = fn[:-4].rsplit("_", 1)[1]
        with open(os.path.join(T.DATA, fn), encoding="utf-8", errors="replace") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                counts[src][(r.get("Standard Measure") or "").strip()] += 1
    out = {}
    for src, c in counts.items():
        best = c.most_common(1)[0]
        if best[0]:
            out[src] = best[0]
    return out


def read_all(measures=None):
    """Every observation, as (market, source commodity, year, grams of silver)."""
    goods = T.by_name()
    places = M.by_market()
    rows = []
    dropped = collections.Counter()
    converted = 0
    if not os.path.isdir(T.DATA):
        return rows, dropped, None
    for fn in sorted(os.listdir(T.DATA)):
        if not fn.endswith(".tab"):
            continue
        market, src_commodity = fn[:-4].rsplit("_", 1)
        if market not in places:
            dropped["market not placed"] += 1
            continue
        if src_commodity in T.EXCLUDE:
            dropped["excluded: " + src_commodity] += 1
            continue
        mapped = goods.get(src_commodity)
        if mapped is None:
            dropped["commodity not mapped"] += 1
            continue
        want_measure = (measures or {}).get(src_commodity) or mapped[3]
        # Grain always ends up in kilograms, whichever way most of it was measured.
        if mapped[0] in T.BULK_DENSITY:
            want_measure = "Kilogram"
        with open(os.path.join(T.DATA, fn), encoding="utf-8", errors="replace") as fh:
            for r in csv.DictReader(fh, delimiter="\t"):
                measure = (r.get("Standard Measure") or "").strip()
                litres = measure == "Litre"
                if measure != want_measure:
                    # Grain measured by the litre becomes kilograms at a bulk density, because
                    # Europe measured by the litre and British India by the kilogram, and choosing
                    # one of them loses a subcontinent.
                    gid0 = mapped[0]
                    if measure == "Litre" and gid0 in T.BULK_DENSITY and want_measure == "Kilogram":
                        measure = "Kilogram"
                    elif measure != want_measure:
                        dropped["wrong measure for " + src_commodity] += 1
                        continue
                raw = (r.get("Standardized Value") or "").strip()
                if not raw:
                    dropped["no silver value"] += 1
                    continue
                try:
                    grams = float(raw)
                except ValueError:
                    dropped["unreadable number"] += 1
                    continue
                if litres and gid0 in T.BULK_DENSITY and want_measure == "Kilogram":
                    grams /= T.BULK_DENSITY[gid0]
                    converted += 1
                if not (grams > MIN_GRAMS):
                    dropped["price is zero or negative"] += 1
                    continue
                if grams > MAX_GRAMS:
                    dropped["price is absurd"] += 1
                    continue
                try:
                    year = int((r.get("Year") or "").strip())
                except ValueError:
                    dropped["unreadable year"] += 1
                    continue
                if not (-10000 <= year <= 2100):
                    dropped["year out of range"] += 1
                    continue
                rows.append((market, src_commodity, year, grams))
    dropped["converted from litres to kilograms"] = -converted   # counted, not lost
    return rows, dropped, True


def moving_median(years, vals, i, half_window_years=15):
    """
    The median price within `half_window_years` either side of this observation.

    The window is in YEARS and not in observations, because these series are full of holes: a
    run of thirty consecutive rows may span a century. Falls back to the whole series at the
    ends, where there is nothing to one side.
    """
    y0 = years[i]
    lo = next((j for j in range(i, -1, -1) if years[j] < y0 - half_window_years), None)
    hi = next((j for j in range(i, len(years)) if years[j] > y0 + half_window_years), None)
    a = 0 if lo is None else lo
    b = len(vals) if hi is None else hi + 1
    window = vals[a:b]
    return statistics.median(window) if window else vals[i]


def build():
    problems = []
    places = M.by_market()
    goods = T.by_name()
    gindex = T.goods_index()

    measures = dominant_measures()
    # Where the data disagrees with the measure written by hand in price_table.py, the data wins
    # and the disagreement is reported, so the table can be brought into line.
    hint = T.by_name()
    for src, meas in sorted(measures.items()):
        if src in hint and hint[src][3] != meas:
            print(f"  note  {src}: the data mostly uses {meas}, the table says {hint[src][3]}; "
                  f"using {meas}")
    rows, dropped, have_data = read_all(measures)
    if have_data is None:
        print("  PROBLEM the Allen-Unger data is not unpacked at " + T.DATA)
        print("           (fetch it with: worldfill/fetch_prices.sh)")
        return None, 1
    if not rows:
        problems.append("no observations were read")

    # place -> good -> year -> [grams]
    tree = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list)))
    for market, src, year, grams in rows:
        gid = goods[src][0]
        tree[market][gid][year].append(grams)

    place_ids = sorted(places)
    good_ids = sorted(gindex)
    place_i = {p: i for i, p in enumerate(place_ids)}
    good_i = {g: i for i, g in enumerate(good_ids)}

    # the measure each good ends up with, from the series actually built
    good_measure = {}
    for src, gid, disp, fam, _m in T.GOODS:
        meas = (measures or {}).get(src) or _m
        # The label has to follow the conversion: grain is stored in kilograms even where the
        # source measured it in litres, and calling it a litre while quoting a kilogram would
        # misprice every grain in the pack by the bulk density.
        if gid in T.BULK_DENSITY:
            meas = "Kilogram"
        good_measure.setdefault(gid, meas)

    series = []
    kept = 0
    for market in place_ids:
        for gid in good_ids:
            by_year = tree.get(market, {}).get(gid)
            if not by_year:
                continue
            years = sorted(by_year)
            vals = []
            for y in years:
                v = by_year[y]
                vals.append(round(sum(v) / len(v), 6))
            base = statistics.median(vals)
            if base <= 0:
                continue
            # A price against the level of its OWN TIME, not of its whole series. The first
            # version divided by the median of the entire series, and since England's wheat runs
            # from 1237 to 1914, every year of the nineteenth century came out at four times
            # "normal" -- which says nothing except that the Middle Ages were cheaper. A centred
            # moving median is what turns the number into a shortage: 1.00 is what grain
            # ordinarily cost in the years around this one, and 1.9 is the Great Famine.
            index = [round(vals[i] / moving_median(years, vals, i), 4)
                     for i in range(len(vals))]
            series.append({"place": place_i[market], "good": good_i[gid],
                           "years": years, "grams": vals, "usual": round(base, 6),
                           "index": index})
            kept += sum(len(by_year[y]) for y in years)

    # ---- shortages -----------------------------------------------------------------------
    # The other half of E4. `culture.json.gz` carries 26 crises, all of them 1873 or later, so
    # the mod knows about 1929 and 2008 and nothing about the Great Famine. Rather than write a
    # list of famines by hand, a shortage is read out of the prices: a year in which this
    # market's grain cost far more than it did in the years around it. Nothing is invented.
    per_place_year = collections.defaultdict(list)
    for s in series:
        # Grain and bread only: a spike in pepper is a rumour, a spike in wheat is a famine.
        if good_ids[s["good"]] not in GRAIN:
            continue
        for y, ix in zip(s["years"], s["index"]):
            if ix >= SHORTAGE_INDEX:
                per_place_year[(s["place"], y)].append((s["good"], ix))
    shortages = []
    for (pi, y), hits in sorted(per_place_year.items()):
        worst = max(hits, key=lambda h: h[1])
        shortages.append({
            "place": pi, "year": y,
            "goods": sorted({good_ids[g] for g, _ in hits}),
            "worst": round(worst[1], 2), "good": good_ids[worst[0]],
        })

    # ---- the conversion test -------------------------------------------------------------
    # Some of the database's currency conversions are wrong: Tuscany's wheat comes out at
    # twenty-eight times the English price, and Tokyo is a hundredth of everyone else's in
    # nearly every commodity. A series whose ordinary level is wildly out of line with the
    # same good everywhere else is marked suspect: its *shape* is still good, since a constant
    # error cancels in the index, but its absolute figure is not to be quoted.
    by_good = collections.defaultdict(list)
    for s in series:
        by_good[s["good"]].append(s)
    n_suspect = 0
    for gid, ss in by_good.items():
        if len(ss) < 4:
            continue
        world = statistics.median(s["usual"] for s in ss)
        if world <= 0:
            continue
        for s in ss:
            ratio = s["usual"] / world
            if ratio > SUSPECT_ABOVE or ratio < SUSPECT_BELOW:
                s["suspect"] = True
                n_suspect += 1

    n_converted = 0 - dropped.pop("converted from litres to kilograms", 0)
    total = kept + sum(dropped.values())
    gaps = [
        "Grain measured by the litre has been converted to kilograms at a bulk density (the pack "
        "carries the densities), because Europe measured grain by the litre and British India by "
        "the kilogram, and keeping only one measure loses either Europe or India.",
        "The database stops in 1914. Nothing after that is in this pack, and the twentieth and "
        "twenty-first centuries are out of its reach entirely.",
        "It is Europe-biased and grain-heavy: wheat has 150 market series and many goods have one "
        "short one. Its own authors say there are many gaps.",
        "Every price is in grams of silver, because the source reports 72 different original "
        "currencies and mapping those onto the mod's money by name would silently misprice things.",
        "The mod cannot yet turn a silver price into days of a labourer's work: it knows a day's "
        "pay in local money (the money table, 401 currencies) and it knows prices in silver, and "
        "nothing in it joins the two.",
        "SLAVE IS DELIBERATELY ABSENT. The source prices 179 observations of human beings, "
        "measured in 'Individual Adult Male'. They are not in this pack and will not be.",
        "Some of the database's own conversions of local currencies into silver are wrong, and "
        "there is no way to tell which without checking each one against its archive. Tuscany's "
        "wheat comes out at twenty-eight times the English price and Tokyo's at a hundredth of "
        "everyone else's in nearly every commodity. Every series therefore carries an INDEX "
        "against its own ordinary level, which is safe to use, and an absolute figure in grams "
        "of silver, which is marked suspect where it disagrees wildly with the same good "
        "elsewhere. The mod quotes the index and does not quote a suspect absolute figure.",
        "Only the years 965 to 1914 have measured shortages at all, and they are European and "
        "Indian; the Americas and Africa have almost nothing.",
        "Market coordinates are placed by hand, because a name-only match against the mod's town "
        "gazetteer files Burgos, Valencia, Zaragoza and Valladolid under the Philippines.",
    ]

    doc = {
        "format": "eternal-prices-1",
        "id": "prices",
        "source": "Allen, Robert C. and Richard W. Unger, 'The Allen-Unger Global Commodity Prices "
                  "Database' (2019), DANS doi 10.17026/dans-zsu-xavf; read from the "
                  "forex-centuries mirror. Wages are not from here: they come from the money "
                  "table (step 23a) and Maddison (step 30b).",
        "note": "Measured prices by market, commodity and year, in grams of silver per unit. "
                "Step 44 (E4): what a thing cost here, then. Pack built by "
                "worldfill/build_prices.py from worldfill/price_markets.py (193 markets placed by "
                "hand) and worldfill/price_table.py (160 commodities given one measure each).",
        "gaps": gaps,
        "counts": {
            "observationsRead": total,
            "observationsKept": kept,
            "dropped": sum(dropped.values()),
            "convertedFromLitres": n_converted,
            "markets": len(place_ids),
            "goods": len(good_ids),
            "series": len(series),
            "suspectSeries": n_suspect,
            "shortageYears": len(shortages),
        },
        "bulkDensityKgPerLitre": dict(sorted(T.BULK_DENSITY.items())),
        "places": [
            {"id": p, "name": p, "place": places[p][0], "lat": places[p][1],
             "lon": places[p][2], "radiusKm": places[p][3]}
            for p in place_ids
        ],
        "goods": [
            {"id": g, "name": gindex[g][0], "family": gindex[g][1], "measure": good_measure[g]}
            for g in good_ids
        ],
        "series": series,
        "shortages": shortages,
    }

    # ------------------------------------------------------------------ checks
    if not series:
        problems.append("no series were built")
    converted_ids = set(T.BULK_DENSITY)
    for g in doc["goods"]:
        if g["id"] in converted_ids and g["measure"] != "Kilogram":
            problems.append(f"good {g['id']}: stored in kilograms but labelled {g['measure']}")
    for p in doc["places"]:
        if not (-90.0 <= p["lat"] <= 90.0 and -180.0 <= p["lon"] <= 180.0):
            problems.append(f"place {p['id']}: bad coordinates {p['lat']},{p['lon']}")
    for s in series:
        if len(s["years"]) != len(s["grams"]):
            problems.append(f"series {s['place']}/{s['good']}: years and values differ in length")
        if s["years"] != sorted(s["years"]):
            problems.append(f"series {s['place']}/{s['good']}: years out of order")
        if any(not (g > 0) for g in s["grams"]):
            problems.append(f"series {s['place']}/{s['good']}: a price is not positive")
        if len(s.get("index", [])) != len(s["years"]):
            problems.append(f"series {s['place']}/{s['good']}: index and years differ in length")
        if any(not (x > 0) for x in s.get("index", [])):
            problems.append(f"series {s['place']}/{s['good']}: an index is not positive")
        if s["place"] < 0 or s["place"] >= len(place_ids):
            problems.append(f"series: place index {s['place']} is out of range")
        if s["good"] < 0 or s["good"] >= len(good_ids):
            problems.append(f"series: good index {s['good']} is out of range")
    # the pack must not carry a human being
    if any(g["id"] == "slave" for g in doc["goods"]):
        problems.append("the pack prices human beings")
    # and a real spot check: wheat at Allahabad in 1861 was 0.666 g of silver a kilogram
    want = None
    ai = place_i.get("Allahabad")
    wi = good_i.get("wheat")
    if ai is not None and wi is not None:
        for s in series:
            if s["place"] == ai and s["good"] == wi and 1861 in s["years"]:
                want = s["grams"][s["years"].index(1861)]
    for sh in shortages:
        if sh["place"] < 0 or sh["place"] >= len(place_ids):
            problems.append(f"shortage: place index {sh['place']} is out of range")
        if sh["worst"] < SHORTAGE_INDEX:
            problems.append(f"shortage: {sh['worst']} is below the threshold")
        if not sh["goods"]:
            problems.append(f"shortage at {sh['place']} {sh['year']}: no goods named")
        if sh["good"] not in good_ids:
            problems.append(f"shortage: '{sh['good']}' is not a good in this pack")
        for g in sh["goods"]:
            if g not in good_ids:
                problems.append(f"shortage: '{g}' is not a good in this pack")
            elif g not in GRAIN:
                problems.append(f"shortage: '{g}' is not grain")
    if want is None:
        problems.append("Allahabad wheat in 1861 is missing, and it was read out of the data by hand")
    elif abs(want - 0.666343) > 0.01:
        problems.append(f"Allahabad wheat 1861 came out as {want} g of silver, expected about 0.666")

    return doc, problems


def main(argv):
    if "--check" in argv:
        if not os.path.exists(OUT):
            print("prices: MISSING")
            return 1
        doc, problems = build()
        if doc is None:
            return 1
        with gzip.open(OUT, "rt", encoding="utf-8") as fh:
            have = json.load(fh)
        same = have == doc
        print(f"prices: {'up to date' if same else 'OUT OF DATE'}")
        return 0 if (same and not problems) else 1

    doc, problems = build()
    if doc is None:
        return 1
    for p in problems:
        print("  PROBLEM " + p)
    if problems:
        print(f"prices: {len(problems)} problem(s); nothing written")
        return 1
    tmp = OUT + ".tmp"
    # mtime=0, or the gzip header carries the time of the build and every run produces a
    # different file from identical data -- which makes the manifest permanently "out of date"
    # for no visible reason. build_culture.py already does this.
    with open(tmp, "wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", compresslevel=9, mtime=0) as fh:
            fh.write(json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    os.replace(tmp, OUT)
    c = doc["counts"]
    print(f"prices: {c['series']} series, {c['markets']} markets, {c['goods']} goods, "
          f"{c['observationsKept']} of {c['observationsRead']} observations kept "
          f"({os.path.getsize(OUT)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
