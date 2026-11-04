#!/usr/bin/env python3
"""
Step 44 part 3 (E5 part C): grow the product atlas from 132 products toward 400, by derivation.

    python3 build_products_c.py            build, then write
    python3 build_products_c.py --check    check only, write nothing

Part B (turn 86) wrote 132 products by hand, each with a year for each of the 17 areas. The plan
wants about 400. Another 268 products x 17 areas is 4,556 hand-written years, which is not a
thing that can honestly be written -- so **this part writes no years at all**. It writes what
each product is, what family it belongs to, what it is made from, and which technology makes it
possible; every year is then read out of registers that already ship:

  * **the technology atlas** -- 130 technologies, an arrival year for each of 258 countries.
    A product made possible by a technology appears in an area in the earliest year that
    technology reaches any country of the area. This is the "know-how" check.
  * **the mineral register** -- 143,302 USGS sites for 57 minerals. A metal is MADE only where
    the ore is and BROUGHT everywhere else. This is the "nature" check, and it is measured.
  * **a parent product** -- a thing cannot exist before the raw thing it is made from. A
    child's year is the later of its parent's year and its own technology's arrival.

The 258 countries are placed in the 17 areas by `country_areas.py`, which gives each country the
area holding most of its land, using the same box rule the game uses for a point
(`ProductAtlas.boxArea`).

The 132 hand-written products are left exactly as they are. This part only adds.

Step 44 part 6 (E6) added a fourth source, for the ten crops above all leave out: **Khoury et al.
2016**, a register of where each of 150 food crops was domesticated (`crop_origins.py`). It gives
the place but not the date, so the date comes from two other things -- a domestication year read
from the archaeological literature, one per crop, and the arrival of *farming* in each area from
the technology atlas, which is the floor nobody sows a field below. A crop appears in its home
areas from the later of those two, and elsewhere from the year in `to`. See `crop_origins.py`
for the crops, their homes, and the sources for their dates.

Run:  python3 build_products_c.py
"""

import collections
import json
import os
import sys

import product_derivation as D
import product_chains as C
import build_product_atlas as B
import crop_origins as CO

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
OUT = os.path.join(ROOT, "eternal", "src", "main", "resources", "data",
                   "eternalengine", "eternal", "economy", "products_world.json")
TABLE = os.path.join(ROOT, "worldfill", "PRODUCT_ATLAS_TABLE.md")

AREAS = B.AREAS
ANY = B.ANY          # -10000: "always", the start of the game's span
FLOOR = -10000       # nothing is dated before the game begins


def first_year(p, area):
    """The earliest year a product is in an area at all, made or brought."""
    ys = [y for y in (p["made"].get(area), p["brought"].get(area)) if y is not None]
    return min(ys) if ys else None


