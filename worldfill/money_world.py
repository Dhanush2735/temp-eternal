#!/usr/bin/env python3
"""Step 23a: the world layer of the money table - real money for the places and years that had a placeholder.

build_money_table.py imports this module and adds CURRENCIES, ROWS and RATES to its own lists. Before step 23a the
table named money for India, the ancient Near East and Mediterranean, western Europe, China, Japan, the USA, Spanish
America before 1860, West Africa's cowries and a few more; everywhere else it said "silver and copper coins"
(600 BCE - 1799) or "local money" (from 1800). This layer names the money of every region and era:

  * Europe: medieval pennies and marks, Italy's lire and ducats, Iberia, the Low Countries, Scandinavia (weighed
    silver, homespun cloth in Iceland), Poland, Hungary, Rus' (grivna, denga), the Balkans, every modern currency to
    the euro (Croatia 2023, Bulgaria 2026);
  * the Middle East and North Africa: Persian siglos and drachms, Ottoman successors, every modern currency;
  * Africa south of the Sahara: commodity money (manillas, nzimbu shells, salt bars, cut silver), colonial pounds,
    francs, shillings, escudos and rupees, every currency since independence;
  * Asia: Central Asian tangas, Tibet, Nepal, Burma, Siam (bullet money and cowries), Vietnam, Korea, Taiwan, Hong
    Kong, Macau, Manchukuo, the Soviet Union and its successors;
  * the Americas: colonial Brazil and the Plata, every republic's currency with its redenominations;
  * Oceania: Australia, New Zealand, the Pacific.

Rules are those of build_money_table.py. Matching: rows by the register's ruler name where the register is
reliable, by box where it is not (colonies lumped together, gaps, the years after 2024), by ruler and box together
where one ruler name covers several monies (British Africa, French Africa, the Portuguese colonies).
Priorities: 70 small special places; 45-48 country rulers; 40-44 older rulers; 31-36 country boxes; 21-29 regional
boxes; 8-15 wide fallbacks; 4-6 barter where nobody rules.

Day's pay: every number here is an estimate (an unskilled labourer's day), written to keep prices sensible;
hyperinflations are not followed day by day (notes say so). Unit systems and dates follow the Wikipedia articles
on each currency, cross-checked with Wikidata (worldfill/sources/money/wikidata_currencies.tsv.xz;
verify or restore the original path with r2_wikipedia/archive_generated_aux.py).
"""

CURRENCIES = []
ROWS = []
RATES = []

MASS = set()


def U(name, plural, size, frm=None, to=None):
    u = {"name": name, "plural": plural, "size": size}
    if frm is not None:
        u["from"] = frm
    if to is not None:
        u["to"] = to
    return u


def cur(id_, name, units, pay, kind="coins", mass=False, metal=None, short=None, note="", decimals=0,
        estimate=True):
    m = {"id": id_, "name": name, "called": name if mass else "the " + name, "kind": kind,
         "units": [U(*u) if isinstance(u, tuple) else u for u in units],
         "pay": [list(p) for p in pay], "estimate": estimate}
    if short:
        m["short"] = short
    if metal:
        m["metal"] = metal
    if decimals:
        m["decimals"] = decimals
    if note:
        m["note"] = note
    CURRENCIES.append(m)
    return id_


def ru(*names):
    return {"ruler": list(names)}


def bx(b):
    return {"box": list(b)}


def rb(names, b):
    return {"ruler": list(names) if isinstance(names, (list, tuple)) else [names], "box": list(b)}


def _emit(id_, money_id, frm, to, where, p, accepts, note, pay=None):
    r = {"id": id_, "money": money_id, "from": frm, "to": to, "where": where, "priority": p}
    if pay:
        r["pay"] = [list(x) for x in pay]
    if accepts:
        r["accepts"] = list(accepts)
    if note:
        r["note"] = note
    ROWS.append(r)


def box_priority(b):
    """Box-level priority: a smaller box wins over a larger one where they overlap."""
    area = (b[2] - b[0]) * (b[3] - b[1])
    return 34 if area <= 10 else 33 if area <= 60 else 32 if area <= 250 else 31


def row(id_, money_id, frm, to, where, p, accepts=None, note="", pb=None, pay=None):
    """A row. When a high-priority row (36 or more) matches by ruler or by box, the boxes go into rows of their own
    at box level (31-34, or pb), so that a neighbour's ruler row wins inside an overlapping box. pay: the day's pay
    of this place when it differs from the money's own (a money shared by richer and poorer places)."""
    where = where if isinstance(where, list) else [where]
    rulers = [w for w in where if "ruler" in w]
    boxes = [w for w in where if "ruler" not in w]
    if rulers and boxes and p >= 36:
        _emit(id_, money_id, frm, to, rulers, p, accepts, note, pay)
        groups = {}
        for w in boxes:
            groups.setdefault(pb if pb is not None else box_priority(w["box"]), []).append(w)
        for i, (bp, ws) in enumerate(sorted(groups.items(), reverse=True)):
            _emit(f"{id_}_box{'' if i == 0 else i + 1}", money_id, frm, to, ws, bp, accepts, note, pay)
    else:
        _emit(id_, money_id, frm, to, where, p, accepts, note, pay)


def rate(a, a_amount, b, b_amount, frm, to, note=""):
    r = {"a": a, "aAmount": a_amount, "b": b, "bAmount": b_amount, "from": frm, "to": to}
    if note:
        r["note"] = note
    RATES.append(r)


def dec(major, majors, minor, minors, frm=None, to=None):
    """A decimal money: 1 major = 100 minor."""
    return [(major, majors, 100), (minor, minors, 1, frm, to)] if (frm or to) else [(major, majors, 100),
                                                                                     (minor, minors, 1)]


def chain(id_, rows_, p, where_of):
    """Rows for one country's run of monies: rows_ = [(money, from, to), ...], all with the same matchers."""
    for money_id, frm, to in rows_:
        row(f"{id_}_{money_id}_{frm}", money_id, frm, to, where_of, p)


# --------------------------------------------------------------------------------------------------------------
# Boxes (latMin, lonMin, latMax, lonMax)
# --------------------------------------------------------------------------------------------------------------
EUROPE_ALL = [34, -25, 72, 45]
WEST_EUROPE = [42, -5.5, 55.5, 16]
NORTH_EUROPE = [55, -11, 72, 60]
EAST_EUROPE = [44, 15, 72, 60]
SCANDINAVIA = [54.5, 4.5, 71.5, 31.5]
DENMARK = [54.5, 8, 57.8, 15.2]
NORWAY = [[57.9, 4.5, 63.5, 11.9], [63.5, 8.0, 66.0, 13.9], [66.0, 12.0, 69.1, 17.9], [68.3, 16.0, 71.3, 31.2]]
SWEDEN = [55.3, 11.0, 69.1, 24.2]
FINLAND = [59.7, 19.5, 70.1, 31.6]
ICELAND = [63.2, -24.6, 66.6, -13.4]
GREENLAND = [59.5, -74, 84, -11]
GREENLAND_NORSE = [59.5, -54, 65.5, -42]
IRELAND = [51.3, -10.7, 55.5, -5.9]
BRITAIN = [49.85, -10.7, 61, 2.0]
ITALY_PEN = [36.5, 6.6, 46.6, 18.6]
MAGNA_GRAECIA = [36.5, 12.5, 41.3, 18.6]
NAPLES = [37.8, 13.5, 42.0, 18.6]
SICILY = [36.6, 12.3, 38.4, 15.7]
SARDINIA = [38.8, 8.1, 41.3, 9.9]
MALTA = [35.78, 14.15, 36.1, 14.6]
PAPAL = [41.6, 11.4, 44.9, 13.9]
IBERIA = [36, -9.6, 43.8, 3.4]
SPAIN = [36, -7.5, 43.8, 3.4]
PORTUGAL = [36.9, -9.6, 42.2, -6.2]
FRANCE = [42.3, -4.8, 51.1, 8.2]
BENELUX = [49.4, 2.5, 53.6, 7.2]
NETHERLANDS = [50.75, 3.3, 53.6, 7.25]
BELGIUM = [49.45, 2.5, 51.5, 6.4]
SWISS = [45.8, 5.95, 47.8, 10.5]
GERMANY = [47.2, 5.8, 55.1, 15.1]
AUSTRIA = [46.4, 9.5, 49.0, 17.2]
CENTRAL_EUROPE = [45.5, 5.8, 55.1, 23]
POLAND = [49, 14.1, 55, 24.2]
BOHEMIA = [48.5, 12.1, 51.1, 18.9]
SLOVAKIA = [47.7, 16.8, 49.6, 22.6]
HUNGARY = [45.7, 16.1, 48.6, 22.9]
BALKANS = [39.5, 13.5, 46.9, 29.7]
GREECE_MOD = [34.8, 19.3, 41.8, 28.3]
BULGARIA = [41.2, 22.3, 44.3, 28.7]
ROMANIA = [43.6, 20.2, 48.3, 29.7]
ALBANIA = [39.6, 19.2, 42.7, 21.1]
MONTENEGRO = [41.8, 18.4, 43.6, 20.4]
KOSOVO = [41.85, 20.0, 43.3, 21.8]
CYPRUS = [34.5, 32.2, 35.75, 34.65]
BALTIC = [53.9, 20.9, 59.7, 28.3]
RUSSIA_EU = [44, 27, 70, 60]

# A labourer's day in euro cents where the euro came to lower wages than its old members paid (step 23a)
PAY_EURO_PT = [(2002, 3500), (2026, 6000)]
PAY_EURO_GR = [(2002, 4000), (2026, 5500)]
PAY_EURO_CY = [(2008, 4000), (2026, 6500)]
PAY_EURO_SK = [(2009, 2500), (2026, 5000)]
PAY_EURO_EE = [(2011, 3000), (2026, 6000)]
PAY_EURO_LV = [(2014, 2500), (2026, 4500)]
PAY_EURO_LT = [(2015, 2500), (2026, 5000)]


# ==============================================================================================================
# EUROPE, 1800 - today
# ==============================================================================================================
EURO = "euro"  # defined in build_money_table.py

cur("lira_it", "Italian lira", [("lira", "lire", 100), ("centesimo", "centesimi", 1, None, 1947)],
    [(1807, 100), (1861, 120), (1900, 200), (1914, 300), (1920, 1500), (1930, 1500), (1940, 2000), (1947, 50000),
     (1950, 80000), (1960, 150000), (1970, 400000), (1980, 2000000), (1990, 6000000), (2001, 7000000)],
    note="Lira = 100 centesimi (Napoleonic lira from 1807, Sardinian lira from 1816, Italian lira 1861-2001;"
         " centesimi gone after the war). Wages are guesses.")
cur("ducato_napoli", "Neapolitan ducat", [("ducat", "ducats", 100), ("carlino", "carlini", 10), ("grano", "grana", 1)],
    [(1472, 8), (1600, 15), (1700, 20), (1800, 25), (1860, 30)],
    note="Kingdom of Naples and the Two Sicilies: ducat = 10 carlini = 100 grana. Wages are guesses.")
cur("scudo_papal", "Papal scudo", [("scudo", "scudi", 100), ("baiocco", "baiocchi", 1)],
    [(1535, 12), (1600, 15), (1700, 20), (1800, 25), (1866, 30)],
    note="Papal States: scudo = 100 baiocchi (decimal from 1835; 10 paoli before). Wages are guesses.")
cur("peseta", "Spanish peseta", dec("peseta", "pesetas", "céntimo", "céntimos"),
    [(1869, 150), (1900, 250), (1914, 300), (1920, 600), (1936, 900), (1940, 1200), (1950, 2500), (1960, 6000),
     (1970, 25000), (1980, 120000), (1990, 400000), (2001, 600000)],
    note="Peseta = 100 centimos, 1869-2001. Wages are guesses.")
cur("real_pt", "Portuguese real", [("mil-réis", "mil-réis", 1000, 1700), ("tostão", "tostões", 100),
                                   ("vintém", "vinténs", 20), ("real", "réis", 1)],
    [(1435, 10), (1500, 25), (1600, 60), (1700, 120), (1800, 200), (1850, 240), (1900, 300), (1911, 400)],
    note="Real (plural reis), 1435-1911; the tostao of 100 reis, the vintem of 20, the mil-reis of 1,000 as the"
         " counting unit. Wages are guesses.")
cur("escudo_pt", "Portuguese escudo", dec("escudo", "escudos", "centavo", "centavos"),
    [(1911, 40), (1920, 200), (1930, 1000), (1950, 2000), (1970, 6000), (1980, 25000), (1990, 150000),
     (2001, 350000)], note="Escudo = 100 centavos (1,000 reis), 1911-2001. Wages are guesses.")
cur("ddr_mark", "East German mark", dec("mark", "marks", "pfennig", "pfennigs"),
    [(1948, 600), (1960, 1200), (1970, 2400), (1990, 3500)], note="Mark of the GDR, 1948-1990. Wages are guesses.")
cur("gulden_kreuzer", "gulden", [("gulden", "gulden", 60), ("kreuzer", "kreuzer", 1)],
    [(1500, 6), (1600, 10), (1700, 15), (1800, 24), (1856, 30)],
    note="Habsburg and south German gulden of 60 kreuzer (Conventionsgulden from 1753). Wages are guesses.")
cur("gulden_at", "Austro-Hungarian gulden", [("gulden", "gulden", 100), ("kreuzer", "kreuzer", 1)],
    [(1857, 50), (1892, 80)], note="Austrian gulden (forint) of 100 kreuzer, 1857-1892. Wages are guesses.")
cur("krone_au", "Austro-Hungarian krone", [("krone", "kronen", 100), ("heller", "heller", 1)],
    [(1892, 160), (1914, 300), (1918, 800)], note="Krone = 100 heller, 1892-1918. Wages are guesses.")
cur("krone_at", "Austrian krone", [("krone", "kronen", 100), ("heller", "heller", 1)],
    [(1919, 2000), (1922, 1000000), (1924, 3000000)], note="1919-1924, through the inflation (rough).")
cur("schilling_at", "Austrian schilling", [("schilling", "schillings", 100), ("groschen", "groschen", 1)],
    [(1925, 500), (1938, 600), (1946, 1000), (1960, 4000), (1980, 40000), (2001, 80000)],
    note="Schilling = 100 groschen, 1925-1938 and 1945-2001. Wages are guesses.")
cur("guilder_nl_old", "Dutch guilder", [("guilder", "guilders", 160), ("stuiver", "stuivers", 8), ("duit", "duits", 1)],
    [(1500, 24), (1600, 80), (1700, 128), (1800, 160), (1816, 176)],
    note="Guilder = 20 stuivers = 160 duits (the Low Countries and the VOC). Wages are guesses.")
cur("guilder_nl", "Dutch guilder", dec("guilder", "guilders", "cent", "cents"),
    [(1817, 80), (1850, 90), (1900, 150), (1914, 250), (1930, 400), (1950, 1000), (1970, 4000), (1990, 12000),
     (2001, 16000)], note="Decimal guilder = 100 cents, 1817-2001. Wages are guesses.")
cur("franc_be", "Belgian franc", dec("franc", "francs", "centime", "centimes"),
    [(1832, 150), (1900, 300), (1914, 400), (1926, 2000), (1950, 15000), (1970, 50000), (1990, 200000),
     (2001, 300000)], note="Belgian franc = 100 centimes, 1832-2001. Wages are guesses.")
cur("franc_lu", "Luxembourg franc", dec("franc", "francs", "centime", "centimes"),
    [(1854, 150), (1900, 300), (1950, 15000), (1990, 200000), (2001, 300000)],
    note="At par with the Belgian franc from 1921. Wages are guesses.")
cur("franc_ch", "Swiss franc", dec("franc", "francs", "rappen", "rappen"),
    [(1850, 150), (1900, 350), (1914, 500), (1920, 1000), (1950, 2000), (1970, 6000), (1990, 18000), (2010, 25000),
     (2026, 30000)], note="Swiss franc = 100 rappen (centimes), from 1850. Wages are guesses.")
cur("rigsdaler_dk", "Danish rigsdaler", [("rigsdaler", "rigsdaler", 96), ("mark", "mark", 16),
                                         ("skilling", "skilling", 1)],
    [(1534, 6), (1650, 12), (1750, 16), (1800, 24), (1850, 32), (1874, 48)],
    note="Rigsdaler = 6 mark = 96 skilling (Denmark-Norway; rigsbankdaler from 1813). Wages are guesses.")
cur("krone_dk", "Danish krone", dec("krone", "kroner", "øre", "øre"),
    [(1875, 200), (1900, 300), (1920, 1200), (1950, 2000), (1970, 7000), (1990, 50000), (2010, 100000),
     (2026, 130000)], note="Krone = 100 ore, from 1875 (Greenland and the Faroes too). Wages are guesses.")
cur("speciedaler", "Norwegian speciedaler", [("speciedaler", "speciedaler", 120), ("ort", "ort", 24),
                                             ("skilling", "skilling", 1)],
    [(1816, 24), (1850, 36), (1874, 60)], note="Speciedaler = 5 ort = 120 skilling, 1816-1874. Guesses.")
cur("krone_no", "Norwegian krone", dec("krone", "kroner", "øre", "øre"),
    [(1875, 200), (1900, 300), (1914, 400), (1920, 1500), (1939, 1000), (1950, 2000), (1970, 8000), (1990, 60000),
     (2010, 120000), (2026, 160000)], note="Krone = 100 ore, from 1875. Wages are guesses.")
cur("daler_se", "Swedish daler", [("daler", "daler", 32), ("mark", "mark", 8), ("öre", "öre", 1)],
    [(1534, 2), (1650, 6), (1750, 12), (1776, 16)],
    note="Daler = 4 mark = 32 ore, 1534-1776 (silver and copper daler are not told apart). Wages are guesses.")
cur("riksdaler_se", "Swedish riksdaler", [("riksdaler", "riksdaler", 576), ("skilling", "skilling", 12),
                                          ("runstycke", "runstycken", 1)],
    [(1777, 96), (1850, 144), (1872, 180)], note="Riksdaler = 48 skilling = 576 runstycken, 1777-1872. Guesses.")
cur("krona_se", "Swedish krona", dec("krona", "kronor", "öre", "öre"),
    [(1873, 150), (1900, 250), (1920, 1000), (1950, 2000), (1970, 6000), (1990, 50000), (2010, 100000),
     (2026, 140000)], note="Krona = 100 ore, from 1873. Wages are guesses.")
cur("markka_old", "Finnish markka", dec("markka", "markkaa", "penni", "penniä"),
    [(1860, 150), (1900, 250), (1918, 1500), (1930, 3000), (1950, 30000), (1962, 70000)],
    note="Markka = 100 pennia, 1860-1962. Wages are guesses.")
cur("markka", "Finnish markka", dec("markka", "markkaa", "penni", "penniä"),
    [(1963, 800), (1980, 10000), (1990, 25000), (2001, 40000)], note="New markka (100 old), 1963-2001. Guesses.")
cur("krona_is_old", "Icelandic króna", dec("króna", "krónur", "eyrir", "aurar"),
    [(1918, 600), (1950, 6000), (1970, 40000), (1980, 1000000)], note="Krona = 100 aurar, 1918-1980. Guesses.")
cur("krona_is", "Icelandic króna", dec("króna", "krónur", "eyrir", "aurar", None, 2002),
    [(1981, 15000), (2000, 600000), (2026, 2500000)], note="New krona (100 old) from 1981. Guesses.")
cur("zloty_pl_old", "Polish złoty", dec("złoty", "złotych", "grosz", "groszy"),
    [(1924, 400), (1939, 400), (1946, 10000), (1949, 30000)], note="Zloty = 100 groszy, 1924-1949. Guesses.")
cur("marka_pl", "Polish mark", dec("mark", "marks", "fenig", "fenigs"),
    [(1917, 1500), (1923, 1000000)], note="Polish mark 1917-1924, through the inflation (rough).")
cur("zloty_pl", "Polish złoty", dec("złoty", "złotych", "grosz", "groszy"),
    [(1950, 1000), (1970, 8000), (1980, 20000), (1989, 500000), (1994, 4000000)],
    note="Zloty 1950-1994 (the 1980s inflation roughly). Guesses.")
cur("zloty_new", "Polish złoty", dec("złoty", "złotych", "grosz", "groszy"),
    [(1995, 1000), (2000, 3000), (2010, 7000), (2026, 18000)], note="New zloty (10,000 old) from 1995. Guesses.")
cur("koruna_cs_old", "Czechoslovak koruna", dec("koruna", "korun", "haléř", "haléřů"),
    [(1919, 1500), (1930, 2000), (1945, 5000), (1952, 20000)], note="1919-1952. Wages are guesses.")
cur("koruna_cs", "Czechoslovak koruna", dec("koruna", "korun", "haléř", "haléřů"),
    [(1953, 3000), (1970, 6000), (1992, 15000)], note="After the 1953 reform, to 1992. Wages are guesses.")
cur("koruna_cz", "Czech koruna", dec("koruna", "korun", "haléř", "haléřů"),
    [(1993, 15000), (2000, 30000), (2010, 60000), (2026, 120000)], note="From February 1993. Guesses.")
cur("koruna_sk", "Slovak koruna", dec("koruna", "korún", "halier", "halierov"),
    [(1993, 12000), (2008, 35000)], note="1993-2008, then the euro. Guesses.")
cur("korona_hu", "Hungarian korona", dec("korona", "korona", "fillér", "fillér"),
    [(1919, 2000), (1925, 2000000)], note="1919-1926, through the inflation (rough).")
cur("pengo", "Hungarian pengő", dec("pengő", "pengő", "fillér", "fillér"),
    [(1927, 300), (1939, 300), (1944, 1000)], note="1927-1946; the 1946 hyperinflation is not followed.")
cur("forint", "Hungarian forint", dec("forint", "forint", "fillér", "fillér"),
    [(1946, 1500), (1960, 4000), (1980, 10000), (1990, 30000), (2000, 150000), (2010, 400000), (2026, 1200000)],
    note="Forint = 100 filler, from August 1946. Guesses.")
cur("dinar_rs_mod", "Serbian dinar", dec("dinar", "dinars", "para", "para"),
    [(1868, 150), (1900, 200), (1918, 300)], note="Kingdom of Serbia, 1868-1918. Guesses.")
cur("perper_me", "Montenegrin perper", dec("perper", "perpera", "para", "para"),
    [(1906, 200), (1918, 300)], note="1906-1918. Guesses.")
cur("dinar_yu", "Yugoslav dinar", dec("dinar", "dinars", "para", "para"),
    [(1919, 2000), (1930, 3000), (1940, 4000), (1950, 30000), (1965, 100000)], note="1918-1965. Guesses.")
cur("dinar_yu_1966", "Yugoslav dinar", dec("dinar", "dinars", "para", "para"),
    [(1966, 1500), (1980, 30000), (1988, 1000000)], note="Heavy dinar (100 old), 1966-1989 (rough).")
cur("dinar_yu_1990", "Yugoslav dinar", dec("dinar", "dinars", "para", "para"),
    [(1990, 15000), (1992, 100000), (2002, 50000)],
    note="Convertible dinar 1990 onwards; the 1992-1994 hyperinflation and the 1994 dinar are not followed.")
cur("dinar_rs", "Serbian dinar", dec("dinar", "dinars", "para", "para"),
    [(2003, 50000), (2010, 100000), (2026, 300000)], note="From 2003. Guesses.")
cur("kuna_ndh", "Croatian kuna", dec("kuna", "kunas", "banica", "banicas"),
    [(1941, 3000), (1945, 10000)], note="Independent State of Croatia, 1941-1945. Guesses.")
cur("dinar_hr", "Croatian dinar", [("dinar", "dinars", 1)], [(1991, 500), (1994, 5000)],
    note="1991-1994 (no subunit in use). Guesses.")
cur("kuna", "Croatian kuna", dec("kuna", "kunas", "lipa", "lipa"),
    [(1994, 3000), (2010, 25000), (2022, 40000)], note="1994-2022, then the euro. Guesses.")
cur("tolar", "Slovenian tolar", dec("tolar", "tolars", "stotin", "stotins"),
    [(1991, 100000), (2006, 400000)], note="1991-2006, then the euro. Guesses.")
cur("dinar_ba", "Bosnian dinar", [("dinar", "dinars", 1)], [(1992, 1000), (1998, 10000)], note="1992-1998.")
cur("mark_ba", "convertible mark", dec("mark", "marks", "fening", "feninga"),
    [(1998, 1500), (2010, 3000), (2026, 6000)], note="Bosnia and Herzegovina from 1998. Guesses.")
cur("denar_mk", "Macedonian denar", dec("denar", "denars", "deni", "deni"),
    [(1993, 30000), (2026, 150000)], note="From 1993 (after the 100 to 1 change). Guesses.")
cur("drachma_mod", "Greek drachma", dec("drachma", "drachmae", "lepton", "lepta"),
    [(1832, 150), (1900, 250), (1914, 300), (1930, 4000), (1940, 6000)],
    note="Modern drachma = 100 lepta, 1832-1944. Guesses.")
cur("drachma_new", "Greek drachma", dec("drachma", "drachmae", "lepton", "lepta"),
    [(1944, 1000), (1954, 2000), (1970, 15000), (1980, 60000), (1990, 300000), (2001, 1200000)],
    note="After 1944 (the 1944 and 1954 changes are not told apart; the 1944-1953 inflation is not followed).")
cur("lek_old", "Albanian lek", dec("lek", "lekë", "qindarkë", "qindarka"),
    [(1926, 200), (1946, 5000), (1964, 50000)], note="1926-1964. Guesses.")
cur("lek", "Albanian lek", dec("lek", "lekë", "qindarkë", "qindarka"),
    [(1965, 1000), (1990, 2000), (2000, 40000), (2026, 150000)], note="New lek (10 old) from 1965. Guesses.")
cur("lev_old", "Bulgarian lev", dec("lev", "leva", "stotinka", "stotinki"),
    [(1881, 150), (1914, 300), (1930, 5000), (1951, 30000)], note="1881-1951. Guesses.")
cur("lev_1952", "Bulgarian lev", dec("lev", "leva", "stotinka", "stotinki"),
    [(1952, 1000), (1961, 2000)], note="1952-1961. Guesses.")
cur("lev", "Bulgarian lev", dec("lev", "leva", "stotinka", "stotinki"),
    [(1962, 300), (1980, 600), (1990, 1500), (1997, 500000)], note="1962-1998 (the 1997 inflation roughly).")
cur("lev_1999", "Bulgarian lev", dec("lev", "leva", "stotinka", "stotinki"),
    [(1999, 800), (2010, 2500), (2025, 7000)], note="New lev (1,000 old) 1999-2025; the euro from 1 January 2026.")
cur("leu_ro", "Romanian leu", dec("leu", "lei", "ban", "bani"),
    [(1867, 150), (1900, 200), (1914, 300), (1930, 10000), (1946, 1000000)], note="1867-1947 (rough later).")
cur("leu_ro_1947", "Romanian leu", dec("leu", "lei", "ban", "bani"),
    [(1947, 1000), (1951, 2000)], note="After the 1947 stabilisation, to 1951. Guesses.")
cur("leu_ro_1952", "Romanian leu", dec("leu", "lei", "ban", "bani"),
    [(1952, 500), (1970, 4000), (1989, 10000), (1995, 700000), (2004, 30000000)], note="1952-2004. Guesses.")
cur("leu_ro_2005", "Romanian leu", dec("leu", "lei", "ban", "bani"),
    [(2005, 3000), (2010, 6000), (2026, 18000)], note="New leu (10,000 old) from 2005. Guesses.")
cur("leu_md", "Moldovan leu", dec("leu", "lei", "ban", "bani"),
    [(1993, 500), (2010, 10000), (2026, 40000)], note="From 1993. Guesses.")
cur("pound_cy_old", "Cypriot pound", [("pound", "pounds", 180), ("shilling", "shillings", 9),
                                      ("piastre", "piastres", 1)],
    [(1879, 9), (1914, 18), (1950, 60)], note="Pound = 20 shillings = 180 piastres, 1879-1954. Guesses.")
cur("pound_cy", "Cypriot pound", [("pound", "pounds", 1000), ("cent", "cents", 10, 1983), ("mil", "mils", 1, None, 1982)],
    [(1955, 400), (1980, 3000), (2000, 15000), (2007, 20000)],
    note="Decimal pound: 1,000 mils (100 cents from 1983), 1955-2007, then the euro. Guesses.")
