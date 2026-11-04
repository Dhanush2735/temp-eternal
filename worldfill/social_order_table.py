#!/usr/bin/env python3
"""Step 42 part 3 (D7, social order): the table of how a society was divided, by region and era.

Why this is hand-written and not fetched
----------------------------------------

The survey measured it: Wikidata holds 386 caste items and 535 guild items, almost all modern and
almost all European, and nothing that says *what the orders of this place were, in this year*.
There is no table to fetch. So this file is a table this project wrote, from the reference works
named on each row - the same shape as `morale_table.py` for step 40, and held to the same rule:
**every row is estimated and says so**, because the share of a population and the way a man
addresses his better are not things any source states as a number.

What a row has to carry
-----------------------

  * `strata`   - the orders, highest first, each with the share of people in it and a line
  * `guilds`   - whether a craft is held by a guild, and what that means for a player
  * `mobility` - whether a man can leave the order he was born to
  * `speak`    - **who may speak to whom**, which is the half of D7 that is not a list of ranks
  * `caste`    - whether birth fixes it for life, and whether it can be left at all

Coverage
--------

Every point of the map in every year must get an answer, which is why the table ends with
`KINSHIP` (the order of a society before there is a state to divide it) and a `DEFAULT` line for
the places and years no row names. A register that shrugs has failed; this one always answers.

Sources are named per row and are Wikipedia articles unless they say otherwise.
"""

# --------------------------------------------------------------------------- regions (ISO3)

WEST_EUROPE = ["FRA", "ESP", "PRT", "ITA", "DEU", "BEL", "NLD", "LUX", "CHE", "AUT", "GBR", "IRL"]
NORTH_EUROPE = ["SWE", "NOR", "DNK", "FIN", "ISL", "EST", "LVA", "LTU"]
EAST_EUROPE = ["POL", "CZE", "SVK", "HUN", "SVN", "HRV", "ROU", "BGR", "SRB", "MKD", "BIH", "MNE",
               "ALB", "GRC", "UKR", "BLR", "RUS", "MDA"]
BALKANS_BYZANTINE = ["GRC", "BGR", "SRB", "ALB", "MKD", "TUR", "CYP"]
MIDDLE_EAST = ["IRQ", "SYR", "LBN", "JOR", "ISR", "PSE", "SAU", "YEM", "OMN", "ARE", "QAT", "BHR",
               "KWT", "IRN", "TUR", "EGY", "AFG"]
NORTH_AFRICA = ["EGY", "LBY", "TUN", "DZA", "MAR", "SDN", "MRT", "SAH"]
SAHEL_WEST_AFRICA = ["SEN", "GMB", "GNB", "GIN", "MLI", "BFA", "NER", "TCD", "NGA", "GHA", "CIV",
                     "LBR", "SLE", "TGO", "BEN", "CPV", "MRT"]
EAST_AFRICA = ["ETH", "ERI", "SOM", "DJI", "KEN", "UGA", "TZA", "RWA", "BDI", "SSD", "MDG", "MUS",
               "SYC", "COM"]
CENTRAL_SOUTHERN_AFRICA = ["COG", "COD", "CAF", "CMR", "GNQ", "GAB", "AGO", "ZMB", "ZWE", "MWI",
                           "MOZ", "BWA", "NAM", "ZAF", "LSO", "SWZ"]
SOUTH_ASIA = ["IND", "PAK", "BGD", "LKA", "NPL", "BTN", "MDV", "AFG"]
EAST_ASIA = ["CHN", "JPN", "KOR", "PRK", "TWN", "MNG", "HKG", "MAC"]
SOUTHEAST_ASIA = ["VNM", "THA", "KHM", "LAO", "MMR", "MYS", "SGP", "IDN", "PHL", "BRN", "TLS"]
CENTRAL_ASIA = ["KAZ", "UZB", "TKM", "KGZ", "TJK", "AZE", "ARM", "GEO", "MNG", "RUS"]
LATIN_AMERICA = ["MEX", "GTM", "BLZ", "HND", "SLV", "NIC", "CRI", "PAN", "CUB", "HTI", "DOM", "JAM",
                 "PRI", "COL", "VEN", "ECU", "PER", "BOL", "PRY", "BRA", "CHL", "ARG", "URY", "GUY",
                 "SUR"]
NORTH_AMERICA = ["USA", "CAN", "GRL"]
OCEANIA = ["AUS", "NZL", "PNG", "FJI", "SLB", "VUT", "WSM", "TON", "KIR", "TUV", "NRU", "PLW",
           "FSM", "MHL", "NCL", "PYF"]
