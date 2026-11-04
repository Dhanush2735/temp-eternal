#!/usr/bin/env python3
"""Step 40 (D10 armies in action), part 5, second half: who is fighting, and as what.

`war/War.java` holds two lists of faction ids. That is the whole of its idea of a side: a side is
an integer, and two integers are either the same or different. It cannot say whether the party is a
state, whether it can be bargained with, whether its troops are its own or hired, or whether it is
fighting for a frontier or for a throne.

This table is the other half. It is built on one rule taken from the source, and it is a rule
worth stating plainly because it is the one that most army models get wrong:

> "conflicts between warlords when there is no state involvement qualify as violent conflicts."
> -- Peter Brecke, *Violent Conflicts 1400 A.D. to the Present*

Brecke's Conflict Catalog -- 3,708 conflicts, 1400 to 2000, with the parties, the fatalities, the
date and the duration -- records **who fought, who was on each side in conflicts of more than two
participants, who initiated, the start and end dates, the location, the common name, the military
and total fatalities, and the number of significant political actors.** Its threshold is 32 deaths
in a year, which is Richardson's magnitude 1.5. Its dates are, in Brecke's own words, "the dates
when the weapons begin to clash and when they cease."

So a party need not be a state. It can be a warlord, a company, an order, a city, a people, or a
rising. It can also be civilians: the catalog's definition covers "political disagreements between
organized groups, or between an organized group and civilians."

What this table carries, and what it does not:

* it carries the **kinds of party** the catalog's own description admits, read from that
  description;
* it carries **no conflicts, no counts and no dates from the catalog.** The catalog is a binary
  spreadsheet and no row of it was read into this file. A register that prints "3,708 conflicts"
  as if it had them would be lying about the one thing this project does not do.

Two fields do real work downstream:

* **`willTreat`** -- whether this kind of party can be bound by an agreement. Part 4's siege
  register offers a conditional surrender only to a town that can be held to one, and a
  conditional surrender signed by a captain whose men are owed four months' pay is not worth the
  parchment. This table is where that comes from.
* **`raised`** -- which row of the morale table tells you how this party's troops were raised, and
  therefore what they will put up with and how fast they will go.

Rules, the same ones every table in this project obeys: no source no row; a row is dated and
placed; `mark` says how sure we are and the estimated rows say so in their note.
"""

KIND = ("state", "dynasty", "city", "faith", "rising", "people", "band", "company",
        "coalition", "civilians")

MARKS = ("recorded", "mixed", "estimated")

WORLD = (-90.0, 90.0, -180.0, 180.0)


def _box(x):
    lo_la, hi_la, lo_lo, hi_lo = x
    assert -90.0 <= lo_la <= hi_la <= 90.0, "bad latitude %s" % (x,)
    assert -180.0 <= lo_lo <= hi_lo <= 180.0, "bad longitude %s" % (x,)
    return x


class P:
    """One kind of party: who it is, what its troops are, and whether it can be bound.

    `scope` is the part-4 rule applied to parties. **general** means a latitude, a longitude and a
    year are enough to guess it: the steppe in 1200 raises a khan's following, and a European
    frontier in 1400 belongs to a sovereign. **local** means nothing on a map can tell you --
    that Florence is a commune, that this war is dynastic, that the troops are a hired company.
    A local party has to be named by a caller who knows, exactly as a concentric castle had to
    be in the wall register, and `partyAt` will not return one.
    """

    def __init__(self, id, name, kind, start, end, box, raised, will_treat, can_initiate, scope,
                 needs, doing, note, src, mark):
        assert kind in KIND, "%s: unknown kind %s" % (id, kind)
        assert -3000 <= start <= end <= 2026, "%s: bad years %s..%s" % (id, start, end)
        assert isinstance(will_treat, bool) and isinstance(can_initiate, bool), "%s: flags" % id
        assert scope in ("general", "local"), "%s: bad scope %s" % (id, scope)
        assert src, "%s: no source" % id
        assert mark in MARKS, "%s: unknown mark %s" % (id, mark)
        self.id, self.name, self.kind, self.start, self.end = id, name, kind, start, end
        self.box = _box(box)
        self.raised, self.will_treat, self.can_initiate = raised, will_treat, can_initiate
        self.scope = scope
        self.needs, self.doing, self.note, self.src, self.mark = needs, doing, note, src, mark

    def guessable(self):
        return self.scope == "general"

    def covers(self, year):
        return self.start <= year <= self.end

    def here(self, lat, lon):
        lo_la, hi_la, lo_lo, hi_lo = self.box
        return lo_la <= lat <= hi_la and lo_lo <= lon <= hi_lo

    def as_dict(self):
        return {"id": self.id, "name": self.name, "kind": self.kind,
                "start": self.start, "end": self.end, "box": list(self.box),
                "raised": self.raised, "willTreat": self.will_treat,
                "canInitiate": self.can_initiate, "scope": self.scope,
                "needs": self.needs, "doing": self.doing,
                "note": self.note, "src": self.src, "mark": self.mark}


