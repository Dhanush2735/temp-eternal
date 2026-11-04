"""Step 30a (system C16): the hand-written part of the technology atlas.

Every technology here: its name, its field, what it needs first, what it replaces, where and when it began, and the
years it reached the lands of today's countries where the record is clear. The years come from English Wikipedia's
articles on each technology ("History of ...", the technology's own article, and lists such as "Global spread of the
printing press", "Timeline of the introduction of television in countries"), written here by hand (turn 12: Wikipedia
first); `source` names the main article. build_technology_atlas.py adds CHAT (Comin and Hobijn, 104 technologies in 161
countries, 1800-2008) for the modern ones, and estimates every other country from the nearest known one (marked as
estimated).

Record: R(where, year, note, at) - where: a country code of today (ADM0_A3, as in Natural Earth: IND, CHN, GBR ...), a
UN subregion ("@Western Europe"), or a group below; at: (lat, lon) of the place it began in that country, when the
record names one (the game counts the spread inside a big country from there; otherwise from the country's biggest
town).

Technology: T(id, name, field, kind, d50, ...)
  name    how a villager says it in a list ("railways", "the telephone", "printed books")
  field   farming, building, metals, energy, land, water, communication, writing, war, medicine, textiles, crafts,
          lighting, home, computing
  kind    craft (a skill people have), farm, infra (a thing a town has: the game decides town by town), home (a thing
          households have: "a few rich people", "most homes"), weapon, medicine, knowledge
  d50     years from its arrival in a country to half of its towns (cities sooner, villages later)
  needs   technologies it needs first in the same land; replaces: older ones it pushes out
  origins records of where it began; records: later arrivals; not_before: not in these lands before these years
  only    True: only where a record says (porcelain is made, high-speed trains run); no estimates elsewhere
  lost    (where, from, to): forgotten in those years (writing in the Indus lands, 1900 BCE to 300 BCE)
  chat    the CHAT series that gives its arrival (and, for things households have, how common it is)
  fame    1-3, how likely a villager is to mention it
"""


def R(where, year, note="", at=None):
    return {"where": where, "year": year, "note": note, "at": at}


def T(id, name, field, kind, d50, origins, records=(), needs=(), replaces=(), not_before=(), only=False, lost=(),
      chat=None, chat_sat=None, source="", fame=1, max_share=1.0, game=None):
    return {"id": id, "name": name, "field": field, "kind": kind, "d50": d50, "origins": list(origins),
            "records": list(records), "needs": list(needs), "replaces": list(replaces),
            "not_before": list(not_before), "only": only, "lost": list(lost), "chat": chat, "chat_sat": chat_sat,
            "source": source, "fame": fame, "max_share": max_share, "game": game or {}}


SUBREGIONS = ["Western Europe", "Northern Europe", "Southern Europe", "Eastern Europe", "Western Asia", "Central Asia",
              "Southern Asia", "Eastern Asia", "South-Eastern Asia", "Northern Africa", "Western Africa",
              "Middle Africa", "Eastern Africa", "Southern Africa", "Northern America", "Central America", "Caribbean",
              "South America", "Australia and New Zealand", "Melanesia", "Micronesia", "Polynesia"]

GROUPS = {
    "EUROPE": ["@Western Europe", "@Northern Europe", "@Southern Europe", "@Eastern Europe"],
    "AMERICAS": ["@Northern America", "@Central America", "@Caribbean", "@South America"],
    "OCEANIA": ["@Australia and New Zealand", "@Melanesia", "@Micronesia", "@Polynesia"],
    "SSA": ["@Western Africa", "@Middle Africa", "@Eastern Africa", "@Southern Africa"],
    "SAHEL": ["MRT", "SEN", "GMB", "MLI", "BFA", "NER", "TCD"],
    "HORN": ["ETH", "ERI", "DJI", "SOM", "SOL"],
    "MENA": ["@Northern Africa", "@Western Asia", "IRN"],
    "ARAB_LANDS": ["EGY", "LBY", "TUN", "DZA", "MAR", "SAH", "SAU", "YEM", "OMN", "ARE", "QAT", "BHR", "KWT", "IRQ",
                   "SYR", "JOR", "ISR", "PSX", "LBN"],
    "SOUTH_ASIA": ["IND", "PAK", "BGD", "NPL", "BTN", "LKA", "MDV", "KAS"],
    "INDUS": ["PAK", "IND"],
    "MESOAMERICA": ["MEX", "GTM", "BLZ", "HND", "SLV"],
    "ANDES": ["PER", "BOL", "ECU", "CHL"],
    "LEVANT": ["SYR", "LBN", "ISR", "PSX", "JOR"],
    "CAUCASUS": ["GEO", "ARM", "AZE"],
    "BRITISH_ISLES": ["GBR", "IRL", "IMN", "JEY", "GGY"],
    "SCANDINAVIA": ["DNK", "SWE", "NOR", "ISL", "FRO", "ALD"],
    "BALKANS": ["SRB", "HRV", "BIH", "MNE", "ALB", "MKD", "KOS", "SVN", "BGR", "ROU", "MDA"],
    "INDOCHINA": ["VNM", "LAO", "KHM"],
    "MALAY": ["MYS", "SGP", "BRN", "IDN", "TLS"],
}
# Lands the rest of the world reached late. A technology from elsewhere arrives there only from that year on (the
# build applies it to every technology without a record there from before).
CONTACT = {
    "CUB": 1492, "BHS": 1492, "HTI": 1492, "DOM": 1492, "PRI": 1493, "JAM": 1494, "TTO": 1498, "VEN": 1498,
    "ATG": 1493, "KNA": 1493, "DMA": 1493, "LCA": 1502, "VCT": 1498, "GRD": 1498, "BRB": 1536, "MSR": 1493,
    "AIA": 1493, "BLM": 1493, "MAF": 1493, "SXM": 1493, "VGB": 1493, "VIR": 1493, "ABW": 1499, "CUW": 1499,
    "TCA": 1512, "CYM": 1503, "BMU": 1505, "PAN": 1501, "HND": 1502, "NIC": 1502, "CRI": 1502, "COL": 1499,
    "MEX": 1519, "GTM": 1524, "SLV": 1524, "BLZ": 1525, "PER": 1532, "ECU": 1531, "BOL": 1535, "CHL": 1536,
    "ARG": 1516, "URY": 1516, "PRY": 1537, "BRA": 1500, "GUY": 1595, "SUR": 1593, "FLK": 1690, "USA": 1513,
    "CAN": 1497, "GRL": 1721, "SPM": 1520, "AUS": 1788, "NZL": 1769, "NFK": 1788, "PNG": 1526, "SLB": 1568,
    "VUT": 1606, "NCL": 1774, "FJI": 1774, "TON": 1616, "WSM": 1722, "ASM": 1722, "PYF": 1767, "COK": 1773,
    "NIU": 1774, "PCN": 1767, "TUV": 1819, "WLF": 1767, "GUM": 1521, "MNP": 1521, "FSM": 1529, "PLW": 1543,
    "MHL": 1529, "KIR": 1606, "NRU": 1798,
}
# A point outside its country's own part of the world (French Guiana under France, Hawaii under the United States)
# takes the year of its own part: the game checks it by the point (TechnologyAtlas.contactFloor).
ZONE_CONTACT = {"americas": 1500, "pacific": 1770, "australia": 1788, "hawaii": 1778, "alaska": 1741}
# Lands nobody lived in until then: no technology arrives there earlier (Iceland was settled about 874).
SETTLED = {"ISL": 874, "FRO": 825, "MDG": 500, "MUS": 1638, "SYC": 1770, "CPV": 1462, "STP": 1485, "SHN": 1659,
           "BMU": 1612, "FLK": 1764, "NZL": 1280, "PCN": 1790, "NFK": 1788, "SGS": 1904, "ATA": 1957, "HMD": 3000,
           "ATF": 1950, "IOT": 1780, "ALD": 500}
# Small entities that share their parent land's history: a record for the parent is a record for them.
PARENT = {"CYN": "CYP", "CNM": "CYP", "ESB": "CYP", "WSB": "CYP", "KAB": "KAZ", "KAS": "IND", "USG": "CUB",
          "BRI": "BRA", "SPI": "ARG", "BRT": "EGY", "SOL": "SOM", "KOS": "SRB", "HKG": "CHN", "MAC": "CHN",
          "ALD": "FIN", "GGY": "GBR", "JEY": "GBR", "IMN": "GBR", "SAH": "MAR", "VAT": "ITA", "SMR": "ITA",
          "MCO": "FRA", "AND": "ESP", "LIE": "CHE", "GIB": "ESP"}
SETTLED.update({"CLP": 3000, "BJN": 3000, "SER": 3000, "ATC": 3000, "CSI": 3000, "PGA": 3000, "SCR": 3000,
                "UMI": 1850})
# Lands closed to the outside: technologies from Europe and the Americas wait until the doors open, unless recorded.
ISOLATION = [("JPN", 1639, 1853, "sakoku: the Tokugawa closed Japan from 1639 until Perry's ships in 1853"),
             ("KOR", 1640, 1876, "Joseon Korea kept foreigners out until the Treaty of Ganghwa, 1876")]
# Technologies from Europe begun between 1450 and 1800 did not reach inland Africa before about 1800 unless a record
# says so (the slave-trade forts and the Cape are recorded where they matter).
EARLY_MODERN_EUROPE_FLOOR = ("SSA", 1800)

TECHS = []
add = TECHS.append

# =================================================================================================== farming and food
add(T("farming", "farming", "farming", "farm", 600, source="Neolithic Revolution", fame=1, origins=[
    R("LEVANT", -9500, "the Fertile Crescent"), R("IRQ", -9000), R("TUR", -9000), R("IRN", -8000),
    R("CHN", -7000, "millet in the north, rice on the Yangtze"), R("PNG", -7000, "Kuk Swamp"),
    R("MEX", -4000, "maize villages; maize was tamed about 7000 BCE"), R("PER", -3000, "the Andes and the coast"),
    R("USA", -2000, "the Eastern Agricultural Complex", (38.0, -88.0))], records=[
    R("EGY", -5000, "the Fayum"), R("PAK", -7000, "Mehrgarh"), R("IND", -6000), R("GRC", -6500), R("BGR", -6000),
    R("ITA", -6000), R("ESP", -5500), R("FRA", -5500), R("DEU", -5500, "the Linear Pottery culture"),
    R("BRITISH_ISLES", -4000), R("SCANDINAVIA", -4000), R("FIN", -2500), R("TKM", -6000, "Jeitun"),
    R("UZB", -5000), R("KOR", -3500), R("JPN", -900, "wet rice of the Yayoi"), R("THA", -2000), R("VNM", -2000),
    R("IDN", -2000), R("PHL", -2000), R("MLI", -2500, "pearl millet"), R("ETH", -2000), R("NGA", -2000),
    R("GTM", -2000), R("BOL", -2000), R("ECU", -3000), R("ZAF", 300, "Bantu farmers in the east"),
    R("AUS", 1788), R("NZL", 1280, "Polynesian settlers with the kumara")]))
add(T("plough", "the plough", "farming", "farm", 400, source="Plough", needs=["farming"], origins=[
    R("IRQ", -4000, "the ard of Mesopotamia")], records=[
    R("SYR", -3500), R("EGY", -3000), R("INDUS", -2800, "ploughed field at Kalibangan"), R("IRN", -3000),
    R("TUR", -3500), R("GRC", -3500), R("DNK", -3500, "ard marks"), R("GBR", -3500, "ard marks under long barrows"),
    R("DEU", -3500), R("FRA", -3500), R("ITA", -3000), R("ESP", -3000), R("CHN", -3000, "stone ploughs of Liangzhu"),
    R("KOR", -100), R("JPN", 500), R("VNM", -200), R("THA", 500), R("IDN", 800), R("ETH", -500, "the ox-plough"),
    R("ERI", -500)], not_before=[R("SSA", 1900, "brought in colonial times"), R("ZAF", 1652, "the Dutch Cape")]))
add(T("watermill", "water mills", "farming", "infra", 300, source="Watermill", fame=2, origins=[
    R("GRC", -250, "Perachora; described by Philo of Byzantium")], records=[
    R("TUR", -71, "the mill of Mithridates at Cabira"), R("ITA", -25, "described by Vitruvius"), R("CHN", 31,
    "water-powered bellows of Du Shi"), R("FRA", 150, "Barbegal"), R("GBR", 100), R("ESP", 100), R("DEU", 300),
    R("EGY", 300), R("SYR", 300), R("IRN", 600), R("IRQ", 700), R("KOR", 600), R("JPN", 610, "Damjing of Goguryeo"),
    R("IND", 1000), R("SCANDINAVIA", 1000), R("POL", 1100), R("RUS", 1200), R("MEX", 1525), R("PER", 1540),
    R("USA", 1620)], not_before=[R("SSA", 1850), R("ETH", 1600), R("ZAF", 1700)]))
