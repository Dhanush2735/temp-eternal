#!/usr/bin/env python3
"""Step 19a: write the money table (which money a place used in a year, its coins, a day's pay).

Writes eternal/src/main/resources/data/eternalengine/eternal/economy/money_table.json.

Rules of the file (MoneyTable.java reads it):
  * "kind": coins, weighed (metal by weight), barter (goods swapped) or local (a fallback that names no coins:
    amounts show as "local money worth about N days' work"). Barter and local count hundredths of a day of work.
  * "name" labels amounts ("1 rupee (Osmania sicca)"); "called" is the name in a sentence ("Money here: the
    denarius").
  * Amounts are whole numbers of a money's smallest unit ("size" 1). A unit may have "from"/"to" years: it is only
    named in those years (the kurus is not named before 1688).
  * "decimals" (weighed money only): the smallest named unit is shown with that many decimals; the stored amount is
    then counted in tenths (decimals 1) of it.
  * "pay": [year, day's pay in the smallest unit] anchors for an ordinary labourer; read in straight lines between
    them and held flat beyond the first and the last.
  * Rows: "money", "from"/"to" years (BCE negative, both inclusive), "where" (any one matcher is enough):
        {"rulerIn": 1947, "names": [...]}   the ruler of this point in 1947 is one of the names
        {"ruler": [...]}                   the ruler of this point in the year asked is one of the names
        {"box": [latMin, lonMin, latMax, lonMax]}
        {"world": true}
    One matcher may hold several keys ({"ruler": [...], "box": [...]}): then all of them must hold.
    The row with the highest "priority" wins; on a tie the earlier row.
  * "accepts": other money taken there too. "rates": fixed exchange rates (aAmount of a = bAmount of b, in
    smallest units). Without a rate, monies compare by a day's pay.
  * "estimate": true marks guessed numbers. Notes are for developers only: the game never shows them, and the
    player never sees where a number came from.
"""
import json
import os

OUT = "/home/user/eternal/src/main/resources/data/eternalengine/eternal/economy/money_table.json"


def unit(name, plural, size, frm=None, to=None):
    u = {"name": name, "plural": plural, "size": size}
    if frm is not None:
        u["from"] = frm
    if to is not None:
        u["to"] = to
    return u


MASS_NOUNS = ("goods to trade", "weighed silver", "copper by weight", "copper cash", "cacao beans", "cowrie shells",
              "silver and copper coins")


def called(name):
    """The name as a sentence uses it: "the denarius", "the Indian rupee", but "weighed silver", "cacao beans"."""
    return name if name in MASS_NOUNS else "the " + name


def money(id_, name, kind, units, pay, estimate=True, note="", metal=None, decimals=0, short=None):
    m = {"id": id_, "name": name, "called": called(name), "kind": kind, "units": units, "pay": pay,
         "estimate": estimate}
    if short:
        m["short"] = short
    if metal:
        m["metal"] = metal
    if decimals:
        m["decimals"] = decimals
    if note:
        m["note"] = note
    return m


RUPEE_ANNA_PAI = [unit("rupee", "rupees", 192), unit("anna", "annas", 12), unit("pai", "pai", 1)]

