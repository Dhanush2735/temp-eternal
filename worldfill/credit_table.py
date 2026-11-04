"""
Step 44 part 8 (E19): banking and credit — what it costs to borrow, who lends, and whether it
is lawful.

The survey for this step was short and bleak: `find` for Bank, Credit or Loan returns **no file**.
There is no bank, no lender, no loan, no interest and no bill of exchange anywhere in the mod. The
money-changer is there (step 19a) and changes coin at a fee — which is a bank's oldest function
with the lending left out.

So this is written by hand, because the numbers are scattered through the literature and no single
dataset carries them. Every row names the source it came from and whether it is **recorded**
(a rate a document states), **measured** (worked out from many records, like the Ottoman waqf
returns) or **estimated** (inferred). That mark is not decoration: the Ottoman and English rows are
solid enough to lean on, and the African and Andean rows are not, and a player is entitled to know
which is which.

Two things this table is careful about.

**It is not a European table.** Part 2 of this step bought its prices from Allen–Unger and had to
record that the source is European and Indian and stops in 1914. Credit has the same bias in the
literature and worse. So the Islamic world, India and China are here with dated figures, and where
a whole region genuinely has no rate — the Inca had no money at all, and pre-colonial West Africa
ran on cowries, pawnship and rotating savings clubs rather than on a price for credit — **the
absence is recorded as a fact rather than filled with a guess**.

**A ban on interest is not the absence of credit.** Where `lawful` is false, credit did not stop:
it was restructured. The Ottomans ran cash waqfs, Islamic lenders use cost-plus sale (murabaha)
and legal stratagems (hiyal), and Buddhist monasteries in China ran pawnshops. Every row that says
interest is not lawful also says what was done instead, because "no lending here" would be the one
answer that is certainly wrong.
"""

# A rate, as the mod carries it.
#
#   id          a name for the row
#   boxes       [latMin, latMax, lonMin, lonMax], the same shape Beliefs uses
#   from, to    the years it holds
#   low, high   the rate, per cent a year. Equal when one figure is known.
#               None when the region has no price for credit at all.
#   kind        what the loan is: silver, grain, commercial, maritime, state,
#               deposit, pawn, mortgage, rosus (a rotating savings club),
#               bill (the discount on a bill of exchange)
#   lender      who lends: temple, monastery, money-changer, bank, goldsmith,
#               waqf, sarraf, pawnshop, kinship, state, none
#   lawful      whether charging interest is permitted here:
#               True, False, or "capped" (permitted up to a legal maximum)
#   instead     what is done where interest is not lawful, or where there is no
#               price for credit at all
#   mark        recorded | measured | estimated
#   note        what the number means
#   source      where it came from