PARTIES = [

    # ---------------------------------------------------------------- the parties that hold a state
    P("sovereign_state", "a sovereign state", "state", -3000, 2026, WORLD,
      "professional_standing", True, True, "general",
      "a government that can raise money, keep a register, and answer for what it signs",
      "raises an army by law, pays for it by tax, and can be held to a treaty by the same "
      "machinery",
      "The default party, and the only kind that is assumed to be able to do all three things: "
      "raise troops, pay them, and answer for a signature. Every other row in this table is a "
      "way of failing at one of the three. Note that `raised` here is an aspiration rather than "
      "a description -- most states in most centuries could not afford a standing army and fell "
      "back on the levy or on hired companies.",
      "Conflict Catalog (Brecke); Sovereign state; Standing army", "recorded"),

    P("dynastic_house", "a house claiming a throne", "dynasty", 1000, 1800,
      (35.0, 60.0, -10.0, 30.0), "retinue", True, True, "local",
      "a family with a claim, an inheritance, and men who hold land from it",
      "fights for the claim rather than for the country, and makes peace for the same reason",
      "The War of the Spanish Succession, the Wars of the Roses, the Habsburg and Valois claims "
      "in Italy. A house **can** treat -- it is often the easiest party in a war to buy, because "
      "what it wants is a throne and not a frontier -- but the treaty binds the family and not "
      "the country, which is why these wars come back in a generation.",
      "War of the Spanish Succession; Wars of the Roses; Dynasty", "recorded"),

    P("city_commune", "a city that governs itself", "city", -800, 1800,
      (35.0, 60.0, -10.0, 40.0), "citizen_militia", True, True, "local",
      "a town with walls, a council, and men who owe it service",
      "fields its own people, which are the best-led militia in the record, and defends its own "
      "walls",
      "The Greek polis, the Lombard commune, the Swiss canton, the Free Imperial City. This is "
      "the party that the siege register in part 4 was written for: it is the one that can be "
      "offered terms, that has a government able to accept them, and whose men will hold a breach "
      "because the street behind it is their own. Florence fought the Visconti for forty years on "
      "condottieri and taxes.",
      "Medieval commune; Italian city-states; Hoplite; Swiss mercenaries", "recorded"),

    P("religious_body", "a church or an order", "faith", 300, 1800,
      (35.0, 62.0, -10.0, 40.0), "retinue", True, True, "local",
      "an institution with land, doctrine, and men sworn to it",
      "fights for doctrine, which is the hardest thing in the record to compromise on",
      "The Teutonic Order in Prussia, the Templars and Hospitallers in the Levant, the Prince-"
      "Bishops of the Rhine. **willTreat is true but it is the weakest true in the table**: a "
      "doctrine is not a frontier, and there is no half of it to hand over. The Peace of Augsburg "
      "in 1555 settled one of these by agreeing that each prince should choose his own, which is "
      "an admission that the question could not be settled any other way.",
      "Teutonic Order; Knights Templar; Peace of Augsburg; Wars of religion", "recorded"),

    P("slave_soldier_state", "a state owned by its own army", "state", 800, 1900,
      (10.0, 45.0, 5.0, 60.0), "slave_soldier", True, True, "local",
      "a ruler whose soldiers were bought as boys and belong to him and to nobody else",
      "fields the most reliable troops in the medieval world and is periodically ruled by them",
      "The Mamluk Sultanate, where the sultan was himself a freed slave soldier and was chosen by "
      "the others; the Janissaries, who deposed and murdered sultans; the ghulams of the "
      "Abbasids. **willTreat is true and the party is the most dangerous in the table anyway**, "
      "because the thing that would have to sign is not the ruler but the corps, and it will not "
      "sign away its own privileges.",
      "Mamluk; Janissary; Ghulam; Slave soldier", "recorded"),

    # ---------------------------------------------------------------- the parties that hold no state
    P("rebellion", "a rising against a government", "rising", -3000, 2026, WORLD,
      "levy", False, True, "general",
      "a government with a grievance against it, and people willing to die over it",
      "fights without a frontier, without a treasury, and often without a uniform",
      "Brecke's catalog records who initiated, and it is very often this party. **willTreat is "
      "false**, and it is false for a structural reason rather than a moral one: a rising has no "
      "machinery that can be held to an agreement, and the government it rose against does not "
      "recognise it as a party that can sign one. Both facts change the moment the rising wins. It "
      "is the default party for anyone who has taken up arms against a government and does not "
      "yet have one of their own, which is why the row runs the whole length of the register.",
      "Conflict Catalog (Brecke); Rebellion; Insurgency", "recorded"),

    P("separatist", "a people claiming its own state", "people", 1776, 2026, WORLD,
      "conscript_national", False, True, "local",
      "a people that can say what it is and where its borders would be",
      "fights for a frontier it does not have yet, which makes it nearly impossible to buy off",
      "Dated from 1776 because that is when the type appears: a party whose whole claim is that "
      "it ought to be a sovereign state. **willTreat is false** in the sense that matters -- you "
      "cannot offer a separatist movement a frontier, because the frontier is the thing in "
      "dispute.",
      "Separatism; Conflict Catalog (Brecke); Self-determination", "recorded"),

    P("tribal_confederacy", "a people without a state", "people", -3000, 1900, WORLD,
      "levy", False, True, "general",
      "a people with a name, a country, and no government anyone would recognise as one",
      "fights as a whole people, which means its whole people are in the field or in the way",
      "The default party outside the state system, and the one that most army models refuse to "
      "see. Brecke's catalog counts conflicts involving these. **willTreat is false and it is "
      "the most consequential false in this table**: a confederacy has no one who can bind the "
      "rest, and a treaty signed by one chief commits nobody. This is the source of the single "
      "most common failure in colonial warfare.",
      "Conflict Catalog (Brecke); Notes regarding the Conflict Catalog; Tribal confederation",
      "recorded"),

    P("warlord_band", "a warlord band", "band", -3000, 2026, WORLD, "warlord_band", False, True, "general",
      "nothing but a man who can feed and arm the men who follow him",
      "fights for the next town, and dissolves when the man dies",
      "Brecke's own example, and the reason this row exists: \"conflicts between warlords when "
      "there is no state involvement qualify as violent conflicts.\" **willTreat is false**, and "
      "the point is best made inside a siege: a conditional surrender is a bargain between two "
      "parties who can each be held to it, and a band has nothing to hold and no one to hold it. "
      "It is the default party for any date before there was a state to be one, and for any "
      "place the state has since failed in, which is why the row runs the whole length of the "
      "register.",
      "Conflict Catalog (Brecke); Violent Conflicts 1400 A.D. to the Present (Brecke); Warlord",
      "recorded"),

    P("steppe_khanate", "a khan and his following", "band", -300, 1800,
      (44.0, 55.0, 30.0, 120.0), "steppe_following", False, True, "general",
      "a khan who keeps winning, because the following is what winning buys",
      "rides as one people under a household of sworn companions, and stops when the khan does",
      "Taylor on the Hellenistic successor armies: \"an implosion of political legitimacy... "
      "effectively transformed all soldiers into de facto volunteers, who swapped their support "
      "between successors.\" That is truer of the steppe than of Macedon. **willTreat is false**: "
      "a following exists for plunder and can be bought off, but it cannot be bound, because it "
      "is a fact about one man and not an institution. The box is the steppe belt and nothing "
      "else -- 44 to 55 north, from the Ponto-Caspian to Manchuria. An earlier box ran to 58 "
      "north and 135 east and swallowed northern China outright, so that Pingyao in 1500 came "
      "back as a khanate: the sown and the steppe are interleaved along that frontier, and a "
      "box generous enough to hold both is not a box that tells you anything.",
      "Mongol military tactics and strategy; Nöker; Motivation in War (Berkovich)", "estimated"),

    # ---------------------------------------------------------------- parties that sell themselves
    P("mercenary_company", "a hired company", "company", 1200, 1650,
      (35.0, 60.0, -10.0, 40.0), "mercenary_company", False, True, "local",
      "a captain with a contract and men willing to follow it",
      "sells itself by the season, and can be a party in its own right when the contract lapses",
      "The Great Company, the White Company, the Catalan Company, which took service from the "
      "Byzantine emperor, murdered his son's envoy and then held the Duchy of Athens for sixty "
      "years as a party of its own. **willTreat is false** and the reason is Slantchev's: hired "
      "troops are \"only as dependable as their pay was regular. When unpaid, hired troops could "
      "passively refuse to fight, mutiny, desert to a higher bidder, and even plunder their "
      "employer's territory.\" An unpaid company cannot be bound, because its captain cannot "
      "deliver it. The date ends in 1650, as it does in the morale pack: after the Thirty "
      "Years' War hired men served inside the standing regiments of a state, and the company "
      "as a party of its own goes with that.",
      "Warfare on Land (Slantchev); Condottieri; Catalan Company; Free company", "recorded"),

    P("chartered_company", "a chartered company", "company", 1600, 1900, WORLD,
      "professional_standing", True, True, "local",
      "a sovereign's charter, a shareholders' capital, and a board that wants a return",
      "raises armies, builds forts, coins money, signs treaties and fights wars -- all for a "
      "dividend",
      "The Dutch East India Company and the English one. The VOC was \"a company, or more "
      "precisely an association of all merchants engaged in Dutch Asian trade\", which concludes "
      "treaties, declares war and administers the conquered territories -- it is, in effect, \"a "
      "state within the state.\" The English Company was raising its own regiments and governing "
      "Bengal by 1757. **willTreat is true**, and that is the interesting thing about this row: "
      "it is the only party in the table that is in the war for money and can still be bound, "
      "because a company has a legal personality that outlives its directors.",
      "Dutch East India Company; East India Company; Chartered company", "recorded"),

    # ---------------------------------------------------------------- the composite and the victim
    P("coalition", "a coalition", "coalition", -3000, 2026, WORLD,
      "professional_standing", True, True, "local",
      "two or more parties who have agreed to be on the same side for the length of this war",
      "fights as one side, and stops being one side the moment the war is over or goes badly",
      "Brecke's catalog records, for conflicts of more than two participants, **who was on each "
      "side**, and the answer is usually a coalition rather than a state. **willTreat is true "
      "but it is the slowest true in the table**: every party in it has to agree, and the "
      "coalitions of the Napoleonic wars took a decade to break apart and a congress to finally "
      "dissolve. It is the default shape of a large war at any date: for conflicts of more than "
      "two participants the catalog's answer is usually a coalition rather than a state.",
      "Conflict Catalog (Brecke); Coalition warfare; Congress of Vienna", "recorded"),

    P("civilians", "civilians", "civilians", -3000, 2026, WORLD, "levy", False, False, "general",
      "nothing; this party is defined by not being one",
      "is the object of the war rather than a belligerent in it",
      "Brecke's definition covers \"political disagreements between organized groups, or between "
      "an organized group and civilians\", and his catalog records civilian fatalities separately "
      "from military ones -- \"military fatalities\" being \"soldiers killed in battles\". "
      "`canInitiate` is false, because by definition this party did not start it, and "
      "`willTreat` is false, because there is nobody to sign. This row exists so that the "
      "register can count what the catalog counts, and it is the default victim at every date and "
      "in every place: it is the one kind of party here defined by not being one.",
      "Conflict Catalog (Brecke); Notes regarding the Conflict Catalog", "recorded"),
]


