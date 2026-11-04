"""Step 38 (C7): migrations and refugees — dated, placed, and given a route.

Why this file exists
--------------------
`MigrationSystem` computes push and pull between two regions and returns a flow in people per
year. It has no distance, no route, and no history: it cannot tell you that in August 1947 the
road from Amritsar to Lahore carried the largest movement of people in the history of the world,
because it does not know that road, or that August, or anybody's name.

This is the table of migrations that actually happened, as records rather than as a formula.

The shape of a record
---------------------
Every row is one movement of people on one route: where they left, where they arrived, in what
year, how many, whether anybody made them go, and what kind of going it was. The register then
asks the news-travel model how long that journey took, so a route is not just a line on a map but
a number of days.

    flight        running from violence
    expulsion     turned out by decree
    transfer      agreed between two states and written into a treaty
    deportation   moved by force to a place chosen for them
    trade         sold and shipped
    indenture     contracted, and often not much better
    famine        leaving because staying is not survivable
    economic      going where the work is
    conquest      moving with an army
    settlement    slow, over centuries, and nobody wrote it down at the time

Rules for a row
---------------
1. No source, no row.
2. `people` is the published figure for this route. Where a migration's total is well known but
   this route is only part of it, the note says which is which.
3. `sea` is whether the route is a sea route, so the travel model is asked the right question.
4. Rows are dated records, not a continuous field. A place in a year with no record is not a
   place with no migration — it is a place whose migration nobody counted, and the mod says so.
"""

RECORDED = "recorded"
MIXED = "mixed"
ESTIMATED = "estimated"
MARKS = (RECORDED, MIXED, ESTIMATED)

KINDS = ("flight", "expulsion", "transfer", "deportation", "trade", "indenture", "famine",
         "economic", "conquest", "settlement")

PARTITION = "English Wikipedia, 'Partition of India'"
SLAVE = ("Voyages: The Trans-Atlantic Slave Trade Database; English Wikipedia, 'Atlantic slave "
         "trade'")
UNHCR = "UNHCR"


class M:
    """One migration: who left, where from, where to, when, how many, and whether they had a say."""

    __slots__ = ("id", "name", "flat", "flon", "fname", "tlat", "tlon", "tname", "year", "end",
                 "people", "kind", "forced", "sea", "mark", "note", "src")

    def __init__(self, id, name, flat, flon, fname, tlat, tlon, tname, year, end, people, kind,
                 forced, sea, mark, note, src):
        assert src, "every row needs a source: " + id
        assert end is None or year <= end, "ends before it starts: " + id
        assert mark in MARKS, "unknown mark %r in %s" % (mark, id)
        assert kind in KINDS, "unknown kind %r in %s" % (kind, id)
        assert people > 0, "no people in " + id
        for v, what in ((flat, "lat"), (tlat, "lat")):
            assert -90 <= v <= 90, "bad %s in %s" % (what, id)
        for v, what in ((flon, "lon"), (tlon, "lon")):
            assert -180 <= v <= 180, "bad %s in %s" % (what, id)
        assert fname and tname, "a route needs two ends: " + id
        self.id = id
        self.name = name
        self.flat = flat
        self.flon = flon
        self.fname = fname
        self.tlat = tlat
        self.tlon = tlon
        self.tname = tname
        self.year = year
        self.end = end
        self.people = people
        self.kind = kind
        self.forced = forced
        self.sea = sea
        self.mark = mark
        self.note = note
        self.src = src


