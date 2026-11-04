"""
Step 44 part E6: where the food crops come from.

The plan names this source for E6 ("crops (B6)") and for part C's crop placement, and until now
it had never been fetched. It is Khoury et al. 2016, *Origins of food crops connect countries
worldwide*, Proc. R. Soc. B 283: 20160792 (doi 10.1098/rspb.2016.0792), data on Dryad
(doi 10.5061/dryad.s08t2) and Zenodo (record 5006466). Table S1 is a matrix of **150 crop
commodities against 23 primary regions of diversity**; Table S2 assigns **212 countries** to those
regions.

What it gives is *where a crop's wild relatives and oldest varieties are concentrated* — the
region it was domesticated in. What it does **not** give is a date. Nobody can read "tomatoes come
from the Andes" and learn when a tomato reached Naples; Khoury's own point is that 69% of what the
world eats is foreign to where it is eaten. So this register answers the *where*, and the *when*
has to come from somewhere else — the technology atlas, as it did for part C.

Two things are deliberately kept apart:

- **The 23 regions are Khoury's, not the mod's.** The mod works in the 17 areas of the
  ways-of-life survey. `REGION_AREA` below is a hand-written map between them, and where a
  Khoury region straddles two of the mod's areas it is given both — the South and East
  Mediterranean is North Africa, West Asia and Europe at once, and pretending otherwise would
  put olives in only one of the three.
- **"Not specified" is kept, not dropped.** 27 of the 150 crops have no region (they are
  aggregates like "Vegetables, other", or the paper could not attribute them). They stay in the
  register marked so, because a crop with no origin cannot be placed and a caller needs to be
  able to tell the difference between "originates nowhere" and "we did not look".
"""
import json
import os

from build_product_atlas import AREAS          # the mod's seventeen; a crop has to be sown in one

# --------------------------------------------------------------------- the 23 regions -> 17 areas

REGION_NAMES = {
    "CAF": "Central Africa", "EAF": "East Africa", "IOI": "Indian Ocean Islands",
    "SAF": "Southern Africa", "WAF": "West Africa", "CAR": "Caribbean",
    "CAM": "Central America and Mexico", "NAM": "North America",
    "SAM-A": "Andean South America", "SAM-Tem": "Temperate South America",
    "SAM-Tro": "Tropical South America", "CAS": "Central Asia", "EAS": "East Asia",
    "SAS": "South Asia", "SEA": "Southeast Asia", "WAS": "West Asia",
    "SEM": "South and East Mediterranean", "EEU-N": "North Eastern Europe",
    "EEU-S": "South Eastern Europe", "WEU-N": "North Western Europe",
    "WEU-S": "South Western Europe", "PAC-ANZ": "Australia and New Zealand",
    "PAC-T": "Tropical Pacific",
}

# Hand-written. The mod's 17 areas are the ways-of-life survey's; Khoury's 23 follow national
# borders and FAO's annex 2. Where one is several of the others it gets all of them: the
# Mediterranean basin is three, and Central America and Mexico straddles the mod's MNA and CAC.
REGION_AREA = {
    "CAF": ["MSA"], "EAF": ["EAF"], "IOI": ["EAF"], "SAF": ["MSA"], "WAF": ["WAF"],
    "CAR": ["CAC"], "CAM": ["MNA", "CAC"], "NAM": ["NNA"],
    "SAM-A": ["SAM"], "SAM-Tem": ["SAM"], "SAM-Tro": ["SAM"],
    "CAS": ["CAS"], "EAS": ["EAS"], "SAS": ["SAS"], "SEA": ["SEA"], "WAS": ["WAS"],
    "SEM": ["NAF", "WAS", "EUR"],
    "EEU-N": ["EEU"], "EEU-S": ["EEU"], "WEU-N": ["EUR"], "WEU-S": ["EUR"],
    "PAC-ANZ": ["AUS"], "PAC-T": ["PAC"],
}

NS = "NS"          # Khoury's "not specified": the crop could not be attributed to a region


def areas_of(regions):
    """The mod's areas for a list of Khoury region codes, in a stable order."""
    out = []
    for r in regions:
        for a in REGION_AREA.get(r, []):
            if a not in out:
                out.append(a)
    return out


# --------------------------------------------------------------------- the table