cur("lira_mt", "Maltese lira", [("lira", "liri", 1000), ("cent", "cents", 10), ("mil", "mils", 1)],
    [(1972, 2000), (1990, 6000), (2007, 12000)], note="1972-2007 (also called the Maltese pound). Guesses.")
cur("pound_ie", "Irish pound", [("pound", "pounds", 960), ("shilling", "shillings", 48), ("penny", "pence", 4),
                                ("farthing", "farthings", 1)],
    [(1928, 480), (1950, 700), (1970, 2400)], note="Saorstat pound = sterling, 1928-1970. Guesses.")
cur("pound_ie_dec", "Irish pound", dec("pound", "pounds", "penny", "pence"),
    [(1971, 250), (1990, 3000), (2001, 5000)], note="Decimal Irish pound, 1971-2001. Guesses.")

# --- Europe rows, 1800 onwards ---
row("it_napoleonic", "lira_it", 1800, 1814, ru("Italian Republic", "Kingdom of Naples (Napoleonic)"), 44)
row("it_sardinia", "lira_it", 1816, 1861, ru("Kingdom of Sardinia"), 44)
row("it_two_sicilies", "ducato_napoli", 1472, 1860,
    [ru("Kingdom of Naples", "Kingdom of the Two Sicilies"), bx(NAPLES), bx(SICILY)], 42)
row("it_papal_scudo", "scudo_papal", 1535, 1866, [ru("Papal States"), bx(PAPAL)], 43)
row("it_papal_lira", "lira_it", 1867, 1870, ru("Papal States"), 44)
row("it_kingdom", "lira_it", 1861, 1946, ru("Kingdom of Italy"), 45)
row("it_republic", "lira_it", 1946, 2001, ru("Republic of Italy"), 45)
row("it_box", "lira_it", 1861, 2001, [bx(ITALY_PEN), bx(SARDINIA), bx(SICILY)], 31)
row("es_peseta", "peseta", 1869, 2001, ru("Kingdom of Spain", "First Spanish Republic", "Second Spanish Republic",
                                           "Spanish Nationalists", "Francoist Spain"), 45)
row("es_peseta_box", "peseta", 1869, 2001, bx(SPAIN), 31)
row("pt_real", "real_pt", 1435, 1910, ru("Kingdom of Portugal", "Portuguese Colonies"), 44)
row("pt_real_box", "real_pt", 1435, 1910, bx(PORTUGAL), 33)
row("pt_escudo", "escudo_pt", 1911, 2001, ru("Portuguese Republic", "Estado Novo", "Portugal"), 44)
row("pt_escudo_box", "escudo_pt", 1911, 2001, bx(PORTUGAL), 33)
row("de_mark_rulers", "mark", 1873, 1947, [ru("German Empire", "Weimar Republic"), rb("Nazi Germany", GERMANY),
                                           rb("Nazi Germany", AUSTRIA)], 45)
row("de_thaler_north", "thaler", 1800, 1872, ru("Kingdom of Prussia", "North German Confederation",
                                                "Kingdom of Saxony", "German Confederation",
                                                "Confederation of the Rhine", "Free City of Danzig"), 41)
row("de_gulden_south", "gulden_kreuzer", 1754, 1875, ru("Duchy of Bavaria", "Kingdom of Bavaria", "Grand Duchy of Baden",
                                                        "Electorate of Baden", "Republic of Baden",
                                                        "Free City of Frankfurt"), 42)
row("de_dm_rulers", "deutsche_mark", 1948, 2001, ru("Federal Republic of Germany", "Federated Republic of Germany"), 45)
row("de_ddr", "ddr_mark", 1949, 1990, ru("German Democratic Republic"), 46)
row("habsburg_gulden", "gulden_kreuzer", 1500, 1856, ru("House of Habsburg", "Habsburg Monarchy", "Austrian Empire"), 42)
row("at_gulden", "gulden_at", 1857, 1891, ru("Austrian Empire", "Austria-Hungary"), 43)
row("at_krone", "krone_au", 1892, 1918, ru("Austria-Hungary"), 43)
row("at_krone_rep", "krone_at", 1919, 1924, ru("Republic of Austria"), 45)
row("at_schilling", "schilling_at", 1925, 1937, ru("Republic of Austria"), 45)
row("at_schilling_box", "schilling_at", 1945, 2001, [ru("Second Republic of Austria"), bx(AUSTRIA)], 44)
row("nl_guilder_old", "guilder_nl_old", 1500, 1816, [ru("Dutch Republic", "Sovereign Principality of the United Netherlands",
                                                       "Napoleonic Batavia Republic", "Batavian Republic"),
                                                    bx(BENELUX)], 31)
row("nl_guilder", "guilder_nl", 1817, 2001, [ru("Netherlands"), bx(NETHERLANDS)], 44)
row("be_franc", "franc_be", 1832, 2001, [ru("Kingdom of Belgium"), bx(BELGIUM)], 45)
row("lu_franc", "franc_lu", 1854, 2001, ru("Luxembourg"), 46)
row("ch_gulden", "gulden_kreuzer", 1500, 1849, [ru("Swiss Confederation"), bx(SWISS)], 43)
row("ch_franc", "franc_ch", 1850, 2100, [ru("Swiss Confederation", "Principality of Liechtenstein"), bx(SWISS)], 46)
row("dk_rigsdaler", "rigsdaler_dk", 1534, 1874, [ru("Denmark-Norway", "Greenland"), bx(DENMARK)], 42)
row("dk_krone", "krone_dk", 1875, 2100, [ru("Denmark-Norway", "Greenland", "Denmark"), bx(DENMARK), bx(GREENLAND)], 42)
row("no_rigsdaler", "rigsdaler_dk", 1534, 1815, [bx(b) for b in NORWAY], 43)
row("no_speciedaler", "speciedaler", 1816, 1874, [ru("Kingdom of Norway")] + [bx(b) for b in NORWAY], 46)
row("no_krone", "krone_no", 1875, 2100, [ru("Kingdom of Norway")] + [bx(b) for b in NORWAY], 46)
row("se_daler", "daler_se", 1534, 1776, [ru("Kingdom of Sweden", "Swedish Empire"), bx(SWEDEN)], 41)
row("se_riksdaler", "riksdaler_se", 1777, 1872, [ru("Kingdom of Sweden", "Swedish Empire",
                                                    "United Kingdoms of Sweden and Norway"), bx(SWEDEN)], 41)
row("se_krona", "krona_se", 1873, 2100, [ru("Kingdom of Sweden", "United Kingdoms of Sweden and Norway"),
                                         bx(SWEDEN)], 41)
row("fi_markka_ru", "markka_old", 1860, 1917, rb("Russian Empire", FINLAND), 47)
row("fi_markka_old", "markka_old", 1918, 1962, [ru("Republic of Finland"), bx(FINLAND)], 45)
row("fi_markka", "markka", 1963, 2001, [ru("Republic of Finland"), bx(FINLAND)], 45)
row("is_danish_rigsdaler", "rigsdaler_dk", 1600, 1874, bx(ICELAND), 41)
row("is_danish_krone", "krone_dk", 1875, 1917, bx(ICELAND), 41)
row("is_krona_old", "krona_is_old", 1918, 1980, [ru("Kingdom of Iceland", "Republic of Iceland"), bx(ICELAND)], 45)
row("is_krona", "krona_is", 1981, 2100, [ru("Republic of Iceland"), bx(ICELAND)], 45)
row("pl_marka", "marka_pl", 1917, 1923, ru("Polish Armed Forces", "Second Polish Republic"), 45)
row("pl_zloty_old", "zloty_pl_old", 1924, 1939, ru("Second Polish Republic"), 45)
row("pl_zloty_old_box", "zloty_pl_old", 1945, 1949, bx(POLAND), 34)
row("pl_zloty", "zloty_pl", 1950, 1994, [ru("Republic of Poland"), bx(POLAND)], 45)
row("pl_zloty_new", "zloty_new", 1995, 2100, [ru("Republic of Poland"), bx(POLAND)], 45)
row("cs_koruna_old", "koruna_cs_old", 1919, 1952, ru("Czechoslovakia"), 45)
row("cs_koruna", "koruna_cs", 1953, 1992, ru("Czechoslovakia", "Czech Republic", "Slovakia"), 45)
CZECHIA = [48.55, 12.1, 51.06, 18.86]
row("cs_koruna_old_box", "koruna_cs_old", 1919, 1952, [bx(CZECHIA), bx(SLOVAKIA)], 34)
row("cs_koruna_box", "koruna_cs", 1953, 1992, [bx(CZECHIA), bx(SLOVAKIA)], 34)
row("cz_koruna_box", "koruna_cz", 1993, 2100, bx(CZECHIA), 34)
row("sk_koruna_box", "koruna_sk", 1993, 2008, bx(SLOVAKIA), 34)
row("sk_euro_box", EURO, 2009, 2100, bx(SLOVAKIA), 34, pay=PAY_EURO_SK)
row("ddr_box", "ddr_mark", 1948, 1990, bx([50.2, 11.0, 54.7, 15.1]), 34)
row("cz_koruna", "koruna_cz", 1993, 2100, ru("Czech Republic"), 45)
row("sk_koruna", "koruna_sk", 1993, 2008, ru("Slovakia"), 45)
row("hu_korona", "korona_hu", 1919, 1926, ru("Hungarian Republic"), 45)
row("hu_pengo", "pengo", 1927, 1945, [ru("Hungarian Republic"), bx(HUNGARY)], 44)
row("hu_forint", "forint", 1946, 2100, [ru("Hungary", "Hungarian People's Republic"), bx(HUNGARY)], 44)
row("rs_ottoman", "akce", 1460, 1843, ru("Kingdom of Serbia", "Serbs", "Principality of Wallachia",
                                         "Principality of Moldavia"), 41)
row("rs_kurus", "kurus", 1844, 1867, ru("Kingdom of Serbia", "Serbs", "Principality of Wallachia",
                                        "Principality of Moldavia", "United Principalities of Moldavia and Wallachia",
                                        "Montenegro"), 41)
row("rs_dinar", "dinar_rs_mod", 1868, 1918, ru("Kingdom of Serbia", "Serbs", "Serbia"), 45)
row("me_gulden", "gulden_at", 1868, 1891, ru("Montenegro"), 45)
row("me_krone", "krone_au", 1892, 1905, ru("Montenegro"), 45)
row("me_perper", "perper_me", 1906, 1918, ru("Montenegro"), 45)
row("yu_dinar", "dinar_yu", 1919, 1965, ru("Yugoslavia", "Yugoslav Partisans", "Socialist Federal Republic of Yugoslavia"), 45)
row("yu_dinar_1966", "dinar_yu_1966", 1966, 1989, ru("Socialist Federal Republic of Yugoslavia"), 45)
row("yu_dinar_1990", "dinar_yu_1990", 1990, 2002, ru("Socialist Federal Republic of Yugoslavia", "Serbia-Montenegro"), 45)
row("rs_dinar_2003", "dinar_rs", 2003, 2100, ru("Serbia-Montenegro", "Republic of Serbia"), 45)
row("me_dm", "deutsche_mark", 1999, 2001, [ru("Montenegro"), bx(MONTENEGRO)], 47)
row("xk_dm", "deutsche_mark", 1999, 2001, [ru("Kosovo"), bx(KOSOVO)], 47)
row("hr_kuna_ndh", "kuna_ndh", 1941, 1945, ru("Independent State of Croatia"), 46)
row("hr_dinar", "dinar_hr", 1991, 1993, ru("Republic of Croatia"), 45)
row("hr_kuna", "kuna", 1994, 2022, ru("Republic of Croatia"), 45)
row("si_tolar", "tolar", 1991, 2006, ru("Republic of Slovenia"), 45)
row("ba_dinar", "dinar_ba", 1992, 1997, ru("Bosnia and Herzegovina"), 45)
row("ba_mark", "mark_ba", 1998, 2100, ru("Bosnia and Herzegovina"), 45)
row("mk_denar", "denar_mk", 1992, 2100, ru("Former Yugoslav Republic of Macedonia"), 45)
row("gr_drachma", "drachma_mod", 1832, 1943, [ru("First Hellenic Republic", "Cretan State"), bx(GREECE_MOD)], 44)
row("gr_drachma_new", "drachma_new", 1944, 2001, [ru("First Hellenic Republic", "Kingdom of Greece", "Greek junta",
                                                     "Third Hellenic Republic"), bx(GREECE_MOD)], 44)
row("al_kurus", "kurus", 1912, 1925, ru("Albania"), 45)
row("al_lek_old", "lek_old", 1926, 1964, [ru("Albania", "People's Socialist Republic of Albania"), bx(ALBANIA)], 45)
row("al_lek", "lek", 1965, 2100, [ru("People's Socialist Republic of Albania", "Republic of Albania"), bx(ALBANIA)], 45)
row("bg_lev_old", "lev_old", 1881, 1951, [ru("Principality of Bulgaria", "Kingdom of Bulgaria", "People's Republic of Bulgaria"),
                                          bx(BULGARIA)], 44)
row("bg_lev_1952", "lev_1952", 1952, 1961, [ru("People's Republic of Bulgaria"), bx(BULGARIA)], 44)
row("bg_lev", "lev", 1962, 1998, [ru("People's Republic of Bulgaria", "Republic of Bulgaria"), bx(BULGARIA)], 44)
row("bg_lev_1999", "lev_1999", 1999, 2025, [ru("Republic of Bulgaria"), bx(BULGARIA)], 44)
row("ro_leu", "leu_ro", 1867, 1946, [ru("United Principalities of Moldavia and Wallachia", "Kingdom of Romania"),
                                     bx(ROMANIA)], 44)
row("ro_leu_1947", "leu_ro_1947", 1947, 1951, [ru("Kingdom of Romania", "Socialist Republic of Romania"), bx(ROMANIA)], 44)
row("ro_leu_1952", "leu_ro_1952", 1952, 2004, [ru("Socialist Republic of Romania", "Romania"), bx(ROMANIA)], 44)
row("ro_leu_2005", "leu_ro_2005", 2005, 2100, [ru("Romania"), bx(ROMANIA)], 44)
row("md_leu", "leu_md", 1993, 2100, ru("Republic of Moldova"), 46)
row("cy_pound_old", "pound_cy_old", 1879, 1954, bx(CYPRUS), 34)
row("cy_pound", "pound_cy", 1955, 2007, [ru("Republic of Cyprus"), bx(CYPRUS)], 44)
row("mt_sterling", "pound_lsd", 1825, 1970, bx(MALTA), 40, pay=[(1825, 24), (1900, 48), (1950, 300), (1970, 1000)])
row("mt_gbp", "gbp", 1971, 1971, bx(MALTA), 40)
row("mt_lira", "lira_mt", 1972, 2007, [ru("Malta"), bx(MALTA)], 45)
row("ie_sterling", "pound_lsd", 1922, 1927, ru("Irish Free State"), 45)
row("ie_pound", "pound_ie", 1928, 1970, ru("Irish Free State", "Éire"), 45)
row("ie_pound_dec", "pound_ie_dec", 1971, 2001, ru("Éire"), 45)
# The euro: cash from 2002, then each new member
row("euro_members", EURO, 2002, 2100, ru("Second Republic of Austria", "Éire", "Republic of Finland",
                                         "Kingdom of Belgium", "Luxembourg", "Republic of Italy",
                                         "Federated Republic of Germany", "Principality of Monaco",
                                         "Principality of Andorra"), 46)
row("euro_portugal", EURO, 2002, 2100, ru("Portugal"), 46, pay=PAY_EURO_PT)
row("euro_greece", EURO, 2002, 2100, ru("Third Hellenic Republic"), 46, pay=PAY_EURO_GR)
row("euro_me_xk", EURO, 2002, 2100, ru("Montenegro", "Kosovo"), 46, pay=[(2002, 1300), (2026, 2800)])
row("euro_spain", EURO, 2002, 2100, rb("Kingdom of Spain", [27, -18.5, 44, 4.5]), 46, pay=[(2002, 5000), (2026, 8500)])
row("euro_netherlands", EURO, 2002, 2100, rb("Netherlands", BENELUX), 46)
row("euro_france", EURO, 2002, 2100, [rb("French Fifth Republic", [41, -5.5, 51.5, 10]),
                                      rb("French Fifth Republic", [1.5, -55, 6, -51]),
                                      rb("French Fifth Republic", [-21.5, 55, -20.8, 56]),
                                      rb("French Fifth Republic", [14, -62, 16.6, -60.7]),
                                      rb("French Fifth Republic", [-13.1, 44.9, -12.5, 45.4])], 46)
row("euro_slovenia", EURO, 2007, 2100, ru("Republic of Slovenia"), 46, pay=[(2007, 3500), (2026, 6500)])
row("euro_cyprus_malta", EURO, 2008, 2100, ru("Republic of Cyprus", "Malta"), 46, pay=PAY_EURO_CY)
row("euro_slovakia", EURO, 2009, 2100, ru("Slovakia"), 46, pay=PAY_EURO_SK)
row("euro_estonia", EURO, 2011, 2100, ru("Republic of Estonia"), 46, pay=PAY_EURO_EE)
row("euro_latvia", EURO, 2014, 2100, ru("Republic of Latvia"), 46, pay=PAY_EURO_LV)
row("euro_lithuania", EURO, 2015, 2100, ru("Republic of Lithuania"), 46, pay=PAY_EURO_LT)
row("euro_croatia", EURO, 2023, 2100, ru("Republic of Croatia"), 46, pay=[(2023, 4500), (2026, 5500)])
row("euro_bulgaria", EURO, 2026, 2100, [ru("Republic of Bulgaria"), bx(BULGARIA)], 46, pay=[(2026, 3800)],
    note="Bulgaria adopted the euro on 1 January 2026.")
row("euro_box_new", EURO, 2002, 2100, [bx(AUSTRIA), bx(FINLAND)], 30)
row("euro_box_pt", EURO, 2002, 2100, bx(PORTUGAL), 30, pay=PAY_EURO_PT)
row("euro_box_gr", EURO, 2002, 2100, bx(GREECE_MOD), 30, pay=PAY_EURO_GR)
row("euro_box_mt", EURO, 2008, 2100, bx(MALTA), 30, pay=PAY_EURO_CY)

rate("lira_it", 193627, EURO, 100, 1999, 2100, "1,936.27 lire = 1 euro.")
rate("peseta", 16638600, EURO, 100000, 1999, 2100, "166.386 pesetas = 1 euro.")
rate("escudo_pt", 20048200, EURO, 100000, 1999, 2100, "200.482 escudos = 1 euro.")
rate("guilder_nl", 220371, EURO, 100000, 1999, 2100, "2.20371 guilders = 1 euro.")
rate("franc_be", 4033990, EURO, 100000, 1999, 2100, "40.3399 Belgian francs = 1 euro.")
rate("franc_lu", 4033990, EURO, 100000, 1999, 2100)
rate("schilling_at", 1376030, EURO, 100000, 1999, 2100, "13.7603 schillings = 1 euro.")
rate("markka", 594573, EURO, 100000, 1999, 2100, "5.94573 markkaa = 1 euro.")
rate("pound_ie_dec", 78756, EURO, 100000, 1999, 2100, "0.787564 Irish pounds = 1 euro.")
rate("drachma_new", 34075000, EURO, 100000, 2001, 2100, "340.750 drachmae = 1 euro.")
rate("tolar", 2396400, EURO, 10000, 2007, 2100, "239.640 tolars = 1 euro.")
rate("pound_cy", 585274, EURO, 100000, 2008, 2100, "0.585274 Cypriot pounds = 1 euro.")
rate("lira_mt", 429300, EURO, 100000, 2008, 2100, "0.4293 Maltese liri = 1 euro.")
rate("koruna_sk", 3012600, EURO, 100000, 2009, 2100, "30.126 korunas = 1 euro.")
rate("kuna", 753450, EURO, 100000, 2023, 2100, "7.5345 kunas = 1 euro.")
rate("lev_1999", 195583, EURO, 100000, 2026, 2100, "1.95583 leva = 1 euro.")
rate("pound_lsd", 960, "pound_ie", 960, 1928, 1970, "The Irish pound was at par with sterling.")
rate("gbp", 100, "pound_ie_dec", 100, 1971, 1978, "At par until March 1979.")
rate("zloty_pl", 1000000, "zloty_new", 100, 1995, 2100, "10,000 old zlotys = 1 new.")
rate("leu_ro_1952", 1000000, "leu_ro_2005", 100, 2005, 2100, "10,000 old lei = 1 new.")
rate("lev", 100000, "lev_1999", 100, 1999, 2100, "1,000 old leva = 1 new.")
rate("markka_old", 10000, "markka", 100, 1963, 2100, "100 old markkaa = 1 new.")
rate("krona_is_old", 10000, "krona_is", 100, 1981, 2100, "100 old kronur = 1 new.")
rate("deutsche_mark", 100, "ddr_mark", 100, 1990, 1990, "Wages and prices changed 1 to 1 in July 1990.")


# ==============================================================================================================
# EUROPE before 1800
# ==============================================================================================================
cur("denier", "Frankish denier", [("pound", "pounds", 240, 793), ("shilling", "shillings", 12), ("denier", "deniers", 1)],
    [(650, 1), (799, 2)], note="Merovingian and Carolingian silver penny; pound and shilling as counting units from"
                               " Charlemagne's reform. Wages are guesses.")
cur("pfennig", "pfennig", [("gulden", "gulden", 240, 1354), ("groschen", "groschen", 12, 1300), ("pfennig", "pfennigs", 1)],
    [(800, 1), (1100, 2), (1250, 3), (1350, 6), (1450, 12), (1499, 16)],
    note="The penny of the German lands, Bohemia and the Low Countries before the thaler; groschen from about 1300"
         " (Prague 1300), the Rhenish gulden from 1354 (both changed a lot against the penny). Wages are guesses.")
cur("lira_it_old", "Italian lira of account", [("lira", "lire", 240), ("soldo", "soldi", 12), ("denaro", "denari", 1)],
    [(650, 1), (800, 2), (1000, 4), (1200, 12), (1300, 36), (1350, 96), (1400, 120), (1500, 180), (1600, 300),
     (1700, 360), (1800, 480)],
    note="Lira = 20 soldi = 240 denari, the counting money of the Italian states (Venice, Genoa, Milan, Florence"
         " and the rest; their gold ducats and florins changed against it). Wages are guesses.")
cur("dinheiro_pt", "Portuguese dinheiro", [("libra", "libras", 240), ("soldo", "soldos", 12), ("dinheiro", "dinheiros", 1)],
    [(1147, 3), (1434, 12)], note="1147-1434, before the real. Wages are guesses.")
cur("maravedi_cas", "Castilian maravedí", [("maravedí", "maravedís", 10), ("dinero", "dineros", 1)],
    [(1100, 4), (1300, 30), (1400, 100), (1496, 250)],
    note="Maravedi = 10 dineros in Castile and Leon before the 1497 reform (the gold dobla changed against it)."
         " Wages are guesses.")
cur("diner_ar", "Aragonese diner", [("lliura", "lliures", 240), ("sou", "sous", 12), ("diner", "diners", 1)],
    [(1100, 2), (1300, 12), (1400, 24), (1515, 36)], note="Lliura = 20 sous = 240 diners. Wages are guesses.")
cur("norse_silver", "weighed silver", [("mark", "marks", 240), ("øre", "øre", 30), ("ørtug", "ørtugar", 10)],
    [(800, 3), (1049, 3)], kind="weighed", metal="silver", decimals=1, mass=True,
    note="Viking-age silver by weight (hacksilver, rings, cut coins): mark = 8 ore = 24 ortugar. A day's work near"
         " a third of an ortug (2-3 grams) is a guess.")
cur("scandi_mark", "Scandinavian mark", [("mark", "marks", 240), ("øre", "øre", 30), ("ørtug", "ørtugar", 10),
                                          ("penning", "penninge", 1)],
    [(1050, 3), (1250, 6), (1400, 12), (1533, 48)],
    note="Medieval Danish, Norwegian and Swedish counting: mark = 8 ore = 24 ortugar = 240 penninge (the Swedish"
         " mark had 192). Wages are guesses.")
cur("vadmal", "homespun cloth (vaðmál)", [("hundred", "hundreds", 120), ("ell", "ells", 1)],
    [(874, 2), (1599, 2)], mass=True,
    note="Icelandic and Norse Greenland money of account: ells of homespun wool cloth; a hundred = 120 ells (a cow's"
         " worth). A day's work near 2 ells is a guess.")
cur("denar_pl", "Polish denar", [("grzywna", "grzywny", 240), ("denar", "denars", 1)],
    [(990, 2), (1337, 4)], note="Silver penny of the Piast kingdom; the grzywna (mark) as counting unit. Guesses.")
cur("grosz_pl", "Polish grosz", [("złoty", "złote", 540, 1496), ("grosz", "groszy", 18), ("denar", "denars", 1)],
    [(1338, 18), (1500, 36), (1600, 90), (1700, 270), (1794, 540)],
    note="Krakow grosz from 1338 (18 denars), the zloty of 30 groszy as counting unit from 1496. Guesses.")
cur("denar_hu", "Hungarian denár", [("forint", "forint", 100, 1325), ("denár", "denár", 1)],
    [(1000, 1), (1300, 2), (1450, 4), (1526, 8)],
    note="Silver denar from Stephen I; the gold forint (florin) from 1325, near 100 denars. Guesses.")
cur("dinar_rs_med", "Serbian medieval dinar", [("perper", "perpers", 24), ("dinar", "dinars", 2), ("half dinar", "half dinars", 1)],
    [(1214, 2), (1459, 2)], note="Perper (counting unit) = 12 dinars. A dinar a day is a guess.")
cur("grivna", "Rus' grivna", [("grivna", "grivnas", 150), ("kuna", "kunas", 6), ("rezana", "rezanas", 3),
                               ("veksha", "vekshas", 1)],
    [(900, 3), (1380, 3)], note="Grivna of silver (ingots) = 25 kunas = 50 rezanas = 150 vekshas (Russkaya Pravda)."
                                " A rezana a day is a guess.")
cur("denga", "Muscovite denga", [("ruble", "rubles", 200, 1400), ("altyn", "altyns", 6), ("denga", "dengas", 1)],
    [(1381, 1), (1534, 2)], note="Silver denga from the 1380s; ruble (counting) = 200 dengas. Guesses.")
cur("scudo_mt", "Maltese scudo", [("scudo", "scudi", 240), ("tarì", "tarì", 20), ("grano", "grani", 1)],
    [(1530, 10), (1798, 20)], note="Knights of Malta: scudo = 12 tari = 240 grani. Guesses.")

row("west_denier", "denier", 650, 799, bx(WEST_EUROPE), 15)
row("franks_denier", "denier", 650, 799, ru("Kingdom of the Franks", "Aquitaine", "Kingdom of Neustria", "Bavarians",
                                            "Kingdom of Alamannia", "Frisia Kingdom", "Saxons"), 21)
row("central_pfennig", "pfennig", 800, 1499, bx(CENTRAL_EUROPE), 24)
row("italy_lira_old", "lira_it_old", 650, 1860, [bx(ITALY_PEN), bx(SARDINIA), bx(SICILY)], 22)
row("italy_states", "lira_it_old", 705, 1860, ru("Republic of Venice", "Republic of Genoa", "Republic of Florence",
                                                 "Duchy of Milan", "County of Savoy", "House of Savoy",
                                                 "Grand Duchy of Tuscany", "Duchy of Spoleto", "Duchy of Benevento",
                                                 "Norman Italy", "Kingdom of Sicily", "House of Anjou-Sicily",
                                                 "Duchy of Naples", "Kingdom of Italy", "Kingdom of Sardinia"), 40)
row("malta_scudo", "scudo_mt", 1530, 1824, bx(MALTA), 40)
row("pt_dinheiro", "dinheiro_pt", 1139, 1434, [ru("County of Portugal", "Kingdom of Portugal"), bx(PORTUGAL)], 33)
row("castile", "maravedi_cas", 900, 1496, ru("Kingdom of Castile", "Crown of Castile", "Kingdom of Navarre",
                                             "Kingdom of León"), 31)
row("aragon", "diner_ar", 830, 1515, ru("County of Aragon", "Kingdom of Aragon", "Crown of Aragon"), 32)
row("scandinavia_silver", "norse_silver", 800, 1049, [bx(SCANDINAVIA), ru("Viking settlements",
                                                                         "Scandinavian minor kingdoms")], 25)
row("scandinavia_mark", "scandi_mark", 1050, 1533, [bx(SCANDINAVIA), ru("Old Kingdom of Norway", "Kingdom of Denmark",
                                                                       "Kingdom of Sweden", "Kalmar Union",
                                                                       "Norway-Denmark", "Danish Magnates")], 25)