add(T("windmill", "windmills", "farming", "infra", 300, source="Windmill", fame=2, origins=[
    R("IRN", 900, "the panemone mills of Sistan", (31.0, 61.5))], records=[
    R("AFG", 900, "Sistan"), R("GBR", 1185, "Weedley, Yorkshire"), R("FRA", 1180), R("BEL", 1190), R("NLD", 1200),
    R("DEU", 1200), R("DNK", 1250), R("ESP", 1300), R("PRT", 1300), R("ITA", 1300), R("POL", 1300), R("SWE", 1300),
    R("CHN", 1219, "Yelü Chucai saw them in Samarkand; China's own followed"), R("RUS", 1600), R("USA", 1630),
    R("CUB", 1600), R("ZAF", 1700), R("AUS", 1820)], not_before=[R("SSA", 1850), R("IND", 1800), R("JPN", 1870)]))
add(T("tractor", "tractors", "farming", "infra", 30, source="Tractor", fame=2, chat="ag_tractor",
      origins=[R("USA", 1892, "John Froelich's tractor", (42.8, -91.0))], records=[R("GBR", 1902, "Ivel")]))
add(T("combine", "combine harvesters", "farming", "infra", 35, source="Combine harvester", max_share=0.6, chat="ag_harvester",
      origins=[R("USA", 1835, "Hiram Moore's combine, Michigan", (42.3, -85.6))], records=[R("AUS", 1885)]))
add(T("fertiliser", "artificial fertiliser", "farming", "infra", 40, source="Fertilizer", chat="fert_total",
      origins=[R("GBR", 1842, "John Bennet Lawes' superphosphate", (51.8, -0.36))], records=[
      R("DEU", 1913, "the Haber-Bosch works at Oppau")]))
add(T("canning", "tinned food", "farming", "home", 60, source="Canning", origins=[
    R("FRA", 1810, "Nicolas Appert's method"), R("GBR", 1813, "Donkin and Hall's cannery")], records=[
    R("USA", 1825), R("AUS", 1846), R("JPN", 1871), R("IND", 1890)]))
add(T("refrigerator", "refrigerators", "home", "home", 25, source="Refrigerator", needs=["electricity"], fame=2,
      origins=[R("USA", 1913, "the first electric refrigerators for homes")], records=[R("GBR", 1930),
      R("DEU", 1930), R("JPN", 1952), R("IND", 1958)]))
add(T("irrigation", "irrigation canals", "farming", "farm", 400, source="History of irrigation", needs=["farming"],
      origins=[R("IRQ", -6000, "Choga Mami"), R("EGY", -3100), R("PER", -3000, "the Norte Chico"), R("CHN", -2000)],
      records=[R("INDUS", -2600), R("IRN", -3000), R("UZB", -1000), R("LKA", -300), R("MEX", -1000),
      R("USA", 300, "the Hohokam canals", (33.4, -112.0)), R("ESP", 800)], not_before=[R("SSA", 1900),
      R("ZAF", 1700)]))
add(T("pottery", "pottery", "crafts", "craft", 500, source="Pottery", origins=[
    R("CHN", -18000, "Xianrendong"), R("JPN", -14000, "Jōmon"), R("LEVANT", -7000), R("SAHEL", -9000,
    "the Sahara and the Sahel"), R("BRA", -5000, "the lower Amazon"), R("COL", -4000), R("ECU", -3500)], records=[
    R("EUROPE", -6000), R("MENA", -7000), R("SOUTH_ASIA", -6000), R("@South-Eastern Asia", -3000),
    R("@Western Africa", -5000), R("@Eastern Africa", -3000), R("@Middle Africa", -2000), R("@Southern Africa", 0),
    R("MEX", -1800), R("PER", -1800), R("USA", -2500), R("CAN", -1000), R("AUS", 1788), R("NZL", 1814),
    R("PNG", -1500, "Lapita potters")], fame=1))

# ============================================================================================================ building
add(T("fired_brick", "fired brick", "building", "craft", 300, source="Brick", fame=2, origins=[
    R("IRQ", -3500, "Mesopotamia")], records=[
    R("INDUS", -2600, "Harappa and Mohenjo-daro"), R("IRN", -2500), R("SYR", -2000), R("CHN", -1000,
    "the Western Zhou; common from the Qin and Han"), R("EGY", -30, "Roman Egypt"), R("ITA", -50), R("GRC", -300),
    R("ESP", -50), R("FRA", -50), R("DEU", 50, "the Roman Rhine"), R("GBR", 50), R("UKR", 989,
    "the Church of the Tithes in Kyiv"), R("RUS", 1100), R("POL", 1150), R("DNK", 1160), R("JPN", 590),
    R("KOR", 300), R("MMR", 100, "Pyu towns"), R("KHM", 800), R("THA", 600), R("IDN", 800), R("VNM", 200),
    R("NLD", 1150), R("SWE", 1250)], lost=[R("GBR", 450, 1190), R("IRL", 450, 1300)],
    not_before=[R("SSA", 1850), R("ZAF", 1700)]))
add(T("cement", "Portland cement", "building", "craft", 60, source="Portland cement", fame=1, origins=[
    R("GBR", 1824, "Joseph Aspdin's patent, Leeds", (53.8, -1.55))], records=[
    R("FRA", 1840), R("DEU", 1855, "Stettin"), R("USA", 1871, "Coplay, Pennsylvania"), R("JPN", 1875,
    "Fukagawa"), R("CHN", 1889, "Tangshan"), R("IND", 1904, "Madras"), R("RUS", 1856), R("AUS", 1882),
    R("BRA", 1892)]))
add(T("skyscraper", "tall steel buildings", "building", "infra", 60, source="Skyscraper", max_share=0.3, fame=2,
      needs=["elevator", "ironworks"], origins=[R("USA", 1885, "the Home Insurance Building, Chicago",
      (41.88, -87.63))], records=[R("GBR", 1906, "the Ritz, London"), R("ARG", 1923, "Palacio Barolo"),
      R("BRA", 1929, "Edifício Martinelli"), R("CHN", 1929, "Shanghai's Bund"), R("JPN", 1931),
      R("RUS", 1953, "the Seven Sisters"), R("IND", 1954)]))
add(T("elevator", "lifts", "building", "infra", 60, source="Elevator", max_share=0.6, origins=[
    R("USA", 1857, "Otis' passenger lift in the Haughwout Building, New York", (40.72, -74.0))], records=[
    R("GBR", 1860), R("FRA", 1867), R("DEU", 1880), R("IND", 1896), R("JPN", 1890)]))
add(T("paved_roads", "paved roads", "building", "infra", 200, source="Roman roads", fame=1, origins=[
    R("ITA", -312, "the Via Appia"), R("CHN", -220, "the roads of the Qin"), R("IRN", -500,
    "the Royal Road of the Achaemenids")], records=[
    R("GRC", -146), R("ESP", -100), R("FRA", -50), R("TUR", -100), R("SYR", -60), R("EGY", -30), R("GBR", 50),
    R("DEU", 50), R("TUN", -100), R("PER", 1438, "the Inca road network", (-13.52, -71.97)), R("BOL", 1450),
    R("ECU", 1470), R("CHL", 1470), R("ARG", 1480)],
    lost=[R("GBR", 450, 1750), R("DEU", 450, 1750), R("BEL", 450, 1750), R("NLD", 450, 1750)]))
add(T("tarmac", "tarred roads", "building", "infra", 40, source="Tarmac", fame=1, origins=[
    R("GBR", 1902, "Edgar Hooley's tarmac", (52.6, -2.1)), R("FRA", 1854, "asphalt paving in Paris")], records=[
    R("USA", 1870, "asphalt in Newark and Washington"), R("DEU", 1900), R("IND", 1920), R("JPN", 1920)]))
add(T("iron_bridge", "iron bridges", "building", "infra", 60, source="The Iron Bridge", max_share=0.5, needs=["cast_iron"],
      origins=[R("GBR", 1779, "the Iron Bridge, Coalbrookdale", (52.63, -2.49))], records=[
      R("DEU", 1796, "Łażany, Silesia"), R("FRA", 1803, "Pont des Arts"), R("USA", 1839), R("IND", 1840),
      R("RUS", 1806), R("AUT", 1828)]))
add(T("running_water", "running water", "home", "infra", 60, source="Tap water", fame=2, max_share=0.9, origins=[
    R("GBR", 1848, "the Public Health Act; mains water in towns")], records=[
    R("FRA", 1860), R("DEU", 1860), R("USA", 1850), R("NLD", 1853), R("JPN", 1887, "Yokohama"),
    R("IND", 1860, "Bombay's Vihar water works", (18.94, 72.83))]))
add(T("aqueduct", "aqueducts", "building", "infra", 200, source="Aqueduct (water supply)", max_share=0.3, origins=[
    R("IRQ", -700, "Sennacherib's aqueduct at Jerwan"), R("IRN", -800, "qanats")], records=[
    R("ITA", -312, "the Aqua Appia"), R("GRC", -530, "the Tunnel of Eupalinos"), R("TUR", -150), R("FRA", -20),
    R("ESP", 50, "Segovia"), R("TUN", 120), R("GBR", 100), R("DEU", 80), R("EGY", -30), R("ISR", -20),
    R("OMN", -500, "aflaj"), R("CHN", -250), R("MEX", 1450, "Chapultepec to Tenochtitlan"), R("PER", 1450)]))

# ============================================================================================================== metals
add(T("bronze", "bronze", "metals", "craft", 300, source="Bronze Age", fame=2, origins=[
    R("IRQ", -3300, "Sumer"), R("PER", 200, "arsenical bronze of the Moche"),
    R("BOL", 600, "Tiwanaku"), R("MEX", 1200, "west Mexico, the Tarascans", (19.5, -101.6))], records=[
    R("IRN", -3000), R("TUR", -3000), R("SYR", -3000), R("EGY", -3150), R("GRC", -3200), R("CYP", -2500),
    R("BGR", -3200), R("ROU", -2500), R("HUN", -2500), R("ITA", -2300), R("ESP", -2200, "El Argar"),
    R("FRA", -2200), R("DEU", -2300, "Únětice"), R("CZE", -2300), R("POL", -2300), R("GBR", -2100), R("IRL", -2000),
    R("DNK", -1700), R("SWE", -1700), R("NOR", -1700), R("FIN", -1500), R("RUS", -3000, "Maykop", (44.6, 40.1)),
    R("UKR", -2500), R("CAUCASUS", -3500, "Kura-Araxes"), R("INDUS", -2600), R("CHN", -2000, "Erlitou"),
    R("MNG", -2000), R("KAZ", -2200, "Andronovo"), R("UZB", -2500), R("TKM", -2500, "Bactria-Margiana"),
    R("KOR", -1000), R("JPN", -300), R("THA", -1500, "Ban Chiang"), R("VNM", -1500), R("KHM", -1500),
    R("LAO", -1500), R("MMR", -1500), R("IDN", -500, "Dong Son drums"), R("PHL", -500), R("MYS", -500),
    R("LKA", -700), R("OMN", -2500, "Magan"), R("YEM", -2000), R("SDN", -2500, "Kerma"), R("ETH", -500),
    R("NGA", 900, "Igbo-Ukwu"), R("MRT", -500, "Akjoujt"), R("ECU", 600), R("CHL", 1400), R("ARG", 1000),
    R("COL", 600)], not_before=[R("SSA", 1500)]))
add(T("iron", "iron", "metals", "craft", 300, source="Iron Age", fame=3, origins=[
    R("TUR", -1200, "Anatolia after the Hittites"), R("IND", -1200, "the Ganges plain; early finds at Malhar"),
    R("NGA", -900, "the Nok culture", (9.6, 8.1))], records=[
    R("LEVANT", -1200), R("IRQ", -1000), R("IRN", -1000), R("EGY", -700), R("GRC", -1050), R("CYP", -1100),
    R("ITA", -900, "Villanovan"), R("ESP", -700), R("FRA", -750), R("DEU", -800), R("AUT", -800, "Hallstatt"),
    R("CHE", -800), R("GBR", -800), R("IRL", -600), R("DNK", -500), R("SWE", -500), R("NOR", -500), R("FIN", -500),
    R("POL", -700), R("CZE", -750), R("HUN", -800), R("ROU", -800), R("BGR", -1000), R("UKR", -900),
    R("RUS", -800), R("CAUCASUS", -1100), R("KAZ", -800), R("UZB", -800), R("CHN", -600), R("KOR", -300),
    R("JPN", -300), R("MNG", -500), R("VNM", -500), R("THA", -500), R("KHM", -500), R("MMR", -500), R("LAO", -500),
    R("MYS", -300), R("IDN", -200), R("PHL", -200), R("LKA", -900), R("PAK", -1100, "the Gandhara grave culture"),
    R("BGD", -800), R("YEM", -900), R("SDN", -500, "Meroë"), R("ETH", -400), R("NER", -800), R("CMR", -800),
    R("MLI", -500), R("GHA", -500), R("SEN", -500), R("RWA", -500), R("BDI", -500), R("UGA", -500), R("TZA", -500),
    R("KEN", -300), R("COD", -300), R("ZMB", 300), R("ZWE", 300), R("MOZ", 200), R("MWI", 200), R("AGO", 300),
    R("ZAF", 300, "the first iron-working farmers"), R("SWZ", 300), R("BWA", 400), R("NAM", 500),
    R("MDG", 800)]))