CURRENCIES = [
    money("barter", "goods to trade", "barter",
          [unit("day of work", "days of work", 100)], [[-100000, 100]], estimate=False,
          note="No money: people swap goods. Amounts are hundredths of a day of work and show as goods worth"
               " about N days of work."),
    money("silver_weighed", "weighed silver", "weighed",
          [unit("mina", "minas", 10800), unit("shekel", "shekels", 180), unit("grain", "grains", 1)],
          [[-2600, 6], [-539, 6]], metal="silver",
          note="1 shekel = 180 grains (se), 1 mina = 60 shekels. Laws of Hammurabi 273: a hired labourer 6 grains"
               " of silver a day in the first five months of the year, 5 grains after. Held flat for the whole period."),
    money("egypt_deben", "copper by weight", "weighed",
          [unit("deben", "deben", 100), unit("kite", "kite", 10)], [[-2000, 40], [-333, 40]],
          metal="copper", decimals=1,
          note="1 deben = 10 kite (qedet). Deir el-Medina workmen (New Kingdom) got about 5.5 khar of grain a"
               " month; a khar of emmer cost about 2 copper deben: about 11 deben a month, near 4 kite a day."),
    money("drachma", "Greek drachma", "coins",
          [unit("drachma", "drachmae", 48), unit("obol", "obols", 8), unit("chalkous", "chalkoi", 1)],
          [[-600, 24], [-450, 48], [-329, 72], [296, 72]],
          note="1 drachma = 6 obols = 48 chalkoi (Athens). Erechtheion accounts 409-406 BCE: 1 drachma a day for"
               " skilled and unskilled alike; Eleusis accounts 329 BCE: unskilled 1.5 drachmae. -600 is a guess."),
    money("denarius", "Roman denarius", "coins",
          [unit("aureus", "aurei", 400, -46), unit("denarius", "denarii", 16), unit("sestertius", "sestertii", 4),
           unit("as", "asses", 1)],
          [[-211, 10], [-70, 12], [30, 16], [200, 24], [295, 32]],
          note="From 141 BCE 1 denarius = 4 sestertii = 16 asses; 1 aureus = 25 denarii (regular from Caesar)."
               " Cicero (Pro Roscio Comoedo): a labourer 12 asses a day; Matthew 20: a denarius a day. Later"
               " anchors are guesses (the 3rd-century debasement is not modelled)."),
    money("solidus", "Byzantine solidus", "coins",
          [unit("solidus", "solidi", 288), unit("miliaresion", "miliaresia", 24), unit("follis", "folles", 1)],
          [[296, 10], [600, 12], [1453, 12]],
          note="6th-7th c.: 1 solidus = 12 miliaresia = 288 folles. A labourer near 1/24 solidus a day: a guess."),
    money("dirham", "dirham", "coins",
          [unit("dinar", "dinars", 480), unit("dirham", "dirhams", 24), unit("fals", "fulus", 1)],
          [[650, 24], [1500, 24]],
          note="Gold dinar, silver dirham, copper fals. The dinar was 10 dirhams early and 20 or more later; 20 is"
               " used. 24 fulus to the dirham and a dirham a day for a labourer are guesses."),
    money("toman", "Persian toman", "coins",
          [unit("toman", "tomans", 10000), unit("abbasi", "abbasis", 200), unit("shahi", "shahis", 50),
           unit("dinar", "dinars", 1)],
          [[1501, 100], [1700, 150], [1850, 500], [1931, 2000]],
          note="Safavid-Qajar money of account: 1 toman = 50 abbasi = 200 shahi = 10,000 dinar. Wages are guesses."),
    money("akce", "Ottoman akçe", "coins",
          [unit("kuruş", "kuruş", 120, 1688), unit("para", "para", 3, 1620), unit("akçe", "akçe", 1)],
          [[1326, 2], [1450, 3], [1550, 6], [1600, 10], [1700, 25], [1800, 90], [1843, 240]],
          note="Ottoman silver akce; para = 3 akce (from the 1620s), kurus = 40 para (from 1688). Unskilled wages"
               " near 3 akce (1450) and 6 (1550) are rough; later anchors follow the debasements, roughly."),
    money("kurus", "Ottoman kuruş", "coins",
          [unit("lira", "lira", 4000), unit("kuruş", "kuruş", 40), unit("para", "para", 1)],
          [[1844, 200], [1900, 400], [1914, 480], [1922, 2000]],
          note="From 1844: 1 lira = 100 kurus, 1 kurus = 40 para. Wages are guesses."),
    money("pound_lsd", "pound sterling", "coins",
          [unit("pound", "pounds", 960), unit("shilling", "shillings", 48), unit("penny", "pence", 4),
           unit("farthing", "farthings", 1, 1279)],
          [[800, 4], [1260, 6], [1349, 8], [1400, 12], [1450, 16], [1540, 16], [1600, 32], [1650, 48], [1750, 56],
           [1800, 80], [1850, 96], [1900, 192], [1914, 240], [1920, 480], [1939, 400], [1950, 800], [1970, 2400]],
          note="1 pound = 20 shillings = 240 pence = 960 farthings. An English building labourer's day: about 1.5d"
               " (1260s), 3-4d after the Black Death, 8d (1600), 12d (1650s); later anchors rough."),
    money("gbp", "pound sterling", "coins",
          [unit("pound", "pounds", 100), unit("penny", "pence", 1)],
          [[1971, 300], [1990, 3500], [2000, 5000], [2026, 10000]],
          note="Decimal pound from 15 February 1971. Wages are guesses (an unskilled day)."),
    money("livre", "French livre", "coins",
          [unit("livre", "livres", 240), unit("sou", "sous", 12), unit("denier", "deniers", 1)],
          [[800, 6], [1300, 12], [1500, 30], [1600, 96], [1700, 120], [1789, 240], [1794, 300]],
          note="1 livre = 20 sous = 240 deniers. A Paris labourer near 20 sous a day in 1789; earlier anchors rough."),
    money("franc", "French franc", "coins",
          [unit("franc", "francs", 100), unit("centime", "centimes", 1)],
          [[1795, 150], [1850, 200], [1900, 400], [1914, 500], [1930, 3000], [1950, 60000], [1959, 100000]],
          note="Franc = 100 centimes (old francs until 1959). Wages are guesses."),
    money("new_franc", "French franc", "coins",
          [unit("franc", "francs", 100), unit("centime", "centimes", 1)],
          [[1960, 1500], [1980, 10400], [2001, 35000]],
          note="New franc (100 old) from 1960. Wages are guesses."),
    money("euro", "euro", "coins",
          [unit("euro", "euros", 100), unit("cent", "cents", 1)],
          [[2002, 7000], [2026, 11000]],
          note="Euro from 2002. Wages are guesses."),
    money("thaler", "thaler", "coins",
          [unit("thaler", "thalers", 288), unit("groschen", "groschen", 12), unit("pfennig", "pfennigs", 1)],
          [[1500, 18], [1550, 24], [1650, 48], [1750, 72], [1850, 120], [1872, 150]],
          note="1 thaler = 24 groschen = 288 pfennigs (Saxon reckoning; it varied by state). Wages are guesses."),
    money("mark", "German mark", "coins",
          [unit("mark", "marks", 100), unit("pfennig", "pfennigs", 1)],
          [[1873, 200], [1914, 400], [1938, 600], [1948, 800]],
          note="Mark = 100 pfennigs (Reichsmark from 1924; the 1923 inflation is not modelled). Wages are guesses."),
    money("deutsche_mark", "Deutsche Mark", "coins",
          [unit("mark", "marks", 100), unit("pfennig", "pfennigs", 1)],
          [[1948, 1000], [1970, 5000], [2001, 15000]],
          note="Deutsche Mark from June 1948. Wages are guesses."),
    money("peso_real", "Spanish peso", "coins",
          [unit("peso", "pesos", 272, 1497), unit("real", "reales", 34), unit("maravedí", "maravedís", 1)],
          [[1497, 68], [1600, 102], [1700, 136], [1800, 204], [1868, 272]],
          note="Peso (piece of eight) = 8 reales; 1 real = 34 maravedis (1497). Wages are rough guesses."),
    money("china_cash", "copper cash", "coins",
          [unit("tael of silver", "taels of silver", 1000, 1400), unit("string of cash", "strings of cash", 1000, -221, 1399),
           unit("bronze coin", "bronze coins", 1, None, -222), unit("cash", "cash", 1, -221)],
          [[-600, 20], [-200, 20], [100, 30], [700, 40], [1100, 100], [1400, 30], [1600, 40], [1750, 50],
           [1850, 100], [1911, 150]],
          note="Round copper cash (wen); 1,000 cash on a string; the silver tael near 1,000 cash (it went from"
               " about 700 to 2,000). Song common labourer near 100 cash a day; the rest are guesses."),
    money("yuan_rep", "Chinese yuan", "coins",
          [unit("yuan", "yuan", 100), unit("fen", "fen", 1)],
          [[1912, 30], [1948, 50]],
          note="Republican silver dollar (yuan) = 100 fen (the 1940s inflation is not modelled). Guesses."),
    money("rmb", "Chinese yuan", "coins",
          [unit("yuan", "yuan", 100), unit("fen", "fen", 1)],
          [[1949, 100], [1980, 150], [2000, 2000], [2026, 20000]],
          note="Renminbi yuan = 10 jiao = 100 fen. Wages are guesses."),
    money("mon", "Japanese mon", "coins",
          [unit("kan", "kan", 1000), unit("mon", "mon", 1)],
          [[708, 10], [1200, 30], [1600, 100], [1700, 150], [1800, 250], [1870, 400]],
          note="Copper mon, 1,000 to the kan (a string). Wages were told in mon; the gold ryo (officially 4,000"
               " mon from 1601; markets varied) is left out. Wages are guesses (an Edo labourer near 200-300 mon)."),
    money("yen", "Japanese yen", "coins",
          [unit("yen", "yen", 100), unit("sen", "sen", 1, None, 1953)],
          [[1871, 15], [1900, 40], [1930, 150], [1950, 20000], [1970, 150000], [2000, 800000], [2026, 1000000]],
          note="Yen = 100 sen (sen out of use from 1953). Wages are guesses."),
    money("dollar", "US dollar", "coins",
          [unit("dollar", "dollars", 100), unit("cent", "cents", 1)],
          [[1792, 75], [1850, 100], [1900, 150], [1920, 400], [1940, 400], [1950, 800], [1970, 2000],
           [2000, 6000], [2026, 12000]],
          note="US dollar = 100 cents. An unskilled day; guesses."),
    money("ruble", "Russian ruble", "coins",
          [unit("ruble", "rubles", 100), unit("kopek", "kopeks", 1)],
          [[1535, 3], [1700, 5], [1800, 15], [1900, 80], [1917, 120]],
          note="Ruble = 100 kopeks (1535 reform). Wages are guesses."),
    money("cacao", "cacao beans", "coins",
          [unit("load of cacao", "loads of cacao", 24000), unit("cacao bean", "cacao beans", 1)],
          [[900, 100], [1600, 100]],
          note="Cacao beans as small change (Aztec, early colonial); a load (carga) = 24,000 beans. A day's pay of"
               " about 100 beans is a guess."),
    money("cowrie", "cowrie shells", "coins",
          [unit("cowrie", "cowries", 1)],
          [[1000, 100], [1500, 200], [1850, 1000], [1900, 2000]],
          note="Cowrie shells as money in West Africa; they lost value as more were shipped in. Guesses."),
    money("pana", "pana", "coins",
          [unit("pana", "panas", 64), unit("mashaka", "mashakas", 4), unit("kakani", "kakanis", 1)],
          [[-600, 11], [1335, 11]],
          note="Arthashastra: 1 pana = 16 mashakas, 1 mashaka = 4 kakanis; the lowest servants 60 panas a year"
               " (about 1/6 pana a day). Kept as the money of account after the Mauryas: a simplification."),
    money("tanka", "tanka", "coins",
          [unit("tanka", "tankas", 48), unit("jital", "jitals", 1)],
          [[1206, 2], [1526, 2]],
          note="Delhi Sultanate silver tanka = 48 copper jitals (Iltutmish). A day's pay of 2 jitals is a guess"
               " (Akbar's 2 dams were about 2.4 jitals)."),
    money("hun", "hun", "coins",
          [unit("hun", "huns", 160), unit("fanam", "fanams", 16), unit("kasu", "kasu", 1)],
          [[1336, 8], [1724, 8]],
          note="Gold hun (pagoda, varaha), fanam and copper kasu (cash). Ratios varied by place (later Madras: 42"
               " fanams to the pagoda); 10 fanams and 16 kasu are simplifications. Half a fanam a day is a guess."),
    money("mughal_rupee", "Mughal rupee", "coins",
          [unit("rupee", "rupees", 1000), unit("dam", "dams", 25), unit("jital", "jitals", 1)],
          [[1540, 50], [1595, 50], [1700, 75], [1857, 100]],
          note="Sher Shah's rupiya and dam; Ain-i-Akbari (1595): 1 rupee = 40 dams, 1 dam = 25 jitals (of"
               " account); an ordinary labourer 2 dams a day. Later anchors are guesses."),
    money("sicca", "sicca rupee", "coins", RUPEE_ANNA_PAI,
          [[1674, 12], [1724, 12], [1800, 18], [1857, 24]],
          note="Rupee = 16 annas = 192 pai, as the Deccan, the Marathas and Bengal reckoned in the 1700s. Wages"
               " are guesses (1-2 annas a day)."),
    money("hali_sicca", "Hali sicca", "coins", RUPEE_ANNA_PAI,
          [[1858, 24], [1890, 30], [1917, 48]], short="Hali",
          note="Hyderabad's Hali sicca rupee (from 1858), 16 annas of 12 pai. Wages are guesses (2-4 annas)."),
    money("osmania_sicca", "Osmania sicca", "coins", RUPEE_ANNA_PAI,
          [[1918, 60], [1939, 72], [1946, 150], [1948, 192], [1959, 230]],
          short="O.S.",
          note="Hyderabad's Osmania sicca 1918-1959: rupee = 16 annas = 192 pai; from 1950 with the Indian rupee"
               " at 7 O.S. = 6 Indian rupees; demonetised 1959. Agricultural Labour Enquiry 1950-51: casual men"
               " earned 16 annas a day in the south and 13 in central India (Indian rupees; 13.7 Indian annas"
               " = 16 O.S. annas). 1948 = 16 annas is the design anchor (a paper 1 anna, a map 8 annas);"
               " the other anchors are guesses."),
    money("indian_rupee_anna", "Indian rupee", "coins",
          [unit("rupee", "rupees", 192), unit("anna", "annas", 12), unit("pice", "pice", 3), unit("pie", "pies", 1)],
          [[1835, 24], [1870, 30], [1900, 36], [1914, 48], [1939, 72], [1946, 168], [1950, 210], [1956, 216]],
          short="Indian",
          note="Company rupee from 1835, British Indian rupee, then India's rupee until 1956: 1 rupee = 16 annas"
               " = 64 pice = 192 pies. Agricultural Labour Enquiry 1950-51: 17.5 annas a day for casual men, all"
               " India. Earlier anchors are guesses."),
    money("indian_rupee_np", "Indian rupee", "coins",
          [unit("rupee", "rupees", 100), unit("naya paisa", "naye paise", 1)],
          [[1957, 115], [1963, 150]], short="Indian",
          note="Decimal rupee from 1 April 1957: 100 naye paise (just paise from 1964). Wages are guesses."),
    money("indian_rupee", "Indian rupee", "coins",
          [unit("rupee", "rupees", 100), unit("paisa", "paise", 1)],
          [[1964, 160], [1970, 250], [1980, 500], [1990, 1500], [2000, 4500], [2005, 5000], [2010, 12000],
           [2015, 25000], [2020, 32000], [2026, 42000]], short="Indian",
          note="Rupee = 100 paise. A rural labourer's day; guesses."),
    money("silver_copper", "silver and copper coins", "local",
          [unit("day's pay", "days' pay", 100)], [[-600, 100]], estimate=False,
          note="Fallback where coins were used but no row says which: no coin names are claimed, and amounts"
               " show as coins worth N days of work (hundredths of a day)."),
    money("local_money", "local money", "local",
          [unit("day's pay", "days' pay", 100)], [[1800, 100]], estimate=False,
          note="Fallback after 1800 where no row names the money: no names are claimed, and amounts show as"
               " local money worth N days of work (hundredths of a day)."),
]