row("iceland_vadmal", "vadmal", 874, 1599, [bx(ICELAND), bx(GREENLAND_NORSE),
                                            ru("Icelandic Commonwealth", "Norse Greenland")], 26)
row("poland_denar", "denar_pl", 962, 1337, [ru("Kingdom of Poland", "Duchy of Greater Poland", "Duchies of Poland"),
                                           bx(POLAND)], 26)
POLAND_LITHUANIA = [47.5, 14.1, 59, 36]
row("poland_grosz", "grosz_pl", 1338, 1794, [rb(["Kingdom of Poland", "House of Jagiellon", "Polish-Lithuanian Commonwealth",
                                                 "Pro-Swedish Poland", "Grand Duchy of Lithuania", "Duchy of Prussia"],
                                                POLAND_LITHUANIA)], 41,
    note="Only inside Poland-Lithuania: the register also gives Saxony to the Commonwealth under its Saxon kings,"
         " where the thaler stayed.")
row("poland_grosz_box", "grosz_pl", 1338, 1794, bx(POLAND), 26)
row("hungary_denar", "denar_hu", 1000, 1526, [ru("Principality of Hungary", "Kingdom of Hungary", "Kingdom of Croatia",
                                                "Principality of Wallachia", "Principality of Moldavia"), bx(HUNGARY)], 27)
row("hungary_east", "gulden_kreuzer", 1527, 1856, ru("Eastern Hungarian Kingdom", "Principality of Transylvania",
                                                     "Principality of Upper Hungary", "Kingdom of Hungary"), 41)
row("serbia_dinar", "dinar_rs_med", 1214, 1459, ru("Grand Principality of Serbia", "Kingdom of Serbia", "Serbian Empire",
                                               "Serbian Despots", "Banate of Bosnia", "Kingdom of Bosnia",
                                               "Albanian Principalities"), 41)
row("bulgaria_solidus", "solidus", 1188, 1394, ru("Second Bulgarian Empire", "Despotate of Epirus", "Nicaean Empire"), 41)
row("rus_grivna", "grivna", 882, 1380, ru("Kievan Rus'", "Novgorod Republic", "Principality of Kiev",
                                          "Principality of Vladimir-Suzdal", "Principality of Galicia-Volhynia",
                                          "Galicia-Volhynia", "Nizhny Novgorod", "Grand Principality of Moscow"), 40)
row("rus_denga", "denga", 1381, 1534, ru("Grand Principality of Moscow", "Novgorod Republic",
                                         "Principality of Vladimir-Suzdal", "Nizhny Novgorod"), 40)
row("britain_sceat", "pound_lsd", 675, 799, bx(BRITAIN), 30, note="Sceattas and the first pennies.")
row("britain_no_coins", "barter", 410, 674, bx(BRITAIN), 21, note="No coins were struck or used in Britain after Rome.")
row("ireland_barter", "barter", -100000, 996, bx(IRELAND), 31, note="Irish pennies from 997 (Dublin).")
row("north_europe_barter", "barter", -146, 799, bx(NORTH_EUROPE), 8)
row("europe_barter_early", "barter", -100000, -147, bx(EUROPE_ALL), 8,
    note="Beyond the Greek cities and Rome people bartered (Celtic coins were for gifts and tribute).")
row("east_europe_barter", "barter", 650, 899, bx(EAST_EUROPE), 8)


# ==============================================================================================================
# RUSSIA, THE SOVIET UNION AND AFTER; THE BALTIC; THE CAUCASUS; CENTRAL ASIA
# ==============================================================================================================
cur("ruble_su", "Soviet ruble", dec("ruble", "rubles", "kopek", "kopeks"),
    [(1924, 100), (1930, 300), (1940, 1000), (1947, 2000), (1960, 3000)], note="Soviet ruble 1924-1960. Guesses.")
cur("ruble_su61", "Soviet ruble", dec("ruble", "rubles", "kopek", "kopeks"),
    [(1961, 300), (1970, 400), (1980, 600), (1990, 900), (1991, 1500)], note="New ruble (10 old) 1961-1991.")
cur("ruble_ru92", "Russian ruble", dec("ruble", "rubles", "kopek", "kopeks"),
    [(1992, 20000), (1995, 2000000), (1997, 4000000)], note="1992-1997, through the inflation (rough).")
cur("ruble_ru", "Russian ruble", dec("ruble", "rubles", "kopek", "kopeks"),
    [(1998, 4000), (2005, 15000), (2010, 30000), (2020, 60000), (2026, 120000)],
    note="Redenominated ruble (1,000 old) from 1998. Guesses.")
cur("karbovanets", "Ukrainian karbovanets", [("karbovanets", "karbovantsi", 1)],
    [(1992, 500), (1996, 150000)], note="1992-1996 (no subunit in use; rough).")
cur("hryvnia", "Ukrainian hryvnia", dec("hryvnia", "hryvni", "kopiyka", "kopiyok"),
    [(1996, 300), (2005, 2000), (2010, 4000), (2020, 15000), (2026, 30000)], note="From 1996. Guesses.")
cur("ruble_by92", "Belarusian ruble", [("ruble", "rubles", 1)], [(1992, 500), (1999, 300000)],
    note="1992-1999 (rough).")
cur("ruble_by00", "Belarusian ruble", [("ruble", "rubles", 1)], [(2000, 2000), (2015, 50000)],
    note="2000-2016 (1,000 old). Guesses.")
cur("ruble_by16", "Belarusian ruble", dec("ruble", "rubles", "kapeyka", "kapeyki"),
    [(2016, 1500), (2026, 5000)], note="From 2016 (10,000 of 2000). Guesses.")
cur("mark_ee", "Estonian mark", dec("mark", "marks", "penn", "penni"), [(1919, 2000), (1927, 3000)],
    note="1919-1927. Guesses.")
cur("kroon", "Estonian kroon", dec("kroon", "krooni", "sent", "senti"),
    [(1928, 300), (1940, 400), (1992, 1000), (2000, 15000), (2010, 35000)], note="1928-1940, 1992-2010. Guesses.")
cur("lats", "Latvian lats", dec("lats", "lati", "santīms", "santīmi"),
    [(1922, 300), (1940, 400), (1993, 300), (2000, 800), (2013, 2000)], note="1922-1940, 1993-2013. Guesses.")
cur("litas", "Lithuanian litas", dec("litas", "litai", "centas", "centai"),
    [(1922, 500), (1940, 500), (1993, 500), (2000, 2500), (2014, 8000)], note="1922-1940, 1993-2014. Guesses.")
cur("lari", "Georgian lari", dec("lari", "lari", "tetri", "tetri"), [(1995, 300), (2010, 1500), (2026, 4000)],
    note="From 1995. Guesses.")
cur("dram", "Armenian dram", [("dram", "drams", 1)], [(1993, 300), (2010, 5000), (2026, 10000)],
    note="From 1993 (luma not in use). Guesses.")
cur("manat_az_old", "Azerbaijani manat", [("manat", "manats", 1)], [(1992, 100), (2005, 20000)],
    note="1992-2005 (rough).")
cur("manat_az", "Azerbaijani manat", dec("manat", "manats", "qəpik", "qəpik"), [(2006, 500), (2026, 2500)],
    note="New manat (5,000 old) from 2006. Guesses.")
cur("tenge", "Kazakhstani tenge", [("tenge", "tenge", 1)], [(1993, 300), (2010, 4000), (2026, 10000)],
    note="From 1993 (tiyn not in use). Guesses.")
cur("sum_uz", "Uzbekistani sum", [("sum", "sum", 1)], [(1994, 100), (2010, 3000), (2026, 150000)],
    note="From 1994. Guesses.")
cur("som_kg", "Kyrgyzstani som", dec("som", "som", "tyiyn", "tyiyn"), [(1993, 1000), (2010, 15000), (2026, 70000)],
    note="From 1993. Guesses.")
cur("ruble_tj", "Tajikistani ruble", [("ruble", "rubles", 1)], [(1995, 300), (2000, 3000)], note="1995-2000.")
cur("somoni", "Tajikistani somoni", dec("somoni", "somoni", "diram", "diram"), [(2000, 300), (2010, 1500), (2026, 6000)],
    note="From 2000. Guesses.")
cur("manat_tm_old", "Turkmenistani manat", [("manat", "manats", 1)], [(1993, 100), (2008, 30000)], note="1993-2008.")
cur("manat_tm", "Turkmenistani manat", dec("manat", "manats", "tenge", "tenge"), [(2009, 600), (2026, 3000)],
    note="New manat (5,000 old) from 2009. Guesses.")
cur("tanga", "Bukharan tanga", [("tilla", "tillas", 1344), ("tanga", "tangas", 64), ("pul", "puls", 1)],
    [(1375, 32), (1700, 48), (1800, 64), (1920, 128)],
    note="Timurid and Uzbek silver tanga; the gold tilla near 21 tangas, the copper pul 64 to the tanga (it"
         " varied by khanate and time). Wages are guesses.")

USSR_BOXES = [[44, 30, 82, 60], [38.4, 40, 44, 50.9], [37.3, 46, 56, 73.6], [40.5, 73.6, 56, 87.5],
              [41.5, 87.5, 82, 180], [60, -180, 72, -168], [53.9, 20.9, 60, 30], [48, 23.6, 56.2, 30],
              [45.2, 28.0, 48.5, 30], [54.3, 19.6, 55.3, 22.9], [47.9, 22.1, 48.7, 23.6]]
USSR = [rb("Union of Soviet Socialist Republics", b) for b in USSR_BOXES]
row("soviet_republics_1920", "ruble", 1920, 1921, [rb("Republics of the Soviet Union", b) for b in USSR_BOXES], 41)
row("russia_ruble_rulers", "ruble", 1535, 1923, ru("Grand Principality of Moscow", "Tsardom of Russia", "Russian Empire",
                                                   "Russian Republic",
                                                   "Provisional Priamurye Government", "Ukrainian People's Republic",
                                                   "Armenia", "Azerbaijan Democratic Republic", "Sloboda Ukraine",
                                                   "Don Cossacks", "Caucasian Imamate", "Khanates of the Caucasus"), 40)
row("ussr_1922", "ruble", 1922, 1923, USSR, 45)
row("ussr_ruble", "ruble_su", 1924, 1960, USSR, 45)
row("ussr_ruble61", "ruble_su61", 1961, 1991, USSR, 45,
    note="Only inside the Soviet Union: the register also names it for occupied Eastern Europe (1946) and for"
         " Czechoslovakia after 1968, which kept their own money.")
row("ru_ruble92", "ruble_ru92", 1992, 1997, ru("Russian Federation", "Chechen Republic"), 45)
row("ru_ruble", "ruble_ru", 1998, 2100, ru("Russian Federation", "Chechen Republic", "Russian-occupied territories"), 45)
row("ua_karbovanets", "karbovanets", 1992, 1995, ru("Ukraine"), 45)
row("ua_hryvnia", "hryvnia", 1996, 2100, ru("Ukraine"), 45)
row("by_ruble92", "ruble_by92", 1992, 1999, ru("Republic of Belarus"), 45)
row("by_ruble00", "ruble_by00", 2000, 2015, ru("Republic of Belarus"), 45)
row("by_ruble16", "ruble_by16", 2016, 2100, ru("Republic of Belarus"), 45)
row("ee_mark", "mark_ee", 1919, 1927, ru("Estonia"), 45)
row("ee_kroon", "kroon", 1928, 1940, ru("Estonia"), 45)
row("ee_kroon2", "kroon", 1992, 2010, ru("Republic of Estonia"), 45)
row("lv_lats", "lats", 1922, 1940, ru("Republic of Latvia"), 45)
row("lv_soviet", "ruble_su", 1941, 1960, ru("Republic of Latvia"), 45)
row("lv_soviet61", "ruble_su61", 1961, 1991, ru("Republic of Latvia"), 45)
row("lv_ruble92", "ruble_ru92", 1992, 1992, ru("Republic of Latvia"), 45)
row("lv_lats2", "lats", 1993, 2013, ru("Republic of Latvia"), 45)
row("lt_mark", "mark", 1919, 1921, ru("Kingdom of Lithuania"), 45)
row("lt_litas", "litas", 1922, 1940, ru("Kingdom of Lithuania"), 45)
row("lt_soviet", "ruble_su61", 1990, 1992, ru("Republic of Lithuania"), 45)
row("lt_litas2", "litas", 1993, 2014, ru("Republic of Lithuania"), 45)
row("ge_ruble", "ruble", 1801, 1921, ru("Georgia", "Kingdom of Georgia"), 41)
row("ge_soviet", "ruble_su", 1922, 1960, ru("Georgia"), 41)
row("ge_soviet61", "ruble_su61", 1961, 1991, ru("Georgia"), 41)
row("ge_ruble92", "ruble_ru92", 1992, 1994, ru("Georgia"), 45)
row("ge_lari", "lari", 1995, 2100, ru("Georgia"), 45)
row("am_ruble", "ruble_ru92", 1992, 1992, ru("Republic of Armenia"), 45)
row("am_dram", "dram", 1993, 2100, ru("Republic of Armenia"), 45)
row("az_manat_old", "manat_az_old", 1992, 2005, ru("Republic of Azerbaijan"), 45)
row("az_manat", "manat_az", 2006, 2100, ru("Republic of Azerbaijan"), 45)
row("kz_ruble", "ruble_ru92", 1992, 1992, ru("Kazakhstan"), 45)
row("kz_tenge", "tenge", 1993, 2100, ru("Kazakhstan"), 45)
row("uz_ruble", "ruble_ru92", 1992, 1993, ru("Republic of Uzbekistan"), 45)
row("uz_sum", "sum_uz", 1994, 2100, ru("Republic of Uzbekistan"), 45)
row("kg_ruble", "ruble_ru92", 1992, 1992, ru("Kyrgyzstan"), 45)
row("kg_som", "som_kg", 1993, 2100, ru("Kyrgyzstan"), 45)
row("tj_ruble92", "ruble_ru92", 1992, 1994, ru("Republic of Tajikistan"), 45)
row("tj_ruble", "ruble_tj", 1995, 1999, ru("Republic of Tajikistan"), 45)
row("tj_somoni", "somoni", 2000, 2100, ru("Republic of Tajikistan"), 45)
row("tm_ruble", "ruble_ru92", 1992, 1992, ru("Turkmenistan"), 45)
row("tm_manat_old", "manat_tm_old", 1993, 2008, ru("Turkmenistan"), 45)
row("tm_manat", "manat_tm", 2009, 2100, ru("Turkmenistan"), 45)
row("md_ruble", "ruble_ru92", 1992, 1992, ru("Republic of Moldova"), 45)
row("central_asia_tanga", "tanga", 1375, 1920, ru("Timurid Empire", "Shaybanids", "Khanate of Bukhara", "Emirate of Bukhara",
                                                  "Khanate of Khiva", "Khanate of Kokand", "Eastern Moghulistan",
                                                  "Western Moghulistan", "Moghulistan", "Eastern Chagatai Khanate",
                                                  "Hotaki Dynasty", "East Turkestan"), 40)
row("horde_dirham", "dirham", 1240, 1600, ru("Golden Horde", "Blue Horde", "White Horde", "Chagatai Khanate", "Ilkhanate",
                                             "Jalayirid Sultanate", "Kartids", "Muzaffarids", "Sarbadars", "Chobanids",
                                             "Khanate of Kazan", "Astrakhan Khanate", "Crimean Khanate", "Nogai Horde",
                                             "Khanate of Sibir", "Qasim Khanate", "Qara Qoyunlu", "Aq Qoyunlu",
                                             "Volga Bulgaria", "Khazaria", "Khwarezmid Empire"), 40,
    note="Silver dirhams and dangs of the Mongol and Turkic khanates (Volga Bulgaria and Khazaria from 750).")
row("volga_dirham", "dirham", 750, 1239, ru("Volga Bulgaria", "Khazaria", "Khwarezmid Empire"), 40)
row("ru_ruble_box_late", "ruble", 1918, 1923, bx(RUSSIA_EU), 25)

rate("ruble_ru92", 100000, "ruble_ru", 100, 1998, 2100, "1,000 old rubles = 1 new.")
rate("ruble_su", 1000, "ruble_su61", 100, 1961, 1991, "10 old rubles = 1 new (1961).")
rate("ruble_su61", 100, "ruble_ru92", 100, 1992, 1997, "The Soviet ruble became the Russian ruble 1 to 1.")
rate("manat_az_old", 5000, "manat_az", 100, 2006, 2100, "5,000 old manats = 1 new.")
rate("manat_tm_old", 5000, "manat_tm", 100, 2009, 2100, "5,000 old manats = 1 new.")
rate("ruble_by00", 10000, "ruble_by16", 100, 2016, 2100, "10,000 rubles of 2000 = 1 new.")


# ==============================================================================================================
# THE MIDDLE EAST AND NORTH AFRICA
# ==============================================================================================================
IRAN = [25, 44, 40, 63.5]
MESOPOTAMIA = [29, 34, 38.5, 50]
CENTRAL_ASIA = [37, 52, 46, 80]
ARABIA = [12, 34.5, 32, 60]
EGYPT = [22, 24.5, 31.7, 35.5]
SUDAN = [8.5, 21.8, 22, 38.6]
SOUTH_SUDAN = [3.5, 24, 10, 36]
LIBYA = [19.5, 9.3, 33.2, 25.2]
TUNISIA = [30.2, 7.5, 37.6, 11.6]
ALGERIA = [19, -8.7, 37.1, 12]
MOROCCO = [27.6, -13.2, 35.95, -1.0]
WESTERN_SAHARA = [20.7, -17.2, 27.7, -8.6]
MAURITANIA = [14.7, -17.1, 27.3, -4.8]
SYRIA = [32.3, 35.7, 37.4, 42.4]
LEBANON = [33.05, 35.1, 34.7, 36.65]
PALESTINE = [29.4, 34.2, 33.35, 35.7]
JORDAN = [29.2, 35.5, 33.4, 39.3]
IRAQ = [29, 38.8, 37.4, 48.6]
KUWAIT = [28.5, 46.5, 30.1, 48.5]
BAHRAIN = [25.75, 50.3, 26.35, 50.85]
QATAR = [24.45, 50.7, 26.2, 51.7]
UAE = [22.6, 51.5, 26.1, 56.4]
OMAN = [16.6, 52, 26.4, 59.9]
YEMEN_N = [12.6, 42.5, 17.5, 46]
YEMEN_S = [12.5, 43.5, 19, 53.2]
ADEN = [12.5, 44.5, 13.2, 45.5]
TURKEY = [35.8, 25.6, 42.2, 44.9]
SAHARA_SAHEL = [12, -18, 23, 40]

cur("siglos", "Persian siglos", [("daric", "darics", 3600), ("siglos", "sigloi", 180),
                                 ("grain of silver", "grains of silver", 1)],
    [(-550, 6), (-331, 8)],
    note="Achaemenid gold daric = 20 silver sigloi; a siglos near a Babylonian shekel (180 grains); small sums in"
         " weighed silver. A day's work near 6-8 grains of silver, as in Babylon.")
cur("drachm_persian", "Persian drachm", [("drachm", "drachms", 48), ("obol", "obols", 8), ("chalkous", "chalkoi", 1)],
    [(-247, 24), (224, 24), (650, 24)],
    note="Parthian and Sasanian silver drachm (and Sogdian, Chorasmian and Kushan coins of that standard), 6 obols;"
         " copper below. Half a drachm a day is a guess.")
cur("shekel_punic", "Carthaginian shekel", [("shekel", "shekels", 24), ("bronze coin", "bronze coins", 1)],
    [(-410, 4), (-146, 4)], note="Punic silver shekel; 24 bronze pieces to it is a guess, as is the day's pay.")
cur("aksum", "Aksumite coin", [("gold coin", "gold coins", 100), ("bronze coin", "bronze coins", 1)],
    [(270, 5), (700, 5)], note="Aksumite gold, silver and bronze coins (about 270-700). The ratio is a guess.")
cur("mt_thaler", "Maria Theresa thaler", [("thaler", "thalers", 16), ("gersh", "gersh", 1)],
    [(1780, 2), (1900, 3), (1945, 4)],
    note="The Austrian silver thaler (dated 1780) that was the money of Ethiopia, Arabia and the Red Sea into the"
         " 20th century; 16 gersh (piastres) to it as in Ethiopia (it varied). Wages are guesses.")
cur("amole", "salt bars (amole)", [("amole", "amoles", 1)], [(1270, 2), (1779, 2)], mass=True,
    note="Ethiopian bars of rock salt used as money (5 to 8 to the thaler in the 1800s). Two bars a day is a guess.")
cur("pound_eg", "Egyptian pound", [("pound", "pounds", 1000), ("piastre", "piastres", 10), ("millieme", "milliemes", 1)],
    [(1834, 10), (1850, 15), (1880, 25), (1900, 30), (1914, 40), (1920, 100), (1930, 80), (1945, 150), (1960, 200),
     (1970, 300), (1980, 1000), (1990, 5000), (2000, 10000), (2010, 30000), (2020, 100000), (2026, 300000)],
    note="Pound = 100 piastres (1,000 milliemes from 1885; 40 para to the piastre before). Wages are guesses.")
cur("pound_sd_old", "Sudanese pound", [("pound", "pounds", 1000), ("piastre", "piastres", 10), ("millieme", "milliemes", 1)],
    [(1956, 200), (1980, 1500), (1991, 20000)], note="1956-1992. Guesses.")
cur("dinar_sd", "Sudanese dinar", dec("dinar", "dinars", "piastre", "piastres"),
    [(1992, 5000), (2006, 100000)], note="1992-2007 (10 old pounds to the dinar). Guesses.")
cur("pound_sd", "Sudanese pound", dec("pound", "pounds", "piastre", "piastres"),
    [(2007, 1000), (2015, 3000), (2020, 30000), (2026, 300000)], note="From 2007. Guesses.")
cur("pound_ss", "South Sudanese pound", dec("pound", "pounds", "piaster", "piasters"),
    [(2011, 1000), (2020, 100000), (2026, 500000)], note="From 2011. Guesses.")
cur("pound_ly", "Libyan pound", [("pound", "pounds", 1000), ("piastre", "piastres", 10), ("millieme", "milliemes", 1)],
    [(1952, 300), (1970, 1500)], note="1951-1971. Guesses.")
cur("dinar_ly", "Libyan dinar", [("dinar", "dinars", 1000), ("dirham", "dirhams", 1)],
    [(1971, 1500), (1990, 5000), (2010, 15000), (2026, 40000)], note="From 1971. Guesses.")
cur("rial_tn", "Tunisian rial", [("rial", "rials", 16), ("kharub", "kharub", 1)],
    [(1706, 3), (1800, 4), (1890, 8)], note="Rial = 16 kharub (burbe below). Guesses.")
cur("franc_tn", "Tunisian franc", dec("franc", "francs", "centime", "centimes"),
    [(1891, 150), (1914, 200), (1920, 600), (1930, 1000), (1945, 5000), (1950, 15000), (1957, 30000)],
    note="At par with the French franc, 1891-1958. Guesses.")
cur("dinar_tn", "Tunisian dinar", [("dinar", "dinars", 1000), ("millime", "millimes", 1)],
    [(1958, 300), (1980, 2000), (2000, 6000), (2010, 10000), (2026, 25000)], note="From 1958. Guesses.")
cur("budju", "Algerian budju", [("budju", "budju", 24), ("muzuna", "muzunas", 1)],
    [(1706, 4), (1800, 6), (1847, 8)], note="Regency of Algiers: budju = 24 muzunas. Guesses.")
cur("franc_dz", "Algerian franc", dec("franc", "francs", "centime", "centimes"),
    [(1848, 100), (1900, 150), (1914, 200), (1920, 600), (1930, 1000), (1945, 5000), (1950, 15000), (1959, 40000)],
    note="At par with the French franc, 1848-1959. Guesses.")
cur("franc_dz_new", "Algerian new franc", dec("franc", "francs", "centime", "centimes"),
    [(1960, 400), (1964, 500)], note="1960-1964 (100 old). Guesses.")
cur("dinar_dz", "Algerian dinar", dec("dinar", "dinars", "centime", "centimes"),
    [(1964, 800), (1980, 5000), (1990, 15000), (2000, 40000), (2010, 80000), (2026, 200000)], note="From 1964.")
cur("mithqal_ma", "Moroccan mithqal", [("mithqal", "mithqals", 40), ("mūzūna", "mūzūnas", 1)],
    [(1670, 3), (1800, 4), (1881, 6)], note="Mithqal = 10 uqiya = 40 muzunas (it fell over time). Guesses.")
cur("rial_ma", "Moroccan rial", [("rial", "rials", 500), ("dirham", "dirhams", 50), ("mazuna", "mazunas", 1)],
    [(1882, 40), (1920, 60)], note="Hassani rial = 10 dirhams = 500 mazunas, 1882-1920. Guesses.")
cur("franc_ma", "Moroccan franc", dec("franc", "francs", "centime", "centimes"),
    [(1921, 600), (1930, 1000), (1945, 5000), (1950, 15000), (1959, 40000)], note="1921-1959. Guesses.")
cur("dirham_ma", "Moroccan dirham", dec("dirham", "dirhams", "santim", "santimat"),
    [(1960, 400), (1980, 1500), (2000, 5000), (2010, 8000), (2026, 15000)], note="From 1960. Guesses.")
cur("ouguiya_old", "Mauritanian ouguiya", [("ouguiya", "ouguiya", 5), ("khoums", "khoums", 1)],
    [(1973, 500), (2017, 10000)], note="1973-2017. Guesses.")
cur("ouguiya", "Mauritanian ouguiya", [("ouguiya", "ouguiya", 5), ("khoums", "khoums", 1)],
    [(2018, 1000), (2026, 1500)], note="New ouguiya (10 old) from 2018. Guesses.")
cur("pound_sy", "Syrian pound", dec("pound", "pounds", "piastre", "piastres"),
    [(1920, 50), (1950, 400), (1970, 800), (1990, 5000), (2000, 15000), (2010, 40000), (2026, 1200000)],
    note="From 1919 (shared with Lebanon to 1939; the collapse after 2011 roughly). Guesses.")
cur("pound_lb", "Lebanese pound", dec("pound", "pounds", "piastre", "piastres"),
    [(1940, 150), (1970, 800), (1985, 5000), (1990, 100000), (2000, 2000000), (2019, 3000000), (2026, 60000000)],
    note="From 1939 (the 1980s and 2019 collapses roughly). Guesses.")
cur("pound_pa", "Palestine pound", [("pound", "pounds", 1000), ("mil", "mils", 1)],
    [(1927, 150), (1940, 200), (1950, 400)], note="1927-1948 (Transjordan to 1950). Guesses.")
cur("dinar_jo", "Jordanian dinar", [("dinar", "dinars", 1000), ("fils", "fils", 1)],
    [(1950, 300), (1970, 600), (1990, 3000), (2010, 10000), (2026, 15000)], note="From 1950. Guesses.")
cur("pound_il", "Israeli pound", [("pound", "pounds", 1000), ("agora", "agorot", 10, 1960), ("pruta", "prutot", 1, None, 1959)],
    [(1949, 1500), (1960, 6000), (1970, 15000), (1979, 300000)], note="1948-1980 (1,000 prutot; 100 agorot from 1960).")
cur("shekel_old", "Israeli shekel", dec("shekel", "shekels", "agora", "agorot"),
    [(1980, 15000), (1985, 2000000)], note="1980-1985 (10 pounds), through the inflation (rough).")
cur("shekel", "Israeli new shekel", dec("shekel", "shekels", "agora", "agorot"),
    [(1986, 3000), (2000, 15000), (2010, 25000), (2026, 45000)], note="From September 1985. Guesses.")
cur("dinar_iq", "Iraqi dinar", [("dinar", "dinars", 1000), ("fils", "fils", 1)],
    [(1932, 100), (1950, 300), (1970, 600), (1985, 3000), (1995, 300000), (2005, 5000000), (2010, 15000000),
     (2026, 30000000)], note="From 1932 (the sanctions inflation roughly). Guesses.")
cur("riyal_sa_old", "Saudi riyal", [("riyal", "riyals", 22), ("ghirsh", "ghirsh", 1)],
    [(1916, 8), (1930, 11), (1950, 44), (1959, 100)], note="Hejazi and Saudi riyal of 22 ghirsh, to 1959. Guesses.")