CARIBBEAN = ["CUB", "HTI", "DOM", "JAM", "PRI", "TTO", "BRB", "BHS", "ATG", "DMA", "GRD", "KNA",
             "LCA", "VCT", "MSR", "CYM", "BMU"]

EUROPE = WEST_EUROPE + NORTH_EUROPE + EAST_EUROPE
ALL = sorted(set(EUROPE + BALKANS_BYZANTINE + MIDDLE_EAST + NORTH_AFRICA + SAHEL_WEST_AFRICA
                 + EAST_AFRICA + CENTRAL_SOUTHERN_AFRICA + SOUTH_ASIA + EAST_ASIA
                 + SOUTHEAST_ASIA + CENTRAL_ASIA + LATIN_AMERICA + NORTH_AMERICA + OCEANIA
                 + CARIBBEAN))


def s(name, who, share, line, may=3):
    """One order of a society. `may` is who this order may address uninvited:

    0 cannot speak to a stranger of rank at all
    1 speaks when spoken to
    2 speaks to their own order and to those beneath
    3 speaks to anyone, and is answered
    """
    return {"name": name, "who": who, "share": share, "line": line, "may": may}


# --------------------------------------------------------------------------- the orders

ORDERS = [
    {
        "id": "kinship",
        "name": "the order of kin",
        "where": ALL,
        "start": -10000, "end": None, "priority": 0,
        "source": "Chiefdom; Band society",
        "mobility": "a man's standing is his kin, his age and what he can give away",
        "guilds": None,
        "caste": None,
        "speak": "everyone speaks to everyone, and the old are answered first",
        "strata": [
            s("the headman and his kin", "the man whose store others draw on", 0.02,
              "the headman decides nothing alone; he persuades, and a man who will not be "
              "persuaded simply does not follow", 3),
            s("the elders", "those who remember", 0.15,
              "an elder is heard because he has seen it before, not because he can compel", 3),
            s("the grown men and women", "everyone who works", 0.70,
              "a grown man does what his household needs and answers to no one outside it", 3),
            s("the children", "those who do not yet count", 0.13,
              "a child is spoken for, and not yet spoken to", 2),
        ],
    },
    {
        "id": "classic_antiquity",
        "name": "the citizen and the slave",
        "where": ["GRC", "ITA", "TUR", "CYP", "EGY", "LBY", "SYR", "IRQ", "IRN", "TUN", "DZA",
                  "MAR", "ESP", "PRT", "FRA", "ISR", "PSE", "JOR", "LBN", "ALB", "HRV", "MLT"],
        "start": -800, "end": 500, "priority": 4,
        "source": "Slavery in ancient Greece; Slavery in ancient Rome",
        "mobility": "a slave may be freed, and a freedman's son is a citizen: the line is crossed, "
                    "often, and everyone knows it",
        "guilds": "a collegium buries its members and keeps its trade's secrets, and it can be "
                  "forbidden by the state as a conspiracy",
        "caste": None,
        "speak": "a slave is not a person before the law and is not asked; a citizen speaks to a "
                 "magistrate as one citizen to another, and says so",
        "strata": [
            s("the great", "the men of consul's or senator's rank", 0.01,
              "a great man is met in the morning, in a hall, in a queue, and he decides who waits", 3),
            s("the citizens", "free men of the city, however poor", 0.25,
              "a citizen is poor and he is still a citizen: he votes, he is tried by his peers, "
              "and he can be beaten by no magistrate", 3),
            s("the freed", "those who were slaves and are not now", 0.10,
              "a freedman owes his former master service and respect, and his son owes nothing", 2),
            s("the slaves", "a kind of property that can speak", 0.35,
              "a slave is a tool with a voice; he may be a steward, a teacher or a doctor, and "
              "he may be sold at any time", 1),
            s("the women and the foreigners", "those the city does not count", 0.29,
              "a woman answering for herself in court does so through a man", 2),
        ],
    },
    {
        "id": "varnas",
        "name": "the four varnas and the jatis",
        "where": SOUTH_ASIA,
        "start": -500, "end": None, "priority": 6,
        "source": "Caste system in India; Varna (Hinduism); Jāti",
        "mobility": "a man is born to his jati and dies in it; a jati may raise its standing over "
                    "generations by moving, marrying and eating as a higher one does, and the "
                    "village decides whether the claim is allowed",
        "guilds": "the shreni, the guild of a craft, fixes price and quality and acts as one body "
                  "before the king",
        "caste": "birth fixes it: who a man may marry, eat with, take water from, and enter whose "
                 "house; the jati, not the varna, is the one that is lived",
        "speak": "a man of a low jati does not use the familiar form to a man of a high one, does "
                 "not enter his courtyard, and does not eat before him; a man outside the varnas "
                 "is not spoken to at all",
        "strata": [
            s("the brahmins", "those who keep the vedas and perform the rites", 0.05,
              "a brahmin is fed first and paid for a rite whether or not anyone understands it", 3),
            s("the kshatriyas", "those who hold land and fight", 0.05,
              "a kshatriya's claim is his arms and his following, and a king without either loses "
              "the kingdom", 3),
            s("the vaishyas", "those who trade, lend and herd", 0.05,
              "a vaishya's power is money, and money does not buy the standing of the twice-born", 3),
            s("the shudras", "those who serve the three above", 0.50,
              "a shudra works the land of another and is fed from it", 2),
            s("the avarna", "those outside the varnas entirely", 0.35,
              "a man outside the varnas carries away what the village will not touch, and the "
              "village will not take water from his hand", 0),
        ],
    },
    {
        "id": "mandarin",
        "name": "the four occupations",
        "where": EAST_ASIA,
        "start": -200, "end": 1912, "priority": 5,
        "source": "Four occupations; Imperial examination; Scholar-official",
        "mobility": "the examinations are open in principle to any free man, and in practice to "
                    "any household that can spare a son to study for twenty years",
        "guilds": "the hang, the guild of a trade, keeps its members' prices and its own hall, and "
                  "answers to the magistrate for them",
        "caste": None,
        "speak": "a commoner kowtows before a magistrate and may not look up; a magistrate is "
                 "addressed through a clerk, and a clerk through a runner, and each takes his fee",
        "strata": [
            s("the emperor and his house", "the one man under heaven", 0.001,
              "the emperor's word is law and his person is not seen", 3),
            s("the scholars and officials", "those who have passed the examinations", 0.02,
              "a degree is a rank, a rank is an office, and an office is a living taken from the "
              "people it governs", 3),
            s("the farmers", "those who feed everyone else", 0.60,
              "the farmer is honoured in texts and pressed in practice, and a bad harvest is "
              "followed by a remittance or a revolt", 2),
            s("the artisans", "those who make", 0.15,
              "an artisan's skill is his household's, and a guild keeps it", 2),
            s("the merchants", "those who move goods and are trusted least", 0.10,
              "a merchant may be rich and may not wear silk, ride in a litter, or sit an "
              "examination in his father's lifetime", 2),
            s("the mean people", "actors, executioners, and the enslaved", 0.13,
              "a mean man's children are barred from the examinations for three generations", 1),
        ],
    },
    {
        "id": "estates",
        "name": "the three estates",
        "where": WEST_EUROPE + ["HUN", "POL", "CZE", "AUT", "HRV", "SVN"],
        "start": 900, "end": 1789, "priority": 5,
        "source": "Estates of the realm; Feudalism; Guild",
        "mobility": "a man is born to his estate and dies in one; the church is the one road out, "
                    "and a town's charter is another, and both are narrow",
        "guilds": "the guild holds a town's trade: no man works a craft there who is not a "
                  "freeman of it, and the guild fixes who may, at what price, and how many "
                  "apprentices he may keep",
        "caste": None,
        "speak": "a villein does not address his lord standing, does not sit in his hall, and is "
                 "answered through a bailiff; in a town a master speaks to a journeyman as a "
                 "householder to a servant, which they both are",
        "strata": [
            s("the first estate", "those who pray", 0.02,
              "acleric is tried in his own court, pays no tallage, and answers to Rome", 3),
            s("the second estate", "those who fight", 0.03,
              "a lord holds his land of another lord for a service, and that service is armed men", 3),
            s("the third estate", "those who work", 0.95,
              "a commoner's whole standing is the franchise of his town or the custom of his "
              "manor, and both can be lost in a morning", 2),
        ],
    },
    {
        "id": "islamic",
        "name": "the free, the protected and the owned",
        "where": MIDDLE_EAST + NORTH_AFRICA + ["ESP", "PRT", "IRN", "AFG", "TKM", "UZB", "TJK",
                                               "IND", "BGD", "PAK", "TUR", "SDN", "SOM", "MLI",
                                               "NER", "TCD", "SEN", "GMB", "MLT"],
        "start": 700, "end": 1900, "priority": 5,
        "source": "Dhimmi; Slavery in the Muslim world; Mamluk",
        "mobility": "a slave may be freed and a freedman may rise to command armies: the mamluk "
                    "who is bought as a boy may be a sultan, and everyone in the city knows it",
        "guilds": "the asnaf, the guilds of a trade, keep the market's order and its prices, and "
                  "their heads carry the trade's voice to the qadi",
        "caste": None,
        "speak": "a believer addresses a believer as a brother; a protected man speaks softly, "
                 "rises first, and does not raise his voice in the street",
        "strata": [
            s("the ruler and his house", "the one who holds the sword and the coin", 0.005,
              "the ruler's law is administered by a qadi who can be dismissed, and the qadi's "
              "court is open to anyone who can pay the fee", 3),
            s("the free believers", "those who owe nothing but the tax on their faith", 0.55,
              "a free man's standing is his reputation among his neighbours, and neighbours "
              "testify", 3),
            s("the protected", "the people of the book who keep their own law", 0.10,
              "a protected community judges itself, keeps its own marriage and inheritance, and "
              "pays for the privilege", 2),
            s("the owned", "slaves, of every colour and every office", 0.20,
              "an owned man may command a province or carry water, and he may be sold either way", 1),
            s("the women", "those who are answered for", 0.145,
              "a woman holds property and pleads in court, and she pleads through an agent", 2),
        ],
    },
    {
        "id": "casta",
        "name": "the castas",
        "where": LATIN_AMERICA + CARIBBEAN,
        "start": 1500, "end": 1825, "priority": 6,
        "source": "Casta; Encomienda; Slavery in the Spanish Empire",
        "mobility": "the categories are written down and argued over: a man's casta is a document "
                    "and a petition, and money and marriage move a family across a line in two "
                    "generations",
        "guilds": "the gremio of a town holds a trade as in Spain, and the Indian cabildo holds "
                  "the community's land and its labour",
        "caste": "birth and blood together: how much Indian or African blood a man is held to "
                 "have, written in a painting and a parish register",
        "speak": "a casta man is addressed by his casta name and no other; an Indian who will not "
                 "remove his hat is beaten for it",
        "strata": [
            s("the peninsulares", "those born in Spain or Portugal", 0.01,
              "a peninsular holds the office, sends the money home, and goes home", 3),
            s("the creoles", "Spaniards born in the Indies", 0.10,
              "a creole owns the land and is not trusted with the government of it", 3),
            s("the castas", "the named mixtures of Spaniard, Indian and African", 0.30,
              "a casta is a word for a kind of person, and there are dozens of them", 2),
            s("the Indians", "the people of the land, under the encomienda", 0.40,
              "an Indian owes tribute and labour, holds his community's land, and is a minor "
              "before the law", 1),
            s("the enslaved Africans", "those brought across the sea", 0.19,
              "an enslaved African works the sugar and the mine, and a manumission is a document", 0),
        ],
    },
    {
        "id": "japanese",
        "name": "shi-no-ko-sho",
        "where": ["JPN"],
        "start": 1600, "end": 1868, "priority": 7,
        "source": "Four divisions of society (Japan); Samurai; Burakumin",
        "mobility": "none in law: a farmer may not leave his village, a merchant may not bear "
                    "arms, and the boundary is policed",
        "guilds": "the za, the guild of a trade, is licensed by the shogunate and holds its "
                  "monopoly for a fee",
        "caste": "an outcaste is born and cannot leave: the eta and the hinin are registered, "
                 "their quarter is separate, and the status descends",
        "speak": "a samurai may cut down a commoner for a discourtesy and answer for it; a "
                 "commoner addresses him flat on the ground",
        "strata": [
            s("the samurai", "those who bear two swords", 0.07,
              "a samurai is paid in rice by a lord he never sees, and may not farm or trade", 3),
            s("the farmers", "those who grow the rice the whole order rests on", 0.75,
              "a farmer is the second-highest estate and the most controlled: he may not sell "
              "his land, leave his village, or eat the rice he grows", 2),
            s("the artisans", "those who make", 0.09,
              "an artisan's house is his workshop and his shop, and his guild licenses him", 2),
            s("the merchants", "those who sell, and are the richest of the four", 0.08,
              "a merchant lends to a daimyo who does not repay and cannot be sued", 2),
            s("the outcastes", "those whose work is death, leather or filth", 0.01,
              "an outcaste is not a person in the register and is counted as a fraction of one", 0),
        ],
    },
    {
        "id": "modern_classes",
        "name": "the classes of an industrial society",
        "where": WEST_EUROPE + NORTH_EUROPE + NORTH_AMERICA + ["AUS", "NZL", "JPN", "RUS", "UKR",
                                                               "BLR", "POL", "CZE", "HUN", "CHL",
                                                               "ARG", "BRA", "URY", "KOR"],
        "start": 1800, "end": None, "priority": 8,
        "source": "Social class; Bourgeoisie; Proletariat; Trade union",
        "mobility": "a man is born to a class and many leave it: schooling is the road, and how "
                    "open it is belongs to the country and the year",
        "guilds": "the union takes the guild's place: it bargains for a trade's wages and "
                  "conditions, and a closed shop is a guild by another name",
        "caste": None,
        "speak": "in law everyone speaks as an equal; in practice a man is heard by how he "
                 "speaks, and a working man who will not take off his cap is told to",
        "strata": [
            s("the owners", "those who own the mills, the mines and the land", 0.02,
              "an owner does not work and does not need to; his name is on the gate", 3),
            s("the professions", "those who sell a qualification", 0.08,
              "a professional's living rests on an examination and a reputation, and both are "
              "guarded by his own body", 3),
            s("the petty bourgeoisie", "those who own a shop, a farm or a trade", 0.20,
              "a shopkeeper is his own master and nobody's: he fears the combine above and the "
              "union below", 3),
            s("the skilled workers", "those whose trade cannot be learned in a week", 0.25,
              "a skilled man's union keeps the rate for the job and the job for the man", 3),
            s("the labourers", "those who sell strength by the day", 0.45,
              "a labourer is hired by the day and dismissed by the day, and has no trade to "
              "defend him", 2),
        ],
    },
    {
        "id": "socialist",
        "name": "the working class and its party",
        "where": ["RUS", "UKR", "BLR", "KAZ", "UZB", "TKM", "KGZ", "TJK", "ARM", "AZE", "GEO",
                  "MDA", "EST", "LVA", "LTU", "POL", "CZE", "SVK", "HUN", "ROU", "BGR", "SRB",
                  "HRV", "SVN", "BIH", "MKD", "MNE", "ALB", "CHN", "PRK", "VNM", "LAO", "KHM",
                  "CUB", "MNG"],
        "start": 1917, "end": 1991, "priority": 9,
        "source": "Nomenklatura; Soviet working class; Soviet Union",
        "mobility": "the party is the road, and it is the only one: a worker's son is educated "
                    "into the party and the party places him",
        "guilds": None,
        "caste": None,
        "speak": "a man addresses a comrade as comrade and an official as citizen; what he says "
                 "in a kitchen and what he says at a meeting are two different languages",
        "strata": [
            s("the nomenklatura", "those whose appointment the party must approve", 0.02,
              "a nomenklatura man's apartment, car, dacha and shop are all assigned, and all can "
              "be taken back", 3),
            s("the party membership", "the card, which is the whole of the road", 0.08,
              "a party card is a claim on every appointment and a risk at every purge", 3),
            s("the workers", "the class the state says it rules for", 0.45,
              "a worker is employed for life, cannot be fired, cannot leave, and cannot strike", 2),
            s("the peasants", "those on the collective farms", 0.35,
              "a collective farmer's internal passport keeps him on the land; without it he cannot leave the "
              "village", 2),
            s("the prisoners", "the camps, which are an economy", 0.10,
              "a camp sentence is a labour allocation, and the camp is counted in the plan", 0),
        ],
    },
    {
        "id": "tribal",
        "name": "the segmentary lineage",
        "where": SAHEL_WEST_AFRICA + EAST_AFRICA + ["SAU", "YEM", "OMN", "ARE", "QAT", "BHR", "KWT",
                                                    "JOR", "IRQ", "SYR", "LBY", "MRT", "SOM", "AFG",
                                                    "TCD", "SDN"],
        "start": 700, "end": 1950, "priority": 4,
        "source": "Segmentary lineage; Tribe; Slavery in Africa",
        "mobility": "a lineage's standing rises and falls with its herds and its men; a client "
                    "lineage is attached to a stronger one and can leave it",
        "guilds": "the caste of the artisans - the smiths, the leatherworkers, the griots - is a "
                  "hereditary craft group held apart and feared for its power over iron and words",
        "caste": "in the Sahel the artisan groups are castes: born to the work, married inside it, "
                 "and set apart by everyone else",
        "speak": "a man does not contradict an elder in front of others; a smith speaks freely to "
                 "anyone and is not answered freely by anyone",
        "strata": [
            s("the chief and his lineage", "those who hold the arbitration and the mare", 0.03,
              "a chief arbitrates and does not command; a man who will not accept the arbitration "
              "walks away, and takes his tents with him", 3),
            s("the free lineages", "those who bear arms and own camels or cattle", 0.47,
              "a free man's honour is his and is defended by his whole lineage", 3),
            s("the artisan castes", "smiths, leatherworkers, griots", 0.05,
              "a smith makes the weapons and the tools and is feared for it; a griot keeps the "
              "names and can ruin one", 2),
            s("the clients", "attached lineages and freed households", 0.25,
              "a client herds for a patron and is defended by him", 2),
            s("the owned", "those taken in raid or bought", 0.20,
              "a person owned in a household is often fed, housed and married by it, and their "
              "children are born into it", 1),
        ],
    },
    {
        "id": "settler_colonial",
        "name": "the settlers and the colonised",
        # Not IND: the Raj was an administration and not a settler colony, and the varnas run
        # unbroken to the present, so a priority that put the colour bar over them described
        # Mughal India by a law that was passed two centuries later.
        "where": ["ZAF", "NAM", "ZWE", "MWI", "ZMB", "MOZ", "AGO", "KEN", "TZA", "UGA", "RWA",
                  "BDI", "DZA", "USA", "CAN", "AUS", "NZL", "PNG", "MYS", "IDN", "MMR",
                  "VNM", "THA", "PHL"],
        "start": 1650, "end": 1975, "priority": 7,
        "source": "Settler colonialism; Colour bar; Indirect rule",
        "mobility": "the colour bar is a law and a wage: the categories are written into the "
                    "pass, the franchise and the job, and are argued over violently",
        "guilds": "the trade union is for white workers, and its closed shop keeps the skilled "
                  "work and the rate for it",
        "caste": "the bar is by race as the jati is by birth: who may live where, work at what, "
                 "marry whom, and enter by which door",
        "speak": "a white man is called sir by every non-white man and calls every adult "
                 "non-white man by his first name or by 'boy'",
        "strata": [
            s("the settlers and their government", "those who hold the state", 0.05,
              "a settler's whole standing rests on a state that is a minority of the people", 3),
            s("the settler workers", "those whose wage is the colour bar", 0.10,
              "a settler worker is protected by the job colour bar and is its fiercest defender", 3),
            s("the intermediaries", "clerks, headmen, interpreters, the mission-educated", 0.10,
              "an intermediary speaks both languages and belongs fully to neither side", 2),
            s("the colonised workers", "those who work for a wage or by coercion", 0.50,
              "a colonised man's labour is required by a tax he can only pay in cash", 1),
            s("the colonised on the land", "those in the reserves and the homelands", 0.25,
              "a reserve is where the colony puts the people it has taken the land from", 1),
        ],
    },
]

# The line for a place and year no row names: a register that shrugs has failed.
DEFAULT = {
    "id": "default",
    "name": "a house and a household",
    "where": [],
    "start": None, "end": None, "priority": -1,
    "source": None,
    "mobility": "a man's standing is his household's, and a household's standing can rise",
    "guilds": None,
    "caste": None,
    "speak": "a stranger is answered by the head of the house, and through him by everyone in it",
    "strata": [
        s("the great house", "the household others owe rent or service to", 0.03,
          "the great house takes a share of every harvest and settles every dispute it hears of", 3),
        s("the householders", "those who hold a house, a shop or a holding", 0.40,
          "a householder pays, and because he pays he is asked", 3),
        s("the dependants", "sons, daughters, servants and labourers of a house", 0.42,
          "a dependant works the house's land and the house answers for him", 2),
        s("the landless", "those with nothing but their hands", 0.15,
          "a landless man hires out by the day and sleeps where he works", 2),
    ],
}

# Who may speak to whom: the four degrees, for the mod to print.
MAY = {
    0: "he is not spoken to and does not speak first",
    1: "he answers when he is spoken to, and not before",
    2: "he speaks to his own order and to those beneath it",
    3: "he speaks to anyone, and is answered",
}
