#!/usr/bin/env python3
"""
Step 47 part 6 (E15): **medicine and healers by era** — the second half.

    python3 healers_table.py         check the register and print it

The plan's row is *"Medicine and healers by era"* and the survey found it split in two unequal
halves:

* **The medicine is done.** Step 38's health register carries 14 remedies, each with a year, a place
  it was learned, a multiplier, and the note that says what it actually did. `MedicineSystem.tierAt`
  asks that register by coordinates, so the old fault (the whole planet becoming modern on one day
  in 1945) is already fixed. **The plan's row is wrong about this and says "old code".**
* **The healers are not.** Nothing in the engine knows that a broken arm in 1200 is set by a
  bonesetter and not by a physician, because in most of the world for most of the record there was
  no physician to be had.

## What a healer is not

A healer is not a remedy. The remedies are *things that work* (quinine, vaccination, anaesthesia)
and they spread as technology spreads. A healer is *a person you can get to*, and their data is
therefore a different shape: **who is available, how far you have to travel, what they will touch,
and whether the neighbours approve of them.** The last one is the part a game always leaves out and
it is the most historical of all.

## The two findings this register exists to hold

1. **Surgery is four thousand years older than anaesthesia.** Cutting is as old as the record:
   trepanation, cataract couching, Caesarean sections on living and dead women, amputations with
   bronze knives. Being able to do it without the patient feeling it starts in 1846. A game that
   gates surgery on anaesthesia has the order of events exactly backwards.
2. **The midwife is the oldest trained practitioner and the least respected one.** Childbirth is
   the one emergency that happens in every place in every century, so the midwife is the only healer
   who is universal. In Europe between about 1450 and 1750 she is also the one prosecuted: the
   *Malleus Maleficarum* of 1487 names her, and the male obstetrician with forceps (the Chamberlen
   family, kept secret from the 1630s) takes her work from her among people who can pay. **A healer
   register whose only axis is "how good is the medicine" cannot show any of that.**
"""

AREAS = ["NNA", "MNA", "CAC", "SAM", "EUR", "EEU", "WAS", "NAF", "WAF", "MSA", "EAF", "CAS",
         "SAS", "EAS", "SEA", "AUS", "PAC"]

# What a healer will touch. A list, so that a game can ask "is there anybody here for a broken arm".
TENDS = ["childbirth", "fever", "wounds", "bones", "teeth", "eyes", "madness", "plague",
         "the dying", "children", "skin", "poison"]

# How far a person will go to reach them.
REACH = ["household", "village", "town", "region", "world"]

# Standing: how the neighbours regard the trade. `respectable` is not the same as `effective`.
STANDING = ["respected", "ordinary", "tolerated", "suspect", "prosecuted"]