add(T("steel", "steel", "metals", "craft", 300, source="History of ferrous metallurgy", needs=["iron"], fame=2,
      origins=[R("TUR", -1800, "a piece of steel at Kaman-Kalehöyük")], records=[
      R("IND", -300, "wootz steel"), R("LKA", -300), R("CHN", -300), R("AUT", -200, "Noric steel"),
      R("ITA", -200), R("GRC", -500), R("JPN", 500), R("SYR", 900, "Damascus blades"), R("IRN", 500)]))
add(T("cast_iron", "cast iron", "metals", "craft", 200, source="Cast iron", needs=["iron"], origins=[
    R("CHN", -500, "the state of Jin")], records=[
    R("KOR", -100), R("SWE", 1150, "the Lapphyttan blast furnace"), R("DEU", 1300), R("BEL", 1340), R("FRA", 1380),
    R("ITA", 1400), R("GBR", 1496, "Newbridge, Sussex"), R("RUS", 1632, "Tula"), R("USA", 1646,
    "Saugus Iron Works")], not_before=[R("MENA", 1800), R("SOUTH_ASIA", 1800), R("SSA", 1850),
    R("@South-Eastern Asia", 1850)]))
add(T("ironworks", "coke ironworks", "metals", "infra", 40, source="Coalbrookdale", max_share=0.15, needs=["cast_iron"], fame=2,
      origins=[R("GBR", 1709, "Abraham Darby's coke furnace, Coalbrookdale", (52.64, -2.48))], records=[
      R("FRA", 1785, "Le Creusot"), R("DEU", 1796, "Gleiwitz"), R("BEL", 1823, "Seraing"), R("USA", 1835),
      R("RUS", 1872, "Yuzovka"), R("IND", 1875, "Barakar"), R("JPN", 1901, "Yawata"), R("CHN", 1894,
      "Hanyang Ironworks"), R("AUS", 1848), R("SWE", 1850), R("CZE", 1830)]))
add(T("bessemer", "Bessemer steelworks", "metals", "infra", 30, source="Bessemer process", max_share=0.08, needs=["ironworks"],
      chat="steel_acidbess", origins=[R("GBR", 1856, "Henry Bessemer, Sheffield", (53.38, -1.47))],
      records=[R("SWE", 1858), R("USA", 1865), R("DEU", 1863), R("FRA", 1858)]))
add(T("open_hearth", "open-hearth steelworks", "metals", "infra", 30, source="Open-hearth furnace", max_share=0.1,
      needs=["ironworks"], chat="steel_ohf", replaces=["bessemer"],
      origins=[R("FRA", 1864, "Pierre-Émile Martin, Sireuil", (45.6, 0.03))], records=[R("GBR", 1866)]))
add(T("electric_steel", "electric steel furnaces", "metals", "infra", 30, source="Electric arc furnace", max_share=0.1,
      needs=["electricity", "ironworks"], chat="steel_eaf", origins=[R("FRA", 1900, "Paul Héroult")]))
add(T("oxygen_steel", "oxygen steelworks", "metals", "infra", 25, source="Basic oxygen steelmaking", max_share=0.08,
      needs=["ironworks"], chat="steel_bof", replaces=["open_hearth"],
      origins=[R("AUT", 1952, "Linz", (48.3, 14.3))]))
add(T("aluminium", "aluminium", "metals", "craft", 50, source="Hall–Héroult process", needs=["electricity"],
      origins=[R("USA", 1888, "Pittsburgh Reduction Company"), R("FRA", 1889)], records=[R("CHE", 1888),
      R("DEU", 1898), R("GBR", 1896), R("NOR", 1908), R("JPN", 1934), R("IND", 1943), R("CHN", 1954)]))

# ============================================================================================================== energy
add(T("steam_engine", "steam engines", "energy", "infra", 60, source="Newcomen atmospheric engine", max_share=0.9, fame=3,
      origins=[R("GBR", 1712, "Thomas Newcomen's engine near Dudley Castle", (52.51, -2.08))], records=[
      R("SVK", 1722, "Nová Baňa, Kingdom of Hungary"), R("FRA", 1726, "Passy, Paris"), R("SWE", 1728,
      "Dannemora"), R("USA", 1755, "the Schuyler copper mine, New Jersey"), R("RUS", 1777, "Kronstadt docks"),
      R("DEU", 1785, "Hettstedt"), R("BEL", 1720), R("NLD", 1776), R("ESP", 1780), R("IND", 1820), R("EGY", 1820,
      "Muhammad Ali's factories"), R("MEX", 1820), R("AUS", 1815), R("JPN", 1855), R("CHN", 1865,
      "the Jiangnan Arsenal"), R("TUR", 1830), R("BRA", 1815)]))
add(T("electricity", "electric light", "energy", "infra", 25, source="Electric power", fame=3,
      needs=["steam_engine"], replaces=["gas_light", "kerosene_lamp"], chat="elecprod", origins=[
      R("GBR", 1881, "Godalming, the first public supply", (51.19, -0.61)), R("USA", 1882,
      "Pearl Street Station, New York", (40.71, -74.01))], records=[
      R("CHN", 1882, "the Shanghai Electric Company", (31.23, 121.47)), R("DEU", 1884, "Berlin"),
      R("ITA", 1883, "Milan"), R("FRA", 1883), R("ROU", 1884, "Timișoara's street lights"), R("RUS", 1886),
      R("JPN", 1887, "Tokyo Electric Light"), R("AUS", 1888, "Tamworth"), R("IND", 1897, "Darjeeling",
      (27.04, 88.26)), R("IND", 1899, "Calcutta", (22.57, 88.36)), R("IND", 1905, "Bombay", (18.94, 72.83)), R("BRA", 1883, "Campos"), R("ARG", 1887), R("CHL", 1883), R("MEX", 1889), R("EGY", 1893),
      R("TUR", 1902), R("IRN", 1904), R("THA", 1884), R("ZAF", 1882, "Kimberley"), R("CAN", 1883)]))
add(T("kerosene_lamp", "paraffin lamps", "lighting", "home", 20, source="Kerosene lamp", origins=[
    R("UKR", 1853, "Ignacy Łukasiewicz's lamps in Lviv", (49.84, 24.03))], records=[
    R("USA", 1859), R("GBR", 1860), R("DEU", 1860), R("RUS", 1865), R("IND", 1870), R("JPN", 1870),
    R("CHN", 1870), R("EGY", 1870)]))
add(T("gas_light", "gas street lights", "lighting", "infra", 30, source="Gas lighting", fame=2, origins=[
    R("GBR", 1807, "Pall Mall, London", (51.506, -0.134))], records=[
    R("USA", 1817, "Baltimore"), R("AUT", 1818), R("BEL", 1819), R("FRA", 1820, "Paris"), R("DEU", 1825,
    "Hanover"), R("NLD", 1826), R("RUS", 1839, "Saint Petersburg"), R("AUS", 1841, "Sydney"), R("TUR", 1857,
    "Istanbul"), R("BRA", 1854, "Rio de Janeiro"), R("ARG", 1856), R("IND", 1857, "Calcutta", (22.57, 88.36)),
    R("CHN", 1865, "Shanghai"), R("EGY", 1865), R("JPN", 1872, "Yokohama"), R("MEX", 1869), R("ZAF", 1864),
    R("CAN", 1838)]))
add(T("nuclear_power", "an atomic power station", "energy", "infra", 15, source="Nuclear power by country", max_share=0.05,
      needs=["electricity"], only=True, origins=[R("RUS", 1954, "Obninsk", (55.1, 36.6))], records=[
      R("GBR", 1956, "Calder Hall"), R("USA", 1957, "Shippingport"), R("FRA", 1956, "Marcoule"),
      R("DEU", 1961), R("CAN", 1962), R("BEL", 1962), R("ITA", 1963), R("JPN", 1963), R("SWE", 1964),
      R("ESP", 1968), R("NLD", 1968), R("CHE", 1969), R("IND", 1969, "Tarapur"), R("PAK", 1971), R("BGR", 1974),
      R("ARG", 1974), R("CZE", 1985), R("SVK", 1972), R("UKR", 1977), R("ARM", 1976), R("FIN", 1977),
      R("TWN", 1977), R("KOR", 1978), R("LTU", 1983), R("SVN", 1981), R("HUN", 1982), R("BRA", 1982),
      R("ZAF", 1984), R("MEX", 1989), R("CHN", 1991), R("ROU", 1996), R("IRN", 2011), R("ARE", 2020),
      R("BLR", 2020), R("BGD", 2024)]))
add(T("solar_panels", "solar panels", "energy", "home", 20, source="Solar panel", needs=["electricity"],
      origins=[R("USA", 1954, "Bell Labs")], records=[R("DEU", 2000), R("JPN", 1994), R("CHN", 2009),
      R("IND", 2010)]))
add(T("wind_turbines", "wind turbines", "energy", "infra", 20, source="Wind turbine", max_share=0.5, needs=["electricity"],
      origins=[R("DNK", 1978, "Tvind")], records=[R("USA", 1981), R("DEU", 1990), R("ESP", 1995),
      R("IND", 1995), R("CHN", 2005)]))

# ======================================================================================================= land transport
add(T("wheel", "wheeled carts", "land", "farm", 400, source="Wheel", fame=2, origins=[
    R("IRQ", -3500, "Uruk")], records=[
    R("TUR", -3000), R("SYR", -3000), R("IRN", -3000), R("POL", -3400, "the Bronocice pot"), R("SVN", -3150,
    "the Ljubljana Marshes wheel"), R("DEU", -3400), R("NLD", -3000), R("DNK", -3000), R("CHE", -3000),
    R("HUN", -3000), R("UKR", -3000, "Yamnaya wagons"), R("RUS", -3000), R("KAZ", -2500), R("FRA", -2500),
    R("ITA", -2500), R("GRC", -2500), R("ESP", -2000), R("GBR", -2000), R("EGY", -1650, "with the chariot"),
    R("INDUS", -2600, "bullock carts of the Indus towns"), R("CHN", -1700, "wheel ruts at Erlitou"),
    R("MNG", -1200), R("KOR", -300), R("JPN", 700), R("VNM", -500), R("KHM", 800), R("IDN", 800), R("LKA", -300),
    R("SDN", 1880), R("ETH", 1900)],
    lost=[R("ARAB_LANDS", 500, 1850)],
    not_before=[R("SSA", 1880, "carts came with colonial roads"), R("ZAF", 1652, "the Dutch Cape")]))
add(T("horses", "horses", "land", "farm", 200, source="Domestication of the horse", fame=3, origins=[
    R("RUS", -2200, "the lower Volga and Don", (47.5, 42.0))], records=[
    R("UKR", -2200), R("KAZ", -2000), R("TUR", -2000), R("IRQ", -2000), R("SYR", -2000), R("IRN", -2000),
    R("EGY", -1650, "the Hyksos"), R("GRC", -1900), R("DEU", -1900), R("FRA", -1900), R("GBR", -1900),
    R("ESP", -1900), R("ITA", -1900), R("IND", -1500), R("PAK", -1500), R("CHN", -1600), R("MNG", -1200),
    R("KOR", -300), R("JPN", 400), R("VNM", -300), R("THA", 500), R("IDN", 800), R("SAU", -1000), R("YEM", -1000),
    R("SDN", -700, "Kush"), R("ETH", 300), R("SAHEL", 1000, "across the Sahara"), R("NGA", 1100),
    R("CUB", 1493), R("DOM", 1493), R("HTI", 1493), R("MEX", 1519), R("PER", 1532), R("ARG", 1536),
    R("CHL", 1541), R("COL", 1525), R("VEN", 1520), R("BRA", 1534), R("USA", 1540, "Coronado", (35.0, -106.0)),
    R("CAN", 1665), R("AUS", 1788), R("NZL", 1814)],
    not_before=[R("SSA", 1900, "tsetse flies kill horses"), R("ZAF", 1652), R("LSO", 1830), R("BWA", 1850),
                R("NAM", 1850), R("MDG", 1850)]))
add(T("chariot", "war chariots", "war", "weapon", 100, source="Chariot", needs=["wheel", "horses"], only=True,
      origins=[R("RUS", -2000, "Sintashta", (52.5, 60.0)), R("KAZ", -2000)], records=[
      R("TUR", -1700, "the Hittites"), R("SYR", -1700), R("IRQ", -1800), R("EGY", -1650), R("GRC", -1600),
      R("CHN", -1200, "Anyang"), R("IND", -1500), R("PAK", -1500), R("IRN", -1500), R("CYP", -1400),
      R("GBR", -300), R("FRA", -500), R("IRL", -300)],
      lost=[R("MENA", -300, 3000), R("GRC", -1100, 3000), R("CHN", -200, 3000), R("IND", 400, 3000),
            R("PAK", 400, 3000), R("GBR", 100, 3000), R("FRA", -50, 3000), R("IRL", 400, 3000), R("RUS", -800, 3000),
            R("KAZ", -800, 3000), R("CYP", -300, 3000)]))
