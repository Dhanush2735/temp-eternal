# J3: what script the signs at a place are written in, and what kinds of sign there are.
#
# WHY THIS TABLE EXISTS, AND WHY IT IS SMALL
# ------------------------------------------
# The survey's decision 4 said the pre-1500 script would be "a reading from the faith map". That
# was wrong, and measuring it is what changed the plan. Two chains were tried and measured first:
#
#   1. nearest living language -> CultureAtlas.scriptOf(language, year)
#      Only 18% of land has a major language within 300 km (174 majors over the whole globe), and
#      only 5% of ALL 6,741 languages match one of the 97 script keys. Result: **12% coverage.**
#
#   2. place -> ruler -> polity languages -> CultureAtlas.scriptOf(language, year)
#      Far better and much richer where it works -- but it is a *modern* chain. Measured:
#      96% in 2000, 81% in 1950, 65% in 1900, 30% in 1300, **24% in 1000, 1% in 500 BC.**
#
# Meanwhile the technology atlas says writing has *arrived* at 100% of land by 1900, 49% by 1300
# and 38% by 1000. So the gap is not "nobody was writing" -- it is "we cannot name the script".
# At AD 1000, 38% of the world had writing and only 24% could be given a script.
#
# So: chain 2 is the *first* answer (it is dated, specific, and says "Persian in the Perso-Arabic
# script" at Delhi in 1700), and this table is the *fallback* that names a script where the chain
# cannot. It is a reading, and every row says so. It is deliberately keyed by the same 17 area
# codes ProductAtlas already uses (NNA, MNA, CAC, SAM, EUR, EEU, WAS, NAF, WAF, MSA, EAF, CAS,
# SAS, EAS, SEA, AUS, PAC) so that it cannot disagree with step 22's writing forms about where
# "here" is.
#
# WHAT IS NOT ESTIMATED
# ---------------------
# Whether there is writing here at all is not from this table. It is
# `TechnologyAtlas.arrivalAt("writing") <= year && !lostAt(...)`, which is measured, dated and per
# country: Sumer -3027, Egypt -3193, Rome -509, Paris -598, Beijing -877, Yucatan -300 (Maya),
# Tenochtitlan 1300 (Aztec), Cuzco 1576 (the Inca had none), Auckland 1814 (missionaries).
# That single instrument is what makes the Cuzco case come out right: chain 2 alone puts
# "Aymara in the Latin alphabet" in Cuzco in 1400, which is a century before any alphabet
# reached the Andes.
#
# Sources are Wikipedia articles, named per row.

from typing import Dict, List, Any


def script(area: str, start, end, name: str, what: str, line: str, source: str,
           note: str = None) -> Dict[str, Any]:
    """One script in one area for a span of years. `end` None means 'still so'."""
    return dict(area=area, start=start, end=end, name=name, what=what, line=line,
                source=source, note=note)


def sign(sid: str, name: str, what: str, line: str, source: str, start=None, end=None,
         areas=None, literacy=0.0, needs=None, note=None) -> Dict[str, Any]:
    """A kind of sign. `areas` None means anywhere; a list means only those areas."""
    return dict(id=sid, name=name, what=what, line=line, source=source, start=start,
                end=end, areas=areas or [], literacy=literacy, needs=needs or [], note=note)


# ===============================================================================================
# The scripts, by area and era. A reading: the script of the region's own documents, not of
# every private letter in it.
# ===============================================================================================