RATES = [
    # ------------------------------------------------------------------ the first credit
    dict(id="mesopotamia_silver", boxes=[[29.0, 37.5, 41.0, 48.5]], **{"from": -2000, "to": -539},
         low=20.0, high=20.0, kind="silver", lender="temple", lawful="capped",
         instead=None, mark="recorded",
         note="One shekel per mina per month, twelve shekels in the year: twenty per cent. Set by "
              "custom and written into the Laws of Eshnunna and the Code of Hammurabi as a legal "
              "maximum, and stable for more than a thousand years. A creditor who took more than "
              "the maximum forfeited the principal.",
         source="Laws of Eshnunna (18A); Code of Hammurabi; Hudson, 'How interest rates were set, "
                "2500 BC to 1000 AD'; Banca d'Italia, Mesopotamian clay tablets"),

    dict(id="mesopotamia_grain", boxes=[[29.0, 37.5, 41.0, 48.5]], **{"from": -2000, "to": -1900},
         low=33.33, high=33.33, kind="grain", lender="temple", lawful="capped", instead=None,
         mark="recorded",
         note="A hundred silas on three hundred: a third. Grain cost more to borrow than silver "
              "because it was borrowed in the hungry months before the harvest, when it was "
              "scarcest, and repaid just after, when it was cheapest. The legal maximum on grain "
              "fell to twenty per cent over the following centuries.",
         source="Laws of Eshnunna (18A); Code of Hammurabi; Ur III loan tablets"),

    dict(id="mesopotamia_grain_later", boxes=[[29.0, 37.5, 41.0, 48.5]], **{"from": -1899, "to": -539},
         low=20.0, high=20.0, kind="grain", lender="temple", lawful="capped", instead=None,
         mark="recorded",
         note="The grain maximum comes down to the silver maximum and the two sit at twenty per "
              "cent together. A crop failure cancelled the year's interest, and a creditor could "
              "not pursue repayment before the harvest was in.",
         source="Mesopotamian interest rates 3000-400 BC; Code of Hammurabi 48, 88, 90"),

    dict(id="egypt_credit", boxes=[[24.0, 31.5, 30.0, 34.0]], **{"from": -1500, "to": -332},
         low=20.0, high=33.0, kind="commercial", lender="temple", lawful="capped", instead=None,
         mark="estimated",
         note="Interest-bearing debt is recorded from the New Kingdom, and the rates in practice "
              "run twenty to thirty-three per cent. The law could in principle reach a thousand "
              "per cent; that figure is a penalty, not a price.",
         source="'Interest-bearing debt in Ancient Egypt'"),

    # ------------------------------------------------------------------ the classical world
    dict(id="athens_commercial", boxes=[[36.0, 40.0, 22.0, 25.0]], **{"from": -500, "to": -200},
         low=12.0, high=12.0, kind="commercial", lender="money-changer", lawful=True, instead=None,
         mark="estimated",
         note="The ordinary rate on a commercial loan. Interest was not capped and not thought "
              "shameful; the complaints are about the rate, not the principle.",
         source="History of banking; Wikipedia, history of interest"),

    dict(id="athens_bottomry", boxes=[[35.0, 41.0, 20.0, 28.0]], **{"from": -500, "to": -200},
         low=20.0, high=30.0, kind="maritime", lender="money-changer", lawful=True, instead=None,
         mark="estimated",
         note="A bottomry loan on a ship's cargo, where the lender loses everything if the ship "
              "goes down. The premium is the sea, not the borrower.",
         source="History of banking; Wikipedia, history of interest"),

    # starts at 350 BC so that 326, the year of the Lex Poetelia, falls inside the row rather than
    # just outside it — a player standing in that year must get the credit, not a silence
    dict(id="rome_argentarii", boxes=[[36.0, 45.0, 8.0, 20.0]], **{"from": -350, "to": 400},
         low=8.0, high=12.0, kind="commercial", lender="bank", lawful="capped",
         instead="Debt bondage (nexum) was the pledge a poor citizen gave, and the Lex Poetelia "
                 "Papiria of 326 BC abolished it: a creditor could no longer take the debtor's "
                 "body for the debt.",
         mark="estimated",
         note="The argentarii took deposits and lent them out at eight to twelve per cent. The "
              "Roman unit fraction was the uncia, a twelfth, which is eight and a third per cent.",
         source="Wikipedia, history of banking; Lex Poetelia Papiria 326 BC; Hudson"),

    dict(id="byzantium", boxes=[[36.0, 42.0, 25.0, 35.0]], **{"from": 500, "to": 1200},
         low=8.0, high=8.0, kind="commercial", lender="money-changer", lawful="capped",
         instead=None, mark="estimated",
         note="Eight per cent, the rate the empire held to for centuries while western Europe had "
              "no organised credit to speak of.",
         source="Wikipedia, history of interest rates"),

    # ------------------------------------------------------------------ China
    dict(id="china_monastery_pawn", boxes=[[22.0, 40.0, 100.0, 122.0]], **{"from": 420, "to": 1368},
         low=12.0, high=36.0, kind="pawn", lender="monastery", lawful="capped",
         instead=None, mark="recorded",
         note="The oldest credit institutions on record in China are pawnshops run by Buddhist "
              "monasteries — the changshengku, or long-life treasuries — from the fifth century. "
              "Borrowing costs in traditional Chinese lending markets ran one to three per cent a "
              "month, which is twelve to thirty-six a year.",
         source="Wikipedia, history of pawnbroking; Yang Lien-sheng, Money and Credit in China; "
                "Lowenstein, 'ROSCAs in prewar China', Economic History Review 2024"),

    dict(id="china_rosus", boxes=[[22.0, 40.0, 100.0, 122.0]], **{"from": 618, "to": 1911},
         low=None, high=None, kind="rosus", lender="kinship", lawful=True,
         instead="A rotating savings and credit association: the she of the Tang, and the same "
                 "thing in every society without banks. Members pay in and take the whole sum in "
                 "turn, so the credit costs nothing but the wait.",
         mark="recorded",
         note="Co-operative loan societies run first by monasteries and then by anybody. No rate: "
              "the price of credit in a she is your place in the rotation. At least seven per cent "
              "of households were in one in the Qing and Republican periods.",
         source="Lowenstein 2024; Wikipedia, ROSCA"),

    dict(id="china_flying_money", boxes=[[30.0, 40.0, 105.0, 118.0]], **{"from": 800, "to": 1000},
         low=None, high=None, kind="commercial", lender="state", lawful=True,
         instead="Feiqian, flying money: a merchant deposits coin at the capital and draws it in "
                 "the provinces, so the treasury moves the silver and the merchant does not carry "
                 "it. A bill of exchange, three centuries before Genoa.",
         mark="recorded",
         note="A transfer instrument rather than a loan, and the ancestor of the paper money that "
              "followed in the Song.",
         source="Wikipedia, history of banking; Wikipedia, jiaozi"),

    # ------------------------------------------------------------------ the Islamic world
    dict(id="ottoman_cash_waqf", boxes=[[36.0, 43.0, 26.0, 45.0]], **{"from": 1500, "to": 1823},
         low=10.8, high=11.5, kind="commercial", lender="waqf", lawful=False,
         instead="A cash waqf lends through a cost-plus sale or a lease-back, so the return is a "
                 "profit on a transaction and not interest on a loan. A sixteenth-century sultan "
                 "capped the effective rate at eleven and a half per cent and had it ratified by "
                 "a fetva; the late empire capped it at nine.",
         mark="measured",
         note="The best-measured credit figures in this table: 1,559 of the 1,563 cash waqfs of "
              "Bursa returned between nine and twelve per cent, year after year from 1555 to 1823. "
              "The constancy is the point — a fixed rate the courts enforced, which kept the "
              "usurers out of the market.",
         source="Ottoman Cash Waqfs Revisited: the case of Bursa 1555-1823; Kuran, 'The absence of "
                "the corporation in Islamic law'; Wikipedia, Riba"),

    dict(id="islamic_general", boxes=[[12.0, 42.0, -15.0, 75.0]], **{"from": 700, "to": 1900},
         low=10.0, high=20.0, kind="commercial", lender="money-changer", lawful=False,
         instead="Riba is forbidden, so the loan is dressed as a sale: murabaha, a cost-plus "
                 "purchase the lender makes on the borrower's behalf, or one of the hiyal, the "
                 "legal stratagems that satisfy the letter of the ban. Eighty per cent of Islamic "
                 "lending is murabaha today.",
         mark="estimated",
         note="A wide band for fourteen centuries and three continents, and honestly a band: what "
              "is forbidden in principle is practised at ten to twenty per cent through the "
              "stratagems. Where a measured figure exists, as for the Ottoman waqfs, use that row "
              "instead of this one.",
         source="Wikipedia, Riba; Wikipedia, Islamic banking and finance; Ottoman credit history"),

    # ------------------------------------------------------------------ India
    dict(id="maurya_adesha", boxes=[[8.0, 35.0, 68.0, 90.0]], **{"from": -321, "to": -185},
         low=None, high=None, kind="commercial", lender="bank", lawful=True,
         instead="The adesha: a written order to a banker to pay a named sum to a third party. It "
                 "is a bill of exchange, and it is the ancestor of the hundi.",
         mark="recorded",
         note="No rate is recorded for the Maurya period. What is recorded is the instrument, "
              "which is more interesting: a transferable order to pay, in India, three centuries "
              "before the Common Era.",
         source="Wikipedia, Hundi; Wikipedia, history of banking; Vedic loans c.1750 BC"),

    dict(id="mughal_sarraf", boxes=[[8.0, 35.0, 68.0, 90.0]], **{"from": 1526, "to": 1800},
         low=12.0, high=30.0, kind="commercial", lender="sarraf", lawful=True,
         instead=None, mark="measured",
         note="The ṣarrāfs of Mughal India — assayers and money-changers who became bankers — "
              "lent at one to two and a half per cent a month, which is twelve to thirty a year. "
              "They took deposits, discounted each other's hundis, insured cargoes, and about "
              "three hundred of them held mint rights by 1660.",
         source="'The Moneychangers (Ṣarrāfs) in Mughal India'; Mughal monetary system"),

    dict(id="mughal_hundi", boxes=[[8.0, 35.0, 68.0, 90.0]], **{"from": 1600, "to": 1800},
         low=1.0, high=8.0, kind="bill", lender="sarraf", lawful=True,
         instead=None, mark="measured",
         note="The discount on a hundi — what a hundred-rupee bill fetched in cash before it fell "
              "due. One per cent at the height of the empire, rising to eight by 1751 as the "
              "Mughal peace came apart. A rise in the discount is a measurement of a state "
              "failing.",
         source="Mughal monetary system; Wikipedia, Hundi; Reserve Bank of India"),

    # ------------------------------------------------------------------ Europe
    # Hyderabad in 1900 was silent until these two rows existed: the Mughal rows stop at 1800 and
    # nothing else reaches the subcontinent. Keynes, in Indian Currency and Finance (1913), watched
    # the two markets behave differently in a squeeze, which is the interesting half of it — the
    # bazaar rate is the one a cultivator and a shroff actually paid.
    dict(id="india_bazaar", boxes=[[8.0, 35.0, 68.0, 92.0]], **{"from": 1858, "to": 1947},
         low=7.0, high=13.0, kind="commercial", lender="sarraf", lawful="capped",
         instead="the Presidency Banks lent to the great houses and the shroffs financed nearly "
                 "the whole of the internal trade, discounting hundis and never touching European "
                 "paper: two markets side by side, with the native one the deeper of the two.",
         mark="measured",
         note="Keynes, Indian Currency and Finance (1913), chapter VII: when the Presidency Banks' "
              "rate rose to ten or twelve per cent, 'the rate in the native market did not respond "
              "to the full extent, but generally stopped at seven or eight'. The two markets were "
              "not one market.",
         source="Keynes, Indian Currency and Finance (1913), ch. VII"),
    dict(id="india_moneylender", boxes=[[8.0, 35.0, 68.0, 92.0]], **{"from": 1858, "to": 1947},
         low=12.0, high=24.0, kind="mortgage", lender="moneylender", lawful="capped",
         instead="the moneylender took the standing crop, and the debt outlived the harvest: "
                 "renewed each season at a rate the cultivator could not pay off, which is why "
                 "every decade of the Raj produced a new usury law and none of them bit.",
         mark="measured",
         note="The Banking Enquiry found annualised rates of twelve to twenty-four per cent across "
              "most districts — nine to twenty-four in the wet villages of Tanjore, twelve to "
              "twenty-four in the dry ones of Bellary. The Presidency Banks could charge no more "
              "than twelve; a ryot borrowing on his crop paid the upper half of that range.",
         source="Banking Enquiry Committee, cited in Credit risk in colonial India"),

    dict(id="italian_cities", boxes=[[42.0, 46.0, 8.0, 14.0]], **{"from": 1150, "to": 1250},
         low=20.0, high=20.0, kind="commercial", lender="bank", lawful=False,
         instead="The bill of exchange: the loan is hidden in the exchange rate between two "
                 "currencies, so nothing is called interest. Genoa's notaries are writing them in "
                 "the 1190s.",
         mark="estimated",
         note="Twenty per cent in the Italian cities around 1150, at the very start of the "
              "commercial revolution — and charged by men who were breaking their own church's "
              "law to do it.",
         source="Wikipedia, history of interest rates; Wikipedia, bill of exchange"),

    dict(id="venice_late", boxes=[[44.0, 46.5, 11.0, 14.0]], **{"from": 1430, "to": 1500},
         low=6.25, high=20.0, kind="commercial", lender="bank", lawful=False,
         instead="the bill of exchange, as elsewhere in Italy, and the funded debt: the Republic "
                 "had borrowed from its own citizens since the Monte Vecchio of 1262, and the "
                 "interest a holder drew was called a share of the state's revenue rather than "
                 "interest on a loan.",
         mark="estimated",
         note="Venice opens the period at twenty per cent and closes it at six and a quarter — "
              "the single largest fall in the price of credit anywhere in this table, inside two "
              "generations, in the city that had the deepest market for government debt.",
         source="Wikipedia, history of interest rates"),

    dict(id="datini", boxes=[[42.0, 46.0, 8.0, 14.0]], **{"from": 1383, "to": 1411},
         low=10.0, high=16.0, kind="commercial", lender="bank", lawful=False,
         instead="Deposits taken as 'discretionary' investments and lent at a profit, which is "
                 "partnership rather than usury.",
         mark="measured",
         note="The Datini archive of Prato, 1383 to 1411, is the one medieval bank whose books "
              "survive whole: effective rates of ten to sixteen per cent a year.",
         source="Wikipedia, history of banking; Datini archive"),

    dict(id="english_jews", boxes=[[51.0, 54.5, -3.0, 1.0]], **{"from": 1100, "to": 1290},
         low=43.0, high=54.0, kind="commercial", lender="money-changer", lawful=False,
         instead="Christians could not lend at interest and Jews could not lend at interest to "
                 "one another, so the Jews of England lent to Christians, at rates the crown "
                 "protected and then confiscated. Expelled in 1290.",
         mark="recorded",
         note="Two pence in the pound a week: about forty-three per cent simple, or fifty-four "
              "compounded. A rate set by the crown's willingness to defend the debt rather than "
              "by the market for it.",
         source="NBER w9742, 'An economic history of usury laws'; Wikipedia, Usury"),

    dict(id="england_legal_max", boxes=[[50.0, 56.0, -6.0, 2.0]], **{"from": 1545, "to": 1854},
         low=5.0, high=10.0, kind="commercial", lender="bank", lawful="capped",
         instead=None, mark="recorded",
         note="Henry VIII's Parliament permits interest in 1545 at a ten per cent maximum; the "
              "maximum is repealed in 1552, restored at ten under Elizabeth in 1571, and then "
              "walked down to eight in 1624, six in 1660 and five in 1713, where it sticks until "
              "the usury laws are repealed in 1854. Because the maximum was also read as the "
              "minimum, the cap is the best single figure for the English rate — though the "
              "market rate in the 1700s was nearer ten.",
         source="NBER w9742; Usury Acts 1545, 1623, 1660, 1713; Usury Laws Repeal Act 1854"),

    dict(id="bank_of_england", boxes=[[51.0, 52.5, -1.0, 0.5]], **{"from": 1694, "to": 1833},
         low=5.0, high=8.0, kind="state", lender="bank", lawful="capped",
         instead=None, mark="recorded",
         note="The Bank of England is founded in 1694 to lend the government £1.2m at eight per "
              "cent. Through the eighteenth century its discount rate is pinned at the legal "
              "maximum of five, so it rations credit rather than pricing it, and lends only to "
              "its regular merchants in London. Freed for bills in 1833, it starts moving the "
              "rate — and spikes it in a crisis, which is where the idea of a lender of last "
              "resort comes from.",
         source="Bank of England; Bank of England Staff Working Paper 691; Broz and Grossman"),

    dict(id="holland", boxes=[[51.0, 53.5, 4.0, 7.0]], **{"from": 1570, "to": 1600},
         low=8.13, high=8.13, kind="state", lender="bank", lawful=True, instead=None,
         mark="measured",
         note="Eight and an eighth per cent in the 1570s, and falling: the Dutch Republic borrows "
              "more cheaply than any state in Europe, and cheaper than its own subjects can.",
         source="Wikipedia, history of interest rates"),

    # split at 1900: one row saying "1.85 to 7.64" across 140 years would be true of no year in it
    dict(id="united_states_early", boxes=[[30.0, 45.0, -95.0, -70.0]], **{"from": 1810, "to": 1899},
         low=6.0, high=7.64, kind="commercial", lender="bank", lawful="capped",
         instead=None, mark="measured",
         note="Seven and two-thirds per cent in the 1810s, and still nearer six than two on the "
              "eve of the Federal Reserve. Every state set its own legal maximum, and nearly "
              "every one of them was broken.",
         source="Wikipedia, history of interest rates"),
    dict(id="united_states_modern", boxes=[[30.0, 45.0, -95.0, -70.0]], **{"from": 1900, "to": 1950},
         low=1.85, high=5.0, kind="commercial", lender="bank", lawful="capped",
         instead=None, mark="measured",
         note="Under two per cent in the 1940s, with the central bank holding the whole structure "
              "down. The lowest rates in this table, and the newest — money has never been so "
              "cheap for so long as in these fifty years.",
         source="Wikipedia, history of interest rates"),

    # ------------------------------------------------------------------ where there is no rate
    dict(id="west_africa_cowrie", boxes=[[4.0, 14.0, -8.0, 12.0]], **{"from": 1400, "to": 1900},
         low=None, high=None, kind="commercial", lender="kinship", lawful=True,
         instead="Cowries are the money, imported from the Indian Ocean. Credit runs on pawnship "
                 "(a person pledged against a debt), on the esusu and ajo rotating savings clubs "
                 "of the Yoruba — three hundred of them in Abeokuta alone by 1856 — and on the "
                 "storehouse keepers who took cowries in for safety and lent them out again.",
         mark="recorded",
         note="**No rate is recorded, and that is the finding.** Pre-colonial West Africa had "
              "money, savings, deposit and credit without a price for credit: the return was a "
              "place in the rotation, or a pledge, or a share of the crop. The king of Benin "
              "offered English traders credit in 1553 on their next voyage — the Africans "
              "extending credit to the Europeans, not the other way round.",
         source="Adebayo, 'Money, Credit and Banking in Precolonial Africa'; Credit, currencies "
                "and culture: African financial institutions; Lovejoy, cowrie currencies"),

    dict(id="andean_no_money", boxes=[[-20.0, 5.0, -82.0, -65.0]], **{"from": 1200, "to": 1532},
         low=None, high=None, kind="none", lender="none", lawful=None,
         instead="The Inca kept the most careful accounts in the Americas — the khipu, knotted "
                 "cords recording everything the state held and moved — and had no money and no "
                 "credit at all. Obligation ran through kinship and the state's redistribution, "
                 "not through a loan.",
         mark="recorded",
         note="**The only major civilisation without money**, and no evidence has contradicted "
              "that since the Spanish arrived in 1532. The khipu is an accounting system and not "
              "an incipient currency. A player asking for the interest rate here should be told "
              "there was not one, not given a number.",
         source="Hornborg, 'Was the Inca economy based on protomoney?', Economic Anthropology "
                "2026; Murra; Science News"),
]

