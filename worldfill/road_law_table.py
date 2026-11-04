"""
Step 46 part 5 (E10 B): the law of the road — who may use it, and on what terms.

A road is not a right of way. Almost every road in history has had somebody standing on it
deciding who may pass, what it costs, what may be carried, which way to keep, and how fast a
vehicle may go — and those rules changed what a road *was*.

**This fills kind 7 of `history/law.json.gz`**, next to step 45's weapon laws in kind 5. The same
rules apply as there, and for the same reason: **a law of the road is a law about a class of
person or a class of vehicle.** The Qin axle standard is not about carts, it is about every
cart having to be the same. The Rhine tolls are not about boats, they are about who may tax a
boat. The red flag is not about speed, it is about a man being required to walk in front of your
machine.

**The shapes**, which are this kind's own and not the weapon kind's:

| shape | meaning | example |
|---|---|---|
| `closed` | the way is shut to some class | the cursus publicus: no warrant, no horses |
| `toll` | passage is bought | the Rhine, per castle, per league |
| `forced` | you cannot pass *through* without selling | the staple right of Cologne |
| `gauge` | your vehicle must be a standard size | Qin: the axle of one length |
| `side` | which side of the road | Britain, 1835 |
| `speed` | how fast, or how loud | the red flag, 1865 |
| `hours` | when vehicles may move at all | Rome: no carts by day |
| `labour` | who must maintain it | six days' statute labour, 1555 |
| `ban` | a vehicle is not admitted | sedan chairs barred to merchants |

Every row names its source. None of them is a number the mod needs; they are all facts about what
a road was for.
"""

SHAPES = ["closed", "toll", "forced", "gauge", "side", "speed", "hours", "labour", "ban"]

#   where    the jurisdiction as the ruler register names it (year-aware join, so "Roman Empire"
#            rather than "Italy" for a Roman law)
#   year     when it was made
#   to       the last year it held, or None while it runs on
#   shape    one of SHAPES
#   who      the class it singles out, or None for everyone
#   text     what the law says
#   note     what it meant
#   source   where it came from

