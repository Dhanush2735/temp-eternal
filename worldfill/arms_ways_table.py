"""
Step 45 part 3 (E9 B): the five ways a weapon gets into a man's hand — and whether he may carry it.

**The five ways**, which is the whole question of army supply in five words:

  1. **issued**  — the state hands you a weapon, and it stays theirs. You give it back.
  2. **bring**   — you arrive already carrying the one you own.
  3. **buy**     — you buy one, from a smith or a market or a ship.
  4. **take**    — you take it off a beaten enemy and keep it.
  5. **gift**    — it is given to you: by a kinsman, a lord, a patron, or a will.

**And a sixth, which is not a way of getting one but is the law that matters most of the time:**

  6. **carry**   — you may go about with it.

The sixth is here because it has to be. **Keeping and carrying are different laws in every age and
a table that merges them misreads both.** The Statute of Northampton 1328 never touched a man's
right to own a sword; it forbade him to walk into a market wearing one. The 1181 Assize of Arms
*required* every freeman to own arms and in the same breath forbade him to sell or pledge them —
so `buy` is open and `gift` is shut. The Indian Arms Act 1878 required a licence to own a gun and
exempted Europeans: `buy` shut for an Indian, open for an Englishman, in the same place and year.

None of those three can be written down as "guns are legal here" or "guns are banned here", which
is why this register carries six flags and not one.

**The rows are illustrative, not comprehensive.** There is no table of how armies were supplied to
be read. Each row is written by hand and names its source. A place and year with no row at all
falls through to the default (row 0), which is the honest answer for most of the map: you bring
your own.
"""

# The five ways, plus carry. The order is fixed and the pack ships it, so a reader can print them.
WAYS = ["issued", "bring", "buy", "take", "gift"]
FLAGS = WAYS + ["carry"]

# What the flag means, one line each, shipped in the pack so the game can explain itself.
FLAG_MEANING = {
    "issued": "the state hands you one, and it stays theirs",
    "bring":  "you arrive already carrying the one you own",
    "buy":    "you buy one, from a smith, a market or a ship",
    "take":   "you take it off a beaten enemy and keep it",
    "gift":   "it is given to you: by a kinsman, a lord, a patron or a will",
    "carry":  "you may go about with it, which is not the same as owning it",
}

# The shape of the law where the row holds, the same five the weapon-law table uses.
SHAPES = ["must", "free", "licence", "banned", "class"]

AREAS = ["EUR", "EEU", "WAS", "NAF", "CAS", "SAS", "EAS", "SEA", "WAF", "MSA", "EAF",
         "NNA", "MNA", "CAC", "SAM", "PAC", "AUS"]

ALL = list(AREAS)

# A row.
#
#   id       a short name, for the checks
#   areas    the area codes it holds in, or ALL
#   y0 / y1  the span of years
#   shape    must | free | licence | banned | class
#   flags    the six, 1 open and 0 shut
#   forWhom  who the row is about — None when it is everybody
#   text     what the row says, printed in the world
#   note     what it meant
#   source   where it came from