# Each row: the year the trade is attested SOMEWHERE, plus per-area exceptions where the ARRIVAL
# differs. `reach` is how far a patient travels for it.
#
# **`standing_changes` is a separate axis and that is the point of this register.** The midwife does
# not arrive in Europe in 1450; she has been there since the first birth, and in 1450 she becomes
# prosecutable and in about 1750 she becomes ordinary again. A register with one axis (year in, year
# out) cannot say that, and the midwife is the case that proves it needs two.
HEALERS = [
    dict(id="household", name="the woman of the house", kind="folk", year=-3000, reach="household",
         tends=["childbirth", "fever", "wounds", "children", "the dying"], standing="ordinary",
         areas={}, note=(
        "**The healer most people actually saw, in every century and in every place.** She is not a "
        "profession, she has no training anybody wrote down, and she is the reason the human race "
        "did not die out: childbirth, fever and the ordinary injuries of a farming household were "
        "her work everywhere. **Nothing in this register would have been visible without her**, "
        "because a register of trades lists only the people who were paid."),
         source="the household accounts, letters and remedy books that survive; the general "
                "ethnography"),
    dict(id="herbalist", name="the herbalist", kind="folk", year=-3000, reach="village",
         tends=["fever", "wounds", "poison", "skin", "children"], standing="ordinary", areas={},
         standing_changes=[("EUR", 1200, "suspect"), ("EUR", 1750, "ordinary")],
         note=(
        "**The plant knowledge that is older than writing and is still the source of most drugs.** "
        "Willow bark is aspirin, poppy is morphine, cinchona is quinine, foxglove is digitalis. The "
        "trade is respected in a village and it becomes *suspect* in Europe once medicine becomes a "
        "university subject: the same knowledge, held by a woman with no Latin, is a poisoner's "
        "knowledge in a courtroom."),
         source="the materia medica of Dioscorides and Shennong; the European cunning-woman trials"),
    dict(id="midwife", name="the midwife", kind="folk", year=-3000, reach="village",
         tends=["childbirth", "children"], standing="respected", areas={},
         standing_changes=[("EUR", 1450, "prosecuted"), ("EUR", 1750, "ordinary")],
         note=(
        "**The oldest trained practitioner and the one with the worst century.** Childbirth happens "
        "everywhere, so the midwife is the only healer who is universal. The *Malleus Maleficarum* "
        "of 1487 names her among witches, and the European witch trials kill midwives "
        "disproportionately between about 1550 and 1650; at the same time the male obstetrician with "
        "forceps (the Chamberlen family's secret, from the 1630s) takes the paying work. **Her "
        "standing in the data drops in 1450, which is what `standing` is for.**"),
         source="the Malleus Maleficarum; the Chamberlen forceps; the European trial records"),
    dict(id="bonesetter", name="the bonesetter", kind="folk", year=-3000, reach="village",
         tends=["bones", "wounds"], standing="ordinary", areas={},
         note=(
        "**Setting a fracture needs no theory and has never needed one.** The Egyptians splinted "
        "limbs with linen and resin and the splint is in the surgical papyrus; the trade survives in "
        "villages today wherever a hospital is far away. It is the clearest case of a skill that "
        "does not improve for five thousand years and does not need to."),
         source="the Edwin Smith papyrus; the modern folk-practitioner literature"),
    dict(id="spirit_healer", name="the spirit healer", kind="religious", year=-3000,
         reach="village", tends=["madness", "fever", "the dying"], standing="respected",
         areas={},
         note=(
        "**Not a mistake and not a placebo: a different account of what illness is.** If a fever is "
        "caused by an offended ancestor, the treatment is a negotiation, and the negotiation is "
        "performed by somebody whose office is to perform it. This register keeps it because a world "
        "in which every healer is a rationalist is not a historical world; it is a modern one in "
        "costume."),
         source="the ethnographic record; the anthropology of possession and healing ritual"),
    dict(id="temple_healer", name="the temple healer", kind="religious", year=-2500,
         reach="region", tends=["fever", "madness", "the dying"], standing="respected",
         areas={"WAS": -500, "SAS": -600, "EAS": -100},
         note=(
        "**The first institution in this register and the ancestor of the hospital.** Asklepios at "
        "Epidaurus, the Egyptian temple of Imhotep, the Buddhist monasteries of India: a place you "
        "travel to, sleep in, and are treated in, staffed by people whose qualification is religious. "
        "The Greek *asklepieion* is a pilgrimage site with a waiting list."),
         source="the Epidaurus inscriptions; the Imhotep cult; the Buddhist monastic medical texts"),
    dict(id="physician", name="the physician", kind="professional", year=-600, reach="town",
         tends=["fever", "skin", "madness", "the dying"], standing="respected",
         areas={"SAS": -600, "EAS": -300, "WAS": -400, "EUR": -400, "NAF": 900, "CAS": 900,
                "EEU": 1100, "WAF": 1400, "MSA": 1400, "EAF": 1400, "SEA": 1400,
                "NNA": 1600, "MNA": 1500, "CAC": 1500, "SAM": 1550, "AUS": 1788, "PAC": 1800},
         note=(
        "**A literate theorist who could do very little, and the reason medicine is a profession.** "
        "Hippocratic medicine on Cos, Ayurvedic medicine in India (Charaka, Sushruta), Chinese "
        "medicine with its own anatomy, and the Islamic synthesis of Ibn Sina whose *Canon* is a "
        "European textbook until the seventeenth century. He arrives **late everywhere outside the "
        "four old literate worlds** and that is the honest shape of the thing: in most of the world "
        "for most of the record there was no physician to see."),
         source="the Hippocratic corpus; Charaka and Sushruta; Ibn Sina's Canon"),
    dict(id="surgeon", name="the surgeon", kind="professional", year=-3000, reach="town",
         tends=["wounds", "bones", "eyes", "teeth"], standing="tolerated",
         areas={"SAS": -600, "WAS": -400, "EUR": 1200},
         note=(
        "**Four thousand years older than anaesthesia, and this is the register's sharpest point.** "
        "Trepanation is Neolithic, cataract couching is described by Sushruta, amputation is as old "
        "as bronze knives, and a Roman army surgeon could ligate an artery. What is missing until "
        "**1846** is only the part where the patient does not feel it. **A game that gates surgery "
        "on anaesthesia has the order of events exactly backwards.** In medieval Europe the trade is "
        "a guild of barbers, which is why the man who shaves you is also the man who cuts you."),
         source="the Edwin Smith papyrus; Sushruta's surgical chapters; the barber-surgeon guilds"),
    dict(id="apothecary", name="the apothecary", kind="professional", year=750, reach="town",
         tends=["fever", "poison", "skin"], standing="respected",
         areas={"WAS": 750, "EAS": 700, "SAS": 800, "EUR": 1200, "NAF": 800, "CAS": 900,
                "EEU": 1300, "SEA": 1300, "WAF": 1500, "MSA": 1500, "EAF": 1500,
                "NNA": 1650, "MNA": 1600, "CAC": 1600, "SAM": 1600, "AUS": 1800, "PAC": 1800},
         note=(
        "**The trade that turns a plant into a dose, and the reason a pharmacy is not a grocer.** "
        "The Baghdad *saydalani* of the ninth century has standards, weights and inspections; the "
        "European apothecary is a guild by 1200 and a shop with a licence by 1400. He is where "
        "measurement enters medicine: the difference between a medicine and a poison is the dose."),
         source="the Baghdad pharmacy regulations; the European apothecary guilds"),
    dict(id="plague_doctor", name="the plague doctor", kind="professional", year=1348,
         reach="town", tends=["plague", "fever"], standing="tolerated", areas={"EUR": 1348},
         note=(
        "**Hired by a city, paid by the city, and useless.** The *medico della peste* appears with "
        "the second pandemic in 1348: a municipal employee who visits the sick, certifies deaths and "
        "has no treatment at all. **The beak mask is 1619** (Charles de Lorme), not medieval, and it "
        "is filled with aromatic herbs because the theory was miasma. His real work was "
        "administration, and the quarantine he helped enforce did work."),
         source="the Italian municipal plague records; de Lorme's 1619 costume"),
    dict(id="anatomist", name="the dissector", kind="professional", year=1315, reach="town",
         tends=["wounds", "bones"], standing="suspect", areas={"EUR": 1315, "SAS": 1500,
                                                               "EAS": 1100, "WAS": 1200},
         note=(
        "**The trade that made the physician wrong about the body.** Mondino de' Luzzi dissects in "
        "Bologna in 1315 and Vesalius corrects Galen in 1543, and both are working from a text and "
        "not from the body: for fourteen centuries the anatomy taught in Europe is that of a pig and "
        "a Barbary ape, because Galen never dissected a person. The dissector was **suspect** for a "
        "reason a game can use: he needed corpses, and getting one was a hanging or a robbery."),
         source="Mondino 1315; Vesalius, De humani corporis fabrica, 1543"),
    dict(id="iatrochemist", name="the alchemist-physician", kind="professional", year=1527,
         reach="town", tends=["fever", "poison", "skin"], standing="suspect", areas={"EUR": 1527},
         note=(
        "**Paracelsus, and the argument that medicine is chemistry.** He burns the books in Basel in "
        "1527, treats syphilis with mercury and wounds with minerals rather than with the humours, "
        "and is run out of every town he works in. He is also the reason a pharmacy stocks chemicals "
        "and not only plants. **The standing is `suspect` and the work is real**, which is the pair "
        "this register exists to keep apart."),
         source="Paracelsus's Basel lectures; the iatrochemistry of Van Helmont"),
    dict(id="field_surgeon", name="the army surgeon", kind="professional", year=-50, reach="region",
         tends=["wounds", "bones"], standing="ordinary", areas={"EUR": -50, "SAS": -300,
                                                                 "EAS": -200, "WAS": 900},
         note=(
        "**War is where surgery is practised in volume, so war is where it improves.** The Roman "
        "legion has a *medicus ordinarius* per cohort and a *valetudinarium* per fortress, which is "
        "a hospital by any standard. Ambroise Paré in the 1530s discovers by accident that gunshot "
        "wounds do not need boiling oil, because the oil runs out; Larrey invents the ambulance "
        "corps at the 1790s and the triage that goes with it."),
         source="the Roman military medical corps; Paré's 1537 campaign account; Larrey's memoirs"),
    dict(id="nurse", name="the nurse", kind="institution", year=300, reach="town",
         tends=["fever", "wounds", "the dying", "children"], standing="respected",
         areas={"WAS": 300, "EUR": 500, "SAS": 300, "EAS": 500},
         note=(
        "**An office of the religious before it is a profession of the paid.** Buddhist monasteries "
        "nurse the sick from the 3rd century, Christian hospitals from the 4th (Basil of Caesarea), "
        "and the Islamic *bimaristan* has salaried nursing staff by the 9th. **Nightingale in 1854 "
        "does not invent nursing: she makes it respectable for a middle-class woman and turns it "
        "into a statistics-based profession**, which is a different and later change."),
         source="the monastic infirmary rules; the bimaristan records; Nightingale's 1858 notes"),
    dict(id="dentist", name="the tooth-puller", kind="professional", year=-3000, reach="town",
         tends=["teeth"], standing="tolerated", areas={"SAS": -600, "EUR": 1200},
         note=(
        "**A drill in a Neolithic jaw is the oldest known surgery of any kind.** Mehrgarh, about "
        "7000 BC: eleven drilled molars in nine people, with the caries removed, and no sign of "
        "abscess, which means the patients survived it. The professional is a barber-surgeon for "
        "most of the record and a dentist only with Fauchard in 1728."),
         source="the Mehrgarh dental drill; Fauchard, Le chirurgien dentiste, 1728"),
    dict(id="alienist", name="the mad-doctor", kind="institution", year=1400, reach="region",
         tends=["madness"], standing="suspect", areas={"EUR": 1400, "WAS": 900, "SAS": 1500,
                                                       "EAS": 1500},
         note=(
        "**An institution before it is a treatment.** Bedlam is a priory by 1247 and a byword by "
        "1600; the Islamic *bimaristan* has wards for the mentally ill from the 9th century and "
        "treats them with music and baths. **The standing is `suspect` because the record is**: for "
        "most of these centuries the family was the treatment and the asylum was the warehouse."),
         source="the Bethlem records; the bimaristan wards; Pinel's 1790s reforms"),
]

