#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Step 38 part 7 (C20 diseases and medicine): two hand-written tables.

Nothing here is generated, and nothing here is invented without saying so. Every row carries the
source it came from. Where a number is **this table's reading** rather than a published figure the
row is marked ``estimated``, and the register repeats that word every time it prints the number —
a case fatality offered without its mark is a case fatality offered as better than it is.

Two tables:

**REMEDIES** — fourteen things people learned to do, each with a year and a place. A remedy is
worthless in a place it has not reached, so each one is either

* ``atlas="..."`` — already in step 30a's technology atlas, which knows per place and per year when
  it arrived (vaccination, anaesthesia, antiseptic surgery, antibiotics, children's vaccines), or
* an origin place and year, from which the register asks the atlas's own spread function,
  ``arrivesIn(startYear, km, factor)``, when it reached anywhere else.

That is the whole of decision (5): `MedicineSystem`'s world-wide year tier — in 1945 the entire
planet became MODERN simultaneously — becomes *has this reached this place*.

**DISEASES** — eighteen named diseases: what they are, how they move, where and when they are first
recorded, how many of the people who caught them died, and which remedy ended them.

The numbers worth defending:
* smallpox killed about **30%** of the people who caught variola major, and variolation about
  **2%** against **14%** for the natural disease in the Boston epidemic of 1721;
* cholera killed **30 to 60%** of the people diagnosed in nineteenth-century cities, and oral
  rehydration brings that below **1%**;
* Lister's carbolic acid took post-operative infection from nearly **60%** to **4%** in one
  hospital that adopted it.
"""


class R:
    """One remedy: a year, a place, what it could do, and to which diseases."""

    __slots__ = ("id", "name", "year", "place", "lat", "lon", "applies", "mult",
                 "note", "src", "mark", "atlas")

    def __init__(self, rid, name, year, place, lat, lon, applies, mult, note, src,
                 mark="recorded", atlas=None):
        assert isinstance(rid, str) and rid, "remedy needs an id"
        assert isinstance(year, int), "remedy %s needs a whole-number year" % rid
        assert -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0, "remedy %s is off the map" % rid
        assert 0.0 < mult <= 1.0, "remedy %s: a multiplier of %r is not a multiplier" % (rid, mult)
        assert src and isinstance(src, str), "no source, no row: remedy %s" % rid
        assert mark in ("recorded", "mixed", "estimated"), \
            "remedy %s: bad mark %r" % (rid, mark)
        assert applies in ("all", "filth", "contact", "vector", "smallpox", "surgical", "air"), \
            "remedy %s applies to an unknown class of disease: %r" % (rid, applies)
        self.id = rid
        self.name = name
        self.year = year
        self.place = place
        self.lat = lat
        self.lon = lon
        self.applies = applies
        self.mult = mult
        self.note = note
        self.src = src
        self.mark = mark
        self.atlas = atlas


REMEDIES = [
    # ---------------------------------------------------------------- before the germ
    R("humoral", "the medicine of the four humours", -400, "Cos", 36.89, 27.29,
      "all", 0.98,
      "Bloodletting, purging and the balance of four fluids. It is in this table because for two "
      "thousand years it was the only medicine there was, and because it could do **nothing** for "
      "an epidemic: the multiplier is 0.98, not 0.50, because what it did for a plague was "
      "nothing, and what it did for a fever was often to bleed the patient.",
      "English Wikipedia, 'Humorism' and 'Hippocrates'; mark estimated"),

    R("hospital", "the hospital: a place kept for the sick", 805, "Baghdad", 33.31, 44.42,
      "all", 0.97,
      "The bimaristan, and the infirmary after it: a building where the sick are gathered, fed "
      "and washed rather than left in the street. It did not cure anything — hence 0.97 — but it "
      "is the beginning of the idea that a society owes the sick somewhere to be.",
      "English Wikipedia, 'Bimaristan'; mark estimated"),

    R("quarantine", "quarantine: forty days", 1377, "Ragusa", 42.65, 18.09,
      "contact", 0.80,
      "Ships from a plague port made to lie at anchor before anyone came ashore: thirty days at "
      "Ragusa in 1377, then forty, and *quaranta giorni* is where the word comes from. The first "
      "measure in history that worked against a disease nobody understood, arrived at a hundred "
      "years before anybody knew why.",
      "English Wikipedia, 'Quarantine'; the date and the figure are this table's reading, mark "
      "estimated"),

    R("variolation", "variolation: giving the disease on purpose", 1721, "Boston", 42.36, -71.06,
      "smallpox", 0.80,
      "Matter from a mild case put into a scratch on a healthy arm. In the Boston epidemic of "
      "1721 **844 of 5,980** people who caught smallpox naturally died — 14% — against **6 of "
      "244** who were variolated, 2.5%. The first time anybody measured a medical intervention "
      "and found it worked.",
      "College of Physicians of Philadelphia, historyofvaccines.org vaccine timeline; "
      "Riedel, 'Edward Jenner and the history of smallpox and vaccination' (PMC1200696)"),

    R("vaccine", "vaccination", 1796, "Berkeley", 51.69, -2.46,
      "smallpox", 0.60,
      "Jenner put cowpox matter into the arm of James Phipps in May 1796: the same principle as "
      "variolation with a source that could not give anybody smallpox. The only disease this has "
      "ever been done to was wiped off the face of the earth — the last natural case in Somalia "
      "in October 1977, certified eradicated on **8 May 1980**.",
      "World Health Organization, 'History of smallpox vaccination'; English Wikipedia, "
      "'Smallpox vaccine'",
      atlas="smallpox_vaccine"),

    # ---------------------------------------------------------------- the nineteenth century
    R("public_health", "public health: clean water and drains, as a duty of the state", 1848,
      "London", 51.51, -0.13,
      "filth", 0.70,
      "The Public Health Act of 1848 in Britain, the first national framework anywhere: water "
      "supply, drainage, housing. Made compulsory in 1875. It saved more lives than any drug of "
      "its century and it was plumbing.",
      "Britannica, 'History of Public Health: A Timeline'"),

    R("anaesthesia", "surgery without pain", 1846, "Boston", 42.36, -71.06,
      "surgical", 0.95,
      "Ether demonstrated at the Massachusetts General Hospital on 16 October 1846. It changed "
      "what a surgeon could attempt; it changed nothing at all about an epidemic, which is why "
      "the multiplier here is 0.95 and the class is ``surgical``.",
      "English Wikipedia, 'Timeline of medicine and medical technology'; "
      "Preceden history of medicine timeline",
      atlas="anaesthesia"),

    R("epidemiology", "epidemiology: counting where the cases are", 1854, "London", 51.51, -0.13,
      "filth", 0.60,
      "John Snow mapped ten days of cholera deaths in Soho, found five hundred of them clustered "
      "on one water pump in Broad Street, and took the handle off — **before the germ theory, "
      "before anybody could say what he was right about**. The founding case of the subject.",
      "Britannica public-health timeline; 'John Snow, Cholera, the Broad Street Pump' "
      "(PMC7150208)"),

    R("antiseptic", "clean surgery", 1867, "Glasgow", 55.86, -4.25,
      "surgical", 0.90,
      "Lister's carbolic acid, published in *Antiseptic Principle of the Practice of Surgery* in "
      "1867 after reading Pasteur. In one hospital that adopted it, deaths from infection after "
      "an operation fell from nearly **60%** to **4%**. Surgery stopped being a death sentence; "
      "epidemics were untouched.",
      "Britannica, 'Germ theory'; English Wikipedia, 'Timeline of medicine and medical "
      "technology'; Infoplease medical advances timeline",
      atlas="antiseptic"),

    R("germ_theory", "the germ theory: a specific germ, a specific disease", 1861, "Paris",
      48.86, 2.35,
      "all", 0.75,
      "Pasteur disproved spontaneous generation in 1861; Koch gave the world the postulates, the "
      "anthrax bacillus in 1876, the tubercle bacillus in **1882** and the cholera vibrio in "
      "1883. Everything after this is downstream of it.",
      "Britannica, 'Germ theory'; English Wikipedia, 'Medical microbiology' and 'Koch-Pasteur "
      "rivalry'"),

    # ---------------------------------------------------------------- the twentieth century
    R("antibiotics", "penicillin", 1941, "Oxford", 51.75, -1.26,
      "all", 0.30,
      "Fleming saw the mould in 1928 at St Mary's in London and could not purify it; Florey and "
      "Chain did, from 1939, and the first clinical trials were in 1941. The American government "
      "funded mass production for D-Day in 1944. Bacterial infection stopped being a death "
      "sentence for the first time in the whole of human history.",
      "USDA Agricultural Research Service, 'Penicillin: Opening the Era of Antibiotics'; "
      "English Wikipedia, 'Timeline of medicine and medical technology'",
      atlas="antibiotics"),

    R("child_vaccines", "vaccines for children", 1948, "London", 51.51, -0.13,
      "contact", 0.45,
      "Diphtheria, whooping cough, tetanus, then polio and measles: the diseases of childhood "
      "taken out of childhood. Between them and penicillin, the infectious mortality of a rich "
      "country fell by more than ninety per cent inside one generation.",
      "English Wikipedia, 'Timeline of medicine and medical technology'; "
      "step 30a technology atlas, tech 'child_vaccines'",
      atlas="child_vaccines"),

    R("rehydration", "oral rehydration: a pinch of salt and a handful of sugar", 1968, "Dhaka",
      23.81, 90.41,
      "filth", 0.10,
      "Worked out in the cholera hospitals of East Pakistan and India in the 1960s. A glass of "
      "water with the right salts in it, given early, takes cholera from killing half the people "
      "it reaches to killing fewer than one in a hundred. The cheapest life-saving medicine there "
      "has ever been.",
      "Our World in Data, 'Historical pandemics' (cholera); 'John Snow, Cholera, the Broad "
      "Street Pump' (PMC7150208); the date is this table's, mark estimated",
      mark="estimated"),

    R("xray", "seeing inside the body", 1895, "Wurzburg", 49.79, 9.93,
      "surgical", 0.95,
      "Rontgen's X-ray, 1895. Diagnosis, not cure — and tuberculosis, the great killer of the "
      "nineteenth century, could at last be found before it was fatal, which is worth something "
      "even without a drug.",
      "English Wikipedia, 'Timeline of medicine and medical technology'; step 30a technology "
      "atlas, tech 'xray'",
      atlas="xray"),
]


class D:
    """One disease: what it is, how it moves, where it started, and how many it killed."""

    __slots__ = ("id", "name", "also", "germ", "route", "oyear", "oplace", "olat", "olon",
                 "cfr", "cls", "ended", "note", "src", "mark", "endemic")

    def __init__(self, did, name, also, germ, route, oyear, oplace, olat, olon,
                 cfr, cls, ended, note, src, mark="recorded", endemic=True):
        assert isinstance(did, str) and did, "disease needs an id"
        assert -90.0 <= olat <= 90.0 and -180.0 <= olon <= 180.0, "disease %s is off the map" % did
        assert 0.0 < cfr <= 1.0, "disease %s: a case fatality of %r is not one" % (did, cfr)
        assert route in ("air", "filth", "contact", "vector", "blood"), \
            "disease %s moves by an unknown route: %r" % (did, route)
        assert cls in ("all", "filth", "contact", "vector", "smallpox", "surgical", "air"), \
            "disease %s is in an unknown class: %r" % (did, cls)
        assert germ in ("bacterial", "viral", "parasitic", "fungal", "prion"), \
            "disease %s: unknown germ %r" % (did, germ)
        assert src and isinstance(src, str), "no source, no row: disease %s" % did
        assert mark in ("recorded", "mixed", "estimated"), "disease %s: bad mark %r" % (did, mark)
        self.id = did
        self.name = name
        self.also = also
        self.germ = germ
        self.route = route
        self.oyear = oyear
        self.oplace = oplace
        self.olat = olat
        self.olon = olon
        self.cfr = cfr
        self.cls = cls
        self.ended = ended
        self.note = note
        self.src = src
        self.mark = mark
        self.endemic = endemic


DISEASES = [
    # ---------------------------------------------------------------- the plagues
    D("plague_justinian", "the Plague of Justinian", "the first plague pandemic", "bacterial",
      "vector", 541, "Pelusium", 31.05, 32.55, 0.40, "contact", None,
      "*Yersinia pestis*, out of Egypt and into every port of the Mediterranean, returning in "
      "waves for two hundred years. It is the first pandemic anybody dated, because Procopius "
      "was there and wrote it down.",
      "English Wikipedia, 'Plague of Justinian'; the fatality is this table's reading, mark "
      "estimated",
      mark="estimated", endemic=False),

    D("black_death", "the Black Death", "bubonic plague", "bacterial",
      "vector", 1347, "Caffa", 45.03, 35.38, 0.50, "contact", None,
      "Rat fleas on the grain ships out of the Black Sea. Roughly a third to a half of Europe "
      "died in four years; the rat flea does not care whether you are a lord. Fever, swellings "
      "in the groin and the armpit, and death in under a week for most of the people it reached.",
      "English Wikipedia, 'Black Death'; the fatality is this table's reading of the modern "
      "untreated figure, mark estimated",
      mark="estimated", endemic=False),

    D("third_plague", "the third plague pandemic", "the plague of the nineteenth century",
      "bacterial", "vector", 1855, "Yunnan", 24.88, 102.83, 0.60, "contact", "antibiotics",
      "Out of the marmot hunters of Yunnan, to Hong Kong in 1894 — where Alexandre Yersin found "
      "the bacillus that carries his name — and then to every port in the world. It killed "
      "millions in India alone, and it is the pandemic that finally told us what plague was.",
      "English Wikipedia, 'Third plague pandemic'; the fatality is this table's reading, mark "
      "estimated",
      mark="estimated", endemic=False),

    # ---------------------------------------------------------------- the great killers
    D("smallpox", "smallpox", "variola", "viral",
      "contact", -10000, "the Nile valley", 26.00, 32.00, 0.30, "smallpox", "vaccine",
      "Variola major killed about **30%** of the people who caught it; variola minor, under 1%. "
      "The survivors were blind or pocked for life. It is the only human disease that has been "
      "wiped off the face of the earth — last natural case October 1977, certified 8 May 1980.",
      "Our World in Data, 'Smallpox'; English Wikipedia, 'Smallpox'; "
      "Fenner et al., WHO Global Commission final report",
      mark="mixed"),

    D("measles", "measles", "rubeola", "viral",
      "air", -1000, "unknown", 27.00, 30.00, 0.05, "contact", "child_vaccines",
      "The most infectious disease there is: one child in an unexposed village gives it to "
      "practically everybody. Mild in a well-fed child and lethal in a malnourished one, which "
      "is why it is a famine disease as much as a childhood one.",
      "English Wikipedia, 'Measles'; the fatality and the origin date are this table's reading, "
      "mark estimated",
      mark="estimated"),

    D("cholera", "cholera", "the blue death", "bacterial",
      "filth", 1817, "the Ganges delta", 23.17, 89.21, 0.45, "filth", "rehydration",
      "**Seven pandemics** since 1817, all of them out of the Ganges delta. It kills by "
      "dehydration and it kills fast — a healthy person can be dead in a day. In nineteenth-"
      "century cities **30 to 60%** of the people diagnosed died of it; oral rehydration brings "
      "that below **1%**. Over ten million died in India alone between 1892 and 1940.",
      "Our World in Data, 'Historical pandemics'; Earth.org, '8 Diseases that Changed the "
      "World'; English Wikipedia, 'Cholera pandemics'",
      mark="mixed"),

    D("typhoid", "typhoid fever", "enteric fever", "bacterial",
      "filth", -430, "Athens", 37.98, 23.73, 0.15, "filth", "public_health",
      "*Salmonella typhi*, in the water. The plague Thucydides described at Athens in 430 BC is "
      "now usually read as typhus or typhoid, and nobody is certain which. It is a disease of "
      "camps and sieges and crowded cities, and clean water ended it.",
      "English Wikipedia, 'Typhoid fever'; the fatality is this table's reading, mark estimated",
      mark="estimated"),

    D("dysentery", "dysentery", "the bloody flux", "bacterial",
      "filth", -400, "unknown", 30.00, 40.00, 0.10, "filth", "public_health",
      "The companion of every army and every siege in history: more soldiers have died of the "
      "flux than of the enemy. Water that has been near sewage.",
      "English Wikipedia, 'Dysentery'; the fatality is this table's reading, mark estimated",
      mark="estimated"),

    D("typhus", "typhus", "camp fever, gaol fever", "bacterial",
      "vector", 1489, "Granada", 37.19, -3.60, 0.20, "contact", "public_health",
      "Carried by the body louse, which is carried by crowded people who cannot wash. It is the "
      "classic disease of war, siege, prison and ship: it killed more people in the Thirty Years' "
      "War and the retreat from Moscow than the fighting did. Delousing ended it.",
      "English Wikipedia, 'Typhus'; the fatality is this table's reading, mark estimated",
      mark="estimated"),

    D("malaria", "malaria", "the ague, the fever", "parasitic",
      "vector", -2000, "West Africa", 9.00, -5.00, 0.10, "vector", None,
      "A parasite in a mosquito, and probably the largest single killer in the whole of human "
      "history. It is why the sickle-cell trait exists, why Roman Campagna was abandoned, and "
      "why quinine was worth a war. Ronald Ross showed the mosquito carried it in 1897. It is "
      "still here.",
      "English Wikipedia, 'Malaria'; the fatality is this table's reading, mark estimated",
      mark="estimated"),

    D("yellow_fever", "yellow fever", "the yellow jack", "viral",
      "vector", 1648, "Yucatan", 20.68, -89.04, 0.25, "vector", None,
      "A mosquito disease that arrived in the Americas with the slave ships and made the tropical "
      "coast of the New World the white man's grave for three hundred years. It is why the French "
      "sold Louisiana, and a large part of why the Panama Canal was an American project and not a "
      "French one.",
      "English Wikipedia, 'Yellow fever'; the fatality is this table's reading, mark estimated",
      mark="estimated"),

    D("tuberculosis", "tuberculosis", "consumption, the white plague", "bacterial",
      "air", -3000, "unknown", 30.00, 30.00, 0.50, "contact", "antibiotics",
      "The great killer of the nineteenth century — the disease of the crowded industrial city, "
      "and of the Romantic poets who made it beautiful. Koch found the bacillus in **1882**; "
      "streptomycin in 1944 was the first thing that touched it. It is still in the top ten.",
      "English Wikipedia, 'Tuberculosis'; Britannica, 'Germ theory'; the fatality is this "
      "table's reading, mark estimated",
      mark="estimated"),

    D("influenza_1918", "the influenza of 1918", "Spanish flu", "viral",
      "air", 1918, "Haskell County", 37.57, -99.87, 0.025, "air", None,
      "The worst single epidemic in recorded history: roughly a third of the human race was "
      "infected and tens of millions were dead inside two years, most of them young adults in "
      "the prime of life. It went everywhere — the trenches, the shipping lanes and the Arctic "
      "settlements that no ship could reach at all.",
      "English Wikipedia, 'Spanish flu'; Our World in Data, 'Historical pandemics'; "
      "the fatality is this table's reading, mark estimated",
      mark="estimated", endemic=False),

    D("diphtheria", "diphtheria", "the strangling angel", "bacterial",
      "air", -1500, "unknown", 31.00, 34.00, 0.20, "contact", "child_vaccines",
      "A membrane in the throat that suffocates a child. One of the great killers of children "
      "before the vaccine, and the reason a nineteenth-century family expected to bury some of "
      "its children.",
      "English Wikipedia, 'Diphtheria'; the fatality is this table's reading, mark estimated",
      mark="estimated"),

    D("leprosy", "leprosy", "Hansen's disease", "bacterial",
      "contact", -1500, "the Ganges valley", 25.00, 85.00, 0.05, "contact", "antibiotics",
      "Slow, not very infectious, and not a killer — but it made its sufferers outcasts for three "
      "thousand years, which is a fate the register should be able to name. The bacillus was "
      "found by Hansen in 1873, the first bacterium ever shown to cause a human disease.",
      "English Wikipedia, 'Leprosy'; the fatality is this table's reading, mark estimated",
      mark="estimated"),

    D("syphilis", "syphilis", "the great pox", "bacterial",
      "blood", 1494, "Naples", 40.85, 14.27, 0.15, "contact", "antibiotics",
      "Broke out in the French army before Naples in 1494 and went round the world inside a "
      "decade, which is the fastest a disease had ever travelled. Whether Columbus's men brought "
      "it back from the Americas is still argued.",
      "English Wikipedia, 'Syphilis'; the fatality is this table's reading, mark estimated",
      mark="estimated"),

    D("hiv_aids", "AIDS", "HIV", "viral",
      "blood", 1981, "New York", 40.71, -74.01, 0.90, "contact", None,
      "First noticed in 1981, and for a decade a death sentence with no treatment at all. "
      "Antiretrovirals from 1996 turned it into a manageable condition **in the places that could "
      "pay for them**, which is not the places where most of it is — the register should not "
      "pretend otherwise.",
      "English Wikipedia, 'HIV/AIDS'; the fatality is the untreated figure, mark estimated",
      mark="estimated"),

    D("covid_19", "COVID-19", "the coronavirus pandemic", "viral",
      "air", 2019, "Wuhan", 30.59, 114.31, 0.02, "air", None,
      "The first pandemic of the connected age: the whole world knew about it within weeks, and "
      "the whole world shut its borders. A vaccine was designed, tested and given in under a "
      "year — a thing that had never happened before — and it was given unevenly.",
      "English Wikipedia, 'COVID-19 pandemic'; the fatality is this table's reading, mark "
      "estimated",
      mark="estimated", endemic=False),
]