# Places (latMin, lonMin, latMax, lonMax)
SOUTH_ASIA = [5, 60, 37, 98]
NORTH_INDIA = [20, 60, 37, 98]
SOUTH_INDIA = [5, 68, 20, 92]
MESOPOTAMIA = [29, 34, 38.5, 50]
EGYPT = [22, 24.5, 31.7, 35.5]
GREECE = [34.5, 19, 42, 30]
MEDITERRANEAN = [30, -10, 55, 42]
BYZANTINE_CORE = [36, 19, 43, 41]
ISLAMIC_WORLD = [12, -17, 42, 75]
IRAN = [25, 44, 40, 63.5]
BRITAIN = [49.85, -10.7, 61, 1.0]
BRITAIN_EAST = [51.0, 1.0, 61, 2.0]
FRANCE = [42.3, -4.8, 51.1, 8.2]
CENTRAL_EUROPE = [45.5, 5.8, 55.1, 23]
GERMANY = [47.2, 5.8, 55.1, 15.1]
ITALY = [36.5, 6.5, 47.1, 18.6]
BENELUX = [49.4, 2.5, 53.6, 7.2]
SPAIN = [36, -7.5, 43.8, 3.4]
NEW_SPAIN = [7, -118, 32.7, -77]
ANDES = [-40, -82, 12, -60]
CACAO = [13, -106, 22.5, -86]
USA = [24.5, -125, 49.5, -66.9]
CHINA = [18, 97.5, 45, 123.5]
JAPAN = [30, 129, 45.6, 146]
WEST_AFRICA = [4, -17.5, 17, 15]
SUB_SAHARA = [-35, -18, 12, 52]
AMERICAS = [-56, -170, 72, -30]
AUSTRALIA = [-48, 110, -9, 180]
NORTH_ASIA = [55, 40, 78, 180]
RUSSIA = [44, 27, 70, 60]