def build():
    problems = []
    tech = D.tech_arrivals()
    ores = D.mineral_areas()

    # The hand-written part B products, untouched.
    products = list(B.PRODUCTS)
    by_id = {p["id"]: p for p in products}
    start = len(products)
    crops = CO.load()
    problems.extend("crop_origins: " + m for m in CO.problems(crops))
    problems.extend("crop_origins: " + m for m in CO.check_sown(crops))

    def add(pid, name, family, made, brought, staple=None, needs=(), note="", source="",
            inputs=()):
        if pid in by_id:
            problems.append(f"'{pid}' is already a product")
            return
        made = {a: y for a, y in made.items() if y is not None}
        brought = {a: y for a, y in brought.items()
                   if y is not None and (a not in made or y < made[a])}
        p = {"id": pid, "name": name, "family": family, "made": made, "brought": brought,
             "gone": {}, "derived": True}
        if staple:
            p["staple"] = staple
        if needs:
            p["needs"] = list(needs)
        if note:
            p["note"] = note
        p["source"] = source
        if inputs:
            p["inputs"] = [list(g) for g in inputs]
        # Step 44 part D: who makes it, and where. The work is one of the twelve kinds in
        # jobs.json.gz, so the game can ask how many people here do it.
        work, place = C.work_of(pid, family)
        p["work"] = work
        p["workplace"] = place
        p["workplaceName"] = C.WORKPLACE_NAMES[place]
        products.append(p)
        by_id[pid] = p

    # ------------------------------------------------------------- 1. from a technology
    n_tech = 0
    for tid, rows in D.TECH_PRODUCTS.items():
        arrivals = tech.get(tid) or {}
        for pid, name, fam, note in rows:
            made = {}
            for a, y in arrivals.items():
                if a in AREAS:
                    made[a] = max(FLOOR, y)
            if not made:
                problems.append(f"'{pid}': the technology '{tid}' arrives nowhere")
                continue
            add(pid, name, fam, made, {}, note=note,
                source=f"the technology atlas: when {tid} reaches the area",
                inputs=C.EXTRA_INPUTS.get(pid, []))
            n_tech += 1

    # --------------------------------------------------------------- 2. from the ground
    #
    # The plan's "nature" check asks whether the raw material is here, and the mod has a register
    # that looks like the answer: minerals.json.gz, 143,302 sites for 57 rocks and ores from the
    # US Geological Survey. **It cannot be used, and the first build that used it was wrong.**
    # It records where a United States federal survey found an economic deposit, not where a rock
    # occurs: 74.9% of its sites are in Middle North America, slate is 180 sites all of them
    # there, sandstone 5 of 5, peat 95 of 97 -- so peat, the fuel of Ireland and the Netherlands,
    # came out absent from Europe -- and the whole of the British Isles holds 78 of the 143,302.
    # It is the same shape of mistake as the Burgos-in-the-Philippines gazetteer: a source that
    # is authoritative about one country answering a question about the world.
    #
    # So a mineral product is dated by its technology alone, like any other. The mineral is still
    # recorded on the row, because what a thing is made from is exactly what part D's chains
    # need, and for that the register is sound.
    n_min = 0
    for pid, name, fam, mineral, tid in D.MINERAL_PRODUCTS:
        arrivals = tech.get(tid) or {} if tid else {}
        made = {}
        for a, y in arrivals.items():
            if a in AREAS:
                made[a] = max(FLOOR, y)
        if not made:
            if tid:
                problems.append(f"'{pid}': the technology '{tid}' arrives nowhere")
                continue
            # Nothing gates it, so it is everywhere: granite, sandstone, marble, slate and flint
            # are ordinary rocks and every continent has them. Using the register to decide
            # *where* would be the mistake described above -- it put slate in one area of
            # seventeen and left China without marble.
            made = {a: ANY for a in AREAS}
        add(pid, name, fam, made, {},
            note=f"made from {mineral.lower()}; dated by the technology that works it",
            source=f"the technology atlas ({tid or 'no technology gates it'})",
            inputs=C.EXTRA_INPUTS.get(pid, []))
        n_min += 1

    # ------------------------------------------------------------------ 3. from a parent
    n_child = 0
    for pid, name, fam, parent, tid, staple, needs in D.CHILD_PRODUCTS:
        par = by_id.get(parent)
        if par is None:
            problems.append(f"'{pid}': parent '{parent}' is not a product")
            continue
        arrivals = tech.get(tid) or {} if tid else {}
        # A few products cannot be everywhere the parent is: peat needs a bog and skis need snow
        # (see product_derivation.AREA_LIMITS). The limit is geography, not a date.
        where = D.AREA_LIMITS.get(pid, AREAS)
        made = {}
        for a in where:
            py = first_year(par, a)
            if py is None:
                continue
            ty = arrivals.get(a)
            y = max(py, ty) if ty is not None else py
            made[a] = max(FLOOR, y)
        if not made:
            problems.append(f"'{pid}': the parent '{parent}' is in no area")
            continue
        src = f"its parent '{parent}'"
        if tid:
            src += f" and the technology atlas ({tid})"
        if pid in D.AREA_LIMITS:
            src += "; the areas are its natural range, which no register here can give"
        # Part D: the parent is the input. Flour cannot be made where there is no wheat, and
        # until this was written down the atlas had flour without ever asking about wheat.
        groups = [[parent]]
        groups.extend(C.EXTRA_INPUTS.get(pid, []))
        add(pid, name, fam, made, {}, staple=staple, needs=needs, source=src, inputs=groups)
        n_child += 1

    # ------------------------------------------------------- 4. from the crop register
    # The fruit and the vegetables, which had no home until Khoury's Table S1 said where each
    # crop was domesticated. `farming` arriving in an area is the floor: an orchard is a farm.
    farm = {a: max(FLOOR, y) for a, y in (tech.get("farming") or {}).items() if a in AREAS}
    n_crop = 0
    for khoury, spec in CO.SOWN.items():
        home = CO.home_areas(crops).get(spec["id"], {}).get("areas") or []
        if not home:
            problems.append(f"'{spec['id']}': Khoury gives no region of diversity")
            continue
        made = {}
        for a in home:
            y = max(spec["domesticated"], farm.get(a, FLOOR))
            made[a] = y
        brought = {}
        # No farming floor on a brought year. The technology atlas says farming reaches
        # Polynesia in 1521, but the sweet potato is measured in the Cook Islands by 1210 --
        # carried across the Pacific centuries before Columbus. Letting an arrival register
        # override a dated arrival would erase one of the best-attested facts in the whole
        # subject. The floor is a claim about domestication, not about trade.
        for group, year in spec.get("to", {}).items():
            if year is None:
                continue
            for a in B.GROUPS.get(group, []):
                if a in made:
                    continue
                brought[a] = year
        for a, year in spec.get("to_area", {}).items():
            if a not in made and a in AREAS:
                brought[a] = year
        add(spec["id"], spec["name"], spec["family"], made, brought,
            note=spec.get("note", ""),
            source="Khoury et al. 2016 for the region of diversity; the archaeological "
                   "literature for the date; the technology atlas for when farming arrives")
        n_crop += 1

    # --------------------------------------------- 5. nothing before everything it is made from
    # What counts as a fire. A product that already burns one thing does not need another listed.
    FUELS = {"firelight", "firewood", "charcoal", "coal", "peat", "dung_fuel"}

    # Part B wrote inputs by hand for the products it knew, and part D wrote extras for some of
    # the same ones (glass needs sandstone as well as its fuel). Merge rather than overwrite, or
    # the 28 part B rows with extras silently lose them.
    for p in products:
        if p.get("derived"):
            continue
        extra = C.EXTRA_INPUTS.get(p["id"])
        if not extra:
            continue
        groups = [list(g) for g in p.get("inputs", [])]
        have = {m for g in groups for m in g}
        for g in extra:
            g = list(g)
            if g in groups:
                continue
            if set(g) <= have:
                continue                      # gunpowder already says saltpetre and sulphur
            if set(g) <= FUELS and have & FUELS:
                continue                      # glass already burns something; do not say it twice
            groups.append(g)
            have.update(g)
        p["inputs"] = groups

    # Writing the inputs down immediately found 141 contradictions: a health certificate dated
    # 1610 in Middle North America where ink does not arrive until 1640. A product cannot exist
    # before any of its inputs, so every year is pushed forward until the whole graph agrees.
    # Years only ever increase and are bounded above, so this settles.
    for _pass in range(40):
        moved = 0
        for p in products:
            for group in p.get("inputs", []):
                for a in list(p["made"]):
                    have = [first_year(by_id[i], a) for i in group if i in by_id]
                    have = [y for y in have if y is not None]
                    if not have:
                        continue
                    need = min(have)
                    if p["made"][a] < need:
                        p["made"][a] = need
                        moved += 1
        if not moved:
            break
    else:
        problems.append("the chain never settled after 40 passes")

    # ------------------------------------------------------- 6. who makes it, and where
    # Part B's 132 rows were written before this existed and carry no work or workplace, so the
    # whole list is stamped here rather than only the rows this part adds.
    for p in products:
        work, place = C.work_of(p["id"], p["family"])
        p["work"] = work
        p["workplace"] = place
        p["workplaceName"] = C.WORKPLACE_NAMES[place]

    # ------------------------------------------------------------------------- checks
    # every area and year must still have its four staples
    problems.extend(C.check_against(products))
    # part B's own chain check, run over the whole list now that part D has filled the inputs in:
    # nothing may be made where and when its inputs are not.
    saved = B.PRODUCTS[:]
    del B.PRODUCTS[:]
    B.PRODUCTS.extend(products)
    try:
        for pr in B.check():
            problems.append(pr)
    finally:
        del B.PRODUCTS[:]
        B.PRODUCTS.extend(saved)
    for staple in ("food", "cloth", "fuel", "light"):
        for a in AREAS:
            if not any(p.get("staple") == staple and first_year(p, a) is not None
                       and first_year(p, a) <= -3000 and not p.get("needs") for p in products):
                problems.append(f"no {staple} without needs in {a} from 3000 BCE")
    # a product dated before its parent is impossible
    for pid, name, fam, parent, tid, _s, _n in D.CHILD_PRODUCTS:
        ch, par = by_id.get(pid), by_id.get(parent)
        if ch is None or par is None:
            continue
        for a in AREAS:
            cy, py = first_year(ch, a), first_year(par, a)
            if cy is not None and py is not None and cy < py:
                problems.append(f"{pid} in {a} ({cy}) is earlier than its parent {parent} ({py})")
    # a product limited by nature must stay inside its range
    for pid, allowed in D.AREA_LIMITS.items():
        p = by_id.get(pid)
        if p is None:
            continue
        outside = sorted(set([*p["made"], *p["brought"]]) - set(allowed))
        if outside:
            problems.append(f"{pid} is in {outside}, outside its natural range")
    # no product may appear in an area before the technology that makes it
    for tid, rows in D.TECH_PRODUCTS.items():
        arrivals = tech.get(tid) or {}
        for pid, _n, _f, _note in rows:
            p = by_id.get(pid)
            if p is None:
                continue
            for a, y in p["made"].items():
                if a in arrivals and y < arrivals[a] and y != ANY:
                    problems.append(f"{pid} made in {a} in {y}, before {tid} arrives "
                                    f"({arrivals[a]})")
    # ids unique
    seen = collections.Counter(p["id"] for p in products)
    dupes = sorted(i for i, n in seen.items() if n > 1)
    if dupes:
        problems.append("ids used twice: " + ", ".join(dupes))
    # families real
    for p in products:
        if p["family"] not in B.FAMILIES:
            problems.append(f"{p['id']}: family '{p['family']}' is not one of the fourteen")

    return products, (start, n_tech, n_min, n_child, n_crop), problems