add(T("camels", "camel caravans", "land", "infra", 100, source="Camel train", only=True, fame=2, origins=[
    R("SAU", -1000, "Arabia"), R("YEM", -1000), R("OMN", -1000), R("ARE", -1000), R("TKM", -2500,
    "Bactrian camels"), R("UZB", -2500), R("KAZ", -2000), R("MNG", -1000), R("IRN", -1000), R("AFG", -1000)],
    records=[R("JOR", -900), R("SYR", -900), R("IRQ", -900), R("ISR", -900), R("PSX", -900), R("KWT", -900),
    R("QAT", -900), R("BHR", -900), R("EGY", -500), R("SOM", -1000), R("SOL", -1000), R("DJI", -1000),
    R("ERI", -1000), R("ETH", -500), R("SDN", -100), R("LBY", 200), R("TUN", 200), R("DZA", 200), R("MAR", 200),
    R("SAH", 200), R("MRT", 300), R("MLI", 300), R("NER", 300), R("TCD", 300), R("PAK", -1000),
    R("IND", -500, "Rajasthan", (27.0, 72.0)), R("CHN", -500, "the Silk Road", (40.0, 94.0)), R("KGZ", -1000),
    R("TJK", -1000), R("TUR", 1000), R("AUS", 1840, "camels for the outback", (-25.0, 134.0))],
    game={"vehicles": ["CARAVAN"]}))
add(T("coaches", "horse carriages", "land", "infra", 100, source="Coach (carriage)", needs=["wheel", "horses"],
      fame=2, origins=[R("HUN", 1450, "the kocsi of Kocs", (47.6, 18.2))], records=[
      R("AUT", 1500), R("DEU", 1500), R("FRA", 1550), R("ITA", 1550), R("GBR", 1555), R("ESP", 1550),
      R("NLD", 1550), R("POL", 1550), R("RUS", 1600), R("SWE", 1600), R("MEX", 1550), R("PER", 1600),
      R("USA", 1700), R("BRA", 1700), R("IND", 1800), R("TUR", 1700), R("EGY", 1850), R("JPN", 1870),
      R("CHN", 1860, "the treaty ports"), R("KOR", 1885), R("AUS", 1820), R("ZAF", 1700)]))
add(T("bicycle", "bicycles", "land", "home", 30, source="History of the bicycle", fame=2, origins=[
    R("GBR", 1885, "the Rover safety bicycle, Coventry", (52.41, -1.51))], records=[
    R("FRA", 1890), R("DEU", 1890), R("USA", 1890), R("NLD", 1890), R("DNK", 1890), R("IND", 1890),
    R("JPN", 1890), R("CHN", 1897, "Shanghai"), R("VNM", 1900), R("EGY", 1900), R("BRA", 1895), R("AUS", 1890),
    R("RUS", 1890), R("ITA", 1890)], max_share=0.9))
add(T("railway", "the railway", "land", "infra", 40, source="History of rail transport", fame=3,
      needs=["steam_engine"], chat="railline", game={"vehicles": ["TRAIN"], "infra": ["RAILWAY", "RAIL"]},
      origins=[R("GBR", 1825, "the Stockton and Darlington Railway", (54.52, -1.55))], records=[
      R("FRA", 1827, "Saint-Étienne to Andrézieux"), R("USA", 1830, "the Baltimore and Ohio", (39.29, -76.61)),
      R("BEL", 1835, "Brussels to Mechelen"), R("DEU", 1835, "Nuremberg to Fürth", (49.45, 11.08)),
      R("CAN", 1836), R("RUS", 1837, "Tsarskoye Selo", (59.93, 30.32)), R("AUT", 1837), R("CUB", 1837,
      "Havana to Bejucal"), R("NLD", 1839), R("ITA", 1839, "Naples to Portici"), R("CZE", 1839),
      R("CHE", 1847), R("DNK", 1847), R("ESP", 1848), R("HUN", 1846), R("POL", 1845), R("IRL", 1834),
      R("JAM", 1845), R("GUY", 1848), R("MEX", 1850), R("CHL", 1851), R("PER", 1851), R("IND", 1853,
      "Bombay to Thane, 16 April 1853", (18.94, 72.83)), R("IND", 1854, "Howrah, Calcutta", (22.58, 88.34)),
      R("IND", 1856, "Royapuram, Madras", (13.11, 80.29)), R("IND", 1864, "Delhi", (28.66, 77.23)),
      R("IND", 1874, "Wadi to Secunderabad, the Nizam's railway", (17.44, 78.50)), R("RUS", 1851, "Moscow",
      (55.76, 37.66)), R("RUS", 1897, "the Ussuri line to Vladivostok", (43.11, 131.88)), R("USA", 1864,
      "San Francisco to San Jose", (37.77, -122.42)), R("CAN", 1887, "Vancouver", (49.28, -123.12)),
      R("AUS", 1855, "Sydney", (-33.87, 151.21)), R("AUS", 1881, "Fremantle", (-32.05, 115.75)),
      R("BRA", 1867, "Santos to Jundiaí", (-23.55, -46.63)), R("CHN", 1897, "Beijing", (39.90, 116.40)),
      R("CHN", 1898, "Shanghai", (31.23, 121.47)), R("EGY", 1854), R("BRA", 1854), R("NOR", 1854),
      R("AUS", 1854, "Melbourne"), R("PAN", 1855), R("PRT", 1856), R("SWE", 1856), R("ARG", 1857),
      R("ZAF", 1860, "Durban"), R("ROU", 1860), R("PAK", 1861, "Karachi to Kotri"), R("PRY", 1861),
      R("BGD", 1862), R("DZA", 1862), R("NZL", 1863), R("LKA", 1864), R("TUR", 1866, "İzmir to Aydın"),
      R("IDN", 1867), R("URY", 1869), R("TUN", 1872), R("JPN", 1872, "Shimbashi to Yokohama", (35.67, 139.76)),
      R("VEN", 1873), R("MMR", 1877), R("GTM", 1880), R("CHN", 1881, "the Kaiping tramway", (39.6, 118.2)),
      R("SEN", 1885), R("MYS", 1885), R("VNM", 1885), R("IRN", 1888), R("ISR", 1892), R("PHL", 1892),
      R("THA", 1893), R("LBN", 1895), R("SYR", 1895), R("ZWE", 1897), R("COD", 1898), R("NGA", 1898),
      R("KEN", 1901), R("KOR", 1899, "Seoul to Incheon"), R("GHA", 1901), R("SDN", 1899), R("SAU", 1908),
      R("IRQ", 1914), R("ETH", 1917), R("AFG", 1925)]))
add(T("tram", "electric trams", "land", "infra", 30, source="Tram", max_share=0.5, needs=["electricity"], fame=2, origins=[
    R("DEU", 1881, "Gross-Lichterfelde, Berlin", (52.43, 13.31))], records=[
    R("AUT", 1883), R("GBR", 1885, "Blackpool"), R("HUN", 1887), R("USA", 1888, "Richmond, Virginia"),
    R("ITA", 1890), R("FRA", 1890), R("UKR", 1892, "Kyiv"), R("RUS", 1896), R("BRA", 1892), R("THA", 1894),
    R("IND", 1895, "Madras", (13.08, 80.27)), R("JPN", 1895, "Kyoto"), R("EGY", 1896, "Cairo"), R("ARG", 1897),
    R("AUS", 1889), R("MEX", 1900), R("CHN", 1904, "Hong Kong"), R("TUR", 1914)]))
add(T("car", "motor cars", "land", "home", 35, source="History of the automobile", fame=3, chat="vehicle_car",
      chat_sat=0.6, max_share=0.9, game={"vehicles": ["AUTOMOBILE"]}, origins=[
      R("DEU", 1886, "Benz's Motorwagen, Mannheim", (49.49, 8.47))], records=[
      R("FRA", 1891, "Panhard et Levassor"), R("USA", 1893, "the Duryea brothers"), R("GBR", 1895),
      R("AUT", 1893), R("BEL", 1895), R("ITA", 1895), R("CHE", 1895), R("NLD", 1895), R("RUS", 1896),
      R("ZAF", 1896, "Pretoria"), R("AUS", 1896), R("IND", 1898, "Bombay and Calcutta", (18.94, 72.83)),
      R("JPN", 1898), R("BRA", 1893), R("ARG", 1892), R("MEX", 1895), R("IRN", 1900), R("CHN", 1901, "Shanghai"),
      R("EGY", 1904), R("THA", 1902), R("KOR", 1903), R("TUR", 1900)]))
add(T("bus", "motor buses", "land", "infra", 30, source="Bus", needs=["car"], fame=2, origins=[
    R("DEU", 1895, "Netphen", (50.9, 8.1))], records=[R("GBR", 1904), R("FRA", 1906), R("USA", 1905),
    R("IND", 1926, "Bombay's BEST buses")]))
add(T("lorry", "lorries", "land", "infra", 30, source="Truck", needs=["car"], chat="vehicle_com",
      game={"vehicles": ["TRUCK"]}, origins=[R("DEU", 1896, "Daimler's motor lorry", (48.78, 9.18))]))
add(T("motorcycle", "motorcycles", "land", "home", 35, source="Motorcycle", needs=["car"], max_share=0.7, origins=[
    R("DEU", 1894, "Hildebrand & Wolfmüller", (48.14, 11.58))], records=[R("FRA", 1898), R("GBR", 1898),
    R("USA", 1901), R("ITA", 1900), R("JPN", 1909), R("IND", 1920)]))
add(T("air_travel", "aeroplanes", "land", "infra", 35, source="Airline", max_share=0.4, needs=["car"], fame=3,
      chat="aviationpkm", game={"vehicles": ["AIRPLANE"], "infra": ["AEROWAY", "RUNWAY"]}, origins=[
      R("USA", 1914, "the St. Petersburg-Tampa Airboat Line; first flight 1903", (27.77, -82.64))], records=[
      R("DEU", 1919), R("GBR", 1919), R("FRA", 1919), R("NLD", 1920), R("COL", 1920, "SCADTA"),
      R("AUS", 1921), R("RUS", 1922), R("BEL", 1923), R("CAN", 1920), R("BRA", 1927), R("ARG", 1927),
      R("MEX", 1921), R("JPN", 1922), R("IND", 1932, "Tata Air Lines", (18.94, 72.83)), R("CHN", 1929),
      R("EGY", 1932), R("ZAF", 1929), R("TUR", 1933), R("IRN", 1927)]))
add(T("motorway", "motorways", "land", "infra", 30, source="Controlled-access highway", max_share=0.6, needs=["car"],
      game={"infra": ["MOTORWAY", "FREEWAY"]}, origins=[R("ITA", 1924, "Milan to Varese", (45.6, 8.9))],
      records=[R("DEU", 1932, "Cologne to Bonn"), R("USA", 1940, "the Pennsylvania Turnpike"), R("NLD", 1937),
      R("FRA", 1946), R("GBR", 1958, "the Preston bypass"), R("JPN", 1963, "the Meishin"), R("ESP", 1969),
      R("BRA", 1947), R("CHN", 1988, "Shanghai to Jiading"), R("IND", 2002, "Mumbai to Pune", (18.94, 72.83)),
      R("TUR", 1973), R("MEX", 1952), R("ARG", 1952), R("KOR", 1968), R("IRN", 1970)]))
add(T("high_speed_rail", "high-speed trains", "land", "infra", 15, source="High-speed rail", max_share=0.3, needs=["railway"],
      only=True, origins=[R("JPN", 1964, "the Tōkaidō Shinkansen", (35.68, 139.77))], records=[
      R("FRA", 1981, "the TGV"), R("ITA", 1977, "the Direttissima"), R("DEU", 1991), R("ESP", 1992),
      R("BEL", 1997), R("GBR", 2003), R("KOR", 2004), R("CHN", 2008, "Beijing to Tianjin"), R("TWN", 2007),
      R("NLD", 2009), R("TUR", 2009), R("RUS", 2009, "the Sapsan"), R("UZB", 2011), R("SAU", 2018),
      R("MAR", 2018), R("IDN", 2023), R("USA", 2000, "the Acela"), R("AUT", 2012), R("CHE", 2007),
      R("SWE", 1990), R("POL", 2014)]))

# ===================================================================================================== water transport
add(T("compass", "the compass", "water", "knowledge", 150, source="Compass", fame=2, origins=[
    R("CHN", 1088, "Shen Kuo's magnetic needle; at sea by 1117")], records=[
    R("GBR", 1190, "Alexander Neckam"), R("FRA", 1190), R("ITA", 1200), R("ESP", 1250), R("PRT", 1250),
    R("IRN", 1232), R("EGY", 1282), R("YEM", 1290), R("KOR", 1300), R("JPN", 1300), R("IND", 1350), R("IDN", 1400),
    R("NLD", 1250), R("DEU", 1250), R("SCANDINAVIA", 1300)]))
add(T("steamship", "steamships", "water", "infra", 50, source="Steamboat", fame=3,
      chat="ship_steam", game={"vehicles": ["STEAMSHIP"]}, origins=[
      R("USA", 1807, "Fulton's Clermont on the Hudson", (40.71, -74.01))], records=[
      R("CAN", 1809, "the Accommodation, Montreal"), R("GBR", 1812, "the Comet on the Clyde"), R("RUS", 1815,
      "the Elizaveta"), R("FRA", 1816), R("DEU", 1816), R("ITA", 1818, "Naples"), R("SWE", 1816), R("NLD", 1823),
      R("IND", 1823, "the Diana, Calcutta", (22.57, 88.36)), R("BRA", 1819), R("ESP", 1817), R("TUR", 1828),
      R("EGY", 1830), R("AUS", 1831, "the Sophia Jane"), R("CHN", 1835, "Canton and Macau"), R("ARG", 1825),
      R("MEX", 1825), R("JPN", 1855), R("ZAF", 1840)]))