SCRIPTS: List[Dict[str, Any]] = [

    # ---- Europe ------------------------------------------------------------------------------
    script("EUR", -800, 500, "the Latin and Greek capitals",
           "letters cut into stone with a chisel, square and even, no spaces between the words",
           "the letters are cut into the stone in square capitals, with no space between the words "
           "and no lowercase: you have to know where one word stops before you can read the next",
           "Roman square capitals; Greek alphabet"),
    script("EUR", 500, 1150, "the Latin alphabet in uncials",
           "rounded letters written with a pen, then the small clear hand the schools of Charlemagne spread",
           "the writing is rounded now, made with a pen and not a chisel, and in the better "
           "scriptoria it is the small clear hand that the schools spread from the north",
           "Uncial; Carolingian minuscule"),
    script("EUR", 1150, 1500, "the Latin alphabet in blackletter",
           "dense, angular, compressed letters, cheap in vellum and hard to read",
           "the letters are dense and angular, packed close to save vellum; a page of it is a wall "
           "of upright strokes with no easy way in",
           "Blackletter"),
    script("EUR", 1500, None, "the Latin alphabet",
           "the plain upright letters of the printed book",
           "the signs are in the plain upright letters of the printed book",
           "Latin alphabet"),

    # ---- Eastern Europe ----------------------------------------------------------------------
    script("EEU", 900, 1708, "Cyrillic",
           "the letters of the Slavonic books, brought in with the liturgy",
           "the letters are Cyrillic, and they came in with the liturgy rather than with trade: "
           "this is a church hand before it is a merchant's",
           "Cyrillic script"),
    script("EEU", 1708, None, "Cyrillic in the civil script",
           "Peter's reformed letters, cut to look like the Latin printing of the west",
           "the letters are the civil script the tsar cut for printing, which looks like the "
           "Latin type of the west and is meant to",
           "Russian alphabet; Civil script"),

    # ---- Western Asia (the Fertile Crescent and after) ---------------------------------------
    script("WAS", None, -1000, "cuneiform",
           "wedges pressed into wet clay with a reed, then baked",
           "the signs are wedges pressed into clay with the end of a reed: nothing here is "
           "written on anything you could carry away and read later",
           "Cuneiform"),
    script("WAS", -1000, 650, "Aramaic in the square script",
           "the script of the administration, from Egypt to the Indus",
           "the writing is Aramaic in the square script, the hand of the administration from "
           "Egypt to the Indus, and a man can carry a letter a thousand miles and still be read",
           "Aramaic alphabet; History of the Aramaic alphabet"),
    script("WAS", 650, 1928, "the Arabic script",
           "a flowing hand written right to left, the letters joined",
           "the writing runs right to left in a joined hand, and the same letters carry Persian "
           "and Turkish and Arabic alike",
           "Arabic script"),
    script("WAS", 1928, None, "the Latin alphabet",
           "the Latin alphabet, adopted by decree",
           "the signs are in the Latin alphabet, adopted by decree and taught from scratch",
           "Turkish alphabet"),

    # ---- Northern Africa ---------------------------------------------------------------------
    script("NAF", None, 300, "hieroglyphs and demotic",
           "sacred cut signs for the stone, and a running hand for grain and lawsuits",
           "the stone carries the carved sacred signs, but the receipts and the lawsuits are in "
           "the running hand beside them: two scripts, two jobs, for three thousand years",
           "Egyptian hieroglyphs; Demotic"),
    script("NAF", 300, 900, "Coptic",
           "the old language in Greek letters, with a few signs borrowed from demotic",
           "the old language is written in Greek letters now, with a handful of borrowed signs "
           "for the sounds Greek has no letter for",
           "Coptic alphabet"),
    script("NAF", 900, None, "the Arabic script",
           "a flowing hand written right to left, the letters joined",
           "the writing runs right to left in a joined hand",
           "Arabic script"),

    # ---- Southern Asia -----------------------------------------------------------------------
    script("SAS", None, -1900, "the Indus script",
           "short rows of signs on soapstone seals, nobody alive can read them",
           "there are signs here, cut small on soapstone seals and on the clay the merchants "
           "seal their bales with, and nobody now living can read a single one of them",
           "Indus script"),
    script("SAS", -300, 600, "Brahmi",
           "the script of the edicts, cut into rock and pillar for anyone to read",
           "the king's words are cut into rock and set up on pillars beside the roads, in a "
           "script any literate man can sound out",
           "Brahmi script; Edicts of Ashoka"),
    script("SAS", 600, 1300, "the Nagari and the scripts of the regions",
           "one script for the north, and a separate one already for the south",
           "the north has settled into Nagari while the south has long since gone its own way: "
           "two scripts that share an ancestor and no longer look like brothers",
           "Nagari; Grantha; Vatteluttu"),
    script("SAS", 1300, None, "Devanagari and the script of each language",
           "each language with its own letters, hanging from a headline",
           "each language keeps its own letters, and they hang from a line across the top like "
           "washing on a rope",
           "Devanagari; Tamil script; Telugu script; Kannada script; Malayalam script"),

    # ---- Eastern Asia ------------------------------------------------------------------------
    script("EAS", None, -1200, "the oracle-bone script",
           "signs cut into bone and shell to ask the ancestors, and to keep the answer",
           "questions are cut into bone and shell and cracked with heat, and the answer is cut "
           "beside it: the oldest writing here is a record of what the dead said",
           "Oracle bone script"),
    script("EAS", -1200, 300, "the seal and clerical scripts",
           "the old pictured signs, squared up for the brush and for the bureaucrat",
           "the old signs have been squared up for the brush, and squared again for the clerk: "
           "the pictures are still in there but you would not know it",
           "Seal script; Clerical script"),
    script("EAS", 300, None, "Chinese characters",
           "signs that stand for words and not for sounds, so a man who cannot speak to you can "
           "still read what you wrote",
           "the signs stand for words and not for sounds, so a man who cannot speak your "
           "language can read your sign perfectly, and neither of you can say a word of it",
           "Chinese characters; Regular script"),

    # ---- South-Eastern Asia ------------------------------------------------------------------
    script("SEA", 400, 1300, "the Pallava and Mon scripts",
           "the Indic letters, carried here with the gods and the law",
           "the letters came with the gods and the law, and they are Indic letters still, "
           "rounded now and curled for the palm leaf",
           "Pallava script; Mon script"),
    script("SEA", 1300, None, "the script of each people",
           "each people with its own letters, and the trading towns with several",
           "each people keeps its own letters, and a trading town carries three or four at once",
           "Thai script; Khmer script; Jawi script"),

    # ---- Central Asia ------------------------------------------------------------------------
    script("CAS", 700, 1000, "the runic and Old Turkic letters",
           "the old Turkic letters, cut into standing stones",
           "the letters are cut into standing stones out on the steppe, and they speak for a "
           "khagan who wants them read",
           "Old Turkic script; Orkhon inscriptions"),
    script("CAS", 1000, 1930, "the Arabic script",
           "a flowing hand written right to left, the letters joined",
           "the writing runs right to left in a joined hand",
           "Arabic script"),
    script("CAS", 1930, None, "Cyrillic",
           "Cyrillic, in the civil script of the Soviet schools",
           "the signs are Cyrillic, in the script the Soviet schools taught",
           "Cyrillic script"),

    # ---- The Americas ------------------------------------------------------------------------
    script("CAC", -300, 1550, "the Maya signs",
           "blocks of carved signs: a head, a hand, a number, a day",
           "the signs sit in blocks, each one a little picture with a number hanging off it: a "
           "day, a king, a god, and the count of days since the last one",
           "Maya script"),
    script("MNA", None, 1600, "nothing written",
           "pictures and memory, and no script at all",
           "nothing here is written: the record is in the pictures and in what is remembered",
           "History of writing"),
    script("MNA", 1600, None, "the Latin alphabet",
           "the Latin alphabet, brought by the colonists and the missions",
           "the signs are in the Latin alphabet, which came with the colonists",
           "Latin alphabet"),
    script("NNA", None, 1700, "nothing written",
           "memory, and the marks on the land",
           "nothing is written here; the boundaries are in the land and in what is told",
           "History of writing"),
    script("NNA", 1700, None, "the Latin alphabet",
           "the Latin alphabet",
           "the signs are in the Latin alphabet", "Latin alphabet"),
    script("SAM", None, 1540, "nothing written, and the knotted cords",
           "no script: the officials keep their count on knotted cords, and the rest is remembered",
           "there is no writing here at all. The officials keep the count on knotted cords, and "
           "everything else is remembered and told",
           "Quipu"),
    script("SAM", 1540, None, "the Latin alphabet",
           "the Latin alphabet, brought by the Spanish and the Portuguese",
           "the signs are in the Latin alphabet, which came with the Spanish",
           "Latin alphabet"),

    # ---- Africa south of the Sahara ----------------------------------------------------------
    script("WAF", 1100, None, "the Arabic script, and Ajami for the languages themselves",
           "Arabic for the law and the faith, and Arabic letters for the local languages too",
           "Arabic for the law and for the faith, and the same letters borrowed to write the "
           "languages people actually speak",
           "Ajami script"),
    script("EAF", 700, None, "Ge'ez for the highlands, Arabic on the coast",
           "the old Ge'ez letters inland, and Arabic along the trading coast",
           "the highlands keep the old Ge'ez letters while the coast writes Arabic: which one "
           "you get depends on how far you are from the sea",
           "Ge'ez script; Arabic script"),
    script("MSA", None, 1500, "nothing written",
           "memory, and the marks on the land",
           "nothing is written here; what is known is remembered and told",
           "History of writing"),
    script("MSA", 1500, None, "the Latin alphabet",
           "the Latin alphabet, brought by the missions and the colonial administration",
           "the signs are in the Latin alphabet, brought by the missions and the administration",
           "Latin alphabet"),

    # ---- Oceania -----------------------------------------------------------------------------
    script("AUS", None, 1788, "nothing written",
           "nothing written: the country is read, not written on",
           "nothing is written. The country is read, not written on, and the map is sung",
           "History of writing; Songline"),
    script("AUS", 1788, None, "the Latin alphabet",
           "the Latin alphabet",
           "the signs are in the Latin alphabet", "Latin alphabet"),
    script("PAC", None, 1810, "nothing written",
           "memory, and the knots and notched sticks",
           "nothing is written: the record is in memory, in knots, and in notched sticks",
           "History of writing"),
    script("PAC", 1810, None, "the Latin alphabet",
           "the Latin alphabet, brought by the missionaries and written down by them first",
           "the signs are in the Latin alphabet, and the missionaries wrote the language down "
           "before they taught anyone to read it",
           "Latin alphabet"),
]