def load(path=None):
    """
    Read Table S1. Returns a list of dicts: crop name, scientific names, the Khoury region codes
    it originates in, the mod's areas, whether it appears in the food-supplies data (what people
    actually eat) or only in production data, and the paper's own note on the attribution.
    """
    import openpyxl

    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "survey",
                            "khoury", "TableS1_crops_regions_table.xlsx")
    path = os.path.abspath(path)
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb["Crops_regions"]
    rows = list(ws.iter_rows(values_only=True))
    regions = list(rows[1][5:28])

    crops = []
    for r in rows[2:]:
        if not r or not r[0]:
            continue
        hits = [regions[i] for i, v in enumerate(r[5:28]) if v == "x"]
        not_specified = r[28] == "x" if len(r) > 28 else False
        crops.append({
            "name": str(r[0]).strip(),
            "scientific": (str(r[1]).strip() if r[1] else ""),
            "regions": hits,
            "areas": areas_of(hits),
            "eaten": r[2] == "x",                 # in the food-supplies data
            "grown": r[3] == "x",                 # in the production data
            "notSpecified": not_specified,
            "note": (str(r[29]).strip() if len(r) > 29 and r[29] else ""),
        })
    wb.close()
    return crops


def problems(crops):
    """Sanity checks, so a bad read cannot ship silently."""
    out = []
    if len(crops) < 140:
        out.append("only %d crops; the paper has 151 commodities" % len(crops))
    for c in crops:
        if not c["regions"] and not c["notSpecified"]:
            # an unattributed crop the paper did not itself mark is a read error, not a fact
            out.append("%s: has no region and is not marked 'not specified'" % c["name"])
        for r in c["regions"]:
            if r not in REGION_AREA:
                out.append("%s: unknown region code %s" % (c["name"], r))
    return out


if __name__ == "__main__":
    import collections

    cs = load()
    probs = problems(cs)
    print("crop origins: %d crops, %d regions" % (len(cs), len(REGION_NAMES)))
    print("  eaten (food supplies): %d   grown (production): %d   not specified: %d" % (
        sum(1 for c in cs if c["eaten"]), sum(1 for c in cs if c["grown"]),
        sum(1 for c in cs if c["notSpecified"])))
    print("  areas covered:", sorted({a for c in cs for a in c["areas"]}))
    print("  crops per area:", dict(sorted(collections.Counter(
        a for c in cs for a in c["areas"]).items())))
    for p in probs:
        print("  PROBLEM", p)
    print("crop_origins: %d problem(s)" % len(probs))


# --------------------------------------------------------------------- what the atlas was missing
#
# Part C of this step grew the atlas to 529 products but could not place the fruit and vegetables,
# for want of a register saying where they came from. This is that register, so the ten below can
# now join it. Each carries:
#
#   home         the areas Khoury's Table S1 gives as the crop's region of diversity. Read, not
#                written: `load()` supplies it, and `SOWN` names the crop by the name the paper
#                uses, so a wrong spelling fails loudly in `problems()`.
#   home_only    optional. Khoury's regions follow national borders and his "palm oil" commodity
#                covers two species on two continents, while "South and East Mediterranean" puts
#                dates in Europe, where they do not grow. Where the region is too wide this
#                narrows it, and `problems()` says so rather than letting it pass.
#   domesticated the year it was brought under cultivation, from the archaeological literature.
#                **One number per crop**, not one per area.
#   to           when it reached the rest of the world, as four numbers (OLD / AFR / AMR / OCE,
#                the same groups part B writes in). Part C refused to hand-write 4,556 per-area
#                years and was right; four per crop is a claim a person can check.
#
# A crop is MADE in its home areas from the later of (farming reaching that area, domestication) —
# nobody sows an orchard before they farm — and BROUGHT elsewhere from the year in `to`. A crop
# with no `to` entry for a group never reaches it, which is a fact about the world and not an
# omission: soybeans did not reach Africa in any quantity before the twentieth century.