DELHI_SULTANS = ["Mamluk Dynasty", "Khalji Dynasty", "Tughlaq Dynasty", "Sayyid Dynasty", "Lodi Dynasty",
                 "Jaunpur Sultanate", "Bahmani Sultanate", "Kashmiri Sultanate", "Sultanate of Bengal"]
DECCAN_HUN = ["Vijayanagara Empire", "Golconda Sultanate", "Bijapur Sultanate", "Ahmadnagar Sultanate",
              "Bidar Sultanate", "Berar Sultanate", "Kingdom of Mysore"]
NEIGHBOURS_1947 = ["Islamic Republic of Pakistan", "People's Republic of Bangladesh", "Sri Lanka", "Ceylon",
                   "British Ceylon", "Nepal", "Gorkha Kingdom", "Kingdom of Bhutan", "Afghanistan", "Burma",
                   "Union of Myanmar", "Tibet"]


def row(id_, money_id, frm, to, where, priority, accepts=None, note=""):
    r = {"id": id_, "money": money_id, "from": frm, "to": to, "where": where, "priority": priority}
    if accepts:
        r["accepts"] = accepts
    if note:
        r["note"] = note
    return r


def box(b):
    return {"box": b}


def ruler(*names):
    return {"ruler": list(names)}


HYD = {"rulerIn": 1947, "names": ["Hyderabad State"]}