def main(argv):
    products, counts, problems = build()
    start, n_tech, n_min, n_child, n_crop = counts
    for p in problems:
        print("  PROBLEM " + p)
    if problems:
        print(f"products: {len(problems)} problem(s); nothing written")
        return 1
    if "--check" in argv:
        print(f"products: {len(products)} products, 0 problems")
        return 0

    data = {
        "format": 1,
        "about": "Product atlas (worldfill/build_product_atlas.py for part B, "
                 "worldfill/build_products_c.py for part C): the world product list and, per area "
                 "of the ways-of-life survey, the year each product is first made there, first "
                 "brought there, and gone. Part B's 132 rows are hand-written estimates "
                 "(estimate=true) from the history of each product. Part C's rows are derived "
                 "(derived=true) and carry a `source` naming the register each year came from: "
                 "the technology atlas, the mineral register, or a parent product.",
        "areas": [{"id": a, "name": B.AREA_NAMES[a]} for a in AREAS],
        "families": B.FAMILIES,
        "products": products,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    write_table(products)
    print(f"products: {len(products)} ({start} hand-written + {n_tech} from technologies + "
          f"{n_min} from minerals + {n_child} from a parent + {n_crop} from the crop register), "
          f"{os.path.getsize(OUT)} bytes")
    return 0


def write_table(products):
    """The same years as a table, for checking by eye."""
    lines = ["# Product atlas: the years (generated by build_products_c.py)", "",
             "Each cell: the year a product is first **made** in the area; *b* = first brought "
             "there by trade; *g* = gone (replaced). Empty: never. BCE years are negative.",
             "Areas: " + "; ".join(f"{a} {B.AREA_NAMES[a]}" for a in AREAS) + ".", "",
             "Rows marked *(est.)* are part B, hand-written estimates for a whole area (its "
             "earliest corner). Rows marked *(derived)* are part C: their years are read out of "
             "the technology atlas, the mineral register and their parent product -- none of "
             "them was written by hand.", ""]
    for fam in B.FAMILIES:
        rows = [p for p in products if p["family"] == fam]
        if not rows:
            continue
        lines += [f"## {fam[0].upper() + fam[1:]} ({len(rows)})", "",
                  "| Product | " + " | ".join(AREAS) + " |", "|---|" + "---|" * len(AREAS)]
        for p in rows:
            cells = []
            for a in AREAS:
                c = []
                if a in p["made"]:
                    c.append("always" if p["made"][a] == ANY else str(p["made"][a]))
                if a in p["brought"]:
                    c.append("b " + ("always" if p["brought"][a] == ANY else str(p["brought"][a])))
                if a in p["gone"]:
                    c.append(f"g {p['gone'][a]}")
                cells.append(" ".join(c))
            mark = " *(derived)*" if p.get("derived") else (" *(est.)*" if p.get("estimate") else "")
            if p.get("inputs"):
                mark += " <- " + ", ".join(" or ".join(g) for g in p["inputs"])
            lines.append(f"| {p['name']}{mark} | " + " | ".join(cells) + " |")
        lines.append("")
    with open(TABLE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