MIGRATIONS = [

    # ------------------------------------------------------------------ the Partition, 1947
    M("partition_punjab_east", "the Partition: Hindus and Sikhs leave West Punjab",
      31.55, 74.34, "Lahore", 31.63, 74.87, "Amritsar", 1947, 1951, 5500000, "flight", True,
      False, RECORDED,
      "The largest mass migration in the history of the world, and this is half of it. In Punjab "
      "alone more than **twelve million** were displaced, roughly **5.5 million** of them Hindus "
      "and Sikhs going east into India and **6.5 million** Muslims going west into Pakistan. The "
      "migration was over within three months in the Punjab. Between **200,000 and two million** "
      "died. The Radcliffe Line was drawn by a man who had never been to India and was published "
      "two days after independence.",
      PARTITION),

    M("partition_punjab_west", "the Partition: Muslims leave East Punjab",
      31.63, 74.87, "Amritsar", 31.55, 74.34, "Lahore", 1947, 1951, 6500000, "flight", True,
      False, RECORDED,
      "The other half of the Punjab exchange, and the larger. Whole villages walked out together "
      "in columns miles long; the trains that carried some of them arrived full of corpses. The "
      "1951 Pakistani census counted **7,226,600** displaced people in Pakistan, and the 1951 "
      "Indian census **7,295,870** in India.",
      PARTITION),

    M("partition_bengal", "the Partition: Hindus leave East Bengal",
      23.81, 90.41, "Dhaka", 22.57, 88.36, "Kolkata", 1947, 1951, 2500000, "flight", True,
      False, MIXED,
      "Bengal moved differently from the Punjab: not all at once in three months, but "
      "intermittently, during every period of communal tension, for decades afterwards. The "
      "figure here is the 1947-51 movement; the flight from East Bengal to West Bengal carried "
      "on through to 1971 and beyond. Marked mixed, because no census cleanly separates the "
      "first wave from the rest.",
      PARTITION + "; English Wikipedia, 'Partition of Bengal'"),

    M("partition_sindh", "the Partition: Sindhi Hindus leave for India",
      24.86, 67.01, "Karachi", 28.61, 77.21, "Delhi", 1947, 1951, 1200000, "flight", True,
      False, MIXED,
      "Sindh's Hindus left almost in their entirety, and unlike the Punjabis they had no "
      "contiguous Indian territory to walk into: they went by sea and by train to Bombay, Delhi "
      "and the refugee colonies of Gujarat. A people who had lived in the Indus valley for "
      "millennia and had no province of their own to go to.",
      PARTITION + "; English Wikipedia, 'Partition of India'"),

    # ------------------------------------------------------------------ South Asia since
    M("bengal_liberation_1971", "the Bangladesh Liberation War",
      23.81, 90.41, "Dhaka", 22.57, 88.36, "Kolkata", 1971, 1972, 10000000, "flight", True,
      False, RECORDED,
      "**Ten million** people fled East Pakistan into India in about nine months — the largest "
      "refugee flight of the second half of the twentieth century, and one of the fastest. Most "
      "walked. India went to war in December, and by the end of the year Bangladesh existed.",
      "English Wikipedia, 'Bangladesh Liberation War' and 'Bangladeshi refugees'"),

    M("afghan_refugees", "the Soviet war in Afghanistan",
      34.53, 69.17, "Kabul", 34.00, 71.58, "Peshawar", 1979, 1996, 6000000, "flight", True,
      False, RECORDED,
      "At its height the largest single refugee population in the world: about **six million** "
      "Afghans, a third of the country, mainly in Pakistan and Iran, and mainly for more than one "
      "generation. Children were born in the camps and grew up and had children in the camps.",
      "UNHCR; English Wikipedia, 'Afghan refugees'"),

    # ------------------------------------------------------------------ the Ottoman settlement
    M("greek_turkish_exchange", "the exchange of Greek and Turkish populations",
      38.42, 27.14, "Izmir", 37.98, 23.73, "Athens", 1923, 1925, 1200000, "transfer", True,
      True, RECORDED,
      "The **Convention Concerning the Exchange of Greek and Turkish Populations**, signed at "
      "Lausanne on 30 January 1923, moved about **1.2 million** Greek Orthodox Christians out of "
      "Turkey and some **350,000 to 400,000** Muslims out of Greece — by religion, not by "
      "language, and not by consent; the Greeks of Crete and the Turkish-speaking Orthodox of "
      "Cappadocia went alike. It raised Greece's population by a fifth. This is the first mass "
      "expulsion agreed between two sovereign states, and the 'Lausanne principle' it established "
      "was in everybody's mind in 1947.",
      "English Wikipedia, 'Population exchange between Greece and Turkey' and 'Treaty of "
      "Lausanne'"),

    M("turkish_exchange_reverse", "the exchange: Muslims leave Greece",
      40.64, 22.94, "Thessaloniki", 38.42, 27.14, "Izmir", 1923, 1925, 400000, "transfer", True,
      True, RECORDED,
      "The other direction of the same treaty. The Muslims of Greek Macedonia and Crete went to "
      "Smyrna and the Aegean coast, into houses whose owners had just been put on ships going the "
      "other way.",
      "English Wikipedia, 'Population exchange between Greece and Turkey'"),

    M("armenian_deportation", "the Armenian deportations",
      38.50, 43.38, "Van", 35.34, 40.14, "Deir ez-Zor", 1915, 1917, 1000000, "deportation", True,
      False, RECORDED,
      "The death marches into the Syrian desert. **Between 600,000 and 1.5 million** Armenians "
      "were killed; the figure here is the order of those driven out of the Armenian highlands "
      "towards Deir ez-Zor, most of whom did not arrive. This row is in a table of migrations "
      "because that is what it was called at the time, and because the euphemism is the point.",
      "English Wikipedia, 'Armenian genocide' and 'Deir ez-Zor camps'"),

    # ------------------------------------------------------------------ Europe in the twentieth century
    M("german_expulsions", "the expulsion of the Germans from the east",
      51.11, 17.04, "Wroclaw", 52.38, 9.73, "Hannover", 1945, 1950, 7000000, "expulsion", True,
      False, RECORDED,
      "**Between twelve and fourteen million** ethnic Germans were driven out of Poland, "
      "Czechoslovakia, Hungary and the rest of eastern Europe after the war, in the largest "
      "forced transfer in European history; the figure here is the Silesian and Pomeranian part "
      "of it. Endorsed at Potsdam by three governments who called it 'transfer' and asked for it "
      "to be done 'in an orderly and humane manner'.",
      "English Wikipedia, 'Flight and expulsion of Germans from Poland during and after World "
      "War II' and 'Population transfer'"),

    M("sudeten_expulsion", "the Sudeten Germans are driven out of Bohemia",
      50.08, 14.44, "Prague", 48.14, 11.58, "Munich", 1945, 1947, 3000000, "expulsion", True,
      False, RECORDED,
      "About **three million** from the Sudetenland alone. Note the date: this is the same "
      "population whose presence had been the pretext for the crisis of 1938, seven years "
      "earlier.",
      "English Wikipedia, 'Expulsion of Germans from Czechoslovakia'"),

    M("polish_transfer", "Poland moves west",
      49.84, 24.03, "Lviv", 51.11, 17.04, "Wroclaw", 1944, 1946, 1500000, "transfer", True,
      False, RECORDED,
      "Poland's borders shifted two hundred miles west, and the people went with them: Poles "
      "expelled from the east, resettled in the German houses of Silesia and Pomerania whose "
      "owners were being expelled at the same time. A whole country walked the same two hundred "
      "miles in opposite directions.",
      "English Wikipedia, 'Population transfer' and 'Recovered Territories'"),

    M("bosnian_displacement", "the Bosnian war",
      44.11, 19.30, "Srebrenica", 44.54, 18.68, "Tuzla", 1992, 1995, 2200000, "flight", True,
      False, RECORDED,
      "More than **two million** displaced out of a country of four and a half million — half of "
      "Bosnia. The term 'ethnic cleansing' entered English during this war, and it means what "
      "this row means.",
      "UNHCR; English Wikipedia, 'Bosnian War' and 'Ethnic cleansing'"),

    # ------------------------------------------------------------------ the diasporas of empire
    M("atlantic_slave_trade_brazil", "the Atlantic slave trade: to Brazil",
      6.52, 3.38, "Lagos", -12.97, -38.50, "Salvador", 1517, 1867, 4900000, "trade", True,
      True, RECORDED,
      "The largest forced migration in the history of the ocean. In 366 years the slaving vessels "
      "embarked about **12.5 million** captives in Africa and landed **10.7 million** in the New "
      "World; the Middle Passage itself took more than **1.8 million** lives. Brazil took the "
      "largest single share, about **4.9 million**, which is the figure here. To put this row "
      "in a table of "
      "migrations at all is to accept a euphemism, and the register should not let a player "
      "read the number without the word *captives*.",
      SLAVE),

    M("atlantic_slave_trade_caribbean", "the Atlantic slave trade: to the islands and Spanish America",
      5.08, -1.35, "Elmina", 18.54, -72.34, "Port-au-Prince", 1517, 1867, 5300000, "trade", True,
      True, RECORDED,
      "The sugar islands and the Spanish mainland together took about **5.3 million**, a little "
      "more than Brazil. Chronic negative population growth on the plantations meant the traffic "
      "never slackened: more arrivals simply replaced more deaths, and Saint-Domingue alone took "
      "more enslaved Africans than the whole of North America. The three rows in this table add "
      "to the **10.7 million** the Slave Voyages database says were landed.",
      SLAVE),

    M("atlantic_slave_trade_north", "the Atlantic slave trade: to North America",
      6.52, 3.38, "Lagos", 32.78, -79.93, "Charleston", 1517, 1808, 500000, "trade", True,
      True, RECORDED,
      "Only about five per cent of the traffic came here directly — about half a million people — "
      "and yet by 1860 their descendants numbered four million, because this was the one place in "
      "the Americas where the enslaved population reproduced itself. The smallest of the three "
      "routes and the one that ended by growing.",
      SLAVE),

    M("indenture_mauritius", "indentured labour: India to Mauritius",
      22.57, 88.36, "Kolkata", -20.16, 57.50, "Port Louis", 1834, 1917, 450000, "indenture", True,
      True, RECORDED,
      "The *girmitiya*: about **1.5 million** Indians went overseas under indenture between 1834 "
      "and 1917, to replace the slave labour that had just been abolished, on contracts that were "
      "in most respects the thing they replaced. Mauritius took the largest single share and is "
      "today the only country in the world with a Hindu majority outside Asia.",
      "English Wikipedia, 'Indian indenture system' and 'Indo-Mauritian'"),

    M("indenture_guyana", "indentured labour: India to British Guiana",
      22.57, 88.36, "Kolkata", 6.80, -58.16, "Georgetown", 1838, 1917, 240000, "indenture", True,
      True, RECORDED,
      "The sugar estates of the Caribbean, worked by Indians shipped eight thousand miles to do "
      "it. Guyana is a little under forty per cent Indo-Guyanese today.",
      "English Wikipedia, 'Indian indenture system' and 'Indo-Guyanese'"),

    M("indenture_fiji", "indentured labour: India to Fiji",
      22.57, 88.36, "Kolkata", -18.14, 178.44, "Suva", 1879, 1916, 60000, "indenture", True,
      True, RECORDED,
      "The smallest and the furthest of the three. Fiji's Indo-Fijians were for most of the "
      "twentieth century a plurality of the population, and the coups of 1987 and 2000 were "
      "largely about that fact.",
      "English Wikipedia, 'Indian indenture system' and 'Indo-Fijians'"),

    M("chinese_coolie_cuba", "the coolie trade: China to Cuba",
      24.48, 118.09, "Xiamen", -23.13, -82.38, "Havana", 1847, 1874, 150000, "indenture", True,
      True, RECORDED,
      "About **a quarter of a million** Chinese labourers were shipped to Cuba and Peru in the "
      "same decades and on the same logic as the Indian indenture system, and with a similar "
      "death rate on the voyage. The word *coolie* is in the register's own name for this kind.",
      "English Wikipedia, 'Coolie' and 'Chinese Cubans'"),

    M("windrush", "the Windrush generation",
      17.97, -76.79, "Kingston", 51.51, -0.13, "London", 1948, 1971, 500000, "economic", False,
      True, RECORDED,
      "They were invited: the British Nationality Act of 1948 gave every subject of the Empire the "
      "right to enter and settle in the United Kingdom, and the *Empire Windrush* docked at "
      "Tilbury in June 1948 with 492 Caribbean passengers. About half a million came from the "
      "Caribbean, and the law that let them in was repealed piecemeal over the next twenty-five "
      "years.",
      "English Wikipedia, 'Windrush generation' and 'British Nationality Act 1948'"),

    M("irish_famine", "the Great Irish Famine",
      51.90, -8.47, "Cork", 40.71, -74.01, "New York", 1845, 1852, 1000000, "famine", True,
      True, RECORDED,
      "A million dead and a million gone, out of eight and a half. The coffin ships to Quebec and "
      "New York carried a third of the passengers who would ever leave Ireland. Note that this "
      "row is marked forced: leaving a country where the potato has failed and the grain is "
      "being exported under guard is not a free choice, whatever the shipping line's advertisement "
      "said.",
      "English Wikipedia, 'Great Famine (Ireland)' and 'Irish diaspora'"),

    M("huguenot_exodus", "the Huguenots leave France",
      46.16, -1.15, "La Rochelle", 52.37, 4.90, "Amsterdam", 1685, 1700, 200000, "expulsion",
      True, False, RECORDED,
      "The Edict of Fontainebleau revoked the Edict of Nantes in October 1685 and made Protestant "
      "worship illegal; about **200,000** of France's 900,000 Protestants left within a few "
      "years, taking the silk and the watchmaking with them to Amsterdam, London, Berlin and the "
      "Cape. France's loss was everybody else's gain, and Colbert knew it and said so.",
      "English Wikipedia, 'Huguenots' and 'Edict of Fontainebleau'"),

    M("morisco_expulsion", "the Moriscos are expelled from Spain",
      39.47, -0.38, "Valencia", 36.81, 10.18, "Tunis", 1609, 1614, 300000, "expulsion", True,
      True, RECORDED,
      "Between 1609 and 1614 the Crown of Castile expelled about **300,000** Moriscos — the "
      "descendants of the Muslims of al-Andalus, four centuries after the fall of Granada, "
      "baptised and legally Christian and expelled all the same. Valencia lost a third of its "
      "people and the silk industry never recovered.",
      "English Wikipedia, 'Expulsion of the Moriscos'"),

    # ------------------------------------------------------------------ the Americas
    M("great_migration_us", "the Great Migration",
      32.30, -90.18, "Jackson", 41.88, -87.63, "Chicago", 1910, 1970, 6000000, "economic", False,
      False, RECORDED,
      "About **six million** Black Americans left the rural South for the cities of the North and "
      "West between 1910 and 1970, the largest internal migration in American history. It was "
      "voluntary and it was not: it was flight from lynching and the convict-lease system as much "
      "as it was pursuit of a wage. Chicago's Black population grew from 44,000 to 813,000.",
      "English Wikipedia, 'Great Migration (African American)'"),

    M("dust_bowl", "the Dust Bowl",
      36.50, -101.00, "the Oklahoma panhandle", 35.37, -119.02, "Bakersfield", 1930, 1940,
      400000, "famine", True, False, MIXED,
      "About **2.5 million** people left the Plains states in the 1930s; of those, somewhere "
      "around **350,000 to 400,000** went to California, and it is the Californian part that is "
      "counted here. They were called 'Okies' whatever state they came from. Marked mixed, "
      "because the larger figure and this route's figure are different things and the sources "
      "disagree about both.",
      "English Wikipedia, 'Dust Bowl' and 'Okie'"),

    M("mexican_repatriation", "the Mexican Repatriation",
      34.05, -118.24, "Los Angeles", 19.43, -99.13, "Mexico City", 1929, 1936, 500000,
      "expulsion", True, False, MIXED,
      "Between **400,000 and two million** people of Mexican descent — a majority of them "
      "American citizens by birth — were removed to Mexico during the Depression, by local "
      "authorities acting without any federal law. The number is genuinely disputed and the range "
      "is wide, so this row is marked mixed and carries the low end.",
      "English Wikipedia, 'Mexican Repatriation'"),

    # ------------------------------------------------------------------ the Middle East and Africa since 1945
    M("nakba", "the Nakba",
      32.79, 34.99, "Haifa", 31.95, 35.93, "Amman", 1948, 1949, 750000, "flight", True,
      False, RECORDED,
      "About **750,000** Palestinians — more than half the Arab population of Mandatory Palestine "
      "— were displaced in 1947-49, and some **500** villages were depopulated. Their descendants "
      "are the largest and oldest refugee population in the world today, and they are still "
      "registered as refugees, because the question of return has never been answered.",
      "UNRWA; English Wikipedia, '1948 Palestinian expulsion and flight'"),

    M("jewish_exodus_iraq", "the Jews of Iraq leave",
      33.31, 44.36, "Baghdad", 32.08, 34.78, "Tel Aviv", 1950, 1952, 123000, "expulsion", True,
      False, RECORDED,
      "Operation Ezra and Nehemiah flew almost the whole of Baghdad's Jewish community — a "
      "community older than Islam and a quarter of the city — to Israel in 1950-51. It is one "
      "part of the wider exodus of about **850,000** Jews from Arab and Muslim countries between "
      "1948 and the 1970s, which is the mirror image of the Nakba and hardly ever mentioned in "
      "the same breath as it.",
      "English Wikipedia, 'Operation Ezra and Nehemiah' and 'Jewish exodus from the Muslim "
      "world'"),

    M("soviet_deportations_1941", "the Volga Germans are deported",
      51.50, 46.12, "Engels", 55.03, 82.92, "Novosibirsk", 1941, 1941, 400000, "deportation",
      True, False, RECORDED,
      "In August and September 1941 the whole Volga German republic — about **400,000** people, "
      "whose families had been invited to Russia by Catherine the Great a century and a half "
      "before — was loaded onto trains for Siberia and Kazakhstan in a matter of weeks. It was "
      "one of a dozen such operations; the Chechens, the Ingush, the Crimean Tatars and the "
      "Kalmyks went in the same years and by the same decree.",
      "English Wikipedia, 'Deportation of the Volga Germans' and 'Population transfer in the "
      "Soviet Union'"),

    M("vietnamese_boat_people", "the Vietnamese boat people",
      10.82, 106.63, "Ho Chi Minh City", 5.62, 103.07, "Pulau Bidong", 1975, 1995, 800000,
      "flight", True, True, RECORDED,
      "About **800,000** people left Vietnam by boat after 1975, and between **200,000 and "
      "400,000** of them did not arrive — to piracy, to storms, to the Gulf of Thailand. The "
      "camps in Malaysia, Hong Kong, Thailand and the Philippines held them for years.",
      "UNHCR; English Wikipedia, 'Vietnamese boat people' and 'Indochina refugee crisis'"),

    M("syrian_refugees", "the Syrian civil war",
      36.20, 37.16, "Aleppo", 37.07, 37.38, "Gaziantep", 2011, None, 3700000, "flight", True,
      False, RECORDED,
      "**About 6.8 million** Syrians are refugees abroad and **6.7 million** more are displaced "
      "inside Syria — more than half the country. The figure here is the Turkish share, which is "
      "the largest single host population in the world. The end year is left open: it has not "
      "ended.",
      UNHCR + "; English Wikipedia, 'Refugees of the Syrian civil war'"),

    M("rwandan_refugees", "the Rwandan genocide and the exodus into Zaire",
      -1.94, 30.06, "Kigali", -1.68, 29.22, "Goma", 1994, 1996, 2000000, "flight", True,
      False, RECORDED,
      "About **two million** Rwandans fled into Zaire and Tanzania in a few weeks in 1994 — the "
      "fastest large refugee flight on record — and the camps that received them became the base "
      "from which the génocidaires continued the war, which is why the camps were later attacked "
      "and the refugees driven on again into the forest.",
      UNHCR + "; English Wikipedia, 'Rwandan genocide' and 'Great Lakes refugee crisis'"),

    # ------------------------------------------------------------------ the deep past
    M("bantu_expansion", "the Bantu expansion",
      5.00, 11.00, "the Benue-Cross rivers", -20.27, 30.93, "Great Zimbabwe", -1000, 1000,
      10000000, "settlement", False, False, ESTIMATED,
      "The largest movement of people in prehistory and the one nobody wrote down: over two "
      "millennia the speakers of Bantu languages spread from the Benue-Cross region over most of "
      "sub-Saharan Africa, carrying cattle, sorghum and iron with them. The number here is the "
      "table's own and is not a migration count at all — there was no census and no route — but "
      "an order of magnitude for the people who were living in the southern half of Africa at "
      "the end of it. Marked estimated.",
      "English Wikipedia, 'Bantu expansion'"),

    M("anglo_saxon_settlement", "the Anglo-Saxon settlement of Britain",
      54.90, 9.50, "Jutland", 51.28, 1.08, "Kent", 400, 650, 200000, "settlement", False, True,
      ESTIMATED,
      "How many came is the most argued-over number in early English history: anywhere from a few "
      "tens of thousands of warriors to a mass folk movement that replaced the population. The "
      "figure here is the table's own, at the high end of the scholarly range, and is marked "
      "estimated. What is not disputed is that within two centuries the language of the island "
      "had changed.",
      "English Wikipedia, 'Anglo-Saxon settlement of Britain'"),

    M("turkic_migration", "the Turkic peoples move west",
      47.00, 92.00, "the Altai", 37.87, 32.48, "Konya", 552, 1100, 1000000, "settlement", False,
      False, ESTIMATED,
      "From the sixth century the Turkic peoples spread out of the Altai, and by the eleventh "
      "they had taken Anatolia — which is Greek today for 'the rising of the sun' and is Turkish "
      "now. The number is the table's own and marked estimated; nobody counted, and the movement "
      "took five hundred years.",
      "English Wikipedia, 'Turkic migration' and 'Seljuk Empire'"),

    M("mongol_expansion", "the Mongol expansion",
      47.20, 102.83, "Karakorum", 39.65, 66.96, "Samarkand", 1206, 1368, 500000, "conquest",
      True, False, ESTIMATED,
      "The conquests moved armies, and armies moved peoples with them: the engineers, the "
      "scribes, the captured craftsmen who were sent east, the garrisons who were sent west and "
      "never came home. Numbers for any of it are guesses. Marked estimated.",
      "English Wikipedia, 'Mongol Empire' and 'Pax Mongolica'"),

    M("mfecane", "the Mfecane",
      -28.88, 31.03, "Zululand", -29.31, 27.48, "Maseru", 1815, 1840, 2000000, "flight", True,
      False, MIXED,
      "The 'crushing': a quarter-century of state formation and warfare across southern Africa "
      "that displaced peoples over a thousand miles, produced the Sotho kingdom in the mountains "
      "of Lesotho and the Ndebele in Zimbabwe, and emptied the highveld. Whether it was caused by "
      "Shaka, by the slave trade at Delagoa Bay, or by drought is still argued, and so is whether "
      "the word 'Mfecane' is the right one. Marked mixed.",
      "English Wikipedia, 'Mfecane'"),
]