cur("riyal_sa", "Saudi riyal", dec("riyal", "riyals", "halala", "halalas"),
    [(1960, 500), (1980, 3000), (2000, 4000), (2026, 6000)], note="Riyal = 100 halalas from 1960. Guesses.")
cur("rial_ye", "Yemeni rial", dec("rial", "rials", "fils", "fils"),
    [(1964, 300), (1990, 6000), (2000, 50000), (2010, 100000), (2026, 300000)], note="From 1964. Guesses.")
cur("dinar_ye", "South Yemeni dinar", [("dinar", "dinars", 1000), ("fils", "fils", 1)],
    [(1965, 500), (1990, 2000)], note="1965-1990. Guesses.")
cur("shilling_ea", "East African shilling", dec("shilling", "shillings", "cent", "cents"),
    [(1921, 50), (1940, 60), (1950, 150), (1969, 400)],
    note="East Africa, Aden, Somaliland, Eritrea and Ethiopia in the war years: shilling = 100 cents. Guesses.")
cur("rupee_gulf", "Gulf rupee", dec("rupee", "rupees", "naya paisa", "naye paise"),
    [(1959, 400), (1966, 500)], note="Indian rupee issued for the Gulf, 1959-1966. Guesses.")
cur("dinar_kw", "Kuwaiti dinar", [("dinar", "dinars", 1000), ("fils", "fils", 1)],
    [(1961, 1000), (1980, 3000), (2000, 4000), (2026, 5000)], note="From 1961. Guesses.")
cur("dinar_bh", "Bahraini dinar", [("dinar", "dinars", 1000), ("fils", "fils", 1)],
    [(1965, 800), (2000, 4000), (2026, 6000)], note="From 1965. Guesses.")
cur("riyal_qd", "Qatar and Dubai riyal", dec("riyal", "riyals", "dirham", "dirhams"),
    [(1966, 800), (1972, 1000)], note="1966-1973. Guesses.")
cur("riyal_qa", "Qatari riyal", dec("riyal", "riyals", "dirham", "dirhams"),
    [(1973, 1500), (2000, 4000), (2026, 6000)], note="From 1973. Guesses.")
cur("dirham_ae", "UAE dirham", dec("dirham", "dirhams", "fils", "fils"),
    [(1973, 1500), (2000, 4000), (2026, 6000)], note="From 1973. Guesses.")
cur("rial_om", "Omani rial", [("rial", "rials", 1000), ("baisa", "baisa", 1)],
    [(1970, 500), (2000, 3000), (2026, 5000)], note="From 1970. Guesses.")
cur("rial_ir", "Iranian rial", [("rial", "rials", 1)],
    [(1932, 5), (1950, 30), (1970, 150), (1979, 500), (1990, 2000), (2000, 20000), (2010, 100000),
     (2020, 1000000), (2026, 3000000)], note="From 1932 (dinars not in use; prices are told in tomans of 10 rials"
                                             " in speech). Guesses.")
cur("lira_tr", "Turkish lira", dec("lira", "lira", "kuruş", "kuruş"),
    [(1924, 100), (1940, 150), (1950, 400), (1960, 1000), (1970, 2500), (1980, 30000), (1990, 1500000),
     (2000, 400000000), (2004, 1500000000)], note="1923-2004 (the inflation roughly). Guesses.")
cur("lira_tr_new", "Turkish lira", dec("lira", "lira", "kuruş", "kuruş"),
    [(2005, 1500), (2010, 3000), (2015, 5000), (2020, 10000), (2024, 60000), (2026, 120000)],
    note="New lira (1,000,000 old) from 2005. Guesses.")
cur("afghan_rupee", "Afghan rupee", [("rupee", "rupees", 60), ("paisa", "paisa", 1)],
    [(1748, 6), (1891, 10), (1925, 20)], note="Kabul rupee = 60 paisa, to 1925. Guesses.")
cur("afghani_old", "Afghan afghani", dec("afghani", "afghanis", "pul", "puls"),
    [(1925, 50), (1950, 1000), (1970, 5000), (1990, 50000), (2002, 5000000)], note="1925-2002. Guesses.")
cur("afghani", "Afghan afghani", dec("afghani", "afghanis", "pul", "puls"),
    [(2003, 10000), (2010, 20000), (2026, 40000)], note="New afghani (1,000 old) from 2002. Guesses.")

row("achaemenid", "siglos", -550, -331, [ru("Achaemenid Empire", "Median Kingdom"), bx(IRAN)], 29)
row("persian_drachm", "drachm_persian", -247, 650, ru("Parthian Empire", "Indo-Parthians", "Sasanian Empire",
                                                      "Indo-Sasanian Empire", "Kingdom of Armenia", "Lakhmid Kingdom",
                                                      "Kingdom of Osroene"), 31)
row("persian_drachm_box", "drachm_persian", -247, 650, bx(IRAN), 29)
row("central_asia_drachm", "drachm_persian", -330, 649, bx(CENTRAL_ASIA), 19)
row("hellenistic_more", "drachma", -332, -31, ru("Greco-Bactrian Kingdom", "Indo-Greeks", "Kingdom of Pontus",
                                                 "Kingdom of Pergamon", "Kingdom of Cappadocia", "Kingdom of Lysimachus",
                                                 "Cyrenaica", "Nabataeans", "Kingdom of Osroene"), 36)
row("south_arabia_drachma", "drachma", -400, 600, ru("Sabaeans", "Minaeans", "Himyarite Kingdom", "Nabataeans"), 36)
row("carthage", "shekel_punic", -410, -146, ru("Carthage", "Kingdom of Numidia", "Mauretania"), 33)
row("aksum", "aksum", 270, 700, ru("Kingdom of Axum"), 33)
row("arabia_barter", "barter", -100000, 649, bx(ARABIA), 9)
row("sahara_barter", "barter", -100000, 649, bx(SAHARA_SAHEL), 9)
row("arabia_akce", "akce", 1501, 1779, bx(ARABIA), 9, note="Ottoman, Persian and Indian coins in the Arabian trade.")
row("arabia_thaler", "mt_thaler", 1780, 1959, bx(ARABIA), 9)
row("arabia_emirates_thaler", "mt_thaler", 1780, 1925, ru("Emirate of Diriyah", "Emirate of Nejd", "Emirate of Jabal Shammar",
                                                         "Asir", "Imamate of Yemen", "Qasimids", "Kingdom of Hejaz",
                                                         "Imamate of Oman"), 41)
row("mesopotamia_persian", "silver_weighed", -538, -331, bx(MESOPOTAMIA), 30,
    note="Babylonia under the Persians kept weighing silver.")
row("eg_akce", "akce", 1805, 1833, ru("Muhammad Ali dynasty"), 45)
row("eg_pound_rulers", "pound_eg", 1834, 2100, ru("Muhammad Ali dynasty", "Khedivate of Egypt", "Kingdom of Egypt",
                                                  "Republic of Egypt", "Arab Republic of Egypt"), 45)
row("eg_pound_uar", "pound_eg", 1958, 1972, rb("United Arab Republic", EGYPT), 46)
row("eg_pound_box", "pound_eg", 1834, 2100, bx(EGYPT), 32)
row("sd_ottoman", "akce", 1821, 1833, bx(SUDAN), 31)
row("sd_egypt", "pound_eg", 1834, 1955, bx(SUDAN), 31)
row("sd_pound_old", "pound_sd_old", 1956, 1991, [ru("Republic of Sudan"), bx(SUDAN)], 45)
row("sd_dinar", "dinar_sd", 1992, 2006, [ru("Republic of Sudan"), bx(SUDAN)], 45)
row("sd_pound", "pound_sd", 2007, 2100, [ru("Republic of Sudan"), bx(SUDAN)], 45)
row("ss_pound", "pound_ss", 2011, 2100, [ru("South Sudan"), bx(SOUTH_SUDAN)], 46)
row("sudan_sultanates_barter", "barter", 1500, 1820, ru("Funj Sultanate", "Sultanate of Darfur", "Wadai Empire",
                                                       "Makuria Kingdom"), 41,
    note="Cloth, salt and gold dust were swapped; no coins of their own.")
row("ly_italian", "lira_it", 1912, 1942, rb("Italian Africa", LIBYA), 45, pay=[(1890, 50), (1913, 80), (1920, 300), (1940, 500)])
row("ly_egypt", "pound_eg", 1943, 1950, bx(LIBYA), 34)
row("ly_pound", "pound_ly", 1951, 1970, [ru("Kingdom of Libya", "Libyan Arab Republic"), bx(LIBYA)], 44)
row("ly_dinar", "dinar_ly", 1971, 2100, [ru("Libyan Arab Republic", "State of Libya"), bx(LIBYA)], 44)
row("tn_rial", "rial_tn", 1706, 1890, [ru("Beylik of Tunis"), bx(TUNISIA)], 43)
row("tn_franc", "franc_tn", 1891, 1957, [rb("French Africa", TUNISIA), ru("Republic of Tunisia"), bx(TUNISIA)], 44)
row("tn_dinar", "dinar_tn", 1958, 2100, [ru("Republic of Tunisia"), bx(TUNISIA)], 45)
row("dz_budju", "budju", 1706, 1847, [ru("Regency of Algiers"), bx([32, -2.2, 37.1, 8.7])], 41)
row("dz_franc", "franc_dz", 1848, 1959, [ru("French Algeria"), rb("French Africa", ALGERIA),
                                         rb("French Fifth Republic", ALGERIA), bx([32, -2.2, 37.1, 8.7])], 42)
row("dz_new_franc", "franc_dz_new", 1960, 1963, [rb("French Fifth Republic", ALGERIA),
                                                 ru("People's Democratic Republic of Algeria"), bx(ALGERIA)], 42)
row("dz_dinar", "dinar_dz", 1964, 2100, [ru("People's Democratic Republic of Algeria"), bx(ALGERIA)], 45)
row("ma_mithqal", "mithqal_ma", 1670, 1881, [ru("Morocco", "Saadi Sultanate"), bx(MOROCCO)], 44)
row("ma_rial", "rial_ma", 1882, 1920, [ru("Morocco"), bx(MOROCCO)], 44)
row("ma_franc", "franc_ma", 1921, 1959, [ru("Morocco", "Tangier International Zone", "Republic of the Rif"),
                                         rb("French Africa", MOROCCO), bx(MOROCCO)], 44)
row("ma_dirham", "dirham_ma", 1960, 2100, [ru("Morocco"), bx(MOROCCO), bx(WESTERN_SAHARA)], 44)
row("eh_peseta", "peseta", 1884, 1975, bx(WESTERN_SAHARA), 34, pay=[(1869, 50), (1950, 1000), (1975, 5000)])
row("mr_ouguiya_old", "ouguiya_old", 1973, 2017, [ru("Mauritania"), bx(MAURITANIA)], 45)
row("mr_ouguiya", "ouguiya", 2018, 2100, [ru("Mauritania"), bx(MAURITANIA)], 45)
row("sy_pound", "pound_sy", 1919, 2100, [ru("French Mandate for Syria and Lebanon", "Second Syrian Republic",
                                            "Republic of Syria", "Ba'athist Syria", "Arab Socialist Ba'ath Party",
                                            "Syria"), rb("United Arab Republic", SYRIA), bx(SYRIA)], 44)
row("lb_pound", "pound_lb", 1939, 2100, [ru("Lebanon"), bx(LEBANON)], 47)
row("pa_egypt", "pound_eg", 1917, 1926, [bx(PALESTINE), bx(JORDAN)], 34)
row("pa_pound", "pound_pa", 1927, 1949, [ru("Palestinians"), bx(PALESTINE), bx(JORDAN)], 34)
row("jo_dinar", "dinar_jo", 1950, 2100, [ru("Kingdom of Jordan"), bx(JORDAN)], 44)
row("jo_pound", "pound_pa", 1947, 1949, ru("Kingdom of Jordan"), 44)
row("il_pound", "pound_il", 1948, 1979, ru("State of Israel"), 46)
row("il_shekel_old", "shekel_old", 1980, 1985, ru("State of Israel"), 46)
row("il_shekel", "shekel", 1986, 2100, ru("State of Israel", "Gaza/Hamas"), 46)
row("iq_rupee", "indian_rupee_anna", 1918, 1931, bx(IRAQ), 33)
row("iq_dinar", "dinar_iq", 1932, 2100, [ru("Kingdom of Iraq", "Iraqi Republic", "Republic of Iraq"),
                                         rb("Arab Federation", IRAQ), bx(IRAQ)], 44)
row("sa_riyal_old", "riyal_sa_old", 1916, 1959, ru("Kingdom of Hejaz", "Kingdom of Hejaz and Nejd",
                                                   "Kingdom of Saudi Arabia"), 45)
row("sa_riyal", "riyal_sa", 1960, 2100, ru("Kingdom of Saudi Arabia"), 45)
row("ye_thaler", "mt_thaler", 1919, 1963, ru("North Yemen"), 45)
row("ye_rial_n", "rial_ye", 1964, 2100, [ru("North Yemen", "Republic of Yemen"), bx(YEMEN_N)], 44)
row("ye_aden_rupee", "indian_rupee_anna", 1839, 1950, bx(ADEN), 46)
row("ye_aden_shilling", "shilling_ea", 1951, 1964, bx(ADEN), 46)
row("ye_dinar_s", "dinar_ye", 1965, 1990, ru("People's Democratic Republic of Yemen"), 45)
row("gulf_rupee_1", "indian_rupee_anna", 1800, 1956, [ru("Kuwait", "Bahrain", "Qatar Dynasty", "Qatar", "Trucial States",
                                                        "Qatar Protectorate", "Sultanate of Muscat and Oman"),
                                                     bx(KUWAIT), bx(BAHRAIN), bx(QATAR), bx(UAE)], 41)
row("gulf_rupee_2", "indian_rupee_np", 1957, 1958, [ru("Kuwait", "Qatar Protectorate", "Sultanate of Oman"),
                                                   bx(KUWAIT), bx(BAHRAIN), bx(QATAR), bx(UAE)], 41)
row("gulf_rupee_3", "rupee_gulf", 1959, 1966, [ru("Kuwait", "Qatar Protectorate"), bx(BAHRAIN), bx(QATAR), bx(UAE)], 41)
row("kw_dinar", "dinar_kw", 1961, 2100, [ru("Kuwait", "State of Kuwait"), bx(KUWAIT)], 45)
row("bh_dinar", "dinar_bh", 1965, 2100, [ru("Kingdom of Bahrain"), bx(BAHRAIN)], 45)
row("qd_riyal", "riyal_qd", 1967, 1972, [bx(QATAR), bx(UAE)], 42)
row("qa_riyal", "riyal_qa", 1973, 2100, [ru("State of Qatar"), bx(QATAR)], 45)
row("ae_dirham", "dirham_ae", 1973, 2100, [ru("United Arab Emirates"), bx(UAE)], 45)
row("om_thaler", "mt_thaler", 1780, 1969, [ru("Sultanate of Oman", "Sultanate of Muscat and Oman", "Imamate of Oman"),
                                           bx(OMAN)], 40)
row("om_rial", "rial_om", 1970, 2100, [ru("Sultanate of Oman"), bx(OMAN)], 45)
row("ir_toman_rulers", "toman", 1501, 1931, ru("Safavid Dynasty", "Afsharid Iran", "Zand Dynasty", "Qajar Dynasty"), 40)
row("ir_rial", "rial_ir", 1932, 2100, [ru("Pahlavi Dynasty", "Islamic Republic of Iran"), bx(IRAN)], 40)
row("tr_lira", "lira_tr", 1924, 2004, [ru("Republic of Turkey", "Turkish Republic of Northern Cyprus"), bx(TURKEY)], 44)
row("tr_lira_new", "lira_tr_new", 2005, 2100, [ru("Republic of Turkey", "Turkish Republic of Northern Cyprus"),
                                               bx(TURKEY)], 44)
row("tr_ottoman_1923", "kurus", 1923, 1923, bx(TURKEY), 31)
row("af_rupee", "afghan_rupee", 1748, 1924, ru("Durrani Empire", "Durrani Dynasty", "Emirate of Afghanistan"), 45)
row("af_afghani_old", "afghani_old", 1925, 2002, ru("Emirate of Afghanistan", "Kingdom of Afghanistan",
                                                    "Republic of Afghanistan", "Afghanistan", "Taliban", "Mujahideen"), 45)
row("af_afghani", "afghani", 2003, 2100, ru("Afghanistan", "Taliban", "Mujahideen"), 45)

rate("lira_tr", 100000000, "lira_tr_new", 100, 2005, 2100, "1,000,000 old lira = 1 new.")
rate("afghani_old", 100000, "afghani", 100, 2003, 2100, "1,000 old afghanis = 1 new.")
rate("pound_eg", 1000, "pound_sd_old", 1000, 1956, 1957, "The Sudanese pound replaced the Egyptian pound at par.")
rate("pound_pa", 1000, "pound_il", 1000, 1948, 1952, "The Israeli pound replaced the Palestine pound at par.")
rate("pound_pa", 1000, "dinar_jo", 1000, 1950, 1951, "The Jordanian dinar replaced the Palestine pound at par.")
rate("shekel_old", 100000, "shekel", 100, 1986, 2100, "1,000 old shekels = 1 new.")
rate("dinar_sd", 10000, "pound_sd", 100, 2007, 2100, "100 dinars = 1 new pound (2007).")


# ==============================================================================================================
# AFRICA SOUTH OF THE SAHARA
# ==============================================================================================================
SUB_SAHARA = [-35, -18, 12, 52]
WEST_AFRICA_BIG = [3, -18, 20, 16]
WEST_CENTRAL_AF = [-5.5, -17.6, 24, 24.5]
CENTRAL_AF = [-13.5, 8.5, 12, 31.5]
EAST_AFRICA = [-12, 29, 5.5, 42]
HORN = [-2, 33, 18.1, 52]
ETHIOPIA = [3.4, 33, 15, 48]
ERITREA = [12.3, 36.4, 18.1, 43.2]
SOMALIA = [-1.7, 40.9, 12, 51.5]
SOMALILAND_BR = [8, 42.6, 11.5, 49]
DJIBOUTI = [10.9, 41.7, 12.8, 43.5]
NIGERIA = [4.2, 2.7, 13.9, 14.7]
GHANA = [4.7, -3.3, 11.2, 1.2]
SIERRA_LEONE = [6.9, -13.3, 10.0, -10.2]
GAMBIA = [13.0, -16.9, 13.85, -13.8]
LIBERIA = [4.3, -11.5, 8.6, -7.4]
GUINEA = [7.2, -15.1, 12.7, -7.6]
GUINEA_BISSAU = [10.9, -16.8, 12.7, -13.6]
MALI = [10.1, -12.3, 25, 4.3]
CAPE_VERDE = [14.8, -25.4, 17.2, -22.6]
SAO_TOME = [-0.1, 6.4, 1.8, 7.5]
EQ_GUINEA = [0.9, 8.4, 3.8, 11.4]
CONGO_BELGE = [-13.5, 12.2, 5.4, 31.3]
RWANDA = [-2.85, 28.85, -1.05, 30.9]
BURUNDI = [-4.5, 29.0, -2.3, 30.85]
KENYA = [-4.7, 33.9, 5.0, 41.9]
UGANDA = [-1.5, 29.5, 4.25, 35.0]
TANZANIA = [-11.75, 29.3, -0.99, 40.5]
ZANZIBAR = [-6.5, 39.1, -4.8, 39.9]
SWAHILI_COAST = [-12, 38, 0, 42]
MOZAMBIQUE = [-26.9, 30.2, -10.4, 41]
ANGOLA = [-18.1, 11.6, -4.3, 24.1]
SOUTH_AFRICA = [-35, 16.4, -22, 33]
SWA = [-29, 11.7, -17, 25.3]
RHODESIAS = [-22.5, 22, -8.2, 36]
ZAMBIA = [-18.1, 21.9, -8.2, 33.7]
MALAWI = [-17.2, 32.6, -9.3, 36]
ZIMBABWE = [-22.5, 25.2, -15.6, 33.1]
MADAGASCAR = [-25.7, 43.1, -11.9, 50.6]
MAURITIUS = [-20.6, 57.2, -19.9, 57.9]
SEYCHELLES = [-9.8, 46, -3.7, 56.3]
COMOROS = [-12.5, 43.2, -11.3, 44.6]
REUNION = [-21.5, 55, -20.8, 56]
BIAFRA_BIGHT = [4, 5, 7.5, 10]
KONGO = [-9, 12, -4.6, 16.5]

cur("manilla", "manillas", [("manilla", "manillas", 1)], [(1500, 2), (1948, 3)], mass=True,
    note="Brass and copper bracelets used as money in the Niger Delta and the Bight of Biafra until 1949. Guesses.")
cur("nzimbu", "nzimbu shells", [("lufuku", "lufuku", 10000), ("nzimbu shell", "nzimbu shells", 1)],
    [(1400, 200), (1800, 400)], mass=True,
    note="Olivancillaria shells from Luanda island, the money of the Kongo kingdom (counted in thousands); the"
         " lufuku of 10,000 and a day's pay are guesses.")
cur("cut_silver_mg", "cut silver (ariary)", [("ariary", "ariary", 24), ("voamena", "voamena", 1)],
    [(1792, 2), (1897, 3)], kind="weighed", metal="silver", mass=True,
    note="Merina Madagascar: silver dollars (ariary) cut into pieces and weighed; a voamena = 1/24 ariary (the"
         " pieces went down to 1/720). Guesses.")
cur("rixdollar_cape", "Cape rixdollar", [("rixdollar", "rixdollars", 48), ("schelling", "schellingen", 6),
                                         ("stuiver", "stuivers", 1)],
    [(1652, 6), (1700, 8), (1800, 16), (1825, 24)], note="Rixdollar = 8 schellingen = 48 stuivers. Guesses.")
cur("franc_fwa", "French colonial franc", dec("franc", "francs", "centime", "centimes"),
    [(1850, 50), (1914, 100), (1930, 300), (1944, 1000)],
    note="The French franc in the African colonies before the CFA franc (local coins and notes at par). Guesses.")
cur("franc_cfa", "CFA franc", [("franc", "francs", 1)],
    [(1945, 30), (1960, 150), (1980, 500), (1994, 700), (2000, 1000), (2010, 1500), (2026, 2500)],
    note="West and Central African CFA francs (at par with each other), from December 1945. Guesses.")
cur("franc_ml", "Malian franc", [("franc", "francs", 1)], [(1962, 150), (1984, 600)], note="1962-1984.")
cur("franc_gn_old", "Guinean franc", [("franc", "francs", 1)], [(1959, 150), (1971, 300)], note="1959-1971.")
cur("syli", "Guinean syli", dec("syli", "sylis", "cauri", "cauris"), [(1972, 3000), (1985, 10000)], note="1972-1985.")
cur("franc_gn", "Guinean franc", [("franc", "francs", 1)], [(1986, 600), (2000, 3000), (2010, 15000), (2026, 40000)],
    note="From 1986. Guesses.")
cur("ekwele", "Equatorial Guinean ekwele", [("ekwele", "bipkwele", 1)], [(1975, 100), (1985, 600)],
    note="1975-1985. Guesses.")
cur("peso_gw", "Guinea-Bissau peso", [("peso", "pesos", 1)], [(1975, 50), (1997, 3000)], note="1975-1997.")
cur("escudo_cv", "Cape Verdean escudo", [("escudo", "escudos", 1)], [(1914, 1), (1975, 30), (2000, 400), (2026, 1000)],
    note="From 1914 (centavos not counted). Guesses.")
cur("dobra_old", "São Tomé dobra", [("dobra", "dobras", 1)], [(1977, 50), (2017, 50000)], note="1977-2017.")
cur("dobra", "São Tomé dobra", dec("dobra", "dobras", "cêntimo", "cêntimos"), [(2018, 6000), (2026, 10000)],
    note="New dobra (1,000 old) from 2018. Guesses.")
cur("madagascar_franc", "Malagasy franc", [("franc", "francs", 1)], [(1925, 3), (1960, 150), (1980, 500), (2004, 5000)],
    note="1925-2004. Guesses.")
cur("ariary", "Malagasy ariary", [("ariary", "ariary", 5), ("iraimbilanja", "iraimbilanja", 1)],
    [(2005, 5000), (2026, 25000)], note="Ariary = 5 iraimbilanja (= 5 old francs), sole money from 2005.")
cur("pound_wa", "West African pound", [("pound", "pounds", 240), ("shilling", "shillings", 12), ("penny", "pence", 1)],
    [(1880, 10), (1913, 12), (1930, 12), (1945, 18), (1968, 48)],
    note="Sterling coins, then the West African Currency Board's pound (1913-1968). Guesses.")
cur("pound_gh", "Ghanaian pound", [("pound", "pounds", 240), ("shilling", "shillings", 12), ("penny", "pence", 1)],
    [(1958, 48), (1965, 60)], note="1958-1965. Guesses.")
cur("cedi_old", "Ghanaian cedi", dec("cedi", "cedis", "pesewa", "pesewas"),
    [(1965, 100), (1980, 1500), (1990, 25000), (2000, 500000), (2007, 1500000)], note="1965-2007. Guesses.")
cur("cedi", "Ghanaian cedi", dec("cedi", "cedis", "pesewa", "pesewas"), [(2007, 200), (2015, 1000), (2026, 3000)],
    note="New cedi (10,000 old) from 2007. Guesses.")
cur("pound_ng", "Nigerian pound", [("pound", "pounds", 240), ("shilling", "shillings", 12), ("penny", "pence", 1)],
    [(1959, 60), (1972, 96)], note="1959-1972. Guesses.")
cur("naira", "Nigerian naira", dec("naira", "naira", "kobo", "kobo"),
    [(1973, 150), (1980, 500), (1990, 1500), (2000, 30000), (2010, 100000), (2020, 200000), (2026, 600000)],
    note="Naira = 100 kobo, from 1973. Guesses.")
cur("leone_old", "Sierra Leonean leone", dec("leone", "leones", "cent", "cents"),
    [(1964, 30), (1980, 150), (2000, 300000), (2021, 3000000)], note="1964-2021. Guesses.")
cur("leone", "Sierra Leonean leone", dec("leone", "leones", "cent", "cents"), [(2022, 4000), (2026, 6000)],
    note="New leone (1,000 old) from 2022. Guesses.")
cur("dalasi", "Gambian dalasi", dec("dalasi", "dalasis", "butut", "bututs"), [(1971, 100), (2000, 2000), (2026, 15000)],
    note="From 1971 (the Gambian pound 1964-1971 is not told apart). Guesses.")
cur("dollar_lr", "Liberian dollar", dec("dollar", "dollars", "cent", "cents"),
    [(1847, 25), (1900, 30), (1982, 300), (2000, 10000), (2026, 80000)],
    note="1847-1907 and from 1982 (the US dollar in between). Guesses.")
cur("rupee_ea", "East African rupee", dec("rupee", "rupees", "cent", "cents"), [(1906, 25), (1920, 40)],
    note="1906-1920. Guesses.")
cur("rupie_de", "German East African rupie", dec("rupie", "rupien", "heller", "heller"), [(1890, 25), (1916, 40)],
    note="1890-1916. Guesses.")
cur("shilling_ke", "Kenyan shilling", dec("shilling", "shillings", "cent", "cents"),
    [(1966, 400), (1980, 1500), (1990, 4000), (2000, 15000), (2010, 30000), (2026, 80000)], note="From 1966.")
cur("shilling_ug_old", "Ugandan shilling", dec("shilling", "shillings", "cent", "cents"),
    [(1966, 400), (1987, 50000)], note="1966-1987. Guesses.")
cur("shilling_ug", "Ugandan shilling", [("shilling", "shillings", 1)], [(1987, 10), (2000, 2000), (2026, 10000)],
    note="New shilling (100 old) from 1987. Guesses.")
cur("shilling_tz", "Tanzanian shilling", [("shilling", "shillings", 1)],
    [(1966, 4), (1990, 200), (2000, 1000), (2010, 2500), (2026, 7000)], note="From 1966. Guesses.")
cur("franc_congo", "Congo franc", dec("franc", "francs", "centime", "centimes"),
    [(1887, 50), (1920, 200), (1950, 2000), (1960, 4000), (1966, 15000)], note="1887-1967. Guesses.")
cur("zaire", "Zaire", dec("zaire", "zaires", "likuta", "makuta"), [(1967, 50), (1980, 1000), (1990, 1000000)],
    note="1967-1997 (the 1990s hyperinflation and the 1993 new zaire are not followed).")
cur("franc_cd", "Congolese franc", dec("franc", "francs", "centime", "centimes"),
    [(1998, 2000), (2010, 150000), (2026, 1000000)], note="From 1998. Guesses.")