ROWS = [
    # --- Hyderabad State (keyed on the 1947 ruler: the register has the British Raj there 1859-1946) ---
    row("hyderabad_sicca", "sicca", 1724, 1857, [HYD], 100,
        note="The Asaf Jahi Nizams struck rupees in the Mughal emperor's name until 1858."),
    row("hyderabad_hali", "hali_sicca", 1858, 1917, [HYD], 100, accepts=["indian_rupee_anna"]),
    row("hyderabad_os", "osmania_sicca", 1918, 1956, [HYD], 100, accepts=["indian_rupee_anna"],
        note="British Indian rupees circulated freely in Hyderabad; from 1950 India's rupee at 7 O.S. = 6."),
    row("hyderabad_os_np", "osmania_sicca", 1957, 1959, [HYD], 100, accepts=["indian_rupee_np"],
        note="Demonetised in 1959 (1 April or 30 June by different accounts)."),
    # --- South Asia by ruler ---
    row("delhi_sultans", "tanka", 1206, 1526, [ruler(*DELHI_SULTANS)], 60),
    row("deccan_hun", "hun", 1336, 1723, [ruler(*DECCAN_HUN)], 60),
    row("mughal", "mughal_rupee", 1540, 1857, [ruler("Mughal Empire", "Sur Empire")], 60),
    row("maratha", "sicca", 1674, 1818, [ruler("Maratha Empire", "Thanjavur Maratha Kingdom")], 60),
    row("company_sicca", "sicca", 1757, 1834,
        [{"ruler": ["British Empire", "Nawabs of Bengal"], "box": SOUTH_ASIA}], 55),
    row("british_india", "indian_rupee_anna", 1835, 1946,
        [{"ruler": ["British Raj", "British Empire"], "box": SOUTH_ASIA}], 55),
    row("india_1947", "indian_rupee_anna", 1947, 1956, [ruler("Republic of India")], 60),
    row("india_np", "indian_rupee_np", 1957, 1963, [ruler("Republic of India")], 60),
    row("india", "indian_rupee", 1964, 2100, [ruler("Republic of India")], 60),
    # --- South Asia by box, when the ruler register has nobody there ---
    row("south_asia_pana", "pana", -600, 1205, [box(SOUTH_ASIA)], 20,
        note="Punch-marked coins from about the 6th century BCE; the pana kept as the money of account."),
    row("north_india_tanka", "tanka", 1206, 1539, [box(NORTH_INDIA)], 20),
    row("south_india_pana", "pana", 1206, 1335, [box(SOUTH_INDIA)], 21),
    row("south_india_hun", "hun", 1336, 1686, [box(SOUTH_INDIA)], 21),
    row("south_india_sicca", "sicca", 1687, 1834, [box(SOUTH_INDIA)], 21),
    row("north_india_mughal", "mughal_rupee", 1540, 1834, [box(NORTH_INDIA)], 20),
    row("south_asia_rupee", "indian_rupee_anna", 1835, 1956, [box(SOUTH_ASIA)], 20),
    row("south_asia_np", "indian_rupee_np", 1957, 1963, [box(SOUTH_ASIA)], 20),
    row("south_asia_paise", "indian_rupee", 1964, 2100, [box(SOUTH_ASIA)], 20),
    # --- The ancient Near East and the Mediterranean ---
    row("mesopotamia_silver", "silver_weighed", -2600, -539, [box(MESOPOTAMIA)], 30,
        note="Silver weighed out as money from the Early Dynastic III period; barley before."),
    row("egypt_deben", "egypt_deben", -2000, -333, [box(EGYPT)], 30),
    row("greek_drachma", "drachma", -600, -147, [box(GREECE)], 30),
    row("hellenistic_drachma", "drachma", -332, -31,
        [ruler("Ptolemaic Kingdom", "Seleucid Empire", "Antigonid Macedonia", "Macedonian Empire"),
         box(EGYPT)], 35),
    row("roman_egypt_drachma", "drachma", -30, 295, [box(EGYPT)], 40,
        note="Roman Egypt kept its own (Alexandrian) drachma until Diocletian."),
    row("rome", "denarius", -211, 295, [ruler("Roman Republic", "Roman Empire", "Western Roman Empire",
                                             "Revolutionary Roman Republic")], 50),
    row("roman_world", "denarius", -146, 295, [box(MEDITERRANEAN)], 20),
    row("byzantium", "solidus", 296, 1453, [ruler("Byzantine Empire", "Eastern Roman Empire", "Roman Empire",
                                                 "Western Roman Empire")], 50),
    row("late_roman_world", "solidus", 296, 649, [box(MEDITERRANEAN)], 20),
    row("byzantine_core", "solidus", 650, 1071, [box(BYZANTINE_CORE)], 19),
    row("islamic_world", "dirham", 650, 1500, [box(ISLAMIC_WORLD)], 18),
    row("iran_toman", "toman", 1501, 1931, [box(IRAN)], 30),
    row("ottoman_akce", "akce", 1326, 1843, [ruler("Ottoman Empire", "Ottoman Tripolitania")], 50),
    row("ottoman_kurus", "kurus", 1844, 1922, [ruler("Ottoman Empire", "Ottoman Tripolitania")], 50),
    # --- Europe ---
    row("britain_lsd", "pound_lsd", 800, 1970, [box(BRITAIN), box(BRITAIN_EAST)], 30),
    row("britain_decimal", "gbp", 1971, 2100, [box(BRITAIN), box(BRITAIN_EAST)], 30),
    row("france_livre", "livre", 800, 1794, [box(FRANCE)], 30),
    row("france_franc", "franc", 1795, 1959, [box(FRANCE)], 30),
    row("france_new_franc", "new_franc", 1960, 2001, [box(FRANCE)], 30),
    row("central_europe_thaler", "thaler", 1500, 1872, [box(CENTRAL_EUROPE)], 25),
    row("germany_mark", "mark", 1873, 1947, [box(GERMANY)], 26),
    row("germany_dm", "deutsche_mark", 1948, 2001, [box(GERMANY)], 26),
    row("euro", "euro", 2002, 2100, [box(FRANCE), box(GERMANY), box(SPAIN), box(ITALY), box(BENELUX)], 29),
    row("spain_peso", "peso_real", 1497, 1868, [box(SPAIN)], 30),
    row("russia_ruble", "ruble", 1535, 1917, [box(RUSSIA)], 25),
    # --- Asia ---
    row("china_cash", "china_cash", -600, 1911, [box(CHINA)], 30),
    row("china_yuan", "yuan_rep", 1912, 1948, [box(CHINA)], 30),
    row("china_rmb", "rmb", 1949, 2100, [box(CHINA)], 30),
    row("japan_mon", "mon", 708, 1870, [box(JAPAN)], 30),
    row("japan_yen", "yen", 1871, 2100, [box(JAPAN)], 30),
    # --- Americas ---
    row("mesoamerica_cacao", "cacao", 900, 1600, [box(CACAO)], 30),
    row("new_spain_peso", "peso_real", 1535, 1860, [box(NEW_SPAIN)], 25),
    row("andes_peso", "peso_real", 1568, 1860, [box(ANDES)], 25),
    row("english_colonies", "pound_lsd", 1620, 1791, [box(USA)], 20,
        note="Colonial pounds, shillings and pence (each colony's pound was worth less than sterling)."),
    row("usa_dollar", "dollar", 1792, 2100, [box(USA)], 30),
    # --- Africa, Oceania, the far north ---
    row("west_africa_cowrie", "cowrie", 1000, 1900, [box(WEST_AFRICA)], 30),
    row("australia_pound", "pound_lsd", 1825, 1965, [box(AUSTRALIA)], 20),
    # --- Where people swapped goods ---
    row("americas_barter", "barter", -100000, 1499, [box(AMERICAS)], 10),
    row("americas_barter_late", "barter", 1500, 1799, [box(AMERICAS)], 5,
        note="Away from the colonies' rows: native peoples kept to barter."),
    row("sub_sahara_barter", "barter", -100000, 1799, [box(SUB_SAHARA)], 10),
    row("australia_barter", "barter", -100000, 1787, [box(AUSTRALIA)], 10),
    row("north_asia_barter", "barter", -100000, 1599, [box(NORTH_ASIA)], 10),
    # --- World fallbacks ---
    row("world_barter", "barter", -100000, -601, [{"world": True}], 0),
    row("world_coins", "silver_copper", -600, 1799, [{"world": True}], 0),
    row("world_modern", "local_money", 1800, 2100, [{"world": True}], 0),
]