# The order in which the trades appear, as an independent expectation the check can test.
MUST_PRECEDE = [("household", "physician"), ("herbalist", "apothecary"), ("surgeon", "anatomist"),
                ("midwife", "physician"), ("bonesetter", "field_surgeon")]

# Remedies from step 38 that a trade's work depends on. A healer may not arrive before the remedy
# only where the remedy IS the work: the surgeon does not, because cutting is ancient and
# anaesthesia is not, which is the finding this register exists to record.
NEEDS_REMEDY = [("iatrochemist", "germ_theory", False)]   # (id, remedy, must the remedy come first)


def effective(h, area):
    """The year this trade is available in this area."""
    return h["areas"].get(area, h["year"])


def standing_at(h, area, year):
    """How the neighbours regard the trade in that area and year."""
    out = h["standing"]
    for a, y, st in h.get("standing_changes", []):
        if a == area and year >= y:
            out = st
    return out


def problems():
    bad = []
    seen = set()
    for h in HEALERS:
        if h["id"] in seen:
            bad.append("duplicate healer " + h["id"])
        seen.add(h["id"])
        for t in h["tends"]:
            if t not in TENDS:
                bad.append(h["id"] + " tends " + t + ", which is not in the list of complaints")
        if h["reach"] not in REACH:
            bad.append(h["id"] + " has the reach " + h["reach"])
        if h["standing"] not in STANDING:
            bad.append(h["id"] + " stands " + h["standing"])
        if not h["tends"]:
            bad.append(h["id"] + " treats nothing, so it is not a healer")
        if not h["note"] or len(h["note"]) < 80:
            bad.append(h["id"] + " does not say anything useful")
        if not h["source"]:
            bad.append(h["id"] + " cites nothing")
        for a in h["areas"]:
            if a not in AREAS:
                bad.append(h["id"] + " names the area " + a)
        for a, y, st in h.get("standing_changes", []):
            if a not in AREAS:
                bad.append(h["id"] + " changes standing in " + a + ", which is not an area")
            if st not in STANDING:
                bad.append(h["id"] + " changes standing to " + st)
            if y < effective(h, a):
                bad.append(h["id"] + " changes standing in " + a + " in " + str(y)
                           + ", before it arrives there")
        if h.get("kind") not in ("folk", "professional", "religious", "institution"):
            bad.append(h["id"] + " has the kind " + str(h.get("kind")))

    # THE COVERAGE TEST. Childbirth happens everywhere in every year, so there must be somebody
    # for it in every area in the first year of the span. This is the check that catches a
    # register of trades that has quietly listed only the paid ones.
    for a in AREAS:
        available = [h["id"] for h in HEALERS if effective(h, a) <= -3000]
        if not any("childbirth" in h["tends"] for h in HEALERS
                   if h["id"] in available):
            bad.append("nobody in " + a + " attends a birth in 3000 BC")

    # THE ORDER OF EVENTS.
    by = {h["id"]: h for h in HEALERS}
    for a, b in MUST_PRECEDE:
        for area in AREAS:
            ya, yb = effective(by[a], area), effective(by[b], area)
            if ya > yb:
                bad.append("%s arrives before %s in %s (%d, %d)" % (b, a, area, yb, ya))

    # THE FINDING, AS A TEST: surgery before anaesthesia, and nowhere near it.
    surgeon = by["surgeon"]
    for area in AREAS:
        y = effective(surgeon, area)
        if y >= 1846:
            bad.append("the surgeon only arrives in " + area + " in " + str(y)
                       + ", which would make cutting depend on anaesthesia")

    # THE MIDWIFE MUST DEGRADE, NOT ARRIVE: her standing drops in Europe and nowhere else.
    mid = by["midwife"]
    if mid["standing"] != "respected":
        bad.append("the midwife is the universal practitioner and must start respected")
    changes = {(a, st) for a, _y, st in mid.get("standing_changes", [])}
    if ("EUR", "prosecuted") not in changes:
        bad.append("the midwife's European prosecution is the point of the row and is missing")
    if standing_at(mid, "EUR", 1600) != "prosecuted":
        bad.append("the midwife is not prosecutable in 1600")
    if standing_at(mid, "SAS", 1600) != "respected":
        bad.append("and the midwife outside Europe is untouched, which is the other half of the "
                   "claim")

    # REMEDY CROSS-CHECKS. A trade whose work IS a remedy may not precede it.
    remedies = _remedy_years()
    for hid, rid, must in NEEDS_REMEDY:
        h = by.get(hid)
        if h is None or rid not in remedies:
            continue
        if must and h["year"] < remedies[rid]:
            bad.append(hid + " arrives in " + str(h["year"]) + ", before the remedy " + rid
                       + " (" + str(remedies[rid]) + ")")
    return bad