cur("franc_rw", "Rwandan franc", [("franc", "francs", 1)], [(1960, 50), (2000, 500), (2026, 2000)],
    note="Rwanda-Burundi franc 1960-1964, then the Rwandan franc. Guesses.")
cur("franc_bi", "Burundian franc", [("franc", "francs", 1)], [(1964, 50), (2000, 400), (2026, 4000)],
    note="From 1964. Guesses.")
cur("birr", "Ethiopian birr", dec("birr", "birr", "santim", "santim"),
    [(1945, 50), (1970, 150), (1990, 300), (2000, 600), (2010, 2000), (2026, 30000)],
    note="Ethiopian dollar (birr in Amharic) from 1945. Guesses.")
cur("nakfa", "Eritrean nakfa", dec("nakfa", "nakfa", "cent", "cents"), [(1997, 1500), (2026, 15000)], note="From 1997.")
cur("somalo", "Somali somalo", dec("somalo", "somali", "centesimo", "centesimi"), [(1950, 150), (1961, 300)],
    note="1950-1962. Guesses.")
cur("shilling_so", "Somali shilling", [("shilling", "shillings", 1)], [(1962, 4), (1990, 500), (2000, 15000), (2026, 30000)],
    note="From 1962 (the shilling fell far; dollars took over). Guesses.")
cur("franc_dj", "Djiboutian franc", [("franc", "francs", 1)], [(1949, 100), (2000, 1000), (2026, 2000)],
    note="From 1949. Guesses.")
cur("pound_za", "South African pound", [("pound", "pounds", 960), ("shilling", "shillings", 48), ("penny", "pence", 4),
                                        ("farthing", "farthings", 1)],
    [(1923, 192), (1940, 240), (1960, 480)], note="1923-1960 (at par with sterling until 1931). Guesses.")
cur("rand", "South African rand", dec("rand", "rand", "cent", "cents"),
    [(1961, 100), (1970, 200), (1980, 500), (1990, 1500), (2000, 4000), (2010, 10000), (2026, 25000)], note="From 1961.")
cur("lilangeni", "Swazi lilangeni", dec("lilangeni", "emalangeni", "cent", "cents"), [(1974, 150), (2026, 20000)],
    note="From 1974 (at par with the rand).")
cur("loti", "Lesotho loti", dec("loti", "maloti", "sente", "lisente"), [(1980, 300), (2026, 15000)],
    note="From 1980 (at par with the rand).")
cur("pula", "Botswana pula", dec("pula", "pula", "thebe", "thebe"), [(1976, 150), (2026, 12000)], note="From 1976.")
cur("dollar_na", "Namibian dollar", dec("dollar", "dollars", "cent", "cents"), [(1993, 1500), (2026, 15000)],
    note="From 1993 (at par with the rand).")
cur("pound_rh", "Rhodesian pound", [("pound", "pounds", 240), ("shilling", "shillings", 12), ("penny", "pence", 1)],
    [(1939, 30), (1969, 120)], note="Southern Rhodesian, Federation and Rhodesian pounds, 1939-1970. Guesses.")
cur("dollar_rh", "Rhodesian dollar", dec("dollar", "dollars", "cent", "cents"), [(1970, 100), (1980, 150)],
    note="1970-1980. Guesses.")
cur("dollar_zw", "Zimbabwean dollar", dec("dollar", "dollars", "cent", "cents"),
    [(1980, 150), (1990, 500), (2000, 30000), (2005, 2000000)],
    note="1980-2008 (the 2006-2008 hyperinflation and its new dollars are not followed).")
cur("rtgs_zw", "Zimbabwean dollar (RTGS)", dec("dollar", "dollars", "cent", "cents"), [(2019, 1000), (2023, 1000000)],
    note="2019-2024 (rough).")
cur("zig", "Zimbabwe Gold (ZiG)", dec("ZiG", "ZiG", "cent", "cents"), [(2024, 10000), (2026, 15000)],
    note="From April 2024. Guesses.")
cur("kwacha_zm_old", "Zambian kwacha", dec("kwacha", "kwacha", "ngwee", "ngwee"),
    [(1968, 100), (1990, 5000), (2000, 300000), (2012, 2000000)], note="1968-2012. Guesses.")
cur("kwacha_zm", "Zambian kwacha", dec("kwacha", "kwacha", "ngwee", "ngwee"), [(2013, 2500), (2026, 8000)],
    note="New kwacha (1,000 old) from 2013. Guesses.")
cur("kwacha_mw", "Malawian kwacha", dec("kwacha", "kwacha", "tambala", "tambala"), [(1971, 50), (2000, 5000), (2026, 300000)],
    note="From 1971. Guesses.")
cur("escudo_mz", "Mozambican escudo", dec("escudo", "escudos", "centavo", "centavos"), [(1914, 30), (1950, 800), (1979, 3000)],
    note="1914-1980. Guesses.")
cur("metical_old", "Mozambican metical", dec("metical", "meticais", "centavo", "centavos"),
    [(1980, 5000), (2000, 1500000), (2005, 3000000)], note="1980-2006. Guesses.")
cur("metical", "Mozambican metical", dec("metical", "meticais", "centavo", "centavos"), [(2006, 4000), (2026, 30000)],
    note="New metical (1,000 old) from 2006. Guesses.")
cur("escudo_ao", "Angolan escudo", dec("escudo", "escudos", "centavo", "centavos"), [(1914, 30), (1950, 800), (1976, 3000)],
    note="Angolan escudo and angolar, 1914-1977. Guesses.")
cur("kwanza_old", "Angolan kwanza", dec("kwanza", "kwanzas", "lwei", "lwei"), [(1977, 5000), (1990, 10000)],
    note="1977-1998 (the 1990s readjustments are not followed).")
cur("kwanza", "Angolan kwanza", dec("kwanza", "kwanzas", "cêntimo", "cêntimos"), [(1999, 1000), (2010, 50000), (2026, 300000)],
    note="From 1999. Guesses.")
cur("rupee_mu", "Mauritian rupee", dec("rupee", "rupees", "cent", "cents"), [(1877, 25), (1950, 150), (2000, 15000), (2026, 60000)],
    note="From 1877. Guesses.")
cur("rupee_sc", "Seychellois rupee", dec("rupee", "rupees", "cent", "cents"), [(1914, 30), (2000, 8000), (2026, 30000)],
    note="From 1914. Guesses.")
cur("franc_km", "Comorian franc", [("franc", "francs", 1)], [(1950, 100), (2000, 1000), (2026, 2000)],
    note="Madagascar-Comoros franc, then the Comorian franc (1981). Guesses.")

row("africa_barter_late", "barter", 1800, 2100, bx(SUB_SAHARA), 5,
    note="Where no ruler of the register is known after 1800, people swapped goods (cattle, cloth, salt).")
row("sahel_barter_late", "barter", 1501, 2100, bx(SAHARA_SAHEL), 4)
row("biafra_manilla", "manilla", 1500, 1948, bx(BIAFRA_BIGHT), 32, accepts=["cowrie"],
    note="Cowries were the small change beside the manillas.")
row("kongo_nzimbu", "nzimbu", 1400, 1800, [bx(KONGO), ru("Kingdom of Kongo")], 32)
row("ethiopia_amole", "amole", 1270, 1779, ru("Ethiopian Empire", "Adal Sultanate"), 41)
row("ethiopia_thaler", "mt_thaler", 1780, 1935, [ru("Ethiopian Empire"), bx(ETHIOPIA)], 41)
row("swahili_coins", "dirham", 1000, 1499, bx(SWAHILI_COAST), 31, note="Kilwa's copper and silver coins.")
row("swahili_rupee", "indian_rupee_anna", 1800, 1905, [bx(SWAHILI_COAST), ru("Omani Slave Coast", "People's Republic of Zanzibar")], 31)
row("mg_cut_silver", "cut_silver_mg", 1792, 1897, [ru("Merina Kingdom"), bx(MADAGASCAR)], 33)
row("cape_rixdollar", "rixdollar_cape", 1652, 1825, ru("Dutch Cape Colony", "British Cape Colony"), 43)
row("southern_africa_sterling", "pound_lsd", 1826, 1922, [ru("British Cape Colony", "Natalia Republic", "Free Orange State",
                                                            "Swaziland"), rb("British Africa", SOUTH_AFRICA)], 43,
    pay=[(1826, 48), (1900, 96), (1922, 160)])
row("za_pound_br", "pound_za", 1923, 1931, rb("British Africa", SOUTH_AFRICA), 43)
row("za_pound", "pound_za", 1932, 1960, [ru("South Africa"), bx(SOUTH_AFRICA)], 41)
row("za_rand", "rand", 1961, 2100, [ru("South Africa"), bx(SOUTH_AFRICA)], 41)
row("swa_mark", "mark", 1884, 1914, rb("German Africa", SWA), 44, pay=[(1884, 30), (1914, 60)])
row("swa_sterling", "pound_lsd", 1915, 1922, bx(SWA), 33, pay=[(1915, 120), (1922, 160)])
row("swa_pound", "pound_za", 1923, 1960, bx(SWA), 33)
row("swa_rand", "rand", 1961, 1992, bx(SWA), 33)
row("na_dollar", "dollar_na", 1993, 2100, [ru("Namibia"), bx(SWA)], 45)
row("bw_rand", "rand", 1961, 1975, ru("Republic of Botswana"), 45)
row("bw_pula", "pula", 1976, 2100, ru("Republic of Botswana"), 45)
row("ls_rand", "rand", 1961, 1979, ru("Lesotho"), 45)
row("ls_loti", "loti", 1980, 2100, ru("Lesotho"), 45)
row("sz_rand", "rand", 1961, 1973, ru("Eswatini"), 45)
row("sz_lilangeni", "lilangeni", 1974, 2100, ru("Eswatini"), 45)
row("rh_sterling", "pound_lsd", 1890, 1938, rb("British Africa", RHODESIAS), 43, pay=[(1890, 24), (1938, 48)])
row("rh_pound", "pound_rh", 1939, 1969, [rb("British Africa", RHODESIAS), ru("Rhodesia"), rb("Malawi", MALAWI),
                                         rb("Zambia", ZAMBIA)], 43)
row("rh_dollar", "dollar_rh", 1970, 1980, [ru("Rhodesia", "Zimbabwe Rhodesia"), bx(ZIMBABWE)], 44)
row("zw_dollar", "dollar_zw", 1981, 2008, [ru("Zimbabwe Rhodesia", "Republic of Zimbabwe"), bx(ZIMBABWE)], 44)
row("zw_usd", "dollar", 2009, 2018, [ru("Republic of Zimbabwe"), bx(ZIMBABWE)], 44, pay=[(2009, 300), (2018, 500)])
row("zw_rtgs", "rtgs_zw", 2019, 2023, [ru("Republic of Zimbabwe"), bx(ZIMBABWE)], 44)
row("zw_zig", "zig", 2024, 2100, [ru("Republic of Zimbabwe"), bx(ZIMBABWE)], 44)
row("zm_kwacha_old", "kwacha_zm_old", 1968, 2012, ru("Zambia"), 45)
row("zm_kwacha", "kwacha_zm", 2013, 2100, ru("Zambia"), 45)
row("mw_kwacha", "kwacha_mw", 1971, 2100, ru("Malawi"), 45)
row("pt_africa_real", "real_pt", 1500, 1913, [rb(["Portuguese Empire", "Portuguese Colonies", "Kingdom of Portugal",
                                                  "Portuguese Africa"], MOZAMBIQUE),
                                              rb(["Portuguese Empire", "Portuguese Colonies", "Kingdom of Portugal",
                                                  "Portuguese Africa"], ANGOLA)], 43)
row("mz_escudo", "escudo_mz", 1914, 1979, [rb(["Portuguese Colonies", "Portuguese Republic", "Estado Novo",
                                               "Kingdom of Portugal"], MOZAMBIQUE), ru("Mozambique")], 45)
row("mz_metical_old", "metical_old", 1980, 2005, ru("Mozambique"), 45)
row("mz_metical", "metical", 2006, 2100, ru("Mozambique"), 45)
row("ao_escudo", "escudo_ao", 1914, 1976, [rb(["Portuguese Colonies", "Portuguese Republic", "Estado Novo",
                                               "Kingdom of Portugal"], ANGOLA), ru("People's Republic of Angola")], 45)
row("ao_kwanza_old", "kwanza_old", 1977, 1998, ru("People's Republic of Angola"), 45)
row("ao_kwanza", "kwanza", 1999, 2100, ru("People's Republic of Angola"), 45)
row("mz_box_late", "metical", 2006, 2100, bx(MOZAMBIQUE), 31)
row("ao_box_late", "kwanza", 1999, 2100, bx(ANGOLA), 31)
row("cv_escudo", "escudo_cv", 1914, 2100, [ru("Republic of Cabo Verde"), bx(CAPE_VERDE)], 46)
row("st_escudo", "escudo_ao", 1914, 1976, bx(SAO_TOME), 45)
row("st_dobra_old", "dobra_old", 1977, 2017, [ru("São Tomé and Príncipe"), bx(SAO_TOME)], 46)
row("st_dobra", "dobra", 2018, 2100, [ru("São Tomé and Príncipe"), bx(SAO_TOME)], 46)
row("gw_escudo", "escudo_pt", 1914, 1974, bx(GUINEA_BISSAU), 44, pay=[(1914, 10), (1974, 1500)])
row("gw_peso", "peso_gw", 1975, 1996, [ru("Republic of Guinea-Bissau"), bx(GUINEA_BISSAU)], 46)
row("gw_cfa", "franc_cfa", 1997, 2100, [ru("Republic of Guinea-Bissau"), bx(GUINEA_BISSAU)], 46)
row("fr_africa_franc", "franc_fwa", 1850, 1944, rb(["French Africa", "Free French", "Vichy France", "French Third Republic"],
                                                   WEST_CENTRAL_AF), 42)
row("fr_africa_cfa", "franc_cfa", 1945, 1960, rb(["French Africa", "French Fourth Republic", "French Fifth Republic",
                                                  "Free French"], WEST_CENTRAL_AF), 42)
row("cfa_countries", "franc_cfa", 1960, 2100, ru("Republic of Senegal", "Burkina Faso", "Republic of the Niger",
                                                 "Republic of Côte d'Ivoire", "Togo", "Republic of Benin",
                                                 "Republic of Cameroon", "Gabon", "Republic of the Congo",
                                                 "Republic of Chad", "Central African Republic"), 45)
row("ml_cfa", "franc_cfa", 1960, 1961, ru("Mali Federation"), 45)
row("ml_franc", "franc_ml", 1962, 1983, ru("Mali Federation"), 45)
row("ml_cfa2", "franc_cfa", 1984, 2100, ru("Mali Federation"), 45)
row("mr_cfa", "franc_cfa", 1960, 1972, ru("Mauritania"), 45)
row("gn_franc_old", "franc_gn_old", 1959, 1971, [ru("Guinea"), bx(GUINEA)], 44)
row("gn_syli", "syli", 1972, 1985, [ru("Guinea"), bx(GUINEA)], 44)
row("gn_franc", "franc_gn", 1986, 2100, [ru("Guinea"), bx(GUINEA)], 44)
row("gq_peseta_guineana", "peseta", 1969, 1974, [ru("Equatorial Guinea"), bx(EQ_GUINEA)], 46, pay=[(1869, 50), (1950, 1000), (1975, 5000)])
row("gq_ekwele", "ekwele", 1975, 1984, [ru("Equatorial Guinea"), bx(EQ_GUINEA)], 46)
row("gq_cfa", "franc_cfa", 1985, 2100, [ru("Equatorial Guinea"), bx(EQ_GUINEA)], 46)
row("gq_peseta", "peseta", 1869, 1968, bx(EQ_GUINEA), 40, pay=[(1869, 50), (1950, 1000), (1975, 5000)])
row("mg_franc_fr", "franc_fwa", 1898, 1924, [rb("French Africa", MADAGASCAR), bx(MADAGASCAR)], 42)
row("mg_franc", "madagascar_franc", 1925, 2004, [ru("Madagascar"), rb(["French Africa", "French Fourth Republic"], MADAGASCAR),
                                                 bx(MADAGASCAR)], 43)
row("mg_ariary", "ariary", 2005, 2100, [ru("Madagascar"), bx(MADAGASCAR)], 45)
row("mu_rupee", "rupee_mu", 1877, 2100, [ru("Mauritius"), bx(MAURITIUS)], 46)
row("sc_rupee", "rupee_sc", 1914, 2100, [ru("Seychelles"), bx(SEYCHELLES)], 46)
row("km_franc", "franc_km", 1950, 2100, bx(COMOROS), 46)
row("re_franc", "franc", 1815, 1959, bx(REUNION), 44, pay=[(1815, 60), (1900, 150), (1950, 20000)])
row("re_new_franc", "new_franc", 1960, 2001, bx(REUNION), 44, pay=[(1960, 700), (1980, 6000), (2001, 25000)])
row("dj_franc_fr", "franc_fwa", 1884, 1948, bx(DJIBOUTI), 44)
row("dj_franc", "franc_dj", 1949, 2100, [ru("Republic of Djibouti"), bx(DJIBOUTI)], 46)
row("br_wa_pound", "pound_wa", 1880, 1957, [rb(["British Africa", "British Colonial Empire"], WEST_AFRICA_BIG),
                                            ru("British Gold Coast")], 43)
row("gh_pound", "pound_gh", 1958, 1964, [ru("Ghana"), bx(GHANA)], 45)
row("gh_cedi_old", "cedi_old", 1965, 2006, [ru("Ghana"), bx(GHANA)], 45)
row("gh_cedi", "cedi", 2007, 2100, [ru("Ghana"), bx(GHANA)], 45)
row("ng_wa_pound", "pound_wa", 1958, 1958, bx(NIGERIA), 35)
row("ng_pound", "pound_ng", 1959, 1972, [ru("Federal Republic of Nigeria"), bx(NIGERIA)], 44)
row("ng_naira", "naira", 1973, 2100, [ru("Federal Republic of Nigeria"), bx(NIGERIA)], 44)
row("sl_wa_pound", "pound_wa", 1958, 1963, bx(SIERRA_LEONE), 44)
row("sl_leone_old", "leone_old", 1964, 2021, [ru("Sierra Leone"), bx(SIERRA_LEONE)], 46)
row("sl_leone", "leone", 2022, 2100, [ru("Sierra Leone"), bx(SIERRA_LEONE)], 46)
row("gm_wa_pound", "pound_wa", 1958, 1970, bx(GAMBIA), 46)
row("gm_dalasi", "dalasi", 1971, 2100, [ru("Republic of The Gambia"), bx(GAMBIA)], 47)
row("lr_dollar", "dollar_lr", 1847, 1906, [ru("Republic of Liberia"), bx(LIBERIA)], 45)
row("lr_wa_pound", "pound_wa", 1907, 1942, [ru("Republic of Liberia"), bx(LIBERIA)], 45)
row("lr_usd", "dollar", 1943, 1981, [ru("Republic of Liberia"), bx(LIBERIA)], 45, pay=[(1943, 25), (1981, 200)])
row("lr_dollar2", "dollar_lr", 1982, 2100, [ru("Republic of Liberia"), bx(LIBERIA)], 45)
row("ea_indian_rupee", "indian_rupee_anna", 1890, 1905, rb(["British Africa", "British Colonial Empire"], EAST_AFRICA), 43)
row("ea_rupee", "rupee_ea", 1906, 1920, rb(["British Africa", "British Colonial Empire"], EAST_AFRICA), 43)
row("ea_shilling", "shilling_ea", 1921, 1966, [rb(["British Africa", "British Colonial Empire", "British East Africa"],
                                                  EAST_AFRICA), ru("British East Africa"), bx(KENYA), bx(UGANDA),
                                               bx(TANZANIA)], 42)
row("ea_shilling_war", "shilling_ea", 1941, 1944, bx(ETHIOPIA), 45)
row("ea_somaliland", "indian_rupee_anna", 1884, 1940, bx(SOMALILAND_BR), 46)
row("ea_somaliland_shilling", "shilling_ea", 1941, 1960, bx(SOMALILAND_BR), 46)
row("de_ea_rupie", "rupie_de", 1890, 1916, rb("German Africa", EAST_AFRICA), 44)
row("de_africa_mark", "mark", 1884, 1916, ru("German Africa"), 43, pay=[(1884, 30), (1914, 60)])
row("zanzibar_rupee", "indian_rupee_anna", 1856, 1935, [ru("Sultanate of Zanzibar", "People's Republic of Zanzibar"),
                                                         bx(ZANZIBAR)], 46)
row("ke_shilling", "shilling_ke", 1966, 2100, [ru("Republic of Kenya"), bx(KENYA)], 44)
row("ug_shilling_old", "shilling_ug_old", 1966, 1986, [ru("Republic of Uganda"), bx(UGANDA)], 45)
row("ug_shilling", "shilling_ug", 1987, 2100, [ru("Republic of Uganda"), bx(UGANDA)], 45)
row("tz_shilling", "shilling_tz", 1966, 2100, [ru("Tanzania", "Sultanate of Zanzibar"), bx(TANZANIA)], 44)
row("cd_franc_be", "franc_congo", 1887, 1966, [ru("Belgian Congo"), rb("Democratic Republic of the Congo", CONGO_BELGE)], 43)
row("rw_bi_franc_be", "franc_congo", 1916, 1959, [bx(RWANDA), bx(BURUNDI)], 44)
row("cd_zaire", "zaire", 1967, 1997, [ru("Democratic Republic of the Congo", "Zaire")], 45)
row("cd_franc", "franc_cd", 1998, 2100, [ru("Democratic Republic of the Congo")], 45)
row("rw_franc", "franc_rw", 1960, 2100, [ru("Republic of Rwanda"), bx(RWANDA)], 46)
row("bi_franc", "franc_bi", 1964, 2100, [ru("Republic of Burundi"), bx(BURUNDI)], 46)
row("et_birr", "birr", 1945, 2100, [ru("Ethiopia"), bx(ETHIOPIA)], 43)
row("it_east_africa", "lira_it", 1890, 1940, [rb("Italian Africa", ERITREA), rb("Italian Africa", SOMALIA),
                                              rb("Italian Africa", ETHIOPIA)], 45, pay=[(1890, 50), (1913, 80), (1920, 300), (1940, 500)])
row("er_shilling", "shilling_ea", 1941, 1952, bx(ERITREA), 46)
row("er_birr", "birr", 1953, 1996, bx(ERITREA), 46)
row("er_nakfa", "nakfa", 1997, 2100, [ru("State of Eritrea"), bx(ERITREA)], 47)
row("so_shilling_ea", "shilling_ea", 1941, 1949, bx(SOMALIA), 44)
row("so_somalo", "somalo", 1950, 1961, [bx(SOMALIA), ru("Federal Republic of Somalia")], 44)
row("so_shilling", "shilling_so", 1962, 2100, [ru("Federal Republic of Somalia"), bx(SOMALIA)], 44)

rate("franc_fwa", 170, "franc_cfa", 1, 1945, 1948, "1 CFA franc = 1.70 French francs (1945).")
rate("cedi_old", 1000000, "cedi", 100, 2007, 2100, "10,000 old cedis = 1 new.")
rate("leone_old", 100000, "leone", 100, 2022, 2100, "1,000 old leones = 1 new.")
rate("metical_old", 100000, "metical", 100, 2006, 2100, "1,000 old meticais = 1 new.")
rate("kwacha_zm_old", 100000, "kwacha_zm", 100, 2013, 2100, "1,000 old kwacha = 1 new.")
rate("pound_wa", 240, "pound_lsd", 960, 1913, 1968, "The West African pound was at par with sterling.")
rate("pound_za", 960, "rand", 200, 1961, 2100, "1 pound = 2 rand (1961).")
rate("madagascar_franc", 5, "ariary", 5, 1961, 2100, "1 ariary = 5 Malagasy francs (5 iraimbilanja).")
rate("shilling_ea", 100, "shilling_ke", 100, 1966, 1970, "At par.")
rate("shilling_ea", 100, "shilling_tz", 1, 1966, 1970, "At par (the Tanzanian shilling counts whole shillings here).")
rate("shilling_ug_old", 10000, "shilling_ug", 1, 1987, 2100, "100 old shillings = 1 new.")


# ==============================================================================================================
# SOUTH ASIA'S NEIGHBOURS (replacing the old "local money" rows of build_money_table.py)
# ==============================================================================================================
BANGLADESH = [20.6, 88.0, 26.7, 92.7]
CEYLON = [5.8, 79.5, 9.9, 82]
NEPAL = [26.3, 80, 30.5, 88.3]
BHUTAN = [26.7, 88.7, 28.4, 92.2]
MALDIVES = [-0.8, 72.6, 7.2, 73.8]
BURMA = [20.5, 92.1, 28.6, 101.2]
BURMA_S = [9.6, 92.1, 20.5, 98.7]
TIBET = [27.3, 78.3, 36.5, 99.2]
AFGHANISTAN = [29.3, 60.5, 38.5, 74.9]

cur("rupee_pk_anna", "Pakistani rupee", [("rupee", "rupees", 192), ("anna", "annas", 12), ("pice", "pice", 3),
                                         ("pie", "pies", 1)],
    [(1948, 180), (1960, 300)], short="Pakistani", note="Rupee = 16 annas = 64 pice = 192 pies, 1948-1960. Guesses.")
cur("rupee_pk", "Pakistani rupee", dec("rupee", "rupees", "paisa", "paise"),
    [(1961, 200), (1970, 400), (1980, 1500), (1990, 4000), (2000, 10000), (2010, 25000), (2020, 60000), (2026, 120000)],
    short="Pakistani", note="Decimal rupee from 1961. Guesses.")
cur("taka", "Bangladeshi taka", dec("taka", "taka", "poisha", "poisha"),
    [(1972, 500), (1980, 1500), (1990, 3000), (2000, 6000), (2010, 15000), (2026, 60000)], note="From 1972. Guesses.")
cur("rixdollar_lk", "Ceylon rixdollar", [("rixdollar", "rixdollars", 48), ("stiver", "stivers", 1)],
    [(1795, 4), (1827, 6)], note="Dutch and early British Ceylon, to 1827. Guesses.")
cur("rupee_lk", "Ceylon rupee", dec("rupee", "rupees", "cent", "cents"),
    [(1872, 25), (1900, 40), (1940, 60), (1950, 200), (1970, 500), (1990, 5000), (2000, 15000), (2010, 50000),
     (2026, 150000)], note="Ceylon rupee from 1872 (Sri Lankan rupee from 1972). Guesses.")
cur("mohur", "Nepalese mohur", [("mohur", "mohurs", 128), ("paisa", "paisa", 4), ("dam", "dams", 1)],
    [(1640, 8), (1800, 12), (1931, 20)],
    note="Silver mohur of 128 dams; the copper paisa of 4 dams (fixed only in 1903, when the mohur became 50 paisa)."
         " Replaced at 2 mohurs to the rupee in 1932. Wages are guesses.")
cur("rupee_np", "Nepalese rupee", dec("rupee", "rupees", "paisa", "paisa"),
    [(1932, 50), (1960, 200), (1980, 1000), (2000, 7000), (2010, 25000), (2026, 70000)], note="From 1932.")
cur("ngultrum", "Bhutanese ngultrum", dec("ngultrum", "ngultrum", "chhertum", "chhertum"),
    [(1974, 300), (2000, 10000), (2026, 50000)], note="From 1974 (at par with the Indian rupee).")
cur("rupee_mv", "Maldivian rupee", dec("rupee", "rupees", "laari", "laari"), [(1947, 100), (1980, 1000)],
    note="1947-1980. Guesses.")
cur("rufiyaa", "Maldivian rufiyaa", dec("rufiyaa", "rufiyaa", "laari", "laari"), [(1981, 1000), (2026, 30000)],
    note="From 1981. Guesses.")
cur("cowrie_md", "cowrie shells", [("cowrie", "cowries", 1)], [(1000, 100), (1599, 150)], mass=True,
    note="The Maldives shipped cowries to half the world and used them at home. Guesses.")
cur("kyat_silver", "Burmese silver kyat", [("kyat", "kyats", 64), ("mat", "mats", 16), ("mu", "mu", 8), ("pe", "pe", 4),
                                           ("pya", "pyas", 1)],
    [(850, 4), (1500, 6), (1852, 8)], kind="weighed", metal="silver",
    note="Silver by weight (a kyat near 16 grams): 1 kyat = 4 mat = 8 mu = 16 pe = 64 pya; coins of the same units"
         " from 1852 to 1889. Wages are guesses.")