ROAD_LAWS = [
    # ------------------------------------------------------------------ ROME
    dict(where="Roman Empire", year=-20, to=None, shape="closed",
         who="anyone without a warrant from the emperor",
         text="the cursus publicus, the state post, might be used only by holders of a diploma, "
              "and a man caught using the relay horses without one was fined and his animals "
              "seized",
         note="**The first great road system in the world was also the first great road "
              "restriction.** The cursus publicus was a courier service, not a public highway: "
              "Augustus built the relay stations, the *mansiones* and *mutationes*, and the "
              "Theodosian Code spends a whole title (CTh 8.5) on prosecuting people who take "
              "the horses anyway, which tells you how many did. A road you may walk on and may "
              "not ride is the ordinary condition of most roads in history.",
         source="Wikipedia, Cursus publicus; Theodosian Code 8.5"),
    dict(where="Roman Republic", year=-45, to=None, shape="hours",
         who="ordinary wheeled traffic during the day",
         text="no wheeled vehicle might be driven in the streets of Rome between sunrise and "
              "the tenth hour, save for building materials for a temple and the transport of "
              "the Vestals",
         note="**Rome banned carts from its own streets in daylight, and the exemption list is "
              "the interesting part.** The Lex Julia Municipalis, known from the Tabula "
              "Heracleensis, keeps the day clear for people, keeps the exemption for sacred "
              "building work and the Vestals, and pushes all the freight into the night — which "
              "is why Juvenal complains that he cannot sleep for the noise of the wagons.",
         source="Wikipedia, Tabula Heracleensis; Lex Julia municipalis"),
    dict(where="Roman Empire", year=-17, to=None, shape="gauge",
         who="every cart on the roads",
         text="the track of a wagon is a public matter: ruts are cut to a gauge and a cart whose "
              "wheels do not fit them cannot use the road",
         note="Ruts of **1.32 to 1.47 m** survive at Pompeii, which is a narrow range and means "
              "the carts that went through the gate fitted it. **The claim that this is the "
              "ancestor of standard gauge is a myth** and this register does not repeat it: "
              "Stephenson's 1,435 mm has no Roman parent. What is true is that a rutted road "
              "imposes a gauge on anyone who uses it, whoever set it.",
         source="PLOS ONE 2020, Using city gates as a means of estimating ancient traffic flows"),

    # ------------------------------------------------------------------ CHINA
    dict(where="Qin dynasty", year=-221, to=None, shape="gauge",
         who="every vehicle in the empire",
         text="the axle-length of carts is fixed to one standard throughout the empire, so that "
              "every cart runs in the ruts of every road",
         note="**車同軌, 'the same track for the carts'**, is one of the three standardisations "
              "the First Emperor's inscriptions claim for themselves, beside the same script and "
              "the same weights. It is the only ancient gauge law we can name a ruler for. The "
              "point is not uniformity for its own sake: a wagon from one commandery had to be "
              "able to use the road through the next.",
         source="Wikipedia, Qin dynasty; Shiji, Annals of the First Emperor"),
    dict(where="Ming dynasty", year=1368, to=None, shape="ban",
         who="merchants",
         text="merchants may not travel in sedan chairs and may not ride horses; only officials "
              "of rank and their families may be carried",
         note="A vehicle law as a class marker. The sedan chair with its bearers is the clearest "
              "example in history of transport being rationed by status rather than by price: "
              "**the Qing regulations fixed not only who might be carried but how many men might "
              "carry him** — two for a low official, four for a high one, eight for the "
              "emperor.",
         source="Wikipedia, Sedan chair; Sumptuary law"),

    # ------------------------------------------------------------------ ISLAMIC WORLD AND INDIA
    dict(where="Mughal Empire", year=1556, to=None, shape="ban",
         who="ordinary travellers",
         text="the sadak, the royal road, is built and held for the movement of the court, the "
              "army and the post, and the kos minar mark each kos for the courier",
         note="**The Grand Trunk Road is not one road but a succession of regimes each "
              "maintaining it for its own purpose**, and the kos minar — the stone markers every "
              "kos, about two miles — are the surviving evidence of a road governed in units of "
              "courier time rather than distance. The road is public; its upkeep, its tolls and "
              "its military use are the state's.",
         source="Wikipedia, Grand Trunk Road; Kos minar"),

    # ------------------------------------------------------------------ THE STAPLE RIGHT
    dict(where="Holy Roman Empire", year=1259, to=1794, shape="forced",
         who="every merchant passing through Cologne",
         text="goods passing through the city must be unloaded and offered for sale in its market "
              "for three days before they may be carried on",
         note="**The staple right, *Stapelrecht*, is the strangest law of the road there ever "
              "was: you could be forbidden to pass.** Cologne held it from 1259, and the right "
              "was worth so much that towns fought for it and emperors sold it. It is why the "
              "Rhine's trade was routed through a handful of privileged towns, and why the "
              "French Revolution's abolition of it in 1790 did more for German commerce than any "
              "road ever built.",
         source="Wikipedia, Staple right; Emigration: The Staple Right of Cologne"),
    dict(where="Holy Roman Empire", year=1250, to=1815, shape="toll",
         who="every boat on the Rhine",
         text="a toll is levied at each castle and each town along the river, for each boat and "
              "each cargo, by whoever holds the bank",
         note="**The Rhine had so many tolls that a cargo could be taxed a dozen times between "
              "Basel and the sea** — the 'robber barons' of the Rhine were not robbers, they "
              "held a legal right, and the toll stations at Kaub, Bingen, Koblenz and St. Goar "
              "are still standing. The Congress of Vienna made the river free in 1815 (Article "
              "109) and the Mainz Convention of 1831 made it work.",
         source="Wikipedia, Rhine; Congress of Vienna, Article 109; Mainz Convention 1831"),

    # ------------------------------------------------------------------ ENGLAND
    dict(where="Kingdom of England", year=1555, to=1835, shape="labour",
         who="every householder in the parish",
         text="every person keeping a plough is to labour six days a year on the highways of the "
              "parish, with his cart, horses and men, under the surveyor of highways",
         note="**The roads were maintained by a forced levy of unpaid labour, and that is why "
              "they were bad.** The statute-labour system (2 & 3 Philip and Mary c.8) set six "
              "days a year, unpaid, and grew no better for two centuries; the turnpikes existed "
              "because statute labour could not keep a road fit for wheels.",
         source="Wikipedia, Statute labour; Highways Act 1555"),
    dict(where="Kingdom of England", year=1663, to=1880, shape="toll",
         who="every traveller with a cart or a horse",
         text="a turnpike trust may erect a gate and take a toll from every vehicle that passes, "
              "and spend the money on the road it gates",
         note="**The first turnpike gate in England was at Wadesmill in Hertfordshire in 1663** "
              "and by the 1830s there were over **1,000 trusts, 30,000 miles of road and 8,000 "
              "gates** taking tolls on almost every main road in the country. The toll is the "
              "reason a road could be kept fit for a coach, and the reason a village could be cut "
              "off by the price of passing.",
         source="Wikipedia, Turnpike trust; Bogart, The Turnpike Roads of England and Wales"),
    dict(where="Kingdom of England", year=1530, to=None, shape="labour",
         who="every parish",
         text="pontage and pavage grants: a toll may be taken at a bridge or a street for a term "
              "of years, on condition that the money repairs it",
         note="**A toll for a bridge is the oldest road charge in England**, and the grant is "
              "usually specific: the Marlow toll was a penny for a cart and a farthing for a "
              "horse-load over five shillings in value. The distinction matters because bridge "
              "tolls outlived road tolls by centuries.",
         source="Journal of Mediaeval Studies, Inland Transportation in England"),
    dict(where="United Kingdom", year=1835, to=None, shape="side",
         who="every driver",
         text="a driver shall keep to the left of the road on meeting another carriage",
         note="**The first statute to put keep-left on the books, and Britain has never repealed "
              "it.** Most of Europe drove to the left too until the French Revolution, when "
              "France moved to the right in 1794 and then made it general under Napoleon; the "
              "countries France conquered changed with it and the ones that fought France did "
              "not. **Sweden drove on the left until 3 September 1967**, when the whole country "
              "switched sides in one morning.",
         source="Wikipedia, Left- and right-hand traffic; Highway Act 1835"),
    dict(where="United Kingdom", year=1865, to=1896, shape="speed",
         who="everyone driving a self-propelled vehicle",
         text="a locomotive on a highway must not exceed two miles an hour in a town or four in "
              "the country, and a man on foot carrying a red flag must walk sixty yards ahead of "
              "it",
         note="**The Red Flag Act, and the only speed law whose purpose was to make a vehicle "
              "useless.** It was passed for the safety of horses and the convenience of the "
              "turnpike trusts and the railways, and it held British motoring back for thirty "
              "years: repealed in 1896 by the Locomotives on Highways Act, which raised the limit "
              "to 14 mph and was celebrated by a run to Brighton.",
         source="Wikipedia, Locomotive Act 1865; Locomotives on Highways Act 1896"),

    # ------------------------------------------------------------------ THE SEA
    dict(where="Kingdom of England", year=1651, to=1849, shape="closed",
         who="foreign ships",
         text="goods may be imported into England or its colonies only in English ships, "
              "commanded by Englishmen and manned mostly by Englishmen",
         note="**The Navigation Acts are a law of the sea route, not of the road**, and they are "
              "the clearest case of a government deciding which carrier may use a route: the "
              "cargo is legal, the ship is not. They were repealed in 1849. The same instrument, "
              "in the opposite direction, is *cabotage* — the reservation of a country's own "
              "coastal trade to its own flag — which most of the world still has.",
         source="Wikipedia, Navigation Acts"),
    dict(where="French First Republic", year=1790, to=None, shape="toll",
         who="everyone using an internal waterway",
         text="the staple rights and the internal tolls on rivers are abolished, and a cargo may "
              "pass from one end of the country to the other without being unloaded",
         note="**The single largest repeal of a law of the road in history.** The decree of 1790 "
              "abolished the *droit d'étape* and the internal tolls at a stroke, and the "
              "measurement of the effect is one of the few places where the economics of "
              "transport can be seen changing a country: freight costs fell, and the price of "
              "grain converged across France.",
         source="Wikipedia, Droit d'étape; Allarde decree 1791"),

    # ------------------------------------------------------------------ THE MODERN ROAD
    dict(where="United Kingdom", year=1861, to=None, shape="speed",
         who="every carrier",
         text="no locomotive may travel on a turnpike road at more than ten miles an hour, and no "
              "vehicle may exceed twelve miles an hour on any road",
         note="The Locomotive Act 1861 raised the red-flag limit and lowered the general one, "
              "which is the ordinary shape of early vehicle law: **the new machine is regulated "
              "at the speed of the old one.**",
         source="Wikipedia, Locomotive Acts"),
    dict(where="United States", year=1901, to=None, shape="speed",
         who="every motor vehicle in Connecticut",
         text="no motor vehicle may be driven at more than twelve miles an hour within a city or "
              "twenty outside it, and shall slow to eight at a crossing",
         note="**Connecticut passed the first speed law for motor cars in the United States in "
              "1901**, and the pattern of the numbers — about twice a horse's pace — is the same "
              "everywhere the motor car arrived.",
         source="Wikipedia, Speed limit; Connecticut motor vehicle law 1901"),
    dict(where="United States", year=1916, to=None, shape="gauge",
         who="states without matching standards",
         text="federal money for roads is granted only to states that maintain a highway "
              "department and match the funds",
         note="**The Federal Aid Road Act of 1916** is the moment the road became a national "
              "instrument rather than a local one: Washington pays, so Washington sets the "
              "standard. Every country's trunk road system begins with a law of this shape.",
         source="Wikipedia, Federal Aid Road Act of 1916"),

    # ------------------------------------------------------------------ THE REST OF THE WORLD
    dict(where="Inca Empire", year=1450, to=1533, shape="closed",
         who="everyone but the state",
         text="the royal road, the Qhapaq Nan, is held for the runners and the army; no one else "
              "travels it without a warrant, and the chasqui relays a message two hundred "
              "kilometres in a day",
         note="**The greatest road system in the Americas was a state instrument and not a "
              "public one** — some 40,000 km of it, with suspension bridges and stairways cut "
              "into the mountainsides, and it carried quipu and orders and the armies of the "
              "Sapa Inca. What it did not carry was merchants, because the Inca had no market "
              "economy to carry. A road can exist for reasons that have nothing to do with trade.",
         source="Wikipedia, Inca road system; Qhapaq Nan"),
    dict(where="Tokugawa shogunate", year=1603, to=1868, shape="closed",
         who="everyone without a pass",
         text="travel on the five highways is barred at the sekisho checkpoints, and a traveller "
              "without a permit is turned back",
         note="**Japan controlled movement on its roads rather than movement of its goods.** The "
              "sekisho at Hakone and Arai checked travellers, and the design was aimed at one "
              "thing above all: keeping the daimyo's wives and children in Edo as hostages, which "
              "is what the sankin-kotai system of alternate attendance was for. The checkpoints "
              "fell in 1868.",
         source="Wikipedia, Sekisho; Sankin-kotai"),
    dict(where="Ottoman Empire", year=1500, to=None, shape="labour",
         who="the villages along each route",
         text="the menzilhane, the post station, is kept by the villages on the route, which owe "
              "the horses, the food and the labour of the courier road",
         note="**The Ottoman post was a tax on the countryside.** A *menzilhane* was a relay "
              "station every few hours on the military roads, and the villages within reach of "
              "one were assessed for its upkeep — the same instrument as England's statute "
              "labour, on a road built for the sultan's orders rather than the parish's carts.",
         source="Wikipedia, Menzilhane; Ottoman postal system"),
    dict(where="Kingdom of France", year=1738, to=1789, shape="labour",
         who="every parish on the route",
         text="the corvee royale: the inhabitants of each parish must labour unpaid on the royal "
              "roads, for as many days as the intendant sets",
         note="**The corvée was the most hated law in pre-revolutionary France** and the first "
              "thing the Revolution abolished, in 1789. It is the same instrument as England's "
              "six days a year, but assessed at the intendant's discretion rather than fixed, "
              "which is what made it intolerable — and Trudaine's roads, built with it, were the "
              "best in Europe.",
         source="Wikipedia, Corvee; Ponts et Chaussees"),
]