RATES = [
    {"a": "osmania_sicca", "aAmount": 7 * 192, "b": "indian_rupee_anna", "bAmount": 6 * 192, "from": 1918, "to": 1959,
     "note": "7 O.S. rupees = 6 Indian rupees (the official rate from 1950; used for the whole period)."},
    {"a": "osmania_sicca", "aAmount": 7 * 192, "b": "indian_rupee_np", "bAmount": 6 * 100, "from": 1957, "to": 1959},
    {"a": "osmania_sicca", "aAmount": 7 * 192, "b": "indian_rupee", "bAmount": 6 * 100, "from": 1960, "to": 2100,
     "note": "For the money-changer after 1959 (old notes)."},
    {"a": "hali_sicca", "aAmount": 7 * 192, "b": "indian_rupee_anna", "bAmount": 6 * 192, "from": 1858, "to": 1959,
     "note": "Rough: the Hali sicca also traded below the British rupee."},
    {"a": "indian_rupee_anna", "aAmount": 192, "b": "indian_rupee_np", "bAmount": 100, "from": 1957, "to": 2100,
     "note": "The rupee kept its value in 1957: 16 annas = 100 naye paise."},
    {"a": "indian_rupee_anna", "aAmount": 192, "b": "indian_rupee", "bAmount": 100, "from": 1964, "to": 2100},
    {"a": "indian_rupee_np", "aAmount": 1, "b": "indian_rupee", "bAmount": 1, "from": 1964, "to": 2100},
    {"a": "pound_lsd", "aAmount": 960, "b": "gbp", "bAmount": 100, "from": 1971, "to": 2100},
    {"a": "franc", "aAmount": 10000, "b": "new_franc", "bAmount": 100, "from": 1960, "to": 2100},
    {"a": "new_franc", "aAmount": 655957, "b": "euro", "bAmount": 100000, "from": 1999, "to": 2100},
    {"a": "deutsche_mark", "aAmount": 195583, "b": "euro", "bAmount": 100000, "from": 1999, "to": 2100},
    {"a": "sicca", "aAmount": 1, "b": "indian_rupee_anna", "bAmount": 1, "from": 1835, "to": 1900,
     "note": "Rough: the sicca rupee was a little heavier than the Company rupee."},
    # Step 19b, for the money-changer: the fixed rates between the rupee, sterling and the dollar.
    {"a": "pound_lsd", "aAmount": 960, "b": "indian_rupee_anna", "bAmount": 10 * 192, "from": 1835, "to": 1872,
     "note": "About 2 shillings a rupee while silver held its price: Rs 10 = 1 pound."},
    {"a": "pound_lsd", "aAmount": 960, "b": "indian_rupee_anna", "bAmount": 15 * 192, "from": 1873, "to": 1916,
     "note": "1 rupee = 1 shilling 4 pence, fixed by the 1899 act: Rs 15 = 1 pound. Rough before 1899: the rupee fell"
             " with silver from 1s 10d (1873) to 1s 1d (1895)."},
    {"a": "pound_lsd", "aAmount": 3 * 960, "b": "indian_rupee_anna", "bAmount": 40 * 192, "from": 1917, "to": 1965,
     "note": "1 rupee = 1 shilling 6 pence (1927 act, kept at independence): Rs 13 1/3 = 1 pound. Rough for 1917-1926,"
             " when the rate moved between 1s 3d and 2s 4d. The anna rupee is the bridge to naye paise and paise after"
             " 1956."},
    {"a": "pound_lsd", "aAmount": 960, "b": "indian_rupee", "bAmount": 2100, "from": 1966, "to": 1967,
     "note": "The devaluation of June 1966: Rs 21 = 1 pound."},
    {"a": "pound_lsd", "aAmount": 960, "b": "indian_rupee", "bAmount": 1800, "from": 1968, "to": 1970,
     "note": "Sterling devalued in November 1967, the rupee did not follow: Rs 18 = 1 pound."},
    {"a": "pound_lsd", "aAmount": 96000, "b": "dollar", "bAmount": 48665, "from": 1879, "to": 1914,
     "note": "The gold standard: 1 pound = 4.8665 dollars."},
    {"a": "pound_lsd", "aAmount": 96000, "b": "dollar", "bAmount": 48665, "from": 1925, "to": 1931,
     "note": "Back on gold, 1925 to September 1931."},
    {"a": "pound_lsd", "aAmount": 960, "b": "dollar", "bAmount": 403, "from": 1940, "to": 1948,
     "note": "1 pound = 4.03 dollars, 1940 to September 1949."},
    {"a": "pound_lsd", "aAmount": 960, "b": "dollar", "bAmount": 280, "from": 1949, "to": 1967,
     "note": "1 pound = 2.80 dollars, September 1949 to November 1967."},
    {"a": "pound_lsd", "aAmount": 960, "b": "dollar", "bAmount": 240, "from": 1968, "to": 1970},
    {"a": "dollar", "aAmount": 403, "b": "indian_rupee_anna", "bAmount": 40 * 64, "from": 1940, "to": 1948,
     "note": "Through sterling: 4.03 dollars = Rs 13 1/3, about Rs 3.31 to the dollar."},
    {"a": "dollar", "aAmount": 2100, "b": "indian_rupee_anna", "bAmount": 100 * 192, "from": 1949, "to": 1965,
     "note": "Rs 4.76 to the dollar (Rs 100 = 21 dollars), 1949 to June 1966."},
    {"a": "dollar", "aAmount": 100, "b": "indian_rupee", "bAmount": 750, "from": 1966, "to": 1970,
     "note": "Rs 7.50 to the dollar after the devaluation of June 1966."},
]