cur("rupee_mm", "Burmese rupee", [("rupee", "rupees", 192), ("anna", "annas", 12), ("pice", "pice", 3), ("pie", "pies", 1)],
    [(1937, 120), (1951, 300)], note="1937-1952. Guesses.")
cur("kyat", "Burmese kyat", dec("kyat", "kyats", "pya", "pyas"),
    [(1952, 300), (1970, 500), (1990, 3000), (2000, 30000), (2010, 200000), (2026, 1000000)], note="From 1952.")
cur("tangka_tb", "Tibetan tangka", [("srang", "srang", 100, 1909), ("sho", "sho", 10), ("skar", "skar", 1)],
    [(1363, 5), (1800, 8), (1950, 20)],
    note="Silver weighed in srang (taels) and counted in sho and skar; the tangka coin = 15 skar = 1.5 sho (struck"
         " from 1763), the srang coin from 1909. Wages are guesses.")

row("pk_indian", "indian_rupee_anna", 1947, 1947, ru("Islamic Republic of Pakistan"), 65)
row("pk_rupee_anna", "rupee_pk_anna", 1948, 1960, ru("Islamic Republic of Pakistan"), 65)
row("pk_rupee", "rupee_pk", 1961, 2100, ru("Islamic Republic of Pakistan"), 65)
row("bd_taka_1972", "taka", 1972, 1972, rb("Islamic Republic of Pakistan", BANGLADESH), 66)
row("bd_taka", "taka", 1972, 2100, ru("People's Republic of Bangladesh"), 65)
row("lk_rixdollar", "rixdollar_lk", 1687, 1827, [ru("Dutch Ceylon", "British Ceylon"), bx(CEYLON)], 66, pb=58)
row("lk_sterling", "pound_lsd", 1828, 1871, [ru("British Ceylon", "Ceylon"), bx(CEYLON)], 66, pb=58, pay=[(1828, 16), (1871, 24)])
row("lk_rupee", "rupee_lk", 1872, 2100, [ru("British Ceylon", "Sri Lanka"), bx(CEYLON)], 66, pb=58)
row("np_mohur", "mohur", 1640, 1931, [ru("Nepal"), bx(NEPAL)], 66, pb=50)
row("np_rupee", "rupee_np", 1932, 2100, [ru("Nepal"), bx(NEPAL)], 66, pb=50)
row("bt_rupee", "indian_rupee_anna", 1947, 1956, ru("Kingdom of Bhutan"), 65)
row("bt_np", "indian_rupee_np", 1957, 1963, ru("Kingdom of Bhutan"), 65)
row("bt_paise", "indian_rupee", 1964, 1973, ru("Kingdom of Bhutan"), 65)
row("bt_ngultrum", "ngultrum", 1974, 2100, [ru("Kingdom of Bhutan"), bx(BHUTAN)], 66, pb=50)
row("mv_cowrie", "cowrie_md", 1000, 1599, bx(MALDIVES), 70)
row("mv_larin", "dirham", 1600, 1899, bx(MALDIVES), 70, note="Larins (silver fish-hook money) and Islamic coins.")
row("mv_ceylon", "rupee_lk", 1900, 1946, bx(MALDIVES), 70)
row("mv_rupee", "rupee_mv", 1947, 1980, bx(MALDIVES), 70)
row("mv_rufiyaa", "rufiyaa", 1981, 2100, bx(MALDIVES), 70)
row("mm_silver", "kyat_silver", 850, 1852, ru("Pagan Kingdom", "Myinsaing Kingdom", "Kingdom of Pinya", "Ava Kingdom",
                                              "Hanthawaddy Kingdom", "Shan States", "Kingdom of Mrauk U",
                                              "First Toungoo Empire", "Konbaung Dynasty", "Burma"), 45)
row("mm_silver_box", "kyat_silver", 850, 1852, [bx(BURMA), bx(BURMA_S)], 32)
row("mm_indian", "indian_rupee_anna", 1853, 1936, [ru("Burma"), bx(BURMA), bx(BURMA_S)], 45)
row("mm_rupee", "rupee_mm", 1937, 1951, [ru("Burma"), bx(BURMA), bx(BURMA_S)], 45)
row("mm_kyat", "kyat", 1952, 2100, [ru("Burma", "Union of Myanmar"), bx(BURMA), bx(BURMA_S)], 45)
row("tb_tangka", "tangka_tb", 1363, 1959, [ru("Tibet", "Khoshut Khanate"), bx(TIBET)], 66, pb=45,
    note="Tibet kept its own money under Qing overlordship.")
row("af_box", "afghani_old", 1925, 2002, bx(AFGHANISTAN), 30)
row("af_box_new", "afghani", 2003, 2100, bx(AFGHANISTAN), 30)
rate("rupee_pk_anna", 192, "rupee_pk", 100, 1961, 2100, "16 annas = 100 paisa (1961).")
rate("indian_rupee_anna", 192, "rupee_pk_anna", 192, 1948, 1960, "At par.")
rate("rupee_np", 100, "indian_rupee_anna", 120, 1932, 1956, "Rough: about 1.6 Nepalese rupees to the Indian rupee.")
rate("ngultrum", 100, "indian_rupee", 100, 1974, 2100, "At par with the Indian rupee.")


# ==============================================================================================================
# EAST ASIA
# ==============================================================================================================
TAIWAN = [21.8, 119.3, 25.4, 122.1]
HONG_KONG = [22.15, 113.82, 22.57, 114.45]
MACAU = [22.1, 113.52, 22.22, 113.6]
MANCHURIA = [38.7, 115.5, 53.6, 135.1]
OKINAWA = [24, 122.9, 28.5, 131.5]
JAPAN = [30, 129, 45.6, 146]
KOREA = [33, 124, 43.1, 131]
MONGOLIA = [41.5, 87.7, 52.2, 120]
XINJIANG = [34.3, 73.5, 49.2, 96.4]
CHINA_CORE = [30, 105, 41, 122]
STEPPE = [40, 45, 55, 125]

cur("silver_tael", "silver by weight", [("tael", "taels", 100), ("mace", "mace", 10), ("candareen", "candareens", 1)],
    [(1000, 5), (1900, 8)], kind="weighed", metal="silver", mass=True,
    note="Silver weighed in taels (liang), mace (qian) and candareens (fen): Mongol ingots, Korean silver vases, the"
         " silver of East and South-East Asian trade. Half a mace a day is a guess.")
cur("cowrie_cn", "cowrie shells", [("string of cowries", "strings of cowries", 10), ("cowrie", "cowries", 1)],
    [(-1600, 5), (-601, 5)], mass=True,
    note="Shang and Zhou cowrie money (shells and bronze imitations), counted in strings. Guesses.")
cur("twd", "New Taiwan dollar", [("dollar", "dollars", 1)],
    [(1949, 3), (1960, 20), (1970, 50), (1980, 200), (1990, 600), (2000, 1000), (2010, 1200), (2026, 1800)],
    note="From 1949 (cents not in use). Guesses.")
cur("hkd", "Hong Kong dollar", dec("dollar", "dollars", "cent", "cents"),
    [(1842, 15), (1900, 30), (1940, 100), (1950, 400), (1970, 1500), (1990, 20000), (2000, 40000), (2026, 70000)],
    note="From 1863 (Spanish and Mexican dollars before). Guesses.")
cur("pataca", "Macanese pataca", dec("pataca", "patacas", "avo", "avos"),
    [(1894, 25), (1950, 400), (2000, 30000), (2026, 70000)], note="From 1894. Guesses.")
cur("yuan_mk", "Manchukuo yuan", dec("yuan", "yuan", "fen", "fen"), [(1932, 40), (1945, 100)], note="1932-1945.")
cur("tugrik", "Mongolian tögrög", dec("tögrög", "tögrög", "möngö", "möngö"),
    [(1925, 100), (1950, 300), (1990, 1000), (2000, 150000), (2010, 600000), (2026, 3500000)], note="From 1925.")
cur("mun_kr", "Korean mun", [("nyang", "nyang", 100), ("jeon", "jeon", 10), ("mun", "mun", 1)],
    [(1678, 20), (1800, 30), (1891, 100)], note="Sangpyeong tongbo cash from 1678: nyang = 10 jeon = 100 mun. Guesses.")
cur("yang_kr", "Korean yang", dec("yang", "yang", "fun", "fun"), [(1892, 50), (1901, 100)], note="1892-1902.")
cur("won_kr_1902", "Korean won", dec("won", "won", "chon", "chon"), [(1902, 20), (1910, 30)], note="1902-1910.")
cur("yen_kr", "Korean yen", dec("yen", "yen", "sen", "sen"), [(1910, 40), (1930, 60), (1945, 300)],
    note="1910-1945, at par with the Japanese yen. Guesses.")
cur("won_kr_1945", "South Korean won", dec("won", "won", "jeon", "jeon"), [(1945, 5000), (1953, 50000)],
    note="1945-1953. Guesses.")
cur("hwan", "South Korean hwan", dec("hwan", "hwan", "jeon", "jeon"), [(1953, 1500), (1961, 10000)],
    note="1953-1962 (100 won). Guesses.")
cur("won_kr", "South Korean won", [("won", "won", 1)],
    [(1962, 100), (1970, 300), (1980, 3000), (1990, 15000), (2000, 40000), (2010, 60000), (2026, 120000)],
    note="From 1962 (10 hwan). Guesses.")
cur("won_kp_old", "North Korean won", dec("won", "won", "chon", "chon"), [(1947, 3000), (1958, 10000)],
    note="1947-1958. Guesses.")
cur("won_kp", "North Korean won", dec("won", "won", "chon", "chon"), [(1959, 200), (1990, 300), (2002, 10000), (2008, 20000)],
    note="1959-2009 (100 old). Guesses.")
cur("won_kp_2009", "North Korean won", dec("won", "won", "chon", "chon"), [(2009, 1000), (2026, 300000)],
    note="From 2009 (100 old; market prices rose far beyond the official ones). Guesses.")

row("china_qing", "china_cash", 1645, 1911, ru("Qing Dynasty", "Southern Ming", "Later Jin Dynasty", "Li Zicheng"), 40)
row("china_ming", "china_cash", 1368, 1644, ru("Ming Dynasty"), 40)
row("china_roc", "yuan_rep", 1912, 1948, ru("Republic of China", "Kuomintang", "Anti-Kuomintang Coalition",
                                            "Communist Party of China", "Chinese Communists", "Empire of China",
                                            "East Turkestan Republic", "Great Mongol State"), 42)
row("china_prc", "rmb", 1949, 2100, ru("People's Republic of China"), 42)
row("taiwan_twd", "twd", 1949, 2100, [ru("Republic of China"), bx(TAIWAN)], 44)
row("taiwan_yen", "yen", 1895, 1945, rb("Empire of Japan", TAIWAN), 46)
row("taiwan_old", "yuan_rep", 1946, 1948, bx(TAIWAN), 44)
row("hk_dollar", "hkd", 1842, 2100, bx(HONG_KONG), 70)
row("macau_pataca", "pataca", 1894, 2100, bx(MACAU), 70)
row("manchukuo", "yuan_mk", 1932, 1945, rb("Empire of Japan", MANCHURIA), 46)
row("okinawa_mon", "mon", 1429, 1878, [bx(OKINAWA), ru("Ryukyu Kingdom")], 35)
row("okinawa_yen", "yen", 1879, 1957, bx(OKINAWA), 35)
row("okinawa_dollar", "dollar", 1958, 1971, bx(OKINAWA), 35, pay=[(1958, 150), (1971, 400)])
row("okinawa_yen2", "yen", 1972, 2100, bx(OKINAWA), 35)
row("japan_barter", "barter", -100000, 707, bx(JAPAN), 15, note="Rice and cloth before the first coins (708).")
row("korea_barter", "barter", -100000, 1100, bx(KOREA), 15, note="Rice and hemp cloth before metal money.")
row("korea_goryeo_silver", "silver_tael", 1101, 1394, [ru("Goryeo"), bx(KOREA)], 41,
    note="Goryeo's silver vases (eunbyeong), weighed silver.")
row("korea_joseon_barter", "barter", 1395, 1677, [ru("Joseon"), bx(KOREA)], 41,
    note="Rice and cotton cloth served as money until copper cash spread in 1678.")
row("korea_mun", "mun_kr", 1678, 1891, [ru("Joseon"), bx(KOREA)], 41)
row("korea_yang", "yang_kr", 1892, 1901, [ru("Joseon", "Korean Empire"), bx(KOREA)], 41)
row("korea_won_1902", "won_kr_1902", 1902, 1910, [ru("Korean Empire"), bx(KOREA)], 41)
row("korea_yen", "yen_kr", 1910, 1945, [rb("Empire of Japan", KOREA), bx(KOREA)], 41)
row("korea_won_1945", "won_kr_1945", 1945, 1953, [ru("Republic of Korea"), bx(KOREA)], 41)
row("korea_hwan", "hwan", 1953, 1961, ru("Republic of Korea"), 45)
row("korea_won", "won_kr", 1962, 2100, ru("Republic of Korea"), 45)
row("nk_won_old", "won_kp_old", 1947, 1958, ru("Democratic People's Republic of Korea"), 46)
row("nk_won", "won_kp", 1959, 2008, ru("Democratic People's Republic of Korea"), 46)
row("nk_won_2009", "won_kp_2009", 2009, 2100, ru("Democratic People's Republic of Korea"), 46)
row("china_cowrie", "cowrie_cn", -1600, -601, bx(CHINA_CORE), 30)
row("mongol_empire_silver", "silver_tael", 1206, 1293, ru("Mongol Empire"), 40)
row("mongolia_tugrik", "tugrik", 1925, 2100, [ru("Mongolian People's Republic", "Mongolia"), bx(MONGOLIA)], 42)
row("xinjiang_tanga", "tanga", 1500, 1758, [ru("Dzungar Khanate", "Oirat Confederation"), bx(XINJIANG)], 21)
row("steppe_barter", "barter", -100000, 1924, bx(STEPPE), 6,
    note="Herders swapped livestock, felt, tea and silk; coins came only with the towns.")
rate("yen", 100, "yen_kr", 100, 1910, 1945, "At par.")
rate("hwan", 1000, "won_kr", 1, 1962, 2100, "10 hwan = 1 won (1962).")
rate("won_kr_1945", 10000, "hwan", 100, 1953, 1961, "100 won = 1 hwan (1953).")


# ==============================================================================================================
# SOUTH-EAST ASIA
# ==============================================================================================================
VIETNAM_N = [17, 102, 23.5, 109.5]
VIETNAM = [8.4, 102.1, 23.4, 109.5]
CAMBODIA = [10.3, 102.3, 14.7, 107.7]
LAOS = [13.9, 100.0, 22.5, 107.7]
SIAM = [5.6, 97.3, 20.5, 105.7]
MALAYA = [1.2, 99.6, 6.8, 104.6]
SINGAPORE = [1.15, 103.6, 1.48, 104.1]
BORNEO_N = [0.8, 109.5, 7.4, 119.3]
BRUNEI = [4.0, 114.0, 5.1, 115.4]
INDONESIA = [-11.1, 95, 6, 141.1]
JAVA_BALI = [-9, 105, -5.8, 115.8]
SUMATRA = [-6, 95, 6, 106.1]
PHILIPPINES = [4.5, 116.8, 21.2, 126.7]
TIMOR_E = [-9.6, 124.0, -8.1, 127.4]
SE_ASIA = [-11, 92, 28.5, 141]

cur("van_vn", "Vietnamese cash", [("quan", "quan", 600), ("tiền", "tiền", 60), ("văn", "văn", 1)],
    [(970, 20), (1500, 40), (1800, 60), (1884, 100), (1948, 600)],
    note="Copper (later zinc) cash, 600 to the string (quan), 60 to the tien, from 970 to 1948. Guesses.")
cur("piastre_ic", "French Indochinese piastre", dec("piastre", "piastres", "cent", "cents"),
    [(1885, 20), (1914, 25), (1930, 30), (1945, 300), (1954, 2000)], note="1885-1955. Guesses.")
cur("dong_dr", "North Vietnamese đồng", dec("đồng", "đồng", "xu", "xu"), [(1946, 1000), (1951, 200), (1977, 300)],
    note="Democratic Republic of Vietnam, 1946-1978 (the 1951 change of 100 to 1 is followed roughly).")
cur("dong_sv", "South Vietnamese đồng", dec("đồng", "đồng", "xu", "xu"), [(1953, 2000), (1975, 50000)],
    note="1953-1975. Guesses.")
cur("dong", "Vietnamese đồng", [("đồng", "đồng", 1)], [(1978, 3), (1985, 30), (1990, 3000), (2000, 15000),
                                                      (2010, 60000), (2026, 250000)],
    note="Unified dong from 1978 (the 1985 change of 10 to 1 roughly). Guesses.")
cur("riel", "Cambodian riel", [("riel", "riels", 1)], [(1955, 30), (1975, 100), (1980, 10), (1990, 300), (2000, 4000),
                                                      (2010, 10000), (2026, 30000)],
    note="1955-1975 and from 1980 (no money under the Khmer Rouge). Guesses.")
cur("tical_kh", "Cambodian tical", [("tical", "ticals", 64), ("att", "att", 1)], [(1847, 8), (1884, 16)],
    note="Cambodian coins on the Siamese pattern, 1847-1884. Guesses.")
cur("kip", "Lao kip", [("kip", "kip", 1)], [(1952, 30), (1975, 300), (1990, 500), (2000, 10000), (2026, 150000)],
    note="From 1952 (att not in use). Guesses.")
cur("baht_old", "Siamese tical", [("tamlueng", "tamlueng", 25600), ("baht", "baht", 6400), ("salueng", "salueng", 1600),
                                  ("fueang", "fueang", 800), ("att", "att", 100), ("bia", "bia", 1)],
    [(1238, 400), (1600, 800), (1800, 1600), (1896, 2400)],
    note="Silver bullet money (pod duang, flat coins from 1860): 1 baht = 4 salueng = 8 fueang = 64 att, 1 att ="
         " 100 bia (cowrie shells); 1 tamlueng = 4 baht. Wages are guesses.")
cur("baht", "Thai baht", dec("baht", "baht", "satang", "satang"),
    [(1897, 50), (1930, 100), (1950, 1000), (1970, 2000), (1990, 9000), (2000, 16000), (2010, 20000), (2026, 38000)],
    note="Decimal baht from 1897. Guesses.")
cur("dollar_es_asia", "Spanish dollar", dec("dollar", "dollars", "cent", "cents"),
    [(1600, 5), (1800, 10), (1867, 15)],
    note="Spanish and Mexican silver dollars, the trade money of Malaya, Borneo and the China coast; reckoned in"
         " 100 cents in the Straits. Guesses.")
cur("straits_dollar", "Straits dollar", dec("dollar", "dollars", "cent", "cents"), [(1867, 15), (1900, 30), (1938, 50)],
    note="Straits Settlements, 1867 (issued 1898)-1939. Guesses.")
cur("malayan_dollar", "Malayan dollar", dec("dollar", "dollars", "cent", "cents"), [(1939, 50), (1953, 150), (1966, 300)],
    note="Malayan dollar, then the Malaya and British Borneo dollar, 1939-1967. Guesses.")
cur("ringgit", "Malaysian ringgit", dec("ringgit", "ringgit", "sen", "sen"),
    [(1967, 300), (1980, 1000), (2000, 2500), (2010, 4000), (2026, 7000)], note="From 1967. Guesses.")
cur("sgd", "Singapore dollar", dec("dollar", "dollars", "cent", "cents"), [(1967, 400), (1990, 3000), (2026, 8000)],
    note="From 1967. Guesses.")
cur("bnd", "Brunei dollar", dec("dollar", "dollars", "cent", "cents"), [(1967, 400), (2026, 6000)],
    note="From 1967 (at par with the Singapore dollar).")
cur("sarawak_dollar", "Sarawak dollar", dec("dollar", "dollars", "cent", "cents"), [(1858, 15), (1952, 100)],
    note="Sarawak and North Borneo dollars, 1858-1953. Guesses.")
cur("mas_java", "Javanese mas", [("tahil", "tahil", 64), ("mas", "mas", 4), ("kupang", "kupang", 1)],
    [(850, 2), (1299, 2)], note="Gold and silver pieces by weight: tahil = 16 mas = 64 kupang. Guesses.")
cur("guilder_ni", "Netherlands Indies guilder", dec("guilder", "guilders", "cent", "cents"),
    [(1817, 15), (1900, 30), (1930, 40), (1945, 100), (1949, 200)], note="1817-1949. Guesses.")
cur("rupiah_old", "Indonesian rupiah", dec("rupiah", "rupiah", "sen", "sen"), [(1946, 300), (1960, 3000), (1965, 300000)],
    note="1946-1965. Guesses.")
cur("rupiah", "Indonesian rupiah", [("rupiah", "rupiah", 1)],
    [(1966, 30), (1980, 1000), (1990, 2500), (2000, 15000), (2010, 50000), (2026, 120000)],
    note="New rupiah (1,000 old) from 1965. Guesses.")
cur("peso_ph", "Philippine peso", dec("peso", "pesos", "centavo", "centavos"),
    [(1857, 25), (1900, 50), (1940, 100), (1950, 300), (1970, 800), (1990, 9000), (2000, 22000), (2010, 35000),
     (2026, 60000)], note="Peso = 100 centimos/centavos from 1857 (8 reales before). Guesses.")
cur("pataca_tl", "Portuguese Timor pataca", dec("pataca", "patacas", "avo", "avos"), [(1894, 15), (1958, 100)],
    note="1894-1958. Guesses.")

row("vn_cash", "van_vn", 970, 1884, [bx(VIETNAM_N), ru("Lê Dynasty", "Đại Việt", "Nguyễn lords", "Tây Sơn dynasty",
                                                     "Nguyễn dynasty")], 35)
row("vn_cash_south", "van_vn", 1700, 1884, bx(VIETNAM), 34)
row("vn_piastre", "piastre_ic", 1885, 1954, [rb("French Indochina", VIETNAM), ru("Nguyễn dynasty"), bx(VIETNAM)], 41)
row("vn_dong_n", "dong_dr", 1946, 1977, ru("Democratic Republic of Vietnam"), 46)
row("vn_dong_s", "dong_sv", 1953, 1975, ru("Republic of Vietnam"), 46)
row("vn_dong", "dong", 1978, 2100, [ru("Socialist Republic of Vietnam"), bx(VIETNAM)], 45)
row("vn_dong_1976", "dong_dr", 1976, 1977, ru("Socialist Republic of Vietnam"), 46)
row("champa_silver", "silver_tael", 207, 1652, ru("Chámpa"), 41)
row("kh_silver", "silver_tael", 800, 1846, [ru("Khmer Empire", "Cambodia", "Land Chenla", "Water Chenla", "Chenla",
                                              "Funan"), bx(CAMBODIA)], 33,
    note="Angkor and after: rice, cloth and silver by weight; no coins of its own until 1847.")
row("kh_tical", "tical_kh", 1847, 1884, [ru("Khmer Empire", "Cambodia"), bx(CAMBODIA)], 41)
row("kh_piastre", "piastre_ic", 1885, 1954, [rb("French Indochina", CAMBODIA), bx(CAMBODIA)], 42)
row("kh_riel", "riel", 1955, 1975, [ru("Kingdom of Cambodia"), bx(CAMBODIA)], 45)
row("kh_none", "barter", 1976, 1979, [ru("Khmer Rouge"), bx(CAMBODIA)], 46, note="The Khmer Rouge abolished money.")
row("kh_riel2", "riel", 1980, 2100, [ru("People's Republic of Kampuchea", "Kingdom of Cambodia"), bx(CAMBODIA)], 45)
row("la_silver", "silver_tael", 1353, 1892, [ru("Lan Xang", "Kingdom of Luang Phrabang", "Kingdom of Champasak"), bx(LAOS)], 33,
    note="Lao bar money (lat and tok) of silver and bronze, by weight.")
row("la_piastre", "piastre_ic", 1893, 1951, [rb("French Indochina", LAOS), bx(LAOS)], 40)
row("la_kip", "kip", 1952, 2100, [ru("Kingdom of Laos", "Communist Laos"), bx(LAOS)], 45)
row("th_tical", "baht_old", 1238, 1896, [ru("Sukhothai Kingdom", "Ayutthaya Kingdom", "Thonburi Kingdom",
                                           "Rattanakosin Kingdom", "Lavo Kingdom"), bx(SIAM)], 32)
row("th_baht", "baht", 1897, 2100, [ru("Rattanakosin Kingdom", "Kingdom of Thailand"), bx(SIAM)], 44)
row("my_dollar_es", "dollar_es_asia", 1600, 1866, [ru("Sultanate of Malacca", "Sultanate of Johor", "Sultanate of Kedah",
                                                     "Kelantan", "Sultanate of Terengganu", "Kedah-Perlis District",
                                                     "Sultanate of Brunei", "Sultanate of Sulu"),
                                                  bx(MALAYA), bx(BORNEO_N)], 33)
row("my_straits", "straits_dollar", 1867, 1938, [rb("British Colonial Empire", MALAYA), ru("Sultanate of Kedah",
                                                                                         "Kelantan", "Sultanate of Terengganu",
                                                                                         "Kedah-Perlis District",
                                                                                         "Sultanate of Johor"), bx(MALAYA)], 40)
row("my_malayan", "malayan_dollar", 1939, 1966, [rb("British Colonial Empire", MALAYA), ru("Federation of Malaya", "Malaysia",
                                                                                         "Republic of Singapore"),
                                                 bx(MALAYA), rb("British Colonial Empire", BORNEO_N)], 41)
row("my_ringgit", "ringgit", 1967, 2100, [ru("Malaysia"), bx(MALAYA)], 44)
row("sg_dollar", "sgd", 1967, 2100, [ru("Republic of Singapore"), bx(SINGAPORE)], 47)
row("bn_dollar", "bnd", 1967, 2100, [ru("Sultanate of Brunei"), bx(BRUNEI)], 47)
row("sarawak", "sarawak_dollar", 1858, 1952, [ru("Kingdom of Sarawak", "Sultanate of Sambaliung"), bx(BORNEO_N)], 39)
row("borneo_n_ringgit", "ringgit", 1967, 2100, bx(BORNEO_N), 38)
row("java_mas", "mas_java", 850, 1299, [ru("Mataram Kingdom", "Srivijaya", "Sunda Kingdom", "Early Balinese Kingdoms",
                                           "Malaya"), bx(JAVA_BALI), bx(SUMATRA)], 31)
row("java_kepeng", "china_cash", 1300, 1601, [ru("Majapahit", "Sunda Kingdom", "Balinese Kingdom", "Sultanate of Aceh",
                                                 "Sultanate of Malacca", "Kingdom of Singapura", "Mataram Sultanate"),
                                              bx(JAVA_BALI), bx(SUMATRA)], 31,
    note="Chinese copper cash (kepeng, picis) were the small money of Java and Bali.")
row("indies_voc", "guilder_nl_old", 1602, 1816, [rb(["Dutch Republic", "Batavian Republic", "Napoleonic Batavia Republic"],
                                                    INDONESIA), bx(JAVA_BALI)], 32, pay=[(1602, 16), (1816, 24)])
row("indies_bali_kepeng", "china_cash", 1602, 1907, ru("Bali", "Balinese Kingdom", "Mataram Sultanate", "Sultanate of Jambi"), 41)
row("indies_guilder", "guilder_ni", 1817, 1949, [ru("Dutch East Indies"), bx(INDONESIA)], 33)
row("id_rupiah_old", "rupiah_old", 1946, 1965, ru("Republic of Indonesia"), 45)
row("id_rupiah", "rupiah", 1966, 2100, [ru("Republic of Indonesia"), bx(INDONESIA)], 44)
row("ph_barter", "barter", -100000, 1564, bx(PHILIPPINES), 9, note="Barter and gold by weight before Spain.")
row("ph_spanish", "peso_real", 1565, 1856, bx(PHILIPPINES), 33)
row("ph_peso", "peso_ph", 1857, 2100, [ru("Republic of the Philippines"), bx(PHILIPPINES)], 44)
row("tl_pataca", "pataca_tl", 1894, 1958, bx(TIMOR_E), 46)
row("tl_escudo", "escudo_pt", 1959, 1975, bx(TIMOR_E), 46, pay=[(1959, 500), (1975, 1000)])
row("tl_rupiah", "rupiah", 1976, 1999, bx(TIMOR_E), 46)
row("tl_dollar", "dollar", 2000, 2100, [ru("East Timor"), bx(TIMOR_E)], 47, pay=[(2000, 300), (2026, 600)])
row("se_asia_barter", "barter", -100000, 2100, bx(SE_ASIA), 4)
rate("baht_old", 6400, "baht", 100, 1897, 1910, "1 baht = 64 att = 100 satang (1897).")
rate("rupiah_old", 100000, "rupiah", 1, 1966, 2100, "1,000 old rupiah = 1 new.")
rate("malayan_dollar", 100, "ringgit", 100, 1967, 1972, "At par.")
rate("ringgit", 100, "sgd", 100, 1967, 1972, "At par until 1973.")
rate("sgd", 100, "bnd", 100, 1967, 2100, "At par (the currency interchangeability agreement).")
rate("guilder_ni", 100, "guilder_nl", 100, 1817, 1940, "At par with the Dutch guilder.")