def _remedy_years():
    """Step 38's health register, if it is there. Absent is not a failure."""
    import gzip
    import json
    import os
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "eternal", "src", "main",
                     "resources", "data", "eternalengine", "eternal", "history", "health.json.gz")
    try:
        with gzip.open(p, "rt", encoding="utf-8") as f:
            d = json.load(f)
        return {r["id"]: r["year"] for r in d["remedies"]}
    except OSError:
        return {}


def main():
    bad = problems()
    print("healers: %d trades over %d areas; %d folk, %d professional, %d religious, "
          "%d institutional"
          % (len(HEALERS), len({a for h in HEALERS for a in h["areas"]} | set(AREAS)),
             len([h for h in HEALERS if h["kind"] == "folk"]),
             len([h for h in HEALERS if h["kind"] == "professional"]),
             len([h for h in HEALERS if h["kind"] == "religious"]),
             len([h for h in HEALERS if h["kind"] == "institution"])))
    print()
    print("  %-14s %-13s %-9s %-7s %-12s %s"
          % ("trade", "kind", "reach", "from", "standing", "treats"))
    for h in HEALERS:
        print("  %-14s %-13s %-9s %-7s %-12s %s"
              % (h["id"], h["kind"], h["reach"], h["year"], h["standing"],
                 ",".join(h["tends"])[:44]))
    for p in bad:
        print("  PROBLEM " + p)
    print("healers_table: %d problem(s)" % len(bad))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