RULER_FILES = ("/home/user/eternal/src/main/resources/data/eternalengine/eternal/history/world_rulers.json.gz",
               "/home/user/eternal/src/main/resources/data/eternalengine/eternal/history/deccan_rulers.json")


def register_names():
    """Every ruler name the game's register can answer with (world and Deccan records)."""
    import gzip
    names = set()
    w = json.load(gzip.open(RULER_FILES[0], "rt", encoding="utf-8"))
    names.update(p[0] for p in w["polities"])
    d = json.load(open(RULER_FILES[1], encoding="utf-8"))

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                if k in ("ruler", "name", "polity") and isinstance(v, str):
                    names.add(v)
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(d.get("timelines", {}))
    return names


def merge_world():
    """Step 23a: add the world layer (money_world.py)."""
    import money_world
    CURRENCIES.extend(money_world.CURRENCIES)
    ROWS.extend(money_world.ROWS)
    RATES.extend(money_world.RATES)


def check_rulers():
    known = register_names()
    unknown = {}
    for r in ROWS:
        for w in r["where"]:
            for n in w.get("ruler", []) + w.get("names", []):
                if n not in known:
                    unknown.setdefault(n, []).append(r["id"])
    return unknown


def main():
    merge_world()
    unknown = check_rulers()
    if unknown:
        for n, ids in sorted(unknown.items()):
            print(f"  unknown ruler name {n!r} in rows {', '.join(ids[:4])}")
        raise SystemExit(f"{len(unknown)} ruler name(s) are not in the register")
    data = {
        "format": 1,
        "about": "Steps 19a and 23a: money by place and year for the whole world. See worldfill/build_money_table.py"
                 " and worldfill/money_world.py for the rules. Notes are for developers only; the game never shows"
                 " them.",
        "currencies": CURRENCIES,
        "rows": ROWS,
        "rates": RATES,
    }
    ids = {c["id"] for c in CURRENCIES}
    for r in ROWS:
        assert r["money"] in ids, r
        for a in r.get("accepts", []):
            assert a in ids, (r["id"], a)
        assert r["from"] <= r["to"], r
    for rt in RATES:
        assert rt["a"] in ids and rt["b"] in ids, rt
        assert rt["aAmount"] > 0 and rt["bAmount"] > 0 and rt["from"] <= rt["to"], rt
    for c in CURRENCIES:
        sizes = [u["size"] for u in c["units"]]
        assert sizes == sorted(sizes, reverse=True), c["id"]
        assert min(sizes) == (10 if c.get("decimals") == 1 else 1) or c["kind"] in ("barter", "local"), c["id"]
        years = [p[0] for p in c["pay"]]
        assert years == sorted(years), c["id"]
    assert len(ids) == len(CURRENCIES), "two monies share an id"
    seen = set()
    for r in ROWS:
        if "pay" in r:
            ys = [x[0] for x in r["pay"]]
            assert ys == sorted(ys) and all(x[1] > 0 for x in r["pay"]), r["id"]
        assert r["id"] not in seen, r["id"]
        seen.add(r["id"])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"wrote {OUT}: {len(CURRENCIES)} kinds of money, {len(ROWS)} rows, {len(RATES)} rates,"
          f" {os.path.getsize(OUT):,} bytes")


if __name__ == "__main__":
    main()