# ==============================================================================================================
# THE AMERICAS
# ==============================================================================================================
AMERICAS = [-56, -170, 72, -30]
NORTH_AMERICA = [14, -170, 72, -50]
CANADA = [41.7, -141, 83.2, -52.6]
CANADA_EAST = [42, -80, 52.5, -59]
RUPERTS_LAND = [49, -120, 70, -60]
NEWFOUNDLAND = [46.6, -59.5, 60.4, -52.6]
ALASKA = [51, -170, 72, -129.9]
HAWAII = [18.5, -161, 22.5, -154.5]
USA_BIG = [24.5, -125, 49.5, -66.9]
MEXICO = [14.5, -118.5, 32.8, -86.7]
CENTRAL_AM = [7, -92.3, 18.5, -77.1]
GUATEMALA = [13.7, -92.3, 17.9, -88.2]
BELIZE = [15.8, -89.3, 18.5, -87.4]
EL_SALVADOR = [13.1, -90.2, 14.5, -87.6]
HONDURAS = [12.9, -89.4, 16.6, -83.1]
NICARAGUA = [10.7, -87.7, 15.1, -82.6]
COSTA_RICA = [8.0, -86.0, 11.3, -82.5]
PANAMA = [7.1, -83.1, 9.7, -77.1]
CUBA = [19.8, -85, 23.3, -74.1]
HISPANIOLA_W = [18.0, -74.5, 20.1, -71.7]
HISPANIOLA_E = [17.5, -71.7, 20.0, -68.3]
JAMAICA = [17.7, -78.4, 18.6, -76.2]
PUERTO_RICO = [17.9, -67.3, 18.6, -65.2]
BAHAMAS = [20.9, -79.6, 27.3, -72.7]
LESSER_ANTILLES = [10, -65.0, 18.6, -59.4]
FR_ANTILLES = [14.3, -61.9, 16.6, -60.8]
ABC = [12.0, -70.1, 12.4, -68.2]
TRINIDAD = [10.0, -61.95, 11.4, -60.5]
COLOMBIA = [-4.3, -79.1, 12.5, -66.8]
VENEZUELA = [0.6, -73.4, 12.3, -59.8]
ECUADOR = [-5.1, -81.1, 1.5, -75.2]
PERU = [-18.4, -81.4, -0.03, -68.6]
BOLIVIA = [-22.9, -69.7, -9.6, -57.4]
CHILE = [-56, -75.8, -17.5, -66.4]
ARGENTINA = [-55.1, -73.6, -21.7, -53.6]
URUGUAY = [-35, -58.3, -30.1, -53.1]
PARAGUAY = [-27.6, -62.7, -19.3, -54.2]
BRAZIL = [-33.8, -74, 5.3, -34.7]
BRAZIL_COAST = [-33.8, -55, -1, -34.7]
RIO_PLATA = [-40, -62, -20, -53]
GUYANA = [1.1, -61.4, 8.6, -56.4]
SURINAME = [1.8, -58.1, 6.1, -53.9]
FR_GUIANA = [2.1, -54.6, 5.8, -51.6]
FALKLANDS = [-52.5, -61.5, -51, -57.6]

cur("made_beaver", "made beaver", [("made beaver", "made beaver", 8), ("eighth of a made beaver",
                                                                     "eighths of a made beaver", 1)],
    [(1670, 4), (1870, 4)], mass=True,
    note="The Hudson's Bay Company's unit of trade: a prime beaver pelt; brass tokens of 1, 1/2, 1/4 and 1/8 made"
         " beaver (1854). Half a made beaver a day is a guess.")
cur("pound_ca", "Canadian pound", [("pound", "pounds", 960), ("shilling", "shillings", 48), ("penny", "pence", 4),
                                   ("farthing", "farthings", 1)],
    [(1764, 60), (1800, 80), (1857, 120)], note="Halifax currency: 1 pound = 4 Spanish dollars, 1764-1857. Guesses.")
cur("cad", "Canadian dollar", dec("dollar", "dollars", "cent", "cents"),
    [(1858, 75), (1900, 150), (1920, 350), (1940, 350), (1950, 700), (1970, 1800), (1990, 6000), (2000, 8000),
     (2010, 12000), (2026, 15000)], note="From 1858 (Newfoundland's dollar 1865-1949 at par). Guesses.")
cur("dollar_hi", "Hawaiian dollar", dec("dollar", "dollars", "cent", "cents"), [(1847, 50), (1898, 100)],
    note="At par with the US dollar, 1847-1898. Guesses.")
cur("peso_mx_real", "Mexican peso", [("peso", "pesos", 8), ("real", "reales", 1)], [(1822, 3), (1862, 4)],
    note="Peso of 8 reales, 1822-1862. Guesses.")
cur("peso_mx", "Mexican peso", dec("peso", "pesos", "centavo", "centavos"),
    [(1863, 37), (1900, 50), (1930, 150), (1950, 500), (1970, 2500), (1980, 15000), (1990, 1000000), (1992, 1300000)],
    note="Decimal peso 1863-1992 (the 1980s inflation roughly). Guesses.")
cur("peso_mx_new", "Mexican peso", dec("peso", "pesos", "centavo", "centavos"),
    [(1993, 1500), (2000, 3500), (2010, 6000), (2026, 30000)], note="New peso (1,000 old) from 1993. Guesses.")
cur("peso_ca", "Central American peso", [("peso", "pesos", 8), ("real", "reales", 1)], [(1823, 3), (1890, 6)],
    note="The peso of 8 reales of the Central American republics before their own currencies. Guesses.")
cur("quetzal", "Guatemalan quetzal", dec("quetzal", "quetzales", "centavo", "centavos"),
    [(1925, 30), (1950, 80), (1980, 300), (2000, 3000), (2026, 13000)], note="From 1925. Guesses.")
cur("colon_sv", "Salvadoran colón", dec("colón", "colones", "centavo", "centavos"),
    [(1919, 50), (1950, 150), (1980, 800), (2000, 4000)], note="1919-2001, then the US dollar. Guesses.")
cur("lempira", "Honduran lempira", dec("lempira", "lempiras", "centavo", "centavos"),
    [(1931, 50), (1980, 400), (2000, 5000), (2026, 40000)], note="From 1931. Guesses.")
cur("cordoba", "Nicaraguan córdoba", dec("córdoba", "córdobas", "centavo", "centavos"),
    [(1912, 30), (1950, 300), (1980, 2000), (1991, 1000), (2000, 3000), (2026, 30000)],
    note="From 1912 (the 1980s collapse and the cordoba oro of 1991 roughly). Guesses.")
cur("colon_cr", "Costa Rican colón", dec("colón", "colones", "céntimo", "céntimos"),
    [(1896, 100), (1950, 600), (1980, 6000), (2000, 300000), (2026, 1500000)], note="From 1896. Guesses.")
cur("balboa", "Panamanian balboa", dec("balboa", "balboas", "centésimo", "centésimos"),
    [(1904, 75), (1950, 300), (1980, 1000), (2000, 1500), (2026, 3000)], note="From 1904, at par with the US dollar.")
cur("bz_dollar", "Belize dollar", dec("dollar", "dollars", "cent", "cents"),
    [(1885, 50), (1950, 200), (2000, 2500), (2026, 5000)], note="British Honduras dollar from 1885. Guesses.")
cur("peso_cu", "Cuban peso", dec("peso", "pesos", "centavo", "centavos"),
    [(1857, 50), (1915, 100), (1950, 300), (1980, 500), (2000, 1000), (2020, 3000), (2026, 30000)],
    note="Spanish Cuban peso, then the Cuban peso from 1915 (US dollars also used to 1951). Guesses.")
cur("gourde", "Haitian gourde", dec("gourde", "gourdes", "centime", "centimes"),
    [(1813, 25), (1900, 50), (1950, 250), (1990, 1500), (2026, 50000)], note="From 1813. Guesses.")
cur("peso_do", "Dominican peso", dec("peso", "pesos", "centavo", "centavos"),
    [(1844, 25), (1950, 150), (1980, 500), (2000, 10000), (2026, 60000)],
    note="From 1844 (the US dollar 1905-1947 is folded in). Guesses.")
cur("pound_jm", "Jamaican pound", [("pound", "pounds", 240), ("shilling", "shillings", 12), ("penny", "pence", 1)],
    [(1840, 12), (1900, 18), (1950, 48), (1968, 96)], note="1840-1969. Guesses.")
cur("dollar_jm", "Jamaican dollar", dec("dollar", "dollars", "cent", "cents"),
    [(1969, 400), (1990, 5000), (2000, 30000), (2026, 300000)], note="From 1969. Guesses.")
cur("dollar_bwi", "British West Indies dollar", dec("dollar", "dollars", "cent", "cents"),
    [(1935, 80), (1950, 200), (1965, 400)],
    note="British West Indies dollar (1935) and British Caribbean dollar (1949-1965). Guesses.")
cur("xcd", "East Caribbean dollar", dec("dollar", "dollars", "cent", "cents"),
    [(1965, 400), (1990, 2000), (2026, 6000)], note="From 1965. Guesses.")
cur("ttd", "Trinidad and Tobago dollar", dec("dollar", "dollars", "cent", "cents"),
    [(1964, 400), (1990, 3000), (2026, 25000)], note="From 1964. Guesses.")
cur("bsd", "Bahamian dollar", dec("dollar", "dollars", "cent", "cents"), [(1966, 800), (2026, 8000)],
    note="From 1966, at par with the US dollar.")
cur("bbd", "Barbadian dollar", dec("dollar", "dollars", "cent", "cents"), [(1973, 800), (2026, 12000)], note="From 1973.")
cur("ang", "Netherlands Antillean guilder", dec("guilder", "guilders", "cent", "cents"),
    [(1828, 30), (1950, 300), (2000, 3000), (2026, 8000)], note="Curacao and the Antilles. Guesses.")
cur("peso_co", "Colombian peso", dec("peso", "pesos", "centavo", "centavos"),
    [(1820, 30), (1900, 80), (1950, 300), (1970, 2000), (1990, 100000), (2000, 1000000), (2026, 5000000)],
    note="From 1810 (decimal from 1847). Guesses.")
cur("bolivar", "Venezuelan bolívar", dec("bolívar", "bolívares", "céntimo", "céntimos"),
    [(1879, 150), (1950, 1000), (1980, 4000), (1990, 15000), (2000, 500000), (2007, 2000000)],
    note="1879-2007 (the venezolano 1871-1879 folded in). Guesses.")
cur("bolivar_fuerte", "Venezuelan bolívar fuerte", dec("bolívar", "bolívares", "céntimo", "céntimos"),
    [(2008, 3000), (2017, 10000000)], note="2008-2018 (the hyperinflation roughly).")
cur("bolivar_soberano", "Venezuelan bolívar soberano", dec("bolívar", "bolívares", "céntimo", "céntimos"),
    [(2018, 10000), (2021, 1000000000)], note="2018-2021 (roughly).")
cur("bolivar_digital", "Venezuelan bolívar", dec("bolívar", "bolívares", "céntimo", "céntimos"),
    [(2021, 1000), (2026, 30000)], note="Bolivar digital from October 2021. Guesses.")
cur("sucre", "Ecuadorian sucre", dec("sucre", "sucres", "centavo", "centavos"),
    [(1884, 50), (1950, 1000), (1980, 10000), (1990, 300000), (1999, 5000000)], note="1884-2000. Guesses.")
cur("sol_pe", "Peruvian sol", dec("sol", "soles", "centavo", "centavos"),
    [(1863, 50), (1900, 80), (1950, 1000), (1970, 5000), (1980, 50000), (1985, 1000000)], note="1863-1985. Guesses.")
cur("inti", "Peruvian inti", dec("inti", "intis", "céntimo", "céntimos"), [(1985, 3000), (1991, 250000000)],
    note="1985-1991 (the hyperinflation roughly).")
cur("sol_pe_new", "Peruvian sol", dec("sol", "soles", "céntimo", "céntimos"),
    [(1991, 250), (2000, 1500), (2010, 3000), (2026, 6000)], note="Nuevo sol (1,000,000 intis) from 1991.")
cur("boliviano_old", "Bolivian boliviano", dec("boliviano", "bolivianos", "centavo", "centavos"),
    [(1864, 50), (1900, 100), (1950, 3000), (1962, 500000)], note="1864-1963. Guesses.")
cur("peso_bo", "Bolivian peso", dec("peso", "pesos", "centavo", "centavos"), [(1963, 500), (1980, 3000), (1986, 300000000)],
    note="1963-1986 (the hyperinflation roughly).")
cur("boliviano", "Bolivian boliviano", dec("boliviano", "bolivianos", "centavo", "centavos"),
    [(1987, 500), (2000, 2000), (2026, 8000)], note="From 1987 (1,000,000 pesos). Guesses.")
cur("peso_cl_old", "Chilean peso", dec("peso", "pesos", "centavo", "centavos"),
    [(1817, 30), (1900, 150), (1950, 5000), (1959, 50000)], note="1817-1959. Guesses.")
cur("escudo_cl", "Chilean escudo", dec("escudo", "escudos", "centésimo", "centésimos"),
    [(1960, 500), (1970, 2000), (1975, 300000)], note="1960-1975. Guesses.")
cur("peso_cl", "Chilean peso", [("peso", "pesos", 1)], [(1975, 50), (1990, 1500), (2000, 5000), (2010, 9000), (2026, 25000)],
    note="New peso (1,000 escudos) from 1975. Guesses.")
cur("peso_ar_old", "Argentine peso", dec("peso", "pesos", "centavo", "centavos"),
    [(1826, 50), (1881, 100), (1900, 200), (1930, 400), (1950, 2000), (1969, 100000)],
    note="Peso fuerte and peso moneda nacional, to 1969. Guesses.")
cur("peso_ar_ley", "Argentine peso ley", dec("peso", "pesos", "centavo", "centavos"), [(1970, 1000), (1982, 2000000)],
    note="1970-1983 (roughly).")
cur("peso_ar_83", "Argentine peso argentino", dec("peso", "pesos", "centavo", "centavos"), [(1983, 3000), (1985, 50000)],
    note="1983-1985 (roughly).")
cur("austral", "Argentine austral", dec("austral", "australes", "centavo", "centavos"), [(1985, 300), (1991, 10000000)],
    note="1985-1991 (the hyperinflation roughly).")
cur("peso_ar", "Argentine peso", dec("peso", "pesos", "centavo", "centavos"),
    [(1992, 1500), (2001, 1500), (2010, 6000), (2020, 50000), (2026, 2500000)],
    note="Convertible peso from 1992 (10,000 australes); the later inflation roughly. Guesses.")
cur("peso_uy_old", "Uruguayan peso", dec("peso", "pesos", "centésimo", "centésimos"),
    [(1862, 50), (1950, 500), (1974, 100000)], note="1862-1975. Guesses.")
cur("peso_uy_nuevo", "Uruguayan nuevo peso", dec("nuevo peso", "nuevos pesos", "centésimo", "centésimos"),
    [(1975, 300), (1992, 50000)], note="1975-1993. Guesses.")
cur("peso_uy", "Uruguayan peso", dec("peso", "pesos", "centésimo", "centésimos"),
    [(1993, 5000), (2010, 30000), (2026, 100000)], note="From 1993 (1,000 nuevos pesos). Guesses.")
cur("peso_py", "Paraguayan peso", dec("peso", "pesos", "centavo", "centavos"), [(1856, 30), (1900, 200), (1942, 5000)],
    note="1856-1943. Guesses.")
cur("guarani", "Paraguayan guaraní", [("guaraní", "guaraníes", 1)], [(1943, 50), (1980, 1000), (2000, 20000), (2026, 120000)],
    note="From 1943 (100 pesos). Guesses.")
cur("real_br", "Brazilian real (réis)", [("conto", "contos", 1000000, 1850), ("mil-réis", "mil-réis", 1000),
                                         ("tostão", "tostões", 100), ("vintém", "vinténs", 20), ("real", "réis", 1)],
    [(1532, 20), (1700, 100), (1800, 320), (1850, 1000), (1900, 2000), (1930, 5000), (1941, 8000)],
    note="Colonial and imperial reis to 1942: the mil-reis of 1,000 reis, the conto of 1,000 mil-reis. Guesses.")
cur("cruzeiro_42", "Brazilian cruzeiro", dec("cruzeiro", "cruzeiros", "centavo", "centavos"),
    [(1942, 1000), (1960, 20000), (1966, 150000)], note="1942-1967 (1 mil-reis). Guesses.")
cur("cruzeiro_novo", "Brazilian cruzeiro novo", dec("cruzeiro novo", "cruzeiros novos", "centavo", "centavos"),
    [(1967, 200), (1970, 500)], note="1967-1970 (1,000 cruzeiros). Guesses.")
cur("cruzeiro_70", "Brazilian cruzeiro", dec("cruzeiro", "cruzeiros", "centavo", "centavos"),
    [(1970, 500), (1980, 10000), (1985, 1000000)], note="1970-1986. Guesses.")
cur("cruzado", "Brazilian cruzado", dec("cruzado", "cruzados", "centavo", "centavos"), [(1986, 3000), (1988, 100000)],
    note="1986-1989 (1,000 cruzeiros). Guesses.")
cur("cruzado_novo", "Brazilian cruzado novo", dec("cruzado novo", "cruzados novos", "centavo", "centavos"),
    [(1989, 300), (1990, 3000)], note="1989-1990 (1,000 cruzados). Guesses.")
cur("cruzeiro_90", "Brazilian cruzeiro", dec("cruzeiro", "cruzeiros", "centavo", "centavos"), [(1990, 3000), (1992, 500000)],
    note="1990-1993 (at par with the cruzado novo). Guesses.")
cur("cruzeiro_real", "Brazilian cruzeiro real", dec("cruzeiro real", "cruzeiros reais", "centavo", "centavos"),
    [(1993, 2000), (1994, 800000)], note="1993-1994 (1,000 cruzeiros). Guesses.")
cur("real_br_new", "Brazilian real", dec("real", "reais", "centavo", "centavos"),
    [(1994, 300), (2000, 700), (2010, 2500), (2020, 5000), (2026, 7000)], note="From 1 July 1994 (2,750 cruzeiros"
                                                                             " reais). Guesses.")
cur("dollar_gy", "Guyanese dollar", dec("dollar", "dollars", "cent", "cents"), [(1839, 30), (1965, 300), (2000, 50000), (2026, 300000)],
    note="British Guiana and Guyana dollar. Guesses.")
cur("guilder_sr", "Surinamese guilder", dec("guilder", "guilders", "cent", "cents"), [(1940, 100), (1980, 1000), (2003, 300000)],
    note="1940-2003 (the Dutch guilder before). Guesses.")
cur("dollar_sr", "Surinamese dollar", dec("dollar", "dollars", "cent", "cents"), [(2004, 1000), (2026, 30000)],
    note="From 2004 (1,000 guilders). Guesses.")
cur("pound_fk", "Falkland Islands pound", dec("pound", "pounds", "penny", "pence"), [(1971, 300), (2026, 10000)],
    note="At par with sterling. Guesses.")

row("americas_barter_rest", "barter", 1800, 2100, bx([-56, -170, 72, -34.5]), 5,
    note="Where no ruler of the register is known after 1800 (the Plains, the Amazon, Patagonia, the Arctic).")
row("hudson_bay", "made_beaver", 1670, 1870, bx(RUPERTS_LAND), 12)
row("new_france", "livre", 1608, 1763, [ru("New France"), bx(CANADA_EAST)], 31)
row("canada_pound", "pound_ca", 1764, 1857, [rb(["British Colonial Empire", "English Colonial Empire"], CANADA_EAST)], 41)
row("canada_dollar", "cad", 1858, 2100, [ru("Canada"), rb("British Colonial Empire", CANADA)], 45)
row("newfoundland", "cad", 1865, 2100, bx(NEWFOUNDLAND), 32)
row("alaska_ruble", "ruble", 1799, 1866, bx(ALASKA), 32, note="Russian America: rubles and company scrip.")
row("alaska_dollar", "dollar", 1867, 2100, [bx(ALASKA), rb("United States of America", NORTH_AMERICA)], 32)
row("usa_rulers", "dollar", 1792, 2100, rb(["United States of America", "Confederate States of America", "Republic of Texas",
                                            "Republic of Hawai'i"], NORTH_AMERICA), 44)
row("hawaii_dollar", "dollar_hi", 1847, 1897, bx(HAWAII), 45)
row("hawaii_usd", "dollar", 1898, 2100, bx(HAWAII), 45)
row("mx_real", "peso_mx_real", 1822, 1862, [ru("First Mexican Empire", "Federated Republic of Mexico", "Centralist Mexico",
                                              "Mexicans"), bx(MEXICO)], 42)
row("mx_peso", "peso_mx", 1863, 1992, [ru("Second Mexican Empire", "Mexican Monarchists", "Mexico", "Federated Republic of Mexico",
                                         "Maderistas"), bx(MEXICO)], 42)
row("mx_peso_new", "peso_mx_new", 1993, 2100, [ru("Mexico"), bx(MEXICO)], 42)
row("ca_peso", "peso_ca", 1823, 1924, [ru("United Provinces of Central America", "Guatemala", "Honduras",
                                         "Republic of El Salvador", "Republic of Nicaragua", "Republic of Costa Rica"),
                                      bx(CENTRAL_AM)], 40)
row("gt_quetzal", "quetzal", 1925, 2100, [ru("Guatemala"), bx(GUATEMALA)], 45)
row("sv_colon", "colon_sv", 1919, 2000, [ru("Republic of El Salvador"), bx(EL_SALVADOR)], 46)
row("sv_usd", "dollar", 2001, 2100, [ru("Republic of El Salvador"), bx(EL_SALVADOR)], 46, pay=[(2001, 500), (2026, 1300)])
row("hn_lempira", "lempira", 1931, 2100, [ru("Honduras"), bx(HONDURAS)], 45)
row("ni_cordoba", "cordoba", 1912, 2100, [ru("Republic of Nicaragua"), bx(NICARAGUA)], 45)
row("cr_colon", "colon_cr", 1896, 2100, [ru("Republic of Costa Rica"), bx(COSTA_RICA)], 46)
row("pa_colombia", "peso_co", 1821, 1903, bx(PANAMA), 41)
row("pa_balboa", "balboa", 1904, 2100, [ru("Republic of Panama"), bx(PANAMA)], 46)
row("bz_dollar", "bz_dollar", 1885, 2100, [ru("Belize"), bx(BELIZE)], 47)
row("cu_peso", "peso_cu", 1857, 2100, [ru("Republic of Cuba", "Communist Cuba", "Cuban Nationalists", "Cuban Communists"),
                                      bx(CUBA)], 45)
row("ht_gourde", "gourde", 1813, 2100, [ru("Haiti", "Empire of Haiti", "Republic of Haiti"), bx(HISPANIOLA_W)], 45)
row("do_peso", "peso_do", 1844, 2100, [ru("Dominican Republic"), bx(HISPANIOLA_E)], 45)
row("jm_pound", "pound_jm", 1840, 1968, bx(JAMAICA), 44)
row("jm_dollar", "dollar_jm", 1969, 2100, [ru("Jamaica"), bx(JAMAICA)], 46)
row("pr_peso", "peso_real", 1500, 1899, bx(PUERTO_RICO), 33)
row("pr_usd", "dollar", 1900, 2100, bx(PUERTO_RICO), 46, pay=[(1900, 50), (1950, 300), (2000, 4000), (2026, 6000)])
row("bs_sterling", "pound_lsd", 1700, 1965, bx(BAHAMAS), 40, pay=[(1700, 8), (1900, 96), (1965, 1000)])
row("bs_dollar", "bsd", 1966, 2100, [ru("Commonwealth of The Bahamas"), bx(BAHAMAS)], 46)
row("caribbean_sterling", "pound_lsd", 1840, 1934, bx(LESSER_ANTILLES), 38, pay=[(1840, 24), (1934, 72)])
row("caribbean_bwi", "dollar_bwi", 1935, 1964, bx(LESSER_ANTILLES), 38)
row("caribbean_xcd", "xcd", 1965, 2100, [ru("Antigua and Barbuda", "Commonwealth of Dominica", "Grenada", "Saint Lucia",
                                           "Saint Vincent", "Saint Kitts"), bx(LESSER_ANTILLES)], 44)
row("bb_dollar", "bbd", 1973, 2100, ru("Barbados"), 46)
row("tt_dollar", "ttd", 1964, 2100, [ru("Republic of Trinidad and Tobago"), bx(TRINIDAD)], 46)
row("fr_antilles_franc", "franc", 1815, 1959, bx(FR_ANTILLES), 45, pay=[(1815, 60), (1900, 150), (1950, 20000)])
row("fr_antilles_new_franc", "new_franc", 1960, 2001, bx(FR_ANTILLES), 45, pay=[(1960, 700), (1980, 6000), (2001, 25000)])
row("fr_antilles_euro", EURO, 2002, 2100, bx(FR_ANTILLES), 45)
row("an_guilder", "ang", 1828, 2100, [ru("Netherlands Antilles"), bx(ABC)], 46)
row("caribbean_spanish", "peso_real", 1500, 1856, [bx(CUBA), bx(HISPANIOLA_E)], 33)
row("caribbean_colonies", "pound_lsd", 1650, 1839, [bx(JAMAICA), bx(LESSER_ANTILLES)], 32, pay=[(1650, 8), (1839, 24)])
row("co_peso", "peso_co", 1810, 2100, [ru("New Granada", "Republic of New Granada", "Granadine Confederation",
                                         "United States of Colombia", "Republic of Colombia", "Gran Colombia"),
                                      bx(COLOMBIA)], 42)
row("ve_peso", "peso_co", 1811, 1878, [ru("Republic of Venezuela", "Venezuela"), bx(VENEZUELA)], 42)
row("ve_bolivar", "bolivar", 1879, 2007, [ru("Venezuela"), bx(VENEZUELA)], 44)
row("ve_bolivar_fuerte", "bolivar_fuerte", 2008, 2017, [ru("Venezuela"), bx(VENEZUELA)], 44)
row("ve_bolivar_soberano", "bolivar_soberano", 2018, 2020, [ru("Venezuela"), bx(VENEZUELA)], 44)
row("ve_bolivar_digital", "bolivar_digital", 2021, 2100, [ru("Venezuela"), bx(VENEZUELA)], 44)
row("ec_peso", "peso_co", 1822, 1883, [ru("Republic of Ecuador"), bx(ECUADOR)], 44)
row("ec_sucre", "sucre", 1884, 1999, [ru("Republic of Ecuador"), bx(ECUADOR)], 45)
row("ec_usd", "dollar", 2000, 2100, [ru("Republic of Ecuador"), bx(ECUADOR)], 45, pay=[(2000, 400), (2026, 1800)])
row("pe_peso", "peso_real", 1822, 1862, [ru("Republic of Peru", "Peru-Bolivian Confederation"), bx(PERU)], 44)
row("pe_sol", "sol_pe", 1863, 1984, [ru("Republic of Peru"), bx(PERU)], 45)
row("pe_inti", "inti", 1985, 1990, [ru("Republic of Peru"), bx(PERU)], 45)
row("pe_sol_new", "sol_pe_new", 1991, 2100, [ru("Republic of Peru"), bx(PERU)], 45)
row("bo_sol", "peso_real", 1825, 1863, [ru("Bolivia"), bx(BOLIVIA)], 43)
row("bo_boliviano_old", "boliviano_old", 1864, 1962, [ru("Bolivia"), bx(BOLIVIA)], 44)
row("bo_peso", "peso_bo", 1963, 1986, [ru("Bolivia"), bx(BOLIVIA)], 44)
row("bo_boliviano", "boliviano", 1987, 2100, [ru("Bolivia"), bx(BOLIVIA)], 44)
row("cl_peso_old", "peso_cl_old", 1817, 1959, [ru("Republic of Chile"), bx(CHILE)], 44)
row("cl_escudo", "escudo_cl", 1960, 1974, [ru("Republic of Chile"), bx(CHILE)], 44)
row("cl_peso", "peso_cl", 1975, 2100, [ru("Republic of Chile"), bx(CHILE)], 44)
row("plata_spanish", "peso_real", 1580, 1825, [bx(RIO_PLATA), ru("Río de la Plata", "Jesuit Reducciones")], 26)
row("ar_peso_old", "peso_ar_old", 1826, 1969, [ru("Río de la Plata", "Argentine Confederation", "Argentine Republic"),
                                               bx(ARGENTINA)], 43)