add(T("motor_ship", "motor ships", "water", "infra", 30, source="Motor ship", chat="ship_motor",
      replaces=["steamship"], game={"vehicles": ["CARGO_SHIP"]}, origins=[
      R("DNK", 1912, "the Selandia, Copenhagen", (55.68, 12.57))]))

# ======================================================================================================= communication
add(T("post", "the public post", "communication", "infra", 60, source="Mail", fame=2, chat="mail", origins=[
    R("DEU", 1490, "the imperial post of Thurn and Taxis", (50.11, 8.68)), R("GBR", 1635, "the Royal Mail opened to all")],
    records=[R("FRA", 1630), R("ESP", 1580), R("ITA", 1550), R("AUT", 1500), R("NLD", 1600), R("SWE", 1636),
    R("DNK", 1624), R("RUS", 1665), R("USA", 1692), R("CAN", 1755), R("MEX", 1580), R("PER", 1600),
    R("IND", 1774, "Warren Hastings' post; open to the public 1837", (22.57, 88.36)), R("TUR", 1840),
    R("EGY", 1865), R("JPN", 1871, "Maejima Hisoka's post"), R("CHN", 1896, "the Imperial Post"),
    R("BRA", 1663), R("ARG", 1748), R("AUS", 1809), R("ZAF", 1792), R("IRN", 1865), R("THA", 1883),
    R("KOR", 1884)]))
add(T("semaphore", "semaphore towers", "communication", "infra", 15, source="Semaphore line", max_share=0.1, only=True,
      needs=["telescope"], origins=[R("FRA", 1794, "Chappe's line from Paris to Lille", (48.86, 2.35))], records=[
      R("SWE", 1794, "Edelcrantz"), R("GBR", 1796, "the Admiralty shutter telegraph"), R("DNK", 1801),
      R("NLD", 1798), R("BEL", 1798), R("ITA", 1800), R("ESP", 1844), R("DEU", 1832, "Berlin to Koblenz"),
      R("RUS", 1824, "Saint Petersburg"), R("POL", 1839), R("EGY", 1823)],
      lost=[R("EUROPE", 1860, 3000), R("EGY", 1860, 3000)]))
add(T("telegraph", "the telegraph", "communication", "infra", 25, source="Electrical telegraph", fame=3,
      chat="telegram", replaces=["semaphore"], origins=[R("GBR", 1839, "Paddington to West Drayton",
      (51.52, -0.18))], records=[
      R("USA", 1844, "Morse: Washington to Baltimore", (38.90, -77.04)), R("FRA", 1845), R("CAN", 1846),
      R("AUT", 1847), R("DEU", 1849), R("BEL", 1846), R("NLD", 1845), R("ITA", 1847), R("ESP", 1852),
      R("RUS", 1852), R("SWE", 1853), R("IND", 1851, "Calcutta to Diamond Harbour", (22.57, 88.36)),
      R("MEX", 1851), R("BRA", 1852, "Rio de Janeiro"), R("CHL", 1852), R("AUS", 1854, "Melbourne"),
      R("TUR", 1855, "Istanbul to Edirne"), R("EGY", 1854), R("ARG", 1857), R("IRN", 1858), R("ZAF", 1859),
      R("LKA", 1858), R("JPN", 1869, "Tokyo to Yokohama"), R("CHN", 1871, "the Shanghai cable"),
      R("THA", 1875), R("KOR", 1885), R("ETH", 1897)]))
add(T("telephone", "the telephone", "communication", "home", 30, source="History of the telephone", fame=3,
      chat="telephone", chat_sat=0.5, max_share=0.95, origins=[
      R("USA", 1877, "Bell's telephone; the first exchange at New Haven in 1878", (42.36, -71.06))], records=[
      R("CAN", 1878), R("GBR", 1879), R("FRA", 1879), R("BRA", 1879), R("AUS", 1880), R("DEU", 1881),
      R("ARG", 1881), R("NZL", 1881), R("ITA", 1881), R("RUS", 1882), R("IND", 1882, "Calcutta, Bombay and Madras",
      (22.57, 88.36)), R("CHN", 1882, "Shanghai"), R("MEX", 1882), R("ZAF", 1882), R("EGY", 1884), R("IRN", 1886),
      R("JPN", 1890, "the Tokyo-Yokohama exchange"), R("THA", 1881), R("KOR", 1898), R("TUR", 1909)]))
add(T("radio", "radio", "communication", "home", 20, source="History of radio", fame=3, chat="radio",
      chat_sat=0.8, max_share=0.95, origins=[R("NLD", 1919, "PCGG, The Hague", (52.08, 4.30)),
      R("USA", 1920, "KDKA, Pittsburgh", (40.44, -79.99)), R("ARG", 1920, "Radio Argentina, Buenos Aires")],
      records=[R("CAN", 1920), R("FRA", 1921), R("MEX", 1921), R("GBR", 1922, "the BBC"), R("CHE", 1922),
      R("BRA", 1922), R("CHL", 1922), R("URY", 1922), R("CUB", 1922), R("NZL", 1922), R("RUS", 1922),
      R("DEU", 1923), R("BEL", 1923), R("CZE", 1923), R("AUS", 1923), R("IND", 1923, "the Radio Club of Bombay",
      (18.94, 72.83)), R("CHN", 1923, "Shanghai"), R("ZAF", 1923), R("AUT", 1924), R("ITA", 1924), R("ESP", 1924),
      R("JPN", 1925), R("SWE", 1925), R("DNK", 1925), R("NOR", 1925), R("POL", 1925), R("FIN", 1926),
      R("PER", 1925), R("LKA", 1925), R("EGY", 1925), R("TUR", 1927), R("KEN", 1928), R("COL", 1929),
      R("THA", 1930), R("GHA", 1935), R("IRQ", 1936), R("PAK", 1937, "Lahore"), R("BGD", 1939, "Dhaka"),
      R("IRN", 1940), R("SAU", 1949), R("NPL", 1951)]))
add(T("television", "television", "communication", "home", 20, source="Timeline of the introduction of television in countries",
      fame=3, needs=["electricity"], chat="tv", chat_sat=0.5, max_share=0.95, origins=[
      R("DEU", 1935, "Fernsehsender Paul Nipkow, Berlin", (52.52, 13.40)), R("GBR", 1936, "the BBC, London"),
      R("FRA", 1935)], records=[
      R("RUS", 1938), R("USA", 1939, "NBC, New York"), R("MEX", 1950), R("BRA", 1950, "TV Tupi"), R("CUB", 1950),
      R("ARG", 1951), R("NLD", 1951), R("DNK", 1951), R("CAN", 1952), R("VEN", 1952), R("POL", 1952),
      R("JPN", 1953, "NHK"), R("BEL", 1953), R("CHE", 1953), R("CZE", 1953), R("PHL", 1953), R("ITA", 1954),
      R("COL", 1954), R("SWE", 1954), R("THA", 1955), R("AUT", 1955), R("AUS", 1956), R("ESP", 1956),
      R("KOR", 1956), R("IRQ", 1956), R("PRT", 1957), R("HUN", 1957), R("CHL", 1957), R("CHN", 1958, "Beijing"),
      R("IRN", 1958), R("PER", 1958), R("IND", 1959, "Doordarshan, Delhi", (28.61, 77.21)), R("NGA", 1959),
      R("EGY", 1960), R("NZL", 1960), R("KEN", 1962), R("TWN", 1962), R("IDN", 1962), R("MYS", 1963),
      R("SGP", 1963), R("PAK", 1964), R("BGD", 1964), R("ETH", 1964), R("GHA", 1965), R("SAU", 1965),
      R("ISR", 1966), R("MNG", 1967), R("TUR", 1968), R("ZAF", 1976), R("LKA", 1979), R("NPL", 1985),
      R("BTN", 1999)]))
add(T("colour_tv", "colour television", "communication", "home", 15, source="Color television",
      needs=["television"], replaces=["television"], origins=[R("USA", 1954, "NTSC colour broadcasts")], records=[
      R("JPN", 1960), R("CAN", 1966), R("GBR", 1967), R("DEU", 1967), R("FRA", 1967), R("NLD", 1967),
      R("RUS", 1967), R("THA", 1967), R("BRA", 1972), R("CHN", 1973), R("NZL", 1973), R("AUS", 1975),
      R("ZAF", 1976), R("PAK", 1976), R("ITA", 1977), R("IDN", 1979), R("ARG", 1980), R("KOR", 1980),
      R("IND", 1982, "the Asian Games, Delhi"), R("TUR", 1984)]))
add(T("cinema", "picture houses", "communication", "infra", 25, source="History of film", fame=3, origins=[
    R("FRA", 1895, "the Lumière brothers, Paris", (48.87, 2.33)), R("DEU", 1895, "the Skladanowsky brothers, Berlin")],
    records=[R("GBR", 1896), R("USA", 1896), R("BEL", 1896), R("RUS", 1896), R("IND", 1896,
    "Watson's Hotel, Bombay, 7 July 1896", (18.93, 72.83)), R("EGY", 1896), R("JPN", 1896), R("CHN", 1896,
    "Shanghai"), R("AUS", 1896), R("BRA", 1896), R("MEX", 1896), R("ARG", 1896), R("ZAF", 1896), R("TUR", 1897),
    R("THA", 1897), R("CUB", 1897), R("IRN", 1904), R("KOR", 1903)]))
add(T("photography", "photographs", "communication", "craft", 40, source="History of photography", fame=2, origins=[
    R("FRA", 1839, "Daguerre's daguerreotype", (48.86, 2.35)), R("GBR", 1839, "Fox Talbot")], records=[
    R("USA", 1839), R("DEU", 1839), R("EGY", 1839, "Horace Vernet in Alexandria"), R("RUS", 1840),
    R("IND", 1840, "Calcutta", (22.57, 88.36)), R("BRA", 1840, "Rio de Janeiro"), R("MEX", 1840), R("AUS", 1842),
    R("IRN", 1844), R("CHN", 1844, "Macau and Canton"), R("TUR", 1845), R("ZAF", 1846), R("JPN", 1857),
    R("THA", 1860), R("KOR", 1883)]))
add(T("newspaper", "printed newspapers", "communication", "home", 60, source="History of newspapers", fame=3,
      needs=["printing_press"], chat="newspaper", chat_sat=0.3, max_share=0.9, origins=[
      R("FRA", 1605, "the Relation of Strasbourg, then in the Holy Roman Empire", (48.58, 7.75))], records=[
      R("DEU", 1609), R("NLD", 1618), R("GBR", 1621), R("BEL", 1620), R("ITA", 1640), R("ESP", 1641),
      R("PRT", 1641), R("SWE", 1645), R("POL", 1661), R("DNK", 1666), R("RUS", 1702), R("USA", 1704),
      R("MEX", 1722), R("PER", 1715), R("CAN", 1752), R("IND", 1780, "Hicky's Bengal Gazette", (22.57, 88.36)),
      R("ZAF", 1800), R("ARG", 1801), R("AUS", 1803), R("BRA", 1808), R("PHL", 1811), R("CHL", 1812),
      R("GHA", 1822), R("EGY", 1828), R("TUR", 1831), R("IRN", 1837), R("THA", 1844), R("IDN", 1744),
      R("NGA", 1859), R("VNM", 1865), R("JPN", 1870, "the Yokohama Mainichi"), R("CHN", 1872, "the Shenbao"),
      R("KOR", 1883), R("KEN", 1902), R("ETH", 1902)]))
add(T("gramophone", "gramophones", "communication", "home", 30, source="Phonograph", origins=[
    R("USA", 1877, "Edison's phonograph"), R("DEU", 1889, "Berliner's gramophone records")], records=[
    R("GBR", 1898), R("FRA", 1898), R("RUS", 1900), R("IND", 1902, "the first Indian recordings, Calcutta"),
    R("JPN", 1903), R("CHN", 1903)], max_share=0.6))

# ================================================================================================ writing and knowledge
add(T("indus_script", "the Indus script", "writing", "knowledge", 200, source="Indus script", only=True, origins=[
    R("PAK", -2600, "Harappa and Mohenjo-daro", (27.32, 68.14)), R("IND", -2600, "Dholavira and Rakhigarhi",
    (29.29, 76.11))], lost=[R("INDUS", -1900, 3000)]))