GAPS = [
    "**The catalog itself was not loaded.** It is a binary spreadsheet, no row of it was read, "
    "and so this table carries the kinds of party Brecke's description admits and not one "
    "conflict, count or date from it.",

    "Brecke's own coverage warning, repeated because it applies to every row here: the catalog is "
    "\"quite complete\" for Western Europe, Eastern Europe, North Africa, West and Central Africa "
    "and East and South Africa -- **and not for the rest.**",

    "Brecke's threshold is 1400, on Luard's authority, because it \"lies between significant "
    "dates for Chinese (1366) and European and American (1492) populations, and demarcates a "
    "point before which the quality and extent of data about many parts of the world drop off "
    "precipitously.\" There is an extension back to 900 AD for Europe and nowhere else. Rows in "
    "this table that begin before 1400 are not from the catalog and say so in their own "
    "sources.",

    "The kinds of party are read from the catalog's description of its own fields, not from a "
    "reading of the catalog. A taxonomy drawn from a description is not the same thing as one "
    "drawn from the data, and Brecke's stated purpose was an empirically-based taxonomy "
    "\"roughly analogous to Kingdom, Phylum, Class, Order\" in biology.",

    "No row for Oceania and none for the Americas before 1491. Not because there were no parties "
    "there -- the catalog's rule that non-state actors qualify would admit them -- but because "
    "nothing was read for them.",
]