row("ar_peso_ley", "peso_ar_ley", 1970, 1982, [ru("Argentine Republic"), bx(ARGENTINA)], 43)
row("ar_peso_83", "peso_ar_83", 1983, 1984, [ru("Argentine Republic"), bx(ARGENTINA)], 43)
row("ar_austral", "austral", 1985, 1991, [ru("Argentine Republic"), bx(ARGENTINA)], 43)
row("ar_peso", "peso_ar", 1992, 2100, [ru("Argentine Republic"), bx(ARGENTINA)], 43)
row("uy_peso_old", "peso_uy_old", 1862, 1974, [ru("Oriental Republic of Uruguay"), bx(URUGUAY)], 46)
row("uy_peso_nuevo", "peso_uy_nuevo", 1975, 1992, [ru("Oriental Republic of Uruguay"), bx(URUGUAY)], 46)
row("uy_peso", "peso_uy", 1993, 2100, [ru("Oriental Republic of Uruguay"), bx(URUGUAY)], 46)
row("uy_spanish", "peso_real", 1826, 1861, [ru("Oriental Republic of Uruguay"), bx(URUGUAY)], 46)
row("py_spanish", "peso_real", 1811, 1855, [ru("Paraguay"), bx(PARAGUAY)], 45)
row("py_peso", "peso_py", 1856, 1942, [ru("Paraguay"), bx(PARAGUAY)], 45)
row("py_guarani", "guarani", 1943, 2100, [ru("Paraguay"), bx(PARAGUAY)], 45)
row("br_colony", "real_br", 1532, 1821, [rb("Portuguese Empire", BRAZIL), bx(BRAZIL_COAST)], 27)
row("br_reis", "real_br", 1822, 1941, [ru("Empire of Brazil", "Brazilian Republic", "Unitary State of Brazil")], 43)
row("br_cruzeiro_42", "cruzeiro_42", 1942, 1966, ru("Brazilian Republic", "Unitary State of Brazil"), 43)
row("br_cruzeiro_novo", "cruzeiro_novo", 1967, 1969, ru("Federated Republic of Brazil", "Brazilian Republic"), 43)
row("br_cruzeiro_70", "cruzeiro_70", 1970, 1985, ru("Federated Republic of Brazil"), 43)
row("br_cruzado", "cruzado", 1986, 1988, ru("Federated Republic of Brazil", "Republic of Brazil"), 43)
row("br_cruzado_novo", "cruzado_novo", 1989, 1989, ru("Republic of Brazil"), 43)
row("br_cruzeiro_90", "cruzeiro_90", 1990, 1992, ru("Republic of Brazil"), 43)
row("br_cruzeiro_real", "cruzeiro_real", 1993, 1993, ru("Republic of Brazil"), 43)
row("br_real", "real_br_new", 1994, 2100, ru("Republic of Brazil"), 43)
row("br_box_reis", "real_br", 1822, 1941, bx(BRAZIL), 24)
row("br_box_real", "real_br_new", 1994, 2100, bx(BRAZIL), 24)
row("gy_dollar", "dollar_gy", 1839, 2100, [ru("Guyana"), bx(GUYANA)], 45)
row("sr_dutch", "guilder_nl", 1817, 1939, bx(SURINAME), 44, pay=[(1817, 20), (1939, 60)])
row("sr_guilder", "guilder_sr", 1940, 2003, [ru("Republic of Suriname"), bx(SURINAME)], 46)
row("sr_dollar", "dollar_sr", 2004, 2100, [ru("Republic of Suriname"), bx(SURINAME)], 46)
row("gf_franc", "franc", 1817, 1959, bx(FR_GUIANA), 45, pay=[(1817, 60), (1900, 150), (1950, 20000)])
row("gf_new_franc", "new_franc", 1960, 2001, bx(FR_GUIANA), 45, pay=[(1960, 700), (1980, 6000), (2001, 25000)])
row("gf_euro", EURO, 2002, 2100, bx(FR_GUIANA), 45)
row("fk_sterling", "pound_lsd", 1833, 1970, bx(FALKLANDS), 46)
row("fk_pound", "pound_fk", 1971, 2100, bx(FALKLANDS), 46)

rate("peso_mx", 100000, "peso_mx_new", 100, 1993, 2100, "1,000 old pesos = 1 new.")
rate("real_br", 1000, "cruzeiro_42", 100, 1942, 1966, "1 mil-reis = 1 cruzeiro (1942).")
rate("cruzeiro_42", 100000, "cruzeiro_novo", 100, 1967, 1969, "1,000 cruzeiros = 1 cruzeiro novo.")
rate("cruzeiro_novo", 100, "cruzeiro_70", 100, 1970, 1985, "Renamed at par.")
rate("cruzeiro_70", 100000, "cruzado", 100, 1986, 1988, "1,000 cruzeiros = 1 cruzado.")
rate("cruzado", 100000, "cruzado_novo", 100, 1989, 1989, "1,000 cruzados = 1 cruzado novo.")
rate("cruzado_novo", 100, "cruzeiro_90", 100, 1990, 1992, "Renamed at par.")
rate("cruzeiro_90", 100000, "cruzeiro_real", 100, 1993, 1993, "1,000 cruzeiros = 1 cruzeiro real.")
rate("cruzeiro_real", 275000, "real_br_new", 100, 1994, 2100, "2,750 cruzeiros reais = 1 real.")
rate("peso_ar_old", 10000, "peso_ar_ley", 100, 1970, 2100, "100 pesos m$n = 1 peso ley.")
rate("peso_ar_ley", 1000000, "peso_ar_83", 100, 1983, 2100, "10,000 pesos ley = 1 peso argentino.")
rate("peso_ar_83", 100000, "austral", 100, 1985, 2100, "1,000 pesos argentinos = 1 austral.")
rate("austral", 1000000, "peso_ar", 100, 1992, 2100, "10,000 australes = 1 peso.")
rate("sol_pe", 100000, "inti", 100, 1985, 2100, "1,000 soles = 1 inti.")
rate("inti", 100000000, "sol_pe_new", 100, 1991, 2100, "1,000,000 intis = 1 nuevo sol.")
rate("peso_cl_old", 100000, "escudo_cl", 100, 1960, 2100, "1,000 pesos = 1 escudo.")
rate("escudo_cl", 100000, "peso_cl", 1, 1975, 2100, "1,000 escudos = 1 new peso.")
rate("peso_uy_old", 100000, "peso_uy_nuevo", 100, 1975, 2100, "1,000 pesos = 1 nuevo peso.")
rate("peso_uy_nuevo", 100000, "peso_uy", 100, 1993, 2100, "1,000 nuevos pesos = 1 peso.")
rate("peso_bo", 100000000, "boliviano", 100, 1987, 2100, "1,000,000 pesos = 1 boliviano.")
rate("peso_py", 10000, "guarani", 1, 1943, 2100, "100 pesos = 1 guarani.")
rate("bolivar", 100000, "bolivar_fuerte", 100, 2008, 2100, "1,000 bolivares = 1 bolivar fuerte.")
rate("bolivar_fuerte", 10000000, "bolivar_soberano", 100, 2018, 2100, "100,000 fuertes = 1 soberano.")
rate("bolivar_soberano", 100000000, "bolivar_digital", 100, 2021, 2100, "1,000,000 soberanos = 1 digital.")
rate("guilder_sr", 100000, "dollar_sr", 100, 2004, 2100, "1,000 guilders = 1 dollar.")
rate("dollar", 100, "balboa", 100, 1904, 2100, "At par.")
rate("dollar", 100, "bsd", 100, 1966, 2100, "At par.")
rate("dollar", 100, "dollar_hi", 100, 1847, 1898, "At par.")
rate("pound_ca", 960, "cad", 400, 1858, 1870, "1 Halifax pound = 4 dollars.")


# ==============================================================================================================
# OCEANIA AND THE ARCTIC
# ==============================================================================================================
AUSTRALIA = [-44, 112, -10, 154]
NEW_ZEALAND = [-47.5, 166, -34, 179]
PNG = [-11.7, 140.8, -1, 156]
FIJI = [-19.3, 177, -12.4, 180]
NEW_CALEDONIA = [-22.8, 163.5, -19.5, 168.2]
VANUATU = [-20.3, 166.5, -13, 170.3]
SOLOMONS = [-11.9, 155.5, -6.5, 162.8]
PACIFIC_W = [-50, 110, 30, 180]
PACIFIC_E = [-50, -180, 30, -100]
FR_POLYNESIA = [-28, -155, -7, -134]
SAMOA_TONGA = [-22.5, -176, -13, -168]
ARCTIC = [60, -180, 90, 180]

cur("aud_pound", "Australian pound", [("pound", "pounds", 960), ("shilling", "shillings", 48), ("penny", "pence", 4),
                                      ("farthing", "farthings", 1)],
    [(1910, 480), (1930, 480), (1950, 1200), (1965, 2400)], note="1910-1965 (at par with sterling to 1931). Guesses.")
cur("aud", "Australian dollar", dec("dollar", "dollars", "cent", "cents"),
    [(1966, 500), (1980, 3000), (1990, 7000), (2000, 10000), (2010, 15000), (2026, 25000)], note="From 1966.")
cur("nzd_pound", "New Zealand pound", [("pound", "pounds", 960), ("shilling", "shillings", 48), ("penny", "pence", 4),
                                       ("farthing", "farthings", 1)],
    [(1933, 480), (1950, 1200), (1966, 2400)], note="1933-1967. Guesses.")
cur("nzd", "New Zealand dollar", dec("dollar", "dollars", "cent", "cents"),
    [(1967, 500), (1990, 6000), (2010, 12000), (2026, 20000)], note="From 1967. Guesses.")
cur("kina", "Papua New Guinean kina", dec("kina", "kina", "toea", "toea"), [(1975, 300), (2000, 1000), (2026, 4000)],
    note="From 1975. Guesses.")
cur("fjd", "Fijian dollar", dec("dollar", "dollars", "cent", "cents"), [(1969, 300), (2000, 1500), (2026, 4000)],
    note="From 1969 (the Fijian pound before). Guesses.")
cur("cfp_franc", "CFP franc", [("franc", "francs", 1)], [(1945, 100), (1980, 1500), (2000, 5000), (2026, 9000)],
    note="French Pacific franc from 1945. Guesses.")
cur("vatu", "Vanuatu vatu", [("vatu", "vatu", 1)], [(1981, 500), (2026, 3000)], note="From 1981. Guesses.")
cur("sbd", "Solomon Islands dollar", dec("dollar", "dollars", "cent", "cents"), [(1977, 200), (2026, 10000)],
    note="From 1977. Guesses.")
cur("tala", "Samoan tala", dec("tālā", "tālā", "sene", "sene"), [(1967, 200), (2026, 5000)], note="From 1967.")
cur("paanga", "Tongan paʻanga", dec("paʻanga", "paʻanga", "seniti", "seniti"), [(1967, 200), (2026, 5000)],
    note="From 1967.")

row("au_sterling_early", "pound_lsd", 1788, 1824, [bx([-38.5, 147, -27, 154]), bx([-43.7, 144.5, -40.5, 148.5])], 21,
    note="The first colonies: New South Wales and Van Diemen's Land.")
row("au_north_barter", "barter", 1788, 1869, bx([-26, 112, -10, 154]), 21,
    note="The north and the interior stayed Aboriginal country long after 1788.")
row("au_pound", "aud_pound", 1910, 1965, [ru("Commonwealth of Australia"), bx(AUSTRALIA)], 44)
row("au_dollar", "aud", 1966, 2100, [ru("Commonwealth of Australia"), bx(AUSTRALIA)], 44)
row("nz_barter", "barter", -100000, 1839, bx(NEW_ZEALAND), 31)
row("nz_sterling", "pound_lsd", 1840, 1932, bx(NEW_ZEALAND), 31)
row("nz_pound", "nzd_pound", 1933, 1966, [ru("New Zealand"), bx(NEW_ZEALAND)], 45)
row("nz_dollar", "nzd", 1967, 2100, [ru("New Zealand"), bx(NEW_ZEALAND)], 45)
row("pg_mark", "mark", 1884, 1914, rb("German Africa", PNG), 41, pay=[(1884, 30), (1914, 60)])
row("pg_aud_pound", "aud_pound", 1915, 1965, bx(PNG), 33, pay=[(1906, 16), (1965, 240)])
row("pg_aud", "aud", 1966, 1974, bx(PNG), 33, pay=[(1966, 100), (1980, 300)])
row("pg_kina", "kina", 1975, 2100, [ru("Papua New Guinea"), bx(PNG)], 45)
row("fj_sterling", "pound_lsd", 1874, 1968, [ru("Kingdom of Fiji"), bx(FIJI)], 41, pay=[(1874, 24), (1968, 300)])
row("fj_dollar", "fjd", 1969, 2100, [ru("Republic of Fiji"), bx(FIJI)], 45)
row("nc_franc", "franc", 1853, 1944, [ru("New Caledonia"), bx(NEW_CALEDONIA)], 41, pay=[(1853, 60), (1900, 150), (1944, 2000)])
row("nc_cfp", "cfp_franc", 1945, 2100, [bx(NEW_CALEDONIA), bx(FR_POLYNESIA)], 46)
row("vu_mixed", "aud_pound", 1906, 1965, [ru("New Hebrides"), bx(VANUATU)], 41, pay=[(1906, 16), (1965, 240)])
row("vu_aud", "aud", 1966, 1980, [ru("New Hebrides"), bx(VANUATU)], 41, pay=[(1966, 100), (1980, 300)])
row("vu_vatu", "vatu", 1981, 2100, [ru("Vanuatu"), bx(VANUATU)], 46)
row("sb_sterling", "pound_lsd", 1899, 1909, bx(SOLOMONS), 33, pay=[(1899, 16), (1909, 16)])
row("sb_aud", "aud_pound", 1910, 1965, bx(SOLOMONS), 33, pay=[(1906, 16), (1965, 240)])
row("sb_aud2", "aud", 1966, 1976, bx(SOLOMONS), 33, pay=[(1966, 100), (1980, 300)])
row("sb_dollar", "sbd", 1977, 2100, [ru("Solomon Islands"), bx(SOLOMONS)], 46)
row("ws_to_tala", "tala", 1967, 2100, bx(SAMOA_TONGA), 40)
row("pf_franc", "franc", 1880, 1944, bx(FR_POLYNESIA), 40, pay=[(1880, 60), (1900, 150), (1944, 2000)])
row("micronesia_usd", "dollar", 1944, 2100, ru("Micronesia", "Palau"), 46, pay=[(1950, 100), (2026, 4000)])
row("pacific_barter_w", "barter", -100000, 2100, bx(PACIFIC_W), 4)
row("pacific_barter_e", "barter", -100000, 2100, bx(PACIFIC_E), 4)
row("arctic_barter", "barter", -100000, 2100, bx(ARCTIC), 4)
row("north_asia_barter_late", "barter", 1600, 2100, bx([55, 40, 78, 180]), 6)
rate("aud_pound", 960, "aud", 200, 1966, 2100, "1 pound = 2 dollars (1966).")
rate("nzd_pound", 960, "nzd", 200, 1967, 2100, "1 pound = 2 dollars (1967).")
rate("pound_lsd", 960, "aud_pound", 960, 1910, 1930, "At par until 1931.")
rate("pound_lsd", 960, "aud_pound", 1200, 1931, 1965, "1 pound sterling = 1.25 Australian pounds (1931).")


# ==============================================================================================================
# GAPS FOUND BY worldfill/money_coverage.py (step 23a, second pass)
# ==============================================================================================================
TARIM = [35, 73, 43, 97.5]
TIBET_PLATEAU = [27.3, 73.5, 37, 104]
SAHARA_N = [23, -18, 33, 35]
STEPPE_WEST = [44, 25, 55, 45]

row("yuan", "china_cash", 1271, 1368, ru("Yuan Dynasty"), 40, note="Yuan paper money and cash, also in Mongolia.")
row("chinese_dynasties", "china_cash", -221, 1279, ru("Qin Dynasty", "Han Dynasty", "Xin Dynasty", "Cao Wei", "Shu Han",
                                                      "Eastern Wu", "Western Jin", "Northern Wei", "Eastern Wei",
                                                      "Western Wei", "Northern Qi", "Northern Zhou", "Sui Dynasty",
                                                      "Tang Dynasty", "Liu Song Dynasty", "Southern Qi",
                                                      "Liang Dynasty", "Chen Dynasty",
                                                      "Protectorate of the Western Regions"), 40)
row("tarim_barter", "barter", -100000, -201, bx(TARIM), 18)
row("tarim_cash", "china_cash", -200, 1499, bx(TARIM), 18,
    note="The oasis kingdoms of the Tarim used Chinese and Sino-Kharosthi coins and bolts of cloth.")
row("kara_khanid", "dirham", 850, 1212, ru("Kara-Khanids", "Eastern Kara-Khanids", "Western Karakhanid Khanate"), 41)
row("tibet_barter", "barter", -100000, 1362, bx(TIBET_PLATEAU), 15,
    note="Barley, salt, tea and wool were swapped on the plateau before the tangka.")
row("tuyuhun_barter", "barter", 287, 665, ru("Tuyuhun"), 41)
row("media_silver", "silver_weighed", -650, -551, ru("Median Kingdom"), 31)
row("atropatene", "drachma", -323, -31, ru("Atropatene"), 36)
row("rus_principalities", "grivna", 1056, 1380, ru("Principality of Chernigov", "Principality of Peremyshl",
                                                    "Principality of Pereyaslavl", "Principality of Polotsky",
                                                    "Principality of Rostov-Suzdal", "Principality of Smolensk",
                                                    "Principality of Volhynia", "Principality of Terebovlia",
                                                    "Principality of Ryazan", "Principality of Drutsk",
                                                    "Principality of Minsk", "Principality of Vitebsk",
                                                    "Principality of Halych", "Principality of Turov and Pinsk",
                                                    "Principality of Beloozero", "Principality of Pinsk",
                                                    "Principality of Turov", "Tver", "Halych-Volhynia occupation"), 40)
row("rus_principalities_late", "denga", 1381, 1520, ru("Principality of Smolensk", "Tver", "Ryazan"), 40)
row("steppe_west_barter", "barter", -100000, 1924, bx(STEPPE_WEST), 6)
row("kipchak_barter", "barter", 750, 1240, ru("Kimek-Kipchak confederation", "Cuman-Kipchak Confederation"), 41,
    note="Kipchak and Cuman herders swapped livestock and furs.")
row("bulgaria_first", "solidus", 682, 1017, ru("First Bulgarian Empire"), 41)
row("maghreb_dirham", "dirham", 1501, 1669, [ru("Wattasid dynasty", "Saadi Sultanate", "Hafsid Dynasty",
                                                "Zayyanid dynasty", "Marinid Sultanate"), bx(MOROCCO)], 30)
row("libyan_desert_egp", "pound_eg", 1885, 1955, rb("British Africa", [19, 17, 30, 25]), 41)
row("sahara_n_barter", "barter", -100000, 2100, bx(SAHARA_N), 4, note="Nomads of the desert swapped goods.")
row("central_asia_barter_early", "barter", -100000, -331, bx(CENTRAL_ASIA), 8)
row("iceland_empty", "barter", -100000, 873, bx(ICELAND), 26)

AZERBAIJAN = [38.4, 44.8, 41.9, 50.6]
KAZAKHSTAN = [40.5, 46.5, 55.5, 87.4]
RUSSIA_S = [41, 36, 56, 50]
LEVANT = [31, 34, 37.5, 42.5]

row("china_dynasties_more", "china_cash", 907, 1279, ru("Liao Dynasty", "Great Jin", "Western Xia", "Northern Song",
                                                         "Southern Song", "Later Liang Dynasty", "Later Tang", "Later Jin",
                                                         "Later Han", "Later Zhou", "Northern Han", "Southern Tang",
                                                         "Southern Han", "Southern Wu", "Southern Chu", "Wuyue", "Min",
                                                         "Former Shu", "Later Shu", "Jingnan", "Qi Kingdom",
                                                         "Yan Kingdom", "Former Jin", "Ganzhou Kingdom",
                                                         "Kingdom of Dali", "Nanzhao"), 40)
row("vietnam_ngo", "van_vn", 970, 1406, ru("Ngô Dynasty"), 40)
row("manchuria_barter", "barter", -100000, 1644, bx(MANCHURIA), 6, note="Jurchen and Mongol herders and hunters.")
row("low_countries_penny", "pfennig", 800, 1499, bx(BENELUX), 24)
row("hu_nationalists_1", "gulden_kreuzer", 1849, 1856, ru("Hungarian Nationalists"), 41)
row("hu_nationalists_2", "gulden_at", 1857, 1891, ru("Hungarian Nationalists"), 41)
row("hu_nationalists_3", "krone_au", 1892, 1918, ru("Hungarian Nationalists"), 41)
row("hu_nationalists_4", "leu_ro", 1919, 1946, rb("Hungarian Nationalists", ROMANIA), 41)
row("hu_nationalists_5", "forint", 1946, 1957, rb("Hungarian Nationalists", HUNGARY), 42)
row("hu_nationalists_6", "leu_ro_1947", 1947, 1951, rb("Hungarian Nationalists", ROMANIA), 41)
row("hu_nationalists_7", "leu_ro_1952", 1952, 1957, rb("Hungarian Nationalists", ROMANIA), 41)
row("bg_1878", "lev_old", 1878, 1880, [ru("Principality of Bulgaria"), bx(BULGARIA)], 44,
    note="Russian rubles also passed until the lev of 1881.")
row("levant_akce", "akce", 1517, 1843, bx(LEVANT), 20)
row("levant_kurus", "kurus", 1844, 1918, bx(LEVANT), 20)
row("caspian_az_soviet", "ruble_su", 1922, 1960, bx(AZERBAIJAN), 33)
row("caspian_az_soviet61", "ruble_su61", 1961, 1991, bx(AZERBAIJAN), 33)
row("caspian_az_manat_old", "manat_az_old", 1992, 2005, bx(AZERBAIJAN), 33)
row("caspian_az_manat", "manat_az", 2006, 2100, bx(AZERBAIJAN), 33)
row("kz_box_soviet", "ruble_su", 1922, 1960, bx(KAZAKHSTAN), 30)
row("kz_box_soviet61", "ruble_su61", 1961, 1991, bx(KAZAKHSTAN), 30)
row("kz_box_tenge", "tenge", 1993, 2100, bx(KAZAKHSTAN), 30)
row("ru_s_box_soviet", "ruble_su", 1922, 1960, bx(RUSSIA_S), 29)
row("ru_s_box_soviet61", "ruble_su61", 1961, 1991, bx(RUSSIA_S), 29)
row("ru_s_box_ruble92", "ruble_ru92", 1992, 1997, bx(RUSSIA_S), 29)
row("ru_s_box_ruble", "ruble_ru", 1998, 2100, bx(RUSSIA_S), 29)
row("ru_s_box_imperial", "ruble", 1800, 1921, bx(RUSSIA_S), 24)

IBERIA_BIG = [27, -18.5, 44, 4.5]
MAGHREB = [27, -18, 37.5, 12]
CAUCASUS = [38, 40, 44, 51]
ESTONIA = [57.5, 21.7, 59.8, 28.3]
LATVIA = [55.6, 20.9, 58.1, 28.3]
LITHUANIA = [53.9, 20.9, 56.5, 26.9]
DANZIG = [54.2, 18.4, 54.5, 18.9]

cur("gulden_dz", "Danzig gulden", dec("gulden", "gulden", "pfennig", "pfennigs"), [(1923, 500), (1939, 600)],
    note="Free City of Danzig, 1923-1939. Guesses.")
row("spain_peso_ruler", "peso_real", 1497, 1868, rb("Kingdom of Spain", IBERIA_BIG), 31)
row("asturias_leon", "maravedi_cas", 718, 1235, ru("Kingdom of Asturias", "Kingdom of Pamplona", "Kingdom of Galicia",
                                                   "Kingdom of León"), 31)
row("syrmia", "dinar_rs_med", 1282, 1325, ru("Kingdom of Syrmia"), 41)
row("romania_denar", "denar_hu", 1000, 1459, bx(ROMANIA), 22)
row("danzig_mark", "mark", 1920, 1922, [ru("Free City of Danzig"), bx(DANZIG)], 47)
row("danzig_gulden", "gulden_dz", 1923, 1939, [ru("Free City of Danzig"), bx(DANZIG)], 47)
row("asturias_galicia_box", "maravedi_cas", 900, 1496, bx([41.8, -9.4, 43.8, -4.5]), 23)
row("maghreb_barter", "barter", -100000, -147, bx(MAGHREB), 8)
row("west_africa_barter", "barter", -100000, 999, bx(WEST_AFRICA_BIG), 8)
row("georgia_toman", "toman", 1501, 1800, ru("Kingdom of Georgia", "Kingdom of Kartli", "Kingdom of Kakheti",
                                            "Khanates of the Caucasus"), 41,
    note="Persian abbasis were struck at Tiflis.")
row("georgia_west_akce", "akce", 1468, 1843, ru("Kingdom of Imereti", "Principality of Abkhazia", "Principality of Guria",
                                                "Principality of Mingrelia"), 41)
row("adiabene", "drachm_persian", -63, 370, ru("Kingdom of Adiabene"), 41)
row("iran_seleucid_gap", "drachma", -330, -248, [bx(IRAN), bx(MESOPOTAMIA)], 28)
row("caucasus_drachma", "drachma", -330, -31, bx(CAUCASUS), 18)
row("armenia_hellenistic", "drachma", -326, -248, ru("Kingdom of Armenia"), 36)
row("habsburg_pfennig", "pfennig", 1260, 1499, ru("House of Habsburg"), 41)
row("baltic_soviet", "ruble_su", 1941, 1960, bx(BALTIC), 28)
row("baltic_soviet61", "ruble_su61", 1961, 1991, bx(BALTIC), 28)
row("ee_box_kroon", "kroon", 1992, 2010, bx(ESTONIA), 30)
row("ee_box_euro", EURO, 2011, 2100, bx(ESTONIA), 30, pay=PAY_EURO_EE)
row("lv_box_lats", "lats", 1993, 2013, bx(LATVIA), 29)
row("lv_box_euro", EURO, 2014, 2100, bx(LATVIA), 29, pay=PAY_EURO_LV)
row("lt_box_litas", "litas", 1993, 2014, bx(LITHUANIA), 29)
row("lt_box_euro", EURO, 2015, 2100, bx(LITHUANIA), 29, pay=PAY_EURO_LT)

# Border cities the register's half-degree cells give to the neighbour
GENEVA = [46.13, 5.95, 46.37, 6.31]
BASEL = [47.51, 7.55, 47.6, 7.7]
row("geneva_gulden", "gulden_kreuzer", 1536, 1849, [bx(GENEVA), bx(BASEL)], 70)
row("geneva_franc", "franc_ch", 1850, 2100, [bx(GENEVA), bx(BASEL)], 70)

rate("sucre", 2500000, "dollar", 100, 2000, 2100, "25,000 sucres = 1 US dollar (2000).")
rate("colon_sv", 875, "dollar", 100, 2001, 2100, "8.75 colones = 1 US dollar (2001).")
rate("kroon", 156466, EURO, 10000, 2011, 2100, "15.6466 krooni = 1 euro.")
rate("lats", 702804, EURO, 1000000, 2014, 2100, "0.702804 lats = 1 euro.")
rate("litas", 345280, EURO, 100000, 2015, 2100, "3.4528 litai = 1 euro.")

# Sakhalin, the Kurils and southern Kamchatka between the Manchuria and Siberia boxes (Ainu, Nivkh, Itelmen)
row("sakhalin_barter", "barter", -100000, 2100, bx([42, 135.2, 62, 165]), 4)