ROWS = [
    # ------------------------------------------------------------------ 0: the default
    dict(id="own", areas=ALL, y0=-10000, y1=2000, shape="free",
         polity=None,
         flags=dict(issued=0, bring=1, buy=1, take=1, gift=1, carry=1), forWhom=None,
         text="You bring your own. The spear is yours, the smith will sell you a better one, your "
              "father's hangs over the door, and what you take off a dead man is yours to keep.",
         note="**The honest answer for most of the map and most of time.** Standing armies that "
              "clothe, feed and arm their men are a few centuries old in most of the world and "
              "very recent in the rest. Before them, an army is men who arrive already armed, and "
              "that is why every law about weapons before the modern age is a law about what the "
              "free man must own.",
         source="the pattern the armory register (part A) and the weapon-law rows both show: "
                "spear, club and dagger are at -10000 in every one of the 17 areas"),

    # ------------------------------------------------------------------ the classical world
    dict(id="rome", areas=["EUR", "NAF", "WAS", "EEU"], y0=-500, y1=400, shape="free",
         polity=None,
         flags=dict(issued=1, bring=1, buy=1, take=1, gift=1, carry=1), forWhom=None,
         text="The legionary is armed by the state, and the cost is stopped out of his pay; the "
              "auxiliary brings the weapon of his own people — the bowman his bow, the slinger his "
              "sling, the cavalryman his lance. Spoils are the army's, and a share of them is his.",
         note="Two systems in one army and both at once: the citizen is **issued** his panoply, "
              "the provincial **brings** the arm he was raised with, which is why the auxilia "
              "look like a gallery of the peoples of the empire. And inside the pomerium none of "
              "them carry anything at all.",
         source="Wikipedia, Roman army; Imperial Roman army; Pomerium"),

    # ------------------------------------------------------------------ medieval Europe
    dict(id="knight", areas=["EUR", "EEU"], y0=500, y1=1500, shape="free",
         polity=None,
         flags=dict(issued=0, bring=1, buy=1, take=1, gift=1, carry=1), forWhom="the free man",
         text="A knight comes with his warhorse, his mail, his sword and the men he has armed "
              "himself. The shire levy is armed by the hundred, each man by his wealth. A clerk "
              "may carry none of it.",
         note="An army of owners. The one thing a lord cannot do is arm a peasant and call it "
              "nothing — which is exactly why England's 1388 statute had to *permit* servants and "
              "labourers to carry bucklers and swords in wartime.",
         source="Wikipedia, Medieval army; Assize of Arms of 1181; 12 Rich. 2"),

    # ------------------------------------------------------------------ England: duty, curb, then carry
    dict(id="assize", areas=["EUR"], y0=1181, y1=1327, shape="must",
         polity=["Angevin", "England"],
         flags=dict(issued=0, bring=1, buy=1, take=1, gift=0, carry=1), forWhom="every freeman, "
                                                                                "but not Jews",
         text="You must own arms, by your rank and your chattels, and you may not sell them, "
              "pledge them, lend them or give them away: on your death they pass to your heir. "
              "Buy one if you need one. A Jew may not keep a coat of mail or a breastplate.",
         note="**A duty, not a restriction, and the one row here where `gift` is shut and `buy` "
              "is open.** The realm is defended by men who arrive already armed, so the law "
              "makes ownership compulsory and disposal impossible — and it names an exemption in "
              "the same breath.",
         source="Wikipedia, Assize of Arms of 1181"),

    dict(id="northampton", areas=["EUR"], y0=1328, y1=1685, shape="licence",
         polity=["England"],
         flags=dict(issued=0, bring=1, buy=1, take=1, gift=1, carry=0), forWhom="everyone but "
                                                                                "the King's servants",
         text="You may keep any weapon you like. You may not wear one into a market, a fair, or "
              "in front of the justices, nor ride armed by night or by day, except in the King's "
              "service or when the hue and cry goes up.",
         note="**The row that shows why `carry` had to be its own flag.** Ownership is untouched: "
              "`buy`, `gift`, `take` and `bring` are all wide open. Only going about armed is "
              "shut. The courts read it that way for three centuries, until James II enforced it "
              "against anyone at all in 1686.",
         source="Wikipedia, Statute of Northampton 1328"),

    # ------------------------------------------------------------------ early modern: the standing army
    dict(id="standing", areas=["EUR", "EEU"], y0=1600, y1=1900, shape="free",
         polity=None,
         flags=dict(issued=1, bring=1, buy=1, take=1, gift=1, carry=1), forWhom=None,
         text="The regiment arms, clothes and feeds its men, and the weapon is numbered and "
              "returned to the armoury. The officer buys his own sword and his own commission.",
         note="The century that invents the standing army invents the armoury that owns what it "
              "hands out — `issued` becomes normal for the first time since Rome, and by the "
              "Napoleonic and industrial wars a rifle is a numbered article of state property.",
         source="Wikipedia, Standing army; Early modern warfare"),

    # ------------------------------------------------------------------ Japan
    dict(id="katanagari", areas=["EAS"], y0=1588, y1=1868, shape="banned",
         polity=["Japan", "Shogunate"],
         flags=dict(issued=1, bring=0, buy=0, take=0, gift=0, carry=0), forWhom="the non-noble "
                                                                                "classes",
         text="A peasant may not keep a sword, a spear or a firearm. The samurai wears two swords "
              "as the badge of his station; the ashigaru is armed from his lord's stores.",
         note="Hideyoshi's Sword Hunt of 29 August 1588, and it held for two hundred and eighty "
              "years. **The weapon became a certificate**: the sword is not what the samurai "
              "fights with so much as what proves he is the sort of man who may.",
         source="guncite.com, Japanese Gun Control (Kopel); Wikipedia, Toyotomi Hideyoshi"),

    # ------------------------------------------------------------------ China
    dict(id="yuan", areas=["EAS"], y0=1281, y1=1368, shape="banned",
         polity=["Yuan"],
         flags=dict(issued=1, bring=0, buy=0, take=0, gift=0, carry=0), forWhom="Han and "
                                                                                "Southerners",
         text="A Han or Southerner civilian may not keep a weapon, may not hunt, may not gather "
              "in numbers, may not go abroad at night. Mongol and Semu households are armed as "
              "before.",
         note="**The `class` shape in its purest form**: the same street, the same year, two "
              "different laws depending on which of the Yuan's four orders of person you are.",
         source="Wikipedia, Yuan dynasty"),

    dict(id="qingban", areas=["EAS"], y0=1644, y1=1649, shape="banned",
         polity=["Qing"],
         flags=dict(issued=0, bring=0, buy=0, take=0, gift=0, carry=0), forWhom="the general "
                                                                                "population",
         text="On the conquest, the population is forbidden to own weapons; in 1649 the ban is "
              "lifted and what was confiscated is handed back.",
         note="Five years, and then reversed — because the Qing noticed what every disarming "
              "power notices: **only the law-abiding handed theirs in.** The outlaws kept theirs, "
              "and the lesson the dynasty took from it was the opposite of censorship.",
         source="AskHistorians, Martial arts prohibition during the Qing dynasty (wotan_weevil)"),

    dict(id="qinglate", areas=["EAS"], y0=1650, y1=1911, shape="licence",
         polity=["Qing"],
         flags=dict(issued=1, bring=1, buy=1, take=1, gift=1, carry=0), forWhom=None,
         text="A man may own a sword, a spear or a hunting bow. The late Qing code forbids "
              "civilians to *carry* firearms, but the local militia, the merchant caravan and the "
              "village all keep them, and the 1910 revision lets an ordinary man register a bird "
              "gun or a foreign gun for self-defence.",
         note="**`carry` shut and `buy` open**, again — the same split as Northampton, four "
              "centuries later and half a world away. The Qing banned martial arts no more than "
              "it banned weapons; that story is false.",
         source="Wang, Between Social Control and Popular Power: private guns in the mid to late "
                "Qing, 1781-1911 (American Journal of Chinese Studies 25, 2017)"),

    # ------------------------------------------------------------------ India
    dict(id="maratha", areas=["SAS"], y0=1650, y1=1818, shape="free",
         polity=["Maratha"],
         flags=dict(issued=1, bring=1, buy=1, take=1, gift=1, carry=1), forWhom=None,
         text="A horseman comes as a **bargir**, on the sarkar's horse with the sarkar's arms, or "
              "as a **shiledar**, on his own with his own — and the two serve side by side in the "
              "same army, for the same pay.",
         note="**The five ways visible in one muster roll.** The bargir is the standing army and "
              "the shiledar is the levy, and the Maratha army ran both at once, which is a large "
              "part of why it beat armies three times its size.",
         source="WEAPONS_RESEARCH.md [L2], Maratha army (bargir / shiledar)"),

    dict(id="armsact", areas=["SAS"], y0=1878, y1=1947, shape="licence",
         polity=["Raj"],
         flags=dict(issued=1, bring=0, buy=0, take=0, gift=0, carry=0), forWhom="Indians, but "
                                                                                "not Europeans",
         text="A licence is required to own, make, sell or carry arms, and **Europeans are "
              "exempt**. The soldier is issued his rifle and it goes back to the armoury.",
         note="Eleven years after 1857, and the exemption is the whole of it. **A law to disarm "
              "the governed and not the governors.** Every decade of the Raj produced another, "
              "and none of them bit.",
         source="Indian Arms Act 1878, via iasgyan.in; WEAPONS_RESEARCH.md [L1]"),

    dict(id="hyderabad", areas=["SAS"], y0=1948, y1=1948, shape="banned",
         polity=["Hyderabad"],
         flags=dict(issued=1, bring=1, buy=1, take=1, gift=1, carry=1), forWhom="the Nizam's "
                                                                                "state",
         text="Under blockade, with the border shut and the trains stopped, arms come in by air "
              "and by night, bought abroad and flown in; the state's stock is what the Indian "
              "Army finds when it arrives.",
         note="**The one row in this register where the shape and the flags disagree on "
              "purpose.** The shape is the law on paper; the flags are what actually happened. A "
              "blockade is that distance, and it is why `take` and `buy` are in this register at "
              "all: they are the two ways a weapon reaches a hand that no statute governs.",
         source="WEAPONS_RESEARCH.md, Hyderabad 1948 (Operation Polo)"),

    # ------------------------------------------------------------------ the Andes
    dict(id="inca", areas=["SAM"], y0=1200, y1=1533, shape="free",
         polity=["Inca"],
         flags=dict(issued=1, bring=0, buy=0, take=0, gift=0, carry=0), forWhom=None,
         text="The army is fed, clothed and armed from the state storehouses, and the weapon goes "
              "back into them when the campaign ends. There is no market in arms and no coin to "
              "buy one in.",
         note="An economy without money cannot have a private arms trade, so four of the five "
              "ways simply do not exist. **The row is a reminder that the five ways are not "
              "universal possibilities — they are what a particular economy permits.**",
         source="Wikipedia, Inca army; Mit'a; Storehouse (qullqa)"),

    # ------------------------------------------------------------------ West Africa
    dict(id="wafrica", areas=["WAF", "MSA"], y0=1500, y1=1900, shape="free",
         polity=None,
         flags=dict(issued=1, bring=1, buy=1, take=1, gift=1, carry=1), forWhom=None,
         text="The smith sells a spear and a blade; the ruler's armoury arms the household "
              "soldiers and the levies; firearms come in from the coast, bought with what the "
              "coast wants, and the horse comes down from the savanna the same way.",
         note="**An arms market with a continent on the other side of it.** The gun that arrived "
              "in exchange for captives is the single clearest case in the register of `buy` "
              "changing what a war even is.",
         source="Wikipedia, Atlantic slave trade; History of West Africa"),

    dict(id="samurai_rest", areas=["EAS"], y0=1868, y1=1945, shape="licence",
         polity=["Japan", "Shogunate"],
         flags=dict(issued=1, bring=0, buy=0, take=0, gift=0, carry=0), forWhom=None,
         text="Conscription arms the nation: the state issues, registers and numbers every "
              "weapon, and the conscript's does not belong to him. Private ownership is a "
              "licensed exception.",
         note="Meiji 1873 conscription ends the samurai's monopoly in one stroke, and the "
              "Haitōrei of 1876 forbids the wearing of swords outright — the badge and the "
              "weapon abolished together.",
         source="Wikipedia, Conscription in Japan; Haitōrei Edict"),

    # ------------------------------------------------------------------ the modern state
    dict(id="modern", areas=ALL, y0=1900, y1=2000, shape="licence",
         polity=None,
         flags=dict(issued=1, bring=0, buy=0, take=0, gift=0, carry=0), forWhom=None,
         text="The state issues the weapon, numbers it, and takes it back. Everything else — "
              "buying, taking, giving, carrying — runs by licence, and in much of the world not "
              "even by that.",
         note="The exception to a rule three thousand years old. **For most of history an army "
              "was men who arrived already armed; for the last century and a bit it has been men "
              "who were handed something.** The United States, where the militia still brings his "
              "own, is the outlier and has been since 1791.",
         source="Law on Control of Guns (PRC, 1996); Firearms regulation by country"),

    dict(id="prc", areas=["EAS"], y0=1957, y1=2000, shape="banned",
         polity=["China"],
         flags=dict(issued=1, bring=0, buy=0, take=0, gift=0, carry=0), forWhom="individuals and "
                                                                                "organisations",
         text="No individual or organisation may possess, make, buy, sell, transport or lend a "
              "firearm outside the state's provisions, and there is no right to keep one.",
         note="The 1957 Act banned the public manufacture, repair, purchase and possession of "
              "firearms outright; the 1996 Law on Control of Guns is the modern form of it.",
         source="Act of 22 October 1957; Law of the PRC on Control of Guns (1996)"),
]