def problems():
    """Everything that would make the table wrong."""
    bad = []
    for r in ROAD_LAWS:
        if r["shape"] not in SHAPES:
            bad.append("%s %d: unknown shape %s" % (r["where"], r["year"], r["shape"]))
        if not r["text"] or not r["note"] or not r["source"]:
            bad.append("%s %d: a row with no text, note or source" % (r["where"], r["year"]))
        if r["to"] is not None and r["to"] < r["year"]:
            bad.append("%s %d: ends before it begins" % (r["where"], r["year"]))
        if r["shape"] == "toll" and "toll" not in (r["text"] + r["note"]).lower():
            bad.append("%s %d: a toll row that does not mention a toll"
                       % (r["where"], r["year"]))
        if r["shape"] in ("closed", "ban") and not r["who"]:
            bad.append("%s %d: a closed road that names nobody shut out"
                       % (r["where"], r["year"]))
    # The table must cover more than one part of the world and more than one era.
    places = {r["where"] for r in ROAD_LAWS}
    if len(places) < 8:
        bad.append("only %d jurisdictions: the law of the road is not one country's" % len(places))
    if max(r["year"] for r in ROAD_LAWS) - min(r["year"] for r in ROAD_LAWS) < 2000:
        bad.append("the table spans less than 2,000 years")
    for s in SHAPES:
        if not any(r["shape"] == s for r in ROAD_LAWS):
            bad.append("no row uses the shape %s, so it is a shape the register claims and "
                       "cannot show" % s)
    return bad


if __name__ == "__main__":
    p = problems()
    print("road laws: %d rows over %d jurisdictions, %d shapes"
          % (len(ROAD_LAWS), len({r["where"] for r in ROAD_LAWS}),
             len({r["shape"] for r in ROAD_LAWS})))
    for r in ROAD_LAWS:
        span = "%d" % r["year"] if r["to"] is None else "%d-%d" % (r["year"], r["to"])
        print("  %-22s %-14s %-8s %s" % (r["where"][:22], span, r["shape"], r["text"][:60]))
    for b in p:
        print("  PROBLEM " + b)
    print("road_law_table: %d problem(s)" % len(p))