add(T("writing", "writing", "writing", "knowledge", 400, source="History of writing", fame=2, origins=[
    R("IRQ", -3200, "Sumerian cuneiform"), R("EGY", -3200, "hieroglyphs"),
    R("CHN", -1250, "oracle bones of the Shang"), R("MEX", -600, "Zapotec signs, Oaxaca", (17.06, -96.72)),
    R("MEX", -300, "Maya writing in Yucatán", (20.68, -88.57)), R("MEX", 1300, "Aztec writing, Tenochtitlan",
    (19.43, -99.13)),
    R("GTM", -300, "Maya writing at San Bartolo")], records=[
    R("IND", -300, "Brahmi, the edicts of Ashoka", (25.61, 85.14)), R("PAK", -500, "Aramaic, then Kharosthi"),
    R("BTN", 700, "with Buddhism"), R("IRN", -3000, "Proto-Elamite"),
    R("SYR", -2400, "Ebla"), R("TUR", -1900, "Assyrian traders at Kültepe"), R("GRC", -1800, "Linear A"),
    R("CYP", -1500), R("ISR", -1700), R("LBN", -1700), R("JOR", -1700), R("PSX", -1700), R("YEM", -800),
    R("SAU", -500), R("OMN", -500), R("ETH", -700), R("ERI", -700), R("SDN", -800), R("ITA", -700, "Etruscan"),
    R("ESP", -600), R("FRA", -600, "Greek Massalia"), R("GBR", 43, "the Romans"), R("DEU", 50),
    R("IRL", 400, "Ogham"), R("DNK", 150, "runes"), R("SWE", 200), R("NOR", 200), R("CZE", 863), R("BGR", 870),
    R("RUS", 950), R("UKR", 950), R("POL", 966), R("HUN", 1000), R("ROU", 1000), R("SRB", 900), R("FIN", 1200),
    R("EST", 1225), R("LVA", 1225), R("LTU", 1300), R("NPL", -250), R("LKA", -250), R("BGD", -250),
    R("AFG", -500), R("UZB", -500), R("TKM", -500), R("MNG", 735, "the Orkhon inscriptions"), R("KAZ", 750),
    R("KOR", -100), R("JPN", 400), R("VNM", -100), R("KHM", 611), R("THA", 600), R("MMR", 500), R("IDN", 400),
    R("MYS", 500), R("PHL", 900, "the Laguna Copperplate"), R("LAO", 1350), R("MLI", 1100), R("NER", 1100),
    R("TCD", 1100), R("NGA", 1100), R("SEN", 1050), R("MRT", 1050), R("KEN", 1150), R("TZA", 1150),
    R("SOM", 1000), R("MDG", 1500), R("AGO", 1491, "the Kingdom of Kongo"), R("COD", 1491),
    R("ZAF", 1652), R("BLZ", -300), R("HND", 400, "Copán"), R("SLV", 0), R("NZL", 1814), R("AUS", 1788)],
    lost=[R("GRC", -1100, -800)]))
add(T("paper", "paper", "writing", "craft", 150, source="History of paper", fame=2, needs=["writing"], origins=[
    R("CHN", 105, "Cai Lun's paper, reported to the emperor", (34.62, 112.45)),
    R("MEX", -300, "amate bark paper of central Mexico", (19.43, -99.13)),
    R("MEX", 300, "bark-paper books of the Maya", (20.68, -88.57))], records=[
    R("KOR", 500), R("JPN", 610, "the monk Damjing"), R("VNM", 300), R("IND", 650,
    "through Tibet and Nepal; common under the Delhi Sultanate", (28.61, 77.21)), R("NPL", 650), R("BTN", 700),
    R("UZB", 751, "Samarkand"), R("TJK", 751), R("KGZ", 800), R("TKM", 800), R("KAZ", 800), R("AFG", 800),
    R("IRN", 800), R("IRQ", 793, "Baghdad's first paper mill"), R("SYR", 800), R("LBN", 850), R("ISR", 850),
    R("JOR", 850), R("SAU", 850), R("YEM", 900), R("EGY", 900, "Fustat"), R("LBY", 950), R("TUN", 950),
    R("DZA", 1000), R("MAR", 1100, "Fez"), R("ESP", 1056, "Xàtiva"), R("PRT", 1100), R("ITA", 1109,
    "Sicily; the Fabriano mills from 1276"), R("GRC", 1050), R("TUR", 1100), R("FRA", 1200), R("DEU", 1300),
    R("GBR", 1310), R("NLD", 1350), R("BEL", 1350), R("CHE", 1400), R("AUT", 1350), R("CZE", 1350),
    R("POL", 1350), R("HUN", 1350), R("RUS", 1400), R("SWE", 1400), R("DNK", 1400), R("NOR", 1450),
    R("FIN", 1450), R("PAK", 1000), R("BGD", 1200), R("LKA", 1200), R("MNG", 1200), R("THA", 1350),
    R("KHM", 1300), R("MMR", 1300), R("LAO", 1400), R("MYS", 1400), R("IDN", 1500), R("PHL", 1565, "the Spanish"),
    R("MLI", 1300, "Timbuktu's manuscripts"), R("NER", 1300), R("TCD", 1300), R("NGA", 1300), R("SEN", 1300),
    R("MRT", 1200), R("SDN", 1300), R("SOM", 1300), R("KEN", 1300), R("TZA", 1300), R("MDG", 1600),
    R("ETH", 1850), R("GTM", 400), R("BLZ", 400), R("HND", 400), R("SLV", 400), R("ZAF", 1652)]))
add(T("woodblock", "woodblock printing", "writing", "knowledge", 150, source="Woodblock printing",
      needs=["paper"], only=True, origins=[R("CHN", 700, "the Tang; the Diamond Sutra of 868")], records=[
      R("KOR", 751, "the Mugujeonggwang Dharani"), R("JPN", 770, "the Hyakumantō Darani"),
      R("VNM", 1250), R("MNG", 1250), R("EGY", 950, "Arabic block prints"), R("DEU", 1400),
      R("ITA", 1400), R("NLD", 1420), R("FRA", 1420), R("GBR", 1470), R("BEL", 1420)],
      lost=[R("EGY", 1400, 3000)]))
add(T("movable_type", "movable type", "writing", "knowledge", 150, source="Movable type", needs=["paper"],
      only=True, origins=[R("CHN", 1040, "Bi Sheng's clay type")], records=[
      R("KOR", 1234, "metal type; the Jikji of 1377"), R("JPN", 1593, "Korean type")]))
add(T("printing_press", "printed books", "writing", "knowledge", 100, source="Global spread of the printing press",
      fame=3, needs=["paper"], origins=[R("DEU", 1440, "Gutenberg, Mainz", (50.0, 8.27))], records=[
      R("ITA", 1465, "Subiaco"), R("CHE", 1468, "Basel"), R("CZE", 1468, "Plzeň"), R("FRA", 1470, "Paris"),
      R("NLD", 1470, "Utrecht"), R("ESP", 1472, "Segovia"), R("BEL", 1473, "Aalst"), R("HUN", 1473, "Buda"),
      R("POL", 1473, "Kraków"), R("GBR", 1476, "Caxton at Westminster"), R("AUT", 1482, "Vienna"),
      R("DNK", 1482, "Odense"), R("SWE", 1483, "Stockholm"), R("PRT", 1487, "Faro"), R("TUR", 1493,
      "the Hebrew press of Istanbul; Ottoman Turkish printing from 1727"), R("MNE", 1494, "Cetinje"),
      R("ROU", 1508), R("LTU", 1522, "Vilnius"), R("ISL", 1530), R("MEX", 1539, "Mexico City"),
      R("IRL", 1551), R("SRB", 1552), R("IND", 1556, "Goa, the first press in Asia", (15.50, 73.83)),
      R("BLR", 1562), R("RUS", 1564, "Ivan Fyodorov's Apostol, Moscow"), R("UKR", 1574, "Lviv"),
      R("ISR", 1577, "Safed"), R("PER", 1584, "Lima"), R("LVA", 1588), R("CHN", 1588, "the Jesuits at Macau"),
      R("JPN", 1590, "the Jesuit press"), R("PHL", 1593, "Manila"), R("LBN", 1610), R("BOL", 1610),
      R("EST", 1631), R("IRN", 1638, "New Julfa"), R("USA", 1638, "Cambridge, Massachusetts", (42.37, -71.11)),
      R("FIN", 1642), R("NOR", 1643), R("GTM", 1660), R("PRY", 1700, "the Jesuit missions"), R("SYR", 1706),
      R("CUB", 1707), R("LKA", 1736), R("COL", 1738), R("CAN", 1751), R("ECU", 1755), R("ARG", 1765),
      R("CHL", 1776), R("ZAF", 1795), R("AUS", 1795), R("EGY", 1798, "the French; Bulaq from 1820"),
      R("GRC", 1798), R("BRA", 1808), R("VEN", 1808), R("BGR", 1840), R("MDG", 1826), R("NZL", 1830),
      R("NGA", 1846), R("ETH", 1863), R("THA", 1836), R("KOR", 1883)],
      not_before=[R("ARAB_LANDS", 1800), R("SAU", 1882), R("YEM", 1877), R("AFG", 1870), R("@Central Asia", 1860),
                  R("MNG", 1913), R("BTN", 1950), R("NPL", 1851)]))
add(T("eyeglasses", "spectacles", "writing", "home", 200, source="Glasses", fame=1, needs=["glass"], max_share=0.3,
      origins=[R("ITA", 1286, "Pisa", (43.72, 10.40))], records=[
      R("FRA", 1300), R("DEU", 1300), R("GBR", 1320), R("NLD", 1350), R("ESP", 1350), R("TUR", 1450),
      R("IRN", 1450), R("CHN", 1450), R("IND", 1520), R("JPN", 1551, "Francis Xavier's gift"), R("KOR", 1580)]))
add(T("clock_tower", "a clock tower", "writing", "infra", 150, source="History of timekeeping devices", fame=2,
      origins=[R("GBR", 1283, "Dunstable Priory", (51.89, -0.52)), R("CHN", 1092, "Su Song's clock tower, Kaifeng",
      (34.80, 114.31))], records=[
      R("ITA", 1336, "Milan"), R("FRA", 1370, "Paris"), R("DEU", 1350), R("ESP", 1350), R("NLD", 1350),
      R("RUS", 1404, "the Moscow Kremlin"), R("CZE", 1410, "the Prague Orloj"), R("POL", 1400), R("HUN", 1400),
      R("SWE", 1400), R("DNK", 1400), R("PRT", 1400), R("TUR", 1550), R("JPN", 1600), R("IND", 1615),
      R("KOR", 1669), R("MEX", 1550), R("PER", 1600), R("USA", 1700), R("BRA", 1700)],
      lost=[R("CHN", 1127, 1601)]))
add(T("pocket_watch", "pocket watches", "writing", "home", 150, source="Pocket watch", needs=["clock_tower"],
      max_share=0.4, origins=[R("DEU", 1510, "Peter Henlein, Nuremberg", (49.45, 11.08))], records=[
      R("FRA", 1550), R("CHE", 1600), R("GBR", 1580), R("ITA", 1550), R("NLD", 1600), R("JPN", 1600),
      R("CHN", 1601), R("IND", 1700), R("TUR", 1600), R("RUS", 1700), R("USA", 1700)]))
add(T("telescope", "telescopes", "writing", "knowledge", 200, source="History of the telescope", fame=1,
      needs=["glass"], origins=[R("NLD", 1608, "Lippershey, Middelburg", (51.5, 3.61))], records=[
      R("ITA", 1609, "Galileo"), R("GBR", 1609, "Harriot"), R("FRA", 1609), R("DEU", 1610), R("ESP", 1610),
      R("JPN", 1613, "John Saris' gift to Tokugawa Ieyasu"), R("IND", 1616), R("TUR", 1620), R("IRN", 1620),
      R("CHN", 1626), R("KOR", 1631)]))

# ================================================================================================================== war
add(T("stirrup", "stirrups", "war", "weapon", 100, source="Stirrup", needs=["horses"], origins=[
    R("CHN", 300, "the Jin dynasty")], records=[R("KOR", 400), R("JPN", 450), R("MNG", 400), R("HUN", 568,
    "the Avars"), R("GRC", 600), R("TUR", 600), R("IRN", 600), R("IRQ", 694), R("SYR", 700), R("EGY", 700),
    R("ITA", 650), R("FRA", 700), R("DEU", 700), R("ESP", 710), R("GBR", 900), R("SCANDINAVIA", 800),
    R("POL", 900), R("RUS", 800), R("IND", 650), R("PAK", 650), R("SAHEL", 1000), R("ETH", 1000)]))
add(T("crossbow", "crossbows", "war", "weapon", 80, source="Crossbow", fame=2, origins=[
    R("CHN", -450, "the Warring States")], records=[R("VNM", -250), R("KOR", -100), R("GRC", -400,
    "the gastraphetes"), R("ITA", 300), R("FRA", 950), R("GBR", 1066, "the Normans"), R("DEU", 1000),
    R("ESP", 1000), R("SYR", 1100), R("EGY", 1100), R("IRQ", 1100), R("TUR", 1100), R("IRN", 1100),
    R("RUS", 1100), R("POL", 1100), R("SCANDINAVIA", 1100), R("JPN", 600), R("GAB", 1600), R("CMR", 1600),
    R("CAF", 1600), R("MEX", 1519), R("PER", 1532)], game={"items": ["crossbow"]}))
add(T("siege_engines", "siege engines", "war", "weapon", 100, source="Siege engine", origins=[
    R("IRQ", -850, "Assyrian rams and towers")], records=[
    R("SYR", -850), R("ISR", -700), R("IRN", -600), R("EGY", -700), R("GRC", -400, "the catapults of Dionysius"),
    R("ITA", -300), R("CHN", -400, "traction trebuchets"), R("IND", -300), R("TUR", -500), R("FRA", 0),
    R("ESP", 0), R("GBR", 50), R("DEU", 300), R("RUS", 1000), R("POL", 1000), R("KOR", 600), R("JPN", 700),
    R("MNG", 1210)], lost=[R("EUROPE", 1550, 3000), R("MENA", 1550, 3000), R("CHN", 1550, 3000),
    R("IND", 1600, 3000)], game={"vehicles": ["SIEGE_ENGINE"]}))