SOWN = {
    "Apples": {
        "id": "apples", "name": "Apples and pears", "family": "other food and drink",
        "domesticated": -4000,
        "to": {"OLD": -500, "AFR": 500, "AMR": 1625, "OCE": 1788},
        "note": ("from the wild apple forests of the Tian Shan; spread west along the Silk Road, "
                 "and named varieties only after grafting was learned"),
    },
    "Oranges & mandarins": {
        "id": "citrus", "name": "Citrus fruit (oranges, lemons, limes)", "family": "other food and drink",
        "domesticated": -2000,
        "to": {"OLD": 100, "AFR": 700, "AMR": 1500, "OCE": 1788},
        "note": ("oranges and mandarins from the east; the citron reached the West first, by way "
                 "of Persia, and the sour kinds came to the Mediterranean in Roman times"),
        "also": ["Lemons & limes", "Grapefruit"],
    },
    "Dates": {
        "id": "dates", "name": "Dates (khajoor)", "family": "other food and drink",
        "domesticated": -4500,
        "home_only": ["WAS", "NAF", "SAS"],
        "to": {"OLD": -2000, "AFR": -3000, "AMR": 1500, "OCE": 1800},
        "note": "among the first fruit trees domesticated, in the Levant and the river valleys of the south",
    },
    "Olives": {
        "id": "olives", "name": "Olives", "family": "other food and drink",
        "domesticated": -4500,
        "to": {"OLD": -2000, "AFR": -2000, "AMR": 1550, "OCE": 1800},
        "note": "domesticated in the Levant with the vine and the fig; the oil is older than the fruit as a food",
    },
    "Peas": {
        "id": "peas", "name": "Peas", "family": "other food and drink",
        "domesticated": -8500,
        "to": {"OLD": -6000, "AFR": -3000, "AMR": 1500, "OCE": 1788},
        "note": "a founder crop of the Fertile Crescent, sown with wheat and barley from the first",
    },
    "Soybean": {
        "id": "soybean", "name": "Soybeans", "family": "other food and drink",
        "domesticated": -1500,
        "to": {"OLD": 1900, "AFR": 1900, "AMR": 1900, "OCE": 1900},
        "to_area": {"SEA": 0, "SAS": 1000},
        "note": "a Chinese crop for three thousand years, and a world crop only in the twentieth",
    },
    "Sweet potatoes": {
        "id": "sweet_potato", "name": "Sweet potatoes", "family": "staple food",
        "domesticated": -3000,
        # Polynesia, not Oceania: the crossing was to the Cook Islands and the tropical
        # Pacific. Australia is on the far side of the continent and got it with the colonists.
        "to": {"OLD": 1500, "AFR": 1500, "AMR": None, "OCE": None},
        "to_area": {"PAC": 1210, "AUS": 1788},
        "note": ("carried into the Pacific and planted in Polynesia centuries before Columbus; the "
                 "one American crop that crossed the ocean on its own"),
    },
    "Tomatoes": {
        "id": "tomatoes", "name": "Tomatoes", "family": "other food and drink",
        "domesticated": -2000,
        # Khoury gives the Andes alone, but the plant was made into a sauce in Mesoamerica
        # and its name is Nahuatl; Britannica and Wikipedia both call Mexico the place it was
        # domesticated. `home_also` widens where the register is too narrow.
        "home_also": ["MNA", "CAC"],
        "to": {"OLD": 1544, "AFR": 1560, "AMR": None, "OCE": 1800},
        "note": ("from the Andes, made into a sauce in Mexico, and written of as food in Italy in "
                 "1544 — grown before that as an ornament"),
    },
    "Pineapples": {
        "id": "pineapple", "name": "Pineapples", "family": "other food and drink",
        "domesticated": -2000,
        "to": {"OLD": 1550, "AFR": 1500, "AMR": None, "OCE": 1788},
        "note": "from the Paraná basin; shown to Columbus in 1493 and grown in European glasshouses after",
    },
    "Palm oil": {
        "id": "palm_oil", "name": "Palm oil", "family": "other food and drink",
        "domesticated": -3000,
        "home_only": ["WAF", "MSA"],
        "to": {"AFR": -3000, "AMR": 1500},
        "note": "the oil palm of the West African forest, tapped and boiled for oil since prehistory",
    },
}


def home_areas(crops):
    """Khoury's home regions for each crop we sow, translated into the mod's 17 areas."""
    by_name = {c["name"]: c for c in crops}
    out = {}
    for khoury, spec in SOWN.items():
        names = [khoury] + list(spec.get("also", []))
        seen, areas = set(), []
        for n in names:
            if n not in by_name:
                continue
            for a in by_name[n]["areas"]:
                if a not in seen:
                    seen.add(a)
                    areas.append(a)
        for a in spec.get("home_also", []):
            if a not in seen:
                seen.add(a)
                areas.append(a)
        only = spec.get("home_only")
        if only:
            areas = [a for a in only if a in seen] or [a for a in only if a in AREAS]
        out[spec["id"]] = {"areas": areas, "found": [n for n in names if n in by_name]}
    return out


def check_sown(crops):
    """A crop that is named but not found is a spelling error, and must not ship."""
    by_name = {c["name"]: c for c in crops}
    out = []
    for khoury, spec in SOWN.items():
        names = [khoury] + list(spec.get("also", []))
        if not any(n in by_name for n in names):
            out.append("'%s' is not in Table S1 (nor is %s)" % (khoury, spec.get("also")))
        for g in spec.get("to", {}):
            if g not in ("OLD", "AFR", "AMR", "OCE"):
                out.append("%s: unknown group '%s'" % (spec["id"], g))
        for a in spec.get("home_also", []):
            if a not in AREAS:
                out.append("%s: home_also '%s' is not one of the seventeen areas" % (spec["id"], a))
        only = spec.get("home_only")
        if only:
            wide = {a for n in names if n in by_name for a in by_name[n]["areas"]}
            if not (set(only) <= wide):
                out.append("%s: home_only %s is not a subset of what the paper gives (%s)"
                           % (spec["id"], only, sorted(wide)))
    return out