# ===============================================================================================
# The kinds of sign. `needs` names a technology that must have arrived; `literacy` is the share
# of people who would have to be able to read for this sign to be worth putting up.
# ===============================================================================================

SIGNS: List[Dict[str, Any]] = [
    sign("edict", "the edict cut in the rock",
         "the ruler's own words cut deep into a cliff or a pillar, where nobody can take them down",
         "the rock itself carries the ruler's words, cut deep enough that no man could take them "
         "down, and set where the road goes past",
         "Edicts of Ashoka; Behistun Inscription", start=-3000, end=1500, literacy=0.0),

    sign("boundary", "the boundary stone",
         "a stone at the corner of a field or a province, with the names cut into it and a curse "
         "on anyone who moves it",
         "a stone stands at the corner with the names cut into it, and a curse on any man who "
         "moves it",
         "Boundary stone; Kudurru", start=-3000, literacy=0.0),

    sign("temple_inscription", "the inscription on the temple",
         "the name of the god, the name of the king who built it, and what it cost",
         "the temple wall carries the god's name, the king's, and what the building cost",
         "Temple inscription; Building inscription", start=-3000, literacy=0.0),

    sign("grave", "the cut stone at the grave",
         "a name, two dates, and often a curse on anyone who disturbs the grave",
         "the stone at the grave gives a name and two dates, and often a curse on whoever "
         "disturbs it",
         "Epitaph", start=-3000, literacy=0.0),

    sign("milestone", "the milestone",
         "a stone pillar at the side of the road giving the distance to the next town and the "
         "name of the man who had the road made",
         "a pillar stands at the roadside giving the distance to the next town and the name of "
         "the man who had the road made",
         "Milestone; Roman milestones", start=-300, end=1900, areas=["EUR", "EEU", "WAS", "NAF"],
         literacy=0.0),

    sign("graffiti", "the graffiti",
         "names, boasts, prices and insults scratched into plaster by people with nothing better "
         "to do",
         "the plaster is scratched with names, boasts, prices and insults, cut by people with "
         "nothing better to do and no thought of being remembered",
         "Graffiti; Pompeii", start=-300, literacy=0.05),

    sign("shop_sign", "the sign over the shop",
         "a painted board, or a thing hung out: a boot, a key, a pretzel, three balls",
         "the shop has a board hung out over the door, painted with the trade or with a thing "
         "that stands for it, so that a man who cannot read still knows what is sold here",
         "Shop sign; Signage", start=1100, literacy=0.05),

    sign("notice", "the posted notice",
         "a sheet nailed to a door or a wall: an auction, a law, a conscription, a ship's sailing",
         "a sheet is nailed up where people pass: an auction, a new law, a ship's sailing, or the "
         "names of the men who must serve",
         "Poster; Public notice", start=1500, literacy=0.1, needs=["paper"]),

    sign("street_name", "the street name at the corner",
         "the name of the street, on a plate at the corner, so a stranger can find an address",
         "the corner carries the name of the street on a plate, which only matters once "
         "strangers are expected to find an address",
         "Street name sign", start=1700, literacy=0.2),

    sign("road_sign", "the road sign",
         "a plate on a post telling you where the road goes and how fast you may take it",
         "a plate on a post tells you where the road goes and what you may do on it",
         "Traffic sign", start=1900, literacy=0.3),

    sign("official_bilingual", "the official notice in two scripts",
         "the same notice twice, in the script of the government and in the script of the people",
         "the notice is written twice, once in the government's script and once in the people's, "
         "and you can tell which is which by which one is worn",
         "Bilingual sign; Language policy", start=1900, literacy=0.3),
]


def all_scripts() -> List[Dict[str, Any]]:
    return SCRIPTS


def all_signs() -> List[Dict[str, Any]]:
    return SIGNS


if __name__ == "__main__":
    print("scripts: %d rows over %d areas" % (len(SCRIPTS), len({s["area"] for s in SCRIPTS})))
    print("signs:   %d kinds" % len(SIGNS))