def problems():
    """Checks, so a bad row cannot ship silently."""
    out = []
    ids = [r["id"] for r in ROWS]
    if len(ids) != len(set(ids)):
        out.append("duplicate ids: %s" % [i for i in ids if ids.count(i) > 1])
    for r in ROWS:
        i = r["id"]
        if r["shape"] not in SHAPES:
            out.append("%s: unknown shape '%s'" % (i, r["shape"]))
        if sorted(r["flags"]) != sorted(FLAGS):
            out.append("%s: flags are not the six (%s)" % (i, sorted(r["flags"])))
        else:
            for k, v in r["flags"].items():
                if v not in (0, 1):
                    out.append("%s: %s is %r, not 0 or 1" % (i, k, v))
        if r["y1"] < r["y0"]:
            out.append("%s: ends before it begins" % i)
        for a in r["areas"]:
            if a not in AREAS:
                out.append("%s: unknown area '%s'" % (i, a))
        pol = r.get("polity")
        if pol is not None:
            if not isinstance(pol, list) or not pol:
                out.append("%s: polity is %r, not a non-empty list" % (i, pol))
            elif not all(isinstance(x, str) and x.strip() for x in pol):
                out.append("%s: polity holds a non-string" % i)
        for key in ("text", "note", "source"):
            if not r.get(key):
                out.append("%s: no %s" % (i, key))
        # a row that shuts every way and does not say why is a row nobody can act on
        if not any(r["flags"][w] for w in WAYS) and r["shape"] not in ("banned", "class"):
            out.append("%s: every way is shut but the shape is '%s'" % (i, r["shape"]))
    return out


if __name__ == "__main__":
    ps = problems()
    print("ways: %d rows over %d areas, %d flags" % (len(ROWS), len(AREAS), len(FLAGS)))
    for r in ROWS:
        fl = "".join(str(r["flags"][f]) for f in FLAGS)
        print("   %-14s %6d..%-6d %-8s %s  %s" % (r["id"], r["y0"], r["y1"], r["shape"], fl,
                                                  ",".join(r["areas"])[:28]))
    print("        flags in order:", " ".join(FLAGS))
    for p in ps:
        print("  PROBLEM " + p)
    print("arms_ways_table: %d problem(s)" % len(ps))