add(T("chain_mail", "mail armour", "war", "weapon", 100, source="Mail (armour)", needs=["iron"], origins=[
    R("ROU", -400, "Celtic smiths", (46.0, 24.0))], records=[R("FRA", -300), R("ITA", -250), R("GRC", -200),
    R("DEU", -200), R("GBR", -100), R("ESP", -200), R("TUR", 0), R("IRN", 0), R("SYR", 0), R("EGY", 0),
    R("IND", 100), R("RUS", 900), R("SCANDINAVIA", 300), R("POL", 900), R("JPN", 1300), R("CHN", 400),
    R("SAHEL", 1300)], lost=[R("EUROPE", 1650, 3000)], game={"items": ["chainmail_armor"]}))
add(T("plate_armour", "plate armour", "war", "weapon", 60, source="Plate armour", needs=["steel"], only=True,
      origins=[R("ITA", 1400, "Milan", (45.46, 9.19)), R("DEU", 1400)], records=[R("FRA", 1410), R("GBR", 1420),
      R("ESP", 1420), R("AUT", 1420), R("POL", 1450), R("HUN", 1450), R("NLD", 1430), R("BEL", 1430),
      R("CZE", 1430), R("SWE", 1450), R("DNK", 1450), R("RUS", 1550), R("MEX", 1519), R("PER", 1532)],
      lost=[R("EUROPE", 1700, 3000), R("MEX", 1700, 3000), R("PER", 1700, 3000)], game={"items": ["iron_armor"]}))
add(T("gunpowder", "gunpowder", "war", "weapon", 80, source="Gunpowder", fame=2, origins=[
    R("CHN", 850, "the formula of the alchemists; fire lances by 950")], records=[
    R("MNG", 1220), R("IRN", 1250), R("IRQ", 1258), R("EGY", 1280, "al-Rammah's treatise"), R("SYR", 1280),
    R("KOR", 1377, "Choe Mu-seon"), R("JPN", 1274, "the Mongol bombs"), R("GBR", 1267, "Roger Bacon"),
    R("DEU", 1300), R("FRA", 1300), R("ITA", 1326, "Florence"), R("ESP", 1331), R("MAR", 1300), R("TUR", 1350),
    R("IND", 1300, "brought by the Mongols", (28.61, 77.21)), R("RUS", 1382), R("POL", 1383), R("VNM", 1390),
    R("IDN", 1350, "Majapahit"), R("THA", 1450), R("MMR", 1450), R("PHL", 1500), R("ETH", 1520),
    R("SAHEL", 1570, "Bornu's musketeers"), R("NGA", 1570), R("KEN", 1500), R("TZA", 1500), R("MEX", 1519),
    R("PER", 1532), R("NZL", 1807, "the Musket Wars")]))
add(T("cannon", "cannons", "war", "weapon", 60, source="Cannon", fame=2, needs=["gunpowder"], origins=[
    R("CHN", 1288, "the Heilongjiang hand cannon")], records=[
    R("ITA", 1326, "Florence"), R("GBR", 1327, "the Milemete picture"), R("FRA", 1338), R("DEU", 1340),
    R("ESP", 1343, "Algeciras"), R("EGY", 1365), R("KOR", 1377), R("RUS", 1382), R("POL", 1383),
    R("VNM", 1390), R("TUR", 1400), R("IRN", 1450), R("IND", 1500), R("JPN", 1576)]))
add(T("matchlock", "matchlock guns", "war", "weapon", 50, source="Matchlock", fame=2, needs=["gunpowder"],
      origins=[R("DEU", 1450, "the arquebus"), R("FRA", 1450)], records=[
      R("TUR", 1450), R("ESP", 1480), R("ITA", 1480), R("RUS", 1480), R("GBR", 1490), R("EGY", 1490),
      R("POL", 1500), R("IND", 1510, "the Portuguese at Goa; Babur in 1526", (15.50, 73.83)), R("MYS", 1511),
      R("IRN", 1520), R("THA", 1520), R("IDN", 1520), R("MEX", 1519), R("PER", 1532), R("ETH", 1530),
      R("SOM", 1529), R("MMR", 1540), R("JPN", 1543, "Tanegashima"), R("CHN", 1548), R("MAR", 1550),
      R("SAHEL", 1570), R("NGA", 1570), R("AGO", 1510), R("GHA", 1600), R("KOR", 1593)]))
add(T("flintlock", "flintlock muskets", "war", "weapon", 50, source="Flintlock", needs=["gunpowder"],
      replaces=["matchlock"], origins=[R("FRA", 1610, "Marin le Bourgeoys", (49.18, -0.37))], records=[
      R("GBR", 1640), R("NLD", 1640), R("USA", 1640), R("DEU", 1660), R("ESP", 1700), R("RUS", 1700),
      R("TUR", 1700), R("SWE", 1680), R("GHA", 1700, "trade guns"), R("NGA", 1700), R("IND", 1740), R("IRN", 1740),
      R("NZL", 1807), R("CHN", 1840), R("JPN", 1854)]))
add(T("rifle", "breech-loading rifles", "war", "weapon", 30, source="Dreyse needle gun", needs=["gunpowder"],
      replaces=["flintlock", "matchlock"], origins=[R("DEU", 1841, "the Dreyse needle gun, Prussia",
      (52.52, 13.40))], records=[R("USA", 1860), R("FRA", 1866), R("GBR", 1866), R("AUT", 1867),
      R("IND", 1867), R("RUS", 1868), R("ITA", 1870), R("EGY", 1870), R("ESP", 1871), R("TUR", 1874),
      R("CHN", 1875), R("JPN", 1880), R("ZAF", 1875), R("ETH", 1885)]))
add(T("machine_gun", "machine guns", "war", "weapon", 25, source="Maxim gun", needs=["rifle"], origins=[
    R("GBR", 1884, "Hiram Maxim, London", (51.51, -0.13))], records=[R("DEU", 1892), R("RUS", 1895),
    R("FRA", 1897), R("USA", 1890), R("JPN", 1897), R("CHN", 1900), R("ETH", 1896)]))
add(T("tank", "tanks", "war", "weapon", 20, source="Tank", needs=["car"], game={"vehicles": ["TANK"]}, origins=[
    R("GBR", 1916, "the Somme", (50.0, 2.7))], records=[R("FRA", 1917), R("DEU", 1918), R("USA", 1918),
    R("ITA", 1918), R("RUS", 1920), R("POL", 1920), R("JPN", 1927), R("CZE", 1925), R("SWE", 1921),
    R("CHN", 1929), R("IND", 1938)]))
add(T("fireworks", "fireworks", "crafts", "home", 150, source="Fireworks", needs=["gunpowder"], max_share=0.5,
      origins=[R("CHN", 1000, "the Song")], records=[R("KOR", 1400), R("JPN", 1613), R("IND", 1450,
      "Vijayanagara", (15.33, 76.46)), R("ITA", 1379), R("DEU", 1400), R("FRA", 1450), R("GBR", 1486),
      R("ESP", 1500), R("RUS", 1700), R("THA", 1500), R("VNM", 1450), R("IDN", 1500), R("IRN", 1500),
      R("TUR", 1500)], game={"items": ["firework_rocket"]}))

# ============================================================================================================= medicine
add(T("smallpox_vaccine", "vaccination against smallpox", "medicine", "medicine", 40, source="Smallpox vaccine",
      fame=2, origins=[R("GBR", 1796, "Edward Jenner, Berkeley", (51.69, -2.46))], records=[
      R("AUT", 1799), R("FRA", 1800), R("DEU", 1800), R("ITA", 1800), R("ESP", 1800), R("NLD", 1800),
      R("USA", 1800, "Benjamin Waterhouse, Boston"), R("DNK", 1801), R("SWE", 1801), R("RUS", 1801),
      R("IND", 1802, "Bombay, June 1802", (18.94, 72.83)), R("LKA", 1802), R("BGD", 1802), R("ZAF", 1803),
      R("MEX", 1804, "the Balmis expedition"), R("VEN", 1804), R("COL", 1804), R("CUB", 1804), R("BRA", 1804),
      R("AUS", 1804), R("ARG", 1805), R("PHL", 1805), R("CHN", 1805, "Macau and Canton"), R("PER", 1806),
      R("EGY", 1827), R("IRN", 1829), R("TUR", 1840), R("JPN", 1849, "Nagasaki"), R("THA", 1840),
      R("KOR", 1879)]))
add(T("anaesthesia", "surgery with anaesthesia", "medicine", "medicine", 30, source="History of general anesthesia",
      origins=[R("USA", 1846, "ether at Massachusetts General Hospital", (42.36, -71.07)),
      R("JPN", 1804, "Hanaoka Seishū's tsūsensan")], records=[R("GBR", 1846), R("FRA", 1847), R("DEU", 1847),
      R("AUT", 1847), R("RUS", 1847), R("IND", 1847, "Calcutta"), R("AUS", 1847), R("BRA", 1847), R("CHN", 1848),
      R("TUR", 1847), R("EGY", 1850)]))
add(T("antiseptic", "clean surgery", "medicine", "medicine", 30, source="Antiseptic", origins=[
    R("GBR", 1867, "Joseph Lister, Glasgow", (55.86, -4.25))], records=[R("DEU", 1872), R("FRA", 1875),
    R("USA", 1876), R("AUT", 1875), R("RUS", 1880), R("JPN", 1880), R("IND", 1885)]))
add(T("xray", "X-ray machines", "medicine", "medicine", 25, source="X-ray", needs=["electricity"], origins=[
    R("DEU", 1895, "Wilhelm Röntgen, Würzburg", (49.79, 9.93))], records=[R("AUT", 1896), R("FRA", 1896),
    R("GBR", 1896), R("USA", 1896), R("RUS", 1896), R("ITA", 1896), R("CAN", 1896), R("AUS", 1896),
    R("JPN", 1896), R("ARG", 1896), R("CHN", 1897), R("BRA", 1897), R("EGY", 1897), R("IND", 1898, "Calcutta")]))
add(T("antibiotics", "penicillin", "medicine", "medicine", 15, source="Penicillin", fame=2, origins=[
    R("GBR", 1941, "Oxford; found by Fleming in 1928", (51.75, -1.25)), R("USA", 1942)], records=[
    R("RUS", 1943), R("JPN", 1944), R("CAN", 1944), R("AUS", 1944), R("FRA", 1945), R("DEU", 1946),
    R("IND", 1945), R("CHN", 1945), R("BRA", 1945), R("EGY", 1946)]))
add(T("child_vaccines", "vaccines for children", "medicine", "medicine", 20, source="DPT vaccine",
      chat="pctimmunizdpt", chat_sat=100.0, origins=[R("USA", 1948, "the DTP vaccine")], records=[
      R("GBR", 1950), R("CAN", 1950)]))
add(T("ct_scanner", "hospital scanners", "medicine", "medicine", 20, source="CT scan", needs=["computer", "xray"],
      chat="med_catscanner", origins=[R("GBR", 1971, "Atkinson Morley's Hospital, London", (51.42, -0.21))],
      records=[R("USA", 1973)]))

# ============================================================================================================= textiles
add(T("spinning_wheel", "spinning wheels", "textiles", "home", 150, source="Spinning wheel", max_share=0.8,
      origins=[R("IRQ", 1000, "the Islamic world"), R("IRN", 1000)], records=[
      R("SYR", 1000), R("EGY", 1050), R("TUR", 1100), R("CHN", 1090), R("ESP", 1250), R("ITA", 1270),
      R("DEU", 1280, "Speyer"), R("FRA", 1280), R("GBR", 1300), R("NLD", 1300), R("IND", 1300), R("PAK", 1300),
      R("RUS", 1450), R("JPN", 1500), R("KOR", 1500), R("MEX", 1530), R("PER", 1550)],
      not_before=[R("SSA", 1850), R("ETH", 1600)]))
add(T("cotton_mill", "cotton mills", "textiles", "infra", 50, source="Textile manufacture during the British Industrial Revolution", max_share=0.3,
      fame=2, chat="spindle_mule", origins=[R("GBR", 1771, "Arkwright's Cromford Mill", (53.11, -1.56))], records=[
      R("FRA", 1785), R("DEU", 1784, "Ratingen"), R("USA", 1790, "Slater Mill, Pawtucket"), R("BEL", 1798),
      R("RUS", 1799), R("CHE", 1801), R("AUT", 1801), R("ESP", 1802), R("IND", 1818, "Fort Gloster near Calcutta; Bombay 1854",
      (22.57, 88.36)), R("EGY", 1818, "Muhammad Ali's mills"), R("MEX", 1835, "Puebla"), R("TUR", 1845),
      R("BRA", 1844), R("JPN", 1867, "Kagoshima"), R("CHN", 1890, "Shanghai"), R("ITA", 1810)]))
add(T("sewing_machine", "sewing machines", "textiles", "home", 40, source="Sewing machine", max_share=0.6, origins=[
    R("FRA", 1830, "Barthélemy Thimonnier"), R("USA", 1851, "Singer")], records=[R("GBR", 1856),
    R("DEU", 1860), R("RUS", 1865), R("BRA", 1865), R("JPN", 1860), R("IND", 1875), R("CHN", 1880),
    R("EGY", 1880)]))