# The kinds of loan, in the order a player would think of them.
KINDS = ["silver", "grain", "commercial", "maritime", "state", "deposit", "pawn", "mortgage",
         "rosus", "none", "bill"]

KIND_WORDS = {
    "silver": "a loan of silver", "grain": "a loan of grain",
    "commercial": "a commercial loan", "maritime": "a loan on a ship's cargo",
    "state": "a loan to a government", "deposit": "money put in and left",
    "pawn": "a loan against a pledge", "mortgage": "a loan against land",
    "rosus": "a turn in a savings club", "none": "no credit at all",
    "bill": "the discount on a bill of exchange",
}

# Who does the lending.
LENDER_WORDS = {
    "temple": "the temple", "monastery": "the monastery", "money-changer": "the money-changer",
    "bank": "the bank", "goldsmith": "the goldsmith", "waqf": "the cash waqf",
    "sarraf": "the ṣarrāf", "pawnshop": "the pawnshop", "kinship": "kin and neighbours",
    "state": "the treasury", "none": "nobody", "moneylender": "the moneylender",
}


def problems():
    """Checks, so a bad row cannot ship silently."""
    out = []
    seen = set()
    for r in RATES:
        if r["id"] in seen:
            out.append("%s: two rows with this id" % r["id"])
        seen.add(r["id"])
        if r["from"] > r["to"]:
            out.append("%s: from %d is after to %d" % (r["id"], r["from"], r["to"]))
        if r["kind"] not in KIND_WORDS:
            out.append("%s: unknown kind '%s'" % (r["id"], r["kind"]))
        if r["lender"] not in LENDER_WORDS:
            out.append("%s: unknown lender '%s'" % (r["id"], r["lender"]))
        if r["lawful"] not in (True, False, "capped", None):
            out.append("%s: lawful must be True, False, 'capped' or None" % r["id"])
        if r["mark"] not in ("recorded", "measured", "estimated"):
            out.append("%s: mark must be recorded, measured or estimated" % r["id"])
        lo, hi = r["low"], r["high"]
        if (lo is None) != (hi is None):
            out.append("%s: one end of the range is missing" % r["id"])
        if lo is not None and lo > hi:
            out.append("%s: low %.2f is above high %.2f" % (r["id"], lo, hi))
        for b in r["boxes"]:
            if len(b) != 4:
                out.append("%s: a box needs four numbers" % r["id"])
            elif b[0] > b[1] or b[2] > b[3]:
                out.append("%s: box %s is inside out" % (r["id"], b))
        if not r.get("source"):
            out.append("%s: no source" % r["id"])
    return out


if __name__ == "__main__":
    import collections

    probs = problems()
    print("credit: %d rows" % len(RATES))
    print("  by mark:", dict(collections.Counter(r["mark"] for r in RATES)))
    print("  by lawful:", dict(collections.Counter(str(r["lawful"]) for r in RATES)))
    print("  with a rate: %d   without (a recorded absence): %d"
          % (sum(1 for r in RATES if r["low"] is not None),
             sum(1 for r in RATES if r["low"] is None)))
    for r in RATES:
        rate = "—" if r["low"] is None else (
            "%.2f%%" % r["low"] if r["low"] == r["high"]
            else "%.2f–%.2f%%" % (r["low"], r["high"]))
        print("   %-22s %6d..%-5d %-14s %-9s %s" % (r["id"], r["from"], r["to"], rate,
                                                    r["mark"], r["lender"]))
    for p in probs:
        print("  PROBLEM", p)
    print("credit_table: %d problem(s)" % len(probs))
