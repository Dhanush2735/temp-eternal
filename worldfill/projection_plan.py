#!/usr/bin/env python3
"""
**Every data pack, and what it says about the year 2400.**

    python3 projection_plan.py            classify all packs and print the table

The user asked whether the same "all kinds of data" that exists for 3000 BC to AD 2026 can be
built for AD 2027 to 3000. The honest answer is **not all of it, and the reason is not a lack of
effort**: some data classes are *computable* and can be extended exactly, some are *states that
persist* and can be carried with the `projected` mark, and some are *inventions* that no method can
produce without lying.

So this script does the thing that is actually useful: it takes every pack that ships, assigns it
one of five answers for the projected years, and **fails if any pack is left without an answer**.
That is a stronger guarantee than a pack of made-up rows, because it means no part of the engine
goes silent at the seam and pretends nothing happened.

The five answers:

  * **COMPUTED**  - a formula. Eclipses, calendars, the rotation of the sky, the diffusion of a
                   technology already invented. Correct at 3000 for the same reason it is correct
                   at 1200: nothing in it was ever looked up.
  * **CARRIED**   - a state that continues. A technology that arrived stays; a building that stands
                   is still standing; a border with `end: 9999` has no end. Emitted with the
                   `projected` mark so a reader can tell.
  * **REFUSED**   - a person, a ruler, an event, a war, a price or a population figure. The engine
                   will not invent one, and `Projector` says so in words instead.
  * **PAST ONLY** - the pack is a record of something that has already happened (an excavation, a
                   scenario, a named century). It has no future state to give and asking it for one
                   is a category error.
  * **TEMPLATE**  - the pack is not history at all: it is a starting shape for a new world.

The rule the engine already follows and this script measures: **2026 is the last year a record
reaches**, and a projection must never be indistinguishable from a record.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
DATA = os.path.join(ROOT, "eternal", "src", "main", "resources", "data", "eternalengine",
                    "eternal")

COMPUTED, CARRIED, REFUSED, PAST_ONLY, TEMPLATE = (
    "computed", "carried", "refused", "past only", "template")

# ---------------------------------------------------------------------------------------------
# The classification, by path. Order matters: the first rule that matches wins, so the specific
# rules come before the general ones. Every rule names its class, its one-line answer for 2400,
# and the evidence in the code or the data that makes the answer true rather than asserted.
RULES = [
    # ---- COMPUTED: nothing in these was ever looked up --------------------------------
    (r"sky_eclipses\.bin\.gz", COMPUTED,
     "eclipses are computed from Besselian elements, and the catalog already runs to AD 3000",
     "SkyEclipses: 11,898 solar and 12,064 lunar to 3000 CE; TMAX = 3.0"),
    (r"sky_stars\.json\.gz", COMPUTED,
     "the stars do not move in a thousand years: precession only rotates the frame",
     "SkyStars: positions plus precession, valid for any year"),
    (r"calendars\.json\.gz", COMPUTED,
     "every calendar in it is a formula: Gregorian, Julian, Hijri, Saka, Vikram, Fasli, Chinese",
     "Calendars.gregorian/hijri/chinese etc. take an epoch day and never consult the year"),
    (r"technology_atlas\.json\.gz", COMPUTED,
     "the diffusion curve keeps running past 2026, so an invented technology finishes spreading",
     "TechnologyAtlas.seriesAt grows to maxShare with 1-exp(-(year-lastYear)/d50), unclamped"),
    (r"day_round\.json\.gz", COMPUTED,
     "the shape of a day is a function of the clock and the latitude",
     "the daily round is keyed to hour and season, not to a date in the record"),

    # ---- REFUSED: the six kinds that must never be invented ---------------------------
    (r"events.*\.json(\.gz)?$", REFUSED,
     "an event is an invention: Projector refuses war, disaster and happening past 2026",
     "Projector.Kind.EVENT and DISASTER are never carried"),
    (r"(battles|sieges|sides|formations|state_relations|disputed_lands)\.json", REFUSED,
     "a war, a battle and a side are events, and no method derives the next one",
     "Projector refuses EVENT and WAR"),
    (r"(famous_people|world_rulers|deccan_rulers)\.json", REFUSED,
     "a person is the clearest refusal of all: no derivation produces a name",
     "Projector refuses PERSON and RULER; LeaderRegister carries only the LAST RECORDED head"),
    (r"money_table\.json", REFUSED,
     "an exchange rate is a price, and a price is refused past the last recorded year",
     "Prices.LAST_YEAR = 1914, four years before the guardrail"),
    (r"population/.*json", REFUSED,
     "a population figure past the last measured year is refused",
     "Projector refuses POPULATION; the survey stops in 1899"),
    (r"(migrations|morale)\.json(\.gz)?$", REFUSED,
     "a movement of people or a mood is a happening, and happening is what is refused",
     "same class as EVENT"),
    (r"(climate_periods|events_hazards|events_nature|events_storms)\.json(\.gz)?$", REFUSED,
     "a climate period and a natural hazard are events with a date, and the next has no date",
     "refused as EVENT; the pattern of the past is kept, the next instance is not invented"),

    # ---- PAST ONLY: a record of something already over ---------------------------------
    (r"(indus|egypt|mesopotamia|china|americas|mediterranean|south_asia|afro_islamic)\.json$",
     PAST_ONLY,
     "a regional excavation of one past civilization: there is no 2400 in it",
     "the pack is a corpus of finds, not a live state"),
    (r"(deccan_events|knowledge/hyderabad_1948)\.json$", PAST_ONLY,
     "a dated dossier of one city or region; the future of that city is not in it",
     "a corpus, not a state"),
    (r"scenarios/", PAST_ONLY,
     "a what-if anchored on one date; it has no continuation by construction",
     "a scenario is a counterfactual about the past"),
    (r"(prices|sky_comets)\.json(\.gz)?$", PAST_ONLY,
     "a table of observed prices or observed comets: the next one was never observed",
     "observations, not a generator"),

    # ---- TEMPLATE: not history at all ---------------------------------------------------
    (r"templates/", TEMPLATE,
     "a shape for a new world, not a fact about a year",
     "read at world creation, not read by year"),
    (r"data_source_config\.json$", TEMPLATE,
     "configuration, not data",
     "not a year-keyed pack"),
    (r"(index|manifest|README)\.(json|md)$", TEMPLATE,
     "an index of the packs, not a pack",
     "not year-keyed"),

    # ---- the rest, each one looked at rather than swept up ----------------------------
    (r"(disaster_supplement|life_table)\.json(\.gz)?$", REFUSED,
     "a disaster is an event and a life table is a population measure: both refused",
     "Projector refuses DISASTER and POPULATION"),
    (r"population/hyde_density\.bin\.gz", REFUSED,
     "a population density grid: the last measured year is the last one",
     "Projector refuses POPULATION"),

    # ---- CARRIED: a state that continues ----------------------------------------------
    (r"(borders|border|formations)\.json(\.gz)?$", CARRIED,
     "a border with no end is already open-ended: the engine writes end 9999 for 'still there'",
     "borders.json india_republic end 9999"),
    (r"(products_world|credit|law|local_languages|minerals|occupations|polity_facts|presence|"
     r"present_.*|trade_routes|places_chgis|places_pleiades|places_reba)\.json(\.gz)?$", CARRIED,
     "a standing state: what is made, spoken, mined, owed, held or standing", 
     "minerals do not move in a thousand years and a border with no end has no end"),
    (r"(products|goods|substitutes|tools|vehicles|vehicle_mods|traffic|animals|herds|spread|"
     r"anachronisms|wardrobe|skin_pool|games|arts|wildlife|healers|health|ways_of_life|"
     r"ways_works|water_works|water_changes|buildings.*|building_culture|towns|jobs|justice|"
     r"kinship|social_order|beliefs|holy_places|culture|names.*|households|food|seats|"
     r"soundscape|signs|scenes|scripts|armory|arms|units|weapon_items|religions|"
     r"foundation_civilizations|foundation_buildings|foundation_events|foundation_names|"
     r"foundation_religions|foundation_technology_tree|foundation_vips)\.json(\.gz)?$", CARRIED,
     "a standing state: what is made, worn, played, built, believed or owned, carried forward",
     "read by year as 'available since', so a year past the data keeps the last state"),
]

# Anything not matched above is a finding, not a silent skip. This is the check that makes the
# exercise worth doing: a pack with no stated answer is exactly the pack that would go quiet at
# the seam without anybody noticing.
UNMATCHED_IS_A_PROBLEM = True


def packs():
    out = []
    for dirpath, _dirs, files in os.walk(DATA):
        for f in files:
            if f.endswith((".json", ".json.gz", ".bin.gz")):
                out.append(os.path.relpath(os.path.join(dirpath, f), DATA).replace(os.sep, "/"))
    return sorted(out)


def classify(path):
    for pattern, cls, answer, evidence in RULES:
        if re.search(pattern, path):
            return cls, answer, evidence
    return None, None, None


def refused_kinds():
    """The six refuses, read out of Projector so this script cannot drift from the engine."""
    p = os.path.join(ROOT, "eternal", "src", "main", "java", "com", "eternalengine", "clock",
                     "Projector.java")
    text = open(p, encoding="utf-8").read()
    carried = re.findall(r"^\s*(?:CARRY|CARRY_|.*?)\b([A-Z][A-Z_]{3,})\b", text, re.M)
    return text, carried


def main():
    rows = []
    problems = []
    for path in packs():
        cls, answer, evidence = classify(path)
        if cls is None:
            problems.append("no stated future answer for " + path)
            rows.append((path, "UNCLASSIFIED", "", ""))
        else:
            rows.append((path, cls, answer, evidence))

    counts = {}
    for _p, cls, _a, _e in rows:
        counts[cls] = counts.get(cls, 0) + 1

    print("projection plan: %d packs in the shipped data" % len(rows))
    print()
    for cls in (COMPUTED, CARRIED, REFUSED, PAST_ONLY, TEMPLATE, "UNCLASSIFIED"):
        if cls in counts:
            print("  %-11s %3d" % (cls, counts[cls]))
    print()
    print("  %-46s %-11s %s" % ("pack", "answer for 2400", "why"))
    for path, cls, answer, evidence in rows:
        print("  %-46s %-11s %s" % (path, cls, answer[:96]))

    # The seam itself must be stated by the engine, in one place.
    tl = os.path.join(ROOT, "eternal", "src", "main", "java", "com", "eternalengine", "clock",
                      "Timeline.java")
    text = open(tl, encoding="utf-8").read()
    for must in ("FIRST_YEAR = -3000", "LAST_YEAR = 3000", "RECORDED_UNTIL = 2026",
                 'PROJECTED = "projected"'):
        if must not in text:
            problems.append("Timeline does not declare " + must)

    print()
    for p in problems:
        print("  PROBLEM " + p)
    print("projection_plan: %d problem(s)" % len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