add(T("synthetic_fibre", "nylon", "textiles", "home", 30, source="Nylon", chat="txtlmat_synth", origins=[
    R("USA", 1939, "DuPont's stockings")], records=[R("DEU", 1939, "Perlon"), R("GBR", 1941), R("JPN", 1942),
    R("IND", 1962)]))
add(T("silk", "silk weaving", "textiles", "craft", 200, source="History of silk", only=True, origins=[
    R("CHN", -3000)], records=[R("KOR", -200), R("JPN", 300), R("IND", 300), R("IRN", 400),
    R("GRC", 552, "Byzantium's silkworms"), R("TUR", 552), R("SYR", 600), R("LBN", 600), R("ESP", 900,
    "al-Andalus"), R("ITA", 1147, "Sicily; Lucca by 1200"), R("FRA", 1466, "Lyon"), R("UZB", 400), R("VNM", -100),
    R("THA", 1300), R("BGD", 1600, "Bengal"), R("MEX", 1530)]))

# =============================================================================================================== crafts
add(T("glass", "glass", "crafts", "craft", 300, source="History of glass", fame=1, origins=[
    R("IRQ", -2500, "Mesopotamian glass beads")], records=[
    R("SYR", -1500), R("EGY", -1500), R("IRN", -1200), R("GRC", -1400), R("ITA", -700), R("ISR", -50,
    "glassblowing"), R("LBN", -50), R("IND", -1000), R("PAK", -1000), R("CHN", -500), R("KOR", -200),
    R("JPN", 200), R("FRA", 50), R("DEU", 50), R("GBR", 50), R("ESP", 0), R("TUR", -500), R("RUS", 1000),
    R("POL", 1000), R("CZE", 1100), R("NGA", 1000, "Ile-Ife beads"), R("THA", 1000), R("VNM", 0)],
    not_before=[R("SSA", 1800)]))
add(T("porcelain", "porcelain", "crafts", "craft", 100, source="Porcelain", only=True, fame=1, origins=[
    R("CHN", 600, "the Sui and Tang; Jingdezhen from 1004")], records=[
    R("KOR", 1100), R("VNM", 1300), R("JPN", 1616, "Arita"), R("DEU", 1710, "Meissen"), R("AUT", 1718),
    R("ITA", 1720), R("RUS", 1744), R("GBR", 1745), R("FRA", 1740), R("ESP", 1760), R("SWE", 1759),
    R("DNK", 1775), R("NLD", 1757), R("USA", 1826), R("IND", 1900)]))
add(T("matches", "matches", "crafts", "home", 30, source="Match", origins=[
    R("GBR", 1826, "John Walker, Stockton-on-Tees", (54.57, -1.32))], records=[R("AUT", 1833), R("DEU", 1833),
    R("FRA", 1832), R("USA", 1836), R("SWE", 1845, "Jönköping"), R("RUS", 1840), R("IND", 1870),
    R("JPN", 1876), R("CHN", 1880)]))
add(T("plastics", "plastic", "crafts", "home", 30, source="Bakelite", origins=[
    R("USA", 1907, "Leo Baekeland's Bakelite")], records=[R("DEU", 1910), R("GBR", 1910), R("JPN", 1915),
    R("IND", 1950)]))
add(T("candles", "candles", "lighting", "home", 200, source="Candle", max_share=0.9, origins=[
    R("ITA", -500, "Roman tallow candles"), R("CHN", -221, "the Qin")], records=[
    R("GRC", -300), R("EGY", -300), R("FRA", 0), R("ESP", 0), R("GBR", 50), R("DEU", 100), R("IND", 100),
    R("JPN", 700), R("KOR", 500), R("RUS", 1000), R("IRN", 300), R("TUR", 0), R("SYR", 0), R("SCANDINAVIA", 800)],
    game={"items": ["candle"]}))
add(T("pencil", "pencils", "crafts", "home", 80, source="Pencil", max_share=0.8, origins=[
    R("GBR", 1565, "Borrowdale graphite", (54.5, -3.15))], records=[R("DEU", 1662, "Nuremberg"),
    R("FRA", 1795, "Conté"), R("USA", 1812), R("JPN", 1887), R("IND", 1900), R("CHN", 1930)]))
add(T("fountain_pen", "fountain pens", "crafts", "home", 40, source="Fountain pen", max_share=0.5, origins=[
    R("USA", 1884, "Waterman, New York")], records=[R("GBR", 1890), R("DEU", 1900), R("JPN", 1910), R("IND", 1905)]))
add(T("ballpoint_pen", "ballpoint pens", "crafts", "home", 15, source="Ballpoint pen", replaces=["fountain_pen"],
      origins=[R("ARG", 1945, "Bíró's pens, Buenos Aires", (-34.6, -58.38))], records=[R("USA", 1945),
      R("FRA", 1950, "Bic"), R("GBR", 1946)]))
add(T("typewriter", "typewriters", "home", "home", 40, source="Typewriter", max_share=0.3, origins=[
    R("USA", 1874, "the Remington")], records=[R("GBR", 1880), R("DEU", 1880), R("FRA", 1880), R("RUS", 1890),
    R("IND", 1900), R("JPN", 1915)]))
add(T("safety_razor", "safety razors", "home", "home", 30, source="Safety razor", max_share=0.8, origins=[
    R("USA", 1904, "Gillette")], records=[R("GBR", 1905), R("FRA", 1905), R("DEU", 1910), R("IND", 1925)]))

# ================================================================================================================= home
add(T("electric_fan", "electric fans", "home", "home", 25, source="Fan (machine)", needs=["electricity"],
      max_share=0.9, origins=[R("USA", 1882, "Schuyler Wheeler")], records=[R("GBR", 1890), R("IND", 1900),
      R("JPN", 1894)]))
add(T("washing_machine", "washing machines", "home", "home", 25, source="Washing machine", needs=["electricity"],
      max_share=0.9, origins=[R("USA", 1908, "the electric washer")], records=[R("GBR", 1920), R("DEU", 1951),
      R("JPN", 1953), R("IND", 1985), R("CHN", 1985)]))
add(T("vacuum_cleaner", "vacuum cleaners", "home", "home", 25, source="Vacuum cleaner", needs=["electricity"],
      max_share=0.8, origins=[R("GBR", 1901, "Hubert Cecil Booth")], records=[R("USA", 1908, "Hoover"),
      R("DEU", 1920), R("JPN", 1931)]))
add(T("air_conditioning", "air conditioning", "home", "home", 30, source="Air conditioning", needs=["electricity"],
      max_share=0.8, origins=[R("USA", 1902, "Willis Carrier, Buffalo")], records=[R("JPN", 1935),
      R("IND", 1960), R("SGP", 1960), R("SAU", 1960), R("CHN", 1985)]))
add(T("microwave", "microwave ovens", "home", "home", 15, source="Microwave oven", needs=["electricity"],
      max_share=0.9, origins=[R("USA", 1967, "the Amana Radarange")], records=[R("JPN", 1966), R("GBR", 1974),
      R("DEU", 1975), R("IND", 1990), R("CHN", 1990)]))
add(T("video_recorder", "video recorders", "home", "home", 12, source="VHS", needs=["television"],
      max_share=0.8, origins=[R("JPN", 1976, "JVC's VHS")], records=[R("USA", 1977), R("GBR", 1978),
      R("DEU", 1978), R("IND", 1982)], lost=[R("EUROPE", 2012, 3000), R("@Northern America", 2012, 3000),
      R("JPN", 2012, 3000)]))
add(T("cd_player", "compact discs", "home", "home", 12, source="Compact disc", needs=["electricity"],
      max_share=0.8, origins=[R("JPN", 1982, "Sony and Philips"), R("DEU", 1982)], records=[R("USA", 1983),
      R("GBR", 1983), R("IND", 1990)]))
add(T("escalator", "moving stairs", "building", "infra", 40, source="Escalator", max_share=0.4, needs=["electricity"], origins=[
    R("USA", 1896, "Coney Island", (40.57, -73.98))], records=[R("GBR", 1898, "Harrods"), R("FRA", 1900),
    R("DEU", 1925), R("JPN", 1914), R("RUS", 1935, "the Moscow Metro"), R("IND", 1960)]))
add(T("traffic_lights", "traffic lights", "land", "infra", 30, source="Traffic light", needs=["electricity", "car"],
      origins=[R("USA", 1914, "Cleveland", (41.5, -81.69))], records=[R("GBR", 1927), R("DEU", 1924),
      R("FRA", 1923), R("JPN", 1930), R("IND", 1953)]))
add(T("electric_car", "electric cars", "land", "home", 25, source="Electric car", needs=["car", "electricity"],
      max_share=0.6, origins=[R("USA", 2008, "the Tesla Roadster")], records=[R("JPN", 2010, "the Nissan Leaf"),
      R("NOR", 2011), R("CHN", 2012), R("DEU", 2013), R("GBR", 2011), R("NLD", 2012), R("FRA", 2012),
      R("IND", 2017)]))
add(T("digital_camera", "digital cameras", "home", "home", 10, source="Digital camera", max_share=0.7, origins=[
    R("JPN", 1994), R("USA", 1994)], records=[R("DEU", 1996), R("GBR", 1996), R("CHN", 2000),
    R("IND", 2002)]))

# ============================================================================================================ computing
add(T("computer", "computers", "computing", "infra", 30, source="History of computing hardware", max_share=0.5,
      needs=["electricity"], fame=2, origins=[R("USA", 1945, "ENIAC, Philadelphia", (39.95, -75.19)),
      R("GBR", 1944, "Colossus, Bletchley Park")], records=[R("UKR", 1950, "MESM, Kyiv"), R("AUS", 1949),
      R("DEU", 1950), R("FRA", 1955), R("JPN", 1956), R("RUS", 1952), R("CHN", 1958), R("IND", 1960,
      "TIFRAC, Bombay"), R("BRA", 1957), R("ISR", 1955), R("NLD", 1952), R("SWE", 1953)]))
add(T("personal_computer", "home computers", "computing", "home", 15, source="Personal computer",
      needs=["computer"], chat="computer", chat_sat=0.6, max_share=0.9, origins=[R("USA", 1977,
      "the Apple II, PET and TRS-80")], records=[R("GBR", 1980), R("JPN", 1979), R("DEU", 1980),
      R("FRA", 1981), R("IND", 1985), R("CHN", 1985)]))
add(T("mobile_phone", "mobile phones", "computing", "home", 10, source="Mobile phone", fame=3, needs=["electricity"],
      chat="cellphone", chat_sat=1.0, max_share=0.98, origins=[R("JPN", 1979, "NTT's network in Tokyo",
      (35.68, 139.77))], records=[R("SWE", 1981), R("NOR", 1981), R("DNK", 1981), R("FIN", 1981),
      R("SAU", 1981), R("USA", 1983, "Chicago"), R("GBR", 1985), R("DEU", 1985), R("CAN", 1985), R("CHN", 1987),
      R("IND", 1995, "Calcutta, July 1995", (22.57, 88.36)), R("BRA", 1990), R("NGA", 1992)]))
add(T("internet", "the internet", "computing", "home", 10, source="History of the Internet", fame=3,
      needs=["computer", "telephone"], chat="internetuser", chat_sat=1.0, max_share=0.97, origins=[
      R("USA", 1983, "the ARPANET goes over to TCP/IP")], records=[R("GBR", 1988), R("NLD", 1988),
      R("DEU", 1989), R("AUS", 1989), R("JPN", 1989), R("FRA", 1988), R("IND", 1995, "VSNL, 15 August 1995"),
      R("CHN", 1994), R("BRA", 1991), R("RUS", 1990), R("ZAF", 1991), R("EGY", 1993), R("NGA", 1996)]))
add(T("smartphone", "smartphones", "computing", "home", 7, source="Smartphone", fame=3,
      needs=["mobile_phone", "internet"], replaces=["mobile_phone"], max_share=0.95, origins=[
      R("USA", 2007, "the iPhone")], records=[R("GBR", 2007), R("DEU", 2007), R("JPN", 2008), R("CHN", 2009),
      R("IND", 2010), R("BRA", 2009), R("NGA", 2010)]))
add(T("satnav", "satellite maps", "computing", "home", 8, source="Global Positioning System", needs=["mobile_phone"],
      max_share=0.9, origins=[R("USA", 2000, "GPS opened to everyone")], records=[R("DEU", 2004), R("JPN", 2001),
      R("GBR", 2004), R("CHN", 2010), R("IND", 2010)]))
add(T("atm", "cash machines", "computing", "infra", 15, source="Automated teller machine", needs=["computer"],
      chat="atm", origins=[R("GBR", 1967, "Barclays, Enfield", (51.65, -0.08))], records=[R("USA", 1969),
      R("JPN", 1969), R("SWE", 1967), R("DEU", 1968), R("IND", 1987, "HSBC, Bombay", (18.94, 72.83)),
      R("CHN", 1987)]))
add(T("bank_card", "bank cards", "computing", "home", 15, source="Payment card", chat="creditdebit", chat_sat=100.0,
      max_share=0.95, origins=[R("USA", 1950, "the Diners Club card")], records=[R("GBR", 1966),
      R("FRA", 1967), R("JPN", 1961), R("DEU", 1968), R("IND", 1980), R("CHN", 1985)]))
